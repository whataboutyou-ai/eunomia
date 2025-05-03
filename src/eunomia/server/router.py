from eunomia_core import schemas
from fastapi import APIRouter

from eunomia.server import EunomiaServer


def server_router_factory(server: EunomiaServer) -> APIRouter:
    router = APIRouter()

    @router.post("/check-access", response_model=bool)
    async def check_access(request: schemas.AccessRequest):
        return server.check_access(request)

    return router
