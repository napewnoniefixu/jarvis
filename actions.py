"""Intent interpretation and LLM tool execution engine for JARVIS.

This module coordinates with a local Ollama instance (running Llama 3.1) to
parse user intent from transcribed speech. It uses Ollama's native tool/function
calling capability to map user queries to executable Python actions registered
in `registry.py` and implemented in `tools.py`.
"""

import ollama
from registry import AVAILABLE_TOOLS, TOOLS_SCHEMA
import tools  # Ensures all @tool decorators execute and register on startup

# --- Ollama Engine Configuration ---
MODEL_NAME: str = 'llama3.1'
SYSTEM_PROMPT: str = (
    'Jesteś inteligentnym, wyluzowanym asystentem głosowym o imieniu Dżarwis. '
    'Prowadź naturalną konwersację.'
)
FALLBACK_RESPONSE: str = "Wybacz, nie wiem co powiedzieć."


def execute_command(user_text: str) -> str:
    """Process user input with the local LLM and execute actions or return dialogue.

    Sends the user text along with the registered `TOOLS_SCHEMA` to Ollama.
    If the model determines that a tool should be called:
    - Extracts the function name from `tool_calls`.
    - Looks up and executes the callable in `AVAILABLE_TOOLS`.
    - Forwards any extracted arguments (`**arguments`) into the callable.
    - Returns the tool's execution result.
    If no tool call is requested, returns the model's direct conversational reply.

    Args:
        user_text (str): Transcribed speech input received from the user.

    Returns:
        str: Response text to be spoken back to the user via TTS.
    """
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': user_text}
        ],
        tools=TOOLS_SCHEMA
    )

    message = response.get('message', {})
    
    # Check if the LLM decided to invoke an external tool
    if message.get('tool_calls'):
        tool_call = message['tool_calls'][0]
        func_name = tool_call['function']['name']
        
        arguments = tool_call['function'].get('arguments', {})
        
        if func_name in AVAILABLE_TOOLS:
            print(f"\n[JARVIS LOGIC]: Uruchamiam narzędzie -> {func_name}")
            print(f"[JARVIS LOGIC]: Przekazane argumenty -> {arguments}")

            return AVAILABLE_TOOLS[func_name](**arguments)
                            
    # Fallback to direct conversational response if no tool call was made
    content = message.get('content', '')
    if content:
        return content.strip()
         
    return FALLBACK_RESPONSE