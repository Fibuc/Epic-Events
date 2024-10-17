from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import ProgrammingError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import models
from config import BASE


database_for_test = 'epic_events_test_session'


@pytest.fixture(scope='session')
def database_session():
    engine = create_engine('sqlite:///:memory:', echo=False)
    BASE.metadata.create_all(engine)
    Session = sessionmaker(engine)
    session = Session()

    yield session

    session.close()


@pytest.fixture
def user_informations():
    return {
        'first_name': 'Jean',
        'last_name': 'Dupond',
        'email': 'email_user@test.com',
        'password': '123',
        'department': 1
    }


@pytest.fixture
def user_instance(user_informations):
    return models.User.create(
            first_name=user_informations['first_name'],
            last_name=user_informations['last_name'],
            email=user_informations['email'],
            password=user_informations['password'],
            department=user_informations['department'],
        )


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
def client_instance(client_informations):
    return models.Client.create(
            first_name=client_informations['first_name'],
            last_name=client_informations['last_name'],
            email=client_informations['email'],
            phone_number=client_informations['phone_number'],
            company_name=client_informations['company_name'],
            commercial_id=client_informations['commercial_id'],
        )


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
def contract_instance(contract_informations):
    return models.Contract.create(
            client_id=contract_informations['client_id'],
            commercial_id=contract_informations['commercial_id'],
            total_amount=contract_informations['total_amount'],
            already_paid=contract_informations['already_paid'],
            status=contract_informations['status'],
        )


@pytest.fixture
def event_informations():
    return {
        'contract_id': 1,
        'client_id': 1,
        'event_start': datetime.today(),
        'event_end': datetime.today() + timedelta(days=1),
        'support_id': 2,
        'location': 'Angers',
        'attendees': 34,
        'notes': 'Notes pour le test',
    }


@pytest.fixture
def event_instance(event_informations):
    return models.Event.create(
            contract_id=event_informations['contract_id'],
            client_id=event_informations['client_id'],
            event_start=event_informations['event_start'],
            event_end=event_informations['event_end'],
            support_id=event_informations['support_id'],
            location=event_informations['location'],
            attendees=event_informations['attendees'],
            notes=event_informations['notes']
        )
