"""Error codes and definitions for Todo AI Chatbot.

Provides structured error handling with user-friendly messages.
Errors are translated to friendly messages per Constitution Principle IV.
"""
from enum import Enum
from typing import Optional


class ErrorCode(str, Enum):
    """Error codes for MCP tool operations."""

    # Task errors
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    INVALID_TITLE = "INVALID_TITLE"
    ALREADY_COMPLETED = "ALREADY_COMPLETED"
    NO_CHANGES = "NO_CHANGES"

    # Conversation errors
    CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
    INVALID_CONVERSATION = "INVALID_CONVERSATION"

    # General errors
    DATABASE_ERROR = "DATABASE_ERROR"
    OPENAI_ERROR = "OPENAI_ERROR"
    AUTH_ERROR = "AUTH_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class ToolError(Exception):
    """Exception raised by MCP tools.

    Contains error code for translation to user-friendly message.
    """

    def __init__(
        self,
        code: ErrorCode,
        message: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        """Initialize ToolError.

        Args:
            code: Error code enum value.
            message: Optional internal message for logging.
            details: Optional additional details.
        """
        self.code = code
        self.message = message or code.value
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert error to dictionary for API response.

        Returns:
            Error dictionary with code and details.
        """
        return {
            "error": True,
            "code": self.code.value,
            "details": self.details,
        }
