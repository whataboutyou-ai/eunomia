from eunomia_core.schemas import (
    AccessRequest,
    Attribute,
    EntityType,
    PrincipalAccess,
    ResourceAccess,
)

from eunomia.engine.internal import PolicyEngine, models, utils


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
                        path="attributes",
                        operator=models.ConditionOperator.EQUALS,
                        value={"key": "role", "value": "read-only"},
                    )
                ],
                resource_conditions=[
                    models.Condition(
                        path="attributes",
                        operator=models.ConditionOperator.EQUALS,
                        value={"key": "visibility", "value": "public"},
                    )
                ],
                action="allow",
            )
        ],
        default_effect=models.PolicyEffect.DENY,
    )
    engine.add_policy(read_only_policy)

    # Create an access request for admin user
    admin_request = AccessRequest(
        principal=PrincipalAccess(
            type=EntityType.principal,
            attributes=[
                Attribute(key="role", value="admin"),
                Attribute(key="department", value="engineering"),
            ],
        ),
        resource=ResourceAccess(
            type=EntityType.resource,
            attributes=[
                Attribute(key="name", value="secret-project"),
                Attribute(key="visibility", value="private"),
            ],
        ),
        action="allow",
    )

    # Evaluate the admin request
    admin_result = engine.evaluate_all(admin_request)
    print(f"Admin accessing private resource: {admin_result.effect}")

    # Create an access request for read-only user with public resource
    readonly_public_request = AccessRequest(
        principal=PrincipalAccess(
            type=EntityType.principal,
            attributes=[
                Attribute(key="role", value="read-only"),
                Attribute(key="department", value="marketing"),
            ],
        ),
        resource=ResourceAccess(
            type=EntityType.resource,
            attributes=[
                Attribute(key="name", value="public-dashboard"),
                Attribute(key="visibility", value="public"),
            ],
        ),
        action="allow",
    )

    # Evaluate the read-only request with public resource
    readonly_public_result = engine.evaluate_all(readonly_public_request)
    print(f"Read-only user accessing public resource: {readonly_public_result.effect}")

    # Create an access request for read-only user with private resource
    readonly_private_request = AccessRequest(
        principal=PrincipalAccess(
            type=EntityType.principal,
            attributes=[
                Attribute(key="role", value="read-only"),
                Attribute(key="department", value="marketing"),
            ],
        ),
        resource=ResourceAccess(
            type=EntityType.resource,
            attributes=[
                Attribute(key="name", value="secret-project"),
                Attribute(key="visibility", value="private"),
            ],
        ),
        action="allow",
    )

    # Evaluate the read-only request with private resource
    readonly_private_result = engine.evaluate_all(readonly_private_request)
    print(
        f"Read-only user accessing private resource: {readonly_private_result.effect}"
    )


if __name__ == "__main__":
    role_based_access_example()
