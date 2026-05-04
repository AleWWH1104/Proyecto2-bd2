"""Helpers compartidos por todos los repositories."""


def to_native(valor):
    """Convierte recursivamente neo4j.time.Date/DateTime → tipos nativos de Python.

    Necesario porque Pydantic no sabe serializar los tipos temporales del driver.
    """
    if hasattr(valor, "to_native"):
        return valor.to_native()
    if isinstance(valor, dict):
        return {k: to_native(v) for k, v in valor.items()}
    if isinstance(valor, list):
        return [to_native(v) for v in valor]
    return valor
