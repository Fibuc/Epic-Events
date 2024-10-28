from datetime import datetime

from models import models
from controllers.session import with_session, add_and_commit_in_base
from controllers.permissions import is_authenticated, is_in_department
from controllers.authentication import AuthController
from views.events import EventView

class EventController:

    def __init__(self):
        self.model = models.Event
        self.view = EventView
        self.auth = AuthController()
        self.model_contract = models.Contract
        self.model_user = models.User

    @is_authenticated
    @with_session
    def get_events(
        self, date=None, my_events=None, no_support=None,
        order_by='id', session=None
    ):
        filters = {}
        if date:
            if date == 'past':
                filters['date'] = True
            if date == 'upcoming':
                filters['date'] = False

        if my_events:
            filters['support_id'] = self.auth.get_user_id()
        
        if no_support:
            filters['support_id'] = False
        
        if filters:
            filters['order_by'] = order_by
            all_events = self.model.get_filtered_events(session, **filters)
        else:
            all_events = self.model.get_all(session, order_by)

        self.view.show_all_events(all_events)
        return all_events

    @is_authenticated
    @is_in_department(['Commercial'])
    @with_session
    def create(self, session=None):
        event_informations = {}
        signed_contracts_of_commercial = self.model_contract.get_filtered_contracts(
            session, status=self.model_contract.ContractStatus.signed,
            user_id=self.auth.get_user_id()
        )
        possible_choices = [
            str(contract.id)
            for contract in signed_contracts_of_commercial
        ]
        choice = self.view.get_event_contract(signed_contracts_of_commercial)
        if choice not in possible_choices:
            return self.view.invalid_user_choice(choice)
        
        contract_selected = next(
            contract
            for contract in signed_contracts_of_commercial
            if contract.id == int(choice)
            )
        event_informations['contract_id'] = contract_selected.id
        event_informations['client_id'] = contract_selected.client_id
        start_datetime = self.get_date_time()
        if not start_datetime:
            return
        
        event_informations['event_start'] = start_datetime
        end_datetime = self.get_date_time(end_date=True)
        if not end_datetime:
            return
        
        event_informations['event_end'] = end_datetime
        event_informations['location'] = self.view.get_location()

        attendees = self.view.get_attendees()
        if not self.verify_is_digit(attendees):
            self.view.invalid_attendees(attendees)
            return
        
        event_informations['attendees'] = attendees
        event_informations['notes'] = self.view.get_notes()

        event = self.model.create(**event_informations)
        if event:
            add_and_commit_in_base(event)
            self.view.creation_success_message()
        else:
            self.view.creation_error_message()

    def get_date_time(self, end_date=False, modify=False):
        date, hour = self.view.get_date_time(end_date, modify)
        datetime = self.format_to_datetime(date, hour)
        result_datetime = self.verify_date_time(datetime)
        if not result_datetime:
            self.view.invalid_datetime(datetime)
            return
        return result_datetime

    @is_authenticated
    @is_in_department(['Management', 'Support'])
    @with_session
    def modify(
        self, event_id, support_id, contract_id, event_start,
        event_end, location, attendees, notes, session=None
    ):
        click_options = support_id or contract_id or event_start or event_end or location or attendees or notes
        event_selected = self._get_event(event_id, session)
        if not event_selected:
            return
        
        user_department = self.auth.get_user_department()
        if user_department == 'Support':
            if event_selected.support_id != self.auth.get_user_id():
                self.view.unauthorized_modification()
                return
        
        elif user_department == 'Management':
            if event_selected.support_id is not None:
                self.view.unauthorized_modification()
                return

        changes = self._apply_changes(
            event_selected, support_id, contract_id, event_start,
            event_end, location, attendees, notes
        )

        if not changes and not click_options:
            changes, support_id = self._get_modifications(user_department, event_selected, session)

        if support_id and changes:
            confirm = self.view.confirm_support_choice(event_selected.support.full_name)
            if not confirm or confirm.lower() != 'oui':
                self.view.cancel_modifications()
                changes = False

        if changes:
            add_and_commit_in_base(event_selected, session)
            self.view.modification_success_message()
  
    def _get_modifications(self, user_department, event_selected, session):
        supports = self.model_user.get_filtred_users(session, ['Support'])
        if user_department == 'Management':
            support_id = self.view.get_support(supports)
            if not support_id or not support_id.isdigit():
                return

            return self._apply_changes(event_selected, support_id=int(support_id)), support_id
        
        elif user_department == 'Support':
            choice, nb_choice = self.view.get_information_to_modify(event_selected)
            if choice in [str(i + 1) for i in range(nb_choice)]:
                contracts = self.model_contract.get_filtered_contracts(
                    session, status=self.model_contract.ContractStatus.signed
                )
                value = self._get_choice(choice, supports, contracts)
            if choice == '1':
                if not value in [str(contract.id) for contract in contracts]:
                    self.view.invalid_id_choice(value)
                    return None, None

            return self._apply_changes(
                event_selected, 
                contract_id=value if choice == '1' else None,
                event_start=value if choice == '2' else None,
                event_end=value if choice == '3' else None,
                location=value if choice == '4' else None,
                attendees=value if choice == '5' else None,
                notes=value if choice == '6' else None,
                support_id=value if choice == '7' else None,
                session=session
            ), None


    def _apply_changes(
        self, event_selected: models.Event, support_id=None, contract_id=None,
        event_start=None, event_end=None, location=None, attendees=None,
        notes=None, session=None
    ) -> bool:
        """Applique les changements dans l'instance de l'événement entré en paramètre
        et retourne un booleen indiquant si oui ou non il y a eu des changements.

        Args:
            event_selected (models.Contract): Instance de l'événement à modifier.
            support_id (int, optional): ID du support. Défaut: None.
            contract_id (int, optional): ID du contrat. Défaut: None.
            event_start (datetime, optional): Date de début de l'événement. Défaut: None.
            event_end (datetime, optional): Date de fin de l'événement (JJ/MM/AAAA HH:MM). Défaut: None.
            location (str, optional): Lieu de l'événement. Défaut: None.
            attendees (int, optional): Nombre de participants à l'événement. Défaut: None.
            notes (str, optional): Notes de l'événement. Défaut: None.

        Returns:
            bool: Etat du changement de l'événement.
        """
        changes = False
        if support_id:
            if self.check_user_is_support(support_id):
                event_selected.support_id = support_id
                changes = True
            else:
                self.view.not_support(support_id)
                return False
                
        if contract_id:
            if self.check_contract_exist(contract_id):
                if session:
                    session.refresh(event_selected)
                event_selected.contract_id = contract_id
                event_selected.client_id = event_selected.contract.client_id
                changes = True
            else:
                self.view.contract_not_exists(contract_id)
        if event_start:
            if type(event_start) is datetime:
                event_selected.event_start = event_start
                changes = True
            elif event_start := self.verify_date_time(event_start):
                event_selected.event_start = event_start
                changes = True
            else:
                self.view.invalid_datetime(event_start)
                return False
            if event_selected.event_end:
                if event_selected.event_start > event_selected.event_end:
                    event_selected.event_end = None
                    self.view.null_end_date()
        if event_end:
            if type(event_end) is datetime:
                event_selected.event_end = event_end
            elif event_end := self.verify_date_time(event_end):
                event_selected.event_end = event_end
            else:
                self.view.invalid_datetime(event_end)
            if event_selected.event_end > event_selected.event_start:
                changes = True
            else:
                self.view.error_past_date()
        if location:
            event_selected.location = location
            changes = True
        if attendees:
            if self.verify_is_digit(attendees):
                event_selected.attendees = attendees
                changes = True
        if notes:
            event_selected.notes = notes
            changes = True

        return changes

    def _get_event(self, event_id, session) -> models.Event | None:
        if event_id:
            return self.model.get_event_by_id(event_id, session)
        user_choice = self._select_event(option='modifier')
        if user_choice:
            return self.model.get_event_by_id(user_choice, session)
        return None

    def _get_choice(self, choice, supports, contracts):
        match choice:
            case '1':
                return self.view.get_event_contract(contracts)
            case '2':
                return self.get_date_time(modify=True)
            case '3':
                return self.get_date_time(end_date=True, modify=True)
            case '4':
                return self.view.get_location(modify=True)
            case '5':
                return self.view.get_attendees(modify=True)
            case '6':
                return self.view.get_notes(modify=True)
            case '7':
                return self.view.get_support(supports)
            case _:
                self.view.invalid_user_choice(choice)
                return

    @with_session
    @is_in_department(['Management', 'Support'])
    def _select_event(self, option, session=None):
        if self.auth.get_user_department() == 'Support':
            all_events = self.get_events(my_events=True)
        else:
            all_events = self.get_events(no_support=True)

        valid_choice = [str(event.id) for event in all_events]
        if not valid_choice:
            self.view.no_event_to_modify()
            return
        
        choice = self.view.select_event(option)
        if not choice:
            return
        
        if choice not in valid_choice:
            self.view.invalid_id_choice(choice)
            return

        return int(choice)

    @with_session
    def check_user_is_support(self, support_id, session=None):
        supports = self.model_user.get_filtred_users(session, ['Support'])
        return support_id in [support.id for support in supports]
    
    @with_session
    def check_contract_exist(self, contract_id, session=None):
        contract = self.model_contract.get_contract_by_id(contract_id, session)
        if not contract or contract.status != self.model_contract.ContractStatus.signed:
            return False
        return True


    @staticmethod
    def verify_date_time(date_time):
        try:
            return datetime.strptime(date_time, "%d/%m/%Y %H:%M")
        except ValueError or TypeError:
            return False

    @staticmethod
    def verify_is_digit(number):
        if type(number) in [int, float]:
            return True
        if number.isdigit():
            return True
        return False

    @staticmethod
    def format_to_datetime(date, hour):
        return f'{date} {hour}'