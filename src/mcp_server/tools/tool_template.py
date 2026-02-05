"""
Template for creating custom MCP tools

INSTRUCTIONS:
1. Copy this file to a new name (e.g., my_tools.py)
2. Modify the functions below with your custom logic
3. Import your module in tools/__init__.py
4. Restart the MCP server

The @mcp.tool() decorator automatically:
- Registers the tool with the MCP server
- Generates JSON schema from type hints
- Exposes the tool to AI agents
"""
from typing import Any
from ..server import mcp
from ..config import config

@mcp.tool()
def custom_tool_example(
    required_param: str,
    optional_param: int = 10
) -> dict[str, Any]:
    """
    Brief description of what this tool does (1-2 sentences).

    This docstring is shown to the AI agent, so make it clear and actionable.
    Explain the purpose, use cases, and any important constraints.

    Args:
        required_param: Clear description of this parameter
        optional_param: Clear description with default value meaning

    Returns:
        Dictionary with operation results

    Raises:
        ValueError: When input validation fails
        RuntimeError: When operation cannot be completed
    """
    # Input validation
    if not required_param:
        raise ValueError("required_param cannot be empty")

    # Your custom logic here
    result = {
        "status": "success",
        "data": f"Processed: {required_param}",
        "value": optional_param,
        "message": "Operation completed successfully"
    }

    return result

@mcp.tool()
async def async_tool_example(data: str) -> str:
    """
    Example async tool for I/O-bound operations.

    Use async functions for:
    - API calls to external services
    - Database queries
    - File I/O operations
    - Network requests

    Args:
        data: Input data to process
    """
    # Async operations (API calls, database, etc.)
    # import httpx
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(f"https://api.example.com/{data}")
    #     return response.text

    return f"Async processed: {data}"

# Add more tool functions below using the same pattern
# Each function decorated with @mcp.tool() will be automatically
# discovered and made available to AI agents
