import asyncio
import os
import time
from urllib.parse import urlparse
import httpx
import keyring

DEFAULTS = [
 dict(id='freellm', name='FreeLLMAPI', base='http://127.0.0.1:31415/v1', model='', kind='openai', paid=False, enabled=False),
 dict(id='freellm-alt', name='FreeLLMAPI alternate', base='http://127.0.0.1:3847/v1', model='', kind='openai', paid=False, enabled=False),
 dict(id='ollama', name='Ollama', base='http://127.0.0.1:11434/v1', model='', kind='openai', paid=False, enabled=False),
 dict(id='groq', name='Groq', base='https://api.groq.com/openai/v1', model='', kind='openai', paid=True, enabled=False),
 dict(id='gemini', name='Google Gemini', base='https://generativelanguage.googleapis.com/v1beta/openai', model='', kind='openai', paid=True, enabled=False),
 dict(id='openrouter', name='OpenRouter', base='https://openrouter.ai/api/v1', model='', kind='openai', paid=True, enabled=False),
]

class Providers:
    def __init__(self, store):
        self.store = store
        self.status = {}
        self.cooldowns = {}

    def configs(self):
        return self.store.get('providers', DEFAULTS)

    def key(self, ident):
        value = os.getenv('NEXUS_KEY_' + ident.upper().replace('-', '_'))
        if value:
            return value
        try:
            return keyring.get_password('NEXUS_AI_ULTRA', ident)
        except Exception:
            return None

    def save(self, configs):
        clean = []
        for p in configs:
            ident = p['id']
            if not ident.replace('-', '').replace('_', '').isalnum():
                raise ValueError('Provider ID must contain letters, numbers, underscores or hyphens.')
            u = urlparse(p['base'])
            if u.scheme not in ('http', 'https') or not u.hostname or u.username or u.password or u.query or u.fragment:
                raise ValueError('Use an API base URL without credentials or query strings.')
            if u.scheme != 'https' and u.hostname not in ('localhost', '127.0.0.1', '::1'):
                raise ValueError('Remote providers require HTTPS.')
            secret = p.get('key', '').strip()
            if secret:
                try:
                    keyring.set_password('NEXUS_AI_ULTRA', ident, secret)
                except Exception as exc:
                    raise ValueError('Secure OS credential storage unavailable; configure NEXUS_KEY_' + ident.upper().replace('-', '_') + ' securely in your environment.') from exc
            clean.append({k: p[k] for k in ('id', 'name', 'base', 'model', 'kind', 'paid', 'enabled')})
        if len({p['id'] for p in clean}) != len(clean):
            raise ValueError('Provider IDs must be unique.')
        self.store.set('providers', clean)
        self.status.clear()

    def headers(self, p):
        k = self.key(p['id'])
        return {'Authorization': 'Bearer ' + k} if k else {}

    async def probe(self, ident):
        p = next((p for p in self.configs() if p['id'] == ident), None)
        if not p:
            raise ValueError('Unknown provider')
        try:
            async with httpx.AsyncClient(timeout=8, follow_redirects=False) as c:
                r = await c.get(p['base'].rstrip('/') + '/models', headers=self.headers(p))
                r.raise_for_status()
                models = [m['id'] for m in r.json().get('data', [])]
            result = dict(connected=True, models=models, error=None)
        except Exception as exc:
            result = dict(connected=False, models=[], error=self.error(exc))
        self.status[ident] = result
        return result

    @staticmethod
    def error(exc):
        if isinstance(exc, httpx.HTTPStatusError):
            return f'Provider HTTP {exc.response.status_code}: {exc.response.reason_phrase}'
        return type(exc).__name__ + ': ' + str(exc).split('Bearer')[0][:180]

    async def request(self, messages, tools=None, allow_paid=False):
        errors = []
        preferred = self.store.get('preferred_provider', '')
        configs = sorted(self.configs(), key=lambda p: p['id'] != preferred)
        async with httpx.AsyncClient(timeout=60, follow_redirects=False) as c:
            for p in configs:
                if not p['enabled'] or not p['model']:
                    continue
                if p['paid'] and not allow_paid:
                    errors.append(p['name'] + ': paid request requires your approval')
                    continue
                if self.cooldowns.get(p['id'], 0) > time.monotonic():
                    errors.append(p['name'] + ': rate-limit cooldown active')
                    continue
                body = dict(model=p['model'], messages=messages)
                if tools:
                    body['tools'] = tools
                for attempt in range(2):
                    try:
                        r = await c.post(p['base'].rstrip('/') + '/chat/completions', json=body, headers=self.headers(p))
                        if r.status_code == 429:
                            self.cooldowns[p['id']] = time.monotonic() + 60
                        if r.status_code in (502, 503, 504) and attempt == 0:
                            await asyncio.sleep(0.5)
                            continue
                        r.raise_for_status()
                        data = r.json()
                        msg = data['choices'][0]['message']
                        self.status[p['id']] = dict(connected=True, models=[data.get('model', p['model'])], error=None)
                        return msg, p['name'], data.get('model', p['model'])
                    except (httpx.HTTPError, ValueError, KeyError, IndexError) as exc:
                        self.status[p['id']] = dict(connected=False, models=[], error=self.error(exc))
                        errors.append(p['name'] + ': ' + self.error(exc))
                        break
        raise ValueError('; '.join(errors) or 'No enabled provider with a model. Configure and test one in Settings.')

    async def image(self, ident, prompt, allow_paid=False):
        p = next((p for p in self.configs() if p['id'] == ident and p['enabled']), None)
        if not p:
            raise ValueError('Select an enabled compatible image provider.')
        if p['paid'] and not allow_paid:
            raise ValueError('Paid image requests require approval.')
        async with httpx.AsyncClient(timeout=90, follow_redirects=False) as c:
            r = await c.post(p['base'].rstrip('/') + '/images/generations', headers=self.headers(p), json=dict(model=p['model'], prompt=prompt, n=1, size='1024x1024', response_format='b64_json'))
            r.raise_for_status()
            return r.json()['data']
