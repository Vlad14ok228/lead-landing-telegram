import html
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException

from config import settings


TELEGRAM_API_BASE = "https://api.telegram.org/bot{token}/sendMessage"


def _build_message(name: str, phone: str) -> str:
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return (
        "🆕 <b>Новий клієнт!</b>\n"
        f"👤 <b>Ім'я:</b> {html.escape(name)}\n"
        f"📞 <b>Телефон:</b> {html.escape(phone)}\n"
        f"🕐 <b>Час:</b> {now_utc}"
    )


async def send_lead_to_telegram(name: str, phone: str) -> None:
    """Send lead notification to Telegram chat. Raises HTTPException(502) on failure."""
    url = TELEGRAM_API_BASE.format(token=settings.telegram_bot_token)
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": _build_message(name, phone),
        "parse_mode": "HTML",
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "ok": False,
                "message": "Не вдалося надіслати повідомлення. Спробуйте пізніше.",
            },
        ) from exc
