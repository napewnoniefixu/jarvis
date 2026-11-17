"""Wake word detection module for JARVIS using openWakeWord.

This module provides continuous, low-latency offline keyword spotting to wake
the assistant from standby mode. It captures live microphone audio in 16-bit PCM
chunks using `sounddevice`, streams flattened samples into an ONNX-backed
openWakeWord model (e.g. 'hey_jarvis_v0.1'), and blocks execution until the
detection confidence exceeds the configured threshold.
"""

import numpy as np
import sounddevice as sd
from openwakeword.model import Model

from config import (
    CHANNELS,
    WAKEWORD_DTYPE,
    WAKEWORD_MODEL,
    WAKEWORD_CHUNK_SIZE,
    WAKEWORD_SAMPLE_RATE,
    WAKEWORD_THRESHOLD,
)

model = Model(wakeword_models=[WAKEWORD_MODEL])


def wait_for_wakeword() -> None:
    """Block execution until the configured wake word is detected from the microphone.

    Opens an audio input stream using `sounddevice.InputStream` configured for 16 kHz
    int16 audio. Resets any lingering internal activations or temporal feature buffers
    in the openWakeWord model before listening. Continuously reads chunks of audio,
    feeds them into the inference engine, and returns as soon as the model's confidence
    score surpasses `WAKEWORD_THRESHOLD`.

    Workflow:
    1. Resets the internal state of the openWakeWord model via `model.reset()`.
    2. Opens a synchronous microphone input stream.
    3. Reads audio chunks of size `WAKEWORD_CHUNK_SIZE` (1280 samples / 80 ms).
    4. Evaluates predictions on the mono audio channel (`data[:, 0]`).
    5. Exits and returns once the target wake word score exceeds `WAKEWORD_THRESHOLD`.
    """
    model.reset()
    with sd.InputStream(
        samplerate=WAKEWORD_SAMPLE_RATE,
        channels=CHANNELS,
        dtype=WAKEWORD_DTYPE,
        blocksize=WAKEWORD_CHUNK_SIZE,
    ) as stream:
        while True:
            data, _ = stream.read(WAKEWORD_CHUNK_SIZE)
            prediction = model.predict(data[:, 0])
            score = prediction[WAKEWORD_MODEL]
            if score > WAKEWORD_THRESHOLD:
                print("Wakeword detected!")
                return


if __name__ == "__main__":
    print("Say 'Hey Jarvis'...")
    wait_for_wakeword()
    print("Wake word detected!")
