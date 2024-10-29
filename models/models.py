import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, Enum, DateTime, ForeignKey, case, asc
)
from sqlalchemy.orm import relationship
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from config import ph, BASE


class User(BASE):
    """Modèle des utilisateurs."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    department_id = Column(ForeignKey('departments.id'), nullable=False)

    department = relationship('Department', back_populates='users')
    clients = relationship('Client', back_populates='commercial')
    contracts = relationship('Contract', back_populates='commercial')
    events = relationship('Event', back_populates='support')

    @property
    def full_name(self) -> str:
        return f'{self.last_name} {self.first_name}'

    @classmethod
    def get_all(cls, session, order_by='name') -> list['User']:
        order = cls.get_order(order_by)
        return session.query(cls).join(User.department).order_by(order).all()

    @classmethod
    def get_filtred_users(
        cls, session, departments, order_by='name'
    ) -> list['User']:
        order = cls.get_order(order_by)
        return (
            session.query(cls).join(cls.department)
            .filter(Department.name.in_(departments))
            .order_by(order).all()
        )

    @classmethod
    def _get_user(cls, filter, information, session) -> 'User':
        return session.query(cls).filter(filter == information).first()

    @classmethod
    def get_user_by_id(cls, user_id, session):
        return cls._get_user(cls.id, user_id, session)

    @classmethod
    def get_user_by_email(cls, user_email, session):
        return cls._get_user(cls.email, user_email, session)

    @classmethod
    def get_order(cls, order_by):
        order = cls.last_name
        if order_by == 'id':
            order = cls.id
        elif order_by == 'department':
            order = Department.name

        return order

    @classmethod
    def create(
        cls, first_name, last_name, email, password, department_id
    ) -> 'User':
        return cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=cls.hash_password(password),
            department_id=department_id
            )

    @staticmethod
    def hash_password(password):
        return ph.hash(password)

    def verify_password(self, password) -> bool:
        try:
            ph.verify(self.password, password)
            return True

        except VerifyMismatchError:
            return False

        except InvalidHashError:
            return False


class Client(BASE):
    """Modèle Client"""
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    company_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(
        DateTime, default=datetime.now(), onupdate=datetime.now()
    )
    commercial_id = Column(
        Integer, ForeignKey('users.id', ondelete='SET NULL')
    )

    commercial = relationship('User', back_populates='clients')
    contracts = relationship('Contract', back_populates='client')
    events = relationship('Event', back_populates='client')

    @property
    def full_name(self) -> str:
        return f'{self.last_name} {self.first_name}'

    @classmethod
    def get_all(cls, session, order_by='name') -> list['Client']:
        order = cls.get_order(order_by)
        return (
            session.query(cls).outerjoin(cls.commercial).order_by(*order).all()
        )

    @classmethod
    def get_filtred_clients(cls, session, user_id, order_by) -> list['Client']:
        order = cls.get_order(order_by)
        return (
            session.query(cls).outerjoin(cls.commercial)
            .filter(cls.commercial_id == user_id).order_by(*order).all()
        )

    @classmethod
    def _get_client(cls, filter, information, session) -> 'Client':
        return session.query(cls).filter(filter == information).first()

    @classmethod
    def get_client_by_id(cls, user_id, session) -> 'Client':
        return cls._get_client(cls.id, user_id, session)

    @classmethod
    def get_order(cls, order_by):
        order = [cls.last_name]
        if order_by == 'id':
            order = [cls.id]
        elif order_by == 'company':
            order = [cls.company_name]
        elif order_by == 'commercial':
            order = case(
                (cls.commercial is None, 1), else_=0
            )
            order = [asc(order), cls.commercial]

        return order

    @classmethod
    def create(
        cls, first_name, last_name, email, phone_number,
        company_name, commercial_id
    ) -> 'Client':
        return cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            company_name=company_name,
            commercial_id=commercial_id
        )


class Contract(BASE):
    """Modèle de Contrat"""
    __tablename__ = 'contracts'

    class ContractStatus(enum.Enum):
        """Status des contrats"""
        signed = 'Signé'
        unsigned = 'Non signé'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    commercial_id = Column(
        Integer, ForeignKey('users.id', ondelete='SET NULL')
    )
    total_amount = Column(Integer, nullable=False)
    already_paid = Column(Integer, default=0)
    status = Column(
        Enum(ContractStatus), nullable=False, default=ContractStatus.unsigned
    )
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(
        DateTime, default=datetime.now(), onupdate=datetime.now()
    )

    client = relationship('Client', back_populates='contracts')
    commercial = relationship('User', back_populates='contracts')
    event = relationship('Event', back_populates='contract')

    @classmethod
    def create(
        cls, client_id, commercial_id, total_amount, already_paid, status=None
    ) -> 'Contract':
        return cls(
            client_id=client_id,
            commercial_id=commercial_id,
            total_amount=cls.multiply_by_100(total_amount),
            already_paid=cls.multiply_by_100(already_paid),
            status=status
        )

    @staticmethod
    def multiply_by_100(number) -> int:
        return number * 100

    @property
    def outstanding_balance(self) -> float:
        return float((self.total_amount - self.already_paid) / 100)

    @property
    def total_amount_100(self) -> float:
        return float(self.total_amount / 100)

    @property
    def already_paid_100(self) -> float:
        return float(self.already_paid / 100)

    @classmethod
    def get_all(cls, session, order_by='id') -> list['Contract']:
        order = cls._get_contracts_order(order_by)
        return (
            session.query(cls).outerjoin(cls.commercial)
            .outerjoin(cls.client).order_by(*order).all()
        )

    @classmethod
    def get_filtered_contracts(
        cls, session, status=None, payment=None,
        user_id: Optional[int] = None, order_by='id'
    ) -> list['Contract']:
        """Applique les filtres sur le session.query selon les
        informations entrées en paramètre."""
        query = (
            session.query(cls).outerjoin(cls.commercial).outerjoin(cls.client)
        )

        if status:
            query = query.filter(cls.status == status)

        if payment is not None:
            if payment:
                query = query.filter(cls.already_paid == cls.total_amount)
            else:
                query = query.filter(cls.already_paid != cls.total_amount)

        if user_id:
            query = query.filter(cls.commercial_id == user_id)

        order = cls._get_contracts_order(order_by)
        return query.order_by(*order).all()

    @classmethod
    def get_contract_by_id(cls, contract_id, session) -> 'Contract':
        return session.query(cls).filter(cls.id == contract_id).first()

    @classmethod
    def _get_contracts_order(cls, order_by):
        order = [cls.id]
        if order_by == 'client':
            order = [Client.last_name]
        elif order_by == 'payment':
            order = [cls.total_amount - cls.already_paid]
        elif order_by == 'status':
            order = [cls.status]
        elif order_by == 'commercial':
            order = case(
                (cls.commercial is None, 1),
                else_=0
            )
            order = [asc(order), User.last_name]
        return order


class Event(BASE):
    """Modèle événement."""
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    event_start = Column(DateTime, nullable=False)
    event_end = Column(DateTime)
    support_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    location = Column(String(255), nullable=False)
    attendees = Column(Integer)
    notes = Column(String(4096))

    contract = relationship('Contract', back_populates='event')
    client = relationship('Client', back_populates='events')
    support = relationship('User', back_populates='events')

    @classmethod
    def get_all(cls, session, order_by='id') -> list['Event']:
        order = cls._get_events_order(order_by)
        return (
            session.query(cls).outerjoin(cls.contract)
            .outerjoin(cls.client).outerjoin(cls.support)
            .order_by(*order).all()
        )

    @classmethod
    def create(
        cls, contract_id, client_id, event_start, event_end,
        location, attendees, notes
    ) -> 'Event':
        return cls(
            contract_id=contract_id,
            client_id=client_id,
            event_start=event_start,
            event_end=event_end,
            location=location,
            attendees=attendees,
            notes=notes
        )

    @classmethod
    def get_filtered_events(
        cls, session, date=None, support_id=None, order_by='id'
    ) -> list['Event']:
        """Applique les filtres sur le session.query selon les
        informations entrées en paramètre."""
        query = (
            session.query(cls).outerjoin(cls.contract)
            .outerjoin(cls.client).outerjoin(cls.support)
        )

        if date is not None:
            if date:
                query = query.filter(cls.event_end < datetime.now())
            else:
                query = query.filter(cls.event_start > datetime.now())

        if support_id is not None:
            if support_id:
                query = query.filter(cls.support_id == support_id)
            else:
                query = query.filter(cls.support_id is None)

        order = cls._get_events_order(order_by)
        return query.order_by(*order).all()

    @classmethod
    def get_event_by_id(cls, event_id, session) -> 'Event':
        return session.query(cls).filter(cls.id == event_id).first()

    @classmethod
    def _get_events_order(cls, order_by):
        order = [cls.id]
        if order_by == 'contract':
            order = [Contract.id]
        elif order_by == 'client':
            order = [Client.last_name]
        elif order_by == 'support':
            order = case(
                (cls.support is None, 1),
                else_=0
            )
            order = [asc(order), User.last_name]
        elif order_by == 'attendees':
            order = [cls.attendees]
        elif order_by == 'start':
            order = [cls.event_start]
        elif order_by == 'end':
            order = [cls.event_end]
        return order


class Department(BASE):
    """Modèle Département."""
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    users = relationship('User', back_populates='department')

    @classmethod
    def create(cls, name) -> 'Department':
        return cls(name=name)

    @classmethod
    def get_all(cls, session) -> list['Department']:
        return session.query(cls).all()
