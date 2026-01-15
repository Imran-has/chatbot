"""API module for Todo AI Chatbot.

Provides FastAPI routers for all endpoints.
"""
from fastapi import APIRouter

from .chat import router as chat_router
from .health import router as health_router

# Main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(health_router, tags=["health"])
api_router.include_router(chat_router, tags=["chat"])

__all__ = ["api_router"]
