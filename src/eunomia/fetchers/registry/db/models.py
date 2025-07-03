from datetime import datetime
from typing import Any

from eunomia_core import enums
from sqlalchemy import JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eunomia.fetchers.registry.db import db


class Entity(db.Base):
    __tablename__ = "entities"

    uri: Mapped[str] = mapped_column(primary_key=True)
    type: Mapped[enums.EntityType]
    registered_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationships
    attributes: Mapped[list["Attribute"]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )


class Attribute(db.Base):
    __tablename__ = "attributes"

    entity_uri: Mapped[str] = mapped_column(ForeignKey(Entity.uri), primary_key=True)
    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[Any] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    registered_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationships
    entity: Mapped["Entity"] = relationship(back_populates="attributes")
