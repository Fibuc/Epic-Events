from pathlib import Path
import os

from argon2 import PasswordHasher
from sqlalchemy.orm import declarative_base
import dotenv

dotenv.load_dotenv()

# Sécurisation des mots de passe.
ph = PasswordHasher()

# Récupération des variables d'environnement.
SECRET_JWT_KEY = os.getenv('SECRET_JWT_KEY')
USERNAME = os.getenv('USERNAME_DB')
PASSWORD = os.getenv('PASSWORD')
DATABASE = 'epic_events'

# Variables des bases de données.
URL_MYSQL = f'mysql+mysqldb://{USERNAME}:{PASSWORD}@localhost/'
URL_DATABASE = URL_MYSQL + DATABASE
BASE = declarative_base()

# Répertoires d'enregistrement.
JWT_TOKEN_PATH = Path(__file__).parent / 'token.json'