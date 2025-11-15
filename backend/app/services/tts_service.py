import os
import base64
from typing import Optional
from loguru import logger
from google.cloud import texttospeech

from app.config import settings


class TTSService:
    """Text-to-Speech service using Google Cloud TTS"""

    def __init__(self):
        # Set credentials if provided
        if settings.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS

        self.client = texttospeech.TextToSpeechClient()

        # Configure voice (Ghanaian English)
        self.voice = texttospeech.VoiceSelectionParams(
            language_code="en-GB",  # British English (closest to Ghanaian English)
            name="en-GB-Standard-A",  # Female voice
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )

        # Configure audio
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.95,  # Slightly slower for clarity
            pitch=0.0
        )

    async def synthesize_speech(self, text: str) -> Optional[str]:
        """
        Convert text to speech

        Args:
            text: Text to convert to speech

        Returns:
            Base64 encoded audio (MP3) or None if failed
        """
        try:
            # Prepare input
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )

            # Encode audio to base64
            audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')

            logger.info(f"TTS generated for text: {text[:50]}...")
            return audio_base64

        except Exception as e:
            logger.error(f"TTS synthesis failed: {str(e)}")
            return None

    async def synthesize_to_file(self, text: str, output_path: str) -> bool:
        """
        Convert text to speech and save to file

        Args:
            text: Text to convert to speech
            output_path: Path to save audio file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Prepare input
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # Perform the text-to-speech request
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )

            # Save to file
            with open(output_path, "wb") as out:
                out.write(response.audio_content)

            logger.info(f"TTS saved to file: {output_path}")
            return True

        except Exception as e:
            logger.error(f"TTS file synthesis failed: {str(e)}")
            return False


# Singleton instance
tts_service = TTSService()
