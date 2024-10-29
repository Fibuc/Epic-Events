import secrets
import string


def generate_secret_key(length: int = 64):
    """Génère une clé secrète en format alphanumérique.
    La longueur de la clé secrète doit être comprise entre 32 et 64 caractères.
    Args:
        length (int): Longueur de la clé secrète.

    Returns:
        str: Clé secrète.
    """
    if length < 32:
        length = 32

    elif length > 64:
        length = 64

    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))
