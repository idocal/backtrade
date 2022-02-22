from db.database import engine, Base
from routers import train, test, agent
from data.query import MissingDataError
from data.providers import DownloadError

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


Base.metadata.create_all(bind=engine)


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
    return JSONResponse(content={"success": True})


app.include_router(agent.router)
app.include_router(train.router)
app.include_router(test.router)


@app.exception_handler(MissingDataError)
async def data_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        content={"success": False, "content": str(exc), "type": "data"}, status_code=400
    )


@app.exception_handler(DownloadError)
async def download_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        content={"success": False, "content": str(exc), "type": "download"},
        status_code=400,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(content={"success": False, "type": "general"}, status_code=500)
