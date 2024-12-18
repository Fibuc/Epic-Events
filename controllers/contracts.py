from typing import Optional

from sentry_sdk import capture_message

from models import models
from controllers.session import with_session, add_and_commit_in_base
from controllers.permissions import is_authenticated, is_in_department
from controllers.authentication import AuthController
from views.contracts import ContractView


class ContractController:
    """Contrôlleur des contrats"""
    def __init__(self):
        self.model = models.Contract
        self.view = ContractView
        self.auth = AuthController()
        self.model_client = models.Client
        self.model_user = models.User

    @is_authenticated
    @with_session
    def get_contracts(
        self, status: str = '', payment: str = '',
        order_by: str = 'id', my_contracts: bool = False, session=None
    ) -> list[models.Contract]:
        """Récupère la liste de tous les contrats correspondants aux filtres
        appliqués.

        Args:
            status (str, optional): Statut du contrat. Défaut ''.
            payment (str, optional): Solde du contrat. Défaut ''.
            order_by (str, optional): Ordre de tri. Défaut 'id'.
            my_contracts (bool, optional): Contrats liés à l'utilisateur
                connecté. Défaut False.
            session (Session, optional): Session de base de données.
                Défaut None.

        Returns:
            list[Contract]: Liste des contrats correspondants.
        """
        if filters := self._get_filters(status, payment, my_contracts):
            filters['order_by'] = order_by
            all_contracts = self.model.get_filtered_contracts(
                session, **filters
            )
        else:
            all_contracts = self.model.get_all(session, order_by)

        self.view.show_all_contracts(all_contracts)
        return all_contracts

    def _get_filters(
        self, status: str | None, payment: str | None, my_contracts: bool
    ) -> dict:
        """Retourne les filtres à appliquer sur la recherche des contrats.

        Args:
            status (str | None): Statut du contrat.
            payment (str | None): Solde du contrat.
            my_contracts (bool): Contrats liés à l'utilisateur connecté.

        Returns:
            dict: Dictionnaire des filtres.
        """
        filters = {}
        if status:
            if status == 'signed':
                filters['status'] = self.model.ContractStatus.signed
            elif status == 'unsigned':
                filters['status'] = self.model.ContractStatus.unsigned

        if payment:
            if payment == 'sold':
                filters['payment'] = True
            elif payment == 'unsold':
                filters['payment'] = False

        if my_contracts:
            filters['user_id'] = self.auth.get_user_id()

        return filters

    @is_in_department(['Management', 'Commercial'])
    def select_contract(self) -> int | None:
        """Affiche les contrats et retourne l'ID de celui choisit par
        l'utilisateur.

        Returns:
            int | None: Le choix de l'utilisateur si valide, sinon None.
        """
        if self.auth.get_user_department() == 'Commercial':
            all_contracts = self.get_contracts(my_contracts=True)
        else:
            all_contracts = self.get_contracts()
        choice = self.view.select_contract_to_modify()
        if not choice:
            return

        valid_choice = [str(contract.id) for contract in all_contracts]
        if choice not in valid_choice:
            self.view.invalid_id_choice(choice)
            return

        return int(choice)

    @is_authenticated
    @is_in_department(['Management'])
    @with_session
    def create(self, session=None):
        """Crée une instance de Contract et l'enregistre dans la base
        de données.

        Args:
            session (Session, optional): Session de base de données.
                Défaut None.
        """
        contract_informations = {}
        clients = self.model_client.get_all(session)
        possible_choices = [str(client.id) for client in clients]
        choice = self.view.get_client(clients)
        if choice in possible_choices:
            contract_informations['client_id'] = choice
        else:
            self.view.invalid_user_choice(choice)
            return

        commercials = self.model_user.get_filtred_users(
            session, ['Commercial']
        )
        possible_choices = [str(commercial.id) for commercial in commercials]
        choice = self.view.get_commercial(commercials)
        if choice in possible_choices:
            contract_informations['commercial_id'] = choice
        else:
            self.view.invalid_user_choice(choice)
            return

        total_amount, already_paid = self.view.get_new_contract_informations()
        total_amount, already_paid = self._format_in_float(
            [total_amount, already_paid]
        )
        if not total_amount or already_paid is None:
            return

        contract_informations['total_amount'] = total_amount
        contract_informations['already_paid'] = already_paid

        status = self.view.get_status(self.model.ContractStatus)
        match status:
            case '1':
                contract_informations['status'] = (
                    self.model.ContractStatus.signed
                )
            case '2':
                contract_informations['status'] = (
                    self.model.ContractStatus.unsigned
                    )
            case _:
                self.view.not_valid_status()
                return

        if client := self.model.create(**contract_informations):
            add_and_commit_in_base(client)
            self.view.creation_success_message()
        else:
            self.view.creation_error_message()

    def _format_in_float(self, list_of_number: list) -> list[float]:
        """Formate les éléments de la liste en décimaux s'ils sont valides.

        Args:
            list_of_number (list): Liste des éléments à formater.

        Returns:
            list[float]: Liste des nombres décimaux formatés.
        """
        formated_number_list = []
        for number in list_of_number:
            try:
                formated_number_list.append(float(number.replace(',', '.')))

            except ValueError:
                self.view.not_digit(number)
                formated_number_list.append(None)

        return formated_number_list

    @is_authenticated
    @is_in_department(['Commercial', 'Management'])
    @with_session
    def modify(
        self, contract_id: Optional[int] = None,
        client_id: Optional[int] = None, commercial_id: Optional[int] = None,
        total_amount: Optional[int] = None, already_paid: Optional[int] = None,
        status=None, session=None
    ):
        """Récupère les modifications du contrat désiré et effectue la
        sauvegarde de la modification en base de données.

        Args:
            contract_id (Optional[int], optional): ID du contrat.
                Défaut: None.
            client_id (Optional[int], optional): ID du client. Défaut: None.
            commercial_id (Optional[int], optional): ID du commercial.
                Défaut: None.
            total_amount (Optional[int], optional): Montant total du contrat.
                Défaut: None.
            already_paid (Optional[int], optional): Montant déjà payé.
                Défaut: None.
            status (ContractStatus, optional): Statut du contrat. Défaut: None.
            session (Session, optional): Session de base de données.
                Défaut: None.
        """
        contract_selected = self._get_contract(contract_id, session)
        if not contract_selected:
            return

        if (
            self.auth.get_user_department() != 'Management'
            and contract_selected.commercial_id != self.auth.get_user_id()
        ):
            self.view.unauthorized_modification()
            return

        # Applique les changements si des éléments sont entrés en paramètres.
        changes = self._apply_changes(
            contract_selected, client_id, commercial_id,
            total_amount, already_paid, status
        )
        value = None
        # Sinon demande à l'utilisateur les modifications souhaitées.
        if not changes:
            choice = self.view.get_information_to_modify(contract_selected)
            if not choice:
                return

            value = self._get_choice(
                choice, self.model_client.get_all(session),
                self.model_user.get_filtred_users(session, ['Commercial'])
            )

            changes = self._apply_changes(
                contract_selected,
                client_id=value if choice == '1' else None,
                commercial_id=value if choice == '2' else None,
                total_amount=value if choice == '3' else None,
                already_paid=value if choice == '4' else None,
                status=value if choice == '5' else None
            )

        if changes:
            if status == 'signed' or value == 'signed':
                self._get_sentry_message(contract_selected)

            add_and_commit_in_base(contract_selected, session)
            self.view.modification_success_message()

    def _apply_changes(
            self, contract_selected: models.Contract, client_id=None,
            commercial_id=None, total_amount=None, already_paid=None,
            status=None
    ) -> bool | str:
        """Applique les changements dans l'instance du contrat entré en
        paramètre et retourne un booleen indiquant si oui ou non il y a eu
        des changements.

        Args:
            contract_selected (models.Contract): Instance du contrat à
                modifier.
            client_id (int, optional): ID du client. Défaut: None.
            commercial_id (int, optional): ID du commercial. Défaut: None.
            total_amount (float, optional): Montant total du contrat.
                Défaut: None.
            already_paid (float, optional): Montant déjà payé du contrat.
                Défaut: None.
            status (str, optional): Statut du contrat. Défaut: None.

        Returns:
            bool | tuple: Etat du changement du contrat. Et d'une chaîne de
            caractères s'il s'agit de la signature d'un contrat.
        """
        changes = False
        if client_id:
            contract_selected.client_id = client_id
            changes = True
        if commercial_id:
            contract_selected.commercial_id = commercial_id
            changes = True
        if total_amount:
            if total_amount := self._format_in_float([total_amount])[0]:
                if total_amount:
                    contract_selected.total_amount = (
                        self.model.multiply_by_100(total_amount)
                    )
                    changes = True
        if already_paid:
            if already_paid := self._format_in_float([already_paid])[0]:
                if already_paid:
                    contract_selected.already_paid = (
                        self.model.multiply_by_100(already_paid)
                    )
                    changes = True
        if status:
            if status == 'signed':
                contract_selected.status = self.model.ContractStatus.signed
                changes = 'signed'
            elif status == 'unsigned':
                contract_selected.status = self.model.ContractStatus.unsigned
                changes = True

        return changes

    def _get_choice(
        self, choice: str, clients: list[models.Client],
        commercials: list[models.User]
    ):
        """Récupère et retourne la valeur de modification de l'utilisateur.

        Args:
            choice (str): Choix de l'élément à modifier.
            clients (list[models.Client]): Liste d'instances de Client.
            commercials (list[models.User]): Liste d'instances de User.
        """
        match choice:
            case '1':
                choice = self.view.get_client(clients)
                possible_choices = [str(c.id) for c in clients]
                if choice in possible_choices:
                    return int(choice)
            case '2':
                choice = self.view.get_commercial(commercials)
                possible_choices = [str(c.id) for c in commercials]
                if choice in possible_choices:
                    return int(choice)
            case '3':
                return self.view.get_new_value('Montant total')
            case '4':
                return self.view.get_new_value('Déjà réglé')
            case '5':
                status = self.view.get_status(self.model.ContractStatus)
                match status:
                    case '1':
                        return 'signed'
                    case '2':
                        return 'unsigned'
                    case _:
                        self.view.invalid_user_choice(choice)
                        return
            case _:
                self.view.invalid_user_choice(choice)
                return

    def _get_contract(
        self, contract_id: int, session
    ) -> models.Contract | None:
        """Récupère et retourne le contrat souhaité selon son ID.

        Args:
            contract_id (int): ID du contrat désiré.

        Returns:
            models.Contract | None: Retourne l'instance de Contract si trouvé
                sinon None.
        """
        if contract_id:
            return self.model.get_contract_by_id(contract_id, session)
        if user_choice := self.select_contract():
            return self.model.get_contract_by_id(user_choice, session)
        return None

    def _get_sentry_message(self, contract: models.Contract):
        """Crée un message Sentry lorsque le contrat passe du statut
        'Non signé' à 'Signé'.

        Args:
            contract (models.Contract): Contrat signé.
        """
        message = (
            f"Contrat n°{contract.id} | {contract.client.full_name} a"
            f" signé son contrat."
        )
        capture_message(message, level="info")
