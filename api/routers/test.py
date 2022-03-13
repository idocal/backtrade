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
    task = test_task.delay(request.dict())
    crud.update_agent(db, request.agent_id,
                      ["task_id", "symbols", "test_interval", "test_start", "test_end"],
        [task.id, request.symbol, request.interval, request.start, request.end])
    return JSONResponse(content={"success": True, "content": request.agent_id})
