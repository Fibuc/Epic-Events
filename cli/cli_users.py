import click

from controllers.users import UserController


@click.group()
def users():
    """Accède au menu concernant les utilisateurs."""
    pass


@users.command('list')
@click.option('--commercial', is_flag=True, help="Liste uniquement les utilisateurs du département 'Commercial'.")
@click.option('--support', is_flag=True, help="Liste uniquement les utilisateurs du département 'Support'.")
@click.option('--management', is_flag=True, help="Liste uniquement les utilisateurs du département 'Management'.")
@click.option('--order-by', type=click.Choice(['id', 'name', 'department']), help="Trie les utilisateurs.")
@click.help_option('--help', help="Les options peuvent être additionnées.")
def list_user(commercial, support, management, order_by):
    """Liste tous les utilisateurs."""
    user_controller = UserController()
    user_controller.get_users(commercial, management, support, order_by)


@users.command('create')
def create_user():
    """Crée un nouvel utilisateur."""
    user_controller = UserController()
    user_controller.create()


@users.command('delete')
@click.option('--user-id', type=int, help="Le numéro de l'utilisateur à supprimer.")
def delete_user(user_id):
    """Supprime un utilisateur."""
    user_controller = UserController()
    user_controller.delete(user_id)


@users.command('modify')
@click.option('--user-id', type=int, help="Le numéro de l'utilisateur à modifier.")
@click.option('--first-name', help="Nouveau prénom.")
@click.option('--last-name', help="Nouveau nom.")
@click.option('--email', help="Nouvel email.")
@click.option('--password', help="Nouveau mot de passe.")
@click.option('--department', type=click.Choice(['Management', 'Commercial', 'Support']), help="Nouveau département.")
def modify_user(user_id, first_name, last_name, email, password, department):
    """Modifie un utilisateur."""
    user_controller = UserController()
    user_controller.modify(user_id, first_name, last_name, email, password, department)

