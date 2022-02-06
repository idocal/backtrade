from agents import SingleDQNAgent
from envs import SingleAssetEnv
from agents.callbacks import write_progress_to_file
from stable_baselines3.common.env_checker import check_env

from data.download import download
from data.query import MissingData

from fastapi import APIRouter
from pydantic import BaseModel
from enum import Enum
from pandas import DataFrame


class TestRequest(BaseModel):
    agent_id: str
    symbol: str
    interval: str
    start: str
    end: str
    initial_amount: float
    commission: float


router = APIRouter()


@router.post("/test/")
async def test(request: TestRequest):
    agent_id = request.agent_id
    try:
        test_env = SingleAssetEnv(request.dict())
    except MissingData:
        download(
            [request.symbol],
            [request.interval],
            request.start,
            request.end,
        )
        test_env = SingleAssetEnv(request.dict())
    check_env(test_env)
    obs = test_env.reset()
    agent = SingleDQNAgent(test_env)
    try:
        agent.load(str(agent_id) + "/" + MODEL_FILE_PATH)
    except FileNotFoundError:
        return Response(
            "Agent model file not found, try train first.", status=500
        )

    # TODO: respond to client before test?

    fp = open(str(agent_id) + "/" + TEST_STATUS_FILE_PATH, "wb")
    while True:
        action = agent.predict(obs)
        obs, reward, done, info = test_env.step(action)
        write_progress_to_file(fp, test_env.step_idx, len(test_env.df))
        if done:
            write_progress_to_file(fp, Status.DONE.value)
            fp.close()
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
        yield f'"{len(df) - 1}":' + df.iloc[len(df) - 1].to_json(
            orient="values"
        ) + "}}"

    return Response(generate_data(agent.env.df), mimetype="application/json")


class Status(Enum):
    DONE = 200
    DID_NOT_START = -1


MODEL_FILE_PATH = "model"
TRAIN_STATUS_FILE_PATH = "train_status"
TEST_STATUS_FILE_PATH = "test_status"


def get_status(param_name: str, path: str):
    try:
        fp = open(path, "rb")
        st = int.from_bytes(fp.read(), byteorder="big")
        fp.close()
        complete = True if st == Status.DONE.value else False
        return {param_name: st, "complete": complete}
    except FileNotFoundError:
        """If haven't trained yet"""
        return {param_name: Status.DID_NOT_START.value, "complete": False}


@router.post("/test/{agent_id}")
async def train_status(agent_id: str):
    return get_status(
        "test_status", str(agent_id) + "/" + TEST_STATUS_FILE_PATH
    )
