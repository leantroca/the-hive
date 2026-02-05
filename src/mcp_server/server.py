"""The Hive MCP Server - Main server implementation"""
from fastmcp import FastMCP
import logging

from .config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP(
    name=config.server_name,
    version=config.version,
)

# Import tools to register them via decorators
# This must happen AFTER mcp instance is created
from . import tools  # noqa: F401, E402

def get_server():
    """Factory function to get the MCP server instance"""
    logger.info(f"MCP Server '{config.server_name}' v{config.version} initialized")
    return mcp
