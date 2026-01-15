"""update_task MCP tool implementation.

Updates task title or description.
Enforces Constitution Principle I: MCP-First Execution.
Enforces Constitution Principle VI: Minimal Data Modification.
"""
from datetime import datetime
from typing import Any, Optional

from sqlmodel import select

from src.db import get_session
from src.errors import ErrorCode, ToolError
from src.models import Task


async def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> dict[str, Any]:
    """Update task title or description.

    Only provided fields are updated - unchanged fields remain untouched.
    This implements Constitution Principle VI: Minimal Data Modification.

    Args:
        user_id: Owner's unique identifier (required).
        task_id: Task's unique identifier (required).
        title: New task title (optional).
        description: New task description (optional).

    Returns:
        Dictionary with task_id, status, and title.

    Raises:
        ToolError: If task not found or no changes provided.
    """
    # Validate at least one field is provided
    if title is None and description is None:
        raise ToolError(
            code=ErrorCode.NO_CHANGES,
            message="No changes provided",
        )

    # Validate title if provided
    if title is not None:
        title = title.strip()
        if not title:
            raise ToolError(
                code=ErrorCode.INVALID_TITLE,
                message="Title cannot be empty",
            )
        if len(title) > 500:
            raise ToolError(
                code=ErrorCode.INVALID_TITLE,
                message="Title exceeds 500 characters",
            )

    async with get_session() as session:
        # Find task with user isolation
        query = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
        )
        result = await session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            raise ToolError(
                code=ErrorCode.TASK_NOT_FOUND,
                message=f"Task {task_id} not found",
            )

        # Update only provided fields (Principle VI)
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description.strip() if description else None

        task.updated_at = datetime.utcnow()
        session.add(task)
        await session.commit()

        return {
            "task_id": task.id,
            "status": "updated",
            "title": task.title,
        }
