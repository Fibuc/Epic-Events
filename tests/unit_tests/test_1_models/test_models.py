from models import models


class TestDepartment:

    def test_create(self, department_informations, database_session):
        department = models.Department.create(**department_informations)
        database_session.add(department)
        database_session.commit()

        assert department is not None
        assert isinstance(department, models.Department)
        assert department.name == department_informations['name']

    def test_get_all(self, database_session):
        all_department = models.Department.get_all(database_session)
        assert len(all_department) > 0


class TestUser:

    def test_create(self, user_informations, database_session):
        user = models.User.create(**user_informations)
        database_session.add(user)
        database_session.commit()

        assert user is not None
        assert isinstance(user, models.User)
        assert user.first_name == user_informations['first_name']
        assert user.last_name == user_informations['last_name']
        assert user.email == user_informations['email']
        assert user.department_id == user_informations['department_id']

    def test_get_all(self, database_session):
        all_users = models.User.get_all(database_session)
        assert len(all_users) > 0

    def test_verify_correct_password(self, user_instance):
        assert user_instance.verify_password('123') is True

    def test_verify_wrong_password(self, user_instance):
        assert user_instance.verify_password('abc') is False

    def test_get_full_name(self, user_instance):
        full_name = f'{user_instance.last_name} {user_instance.first_name}'
        assert user_instance.full_name == full_name

    def test_get_filtred_users(self, database_session):
        filtred_users = models.User.get_filtred_users(
            database_session, ['Management']
        )
        assert len(filtred_users) > 0

    def test_get_user_by_email(
        self, database_session, user_instance, user_informations
    ):
        user = models.User.get_user_by_email(
            user_instance.email, database_session
        )
        assert isinstance(user, models.User)
        assert user_informations['email'] == user.email

    def test_get_user_by_id(self, database_session, user_instance):
        id_research = 1
        user = models.User.get_user_by_id(id_research, database_session)
        assert isinstance(user, models.User)
        assert user.id == id_research


class TestClient:

    def test_create(self, client_informations, database_session):
        client = models.Client.create(**client_informations)
        database_session.add(client)
        database_session.commit()

        assert client is not None
        assert isinstance(client, models.Client)
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
        full_name = f'{client_instance.last_name} {client_instance.first_name}'
        assert client_instance.full_name == full_name

    def test_get_filtred_client(self, database_session):
        filtred_clients = models.Client.get_filtred_clients(
            database_session, 1
        )
        assert len(filtred_clients) > 0

    def test_get_client_by_id(self, database_session):
        id_research = 1
        client = models.Client.get_client_by_id(id_research, database_session)
        assert isinstance(client, models.Client)
        assert client.id == id_research


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
        assert isinstance(contract, models.Contract)
        assert contract.client_id == contract_informations['client_id']
        assert contract.commercial_id == contract_informations['commercial_id']
        assert contract.total_amount == (
            contract_informations['total_amount'] * 100
        )
        assert contract.already_paid == (
            contract_informations['already_paid'] * 100
        )
        assert contract.status == contract_informations['status']

    def test_get_all(self, database_session):
        all_contracts = models.Contract.get_all(database_session)
        assert len(all_contracts) > 0

    def test_get_outstanding_balance(self, contract_instance):
        outstanding_balance = (
            contract_instance.total_amount - contract_instance.already_paid
        )
        assert contract_instance.outstanding_balance == (
            outstanding_balance / 100
        )

    def test_get_signed_contracts(self, database_session):
        filtred_contracts = models.Contract.get_filtered_contracts(
            database_session, status=models.Contract.ContractStatus.signed
        )
        assert len(filtred_contracts) > 0

    def test_get_unsigned_contracts(self, database_session):
        filtred_contracts = models.Contract.get_filtered_contracts(
            database_session, status=models.Contract.ContractStatus.unsigned
        )
        assert len(filtred_contracts) == 0

    def test_get_filtred_by_user_id(self, database_session):
        filtred_contracts = models.Contract.get_filtered_contracts(
            database_session, user_id=1
        )
        assert len(filtred_contracts) > 0

    def test_total_amount_100(self, contract_instance, contract_informations):
        assert contract_instance.total_amount == (
            contract_informations['total_amount'] * 100
        )
        assert contract_instance.total_amount_100 == (
            contract_informations['total_amount']
        )

    def test_already_paid_100(self, contract_instance, contract_informations):
        assert contract_instance.already_paid == (
            contract_informations['already_paid'] * 100
        )
        assert contract_instance.already_paid_100 == (
            contract_informations['already_paid']
        )


class TestEvent:

    def test_create(self, event_informations, database_session):
        event = models.Event.create(
            contract_id=event_informations['contract_id'],
            client_id=event_informations['client_id'],
            event_start=event_informations['event_start'],
            event_end=event_informations['event_end'],
            location=event_informations['location'],
            attendees=event_informations['attendees'],
            notes=event_informations['notes']
        )
        database_session.add(event)
        database_session.commit()

        assert event is not None
        assert isinstance(event, models.Event)
        assert event.contract_id == event_informations['contract_id']
        assert event.client_id == event_informations['client_id']
        assert event.event_start.replace(microsecond=0, second=0) == (
            event_informations['event_start'].replace(microsecond=0, second=0)
        )
        assert event.event_end.replace(microsecond=0, second=0) == (
            event_informations['event_end'].replace(microsecond=0, second=0)
        )
        assert event.location == event_informations['location']
        assert event.attendees == event_informations['attendees']
        assert event.notes == event_informations['notes']

    def test_get_all(self, database_session):
        all_events = models.Event.get_all(database_session)
        assert len(all_events) > 0
