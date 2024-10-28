import click

from controllers.authentication import AuthController
from cli.cli_manager import login, logout, create_database
if AuthController().get_user_id():
    from cli.cli_clients import clients
    from cli.cli_contracts import contracts
    from cli.cli_users import users
    from cli.cli_events import events


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
    if user_department := auth.get_user_department():
        cli.add_command(clients)
        cli.add_command(contracts)
        cli.add_command(events)
        if user_department == 'Management':
            cli.add_command(users)



if __name__ == '__main__':
    try:
        get_summary()
    except:
        pass
    cli()

