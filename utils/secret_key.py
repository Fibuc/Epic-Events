import secrets
import string


def _generate_secret_key(length: int):
    """Génère une clé secrète en format alphanumérique de la longueur entrée
    en paramètre.

    Args:
        length (int): Longueur de la clé secrète.

    Returns:
        str: Clé secrète.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))


def _add_secret_key_to_env(secret_key: str):
    """Ajoute la clé secrète à l'environnement virtuel '.env'.

    Args:
        secret_key (str): Clé secrète.
    """
    with open('.env', 'a') as env:
        env.write(f'\nSECRET_JWT_KEY={secret_key}')


def create_secret_key(length: int=64):
    """Génère et enregistre la clé secrète dans l'environnement virtuel.
    La longueur de la clé secrète doit être comprise entre 32 et 64 caractères.

    Args:
        length (int, optional): Longueur de la clé secrète. Défaut 64.

    Returns:
        str: Clé secrète.
    """
    if length < 32:
        length = 32
    
    elif length > 64:
        length = 64

    secret_key = _generate_secret_key(length)
    _add_secret_key_to_env(secret_key)
    return secret_key
