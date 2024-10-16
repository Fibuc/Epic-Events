import enum
from datetime import datetime

from sqlalchemy import Column, Integer, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from config import BASE


class Contract(BASE):
    __tablename__ = 'contracts'

    class ContractStatus(enum.Enum):
        signed = 'Signé'
        unsigned = 'Non signé'

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    commercial_id = Column(Integer, ForeignKey('users.id'), nullable=False)
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