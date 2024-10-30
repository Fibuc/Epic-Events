from sentry_sdk import capture_message
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from dotenv import set_key

import config
from config import DATABASE, BASE, ENV_FILE
from controllers.session import get_engine
from utils.secret_key import generate_secret_key
from utils.utils_database import generate_datas
from views.database import DatabaseView
from models import models  # noqa: F401


class DatabaseController:
    """Contrôleur de la base de données"""
    def __init__(self):
        self.view = DatabaseView

    @staticmethod
    def _create_database(base_name: str = '') -> bool:
        """Créé la base de données de l'application.
        Si un autre nom est entré en paramètre, alors créé une autre base de
        données.

        Args:
            base_name (str, optional): Nom de la base de données souhaitée.
                Défaut: ''.

        Returns:
            bool: Etat de réussite de la création.
        """
        if not base_name:
            base_name = DATABASE

        engine = get_engine()
        try:
            with engine.connect() as connection:
                connection.execute(text(f'CREATE DATABASE {base_name}'))
                return True

        except ProgrammingError:
            return False

    @staticmethod
    def _create_tables(base_name: str = ''):
        """Créé les tables dans la base de données en utilisant les
        informations des modèles dont la classe mère est BASE.

        Args:
            base_name (str, optional): Nom de la base de données. Défaut ''.
        """
        if not base_name:
            base_name = DATABASE

        engine = get_engine(base_name)
        BASE.metadata.create_all(bind=engine)

    def _create_env_file(self):
        """Crée le fichier d'environnement '.env' ainsi que les différentes
        variables d'environnement nécessaires à l'application.
        """
        ENV_FILE.touch()
        config.USERNAME = self.view.get_mysql_username()
        config.PASSWORD = self.view.get_mysql_password()
        config.SECRET_JWT_KEY = generate_secret_key()
        set_key(ENV_FILE, 'USERNAME_DB', config.USERNAME)
        set_key(ENV_FILE, 'PASSWORD', config.PASSWORD)
        set_key(ENV_FILE, 'SECRET_JWT_KEY', config.SECRET_JWT_KEY)
        self.view.success_creation_env()

    def init_database(self, database: str = DATABASE, datas: bool = False):
        """Permet de créer la base de données ainsi que toutes les tables.
        Si aucun nom de base de données est entré en paramètre, cela créera
        la base de données avec pour nom le nom entré dans config.DATABASE.

        Args:
            base_name (str, optional): Nom de la base de données si nécessaire.
                Défaut: ''.
        """
        if not ENV_FILE.exists():
            self._create_env_file()

        result = self._create_database(database)
        if not result:
            self.view.error_creation_database(database)
            return

        self.view.success_creation_database(database)
        self._create_tables(database)
        self.view.success_creation_tables()
        if datas:
            generate_datas()
            self.view.show_datas_created()

        capture_message(
            'Base de données | Succès de la création de la base de données.',
            level='info'
        )
