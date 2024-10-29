from utils.utils_view import (
    get_success_error_console, get_table, space, convert_date
)

console = get_success_error_console()


class ClientView:

    @staticmethod
    def select_client_to_modify():
        return console.input("Quel est l'ID du client à modifier? : ")

    @staticmethod
    def get_information_to_modify(client):
        space()
        table = get_table(
            "Elément à modifier", ['Numéro', 'Information', 'Valeur']
        )
        table.add_row('1', 'Prénom', client.first_name)
        table.add_row('2', 'Nom', client.last_name)
        table.add_row('3', 'Email', client.email)
        table.add_row('4', 'Téléphone', client.phone_number)
        table.add_row('5', "Nom d'entreprise", client.company_name)
        table.add_row('6', 'Commercial', client.commercial.full_name)
        console.print(table)
        return console.input('Quel est votre choix? : '), table.row_count

    @staticmethod
    def get_new_value(information):
        console.print(f"Nouvelle valeur pour '{information}'?")
        console.print('(Laissez vide pour annuler)', style='italic')
        return console.input(f'{information}: ')

    @staticmethod
    def show_all_clients(all_clients):
        space()
        table = get_table(
            'Clients', [
                'ID', 'Nom', 'Email', 'Téléphone', 'Entreprise', 'Commercial',
                'Date création', 'Date modification'
            ]
        )
        for client in all_clients:
            commercial_name = (
                '-' if client.commercial is None
                else client.commercial.full_name
            )
            table.add_row(
                str(client.id),
                client.full_name,
                client.email,
                client.phone_number,
                client.company_name,
                commercial_name,
                convert_date(client.created_at),
                convert_date(client.updated_at)
            )

        console.print(table)

    @staticmethod
    def creation_success_message():
        console.print("Le client a été créé avec succès.", style='success')

    @staticmethod
    def modification_success_message():
        console.print(
            "La modification a été effectuée avec succès.", style='success'
        )

    @staticmethod
    def creation_error_message():
        console.print('Erreur: Création impossible.', style='error')

    @staticmethod
    def invalid_user_choice(choice):
        console.print(
            f"Votre choix '{choice}' n'est pas un choix valide.", style='error'
        )

    @staticmethod
    def invalid_phone_number():
        console.print(
            "Erreur: Le numéro de téléphone n'est pas valide.", style='error'
        )

    @staticmethod
    def invalid_email(email):
        console.print(f"L'adresse email {email} est invalide.", style='error')

    @staticmethod
    def invalid_commercial():
        console.print("L'ID du commercial entrée est invalide.", style='error')

    @staticmethod
    def get_commercial(all_commercials):
        space()
        table = get_table("Commercial", ['ID', 'Nom'])
        for commercial in all_commercials:
            table.add_row(str(commercial.id), commercial.full_name)

        console.print(table)
        return console.input("Quel est l'ID du commercial? : ")

    @staticmethod
    def invalid_id_choice(choice):
        console.print(
            f"Erreur: L'ID '{choice}' n'est pas un choix valide.",
            style='error'
        )

    @staticmethod
    def unauthorized_modification():
        console.print(
            "Accès refusé: Vous n'êtes pas autorisé à modifier ce client.",
            style='error'
        )

    @staticmethod
    def get_new_client_informations() -> dict[str, str | int]:
        return {
            'first_name': console.input('Prénom du nouveau client: '),
            'last_name': console.input('Nom du nouveau client: '),
            'email': console.input('Email du nouveau client: '),
            'phone_number': console.input(
                'N° de téléphone du nouveau client: '
            ),
            'company_name': console.input(
                "Nom de l'entreprise du nouveau client: "
            )
        }
