import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from config import ph, BASE


class User(BASE):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    department = Column(ForeignKey('departments.id') , nullable=False)

    @property
    def full_name(self):
        return f'{self.first_name} {self. last_name}'
    
    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()
    
    @classmethod
    def create(cls, first_name, last_name, email, password, department):
        hashed_password = ph.hash(password)
        return cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=hashed_password,
            department=department
            )
    
    def verify_password(self, password):
        try:
            ph.verify(self.password, password)
            return True

        except VerifyMismatchError:
            return False

        except InvalidHashError:
            return False


class Commercial(User):
    
    clients = relationship('Client', back_populates='commercial')
    contracts = relationship('Contract', back_populates='commercial')

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()


class Supporter(User):
    
    events = relationship('Event', back_populates='support')

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()


class Manager(User):

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()


class Client(BASE):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20), nullable=False)
    company_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    commercial_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))

    commercial = relationship('Commercial', back_populates='clients')
    contracts = relationship('Contract', back_populates='client')
    events = relationship('Event', back_populates='client')

    @property
    def full_name(self):
        return f'{self.first_name} {self. last_name}'

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def create(cls, first_name, last_name, email, phone_number, company_name, commercial_id):
        return cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            company_name=company_name,
            commercial_id=commercial_id
        )


class Contract(BASE):
    __tablename__ = 'contracts'

    class ContractStatus(enum.Enum):
        signed = 'Signé'
        unsigned = 'Non signé'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    commercial_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    total_amount = Column(Integer, nullable=False)
    already_paid = Column(Integer, default=0)
    status = Column(Enum(ContractStatus), nullable=False, default=ContractStatus.unsigned)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    client = relationship('Client', back_populates='contracts')
    commercial = relationship('Commercial', back_populates='contracts')
    event = relationship('Event', back_populates='contract')

    @property
    def outstanding_balance(self):
        return self.total_amount - self.already_paid
    
    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def create(cls, client_id, commercial_id, total_amount, already_paid, status=None):
        return cls(
            client_id=client_id,
            commercial_id=commercial_id,
            total_amount=total_amount,
            already_paid=already_paid,
            status=status
        )


class Event(BASE):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    event_start = Column(DateTime, nullable=False)
    event_end = Column(DateTime, nullable=False)
    support_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    location = Column(String(255), nullable=False)
    attendees = Column(Integer)
    notes = Column(String(4096))

    contract = relationship('Contract', back_populates='event')
    client = relationship('Client', back_populates='events')
    support = relationship('Supporter', back_populates='events')

    @property
    def duration(self):
        return self.event_end - self.event_start

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def create(
        cls, contract_id, client_id, event_start, event_end,
        support_id, location, attendees, notes
    ):
        return cls(
            contract_id=contract_id,
            client_id=client_id,
            event_start=event_start,
            event_end=event_end,
            support_id=support_id,
            location=location,
            attendees=attendees,
            notes=notes
        )


class Department(BASE):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)


    @classmethod
    def create(cls, name):
        return cls(name=name)

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()
    
    @classmethod
    def get_department_dict(cls, session):
        departments_dict = {}
        departments = cls.get_all(session)
        for department in departments:
            departments_dict[department.id] = department.name
        
        return departments_dict