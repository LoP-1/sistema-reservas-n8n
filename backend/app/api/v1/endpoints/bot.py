import logging
import httpx
from fastapi import APIRouter, BackgroundTasks, status
from app.core.config import settings
from app.schemas.schemas import TelegramUpdate

router = APIRouter(prefix="/bot", tags=["Bot / Telegram"])
logger = logging.getLogger(__name__)

async def dispatch_to_n8n(payload: dict):
    """Envía el evento a n8n en segundo plano si está configurado."""
    if not settings.N8N_WEBHOOK_URL:
        logger.info(f"N8N_WEBHOOK_URL no configurado. Mensaje recibido: {payload}")
        return

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(settings.N8N_WEBHOOK_URL, json=payload)
            logger.info(f"Despachado a n8n exitosamente. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error al enviar datos a n8n: {e}")

@router.post("/mensaje", status_code=status.HTTP_200_OK)
async def recibir_mensaje_telegram(
    update: TelegramUpdate,
    background_tasks: BackgroundTasks
):
    """
    Receptor de eventos entrantes de Telegram (Update object).
    Extrae chat.id, información del usuario y texto del mensaje,
    responde 200 OK inmediatamente y despacha a n8n en segundo plano.
    """
    datos_despacho = {
        "update_id": update.update_id,
        "chat_id": None,
        "usuario": None,
        "username": None,
        "texto": None
    }

    if update.message:
        datos_despacho["chat_id"] = update.message.chat.id
        datos_despacho["texto"] = update.message.text
        if update.message.from_:
            datos_despacho["usuario"] = update.message.from_.first_name
            datos_despacho["username"] = update.message.from_.username

    # Enviar a n8n en segundo plano sin bloquear la respuesta de Telegram
    background_tasks.add_task(dispatch_to_n8n, datos_despacho)

    return {"ok": True, "detail": "Evento recibido y encolado para procesamiento"}
