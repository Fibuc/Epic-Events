from unittest.mock import patch

import pytest

from controllers.contracts import ContractController
from controllers.authentication import AuthController
from tests.mocks.contracts_mock import MockContractsView


@pytest.fixture
def contract_controller():
    return ContractController()


@pytest.fixture
def auth_controller():
    return AuthController()


class TestGetContract:
    def test_get_all_contracts(self, contract_controller):
        contract_controller.view = MockContractsView()
        contract_controller.get_contracts()
        assert len(contract_controller.view.contracts) > 0

    def test__get_filters(self, contract_controller):
        filters_signed_sold = {
            'status': 'signed',
            'payment': 'sold',
            'my_contracts': True
        }
        filters_unsigned_unsold = {
            'status': 'unsigned',
            'payment': 'unsold',
            'my_contracts': False
        }
        result = contract_controller._get_filters(**filters_signed_sold)
        assert result
        assert filters_signed_sold['status'] != result['status']
        assert filters_signed_sold['payment'] != result['payment']

        result = contract_controller._get_filters(**filters_unsigned_unsold)
        assert result
        assert filters_signed_sold['status'] != result['status']
        assert filters_signed_sold['payment'] != result['payment']


class TestModify:

    def test_modify(self, contract_controller, contract_instance):
        new_infos = {
            'client_id': 1,
            'commercial_id': 1,
            'total_amount': '146',
            'already_paid': '146',
            'status': 'signed'
        }
        contract_controller.view = MockContractsView()
        contract_controller.modify(
            contract_id=contract_instance.id, **new_infos
        )
        contract_controller.get_contracts()
        contract = contract_controller.view.contracts[0]
        assert 'success_modification' in contract_controller.view.message
        assert contract.client_id == new_infos['client_id']
        assert contract.commercial_id == new_infos['commercial_id']
        assert contract.total_amount_100 == float(new_infos['total_amount'])
        assert contract.already_paid_100 == float(new_infos['already_paid'])
        assert contract.status != new_infos['status']

    def test_apply_changes(self, contract_controller, contract_instance):
        new_infos = {
            'client_id': 1,
            'total_amount': '134.44',
            'already_paid': '134.44',
            'status': contract_controller.model.ContractStatus.signed,
        }

        changes = contract_controller._apply_changes(
            contract_instance, **new_infos)
        assert changes is True
        assert contract_instance.client_id == new_infos['client_id']
        assert contract_instance.total_amount_100 == float(
            new_infos['total_amount']
        )
        assert contract_instance.already_paid_100 == float(
            new_infos['already_paid']
        )
        assert contract_instance.status == new_infos['status']


class TestCreate:
    def test_create(self, contract_controller, user_instance):
        contract_controller.view = MockContractsView()
        with patch(
            'models.models.User.get_filtred_users'
        ) as mock_filtred_users:
            user_instance.id = 1
            mock_filtred_users.return_value = [user_instance]
            contract_controller.create()
            contract_controller.get_contracts()
            assert 'success_creation' in contract_controller.view.message
