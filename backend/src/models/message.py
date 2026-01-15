"""Message SQLModel definition.

Represents a single message in a conversation.
Messages are persisted for stateless operation - history is loaded from DB per request.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class MessageRole(str, Enum):
    """Message sender role."""

    USER = "user"
    ASSISTANT = "assistant"


class MessageBase(SQLModel):
    """Base Message model with shared fields."""

    role: MessageRole
    content: str


class Message(MessageBase, table=True):
    """Message database model.

    Attributes:
        id: Unique message identifier (auto-generated).
        conversation_id: Parent conversation ID (foreign key).
        user_id: Message author's user ID.
        role: Message sender type (user or assistant).
        content: Message text content.
        created_at: Timestamp when message was created.
    """

    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class MessageCreate(MessageBase):
    """Schema for creating a new message."""

    conversation_id: int
    user_id: str


class MessageRead(MessageBase):
    """Schema for reading a message."""

    id: int
    conversation_id: int
    user_id: str
    created_at: datetime
