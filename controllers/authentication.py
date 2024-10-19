from datetime import datetime, timezone, timedelta
import os
import json

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from models.models import User
from controllers.session import with_session
from config import JWT_TOKEN_PATH, SECRET_JWT_KEY, TOKEN_DURATION

@with_session
def login(email: str, password: str, session) -> bool:
    """Permet à l'utilisateur de se connecter à l'application.

    Args:
        email (str): Email de l'utilisateur.
        password (str): Mot de passe de l'utilisateur.

    Returns:
        bool: Etat de la connexion de l'utilisateur. True = Connecté, False = Non connecté.
    """
    user = session.query(User).filter_by(email=email).first()
    if not user or not user.verify_password(password):
        return False

    generate_token(user_id=user.id, user_department=user.department)

    return True


def logout() -> bool:
    """Permet à l'utilisateur de se déconnecter de l'application.

    Returns:
        bool: Etat de la déconnexion.
    """

    try:
        os.remove(JWT_TOKEN_PATH)
        return True
    
    except FileNotFoundError:
        return False


def generate_token(user_id: int, user_department: int):
    """Génère un JSON Web Token de l'utilisateur et l'enregistre dans un fichier json.

    Args:
        user_id (int): L'id de l'utilisateur.
        user_department (str): Le département de l'utilisateur.

    """
    payload = {
        'user_id': user_id,
        'user_department': user_department,
        'exp': datetime.now(timezone.utc).replace(tzinfo=None) + TOKEN_DURATION
    }
    token = jwt.encode(payload, SECRET_JWT_KEY, algorithm='HS256')
    _save_token_json(token)


def _save_token_json(token):
    """Sauvegarde le token dans le fichier indiqué dans config.JWT_TOKEN_PATH.

    Args:
        token (str): Token d'authentification.
    """
    with open(JWT_TOKEN_PATH, 'w') as file:
        json.dump({'token': token}, file, indent=4)


def _load_token_json() -> str | None:
    """Charge le token dans le fichier token.json.
    Si le fichier n'existe pas, alors il renvoie None, sinon renvoie le token.

    Returns:
        str | None: Le token si trouvé, sinon None.
    """
    try:
        with open(JWT_TOKEN_PATH) as file:
            return json.load(file)['token']

    except FileNotFoundError:
        return None


def verify_token():
    """Vérifie le JWT de l'utilisateur et retourne le statut de la vérification.

    Returns:
        bool: Statut de la vérification.
    """
    token = _load_token_json()
    if token:
        try:
            decoded_token = jwt.decode(token, SECRET_JWT_KEY, algorithms=['HS256'], options={'verify_exp': True})
            return decoded_token
        
        except ExpiredSignatureError:
            return False

        except InvalidTokenError:
            return False

    else:
        return False


def get_user_id():
    """Récupère et retourne l'ID de l'utilisateur connecté.

    Returns:
        int: L'ID de l'utilisateur connecté
    """
    token = verify_token()
    if token:
        return token['user_id']


def get_user_department():
    """Récupère et retourne l'ID du département de l'utilisateur connecté.

    Returns:
        int: L'ID du département de l'utilisateur connecté.
    """
    token = verify_token()
    if token:
        return token['user_department']
