@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
 echo Run INSTALL.bat first.
 pause
 exit /b 1
)
.venv\Scripts\python -m pip install -r requirements-voice.txt
if errorlevel 1 (
 echo Voice dependency installation failed. Check the error above and Internet access to PyPI.
 pause
 exit /b 1
)
echo Voice components installed. Restart NEXUS.
echo In Voice Assistant, click Install offline model once, then run Microphone diagnostics.
echo Model download needs Internet once; microphone recognition then works offline.
pause
