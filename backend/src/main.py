"""FastAPI application entry point.

Main application module for Todo AI Chatbot.
Configures CORS, routers, and lifecycle events.
"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import api_router
from src.db import close_db, init_db
from src.mcp import mcp_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI application
app = FastAPI(
    title="Todo AI Chatbot",
    description="AI-powered task management via natural language chat",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)

# Include MCP router for OpenAI Agents SDK integration
app.include_router(mcp_router)


@app.get("/")
async def root() -> dict:
    """Root endpoint.

    Returns:
        Welcome message.
    """
    return {
        "message": "Todo AI Chatbot API",
        "docs": "/docs",
        "health": "/health",
    }
