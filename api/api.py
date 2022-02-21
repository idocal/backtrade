from routers import train, test, agent
from data.query import MissingDataError
from data.providers import DownloadError

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


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
