from .request_template import RunRequest
from agents import SingleDQNAgent, SingleAgent, StatusCallbackDB
from envs import SingleAssetEnv
from data.download import download
from data.query import MissingDataError, get_ohlcv
from db.database import get_db

from stable_baselines3.common.env_checker import check_env
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .utils import initialize_agent_env


class TrainRequest(RunRequest):
    pass


router = APIRouter()


def call_train(agent: SingleAgent, num_train_steps: int, agent_id: str, db: Session):
    agent.learn(
        num_train_steps,
        callback=[
            StatusCallbackDB(db, agent_id, num_train_steps)
        ],
    )
    agent.save("models" + "/" + agent_id)


@router.post("/train")
async def train(request: TrainRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    agent, env = initialize_agent_env(request)
    background_tasks.add_task(call_train, agent, len(env.df), request.agent_id, db)

    return JSONResponse(content={"success": True, "content": request.agent_id})
