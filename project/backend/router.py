from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from schemas import LeadRequest, LeadResponse
from telegram import send_lead_to_telegram

router = APIRouter()


@router.post(
    "/leads",
    response_model=LeadResponse,
    summary="Submit a new lead",
    response_description="Confirmation that the lead was received and forwarded.",
)
async def create_lead(body: LeadRequest) -> JSONResponse:
    """
    Accept a lead (name + phone), forward it to Telegram, and return a success response.
    Returns HTTP 502 if the Telegram notification fails.
    """
    try:
        await send_lead_to_telegram(name=body.name, phone=body.phone)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail={"ok": False, "message": "Не вдалося надіслати повідомлення. Спробуйте пізніше."},
        ) from exc

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "message": "Дякуємо! Ми зв'яжемося з вами найближчим часом.",
        },
    )
