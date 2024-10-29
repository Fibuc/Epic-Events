from utils.utils_view import get_success_error_console

console = get_success_error_console()


class AuthView:

    @staticmethod
    def get_password():
        return console.input(
            'Veuillez entrer votre mot de passe: ', password=True
        )

    @staticmethod
    def error_login():
        console.print(
            'Erreur: Identifiant ou mot de passe incorrect.', style='error'
        )

    @staticmethod
    def success_login(username):
        console.print(
            f'Bienvenue {username}, vous êtes connecté.', style='success'
        )

    @staticmethod
    def error_no_user_authenticated():
        console.print(
            'Erreur: Aucun utilisateur connecté actuellement.', style='error'
        )

    @staticmethod
    def success_logout():
        console.print('Vous avez été déconnecté. A bientôt.', style='success')

    @staticmethod
    def get_email():
        return console.input('Veuillez entrer votre adresse email: ')

    @staticmethod
    def error_login_no_database():
        console.print(
            'Erreur: Aucune base de données trouvée. Utilisez createdatabase'
            ' pour en créer une.',
            style='error'
        )

    @staticmethod
    def expired_token():
        console.print(
            "Erreur: Votre session est expirée. Veuillez-vous reconnecter.",
            style='error'
        )

    @staticmethod
    def error_token():
        console.print(
            "Erreur: Une erreur s'est produite. Veuillez-vous reconnecter.",
            style='error'
        )
