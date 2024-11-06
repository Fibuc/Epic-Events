from unittest.mock import patch
from datetime import datetime

import pytest

from controllers.events import EventController
from controllers.authentication import AuthController
from tests.mocks.events_mock import MockEventsView
from controllers.session import add_and_commit_in_base
from models import models


@pytest.fixture
def event_controller():
    return EventController()


@pytest.fixture
def auth_controller():
    return AuthController()


class TestGetEvent:
    def test_get_all_events(self, event_controller: EventController):
        event_controller.view = MockEventsView()
        event_controller.get_events()
        assert len(event_controller.view.events) > 0

    def test__get_filters(self, event_controller: EventController):
        with patch(
            "controllers.authentication.AuthController.get_user_id"
        ) as mock_get_user_department:
            mock_get_user_department.return_value = '1'
        filters_past = {'date': 'past', 'my_events': True, 'no_support': None}
        filters_upcoming = {
            'date': 'upcoming',
            'my_events': None,
            'no_support': True
        }
        result = event_controller._get_filters(**filters_past)
        assert result
        assert filters_past['date'] != result['date']
        assert result['support_id'] == 1
        result = event_controller._get_filters(**filters_upcoming)
        assert result
        assert filters_upcoming['date'] != result['date']
        assert result['support_id'] is False


class TestModify:

    def test_modify_support_id(
            self, event_controller, event_instance, database_session
    ):
        event_controller.view = MockEventsView()
        with patch(
            'controllers.authentication.AuthController._get_user_info'
        ) as mock_get_user_info:
            mock_get_user_info.return_value = "Management"
            user = models.User.get_all(database_session)[0]
            department = models.Department.create(name='Support')
            add_and_commit_in_base(department)
            department = models.Department.get_all(database_session)[1]
            user.department_id = department.id
            database_session.add(user)
            database_session.commit()
            event_controller.modify(
                event_id=event_instance.id, support_id=1
            )

        assert 'success_modification' in event_controller.view.message

    def test_apply_changes(self, event_controller, event_instance):
        new_infos = {
            'event_start': '13/03/2024 14:45',
            'event_end': '13/03/2024 18:45',
            'location': '56 Rue de la Liberté',
            'attendees': 57,
            'notes': 'Pas de notes'
        }

        changes = event_controller._apply_changes(
            event_instance, **new_infos
        )
        assert changes is True
        assert event_instance.event_start == datetime.strptime(
            new_infos['event_start'], '%d/%m/%Y %H:%M'
        )
        assert event_instance.event_end == datetime.strptime(
            new_infos['event_end'], '%d/%m/%Y %H:%M'
        )
        assert event_instance.location == new_infos['location']
        assert event_instance.attendees == new_infos['attendees']
        assert event_instance.notes == new_infos['notes']


class TestCreate:
    @patch('models.models.Contract.get_filtered_contracts')
    def test_create(
        self, mock_get_filtered_contracts, event_controller, contract_instance
    ):
        event_controller.view = MockEventsView()
        with patch(
            'controllers.authentication.AuthController._get_user_info'
        ) as mock_get_user_info:
            mock_get_user_info.return_value = "Commercial"
            contract_instance.id = 1
            mock_get_filtered_contracts.return_value = [contract_instance]
            event_controller.create()
            event_controller.get_events()

        assert 'success_creation' in event_controller.view.message
