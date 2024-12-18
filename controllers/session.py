import importlib
from functools import wraps

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import config


def get_engine(database: str = ''):
    """Créé et retourne un moteur qui permet de faire la liaison entre l'ORM
    et la base de données.

    Args:
        database (str, optional): Nom de la base de données. Defaults to ''.

    Returns:
        Engine: Moteur liant l'ORM avec la base de données.
    """
    importlib.reload(config)
    url = config.URL_MYSQL

    if database:
        url += database

    return create_engine(url)


def get_database_engine():
    """Retourne le moteur pour la base de données indiquée dans
    config.DATABASE.

    Returns:
        Engine: Moteur de la base de données.
    """
    return get_engine(config.DATABASE)


def get_session():
    """Créé et retourne une session permettant d'utiliser le moteur
    pour interagir avec la base de données.

    Returns:
        Session: Session d'interaction.
    """
    engine = get_database_engine()
    Session = sessionmaker(engine)
    return Session()


def add_and_commit_in_base(element_to_commit, session=None):
    """Créé une session dans laquelle un élément est ajouté à la base de
    données puis se ferme.

    Args:
        element_to_commit: Elément à ajouter à la base de données.
    """
    if not session:
        session = get_session()
    session.add(element_to_commit)
    session.commit()
    session.close()


def with_session(func):
    """Décorateur permettant d'ouvrir et fermer une session de base de données
    le temps de l'exécution de la fonction décorée.

    Args:
        func: Fonction décorée nécessitant une session.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        session = get_session()

        func_result = func(*args, session=session, **kwargs)

        session.close()

        return func_result

    return wrapper
