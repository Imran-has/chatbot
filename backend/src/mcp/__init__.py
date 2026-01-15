"""MCP (Model Context Protocol) server module.

Provides stateless tools for AI agent to interact with the database.
The AI agent NEVER accesses the database directly - only through these tools.

Includes HTTP handler for OpenAI Agents SDK integration.
"""
from .server import mcp_server, get_tools
from .http_handler import router as mcp_router

__all__ = ["mcp_server", "get_tools", "mcp_router"]
