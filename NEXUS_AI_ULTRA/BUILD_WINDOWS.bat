@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
 echo Run INSTALL.bat first.
 pause
 exit /b 1
)
.venv\Scripts\python -m pip install -r requirements-build.txt -r requirements-optional.txt
if errorlevel 1 goto failed
.venv\Scripts\python -m PyInstaller --noconfirm nexus_desktop.spec
if errorlevel 1 goto failed
echo Portable app: dist\NEXUS_AI_ULTRA\NEXUS_AI_ULTRA.exe
echo Distribute the ENTIRE dist\NEXUS_AI_ULTRA folder, including _internal.
echo Microsoft Edge WebView2 Evergreen Runtime must be installed on the target PC.
pause
exit /b 0
:failed
echo Build failed. Check the error above. Build on Windows x64, not Linux.
pause
exit /b 1
