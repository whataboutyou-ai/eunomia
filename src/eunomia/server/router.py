from eunomia_core import schemas
from fastapi import APIRouter

from eunomia.server import EunomiaServer


def server_router_factory(server: EunomiaServer) -> APIRouter:
    router = APIRouter()

    @router.post("/check", response_model=schemas.CheckResponse)
    async def check(request: schemas.CheckRequest):
        return await server.check(request)

    @router.post("/check/bulk", response_model=list[schemas.CheckResponse])
    async def bulk_check(requests: list[schemas.CheckRequest]):
        return await server.bulk_check(requests)

    return router
