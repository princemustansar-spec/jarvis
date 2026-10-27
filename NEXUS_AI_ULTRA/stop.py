"""Stop only this source installation or its portable executable."""
import os
from pathlib import Path
import psutil

root = Path(__file__).resolve().parent
p = Path(os.getenv('NEXUS_DATA_DIR', str(Path.home()/'.nexus_ai_ultra'))) / 'server.pid'
if p.exists():
    try:
        proc = psutil.Process(int(p.read_text()))
        cmd = proc.cmdline()
        executable = Path(proc.exe()).resolve()
        portable_paths = {root/'dist'/'NEXUS_AI_ULTRA'/'NEXUS_AI_ULTRA.exe', root/'NEXUS_AI_ULTRA.exe'}
        source_owned = any(Path(c).name == 'run.py' for c in cmd) and Path(proc.cwd()).resolve() == root
        if executable in portable_paths or source_owned:
            proc.terminate()
            print('NEXUS stop requested. Closing the desktop window is preferred for graceful shutdown.')
        else:
            print('PID does not belong to this project; no process stopped.')
    except psutil.AccessDenied:
        print('Process identity cannot be verified. Close the NEXUS window; no process stopped.')
    except (psutil.NoSuchProcess, ValueError):
        print('NEXUS is not running.')
else:
    print('No running NEXUS PID found.')
