"""Audio capture and Voice Activity Detection (VAD) module for JARVIS.

This module provides real-time microphone stream capture with dynamic speech
and silence detection based on Root Mean Square (RMS) energy analysis. Recorded
audio is captured as floating-point samples and can be converted and exported to
16-bit mono WAV format suitable for speech recognition engines like whisper.cpp.
"""

from pathlib import Path
from typing import Union
import numpy as np
import sounddevice as sd
import wave

# --- Audio Stream Configuration ---
SAMPLE_RATE: int = 16000  # Sampling frequency in Hz (16 kHz required by whisper.cpp)
CHANNELS: int = 1  # Mono recording channel
DTYPE: str = 'float32'  # Data type for captured raw audio buffers
BLOCKSIZE: int = 1600  # Number of samples per buffer chunk (1600 / 16000 = 100 ms)

# --- Voice Activity Detection (VAD) Tuning ---
# RMS amplitude threshold above which input is classified as active speech
THRESHOLD: float = 0.003

# Maximum consecutive silent frames allowed after speech begins before stopping (8 * 100 ms = ~800 ms)
SILENCE_LIMIT_FRAMES: int = 8

# Maximum consecutive silent frames before timing out if no speech is detected (50 * 100 ms = ~5.0 s)
MAX_INITIAL_SILENCE_FRAMES: int = 50


def calculate_RMS(audio_chunk: np.ndarray) -> float:
    """Calculate the Root Mean Square (RMS) energy of an audio buffer.

    RMS measures signal power and serves as a simple, effective metric for
    voice activity detection (VAD) to distinguish speech from ambient noise.

    Args:
        audio_chunk (np.ndarray): Audio sample array of numerical amplitude values.

    Returns:
        float: Calculated RMS energy of the chunk.
    """
    return float(np.sqrt(np.mean(audio_chunk**2)))


def record_command() -> np.ndarray:
    """Record speech from the default microphone using dynamic silence detection.

    Opens an audio input stream and continuously buffers audio chunks. Recording
    starts in a listening state and monitors energy level:
    - If energy exceeds `THRESHOLD`, speech is marked as started.
    - Once speech has begun, recording ends automatically when silence persists
      for more than `SILENCE_LIMIT_FRAMES` chunks (~800 ms).
    - If no speech occurs within 50 chunks (~5 seconds), recording times out.

    Returns:
        np.ndarray: Concatenated float32 audio samples representing the complete recording.
    """
    frames = []
    has_spoken = False
    silence_frames = 0

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE, blocksize=BLOCKSIZE) as stream:
        while True:
            data, _ = stream.read(BLOCKSIZE)
            frames.append(data.copy())

            current_rms = calculate_RMS(data)

            if current_rms > THRESHOLD:
                has_spoken = True
                silence_frames = 0
            else:
                if has_spoken:
                    silence_frames += 1
                    if silence_frames > SILENCE_LIMIT_FRAMES:
                        break
                else:
                    silence_frames += 1
                    if silence_frames >= MAX_INITIAL_SILENCE_FRAMES:
                        break
    
    full_audio = np.concatenate(frames, axis=0)
    return full_audio


def save_wav(audio_data: np.ndarray, filename: Union[str, Path] = "temp_command.wav") -> None:
    """Export normalized float32 audio data to a 16-bit PCM WAV file.

    Scales floating point values in the range [-1.0, 1.0] to 16-bit signed
    integers ([-32768, 32767]) and writes a standard uncompressed WAV file
    matching the configured sample rate and channel count.

    Args:
        audio_data (np.ndarray): Array of float32 audio samples to export.
        filename (Union[str, Path], optional): Output file destination.
            Defaults to "temp_command.wav".
    """
    audio_data_int16 = (audio_data * 32767).astype(np.int16)

    with wave.open(str(filename), 'w') as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)  # 2 bytes per sample = 16-bit PCM
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio_data_int16.tobytes())