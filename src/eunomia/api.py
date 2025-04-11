from contextlib import asynccontextmanager

from fastapi import FastAPI

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
