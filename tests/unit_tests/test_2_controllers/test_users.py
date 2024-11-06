from unittest.mock import patch

import pytest

from controllers.users import UserController
from controllers.authentication import AuthController
from tests.mocks.users_mock import MockUsersView


@pytest.fixture
def user_controller():
    return UserController()


@pytest.fixture
def auth_controller():
    return AuthController()


class TestGetUser:
    def test_get_all_users(self, user_controller):
        user_controller.view = MockUsersView()
        user_controller.get_all_users()
        assert len(user_controller.view.users) > 0


class TestModify:

    def test_modify(self, user_controller, user_instance):
        new_infos = {
            'first_name': 'New',
            'last_name': 'Name',
            'email': 'email.test@test.com',
        }
        user_controller.view = MockUsersView()
        user_controller.modify(
            user_id=1, **new_infos
        )
        assert 'success_modification' in user_controller.view.message

    def test_apply_changes(self, user_controller, user_instance):
        new_infos = {
            'first_name': 'Nouveau',
            'last_name': 'Nom',
            'email': 'nouvel.email@test.com',
            'password': '1354',
            'department_id': 1
        }
        changes = user_controller._apply_changes(
            user_instance, **new_infos)
        assert changes is True
        assert user_instance.first_name == new_infos['first_name']
        assert user_instance.last_name == new_infos['last_name']
        assert user_instance.email == new_infos['email']

    def test__get_choice_label(self, user_controller):
        choice = user_controller._get_choice_label('1')
        assert choice == 'Prénom'
        choice = user_controller._get_choice_label('2')
        assert choice == 'Nom'
        choice = user_controller._get_choice_label('3')
        assert choice == 'Email'
        choice = user_controller._get_choice_label('4')
        assert choice == 'Mot de passe'


class TestCreate:
    def test_create(self, user_controller):
        user_controller.view = MockUsersView()
        user_controller.create()
        assert 'success_creation' in user_controller.view.message


class TestDelete:
    def test_create(self, user_controller):
        user_controller.view = MockUsersView()
        user_controller.delete()
        assert 'success_delete' in user_controller.view.message
