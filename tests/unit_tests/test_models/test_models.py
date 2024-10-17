from models import models


class TestUser:

    def test_create(self, user_informations, database_session):
        user = models.User.create(
            first_name=user_informations['first_name'],
            last_name=user_informations['last_name'],
            email=user_informations['email'],
            password=user_informations['password'],
            department=user_informations['department'],
        )
        database_session.add(user)
        database_session.commit()

        assert user is not None
        assert isinstance(user, models.User) is True
        assert user.first_name == user_informations['first_name']
        assert user.last_name == user_informations['last_name']
        assert user.email == user_informations['email']
        assert user.department == user_informations['department']

    def test_verify_correct_password(self, user_instance):
        assert user_instance.verify_password('123') is True

    def test_verify_wrong_password(self, user_instance):
        assert user_instance.verify_password('abc') is False

    def test_get_all(self, database_session):
        all_users = models.User.get_all(database_session)
        assert len(all_users) > 0

    def test_get_full_name(self, user_instance):
        full_name = f'{user_instance.first_name} {user_instance.last_name}'
        assert user_instance.full_name == full_name


class TestClient:

    def test_create(self, client_informations, database_session):
        client = models.Client.create(
            first_name=client_informations['first_name'],
            last_name=client_informations['last_name'],
            email=client_informations['email'],
            phone_number=client_informations['phone_number'],
            company_name=client_informations['company_name'],
            commercial_id=client_informations['commercial_id'],
        )
        database_session.add(client)
        database_session.commit()

        assert client is not None
        assert isinstance(client, models.Client) is True
        assert client.first_name == client_informations['first_name']
        assert client.last_name == client_informations['last_name']
        assert client.email == client_informations['email']
        assert client.phone_number == client_informations['phone_number']
        assert client.company_name == client_informations['company_name']
        assert client.commercial_id == client_informations['commercial_id']

    def test_get_all(self, database_session):
        all_clients = models.Client.get_all(database_session)
        assert len(all_clients) > 0

    def test_get_full_name(self, client_instance):
        full_name = f'{client_instance.first_name} {client_instance.last_name}'
        assert client_instance.full_name == full_name


class TestContract:

    def test_create(self, contract_informations, database_session):
        contract = models.Contract.create(
            client_id=contract_informations['client_id'],
            commercial_id=contract_informations['commercial_id'],
            total_amount=contract_informations['total_amount'],
            already_paid=contract_informations['already_paid'],
            status=contract_informations['status'],
        )
        database_session.add(contract)
        database_session.commit()

        assert contract is not None
        assert isinstance(contract, models.Contract) is True
        assert contract.client_id == contract_informations['client_id']
        assert contract.commercial_id == contract_informations['commercial_id']
        assert contract.total_amount == contract_informations['total_amount']
        assert contract.already_paid == contract_informations['already_paid']
        assert contract.status == contract_informations['status']

    def test_get_all(self, database_session):
        all_contracts = models.Contract.get_all(database_session)
        assert len(all_contracts) > 0

    def test_get_outstanding_balance(self, contract_instance):
        outstanding_balance = contract_instance.total_amount - contract_instance.already_paid
        assert outstanding_balance == contract_instance.outstanding_balance


class TestEvent:

    def test_create(self, event_informations, database_session):
        event = models.Event.create(
            contract_id=event_informations['contract_id'],
            client_id=event_informations['client_id'],
            event_start=event_informations['event_start'],
            event_end=event_informations['event_end'],
            support_id=event_informations['support_id'],
            location=event_informations['location'],
            attendees=event_informations['attendees'],
            notes=event_informations['notes']
        )
        database_session.add(event)
        database_session.commit()
        
        assert event is not None
        assert isinstance(event, models.Event) is True
        assert event.contract_id == event_informations['contract_id']
        assert event.client_id == event_informations['client_id']
        assert event.event_start == event_informations['event_start']
        assert event.event_end == event_informations['event_end']
        assert event.support_id == event_informations['support_id']
        assert event.location == event_informations['location']
        assert event.attendees == event_informations['attendees']
        assert event.notes == event_informations['notes']

    def test_get_all(self, database_session):
        all_events = models.Event.get_all(database_session)
        assert len(all_events) > 0
        
    def test_get_duration(self, event_instance):
        duration = event_instance.event_end - event_instance.event_start
        assert duration == event_instance.duration
