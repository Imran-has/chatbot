"""Chat API endpoint for Todo AI Chatbot.

Implements POST /api/{user_id}/chat with stateless architecture.
All state is persisted in the database - no in-memory state.
"""
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select

from src.agent import process_message
from src.auth import get_current_user_dev
from src.db import get_session
from src.models import (
    Conversation,
    Message,
    MessageRole,
)

router = APIRouter()


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    message: str
    conversation_id: Optional[int] = None


class ToolCallResult(BaseModel):
    """Result of a tool call."""

    tool: str
    arguments: dict[str, Any]
    result: Optional[dict[str, Any]] = None
    error: Optional[dict[str, Any]] = None


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""

    conversation_id: int
    response: str
    tool_calls: list[ToolCallResult]


@router.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: str = Depends(get_current_user_dev),
) -> ChatResponse:
    """Process a chat message and return AI response.

    Stateless Request Flow:
    1. Validate user authentication
    2. Create new conversation if conversation_id is absent
    3. Fetch conversation history from database
    4. Store user message in database (before AI call)
    5. Invoke AI agent with conversation history
    6. Store assistant response in database (after AI call)
    7. Return response with conversation_id and tool_calls

    Args:
        user_id: User identifier from path.
        request: Chat request with message and optional conversation_id.
        current_user: Authenticated user from dependency.

    Returns:
        ChatResponse with conversation_id, response, and tool_calls.

    Raises:
        HTTPException: If message is missing or conversation invalid.
    """
    # Validate message is not empty
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="message is required",
        )

    async with get_session() as session:
        conversation: Optional[Conversation] = None

        # Step 2: Create or fetch conversation
        if request.conversation_id:
            # Fetch existing conversation with user validation
            query = select(Conversation).where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == user_id,
            )
            result = await session.execute(query)
            conversation = result.scalar_one_or_none()

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="conversation not found",
                )

            # Update conversation timestamp
            conversation.updated_at = datetime.utcnow()
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(conversation)
            await session.flush()  # Get the ID

        # Step 3: Fetch conversation history
        history_query = (
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc())
        )
        history_result = await session.execute(history_query)
        messages = history_result.scalars().all()

        # Build conversation history for agent
        conversation_history = [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]

        # Step 4: Store user message BEFORE AI call (crash recovery)
        user_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=MessageRole.USER,
            content=request.message.strip(),
            created_at=datetime.utcnow(),
        )
        session.add(user_message)
        await session.flush()

        # Step 5: Invoke AI agent with history
        try:
            agent_result = await process_message(
                user_id=user_id,
                message=request.message.strip(),
                conversation_history=conversation_history,
            )
        except Exception as e:
            # Handle AI errors gracefully
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="something went wrong",
            )

        # Step 6: Store assistant response AFTER AI call
        assistant_message = Message(
            conversation_id=conversation.id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content=agent_result["response"],
            created_at=datetime.utcnow(),
        )
        session.add(assistant_message)

        # Commit all changes
        await session.commit()

        # Step 7: Return response
        return ChatResponse(
            conversation_id=conversation.id,
            response=agent_result["response"],
            tool_calls=[
                ToolCallResult(**tc) for tc in agent_result["tool_calls"]
            ],
        )
