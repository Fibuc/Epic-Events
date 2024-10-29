import os
from functools import wraps

import sentry_sdk

from controllers.authentication import AuthController


def is_authenticated(func):
    """Décorateur qui vérifie si l'utilisateur est connecté avant
    d'exécuter la fonction entrée en paramètre.

    Args:
        func: Fonction à exécuter si l'utilisateur est vérifié.

    Raises:
        PermissionError: Erreur de permission disant que l'utilisateur n'est
            pas connecté.

    Returns:
        func: Retourne le résultat de la fonction si exécutée.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            if os.getenv('JWT_TOKEN'):
                result = AuthController().verify_token()
                if result:
                    return func(*args, **kwargs)

                else:
                    raise PermissionError(
                        "Vous n'êtes plus connecté, veuillez-vous reconnecter."
                    )

        except PermissionError as e:
            sentry_sdk.capture_exception(e)

    return wrapper


def is_in_department(required_department: list['str']):
    """Décorateur qui vérifie si l'utilisateur est fait parti
    du département présent dans la liste des départements entrée en paramètre.

    Args:
        func: Fonction à exécuter si l'utilisateur fait parti d'un des
            départements requis.

    Raises:
        PermissionError: Erreur de permission disant que l'utilisateur n'a pas
            les droits necéssaires pour exécuter la fonction.

    Returns:
        func: Retourne le résultat de la fonction si exécutée.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_department = AuthController().get_user_department()
            try:
                if (
                    user_department is None
                    or user_department not in required_department
                ):
                    raise PermissionError(
                        "Accès refusé : Vous n'avez pas les droits nécessaires "
                        "pour effectuer cette opération."
                    )
            except PermissionError as e:
                sentry_sdk.capture_exception(e)

            return func(*args, **kwargs)

        return wrapper

    return decorator
