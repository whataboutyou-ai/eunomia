from eunomia_core import schemas
from fastapi import APIRouter

from eunomia.server import EunomiaServer

server_router = APIRouter()
server = EunomiaServer()


@server_router.post("/check-access", response_model=bool)
async def check_access(request: schemas.AccessRequest):
    return server.check_access(request)


@server_router.post("/create-policy", response_model=schemas.Policy)
async def create_policy(request: schemas.AccessRequest, name: str):
    return server.create_policy(request, name)
