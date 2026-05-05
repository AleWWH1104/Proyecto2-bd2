"""Router para usuarios.

Endpoints:
    POST   /usuarios              - Registrarse (crear nodo Usuario)
    GET    /usuarios              - Buscar otros usuarios (consultar muchos nodos)
    GET    /usuarios/{id}         - Ver perfil propio (consultar 1 nodo)
    GET    /usuarios/{id}/perfil  - Perfil completo con relaciones
    PATCH  /usuarios/{id}         - Editar perfil (gestión de propiedades de 1 nodo)
    DELETE /usuarios/{id}         - Eliminar cuenta (eliminar 1 nodo)
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models import (
    UsuarioCreate,
    UsuarioPatch,
    UsuarioResponse,
    UsuarioPerfilCompleto,
    UsuariosListResponse,
)
from app.repositories import usuarios as usuarios_repo


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.post("", response_model=UsuarioResponse, status_code=201, summary="Registrarse")
def crear_usuario(datos: UsuarioCreate):
    """Crea un usuario nuevo (registro).

    El backend genera automáticamente el `id` y la `fechaRegistro`.
    Rúbrica: Crear nodo 1 label + con propiedades.
    """
    usuario = usuarios_repo.crear(
        nombre=datos.nombre,
        email=datos.email,
        edad=datos.edad,
        activo=datos.activo,
    )
    return usuario


@router.get("", response_model=UsuariosListResponse, summary="Buscar otros usuarios")
def listar_usuarios(
    edad_min: Optional[int] = Query(None, ge=0, description="Edad mínima"),
    edad_max: Optional[int] = Query(None, le=120, description="Edad máxima"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0, description="Cantidad de registros a saltar (paginación)"),
    limit: int = Query(50, ge=1, le=200, description="Máximo de registros a devolver"),
):
    """Lista usuarios con filtros opcionales y paginación.

    Rúbrica: Consultar muchos nodos.
    """
    return usuarios_repo.listar(
        edad_min=edad_min,
        edad_max=edad_max,
        activo=activo,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{usuario_id}/perfil",
    response_model=UsuarioPerfilCompleto,
    summary="Perfil completo con relaciones",
)
def obtener_perfil_completo(usuario_id: str):
    """Devuelve el usuario junto con todas sus relaciones:
    series vistas, que le gustan, en lista, y usuarios que sigue.
    """
    perfil = usuarios_repo.obtener_perfil_completo(usuario_id)
    if perfil is None:
        raise HTTPException(status_code=404, detail=f"Usuario {usuario_id} no encontrado")
    return perfil


@router.get("/{usuario_id}", response_model=UsuarioResponse, summary="Ver perfil propio")
def obtener_usuario(usuario_id: str):
    """Devuelve los datos básicos de un usuario por su id.

    Rúbrica: Consultar 1 nodo.
    """
    usuario = usuarios_repo.obtener_por_id(usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail=f"Usuario {usuario_id} no encontrado")
    return usuario


@router.patch("/{usuario_id}", response_model=UsuarioResponse, summary="Editar perfil")
def actualizar_usuario(usuario_id: str, datos: UsuarioPatch):
    """Agrega o actualiza propiedades del usuario.

    No permite modificar `id` ni `fechaRegistro` (se filtran en el repo).
    Rúbrica: Gestión de propiedades de nodos — 1 nodo.
    """
    usuario = usuarios_repo.actualizar(usuario_id, datos.propiedades)
    if usuario is None:
        raise HTTPException(status_code=404, detail=f"Usuario {usuario_id} no encontrado")
    return usuario


@router.delete("/{usuario_id}", status_code=204, summary="Eliminar cuenta")
def eliminar_usuario(usuario_id: str):
    """Elimina un usuario y todas sus relaciones (DETACH DELETE).

    También borra: VIO, LE_GUSTA, EN_LISTA, SIGUE_A, ESCRIBIO.
    Rúbrica: Eliminar 1 nodo.
    """
    eliminado = usuarios_repo.eliminar(usuario_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail=f"Usuario {usuario_id} no encontrado")
    # status 204 = No Content, no devuelve body
