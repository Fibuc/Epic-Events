class MockContractsView:
    def __init__(self):
        self.contracts = []
        self.message = ''

    def show_all_contracts(self, all_contracts):
        self.contracts = all_contracts

    def get_client(self, clients):
        return '2'

    def get_commercial(self, commercials):
        return '1'

    def invalid_user_choice(self, choice):
        self.message = 'invalid_user_choice'

    def get_new_contract_informations(self):
        return '134', '134'

    def get_status(self, all_status):
        return '1'

    def creation_success_message(self):
        self.message = 'success_creation'

    def select_contract_to_modify(self):
        return '1'

    def modification_success_message(self):
        self.message = 'success_modification'
