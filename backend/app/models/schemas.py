from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None


# Voice Interaction Schemas
class VoiceRequest(BaseModel):
    audio_data: Optional[str] = None  # Base64 encoded audio
    text_message: Optional[str] = None  # Alternative to audio


class VoiceResponse(BaseModel):
    text_response: str
    audio_url: Optional[str] = None
    is_emergency: bool = False
    symptoms_detected: List[str] = []
    conversation_id: int


# Appointment Schemas
class AppointmentCreate(BaseModel):
    full_name: str
    phone: str
    preferred_date: str
    preferred_time: str
    reason: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    preferred_date: str
    preferred_time: str
    reason: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Conversation Schemas
class ConversationResponse(BaseModel):
    id: int
    user_message: str
    ai_response: str
    audio_url: Optional[str]
    response_audio_url: Optional[str]
    is_emergency: bool
    symptoms_extracted: Optional[List[str]]
    llm_provider: Optional[str]
    response_time_ms: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Health Check Schema
class HealthCheck(BaseModel):
    status: str
    app_name: str
    version: str
    author: str
    timestamp: datetime
