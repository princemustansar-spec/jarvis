import asyncio
import json
import httpx
import pytest
from nexus.providers import Providers

class Memory:
    def __init__(self, configs): self.configs = configs
    def get(self, key, default=None): return self.configs if key == 'providers' else default

def config(ident='freellm', model='', paid=False):
    return dict(id=ident, name=ident, base='https://'+ident+'.example/v1', model=model, enabled=True, paid=paid, kind='openai')

def setup(monkeypatch, configs, handler):
    router=Providers(Memory(configs)); real=httpx.AsyncClient
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kw:real(transport=httpx.MockTransport(handler),**kw))
    monkeypatch.setattr(router,'key',lambda ident:'synthetic-test-key')
    return router

def ok(model):
    return httpx.Response(200,json={'model':model,'choices':[{'message':{'role':'assistant','content':'ok'}}]})

def test_authenticated_cached_discovery_and_working_priority(monkeypatch):
    calls=[]
    def handler(req):
        assert req.headers['Authorization']=='Bearer synthetic-test-key'
        calls.append(req)
        if req.method=='GET':return httpx.Response(200,json={'data':[{'id':'embedding-small'},{'id':'bad'},{'id':'good'}]})
        model=json.loads(req.content)['model']
        return httpx.Response(429,headers={'Retry-After':'120'}) if model=='bad' else ok(model)
    p=setup(monkeypatch,[config()],handler)
    async def run():
        assert (await p.request([]))[2]=='good'
        assert (await p.request([]))[2]=='good'
    asyncio.run(run())
    assert sum(r.method=='GET' for r in calls)==1
    assert [json.loads(r.content)['model'] for r in calls if r.method=='POST']==['bad','good','good']
    assert p.active['model']=='good'

def test_timeout_next_model_then_provider_fallback(monkeypatch):
    def handler(req):
        if req.method=='GET':return httpx.Response(200,json={'data':[{'id':'one'},{'id':'two'}]})
        if req.url.host=='freellm.example':raise httpx.ReadTimeout('synthetic timeout',request=req)
        return ok('gemini-model')
    p=setup(monkeypatch,[config(),config('gemini',model='gemini-model',paid=True)],handler)
    assert asyncio.run(p.request([],allow_paid=True))[1]=='gemini'
    assert len(p.model_cooldowns)==2

def test_discovery_failure_cached_and_paid_guard(monkeypatch):
    calls=[]
    def handler(req):calls.append(req);return httpx.Response(401)
    p=setup(monkeypatch,[config(),config('groq',paid=True)],handler)
    async def run():
        for _ in range(2):
            with pytest.raises(ValueError,match='approval'):await p.request([])
    asyncio.run(run());assert len(calls)==1

def test_manual_selection_skips_scan(monkeypatch):
    def handler(req):assert req.method=='POST';return ok('manual')
    p=setup(monkeypatch,[config(model='manual')],handler)
    assert asyncio.run(p.request([]))[2]=='manual'

def test_catalog_filter_and_limit():
    assert Providers.chat_models({'data':[{'id':'audio','capabilities':{'chat':False}},{'id':'chat'},{'id':'chat'}]})==['chat']
    assert len(Providers.chat_models({'data':[{'id':str(i)} for i in range(500)]}))==128

def test_restart_credentials_resolved_without_resaving(monkeypatch):
    monkeypatch.setenv('NEXUS_KEY_FREELLM','synthetic-env')
    p=Providers(Memory([config()]));assert p.headers(config())['Authorization']=='Bearer synthetic-env'
    monkeypatch.delenv('NEXUS_KEY_FREELLM')
    monkeypatch.setattr('nexus.providers.keyring.get_password',lambda service,ident:'synthetic-vault')
    assert Providers(Memory([config()])).headers(config())['Authorization']=='Bearer synthetic-vault'

def test_missing_freellm_credential_prevents_unauthenticated_scan(monkeypatch):
    def handler(req):raise AssertionError('must not send unauthenticated discovery')
    p=setup(monkeypatch,[config()],handler)
    monkeypatch.setattr(p,'key',lambda ident:None)
    with pytest.raises(ValueError,match='credential missing'):
        asyncio.run(p.request([]))

