from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from router import router

app = FastAPI(
    title="LeadFlow API",
    description="Receives leads from the landing page and forwards them to Telegram.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

app.include_router(router)


@app.get("/health", tags=["healthcheck"])
async def health() -> dict:
    return {"status": "ok"}
