import os
from functools import wraps

from controllers.authentication import AuthController


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
 
        except PermissionError as e:
            print(e)
            

    return wrapper


def is_in_department(required_department):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_department = AuthController().get_user_department()
            if user_department is None or user_department not in required_department:
                raise PermissionError("Accès refusé : Vous n'avez pas les droits nécessaires pour effectuer cette opération.")
            
            return func(*args, **kwargs)
            
        return wrapper
    
    return decorator
