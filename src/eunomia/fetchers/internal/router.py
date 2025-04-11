from eunomia_core import schemas
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from eunomia.fetchers.internal import EunomiaInternalFetcher
from eunomia.fetchers.internal.db import db

fetcher_router = APIRouter()
fetcher = EunomiaInternalFetcher()


@fetcher_router.post("/register-entity", response_model=schemas.EntityInDb)
async def register_entity(
    entity: schemas.EntityCreate, db_session: Session = Depends(db.get_db)
):
    try:
        return fetcher.register_entity(entity, db=db_session)
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


@fetcher_router.post("/update-entity", response_model=schemas.EntityInDb)
async def update_entity(
    entity: schemas.EntityUpdate,
    override: bool = False,
    db_session: Session = Depends(db.get_db),
):
    try:
        return fetcher.update_entity(entity, override=override, db=db_session)
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


@fetcher_router.post("/delete-entity")
async def delete_entity(uri: str, db_session: Session = Depends(db.get_db)):
    try:
        fetcher.delete_entity(uri, db=db_session)
        return {"uri": uri, "message": "Entity deleted successfully"}
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
