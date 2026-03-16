from django.db.models import F, Q

from .models import Campo


def _filtrar_campos_por_contexto(campos, servicio_id, contratista_id, producto_id):
    """
    Filtra una lista de campos por relaciones de tipo contexto_campo.
    - Si un campo no tiene relaciones contexto_campo → es global y se incluye.
    - Si tiene relaciones contexto_campo → se incluye solo si el contexto actual
      (servicio_id, contratista_id, producto_id) coincide con todas ellas.
    """
    from apps.relaciones.models import Relacion

    if not campos:
        return []
    campo_ids = [c.id for c in campos]
    relaciones = Relacion.objects.filter(
        origen_tipo='campo',
        origen_id__in=campo_ids,
        tipo_relacion='contexto_campo',
        estado='1',
    ).values_list('origen_id', 'destino_tipo', 'destino_id')

    # Agrupar por origen_id (campo_id)
    from collections import defaultdict
    rel_por_campo = defaultdict(list)
    for oid, dest_tipo, dest_id in relaciones:
        rel_por_campo[oid].append((dest_tipo, dest_id))

    campos_validos = []
    for campo in campos:
        rels = rel_por_campo.get(campo.id, [])
        if not rels:
            campos_validos.append(campo)
            continue
        aplica = True
        for dest_tipo, dest_id in rels:
            if dest_tipo == 'servicio' and (servicio_id is None or dest_id != servicio_id):
                aplica = False
                break
            if dest_tipo == 'contratista' and (contratista_id is None or dest_id != contratista_id):
                aplica = False
                break
            if dest_tipo == 'producto' and (producto_id is None or dest_id != producto_id):
                aplica = False
                break
        if aplica:
            campos_validos.append(campo)
    return campos_validos


def _get_campos_base_campos_formulario(servicio_id, contratista_id):
    """
    Devuelve solo los campos "base" de la sección campos_formulario:
    el selector de producto (entity_select, entidad=producto).
    Usado cuando no hay producto_id para no mostrar campos dependientes del producto.
    """
    qs = Campo.objects.filter(
        activo=True,
        estado='1',
        fecha_elimina__isnull=True,
        seccion='campos_formulario',
        tipo='entity_select',
        entidad__iexact='producto',
    ).select_related('servicio', 'contratista', 'depende_de').prefetch_related('opciones').order_by('orden', 'id')

    if servicio_id is None and contratista_id is None:
        qs = qs.filter(servicio_id__isnull=True, contratista_id__isnull=True)
    else:
        qs = qs.filter(
            Q(servicio_id__isnull=True, contratista_id__isnull=True)
            | (Q(servicio_id=servicio_id) & (Q(contratista_id=contratista_id) | Q(contratista_id__isnull=True)))
        )
    return qs


def get_campos_formulario_por_producto_id(servicio_id, contratista_id, producto_id):
    """
    Para sección campos_formulario con producto_id: devuelve campos base (selector producto)
    + campos relacionados al producto vía tabla Relacion con tipo_relacion=estructura (Producto → Campo).
    Luego filtra por relaciones contexto_campo: solo se incluyen campos que aplican al contexto actual.
    """
    from apps.relaciones.models import Relacion

    base = _get_campos_base_campos_formulario(servicio_id, contratista_id)
    campo_ids = list(
        Relacion.objects.filter(
            origen_tipo='producto',
            origen_id=producto_id,
            destino_tipo='campo',
            tipo_relacion='estructura',
            estado='1',
        ).values_list('destino_id', flat=True)
    )
    if not campo_ids:
        return _filtrar_campos_por_contexto(list(base), servicio_id, contratista_id, producto_id)

    qs_relacionados = Campo.objects.filter(
        id__in=campo_ids,
        activo=True,
        estado='1',
        fecha_elimina__isnull=True,
        seccion='campos_formulario',
    ).select_related('servicio', 'contratista', 'depende_de').prefetch_related('opciones').order_by('orden', 'id')

    if servicio_id is not None and contratista_id is not None:
        qs_relacionados = qs_relacionados.filter(
            Q(servicio_id__isnull=True, contratista_id__isnull=True)
            | (Q(servicio_id=servicio_id) & (Q(contratista_id=contratista_id) | Q(contratista_id__isnull=True)))
        )
    else:
        qs_relacionados = qs_relacionados.filter(servicio_id__isnull=True, contratista_id__isnull=True)

    # Unir base + relacionados preservando orden: primero base, luego por orden
    ids_base = list(base.values_list('id', flat=True))
    ids_rel = list(qs_relacionados.exclude(id__in=ids_base).values_list('id', flat=True))
    orden_final = ids_base + ids_rel
    if not orden_final:
        return _filtrar_campos_por_contexto(list(base), servicio_id, contratista_id, producto_id)
    # Ordenar por la lista de ids (base primero, luego relacionados en su orden)
    preserved = {pk: i for i, pk in enumerate(orden_final)}
    todos = list(base) + [c for c in qs_relacionados if c.id not in ids_base]
    todos.sort(key=lambda c: preserved.get(c.id, 999))
    # Filtrar por contexto: solo campos globales o con relaciones contexto_campo que coincidan
    return _filtrar_campos_por_contexto(todos, servicio_id, contratista_id, producto_id)


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


def get_campos_formulario(servicio_id: int = None, contratista_id: int = None, producto: str = None, solo_sin_producto: bool = False, seccion: str = None):
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
    - Si seccion se proporciona: filtra solo los campos de esa sección (cliente, datos_base, campos_formulario, vendedor).
    Solo activos, ordenados por `orden`, con opciones para tipo select.
    """
    from django.db.models import Q
    qs = Campo.objects.filter(
        activo=True,
        estado='1',
        fecha_elimina__isnull=True,
    ).select_related('servicio', 'contratista', 'depende_de').prefetch_related('opciones').order_by('seccion', 'orden', 'id')

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

    if seccion and str(seccion).strip():
        qs = qs.filter(seccion=str(seccion).strip())

    return qs
