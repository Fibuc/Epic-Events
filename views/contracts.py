from utils.utils_view import get_success_error_console, get_table, get_console, space, convert_date

console = get_success_error_console()

class ContractView:

    @staticmethod
    def select_contract_for_option():
        return console.input(f"Quel est l'ID du contrat que vous voulez modifier? : ")

    @staticmethod
    def get_information_to_modify(contract, clients, commercials):
        space()
        table = get_table("Elément à modifier", ['ID', 'Information', 'Valeur'])
        table.add_row('1', 'Client', clients[contract.client_id])
        table.add_row('2', 'Commercial', commercials[contract.commercial_id])
        table.add_row('3', 'Montant total', str(contract.total_amount_100))
        table.add_row('4', 'Déjà réglé', str(contract.already_paid_100))
        table.add_row('5', 'Statut', contract.status.value)
        console.print(table)
        return console.input('Quel est votre choix? : '), table.row_count

    @staticmethod
    def get_new_value(information):
        console.print(f"Nouvelle valeur pour '{information}'?")
        console.print('(Laissez vide pour annuler)', style='italic')
        return console.input(f'{information}: ')

    @staticmethod
    def get_new_client(clients):
        space()
        table = get_table("Nouveau département", ['Numéro', 'Département'])
        for key, value in clients.items():
            table.add_row(str(key), value)
        
        console.print(table)
        return console.input('Quel est le numéro du nouveau département? : ')

    @staticmethod
    def change_status(contract):
        status_to_change = contract.ContractStatus.signed.value if contract.status == contract.ContractStatus.unsigned else contract.ContractStatus.unsigned.value
        return console.input(f"Tapez 'Oui' changer le statut du contrat '{contract.status.value}' en '{status_to_change}' : ")
        

    @staticmethod
    def get_new_commercial(commercials):
        space()
        table = get_table("Nouveau département", ['Numéro', 'Département'])
        for key, value in commercials.items():
            table.add_row(str(key), value)
        
        console.print(table)
        return console.input('Quel est le numéro du nouveau département? : ')

    @staticmethod
    def show_all_contracts(all_contracts, all_clients, all_commercials):
        space()
        table = get_table('Contrats', ['ID', 'Client', 'Commercial', 'Montant total', 'Déjà réglé', 'Statut', 'Date création', 'Date modification'])
        for contract in all_contracts:
            status = contract.status.value
            if contract.status.value == 'Non signé':
                status = f'[red]{contract.status.value}[/red]'

            table.add_row(
                str(contract.id),
                all_clients[contract.client_id],
                all_commercials[contract.commercial_id],
                str(contract.total_amount_100),
                str(contract.already_paid_100),
                status,
                convert_date(contract.created_at),
                convert_date(contract.updated_at)
            )

        console.print(table)

    @staticmethod
    def creation_success_message():
        console.print(f"Le contrat à été créé avec succès.", style='success')

    @staticmethod
    def modification_success_message():
        console.print("La modification a été effectuée avec succès.", style='success')
    
    @staticmethod
    def creation_error_message():
        console.print('Erreur: Création impossible.', style='error')

    @staticmethod
    def invalid_user_choice(choice):
        console.print(f"Votre choix '{choice}' n'est pas un choix valide.", style='error')
