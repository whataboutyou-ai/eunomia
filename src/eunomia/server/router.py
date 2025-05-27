import asyncio

from eunomia_core import schemas
from fastapi import APIRouter

from eunomia.server import EunomiaServer


def server_router_factory(server: EunomiaServer) -> APIRouter:
    router = APIRouter()

    @router.post("/check", response_model=bool)
    async def check(request: schemas.CheckRequest):
        return await server.check(request)

    @router.post("/check/bulk", response_model=list[bool])
    async def bulk_check(requests: list[schemas.CheckRequest]):
        return await asyncio.gather(*[server.check(request) for request in requests])

    return router
