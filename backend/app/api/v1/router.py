from fastapi import APIRouter
from app.api.v1.endpoints import citas, bot, negocio

api_router = APIRouter()
api_router.include_router(citas.router)
api_router.include_router(bot.router)
api_router.include_router(negocio.router)
