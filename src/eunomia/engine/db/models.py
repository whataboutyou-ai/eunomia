from datetime import datetime
from typing import Any, Optional

from eunomia_core import enums
from sqlalchemy import JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eunomia.engine.db import db


class Policy(db.Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[str]
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]]
    default_effect: Mapped[enums.PolicyEffect]
    registered_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationships
    rules: Mapped[list["Rule"]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )


class Rule(db.Base):
    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    policy_id: Mapped[int] = mapped_column(ForeignKey(Policy.id))
    effect: Mapped[enums.PolicyEffect]
    actions: Mapped[list[str]] = mapped_column(JSON)
    registered_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # relationships
    policy: Mapped["Policy"] = relationship(back_populates="rules")
    principal_conditions: Mapped[list["Condition"]] = relationship(
        foreign_keys="[Condition.rule_id, Condition.entity_type]",
        primaryjoin=f"and_(Rule.id==Condition.rule_id, Condition.entity_type=='{enums.EntityType.principal.value}')",
        cascade="all, delete-orphan",
        overlaps="resource_conditions",
    )
    resource_conditions: Mapped[list["Condition"]] = relationship(
        foreign_keys="[Condition.rule_id, Condition.entity_type]",
        primaryjoin=f"and_(Rule.id==Condition.rule_id, Condition.entity_type=='{enums.EntityType.resource.value}')",
        cascade="all, delete-orphan",
        overlaps="principal_conditions",
    )


class Condition(db.Base):
    __tablename__ = "conditions"

    id: Mapped[int] = mapped_column(primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey(Rule.id))
    entity_type: Mapped[enums.EntityType]
    path: Mapped[str]
    operator: Mapped[enums.ConditionOperator]
    value: Mapped[Any] = mapped_column(JSON)
    registered_at: Mapped[datetime] = mapped_column(server_default=func.now())
