from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, HTTPException, status

from eunomia.server import EunomiaServer

router = APIRouter()
server = EunomiaServer()


@router.get("/check-access")
async def check_access(principal_id: str, resource_id: str) -> bool:
    """
    Check access of the principal specified by principal_id to the resource specified by resource_id.
    """
    try:
        return await server.check_access(principal_id, resource_id)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OPA call failed: {exc}",
        )


@router.get("/allowed-resources")
async def allowed_resources(principal_id: str) -> List[str]:
    """
    Return the resources the principal specified by principal_id has access to.
    """
    try:
        return await server.allowed_resources(principal_id)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OPA call failed: {exc}",
        )


@router.post("/register_resource/")
async def register_resource(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Receive and process a document payload.

    The payload is expected to contain keys such as "doc_id", "metadata", and "content".
    """
    try:
        resource_metadata = payload.get("metadata", None)
        resource_content = payload.get("content", None)

        if resource_metadata is None:
            raise HTTPException(
                status_code=500, detail=f"Processing failed: Missing resoure metadata"
            )

        success = await server.register_resource(resource_metadata, resource_content)
        if success is True:
            return {"status": "success", "eunomia_id": resource_metadata["eunomia_id"]}
        else:
            raise HTTPException(
                status_code=500, detail=f"Processing failed: Internal Problem"
            )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}")
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
