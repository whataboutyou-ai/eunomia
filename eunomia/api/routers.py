from typing import List

import httpx
from fastapi import APIRouter, HTTPException, status

from eunomia.server import EunomiaServer

router = APIRouter()


@router.get("/check-access/")
async def check_access(principal_id: str, resource_id: str) -> bool:
    """
    Check access of the principal specified by principal_id to the resource specified by resource_id.
    """
    try:
        server = EunomiaServer()
        return await server.check_access(principal_id, resource_id)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OPA call failed: {exc}",
        )


@router.get("/allowed-resources/")
async def allowed_resources(principal_id: str) -> List[str]:
    """
    Return the resources the principal specified by principal_id has access to.
    """
    try:
        server = EunomiaServer()
        return await server.allowed_resources(principal_id)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OPA call failed: {exc}",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )
