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
from app.models.serie import (
    SerieCreate,
    SeriePatch,
    SerieResponse,
    SerieDetalleResponse,
    SerieListResponse,
    SeriesMasivoPatchRequest,
    GeneroCreate,
    GeneroResponse,
    PlataformaCreate,
    PlataformaResponse,
)
from app.models.usuario import (
    UsuarioCreate,
    UsuarioPatch,
    UsuarioResponse,
    UsuarioPerfilCompleto,
    UsuariosListResponse,
)
from app.models.relaciones import (
    PerteneceACreate,
    PerteneceAPatch,
    TransmiteCreate,
    SimilarACreate,
    VioCreate,
    VioPatch,
    VioMasivoItem,
    VioMasivoUpdate,
    LeGustaCreate,
    LeGustaEliminarMasivo,
    EnListaCreate,
    SigueACreate,
    RelacionResponse,
    OperacionMasivaResponse,
)
from app.models.resena import (
    ResenaCreate,
    ResenaResponse,
    ResenasListResponse,
)
from app.models.consultas import (
    SerieRecomendada,
    RecomendacionesResponse,
    UsuarioInfluyente,
    UsuariosInfluyentesResponse,
    SerieRecomendadaAvanzada,
    PesosUsados,
    RecomendacionesAvanzadasResponse,
)
