"""Router para usuarios.

Define los endpoints HTTP de esta entidad.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioPerfilCompleto,
    UsuariosListResponse,
)
from app.repositories import usuarios as usuarios_repo


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("", response_model=UsuariosListResponse, summary="Listar usuarios con filtros")
def listar_usuarios(
    edad_min: Optional[int] = Query(None, ge=0, description="Edad mínima"),
    edad_max: Optional[int] = Query(None, le=120, description="Edad máxima"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0, description="Cantidad de registros a saltar (paginación)"),
    limit: int = Query(50, ge=1, le=200, description="Máximo de registros a devolver"),
):
    """Lista usuarios con filtros opcionales.

    Soporta paginación con `skip` y `limit`.
    """
    return usuarios_repo.listar(
        edad_min=edad_min,
        edad_max=edad_max,
        activo=activo,
        skip=skip,
        limit=limit,
    )


@router.get("/{usuario_id}", response_model=UsuarioPerfilCompleto, summary="Perfil completo")
def obtener_perfil(usuario_id: str):
    """Devuelve un usuario con todas sus relaciones:
    series vistas, que le gustan, en lista, y usuarios que sigue.
    """
    perfil = usuarios_repo.obtener_perfil_completo(usuario_id)
    if perfil is None:
        raise HTTPException(status_code=404, detail=f"Usuario {usuario_id} no encontrado")
    return perfil


@router.post("", response_model=UsuarioResponse, status_code=201, summary="Crear usuario")
def crear_usuario(datos: UsuarioCreate):
    """Crea un usuario nuevo.

    El backend genera automáticamente el `id` y la `fechaRegistro`.
    """
    usuario = usuarios_repo.crear(
        nombre=datos.nombre,
        email=datos.email,
        edad=datos.edad,
        activo=datos.activo,
    )
    return usuario


@router.delete("/{usuario_id}", status_code=204, summary="Eliminar usuario")
def eliminar_usuario(usuario_id: str):
    """Elimina un usuario y todas sus relaciones.

    Usa DETACH DELETE en Neo4j, así que también borra:
    VIO, LE_GUSTA, EN_LISTA, SIGUE_A, ESCRIBIO.
    """
    eliminado = usuarios_repo.eliminar(usuario_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail=f"Usuario {usuario_id} no encontrado")
    # status 204 = No Content, no devuelve body
