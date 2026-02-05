"""Configuration management for MCP server"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class MCPConfig(BaseSettings):
    """MCP Server Configuration"""

    model_config = SettingsConfigDict(
        env_prefix="MCP_",
        env_file=".env",
        # env_file=".local.env",
    )

    # Server settings
    server_name: str = "the-hive-mcp"
    version: str = "0.1.0"

    # HTTP settings
    host: str = "0.0.0.0"
    port: int = 8080

    # Data directory for file operations
    data_dir: Path = Path("/app/data")

    # Feature flags
    enable_example_tools: bool = True

config = MCPConfig()
