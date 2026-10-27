# Troubleshooting

- **Python launcher missing:** install current Python 3.11+ x64 with the launcher. `INSTALL.bat` uses `py -3`.
- **Dependency install fails:** inspect the exact pip error. Check Internet access to pypi.org and files.pythonhosted.org; do not disable TLS verification. Re-run INSTALL after fixing connectivity.
- **Port 8765 occupied:** stop your existing NEXUS console first. The launcher refuses to replace another instance. Do not kill unrelated processes.
- **Dashboard has no provider:** install/run your local provider or configure a hosted provider in Settings. The app does not install a model automatically.
- **Connection refused at 31415/3847/11434:** that server is not running on this computer or the port differs. A cloud machine's localhost is not your Windows PC.
- **HTTP 401/403:** check key, provider account permissions and base URL. Keys go into the app's password field or secure environment configuration, never chat.
- **HTTP 404:** API path or model may be wrong. Use the provider's documented OpenAI-compatible base URL.
- **Model test works but chat fails:** `/models` access does not prove the selected model supports chat or function calling. Use a supported model. No automatic fake fallback exists.
- **429:** provider quota/rate limit; NEXUS waits at least 60 seconds before retrying that provider. Check quota, then retry manually.
- **Secure credential storage unavailable:** Windows should use the OS vault. Linux headless environments may lack a keyring. Configure the provider-specific environment variable securely or use the app on Windows; no plaintext fallback is created.
- **Key remains after changing fields:** blank key preserves the existing credential. Rotate in Settings with a new key; remove it using Windows Credential Manager when required.
- **File tool denied:** add an existing folder you trust under Settings. Paths resolve against approved roots; escaping symlinks are rejected. Existing destination files are never overwritten.
- **Approval gone:** approvals expire after five minutes, on use, on restart or on Emergency Stop. Submit the action again and review it.
- **Microphone unsupported:** use Microsoft Edge/Chrome, allow microphone access and check Windows privacy settings. Browser recognition may require Internet and a speech service. No wake-word recorder runs.
- **No speaker:** install an allowed Windows voice, choose it in Voice Assistant, check output volume. Asad/Uzma are excluded.
- **Screenshot unsupported:** Windows desktop plus optional Pillow package are required. Select a new PNG path in an approved folder.
- **Reminder did not notify while app was closed:** this is an in-process scheduler, not a Windows background service. Overdue notifications arrive after restart.
- **Browser or WhatsApp draft did not open:** the tool reports the browser request result; a headless cloud host cannot open your personal browser. On Windows review the browser selection and URL.
- **Disk/RAM numbers differ from Task Manager:** sampling time and OS accounting can differ. Values come directly from psutil. No promised RAM reduction is applied.

Data lives in the per-user `.nexus_ai_ultra` directory. Stop the app before backing up or resetting SQLite. Deleting it permanently removes local history and reminders; the Windows credential vault is separate.
