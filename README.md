# JARVIS

A local voice assistant for Windows that runs entirely on your own computer. There are no cloud APIs, external subscriptions, or third-party tracking. It listens to your microphone, transcribes your speech locally, figures out what you want using a local language model, runs system commands or tools, and speaks the answer back to you in Polish.

---

## How It Works

1. **Listening**: Captures audio from your microphone and monitors sound levels. When you finish speaking, it automatically detects silence and finishes recording.
2. **Transcription**: Converts the recorded audio to text using a locally compiled `whisper.cpp` engine.
3. **Reasoning and Function Calling**: Passes your words to Ollama running `llama3.1`. The model maintains conversation history and either answers directly or triggers a specific Python tool.
4. **Tool Execution**: Runs system tasks like launching or closing applications, searching the web, checking the time or date, and gathering basic system information.
5. **Speech Synthesis**: Streams the reply through Piper TTS directly in memory and plays it through your speakers.

---

## Project Structure

```text
jarvis/
├── config.py         Central configuration (thresholds, models, paths, prompts)
├── audio.py          Microphone capture and voice activity detection (VAD)
├── transcriber.py    Speech-to-text wrapper using whisper.cpp
├── tts.py            Text-to-speech using Piper and sounddevice
├── registry.py       Tool registration decorator and Ollama tool schema builder
├── tools.py          Executable system and conversational tools
├── actions.py        Ollama integration, history management, and tool routing
├── main.py           Main application loop and voice interaction flow
├── requirements.txt  Python package dependencies
├── models/           Whisper and Piper model files (ignored in git)
└── piper/            Piper executable and runtime libraries (ignored in git)
```

---

## Prerequisites

- Windows 10 or 11 (64-bit)
- Python 3.10 or newer
- [Ollama](https://ollama.com) installed and running
- C++ compiler (MinGW-w64 or Visual Studio Build Tools) and CMake (to build whisper.cpp)
- `curl` and PowerShell (standard on modern Windows)

---

## Setup Guide

### 1. Clone the repository

```powershell
git clone https://github.com/napewnoniefixu/jarvis.git
cd jarvis
```

### 2. Set up a Python virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Build whisper.cpp

Compile the C++ transcription binary:

```powershell
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
cmake -B build -G "MinGW Makefiles"
cmake --build build --config Release
cd ..
```

This produces `whisper.cpp/build/bin/whisper-cli.exe`.

### 4. Download Piper TTS

Download the standalone Piper release for Windows and extract it into a `piper` directory:

```powershell
curl.exe -L "https://github.com/rhasspy/piper/releases/latest/download/piper_windows_amd64.zip" -o "piper_windows.zip"
Expand-Archive -Path "piper_windows.zip" -DestinationPath "."
Remove-Item "piper_windows.zip"
```

The executable will be located at `piper/piper.exe`.

### 5. Download Model Files

Create the `models` folder and download the Whisper GGML model and Piper voice files:

```powershell
if (!(Test-Path -Path "models")) { New-Item -ItemType Directory -Path "models" }

# Whisper base model (~140 MB)
curl.exe -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin" -o "models/ggml-base.bin"

# Piper Polish voice model (bass-high, ~114 MB + JSON config)
curl.exe -L "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/bass/high/pl_PL-bass-high.onnx" -o "models/pl_PL-bass-high.onnx"
curl.exe -L "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/bass/high/pl_PL-bass-high.onnx.json" -o "models/pl_PL-bass-high.onnx.json"
```

### 6. Pull the Llama 3.1 Model in Ollama

Make sure Ollama is running, then pull the model:

```powershell
ollama pull llama3.1
```

---

## Running the Assistant

### Test Text-to-Speech

Before running the full loop, verify that audio output and Piper work properly:

```powershell
python tts.py
```

You should hear a confirmation phrase through your speakers.

### Start JARVIS

Launch the assistant loop:

```powershell
python main.py
```

1. JARVIS will greet you: *"Witam szefie, co robimy?"*
2. The console will display `Słucham...` indicating the microphone is active.
3. Speak your command in Polish (e.g. *"która jest godzina"*, *"włącz kalkulator"*, *"znajdź przepis na sernik"*).
4. When you stop speaking, JARVIS detects the pause, transcribes your speech, decides what to do, and replies out loud.

### Stopping the Assistant

You can stop the assistant anytime by:
- Saying one of the exit phrases: *"wyłącz się"*, *"do widzenia"*, *"koniec"*, *"dobranoc"*, or *"nara"*.
- Pressing `Ctrl + C` in the console window.

---

## Available Tools

JARVIS includes several built-in tools in `tools.py`:

- **open_app**: Launches programs by name (e.g. notepad, calc, mspaint, explorer, steam).
- **close_app**: Terminates a process using Windows taskkill.
- **get_time**: Returns the current time formatted in Polish.
- **get_date**: Returns today's date and day of the week in Polish.
- **search_web**: Runs a Google search in your default web browser.
- **open_website**: Opens a specific URL in your default browser.
- **system_command**: Runs safe, read-only system diagnostic utilities (`systeminfo`, `ipconfig`, `hostname`, `whoami`, `tasklist`).
- **zwykla_odpowiedz**: Handles general conversation, greetings, humor, and casual questions.

---

## Adding Custom Tools

You can add new actions to `tools.py` using the `@tool` decorator from `registry.py`. The function is automatically converted into an Ollama-compatible schema on startup.

### Simple Tool (No Parameters)

```python
from registry import tool
import subprocess

@tool(
    name="open_task_manager",
    description="Otwiera Menedżer Zadań Windows. Użyj, gdy użytkownik prosi o menedżer zadań lub procesy."
)
def open_task_manager() -> str:
    """Launch Windows Task Manager."""
    subprocess.Popen(["taskmgr.exe"])
    return "Menedżer zadań został otwarty."
```

### Parameterized Tool (With JSON Schema)

```python
from registry import tool
import webbrowser

@tool(
    name="play_youtube_search",
    description="Wyszukuje film na YouTube i otwiera wyniki w przeglądarce.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Czego użytkownik szuka na YouTube."
            }
        },
        "required": ["query"]
    }
)
def play_youtube_search(query: str) -> str:
    """Search YouTube and open results in the browser."""
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return f"Szukam {query} na YouTube."
```

---

## Configuration

All runtime settings are located in `config.py`. You can adjust:

- **Microphone and VAD**: `VAD_THRESHOLD` (energy threshold for speech), `SILENCE_LIMIT_FRAMES` (silence duration before stopping), `MAX_INITIAL_SILENCE_FRAMES` (timeout if no speech is heard).
- **Speech Recognition**: `WHISPER_LANGUAGE`, `WHISPER_THREADS`.
- **Speech Synthesis**: `TTS_VOLUME` (default volume scale 0.0 to 1.0), `TTS_LENGTH_SCALE` (speaking rate), `TTS_MODEL_PATH` (change voice models).
- **LLM Settings**: `LLM_MODEL` (e.g. `llama3.1`), `LLM_SYSTEM_PROMPT` (persona and response style), `MAX_HISTORY_MESSAGES` (number of conversational turns to remember).
