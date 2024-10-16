import enum

from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from argon2.exceptions import VerifyMismatchError, InvalidHashError

from config import ph, BASE


class User(BASE):
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

    @classmethod
    def create(cls, first_name, last_name, email, password):
        return super().create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            department='Commercial'
        )

class Supporter(User):
    
    events = relationship('Event', back_populates='support')

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def create(cls, first_name, last_name, email, password):
        return super().create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            department='Support'
        )
    

class Manager(User):

    @classmethod
    def get_all(cls, session):
        return session.query(cls).all()

    @classmethod
    def create(cls, first_name, last_name, email, password):
        return super().create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            department='Management'
        )
