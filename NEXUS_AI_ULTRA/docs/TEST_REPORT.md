# Test report — 27 October 2026

This is a tested core implementation, not a claim of completed Windows or real-provider acceptance. Environment: Linux cloud, Python 3.12.14, headless system Chromium. No actual provider credentials were supplied. FreeLLMAPI ports 31415/3847 and Ollama 11434 were probed and refused connections. None was shown as verified.

## Executed and passed

- `python -m compileall -q nexus run.py stop.py` — syntax/import compilation.
- `node --check static/app.js` — frontend JavaScript syntax.
- `python -m pip check` — no broken dependencies.
- `python -m pytest -q` — **21 passed**, zero skipped. One third-party Starlette/AnyIO deprecation warning, no functional test failures in the final run.
- SQLite reopen persistence, settings and memory deletion.
- Real system measurement, unavailable-battery handling.
- Approved-root enforcement, ordinary symlink escape rejection, non-overwriting creation, copy and move.
- Session-token, cross-origin and Host rejection; security headers.
- Approval before file creation, single-use and expired/denied approvals, Emergency Stop and per-tool denial.
- Reminder validation, exactly-once delivery under the single in-process scheduler, and persisted delivered status. Notification and delivered-state writes share one transaction.
- Missing provider error and HTTPS validation.
- Unified controller calling a real system tool through a controlled provider test double.
- Mock HTTP provider model probing, chat parsing, fallback, 429 cooldown and paid-request guard.
- In-flight request cancellation and sensitive AI calls queued without file execution.
- Credential storage interface test confirms keys are absent from saved configuration.
- Image HTTP transport and cost approval guard with controlled responses.

**Important:** mocked transports validate integration logic, not external provider availability or AI quality. No test fixture response is used in the production app.

## Real browser checks

`tests/browser.cjs` uses Playwright with the installed system Chromium. `docs/browser-results.json` records the results; `dashboard-*.png` are screenshots of the real running application.

- 1366 × 768, 1536 × 1024, 1920 × 1080 and 390 × 844 rendered without horizontal overflow.
- All 17 navigation sections opened, without JavaScript page errors.
- Memory created through the UI remained visible after page reload.
- System-info tool returned actual RAM/OS data through the UI.
- Emergency Stop and Resume changed live state.
- File creation remained pending until the exact action was approved through the UI, then produced the expected file. Test artifacts were removed.

Content can scroll vertically; fitting every dashboard panel above the fold at 768 pixels is not claimed. No screen-size test can establish microphone or Windows API correctness.

Browser test reproduction: install Playwright in a disposable tooling folder (`npm install --prefix /tmp/nexus-browser --cache /tmp/nexus-npm-cache playwright`), start the app, then `NODE_PATH=/tmp/nexus-browser/node_modules node tests/browser.cjs`. Linux defaults to `/usr/bin/chromium`; set `CHROMIUM_PATH` to a compatible browser on another platform. Playwright browser download was denied by cloud domain policy; the existing system Chromium was used successfully. No TLS checks were disabled.

## Real lifecycle and cloud performance

`python tests/lifecycle.py` starts the actual server, checks HTTP readiness, creates a memory, shuts down, restarts and verifies that memory. Both shutdowns completed and the port stopped responding. The script uses disposable data, not user history.

Measured cloud results (see lifecycle-results.json): initial startup 0.345 s; restart 0.312 s; idle backend RSS 43.7 MB; CPU 0.3% over a 3-second idle sample. This is a short backend-only cloud measurement, not a representative Windows laptop benchmark; browser resources and AI latency are excluded.

A cloud permission restriction prevents STOP_NEXUS's helper from reading another process's working directory. The helper now refuses safely with a clear message. The owned server was stopped directly, and subprocess lifecycle termination was verified. Windows batch launchers were inspected, not executed on Windows.

## Unverified / external prerequisites

- At least one live configured AI conversation (required for full acceptance).
- Windows 11 installation, allowlisted application launching, visible windows, folder/browser opening, manual WhatsApp browser draft and screenshot capture.
- Actual Windows Credential Manager storage and retrieval.
- Physical microphone, speech service, real speaker, voice selection and Roman Urdu recognition quality.
- Real image generation and media output from a configured provider.
- Performance on the specified i3 / 4 GB laptop.

## Deliberately unavailable

Video generation/editing, continuous wake word, arbitrary scheduled desktop actions, built-in public-page retrieval and destructive “RAM boost” behavior. These have no fake working buttons or fabricated success states.

## Saved environment instructions

Cloud install_script and start_skill were saved successfully to the environment draft. They use the existing new project folder and a separate runtime data directory. Saving did not publish a snapshot or establish fresh-task restoration; review/save in environment settings, then publish to retain this filesystem. No credentials were added.
