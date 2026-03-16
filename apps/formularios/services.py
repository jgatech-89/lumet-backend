from django.db.models import F

from .models import Campo


def reordenar_campos_para_insertar(empresa_id, servicio_id, producto, seccion, orden, excluir_campo_id=None):
    """
    Antes de insertar o actualizar un campo en la posición (seccion, orden), incrementa en +1
    el orden de todos los campos del mismo ámbito (empresa, servicio, producto) y misma sección
    que tengan orden >= orden. Solo afecta a la misma sección.
    """
    producto_val = (producto or '').strip()
    qs = Campo.objects.filter(
        empresa_id=empresa_id,
        servicio_id=servicio_id,
        producto=producto_val,
        seccion=seccion,
        orden__gte=orden,
        fecha_elimina__isnull=True,
    )
    if excluir_campo_id is not None:
        qs = qs.exclude(pk=excluir_campo_id)
    qs.update(orden=F('orden') + 1)


def get_campos_formulario(empresa_id: int = None, servicio_id: int = None, producto: str = None, solo_sin_producto: bool = False):
    """
    Devuelve los campos configurados para un formulario.
    - Si empresa_id y servicio_id son None: devuelve campos globales (empresa=null, servicio=null).
    - Si se pasan ambos: devuelve campos que aplican a esa empresa+servicio, incluyendo:
      - Campos con empresa_id=null y servicio_id=null (aplican a todos).
      - Campos con empresa_id=X y servicio_id=null (aplican a todos los servicios de esa empresa).
      - Campos con empresa_id=X y servicio_id=Y (aplican a ese servicio).
    - Si solo_sin_producto=True: solo campos con producto vacío (no tienen restricción por producto).
    - Si producto se proporciona (y no solo_sin_producto): filtra campos que aplican a ese producto:
      - Campos con producto vacío (aplican a todos los productos).
      - Campos cuyo producto coincide con el valor seleccionado.
    Solo activos, ordenados por `orden`, con opciones para tipo select.
    """
    from django.db.models import Q
    qs = Campo.objects.filter(
        activo=True,
        estado='1',
        fecha_elimina__isnull=True,
    ).select_related('empresa', 'servicio').prefetch_related('opciones').order_by('seccion', 'orden', 'id')

    if empresa_id is None and servicio_id is None:
        qs = qs.filter(empresa_id__isnull=True, servicio_id__isnull=True)
    else:
        qs = qs.filter(
            Q(empresa_id__isnull=True, servicio_id__isnull=True)
            | (Q(empresa_id=empresa_id) & (Q(servicio_id=servicio_id) | Q(servicio_id__isnull=True)))
        )

    if solo_sin_producto:
        qs = qs.filter(producto='')
    elif producto and str(producto).strip():
        producto_val = str(producto).strip()
        qs = qs.filter(Q(producto='') | Q(producto__iexact=producto_val))

    return qs
