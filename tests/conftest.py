from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from controllers.database import DatabaseController
from models import models
from config import BASE, URL_MYSQL

DATABASE_TEST_NAME = 'epic_events_test_session'
URL_DATABASE_TEST = URL_MYSQL + DATABASE_TEST_NAME
CREATION = False


@pytest.fixture(scope='session')
def database_session():
    controller = DatabaseController()
    engine = create_engine(URL_DATABASE_TEST)
    Session = sessionmaker(engine)
    session = Session()
    controller.init_database(database=DATABASE_TEST_NAME)

    yield session

    session.close()
    with engine.connect() as connection:
        connection.execute(text(f'DROP DATABASE {DATABASE_TEST_NAME}'))


@pytest.fixture(scope='session', autouse=True)
def mock_get_session(database_session):
    with patch(
        'controllers.session.get_session', return_value=database_session
    ) as mock:
        yield mock


@pytest.fixture(scope='session', autouse=True)
def mock_with_session(database_session):
    with patch(
        'controllers.session.with_session', return_value=database_session
    ) as mock:
        yield mock


@pytest.fixture
def user_informations():
    return {
        'first_name': 'Jean',
        'last_name': 'Dupond',
        'email': 'email_user@test.com',
        'password': '123',
        'department_id': 1
    }


@pytest.fixture
def user_instance(user_informations) -> models.User:
    return models.User.create(**user_informations)


@pytest.fixture
def client_informations():
    return {
        'first_name': 'Gilbert',
        'last_name': 'Le Doux',
        'email': 'email_client@test.com',
        'phone_number': '+336574627',
        'company_name': 'Le Doux SARL',
        'commercial_id': 1,
    }


@pytest.fixture
def client_instance(client_informations) -> models.Client:
    return models.Client.create(**client_informations)


@pytest.fixture
def contract_informations():
    return {
        'client_id': 1,
        'commercial_id': 1,
        'total_amount': 44,
        'already_paid': 30,
        'status': models.Contract.ContractStatus.signed,
    }


@pytest.fixture
def contract_instance(contract_informations) -> models.Contract:
    return models.Contract.create(**contract_informations)


@pytest.fixture
def event_informations():
    return {
        'contract_id': 1,
        'client_id': 1,
        'event_start': datetime.today(),
        'event_end': datetime.today() + timedelta(days=1),
        'location': 'Angers',
        'attendees': 34,
        'notes': 'Notes pour le test',
    }


@pytest.fixture
def event_instance(event_informations) -> models.Event:
    return models.Event.create(**event_informations)


@pytest.fixture
def department_informations():
    return {'name': 'Management'}


@pytest.fixture
def department_instance(department_informations) -> models.Department:
    return models.Department.create(**department_informations)
