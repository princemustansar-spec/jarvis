"""Create a native desktop shortcut without changing PowerShell execution policy."""
import os
from pathlib import Path
import subprocess
import sys


def shortcut_target(root):
    root = Path(root).resolve()
    portable = root / 'dist' / 'NEXUS_AI_ULTRA' / 'NEXUS_AI_ULTRA.exe'
    if portable.is_file():
        return portable, '', portable.parent
    if (root / 'NEXUS_AI_ULTRA.exe').is_file():
        return root / 'NEXUS_AI_ULTRA.exe', '', root
    pythonw = root / '.venv' / 'Scripts' / 'pythonw.exe'
    if not pythonw.is_file():
        raise RuntimeError('Run INSTALL.bat first or build the portable Windows application.')
    return pythonw, '"' + str(root / 'run.py') + '"', root


def main():
    if sys.platform != 'win32':
        print('Desktop shortcuts require Windows.')
        return 1
    try:
        root = Path(__file__).resolve().parent
        target, arguments, working = shortcut_target(root)
        # Paths stay in environment values, never interpolated into PowerShell code.
        script = '''$ErrorActionPreference = 'Stop'
$desktop = [Environment]::GetFolderPath('Desktop')
$shell = New-Object -ComObject WScript.Shell
$link = $shell.CreateShortcut((Join-Path $desktop 'NEXUS AI ULTRA.lnk'))
$link.TargetPath = $env:NEXUS_SHORTCUT_TARGET
$link.Arguments = $env:NEXUS_SHORTCUT_ARGUMENTS
$link.WorkingDirectory = $env:NEXUS_SHORTCUT_WORKING
$link.Description = 'NEXUS AI ULTRA desktop assistant'
$link.Save()
'''
        subprocess.run(['powershell.exe', '-NoProfile', '-NonInteractive', '-Command', script],
                       env={**os.environ, 'NEXUS_SHORTCUT_TARGET': str(target),
                            'NEXUS_SHORTCUT_ARGUMENTS': arguments, 'NEXUS_SHORTCUT_WORKING': str(working)}, check=True)
        print('NEXUS AI ULTRA desktop shortcut created.')
        return 0
    except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        print('Shortcut could not be created: ' + str(exc))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
