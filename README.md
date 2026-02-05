# The Hive

AI agent system combining local LLMs (Ollama), web interface (Open WebUI), and a custom MCP server with extensible tools. Includes a Strands-powered agent with both local and MCP-provided tools.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Poetry](https://python-poetry.org/docs/#installation) for Python dependency management (host-side agent)
- (Optional) NVIDIA GPU with [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) for GPU acceleration

## Quick Start

1. **Start the services:**
   ```bash
   docker compose up -d
   ```

2. **Access Open WebUI:**
   Open http://localhost:3000 in your browser

3. **Create an account:**
   On first visit, create a local admin account

4. **Pull a model:**
   ```bash
   docker compose exec ollama ollama pull llama3
   ```

5. **Start chatting:**
   Select the model in Open WebUI and begin your conversation

## Available Models

Pull any model from the [Ollama library](https://ollama.com/library):

```bash
# Examples - currently installed:
docker compose exec ollama ollama pull qwen3:14b
docker compose exec ollama ollama pull qwen3-vl:8b

# Other popular models:
docker compose exec ollama ollama pull llama3
docker compose exec ollama ollama pull mistral
docker compose exec ollama ollama pull codellama
```

List downloaded models:
```bash
docker compose exec ollama ollama list
```

## Configuration

### Without GPU

If you don't have an NVIDIA GPU, edit `docker-compose.yml` and remove the `deploy` section from the ollama service:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ./ollama-data:/root/.ollama
    restart: unless-stopped
```

### Change Ports

To use different ports, modify the `ports` section in `docker-compose.yml`:

```yaml
# Change Open WebUI port (default: 3000)
ports:
  - "8080:8080"  # Access at http://localhost:8080

# Change Ollama API port (default: 11434)
ports:
  - "11435:11434"  # API at http://localhost:11435
```

## Data Persistence

Data is stored in local directories:

- `./ollama-data/` - Downloaded models and Ollama configuration
- `./open-webui-data/` - User accounts, chat history, and settings
- `./mcp-data/` - MCP server persistent data

To reset everything, stop the services and delete these directories:
```bash
docker compose down
rm -rf ollama-data open-webui-data mcp-data
```

## Common Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# View logs for a specific service
docker compose logs -f ollama
docker compose logs -f open-webui
docker compose logs -f mcp-server

# Restart services
docker compose restart

# Check service status
docker compose ps

# Pull latest images
docker compose pull
docker compose up -d
```

## Troubleshooting

### GPU not detected

Ensure nvidia-container-toolkit is installed:
```bash
# Ubuntu/Debian
sudo apt install nvidia-container-toolkit
sudo systemctl restart docker
```

Verify GPU access:
```bash
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

### Open WebUI can't connect to Ollama

1. Check if Ollama is running:
   ```bash
   docker compose ps
   ```

2. Check Ollama logs:
   ```bash
   docker compose logs ollama
   ```

3. Restart the services:
   ```bash
   docker compose restart
   ```

### Port already in use

Change the port in `docker-compose.yml` or stop the conflicting service:
```bash
# Find what's using port 3000
sudo lsof -i :3000
```

## Strands Agent with MCP Tools

The Hive includes a Strands-powered agent that combines local tools with MCP server tools for enhanced capabilities.

### Quick Start

1. **Start all services** (including MCP server):
   ```bash
   docker compose up -d
   ```

2. **Verify MCP server is running**:
   ```bash
   docker compose ps mcp-server
   # Should show: Up (healthy) or Up (starting)
   ```

3. **Install host dependencies** (first time only):
   ```bash
   poetry install
   ```

4. **Run the Strands agent**:
   ```bash
   poetry run python src/main.py
   ```

The agent will connect to:
- **Ollama** (localhost:11434) for LLM inference (qwen3:14b)
- **MCP Server** (localhost:8080/sse) for remote tools

### Available Tools

**Local Tools** (host-side):
- `calculator` - Basic math operations
- `current_time` - Get current timestamp
- `file_read` - Read files from disk
- `file_write` - Write files to disk
- `piper_speak` - Text-to-speech using Piper TTS

**MCP Tools** (server-side):
- `echo` - Echo back messages with server info
- `add` - Add two numbers
- `multiply` - Multiply two numbers

View connected tools:
```bash
poetry run python src/main.py
# Output shows: "Connected to MCP server - X tools available"
```

### Adding Custom MCP Tools

1. Create a new file in `src/mcp_server/tools/` (e.g., `my_tools.py`)
2. Use the `@mcp.tool()` decorator:
   ```python
   from ..server import mcp

   @mcp.tool()
   def my_tool(input: str) -> str:
       """What this tool does"""
       return f"Processed: {input}"
   ```
3. Import your module in `src/mcp_server/tools/__init__.py`:
   ```python
   from . import my_tools
   ```
4. Rebuild and restart:
   ```bash
   docker compose build mcp-server
   docker compose restart mcp-server
   ```

See `src/mcp_server/tools/tool_template.py` for a complete template.

📚 **Detailed MCP documentation**: See [docs/MCP_SERVER.md](docs/MCP_SERVER.md) for comprehensive development guide, testing, deployment, and troubleshooting.

### Configuration

Environment variables (set in `.env` or `docker-compose.yml`):
- `MCP_SERVER_NAME` - Server identifier (default: "the-hive-mcp")
- `MCP_HOST` - HTTP server host (default: "0.0.0.0")
- `MCP_PORT` - HTTP server port (default: 8080)
- `MCP_ENABLE_EXAMPLE_TOOLS` - Enable example tools (default: true)

### Development

**View MCP server logs**:
```bash
docker compose logs -f mcp-server
```

**Hot reload** (with volume mount):
Edit files in `src/mcp_server/`, then:
```bash
docker compose restart mcp-server
```

**Test tools directly**:
```bash
# Unit test a tool function
docker compose exec mcp-server python -c "from src.mcp_server.tools.example_tools import add; print(add(5, 3))"

# Integration test with agent
poetry run python src/main.py
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Host Machine                           │
│                                                     │
│  ┌──────────────┐    HTTP    ┌─────────────────┐   │
│  │  Strands     │  (8080)    │  MCP Server     │   │
│  │  Agent       │◄──────────►│  (Container)    │   │
│  │  (Poetry)    │   /sse     │  - FastMCP      │   │
│  │              │            │  - Custom Tools │   │
│  │  Local Tools:│            └─────────────────┘   │
│  │  - calculator│                                   │
│  │  - file_ops  │            ┌─────────────────┐   │
│  │  - piper_tts │   HTTP     │  Ollama         │   │
│  └──────────────┘◄──────────►│  (Container)    │   │
│                   (11434)    │  - qwen3:14b    │   │
│                              │  - GPU Accel    │   │
│  ┌──────────────┐            └─────────────────┘   │
│  │  Open WebUI  │                                   │
│  │  (Container) │            Port Mappings:         │
│  │  Port: 3000  │            - 3000  → WebUI        │
│  └──────────────┘            - 8080  → MCP          │
│                              - 11434 → Ollama       │
└─────────────────────────────────────────────────────┘
```

## Project Structure

```
the-hive/
├── src/
│   ├── main.py                 # Strands agent entry point
│   ├── tools/                  # Local (host-side) tools
│   │   └── piper_speak.py      # TTS tool
│   └── mcp_server/             # MCP server (runs in container)
│       ├── server.py           # FastMCP server
│       ├── config.py           # Server configuration
│       └── tools/              # MCP tools (server-side)
│           ├── example_tools.py
│           └── tool_template.py
├── docker/
│   ├── Dockerfile.mcp          # MCP server container
│   └── pyproject.mcp.toml      # Container dependencies
├── docker-compose.yml          # All services
├── pyproject.toml              # Host dependencies (Poetry)
├── .env                        # Configuration
└── docs/
    └── MCP_SERVER.md           # Detailed MCP documentation
```

## Contributing

When adding features:
1. **Local tools** go in `src/tools/` (host-side)
2. **MCP tools** go in `src/mcp_server/tools/` (containerized)
3. Update documentation in `docs/` as needed
4. Test both unit and integration scenarios
