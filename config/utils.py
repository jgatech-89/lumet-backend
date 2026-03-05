import random


def generate_verification_code(length=6):
    """
    Genera un código numérico aleatorio de N dígitos.
    Por defecto 6 dígitos (100000 - 999999).
    """
    if length < 1:
        length = 6
    min_val = 10 ** (length - 1)
    max_val = (10 ** length) - 1
    return str(random.randint(min_val, max_val))
