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
