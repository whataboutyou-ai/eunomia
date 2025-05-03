from eunomia_core import schemas
from sqlalchemy.orm import Session

from eunomia.fetchers.base import BaseFetcher, BaseFetcherConfig
from eunomia.fetchers.internal.db import crud, db


class InternalFetcherConfig(BaseFetcherConfig):
    SQL_DATABASE_URL: str


class InternalFetcher(BaseFetcher):
    def __init__(self, config: InternalFetcherConfig):
        self._config = config
        db.init_db(self._config.SQL_DATABASE_URL)

    def register_entity(
        self, entity: schemas.EntityCreate, db: Session
    ) -> schemas.EntityInDb:
        """
        Register a new entity in the system.

        Creates a new entity with the provided attributes,
        generating a unique identifier for future reference,
        if not provided.

        Parameters
        ----------
        entity : schemas.EntityCreate
            Pydantic model containing attributes about the entity.
        db : Session
            The SQLAlchemy database session.

        Returns
        -------
        schemas.EntityInDb
            The generated entity as a Pydantic model.

        Raises
        ------
        ValueError
            If the entity is already registered.
        """
        db_entity = crud.get_entity(entity.uri, db=db)
        if db_entity is not None:
            raise ValueError(f"Entity with uri '{entity.uri}' is already registered")

        db_entity = crud.create_entity(entity, db=db)
        return schemas.EntityInDb.model_validate(db_entity)

    def update_entity(
        self, entity: schemas.EntityUpdate, override: bool, db: Session
    ) -> schemas.EntityInDb:
        """
        Update the attributes of an existing entity.

        Parameters
        ----------
        entity : schemas.EntityUpdate
            The entity to update, with its identifier and the attributes to update.
        override : bool
            If True, the existing attributes are deleted and the new attributes are added.
            If False, the existing attributes are maintaned or updated in case of overlap,
            and the additional new attributes are added.
        db : Session
            The SQLAlchemy database session.

        Returns
        -------
        schemas.EntityInDb
            The updated entity as a Pydantic model.

        Raises
        ------
        ValueError
            If the entity is not registered.
        """
        db_entity = crud.get_entity(entity.uri, db=db)
        if db_entity is None:
            raise ValueError(f"Entity with uri '{entity.uri}' is not registered")

        if override:
            crud.delete_entity_attributes(db_entity, db=db)

        db_entity = crud.update_entity_attributes(db_entity, entity.attributes, db=db)
        return schemas.EntityInDb.model_validate(db_entity)

    def delete_entity(self, uri: str, db: Session) -> None:
        """
        Delete an entity from the system.

        Parameters
        ----------
        uri : str
            The uri of the entity to delete.
        db : Session
            The SQLAlchemy database session.


        Raises
        ------
        ValueError
            If the entity is not registered.
        """
        db_entity = crud.get_entity(uri, db=db)
        if db_entity is None:
            raise ValueError(f"Entity with uri '{uri}' is not registered")

        return crud.delete_entity(db_entity, db=db)

    def fetch_attributes(self, uri: str) -> dict:
        """
        Fetch the attributes of an entity.

        Parameters
        ----------
        uri : str
            The uri of the entity to fetch the attributes of.

        Returns
        -------
        dict
            The attributes of the entity.
        """
        with db.SessionLocal() as db_session:
            return crud.get_entity_attributes(uri, db=db_session)
