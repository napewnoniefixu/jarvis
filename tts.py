import pyttsx3

def init_tts():
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    engine.setProperty("volume", 1.0)
    return engine


def speak(engine, text):
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    engine = init_tts()
    speak(engine, "System Dżarwis jest gotowy do użycia")