from fastapi import APIRouter, Depends

from eunomia.api.dependencies import validate_api_key
from eunomia.engine.router import engine_router_factory
from eunomia.fetchers.factory import FetcherFactory
from eunomia.server import EunomiaServer
from eunomia.server.router import server_router_factory


def public_router_factory(server: EunomiaServer) -> APIRouter:
    router = APIRouter()

    router.include_router(server_router_factory(server), tags=["server"])

    return router


def admin_router_factory(server: EunomiaServer) -> APIRouter:
    router = APIRouter(dependencies=[Depends(validate_api_key)], prefix="/admin")

    router.include_router(engine_router_factory(server.engine), tags=["engine"])

    for fetcher_id, fetcher_router in FetcherFactory.get_all_routers().items():
        router.include_router(
            fetcher_router, prefix=f"/fetchers/{fetcher_id}", tags=[fetcher_id]
        )

    return router
