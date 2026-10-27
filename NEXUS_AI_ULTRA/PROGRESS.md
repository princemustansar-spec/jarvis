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
