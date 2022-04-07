from fastapi.encoders import jsonable_encoder
from loguru import logger

from data.query import get_ohlcv
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
    temp_request = request.dict()
    agent = crud.get_agent(db, request.agent_id)
    temp_request["symbols"] = getattr(agent, "symbols")  # get test symbols from db
    task = test_task.delay(temp_request)
    crud.add_evaluation(
        db, request, evaluation_id=task.id, symbols=temp_request["symbols"]
    )
    content = {"evaluation_id": task.id}
    return JSONResponse(content={"success": True, "content": content})


@router.get("/api/evaluation/result/{evaluation_id}")
async def evaluation_result(evaluation_id: str, db: Session = Depends(get_db)):
    evaluation = crud.get_evaluation(db, evaluation_id)
    data = dict()
    balances = crud.get_balances(db, evaluation_id)
    data["balances"] = balances["balance"].values.tolist()
    data["timestamps"] = balances["timestamp"].tolist()
    trades = crud.get_trades(db, evaluation_id)
    data["trades"] = trades.values.tolist()
    data["candles"] = get_ohlcv(
        evaluation.symbols,
        evaluation.start_date,
        evaluation.end_date,
        evaluation.interval,
    ).values.tolist()
    logger.debug(data)
    content = jsonable_encoder({"success": True, "content": data})
    logger.debug(content)
    return JSONResponse(content=content)


@router.get("/api/evaluation/get/{evaluation_id}")
async def evaluation_status(evaluation_id: str, db: Session = Depends(get_db)):
    evaluation = crud.get_evaluation(db, evaluation_id)
    content = jsonable_encoder({"success": True, "content": evaluation.__dict__})
    return JSONResponse(content=content)
