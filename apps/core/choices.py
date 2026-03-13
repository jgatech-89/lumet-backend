"""
Choices centralizados del sistema.
Única fuente de verdad para los valores de selects/opciones usados en modelos y frontend.
"""

TIPO_IDENTIFICACION = [
    ('CC', 'Cédula de ciudadanía'),
    ('CE', 'Cédula de extranjería'),
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

ESTADO_EMPRESA = [
    ('1', 'Activo'),
    ('0', 'Inactivo'),
]

ESTADO_SERVICIO = [
    ('1', 'Activo'),
    ('0', 'Inactivo'),
]

TIPO_CAMPO = [
    ('text', 'Texto'),
    ('number', 'Número'),
    ('select', 'Select'),
    ('date', 'Fecha'),
    ('checkbox', 'Checkbox'),
    ('textarea', 'Área de texto'),
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