"""AI Agent module for Todo AI Chatbot.

Provides the OpenAI-powered chat agent that uses MCP tools.
"""
from .chat_agent import ChatAgent, process_message
from .prompts import SYSTEM_PROMPT

__all__ = ["ChatAgent", "process_message", "SYSTEM_PROMPT"]
