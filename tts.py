"""Text-to-Speech (TTS) module for JARVIS using Piper neural speech synthesis.

This module provides completely offline, low-latency neural speech synthesis
by executing the standalone Piper TTS binary (`piper.exe`) with a Polish voice
model. It includes software-level audio volume attenuation and synchronous
audio playback via `sounddevice`.
"""

from pathlib import Path
import subprocess
from typing import Union
import numpy as np
import sounddevice as sd
import wave

# --- Engine & File Paths ---
BASE_DIR: Path = Path(__file__).resolve().parent
PIPER_EXE: Path = BASE_DIR / "piper" / "piper.exe"
MODEL_PATH: Path = BASE_DIR / "models" / "pl_PL-bass-high.onnx"
OUTPUT_WAV: Path = BASE_DIR / "temp_response.wav"

# --- Audio Playback & Synthesis Settings ---
DEFAULT_VOLUME: float = 0.2  # Software attenuation factor (0.0 to 1.0)
DEFAULT_LENGTH_SCALE: str = "0.85"  # Speech rate: < 1.0 speeds up voice output (0.85 = ~15% faster)


def play_audio(wav_path: Union[str, Path], volume: float = DEFAULT_VOLUME) -> None:
    """Read a WAV audio file, apply software volume scaling, and play synchronously.

    Loads the uncompressed PCM samples from the specified WAV file into a NumPy
    buffer, scales the sample amplitudes by `volume` to prevent distortion or
    excessive loudness, and plays the audio via `sounddevice.play()`.

    Args:
        wav_path (Union[str, Path]): Path to the WAV file to play.
        volume (float, optional): Volume multiplier factor between 0.0 and 1.0.
            Defaults to 0.2 (20% volume).
    """
    with wave.open(str(wav_path), "rb") as wf:
        samplerate: int = wf.getframerate()
        frames: bytes = wf.readframes(wf.getnframes())
        audio_data: np.ndarray = np.frombuffer(frames, dtype=np.int16)

    # Scale amplitude to adjust volume without distortion
    audio_data = (audio_data * volume).astype(np.int16)

    sd.play(audio_data, samplerate=samplerate)
    sd.wait()  # Block execution until audio playback has completed


def speak(text: str) -> None:
    """Synthesize speech from input text using Piper and play the audio.

    Invokes `piper.exe` via a subprocess, streams the input text via standard input,
    saves the synthesized audio to a temporary WAV file, and triggers playback.

    Args:
        text (str): Sentence or phrase to synthesize into speech.
    """
    cmd = [
        str(PIPER_EXE),
        "-m", str(MODEL_PATH),
        "-f", str(OUTPUT_WAV),
        "--length-scale", DEFAULT_LENGTH_SCALE,
    ]
    subprocess.run(
        cmd, input=text, text=True, encoding="utf-8", capture_output=True
    )
    play_audio(OUTPUT_WAV)


if __name__ == "__main__":
    # Test speech synthesis directly when script is executed standalone
    speak("Jestem gotowy do działania!")
