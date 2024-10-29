from utils.utils_view import get_success_error_console

console = get_success_error_console()


class DatabaseView:

    @staticmethod
    def error_creation_database(base_name):
        console.print(
            f'Erreur: La base de données [italic]{base_name}[/italic] '
            f'existe déjà.', style='error'
        )

    @staticmethod
    def success_creation_database(base_name):
        console.print(
            f'La base de données [italic]{base_name}[/italic] a été créée '
            f'avec succès!', style='success'
        )

    @staticmethod
    def success_creation_tables():
        console.print(
            'Les tables de la base de données ont été créées avec succès.',
            style='success'
        )

    @staticmethod
    def get_mysql_username():
        return console.input("Nom d'utilisateur MySQL: ")

    @staticmethod
    def get_mysql_password():
        return console.input('Le mot de passe MySQL: ', password=True)

    @staticmethod
    def success_creation_env():
        console.print(
            "L'environnement a bien été créé dans le fichier "
            "[italic bold]'.env'[/italic bold].", style='success'
        )

    @staticmethod
    def show_datas_created():
        console.print(
            "Les données ont été créées avec succès.", style='success'
        )
