# ShivAI - AGI Assistant

ShivAI is an India's First Offline Autonomous General Intelligence Assistant. It is designed to be a completely offline, expert-level assistant capable of multi-step workflows, app generation, and Android device control.

## Unique Features

- **Offline AGI**: No LLM dependency, fully functional offline.
- **Android Control (ADB)**: Control your phone, take screenshots, manage files, and automate apps.
- **App Builder**: Automatically generates code for simple apps (Todo, Calculator, Notes) from templates.
- **Workflow Automation**: Execute complex multi-step workflows (e.g., Morning Routine, Backup).
- **Expert Tasks**: Perform advanced operations like creating project structures, database creation, and system analysis.
- **Bilingual**: Supports Hindi and English.

## Capabilities

- **500+ Commands**: Covering system, file, web, and window management.
- **Context Learning**: Remembers user preferences and learns new command patterns.
- **Productivity**: Pomodoro timer, integrated todo list, quick notes.

## Usage

Interactive REPL (text input by default):

```bash
python shiv_ai_assistant.py
```

Inside the REPL type commands like `help`, `stats`, `what time is it`,
`build todo app`, `run morning workflow`, or `phone battery check`.
Exit with `exit` / `quit`, or press Ctrl+C.

Run a single command non-interactively (repeatable):

```bash
python shiv_ai_assistant.py -c "stats" -c "what time is it"
```

Show all CLI options:

```bash
python shiv_ai_assistant.py --help
```

### Demo mode

Demo mode runs fully offline with no side effects: mic, GUI automation,
phone (ADB), and file-system actions are *simulated*, not executed. Useful
for trying the assistant on a machine without the optional dependencies.

```bash
python shiv_ai_assistant.py --demo
# or via environment variable:
SHIVAI_DEMO=1 python shiv_ai_assistant.py
```

### Environment variables

| Variable      | Effect                                              |
|---------------|-----------------------------------------------------|
| `SHIVAI_DEMO` | Set to `1`/`true`/`yes` to force demo mode.        |

No API key is required: ShivAI is offline by design (no LLM dependency).

### Voice input

```bash
python shiv_ai_assistant.py --voice   # needs the speech_recognition package + a mic
```

Without `--voice` (or when the package is missing) the assistant falls
back to typed input automatically. Spoken output via `pyttsx3` is used
when installed; otherwise responses are printed as text.

## Dependencies

Core (REPL, demo mode, offline knowledge base): **standard library only**.

Optional extras, enabled automatically when installed:

- `pyttsx3` — spoken responses
- `speech_recognition` — microphone input (`--voice`)
- `pyautogui` — GUI/window automation, workflows, screenshots
- `psutil` — system performance analysis
- `pillow`, `opencv-python` — image handling
- `adb` (Android platform tools, on PATH) — phone control

Missing extras degrade gracefully: the assistant prints a hint and keeps
running instead of crashing at import.
