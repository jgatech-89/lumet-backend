from .models import Campo


def get_campos_formulario(empresa_id: int, servicio_id: int):
    """
    Devuelve los campos configurados para un formulario (empresa + servicio).
    Solo activos, ordenados por `orden`, con opciones para tipo select.
    """
    return (
        Campo.objects
        .filter(
            empresa_id=empresa_id,
            servicio_id=servicio_id,
            activo=True,
            estado='1',
            deleted_at__isnull=True,
        )
        .select_related('empresa', 'servicio')
        .prefetch_related('opciones')
        .order_by('orden', 'id')
    )
