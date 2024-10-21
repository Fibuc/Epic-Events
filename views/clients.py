from utils.utils_view import get_success_error_console, get_table, get_console, space, convert_date

console = get_success_error_console()

class ClientView:

    @staticmethod
    def select_client_for_option():
        return console.input(f"Quel est le numéro du client que vous voulez modifier? : ")

    @staticmethod
    def get_information_to_modify(client):
        space()
        table = get_table("Elément à modifier", ['Numéro', 'Information', 'Valeur'])
        table.add_row('1', 'Prénom', client.first_name)
        table.add_row('2', 'Nom', client.last_name)
        table.add_row('3', 'Email', client.email)
        table.add_row('4', 'Téléphone', client.phone_number)
        table.add_row('5', 'Entreprise', client.company_name)
        console.print(table)
        return console.input('Quel est votre choix? : '), table.row_count

    @staticmethod
    def get_new_value(information):
        console.print(f"Nouvelle valeur pour '{information}'?")
        console.print('(Laissez vide pour annuler)', style='italic')
        return console.input(f'{information}: ')

    @staticmethod
    def show_all_clients(all_clients, all_commercials):
        space()
        table = get_table('Clients', ['Numéro', 'Nom', 'Email', 'Téléphone', 'Entreprise', 'Commercial', 'Date création', 'Date modification'])
        for i, client in enumerate(all_clients):
            table.add_row(
                str(i + 1),
                client.full_name,
                client.email,
                client.phone_number,
                client.company_name,
                all_commercials[client.commercial_id],
                convert_date(client.created_at),
                convert_date(client.updated_at)
            )

        console.print(table)

    @staticmethod
    def creation_success_message():
        console.print(f"Le client a été créé avec succès.", style='success')

    @staticmethod
    def modification_success_message():
        console.print("La modification a été effectuée avec succès.", style='success')

    @staticmethod
    def creation_error_message():
        console.print('Erreur: Création impossible.', style='error')

    @staticmethod
    def invalid_user_choice(choice):
        console.print(f"Votre choix '{choice}' n'est pas un choix valide.", style='error')

    @staticmethod
    def invalid_phone_number():
        console.print("Erreur: Le numéro de téléphone n'est pas valide.", style='error')
