from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eunomia.db import db


class Resource(db.Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True)
    eunomia_id: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    registered_at: Mapped[datetime]

    # relationships
    resources_metadatas: Mapped[list["ResourceMetadata"]] = relationship(
        back_populates="resource"
    )


class ResourceMetadata(db.Base):
    __tablename__ = "resource_metadatas"

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey(Resource.id))
    key: Mapped[str]
    value: Mapped[str]

    # relationships
    resource: Mapped["Resource"] = relationship(back_populates="resources_metadatas")


class Principal(db.Base):
    __tablename__ = "principals"

    id: Mapped[int] = mapped_column(primary_key=True)
    eunomia_id: Mapped[str] = mapped_column(String, nullable=False)
    registered_at: Mapped[datetime]

    # relationships
    principals_metadatas: Mapped[list["PrincipalMetadata"]] = relationship(
        back_populates="principal"
    )


class PrincipalMetadata(db.Base):
    __tablename__ = "principal_metadatas"

    id: Mapped[int] = mapped_column(primary_key=True)
    principal_id: Mapped[int] = mapped_column(ForeignKey(Principal.id))
    key: Mapped[str]
    value: Mapped[str]

    # relationships
    principal: Mapped["Principal"] = relationship(back_populates="principals_metadatas")
