from email_validator import validate_email, EmailNotValidError

from models import models
from controllers.session import with_session, add_and_commit_in_base, get_session
from controllers.permissions import is_authenticated, is_in_department
from views.clients import ClientView
from controllers.authentication import AuthController

class ClientController:

    def __init__(self):
        self.auth = AuthController()
        self.model_user = models.User
        self.model = models.Client
        self.view = ClientView

    @is_authenticated
    def get_clients(self, my_client, order_by='name'):
        if my_client:
            self.get_clients_of_commercial(order_by=order_by)
        else:
            self.get_all_clients(order_by=order_by)

    @is_authenticated
    @with_session
    def get_all_clients(self, order_by='name', session=None):
        all_clients = self.model.get_all(session, order_by)
        self.view.show_all_clients(all_clients)

    @is_authenticated
    @is_in_department(['Commercial'])
    @with_session
    def get_clients_of_commercial(self, order_by='name', session=None):
        authenticated_user_id = self.auth.get_user_id()
        all_clients = self.model.get_filtred_clients(session, authenticated_user_id, order_by)
        self.view.show_all_clients(all_clients)
        return all_clients

    @with_session
    @is_in_department(['Commercial'])
    def select_client(self, option, session=None):
        all_clients = self.get_clients_of_commercial()
        choice = self.view.select_client(option)
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
    def create(self, session):
        client_informations = self.view.get_new_client_informations()
        phone_number, email = self.verify_user_informations(client_informations)
        if not phone_number:
            return self.view.invalid_phone_number()

        if not email:
            return self.view.invalid_email(client_informations['email'])

        client_informations['commercial_id'] = self.auth.get_user_id()
        client = self.model.create(**client_informations)

        if client:
            add_and_commit_in_base(client)
            self.view.creation_success_message()
        else:
            self.view.creation_error_message()

    def verify_user_informations(self, informations):
        valid_phone_number = self.format_phone_number(informations['phone_number'])
        valid_email_number = self.validate_client_email(informations['email'])
        return valid_phone_number, valid_email_number

    @staticmethod
    def validate_client_email(email) -> bool:
        try:
            valid = validate_email(email)
            email = valid.email
            return True

        except EmailNotValidError:
            return False

    def validate_client_commercial(self, commercial_id, all_commercials):
        try:
            commercial_id = int(commercial_id)
            commercial_list = [c.id for c in all_commercials if c.id == commercial_id]
            if commercial_list:
                return True
            else:
                return False
            
        except ValueError:
            return False

    @is_authenticated
    @is_in_department(['Commercial'])
    @with_session
    def modify(
        self, client_id=None, first_name=None, last_name=None, email=None,
        phone_number=None, company_name=None, commercial_id=None, session=None
    ):
        """Récupère les modifications du client désiré et effectue la sauvegarde de la modification
        en base de données.

        Args:
            client_id (int, optional): ID du client. Défaut: None.
            first_name (str, optional): Prénom du client. Défaut: None.
            last_name (str, optional): Nom du client. Défaut: None.
            email (str, optional): Email du client. Défaut: None.
            phone_number (str, optional): N° de téléphone du client. Défaut: None.
            company_name (str, optional): Nom de l'entreprise du client. Défaut: None.
            commercial_id (int, optional): ID du commercial. Défaut: None.
        """
        client_selected = self._get_client(client_id, session)
        if not client_selected:
            return

        if client_selected.commercial_id != self.auth.get_user_id():
            self.view.unauthorized_modification()
            return
        
        changes = self._apply_changes(client_selected, first_name, last_name, email, phone_number, company_name, commercial_id)

        if not changes:
            choice, nb_choices = self.view.get_information_to_modify(client_selected)
            possible_choices = self._get_possible_choices(nb_choices)
            if not choice:
                return

            if choice not in possible_choices:
                self.view.invalid_choice(choice)
                return

            if choice == possible_choices[-1]:
                commercials = self.model_user.get_filtred_users(session, ['Commercial'])
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
        """Applique les changements dans l'instance du client entré en paramètre
        et retourne un booleen indiquant si oui ou non il y a eu des changements.

        Args:
            client_selected (models.Client): Instance du client à modifier.
            first_name (str, optional): Prénom du client. Défaut: None.
            last_name (str, optional): Nom du client. Défaut: None.
            email (str, optional): Email du client. Défaut: None.
            phone_number (str, optional): N° de téléphone du client. Défaut: None.
            company_name (str, optional): Nom de l'entreprise du client. Défaut: None.
            commercial_id (int, optional): ID du commercial lié au client. Défaut: None.

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
            commercials = self.model_user.get_filtred_users(session, ['Commercial'])
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

    def _get_client(self, client_id: int, session) -> models.Client | None:
        """Récupère et retourne le client souhaité selon son ID.

        Args:
            user_id (int): ID du client désiré.

        Returns:
            models.Client | None: Retourne l'instance de Client si trouvé sinon None.
        """
        if client_id:
            return self.model.get_client_by_id(client_id, session)
        user_choice = self.select_client(option='modifier')
        if user_choice:
            return self.model.get_client_by_id(user_choice, session)
        return None

    @staticmethod
    def _get_possible_choices(possible_choices):
        if type(possible_choices) == int:
            return [str(i + 1) for i in range(possible_choices)]
        elif type(possible_choices) == list[models.Client]:
            return [str(choice.id) for choice in possible_choices]

    @staticmethod
    def _verify_phone_number(phone_number):
        dialing_code = [f'0{i + 1}' for i in range(9)]
        return phone_number.isdigit() and len(phone_number) == 10 and phone_number[:2] in dialing_code

    def format_phone_number(self, phone_number):
        phone_number = phone_number.replace('+33', '0')
        phone_number = phone_number.replace(' ', '').replace('-', '').replace('.', '')
        result = self._verify_phone_number(phone_number)
        if not result:
            return None

        formatted_phone = '.'.join([phone_number[i:i+2] for i in range(0, len(phone_number), 2)])
        return formatted_phone
