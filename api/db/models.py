from sqlalchemy import Boolean, Column, String, Float

from .database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    training_progress = Column(Float, default=0.0)
    training_completed = Column(Boolean, default=False)
    testing_progress = Column(Float, default=0.0)
    testing_completed = Column(Boolean, default=False)
