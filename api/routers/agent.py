from db.database import get_db
from db import crud, models

from fastapi import APIRouter, Depends
from secrets import token_hex
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

router = APIRouter()

KEY_SIZE = 32


@router.get("/agent_id")
async def agent_id(db: Session = Depends(get_db)):
    """
    Generate unique token
    """
    key = token_hex(KEY_SIZE)
    agent = crud.create_agent(db, key)

    return JSONResponse(content={"success": True, "content": agent.id})
