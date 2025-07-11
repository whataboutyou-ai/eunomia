import json

from eunomia_core import schemas
from sqlalchemy.orm import Session, joinedload

from eunomia.fetchers.registry.db import models


def create_entity(entity: schemas.EntityCreate, db: Session) -> models.Entity:
    """
    Create a new entity in the database.

    This function creates a new entity record and its associated attributes
    in the database.

    Parameters
    ----------
    entity : schemas.EntityCreate
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
            key=attribute.key, value=json.dumps(attribute.value)
        )
        db_entity.attributes.append(db_attribute)

    db.add(db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


def update_entity_attributes(
    db_entity: models.Entity, attributes: list[schemas.Attribute], db: Session
) -> models.Entity:
    """
    Update the attributes of an existing entity.

    This function updates the attributes of an existing entity.
    If an attribute does not exist, it is created.
    If an attribute exists, it is updated.

    Parameters
    ----------
    db_entity : models.Entity
        The entity to update.
    attributes : list[schemas.Attribute]
        The attributes to update.
    db : Session
        SQLAlchemy database session.

    Returns
    -------
    models.Entity
        The updated entity as a SQLAlchemy model.
    """
    for attribute in attributes:
        db_attribute = get_attribute(db_entity.uri, attribute.key, db)
        if db_attribute is not None:
            db_attribute.value = attribute.value
        else:
            db_attribute = models.Attribute(
                key=attribute.key, value=json.dumps(attribute.value)
            )
            db_entity.attributes.append(db_attribute)

    db.commit()
    db.refresh(db_entity)
    return db_entity


def delete_entity(db_entity: models.Entity, db: Session) -> bool:
    """
    Delete an entity from the database.

    This function deletes an entity record and its associated attributes
    from the database.

    Parameters
    ----------
    db_entity : models.Entity
        The entity to delete.
    db : Session
        SQLAlchemy database session.

    Returns
    -------
    bool
        True if the entity was deleted successfully, False otherwise.
    """
    delete_entity_attributes(db_entity, db)
    db.delete(db_entity)
    db.commit()
    return True


def delete_entity_attributes(db_entity: models.Entity, db: Session) -> None:
    """
    Delete all attributes of an entity.

    Parameters
    ----------
    db_entity : models.Entity
        The entity to delete attributes from.
    db : Session
        SQLAlchemy database session.
    """
    db.query(models.Attribute).filter(
        models.Attribute.entity_uri == db_entity.uri
    ).delete()
    db.commit()


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


def get_entities_count(db: Session) -> int:
    """
    Retrieve the total number of entities in the database.

    Parameters
    ----------
    db : Session
        SQLAlchemy database session.

    Returns
    -------
    int
        The total number of entities in the database.
    """
    return db.query(models.Entity).count()


def get_entities(offset: int, limit: int, db: Session) -> list[models.Entity]:
    """
    Retrieve a list of entities from the database.

    Parameters
    ----------
    offset : int
        The number of entities to skip.
    limit : int
        The number of entities to retrieve.
    db : Session
        SQLAlchemy database session.

    Returns
    -------
    list[models.Entity]
        A list of entities with their attributes eagerly loaded.
    """
    return (
        db.query(models.Entity)
        .options(joinedload(models.Entity.attributes))
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_attribute(uri: str, key: str, db: Session) -> models.Attribute | None:
    """
    Retrieve an attribute from the database by its key and entity uri.

    Parameters
    ----------
    uri : str
        The uri of the entity.
    key : str
        The key of the attribute.
    db : Session
        SQLAlchemy database session.

    Returns
    -------
    models.Attribute | None
        The attribute as a SQLAlchemy model or None if it does not exist.
    """
    return (
        db.query(models.Attribute)
        .filter(models.Attribute.entity_uri == uri, models.Attribute.key == key)
        .first()
    )
