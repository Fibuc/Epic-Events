from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from config import BASE


class Event(BASE):
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