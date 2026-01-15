"""Initial schema for Todo AI Chatbot.

Creates Task, Conversation, and Message tables with indexes.

Revision ID: 001_initial
Revises:
Create Date: 2026-01-06
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create tasks table
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("completed", sa.Boolean(), nullable=False, default=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_task_user_id", "tasks", ["user_id"])

    # Create conversations table
    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_conversation_user_id", "conversations", ["user_id"])

    # Create messages table
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("user", "assistant", name="messagerole"),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_message_conversation_id", "messages", ["conversation_id"])
    op.create_index("idx_message_created_at", "messages", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_message_created_at", table_name="messages")
    op.drop_index("idx_message_conversation_id", table_name="messages")
    op.drop_table("messages")

    op.drop_index("idx_conversation_user_id", table_name="conversations")
    op.drop_table("conversations")

    op.drop_index("idx_task_user_id", table_name="tasks")
    op.drop_table("tasks")

    # Drop the enum type
    op.execute("DROP TYPE IF EXISTS messagerole")
