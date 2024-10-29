import click

from controllers.authentication import AuthController
from controllers.database import DatabaseController


@click.command()
@click.option(
    '--email',
    type=str,
    help="Email de l'utilisateur"
)
def login(*args, **kwargs):
    """Se connecte au CRM."""
    auth = AuthController()
    auth.login(*args, **kwargs)


@click.command()
def logout():
    """Se déconnecte du CRM."""
    auth = AuthController()
    auth.logout()


@click.command(name='createdatabase')
@click.option(
    '--datas',
    is_flag=True,
    help='Base de données avec des données initiales.'
)
def create_database(*args, **kwargs):
    """Crée une base de données."""
    database = DatabaseController()
    database.init_database(*args, **kwargs)
