# NEXUS AI ULTRA

Independent Python + local browser Windows assistant, built from scratch. No existing JARVIS or ZAYRON source was used. Midnight navy dashboard, animated cyan AI core, 17 navigation sections, real system telemetry, an approval-controlled tool registry, persistent SQLite records and configurable API integrations.

**Release status:** tested core implementation, not fully verified Windows handover. Real AI conversation requires your configured running provider. This environment had no provider credentials or local model. Transport tests use explicit test doubles, never displayed as real AI connectivity. Windows desktop, microphone, OS credential vault and image-provider verification remain necessary on your computer.

## Windows installation

1. Install Python 3.11+ 64-bit from python.org with the Python launcher enabled.
2. Extract the project to `C:\NEXUS_AI_ULTRA` (or another folder you own).
3. Double-click `INSTALL.bat`. It creates a local virtual environment and installs dependencies with TLS verification enabled.
4. Double-click `START_NEXUS.bat`. The local dashboard opens in your browser. Keep the console open.
5. For a desktop shortcut: right-click `START_NEXUS.bat` → Show more options → Send to → Desktop.
6. To stop, press Ctrl+C in the console, or double-click `STOP_NEXUS.bat`. The stopper checks the PID's project path before terminating it.

Optional screenshot support: run `.venv\Scripts\python -m pip install -r requirements-optional.txt` from this folder. Pillow is not needed for other modules.

## First-run API setup

Open Settings. The application uses OpenAI-compatible APIs including Gemini's compatibility endpoint, Groq, OpenRouter, Ollama and configurable FreeLLMAPI endpoints. An endpoint is not assumed to have any particular model or capabilities.

- Configure the API base URL, not the full chat-completions URL. Local defaults are `http://127.0.0.1:31415/v1`, `http://127.0.0.1:3847/v1` and Ollama's `http://127.0.0.1:11434/v1`.
- If your FreeLLMAPI server has a different API path, edit the base accordingly. Compatibility must be verified with your server.
- Enter credentials in the password field. They go to the OS credential vault through `keyring`, not SQLite or source code. Blank retains an existing credential. If a vault is unavailable, saving a new key fails clearly; it never silently falls back to a plaintext file.
- Alternatively, securely supply `NEXUS_KEY_<PROVIDER_ID>` as an environment variable. Uppercase ID, with hyphens replaced by underscores: `NEXUS_KEY_GROQ`, `NEXUS_KEY_FREELLM_ALT`, etc. `.env.example` documents names; the app intentionally does not load a plaintext `.env` file.
- Save all providers, then Test saved endpoint. Copy an actual model ID returned by the endpoint into the model field and save again. An authenticated `/models` response verifies that endpoint only; a successful chat additionally verifies inference.
- Enable providers you want to use. Choose a preferred provider; other enabled providers are fallback candidates. Enabled endpoints are probed at app startup.
- Remote commercial providers default to “may incur cost.” Check “Allow paid request” per chat/image request to authorize those calls, including fallback calls in that request. Do not mark a paid service free unless you have independently verified its billing policy.
- HTTP 429 triggers a 60-second cooldown; transient gateway errors get one bounded retry per provider. Maximum five tool-planning rounds and eight calls per round.

Use a trusted provider: messages, approved file-tool results and approved long-term memories can be sent to it. Only OpenAI-compatible tool-calling models can use the unified tool workflow. Connectivity status is observational; a failed provider becomes unavailable, not a simulated assistant.

## Actual capabilities

