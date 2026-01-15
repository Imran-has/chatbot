"""complete_task MCP tool implementation.

Marks a task as completed.
Enforces Constitution Principle I: MCP-First Execution.
"""
from datetime import datetime
from typing import Any

from sqlmodel import select

from src.db import get_session
from src.errors import ErrorCode, ToolError
from src.models import Task


async def complete_task(
    user_id: str,
    task_id: int,
) -> dict[str, Any]:
    """Mark a task as completed.

    Args:
        user_id: Owner's unique identifier (required).
        task_id: Task's unique identifier (required).

    Returns:
        Dictionary with task_id, status, and title.

    Raises:
        ToolError: If task not found or already completed.
    """
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

        if task.completed:
            raise ToolError(
                code=ErrorCode.ALREADY_COMPLETED,
                message=f"Task {task_id} is already completed",
            )

        # Update task
        task.completed = True
        task.updated_at = datetime.utcnow()
        session.add(task)
        await session.commit()

        return {
            "task_id": task.id,
            "status": "completed",
            "title": task.title,
        }
