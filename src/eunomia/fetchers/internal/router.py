from eunomia_core import schemas
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from eunomia.fetchers.internal import InternalFetcher
from eunomia.fetchers.internal.db import crud, db


def internal_router_factory(fetcher: InternalFetcher) -> APIRouter:
    router = APIRouter()

    @router.post("/register-entity", response_model=schemas.EntityInDb)
    async def register_entity(
        entity: schemas.EntityCreate, db_session: Session = Depends(db.get_db)
    ):
        return fetcher.register_entity(entity, db=db_session)

    @router.post("/update-entity", response_model=schemas.EntityInDb)
    async def update_entity(
        entity: schemas.EntityUpdate,
        override: bool = False,
        db_session: Session = Depends(db.get_db),
    ):
        return fetcher.update_entity(entity, override=override, db=db_session)

    @router.post("/delete-entity")
    async def delete_entity(uri: str, db_session: Session = Depends(db.get_db)):
        fetcher.delete_entity(uri, db=db_session)
        return {"uri": uri, "message": "Entity deleted successfully"}

    @router.get("/entities", response_model=list[schemas.EntityInDb])
    async def get_entities(
        offset: int = 0, limit: int = 10, db_session: Session = Depends(db.get_db)
    ):
        return crud.get_entities(offset=offset, limit=limit, db=db_session)

    @router.get("/entities/count")
    async def get_entities_count(db_session: Session = Depends(db.get_db)) -> int:
        return crud.get_entities_count(db=db_session)

    return router
