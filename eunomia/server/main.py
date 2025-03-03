from contextlib import asynccontextmanager

from fastapi import FastAPI

from eunomia.engine.opa import OpaPolicyEngine
from eunomia.server.api import routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = OpaPolicyEngine()
    try:
        engine.start()
        yield
    finally:
        engine.stop()


app = FastAPI(lifespan=lifespan)

app.include_router(routers.router)
