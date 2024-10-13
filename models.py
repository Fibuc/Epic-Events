import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    class DepartementUser(enum.Enum):
        commercial = 'Commercial'
        management = 'Management'
        support = 'Support'

    id = Column(Integer, primary_key=True, autoincrement=True)
    last_name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    department = Column(Enum(DepartementUser) , nullable=False)

    @property
    def full_name(self):
        return f'{self.first_name} {self. last_name}'


class Commercial(User):
    
    clients = relationship('Client', back_populates='commercial')
    contracts = relationship('Contract', back_populates='commercial')


class Supporter(User):
    
    events = relationship('Event', back_populates='support')


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(255), unique=True)
    phone_number = Column(String(20))
    company_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    commercial_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    commercial = relationship('Commercial', back_populates='clients')
    contracts = relationship('Contract', back_populates='client')
    events = relationship('Event', back_populates='client')

    @property
    def full_name(self):
        return f'{self.first_name} {self. last_name}'


class Contract(Base):
    __tablename__ = 'contracts'

    class ContractStatus(enum.Enum):
        signed = 'Signé'
        unsigned = 'Non signé'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    commercial_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_amount = Column(Integer, nullable=False)
    status = Column(Enum(ContractStatus), nullable=False, default=ContractStatus.unsigned)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    client = relationship('Client', back_populates='contracts')
    commercial = relationship('Commercial', back_populates='contracts')
    event = relationship('Event', back_populates='contract')


class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    event_start = Column(DateTime, nullable=False)
    event_end = Column(DateTime, nullable=False)
    support_id = Column(Integer, ForeignKey('users.id'))
    location = Column(String(255), nullable=False)
    attendees = Column(Integer)
    notes = Column(String(4096))

    contract = relationship('Contract', back_populates='event')
    client = relationship('Client', back_populates='events')
    support = relationship('Supporter', back_populates='events')
