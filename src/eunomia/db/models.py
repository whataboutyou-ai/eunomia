from datetime import datetime

from eunomia_core.enums import EntityType
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eunomia.db import db


class Entity(db.Base):
    __tablename__ = "entities"

    uri: Mapped[str] = mapped_column(primary_key=True)
    type: Mapped[EntityType]
    registered_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationships
    attributes: Mapped[list["Attribute"]] = relationship(
        back_populates="entity", cascade="all, delete-orphan"
    )


class Attribute(db.Base):
    __tablename__ = "attributes"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_uri: Mapped[str] = mapped_column(ForeignKey(Entity.uri))
    key: Mapped[str]
    value: Mapped[str]
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    registered_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationships
    entity: Mapped["Entity"] = relationship(back_populates="attributes")
