"""Choices para la app persona."""

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

# Estado del vendedor: activo/inactivo (desactivar sin eliminar)
ESTADO_VENDEDOR = [
    ('1', 'Activo'),
    ('0', 'Inactivo'),
]
