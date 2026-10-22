from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Backend Reservas & Automatización Telegram"
    VERSION: str = "1.0.0"
    API_V1_STR: str = ""  # Rutas directas según especificación: /citas, /bot, /negocio
    
    # Base de datos
    DATABASE_URL: str = "postgresql://postgres:postgrespassword@localhost:5432/automation_hub"
    
    # Webhook de n8n para despachar mensajes entrantes
    N8N_WEBHOOK_URL: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
