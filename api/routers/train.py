from .schemas import RunRequest
from agents import SingleAgent, StatusCallbackDB
from api.db.database import get_db
from .utils import initialize_agent_env

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.worker import train_task
from api.db import crud


class TrainRequest(RunRequest):
    pass


router = APIRouter()


# def task_train(agent: SingleAgent, num_train_steps: int, agent_id: str, db: Session):
#     agent.learn(
#         num_train_steps,
#         callback=[StatusCallbackDB(db, agent_id, num_train_steps)],
#     )
#     agent.save("models" + "/" + agent_id)


@router.post("/api/train")
async def train(
        request: TrainRequest,
        db: Session = Depends(get_db),
):

    task = train_task.delay(request.dict())
    crud.update_agent(db, request.agent_id, "task_id", task.id)

    return JSONResponse(content={"success": True, "content": request.agent_id})
