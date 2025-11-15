import time
import httpx
from typing import Optional, Tuple
from loguru import logger
from openai import OpenAI
import google.generativeai as genai
from groq import Groq

from app.config import settings
from app.db.models import LLMLog
from sqlalchemy.orm import Session


class LLMService:
    """LLM service with fallback chain: Grok -> Groq -> Gemini"""

    def __init__(self):
        self.disclaimer = "\n\n⚠️ **DISCLAIMER**: This is not medical advice. Please consult a qualified healthcare professional for proper diagnosis and treatment."

    async def generate_response(
        self,
        prompt: str,
        medical_context: str = "",
        db: Optional[Session] = None
    ) -> Tuple[str, str]:
        """
        Generate response with fallback chain
        Returns: (response_text, provider_used)
        """

        full_prompt = self._build_prompt(prompt, medical_context)

        # Try Grok (xAI) first
        if settings.XAI_API_KEY:
            response = await self._try_grok(full_prompt, db)
            if response:
                return response + self.disclaimer, "grok"

        # Fallback to Groq
        if settings.GROQ_API_KEY:
            response = await self._try_groq(full_prompt, db)
            if response:
                return response + self.disclaimer, "groq"

        # Final fallback to Gemini
        if settings.GOOGLE_API_KEY:
            response = await self._try_gemini(full_prompt, db)
            if response:
                return response + self.disclaimer, "gemini"

        # All failed
        logger.error("All LLM providers failed")
        return "I apologize, but I'm experiencing technical difficulties. Please try again later." + self.disclaimer, "none"

    def _build_prompt(self, user_message: str, medical_context: str = "") -> str:
        """Build the full prompt with system instructions and context"""

        system_prompt = """You are MediVoice GH, an AI health advisor for Ghana.

Your role:
- Provide helpful, accurate health information
- Use simple language (assume Grade 8 reading level)
- Be culturally sensitive to Ghanaian context
- Recommend seeking professional medical care when appropriate
- Focus on common conditions in Ghana (Malaria, Typhoid, Cholera, etc.)

Guidelines:
- Keep responses concise (2-3 paragraphs max)
- If symptoms suggest emergency, CLEARLY state: "EMERGENCY: Please call 112 or visit the nearest hospital immediately"
- For serious conditions, recommend seeing a doctor
- Provide first aid advice when appropriate
- Be empathetic and supportive

Remember: You are an information tool, not a replacement for medical professionals."""

        if medical_context:
            return f"""{system_prompt}

MEDICAL KNOWLEDGE CONTEXT:
{medical_context}

USER MESSAGE:
{user_message}

Provide a helpful response based on the context above:"""
        else:
            return f"""{system_prompt}

USER MESSAGE:
{user_message}

Provide a helpful response:"""

    async def _try_grok(self, prompt: str, db: Optional[Session]) -> Optional[str]:
        """Try Grok (xAI) API"""
        start_time = time.time()
        try:
            client = OpenAI(
                api_key=settings.XAI_API_KEY,
                base_url=settings.XAI_API_BASE
            )

            response = client.chat.completions.create(
                model="grok-beta",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            # Log success
            if db:
                self._log_llm_call(
                    db=db,
                    provider="grok",
                    model="grok-beta",
                    response_time_ms=response_time_ms,
                    success=True
                )

            logger.info(f"Grok response generated in {response_time_ms}ms")
            return response.choices[0].message.content

        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            logger.warning(f"Grok failed: {str(e)}")

            # Log failure
            if db:
                self._log_llm_call(
                    db=db,
                    provider="grok",
                    model="grok-beta",
                    response_time_ms=response_time_ms,
                    success=False,
                    error_message=str(e)
                )
            return None

    async def _try_groq(self, prompt: str, db: Optional[Session]) -> Optional[str]:
        """Try Groq API"""
        start_time = time.time()
        try:
            client = Groq(api_key=settings.GROQ_API_KEY)

            response = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            # Log success
            if db:
                self._log_llm_call(
                    db=db,
                    provider="groq",
                    model="llama-3.1-70b-versatile",
                    response_time_ms=response_time_ms,
                    success=True
                )

            logger.info(f"Groq response generated in {response_time_ms}ms")
            return response.choices[0].message.content

        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            logger.warning(f"Groq failed: {str(e)}")

            # Log failure
            if db:
                self._log_llm_call(
                    db=db,
                    provider="groq",
                    model="llama-3.1-70b-versatile",
                    response_time_ms=response_time_ms,
                    success=False,
                    error_message=str(e)
                )
            return None

    async def _try_gemini(self, prompt: str, db: Optional[Session]) -> Optional[str]:
        """Try Gemini API"""
        start_time = time.time()
        try:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')

            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500
                )
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            # Log success
            if db:
                self._log_llm_call(
                    db=db,
                    provider="gemini",
                    model="gemini-1.5-flash",
                    response_time_ms=response_time_ms,
                    success=True
                )

            logger.info(f"Gemini response generated in {response_time_ms}ms")
            return response.text

        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            logger.warning(f"Gemini failed: {str(e)}")

            # Log failure
            if db:
                self._log_llm_call(
                    db=db,
                    provider="gemini",
                    model="gemini-1.5-flash",
                    response_time_ms=response_time_ms,
                    success=False,
                    error_message=str(e)
                )
            return None

    def _log_llm_call(
        self,
        db: Session,
        provider: str,
        model: str,
        response_time_ms: int,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Log LLM API call"""
        try:
            log_entry = LLMLog(
                provider=provider,
                model=model,
                response_time_ms=response_time_ms,
                success=success,
                error_message=error_message
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log LLM call: {str(e)}")


# Singleton instance
llm_service = LLMService()
