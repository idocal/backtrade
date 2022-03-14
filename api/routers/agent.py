from celery.result import AsyncResult
from api.db.database import get_db
from api.db import crud

from fastapi import APIRouter, Depends
from secrets import token_hex
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from api.worker import app

KEY_SIZE = 32

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


@router.get("/api/agent/delete/{agent_id}")
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """
    Deletes an agent
    """
    crud.delete_agent(db, agent_id)
    content = {
        "id": agent_id
    }
    return JSONResponse(content={"success": True, "content": content})


@router.get("/api/agent/all")
async def all_agents(db: Session = Depends(get_db)):
    """
    Gets a list of all agents
    """
    agents = crud.get_all_agents(db)
    agents = [a.id for a in agents]
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

# @router.post("/update_agent/{agent_id}/{attr}/{val}")
# async def update_agent(agent_id: str, attr: str, val, db: Session = Depends(get_db)):
#     agent = crud.update_agent(db, agent_id, attr, val)
#     return JSONResponse(content={"success": True, "agent_status": agent.as_dict()})
