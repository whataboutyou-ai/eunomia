from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from eunomia.db import models, schemas


def create_resource(
    resource_create: schemas.ResourceCreate, eunomia_id: str, db: Session
) -> schemas.Resource:
    """
    Create a new resource in the database.

    This function creates a new resource record and its associated metadata
    in the database.

    Parameters
    ----------
    resource_create : schemas.ResourceCreate
        Pydantic model containing the resource data to be created.
    eunomia_id : str
        Unique identifier for the resource.
    db : Session
        SQLAlchemy database session.

    Returns
    -------
    schemas.Resource
        The created resource as a Pydantic model, including its ID and registration timestamp.
    """
    db_resource = models.Resource(
        eunomia_id=eunomia_id,
        content=resource_create.content,
        registered_at=datetime.now(),
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)

    # add metadata
    for key, value in resource_create.metadatas.items():
        _ = _create_resource_metadata(db_resource.id, key, str(value), db)

    doc_schema = schemas.Resource(
        id=db_resource.id,
        registered_at=db_resource.registered_at,
        **resource_create.model_dump(),
    )
    return doc_schema


def _create_resource_metadata(
    resource_id: int, key: str, value: str, db: Session
) -> models.ResourceMetadata:
    db_doc_metadata = models.ResourceMetadata(
        resource_id=resource_id, key=key, value=value
    )
    db.add(db_doc_metadata)
    db.commit()
    db.refresh(db_doc_metadata)
    return db_doc_metadata


def create_principal(
    principal_create: schemas.PrincipalCreate, eunomia_id: str, db: Session
) -> schemas.Principal:
    """
    Create a new principal in the database.

    This function creates a new principal record and its associated metadata
    in the database.

    Parameters
    ----------
    principal_create : schemas.PrincipalCreate
        Pydantic model containing the principal data to be created.
    eunomia_id : str
        Unique identifier for the principal.
    db : Session
        SQLAlchemy database session.

    Returns
    -------
    schemas.Principal
        The created principal as a Pydantic model, including its ID and registration timestamp.
    """
    db_principal = models.Principal(
        eunomia_id=eunomia_id,
        registered_at=datetime.now(),
    )
    db.add(db_principal)
    db.commit()
    db.refresh(db_principal)

    # add metadata
    for key, value in principal_create.metadatas.items():
        _ = _create_principal_metadata(db_principal.id, key, str(value), db)

    doc_schema = schemas.Principal(
        id=db_principal.id,
        registered_at=db_principal.registered_at,
        **principal_create.model_dump(),
    )
    return doc_schema


def _create_principal_metadata(
    principal_id: int, key: str, value: str, db: Session
) -> models.PrincipalMetadata:
    db_doc_metadata = models.PrincipalMetadata(
        principal_id=principal_id, key=key, value=value
    )
    db.add(db_doc_metadata)
    db.commit()
    db.refresh(db_doc_metadata)
    return db_doc_metadata


def get_resource_metadata(eunomia_id: str, db: Session) -> dict:
    """
    Retrieve metadata for a resource by its unique identifier.

    This function retrieves all metadata associated with a specific resource
    and returns it as a dictionary.

    Parameters
    ----------
    eunomia_id : str
        Unique identifier of the resource.
    db : Session
        SQLAlchemy database session.

    Returns
    -------
    dict
        Dictionary containing all metadata key-value pairs for the resource.

    Raises
    ------
    ValueError
        If no resource with the specified eunomia_id is found.
    """
    stmt = select(models.Resource).where(models.Resource.eunomia_id == eunomia_id)
    resource = db.scalars(stmt).first()

    if not resource:
        raise ValueError("Resource not found.")

    metadata_dict = {
        metadata.key: metadata.value for metadata in resource.resources_metadatas
    }
    return metadata_dict


def get_principal_metadata(eunomia_id: str, db: Session) -> dict:
    """
    Retrieve metadata for a principal by its unique identifier.

    This function retrieves all metadata associated with a specific principal
    and returns it as a dictionary.

    Parameters
    ----------
    eunomia_id : str
        Unique identifier of the principal.
    db : Session
        SQLAlchemy database session.

    Returns
    -------
    dict
        Dictionary containing all metadata key-value pairs for the principal.

    Raises
    ------
    ValueError
        If no principal with the specified eunomia_id is found.
    """
    stmt = select(models.Principal).where(models.Principal.eunomia_id == eunomia_id)
    resource = db.scalars(stmt).first()

    if not resource:
        raise ValueError("Principal not found.")

    metadata_dict = {
        metadata.key: metadata.value for metadata in resource.principals_metadatas
    }
    return metadata_dict
