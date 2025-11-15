from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.config import settings
from app.api.routes import auth, health, voice, appointments, conversations, telegram
from app.db.database import engine, Base

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.DEBUG else "INFO"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=f"AI Voice Health Advisor for Ghana | Author: {settings.AUTHOR}",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health Check"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice Interaction"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["Conversations"])
app.include_router(telegram.router, prefix="/api/telegram", tags=["Telegram Bot"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "author": settings.AUTHOR,
        "message": "Welcome to MediVoice GH API",
        "docs": "/docs"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
