from eunomia_core.schemas import (
    AccessRequest,
    EntityType,
    PrincipalAccess,
    ResourceAccess,
)

from eunomia.engine import PolicyEngine, models, utils


def role_based_access_example():
    """Example of role-based access control policies."""

    # Create a policy engine
    engine = PolicyEngine()

    # Add an admin policy
    admin_policy = utils.create_simple_policy(
        name="admin-access",
        description="Administrators can access all resources",
        principal_attributes={"role": "admin"},
        effect=models.PolicyEffect.ALLOW,
    )
    engine.add_policy(admin_policy)

    # Add a more specific policy with conditions
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

    # Create an access request for admin user
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

    # Evaluate the admin request
    admin_result = engine.evaluate_all(admin_request)
    print(
        f"Admin accessing private resource: {admin_result.effect}"
        + (
            f" from rule {admin_result.matched_rule.description}"
            if admin_result.matched_rule
            else " from default"
        )
    )

    # Create an access request for read-only user with public resource
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

    # Evaluate the read-only request with public resource
    readonly_public_result = engine.evaluate_all(readonly_public_request)
    print(
        f"Read-only user accessing public resource: {readonly_public_result.effect}"
        + (
            f" from rule {readonly_public_result.matched_rule.description}"
            if readonly_public_result.matched_rule
            else " from default"
        )
    )

    # Create an access request for read-only user with private resource
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

    # Evaluate the read-only request with private resource
    readonly_private_result = engine.evaluate_all(readonly_private_request)
    print(
        f"Read-only user accessing private resource: {readonly_private_result.effect}"
        + (
            f" from rule {readonly_private_result.matched_rule.description}"
            if readonly_private_result.matched_rule
            else " from default"
        )
    )


if __name__ == "__main__":
    role_based_access_example()
