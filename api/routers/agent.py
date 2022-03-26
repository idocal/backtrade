from celery.result import AsyncResult

from api.db.database import get_db
from api.db import crud

from fastapi import APIRouter, Depends
from secrets import token_hex
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.routers.schemas import AgentUpdateRequest, KEY_SIZE
from api.worker import app
import os


router = APIRouter()


@router.get("/api/agent/create")
async def create_agent(db: Session = Depends(get_db)):
    """
    Generate unique token
    """
    key = token_hex(KEY_SIZE)
    agent = crud.create_agent(db, key)
    content = {"id": agent.id}
    return JSONResponse(content={"success": True, "content": content})


@router.get("/api/agent/all")
async def all_agents(db: Session = Depends(get_db)):
    """
    Gets a list of all agents
    """
    agents = crud.get_all_agents(db)
    agents = [a.as_dict() for a in agents]
    return JSONResponse(content={"success": True, "content": agents})


@router.post("/api/agent/status/{agent_id}")
async def agent_status(agent_id: str, db: Session = Depends(get_db)):
    agent = crud.get_agent(db, agent_id)
    status = {
        a: getattr(agent, a)
        for a in ["train_progress", "train_done", "test_progress", "test_done"]
    }
    return JSONResponse(content={"success": True, "content": status})


@router.post("/api/agent/result/{agent_id}")
async def agent_result(agent_id: str, db: Session = Depends(get_db)):
    agent = crud.get_agent(db, agent_id)
    task_id = agent.task_id
    result = AsyncResult(task_id)
    data = result.get()
    return JSONResponse(content={"success": True, "content": data})


@router.post("/api/agent/kill/{agent_id}")
async def agent_kill(agent_id: str, db: Session = Depends(get_db)):
    agent = crud.get_agent(db, agent_id)
    task_id = agent.task_id
    app.control.revoke(task_id, terminate=True, signal="SIGKILL")
    return JSONResponse(content={"success": True, "content": {"id": agent_id}})


@router.get("/api/agent/delete/{agent_id}")
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """
    Deletes an agent
    """
    crud.delete_agent(db, agent_id)
    content = {
        "id": agent_id
    }
    os.remove(f"models/{agent_id}.zip")
    return JSONResponse(content={"success": True, "content": content})


@router.post("/api/agent/update")
async def update_agent(request: AgentUpdateRequest, db: Session = Depends(get_db)):
    agent_id = request.agent_id
    agent = crud.update_agent(db, agent_id, list(request.updates.keys()), list(request.updates.values()))
    return JSONResponse(content={"success": True, "content": agent.id})
