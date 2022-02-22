import os
import pathlib
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from secrets import token_hex
from api.routers import train, test
from fastapi.middleware.cors import CORSMiddleware

MODELS_DIR = "models"

app = FastAPI()
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
async def root():
    return JSONResponse(content=True)


@app.get("/agent_id")
async def agent_id():
    return JSONResponse(content=token_hex(32))


@app.get("/api/agents")
async def get_agents():
    dirs = [f.path for f in os.scandir(MODELS_DIR) if f.is_dir()]
    agents = [pathlib.PurePath(d).name for d in dirs]
    res = {
        'agents': agents
    }
    return JSONResponse(content=res)

app.include_router(train.router)
app.include_router(test.router)
