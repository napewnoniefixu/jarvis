# JARVIS — Local Intelligent Voice Assistant

[![Platform](https://img.shields.io/badge/Platform-Windows%2011-blue?logo=windows)](https://microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Whisper.cpp](https://img.shields.io/badge/ASR-whisper.cpp%20(C%2B%2B)-green)](https://github.com/ggerganov/whisper.cpp)
[![Piper TTS](https://img.shields.io/badge/TTS-Piper%20(In--Memory%20Streaming)-orange)](https://github.com/rhasspy/piper)
[![Ollama](https://img.shields.io/badge/LLM-Ollama%20(Llama%203.1)-purple)](https://ollama.com)

A private, real-time voice assistant running 100% locally on Windows 11. JARVIS combines high-performance native engines with the flexibility of Python: speech transcription via compiled `whisper.cpp` (C++), cognitive reasoning and function-calling via `Ollama` (`llama3.1`), and neural speech synthesis via standalone `Piper TTS` streaming raw PCM audio directly in-memory without disk overhead.

---

## 🚀 Architecture & Core Features

```mermaid
flowchart TD
    Mic([🎤 Microphone]) -->|16 kHz Mono PCM| Audio[audio.py: RMS Voice Activity Detection]
    Audio -->|Speech Finalized (~800ms silence)| WAV[(temp_command.wav)]
    WAV --> Transcriber[transcriber.py: whisper.cpp C++ CLI]
    Transcriber -->|Transcribed Polish Text| Actions[actions.py: Ollama Llama 3.1]
    
    Actions -->|Function Call| Registry{registry.py: Tool Router}
    Registry -->|open_notepad| ToolNotepad[tools.py: notepad.exe]
    Registry -->|get_time| ToolTime[tools.py: system clock]
    Registry -->|zwykla_odpowiedz| ToolChat[tools.py: conversational response]
    
    Actions -->|Direct Text / Tool Result| TTS[tts.py: Piper TTS Engine]
    ToolNotepad -->|Confirmation| TTS
    ToolTime -->|Time String| TTS
    ToolChat -->|Spoken Reply| TTS
    
    TTS -->|--output_raw stdout pipe| Buffer[In-Memory NumPy Float32 Buffer]
    Buffer -->|Software Volume Scaling| Playback[sounddevice.play @ 22.05 kHz]
    Playback --> Speaker([🔊 Speakers])
```

- **Audio Capture & VAD (Voice Activity Detection):** Continuous 16 kHz 16-bit mono audio streaming via `sounddevice`. Employs vectorized Root Mean Square (RMS) energy analysis with dynamic thresholding to detect speech onset and automatically cut off recording after ~800 ms of trailing silence (or a ~5.0 s timeout if no speech is detected).
- **Speech Transcription (ASR):** High-speed local Automatic Speech Recognition powered by a locally compiled C++ `whisper.cpp` (`whisper-cli.exe`) binary running the GGML `base` model with multi-threading and non-speech token suppression (`--suppress-nst`).
- **Cognitive Reasoning & Native Function Calling:** Intent classification and dialogue generation powered locally by `Ollama` running `llama3.1`. Employs structured system instructions and native tool-calling schemas to automatically route queries to Python actions or conversational handlers.
- **Extensible Tool Registry & Schema Builder:** Decorator-based registry (`@tool`) supporting arbitrary OpenAI/Ollama-compliant JSON Schema parameters (`registry.py`). Extracts function arguments dynamically and executes functions with `**arguments`.
- **Built-in System & Conversational Tools:**
  - `open_notepad`: Launches the Windows Notepad application as a background subprocess.
  - `get_time`: Queries the system clock and formats the current time in Polish.
  - `zwykla_odpowiedz`: Structured conversational response handler for natural dialogue, greetings, and jokes.
- **Zero-Disk-I/O In-Memory Neural TTS:** Offline neural speech synthesis via standalone `Piper TTS` (`piper.exe`) with the Polish `pl_PL-bass-high` voice model (supports `darkman-medium`). Streams raw 16-bit PCM bytes via standard output (`--output_raw`), converts in-memory into normalized float32 samples in NumPy, applies software volume attenuation, and plays synchronously via `sounddevice` at 22050 Hz without writing temporary WAV files to disk.
- **Conversational Resilience:** Interactive conversational loop with an initial voice greeting (*"Witam szefie, co robimy?"*), console transcription display, and automatic fallback retry prompting (*"Nie dosłyszałem, powtórz proszę."*) before standing down.
- **Strict Code Quality:** Fully typed with PEP 484 type annotations and documented with Google-style docstrings across all modules.

---

## 📁 Project Structure

```text
jarvis/
├── audio.py              # Microphone streaming, vectorized RMS energy analysis, and VAD
├── transcriber.py        # Subprocess wrapper for native whisper.cpp (whisper-cli.exe)
├── tts.py                # In-memory raw PCM streaming Piper neural TTS synthesis & playback
├── registry.py           # Tool decorator and OpenAI/Ollama function-calling schema builder
├── tools.py              # Executable system tools and OS integrations (Notepad, Clock, Chat)
├── actions.py            # Ollama LLM integration, intent routing, and tool invocation
├── main.py               # Core application entry point and conversational orchestration loop
├── models/               # Model weights (Whisper GGML & Piper ONNX) [git-ignored]
│   ├── ggml-base.bin
│   ├── pl_PL-bass-high.onnx
│   └── pl_PL-bass-high.onnx.json
├── piper/                # Standalone Piper Windows binary and dependencies [git-ignored]
│   └── piper.exe
└── whisper.cpp/          # Locally compiled C++ speech recognition engine [git-ignored]
    └── build/bin/whisper-cli.exe
```

---

## 🛠️ System Requirements

- **Operating System:** Windows 11 (64-bit)
- **Python:** 3.10+
- **LLM Engine:** [Ollama](https://ollama.com) with the `llama3.1` model installed
- **C++ Compiler:** MinGW-w64 (GCC/G++) or Visual Studio Build Tools (MSVC)
- **Tools:** CMake, Git, `curl`, PowerShell

---

## 📦 Installation & Setup

### 1. Clone the repository
```powershell
git clone https://github.com/napewnoniefixu/jarvis.git
cd jarvis
```

### 2. Set Up Python Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install sounddevice numpy ollama
```

### 3. Build the C++ Transcription Engine (`whisper.cpp`)
Compile the native `whisper.cpp` engine locally:

```powershell
# Clone the whisper.cpp repository
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp

# Configure and compile using MinGW
cmake -B build -G "MinGW Makefiles"
cmake --build build --config Release

cd ..
```

### 4. Setup Piper TTS Engine
Download and extract the standalone Piper Windows binary release into the `piper/` folder:

```powershell
curl.exe -L "https://github.com/rhasspy/piper/releases/latest/download/piper_windows_amd64.zip" -o "piper_windows.zip"
Expand-Archive -Path "piper_windows.zip" -DestinationPath "."
Remove-Item "piper_windows.zip"
```

### 5. Download Model Weights
All weights are stored in the `models/` directory (excluded from version control):

```powershell
if (!(Test-Path -Path "models")) { New-Item -ItemType Directory -Path "models" }

# Whisper ASR model (~140 MB)
curl.exe -L "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin" -o "models/ggml-base.bin"

# Piper TTS Polish Bass voice model (Default, ~114 MB + config)
curl.exe -L "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/bass/high/pl_PL-bass-high.onnx" -o "models/pl_PL-bass-high.onnx"
curl.exe -L "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/bass/high/pl_PL-bass-high.onnx.json" -o "models/pl_PL-bass-high.onnx.json"

# (Optional) Piper TTS Polish Darkman voice model (~63 MB + config)
curl.exe -L "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/darkman/medium/pl_PL-darkman-medium.onnx" -o "models/pl_PL-darkman-medium.onnx"
curl.exe -L "https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/darkman/medium/pl_PL-darkman-medium.onnx.json" -o "models/pl_PL-darkman-medium.onnx.json"
```

### 6. Setup Ollama (Llama 3.1)
Ensure Ollama is running and download the model:

```powershell
ollama pull llama3.1
```

---

## ▶️ Running the Project

### Test Text-to-Speech (TTS)
Verify low-latency in-memory speech synthesis and audio playback in isolation:
```powershell
python tts.py
```
*Output:*
```text
[JARVIS]: Inicjalizacja modułu mowy zakończona. Przesyłanie strumieniowe działa poprawnie.
```

### Run the Core Voice Loop
Launch the complete voice assistant:
```powershell
python main.py
```

### Execution Flow:
1. **Greeting:** JARVIS vocalizes readiness (*"Witam szefie, co robimy?"*).
2. **Listening:** Terminal displays `Słucham...` as the microphone opens.
3. **Voice Activity Detection:** Vectorized RMS energy calculation monitors speech. Recording automatically finalizes after ~800 ms of trailing silence.
4. **Transcription:** Terminal displays `Przetwarzam...` while `whisper-cli.exe` performs fast local C++ speech inference and outputs `Usłyszałem: <twoja komenda>`.
5. **Reasoning & Tool Execution:**
   - If a system action is requested (e.g. *"otwórz notatnik"* or *"która godzina"*), Ollama triggers the appropriate registered tool function (`open_notepad` or `get_time`).
   - If a conversational query, greeting, or joke is asked, the `zwykla_odpowiedz` tool or fallback LLM content supplies a natural Polish reply.
6. **Voice Response:** JARVIS speaks the response using Piper in-memory streaming.
7. **Fallback Retry:** If no speech was detected, JARVIS prompts for a retry (*"Nie dosłyszałem, powtórz proszę."*) and listens a second time before gracefully standing down.

---

## 🛠️ Adding New Tools

Adding custom tools to JARVIS is modular and declarative using the `@tool` decorator in [tools.py](file:///c:/Users/filip/OneDrive/Desktop/projekty/jarvis/tools.py).

### Example 1: Simple Action (No Parameters)
```python
from registry import tool
import subprocess

@tool(
    name="open_calculator",
    description="Otwiera kalkulator systemowy. Użyj, gdy użytkownik prosi o włączenie lub otwarcie kalkulatora."
)
def open_calculator() -> str:
    """Launch the Windows Calculator application."""
    subprocess.Popen(["calc.exe"])
    return "Kalkulator został otwarty."
```

### Example 2: Parameterized Tool (With JSON Schema)
```python
from registry import tool

@tool(
    name="zwykla_odpowiedz",
    description="Użyj tego narzędzia ZAWSZE, gdy użytkownik prowadzi zwykłą rozmowę (np. wita się, pyta co u ciebie, żartuje).",
    parameters={
        "type": "object",
        "properties": {
            "tekst_dla_uzytkownika": {
                "type": "string",
                "description": "Treść twojej odpowiedzi w języku polskim."
            }
        },
        "required": ["tekst_dla_uzytkownika"]
    }
)
def zwykla_odpowiedz(tekst_dla_uzytkownika: str) -> str:
    """Return conversational response text for ordinary chat interactions."""
    return tekst_dla_uzytkownika
```

Any function decorated with `@tool` in `tools.py` is dynamically converted into the OpenAI/Ollama function calling schema on startup and executed with its extracted arguments automatically.

---

## 🗺️ Roadmap

- [x] Continuous audio streaming and vectorized RMS calculation in NumPy (`audio.py`)
- [x] Energy-based Voice Activity Detection (VAD) to auto-stop recording
- [x] High-performance `whisper-cli.exe` C++ transcription via `subprocess` (`transcriber.py`)
- [x] In-memory zero-disk-I/O neural speech synthesis with Piper raw PCM streaming (`tts.py`)
- [x] Modular architecture refactoring (`audio.py`, `transcriber.py`, `tts.py`, `registry.py`, `tools.py`, `actions.py`, `main.py`)
- [x] Strict PEP 484 type annotations and Google-style docstrings across all modules
- [x] Conversational retry and fallback logic for missing speech input
- [x] Local LLM integration with Llama 3.1 via Ollama (`actions.py`)
- [x] Extensible tool registry with JSON Schema and argument forwarding (`registry.py`)
- [x] Built-in OS and conversational tools (`open_notepad`, `get_time`, `zwykla_odpowiedz`)
- [ ] Background wake word detection (*Keyword: "Jarvis"*) via lightweight ONNX runtime
- [ ] Expanded OS integrations (system volume control, default browser search, media keys)
- [ ] Multi-turn conversational memory and context retention