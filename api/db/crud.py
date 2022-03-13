from typing import List, Any, Union

from sqlalchemy.orm import Session
from . import models


def get_agent(db: Session, agent_id: str):
    return db.query(models.Agent).filter(models.Agent.id == agent_id).first()


def get_agent_attr(db: Session, agent_id: str, attr: str):
    db_agent = get_agent(db, agent_id)
    return db_agent.get(attr)


def get_all_agents(db: Session):
    return db.query(models.Agent).all()


def update_agent(
    db: Session, agent_id: str, attr: Union[List[str], str], value: Union[List, Any]
):
    db_agent = get_agent(db, agent_id)
    if isinstance(attr, str):
        db_agent.set(attr, value)
    else:
        for a, v in zip(attr, value):
            db_agent.set(a, v)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def create_agent(db: Session, agent_id: str):
    db_agent = models.Agent(id=agent_id)
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent
