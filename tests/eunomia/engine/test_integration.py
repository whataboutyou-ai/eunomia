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
        version="1.0",
        name="read-only-access",
        description="Users with read-only role can only access resources with 'public' visibility",
        rules=[
            schemas.Rule(
                name="read-only-rule",
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

    admin_request = schemas.CheckRequest(
        principal=schemas.PrincipalCheck(
            type=enums.EntityType.principal,
            attributes={"role": "admin", "department": "engineering"},
        ),
        resource=schemas.ResourceCheck(
            type=enums.EntityType.resource,
            attributes={"name": "secret-project", "visibility": "private"},
        ),
        action="access",
    )

    admin_result = fixture_engine.evaluate_all(admin_request)
    assert admin_result.allowed is True
    assert "admin-access" in admin_result.reason

    readonly_public_request = schemas.CheckRequest(
        principal=schemas.PrincipalCheck(
            type=enums.EntityType.principal,
            attributes={"role": "read-only", "department": "marketing"},
        ),
        resource=schemas.ResourceCheck(
            type=enums.EntityType.resource,
            attributes={"name": "public-dashboard", "visibility": "public"},
        ),
        action="access",
    )

    readonly_public_result = fixture_engine.evaluate_all(readonly_public_request)
    assert readonly_public_result.allowed is True
    assert "read-only-access" in readonly_public_result.reason

    readonly_private_request = schemas.CheckRequest(
        principal=schemas.PrincipalCheck(
            type=enums.EntityType.principal,
            attributes={"role": "read-only", "department": "marketing"},
        ),
        resource=schemas.ResourceCheck(
            type=enums.EntityType.resource,
            attributes={"name": "secret-project", "visibility": "private"},
        ),
        action="access",
    )

    readonly_private_result = fixture_engine.evaluate_all(readonly_private_request)
    assert readonly_private_result.allowed is False
