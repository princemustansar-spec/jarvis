@echo off
cd /d "%~dp0"
if exist dist\NEXUS_AI_ULTRA\NEXUS_AI_ULTRA.exe (
 start "" "%~dp0dist\NEXUS_AI_ULTRA\NEXUS_AI_ULTRA.exe"
 exit /b 0
)
if not exist .venv\Scripts\pythonw.exe (
 echo Run INSTALL.bat first.
 pause
 exit /b 1
)
start "" "%~dp0.venv\Scripts\pythonw.exe" "%~dp0run.py"
