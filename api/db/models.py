from sqlalchemy import Integer, Column, String, Float, PickleType, ARRAY, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    name = Column(String)
    train_progress = Column(Float, default=-1.0)
    train_done = Column(Integer, default=0)
    test_progress = Column(Float, default=-1.0)
    test_done = Column(Integer, default=0)
    task_id = Column(String, default="")
    symbols = Column(ARRAY(String))
    train_interval = Column(String)
    train_start = Column(String)
    train_end = Column(String)
    # train_initial_amount = Column(Float)
    # train_commission = Column(Float)
    test_interval = Column(String)
    test_start = Column(String)
    test_end = Column(String)
    # test_initial_amount = Column(Float)
    # test_commission = Column(Float)
    test_balances = relationship("Balance", cascade='delete, delete-orphan')
    test_trades = relationship("Trade", cascade='delete, delete-orphan')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def set(self, name, value):
        self.__setattr__(name, value)


class Balance(Base):
    __tablename__ = "balances"
    agent_id = Column(String, ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    balance = Column(Float, primary_key=True)


class Trade(Base):
    __tablename__ = "trades"
    agent_id = Column(String, ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    idx = Column(Integer, primary_key=True)
    start = Column(DateTime)
    end = Column(DateTime)
    price_start = Column(Float)
    price_end = Column(Float)
    num_units = Column(Float)
    commission = Column(Float)
    trigger_start = Column(Integer)
    trigger_end = Column(Integer)
