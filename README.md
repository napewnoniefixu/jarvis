# JARVIS — Local Intelligent Voice Assistant

A private, real-time voice assistant running locally on Windows 11. The project combines the flexibility of Python with a high-performance C++ speech transcription engine (`whisper.cpp`), minimizing system resource overhead and eliminating any dependency on external cloud services.

---

## 🚀 Architecture & Features

- **Audio Capture & VAD (Voice Activity Detection):** Continuous audio streaming (16 kHz, 16-bit PCM mono) with dynamic speech/silence detection powered by vectorized RMS computation in NumPy.
- **Speech Transcription (ASR):** Fast, local inference using a compiled `whisper.cpp` binary (GGML model format).
- **Wake Word Detection (In Progress):** Lightweight keyword spotting (*"Jarvis"*) running continuously in the background via the ONNX runtime.
- **Orchestration & Tool Execution (Planned):** Local LLM integration to parse intent and execute operating system tasks and integrations.

---

## 🛠️ System Requirements

- **Operating System:** Windows 11
- **Python:** 3.10+
- **C++ Compiler:** MinGW-w64 (GCC/G++) or Visual Studio Build Tools (MSVC)
- **Tools:** CMake, Git, `curl`

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
pip install -r requirements.txt
```

*(If you do not have `requirements.txt` yet, install the core dependencies manually: `pip install sounddevice numpy`)*

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

### 4. Download Whisper Model Weights
Download the quantized `base` model (~140 MB) into a dedicated `models/` folder:

```powershell
if (!(Test-Path -Path "models")) { New-Item -ItemType Directory -Path "models" }
curl.exe -L "[https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin)" -o "models/ggml-base.bin"
```

---

## ▶️ Running the Project

Run the recording and silence detection module:

```powershell
python test_silence.py
```

1. Speak into the microphone — the algorithm triggers recording automatically once audio energy exceeds the RMS threshold.
2. Stop speaking and remain quiet for ~1.5 seconds.
3. The script automatically finalizes the audio buffer and plays back the captured input.

---

## 🗺️ Roadmap

- [x] Continuous audio streaming and vectorized RMS calculation in NumPy
- [x] Energy-based silence detection mechanism to auto-stop recording
- [x] WAV buffer conversion and `whisper-cli.exe` integration via `subprocess`
- [ ] Background wake word detection (*Wake Word: Jarvis*)
- [ ] Local LLM integration (e.g., Llama via Ollama / `llama.cpp`)
- [ ] OS-level action execution (system commands, application launcher, media control)
- [ ] Local Text-to-Speech (TTS) response synthesis
