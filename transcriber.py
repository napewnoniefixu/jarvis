"""Speech transcription (ASR) module for JARVIS using whisper.cpp.

This module interfaces with a locally compiled `whisper-cli.exe` binary
to perform offline, high-speed Automatic Speech Recognition (ASR). It processes
WAV audio recordings and converts spoken Polish sentences into clean text.
"""

from pathlib import Path
import subprocess
from typing import Optional, Union

from config import (
    WHISPER_CLI_PATH, WHISPER_MODEL_PATH,
    WHISPER_LANGUAGE, WHISPER_THREADS, TEMP_COMMAND_WAV,
)


def transcribe(filename: Union[str, Path] = TEMP_COMMAND_WAV) -> Optional[str]:
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
            Defaults to TEMP_COMMAND_WAV from config.

    Returns:
        Optional[str]: Normalized (lowercase, stripped) transcribed text if
            successful, or None if transcription failed or returned no text.
    """
    cmd = [
        str(WHISPER_CLI_PATH),
        "-m", str(WHISPER_MODEL_PATH),
        "-f", str(filename),
        "-l", WHISPER_LANGUAGE,
        "--no-timestamps",
        "-t", str(WHISPER_THREADS),
        "--suppress-nst",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=30)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
        print(f"[ERROR] Whisper transcription failed: {e}")
        return None

    if result.returncode == 0 and result.stdout:
        return result.stdout.strip().lower()

    return None
