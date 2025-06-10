import json

from eunomia_core import enums, schemas
from sqlalchemy.orm import Session

from eunomia.engine.db import models


def create_policy(policy: schemas.Policy, db: Session) -> models.Policy:
    """
    Create a new policy in the database.
    """
    if get_policy(policy.name, db) is not None:
        raise ValueError(f"Policy with name {policy.name} already exists")

    db_policy = models.Policy(
        version=policy.version,
        name=policy.name,
        description=policy.description,
        default_effect=policy.default_effect,
    )
    for rule in policy.rules:
        db_rule = models.Rule(
            name=rule.name, effect=rule.effect, actions=json.dumps(rule.actions)
        )

        for condition in rule.principal_conditions:
            db_condition = models.Condition(
                entity_type=enums.EntityType.principal,
                path=condition.path,
                operator=condition.operator,
                value=json.dumps(condition.value),
            )
            db_rule.principal_conditions.append(db_condition)

        for condition in rule.resource_conditions:
            db_condition = models.Condition(
                entity_type=enums.EntityType.resource,
                path=condition.path,
                operator=condition.operator,
                value=json.dumps(condition.value),
            )
            db_rule.resource_conditions.append(db_condition)

        db_policy.rules.append(db_rule)

    db.add(db_policy)
    db.commit()
    db.refresh(db_policy)
    return db_policy


def get_policy(name: str, db: Session) -> models.Policy | None:
    """
    Retrieve a policy from the database by its name.
    """
    return db.query(models.Policy).filter(models.Policy.name == name).first()


def get_all_policies(db: Session) -> list[models.Policy]:
    """
    Retrieve a list of policies from the database.
    """
    return db.query(models.Policy).all()


def delete_policy(name: str, db: Session) -> bool:
    """
    Delete a policy from the database.
    """
    db_policy = get_policy(name, db)
    if db_policy is None:
        return False

    db.delete(db_policy)
    db.commit()
    return True
