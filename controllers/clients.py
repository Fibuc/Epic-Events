from typing import Optional
from email_validator import validate_email, EmailNotValidError

from models import models
from controllers.session import (
    with_session, add_and_commit_in_base, get_session
)
from controllers.permissions import is_authenticated, is_in_department
from views.clients import ClientView
from controllers.authentication import AuthController


class ClientController:
    """Contrôleur des clients"""
    def __init__(self):
        self.auth = AuthController()
        self.model_user = models.User
        self.model = models.Client
        self.view = ClientView

    @is_authenticated
    def get_clients(self, my_client: bool = False, order_by='name'):
        """Sélectionne la méthode à effectuer selon si l'on veut récupérer
        l'intégralité des clients ou uniquement ceux de liés au commercial
        connecté.

        Args:
            my_client (bool): Clients liés à l'utilisateur
                connecté. Défaut False.
            order_by (str, optional): _description_. Défaut 'name'.
        """
        if my_client:
            self.get_clients_of_commercial(order_by=order_by)
        else:
            self.get_all_clients(order_by=order_by)

    @is_authenticated
    @with_session
    def get_all_clients(self, order_by='name', session=None):
        """Récupère et affiche tous les clients présents dans la base
        de données.
        """
        all_clients = self.model.get_all(session, order_by)
        self.view.show_all_clients(all_clients)

    @is_authenticated
    @is_in_department(['Commercial'])
    @with_session
    def get_clients_of_commercial(
        self, order_by='name', session=None
    ) -> list[models.Client]:
        """Récupère affiche et retourne tous les clients liés au commercial
        connecté.

        Args:
            order_by (str, optional): Option de tri des clients. Défaut 'name'.
            session (Session, optional): Session de base de données.
                Défaut None.

        Returns:
            list[Client]: Liste triée des instances de Client trouvées.
        """
        authenticated_user_id = self.auth.get_user_id()
        all_clients = self.model.get_filtred_clients(
            session, authenticated_user_id, order_by
        )
        self.view.show_all_clients(all_clients)
        return all_clients

    @with_session
    @is_in_department(['Commercial'])
    def select_client_to_modify(self, session=None) -> int | None:
        """Selectionne le client à modifier.

        Args:
            session (Session, optional): Session de base de données.
                Défaut None.

        Returns:
            int | None: Entier correspondant au choix de l'utilisateur si
                valide, sinon None.
        """
        all_clients = self.get_clients_of_commercial()
        choice = self.view.select_client_to_modify()
        valid_choice = [str(client.id) for client in all_clients]
        if not choice:
            return

        if choice not in valid_choice:
            self.view.invalid_id_choice(choice)
            return

        return int(choice)

    @is_authenticated
    @is_in_department(['Commercial'])
    @with_session
    def create(self, session=None):
        """Crée une instance de Client et l'enregistre en base de données.

        Args:
            session (Session, optional): Session de base de données.
                Défaut None.
        """
        client_informations = self.view.get_new_client_informations()
        phone_number, email = self.verify_client_informations(
            client_informations
        )
        if not phone_number:
            self.view.invalid_phone_number()
            return

        if not email:
            self.view.invalid_email(client_informations['email'])
            return

        client_informations['commercial_id'] = self.auth.get_user_id()
        if client := self.model.create(**client_informations):
            add_and_commit_in_base(client)
            self.view.creation_success_message()
        else:
            self.view.creation_error_message()

    def verify_client_informations(
        self, informations: dict
    ) -> tuple[str | None, bool]:
        """Vérifie les informations du client entrés en paramètre.

        Args:
            informations (dict): Dictionnaire des informations à contrôler.

        Returns:
            tuple[str | None, bool]: Tuple comprenant les résultats des
                vérifications.
        """
        valid_phone_number = self.format_phone_number(
            informations['phone_number']
        )
        valid_email_number = self.validate_client_email(informations['email'])
        return valid_phone_number, valid_email_number

    @staticmethod
    def validate_client_email(email) -> bool:
        """Vérifie et retourne la validité de l'email entré en paramètre.

        Args:
            email (str): Email à vérifier.

        Returns:
            bool: Statut de la validité de l'email.
        """
        try:
            valid = validate_email(email)
            email = valid.email
            return True

        except EmailNotValidError:
            return False

    def validate_client_commercial(
        self, commercial_id: int | str, all_commercials: list[models.User]
    ) -> bool:
        """Vérifie et retourne la présence d'un commercial dans la liste des
        commerciaux fournie via son ID entrée en paramètre.

        Args:
            commercial_id (int): ID du commercial à rechercher.
            all_commercials (list[User]): Liste des commerciaux.

        Returns:
            bool: Présence du commercial dans la liste.
        """
        try:
            commercial_id = int(commercial_id)
            commercial_list = [c.id for c in all_commercials]
            return commercial_id in commercial_list

        except ValueError:
            return False

    @is_authenticated
    @is_in_department(['Commercial'])
    @with_session
    def modify(
        self, client_id: Optional[int] = None, first_name=None, last_name=None,
        email=None, phone_number=None, company_name=None, commercial_id=None,
        session=None
    ):
        """Récupère les modifications du client désiré et effectue la
        sauvegarde de la modification en base de données.

        Args:
            client_id (int, optional): ID du client. Défaut: None.
            first_name (str, optional): Prénom du client. Défaut: None.
            last_name (str, optional): Nom du client. Défaut: None.
            email (str, optional): Email du client. Défaut: None.
            phone_number (str, optional): N° de téléphone du client.
                Défaut: None.
            company_name (str, optional): Nom de l'entreprise du client.
                Défaut: None.
            commercial_id (int, optional): ID du commercial. Défaut: None.
        """
        client_selected = self._get_client(client_id, session)
        if not client_selected:
            return

        if client_selected.commercial_id != self.auth.get_user_id():
            self.view.unauthorized_modification()
            return

        # Applique les changements si des éléments sont entrés en paramètres.
        changes = self._apply_changes(
            client_selected, first_name, last_name, email,
            phone_number, company_name, commercial_id
        )

        # Sinon demande à l'utilisateur les modifications souhaitées.
        if not changes:
            choice, nb_choices = self.view.get_information_to_modify(
                client_selected
            )
            possible_choices = self._get_possible_choices(nb_choices)
            if not choice:
                return

            if choice not in possible_choices:
                self.view.invalid_user_choice(choice)
                return

            if choice == possible_choices[-1]:
                commercials = self.model_user.get_filtred_users(
                    session, ['Commercial']
                )
                value = self.view.get_commercial(commercials)
                possible_choices = [str(c.id) for c in commercials]
                if value not in possible_choices:
                    self.view.invalid_user_choice(value)
                    return

            else:
                label = self._get_choice_label(choice)
                value = self.view.get_new_value(label)

            changes = self._apply_changes(
                client_selected,
                first_name=value if choice == '1' else None,
                last_name=value if choice == '2' else None,
                email=value if choice == '3' else None,
                phone_number=value if choice == '4' else None,
                company_name=value if choice == '5' else None,
                commercial_id=int(value) if choice == '6' else None
            )

        if changes:
            add_and_commit_in_base(client_selected, session)
            self.view.modification_success_message()

    def _apply_changes(
        self, client_selected: models.Client, first_name=None, last_name=None,
        email=None, phone_number=None, company_name=None, commercial_id=None
    ) -> bool:
        """Applique les changements dans l'instance du client entré en
        paramètre et retourne un booleen indiquant si oui ou non il y a eu
        des changements.

        Args:
            client_selected (models.Client): Instance du client à modifier.
            first_name (str, optional): Prénom du client. Défaut: None.
            last_name (str, optional): Nom du client. Défaut: None.
            email (str, optional): Email du client. Défaut: None.
            phone_number (str, optional): N° de téléphone du client.
                Défaut: None.
            company_name (str, optional): Nom de l'entreprise du client.
                Défaut: None.
            commercial_id (int, optional): ID du commercial lié au client.
                Défaut: None.

        Returns:
            bool: Etat du changement du client.
        """
        changes = False
        if first_name:
            client_selected.first_name = first_name
            changes = True
        if last_name:
            client_selected.last_name = last_name
            changes = True
        if email and self.validate_client_email(email):
            client_selected.email = email
            changes = True
        if phone_number:
            if formated_phone_number := self.format_phone_number(phone_number):
                client_selected.phone_number = formated_phone_number
                changes = True
        if company_name:
            client_selected.company_name = company_name
            changes = True
        if commercial_id:
            session = get_session()
            commercials = self.model_user.get_filtred_users(
                session, ['Commercial']
            )
            if self.validate_client_commercial(commercial_id, commercials):
                client_selected.commercial_id = commercial_id
                changes = True
            session.close()
        return changes

    def _get_choice_label(self, choice):
        """Renvoie l'étiquette associée à chaque choix."""
        return {
            '1': 'Prénom',
            '2': 'Nom',
            '3': 'Email',
            '4': 'Téléphone',
            '5': "Nom d'entreprise"
        }[choice]

    def _get_client(
        self, client_id: int | None, session
    ) -> models.Client | None:
        """Récupère et retourne le client souhaité selon son ID.

        Args:
            client_id (int): ID du client désiré.

        Returns:
            models.Client | None: Retourne l'instance de Client si trouvé
                sinon None.
        """
        if client_id:
            return self.model.get_client_by_id(client_id, session)
        if user_choice := self.select_client_to_modify():
            return self.model.get_client_by_id(user_choice, session)
        return None

    @staticmethod
    def _get_possible_choices(
        possible_choices: int | models.Client
    ) -> list[str]:
        """Retourne la liste des choix possibles pour l'utilisateur selon les
        données entrées en paramètres.

        Args:
            possible_choices (int | models.Client): Nombre de choix possibles
                ou liste des clients possibles.

        Returns:
            list[str]: Liste des différents choix disponibles.
        """
        possible_choices_list = []
        if isinstance(possible_choices, int):
            possible_choices_list = [
                str(i + 1) for i in range(possible_choices)
            ]
        elif type(possible_choices) == list[models.Client]:  # noqa: E721
            possible_choices_list = [
                str(choice.id) for choice in possible_choices
            ]
        return possible_choices_list

    @staticmethod
    def _verify_phone_number(phone_number: str) -> bool:
        """Vérifie et retourne la validité du numéro de téléphone entré en
        paramètre.

        Args:
            phone_number (str): Numéro de téléphone à vérifier

        Returns:
            bool: Validité du numéro de téléphone.
        """
        dialing_code = [f'0{i + 1}' for i in range(9)]
        return (
            phone_number.isdigit()
            and len(phone_number) == 10 and phone_number[:2] in dialing_code
        )

    def format_phone_number(self, phone_number: str) -> str | None:
        """Formate le numéro de téléphone entré en paramètre s'il est validé
        préalablement.

        Args:
            phone_number (str): Numéro de téléphone à formater.

        Returns:
            str | None: Retourne le numéro de téléphone formaté si valide,
                Sinon None.
        """
        phone_number = phone_number.replace('+33', '0')
        phone_number = (
            phone_number.replace(' ', '').replace('-', '').replace('.', '')
        )
        if not self._verify_phone_number(phone_number):
            return None

        return '.'.join(
            [phone_number[i:i+2] for i in range(0, len(phone_number), 2)]
        )
