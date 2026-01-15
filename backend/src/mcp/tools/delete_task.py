"""delete_task MCP tool implementation.

Permanently removes a task.
Enforces Constitution Principle I: MCP-First Execution.
"""
from typing import Any

from sqlmodel import select

from src.db import get_session
from src.errors import ErrorCode, ToolError
from src.models import Task


async def delete_task(
    user_id: str,
    task_id: int,
) -> dict[str, Any]:
    """Permanently remove a task.

    Args:
        user_id: Owner's unique identifier (required).
        task_id: Task's unique identifier (required).

    Returns:
        Dictionary with task_id, status, and title.

    Raises:
        ToolError: If task not found.
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

        # Store title before deletion
        title = task.title

        # Delete task
        await session.delete(task)
        await session.commit()

        return {
            "task_id": task_id,
            "status": "deleted",
            "title": title,
        }
