"""Centralized configuration for JARVIS Voice Assistant.

Defines all tunable parameters, file paths, and runtime settings for audio
capture, speech recognition (whisper.cpp), speech synthesis (Piper TTS),
language model orchestration (Ollama), and wake word detection (openWakeWord).
"""

from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parent

SAMPLE_RATE: int = 16000
CHANNELS: int = 1
AUDIO_DTYPE: str = 'float32'
BLOCKSIZE: int = 1600
VAD_THRESHOLD: float = 0.003
SILENCE_LIMIT_FRAMES: int = 8
MAX_INITIAL_SILENCE_FRAMES: int = 50

WHISPER_CLI_PATH: Path = BASE_DIR / "whisper.cpp" / "build" / "bin" / "whisper-cli.exe"
WHISPER_MODEL_PATH: Path = BASE_DIR / "models" / "ggml-base.bin"
WHISPER_LANGUAGE: str = "pl"
WHISPER_THREADS: int = 8

PIPER_EXE_PATH: Path = BASE_DIR / "piper" / "piper.exe"
TTS_MODEL_PATH: Path = BASE_DIR / "models" / "pl_PL-bass-high.onnx"
TTS_SAMPLE_RATE: int = 22050
TTS_VOLUME: float = 0.3
TTS_LENGTH_SCALE: float = 0.85

LLM_MODEL: str = 'llama3.1'
LLM_SYSTEM_PROMPT: str = (
    'Jesteś inteligentnym, wyluzowanym asystentem głosowym o imieniu Dżarwis. '
    'Prowadź naturalną konwersację. Odpowiadaj krótko i zwięźle — '
    'twoje odpowiedzi będą czytane na głos, więc unikaj długich wywodów.'
)
LLM_FALLBACK_RESPONSE: str = "Wybacz, nie wiem co powiedzieć."
MAX_HISTORY_MESSAGES: int = 20

# --- Temp Files ---
TEMP_COMMAND_WAV: Path = BASE_DIR / "temp_command.wav"

# --- Wake Word Detection (openWakeWord) ---
WAKEWORD_MODEL: str = "hey_jarvis_v0.1"
WAKEWORD_THRESHOLD: float = 0.7
WAKEWORD_CHUNK_SIZE: int = 1280
WAKEWORD_SAMPLE_RATE: int = 16000
WAKEWORD_DTYPE: str = 'int16'