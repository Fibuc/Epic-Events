from pathlib import Path
from datetime import timedelta
import os

from argon2 import PasswordHasher
from sqlalchemy.orm import declarative_base
import dotenv

dotenv.load_dotenv()

# Sécurisation des mots de passe.
ph = PasswordHasher()

# Récupération des variables d'environnement.
ENV_FILE = Path(__file__).parent / '.env'
SECRET_JWT_KEY = os.getenv('SECRET_JWT_KEY')
USERNAME = os.getenv('USERNAME_DB')
PASSWORD = os.getenv('PASSWORD')
DATABASE = 'epic_events'

# Variables des bases de données.
URL_MYSQL = f'mysql+mysqldb://{USERNAME}:{PASSWORD}@localhost/'
URL_DATABASE = URL_MYSQL + DATABASE
BASE = declarative_base()

# Variables du JWT d'authentification.
TOKEN_DURATION = timedelta(days=0,hours=1,minutes=0)
