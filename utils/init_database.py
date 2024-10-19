from models import models
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from config import DATABASE, BASE
from controllers.session import get_engine




def _create_database(base_name: str = '') -> bool:
    """Créé la base de données de l'application.
    Si un autre nom est entré en paramètre, alors créé une autre base de données. 

    Args:
        base_name (str, optional): Nom de la base de données souhaitée. Défaut: ''.

    Returns:
        bool: Etat de réussite de la création.
    """
    if not base_name:
        base_name = DATABASE

    engine = get_engine()
    try:
        with engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE {base_name}'))
            print(f'La base de données {base_name} a été créée avec succès!')
            return True
    
    except ProgrammingError:
        print(f'Création impossible: La base de données {base_name} existe déjà.')
        return False


def _create_tables(base_name: str = ''):
    """Créé les tables dans la base de données en utilisant les informations des modèles
    dont la classe mère est BASE.

    Args:
        base_name (str, optional): Nom de la base de données. Défaut ''.
    """
    if not base_name:
        base_name = DATABASE

    engine = get_engine(base_name)
    BASE.metadata.create_all(bind=engine)
    print('Les tables ont été créées avec succès!')



def init_database(base_name: str = ''):
    """Permet de créer la base de données ainsi que toutes les tables.
    Si aucun nom de base de données est entré en paramètre, cela créera
    la base de données avec pour nom le nom entré dans config.DATABASE.

    Args:
        base_name (str, optional): Nom de la base de données si nécessaire. Défaut: ''.
    """
    result = _create_database(base_name)
    if result:
        _create_tables(base_name)
