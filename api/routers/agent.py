from api.db.database import get_db
from api.db import crud

from loguru import logger
from fastapi import APIRouter, Depends
from secrets import token_hex
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from api.routers.schemas import AgentUpdateRequest, KEY_SIZE
from api.worker import app
import os

from data.query import get_ohlcv

router = APIRouter()


@router.get("/api/agent/create")
async def create_agent(db: Session = Depends(get_db)):
    """
    Create new agent
    """
    key = token_hex(KEY_SIZE)
    agent = crud.create_agent(db, key)
    content = {"id": agent.id}
    return JSONResponse(content={"success": True, "content": content})


@router.get("/api/agent/clear")
async def clear_agents(db: Session = Depends(get_db)):
    crud.clear_agents(db)
    return JSONResponse(content={"success": True})


@router.get("/api/agent/get/{agent_id}")
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """
    Gets an agent
    """
    agent = crud.get_agent(db, agent_id)
    content = jsonable_encoder({"success": True, "content": agent.__dict__})
    return JSONResponse(content=content)


@router.get("/api/agent/all")
async def all_agents(db: Session = Depends(get_db)):
    """
    Gets a list of all agents
    """
    agents = crud.get_trained_agents(db)
    agents = [a.__dict__ for a in agents]
    content = jsonable_encoder({"success": True, "content": agents})
    return JSONResponse(content=content)


@router.get("/api/agent/status/{agent_id}")
async def agent_status(agent_id: str, db: Session = Depends(get_db)):
    agent = crud.get_agent(db, agent_id)
    status = {
        a: getattr(agent, a)
        for a in [
            "train_progress",
            "train_done",
            "test_progress",
            "test_done",
            "action",
            "obs",
            "balance",
        ]
    }
    return JSONResponse(content={"success": True, "content": status})


@router.post("/api/agent/kill/{agent_id}")
async def agent_kill(agent_id: str, db: Session = Depends(get_db)):
    agent = crud.get_agent(db, agent_id)
    task_id = agent.task_id
    app.control.revoke(task_id, terminate=True, signal="SIGKILL")
    content = {"agent_id": agent_id}
    return JSONResponse(content={"success": True, "content": content})


@router.get("/api/agent/delete/{agent_id}")
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """
    Deletes an agent
    """
    crud.delete_agent(db, agent_id)
    try:
        os.remove(f"models/{agent_id}.zip")
    except FileNotFoundError:
        pass
    content = {"agent_id": agent_id}
    return JSONResponse(content={"success": True, "content": content})


@router.post("/api/agent/update")
async def update_agent(request: AgentUpdateRequest, db: Session = Depends(get_db)):
    agent_id = request.agent_id
    crud.update_agent(
        db, agent_id, list(request.updates.keys()), list(request.updates.values())
    )
    content = {"agent_id": agent_id}
    return JSONResponse(content={"success": True, "content": content})
