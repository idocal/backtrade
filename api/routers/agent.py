from api.db.database import get_db
from api.db import crud

from fastapi import APIRouter, Depends
from secrets import token_hex
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

KEY_SIZE = 32

router = APIRouter()


@router.get("/api/agent/create")
async def create_agent(db: Session = Depends(get_db)):
    """
    Generate unique token
    """
    key = token_hex(KEY_SIZE)
    agent = crud.create_agent(db, key)
    content = {
        "id": agent.id
    }
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
    return JSONResponse(content={"success": True, "content": agent.as_dict()})


# @router.post("/update_agent/{agent_id}/{attr}/{val}")
# async def update_agent(agent_id: str, attr: str, val, db: Session = Depends(get_db)):
#     agent = crud.update_agent(db, agent_id, attr, val)
#     return JSONResponse(content={"success": True, "agent_status": agent.as_dict()})
