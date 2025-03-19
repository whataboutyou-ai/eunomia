import httpx
from eunomia_core import schemas
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from eunomia.db import db
from eunomia.server import EunomiaServer

router = APIRouter()
server = EunomiaServer()


@router.post("/check-access", response_model=bool)
async def check_access(
    request: schemas.AccessRequest, db_session: Session = Depends(db.get_db)
):
    try:
        return await server.check_access(request, db=db_session)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OPA call failed: {exc}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed /check-access: {exc}",
        )


@router.post("/register-entity", response_model=schemas.EntityInDb)
async def register_entity(
    entity: schemas.EntityCreate, db_session: Session = Depends(db.get_db)
):
    try:
        return server.register_entity(entity, db=db_session)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed /register-entity: {exc}",
        )


@router.post("/update-entity", response_model=schemas.EntityInDb)
async def update_entity(
    entity: schemas.EntityUpdate,
    override: bool = False,
    db_session: Session = Depends(db.get_db),
):
    try:
        return server.update_entity(entity, override=override, db=db_session)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed /update-entity: {exc}",
        )


@router.post("/delete-entity", response_model=schemas.EntityInDb)
async def delete_entity(uri: str, db_session: Session = Depends(db.get_db)):
    try:
        return server.delete_entity(uri, db=db_session)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed /delete-entity: {exc}",
        )
