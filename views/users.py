from utils.utils_view import get_success_error_console, get_table, get_console, space

console = get_success_error_console()

class UserView:

    @staticmethod
    def prompt_user_action():
        console = get_console()
        console.print('[bold green]1 - Modifier[/bold green]   [bold red]2 - Supprimer[/bold red]')
        return console.input('Quel est votre choix? : ')
    
    @staticmethod
    def select_user_for_option():
        return console.input(f"Quel est le numéro de l'utilisateur avec lequel vous voulez interagir? : ")

    @staticmethod
    def get_information_to_modify(user, all_departments):
        space()
        table = get_table("Elément à modifier", ['Numéro', 'Information', 'Valeur'])
        table.add_row('1', 'Prénom', user.first_name)
        table.add_row('2', 'Nom', user.last_name)
        table.add_row('3', 'Email', user.email)
        table.add_row('4', 'Département', all_departments[user.department])
        console.print(table)
        return console.input('Quel est votre choix? : '), table.row_count
    
    @staticmethod
    def get_new_value(information):
        console.print(f"Nouvelle valeur pour '{information}'?")
        console.print('(Laissez vide pour annuler)', style='italic')
        return console.input(f'{information}: ')

    @staticmethod
    def get_new_department(all_departments):
        space()
        table = get_table("Nouveau département", ['Numéro', 'Département'])
        for key, value in all_departments.items():
            table.add_row(str(key), value)
        
        console.print(table)
        return console.input('Quel est le numéro du nouveau département? : ')

    @staticmethod
    def confirm_delete(user):
        return console.input(f"Tapez 'Oui' pour confirmer la suppression de '{user.full_name}' : ").lower()

    @staticmethod
    def show_all_users(all_users, all_departments):
        space()
        table = get_table('Utilisateurs', ['Numéro', 'Nom', 'Email', 'Département'])
        for i, user in enumerate(all_users):
            table.add_row(str(i + 1), user.full_name, user.email, all_departments[user.department])

        console.print(table)

    @staticmethod
    def creation_success_message(user):
        console.print(f"L'utilistateur {user.full_name} a été créé avec succès.", style='success')

    @staticmethod
    def delete_success_message(user):
        console.print(f"L'utilistateur {user.full_name} a été supprimé avec succès.", style='success')

    @staticmethod
    def modification_success_message():
        console.print("La modification a été effectuée avec succès.", style='success')
    
    @staticmethod
    def creation_error_message():
        console.print('Erreur: Création impossible.', style='error')

    @staticmethod
    def invalid_user_choice(choice):
        console.print(f"Votre choix '{choice}' n'est pas un choix valide.", style='error')
