# pywebview desktop conversion — 27 October 2026

Historical conversion report. The later 28 October viewport-fit correction intentionally updates responsive CSS; HTML/actions and the native host remain unchanged. See AUTOFIT_TEST_REPORT.md for current layout evidence.

## Change and preservation

The existing application is hosted by pywebview 6.2.1 with the Windows Edge WebView2 renderer. The native entry point starts one owned Uvicorn backend in a thread, waits for a successful `/api/state` response containing the expected PID and 18 tools, then creates the native window. Closing the window shuts down that backend, cancels outstanding requests through Uvicorn's bounded shutdown and removes its PID file. The default browser is never called by the app launcher. `--headless` is an explicit API-only development mode; `--no-browser` remains an alias.

Unchanged: all three frontend files, all backend API/controller/provider/store/tool modules, database location/schema, permissions, buttons, provider configuration and tool behavior. The same local URL and existing same-origin protection are used. Intentional browser-opening tools still perform their documented actions.

Frontend SHA-256 baseline from the existing uploaded project:
- `static/index.html`: `5f02dc402cb95cb001fa82b94f29864493e6948411e4a364af0a93cbfdeb6766`
- `static/style.css`: `e5101c992c3f00d4a622753613afb1eb65297befb4bcf6201c0fcc264cbb0158`
- `static/app.js`: `b051b7cf8607313690c4ea88fe77a088670638815b97d8e5314c6b4197269d89`

## Executed in Linux cloud

- **33 pytest tests passed**, zero skipped. All 21 original tests still pass; 12 desktop tests cover the native-host configuration, GUI asset hashes, no browser fallback on renderer failure, backend failure cleanup, occupied-port handling without PID overwrite, ownership-aware PID removal, unsupported OS reporting, source/portable shortcut paths, default desktop mode/headless compatibility, and a real embedded-server lifecycle.
- The embedded-server test runs real HTTP requests during an explicitly mocked GUI loop: real `/api/state`, dashboard request, SQLite memory write/read, native-loop return, backend thread shutdown, closed port and PID cleanup. It is not a native window rendering test.
- Real subprocess lifecycle: API readiness, persisted memory, shutdown and restart. Backend-only measurements: startup 0.575 s, restart 0.407 s, idle RSS 42.1 MB, CPU 0.0% over a 3-second sample. This does not measure Windows or WebView2 child processes.
- Python syntax and frontend JavaScript syntax checks. Desktop PyInstaller spec parsed without executing a Windows build.
- Runtime dependencies validated with pip; the Windows-only pywebview marker correctly excludes native GUI dependencies from cloud/headless installation.
- pywebview 6.2.1 wheel downloaded from PyPI with verification enabled; its actual create_window/start signatures and built-in PyInstaller hook inspected. Windows renderer and data collection options match those supported interfaces.
- Source installer and launcher scripts inspected; Windows batch execution is not claimed.

The original browser screenshot/layout evidence remains relevant because the frontend bytes are identical. It is historical browser evidence, not proof of native WebView2 rendering.

## 4 GB RAM design

One Python backend, one native window, shared OS WebView2 runtime; no bundled Chromium, Electron, Qt/CEF fallback, local LLM preload, hot reload, devtools, extra monitoring timers or hidden browser-launch worker. Access logging is disabled in desktop/headless host configuration. Rotating diagnostics use at most three 1 MB log files. The portable build is one folder to avoid one-file extraction overhead. Existing monitoring cadence and animations are unchanged to preserve the design.

Targets on the requested i3 / 4 GB Windows PC: backend idle RSS <120 MB, backend idle CPU <2%, total desktop tree steady-state working set <300 MB, startup <3 seconds. These are targets, not measured Windows guarantees. WebView2 is multiprocess: include its child processes when measuring total memory. No GPU/TLS/security features are disabled to reduce memory.

## Windows acceptance still required

This machine is Linux and has no Windows desktop, WebView2 runtime, Windows Python/.NET bridge or Windows compiler environment. No Windows executable was built here. Run the following on Windows 11 x64:

1. Run INSTALL.bat with Python 3.11 or 3.12 x64. Verify dependency installation and desktop shortcut creation.
2. Run START_NEXUS.bat or the shortcut: one native window, same dashboard, no default-browser startup. Verify actual 1366×768 / 1536×1024 / 1920×1080 layout and native dialogs.
3. Configure a real provider, test chat, approvals, memory, reminders, Windows tools and image integration with your credentials.
4. Check microphone/speaker support inside WebView2; SpeechRecognition availability can differ from a full browser. The unchanged UI reports actual capability.
5. Close the native window; confirm the API stops, then reopen and verify the same saved records.
6. Run BUILD_WINDOWS.bat. Launch dist\NEXUS_AI_ULTRA\NEXUS_AI_ULTRA.exe and verify the same checks on a PC without Python, with WebView2 installed. Distribute the whole folder, not the EXE alone.
7. Measure the backend plus WebView2 process tree on the 4 GB machine and record results before calling low-memory hardware acceptance complete.

The portable build uses the official pywebview PyInstaller hook plus explicit backend/Windows-vault/screenshot imports. The target PC needs no Python after a successful Windows build; it still requires WebView2. Build artifacts are not committed.
