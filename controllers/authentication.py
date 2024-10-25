from datetime import datetime, timezone
import os
import logging

import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.exc import OperationalError
from dotenv import set_key, unset_key, get_key

from controllers.session import with_session
from models.models import User
from views.authentication import AuthView
from config import SECRET_JWT_KEY, TOKEN_DURATION, ENV_FILE

logging.disable(logging.WARNING)

class AuthController:

    def __init__(self):
        self.view = AuthView()

    @with_session
    def login(self, email: str, session):
        """Permet à l'utilisateur de se connecter à l'application.

        Args:
            email (str): Email de l'utilisateur.
        """
        if not email:
            email = self.view.get_email()

        try:
            user = User.get_user_by_email(email, session)

        except OperationalError:
            self.view.error_login_no_database()
            return

        password = self.view.get_password()
        if not user or not user.verify_password(password):
            self.view.error_login()
            return

        self.generate_token(user_id=user.id, user_department=user.department.name)
        self.view.success_login(user.full_name)

    def logout(self):
        """Permet à l'utilisateur de se déconnecter de l'application."""
        if unset_key(ENV_FILE, 'JWT_TOKEN')[0]:
            self.view.success_logout()
        else:
            self.view.error_no_user_authenticated()

    def generate_token(self, user_id: int, user_department: int):
        """Génère un JSON Web Token de l'utilisateur et l'enregistre dans une variable d'environnement.

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
        self._save_token(token)

    @staticmethod
    def _save_token(token):
        """Sauvegarde le token dans le fichier indiqué dans le fichier d'environnement.

        Args:
            token (str): Token d'authentification.
        """
        set_key(ENV_FILE, 'JWT_TOKEN', token)

    @staticmethod
    def _get_token() -> str | None:
        """Récupère et retourne le token d'authentification de l'utilisateur.

        Returns:
            str | None: Le token si trouvé, sinon None.
        """
        return get_key(ENV_FILE, 'JWT_TOKEN')

    def verify_token(self) -> dict | None:
        """Vérifie le JWT de l'utilisateur et retourne le token si la vérification s'est bien déroulée.

        Returns:
            dict | None: Un dictionnaire des informations si la vérification s'est bien passée, ou None.
        """
        token = self._get_token()
        if token:
            try:
                decoded_token = jwt.decode(token, SECRET_JWT_KEY, algorithms=['HS256'], options={'verify_exp': True})
                return decoded_token

            except ExpiredSignatureError:
                self.view.expired_token()
                return

            except InvalidTokenError:
                self.view.error_token()
                return

        else:
            return

    def get_user_id(self):
        """Récupère et retourne l'ID de l'utilisateur connecté.

        Returns:
            int: L'ID de l'utilisateur connecté
        """
        return self._get_user_info('user_id')

    def get_user_department(self):
        """Récupère et retourne l'ID du département de l'utilisateur connecté.

        Returns:
            int: L'ID du département de l'utilisateur connecté.
        """
        return self._get_user_info('user_department')

    def _get_user_info(self, key: str):
        """Récupère et retourne l'information de l'utilisateur à partir du token JWT.

        Args:
            key (str): La clé à récupérer dans le payload du token.

        Returns:
            int | None: La valeur associée à la clé dans le token, ou None si le token est invalide.
        """
        token = self.verify_token()
        if token:
            return token.get(key)

        return None
