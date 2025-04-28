from eunomia_core.schemas import (
    AccessRequest,
    EntityType,
    PrincipalAccess,
    ResourceAccess,
)

from eunomia.engine import PolicyEngine, models, utils


def test_role_based_access():
    """Test role-based access control policies."""
    engine = PolicyEngine()

    admin_policy = utils.create_simple_policy(
        name="admin-access",
        description="Administrators can access all resources",
        principal_attributes={"role": "admin"},
        effect=models.PolicyEffect.ALLOW,
    )
    engine.add_policy(admin_policy)

    read_only_policy = models.Policy(
        name="read-only-access",
        description="Users with read-only role can only access resources with 'public' visibility",
        rules=[
            models.PolicyRule(
                description="Allow read-only users to access public resources",
                effect=models.PolicyEffect.ALLOW,
                principal_conditions=[
                    models.Condition(
                        path="attributes.role",
                        operator=models.ConditionOperator.EQUALS,
                        value="read-only",
                    )
                ],
                resource_conditions=[
                    models.Condition(
                        path="attributes.visibility",
                        operator=models.ConditionOperator.EQUALS,
                        value="public",
                    )
                ],
                action="access",
            )
        ],
        default_effect=models.PolicyEffect.DENY,
    )
    engine.add_policy(read_only_policy)

    admin_request = AccessRequest(
        principal=PrincipalAccess(
            type=EntityType.principal,
            attributes={"role": "admin", "department": "engineering"},
        ),
        resource=ResourceAccess(
            type=EntityType.resource,
            attributes={"name": "secret-project", "visibility": "private"},
        ),
        action="access",
    )

    admin_result = engine.evaluate_all(admin_request)
    assert admin_result.effect == models.PolicyEffect.ALLOW
    assert admin_result.matched_rule is not None
    assert admin_result.policy_name == "admin-access"

    readonly_public_request = AccessRequest(
        principal=PrincipalAccess(
            type=EntityType.principal,
            attributes={"role": "read-only", "department": "marketing"},
        ),
        resource=ResourceAccess(
            type=EntityType.resource,
            attributes={"name": "public-dashboard", "visibility": "public"},
        ),
        action="access",
    )

    readonly_public_result = engine.evaluate_all(readonly_public_request)
    assert readonly_public_result.effect == models.PolicyEffect.ALLOW
    assert readonly_public_result.matched_rule is not None
    assert readonly_public_result.policy_name == "read-only-access"

    readonly_private_request = AccessRequest(
        principal=PrincipalAccess(
            type=EntityType.principal,
            attributes={"role": "read-only", "department": "marketing"},
        ),
        resource=ResourceAccess(
            type=EntityType.resource,
            attributes={"name": "secret-project", "visibility": "private"},
        ),
        action="access",
    )

    readonly_private_result = engine.evaluate_all(readonly_private_request)
    assert readonly_private_result.effect == models.PolicyEffect.DENY
    assert readonly_private_result.matched_rule is None
    assert readonly_private_result.policy_name == "read-only-access"
