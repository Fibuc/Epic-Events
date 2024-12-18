from utils.utils_view import get_success_error_console, get_table, space

console = get_success_error_console()


class UserView:

    @staticmethod
    def select_user_for_option():
        return console.input(
            "Quel est le numéro de l'utilisateur avec lequel vous "
            "voulez interagir? : "
        )

    @staticmethod
    def get_information_to_modify(user):
        space()
        table = get_table(
            "Elément à modifier", ['Numéro', 'Information', 'Valeur']
        )
        table.add_row('1', 'Prénom', user.first_name)
        table.add_row('2', 'Nom', user.last_name)
        table.add_row('3', 'Email', user.email)
        table.add_row('4', 'Mot de passe', '**********')
        table.add_row('5', 'Département', user.department.name)
        console.print(table)
        return console.input('Quel est votre choix? : '), table.row_count

    @staticmethod
    def get_new_value(information):
        console.print(f"Nouvelle valeur pour '{information}'?")
        console.print('(Laissez vide pour annuler)', style='italic')
        return console.input(f'{information}: ')

    @staticmethod
    def select_user(option):
        return console.input(f"Quel est l'ID de l'utilisateur à {option}? : ")

    @staticmethod
    def get_department(all_departments):
        space()
        table = get_table("Département", ['Numéro', 'Département'])
        for department in all_departments:
            table.add_row(str(department.id), department.name)

        console.print(table)
        return console.input(
            'Quel est le numéro du département? : '
        ), table.row_count

    @staticmethod
    def confirm_delete(user):
        return console.input(
            f"Tapez 'Oui' pour confirmer la suppression de "
            f"'{user.full_name}' : "
        ).lower()

    @staticmethod
    def show_all_users(all_users):
        space()
        table = get_table(
            'Utilisateurs', ['ID', 'Nom', 'Email', 'Département']
        )
        for user in all_users:
            table.add_row(
                str(user.id), user.full_name, user.email,
                user.department.name
            )

        console.print(table)

    @staticmethod
    def creation_success_message():
        console.print(
            "L'utilistateur a été créé avec succès.", style='success'
        )

    @staticmethod
    def delete_success_message(user):
        console.print(
            f"L'utilistateur {user.full_name} a été supprimé avec succès.",
            style='success'
        )

    @staticmethod
    def modification_success_message():
        console.print(
            "La modification a été effectuée avec succès.", style='success'
        )

    @staticmethod
    def creation_error_message():
        console.print('Erreur: Création impossible.', style='error')

    @staticmethod
    def invalid_id_choice(choice):
        console.print(f"Erreur: L'ID '{choice}' n'existe pas.", style='error')

    @staticmethod
    def invalid_choice(choice):
        console.print(
            f"Erreur: Le choix '{choice}' est invalide.", style='error'
        )

    @staticmethod
    def invalid_email(email):
        console.print(f"L'adresse email {email} est invalide.", style='error')

    @staticmethod
    def invalid_department():
        console.print("Le département entré est invalide.", style='error')

    @staticmethod
    def get_new_user_informations():
        user_informations = {}
        user_informations['first_name'] = (
            console.input('Prénom du nouvel utilisateur: ')
        )
        user_informations['last_name'] = (
            console.input('Nom du nouvel utilisateur: ')
        )
        user_informations['password'] = (
            console.input('Mot de passe du nouvel utilisateur: ')
        )
        user_informations['email'] = (
            console.input('Email du nouvel utilisateur: ')
        )
        return user_informations
