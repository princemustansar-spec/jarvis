# Build a portable Windows folder; no bundled Chromium or one-file extraction.
from pathlib import Path
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

if sys.platform != 'win32':
    raise SystemExit('Build this executable on Windows x64; cross-compiling Windows is unsupported.')

root = Path(SPECPATH)
a = Analysis(
    [str(root / 'run.py')], pathex=[str(root)],
    datas=[(str(root / 'static'), 'static')] + collect_data_files('faster_whisper') + collect_data_files('uroman') + collect_data_files('_sounddevice_data') + collect_data_files('speech_recognition'),
    binaries=collect_dynamic_libs('ctranslate2') + collect_dynamic_libs('_sounddevice_data'),
    hiddenimports=['nexus.app', 'webview.platforms.winforms', 'webview.platforms.edgechromium', 'keyring.backends.Windows', 'PIL.ImageGrab', 'nexus.voice', 'sounddevice', 'faster_whisper', 'uroman', 'onnxruntime', 'tokenizers', 'av', 'speech_recognition', 'edge_tts', 'pygame', 'pyttsx3.drivers.sapi5', 'comtypes'],
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
