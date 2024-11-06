from unittest.mock import patch

import pytest

from controllers.authentication import AuthController
from tests.mocks.auth_mock import MockAuthenticationView


@pytest.fixture
def auth_controller():
    """Fixture pour créer une instance d'AuthController."""
    return AuthController()


class TestLogin:
    def test_success_login(
        self, auth_controller, user_informations, mock_get_session
    ):
        auth_controller.view = MockAuthenticationView(user_informations)
        auth_controller.login(email=auth_controller.view.get_email())
        assert "login_success" in auth_controller.view.messages[0]
        assert auth_controller.view.messages[0] == (
            f"login_success_{user_informations['first_name']}"
        )

    def test_error_login(
        self, auth_controller, user_informations, mock_get_session
    ):
        auth_controller.view = MockAuthenticationView(user_informations)
        auth_controller.view.password = 'Bad_password'
        auth_controller.login(email=auth_controller.view.get_email())
        assert 'login_failed' in auth_controller.view.messages


class TestGetUserInfo:

    @patch("controllers.authentication.AuthController._get_user_info")
    def test_get_user_id(self, mock_get_user_info, auth_controller):
        mock_get_user_info.return_value = 2
        user_id = auth_controller.get_user_id()
        assert user_id == 2

    @patch("controllers.authentication.AuthController._get_user_info")
    def test_get_user_department(self, mock_get_user_info, auth_controller):
        mock_get_user_info.return_value = "Management"
        user_department = auth_controller.get_user_department()
        assert user_department == 'Management'

    @patch("controllers.authentication.AuthController._get_user_info")
    def test_get_user_name(self, mock_get_user_info, auth_controller):
        mock_get_user_info.return_value = "Nom"
        user_name = auth_controller.get_user_name()
        assert user_name == 'Nom'
