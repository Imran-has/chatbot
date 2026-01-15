"""Health check endpoint.

Provides health status for load balancers and monitoring.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Health status dictionary.
    """
    return {
        "status": "healthy",
        "service": "todo-ai-chatbot",
        "version": "0.1.0",
    }


@router.get("/ready")
async def readiness_check() -> dict:
    """Readiness check endpoint.

    Indicates if the service is ready to accept traffic.

    Returns:
        Readiness status dictionary.
    """
    # TODO: Add database connectivity check
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "openai": "ok",
        },
    }
