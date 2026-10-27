import argparse
import os
import threading
import socket
import webbrowser
from pathlib import Path
import uvicorn

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-browser',action='store_true')
    args = parser.parse_args()
    data = Path(os.getenv('NEXUS_DATA_DIR',str(Path.home()/'.nexus_ai_ultra')))
    data.mkdir(parents=True,exist_ok=True)
    pidfile = data/'server.pid'
    with socket.socket() as check:
        if check.connect_ex(('127.0.0.1',8765)) == 0:
            print('Port 8765 is already in use. Stop the existing app before starting NEXUS.')
            raise SystemExit(1)
    if not args.no_browser:
        threading.Timer(1.5,lambda:webbrowser.open('http://127.0.0.1:8765')).start()
    pidfile.write_text(str(os.getpid()))
    try: uvicorn.run('nexus.app:app',host='127.0.0.1',port=8765,log_level='info')
    finally:
        if pidfile.exists() and pidfile.read_text()==str(os.getpid()): pidfile.unlink()
