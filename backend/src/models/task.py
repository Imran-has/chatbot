"""Task SQLModel definition.

Represents a user's todo item in the database.
All task operations are performed via MCP tools - never directly.
"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class TaskBase(SQLModel):
    """Base Task model with shared fields."""

    title: str = Field(max_length=500, index=False)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    """Task database model.

    Attributes:
        id: Unique task identifier (auto-generated).
        user_id: Owner's user ID (required for user isolation).
        title: Task title (1-500 characters).
        description: Optional task description.
        completed: Whether task is completed (default: False).
        created_at: Timestamp when task was created.
        updated_at: Timestamp when task was last modified.
    """

    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskCreate(TaskBase):
    """Schema for creating a new task."""

    pass


class TaskRead(TaskBase):
    """Schema for reading a task."""

    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime


class TaskUpdate(SQLModel):
    """Schema for updating a task.

    All fields are optional - only provided fields are updated.
    This enforces Constitution Principle VI: Minimal Data Modification.
    """

    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None)
