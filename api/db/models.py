from sqlalchemy import *
from sqlalchemy.orm import relationship

from .database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, unique=True)
    name = Column(String)
    train_progress = Column(Float, default=-1.0)
    train_done = Column(Integer, default=0)
    task_id = Column(String, default="")
    symbols = Column(ARRAY(String))
    train_interval = Column(String)
    train_start = Column(Date)
    train_end = Column(Date)
    train_initial_amount = Column(Float)
    train_commission = Column(Float)
    train_episodes = Column(Integer)
    last_trained = Column(DateTime)
    evaluation = relationship("Evaluation", cascade="all, delete-orphan")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def set(self, name, value):
        self.__setattr__(name, value)


class Evaluation(Base):
    __tablename__ = "evaluations"
    date = Column(DateTime)
    agent_id = Column(String, ForeignKey("agents.id", ondelete="CASCADE"))
    evaluation_id = Column(String, primary_key=True, unique=True)
    symbols = Column(ARRAY(String))
    interval = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    initial_amount = Column(Float)
    commission = Column(Float)
    last_balance = Column(Float)
    evaluation_progress = Column(Float, default=-1.0)
    evaluation_done = Column(Integer, default=0)
    balances = relationship("Balance", cascade="all, delete-orphan")
    trades = relationship("Trade", cascade="all, delete-orphan")

    def set(self, name, value):
        self.__setattr__(name, value)


class Balance(Base):
    __tablename__ = "balances"
    evaluation_id = Column(
        String,
        ForeignKey("evaluations.evaluation_id", ondelete="CASCADE"),
        primary_key=True,
    )
    timestamp = Column(DateTime, primary_key=True)
    balance = Column(Float, primary_key=True)


class Trade(Base):
    __tablename__ = "trades"
    evaluation_id = Column(
        String,
        ForeignKey("evaluations.evaluation_id", ondelete="CASCADE"),
        primary_key=True,
    )
    idx = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    price_start = Column(Float)
    price_end = Column(Float)
    num_units = Column(Float)
    commission = Column(Float)

    def as_dict(self):
        return {c.name: getattr(self, c.name).to for c in self.__table__.columns}
