# MCP Server Documentation

**Status**: ✅ READY FOR USE | Last verified: 2026-02-05

## Overview

The MCP (Model Context Protocol) server is fully operational and provides tool capabilities to Strands agents via HTTP/SSE transport using the FastMCP framework.

### What's Working

1. **Docker Container** - MCP server running in isolated container
2. **HTTP/SSE Transport** - FastAPI integration with lifespan management
3. **Health Checks** - Container health monitoring
4. **Tool Registration** - Tools registered via decorators
5. **Example Tools** - 3 demonstration tools:
   - `echo` - Echo back a message with server info
   - `add` - Add two numbers
   - `multiply` - Multiply two numbers

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Host Machine                           │
│                                                     │
│  ┌──────────────┐    HTTP    ┌─────────────────┐   │
│  │  Strands     │  (8080)    │  MCP Server     │   │
│  │  Agent       │◄──────────►│  (Container)    │   │
│  │              │            │  - FastMCP      │   │
│  │              │            │  - 3 Tools      │   │
│  └──────────────┘            └─────────────────┘   │
│                                                     │
│  ┌──────────────┐            ┌─────────────────┐   │
│  │  Ollama      │            │  Open WebUI     │   │
│  │  (Container) │            │  (Container)    │   │
│  └──────────────┘            └─────────────────┘   │
└─────────────────────────────────────────────────────┘
```

The MCP server uses FastMCP framework with HTTP/SSE transport for production multi-client support.

## Project Structure

```
the-hive/
├── docker/
│   ├── Dockerfile.mcp          # MCP server container
│   └── pyproject.mcp.toml      # Container dependencies
│
├── src/mcp_server/
│   ├── __init__.py             # Package initialization
│   ├── server.py               # FastMCP server instance
│   ├── config.py               # Pydantic configuration
│   │
│   ├── tools/
│   │   ├── __init__.py         # Tool registry
│   │   ├── example_tools.py    # Example tools (echo, add, multiply)
│   │   └── tool_template.py    # Template for new tools
│   │
│   └── transport/
│       ├── __init__.py
│       └── http_server.py      # HTTP/SSE transport with FastAPI
│
├── docker-compose.yml          # Includes mcp-server service
└── .env                        # Configuration
```

## Configuration

Environment variables (in `.env`):

```bash
MCP_SERVER_NAME=the-hive-mcp
MCP_HOST=0.0.0.0
MCP_PORT=8080
MCP_ENABLE_EXAMPLE_TOOLS=true
MCP_SERVER_URL=http://localhost:8080/sse
```

### Dependencies

**Container** (docker/pyproject.mcp.toml):
- mcp ^1.2.0
- fastmcp ^2.0.0
- uvicorn ^0.32.0
- fastapi ^0.115.0
- pydantic ^2.10.0
- pydantic-settings ^2.7.0
- httpx ^0.28.0
- python-dotenv ^1.0.0

**Host** (pyproject.toml):
- Kept separate for host-side dependencies

## Quick Start & Verification

### Start the Server

```bash
# Start MCP server
docker compose up -d mcp-server

# View logs
docker compose logs -f mcp-server
```

### Verify Server Health

```bash
# Check server status
docker compose ps mcp-server
# Output: Should show "Up (healthy)"

# Test health endpoint (if implemented)
curl http://localhost:8080/health

# Check registered tools
docker compose exec mcp-server python -c "
from src.mcp_server.server import mcp
print('Tools:', list(mcp._tool_manager._tools.keys()))
"
# Output: Tools: ['echo', 'add', 'multiply']
```

### Test with Agent

```bash
# Run main.py to test agent integration
poetry run python src/main.py
```

## Creating Custom Tools

### Basic Tool Pattern

```python
from ..server import mcp

@mcp.tool()
def my_tool(param: str) -> str:
    """Tool description for AI agent"""
    return f"Result: {param}"
```

### Best Practices

1. **Type Hints**: Always use type hints - FastMCP generates schemas from them
2. **Docstrings**: Write clear docstrings - AI agents read these to understand tool usage
3. **Error Handling**: Raise specific exceptions with clear messages
4. **Validation**: Validate inputs at the start of the function
5. **Async**: Use `async def` for I/O-bound operations

### Tool Template

Copy `src/mcp_server/tools/tool_template.py` as a starting point for new tools. It includes:
- Function structure
- Type hints
- Docstring format
- Error handling patterns
- Registration instructions

### Adding New Tools

1. Create a new file in `src/mcp_server/tools/` or use `tool_template.py`
2. Import the MCP server instance: `from ..server import mcp`
3. Decorate your function with `@mcp.tool()`
4. Import your tool in `src/mcp_server/tools/__init__.py`
5. Restart the MCP server: `docker compose restart mcp-server`

## Testing

### Unit Testing

```python
# Test tools directly
from src.mcp_server.tools.example_tools import add
assert add(2, 3) == 5
```

### Integration Testing

```bash
# Start MCP server
docker compose up -d mcp-server

# Test with MCP client (from Strands agent)
poetry run python src/main.py
```

## Deployment

### Local Development

```bash
# Start MCP server
docker compose up -d mcp-server

# View logs
docker compose logs -f mcp-server

# Restart after changes
docker compose restart mcp-server

# Rebuild after code changes
docker compose build mcp-server
docker compose up -d mcp-server
```

### Production

```bash
# Build optimized image
docker compose build --no-cache mcp-server

# Deploy with compose
docker compose up -d

# Check health
docker compose ps
```

**Production Notes**:
- Remove development volume mount in docker-compose.yml
- Set appropriate resource limits
- Configure proper logging
- Use environment-specific .env files

## Troubleshooting

### MCP Server won't start

```bash
# Check logs
docker compose logs mcp-server

# Common issues:
# - Port 8080 already in use -> change MCP_PORT in .env
# - Import errors -> rebuild container
# - Missing dependencies -> update docker/pyproject.mcp.toml and rebuild
```

### Agent can't connect to MCP

```bash
# Verify server is running
docker compose ps mcp-server

# Check network connectivity
docker network ls
docker network inspect the-hive_default

# Test MCP endpoint
curl http://localhost:8080/sse
```

### Tools not appearing

```bash
# Verify tools are imported in tools/__init__.py
cat src/mcp_server/tools/__init__.py

# Restart MCP server
docker compose restart mcp-server

# Check server logs for import errors
docker compose logs mcp-server | grep -i error

# Verify tool registration
docker compose exec mcp-server python -c "
from src.mcp_server.server import mcp
print('Registered tools:', list(mcp._tool_manager._tools.keys()))
"
```

### Container shows as unhealthy

```bash
# Check health check logs
docker inspect mcp-server | grep -A 10 Health

# Verify health endpoint
curl -v http://localhost:8080/health

# Check if server is listening
docker compose exec mcp-server netstat -tlnp | grep 8080
```

## Next Steps

1. **Add Custom Tools**: Use `tool_template.py` to create domain-specific tools
2. **Remove Example Tools**: Set `MCP_ENABLE_EXAMPLE_TOOLS=false` in production
3. **Add Authentication**: Implement API key validation if needed
4. **Monitor Performance**: Add logging and metrics
5. **Scale**: Deploy multiple instances behind a load balancer if needed

## Known Issues

None - all functionality working as expected.
