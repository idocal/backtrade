import datetime
from typing import List, Any, Union

import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import insert, desc

from envs.utils import Trade
from . import models


def get_agent(db: Session, agent_id: str) -> models.Agent:
    return db.query(models.Agent).filter(models.Agent.id == agent_id).first()


def get_trained_agents(db: Session):
    return (
        db.query(models.Agent)
        .filter(models.Agent.last_trained != None)
        .order_by(desc(models.Agent.last_trained))
        .all()
    )


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


def clear_agents(db: Session):
    agents = db.query(models.Agent).all()
    for a in agents:
        db.delete(a)
    db.commit()
    return


def add_balances(db: Session, evaluation_id: str, ledger):
    # TODO: add ON_DUPLICATE_UPDATE
    db.execute(
        insert(models.Balance.__table__),
        [
            {"evaluation_id": evaluation_id, "timestamp": t, "balance": b}
            for t, b in zip(ledger["timestamps"], ledger["balances"])
        ],
    )
    db.commit()
    return


def delete_balances(db: Session, evaluation_id: str):
    db.query(models.Balance).filter(
        models.Balance.evaluation_id == evaluation_id
    ).delete()
    db.commit()
    return


def get_balances(db: Session, evaluation_id: str):
    q = f"SELECT timestamp , balance FROM balances WHERE evaluation_id = '{evaluation_id}'"
    return pd.read_sql_query(q, db.connection())


def add_trades(db: Session, evaluation_id: str, trades: List[Trade]):
    # TODO: add ON_DUPLICATE_UPDATE
    db.execute(
        insert(models.Trade.__table__),
        [{**{"evaluation_id": evaluation_id}, **t.as_dict()} for t in trades],
    )
    db.commit()
    return


def delete_trades(db: Session, evaluation_id: str):
    db.query(models.Trade).filter(models.Trade.evaluation_id == evaluation_id).delete()
    db.commit()
    return


def get_trades(db: Session, evaluation_id: str):
    q = (
        f"SELECT idx , start_time, end_time, price_start, price_end, num_units, "
        f"commission FROM trades WHERE evaluation_id = '{evaluation_id}'"
    )
    return pd.read_sql_query(q, db.connection())


def add_evaluation(db: Session, request, evaluation_id: str, symbols: List[str]):
    db_evaluation = models.Evaluation(
        date=datetime.datetime.now(),
        agent_id=request.agent_id,
        evaluation_id=evaluation_id,
        symbols=symbols,
        interval=request.interval,
        start_date=request.start_date,
        end_date=request.end_date,
        initial_amount=request.initial_amount,
        commission=request.commission,
    )
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    return


def get_evaluation(db: Session, evaluation_id: str) -> models.Evaluation:
    return (
        db.query(models.Evaluation)
        .filter(models.Evaluation.evaluation_id == evaluation_id)
        .first()
    )


def update_evaluation(
    db: Session,
    evaluation_id: str,
    attr: Union[List[str], str],
    value: Union[List, Any],
):
    db_evaluation = get_evaluation(db, evaluation_id)
    if isinstance(attr, str):
        db_evaluation.set(attr, value)
    else:
        for a, v in zip(attr, value):
            db_evaluation.set(a, v)
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation
