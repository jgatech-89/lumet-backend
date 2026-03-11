"""
Servicio que expone los choices centralizados en formato JSON para el frontend.
Lee las constantes en mayúsculas de apps.core.choices y las convierte a { value, label }.
"""
from apps.core import choices as choices_module


def _constant_name_to_key(name: str) -> str:
    """Convierte nombre de constante (ej. ESTADO_EMPRESA) a clave snake_case en minúsculas."""
    return name.lower()


def _is_choices_list(obj) -> bool:
    """Indica si el objeto es una lista de tuplas (value, label) válida para choices."""
    if not isinstance(obj, list) or not obj:
        return False
    return all(
        isinstance(item, (list, tuple)) and len(item) == 2
        for item in obj
    )


def get_all_choices_for_api() -> dict:
    """
    Obtiene todas las constantes en mayúsculas del módulo choices que son listas
    de tuplas (value, label) y las devuelve como diccionario listo para la API.

    Returns:
        Dict con claves en snake_case y listas de { "value", "label" }.
    """
    result = {}
    for name in dir(choices_module):
        if name.isupper():
            obj = getattr(choices_module, name)
            if _is_choices_list(obj):
                key = _constant_name_to_key(name)
                result[key] = [
                    {'value': value, 'label': label}
                    for value, label in obj
                ]
    return result
