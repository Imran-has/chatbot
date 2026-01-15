"""Conversation SQLModel definition.

Represents a chat session between a user and the AI assistant.
Conversations are used to maintain context across messages.
"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ConversationBase(SQLModel):
    """Base Conversation model with shared fields."""

    pass


class Conversation(ConversationBase, table=True):
    """Conversation database model.

    Attributes:
        id: Unique conversation identifier (auto-generated).
        user_id: Owner's user ID (required for user isolation).
        created_at: Timestamp when conversation was started.
        updated_at: Timestamp when conversation was last active.
    """

    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""

    user_id: str


class ConversationRead(ConversationBase):
    """Schema for reading a conversation."""

    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
