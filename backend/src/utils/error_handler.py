"""Error translation layer for user-friendly messages.

Translates internal error codes to friendly messages.
Implements Constitution Principle IV: Graceful Error Handling.
"""
from src.errors import ErrorCode, ToolError


# User-friendly error message mappings
ERROR_MESSAGES: dict[ErrorCode, str] = {
    ErrorCode.TASK_NOT_FOUND: (
        "I couldn't find that task. Would you like me to show your current tasks?"
    ),
    ErrorCode.INVALID_TITLE: (
        "The task title seems too long. Could you shorten it a bit?"
    ),
    ErrorCode.ALREADY_COMPLETED: "That task is already marked as complete.",
    ErrorCode.NO_CHANGES: (
        "I didn't receive any changes to make. "
        "What would you like to update - the title or description?"
    ),
    ErrorCode.CONVERSATION_NOT_FOUND: (
        "I couldn't find that conversation. Let's start a new one!"
    ),
    ErrorCode.INVALID_CONVERSATION: (
        "There's an issue with this conversation. Let's start fresh!"
    ),
    ErrorCode.DATABASE_ERROR: (
        "I'm having trouble right now. Please try again in a moment."
    ),
    ErrorCode.OPENAI_ERROR: (
        "I'm having trouble right now. Please try again in a moment."
    ),
    ErrorCode.AUTH_ERROR: "Please sign in to continue.",
    ErrorCode.VALIDATION_ERROR: (
        "I didn't quite understand that. Could you rephrase your request?"
    ),
    ErrorCode.UNKNOWN_ERROR: (
        "Something unexpected happened. Please try again in a moment."
    ),
}


def get_user_friendly_message(code: ErrorCode) -> str:
    """Get user-friendly message for an error code.

    Args:
        code: Error code enum value.

    Returns:
        User-friendly error message string.
    """
    return ERROR_MESSAGES.get(code, ERROR_MESSAGES[ErrorCode.UNKNOWN_ERROR])


def translate_error(error: ToolError) -> str:
    """Translate a ToolError to user-friendly message.

    Args:
        error: ToolError instance with error code.

    Returns:
        User-friendly error message string.
    """
    return get_user_friendly_message(error.code)


def format_error_response(error: ToolError) -> dict:
    """Format error for API response.

    Returns a dictionary suitable for JSON response.
    Never exposes internal error details to users.

    Args:
        error: ToolError instance.

    Returns:
        Dictionary with 'error' boolean and 'message' string.
    """
    return {
        "error": True,
        "message": translate_error(error),
    }
