from eunomia_core import enums, schemas

from eunomia.engine import utils
from eunomia.engine.engine import PolicyEngine


def test_role_based_access(fixture_engine: PolicyEngine):
    """Test role-based access control policies."""
    admin_policy = utils.create_simple_policy(
        name="admin-access",
        description="Administrators can access all resources",
        principal_attributes={"role": "admin"},
        effect=enums.PolicyEffect.ALLOW,
    )
    fixture_engine.add_policy(admin_policy)

    read_only_policy = schemas.Policy(
        name="read-only-access",
        description="Users with read-only role can only access resources with 'public' visibility",
        rules=[
            schemas.Rule(
                effect=enums.PolicyEffect.ALLOW,
                principal_conditions=[
                    schemas.Condition(
                        path="attributes.role",
                        operator=enums.ConditionOperator.EQUALS,
                        value="read-only",
                    )
                ],
                resource_conditions=[
                    schemas.Condition(
                        path="attributes.visibility",
                        operator=enums.ConditionOperator.EQUALS,
                        value="public",
                    )
                ],
                actions=["access"],
            )
        ],
        default_effect=enums.PolicyEffect.DENY,
    )
    fixture_engine.add_policy(read_only_policy)

    admin_request = schemas.AccessRequest(
        principal=schemas.PrincipalAccess(
            type=enums.EntityType.principal,
            attributes={"role": "admin", "department": "engineering"},
        ),
        resource=schemas.ResourceAccess(
            type=enums.EntityType.resource,
            attributes={"name": "secret-project", "visibility": "private"},
        ),
        action="access",
    )

    admin_result = fixture_engine.evaluate_all(admin_request)
    assert admin_result.effect == enums.PolicyEffect.ALLOW
    assert admin_result.matched_rule is not None
    assert admin_result.policy_name == "admin-access"

    readonly_public_request = schemas.AccessRequest(
        principal=schemas.PrincipalAccess(
            type=enums.EntityType.principal,
            attributes={"role": "read-only", "department": "marketing"},
        ),
        resource=schemas.ResourceAccess(
            type=enums.EntityType.resource,
            attributes={"name": "public-dashboard", "visibility": "public"},
        ),
        action="access",
    )

    readonly_public_result = fixture_engine.evaluate_all(readonly_public_request)
    assert readonly_public_result.effect == enums.PolicyEffect.ALLOW
    assert readonly_public_result.matched_rule is not None
    assert readonly_public_result.policy_name == "read-only-access"

    readonly_private_request = schemas.AccessRequest(
        principal=schemas.PrincipalAccess(
            type=enums.EntityType.principal,
            attributes={"role": "read-only", "department": "marketing"},
        ),
        resource=schemas.ResourceAccess(
            type=enums.EntityType.resource,
            attributes={"name": "secret-project", "visibility": "private"},
        ),
        action="access",
    )

    readonly_private_result = fixture_engine.evaluate_all(readonly_private_request)
    assert readonly_private_result.effect == enums.PolicyEffect.DENY
    assert readonly_private_result.matched_rule is None
    assert readonly_private_result.policy_name == "read-only-access"
