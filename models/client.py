from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from config import BASE


class Client(BASE):
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
    
    