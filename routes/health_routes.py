from fastapi import APIRouter
from datetime import datetime
from loguru import logger

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.debug("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ComicCraft API"
    }

@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ComicCraft - AI-Powered Comic Generation",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "comics": "/api/v1/comics",
            "docs": "/docs"
        }
    }
