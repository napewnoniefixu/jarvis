import subprocess
from pathlib import Path
import sounddevice as sd
import wave
import numpy as np

BASE_DIR = Path(__file__).resolve().parent

PIPER_EXE = BASE_DIR / "piper" / "piper.exe"
MODEL_PATH = BASE_DIR / "models" / "pl_PL-darkman-medium.onnx"
OUTPUT_WAV = BASE_DIR / "temp_response.wav"

def play_audio(wav_path, volume = 0.4):
    with wave.open(str(wav_path), "rb") as wf:
        samplerate = wf.getframerate()  
        frames = wf.readframes(wf.getnframes())
        audio_data = np.frombuffer(frames, dtype=np.int16)

    audio_data = (audio_data * volume).astype(np.int16)

    sd.play(audio_data, samplerate=samplerate)
    sd.wait()

def speak(text):
    cmd = [
    str(PIPER_EXE),
    "-m",
    str(MODEL_PATH),
    "-f",
    str(OUTPUT_WAV),
    "--length-scale",
    "0.75", 
]
    subprocess.run(
        cmd, input=text, text=True, encoding="utf-8", capture_output=True
    )
    play_audio(OUTPUT_WAV)


if __name__ == "__main__":
    speak("System Dżarwis jest gotowy do użycia")
