from typing import List, Any, Union
from datetime import datetime

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import insert

from envs.utils import Trade
from . import models


def get_agent(db: Session, agent_id: str) -> models.Agent:
    return db.query(models.Agent).filter(models.Agent.id == agent_id).first()


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


def delete_agent(db: Session, agent_id: str):
    db_agent = get_agent(db, agent_id)
    db.delete(db_agent)
    db.commit()
    return


def add_balances(db: Session, agent_id: str, ledger):
    # TODO: add ON_DUPLICATE_UPDATE
    db.execute(
        insert(models.Balance.__table__),
        [
            {"agent_id": agent_id, "timestamp": t, "balance": b}
            for t, b in zip(ledger["timestamps"], ledger["balances"])
        ],
    )
    db.commit()
    return


def get_balances(db: Session, agent_id: str):
    q = f"SELECT timestamp , balance FROM balances WHERE agent_id = '{agent_id}'"
    return pd.read_sql_query(q, db.connection())


def add_trades(db: Session, agent_id: str, trades: List[Trade]):
    # TODO: add ON_DUPLICATE_UPDATE
    db.execute(
        insert(models.Trade.__table__),
        [
            {
                "agent_id": agent_id,
                "start_time": t.start_time,
                "price_start": t.price_start,
                "num_units": t.num_units,
                "trigger_start": t.trigger_start.value,
                "idx": t.idx,
                "commission": t.commission,
                "end_time": t.end_time,
                "price_end": t.price_end,
                "trigger_end": t.trigger_end.value,
            }
            for t in trades
        ],
    )
    db.commit()
    return


def get_trades(db: Session, agent_id: str):
    q = f"SELECT idx , start_time, end_time, price_start, price_end, num_units, commission, trigger_start, trigger_end FROM trades WHERE agent_id = '{agent_id}'"
    return pd.read_sql_query(q, db.connection())
