"""Script para borrar TODOS los nodos y relaciones de Neo4j.

CUIDADO: esto borra absolutamente todo.

Ejecutar:
    uv run python scripts/reset.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_session, Neo4jDriver


def main():
    print("=" * 60)
    print("RESET DE BASE DE DATOS")
    print("=" * 60)
    print()
    print("ADVERTENCIA: esto borrará TODOS los datos de Neo4j.")
    confirmacion = input("Escribe 'BORRAR' para confirmar: ")
    if confirmacion != "BORRAR":
        print("Cancelado.")
        return

    if not Neo4jDriver.verify_connectivity():
        print("ERROR: no se puede conectar a Neo4j.")
        sys.exit(1)

    with get_session() as session:
        print("Borrando relaciones y nodos...")
        # En Neo4j, eliminar nodos con DETACH DELETE también borra sus relaciones
        # Lo hacemos en batches para no llenar memoria con BDs grandes
        result = session.run("""
            CALL apoc.periodic.iterate(
                "MATCH (n) RETURN n",
                "DETACH DELETE n",
                {batchSize: 1000, parallel: false}
            )
        """).single()

        # Si APOC no está disponible, usar fallback
        if result is None:
            session.run("MATCH (n) DETACH DELETE n")

        print("Borrando índices...")
        try:
            indices = session.run("SHOW INDEXES").data()
            for idx in indices:
                if idx.get("type") == "RANGE" and idx.get("name"):
                    session.run(f"DROP INDEX {idx['name']} IF EXISTS")
        except Exception as e:
            print(f"  (no se pudieron borrar índices: {e})")

        # Verificar
        result = session.run("MATCH (n) RETURN count(n) AS total").single()
        print(f"Nodos restantes: {result['total']}")

    Neo4jDriver.close()
    print()
    print("Base de datos limpia.")


if __name__ == "__main__":
    main()
