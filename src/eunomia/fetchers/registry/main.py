from eunomia_core import schemas
from sqlalchemy.orm import Session

from eunomia.fetchers.base import BaseFetcher, BaseFetcherConfig
from eunomia.fetchers.registry.db import crud, db


class RegistryFetcherConfig(BaseFetcherConfig):
    sql_database_url: str


class RegistryFetcher(BaseFetcher):
    config: RegistryFetcherConfig

    def __init__(self, config: RegistryFetcherConfig):
        super().__init__(config)
        db.init_db(self.config.sql_database_url)

    def get_entity(self, uri: str) -> schemas.EntityInDb | None:
        with db.SessionLocal() as db_session:
            db_entity = crud.get_entity(uri, db=db_session)
            if db_entity is not None:
                return schemas.EntityInDb.model_validate(db_entity)
            return None

    def register_entity(
        self, entity: schemas.EntityCreate, db_session: Session
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
        db_session : Session
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
        db_entity = crud.get_entity(entity.uri, db=db_session)
        if db_entity is not None:
            raise ValueError(f"Entity with uri '{entity.uri}' is already registered")

        db_entity = crud.create_entity(entity, db=db_session)
        return schemas.EntityInDb.model_validate(db_entity)

    def update_entity(
        self, entity: schemas.EntityUpdate, override: bool, db_session: Session
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
        db_session : Session
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
        db_entity = crud.get_entity(entity.uri, db=db_session)
        if db_entity is None:
            raise ValueError(f"Entity with uri '{entity.uri}' is not registered")

        if override:
            crud.delete_entity_attributes(db_entity, db=db_session)

        db_entity = crud.update_entity_attributes(
            db_entity, entity.attributes, db=db_session
        )
        return schemas.EntityInDb.model_validate(db_entity)

    def delete_entity(self, uri: str, db_session: Session) -> None:
        """
        Delete an entity from the system.

        Parameters
        ----------
        uri : str
            The uri of the entity to delete.
        db_session : Session
            The SQLAlchemy database session.


        Raises
        ------
        ValueError
            If the entity is not registered.
        """
        db_entity = crud.get_entity(uri, db=db_session)
        if db_entity is None:
            raise ValueError(f"Entity with uri '{uri}' is not registered")

        return crud.delete_entity(db_entity, db=db_session)

    async def fetch_attributes(self, uri: str) -> dict:
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
            db_entity = crud.get_entity(uri, db=db_session)
            if db_entity is None:
                return {}

            entity = schemas.EntityInDb.model_validate(db_entity)
            return entity.attributes_dict
