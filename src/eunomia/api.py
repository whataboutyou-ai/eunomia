from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from eunomia.config import settings
from eunomia.engine.router import engine_router_factory
from eunomia.fetchers.factory import FetcherFactory
from eunomia.server import EunomiaServer
from eunomia.server.router import server_router_factory

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)
server = EunomiaServer()

app.include_router(server_router_factory(server), tags=["server"])
app.include_router(engine_router_factory(server.engine), tags=["engine"])

for fetcher_id, router in FetcherFactory.get_all_routers().items():
    app.include_router(router, prefix=f"/fetchers/{fetcher_id}", tags=[fetcher_id])


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": str(exc)}
    )
