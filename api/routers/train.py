from data.providers import VALID_SYMBOLS, VALID_INTERVALS
from .schemas import RunRequest
from api.db.database import get_db

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.worker import train_task
from api.db import crud
from pydantic import Field


class TrainRequest(RunRequest):
    ...


router = APIRouter()


@router.post("/api/train")
async def train(
    request: TrainRequest,
    db: Session = Depends(get_db),
):
    task = train_task.delay(request.dict())
    crud.update_agent(
        db,
        request.agent_id,
        ["task_id", "symbols", "train_interval", "train_start", "train_end"],
        [task.id, request.symbol, request.interval, request.start, request.end],
    )

    return JSONResponse(content={"success": True, "content": request.agent_id})
