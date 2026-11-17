# JARVIS

JARVIS is a private, local voice assistant for Windows. It runs entirely on your host machine without relying on external cloud APIs, paid subscriptions, or remote data transmission.

The assistant combines offline keyword spotting (`openWakeWord`), speech recognition (`whisper.cpp`), local language model reasoning with function calling (`Ollama` running `llama3.1`), and in-memory neural speech synthesis (`Piper TTS`).

---

## Contents

- [Architecture and Execution Flow](#architecture-and-execution-flow)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Running the Assistant](#running-the-assistant)
- [Available Tools](#available-tools)
- [Configuration Reference](#configuration-reference)
- [Repositories and Sources](#repositories-and-sources)

---

## Architecture and Execution Flow

JARVIS operates as a two-tier state machine to balance responsiveness with minimal idle resource consumption:

### 1. Standby State (Passive Listening)
- The assistant initializes in a passive listening mode managed by `wakeword.py`.
- Audio is read in small 80 ms chunks (1280 samples at 16 kHz, 16-bit PCM) via `sounddevice` and evaluated against an openWakeWord model (`jarvis_v2.tflite`).
- While in standby, CPU overhead remains minimal. Execution blocks until detection confidence exceeds `WAKEWORD_THRESHOLD` (default: `0.7`).

### 2. Active Session State (Interactive Dialogue)
Once the wake word is detected, JARVIS acknowledges activation (*"Słucham, szefie?"*) and enters an active dialogue loop:
1. **Voice Activity Detection (VAD)**: `audio.py` monitors microphone input and tracks Root Mean Square (RMS) energy. Recording terminates automatically after trailing silence (~800 ms) or after a 5-second timeout if no speech occurs.
2. **Speech Recognition (ASR)**: The captured audio is passed to `transcriber.py`, which invokes a locally compiled `whisper.cpp` (`whisper-cli.exe`) binary running the GGML `base` model.
3. **Session Timeout Check**: If no speech was transcribed (for example, the user walked away), JARVIS says *"Żegnam"* and drops back to the passive standby state.
4. **Intent Interpretation & Function Calling**: `actions.py` submits the transcribed query along with recent conversation history and registered tool schemas to `Ollama`. The model decides whether to invoke an OS tool or respond conversationally.
5. **Speech Synthesis (TTS)**: The output text is synthesized via `tts.py` using `piper.exe` and the Polish `pl_PL-bass-high` voice model. Raw 16-bit PCM samples are read directly from stdout into a NumPy buffer, scaled for volume, and played synchronously through `sounddevice` without intermediate disk I/O.
6. **Graceful Termination**: Saying a shutdown phrase (such as *"wyłącz się"*, *"do widzenia"*, or *"koniec"*) or pressing `Ctrl + C` terminates the assistant cleanly.

---

## Project Structure

```text
jarvis/
├── config.py         Central configuration parameters, thresholds, paths, and prompts
├── wakeword.py       Low-overhead wake word detection using openWakeWord
├── audio.py          Microphone capture, RMS energy analysis, and VAD recording
├── transcriber.py    Speech-to-text wrapper calling whisper.cpp CLI
├── tts.py            In-memory neural text-to-speech using Piper and sounddevice
├── registry.py       Tool registration decorator and Ollama JSON Schema builder
├── tools.py          Executable system and conversational tools
├── actions.py        Ollama integration, multi-turn history, and tool dispatch
├── main.py           Application entry point and two-tier orchestration loop
├── requirements.txt  Python dependencies
├── models/           Local model weights (git-ignored)
│   ├── jarvis_v2.tflite           Wake word model
│   ├── ggml-base.bin              Whisper ASR model
│   ├── pl_PL-bass-high.onnx       Piper TTS voice model
│   └── pl_PL-bass-high.onnx.json  Piper voice configuration
└── piper/            Standalone Piper Windows binary and dependencies (git-ignored)
    └── piper.exe
```

---

## Prerequisites

- **Operating System**: Windows 10 or 11 (64-bit)
- **Python**: 3.10 or newer
- **Ollama**: Installed and running locally
- **C++ Build Environment**: MinGW-w64 or Visual Studio C++ Build Tools with CMake (for compiling `whisper.cpp`)
- **System Utilities**: `curl`, `git`, and PowerShell

---

## Installation and Setup

### 1. Clone the Repository

```powershell
git clone https://github.com/napewnoniefixu/jarvis.git
cd jarvis
```

### 2. Set Up Python Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Build whisper.cpp

Compile the native C++ transcription engine:

```powershell
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
cmake -B build -G "MinGW Makefiles"
cmake --build build --config Release
cd ..
```

The compiled binary will be placed at `whisper.cpp/build/bin/whisper-cli.exe`.

### 4. Download Piper TTS

Download the standalone Piper release for Windows and extract it to the project root:

```powershell
curl.exe -L "https://github.com/rhasspy/piper/releases/latest/download/piper_windows_amd64.zip" -o "piper_windows.zip"
Expand-Archive -Path "piper_windows.zip" -DestinationPath "."
Remove-Item "piper_windows.zip"
```

The executable will be located at `piper/piper.exe`.

### 5. Download Model Weights

Create the `models/` folder and download the required models:

```powershell
if (!(Test-Path -Path "models")) { New-Item -ItemType Directory -Path "models" }

# 1. Wake Word model (jarvis_v2 from fwartner/home-assistant-wakewords-collection)
curl.exe -L "https://raw.githubusercontent.com/fwartner/home-assistant-wakewords-collection/main/en/jarvis_v2.tflite" -o "models/jarvis_v2.tflite"

# 2. Whisper ASR model (GGML base, ~140 MB)
curl.exe -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin" -o "models/ggml-base.bin"

# 3. Piper TTS Polish voice model (bass-high, ~114 MB + JSON config)
curl.exe -L "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/bass/high/pl_PL-bass-high.onnx" -o "models/pl_PL-bass-high.onnx"
curl.exe -L "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/bass/high/pl_PL-bass-high.onnx.json" -o "models/pl_PL-bass-high.onnx.json"
```

### 6. Pull the Language Model

Ensure Ollama is running in the background, then pull the target model:

```powershell
ollama pull llama3.1
```

---

## Running the Assistant

### Test Individual Subsystems

Verify text-to-speech output:
```powershell
python tts.py
```

Verify wake word detection:
```powershell
python wakeword.py
```
Say *"Jarvis"* into your microphone. The script prints a confirmation when confidence crosses the threshold.

### Start the Assistant

Run the main orchestration script:
```powershell
python main.py
```

1. JARVIS confirms initialization: *"System aktywny - czekam na wezwanie"*.
2. The assistant enters standby mode. Say *"Jarvis"*.
3. JARVIS acknowledges with *"Słucham, szefie?"* and begins listening for commands.
4. Speak a command in Polish (such as *"otwórz notatnik"*, *"która godzina"*, or *"wyszukaj wiadomości w google"*).
5. The session remains open for follow-up dialogue until silence causes a timeout (*"Żegnam"*, returning to standby) or an explicit shutdown command is received.

### Stopping the Assistant

- Voice command: Say *"wyłącz się"*, *"do widzenia"*, *"koniec"*, *"dobranoc"*, or *"nara"*.
- Keyboard: Press `Ctrl + C` in the console window.

---

## Available Tools

Tools are defined in `tools.py` and registered via the `@tool` decorator:

| Tool Name | Parameters | Description |
|---|---|---|
| `open_app` | `app_name: str` | Launches Windows applications (e.g., `notepad.exe`, `calc.exe`, `mspaint.exe`, `explorer.exe`). Validates input to block path traversal. |
| `close_app` | `process_name: str` | Terminates running processes using Windows `taskkill /im <process_name> /f`. |
| `get_time` | None | Returns the current time formatted in Polish. |
| `get_date` | None | Returns today's date and day of the week in Polish. |
| `search_web` | `query: str` | Opens a Google search in the system default web browser. |
| `open_website` | `url: str` | Opens a given web URL in the default browser (automatically adds `https://` if omitted). |
| `system_command` | `command: str` | Executes safe, read-only diagnostic utilities (`systeminfo`, `ipconfig`, `hostname`, `whoami`, `tasklist`). Output is truncated to 500 characters. |
| `normal_response` | `text_for_user: str` | Handles casual conversation, greetings, humor, and general questions. |

### Adding Custom Tools

New tools can be registered by adding decorated functions to `tools.py`:

```python
from registry import tool
import subprocess

@tool(
    name="open_task_manager",
    description="Otwiera Menedżer Zadań Windows. Użyj, gdy użytkownik prosi o menedżer zadań lub listę procesów."
)
def open_task_manager() -> str:
    """Launch Windows Task Manager."""
    subprocess.Popen(["taskmgr.exe"])
    return "Menedżer zadań został otwarty."
```

Functions decorated with `@tool` are dynamically exposed as JSON Schemas to Ollama and executed when selected by the model.

---

## Configuration Reference

All runtime constants are centralized in `config.py`:

- **Wake Word (`openWakeWord`)**:
  - `WAKEWORD_MODEL`: Name or path of the target model (`jarvis_v2.tflite`).
  - `WAKEWORD_THRESHOLD`: Detection confidence cutoff (`0.7`).
  - `WAKEWORD_CHUNK_SIZE`: Number of audio frames per prediction step (`1280` samples = 80 ms).
  - `WAKEWORD_SAMPLE_RATE`: Required input sample rate (`16000` Hz).
- **Audio Capture & VAD**:
  - `SAMPLE_RATE`: Audio capture rate (`16000` Hz).
  - `BLOCKSIZE`: Input buffer size (`1600` samples = 100 ms).
  - `VAD_THRESHOLD`: RMS power threshold for distinguishing speech from silence (`0.003`).
  - `SILENCE_LIMIT_FRAMES`: Consecutive silent frames before speech cut-off (`8` frames ≈ 800 ms).
  - `MAX_INITIAL_SILENCE_FRAMES`: Silence timeout before aborting recording (`50` frames ≈ 5 s).
- **Speech Recognition (`whisper.cpp`)**:
  - `WHISPER_CLI_PATH`: Path to the compiled `whisper-cli.exe`.
  - `WHISPER_MODEL_PATH`: Path to the GGML model weights (`ggml-base.bin`).
  - `WHISPER_LANGUAGE`: Language code (`pl`).
  - `WHISPER_THREADS`: CPU worker threads allocated for inference (`8`).
- **Speech Synthesis (`Piper`)**:
  - `PIPER_EXE_PATH`: Path to `piper.exe`.
  - `TTS_MODEL_PATH`: Path to the ONNX voice model (`pl_PL-bass-high.onnx`).
  - `TTS_SAMPLE_RATE`: Output audio rate (`22050` Hz).
  - `TTS_VOLUME`: Software volume scaling factor (`0.3`).
  - `TTS_LENGTH_SCALE`: Speech duration/rate factor (`0.85`).
- **Language Model (`Ollama`)**:
  - `LLM_MODEL`: Ollama model identifier (`llama3.1`).
  - `LLM_SYSTEM_PROMPT`: Assistant persona and concise response guidelines.
  - `MAX_HISTORY_MESSAGES`: Upper limit on retained conversation turns (`20`).

---

## Repositories and Sources

JARVIS builds upon the following open-source projects, models, and collections:

- **Wake Word Model (`jarvis_v2.tflite`)**: [fwartner/home-assistant-wakewords-collection](https://github.com/fwartner/home-assistant-wakewords-collection) — Community wake word models for Home Assistant and openWakeWord.
- **Wake Word Detection Engine**: [dscripka/openWakeWord](https://github.com/dscripka/openWakeWord) — Lightweight, offline wake word and keyword spotting engine.
- **Speech Recognition Engine**: [ggerganov/whisper.cpp](https://github.com/ggerganov/whisper.cpp) — High-performance C/C++ port of OpenAI's Whisper model.
- **Whisper GGML Model Weights**: [ggerganov/whisper.cpp on Hugging Face](https://huggingface.co/ggerganov/whisper.cpp) — Pre-quantized models for `whisper.cpp` (`ggml-base.bin`).
- **Text-to-Speech Engine**: [rhasspy/piper](https://github.com/rhasspy/piper) — Fast, local neural text-to-speech engine.
- **Piper Voice Weights**: [rhasspy/piper-voices on Hugging Face](https://huggingface.co/rhasspy/piper-voices) — Trained ONNX voice models for Polish (`pl_PL-bass-high`, `pl_PL-darkman-medium`).
- **Local Language Model Runner**: [ollama/ollama](https://github.com/ollama/ollama) — Local model server powering conversational context and function calling with `llama3.1`.
- **Audio Capture and Playback**: [sounddevice](https://github.com/spatialaudio/python-sounddevice) and [NumPy](https://github.com/numpy/numpy) — PortAudio bindings and array operations for real-time PCM streaming.
