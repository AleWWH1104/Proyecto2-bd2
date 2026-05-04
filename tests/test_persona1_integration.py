import uuid


def test_integration_series_and_catalog_queries(real_client):
    health = real_client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    series = real_client.get("/series", params={"limit": 5})
    assert series.status_code == 200
    payload = series.json()
    assert "series" in payload
    assert "agregaciones" in payload
    assert payload["agregaciones"]["total"] > 0
    assert len(payload["series"]) > 0

    first = payload["series"][0]
    assert {"id", "titulo", "anio", "calificacion", "activa"}.issubset(first.keys())

    detail = real_client.get(f"/series/{first['id']}")
    assert detail.status_code == 200
    detail_payload = detail.json()
    assert detail_payload["id"] == first["id"]
    assert "generos" in detail_payload
    assert "plataformas" in detail_payload
    assert "similares" in detail_payload

    generos = real_client.get("/generos")
    assert generos.status_code == 200
    assert isinstance(generos.json(), list)
    assert len(generos.json()) > 0

    plataformas = real_client.get("/plataformas")
    assert plataformas.status_code == 200
    assert isinstance(plataformas.json(), list)
    assert len(plataformas.json()) > 0

    consulta_1 = real_client.get("/consultas/series-mejor-calificadas-por-genero")
    assert consulta_1.status_code == 200
    assert isinstance(consulta_1.json(), list)
    assert len(consulta_1.json()) > 0
    assert {"genero", "top_series", "promedio_calificacion", "cantidad_series"}.issubset(
        consulta_1.json()[0].keys()
    )

    consulta_2 = real_client.get("/consultas/plataformas-mas-exclusivas")
    assert consulta_2.status_code == 200
    assert isinstance(consulta_2.json(), list)
    assert len(consulta_2.json()) > 0
    assert {"plataforma", "total_exclusivas", "total_series", "porcentaje_exclusivas"}.issubset(
        consulta_2.json()[0].keys()
    )


def test_integration_persona1_full_lifecycle(real_client, db_session):
    suffix = uuid.uuid4().hex[:8]
    created = {"serie_id": None, "genero_id": None, "plataforma_id": None}

    existing_serie = db_session.run("MATCH (s:Serie) RETURN s.id AS id LIMIT 1").single()["id"]

    try:
        genero = real_client.post(
            "/generos",
            json={
                "nombre": f"IT Genero {suffix}",
                "descripcion": "Genero temporal de integración",
                "popularidad": 33.3,
                "tendencia": True,
                "anio": 2026,
            },
        )
        assert genero.status_code == 201
        created["genero_id"] = genero.json()["id"]

        plataforma = real_client.post(
            "/plataformas",
            json={
                "nombre": f"IT Plataforma {suffix}",
                "pais": "GT",
                "precio": 7.5,
                "fechaFundacion": "2020-01-01",
                "suscriptores": 1234,
            },
        )
        assert plataforma.status_code == 201
        created["plataforma_id"] = plataforma.json()["id"]

        serie = real_client.post(
            "/series",
            json={
                "titulo": f"IT Serie {suffix}",
                "sinopsis": "Serie temporal para integración",
                "anio": 2026,
                "calificacion": 4.1,
                "numTemporadas": 1,
                "numEpisodios": 8,
                "estadoEmision": True,
                "activa": True,
            },
        )
        assert serie.status_code == 201
        created["serie_id"] = serie.json()["id"]

        detail = real_client.get(f"/series/{created['serie_id']}")
        assert detail.status_code == 200
        assert detail.json()["titulo"] == f"IT Serie {suffix}"

        patch_single = real_client.patch(
            f"/series/{created['serie_id']}",
            json={"propiedades": {"calificacion": 4.6, "propTemporal": "x"}},
        )
        assert patch_single.status_code == 200
        assert patch_single.json()["calificacion"] == 4.6

        patch_bulk = real_client.patch(
            "/series/masivo",
            json={"ids": [created["serie_id"]], "propiedades": {"propMasiva": True}},
        )
        assert patch_bulk.status_code == 200
        assert patch_bulk.json()["actualizadas"] >= 1

        relacion_genero = real_client.post(
            f"/relaciones/pertenece-a/{created['serie_id']}/{created['genero_id']}",
            json={
                "esPrincipal": True,
                "relevancia": 0.77,
                "fechaAsignacion": "2026-05-04",
            },
        )
        assert relacion_genero.status_code == 201

        relacion_genero_patch = real_client.patch(
            f"/relaciones/pertenece-a/{created['serie_id']}/{created['genero_id']}",
            json={"propiedades": {"relevancia": 0.9}},
        )
        assert relacion_genero_patch.status_code == 200
        assert relacion_genero_patch.json()["relevancia"] == 0.9

        relacion_transmite = real_client.post(
            f"/relaciones/transmite/{created['plataforma_id']}/{created['serie_id']}",
            json={
                "fechaDisponible": "2026-05-04",
                "exclusiva": True,
                "regiones": ["GT", "MX"],
            },
        )
        assert relacion_transmite.status_code == 201

        relacion_similar = real_client.post(
            f"/relaciones/similar-a/{created['serie_id']}/{existing_serie}",
            json={
                "puntuacionSimilitud": 0.81,
                "algoritmo": "integration-test",
                "fechaCalculada": "2026-05-04",
            },
        )
        assert relacion_similar.status_code == 201

        delete_props = real_client.request(
            "DELETE",
            f"/series/{created['serie_id']}/propiedades",
            json={"nombres": ["propTemporal", "propMasiva"]},
        )
        assert delete_props.status_code == 200

        delete_rel = real_client.delete(
            f"/relaciones/pertenece-a/{created['serie_id']}/{created['genero_id']}"
        )
        assert delete_rel.status_code == 200

        delete_series = real_client.request(
            "DELETE", "/series", json={"ids": [created["serie_id"]]}
        )
        assert delete_series.status_code == 200
        assert delete_series.json()["eliminadas"] >= 1
        created["serie_id"] = None

    finally:
        if created["serie_id"]:
            db_session.run("MATCH (s:Serie {id: $id}) DETACH DELETE s", id=created["serie_id"])
        if created["plataforma_id"]:
            db_session.run(
                "MATCH (p:Plataforma {id: $id}) DETACH DELETE p", id=created["plataforma_id"]
            )
        if created["genero_id"]:
            db_session.run("MATCH (g:Genero {id: $id}) DETACH DELETE g", id=created["genero_id"])


def test_integration_missing_resources_return_404(real_client):
    missing_id = f"missing-{uuid.uuid4().hex}"

    get_response = real_client.get(f"/series/{missing_id}")
    patch_response = real_client.patch(
        f"/series/{missing_id}", json={"propiedades": {"activa": False}}
    )
    delete_response = real_client.delete(f"/series/{missing_id}")
    delete_rel_response = real_client.delete(f"/relaciones/pertenece-a/{missing_id}/{missing_id}")

    assert get_response.status_code == 404
    assert patch_response.status_code == 404
    assert delete_response.status_code == 404
    assert delete_rel_response.status_code == 404
