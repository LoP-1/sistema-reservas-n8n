import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.models import NegocioInformacion
from app.schemas.schemas import (
    NegocioDatosCreate,
    NegocioDatosResponse,
    NegocioPreguntaRequest,
    NegocioPreguntaResponse
)

router = APIRouter(prefix="/negocio", tags=["Negocio / Base de Conocimiento"])

@router.post("/datos", response_model=NegocioDatosResponse, status_code=status.HTTP_201_CREATED)
def agregar_datos_negocio(
    datos_in: NegocioDatosCreate,
    db: Session = Depends(get_db)
):
    """
    Ingesta de información operativa del negocio (horarios, precios, servicios, FAQ).
    """
    registro = NegocioInformacion(
        seccion=datos_in.seccion,
        contenido=datos_in.contenido
    )
    db.add(registro)
    db.commit()
    db.refresh(registro)
    return registro

@router.post("/preguntar", response_model=NegocioPreguntaResponse)
def consultar_conocimiento_negocio(
    consulta: NegocioPreguntaRequest,
    db: Session = Depends(get_db)
):
    """
    Búsqueda directa sobre la información del negocio en PostgreSQL.
    Devuelve la información relevante para que n8n / IA elabore la respuesta final.
    """
    pregunta_texto = consulta.pregunta.lower()

    # Extraer palabras clave mayores a 3 letras
    palabras_clave = [p for p in re.findall(r'\w+', pregunta_texto) if len(p) > 3]

    query = db.query(NegocioInformacion)

    if palabras_clave:
        filtros = []
        for palabra in palabras_clave:
            filtros.append(NegocioInformacion.contenido.ilike(f"%{palabra}%"))
            filtros.append(NegocioInformacion.seccion.ilike(f"%{palabra}%"))
        resultado = query.filter(or_(*filtros)).first()
    else:
        resultado = query.first()

    if not resultado:
        # Si no hay match específico, devolver el primer registro o mensaje explicativo
        primer_registro = db.query(NegocioInformacion).first()
        if primer_registro:
            return NegocioPreguntaResponse(
                pregunta=consulta.pregunta,
                seccion=primer_registro.seccion,
                contenido=primer_registro.contenido
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró información del negocio cargada en la base de datos."
        )

    return NegocioPreguntaResponse(
        pregunta=consulta.pregunta,
        seccion=resultado.seccion,
        contenido=resultado.contenido
    )
