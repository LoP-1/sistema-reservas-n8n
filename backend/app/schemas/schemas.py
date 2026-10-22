from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field

# --- Citas ---
class CitaCreate(BaseModel):
    cliente_nombre: str = Field(..., example="Carlos Perez")
    cliente_contacto: str = Field(..., example="@carlosperez / +51999888777")
    servicio: str = Field(..., example="Consulta General")
    fecha_hora: datetime = Field(..., example="2026-10-15T10:00:00")

class CitaResponse(BaseModel):
    id: int
    cliente_nombre: str
    cliente_contacto: str
    servicio: str
    fecha_hora: datetime
    estado: str
    creado_en: datetime

    class Config:
        from_attributes = True

class DisponibilidadResponse(BaseModel):
    fecha: date
    horarios_libres: List[str]


# --- Bot / Telegram ---
class TelegramFrom(BaseModel):
    id: int
    first_name: Optional[str] = None
    username: Optional[str] = None

class TelegramChat(BaseModel):
    id: int
    type: Optional[str] = "private"

class TelegramMessage(BaseModel):
    message_id: int
    from_: Optional[TelegramFrom] = Field(None, alias="from")
    chat: TelegramChat
    text: Optional[str] = None

    class Config:
        populate_by_name = True

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None


# --- Negocio ---
class NegocioDatosCreate(BaseModel):
    seccion: str = Field(..., example="Precios")
    contenido: str = Field(..., example="Consulta general S/ 50...")

class NegocioDatosResponse(BaseModel):
    id: int
    seccion: str
    contenido: str

    class Config:
        from_attributes = True

class NegocioPreguntaRequest(BaseModel):
    pregunta: str = Field(..., example="¿Cuánto cuesta la consulta?")

class NegocioPreguntaResponse(BaseModel):
    pregunta: str
    seccion: Optional[str] = None
    contenido: str
