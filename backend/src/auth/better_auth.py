"""Better Auth integration for user authentication.

Provides JWT-based authentication for the Todo AI Chatbot.
Validates that the user_id in the request path matches the authenticated user.
"""
import os
from typing import Optional

import jwt
from fastapi import HTTPException, status


# Better Auth configuration
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "development-secret-key")
ALGORITHM = "HS256"


class AuthError(Exception):
    """Authentication error."""

    pass


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token.

    Args:
        token: JWT token string.

    Returns:
        Decoded token payload.

    Raises:
        AuthError: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthError("Invalid token")


def extract_user_id(token: str) -> str:
    """Extract user_id from JWT token.

    Args:
        token: JWT token string.

    Returns:
        User ID from token payload.

    Raises:
        AuthError: If token is invalid or missing user_id.
    """
    payload = decode_token(token)
    user_id = payload.get("sub") or payload.get("user_id")
    if not user_id:
        raise AuthError("Token missing user identifier")
    return user_id


def validate_user_access(token: str, path_user_id: str) -> str:
    """Validate that authenticated user matches path user_id.

    Enforces that users can only access their own resources.

    Args:
        token: JWT token string.
        path_user_id: User ID from request path.

    Returns:
        Validated user ID.

    Raises:
        AuthError: If user doesn't match or token is invalid.
    """
    token_user_id = extract_user_id(token)
    if token_user_id != path_user_id:
        raise AuthError("Access denied: user mismatch")
    return token_user_id


def get_token_from_header(authorization: Optional[str]) -> str:
    """Extract token from Authorization header.

    Args:
        authorization: Authorization header value.

    Returns:
        JWT token string.

    Raises:
        HTTPException: If header is missing or malformed.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="authentication required",
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    return parts[1]
