"""Executable system tools and OS integrations for JARVIS.

This module defines the actual functions that JARVIS can invoke on the host
machine in response to user voice commands. Each tool is decorated with `@tool`
to register it with the function calling system in `registry.py`.
"""

from datetime import datetime
import subprocess
from registry import tool


@tool(
    name="open_notepad", 
    description="Otwiera systemowy edytor tekstu (notatnik). Użyj, gdy użytkownik jawnie prosi o otwarcie, włączenie lub uruchomienie notatnika."
)
def open_notepad() -> str:
    """Launch the Windows Notepad application as a background subprocess.

    Returns:
        str: Spoken confirmation message indicating the action was performed.
    """
    subprocess.Popen(["notepad.exe"])
    return "Notatnik został otwarty."


@tool(
    name="get_time", 
    description="Sprawdza aktualną godzinę. Użyj, gdy użytkownik pyta o czas, godzinę lub o to, która jest."
)
def get_time() -> str:
    """Retrieve the current system time formatted as a natural Polish sentence.

    Returns:
        str: Current time response string (e.g. 'Jest godzina 14:35.').
    """
    now = datetime.now()
    return f"Jest godzina {now.hour}:{now.minute:02d}."