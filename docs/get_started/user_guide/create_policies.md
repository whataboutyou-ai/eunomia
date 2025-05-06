To enforce access control, you need to create policies that specify the rules for granting or denying access. In general, a policy is a collection of rules that define under which conditions a principal is allowed to access a resource based on their attributes. 
 
## Create a Policy

You can create policies using the **`POST /create-policy`** endpoint. The policy will be stored in the database specified in the **`ENGINE_SQL_DATABASE_URL`** environment variable.

Your policy JSON payload should include a **`rules`** field, which is an array of rule objects. Each rule is defined by the **`AccessRequest`** schema, which includes:

- **`principal`**: Defines the conditions (attributes) that a principal must meet.
- **`resource`**: Specifies the target resource using its identifier.
- **`action`**: (Optional) The action to be performed (currently only `"allow"` is supported).

=== "Python"
    ```python
    from eunomia_core.schemas import AccessRequest, Policy, PrincipalAccess, ResourceAccess
    from eunomia_sdk_python import EunomiaClient

    eunomia = EunomiaClient()

    # Example policy: Two rules are defined for granting access based on principal attributes.
    policy = Policy(
        rules=[
            AccessRequest(
                principal=PrincipalAccess(attributes={"department": "it"}),
                resource=ResourceAccess(uri="it-desk-agent"),
            ),
            AccessRequest(
                principal=PrincipalAccess(attributes={"department": "hr", "role": "manager"}),
                resource=ResourceAccess(uri="hr-agent"),
            ),
        ],
    )

    eunomia.create_policy(policy)
    ```

    !!! info
        To use the Python SDK, check out its [documentation](../../api/sdks/python.md) for installation instructions.

=== "Curl"
    ```bash
    curl -X POST 'http://localhost:8000/create-policy' \
    -H "Content-Type: application/json" \
    -d '{"rules": [{"principal": {"attributes": {"department": "it"}}, "resource": {"uri": "it-desk-agent"}}, {"principal": {"attributes": {"department": "hr", "role": "manager"}}, "resource": {"uri": "hr-agent"}}]}'
    ```

=== "Output"
    ```json
    {
        "path": "/your-path/policies/policy.rego",
        "message": "Policy created successfully at path"
    }
    ```
