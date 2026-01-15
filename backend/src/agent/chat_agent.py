"""Chat Agent implementation using OpenAI Agents SDK.

The agent acts as a decision-maker only - it detects intent and selects tools.
It does NOT access the database directly (Constitution Principle I).

Uses OpenAI Agents SDK with MCP server integration for tool execution.
"""
import os
from typing import Any, Optional

from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

from .prompts import SYSTEM_PROMPT


class ChatAgent:
    """OpenAI Agents SDK-powered chat agent for Todo management.

    The agent:
    - Receives conversation history
    - Detects user intent from natural language
    - Uses MCP server tools via OpenAI Agents SDK
    - Formats confirmation responses

    The agent does NOT:
    - Store any state (stateless per Constitution Principle III)
    - Access database directly (MCP-first per Principle I)
    """

    def __init__(self) -> None:
        """Initialize the chat agent."""
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        # MCP server URL - internal endpoint
        self.mcp_server_url = os.getenv(
            "MCP_SERVER_URL",
            "http://localhost:8000/mcp"
        )

    async def process_message(
        self,
        user_id: str,
        message: str,
        conversation_history: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Process a user message and generate a response.

        Args:
            user_id: The user's unique identifier.
            message: The user's message text.
            conversation_history: Previous messages in the conversation.

        Returns:
            Dictionary with 'response' (str) and 'tool_calls' (list).
        """
        # Build context from conversation history
        context_messages = []
        for msg in conversation_history:
            context_messages.append(f"{msg['role'].capitalize()}: {msg['content']}")

        # Create context string
        context = "\n".join(context_messages) if context_messages else ""

        # Build the full prompt with user context
        full_prompt = f"""User ID: {user_id}

Previous conversation:
{context}

Current message: {message}"""

        tool_calls_result = []

        try:
            # Connect to MCP server via HTTP
            async with MCPServerStreamableHttp(
                name="Todo MCP Server",
                params={
                    "url": self.mcp_server_url,
                    "timeout": 30,
                },
                cache_tools_list=True,
            ) as mcp_server:
                # Create agent with MCP tools
                agent = Agent(
                    name="Todo Assistant",
                    instructions=SYSTEM_PROMPT,
                    mcp_servers=[mcp_server],
                    model=self.model,
                )

                # Run the agent
                result = await Runner.run(
                    agent,
                    full_prompt,
                )

                response_text = result.final_output or ""

                # Extract tool calls from result if available
                if hasattr(result, 'raw_responses'):
                    for response in result.raw_responses:
                        if hasattr(response, 'tool_calls') and response.tool_calls:
                            for tc in response.tool_calls:
                                tool_calls_result.append({
                                    "tool": tc.function.name if hasattr(tc, 'function') else str(tc),
                                    "status": "executed",
                                })

        except Exception as e:
            # Fallback: if MCP connection fails, return error message
            response_text = f"I'm having trouble connecting to the task service. Please try again. Error: {str(e)}"

        return {
            "response": response_text,
            "tool_calls": tool_calls_result,
        }


# Global agent instance
_agent: Optional[ChatAgent] = None


def get_agent() -> ChatAgent:
    """Get or create the global chat agent instance.

    Returns:
        ChatAgent instance.
    """
    global _agent
    if _agent is None:
        _agent = ChatAgent()
    return _agent


async def process_message(
    user_id: str,
    message: str,
    conversation_history: list[dict[str, str]],
) -> dict[str, Any]:
    """Process a user message through the chat agent.

    Convenience function for the global agent.

    Args:
        user_id: The user's unique identifier.
        message: The user's message text.
        conversation_history: Previous messages in the conversation.

    Returns:
        Dictionary with 'response' and 'tool_calls'.
    """
    agent = get_agent()
    return await agent.process_message(user_id, message, conversation_history)
