from datetime import datetime
from typing import Optional

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eunomia.db import db


class Resource(db.Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    registered_at: Mapped[datetime]

    # relationships
    metadatas: Mapped[list["ResourceMetadata"]] = relationship(
        back_populates="resource"
    )


class ResourceMetadata(db.Base):
    __tablename__ = "resource_metadatas"

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey(Resource.id))
    key: Mapped[str]
    value: Mapped[str]

    # relationships
    resource: Mapped["Resource"] = relationship(back_populates="metadatas")
