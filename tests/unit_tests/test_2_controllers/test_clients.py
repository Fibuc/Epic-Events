from unittest.mock import patch

import pytest

from controllers.clients import ClientController
from controllers.authentication import AuthController
from tests.mocks.clients_mock import MockClientsView


@pytest.fixture
def client_controller():
    return ClientController()


@pytest.fixture
def auth_controller():
    return AuthController()


class TestGetClient:
    def test_get_all_clients(self, client_controller):
        client_controller.view = MockClientsView()
        client_controller.get_all_clients()
        assert len(client_controller.view.clients) > 0


class TestModify:

    def test_modify(self, client_controller, client_instance):
        new_infos = {
            'first_name': 'New',
            'last_name': 'Name',
            'email': 'email.test@test.com',
            'phone_number': '02.02.02.02.02',
            'company_name': 'New Company',
            'commercial_id': 1
        }
        client_controller.view = MockClientsView()
        with patch(
            "controllers.authentication.AuthController.get_user_department"
        ) as mock_get_user_department:
            mock_get_user_department.return_value = 'Commercial'
            client_controller.modify(
                client_id=client_instance.id, **new_infos
            )
        client_controller.get_all_clients()
        client = client_controller.view.clients[0]
        assert 'success_modification' in client_controller.view.messages
        assert client.first_name == new_infos['first_name']
        assert client.last_name == new_infos['last_name']
        assert client.email == new_infos['email']
        assert client.phone_number == new_infos['phone_number']
        assert client.company_name == new_infos['company_name']
        assert client.commercial_id == new_infos['commercial_id']

    def test_apply_changes(self, client_controller, client_instance):
        new_infos = {
            'first_name': 'Nouveau',
            'last_name': 'Nom',
            'email': 'nouvel.email@test.com',
            'phone_number': '04.04.04.04.04',
            'company_name': 'Nouvelle Entreprise',
            'commercial_id': 1
        }
        changes = client_controller._apply_changes(
            client_instance, **new_infos)
        assert changes is True
        assert client_instance.first_name == new_infos['first_name']
        assert client_instance.last_name == new_infos['last_name']
        assert client_instance.email == new_infos['email']
        assert client_instance.phone_number == new_infos['phone_number']
        assert client_instance.company_name == new_infos['company_name']
        assert client_instance.commercial_id == new_infos['commercial_id']

    def test__get_choice_label(self, client_controller):
        choice = client_controller._get_choice_label('1')
        assert choice == 'Prénom'
        choice = client_controller._get_choice_label('2')
        assert choice == 'Nom'
        choice = client_controller._get_choice_label('3')
        assert choice == 'Email'
        choice = client_controller._get_choice_label('4')
        assert choice == 'Téléphone'
        choice = client_controller._get_choice_label('5')
        assert choice == "Nom d'entreprise"


class TestCreate:
    def test_create(self, client_controller):
        client_controller.view = MockClientsView()
        with patch(
            "controllers.authentication.AuthController.get_user_department"
        ) as mock_get_user_department:
            mock_get_user_department.return_value = 'Commercial'
            client_controller.create()
            client_controller.get_all_clients()
            print(client_controller.view.clients)
        assert 'success_creation' in client_controller.view.messages
