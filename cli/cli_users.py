import click

from controllers.users import UserController


@click.group()
def users():
    """Menu des utilisateurs."""
    pass


@users.command('list')
@click.option(
    '--commercial',
    is_flag=True,
    help="Liste uniquement les utilisateurs du département 'Commercial'."
)
@click.option(
    '--support',
    is_flag=True,
    help="Liste uniquement les utilisateurs du département 'Support'."
)
@click.option(
    '--management',
    is_flag=True,
    help="Liste uniquement les utilisateurs du département 'Management'."
)
@click.option(
    '--order-by',
    type=click.Choice(['id', 'name', 'department']),
    help="Trie les utilisateurs."
)
@click.help_option(
    '--help',
    help="Les options peuvent être additionnées."
)
def list_user(commercial, support, management, order_by):
    """Liste tous les utilisateurs."""
    controller = UserController()
    controller.get_users(commercial, management, support, order_by)


@users.command('create')
def create_user():
    """Crée un nouvel utilisateur."""
    controller = UserController()
    controller.create()


@users.command('delete')
@click.option(
    '--user-id',
    type=int,
    help="Le numéro de l'utilisateur à supprimer."
)
def delete_user(user_id):
    """Supprime un utilisateur."""
    controller = UserController()
    controller.delete(user_id)


@users.command('modify')
@click.option(
    '--user-id',
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
    '--password',
    type=str,
    help="Nouveau mot de passe."
)
@click.option(
    '--department',
    type=click.Choice(['Management', 'Commercial', 'Support']),
    help="Nouveau département."
)
def modify_user(user_id, first_name, last_name, email, password, department):
    """Modifie un utilisateur."""
    controller = UserController()
    controller.modify(
        user_id, first_name, last_name, email, password, department
    )
