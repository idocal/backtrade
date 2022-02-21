from fastapi import APIRouter
from secrets import token_hex
from fastapi.responses import JSONResponse

router = APIRouter()

KEY_SIZE = 32


@router.get("/agent_id")
async def agent_id():
    """
    Generate unique token
    """
    return JSONResponse(content={"success": True, "content": token_hex(KEY_SIZE)})
