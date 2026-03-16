"""
Choices centralizados del sistema.
Única fuente de verdad para los valores de selects/opciones usados en modelos y frontend.
"""

TIPO_IDENTIFICACION = [
    ('CC', 'Cédula de ciudadanía'),
    ('CE', 'Cédula de extranjería'),
    ('DNI', 'DNI'),
    ('NIT', 'NIT'),
    ('PAS', 'Pasaporte'),
    ('PPT', 'Permiso provisional de trabajo'),
    ('OTRO', 'Otro'),
]

PERFIL = [
    ('admin', 'Administrador'),
    ('usuario', 'Usuario'),
    ('cliente', 'Cliente'),
    ('invitado', 'Invitado'),
]

ESTADO = [
    ('1', 'Activo'),
    ('0', 'Inactivo'),
]

ESTADO_VENDEDOR = [
    ('1', 'Activo'),
    ('0', 'Inactivo'),
]

ESTADO_SERVICIO = [
    ('1', 'Activo'),
    ('0', 'Inactivo'),
]

ESTADO_CONTRATISTA = [
    ('1', 'Activo'),
    ('0', 'Inactivo'),
]

TIPO_CAMPO = [
    ('text', 'Texto'),
    ('number', 'Número'),
    ('date', 'Fecha'),
    ('textarea', 'Área de texto'),
    ('select', 'Select'),
    ('checkbox', 'Checkbox'),
    ('entity_select', 'Selector de entidad'),
]

# Entidades para campos tipo entity_select (opciones cargadas desde el backend).
ENTIDAD_CAMPO = [
    ('servicio', 'Servicio'),
    ('contratista', 'Contratista'),
    ('producto', 'Producto'),
    ('vendedor', 'Vendedor'),
]

# Secciones fijas del formulario (form builder de campos dinámicos).
SECCIONES_FORMULARIO = [
    ('cliente', 'Cliente'),
    ('datos_base', 'Datos base'),
    ('campos_formulario', 'Campos del formulario'),
    ('vendedor', 'Vendedor'),
]

# Estado de venta: preparado para manejarse por select (configurable).
ESTADO_VENTA = [
    ('venta_iniciada', 'Venta iniciada'),
    ('completada', 'Venta completada'),
    ('cancelada', 'Venta cancelada'),
    ('pospuesta', 'Venta pospuesta'),
    ('pendiente', 'Venta pendiente'),
]

# Tipo de cliente: 1 = particular, 2 = empresa.
TIPO_CLIENTE = [
    ('1', 'Particular'),
    ('2', 'Empresa'),
]

ESTADO_PRODUCTO = [
    ('1', 'Activo'),
    ('0', 'Inactivo'),
]

# Tipo de relación: estructura (Servicio→Contratista, Contratista→Producto) o contexto_campo (Campo→Servicio/Contratista/Producto).
TIPO_RELACION = [
    ('estructura', 'Relación estructural'),
    ('contexto_campo', 'Campo aplica a contexto'),
]

# Tipos de entidad para relaciones dinámicas (app relaciones).
# Origen/destino en Relacion: servicio, contratista, producto, campo, vendedor.
TIPO_ENTIDAD_RELACION = [
    ('servicio', 'Servicio'),
    ('contratista', 'Contratista'),
    ('producto', 'Producto'),
    ('campo', 'Campo'),
    ('vendedor', 'Vendedor'),
]