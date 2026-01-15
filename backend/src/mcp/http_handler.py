"""MCP HTTP Handler for OpenAI Agents SDK integration.

This module provides HTTP endpoints for MCP server communication,
compatible with OpenAI Agents SDK's MCPServerStreamableHttp.
"""
import json
from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse

from .server import mcp_server

router = APIRouter(prefix="/mcp", tags=["MCP"])


@router.post("")
@router.post("/")
async def mcp_endpoint(request: Request) -> Response:
    """MCP HTTP endpoint for tool execution.

    Handles JSON-RPC style requests from OpenAI Agents SDK.

    Expected request format:
    {
        "jsonrpc": "2.0",
        "method": "tools/call" | "tools/list",
        "params": {...},
        "id": 1
    }
    """
    try:
        body = await request.json()
    except Exception:
        return Response(
            content=json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": None,
            }),
            media_type="application/json",
            status_code=400,
        )

    method = body.get("method", "")
    params = body.get("params", {})
    request_id = body.get("id", 1)

    try:
        if method == "tools/list":
            # Return list of available tools
            tools = mcp_server.get_tool_definitions()
            result = {
                "tools": [
                    {
                        "name": t["function"]["name"],
                        "description": t["function"]["description"],
                        "inputSchema": t["function"]["parameters"],
                    }
                    for t in tools
                ]
            }
        elif method == "tools/call":
            # Execute a tool
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})

            result = await mcp_server.execute_tool(tool_name, tool_args)
            result = {"content": [{"type": "text", "text": json.dumps(result)}]}
        elif method == "initialize":
            # Initialize handshake
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": False},
                },
                "serverInfo": {
                    "name": "todo-ai-chatbot-mcp",
                    "version": "0.1.0",
                },
            }
        else:
            return Response(
                content=json.dumps({
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                    "id": request_id,
                }),
                media_type="application/json",
            )

        return Response(
            content=json.dumps({
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id,
            }),
            media_type="application/json",
        )

    except ValueError as e:
        return Response(
            content=json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": str(e)},
                "id": request_id,
            }),
            media_type="application/json",
        )
    except Exception as e:
        return Response(
            content=json.dumps({
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                "id": request_id,
            }),
            media_type="application/json",
        )


@router.get("/health")
async def mcp_health() -> dict[str, Any]:
    """Health check for MCP server."""
    return {
        "status": "healthy",
        "server": "todo-ai-chatbot-mcp",
        "version": "0.1.0",
        "tools_count": len(mcp_server.get_tool_definitions()),
    }
