from eunomia_core import schemas
from sqlalchemy.orm import Session

from eunomia.db import models


def create_entity(entity: schemas.EntityRequest, db: Session) -> models.Entity:
    """
    Create a new entity in the database.

    This function creates a new entity record and its associated attributes
    in the database.

    Parameters
    ----------
    entity : schemas.EntityRequest
        Pydantic model containing the entity data to be created.
    db : Session
        SQLAlchemy database session.

    Returns
    -------
    models.Entity
        The created entity as a SQLAlchemy model.
    """
    db_entity = models.Entity(
        uri=entity.uri,
        type=entity.type,
    )
    for attribute in entity.attributes:
        db_attribute = models.Attribute(
            key=attribute.key,
            value=attribute.value,
        )
        db_entity.attributes.append(db_attribute)

    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


def get_entity(uri: str, db: Session) -> models.Entity | None:
    """
    Retrieve an entity from the database by its unique identifier.

    Parameters
    ----------
    uri : str
        Unique identifier of the entity.
    db : Session
        SQLAlchemy database session.

    Returns
    -------
    models.Entity | None
        The entity as a SQLAlchemy model or None if it does not exist.
    """
    return db.query(models.Entity).filter(models.Entity.uri == uri).first()


def get_entity_attributes(uri: str, db: Session) -> dict:
    """
    Retrieve attributes for a resource by its unique identifier.

    This function retrieves all attributes associated with a specific resource
    and returns it as a dictionary.

    Parameters
    ----------
    uri : str
        Unique identifier of the entity.
    db : Session
        SQLAlchemy database session.

    Returns
    -------
    dict
        Dictionary containing all attributes key-value pairs for the entity.

    Raises
    ------
    ValueError
        If no entity with the specified uri is found.
    """
    db_entity = get_entity(uri, db)
    if db_entity is None:
        raise ValueError(f"Entity with uri '{uri}' not found.")
    return {attribute.key: attribute.value for attribute in db_entity.attributes}
