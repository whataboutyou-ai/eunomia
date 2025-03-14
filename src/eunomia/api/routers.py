from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from eunomia.db import db
from eunomia.server import EunomiaServer

router = APIRouter()
server = EunomiaServer()


@router.get("/check-access")
async def check_access(
    principal_id: str, resource_id: str, db_session: Session = Depends(db.get_db)
) -> bool:
    try:
        return await server.check_access(principal_id, resource_id, db=db_session)
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OPA call failed: {exc}",
        )


@router.post("/register_resource")
async def register_resource(
    payload: Dict[str, Any], db_session: Session = Depends(db.get_db)
) -> Dict[str, Any]:
    try:
        resource_metadata = payload.get("metadata", None)
        resource_content = payload.get("content", None)

        if resource_metadata is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Processing failed: Missing resoure metadata",
            )

        eunomia_id = await server.register_resource(resource_metadata, db=db_session)
        if eunomia_id is not None:
            return {"status": "success", "eunomia_id": eunomia_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Processing failed: Internal Problem",
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
async def register_principal(
    payload: Dict[str, Any], db_session: Session = Depends(db.get_db)
) -> Dict[str, Any]:
    try:
        principal_metadata = payload.get("metadata", None)

        if principal_metadata is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Processing failed: Missing resoure metadata",
            )

        eunomia_id = await server.register_principal(principal_metadata, db=db_session)
        if eunomia_id is not None:
            return {"status": "success", "eunomia_id": eunomia_id}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Processing failed: Internal Problem",
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
