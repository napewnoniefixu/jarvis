"""Speech transcription (ASR) module for JARVIS using whisper.cpp.

This module interfaces with a locally compiled `whisper-cli.exe` binary
to perform offline, high-speed Automatic Speech Recognition (ASR). It processes
WAV audio recordings and converts spoken Polish sentences into clean text.
"""

from pathlib import Path
import subprocess
from typing import Optional, Union

# --- Transcription Engine Configuration ---
BASE_DIR: Path = Path(__file__).resolve().parent
WHISPER_CLI_PATH: Path = BASE_DIR / "whisper.cpp" / "build" / "bin" / "whisper-cli.exe"
MODEL_PATH: Path = BASE_DIR / "models" / "ggml-base.bin"
DEFAULT_LANGUAGE: str = "pl"
DEFAULT_THREADS: str = "8"


def transcribe(filename: Union[str, Path] = "temp_command.wav") -> Optional[str]:
    """Transcribe a WAV audio file into text using whisper.cpp CLI.

    Executes the native `whisper-cli.exe` inference binary with parameters configured
    for low-latency speech recognition:
    - `-m`: Path to the GGML Whisper model weights.
    - `-f`: Path to the input 16 kHz WAV audio file.
    - `-l`: Language code (defaults to Polish: 'pl').
    - `--no-timestamps`: Omits segment timestamp markers from output.
    - `-t`: Specifies CPU worker thread allocation.
    - `--suppress-nst`: Suppresses non-speech tokens to reduce hallucinations.

    Args:
        filename (Union[str, Path], optional): Path to the WAV file to transcribe.
            Defaults to "temp_command.wav".

    Returns:
        Optional[str]: Normalized (lowercase, stripped) transcribed text if
            successful, or None if transcription failed or returned no text.
    """
    cmd = [
        str(WHISPER_CLI_PATH),
        "-m", str(MODEL_PATH),
        "-f", str(filename),
        "-l", DEFAULT_LANGUAGE,
        "--no-timestamps",
        "-t", DEFAULT_THREADS,
        "--suppress-nst",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    if result.returncode == 0 and result.stdout:
        return result.stdout.strip().lower()

    return None