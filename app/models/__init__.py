"""Re-exportaciones para que los imports queden limpios.

En lugar de:
    from app.models.usuario import UsuarioCreate
    from app.models.serie import SerieCreate

Puedes hacer:
    from app.models import UsuarioCreate, SerieCreate
"""
from app.models.common import (
    IdsRequest,
    PropiedadesRequest,
    EliminarPropiedadesRequest,
)
from app.models.usuario import (
    UsuarioCreate,
    UsuarioResponse,
    UsuarioPerfilCompleto,
    UsuariosListResponse,
)
from app.models.relaciones import (
    VioCreate,
    VioMasivoItem,
    VioMasivoUpdate,
    LeGustaCreate,
    LeGustaEliminarMasivo,
    EnListaCreate,
    SigueACreate,
    RelacionResponse,
    OperacionMasivaResponse,
)
# Cuando se vayan agregando los demás:
# from app.models.serie import SerieCreate, SerieResponse, ...
# from app.models.resena import ResenaCreate, ResenaResponse, ...