# JARVIS — Local Intelligent Voice Assistant

A private, real-time voice assistant running locally on Windows 11. The project combines the flexibility of Python with high-performance native engines: speech transcription via `whisper.cpp` (C++) and neural speech synthesis via `Piper TTS`, minimizing system resource overhead and eliminating any dependency on external cloud services.

---

## 🚀 Architecture & Features

- **Audio Capture & VAD (Voice Activity Detection):** Continuous audio streaming (16 kHz, 16-bit PCM mono) with dynamic speech/silence detection powered by vectorized RMS computation in NumPy.
- **Speech Transcription (ASR):** Fast, local inference using a compiled `whisper.cpp` binary (GGML model format).
- **Speech Synthesis (TTS):** Completely offline, low-latency neural text-to-speech using standalone Piper TTS (`piper.exe`) with the Polish `darkman-medium` voice model, featuring configurable speech rate and software-level volume attenuation.
- **Wake Word Detection (In Progress):** Lightweight keyword spotting (*"Jarvis"*) running continuously in the background via the ONNX runtime.
- **Orchestration & Tool Execution (Planned):** Local LLM integration to parse intent and execute operating system tasks and integrations.

---

## 🛠️ System Requirements

- **Operating System:** Windows 11
- **Python:** 3.10+
- **C++ Compiler:** MinGW-w64 (GCC/G++) or Visual Studio Build Tools (MSVC)
- **Tools:** CMake, Git, `curl`, PowerShell

---

## 📦 Installation & Setup

### 1. Clone the repository
```powershell
git clone <YOUR_REPOSITORY_URL>
cd <REPOSITORY_DIRECTORY>
```

### 2. Python Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install sounddevice numpy
```

### 3. Build the C++ Transcription Engine (`whisper.cpp`)
The core speech engine is built locally and is excluded from version control:

```powershell
# Clone the whisper.cpp repository
git clone [https://github.com/ggerganov/whisper.cpp.git](https://github.com/ggerganov/whisper.cpp.git)
cd whisper.cpp

# Configure and compile (using MinGW)
cmake -B build -G "MinGW Makefiles"
cmake --build build --config Release

cd ..
```

### 4. Setup Piper TTS Engine
Download and extract the standalone Windows binary release:

```powershell
curl.exe -L "[https://github.com/rhasspy/piper/releases/latest/download/piper_windows_amd64.zip](https://github.com/rhasspy/piper/releases/latest/download/piper_windows_amd64.zip)" -o "piper_windows.zip"
Expand-Archive -Path "piper_windows.zip" -DestinationPath "."
Remove-Item "piper_windows.zip"
```

### 5. Download Model Weights
All model weights are placed in a central `models/` directory (excluded from git):

```powershell
if (!(Test-Path -Path "models")) { New-Item -ItemType Directory -Path "models" }

# Whisper ASR model (~140 MB)
curl.exe -L "[https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin)" -o "models/ggml-base.bin"

# Piper TTS Polish Darkman voice model (~60 MB + config)
curl.exe -L "[https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/darkman/medium/pl_PL-darkman-medium.onnx](https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/darkman/medium/pl_PL-darkman-medium.onnx)" -o "models/pl_PL-darkman-medium.onnx"
curl.exe -L "[https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/darkman/medium/pl_PL-darkman-medium.onnx.json](https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/darkman/medium/pl_PL-darkman-medium.onnx.json)" -o "models/pl_PL-darkman-medium.onnx.json"
```

---

## ▶️ Running the Project

### Test Text-to-Speech (TTS)
Verify the Piper neural voice engine in isolation:
```powershell
python tts.py
```

### Run the Core Pipeline
Run speech recording, silence detection, transcription, and synthesized response:
```powershell
python main.py
```
1. Speak into your microphone after the prompt appears.
2. Stop speaking — the silence detector will automatically finalize recording after ~800 ms of quiet.
3. The audio is transcribed locally using `whisper.cpp`, and JARVIS responds using the neural TTS voice.

---

## 🗺️ Roadmap

- [x] Continuous audio streaming and vectorized RMS calculation in NumPy
- [x] Energy-based silence detection mechanism to auto-stop recording
- [x] WAV buffer conversion and `whisper-cli.exe` integration via `subprocess`
- [x] Local Text-to-Speech (TTS) synthesis via Piper TTS (`darkman` voice model)
- [ ] Modular code refactoring (`audio.py`, `transcriber.py`, `tts.py`, `main.py`)
- [ ] Background wake word detection (*Wake Word: Jarvis*)
- [ ] Local LLM integration (e.g., Llama via Ollama / `llama.cpp`)
- [ ] OS-level action execution (system commands, application launcher, media control)