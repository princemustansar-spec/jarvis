import os
from pathlib import Path
import psutil
p = Path(os.getenv('NEXUS_DATA_DIR',str(Path.home()/'.nexus_ai_ultra')))/'server.pid'
if p.exists():
    try:
        proc = psutil.Process(int(p.read_text()))
        cmd = proc.cmdline()
        if any(Path(c).name == 'run.py' for c in cmd) and Path(proc.cwd()).resolve()==Path(__file__).resolve().parent:
            proc.terminate()
            print('NEXUS stop requested.')
        else: print('PID does not belong to this project; no process stopped.')
    except psutil.AccessDenied:
        print('Process identity cannot be verified with current permissions. Use Ctrl+C in the NEXUS console; no process stopped.')
    except (psutil.NoSuchProcess, ValueError): print('NEXUS is not running.')
else: print('No running NEXUS PID found.')
