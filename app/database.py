"""Conexión a Neo4j.

Implementa un singleton del driver para reutilizar la conexión
en toda la app, y un helper para obtener sesiones.
"""
from neo4j import GraphDatabase, Driver, Session
from app.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE


class Neo4jDriver:
    """Singleton para el driver de Neo4j."""

    _instance: Driver | None = None

    @classmethod
    def get_driver(cls) -> Driver:
        """Devuelve la instancia única del driver, creándola si no existe."""
        if cls._instance is None:
            cls._instance = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD),
            )
        return cls._instance

    @classmethod
    def close(cls) -> None:
        """Cierra el driver (llamar al apagar la app)."""
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None

    @classmethod
    def verify_connectivity(cls) -> bool:
        """Verifica que se puede conectar a Neo4j."""
        try:
            driver = cls.get_driver()
            driver.verify_connectivity()
            return True
        except Exception:
            return False


def get_session() -> Session:
    """Devuelve una sesión de Neo4j.

    Uso:
        with get_session() as session:
            result = session.run("MATCH (n) RETURN count(n)")
    """
    driver = Neo4jDriver.get_driver()
    return driver.session(database=NEO4J_DATABASE)
