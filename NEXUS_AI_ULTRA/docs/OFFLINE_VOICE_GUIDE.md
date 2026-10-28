# Python offline microphone setup

The former WebView2/browser SpeechRecognition path is removed. `Microphone: network` came from that browser service; NEXUS now captures from the PC microphone in Python and transcribes locally, without a speech API. Speaker output is still the same existing speechSynthesis implementation and voice selector.

## Update an existing Windows installation

1. Close NEXUS. Update this source folder, then double-click **INSTALL_VOICE.bat**. For a fresh install, INSTALL.bat includes these dependencies automatically. Python 3.11/3.12 x64 remains the supported source runtime.
2. Start NEXUS. In **Voice Assistant**, click **Install offline model (~75 MB)** and confirm the one-time public download. It downloads `Systran/faster-whisper-tiny`, the multilingual model, not `tiny.en`. No API key is needed. Downloads use normal TLS and authoritative file checksums, pinned to the actual immutable repository revision resolved at install time.
3. Select **Microphone diagnostics**. Choose the intended input device; device IDs can change after unplugging/reconnecting equipment. Default uses Windows' default input. Enumeration alone does not prove microphone permission.
4. Select **Test input (3 seconds)**, then speak. It reports duration, RMS level in dBFS, peak/clipping, input overflows and whether the signal was silent. No model is needed for this test, and no transcript is created.
5. Select **English** or **Roman Urdu**, and a 5/10/15-second maximum clip. Press **Start microphone**, wait for **Listening**, and speak. **Stop & transcribe** ends capture early. At the maximum duration, capture ends automatically.
6. The editable transcript appears in AI Chat. Review/correct it and press **Send** yourself. No voice request automatically submits chat or authorizes a desktop action.

**Cancel voice** discards the active worker. Emergency Stop and application shutdown also terminate the owned voice worker and release the device. No continuous/background wake-word listening is added. Ordinary idle startup does not load an STT model or open a microphone.

If you use the portable EXE, run **BUILD_WINDOWS.bat** on Windows to include the voice dependencies and PortAudio/ONNX/uroman resources, then distribute the complete new dist\NEXUS_AI_ULTRA folder. Install the offline model once inside the running application; it is stored separately from the executable. Existing database/API credentials are not moved or erased.

## English and Roman Urdu

Whisper tiny multilingual recognizes English and Urdu (`en`, `ur`; automatic detection is also available). Roman Urdu is a Latin writing style, not a separate acoustic language. Urdu-script output is converted to Latin characters with the offline uroman library. Original script is retained in the temporary voice result for diagnostics; the editable chat input defaults to the Latin text.

**Roman spelling is approximate**, not a promise of natural standardized Roman Urdu. Urdu vowels, names, code-switching, short clips, accents and noise can be inaccurate, especially with the deliberately small model. Choose the language explicitly and correct the transcript before sending. Existing AI chat can still converse in English/Roman Urdu through your configured provider; it is not used for STT or romanization.

## Offline behavior, storage and memory

- Internet is needed for package installation and one model download only. Recording, resampling, VAD, recognition and transliteration call no remote speech service. Recognition uses the verified local model and local_files_only=True; no automatic model fallback/download happens during capture.
- Audio stays in the worker's RAM, including native-sample-rate resampling with PyAV; no WAV recording is written or uploaded. Transcripts are not saved to chat until you press Send. Temporary result state remains in RAM until another operation/restart.
- Model location: `%USERPROFILE%\.nexus_ai_ultra\voice-models\tiny` (or NEXUS_DATA_DIR). `verified.json` stores the exact revision and file hashes. Checksums are rechecked before capture. Corrupt/missing model files are rejected.
- The model loads only inside one short-lived process. It uses CPU INT8, at most two CPU threads, one worker, greedy decoding and clips bounded to 15 seconds. The process exits after the operation, releasing model/native-library memory. Cancellation can terminate an in-progress inference without killing other apps.
- There is no CUDA/GPU requirement, extra LLM, idle microphone stream or permanently loaded recognizer. Actual Windows STT memory/latency/accuracy on the 4 GB laptop remains unmeasured; backend-only cloud idle RSS was about 44 MB. WebView2 and the temporary STT worker use additional memory.

## Troubleshooting

- **No devices / cannot open input:** Windows Settings → Privacy & security → Microphone → enable Microphone access and **Let desktop apps access your microphone**. Also check Windows Sound → Input, physical mute, headset selection and another app holding the device exclusively. Python capture does not use the WebView2 browser permission prompt.
- **No signal:** run Test input while speaking. Select another microphone; raise Windows input gain. A successful device listing is not proof that audio was captured.
- **Clipping / overflows:** lower input gain, close heavy workloads, or select another device/host API. Capture uses the microphone's native default rate and resamples locally for STT.
- **Dependencies/DLL error:** rerun INSTALL_VOICE.bat with supported 64-bit Python. The Windows sounddevice wheel includes PortAudio DLLs. CTranslate2/ONNX may require Microsoft's Visual C++ Redistributable x64: https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist . No TLS or DLL verification should be disabled.
- **Model download fails:** allow `huggingface.co` and its Hugging Face/Xet artifact destinations (`cas-bridge.xethub.hf.co`, `cas-server.xethub.hf.co`, `transfer.xethub.hf.co`, `cdn-lfs.huggingface.co`, `cdn-lfs-us-1.hf.co`) on your network as needed. No Hugging Face token is required for this public model. Do not paste keys into chat. Package install uses pypi.org/files.pythonhosted.org.
- **Checksum failure:** no unverified model is used. Retry after fixing connectivity. If the active model folder is corrupt, close voice operations, rename/remove only voice-models\tiny, then reinstall; leave nexus.sqlite3 and credentials alone.
- **Slow transcription:** tiny is deliberately CPU-friendly; keep clips short and select the language explicitly. No Windows latency guarantee is claimed without testing the hardware. A stuck voice job has a timeout and can be cancelled.
- **Speaker issue:** voice output remains the existing WebView2 speechSynthesis path. It is separate from Python STT; choose an allowed installed speaker voice and check volume.

The Linux cloud lacks PortAudio and a physical microphone, and its egress policy blocks the model host. Do not treat the automated audio/model test doubles as a successful live Windows microphone or real-model accuracy test. See VOICE_TEST_REPORT.md.
