"""add_task MCP tool implementation.

Creates a new task for a user.
Enforces Constitution Principle I: MCP-First Execution.
"""
from datetime import datetime
from typing import Any, Optional

from sqlmodel import select

from src.db import get_session
from src.errors import ErrorCode, ToolError
from src.models import Task


async def add_task(
    user_id: str,
    title: str,
    description: Optional[str] = None,
) -> dict[str, Any]:
    """Create a new task for the user.

    Args:
        user_id: Owner's unique identifier (required).
        title: Task title, 1-500 characters (required).
        description: Optional task description.

    Returns:
        Dictionary with task_id, status, and title.

    Raises:
        ToolError: If title is invalid.
    """
    # Validate title
    if not title or not title.strip():
        raise ToolError(
            code=ErrorCode.INVALID_TITLE,
            message="Title cannot be empty",
        )

    title = title.strip()
    if len(title) > 500:
        raise ToolError(
            code=ErrorCode.INVALID_TITLE,
            message="Title exceeds 500 characters",
        )

    # Create task in database
    async with get_session() as session:
        task = Task(
            user_id=user_id,
            title=title,
            description=description.strip() if description else None,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title,
        }
