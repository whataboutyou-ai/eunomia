from typing import List

import httpx
from fastapi import APIRouter, HTTPException

from eunomia.server.logic import allowed_resources_logic, check_access_logic

router = APIRouter()


@router.get("/check_access/")
async def check_access(principal_id: str, resource_id: str) -> bool:
    """
    Check access of the principal specified by principal_id to the resource specified by resource_id.
    """
    try:
        check_access_logic()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=500, detail=f"OPA call failed: {exc}")
    return True


@router.get("/allowed_resources/")
async def allowed_resources_logic(principal_id: str) -> List[str]:
    """
    Return the resources the principal specified by principal_id has access to.
    """
    try:
        check_access_logic()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=500, detail=f"OPA call failed: {exc}")
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
