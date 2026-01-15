"""Database connection module with async SQLModel engine.

Provides stateless database connections for the Todo AI Chatbot.
Each request gets a fresh session - no state persists between requests.
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

# Load database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://localhost/todo_chatbot")

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
)

# Async session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables.

    Creates all tables defined in SQLModel metadata.
    Should be called on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db() -> None:
    """Close database connections.

    Should be called on application shutdown.
    """
    await engine.dispose()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session.

    Provides a fresh async session for each request.
    Session is automatically closed after use.

    Usage:
        async with get_session() as session:
            result = await session.execute(query)

    Yields:
        AsyncSession: Database session for executing queries.
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
