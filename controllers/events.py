from datetime import datetime
from typing import Optional

from models import models
from controllers.session import with_session, add_and_commit_in_base
from controllers.permissions import is_authenticated, is_in_department
from controllers.authentication import AuthController
from views.events import EventView


class EventController:
    """Contrôleur des événements"""
    def __init__(self):
        self.model = models.Event
        self.view = EventView
        self.auth = AuthController()
        self.model_contract = models.Contract
        self.model_user = models.User

    @is_authenticated
    @with_session
    def get_events(
        self, date: str = '', my_events: bool = False,
        no_support: bool = False, order_by: str = 'id', session=None
    ) -> list[models.Event]:
        """Récupère la liste de tous les événements correspondants aux filtres
        appliqués.

        Args:
            date (str, optional): Dates de l'événement. Défaut None.
            my_events (bool, optional): Evénements liés à l'utilisateur
                connecté. Défaut None.
            no_support (bool, optional): Evénements n'ayant pas de support
                associé. Défaut None.
            order_by (str, optional): Ordre de tri des événements. Défaut 'id'.
            session (Session, optional): Session de base de données.
                Défaut None.

        Returns:
            list[Event]: Liste des événements correspondants.
        """
        if filters := self._get_filters(date, my_events, no_support):
            filters['order_by'] = order_by
            all_events = self.model.get_filtered_events(session, **filters)
        else:
            all_events = self.model.get_all(session, order_by)

        self.view.show_all_events(all_events)
        return all_events

    def _get_filters(
        self, date: str | None, my_events: bool, no_support: bool
    ) -> dict:
        """Retourne les filtres à appliquer sur la recherche des événements.

        Args:
            date (str | None): Filtre de date.
            my_events (bool): Evénements liés à l'utilisateur connecté.
            no_support (bool): Evénements n'ayant pas de support associé.

        Returns:
            dict: Dictionnaire des filtres.
        """
        filters = {}
        if date:
            if date == 'past':
                filters['date'] = True
            elif date == 'upcoming':
                filters['date'] = False

        if my_events:
            filters['support_id'] = self.auth.get_user_id()

        if no_support:
            filters['support_id'] = False

        return filters

    @is_authenticated
    @is_in_department(['Commercial'])
    @with_session
    def create(self, session=None):
        """Crée une instance de Event et l'enregistre dans la base
        de données.

        Args:
            session (Session, optional): Session de base de données.
                Défaut None.
        """
        signed_contracts_of_commercial = (
            self.model_contract.get_filtered_contracts(
                session, status=self.model_contract.ContractStatus.signed,
                user_id=self.auth.get_user_id()
            )
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
        event_informations = {
            'contract_id': contract_selected.id,
            'client_id': contract_selected.client_id,
        }
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

        if event := self.model.create(**event_informations):
            add_and_commit_in_base(event)
            self.view.creation_success_message()
        else:
            self.view.creation_error_message()

    def get_date_time(self, end_date=False, modify=False) -> datetime | None:
        """Transforme une chaîne de caractères en instance datetime.

        Args:
            end_date (bool, optional): Date de fin (True), Date de début
                (False). Défaut False.
            modify (bool, optional): Modification True or False. Défaut False.

        Returns:
            datetime | None: Instance datetime si valide, sinon None.
        """
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
        self, event_id: Optional[int] = None, support_id: Optional[int] = None,
        contract_id: Optional[int] = None, event_start: str = '',
        event_end: str = '', location: str = '',
        attendees: Optional[int] = None, notes: str = '', session=None
    ):
        """Récupère les modifications de l'événement désiré et effectue la
        sauvegarde de la modification en base de données.

        Args:
            event_id (Optional[int], optional): ID de l'événement. Défaut None.
            support_id (Optional[int], optional): ID du support. Défaut None.
            contract_id (Optional[int], optional): ID du contrat. Défaut None.
            event_start (str, optional): Date de début. Défaut ''.
            event_end (str, optional): Date de fin. Défaut ''.
            location (str, optional): Lieu. Défaut ''.
            attendees (Optional[int], optional): Nombre de participants.
                Défaut None.
            notes (str, optional): Notes. Défaut ''.
            session (Session, optional): Session de base de données.
                Défaut None.
        """
        click_options = any([
            support_id, contract_id, event_start,
            event_end, location, attendees, notes
        ])
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

        # Applique les changements si des éléments sont entrés en paramètres.
        changes = self._apply_changes(
            event_selected, support_id, contract_id, event_start,
            event_end, location, attendees, notes
        )

        # Sinon demande à l'utilisateur les modifications souhaitées.
        if not changes and not click_options:
            changes, support_id = self._get_modifications(
                user_department, event_selected, session
            )

        if support_id and changes:
            confirm = self.view.confirm_support_choice(
                event_selected.support.full_name
            )
            if not confirm or confirm.lower() != 'oui':
                self.view.cancel_modifications()
                changes = False

        if changes:
            add_and_commit_in_base(event_selected, session)
            self.view.modification_success_message()

    def _get_modifications(
        self, user_department: str, event_selected: models.Event, session=None
    ):
        """Affiche les différentes possibilités de modification selon le
        département de l'utilisateur connecté et retourne les changements.

        Args:
            user_department (str): Département de l'utilisateur connecté.
            event_selected (Event): Evénement sélectionné.
            session (Session, optionnal): Session de base de données.
            Défaut None.

        Returns:
            bool: Etat des modifications.
        """
        supports = self.model_user.get_filtred_users(session, ['Support'])
        if user_department == 'Management':
            support_id = self.view.get_support(supports)
            if not support_id or not support_id.isdigit():
                return

            return (
                self._apply_changes(
                    event_selected, support_id=int(support_id)
                ), support_id
            )

        elif user_department == 'Support':
            choice, nb_choice = (
                self.view.get_information_to_modify(event_selected)
            )
            if choice in [str(i + 1) for i in range(nb_choice)]:
                contracts = self.model_contract.get_filtered_contracts(
                    session, status=self.model_contract.ContractStatus.signed
                )
                value = self._get_choice(choice, supports, contracts)
            if choice == '1' and value not in [str(c.id) for c in contracts]:
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
        """Applique les changements dans l'instance de l'événement entré en
        paramètre et retourne un booleen indiquant si oui ou non il y a eu
        des changements.

        Args:
            event_selected (models.Event): Instance de l'événement à
                modifier.
            support_id (int, optional): ID du support. Défaut: None.
            contract_id (int, optional): ID du contrat. Défaut: None.
            event_start (datetime, optional): Date de début de l'événement.
                Défaut: None.
            event_end (datetime, optional): Date de fin de l'événement
                (JJ/MM/AAAA HH:MM). Défaut: None.
            location (str, optional): Lieu de l'événement. Défaut: None.
            attendees (int, optional): Nombre de participants.
                Défaut: None.
            notes (str, optional): Notes pour l'événement. Défaut: None.

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
            if isinstance(event_start, datetime):
                event_selected.event_start = event_start
                changes = True
            elif event_start := self.verify_date_time(event_start):
                event_selected.event_start = event_start
                changes = True
            else:
                self.view.invalid_datetime(event_start)
                return False
            if (
                event_selected.event_end
                and event_selected.event_start > event_selected.event_end
            ):
                event_selected.event_end = None
                self.view.null_end_date()
        if event_end:
            if isinstance(event_end, datetime):
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
        if attendees and self.verify_is_digit(attendees):
            event_selected.attendees = attendees
            changes = True
        if notes:
            event_selected.notes = notes
            changes = True

        return changes

    def _get_event(self, event_id: int, session=None) -> models.Event | None:
        """Récupère et retourne un événement selon son id si trouvé.

        Args:
            event_id (int): ID de l'événement recherché.
            session (Session, optionnal): Session de base de données.
                Défaut None.

        Returns:
            models.Event | None: Evénement si trouvé, sinon None.
        """
        if event_id:
            return self.model.get_event_by_id(event_id, session)
        if user_choice := self._select_event():
            return self.model.get_event_by_id(user_choice, session)
        return None

    def _get_choice(
        self, choice, supports: list[models.User],
        contracts: list[models.Contract]
    ):
        """Traite le choix de l'utilisateur et retourne la valeur
        de obtenue.

        Args:
            choice (str): Choix de l'utilisateur.
            supports (list[User]): Liste des différents Supports.
            contracts (list[Contract]): Liste des différents Contracts.
        """
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
    def _select_event(self, session=None) -> int | None:
        """Sélectionne l'événement selon le département de l'utilisateur
        connecté et retourne le choix de l'utilisateur si valide.

        Args:
            session (Session, optional): Session de base de données.
                Défault None.

        Returns:
            int: Choix utilisateur si valide, sinon None.
        """
        if self.auth.get_user_department() == 'Support':
            all_events = self.get_events(my_events=True)
        else:
            all_events = self.get_events(no_support=True)

        valid_choice = [str(event.id) for event in all_events]
        if not valid_choice:
            self.view.no_event_to_modify()
            return

        choice = self.view.select_event_to_modify()
        if not choice:
            return

        if choice not in valid_choice:
            self.view.invalid_id_choice(choice)
            return

        return int(choice)

    @with_session
    def check_user_is_support(self, support_id: int, session=None) -> bool:
        """Vérifie si l'utilisateur fait parti du département Support.

        Args:
            support_id (int): ID du support recherché.
            session (Session, optional): Session en base de données.
                Défaut None.

        Returns:
            bool: Etat de la vérification.
        """
        supports = self.model_user.get_filtred_users(session, ['Support'])
        return support_id in [support.id for support in supports]

    @with_session
    def check_contract_exist(self, contract_id: int, session=None) -> bool:
        """Vérifie si le contrat existe.

        Args:
            contract_id (int): ID du contrat recherché
            session (Session, optional):Session en base de données.
                Défaut None.

        Returns:
            bool: Etat de la vérification.
        """
        contract = self.model_contract.get_contract_by_id(contract_id, session)
        return bool(
            contract
            and contract.status == self.model_contract.ContractStatus.signed
        )

    @staticmethod
    def verify_date_time(date_time: str) -> datetime | None:
        """Vérifie la validité de la date entrée en paramètre.
        (Format JJ/MM/AAAA hh:mm) et retourne l'instance datetime si valide.

        Args:
            date_time (str): Date à vérifier.

        Returns:
            datetime | None: Instance datetime si valide, sinon None.
        """
        try:
            return datetime.strptime(date_time, "%d/%m/%Y %H:%M")
        except ValueError or TypeError:
            return None

    @staticmethod
    def verify_is_digit(number) -> bool:
        """Vérifie si l'élément entré en paramètre est un nombre.

        Args:
            number: Elément à vérifier.

        Returns:
            bool: Etat de la vérification.
        """
        return True if type(number) in [int, float] else bool(number.isdigit())

    @staticmethod
    def format_to_datetime(date: str, hour: str):
        """Formate la date et l'heure pour la transformation en instance
        datetime.

        Returns:
            str: La date et l'heure formatés.
        """
        return f'{date} {hour}'
