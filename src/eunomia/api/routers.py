from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, HTTPException, status

from eunomia.server import EunomiaServer

router = APIRouter()
server = EunomiaServer()


@router.get("/check-access")
async def check_access(principal_id: str, resource_id: str) -> bool:
    try:
        return await server.check_access(principal_id, resource_id)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OPA call failed: {exc}",
        )


@router.get("/allowed-resources")
async def allowed_resources(principal_id: str) -> List[str]:
    try:
        return await server.allowed_resources(principal_id)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OPA call failed: {exc}",
        )


@router.post("/register_resource")
async def register_resource(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        resource_metadata = payload.get("metadata", None)
        resource_content = payload.get("content", None)

        if resource_metadata is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Processing failed: Missing resoure metadata",
            )

        eunomia_id = await server.register_resource(resource_metadata, resource_content)
        if eunomia_id is not None:
            return {"status": "success", "eunomia_id": eunomia_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Processing failed: Internal Problem",
            )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {exc}",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


@router.post("/register_principal")
async def register_principal(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        principal_metadata = payload.get("metadata", None)

        if principal_metadata is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Processing failed: Missing resoure metadata",
            )

        eunomia_id = await server.register_principal(principal_metadata)
        if eunomia_id is not None:
            return {"status": "success", "eunomia_id": eunomia_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Processing failed: Internal Problem",
            )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {exc}",
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )
