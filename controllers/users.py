from typing import Optional

from email_validator import validate_email, EmailNotValidError
from sentry_sdk import capture_message

from models import models
from controllers.permissions import is_authenticated, is_in_department
from controllers.session import (
    add_and_commit_in_base, with_session, get_session
)
from views.users import UserView
from controllers.authentication import AuthController


class UserController:
    """Contrôleur des utilisateurs."""
    def __init__(self):
        self.model = models.User
        self.model_department = models.Department
        self.view = UserView
        self.auth = AuthController()

    @is_authenticated
    @is_in_department(['Management'])
    @with_session
    def get_all_users(self, session=None, order_by='name'):
        """Récupère et affiche tous les utilisateurs.

        Args:
            session (Session, optional): Session de base de données.
                Défaut None.
            order_by (str, optional): Ordre de tri. Défaut 'name'.
        """
        all_users = self.model.get_all(session, order_by)
        self.view.show_all_users(all_users)

    @is_authenticated
    @is_in_department(['Management'])
    @with_session
    def _get_filtred_users(
        self, departments: list[str], order_by: str = 'name', session=None
    ):
        """Récupère et affiche les utilisateurs du département entré en
        paramètre.

        Args:
            departments (list[str]): Liste des départements souhaités.
            order_by (str, optional): Ordre de tri. Défaut 'name'.
            session (Session, optional): Session de base de données.
                Défaut None.
        """
        all_users = self.model.get_filtred_users(
            session, departments, order_by
        )
        self.view.show_all_users(all_users)

    @is_authenticated
    @is_in_department(['Management'])
    def get_users(
        self, commercial: bool = False, management: bool = False,
        support: bool = False, order_by: str = 'name'
    ):
        """Contrôle et retourne la fonction de récupération des utilisateurs
        en fonction des paramètres entrés.

        Args:
            commercial (bool, optional): Filtrer les commerciaux. Défaut False.
            management (bool, optional): Filtrer les gestionnaires.
                Défaut False.
            support (bool, optional): Filtrer les supports. Défaut False.
            order_by (str, optional): Ordre de tri. Défaut 'name'.
        """
        if commercial or management or support:
            departments = []
            if commercial:
                departments.append('Commercial')

            if management:
                departments.append('Management')

            if support:
                departments.append('Support')
            self._get_filtred_users(departments, order_by=order_by)
        else:
            self.get_all_users(order_by=order_by)

    @is_authenticated
    @is_in_department(['Management'])
    @with_session
    def select_user(self, session=None, option: str = 'modifier'):
        """Récupère et retourne l'id de l'utilisateur sélectionné.

        Args:
            option (str): Option qui sera effectué sur l'utilisateur
                (Modification/Suppression).
            session (Session, optional): Session de base de données.
                Défaut None
        Returns:
            int | None: L'ID de l'utilisateur si bien sélectionné sinon None.
        """
        all_users = self.model.get_all(session)
        self.view.show_all_users(all_users)
        valid_choice = [str(user.id) for user in all_users]
        choice = self.view.select_user(option)
        if not choice:
            return

        elif choice not in valid_choice:
            self.view.invalid_id_choice(choice)
            return

        return int(choice)

    @is_authenticated
    @is_in_department(['Management'])
    @with_session
    def modify(
        self, user_id: Optional[int] = None, first_name: str = '',
        last_name: str = '', email: str = '', password: str = '',
        department_name: str = '', session=None
    ):
        """Récupère les modifications de l'utilisateur désiré et effectue la
        sauvegarde de la modification en base de données.

        Args:
            user_id (int, optional): ID de l'utilisateur. Défaut: None.
            first_name (str, optional): Prénom de l'utilisateur. Défaut: ''.
            last_name (str, optional): Nom de l'utilisateur. Défaut: ''.
            email (str, optional): Email de l'utilisateur. Défaut: ''.
            password (str, optional): Mot de passe de l'utilisateur.
                Défaut: ''.
            department_name (str, optional): Département de l'utilisateur.
                Défaut: ''.
            session (Session, optional): Session de base de données.
                Défaut None
        """
        user_selected = self._get_user(user_id, session)
        if not user_selected:
            return

        changes = self._apply_changes(
            user_selected, first_name, last_name,
            email, password, department_name
        )

        if not changes:
            choice, nb_choices = (
                self.view.get_information_to_modify(user_selected)
            )
            possible_choices = self._get_possible_choices(nb_choices)
            if not choice:
                return

            if choice not in possible_choices:
                self.view.invalid_choice(choice)
                return

            if choice == possible_choices[-1]:
                departments = self.model_department.get_all(session)
                value, nb_choices = self.view.get_department(departments)
                possible_choices = self._get_possible_choices(nb_choices)
                if value not in possible_choices:
                    self.view.invalid_choice(value)
                    return

            else:
                label = self._get_choice_label(choice)
                value = self.view.get_new_value(label)

            changes = self._apply_changes(
                user_selected,
                first_name=value if choice == '1' else None,
                last_name=value if choice == '2' else None,
                email=value if choice == '3' else None,
                password=value if choice == '4' else None,
                department_id=int(value) if choice == '5' else None
            )

        if changes:
            add_and_commit_in_base(user_selected, session)
            self.view.modification_success_message()

    def _get_user(
        self, user_id: int | None, session=None
    ) -> models.User | None:
        """Récupère et retourne l'utilisateur souhaité selon son ID.

        Args:
            user_id (int | None): ID de l'utilisateur désiré si existe.
            session (Session, optional): Session de base de données.
                Défaut None

        Returns:
            models.User | None: Retourne l'instance de User ou None.
        """
        if user_id:
            return self.model.get_user_by_id(user_id, session)
        if user_choice := self.select_user(option='modifier'):
            return self.model.get_user_by_id(user_choice, session)
        return None

    def _apply_changes(
        self, user_selected: models.User, first_name: str = '',
        last_name: str = '', email: str = '', password: str = '',
        department_id: Optional[int] = None
    ) -> bool:
        """Applique les changements dans l'instance de l'utilisateur entré en
        paramètre et retourne un booleen indiquant si oui ou non il y a eu
        des changements.

        Args:
            user_selected (models.User): Instance de l'utilisateur à modifier.
            first_name (str, optional): Prénom de l'utilisateur. Défaut: None.
            last_name (str, optional): Nom de l'utilisateur. Défaut: None.
            email (str, optional): Email de l'utilisateur. Défaut: None.
            password (str, optional): Mot de passe de l'utilisateur.
                Défaut: None.
            department_name (str, optional): Département de l'utilisateur.
                Défaut: None.

        Returns:
            bool: Etat du changement de l'utilisateur.
        """
        changes = False
        if first_name:
            user_selected.first_name = first_name
            changes = True
        if last_name:
            user_selected.last_name = last_name
            changes = True
        if password:
            user_selected.password = user_selected.hash_password(password)
            changes = True
        if email and self.validate_user_email(email):
            user_selected.email = email
            changes = True
        if department_id:
            session = get_session()
            departments = self.model_department.get_all(session)
            if self.validate_user_department(department_id, departments):
                user_selected.department_id = department_id
                changes = True
            session.close()
        return changes

    def _get_choice_label(self, choice):
        """Renvoie l'étiquette associée à chaque choix."""
        return {
            '1': 'Prénom',
            '2': 'Nom',
            '3': 'Email',
            '4': 'Mot de passe'
        }[choice]

    @staticmethod
    def _get_possible_choices(number_of_choices: int) -> list[str]:
        """Retourne la liste des choix possibles selon le nombre
        de choix possibles entrés en paramètre.
        """
        return [str(i + 1) for i in range(number_of_choices)]

    @is_authenticated
    @is_in_department(['Management'])
    @with_session
    def delete(self, user_id=None, session=None):
        """Supprime l'utilisateur indiqué en paramètre.

        Args:
            user_id (int, optional): ID de l'utilisateur à supprimer.
                Défaut: None.
        """
        if user_id:
            user_selected = self.model.get_user_by_id(user_id, session)
        elif user_choice := self.select_user(option='supprimer'):
            user_selected = self.model.get_user_by_id(user_choice, session)

        else:
            return

        confirm_choice = self.view.confirm_delete(user_selected)
        if confirm_choice == 'oui' and session:
            self._get_sentry_message(
                user=user_selected, department=user_selected.department.name
            )
            session.delete(user_selected)
            session.commit()
            return self.view.delete_success_message(user_selected)

        return

    @is_authenticated
    @is_in_department(['Management'])
    @with_session
    def create(self, session=None):
        """Crée un nouvel utilisateur et l'enregistre
        dans la base de données.
        """
        user_informations = self.view.get_new_user_informations()
        valid_email = self.validate_user_email(user_informations['email'])
        if not valid_email:
            return self.view.invalid_email(user_informations['email'])

        departments = self.model_department.get_all(session)
        user_informations['department_id'] = (
            self.view.get_department(departments)[0]
        )
        if not self.validate_user_department(
            user_informations['department_id'], departments
        ):
            return self.view.invalid_department()

        user_informations['department_id'] = int(
            user_informations['department_id']
        )
        if user := self.model.create(**user_informations):
            department = next(
                department.name
                for department in departments
                if department.id == user_informations['department_id']
            )
            print(department)
            self._get_sentry_message(
                user=user, department=department, creation=True
            )
            add_and_commit_in_base(user)
            self.view.creation_success_message()
        else:
            self.view.creation_error_message()

    @staticmethod
    def validate_user_email(email: str) -> bool:
        """Vérifie et retourne la validité de l'email entré en paramètre.

        Args:
            email (str): Email à vérifier.

        Returns:
            bool: Etat de la vérification.
        """
        try:
            valid = validate_email(email)
            email = valid.email
            return True

        except EmailNotValidError:
            return False

    def validate_user_department(
        self, department: str, all_departments: list[models.Department]
    ) -> bool:
        """Vérifie et retourne si le département entré fait parti de la liste
        des départements fournie.

        Args:
            department (str): ID du département en chaîne de caractères.
            all_departments (list[Department]): Liste des départments.

        Returns:
            bool: Etat de la vérification.
        """
        try:
            department_id = int(department)
            return bool([
                    d.id for d in all_departments if d.id == department_id
            ])
        except ValueError:
            return False

    def _get_sentry_message(
        self, user: models.User, department: str, creation: bool = False
    ):
        """Crée un message Sentry personnalisé selon la création ou la
        suppression.

        Args:
            user (models.User): Utilisateur créé ou supprimé.
            department (str): Département de l'utilisateur créé ou supprimé.
            creation (bool, optional): Création si True, Suppression si False.
        """
        auth_user_name = self.auth.get_user_name()
        if creation:
            action = 'Création'
            action_verb = 'créé'
            action_verb = 'créé'
        else:
            action = 'Suppression'
            action_verb = 'supprimé'

        role = (
            'Gestionnaire'
            if department == 'Management'
            else department
        )
        message = (
            f"{action} utilisateur | {auth_user_name} a "
            f"{action_verb} le {role} {user.full_name}.")

        capture_message(message, level="info")
