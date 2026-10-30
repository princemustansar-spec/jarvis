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
        self.discovery = {}
        self.model_cooldowns = {}
        self.working = {}
        self.active = None
        self.discovery_lock = asyncio.Lock()

    @staticmethod
    def chat_models(data):
        # OpenAI catalogs often omit capabilities. Explicit non-chat entries are
        # excluded; unknown entries are candidates, verified only by inference.
        result = []
        for item in data.get('data', []):
            ident = item.get('id', '')
            if not isinstance(ident, str) or not ident or len(ident) > 256:
                continue
            caps = item.get('capabilities', {})
            if isinstance(caps, dict) and caps.get('chat') is False:
                continue
            if any(word in ident.lower() for word in ('embedding', 'whisper', 'tts', 'dall-e', 'moderation', 'rerank', 'stable-diffusion')):
                continue
            if ident not in result:
                result.append(ident)
            if len(result) >= 128:
                break
        return result

    def router_status(self):
        return dict(mode='AUTO', active=self.active, providers=self.status)

    async def discover(self, p, force=False):
        cache_key = (p['id'], p['base'])
        async with self.discovery_lock:
            cached = self.discovery.get(cache_key)
            if not force and cached and cached[0] > time.monotonic():
                return cached[1]
            try:
                if p['id'].startswith('freellm') and not self.key(p['id']):
                    raise ValueError('FreeLLMAPI credential missing; save its API key in Settings')
                async with httpx.AsyncClient(timeout=8, follow_redirects=False) as c:
                    r = await c.get(p['base'].rstrip('/') + '/models', headers=self.headers(p))
                    r.raise_for_status()
                    models = self.chat_models(r.json())
                result = dict(connected=True, models=models, error=None)
                ttl = 600
            except Exception as exc:
                result = dict(connected=False, models=[], error=self.error(exc))
                ttl = 30
            self.discovery[cache_key] = (time.monotonic() + ttl, result)
            self.status[p['id']] = result
            return result

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
        self.discovery.clear()
        self.model_cooldowns.clear()
        self.cooldowns.clear()
        self.working.clear()
        self.active = None

    def headers(self, p):
        k = self.key(p['id'])
        return {'Authorization': 'Bearer ' + k} if k else {}

    async def probe(self, ident):
        p = next((p for p in self.configs() if p['id'] == ident), None)
        if not p:
            raise ValueError('Unknown provider')
        return await self.discover(p, force=True)

    @staticmethod
    def error(exc):
        if isinstance(exc, httpx.HTTPStatusError):
            return f'Provider HTTP {exc.response.status_code}: {exc.response.reason_phrase}'
        return type(exc).__name__ + ': ' + str(exc).split('Bearer')[0][:180]

    async def request(self, messages, tools=None, allow_paid=False):
        errors = []
        preferred = self.store.get('preferred_provider', '')
        configs = sorted(self.configs(), key=lambda p: (
            p['id'] != preferred if preferred else not p['id'].startswith('freellm'),
            0 if p['id'].startswith('freellm') else 1 if p['id'] in ('gemini', 'groq') else 2))
        self.active = None
        # A bounded overall deadline prevents large catalogs multiplying latency.
        try:
            async with asyncio.timeout(45):
                async with httpx.AsyncClient(timeout=httpx.Timeout(6, connect=3), follow_redirects=False) as c:
                    for p in configs:
                        if not p['enabled']:
                            continue
                        if p['paid'] and not allow_paid:
                            errors.append(p['name'] + ': paid request requires your approval')
                            continue
                        if self.cooldowns.get(p['id'], 0) > time.monotonic():
                            errors.append(p['name'] + ': provider cooldown active')
                            continue
                        manual = p.get('model', '').strip()
                        if manual and manual.upper() != 'AUTO':
                            models = [manual]
                        else:
                            discovered = await self.discover(p)
                            models = discovered['models']
                            if not models:
                                errors.append(p['name'] + ': ' + (discovered['error'] or 'no chat model candidates'))
                                continue
                        models = sorted(models, key=lambda m: -self.working.get((p['id'], m), 0))
                        # Reserve opportunities for fallback providers even with huge catalogs.
                        attempted = 0
                        for model in models:
                            key = (p['id'], model)
                            if self.model_cooldowns.get(key, 0) > time.monotonic():
                                errors.append(p['name'] + ': model cooldown active')
                                continue
                            if attempted >= 3:
                                break
                            attempted += 1
                            body = dict(model=model, messages=messages)
                            if tools:
                                body['tools'] = tools
                            try:
                                r = await c.post(p['base'].rstrip('/') + '/chat/completions', json=body, headers=self.headers(p))
                                r.raise_for_status()
                                data = r.json()
                                msg = data['choices'][0]['message']
                                if not isinstance(msg, dict) or not (msg.get('content') or msg.get('tool_calls')):
                                    raise ValueError('Model returned no assistant content or tool calls')
                                actual = data.get('model', model)
                                self.working[key] = time.monotonic()
                                self.status[p['id']] = dict(connected=True, models=models, error=None)
                                self.active = dict(provider=p['name'], provider_id=p['id'], model=actual)
                                return msg, p['name'], actual
                            except (httpx.HTTPError, ValueError, KeyError, IndexError, TypeError) as exc:
                                delay = 60
                                if isinstance(exc, httpx.HTTPStatusError):
                                    if exc.response.status_code == 429:
                                        try:
                                            delay = min(300, max(60, float(exc.response.headers.get('Retry-After', '60'))))
                                        except ValueError:
                                            pass
                                    if exc.response.status_code in (401, 403):
                                        self.cooldowns[p['id']] = time.monotonic() + 60
                                self.model_cooldowns[key] = time.monotonic() + delay
                                self.status[p['id']] = dict(connected=False, models=models, error=self.error(exc))
                                errors.append(p['name'] + ': ' + self.error(exc))
                                if self.cooldowns.get(p['id'], 0) > time.monotonic():
                                    break
        except TimeoutError:
            errors.append('Router request deadline exceeded')
        raise ValueError('; '.join(errors[-8:]) or 'No enabled provider with a model. Enable a provider in Settings; blank model uses AUTO discovery.')

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
