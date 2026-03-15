from django.db.models import F

from .models import Campo


def reordenar_campos_para_insertar(servicio_id, contratista_id, producto, seccion, orden, excluir_campo_id=None):
    """
    Antes de insertar o actualizar un campo en la posición (seccion, orden), incrementa en +1
    el orden de todos los campos del mismo ámbito (servicio, contratista, producto) y misma sección
    que tengan orden >= orden. Solo afecta a la misma sección.
    """
    producto_val = (producto or '').strip()
    qs = Campo.objects.filter(
        servicio_id=servicio_id,
        contratista_id=contratista_id,
        producto=producto_val,
        seccion=seccion,
        orden__gte=orden,
        fecha_elimina__isnull=True,
    )
    if excluir_campo_id is not None:
        qs = qs.exclude(pk=excluir_campo_id)
    qs.update(orden=F('orden') + 1)


def get_campos_formulario(servicio_id: int = None, contratista_id: int = None, producto: str = None, solo_sin_producto: bool = False):
    """
    Devuelve los campos configurados para un formulario.
    - Si servicio_id y contratista_id son None: devuelve campos globales (servicio=null, contratista=null).
    - Si se pasan ambos: devuelve campos que aplican a ese servicio+contratista, incluyendo:
      - Campos con servicio_id=null y contratista_id=null (aplican a todos).
      - Campos con servicio_id=X y contratista_id=null (aplican a todos los contratistas de ese servicio).
      - Campos con servicio_id=X y contratista_id=Y (aplican a ese contratista).
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
    ).select_related('servicio', 'contratista').prefetch_related('opciones').order_by('seccion', 'orden', 'id')

    if servicio_id is None and contratista_id is None:
        qs = qs.filter(servicio_id__isnull=True, contratista_id__isnull=True)
    else:
        qs = qs.filter(
            Q(servicio_id__isnull=True, contratista_id__isnull=True)
            | (Q(servicio_id=servicio_id) & (Q(contratista_id=contratista_id) | Q(contratista_id__isnull=True)))
        )

    if solo_sin_producto:
        qs = qs.filter(producto='')
    elif producto and str(producto).strip():
        producto_val = str(producto).strip()
        qs = qs.filter(Q(producto='') | Q(producto__iexact=producto_val))

    return qs
