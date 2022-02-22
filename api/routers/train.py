import os
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

MODEL_FILE_PATH = "model"
MODEL_DIRECTORY = "models"
TRAIN_STATUS_FILE_PATH = "train_status"
TEST_STATUS_FILE_PATH = "test_status"


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
    agent_dir = os.path.join(MODEL_DIRECTORY, str(agent_id))
    model_filepath = os.path.join(agent_dir, MODEL_FILE_PATH)
    status_filepath = os.path.join(agent_dir, TRAIN_STATUS_FILE_PATH)
    Path(agent_dir).mkdir(exist_ok=True)

    agent.learn(
        num_train_steps,
        callback=[
            StatusCallback(
                Status,
                status_filepath,
                num_train_steps,
            ),
        ],
    )

    # save agent model to dedicated directory
    # TODO: this should be stored in a DB with URL
    agent.save(model_filepath)


@router.post("/api/train")
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

    background_tasks.add_task(call_train, agent, num_train_steps, agent_id)

    return JSONResponse(content=agent_id)


class Status(Enum):
    DONE = 200
    DID_NOT_START = -1


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


@router.post("/api/train/{agent_id}")
async def train_status(agent_id: str):
    agent_dir = os.path.join(MODEL_DIRECTORY, str(agent_id))
    status_filepath = os.path.join(agent_dir, TRAIN_STATUS_FILE_PATH)

    return JSONResponse(
        content=get_status(
            TRAIN_STATUS_FILE_PATH, status_filepath
        ),
    )
