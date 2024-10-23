import click

from cli.cli_users import users
from cli.cli_manager import login, logout, create_database
from controllers.authentication import AuthController
from controllers.session import with_session
from models.models import Department

@click.group()
@click.help_option(help="Saisir cette option avec n'importe quelle commande du CRM affichera des informations détaillées sur son utilisation.")
def cli():
    """
    | ==================================================================== |
| ================= Documentation du CRM Epic-Events ================= |
| ==================================================================== |
    """
    pass


cli.add_command(login)
cli.add_command(logout)
cli.add_command(create_database)


@with_session
def get_summary(session=None):
    auth = AuthController()
    departments = Department.get_departments_dict(session)
    user_department = auth.get_user_department()
    department = departments[user_department]
    if department == 'Management':
        cli.add_command(users)



if __name__ == '__main__':
    try:
        get_summary()
    except:
        pass
    cli()

