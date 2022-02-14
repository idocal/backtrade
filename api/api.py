from fastapi import FastAPI
from fastapi.responses import JSONResponse
from secrets import token_hex
from routers import train, test

app = FastAPI()


@app.get("/")
async def root():
    return JSONResponse(content=True)


@app.get("/agent_id")
async def agent_id():
    return JSONResponse(content=token_hex(32))


app.include_router(train.router)
app.include_router(test.router)
