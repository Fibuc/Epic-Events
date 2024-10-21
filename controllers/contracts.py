from models import models
from controllers.session import with_session, add_and_commit_in_base
from controllers.permissions import is_authenticated, is_in_department
from views.contracts import ContractView

class ContractController:

    @with_session
    def __init__(self, session):
        self.model = models.Contract
        self.view = ContractView
        self.all_commercials = models.Commercial.get_users_dict(session)
        self.all_clients = models.Client.get_clients_dict(session)

    @is_authenticated
    @with_session
    def get_all(self, session):
        self.all_contracts = self.model.get_all(session)
        session.close()
        self.view.show_all_contracts(self.all_contracts, self.all_clients, self.all_commercials)
        self.select_contract()

    @with_session
    @is_in_department(['Commercial', 'Management'])
    def select_contract(self, session):
        valid_choice = [str(i) for i in [c.id for c in self.all_contracts]]
        choice = None
        while choice not in valid_choice:
            choice = self.view.select_contract_for_option()
            if not choice:
                return
            elif choice not in valid_choice:
                self.view.invalid_user_choice(choice)
                continue

        self.contract_selected = session.query(models.Contract).filter(models.Contract.id == str(choice)).first()
        session.close()
        self.modify()

    @is_authenticated
    @is_in_department(['Commercial', 'Management'])
    def modify(self):
        choice, number_of_choices = self.view.get_information_to_modify(self.contract_selected, self.all_clients, self.all_commercials)
        possible_choices = [str(i) for i in list(range(1, number_of_choices + 1))]
        while choice not in possible_choices:
            if not choice:
                return
            elif choice not in possible_choices:
                self.view.invalid_user_choice(choice)
                choice = self.view.get_information_to_modify(self.contract_selected, self.all_clients, self.all_commercials)[0]
                continue

        match choice:
            case '1':
                new_value = self.view.get_new_client(self.all_clients)
                if new_value:
                    self.contract_selected.client_id = new_value
            case '2':
                new_value = self.view.get_new_commercial(self.all_commercials)
                if new_value:
                    self.contract_selected.commercial_id = new_value
            case '3':
                new_value = self.view.get_new_value('Montant total')
                result = self.verify_amount_is_digit(new_value)
                if not result:
                    self.view.invalid_user_choice(new_value)
                    return

                self.contract_selected.total_amount = self.model.multiply_by_100(result)
            case '4':
                new_value = self.view.get_new_value('Déjà réglé')
                result = self.verify_amount_is_digit(new_value)
                if not result:
                    self.view.invalid_user_choice(new_value)
                    return

                self.contract_selected.already_paid = self.model.multiply_by_100(result)
            case '5':
                new_value = self.view.change_status(self.contract_selected)
                status_to_change = (
                    self.model.ContractStatus.signed
                    if self.contract_selected.status == self.model.ContractStatus.unsigned
                    else self.model.ContractStatus.unsigned
                )
                if new_value.lower() == 'oui':
                    self.contract_selected.status = status_to_change
            case _:
                self.view.invalid_user_choice(choice)
                return

        if new_value:
            add_and_commit_in_base(self.contract_selected)
            self.view.modification_success_message()

    @staticmethod
    def verify_amount_is_digit(value):
        try:
            value = value.replace(',', '.')
            return float(value)

        except ValueError:
            return None

    @is_authenticated
    @is_in_department(['Management'])
    def create(self, client_id, commercial_id, total_amount, already_paid, status):
        contract = self.model.create(
            client_id=client_id,
            commercial_id=commercial_id,
            total_amount=total_amount,
            already_paid=already_paid,
            status=status
        )
        if contract:
            add_and_commit_in_base(contract)
            self.view.creation_success_message()

        else:
            self.view.creation_error_message()
