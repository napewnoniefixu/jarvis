"""Tool registry and schema builder for JARVIS function calling.

This module provides a decorator-based registry system to dynamically register
callable Python functions as tools for the local LLM (Ollama). It automatically
builds the OpenAI/Ollama-compatible JSON schema required for function calling.
"""

from typing import Any, Callable, Dict, List, Optional

# Dictionary mapping registered tool names to their corresponding callable functions
AVAILABLE_TOOLS: Dict[str, Callable[..., Any]] = {}

# List of tool schema definitions formatted for Ollama function calling
TOOLS_SCHEMA: List[Dict[str, Any]] = []


def tool(
    name: str,
    description: str,
    parameters: Optional[Dict[str, Any]] = None
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to register a function as an LLM-executable tool.

    Registers the target function into `AVAILABLE_TOOLS` and appends its metadata
    to `TOOLS_SCHEMA` following the standard function-calling specification.

    Args:
        name (str): The unique identifier for the function (must match LLM tool name).
        description (str): A natural language description of what the tool does and
            when the LLM should invoke it.
        parameters (Optional[Dict[str, Any]], optional): JSON Schema dictionary specifying
            tool argument types, descriptions, and required fields. Defaults to an empty
            object schema `{"type": "object", "properties": {}}`.

    Returns:
        Callable[[Callable[..., Any]], Callable[..., Any]]: Decorator function that
            registers and returns the original function unchanged.
    """
    if parameters is None:
        parameters = {"type": "object", "properties": {}}
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        AVAILABLE_TOOLS[name] = func
        TOOLS_SCHEMA.append({
            'type': 'function',
            'function': {
                'name': name,
                'description': description,
                'parameters' : parameters
            }
        })
        return func
    return decorator