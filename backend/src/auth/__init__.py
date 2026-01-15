"""Authentication module for Todo AI Chatbot.

Provides FastAPI middleware and dependencies for user authentication.
"""
from typing import Optional

from fastapi import Depends, Header, HTTPException, status

from .better_auth import (
    AuthError,
    get_token_from_header,
    validate_user_access,
)


async def get_current_user(
    user_id: str,
    authorization: Optional[str] = Header(None),
) -> str:
    """FastAPI dependency for authenticated user.

    Validates that the authenticated user matches the path user_id.

    Args:
        user_id: User ID from request path.
        authorization: Authorization header with Bearer token.

    Returns:
        Validated user ID.

    Raises:
        HTTPException: If authentication fails or user doesn't match.
    """
    try:
        token = get_token_from_header(authorization)
        validated_user_id = validate_user_access(token, user_id)
        return validated_user_id
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="forbidden",
        ) from e


# For development/testing - bypasses auth when no token provided
async def get_current_user_dev(
    user_id: str,
    authorization: Optional[str] = Header(None),
) -> str:
    """Development-mode user dependency.

    In development, if no authorization header is provided,
    the path user_id is trusted directly.

    Args:
        user_id: User ID from request path.
        authorization: Optional authorization header.

    Returns:
        User ID (validated if token provided, trusted if not).
    """
    if authorization:
        return await get_current_user(user_id, authorization)
    # Development mode: trust the path user_id
    return user_id


__all__ = [
    "get_current_user",
    "get_current_user_dev",
    "AuthError",
]
