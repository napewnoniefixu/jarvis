import subprocess

def transcribe(filename = "temp_command.wav"):
    cmd = [
    "whisper.cpp/build/bin/whisper-cli.exe",
    "-m", "models/ggml-base.bin",
    "-f", filename,
    "-l", "pl",
    "--no-timestamps",
    "-t", "8",
    "--suppress-nst"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

    if result.returncode == 0 and result.stdout:
        return result.stdout.strip().lower()

    return None