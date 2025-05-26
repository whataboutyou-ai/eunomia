from eunomia_core import schemas
from fastapi import APIRouter

from eunomia.server import EunomiaServer


def server_router_factory(server: EunomiaServer) -> APIRouter:
    router = APIRouter()

    @router.post("/check", response_model=bool)
    async def check(request: schemas.CheckRequest):
        return await server.check(request)

    return router
