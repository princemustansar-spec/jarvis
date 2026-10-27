# Build a portable Windows folder; no bundled Chromium or one-file extraction.
from pathlib import Path
import sys

if sys.platform != 'win32':
    raise SystemExit('Build this executable on Windows x64; cross-compiling Windows is unsupported.')

root = Path(SPECPATH)
a = Analysis(
    [str(root / 'run.py')], pathex=[str(root)],
    datas=[(str(root / 'static'), 'static')],
    hiddenimports=['nexus.app', 'webview.platforms.winforms', 'webview.platforms.edgechromium', 'keyring.backends.Windows', 'PIL.ImageGrab'],
    excludes=['pytest', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'cefpython3', 'tkinter'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name='NEXUS_AI_ULTRA',
    debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
    console=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='NEXUS_AI_ULTRA')
