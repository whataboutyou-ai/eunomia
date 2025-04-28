import json

from sqlalchemy.orm import Session

from eunomia.engine import schemas
from eunomia.engine.db import models


def create_policy(policy: schemas.Policy, db: Session) -> models.Policy:
    """
    Create a new policy in the database.
    """
    db_policy = models.Policy(
        name=policy.name,
        description=policy.description,
        default_effect=policy.default_effect,
    )
    for rule in policy.rules:
        db_rule = models.Rule(effect=rule.effect, actions=json.dumps(rule.actions))

        for condition in rule.principal_conditions:
            db_condition = models.Condition(
                entity_type="principal",
                path=condition.path,
                operator=condition.operator,
                value=json.dumps(condition.value),
            )
            db_rule.principal_conditions.append(db_condition)

        for condition in rule.resource_conditions:
            db_condition = models.Condition(
                entity_type="resource",
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


def db_policy_to_schema(db_policy: models.Policy) -> schemas.Policy:
    # TODO: include in the schema
    rules = []
    for db_rule in db_policy.rules:
        principal_conditions = [
            schemas.Condition(
                path=db_condition.path,
                operator=db_condition.operator,
                value=json.loads(db_condition.value),
            )
            for db_condition in db_rule.principal_conditions
        ]

        resource_conditions = [
            schemas.Condition(
                path=db_condition.path,
                operator=db_condition.operator,
                value=json.loads(db_condition.value),
            )
            for db_condition in db_rule.resource_conditions
        ]

        rule = schemas.Rule(
            effect=db_rule.effect,
            actions=json.loads(db_rule.actions),
            principal_conditions=principal_conditions,
            resource_conditions=resource_conditions,
        )
        rules.append(rule)

    return schemas.Policy(
        name=db_policy.name,
        description=db_policy.description,
        default_effect=db_policy.default_effect,
        rules=rules,
    )
