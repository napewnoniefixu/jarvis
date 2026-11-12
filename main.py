"""Main entry point and orchestration pipeline for JARVIS Voice Assistant.

This script coordinates audio capture (via `audio.py`), local offline speech
recognition (via `transcriber.py`), local LLM intent interpretation and tool
execution (via `actions.py`), and neural speech synthesis response (via `tts.py`).
It implements a continuous conversational interaction loop with voice activity
detection, automatic retry on missed speech, and graceful shutdown via voice
command.
"""

from audio import record_command, save_wav
from transcriber import transcribe
from tts import speak
from actions import execute_command

SHUTDOWN_KEYWORDS: list[str] = [
    "wyłącz się", "do widzenia", "koniec", "zamknij się",
    "dobranoc", "pa pa", "zakończ", "spadaj", "papa", "nara"
]


def main() -> None:
    """Execute the continuous voice interaction loop.

    Workflow:
    1. Plays an initial greeting indicating readiness ("Witam szefie, co robimy?").
    2. Enters a continuous loop that:
       a. Listens for user voice input via the microphone and records the command.
       b. Saves captured audio to a temporary WAV file.
       c. Transcribes the audio locally using whisper.cpp.
       d. If transcription matches a shutdown keyword, says goodbye and exits.
       e. If transcription is successful, passes the text to the local LLM
          to run system tools or generate conversational responses, then speaks.
       f. If no speech is recognized, prompts the user to repeat and continues.
    3. Handles Ctrl+C for manual exit and recovers from errors gracefully.
    """
    try:
        speak("Witam szefie, co robimy?")
    except Exception as e:
        print(f"[FATAL] TTS initialization failed — cannot continue: {e}")
        return

    while True:
        try:
            print("\nSłucham...")
            audio, has_spoken = record_command()
            if not has_spoken:
                speak("Nie dosłyszałem, powtórz proszę.")
                continue
            
            save_wav(audio)

            print("Przetwarzam...")
            text = transcribe()

            if not text:
                speak("Nie dosłyszałem, powtórz proszę.")
                continue

            print(f"Usłyszałem: {text}")

            if any(keyword in text for keyword in SHUTDOWN_KEYWORDS):
                speak("Do usłyszenia, szefie.")
                break

            response = execute_command(text)
            speak(response)

        except KeyboardInterrupt:
            print("\n[INFO] Przerwanie ręczne (Ctrl+C)")
            speak("Do usłyszenia, szefie.")
            break

        except ConnectionError:
            speak("Nie mogę się połączyć z silnikiem myślenia. Sprawdź czy Ollama działa.")

        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            speak("Przepraszam, coś poszło nie tak. Spróbuj ponownie.")


if __name__ == "__main__":
    main()
