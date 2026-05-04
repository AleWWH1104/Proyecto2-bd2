import pytest

from app import repositories


SERIE_RESPONSE = {
    "id": "serie-1",
    "titulo": "Dark Matter",
    "sinopsis": "Ciencia ficción.",
    "anio": 2024,
    "calificacion": 4.8,
    "numTemporadas": 1,
    "numEpisodios": 10,
    "estadoEmision": True,
    "activa": True,
}


SERIE_DETALLE_RESPONSE = {
    **SERIE_RESPONSE,
    "generos": [{"id": "gen-1", "nombre": "Sci-Fi"}],
    "plataformas": [{"id": "plat-1", "nombre": "Apple TV+"}],
    "similares": [{"id": "serie-2", "titulo": "Severance"}],
}


SERIES_LIST_RESPONSE = {
    "series": [
        {
            "id": "serie-1",
            "titulo": "Dark Matter",
            "anio": 2024,
            "calificacion": 4.8,
            "activa": True,
        }
    ],
    "agregaciones": {
        "total": 1,
        "promedio_calificacion": 4.8,
        "por_genero": [{"nombre": "Sci-Fi", "total": 1}],
        "por_plataforma": [{"nombre": "Apple TV+", "total": 1}],
    },
}


GENERO_RESPONSE = {
    "id": "gen-1",
    "nombre": "Sci-Fi",
    "descripcion": "Ciencia ficción",
    "popularidad": 91.2,
    "tendencia": True,
    "anio": 2020,
}


PLATAFORMA_RESPONSE = {
    "id": "plat-1",
    "nombre": "Apple TV+",
    "pais": "US",
    "precio": 9.99,
    "fechaFundacion": "2019-11-01",
    "suscriptores": 50000000,
}


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "neo4j": "conectado"}


def test_get_series_forward_filters(client, monkeypatch):
    captured = {}

    def fake_listar_series(**kwargs):
        captured.update(kwargs)
        return SERIES_LIST_RESPONSE

    monkeypatch.setattr(repositories.series, "listar_series", fake_listar_series)

    response = client.get(
        "/series",
        params={
            "titulo": "Dark",
            "anio": 2024,
            "calificacion_min": 4.5,
            "calificacion_max": 5.0,
            "activa": True,
            "estadoEmision": True,
            "genero_id": "gen-1",
            "plataforma_id": "plat-1",
            "limit": 5,
            "skip": 1,
        },
    )

    assert response.status_code == 200
    assert response.json() == SERIES_LIST_RESPONSE
    assert captured == {
        "titulo": "Dark",
        "anio": 2024,
        "calificacion_min": 4.5,
        "calificacion_max": 5.0,
        "activa": True,
        "estadoEmision": True,
        "genero_id": "gen-1",
        "plataforma_id": "plat-1",
        "limit": 5,
        "skip": 1,
    }


def test_get_serie_detail_success(client, monkeypatch):
    monkeypatch.setattr(
        repositories.series, "obtener_serie_por_id", lambda serie_id: SERIE_DETALLE_RESPONSE
    )

    response = client.get("/series/serie-1")

    assert response.status_code == 200
    assert response.json()["id"] == "serie-1"
    assert response.json()["generos"][0]["nombre"] == "Sci-Fi"


