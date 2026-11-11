"""Text-to-Speech (TTS) module for JARVIS using Piper neural speech synthesis.

This module provides completely offline, low-latency neural speech synthesis
by executing the standalone Piper TTS binary (`piper.exe`) with a Polish voice
model. Synthesized audio is streamed as raw 16-bit PCM directly from the Piper
process stdout into memory, normalized to float32 samples, attenuated for
software volume control, and played synchronously via `sounddevice` without
disk I/O.
"""

import subprocess
import numpy as np
import sounddevice as sd

from config import (
    PIPER_EXE_PATH, TTS_MODEL_PATH,
    TTS_SAMPLE_RATE, TTS_VOLUME, TTS_LENGTH_SCALE,
)


def speak(text: str, volume: float = TTS_VOLUME) -> None:
    """Synthesize speech from input text using Piper and stream audio to playback.

    Invokes `piper.exe` via a subprocess with `--output_raw`, pipe-streams input
    text encoded as UTF-8, and captures the raw 16-bit PCM byte stream from stdout.
    The raw bytes are loaded directly into a NumPy buffer, converted to 32-bit floats,
    scaled by `volume`, and played synchronously through the default sound device.

    Args:
        text (str): Sentence or phrase to synthesize into speech.
        volume (float, optional): Software volume scaling factor between 0.0 and 1.0.
            Defaults to TTS_VOLUME from config.
    """
    print(f"\n[JARVIS]: {text}")

    cmd = [
        str(PIPER_EXE_PATH),
        "-m", str(TTS_MODEL_PATH),
        "--output_raw",
        "--length-scale", str(TTS_LENGTH_SCALE),
    ]

    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        raw_audio, _ = process.communicate(input=text.encode("utf-8"))

        if not raw_audio:
            print("[ERROR] Piper returned no audio data.")
            return

        audio_data = np.frombuffer(raw_audio, dtype=np.int16)

        audio_float = (audio_data.astype(np.float32) / 32768.0) * volume

        sd.play(audio_float, samplerate=TTS_SAMPLE_RATE)
        sd.wait()

    except FileNotFoundError:
        print(f"[ERROR] Piper executable not found at: {PIPER_EXE_PATH}")
    except Exception as e:
        print(f"[ERROR] TTS synthesis failed: {e}")


if __name__ == "__main__":
    speak("Inicjalizacja modułu mowy zakończona. Przesyłanie strumieniowe działa poprawnie.")
