from contextlib import asynccontextmanager

from fastapi import FastAPI

from eunomia.api.routers import router
from eunomia.config import settings
from eunomia.db import db
from eunomia.engine.opa import OpaPolicyEngine


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
app.include_router(router)
