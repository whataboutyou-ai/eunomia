import secrets
from datetime import datetime

from sqlalchemy.orm import Session

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
