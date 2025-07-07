from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from eunomia.api.routers import admin_router_factory, public_router_factory
from eunomia.config import settings
from eunomia.server import EunomiaServer

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)
server = EunomiaServer()


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(public_router_factory(server))
app.include_router(admin_router_factory(server))


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
