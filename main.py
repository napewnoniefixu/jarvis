"""Main entry point and orchestration pipeline for JARVIS Voice Assistant.

This script coordinates audio capture (via `audio.py`), local offline speech
recognition (via `transcriber.py`), and neural speech synthesis response
(via `tts.py`). It implements a conversational interaction flow with an automatic
retry mechanism when speech is not detected or cannot be recognized.
"""

from audio import record_command, save_wav
from transcriber import transcribe
from tts import speak


def main() -> None:
    """Execute the core voice interaction loop.

    Workflow:
    1. Plays an initial greeting indicating readiness.
    2. Listens for user voice input via the microphone and records the command.
    3. Saves captured audio to a temporary WAV file.
    4. Transcribes the audio locally using whisper.cpp.
    5. If transcription is successful, prints and vocalizes what was heard.
    6. If no speech is recognized, prompts the user to repeat and performs
       a secondary listening and transcription attempt before standing down.
    """
    # Notify user that the assistant is ready
    speak("Jestem gotów!")
    
    # --- Primary Listening Pass ---
    print("Słucham...")
    audio = record_command()
    save_wav(audio)

    print("Przetwarzam...")
    text = transcribe()
    
    if text:
        print(f"Usłyszałem: {text}")
        speak(f"Usłyszałem: {text}")
    else:
        # --- Fallback / Retry Pass ---
        speak("Nie dosłyszałem, powtórz proszę.")

        print("Słucham...")
        audio = record_command()
        save_wav(audio)

        print("Przetwarzam...")
        text = transcribe()
        
        if text:
            print(f"Usłyszałem: {text}")
            speak(f"Usłyszałem: {text}")
        else:
            speak("Nie dosłyszałem nadal, odstawiam to.")


if __name__ == "__main__":
    main()