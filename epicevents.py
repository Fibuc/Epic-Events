import click

from cli.cli_clients import clients
from cli.cli_users import users
from cli.cli_manager import login, logout, create_database
from controllers.authentication import AuthController


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


def get_summary():
    auth = AuthController()
    user_department = auth.get_user_department()
    cli.add_command(clients)
    if user_department == 'Management':
        cli.add_command(users)



if __name__ == '__main__':
    try:
        get_summary()
    except:
        pass
    cli()

