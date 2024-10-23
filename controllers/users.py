from email_validator import validate_email, EmailNotValidError
from models import models
from controllers.permissions import is_authenticated, is_in_department
from controllers.session import add_and_commit_in_base, with_session
from views.users import UserView

class UserController:

    @with_session
    def __init__(self, session):
        self.model = models.User
        self.view = UserView
        self.all_departments = models.Department.get_departments_dict(session)
        session.close()

    @is_authenticated
    @is_in_department(['Management'])
    @with_session
    def get_all_users(self, session, order_by='name'):
        all_users = self.model.get_all(session, order_by)
        self.view.show_all_users(all_users, self.all_departments)

    @is_authenticated
    @is_in_department(['Management'])
    @with_session
    def get_filtred_users(self, departments, order_by, session):
        all_users = self.model.get_filtred_users(session, departments, order_by)
        self.view.show_all_users(all_users, self.all_departments)

    @is_authenticated
    @is_in_department(['Management'])
    def get_users(self, commercial, management, support, order_by='name'):
        if commercial or management or support:
            departments = []
            if commercial:
                departments.append('Commercial')

            if management:
                departments.append('Management')

            if support:
                departments.append('Support')
            self.get_filtred_users(departments, order_by=order_by)
        else:
            self.get_all_users(order_by=order_by)
        

    @is_authenticated
    @is_in_department(['Management'])
    @with_session
    def select_user(self, session, option):
        """Récupère et retourne l'id de l'utilisateur sélectionné.

        Args:
            option (str): Option qui sera effectué sur l'utilisateur (Modification/Suppression).

        Returns:
            int | None: L'ID de l'utilisateur si bien sélectionné sinon None.
        """
        all_users = self.model.get_all(session)
        self.view.show_all_users(all_users, self.all_departments)
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
    def modify(
        self, user_id=None, first_name=None, last_name=None, email=None,
        password=None, department_name=None
    ):
        """Récupère les modifications de l'utilisateur désiré et effectue la sauvegarde la modification
        en base de données.

        Args:
            user_id (int, optional): ID de l'utilisateur. Défaut: None.
            first_name (str, optional): Prénom de l'utilisateur. Défaut: None.
            last_name (str, optional): Nom de l'utilisateur. Défaut: None.
            email (str, optional): Email de l'utilisateur. Défaut: None.
            password (str, optional): Mot de passe de l'utilisateur. Défaut: None.
            department_name (str, optional): Département de l'utilisateur. Défaut: None.
        """
        user_selected = self._get_user(user_id)
        if not user_selected:
            return

        changes = self._apply_changes(user_selected, first_name, last_name, email, password, department_name)

        if not changes:
            choice, nb_choices = self.view.get_information_to_modify(user_selected, self.all_departments)
            possible_choices = [str(i + 1) for i in range(nb_choices)]
            if not choice:
                return

            if choice not in possible_choices:
                self.view.invalid_choice(choice)
                return

            if choice == possible_choices[-1]:
                value = int(self.view.get_department(self.all_departments))
            else:
                label = self._get_choice_label(choice)
                value = self.view.get_new_value(label)

            changes = self._apply_changes(
                user_selected, 
                first_name=value if choice == '1' else None,
                last_name=value if choice == '2' else None,
                email=value if choice == '3' else None,
                password=value if choice == '4' else None,
                department_name=self.all_departments[value] if choice == '5' else None
            )

        if changes:
            add_and_commit_in_base(user_selected)
            self.view.modification_success_message()

    @with_session
    def _get_user(self, user_id: int, session) -> models.User | None:
        """Récupère et retourne l'utilisateur souhaité selon son ID.

        Args:
            user_id (int): ID de l'utilisateur désiré.

        Returns:
            models.User | None: Retourne l'instance de User si trouvé sinon None.
        """
        if user_id:
            return self.model.get_user(session, user_id)
        user_choice = self.select_user(option='modifier')
        if user_choice:
            return self.model.get_user(session, user_choice)
        return None

    def _apply_changes(
            self, user_selected: models.User, first_name=None, last_name=None,
            email=None, password=None, department_name=None) -> bool:
        """Applique les changements dans l'instance de l'utilisateur entré en paramètre
        et retourne un booleen indiquant si oui ou non il y a eu des changements.

        Args:
            user_selected (models.User): Instance de l'utilisateur à modifier.
            first_name (str, optional): Prénom de l'utilisateur. Défaut: None.
            last_name (str, optional): Nom de l'utilisateur. Défaut: None.
            email (str, optional): Email de l'utilisateur. Défaut: None.
            password (str, optional): Mot de passe de l'utilisateur. Défaut: None.
            department_name (str, optional): Département de l'utilisateur. Défaut: None.

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
        if department_name:
            department_id = next((key for key, value in self.all_departments.items() if value == department_name), None)
            if department_id and self.validate_user_department(department_id):
                user_selected.department = department_id
                changes = True
        return changes

    def _get_choice_label(self, choice):
        """Renvoie l'étiquette associée à chaque choix."""
        return {
            '1': 'Prénom',
            '2': 'Nom',
            '3': 'Email',
            '4': 'Mot de passe'
        }[choice]



    @is_authenticated
    @is_in_department(['Management'])
    @with_session
    def delete(self, user_id=None, session=None):
        """Supprime l'utilisateur indiqué en paramètre.

        Args:
            user_id (int, optional): ID de l'utilisateur à supprimer. Défaut: None.
        """
        if user_id:
            user_selected = self.model.get_user(session, user_id)
        else:
            user_choice = self.select_user(option='supprimer')
            if not user_choice:
                return

            user_selected = self.model.get_user(session, user_choice)
            
        confirm_choice = self.view.confirm_delete(user_selected)
        if confirm_choice == 'oui' and session:
            session.delete(user_selected)
            session.commit()
            return self.view.delete_success_message(user_selected)

        return
        

    @is_authenticated
    @is_in_department(['Management'])
    def create(self):
        """Crée un nouvel utilisateur et l'enregistre dans la base de données."""
        user_informations = self.view.get_new_user_informations()
        valid_email = self.validate_user_email(user_informations['email'])
        if not valid_email:
            return self.view.invalid_email(user_informations['email'])
        
        user_informations['department'] = self.view.get_department(self.all_departments)
        valid_department = self.validate_user_department(user_informations['department'])
        if not valid_department:
            return self.view.invalid_department()
        
        user = self.model.create(**user_informations)

        if user:
            add_and_commit_in_base(user)
            self.view.creation_success_message()

        else:
            self.view.creation_error_message()

    @staticmethod
    def validate_user_email(email) -> bool:
        try:
            valid = validate_email(email)
            email = valid.email
            return True

        except EmailNotValidError:
            return False

    def validate_user_department(self, department):
        try:
            int_department = int(department)

        except ValueError:
            return False
            
        if int_department in self.all_departments:
            return True
        
        return False