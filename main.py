from tts import speak
from audio import record_command, save_wav
from transcriber import transcribe


def main():
    speak("Gotów!")
    
    print("Słucham...")
    audio = record_command()
    save_wav(audio)

    print("Przetwarzam...")
    text = transcribe()
    
    if text:
        print(f"Usłyszałem: {text}")
        speak(f"Usłyszałem: {text}")
    else:
        speak("Nie dosłyszałem, powtórz proszę.")
        
if __name__ == "__main__":
    main()