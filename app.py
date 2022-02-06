from fastapi import FastAPI
from secrets import token_hex
from api.routers import train, test

app = FastAPI()


@app.get("/")
async def root():
    return True


@app.get("/agent_id")
async def agent_id():
    return {"agent_id": token_hex(32)}


app.include_router(train.router)
app.include_router(test.router)

