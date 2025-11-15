from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "MediVoice GH"
    AUTHOR: str = "JOHN EVANS OKYERE"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # LLM APIs - Fallback Chain
    XAI_API_KEY: str = ""
    XAI_API_BASE: str = "https://api.x.ai/v1"
    GROQ_API_KEY: str
    GOOGLE_API_KEY: str

    # STT
    GROQ_WHISPER_API_KEY: str

    # TTS
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    GCP_PROJECT_ID: str = ""

    # n8n Integration
    N8N_WEBHOOK_URL: str
    N8N_API_KEY: str = ""

    # Telegram (Optional)
    TELEGRAM_BOT_TOKEN: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
