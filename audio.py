import numpy as np
import sounddevice as sd
import wave

THRESHOLD = 0.003
SILENCE_LIMIT_FRAMES = 8

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'float32'
BLOCKSIZE = 1600

def calculate_RMS(audio_chunk):
    return float(np.sqrt(np.mean(audio_chunk**2)))


def record_command():
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
                    if silence_frames >= 50:
                        break
    
    full_audio = np.concatenate(frames, axis=0)
    return full_audio

def save_wav(audio_data, filename = "temp_command.wav"):
    audio_data_int16 = (audio_data * 32767).astype(np.int16)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(audio_data_int16.tobytes())