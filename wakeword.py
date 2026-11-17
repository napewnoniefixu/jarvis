"""Wake word detection module for JARVIS using openWakeWord.

This module provides continuous, low-latency offline keyword spotting to wake
the assistant from standby mode. It captures live microphone audio in 16-bit PCM
chunks using `sounddevice`, streams flattened samples into an openWakeWord
model (such as 'jarvis_v2.onnx'), and blocks execution until the detection
confidence exceeds the configured threshold.
"""

from pathlib import Path
import numpy as np
import sounddevice as sd
from openwakeword.model import Model

from config import (
    BASE_DIR,
    CHANNELS,
    WAKEWORD_DTYPE,
    WAKEWORD_MODEL,
    WAKEWORD_CHUNK_SIZE,
    WAKEWORD_SAMPLE_RATE,
    WAKEWORD_THRESHOLD,
)

# Resolve model target: check direct path, inside models/, or as a built-in model name
_model_target = WAKEWORD_MODEL
_candidate = Path(WAKEWORD_MODEL)

if _candidate.is_file():
    _model_target = str(_candidate)
elif (BASE_DIR / "models" / WAKEWORD_MODEL).is_file():
    _model_target = str(BASE_DIR / "models" / WAKEWORD_MODEL)
elif (BASE_DIR / "models" / f"{WAKEWORD_MODEL}.onnx").is_file():
    _model_target = str(BASE_DIR / "models" / f"{WAKEWORD_MODEL}.onnx")

model = Model(wakeword_models=[_model_target])
# Dynamically extract the prediction dictionary key assigned by openWakeWord (e.g. 'jarvis_v2')
_model_key = list(model.models.keys())[0]


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
            score = prediction[_model_key]
            if score > WAKEWORD_THRESHOLD:
                print("Wakeword detected!")
                return


if __name__ == "__main__":
    print("Say 'Hey Jarvis'...")
    wait_for_wakeword()
    print("Wake word detected!")
