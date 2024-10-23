import os
from functools import wraps
from models.models import Department

from controllers.authentication import AuthController
from controllers.session import get_session


def is_authenticated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            if os.getenv('JWT_TOKEN'):
                result = AuthController().verify_token()
                if result:
                    return func(*args, **kwargs)
                
                else:
                    raise PermissionError("Vous n'êtes plus connecté, veuillez-vous reconnecter.")

            else:
                raise FileNotFoundError("Vous n'êtes pas connecté.")
            
        except PermissionError or FileNotFoundError as error:
            print(error)

    return wrapper


def is_in_department(required_department):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            session = get_session()
            user_department_id = AuthController().get_user_department()
            department_user = session.query(Department).filter(Department.id == user_department_id).first()
            if department_user is None or department_user.name not in required_department:
                raise PermissionError(f"Accès refusé : Vous n'avez pas les droits nécessaires pour effectuer cette opération.")
            
            session.close()
            return func(*args, **kwargs)
            
        return wrapper
    
    return decorator
