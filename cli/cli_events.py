import click

from controllers.events import EventController
from controllers.authentication import AuthController 

user = AuthController().get_user_department

@click.group()
def events():
    """Accède au menu concernant les événements."""
    pass

def add_my_events_option(command):
    user_authenticated = user()
    if user_authenticated == 'Support':
        command = click.option('--my-events', is_flag=True, help="Affiche uniquement mes événements.")(command)
    elif user_authenticated == 'Management':
        command = click.option('--no-support', is_flag=True, help="Liste uniquement les événements n'ayant pas de support.")(command)
    return command

@events.command('list')
@add_my_events_option
@click.option('--date', type=click.Choice(['past', 'upcoming']), help="Liste uniquement les événements correspondant à la période indiquée.")
@click.option('--order-by', type=click.Choice(['id', 'contract', 'client', 'support', 'attendees', 'start', 'end']), help="Trie les événements.")
@click.help_option('--help', help="Les options peuvent être additionnées.")
def list_events(date, order_by, my_events=False, no_support=False):
    """Liste tous les événements"""
    controller = EventController()
    controller.get_events(date, my_events, no_support, order_by)


@click.command('create')
def create_event():
    """Crée un nouvel événement"""
    controller = EventController()
    controller.create()

def add_modify_options(command):
    user_authenticated = user()
    if user_authenticated == 'Support':
        command = click.option('--notes', type=str, help="Nouvelles notes pour l'événement.")(command)
        command = click.option('--attendees', type=int, help="Nouveau nombre de participants.")(command)
        command = click.option('--location', type=str, help="Nouveau lieu de l'événément.")(command)
        command = click.option('--event-end', type=str, help="Nouvelle date de fin de l'événement (JJ/MM/AAAA HH:MM).")(command)
        command = click.option('--event-start', type=str, help="Nouvelle date de début de l'événement (JJ/MM/AAAA HH:MM).")(command)
        command = click.option('--contract-id', type=int, help="L'ID du nouveau contrat.")(command)
    return command

@click.command('modify')
@click.option('--event-id', type=int, help="L'ID de l'événement à associer à un support.")
@click.option('--support-id', type=int, help="L'ID du nouveau support.")
@add_modify_options
def modify_event(
    event_id, support_id=None, contract_id=None, event_start=None,
    event_end=None, location=None, attendees=None, notes=None
):
    """Modifie un événement"""
    controller = EventController()
    controller.modify(
        event_id, support_id, contract_id, event_start, event_end,
        location, attendees, notes
    )


user_authenticated = user()
if user_authenticated == 'Commercial':
    events.add_command(create_event)
if user_authenticated in ['Management', 'Support']:
    events.add_command(modify_event)
