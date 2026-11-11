"""Intent interpretation and LLM tool execution engine for JARVIS.

This module coordinates with a local Ollama instance (running Llama 3.1) to
parse user intent from transcribed speech. It uses Ollama's native tool/function
calling capability to map user queries to executable Python actions registered
in `registry.py` and implemented in `tools.py`.

Maintains a rolling conversation history to enable multi-turn context retention.
"""

import ollama
from registry import AVAILABLE_TOOLS, TOOLS_SCHEMA
import tools  # Ensures all @tool decorators execute and register on startup

from config import LLM_MODEL, LLM_SYSTEM_PROMPT, LLM_FALLBACK_RESPONSE, MAX_HISTORY_MESSAGES

# --- Conversation History ---
# Rolling message buffer that enables multi-turn context retention.
# Initialized with the system prompt; user/assistant messages are appended
# on each turn and trimmed to MAX_HISTORY_MESSAGES to prevent unbounded growth.
conversation_history: list[dict[str, str]] = [
    {'role': 'system', 'content': LLM_SYSTEM_PROMPT}
]


def _trim_history() -> None:
    """Trim conversation history to keep the system prompt + last N messages.

    Preserves the system prompt (index 0) and retains only the most recent
    MAX_HISTORY_MESSAGES user/assistant exchanges to prevent unbounded memory
    growth while maintaining sufficient conversational context.
    """
    if len(conversation_history) > MAX_HISTORY_MESSAGES + 1:
        # Keep system prompt + last MAX_HISTORY_MESSAGES messages
        conversation_history[:] = [conversation_history[0]] + conversation_history[-(MAX_HISTORY_MESSAGES):]


def clear_history() -> None:
    """Reset conversation history to only the system prompt.

    Useful for explicit "forget everything" commands or session resets.
    """
    conversation_history.clear()
    conversation_history.append({'role': 'system', 'content': LLM_SYSTEM_PROMPT})


def execute_command(user_text: str) -> str:
    """Process user input with the local LLM and execute actions or return dialogue.

    Sends the user text along with the full conversation history and registered
    TOOLS_SCHEMA to Ollama. If the model determines that a tool should be called:
    - Extracts the function name from `tool_calls`.
    - Looks up and executes the callable in `AVAILABLE_TOOLS`.
    - Forwards any extracted arguments (`**arguments`) into the callable.
    - Returns the tool's execution result.
    If no tool call is requested, returns the model's direct conversational reply.

    The user message and assistant response are appended to conversation_history
    to enable multi-turn context retention.

    Args:
        user_text (str): Transcribed speech input received from the user.

    Returns:
        str: Response text to be spoken back to the user via TTS.
    """
    # Append user message to history
    conversation_history.append({'role': 'user', 'content': user_text})

    try:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=conversation_history,
            tools=TOOLS_SCHEMA
        )
    except Exception as e:
        print(f"[ERROR] Ollama communication failed: {e}")
        # Remove the user message since the exchange failed
        conversation_history.pop()
        raise ConnectionError(f"Ollama error: {e}") from e

    message = response.get('message', {})
    result = LLM_FALLBACK_RESPONSE

    # Check if the LLM decided to invoke an external tool
    if message.get('tool_calls'):
        tool_call = message['tool_calls'][0]
        func_name = tool_call['function']['name']
        
        arguments = tool_call['function'].get('arguments', {})
        
        if func_name in AVAILABLE_TOOLS:
            print(f"\n[JARVIS LOGIC]: Uruchamiam narzędzie -> {func_name}")
            print(f"[JARVIS LOGIC]: Przekazane argumenty -> {arguments}")

            try:
                result = AVAILABLE_TOOLS[func_name](**arguments)
            except Exception as e:
                print(f"[ERROR] Tool '{func_name}' execution failed: {e}")
                result = f"Przepraszam, nie udało się wykonać polecenia: {e}"
        else:
            print(f"[ERROR] Unknown tool requested: {func_name}")
            result = "Przepraszam, nie znam tego polecenia."
    else:
        # Fallback to direct conversational response if no tool call was made
        content = message.get('content', '')
        if content:
            result = content.strip()

    # Store assistant response in history for context continuity
    conversation_history.append({'role': 'assistant', 'content': result})
    _trim_history()

    return result
