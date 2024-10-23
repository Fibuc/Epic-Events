from models import models
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from dotenv import set_key

from config import DATABASE, BASE, ENV_FILE, USERNAME, PASSWORD, SECRET_JWT_KEY
from controllers.session import get_engine
from utils.secret_key import generate_secret_key
from utils.utils_database import generate_datas
from views.database import DatabaseView


class DatabaseController:

    def __init__(self):
        self.view = DatabaseView

    @staticmethod
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
                return True
        
        except ProgrammingError:
            return False

    @staticmethod
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

    def _create_env_file(self):
        ENV_FILE.touch()
        USERNAME = self.view.get_mysql_username()
        PASSWORD = self.view.get_mysql_password()
        SECRET_JWT_KEY = generate_secret_key()
        set_key(ENV_FILE, 'USERNAME_DB', USERNAME)
        set_key(ENV_FILE, 'PASSWORD', PASSWORD)
        set_key(ENV_FILE, 'SECRET_JWT_KEY', SECRET_JWT_KEY)
        self.view.success_creation_env()
     

    def init_database(self, datas):
        """Permet de créer la base de données ainsi que toutes les tables.
        Si aucun nom de base de données est entré en paramètre, cela créera
        la base de données avec pour nom le nom entré dans config.DATABASE.

        Args:
            base_name (str, optional): Nom de la base de données si nécessaire. Défaut: ''.
        """
        if not ENV_FILE.exists():
            self._create_env_file()
            
        
        result = self._create_database(DATABASE)
        if not result:
            self.view.error_creation_database(DATABASE)
            return

        self.view.success_creation_database(DATABASE)
        self._create_tables(DATABASE)
        self.view.success_creation_tables()
        if datas:
            generate_datas()
            self.view.show_datas_created()