from .schemas import RunRequest
from api.db.database import get_db
from api.db import crud

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.worker import test_task


class TestRequest(RunRequest):
    ...


router = APIRouter()


@router.post("/api/test")
async def test(request: TestRequest, db: Session = Depends(get_db)):
    crud.update_agent(db, request.agent_id, "test_done", 0)
    crud.update_agent(db, request.agent_id, "test_progress", 0)
    temp_request = request.dict()
    agent = crud.get_agent(db, request.agent_id)
    temp_request["symbols"] = getattr(agent, "symbols")  # get test symbols from db
    task = test_task.delay(temp_request)

    crud.update_agent(
        db,
        request.agent_id,
        [
            "task_id",
            "symbols",
            "test_interval",
            "test_start",
            "test_end",
            "test_initial_amount",
            "test_commission",
        ],
        [
            task.id,
            temp_request["symbols"],
            request.interval,
            request.start_date,
            request.end_date,
            request.initial_amount,
            request.commission,
        ],
    )
    crud.add_test(db, request.agent_id, task.id)
    return JSONResponse(content={"success": True, "content": request.agent_id})
