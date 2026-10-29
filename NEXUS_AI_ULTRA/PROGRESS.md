# Persistent delivery checklist

Implemented and verified in cloud:
- [x] Independent source tree; existing jarvis checkout untouched
- [x] FastAPI local server, SQLite, configurable application name
- [x] Screenshot-inspired responsive navy/cyan dashboard, animated core, 17 sections
- [x] Real CPU/RAM/disk/network monitoring and unavailable-battery handling
- [x] Provider configuration, OS-vault integration code, fallback, bounded retries/cooldown
- [x] Unified AI controller, tool-call loops, context/history/memory and cancellation (controlled transport tests)
- [x] 18 allowlisted tools, approved paths, non-overwrite file operations
- [x] Single-use approvals, tool permissions, Emergency Stop
- [x] Persistent memory, reminders, notifications and activity
- [x] Browser navigation, local tool execution, Stop/Resume and memory reload
- [x] Layout checks at requested desktop sizes plus mobile
- [x] Push-to-talk/speaker UI with browser capability checks; no background recording
- [x] Image API transport and paid guard tests; manual WhatsApp draft code
- [x] Windows install/start/stop files and guides created
- [x] 21 backend tests passed; browser file approval confirmed
- [x] Reusable cloud install_script and start_skill saved to draft (not published)

Requires real credentials/hardware; do not mark complete without evidence:
- [ ] Successful live AI chat with a configured real provider
- [ ] Windows 11 installer and native app/window/folder/browser tools
- [ ] Windows Credential Manager actual secret storage/retrieval
- [ ] Microphone recognition, speaker output and voice-language quality
- [ ] Real image provider response and generation
- [ ] Windows screenshot capture using optional Pillow
- [ ] Baseline i3 / 4 GB hardware performance measurements

Explicitly outside current implementation: background wake-word detection, arbitrary scheduled desktop workflows, video generation/editing, built-in webpage retrieval, large bundled local models and destructive optimizer actions. No UI claims these are working.

Resume: use this project folder, read docs/TEST_REPORT.md, configure one real provider through app Settings, run a real chat, then run Windows hardware checks above. Continue from this checklist; do not replace working components or restart the project.

## Desktop conversion (existing application, version 0.2.0)

- [x] Same HTML/CSS/JavaScript preserved byte-for-byte
- [x] pywebview/Edge WebView2 host, no default browser at launch
- [x] Actual API readiness before native window; owned backend shutdown on close
- [x] Console-free Windows launcher, native shortcut creator, bounded diagnostics
- [x] Portable Windows onedir EXE build recipe with existing assets
- [x] 33 tests pass, including real embedded backend lifecycle and original API tests
- [x] 4 GB design constraints and measured backend cloud footprint documented
- [ ] Native Windows WebView2 rendering, microphone and complete process-tree RAM acceptance
- [ ] Build and verify the portable executable on Windows x64

Read docs/DESKTOP_TEST_REPORT.md for evidence and Windows acceptance steps. The previous original browser implementation report is historical; startup now uses the native desktop host. Do not confuse mocked native-host tests with a real Windows window test.

## Laptop auto-fit correction — 28 October 2026

- [x] Existing dashboard adapts to usable window width and height
- [x] AI core/rings scale to their own container without cropping
- [x] Sidebar and Settings remain vertically accessible
- [x] All dashboard action buttons fit at 1366×768 and 1920×1080
- [x] Resize preserves unsaved Settings input; smaller/scaled-window fallbacks tested
- [x] Navy/cyan palette, HTML, action JavaScript and all backend/native-host functionality preserved
- [x] 33 Python tests and both browser suites passed

The stylesheet intentionally supersedes the earlier desktop-conversion CSS hash baseline. Read docs/AUTOFIT_TEST_REPORT.md for current layout evidence.


## Python offline microphone replacement — 28 October 2026

- [x] Removed WebView2/browser SpeechRecognition; Python push-to-talk capture
- [x] CPU INT8 tiny multilingual STT configuration, lazy short-lived worker, in-memory audio only
- [x] English / Urdu plus offline approximate Latin transliteration, editable transcript, no auto-send
- [x] Input device diagnostics, explicit 3-second level test, Stop/Cancel/Emergency Stop
- [x] Verified model setup/checksums, missing-component/device/model error handling
- [x] Existing GUI HTML/CSS and exact speaker output function preserved
- [x] Windows installer/build dependencies and freeze support updated
- [x] 55 Python tests and browser voice/API, functional and auto-fit suites passed
- [ ] Actual Windows microphone and portable EXE run
- [ ] Real offline model transcription accuracy/latency/RAM (cloud model host access denied)

Use docs/OFFLINE_VOICE_GUIDE.md and docs/VOICE_TEST_REPORT.md. Earlier browser-microphone instructions are historical and superseded; do not claim live speech recognition passed from fixture tests.

## JARVIS-style voice feature branch — 29 October 2026

- [x] Actual JARVIS microphone/TTS source inspected at 45648afc5b4593093d0b20a5562da2f60a25eb3b
- [x] Python Google en-IN primary, configurable locales, automatic silence detection
- [x] Existing offline same-audio fallback, 45-second warm-worker/model reuse
- [x] Opt-in Edge Prabhat output, allowed Windows fallback, Stop/Mute
- [x] Safe PowerShell backup/update/rollback; parser and rollback filesystem test
- [x] 67 Linux Python tests plus existing browser suites
- [ ] Actual Windows microphone/accuracy/latency/output acceptance
- [ ] Full Windows installer and low-RAM hardware acceptance
- [ ] PR creation/merge if authenticated GitHub API access is available (native Git access alone is insufficient)
