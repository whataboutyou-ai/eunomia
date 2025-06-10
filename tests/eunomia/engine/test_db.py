from eunomia_core import enums, schemas
from sqlalchemy.orm import Session

from eunomia.engine.db import crud


def test_create_and_get_policy(fixture_db: Session):
    policy = schemas.Policy(
        version="1.0",
        name="test-db-policy",
        description="Test database policy",
        rules=[
            schemas.Rule(
                name="test-rule",
                effect=enums.PolicyEffect.ALLOW,
                principal_conditions=[
                    schemas.Condition(
                        path="attributes.role",
                        operator=enums.ConditionOperator.EQUALS,
                        value="admin",
                    )
                ],
                resource_conditions=[],
                actions=["access"],
            )
        ],
        default_effect=enums.PolicyEffect.DENY,
    )

    # Create policy
    db_policy = crud.create_policy(policy, fixture_db)
    assert db_policy is not None
    assert db_policy.name == "test-db-policy"

    # Get policy
    retrieved_policy = crud.get_policy("test-db-policy", fixture_db)
    assert retrieved_policy is not None
    assert retrieved_policy.name == "test-db-policy"

    # Get all policies
    all_policies = crud.get_all_policies(fixture_db)
    assert len(all_policies) == 1
    assert all_policies[0].name == "test-db-policy"


def test_delete_policy(fixture_db: Session):
    policy = schemas.Policy(
        version="1.0",
        name="policy-to-delete",
        description="Policy to be deleted",
        rules=[],
        default_effect=enums.PolicyEffect.DENY,
    )

    # Create and then delete
    crud.create_policy(policy, fixture_db)
    assert crud.delete_policy("policy-to-delete", fixture_db) is True

    # Verify deletion
    assert crud.get_policy("policy-to-delete", fixture_db) is None
    assert len(crud.get_all_policies(fixture_db)) == 0

    # Try to delete non-existent policy
    assert crud.delete_policy("non-existent", fixture_db) is False


def test_db_policy_to_schema(fixture_db: Session):
    original_policy = schemas.Policy(
        version="1.0",
        name="conversion-test",
        description="Test conversion between DB and schema",
        rules=[
            schemas.Rule(
                name="test-rule",
                effect=enums.PolicyEffect.ALLOW,
                principal_conditions=[
                    schemas.Condition(
                        path="attributes.role",
                        operator=enums.ConditionOperator.EQUALS,
                        value="admin",
                    )
                ],
                resource_conditions=[
                    schemas.Condition(
                        path="attributes.type",
                        operator=enums.ConditionOperator.EQUALS,
                        value={"foo": {"bar": 123}},
                    ),
                    schemas.Condition(
                        path="attributes.list",
                        operator=enums.ConditionOperator.CONTAINS,
                        value=[1, 2, "foo", "bar"],
                    ),
                ],
                actions=["read", "write"],
            )
        ],
        default_effect=enums.PolicyEffect.DENY,
    )

    # Create policy in DB
    db_policy = crud.create_policy(original_policy, fixture_db)

    # Convert back to schema
    schema_policy = schemas.Policy.model_validate(db_policy)

    # Verify conversion was correct
    assert schema_policy.name == original_policy.name
    assert schema_policy.description == original_policy.description
    assert schema_policy.default_effect == original_policy.default_effect
    assert len(schema_policy.rules) == len(original_policy.rules)

    # Check rule details
    schema_rule = schema_policy.rules[0]
    original_rule = original_policy.rules[0]
    assert schema_rule.effect == original_rule.effect
    assert sorted(schema_rule.actions) == sorted(original_rule.actions)
    assert len(schema_rule.principal_conditions) == len(
        original_rule.principal_conditions
    )
    assert len(schema_rule.resource_conditions) == len(
        original_rule.resource_conditions
    )

    # Check principal condition
    schema_principal_condition = schema_rule.principal_conditions[0]
    original_principal_condition = original_rule.principal_conditions[0]
    assert schema_principal_condition.path == original_principal_condition.path
    assert schema_principal_condition.operator == original_principal_condition.operator
    assert schema_principal_condition.value == original_principal_condition.value

    # Check resource condition
    schema_resource_condition = schema_rule.resource_conditions[0]
    original_resource_condition = original_rule.resource_conditions[0]
    assert schema_resource_condition.path == original_resource_condition.path
    assert schema_resource_condition.operator == original_resource_condition.operator
    assert schema_resource_condition.value == original_resource_condition.value
