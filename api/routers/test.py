from .utils import initialize_agent_env
from .request_template import RunRequest
from db.database import get_db
from db import crud
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session


class TestRequest(RunRequest):
    pass


router = APIRouter()


@router.post("/test")
async def test(request: TestRequest, db: Session = Depends(get_db)):
    agent, env = initialize_agent_env(request)
    agent.load("models" + "/" + request.agent_id)
    obs = env.reset()
    total_steps = len(env.df)

    while True:
        action = agent.predict(obs)
        obs, reward, done, info = env.step(action)
        crud.update_agent(
            db, request.agent_id, "test_progress", env.step_idx / total_steps
        )
        if done:
            crud.update_agent(db, request.agent_id, "test_done", 1)
            break

    # TODO assert length of ledger and candles is the same (or not)

    def generate_data():
        return {
            "timestamps": [str(d) for d in agent.env.ledger.dates],
            "balances": agent.env.ledger.balances,
            "candles": env.df.to_json(orient="values"),
        }

    return JSONResponse(content={"success": True, "content": generate_data()})
