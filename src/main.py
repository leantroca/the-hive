from strands import Agent
from strands.models.ollama import OllamaModel
from strands_tools import calculator, current_time, file_read, file_write
from tools.piper_speak import piper_speak
from mcp.client.sse import sse_client
from strands.tools.mcp import MCPClient
import os

# Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_LLM = os.getenv("OLLAMA_LLM", "qwen3:14b")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080/sse")

# Initialize Ollama model
ollama = OllamaModel(
	host=OLLAMA_HOST,
	model_id=OLLAMA_LLM,
)

# Create MCP client for HTTP transport
mcp_client = MCPClient(
	lambda: sse_client(MCP_SERVER_URL)
)

# Connect to MCP server and get tools
mcp_client.__enter__()
	
# List available MCP tools
mcp_tools = mcp_client.list_tools_sync()
print(f"Connected to MCP server - {len(mcp_tools)} tools available")

# Combine local tools with MCP tools
agent_tools = [
	# calculator,
	current_time,
	file_read,
	file_write,
	piper_speak,  # TTS stays local on host
]
all_tools = agent_tools + mcp_tools

# Create agent with all tools
agent = Agent(
	model=ollama,
	tools=all_tools,
)

print(f"Agent initialized with {len(all_tools)} total tools")
print("Local tools:", [agent_tools])
if mcp_tools:
	print("MCP tools:", [tool.tool_name for tool in mcp_tools])
