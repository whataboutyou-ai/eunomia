from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from eunomia.config import settings
from eunomia.engine.opa import OpaPolicyEngine
from eunomia.fetchers.internal.db import db
from eunomia.fetchers.internal.router import fetcher_router
from eunomia.server.router import server_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = OpaPolicyEngine()
    try:
        engine.start()
        db.init_db()
        yield
    finally:
        engine.stop()


app = FastAPI(lifespan=lifespan, title=settings.PROJECT_NAME, debug=settings.DEBUG)
app.include_router(server_router)
app.include_router(fetcher_router)


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": str(exc)}
    )
