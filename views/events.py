from utils.utils_view import get_success_error_console, get_table, get_console, space, convert_date

console = get_success_error_console()

class EventView:

    @staticmethod
    def select_event(option):
        return console.input(f"Quel est l'ID de l'événement à {option}? : ")

    @staticmethod
    def get_date_time(end_date=False, modify=False):
        date = console.input(f'Quelle est la {'nouvelle ' if modify else ''}date de {'fin' if end_date else 'début'}? (JJ/MM/AAAA) : ')
        time = console.input(f'Quelle est la {'nouvelle ' if modify else ''}heure de {'fin' if end_date else 'début'}? (HH:MM): ')
        return date, time

    @staticmethod
    def show_all_events(all_events):
        table = get_table('Evénements', ['ID', 'Client', 'N°Contrat', 'Début Evénement', 'Fin Evénement', 'Support', 'Lieu', 'Nb. Participants', 'Notes'])
        for event in all_events:
            end_date = '[italic black]Aucune[/italic black]' if not event.event_end else convert_date(event.event_end)
            support_name = '[italic black]Aucun[/italic black]' if not event.support else event.support.full_name
            notes = '[italic black]Aucunes[/italic black]' if not event.notes else event.notes
            table.add_row(
                str(event.id),
                event.client.full_name,
                str(event.contract_id),
                convert_date(event.event_start),
                end_date,
                support_name,
                event.location,
                str(event.attendees),
                notes
            )
        if table.row_count > 0:
            space()
            console.print(table)

    @staticmethod
    def get_information_to_modify(event):
        end_date = '[italic black]Aucune[/italic black]' if not event.event_end else convert_date(event.event_end)
        notes = '[italic black]Aucunes[/italic black]' if not event.notes else event.notes
        space()
        table = get_table("Elément à modifier", ['Numéro', 'Information', 'Valeur'])
        table.add_row('1', 'Contrat', f'Contrat n°{event.contract.id} - Client {event.contract.client.full_name}')
        table.add_row('2', 'Début événement', convert_date(event.event_start))
        table.add_row('3', 'Fin événement', end_date)
        table.add_row('4', 'Lieu', event.location)
        table.add_row('5', 'Nb. Participants', str(event.attendees))
        table.add_row('6', 'Notes', notes)
        table.add_row('7', 'Support', event.support.full_name)
        console.print(table)
        return console.input('Quel est votre choix? : '), table.row_count

    @staticmethod
    def creation_success_message():
        console.print(f"L'événement a été créé avec succès.", style='success')

    @staticmethod
    def modification_success_message():
        console.print("La modification a été effectuée avec succès.", style='success')

    @staticmethod
    def creation_error_message():
        console.print('Erreur: Création impossible.', style='error')

    @staticmethod
    def invalid_user_choice(choice):
        console.print(f"Votre choix \"{choice}\" n'est pas un choix valide.", style='error')

    @staticmethod
    def get_event_contract(all_contracts):
        space()
        table = get_table('Contrats', ['ID', 'Client', 'Commercial', 'Montant total', 'Statut'])
        for contract in all_contracts:
            commercial_name = '-' if contract.commercial == None else contract.commercial.full_name
            table.add_row(
                str(contract.id),
                contract.client.full_name,
                commercial_name,
                str(contract.total_amount_100),
                f'[yellow]{contract.status.value}[/yellow]',
            )

        console.print(table)
        return console.input("Quel est l'ID du contrat? : ")
    
    @staticmethod
    def invalid_datetime(date_time):
        console.print(f"La date \"{date_time}\" ne respecte pas le format \"JJ/MM/AAAA hh:mm\".", style='error')

    @staticmethod
    def invalid_attendees(attendees):
        console.print(f"Le nombre de participants \"{attendees}\" n'est pas valide.", style='error')

    @staticmethod
    def get_location(modify=False):
        return console.input(f"Quelle est l{"a nouvelle " if modify else "'"}adresse de l'événement? : ")

    @staticmethod
    def get_attendees(modify=False):
        return console.input(f"Quel est le {"nouveau " if modify else ''}nombre de participants? : ")

    @staticmethod
    def invalid_id_choice(choice):
        console.print(f"Erreur: L'ID '{choice}' n'est pas un choix valide.", style='error')

    @staticmethod
    def get_notes(modify=False):
        return console.input(f"{'' if modify else '[italic][Facultatif][/italic] '}Ajouter des notes? : ")
    
    @staticmethod
    def unauthorized_modification():
        console.print(f"Accès refusé: Vous n'êtes pas autorisé à modifier cet événement.", style='error')
    
    @staticmethod
    def contract_not_exists(contract_id):
        console.print(f"Erreur: Le contrat ayant pour ID {contract_id} n'existe pas.", style='error')

    @staticmethod
    def not_support(support_id):
        console.print(f"Erreur: L'utilisateur ayant pour ID {support_id} n'existe pas ou n'est pas support.", style='error')
 
    @staticmethod
    def no_event_to_modify():
        console.print(f"\n - Vous n'avez aucun événement.\n", style='italic')

    @staticmethod
    def confirm_support_choice(support_name):
        return console.input(f"Saisissez '[bold]Oui[/bold]' pour confirmer l'association de {support_name} à l'événement : ")

    @staticmethod
    def cancel_modifications():
        console.print(f"La modification n'a pas été effectuée.", style='italic')

    @staticmethod
    def error_past_date():
        console.print(f"Erreur: La date désirée est antérieure à la date du début l'événement", style='error')
   
    @staticmethod
    def null_end_date():
        console.print(f"Avertissement: La date de fin de l'événement a été supprimée car elle est antérieure à la date de début.", style='warning')

    @staticmethod
    def get_support(all_supports):
        space()
        table = get_table('Supports', ['ID', 'Nom'])
        for support in all_supports:
            table.add_row(str(support.id), support.full_name)
        
        console.print(table)
        return console.input("Quel est l'ID du support à associer au contrat? : ")