- Local FastAPI server bound only to loopback, same-origin/session-token protection, CSP, parameterized SQLite queries, no shell execution.
- Configurable application name, exact model configuration, secure key handling, fallback, cooldown, cancellation and bounded tool calling.
- Real CPU/RAM/disk/network measurements, optional battery detection, process information and app RSS.
- 18 real tools: system info, process list, visible Windows windows, folder listing, filename search, approved text reading/creation/copy/move, allowlisted Windows apps, folders, web search/browser opening, manual WhatsApp drafts, screenshot, reminders, approved memory and maintenance report.
- File paths constrained to approved folders with resolved-path checks. Text reads limited to 1 MB; listing/search bounded. New files do not overwrite existing files.
- Single-use five-minute action approvals, per-tool permissions, activity/error log, Emergency Stop and inference cancellation.
- SQLite chat history, approved memory, reminders and activity. Due reminders notify in the app while running; overdue items are delivered on restart. No Windows service is installed.
- Browser speech recognition and speech synthesis where supported. Push-to-talk, transcript review before sending, speaker selection excluding Asad/Uzma. Browser recognition may use an external speech service. No continuous listening or wake word by default.
- Image generation through a compatible configured `/images/generations` endpoint. Response images or secure result links render in Media Studio.
- WhatsApp drafts open for manual review and sending; nothing sends automatically.

## Scope and limits

No fake RAM booster, process killer, arbitrary shell executor, automatic WhatsApp sender, bundled LLM, video generation/editor, autonomous background wake word or general-purpose desktop macro engine. Scheduled automation currently means persistent reminders; arbitrary scheduled app/file actions are unsupported. Web search opens the browser; the app does not crawl pages or provide a built-in search-results API. Memory teaching stores guidance, not model training. Tool approval executes the reviewed action and shows its result; further AI discussion is a new chat turn.

AI cancellation stops local waiting and pending operations where possible. It cannot reverse completed file/browser actions or guarantee cancellation/billing reversal at a remote provider. In-progress synchronous local file operations are not forcibly interrupted. Approved folders must be trusted: resolved paths prevent ordinary traversal/symlink escape but this is not a hardened sandbox against another process concurrently modifying filesystem links. Run as a standard user, not administrator. Other local processes under your account are within the trust boundary.

Linux can exercise the dashboard, storage, API transports and most read-only/file tools. Windows-specific tools report unsupported instead of claiming success. Battery, native windows, browser-opening, microphone and secure vault support depend on the host. Keys stored in Windows Credential Manager should be managed there for rotation/removal. Local SQLite records are unencrypted and contain chat/memory; protect the user account and backups.

## Data and project layout

Default data: `%USERPROFILE%\.nexus_ai_ultra\nexus.sqlite3`; override with `NEXUS_DATA_DIR`. No credentials are saved in the database. Back up this directory with the app stopped.

```
NEXUS_AI_ULTRA/
  nexus/app.py         HTTP API, AI controller, approvals, scheduler
  nexus/providers.py  provider transports and secure key references
  nexus/tools.py      allowlisted tools and live monitoring
  nexus/store.py      SQLite persistence
  static/             HTML, CSS, JavaScript dashboard
  tests/              isolated integration/unit tests
  docs/               guides, test report, browser evidence
  run.py / stop.py    local lifecycle
  INSTALL.bat / START_NEXUS.bat / STOP_NEXUS.bat
```

## Development and validation

Python 3.11+; tested here with Python 3.12 on Linux. Use the existing project folder; a separate Git worktree is unnecessary.

```
python -m venv .venv
# Windows: .venv\Scripts\python ; Linux: .venv/bin/python
.venv/bin/python -m pip install -r requirements.txt
NEXUS_DATA_DIR=/workspace/nexus-runtime .venv/bin/python run.py --no-browser
.venv/bin/python -m pytest -q
```

On Windows run `.venv\Scripts\python run.py` without the Linux environment assignment. Browser layout tests and screenshots are documented in `docs/TEST_REPORT.md`.

Performance targets on the baseline i3 / 4 GB Windows 11 machine: backend startup under 3 seconds, backend idle RSS under 120 MB, backend average idle CPU below 2%, local dashboard interactions under 200 ms excluding network/AI calls. Browser memory is additional. Actual baseline hardware measurements remain pending; cloud measurements are not equivalent.

See `docs/USER_GUIDE_ROMAN_URDU.md`, `docs/TROUBLESHOOTING.md`, and `PROGRESS.md`.
