from eunomia_core import schemas
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from eunomia.fetchers.registry import RegistryFetcher
from eunomia.fetchers.registry.db import crud, db


def registry_router_factory(fetcher: RegistryFetcher) -> APIRouter:
    router = APIRouter()

    @router.get("/entities", response_model=list[schemas.EntityInDb])
    async def get_entities(
        offset: int = 0, limit: int = 10, db_session: Session = Depends(db.get_db)
    ):
        return crud.get_entities(offset=offset, limit=limit, db=db_session)

    @router.get("/entities/$count")
    async def get_entities_count(db_session: Session = Depends(db.get_db)) -> int:
        return crud.get_entities_count(db=db_session)

    @router.post("/entities", response_model=schemas.EntityInDb)
    async def create_entity(
        entity: schemas.EntityCreate, db_session: Session = Depends(db.get_db)
    ):
        return fetcher.register_entity(entity, db_session=db_session)

    @router.get("/entities/{uri}", response_model=schemas.EntityInDb)
    async def get_entity(uri: str, db_session: Session = Depends(db.get_db)):
        entity = crud.get_entity(uri, db=db_session)
        if entity is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Entity not found"
            )
        return entity

    @router.put("/entities/{uri}", response_model=schemas.EntityInDb)
    async def update_entity(
        uri: str,
        entity: schemas.EntityUpdate,
        override: bool = False,
        db_session: Session = Depends(db.get_db),
    ):
        if uri != entity.uri:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URI mismatch",
            )
        return fetcher.update_entity(entity, override=override, db_session=db_session)

    @router.delete("/entities/{uri}", response_model=bool)
    async def delete_entity(uri: str, db_session: Session = Depends(db.get_db)):
        return fetcher.delete_entity(uri, db_session=db_session)

    return router
