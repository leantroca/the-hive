"""SSE transport for MCP server"""
import logging
from ..server import get_server
from ..config import config

logger = logging.getLogger(__name__)

def main():
    """Run the MCP server with SSE transport"""
    mcp_server = get_server()

    logger.info(f"Starting MCP SSE server on {config.host}:{config.port}")
    logger.info(f"MCP SSE endpoint: http://{config.host}:{config.port}/sse")

    # Run FastMCP with SSE transport
    # This provides standard MCP SSE protocol compatible with mcp.client.sse
    mcp_server.run(
        transport="sse",
        host=config.host,
        port=config.port
    )

if __name__ == "__main__":
    main()
