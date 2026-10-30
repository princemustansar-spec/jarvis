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
