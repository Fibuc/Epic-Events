import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, case, asc
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
    department_id = Column(ForeignKey('departments.id') , nullable=False)

    department = relationship('Department', back_populates='users')
    clients = relationship('Client', back_populates='commercial')
    contracts = relationship('Contract', back_populates='commercial')
    events = relationship('Event', back_populates='support')

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name}'
    
    @classmethod
    def get_all(cls, session, order_by='name'):
        order = cls.get_order(order_by)
        return session.query(cls).join(User.department).order_by(order).all()
    
    @classmethod
    def get_filtred_users(cls, session, departments, order_by='name'):
        order = cls.get_order(order_by)
        return (
            session.query(cls).join(cls.department)
            .filter(Department.name.in_(departments))
            .order_by(order).all()
        )      

    @classmethod
    def get_user(cls, filter, information, session):
        return session.query(cls).filter(filter == information).first()

    @classmethod
    def get_user_by_id(cls, user_id, session):
        return cls.get_user(cls.id, user_id, session)

    @classmethod
    def get_user_by_email(cls, user_email, session):
        return cls.get_user(cls.email, user_email, session)

    @classmethod
    def get_order(cls, order_by):
        order = cls.last_name
        if order_by == 'id':
            order = cls.id
        elif order_by == 'department':
            order = Department.name
        
        return order
    
    @classmethod
    def create(cls, first_name, last_name, email, password, department_id):
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

    @classmethod
    def get_users_dict(cls, session):
        users_dict = {}
        users = cls.get_all(session)
        for user in users:
            users_dict[user.id] = user.full_name
        
        return users_dict
    
    def verify_password(self, password):
        try:
            ph.verify(self.password, password)
            return True

        except VerifyMismatchError:
            return False

        except InvalidHashError:
            return False


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

    commercial = relationship('User', back_populates='clients')
    contracts = relationship('Contract', back_populates='client')
    events = relationship('Event', back_populates='client')

    @property
    def full_name(self):
        return f'{self.last_name} {self.first_name}'

    @classmethod
    def get_all(cls, session, order_by='name'):
        order = cls.get_order(order_by)
        return session.query(cls).outerjoin(cls.commercial).order_by(*order).all()
    
    @classmethod
    def get_filtred_clients(cls, session, user_id, order_by):
        order = cls.get_order(order_by)
        return session.query(cls).outerjoin(cls.commercial).filter(cls.commercial_id == user_id).order_by(*order).all()

    @classmethod
    def get_client(cls, filter, information, session):
        return session.query(cls).filter(filter == information).first()

    @classmethod
    def get_client_by_id(cls, user_id, session):
        return cls.get_client(cls.id, user_id, session)

    @classmethod
    def get_order(cls, order_by):
        order = [cls.last_name]
        if order_by == 'id':
            order = [cls.id]
        elif order_by == 'company':
            order = [cls.company_name]
        elif order_by == 'commercial':
            order = case(
            (cls.commercial == None, 1), else_=0
            )
            order = [asc(order), cls.commercial]

        return order

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
    commercial = relationship('User', back_populates='contracts')
    event = relationship('Event', back_populates='contract')

    @classmethod
    def create(cls, client_id, commercial_id, total_amount, already_paid, status=None):
        return cls(
            client_id=client_id,
            commercial_id=commercial_id,
            total_amount=cls.multiply_by_100(total_amount),
            already_paid=cls.multiply_by_100(already_paid),
            status=status
        )

    @staticmethod
    def multiply_by_100(number):
        return number * 100

    @property
    def outstanding_balance(self):
        return float((self.total_amount - self.already_paid) / 100)
    
    @property
    def sold(self):
        return self.total_amount == self.already_paid

    @property
    def total_amount_100(self):
        return float(self.total_amount / 100)
    
    @property
    def already_paid_100(self):
        return float(self.already_paid / 100)

    @classmethod
    def get_all(cls, session, order_by='id'):
        order = cls._get_contracts_order(order_by)
        return session.query(cls).outerjoin(cls.commercial).outerjoin(cls.client).order_by(*order).all()

    @classmethod
    def get_filtered_contracts(cls, session, status=None, payment=None, user_id=False, order_by='id'):
        query = session.query(cls).outerjoin(cls.commercial).outerjoin(cls.client)
        
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
    def get_contract_by_id(cls, contract_id, session):
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
                (cls.commercial == None, 1),
                else_=0
            )
            order = [asc(order), User.last_name]
        return order


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
    support = relationship('User', back_populates='events')

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

    users = relationship('User', back_populates='department')

    @classmethod
    def create(cls, name):
        return cls(name=name)

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

