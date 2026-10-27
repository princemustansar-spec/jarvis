"""Real subprocess startup, HTTP readiness, restart persistence and idle measurements."""
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
import httpx
import psutil

root=Path(__file__).resolve().parent.parent
python=root/'.venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
data=tempfile.mkdtemp(prefix='nexus-lifecycle-')
url='http://127.0.0.1:8765'

def start():
    started=time.monotonic()
    p=subprocess.Popen([str(python),'run.py','--no-browser'],cwd=root,env={**os.environ,'NEXUS_DATA_DIR':data},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    for _ in range(80):
        if p.poll() is not None: raise RuntimeError('Server exited during startup')
        try:
            s=httpx.get(url+'/api/state',timeout=.2,trust_env=False)
            if s.status_code==200 and s.json()['monitor']['pid']==p.pid: return p,s.json(),time.monotonic()-started
        except httpx.HTTPError: pass
        time.sleep(.05)
    p.terminate();raise RuntimeError('Readiness timed out')

def stop(p):
    p.terminate();p.wait(timeout=10)
    try: httpx.get(url+'/api/state',timeout=.2,trust_env=False)
    except httpx.HTTPError: return
    raise RuntimeError('Server still responds after shutdown')

p,s,startup=start()
try:
    headers={'x-nexus-token':s['token']}
    r=httpx.post(url+'/api/records/memory',json={'text':'restart-proof'},headers=headers,trust_env=False);r.raise_for_status()
    proc=psutil.Process(p.pid);cpu=proc.cpu_percent(interval=3);rss=proc.memory_info().rss
finally:stop(p)
p,s,restart=start()
try:
    assert any(m['text']=='restart-proof' for m in s['memory'])
finally:stop(p)
result=dict(startup_seconds=round(startup,3),restart_seconds=round(restart,3),idle_cpu_percent=cpu,rss_mb=round(rss/1048576,1),restart_persistence=True,shutdown=True,platform=os.name)
(root/'docs/lifecycle-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result))