def test_get_serie_detail_not_found(client, monkeypatch):
    monkeypatch.setattr(repositories.series, "obtener_serie_por_id", lambda serie_id: None)

    response = client.get("/series/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "Serie 'missing' no encontrada"}


def test_post_series_success(client, monkeypatch):
    monkeypatch.setattr(repositories.series, "crear_serie", lambda data: SERIE_RESPONSE)

    response = client.post(
        "/series",
        json={
            "titulo": "Dark Matter",
            "sinopsis": "Ciencia ficción.",
            "anio": 2024,
            "calificacion": 4.8,
            "numTemporadas": 1,
            "numEpisodios": 10,
            "estadoEmision": True,
            "activa": True,
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == "serie-1"


def test_patch_series_masivo_success(client, monkeypatch):
    monkeypatch.setattr(
        repositories.series,
        "actualizar_propiedades_series_masivo",
        lambda ids, propiedades: len(ids),
    )

    response = client.patch(
        "/series/masivo",
        json={"ids": ["serie-1", "serie-2"], "propiedades": {"activa": False}},
    )

    assert response.status_code == 200
    assert response.json() == {"actualizadas": 2, "ids": ["serie-1", "serie-2"]}


def test_patch_series_not_found(client, monkeypatch):
    monkeypatch.setattr(
        repositories.series, "actualizar_propiedades_serie", lambda serie_id, propiedades: None
    )

    response = client.patch("/series/missing", json={"propiedades": {"activa": False}})

    assert response.status_code == 404
    assert response.json() == {"detail": "Serie 'missing' no encontrada"}


def test_delete_series_propiedades_success(client, monkeypatch):
    monkeypatch.setattr(
        repositories.series, "eliminar_propiedades_serie", lambda serie_id, nombres: SERIE_RESPONSE
    )

    response = client.request(
        "DELETE",
        "/series/serie-1/propiedades",
        json={"nombres": ["foo", "bar"]},
    )

    assert response.status_code == 200
    assert response.json()["mensaje"] == "Propiedades eliminadas"


def test_delete_series_single_and_bulk(client, monkeypatch):
    monkeypatch.setattr(repositories.series, "eliminar_serie", lambda serie_id: True)
    monkeypatch.setattr(repositories.series, "eliminar_series", lambda ids: len(ids))

    single_response = client.delete("/series/serie-1")
    bulk_response = client.request("DELETE", "/series", json={"ids": ["serie-1", "serie-2"]})

    assert single_response.status_code == 200
    assert bulk_response.status_code == 200
    assert bulk_response.json() == {"eliminadas": 2, "ids": ["serie-1", "serie-2"]}


def test_generos_get_and_post(client, monkeypatch):
    monkeypatch.setattr(repositories.generos, "listar_generos", lambda: [GENERO_RESPONSE])
    monkeypatch.setattr(repositories.generos, "crear_genero", lambda data: GENERO_RESPONSE)

    get_response = client.get("/generos")
    post_response = client.post(
        "/generos",
        json={
            "nombre": "Sci-Fi",
            "descripcion": "Ciencia ficción",
            "popularidad": 91.2,
            "tendencia": True,
            "anio": 2020,
        },
    )

    assert get_response.status_code == 200
    assert post_response.status_code == 201
    assert get_response.json()[0]["id"] == "gen-1"
    assert post_response.json()["nombre"] == "Sci-Fi"


def test_plataformas_get_and_post(client, monkeypatch):
    monkeypatch.setattr(
        repositories.plataformas, "listar_plataformas", lambda: [PLATAFORMA_RESPONSE]
    )
    monkeypatch.setattr(
        repositories.plataformas, "crear_plataforma", lambda data: PLATAFORMA_RESPONSE
    )

    get_response = client.get("/plataformas")
    post_response = client.post(
        "/plataformas",
        json={
            "nombre": "Apple TV+",
            "pais": "US",
            "precio": 9.99,
            "fechaFundacion": "2019-11-01",
            "suscriptores": 50000000,
        },
    )

    assert get_response.status_code == 200
    assert post_response.status_code == 201
    assert get_response.json()[0]["id"] == "plat-1"
    assert post_response.json()["fechaFundacion"] == "2019-11-01"


def test_relaciones_pertenece_a_crud_success(client, monkeypatch):
    created = {
        "serie_id": "serie-1",
        "genero_id": "gen-1",
        "esPrincipal": True,
        "relevancia": 0.9,
        "fechaAsignacion": "2026-05-04",
    }

    monkeypatch.setattr(repositories.relaciones, "crear_pertenece_a", lambda *args: created)
    monkeypatch.setattr(repositories.relaciones, "actualizar_pertenece_a", lambda *args: created)
    monkeypatch.setattr(repositories.relaciones, "eliminar_pertenece_a", lambda *args: True)

    post_response = client.post(
        "/relaciones/pertenece-a/serie-1/gen-1",
        json={
            "esPrincipal": True,
            "relevancia": 0.9,
            "fechaAsignacion": "2026-05-04",
        },
    )
    patch_response = client.patch(
        "/relaciones/pertenece-a/serie-1/gen-1",
        json={"propiedades": {"relevancia": 0.95}},
    )
    delete_response = client.delete("/relaciones/pertenece-a/serie-1/gen-1")

    assert post_response.status_code == 201
    assert patch_response.status_code == 200
    assert delete_response.status_code == 200


@pytest.mark.parametrize(
    ("path", "payload", "repo_name"),
    [
        (
            "/relaciones/transmite/plat-1/serie-1",
            {"fechaDisponible": "2026-05-04", "exclusiva": True, "regiones": ["GT"]},
            "crear_transmite",
        ),
        (
            "/relaciones/similar-a/serie-1/serie-2",
            {
                "puntuacionSimilitud": 0.88,
                "algoritmo": "cosine",
                "fechaCalculada": "2026-05-04",
            },
            "crear_similar_a",
        ),
    ],
)
def test_relaciones_create_not_found(client, monkeypatch, path, payload, repo_name):
    monkeypatch.setattr(repositories.relaciones, repo_name, lambda *args: None)

    response = client.post(path, json=payload)

    assert response.status_code == 404


def test_consultas_persona1(client, monkeypatch):
    monkeypatch.setattr(
        repositories.consultas,
        "series_mejor_calificadas_por_genero",
        lambda: [
            {
                "genero_id": "gen-1",
                "genero": "Sci-Fi",
                "top_series": [{"id": "serie-1", "titulo": "Dark Matter", "calificacion": 4.8}],
                "promedio_calificacion": 4.8,
                "cantidad_series": 1,
            }
        ],
    )
    monkeypatch.setattr(
        repositories.consultas,
        "plataformas_mas_exclusivas",
        lambda: [
            {
                "plataforma_id": "plat-1",
                "plataforma": "Apple TV+",
                "total_exclusivas": 10,
                "total_series": 20,
                "porcentaje_exclusivas": 50.0,
            }
        ],
    )

    series_response = client.get("/consultas/series-mejor-calificadas-por-genero")
    plataformas_response = client.get("/consultas/plataformas-mas-exclusivas")

    assert series_response.status_code == 200
    assert plataformas_response.status_code == 200
    assert series_response.json()[0]["genero"] == "Sci-Fi"
    assert plataformas_response.json()[0]["porcentaje_exclusivas"] == 50.0
