from agents import StatusCallback, SingleDQNAgent, SingleAgent
from envs import SingleAssetEnv
from stable_baselines3.common.env_checker import check_env

from data.download import download
from data.query import MissingData

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pathlib import Path
from enum import Enum


class TrainRequest(BaseModel):
    agent_id: str
    symbol: str
    interval: str
    start: str = Field(..., description="Date in %Y-%m-%d format")
    end: str = Field(..., description="Date in %Y-%m-%d format")
    initial_amount: float = Field(..., ge=0)
    commission: float = Field(..., ge=0, lt=1)


router = APIRouter()


def call_train(agent: SingleAgent, num_train_steps: int, agent_id: str):
    agent.learn(
        num_train_steps,
        callback=[
            StatusCallback(
                Status,
                str(agent_id) + "/" + TRAIN_STATUS_FILE_PATH,
                num_train_steps,
            ),
        ],
    )

    agent.save(str(agent_id) + "/" + MODEL_FILE_PATH)


@router.post("/train/")
async def train(request: TrainRequest, background_tasks: BackgroundTasks):
    agent_id = request.agent_id
    try:
        env = SingleAssetEnv(request.dict())
    except MissingData:
        download(
            [request.symbol],
            [request.interval],
            request.start,
            request.end,
        )
        env = SingleAssetEnv(request.dict())
    check_env(env)
    agent = SingleDQNAgent(env)
    num_train_steps = len(env.df)
    Path(str(agent_id)).mkdir(exist_ok=True)

    background_tasks.add_task(call_train, agent, num_train_steps, agent_id)

    return JSONResponse(content=agent_id)


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
            "train_status", str(agent_id) + "/" + TRAIN_STATUS_FILE_PATH
        ),
    )
