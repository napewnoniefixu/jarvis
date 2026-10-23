from tts import speak
from audio import record_command, save_wav
from transcriber import transcribe


def main():
    speak("Jestem gotowy.")
    
    audio = record_command()
    save_wav(audio)
    text = transcribe()
    
    if text:
        speak(tts, f"Usłyszałem: {text}")

if __name__ == "__main__":
    main()