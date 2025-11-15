from fastapi import APIRouter, Request, HTTPException
from loguru import logger

from app.config import settings
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service

router = APIRouter()


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """
    Telegram bot webhook endpoint

    Setup instructions:
    1. Create bot with @BotFather on Telegram
    2. Get bot token
    3. Set webhook: https://api.telegram.org/bot<TOKEN>/setWebhook?url=<YOUR_BACKEND_URL>/api/telegram/webhook
    """

    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=404, detail="Telegram bot not configured")

    try:
        data = await request.json()
        logger.info(f"Telegram webhook data: {data}")

        # Extract message
        if "message" not in data:
            return {"ok": True}

        message = data["message"]
        chat_id = message["chat"]["id"]
        user_message = message.get("text", "")

        if not user_message:
            return {"ok": True}

        # Check for emergency
        is_emergency = rag_service.is_emergency(user_message)

        if is_emergency:
            response_text = (
                "🚨 EMERGENCY DETECTED 🚨\n\n"
                "Your symptoms suggest a medical emergency. "
                "Please call 112 immediately or visit the nearest hospital. "
                "Do not delay seeking professional medical care."
            )
        else:
            # Get medical context and generate response
            medical_context = rag_service.search(user_message, n_results=3)
            response_text, _ = await llm_service.generate_response(
                prompt=user_message,
                medical_context=medical_context,
                db=None  # No DB session for telegram
            )

        # Send response back to user
        import httpx
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": response_text,
                    "parse_mode": "Markdown"
                }
            )

        return {"ok": True}

    except Exception as e:
        logger.error(f"Telegram webhook error: {str(e)}")
        return {"ok": False, "error": str(e)}


@router.get("/info")
async def telegram_info():
    """Get Telegram bot information"""

    if not settings.TELEGRAM_BOT_TOKEN:
        raise HTTPException(status_code=404, detail="Telegram bot not configured")

    return {
        "configured": True,
        "setup_instructions": [
            "1. Create bot with @BotFather on Telegram",
            "2. Get bot token and add to .env",
            f"3. Set webhook: https://api.telegram.org/bot<TOKEN>/setWebhook?url=<YOUR_BACKEND_URL>/api/telegram/webhook",
            "4. Test by sending a message to your bot"
        ]
    }
