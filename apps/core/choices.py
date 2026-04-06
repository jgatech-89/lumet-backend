"""
Choices centralizados del sistema.
Única fuente de verdad para los valores de selects/opciones usados en modelos y frontend.
"""

# Códigos en `value`; `label` solo la descripción (el UI muestra "CC - CÉDULA DE CIUDADANÍA").
TIPO_IDENTIFICACION = [
    ('CC', 'CÉDULA DE CIUDADANÍA'),
    ('CE', 'CÉDULA DE EXTRANJERÍA'),
    ('NIT', 'NÚMERO DE IDENTIFICACIÓN TRIBUTARIO'),
    ('PAS', 'PASAPORTE'),
    ('TI', 'TARJETA DE IDENTIDAD'),
    ('PPT', 'PERMISO PROVISIONAL DE TRABAJO'),
    ('DNI', 'DOCUMENTO NACIONAL DE IDENTIDAD'),
    ('NIE', 'NÚMERO DE IDENTIFICACIÓN DE EXTRANJERO'),
    ('CIF', 'CÓDIGO DE IDENTIFICACIÓN FISCAL'),
    ('OTRO', 'OTRO DOCUMENTO'),
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

# Secciones fijas del formulario (form builder de campos dinámicos).
SECCIONES_FORMULARIO = [
    ('cliente', 'Cliente'),
    ('datos_base', 'Datos base'),
    ('campos_formulario', 'Campos del formulario'),
    ('vendedor', 'Comercial'),
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