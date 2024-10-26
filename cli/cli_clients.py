import click

from controllers.clients import ClientController
from controllers.authentication import AuthController 


@click.group()
def clients():
    """Accède au menu concernant les clients."""
    pass


def add_my_clients_option(command):
    if AuthController().get_user_department() == 'Commercial':
        command = click.option('--my-clients', is_flag=True, help="Affiche uniquement mes clients.")(command)
    return command


@clients.command('list')
@add_my_clients_option
@click.option('--order-by', type=click.Choice(['id', 'name', 'company', 'commercial']), help="Trie les clients.")
@click.help_option('--help', help="Les options peuvent être additionnées.")
def list_clients(order_by, my_clients=None):
    """Liste tous les utilisateurs."""
    client_controller = ClientController()
    client_controller.get_clients(my_clients, order_by)


@clients.command('create')
def create_client():
    """Crée un nouveau client."""
    client_controller = ClientController()
    client_controller.create()


@clients.command('modify')
@click.option('--client-id', type=int, help="Le numéro de l'utilisateur à modifier.")
@click.option('--first-name', help="Nouveau prénom.")
@click.option('--last-name', help="Nouveau nom.")
@click.option('--email', help="Nouvel email.")
@click.option('--phone-number', help="Nouveau n° de téléphone.")
@click.option('--company-name', help="Nouveau nom d'entreprise.")
@click.option('--commercial-id', help="Nouveau commercial.")
def modify_user(client_id, first_name, last_name, email, phone_number, company_name, commercial_id):
    """Modifie un client."""
    client_controller = ClientController()
    client_controller.modify(client_id, first_name, last_name, email, phone_number, company_name, commercial_id)
