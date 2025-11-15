from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    """Conversation model - stores each interaction"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Input
    user_message = Column(Text, nullable=False)
    audio_url = Column(String(500), nullable=True)  # URL to stored audio file

    # Processing
    transcription = Column(Text, nullable=True)
    symptoms_extracted = Column(JSON, nullable=True)  # List of symptoms

    # Response
    ai_response = Column(Text, nullable=False)
    response_audio_url = Column(String(500), nullable=True)

    # Metadata
    is_emergency = Column(Boolean, default=False)
    llm_provider = Column(String(50), nullable=True)  # Which LLM was used
    response_time_ms = Column(Integer, nullable=True)  # Response time in milliseconds

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="conversations")


class Appointment(Base):
    """Appointment model"""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Appointment details
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    preferred_date = Column(String(100), nullable=False)
    preferred_time = Column(String(100), nullable=False)
    reason = Column(Text, nullable=True)

    # Status tracking
    status = Column(String(50), default="pending")  # pending, confirmed, cancelled
    n8n_response = Column(JSON, nullable=True)  # Response from n8n webhook

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="appointments")


class LLMLog(Base):
    """LLM call logging for monitoring"""
    __tablename__ = "llm_logs"

    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String(50), nullable=False)  # grok, groq, gemini
    model = Column(String(100), nullable=False)

    # Request
    prompt_tokens = Column(Integer, nullable=True)

    # Response
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=False)

    # Status
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
