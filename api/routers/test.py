from agents import SingleDQNAgent
from .request_template import RunRequest
from envs import SingleAssetEnv
from agents.callbacks import write_progress_to_file
from stable_baselines3.common.env_checker import check_env

from data.download import download
from data.query import MissingDataError

from fastapi import APIRouter, Depends
from enum import Enum
from pandas import DataFrame
from sqlalchemy.orm import Session
from db.database import get_db

from .utils import initialize_agent_env


class TestRequest(RunRequest):
    pass


router = APIRouter()


@router.post("/test")
async def test(request: TestRequest, db: Session = Depends(get_db)):
    agent, env = initialize_agent_env(request)
    agent.load("models" + "/" + request.agent_id)
    obs = env.reset()
    total_steps = len(env.df)

    while True:
        action = agent.predict(obs)
        obs, reward, done, info = env.step(action)
        crud.update_agent(db, request.agent_id, "test_progress", env.step_idx / total_steps)
        if done:
            crud.update_agent(db, request.agent_id, "test_done", 1)
            break

    # TODO assert length of ledger and candles is the same (or not)

    def generate_data(df: DataFrame):
        """Yields the whole ledger in one chunk, then yields every candle in order"""

        yield '{"ledger":' + dumps(
            dict(
                balances=agent.env.ledger.balances,
                timestamps=agent.env.ledger.dates,
            ),
            indent=4,
            default=str,
        ) + ',"candles":{'
        for i in range(len(df) - 1):
            yield f'"{i}":' + df.iloc[i].to_json(orient="values") + ","
        yield f'"{len(df) - 1}":' + df.iloc[len(df) - 1].to_json(orient="values") + "}}"

    return Response(generate_data(agent.env.df), mimetype="application/json")