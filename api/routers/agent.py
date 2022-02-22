from db.database import get_db
from db import crud

from fastapi import APIRouter, Depends
from secrets import token_hex
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

router = APIRouter()

KEY_SIZE = 32


@router.get("/create_agent")
async def create_agent(db: Session = Depends(get_db)):
    """
    Generate unique token
    """
    key = token_hex(KEY_SIZE)
    agent = crud.create_agent(db, key)
    return JSONResponse(content={"success": True, "content": agent.id})


@router.post("/agent_status/{agent_id}")
async def agent_status(agent_id: str, db: Session = Depends(get_db)):
    agent = crud.get_agent(db, agent_id)
    return JSONResponse(content={"success": True, "content": agent.as_dict()})


# @router.post("/update_agent/{agent_id}/{attr}/{val}")
# async def update_agent(agent_id: str, attr: str, val, db: Session = Depends(get_db)):
#     agent = crud.update_agent(db, agent_id, attr, val)
#     return JSONResponse(content={"success": True, "agent_status": agent.as_dict()})
