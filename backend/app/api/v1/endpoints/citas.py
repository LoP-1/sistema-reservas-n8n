from datetime import date, datetime, time
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Cita
from app.schemas.schemas import CitaCreate, CitaResponse, DisponibilidadResponse

router = APIRouter(prefix="/citas", tags=["Citas"])

# Horarios base de atención estándar (ej. 09:00 a 17:00 en intervalos de 1 hora)
HORARIOS_LABORALES = [
    "09:00", "10:00", "11:00", "12:00",
    "14:00", "15:00", "16:00", "17:00"
]

@router.get("/disponibles", response_model=DisponibilidadResponse)
def get_citas_disponibles(
    fecha: date = Query(..., description="Fecha a consultar (YYYY-MM-DD)"),
    servicio_id: Optional[str] = Query(None, description="Identificador o nombre del servicio (opcional)"),
    db: Session = Depends(get_db)
):
    """
    Calcula y devuelve los horarios libres para una fecha dada consultando citas activas en PostgreSQL.
    """
    inicio_dia = datetime.combine(fecha, time.min)
    fin_dia = datetime.combine(fecha, time.max)

    # Filtrar citas CONFIRMADAS para ese día
    citas_ocupadas = db.query(Cita).filter(
        Cita.fecha_hora >= inicio_dia,
        Cita.fecha_hora <= fin_dia,
        Cita.estado == "CONFIRMADO"
    ).all()

    horas_ocupadas = {c.fecha_hora.strftime("%H:%M") for c in citas_ocupadas}
    horarios_libres = [h for h in HORARIOS_LABORALES if h not in horas_ocupadas]

    return DisponibilidadResponse(fecha=fecha, horarios_libres=horarios_libres)


@router.post("", response_model=CitaResponse, status_code=status.HTTP_201_CREATED)
def crear_cita(
    cita_in: CitaCreate,
    db: Session = Depends(get_db)
):
    """
    Registra una nueva reserva confirmada en la base de datos.
    Valida que el turno no esté ya ocupado en estado CONFIRMADO.
    """
    cita_existente = db.query(Cita).filter(
        Cita.fecha_hora == cita_in.fecha_hora,
        Cita.estado == "CONFIRMADO"
    ).first()

    if cita_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El horario seleccionado ya se encuentra reservado."
        )

    nueva_cita = Cita(
        cliente_nombre=cita_in.cliente_nombre,
        cliente_contacto=cita_in.cliente_contacto,
        servicio=cita_in.servicio,
        fecha_hora=cita_in.fecha_hora,
        estado="CONFIRMADO"
    )

    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita


@router.patch("/{id}/cancelar", response_model=CitaResponse)
def cancelar_cita(
    id: int,
    db: Session = Depends(get_db)
):
    """
    Actualización parcial para liberar el horario cambiando el estado a CANCELADO.
    """
    cita = db.query(Cita).filter(Cita.id == id).first()
    if not cita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cita con ID {id} no encontrada."
        )

    cita.estado = "CANCELADO"
    db.commit()
    db.refresh(cita)
    return cita
