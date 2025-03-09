import secrets
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select

from eunomia.db import db, models, schemas


def create_resource(
    resource_create: schemas.ResourceCreate, eunomia_id: str, db: Session
) -> schemas.Resource:
    """Create a new resource in db"""
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
    """Create a new resource in db"""
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
    """Given a eunomia_id for a Resource, this function returns its associated metadata as a dictionary, where each key is the metadata key and each value is the metadata value."""
    stmt = select(models.Resource).where(models.Resource.eunomia_id == eunomia_id)
    resource = db.scalars(stmt).first()

    if not resource:
        raise ValueError("Resource not found.")

    metadata_dict = {metadata.key: metadata.value for metadata in resource.resources_metadatas}
    return metadata_dict

def get_principal_metadata(eunomia_id: str, db: Session) -> dict:
    """Given a eunomia_id for a Principal, this function returns its associated metadata as a dictionary, where each key is the metadata key and each value is the metadata value."""
    stmt = select(models.Principal).where(models.Principal.eunomia_id == eunomia_id)
    resource = db.scalars(stmt).first()

    if not resource:
        raise ValueError("Principal not found.")

    metadata_dict = {metadata.key: metadata.value for metadata in resource.principals_metadatas}
    return metadata_dict