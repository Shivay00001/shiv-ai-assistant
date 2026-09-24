# ShivAI Assistant

**Desktop app** — command-line personal AI assistant (offline, no API key needed). Boots a text REPL by default; voice mode (mic + TTS) is optional and needs audio hardware.

## Run

```bash
python shiv_ai_assistant.py                 # interactive REPL (text input by default)
python shiv_ai_assistant.py --demo          # demo mode: all device/GUI actions simulated, nothing executed
python shiv_ai_assistant.py -c "help"       # run one command non-interactively
python shiv_ai_assistant.py --voice         # microphone input (needs `speech_recognition` + mic hardware)
```

## Optional deps

Core works on stdlib only. Install extras for full features:
`pip install pyautogui SpeechRecognition pyttsx3 keyboard pyperclip opencv-python pillow psutil`

Missing deps degrade gracefully — the assistant starts and tells you what is unavailable.

## Notes

- Mic/speaker paths cannot be verified on headless/server machines; they need a real desktop with audio hardware. Demo and text modes are verified working.
- GUI/desktop automation features (window control, screenshots, Android ADB) only work on a real desktop OS.
