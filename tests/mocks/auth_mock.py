class MockAuthenticationView:
    def __init__(self, user_informations):
        self.email = user_informations['email']
        self.password = user_informations['password']
        self.messages = []

    def get_email(self):
        return self.email

    def get_password(self):
        return self.password

    def error_login_no_database(self):
        self.messages.append("database_error")

    def error_login(self):
        self.messages.append("login_failed")

    def success_login(self, user_name):
        self.messages.append(f"login_success_{user_name}")
