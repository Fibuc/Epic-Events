class MockClientsView:

    def __init__(self):
        self.clients = []
        self.information_to_modify = {
            'first_name': '1',
            'last_name': '2',
            'email': '3',
            'phone_number': '4',
            'company_name': '5',
            'commercial_id': '6'
        }
        self.messages = []

    def show_all_clients(self, all_clients):
        self.clients = all_clients

    def get_information_to_modify(self, information):
        return self.information_to_modify[information], len(information)

    def select_client_to_modify(self):
        return '1'

    def modification_success_message(self):
        self.messages.append('success_modification')

    def creation_success_message(self):
        self.messages.append('success_creation')

    def get_new_client_informations(self):
        return {
            'first_name': 'Jean',
            'last_name': 'Eude',
            'email': 'jean.eude@test.com',
            'phone_number': '03.30.30.30.30',
            'company_name': 'J-Eude Comp'
        }
