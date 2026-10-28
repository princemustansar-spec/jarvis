# Offline voice change — 28 October 2026

## Implemented

Python sounddevice input, faster-whisper 1.2.1 tiny multilingual CPU INT8, native-rate PCM capture with in-memory PyAV resampling, Silero VAD, bounded short clips, offline uroman Urdu-to-Latin output, explicit microphone consent, diagnostics, stop/transcribe, cancellation and Emergency Stop/shutdown integration. The old JavaScript SpeechRecognition constructor and network speech path are gone. Existing speaker function, HTML, responsive CSS and all nonvoice tools/providers remain preserved.

The dedicated worker is spawned on demand and exits after each operation. PyInstaller entry now calls multiprocessing.freeze_support; Windows build includes PortAudio/native CPU libraries, ONNX VAD assets and uroman data. No binary Windows build was run in this Linux environment.

## Passed automated checks

**55 Python tests passed**, zero skipped; one existing third-party Starlette/AnyIO deprecation warning. Existing backend/desktop tests remain included. New checks cover:

- Authoritative SHA-256 and Git-blob SHA-1 validation, immutable model revision pinning, manifest tamper detection and rejection/cleanup of a bad download. Controlled test artifacts are not production weights.
- Bounded mono capture at the actual device rate, early Stop, silence/clipping/level diagnostics using explicitly generated PCM.
- Real offline uroman transliteration of Urdu script; English unchanged. This verifies script conversion, not speech accuracy or natural Roman spelling.
- Actual PyAV resampling of 48 kHz PCM to the recognizer's 16 kHz ndarray; CPU INT8/local-only/thread/beam/VAD configuration checked against an explicit recognizer test double. No real model was available.
- Device/host API enumeration versus permission-test distinction, missing-model rejection without opening a microphone, duration/device/language validation.
- Real spawned-worker error handling/resource cleanup, real owned-worker cancellation, API consent/session protection, no automatic chat insertion, and Emergency Stop rejection/cancellation.
- HTML/CSS palette/layout and the exact existing speaker function preserved by hashes. The old all-JavaScript hash assertion was replaced because this task intentionally replaces STT code.

**Browser/API transport test passed** (`tests/voice_browser.cjs`): zero browser speech-recognition constructor calls, Python consent/language payload, Stop→transcribe flow, Roman transcript in editable chat, no automatic chat send, and diagnostics populating the device selector. These use clearly identified API fixtures, not real microphone results. Speaker output function remains unchanged; actual sound output is not tested.

Existing full browser functional suite and auto-fit suite passed, including requested 1366×768/1920×1080 layouts, Settings scrolling, all 17 navigation sections, real system tools, SQLite memory, approval-gated file creation and Stop/Resume. Their implementation was not rebuilt.

## Actual runtime/platform evidence

- faster-whisper/CTranslate2, PyAV, ONNX Runtime and uroman imports succeeded. `pip check` passed.
- Windows AMD64/Python 3.11 binary dependency resolution succeeded for the complete voice requirements (see voice-windows-packages.json). This validates available distribution artifacts, not a Windows run.
- Official Windows AMD64 sounddevice 0.5.6 wheel downloaded from PyPI and inspected: it contains native PortAudio DLLs including the x64 build. This is packaging inspection, not Windows execution.
- Real API microphone diagnostics in this Linux cloud reported missing PortAudio, with an actionable dependency/runtime message. No physical microphone was available.
- Actual model setup attempted the official Hugging Face endpoint and failed with the cloud proxy's access denial. The application reported a model-download error, retained model_ready=false and did not claim a provider/model was ready. No verification was bypassed.
- Backend-only idle footprint after these probes: about 44 MB RSS. This does not measure WebView2, real model inference or Windows 4 GB performance.

See voice-runtime-probe.json and voice-browser-results.json for recorded outcomes. Raw audio, keys and tokens are absent from reports.

## Required Windows acceptance

1. Update/install dependencies, verify Microsoft's x64 VC++ runtime as needed, rebuild a previously packaged EXE.
2. Install/verify the offline model once with normal Internet access.
3. Enumerate the real microphone, permit desktop-app microphone access, and run the 3-second input test.
4. Disconnect Internet and record clear English and Urdu speech. Verify real transcripts, Roman conversion quality, device selection, native-rate capture, Stop, Cancel and Emergency Stop.
5. Verify existing speaker output and providers still behave as before.
6. Measure full WebView2 + backend + temporary worker memory and latency on the actual 4 GB laptop; confirm the worker releases memory after completion/cancel/close.

Live Windows microphone capture, real-model English/Urdu recognition quality and inference memory/latency remain **unverified**, not passed. GUI/API/fixture tests do not establish those outcomes.
