"""Router de admin.

Endpoints:
    POST /admin/cargar-csv   - Cargar todos los CSVs de data/ a Neo4j
    POST /admin/subir-csv    - Subir un CSV y agregar/actualizar registros
"""
import csv
import io
import sys
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.database import get_session


# scripts/ no es un paquete instalado: añadimos la raíz del proyecto al path
# para poder importar la lógica de carga desde scripts/seed.py.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.seed import cargar_todo, procesar_csv, TIPOS_VALIDOS  # noqa: E402


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post(
    "/cargar-csv",
    summary="Cargar nodos y relaciones desde los CSVs de data/",
)
def cargar_csv():
    """Ejecuta la carga completa desde los CSVs en `data/` hacia Neo4j.

    Crea índices, carga todos los nodos (Genero, Plataforma, EstudioProduccion,
    Actor/Director, Serie, Usuario, Resena) y todas las relaciones del esquema.

    Rúbrica: Carga de data (csv).
    """
    try:
        with get_session() as session:
            resumen = cargar_todo(session)
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Falta un CSV requerido en data/: {e.filename}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la carga: {e}")

    return {
        "mensaje": "Carga de CSVs completada correctamente",
        "total_nodos": resumen["total_nodos"],
        "total_relaciones": resumen["total_relaciones"],
    }


@router.post(
    "/subir-csv",
    summary="Subir un CSV y agregar/actualizar registros en Neo4j",
)
async def subir_csv(
    tipo: str = Form(..., description=f"Tipo de entidad o relación. Válidos: {', '.join(TIPOS_VALIDOS)}"),
    file: UploadFile = File(...),
):
    """Recibe un CSV con encabezados y hace MERGE de cada fila en Neo4j.

    Funciona para nodos (series, actores, usuarios…) y relaciones (actua_en, vio…).
    Los registros existentes se actualizan; los nuevos se crean.
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe tener extensión .csv")

    contents = await file.read()
    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError:
        text = contents.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)

    if not rows:
        raise HTTPException(status_code=400, detail="El CSV está vacío o no tiene encabezados")

    try:
        with get_session() as session:
            total = procesar_csv(session, tipo, rows)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el CSV: {e}")

    return {
        "mensaje": f"{total} registros de '{tipo}' procesados correctamente",
        "tipo": tipo,
        "total": total,
    }
