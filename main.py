"""Main entry point and orchestration pipeline for JARVIS Voice Assistant.

This script coordinates passive wake word detection (via `wakeword.py`), audio
capture (via `audio.py`), local offline speech recognition (via `transcriber.py`),
local LLM intent interpretation and tool execution (via `actions.py`), and neural
speech synthesis response (via `tts.py`).

It implements a two-tier voice interaction architecture:
1. Standby mode: Passively monitors the microphone for the keyword ("Hey Jarvis")
   with minimal processing overhead.
2. Active conversation session: Once awakened, conducts multi-turn voice dialogues,
   executing tools and speaking responses until silence or an explicit shutdown command.
"""

from audio import record_command, save_wav
from transcriber import transcribe
from tts import speak
from actions import execute_command
from wakeword import wait_for_wakeword

SHUTDOWN_KEYWORDS: list[str] = [
    "wyłącz się", "do widzenia", "koniec", "zamknij się",
    "dobranoc", "pa pa", "zakończ", "spadaj", "papa", "nara"
]


def main() -> None:
    """Execute the two-tier voice interaction orchestration loop.

    Workflow:
    1. Plays an initial system readiness greeting ("System aktywny - czekam na wezwanie").
    2. Outer Standby Loop:
       - Blocks on `wait_for_wakeword()` until "Hey Jarvis" is spotted.
       - Vocalizes an acknowledgement ("Słucham, szefie?") upon wake detection.
    3. Inner Conversation Session Loop:
       - Captures speech with energy-based Voice Activity Detection (`record_command()`).
       - If no speech is detected (silence timeout), prompts user or breaks back to standby.
       - Transcribes audio locally using whisper.cpp (`transcribe()`).
       - Checks for voice shutdown keywords (e.g. "do widzenia", "wyłącz się") to terminate.
       - Interprets user intent with local LLM (Ollama) and dispatches tools (`execute_command()`).
       - Synthesizes and vocalizes the assistant response via Piper TTS (`speak()`).
    4. Handles keyboard interrupts (Ctrl+C) and connection failures with graceful spoken fallbacks.
    """
    try:
        speak("System aktywny - czekam na wezwanie")
    except Exception as e:
        print(f"[FATAL] TTS initialization failed — cannot continue: {e}")
        return

    while True:
        try:
            print("\nSłucham...")
            wait_for_wakeword()

            speak("Słucham, szefie?")
            
            while True:
                print("\nSłucham...")
                
                audio, has_spoken = record_command()
                if not has_spoken:
                    speak("Nie dosłyszałem, powtórz proszę.")
                    continue
                
                save_wav(audio)

                print("Przetwarzam...")
                text = transcribe()

                if not text:
                    speak("Żegnam")
                    break

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
