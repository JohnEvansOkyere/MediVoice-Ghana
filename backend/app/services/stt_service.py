import base64
import io
from typing import Optional
from loguru import logger
from groq import Groq

from app.config import settings


class STTService:
    """Speech-to-Text service using Groq Whisper API"""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_WHISPER_API_KEY)

    async def transcribe_audio(self, audio_data: str) -> Optional[str]:
        """
        Transcribe audio from base64 encoded data

        Args:
            audio_data: Base64 encoded audio file (webm, mp3, wav, etc.)

        Returns:
            Transcribed text or None if failed
        """
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_data)

            # Create a file-like object
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.webm"  # Groq needs a filename

            # Transcribe using Groq Whisper
            transcription = self.client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                language="en",  # English only for now
                response_format="text"
            )

            logger.info(f"Audio transcribed successfully: {transcription[:50]}...")
            return transcription

        except Exception as e:
            logger.error(f"STT transcription failed: {str(e)}")
            return None

    async def transcribe_file(self, file_path: str) -> Optional[str]:
        """
        Transcribe audio from file path

        Args:
            file_path: Path to audio file

        Returns:
            Transcribed text or None if failed
        """
        try:
            with open(file_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    language="en",
                    response_format="text"
                )

            logger.info(f"File transcribed successfully: {transcription[:50]}...")
            return transcription

        except Exception as e:
            logger.error(f"STT file transcription failed: {str(e)}")
            return None


# Singleton instance
stt_service = STTService()
