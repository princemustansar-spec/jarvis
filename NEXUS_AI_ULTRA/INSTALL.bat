@echo off
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto failed
.venv\Scripts\python -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Installation complete. Run START_NEXUS.bat
pause
exit /b 0
:failed
echo Installation failed. Install Python 3.11 or newer, then retry.
pause
exit /b 1
