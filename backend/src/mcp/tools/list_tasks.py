"""list_tasks MCP tool implementation.

Retrieves user's tasks with optional status filtering.
Enforces Constitution Principle I: MCP-First Execution.
"""
from typing import Any, Optional

from sqlmodel import select

from src.db import get_session
from src.models import Task


async def list_tasks(
    user_id: str,
    status: Optional[str] = "all",
) -> dict[str, Any]:
    """Retrieve user's tasks with optional filtering.

    Args:
        user_id: Owner's unique identifier (required).
        status: Filter by status - "all", "pending", or "completed".
                Default is "all".

    Returns:
        Dictionary with tasks array and count.
    """
    async with get_session() as session:
        # Build query with user isolation
        query = select(Task).where(Task.user_id == user_id)

        # Apply status filter
        if status == "pending":
            query = query.where(Task.completed == False)
        elif status == "completed":
            query = query.where(Task.completed == True)
        # "all" - no additional filter

        # Order by creation time (newest first)
        query = query.order_by(Task.created_at.desc())

        result = await session.execute(query)
        tasks = result.scalars().all()

        # Format tasks for response
        task_list = [
            {
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
            }
            for task in tasks
        ]

        return {
            "tasks": task_list,
            "count": len(task_list),
        }
