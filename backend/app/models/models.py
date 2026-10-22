from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base

class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_nombre = Column(String(255), nullable=False)
    cliente_contacto = Column(String(255), nullable=False)
    servicio = Column(String(255), nullable=False)
    fecha_hora = Column(DateTime, nullable=False, index=True)
    estado = Column(String(50), nullable=False, default="CONFIRMADO", index=True)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)

class NegocioInformacion(Base):
    __tablename__ = "negocio_informacion"

    id = Column(Integer, primary_key=True, index=True)
    seccion = Column(String(100), nullable=False, index=True)
    contenido = Column(Text, nullable=False)
