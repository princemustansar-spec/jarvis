# JARVIS-style voice upgrade — 29 October 2026

## Inspected source, not assumptions

Reference repository `princemustansar-spec/JARVIS-ULTRA-V67` at commit `45648afc5b4593093d0b20a5562da2f60a25eb3b`:

- `jarvis_v67_web_gui.py:1752`: SpeechRecognition `Recognizer`, PyAudio-backed `Microphone`, 0.5-second ambient calibration, one-second start-wait slices up to 15 seconds, eight-second phrase limit, `recognize_google(audio, language="en-IN")`, explicit `voice_stop`. It handles UnknownValueError and RequestError. This is code inspection, not proof that it recognizes accurately on this laptop.
- `jarvis_v67_tts.py`: Edge `en-IN-PrabhatNeural`, rate `-5%`, 280-character chunks, pygame playback, cancel event and Windows System.Speech/SAPI fallback. It also includes an optional paid Gemini voice and a local `.env` key reader; neither was copied.
- `jarvis_next5_pack.py:147`: basic pyttsx3 speech fallback. No requirements manifest was found; dependencies were verified from actual imports.

NEXUS retains its existing sounddevice/PortAudio capture instead of adding a second PyAudio capture stack. It uses the same SpeechRecognition Google API, starting with en-IN, with an explicit HTTPS endpoint and six-second network timeout. Native-rate PCM is downsampled to 16 kHz before upload. This is Python Google recognition, not the former unreliable WebView2 browser SpeechRecognition.

## Using it

1. Update source/dependencies using `install_update.ps1` (below). Close NEXUS first. Launch START_UPDATED_NEXUS.bat or the updated desktop shortcut so an old portable EXE is not accidentally launched.
2. In Voice Assistant choose **Google online + offline fallback**, locale **en-IN**, and **Roman Urdu** output. Alternatives are ur-PK, hi-IN, en-US and en-GB; compare on your microphone rather than assuming a locale is superior.
3. Start microphone, stay quiet during the half-second calibration, then speak after Listening appears. The phrase finishes after the selected silence gap (default 0.8 s), or Stop ends it manually. Default maximum phrase is 8 s; speech-start timeout defaults to 5 s. Both are configurable. No always-listening mode was added.
4. Review/edit the transcript, then Send through the existing AI Brain. PC actions still use existing approvals. No automatic chat submission is introduced.
5. Enable **Speak AI responses**. For the natural JARVIS-style voice also enable **Allow Edge neural voice**; reply text goes to Microsoft. Otherwise use an installed Windows SAPI voice. Asad/Uzma are excluded from both native and existing browser fallback voice choices. The existing speaker selector is applied to Windows fallback where a matching voice is available.

Google mode sends the explicitly started audio clip to Google. Edge mode sends reply text to Microsoft. Do not use these online modes for confidential speech without accepting that behavior. Offline-only mode keeps audio local. No provider keys or raw recordings are saved to source or logs. SpeechRecognition's legacy Google endpoint uses its library's generic testing access, which may be limited/revoked; it is not a guaranteed production service or an accuracy guarantee.

## Fallback and resource limits

Google has one recognition attempt per utterance, without cascading language retries. On network/unintelligible failure, the same captured clip is passed to the existing verified faster-whisper tiny model if installed. Otherwise the UI explains what is missing. Offline-only selection remains available. Install the offline model once using the existing button if you want fallback.

One recent capture worker is reused for up to 45 idle seconds; its microphone is closed between explicit requests. If Whisper was needed its CPU INT8 model is cached in that worker to avoid per-utterance reloads, then released when the worker expires, is cancelled, muted, or the app closes. At most two Whisper CPU threads, one worker and bounded clips remain in force. Google success does not load/hash the offline model. Edge/Windows output uses a separate on-demand worker, small chunks and in-memory MP3 data. No Gemini, GPU, bundled model, always-recording loop or arbitrary spoken shell commands were added.

Mute microphone & speaker blocks new captures/output and cancels current operations. Emergency Stop also cancels both. Text chat, SQLite, tasks, providers, approvals, dashboard HTML/CSS and other tools remain in place.

## Safe PowerShell install/update/rollback

`install_update.ps1` accepts `-Revision <commit>` and optional `-Destination <existing folder>`. Without a destination it checks the current project folder, C:\NEXUS_AI_ULTRA and %USERPROFILE%\NEXUS_AI_ULTRA; multiple installations require an explicit destination. It refuses to update a running NEXUS rather than killing unrelated processes.

It downloads GitHub source over verified HTTPS, rejects unsafe archive paths, creates a private sibling backup of the complete existing folder including .venv, overlays source without deleting unknown files, excludes env/SQLite/models/runtime files, installs dependencies only into .venv, checks dependencies and syntax, and updates the desktop shortcut to the new source launcher. It does not touch the external NEXUS_DATA_DIR or Windows credential vault. No machine execution-policy setting is changed; a copy-paste launcher can use a process-only policy after verifying the downloaded script's SHA-256.

The printed backup receipt supports:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install_update.ps1 -Destination 'C:\NEXUS_AI_ULTRA' -Rollback -BackupPath 'C:\NEXUS_AI_ULTRA.backup-<printed-id>'
```

Rollback restores old code and .venv while carrying current nonmanaged/user files (including SQLite/env files) forward; the replaced updated folder is retained as `.before-rollback-*`. A failed update restores the previous installation automatically and retains failed output for inspection. Do not remove backups until laptop acceptance passes. Copying a complete venv needs free disk space; failure to secure/copy a backup aborts before changes. Portable EXEs are preserved, not silently overwritten; BUILD_WINDOWS.bat can package this source separately after acceptance.

## Verification and limits

- 67 Python tests passed in Linux: existing APIs/tools/storage/desktop tests plus Google en-IN/HTTPS request contract, silence/onset detection, same-clip offline fallback, no Whisper load on Google success, warm-model reuse, Edge→Windows fallback, no online TTS without opt-in and banned-voice rejection.
- Existing three browser suites passed: auto-fit at 1366×768 and 1920×1080 plus smaller sizes, navigation, memory, real system tools, approvals, Python mic transport, editable transcript and no auto-send. New Google preference/consent payload assertions are included.
- Official PowerShell 7.5.4 was checksum-verified, used to parse the updater, and run a real rollback filesystem test. Process detection was mocked; old code restored and latest SQLite/env fixture data survived. Full Windows robocopy/ACL/pip installation is not claimed tested on Linux.
- Actual Google en-IN HTTPS probe with synthetic silence returned RequestError in the cloud. Actual Edge connection returned ClientConnectorDNSError. See jarvis-voice-network-probe.json. Neither is a real microphone/recognition test.
- Windows GitHub Actions checks are configured on the feature branch/PR; inspect their actual outcome before merging. They test contracts and rollback, not a physical microphone.

**Still required on your Windows laptop:** actual input device/permissions, latency and accuracy of en-IN versus alternatives for mixed speech, real Edge/SAPI playback, offline fallback with your model, full updater/automatic-restore behavior, and process-tree RAM on the i3-1115G4/4 GB system. No speech accuracy, live microphone success or measured Windows speed/RAM improvement is claimed from fixtures.

Short test: say **“NEXUS, mera CPU aur RAM check karo.”** Review the transcript; with Speak AI responses enabled, Send and verify a reply from the existing configured AI provider. Check Stop/Mute. Then disconnect Internet to verify the installed offline fallback separately.
