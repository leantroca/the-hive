"""Example MCP tools to demonstrate functionality"""
from typing import Any
from ..server import mcp
from ..config import config

@mcp.tool()
def echo(message: str) -> dict[str, Any]:
    """
    Echo back a message - simple test tool.

    Args:
        message: The message to echo back

    Returns:
        Dictionary with the echoed message and server info
    """
    return {
        "status": "success",
        "message": message,
        "server": config.server_name,
        "version": config.version
    }

@mcp.tool()
def add(a: float, b: float) -> float:
    """
    Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        The sum of a and b
    """
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        The product of a and b
    """
    return a * b
