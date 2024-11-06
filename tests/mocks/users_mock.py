class MockUsersView:
    def __init__(self):
        self.users = []
        self.message = ''

    def show_all_users(self, all_users):
        self.users = all_users

    def select_user(self, user):
        return '1'

    def modification_success_message(self):
        self.message = 'success_modification'

    def creation_success_message(self):
        self.message = 'success_creation'

    def get_new_user_informations(self):
        return {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'password': '1325',
            'email': 'email.test@gmail.com',
        }

    def get_department(self, department):
        return '1'

    def confirm_delete(self, confirm):
        return 'oui'

    def delete_success_message(self, delete):
        self.message = 'success_delete'
