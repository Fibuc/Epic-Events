from utils.utils_view import (
    get_success_error_console, get_table, space, convert_date
)

console = get_success_error_console()


class ContractView:

    @staticmethod
    def select_contract_to_modify():
        return console.input("Quel est l'ID du contrat à modifier? : ")

    @staticmethod
    def get_information_to_modify(contract):
        commercial_name = (
            '-'
            if contract.commercial is None
            else contract.commercial.full_name
        )
        space()
        table = get_table(
            "Elément à modifier", ['ID', 'Information', 'Valeur']
        )
        table.add_row('1', 'Client', contract.client.full_name)
        table.add_row('2', 'Commercial', commercial_name)
        table.add_row('3', 'Montant total', str(contract.total_amount_100))
        table.add_row('4', 'Déjà réglé', str(contract.already_paid_100))
        table.add_row('5', 'Statut', contract.status.value)
        console.print(table)
        return console.input('Quel est votre choix? : ')

    @staticmethod
    def get_new_value(information):
        console.print(f"Nouvelle valeur pour '{information}'?")
        console.print('(Laissez vide pour annuler)', style='italic')
        return console.input(f'{information}: ')

    @staticmethod
    def get_new_client(clients):
        space()
        table = get_table("Nouveau client", ['Numéro', 'Nom'])
        for key, value in clients.items():
            table.add_row(str(key), value)

        console.print(table)
        return console.input('Quel est le numéro du nouveau client? : ')

    @staticmethod
    def change_status(contract):
        status_to_change = (
            contract.ContractStatus.signed.value
            if contract.status == contract.ContractStatus.unsigned
            else contract.ContractStatus.unsigned.value
        )
        return console.input(
            f"Tapez 'Oui' changer le statut du contrat '"
            f"{contract.status.value}' en '{status_to_change}' : "
        )

    @staticmethod
    def get_new_commercial(commercials):
        space()
        table = get_table("Nouveau commercial", ['Numéro', 'Nom'])
        for key, value in commercials.items():
            table.add_row(str(key), value)

        console.print(table)
        return console.input('Quel est le numéro du nouveau commercial? : ')

    @staticmethod
    def show_all_contracts(all_contracts):
        space()
        table = get_table(
            'Contrats', [
                'ID', 'Client', 'Commercial', 'Montant total', 'Déjà réglé',
                'Restant dû', 'Statut', 'Date création', 'Date modification'
            ]
        )
        for contract in all_contracts:
            sold = (
                str(contract.outstanding_balance)
                if contract.outstanding_balance > 0
                else (
                    '[italic bold bright_green]Soldé'
                    '[/italic bold bright_green]'
                )
            )
            status = contract.status.value
            if contract.status.value == 'Non signé':
                status = f'[red]{contract.status.value}[/red]'
            commercial_name = (
                '-'
                if contract.commercial is None
                else contract.commercial.full_name
            )
            table.add_row(
                str(contract.id),
                contract.client.full_name,
                commercial_name,
                str(contract.total_amount_100),
                str(contract.already_paid_100),
                sold,
                status,
                convert_date(contract.created_at),
                convert_date(contract.updated_at)
            )

        console.print(table)

    @staticmethod
    def creation_success_message():
        console.print("Le contrat a été créé avec succès.", style='success')

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
            f"Votre choix '{choice}' n'est pas un choix valide.",
            style='error'
        )

    @staticmethod
    def get_new_contract_informations():
        total_amount = console.input('Montant du contrat: ')
        already_paid = console.input('Montant déjà réglé: ')
        return total_amount, already_paid

    @staticmethod
    def get_client(all_clients):
        space()
        table = get_table("Clients", ['ID', 'Nom'])
        for client in all_clients:
            table.add_row(str(client.id), client.full_name)

        console.print(table)
        return console.input("Quel est l'ID du client? : ")

    @staticmethod
    def get_commercial(all_commercials):
        space()
        table = get_table("Clients", ['ID', 'Nom'])
        for commercial in all_commercials:
            table.add_row(str(commercial.id), commercial.full_name)

        console.print(table)
        return console.input("Quel est l'ID du commercial? : ")

    @staticmethod
    def not_digit(number):
        console.print(
            f"Votre choix '{number}' n'est pas un nombre.", style='error'
        )

    @staticmethod
    def get_status(all_status):
        space()
        table = get_table("Statut", ['Number', 'Statut'])
        for i, status in enumerate(all_status):
            table.add_row(str(i + 1), status.value)

        console.print(table)
        return console.input("Quel est l'ID du client? : ")

    @staticmethod
    def not_valid_status():
        console.print("Le statut choisi n'est pas valide", style='error')

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
