import httpx
from eunomia_core import schemas
from fastapi import APIRouter, HTTPException, status

from eunomia.server import EunomiaServer

server_router = APIRouter()
server = EunomiaServer()


@server_router.post("/check-access", response_model=bool)
async def check_access(request: schemas.AccessRequest):
    try:
        return await server.check_access(request)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OPA call failed: {exc}",
        )


@server_router.post("/create-policy")
async def create_policy(policy: schemas.Policy, filename: str = "policy.rego"):
    path = server.create_policy(policy, filename=filename)
    return {"path": path, "message": "Policy created successfully at path"}
