from typing import List, Optional

from data.providers import VALID_SYMBOLS, VALID_INTERVALS
from .schemas import RunRequest
from api.db.database import get_db

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.worker import train_task
from api.db import crud
from pydantic import Field, validator


class TrainRequest(RunRequest):
    symbols: List[str] = Field(..., description=f"Enter a subset of {VALID_SYMBOLS}")
    name: Optional[str]

    @validator("symbols")
    def ensure_allowed_symbols(cls, symbols):
        assert set(symbols).issubset(
            VALID_SYMBOLS
        ), f"Enter a subset of {list(VALID_SYMBOLS)}"

        return symbols


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
        ["task_id", "symbols", "train_interval", "train_start", "train_end", "name", "train_initial_amount",
         "train_commission"],
        [task.id, request.symbols, request.interval, request.start_date, request.end_date, request.name,
         request.initial_amount, request.commission],
    )

    return JSONResponse(content={"success": True, "content": request.agent_id})