@pytest.mark.parametrize('base', ['', 'https://api.groq.com', 'https://api.groq.com/v1', 'https://api.groq.com/openai/v1/chat/completions'])
def test_groq_endpoint_normalization(base):
    p=config('groq',paid=True);p['base']=base
    normalized=Providers.normalize(p)
    assert normalized['base']=='https://api.groq.com/openai/v1'
    assert normalized['paid'] is True


def test_stale_manual_model_falls_back_to_discovered_model(monkeypatch):
    calls=[]
    def handler(req):
        calls.append(req)
        if req.method=='GET':return httpx.Response(200,json={'data':[{'id':'fresh'}]})
        model=json.loads(req.content)['model']
        return httpx.Response(404) if model=='retired' else ok(model)
    p=setup(monkeypatch,[config('groq',model='retired',paid=True)],handler)
    with pytest.raises(ValueError,match='approval'):asyncio.run(p.request([]))
    assert calls==[]
    assert asyncio.run(p.request([],allow_paid=True))[2]=='fresh'
    assert [r.method for r in calls]==['POST','GET','POST']


def test_saved_freellm_paid_flag_is_not_silently_removed(monkeypatch):
    def handler(req):raise AssertionError('no paid request without approval')
    p=setup(monkeypatch,[config(model='auto',paid=True)],handler)
    with pytest.raises(ValueError,match='approval'):asyncio.run(p.request([]))


def test_connect_saves_enables_discovers_and_keeps_vault(tmp_path, monkeypatch):
    import importlib
    monkeypatch.setenv('NEXUS_DATA_DIR',str(tmp_path))
    import nexus.app
    app=importlib.reload(nexus.app)
    vault={}
    monkeypatch.setattr('nexus.providers.keyring.set_password',lambda service,ident,key:vault.update({ident:key}))
    monkeypatch.setattr('nexus.providers.keyring.get_password',lambda service,ident:vault.get(ident))
    real=httpx.AsyncClient
    def handler(req):
        assert req.method=='GET' and req.url.path=='/openai/v1/models'
        assert req.headers['authorization']=='Bearer synthetic-key'
        return httpx.Response(200,json={'data':[{'id':'chat-model'}]})
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kw:real(transport=httpx.MockTransport(handler),**kw))
    async def run():
        async with real(transport=httpx.ASGITransport(app=app.app),base_url='http://127.0.0.1',headers={'x-nexus-token':app.session_token}) as client:
            assert (await client.post('/api/providers/groq/connect',json={'key':'synthetic-key','base':'https://api.groq.com/v1'})).json()['models']==['chat-model']
            assert (await client.post('/api/providers/groq/connect',json={'key':''})).json()['connected']
            assert (await client.post('/api/providers/missing/connect',json={})).status_code==400
    asyncio.run(run())
    groq=next(p for p in app.providers.configs() if p['id']=='groq')
    assert groq['enabled'] and groq['paid']
    assert vault['groq']=='synthetic-key'
    assert 'synthetic-key' not in json.dumps(app.store.get('providers'))


@pytest.mark.parametrize('failure', ['404', 'connection'])
def test_freellm_detects_alternate_local_port(monkeypatch, failure):
    cfg=config();cfg['base']='http://127.0.0.1:31415/v1'
    def handler(req):
        if req.url.port==31415:
            if failure=='connection':raise httpx.ConnectError('unavailable',request=req)
            return httpx.Response(404)
        if req.method=='GET':return httpx.Response(200,json={'data':[{'id':'local-chat'}]})
        assert req.url.port==3847
        return ok('local-chat')
    p=setup(monkeypatch,[cfg],handler)
    async def run():
        assert (await p.probe('freellm'))['connected']
        assert (await p.request([]))[2]=='local-chat'
    asyncio.run(run())
    assert p.configs()[0]['base']=='http://127.0.0.1:3847/v1'
