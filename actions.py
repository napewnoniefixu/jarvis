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
    'Jesteś krótkim i zwięzłym asystentem głosowym o imieniu Jarvis (wymawiane "Dżarwis"). '
    'Odpowiadaj maksymalnie w jednym lub dwóch zdaniach.'
)
FALLBACK_RESPONSE: str = "Wybacz, nie wiem co powiedzieć."


def execute_command(user_text: str) -> str:
    """Process user input with the local LLM and execute actions or return dialogue.

    Sends the user text along with the registered `TOOLS_SCHEMA` to Ollama.
    If the model determines that a tool should be called:
    - Extracts the function name from `tool_calls`.
    - Looks up and executes the callable in `AVAILABLE_TOOLS`.
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
        for tool_call in message['tool_calls']:
            func_name = tool_call['function']['name']
            
            if func_name in AVAILABLE_TOOLS:
                print(f"[LLM DECYZJA]: Wywołuję funkcję -> {func_name}")
                return str(AVAILABLE_TOOLS[func_name]())
                
    # Fallback to direct conversational response if no tool call was made
    content = message.get('content', '')
    if content:
        return content
         
    return FALLBACK_RESPONSE