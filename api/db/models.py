from sqlalchemy import Integer, Column, String, Float, PickleType

from .database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    train_progress = Column(Float, default=-1.0)
    train_done = Column(Integer, default=0)
    test_progress = Column(Float, default=-1.0)
    test_done = Column(Integer, default=0)
    task_id = Column(String, default="")
    symbols = Column(PickleType, default=[])


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def get(self, name):
        self.__getattr__(name)

    def set(self, name, value):
        self.__setattr__(name, value)
