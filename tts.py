"""Text-to-Speech (TTS) module for JARVIS using Piper neural speech synthesis.

This module provides completely offline, low-latency neural speech synthesis
by executing the standalone Piper TTS binary (`piper.exe`) with a Polish voice
model. Synthesized audio is streamed as raw 16-bit PCM directly from the Piper
process stdout into memory, normalized to float32 samples, attenuated for
software volume control, and played synchronously via `sounddevice` without
disk I/O.
"""

from pathlib import Path
import subprocess
import numpy as np
import sounddevice as sd

# --- Engine & File Paths ---
BASE_DIR: Path = Path(__file__).resolve().parent
PIPER_EXE: Path = BASE_DIR / "piper" / "piper.exe"
MODEL_PATH: Path = BASE_DIR / "models" / "pl_PL-bass-high.onnx"

# --- Audio Playback & Synthesis Settings ---
SAMPLE_RATE: int = 22050  # Sampling rate produced by the Piper Polish voice model (Hz)
DEFAULT_VOLUME: float = 0.3  # Software attenuation factor (0.0 to 1.0)
DEFAULT_LENGTH_SCALE: str = "0.85"  # Speech rate: < 1.0 speeds up voice output (0.85 = ~15% faster)


def speak(text: str, volume: float = DEFAULT_VOLUME) -> None:
    """Synthesize speech from input text using Piper and stream audio to playback.

    Invokes `piper.exe` via a subprocess with `--output_raw`, pipe-streams input
    text encoded as UTF-8, and captures the raw 16-bit PCM byte stream from stdout.
    The raw bytes are loaded directly into a NumPy buffer, converted to 32-bit floats,
    scaled by `volume`, and played synchronously through the default sound device.

    Args:
        text (str): Sentence or phrase to synthesize into speech.
        volume (float, optional): Software volume scaling factor between 0.0 and 1.0.
            Defaults to DEFAULT_VOLUME (0.3).
    """
    print(f"\n[JARVIS]: {text}")

    cmd = [
        str(PIPER_EXE),
        "-m", str(MODEL_PATH),
        "--output_raw",
        "--length-scale", DEFAULT_LENGTH_SCALE,
    ]

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )

    raw_audio, _ = process.communicate(input=text.encode("utf-8"))

    # Convert raw 16-bit signed PCM buffer to NumPy array
    audio_data = np.frombuffer(raw_audio, dtype=np.int16)

    # Normalize samples to [-1.0, 1.0] float32 range and apply volume attenuation
    audio_float = (audio_data.astype(np.float32) / 32768.0) * volume

    # Synchronous audio playback
    sd.play(audio_float, samplerate=SAMPLE_RATE)
    sd.wait()


if __name__ == "__main__":
    speak("Inicjalizacja modułu mowy zakończona. Przesyłanie strumieniowe działa poprawnie.")