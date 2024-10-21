from models import models
from controllers.session import with_session, add_and_commit_in_base
from controllers.permissions import is_authenticated, is_in_department
from views.clients import ClientView
from controllers.authentication import get_user_id

class ClientController:

    @with_session
    def __init__(self, session):
        self.model = models.Client
        self.view = ClientView
        self.all_commercials = models.Commercial.get_users_dict(session)

    @is_authenticated
    @with_session
    def get_all(self, session):
        self.all_clients = self.model.get_all(session)
        session.close()
        self.view.show_all_clients(self.all_clients, self.all_commercials)
        user_id = get_user_id()
        self.select_client()

    @with_session
    @is_in_department(['Commercial'])
    def select_client(self, session):
        valid_choice = [str(i) for i in range(1, len(self.all_clients) + 1)]
        choice = None
        while choice not in valid_choice:
            choice = self.view.select_client_for_option()
            if not choice:
                return
            elif choice not in valid_choice:
                self.view.invalid_user_choice(choice)
                continue

        self.client_selected = self.all_clients[int(choice) - 1]
        session.close()
        user_id = get_user_id()
        if user_id == self.client_selected.commercial_id:
            self.modify()

    @is_authenticated
    @is_in_department(['Commercial'])
    def create(self, first_name, last_name, email, phone_number, company_name):
        result = self.format_phone_number(phone_number)
        if not result:
            return self.view.invalid_phone_number()

        client = self.model.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=self.format_phone_number(phone_number),
            company_name=company_name,
            commercial_id=get_user_id()
        )
        if client:
            add_and_commit_in_base(client)
            self.view.creation_success_message()
        else:
            self.view.creation_error_message()

    @is_authenticated
    @is_in_department(['Commercial'])
    def modify(self):
        choice, number_of_choices = self.view.get_information_to_modify(self.client_selected)
        possible_choices = [str(i) for i in list(range(1, number_of_choices + 1))]
        while choice not in possible_choices:
            if not choice:
                return
            elif choice not in possible_choices:
                self.view.invalid_user_choice(choice)
                choice = self.view.get_information_to_modify(self.client_selected)[0]
                continue

        match choice:
            case '1':
                new_value = self.view.get_new_value('Prénom')
                if new_value:
                    self.client_selected.first_name = new_value
            case '2':
                new_value = self.view.get_new_value('Nom')
                if new_value:
                    self.client_selected.last_name = new_value
            case '3':
                new_value = self.view.get_new_value('Email')
                if new_value:
                    self.client_selected.email = new_value
            case '4':
                new_value = self.view.get_new_value('Téléphone')
                if new_value:
                    result = self.format_phone_number(new_value)

                if not result:
                    self.view.invalid_user_choice(new_value)
                    return

                self.client_selected.phone_number = result
            case '5':
                new_value = self.view.get_new_value('Entreprise')
                if new_value:
                    self.client_selected.company_name = new_value
            case _:
                self.view.invalid_user_choice(choice)
                return

        if new_value:
            add_and_commit_in_base(self.client_selected)
            self.view.modification_success_message()

    @staticmethod
    def _verify_phone_number(phone_number):
        dialing_code = [f'0{i + 1}' for i in range(7)]
        return phone_number.isdigit() and len(phone_number) == 10 and phone_number[:2] in dialing_code

    def format_phone_number(self, phone_number):
        phone_number = phone_number.replace('+33', '0')
        phone_number = phone_number.replace(' ', '').replace('-', '').replace('.', '')
        result = self._verify_phone_number(phone_number)
        if not result:
            return None

        formatted_phone = '.'.join([phone_number[i:i+2] for i in range(0, len(phone_number), 2)])
        return formatted_phone
