"""MCP Server setup using official MCP Python SDK.

The MCP server provides 5 stateless tools for task management:
- add_task: Create a new task
- list_tasks: Retrieve tasks with optional filtering
- complete_task: Mark a task as completed
- delete_task: Remove a task
- update_task: Modify task title or description

All tools enforce user isolation via user_id parameter.
No state is stored in the MCP server - each call is independent.
"""
from typing import Any

from .tools import (
    add_task,
    complete_task,
    delete_task,
    list_tasks,
    update_task,
)


class MCPServer:
    """Stateless MCP Server for Todo AI Chatbot.

    Provides tool registration and execution for the AI agent.
    Each tool invocation is independent - no state persists between calls.
    """

    def __init__(self) -> None:
        """Initialize MCP server with registered tools."""
        self._tools: dict[str, Any] = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "delete_task": delete_task,
            "update_task": update_task,
        }

    def get_tool_definitions(self) -> list[dict[str, Any]]:
        """Get OpenAI-compatible tool definitions.

        Returns tool schemas for use with OpenAI Agents SDK.

        Returns:
            List of tool definitions with name, description, and parameters.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "add_task",
                    "description": "Create a new task for the user",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The user's unique identifier",
                            },
                            "title": {
                                "type": "string",
                                "description": "Task title (1-500 characters)",
                            },
                            "description": {
                                "type": "string",
                                "description": "Optional task description",
                            },
                        },
                        "required": ["user_id", "title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "Retrieve user's tasks with optional status filter",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The user's unique identifier",
                            },
                            "status": {
                                "type": "string",
                                "enum": ["all", "pending", "completed"],
                                "description": "Filter by task status (default: all)",
                            },
                        },
                        "required": ["user_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "complete_task",
                    "description": "Mark a task as completed",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The user's unique identifier",
                            },
                            "task_id": {
                                "type": "integer",
                                "description": "The task's unique identifier",
                            },
                        },
                        "required": ["user_id", "task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Permanently remove a task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The user's unique identifier",
                            },
                            "task_id": {
                                "type": "integer",
                                "description": "The task's unique identifier",
                            },
                        },
                        "required": ["user_id", "task_id"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update task title or description",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The user's unique identifier",
                            },
                            "task_id": {
                                "type": "integer",
                                "description": "The task's unique identifier",
                            },
                            "title": {
                                "type": "string",
                                "description": "New task title (optional)",
                            },
                            "description": {
                                "type": "string",
                                "description": "New task description (optional)",
                            },
                        },
                        "required": ["user_id", "task_id"],
                    },
                },
            },
        ]

    async def execute_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool by name with given arguments.

        Each tool execution is stateless - creates fresh DB session.

        Args:
            name: Tool name to execute.
            arguments: Tool arguments as dictionary.

        Returns:
            Tool execution result.

        Raises:
            ValueError: If tool name is not found.
        """
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")

        tool_fn = self._tools[name]
        return await tool_fn(**arguments)


# Global MCP server instance
mcp_server = MCPServer()


def get_tools() -> list[dict[str, Any]]:
    """Get OpenAI-compatible tool definitions.

    Convenience function for use with OpenAI Agents SDK.

    Returns:
        List of tool definitions.
    """
    return mcp_server.get_tool_definitions()
