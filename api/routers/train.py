from .request_template import RunRequest

from agents import StatusCallback, SingleDQNAgent, SingleAgent
from envs import SingleAssetEnv
from data.download import download
from data.query import MissingDataError, get_ohlcv

from stable_baselines3.common.env_checker import check_env
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from pathlib import Path
from enum import Enum


class TrainRequest(RunRequest):
    pass


router = APIRouter()


def call_train(agent: SingleAgent, num_train_steps: int, agent_id: str):
    agent.learn(
        num_train_steps,
        callback=[
            StatusCallback(
                Status,
                "models" + "/" + str(agent_id) + "/" + TRAIN_STATUS_FILE_PATH,
                num_train_steps,
            ),
        ],
    )

    agent.save("models" + "/" + str(agent_id))


@router.post("/train")
async def train(request: TrainRequest, background_tasks: BackgroundTasks):
    try:
        df = get_ohlcv(request.symbol, request.start, request.end, request.interval)
    except MissingDataError:
        download(
            request.provider,
            request.symbol,
            request.interval,
            request.start,
            request.end,
        )
        df = get_ohlcv(request.symbol, request.start, request.end, request.interval)
    env = SingleAssetEnv(request.dict(), df)
    check_env(env)
    agent = SingleDQNAgent(env)
    num_train_steps = len(env.df)
    Path("models" + "/" + str(request.agent_id)).mkdir(exist_ok=True)

    background_tasks.add_task(call_train, agent, num_train_steps, request.agent_id)

    return JSONResponse(content={"success": True, "content": request.agent_id})


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


@router.post("/train/{agent_id}")
async def train_status(agent_id: str):
    return JSONResponse(
        content=get_status(
            "train_status",
            "models" + "/" + str(agent_id) + "/" + TRAIN_STATUS_FILE_PATH,
        ),
    )
