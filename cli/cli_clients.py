import click

from controllers.clients import ClientController
from controllers.authentication import AuthController


@click.group()
def clients():
    """Menu des clients."""
    pass


def add_my_clients_option(command):
    """Ajoute l'option '--my-clients' si l'utilisateur est un commercial."""
    if AuthController().get_user_department() == 'Commercial':
        command = click.option(
            '--my-clients',
            is_flag=True,
            help="Affiche uniquement mes clients."
        )(command)
    return command


@clients.command('list')
@add_my_clients_option
@click.option(
    '--order-by',
    type=click.Choice(['id', 'name', 'company', 'commercial']),
    help="Trie les clients."
)
@click.help_option(
    '--help',
    help="Les options peuvent être additionnées."
)
def list_clients(order_by: str, my_clients: bool = False):
    """Liste tous les clients."""
    controller = ClientController()
    controller.get_clients(my_clients, order_by)


@clients.command('create')
def create_client():
    """Crée un nouveau client."""
    controller = ClientController()
    controller.create()


@clients.command('modify')
@click.option(
    '--client-id',
    type=int,
    help="Le numéro de l'utilisateur à modifier."
)
@click.option(
    '--first-name',
    type=str,
    help="Nouveau prénom."
)
@click.option(
    '--last-name',
    type=str,
    help="Nouveau nom."
)
@click.option(
    '--email',
    type=str,
    help="Nouvel email."
)
@click.option(
    '--phone-number',
    type=str,
    help="Nouveau n° de téléphone."
)
@click.option(
    '--company-name',
    type=str,
    help="Nouveau nom d'entreprise."
)
@click.option(
    '--commercial-id',
    type=int,
    help="Nouveau commercial."
)
def modify_client(
    client_id: int, first_name: str, last_name: str, email: str,
    phone_number: str, company_name: str, commercial_id: int
):
    """Modifie un client."""
    controller = ClientController()
    controller.modify(
        client_id, first_name, last_name, email,
        phone_number, company_name, commercial_id
    )
