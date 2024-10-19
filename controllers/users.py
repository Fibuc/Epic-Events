from models import models

from controllers.permissions import is_authenticated, is_in_department
from controllers.session import add_and_commit_in_base, with_session

from views.users import UserView

class UserController:

    def __init__(self):
        self.model = models.User
        self.view = UserView

    @is_authenticated
    @is_in_department('Management')
    @with_session
    def get_all(self, session):
        self.all_users = self.model.get_all(session)
        self.all_departments = models.Department.get_department_dict(session)
        session.close()
        self.view.show_all_users(self.all_users, self.all_departments)
        self.select_user()

    def select_user(self):
        valid_choice = [str(i) for i in range(1, len(self.all_users) + 1)]
        choice = None
        while choice not in valid_choice:
            choice = self.view.select_user_for_option()
            if not choice:
                return
            elif choice not in valid_choice:
                self.view.invalid_user_choice(choice)
                continue

        self.user_selected = self.all_users[int(choice) - 1]
        choice = self.view.prompt_user_action()
        match choice:
            case '1':
                self.modify()
            case '2':
                self.delete()
            case '':
                return
            case _:
                self.view.invalid_user_choice(choice)

    @is_authenticated
    @is_in_department('Management')
    def modify(self):
        choice, number_of_choices = self.view.get_information_to_modify(self.user_selected, self.all_departments)
        possible_choices = [str(i) for i in list(range(1, number_of_choices + 1))]
        while choice not in possible_choices:
            if not choice:
                return
            elif choice not in possible_choices:
                self.view.invalid_user_choice(choice)
                choice = self.view.get_information_to_modify(self.user_selected, self.all_departments)[0]
                continue


        match choice:
            case '1':
                new_value = self.view.get_new_value('Prénom')
                if new_value:
                    self.user_selected.first_name = new_value
            case '2':
                new_value = self.view.get_new_value('Nom')
                if new_value:
                    self.user_selected.last_name = new_value
            case '3':
                new_value = self.view.get_new_value('Email')
                if new_value:
                    self.user_selected.email = new_value
            case '4':
                new_value = self.view.get_new_department(self.all_departments)
                if new_value:
                    self.user_selected.department = new_value
            case _:
                self.view.invalid_user_choice(choice)
                return
            
        if new_value:
            add_and_commit_in_base(self.user_selected)
            self.view.modification_success_message()

    @is_authenticated
    @is_in_department('Management')
    @with_session
    def delete(self, session=None):
        confirm_choice = self.view.confirm_delete(self.user_selected)
        if confirm_choice == 'oui' and session:
            session.delete(self.user_selected)
            session.commit()
            self.view.delete_success_message(self.user_selected)
        

    @is_authenticated
    @is_in_department('Management')
    def create(self, first_name, last_name, email, password, department):
        user = self.model.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            department=department
        )
        if user:
            add_and_commit_in_base(user)
            self.view.creation_success_message(user)
        
        else:
            self.view.creation_error_message()
