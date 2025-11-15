from fastapi import APIRouter
from datetime import datetime
from app.config import settings
from app.models.schemas import HealthCheck

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="healthy",
        app_name=settings.APP_NAME,
        version=settings.VERSION,
        author=settings.AUTHOR,
        timestamp=datetime.utcnow()
    )
