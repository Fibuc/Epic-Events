from functools import wraps

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from config import URL_MYSQL, DATABASE


def get_engine(database: str = ''):
    """Créé et retourne un moteur qui permet de faire la liaison entre l'ORM et la base de données.  

    Args:
        database (str, optional): Nom de la base de données. Defaults to ''.

    Returns:
        Engine: Moteur liant l'ORM avec la base de données.
    """
    url = URL_MYSQL
    if database:
        url += database

    return create_engine(url)


def get_database_engine():
    """Retourne le moteur pour la base de données indiquée dans config.DATABASE.

    Returns:
        Engine: Moteur de la base de données.
    """
    return get_engine(DATABASE)


engine = get_database_engine()


def get_session():
    """Créé et retourne une session permettant d'utiliser le moteur
    pour interagir avec la base de données.

    Returns:
        Session: Session d'interaction.
    """
    Session = sessionmaker(engine)
    return Session()


def add_and_commit_in_base(element_to_commit):
    """Créé une session dans laquelle un élément est ajouté à la base de données
    puis se ferme.

    Args:
        element_to_commit: Elément à ajouter à la base de données.
    """
    session = get_session()
    session.add(element_to_commit)
    session.commit()
    session.close()


def with_session(func):
    """Décorateur permettant d'ouvrir et fermer une session le temps de
    l'exécution de la fonction décorée.

    Args:
        func: Fonction décorée nécessitant une session.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = get_session()
        
        func(*args, session=session, **kwargs)

        session.close()

    return wrapper