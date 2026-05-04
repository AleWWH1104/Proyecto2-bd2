from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.database import Neo4jDriver, get_session
from app.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    """Cliente HTTP para tests sin depender de Neo4j real en startup."""

    monkeypatch.setattr(
        "app.database.Neo4jDriver.verify_connectivity", classmethod(lambda cls: True)
    )
    monkeypatch.setattr("app.database.Neo4jDriver.close", classmethod(lambda cls: None))

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def real_client() -> Iterator[TestClient]:
    """Cliente HTTP contra la app real y Neo4j seeded."""

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    """Sesión real de Neo4j para preparar y limpiar datos de integración."""

    with get_session() as session:
        yield session
    Neo4jDriver.close()
