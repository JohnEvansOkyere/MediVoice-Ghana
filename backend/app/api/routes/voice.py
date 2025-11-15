import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger

from app.db.database import get_db
from app.db.models import User, Conversation
from app.models.schemas import VoiceRequest, VoiceResponse
from app.utils.auth import get_current_user
from app.services.stt_service import stt_service
from app.services.tts_service import tts_service
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service

router = APIRouter()


@router.post("/interact", response_model=VoiceResponse)
async def voice_interact(
    request: VoiceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Main voice interaction endpoint

    - Accepts audio (base64) or text input
    - Transcribes audio if provided
    - Extracts symptoms and retrieves medical knowledge
    - Generates AI response with fallback LLM chain
    - Synthesizes speech response
    - Detects emergencies
    - Stores conversation in database
    """

    start_time = time.time()

    try:
        # Step 1: Get user message (transcribe if audio)
        if request.audio_data:
            logger.info("Transcribing audio...")
            user_message = await stt_service.transcribe_audio(request.audio_data)
            if not user_message:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to transcribe audio"
                )
        elif request.text_message:
            user_message = request.text_message
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either audio_data or text_message must be provided"
            )

        logger.info(f"User message: {user_message}")

        # Step 2: Check for emergency
        is_emergency = rag_service.is_emergency(user_message)

        if is_emergency:
            emergency_response = (
                "🚨 EMERGENCY DETECTED 🚨\n\n"
                "Your symptoms suggest a medical emergency. "
                "Please call 112 immediately or visit the nearest hospital. "
                "Do not delay seeking professional medical care.\n\n"
                "If you are unable to get to a hospital, ask someone nearby to help you."
            )

            # Generate audio response
            audio_response = await tts_service.synthesize_speech(emergency_response)

            # Save conversation
            conversation = Conversation(
                user_id=current_user.id,
                user_message=user_message,
                transcription=user_message if request.audio_data else None,
                ai_response=emergency_response,
                is_emergency=True,
                llm_provider="emergency_detection",
                response_time_ms=int((time.time() - start_time) * 1000)
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            return VoiceResponse(
                text_response=emergency_response,
                audio_url=None,  # In production, save audio and return URL
                is_emergency=True,
                symptoms_detected=[],
                conversation_id=conversation.id
            )

        # Step 3: Extract symptoms
        symptoms = rag_service.extract_symptoms(user_message)
        logger.info(f"Symptoms detected: {symptoms}")

        # Step 4: Retrieve relevant medical knowledge (RAG)
        medical_context = rag_service.search(user_message, n_results=3)
        logger.info(f"Retrieved medical context ({len(medical_context)} chars)")

        # Step 5: Generate AI response with fallback chain
        ai_response, provider_used = await llm_service.generate_response(
            prompt=user_message,
            medical_context=medical_context,
            db=db
        )

        logger.info(f"AI response generated using {provider_used}")

        # Step 6: Generate audio response
        audio_response = await tts_service.synthesize_speech(ai_response)

        # Step 7: Save conversation
        response_time_ms = int((time.time() - start_time) * 1000)

        conversation = Conversation(
            user_id=current_user.id,
            user_message=user_message,
            transcription=user_message if request.audio_data else None,
            symptoms_extracted=symptoms,
            ai_response=ai_response,
            is_emergency=False,
            llm_provider=provider_used,
            response_time_ms=response_time_ms
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        logger.info(f"Conversation saved (ID: {conversation.id}, Time: {response_time_ms}ms)")

        return VoiceResponse(
            text_response=ai_response,
            audio_url=None,  # In production, save audio to storage and return URL
            is_emergency=False,
            symptoms_detected=symptoms,
            conversation_id=conversation.id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice interaction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your request"
        )
