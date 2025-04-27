from eunomia_core import schemas
from fastapi import APIRouter

from eunomia.server import EunomiaServer

server_router = APIRouter()
server = EunomiaServer()


@server_router.post("/check-access", response_model=bool)
async def check_access(request: schemas.AccessRequest):
    return await server.check_access(request)


@server_router.post("/create-policy")
async def create_policy(policy: schemas.Policy):
    path = server.create_policy(policy)
    return {"path": path, "message": "Policy created successfully at path"}
