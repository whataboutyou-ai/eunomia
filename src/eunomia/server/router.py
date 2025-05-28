import asyncio

from eunomia_core import schemas
from fastapi import APIRouter, HTTPException, status

from eunomia.config import settings
from eunomia.server import EunomiaServer


def server_router_factory(server: EunomiaServer) -> APIRouter:
    router = APIRouter()

    @router.post("/check", response_model=bool)
    async def check(request: schemas.CheckRequest):
        return await server.check(request)

    @router.post("/check/bulk", response_model=list[bool])
    async def bulk_check(requests: list[schemas.CheckRequest]):
        if not requests:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Empty request list"
            )
        if len(requests) > settings.BULK_CHECK_MAX_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Too many requests. Maximum allowed: {settings.BULK_CHECK_MAX_REQUESTS}",
            )

        return await asyncio.gather(*[server.check(request) for request in requests])

    return router
