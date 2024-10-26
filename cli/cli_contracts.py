import click

from controllers.contracts import ContractController
from controllers.authentication import AuthController 


@click.group()
def contracts():
    """Accède au menu concernant les contrats."""
    pass


def add_my_clients_option(command):
    if AuthController().get_user_department() == 'Commercial':
        command = click.option('--my-contracts', is_flag=True, help="Affiche uniquement mes contrats.")(command)
    return command


@contracts.command('list')
@add_my_clients_option
@click.option('--status', type=click.Choice(['signed', 'unsigned']), help="Liste uniquement les contrats correspondant au statut indiqué.")
@click.option('--payment', type=click.Choice(['sold', 'unsold']), help="Liste uniquement les contrats correspondant au paiement indiqué.")
@click.option('--order-by', type=click.Choice(['id', 'client', 'commercial', 'payment', 'status']), help="Trie les contrats.")
@click.help_option('--help', help="Les options peuvent être additionnées.")
def list_contracts(status, payment, order_by, my_contracts=False):
    """Liste tous les contrats."""
    controller = ContractController()
    controller.get_contracts(status, payment, order_by, my_contracts)


@contracts.command('create')
def create_contract():
    """Crée un nouveau contrat."""
    controller = ContractController()
    controller.create()


@contracts.command('modify')
@click.option('--contract-id', type=int, help="Le numéro du à modifier.")
@click.option('--client-id', type=int, help="L'ID du nouveau client.")
@click.option('--commercial-id', type=int, help="L'ID du nouveau commercial.")
@click.option('--total-amount', type=str,help="Nouveau montant total du contrat.")
@click.option('--already-paid', type=str, help="Nouveau montant déjà payé.")
@click.option('--status', type=click.Choice(['signed', 'unsigned']),help="Nouveau statut du contrat.")
def modify_user(contract_id, client_id, commercial_id, total_amount, already_paid, status):
    """Modifie un contrat."""
    controller = ContractController()
    controller.modify(contract_id, client_id, commercial_id, total_amount, already_paid, status)
