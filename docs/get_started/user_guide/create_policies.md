To enforce access control, you need to create policies that specify the rules for granting or denying access. In general, a policy is a collection of rules that define under which conditions a principal is allowed to access a resource based on their attributes. 
 
## Create a Policy

You can create policies using the **`POST /policies`** endpoint. The policy will be stored in the database specified in the **`ENGINE_SQL_DATABASE_URL`** environment variable.

Your request JSON payload should include a rule defined by the **`AccessRequest`** schema, which includes:

- **`principal`**: The conditions (attributes) that the principal trying to access must meet.
- **`resource`**: The conditions (attributes) that the resource being accessed must meet.
- **`action`**: (Optional) The action that the principal is trying to perform on the resource.

=== "Python"
    ```python
    from eunomia_core.schemas import AccessRequest, PrincipalAccess, ResourceAccess
    from eunomia_sdk_python import EunomiaClient

    eunomia = EunomiaClient()

    policy = eunomia.create_policy(
        AccessRequest(
            principal=PrincipalAccess(attributes={"department": "it"}),
            resource=ResourceAccess(attributes={"agent-id": "it-desk-agent"}),
            action="access",
        ),
        name="it-desk-policy",
    )
    ```

    !!! info
        To use the Python SDK, check out its [documentation](../../api/sdks/python.md) for installation instructions.

=== "Curl"
    ```bash
    curl -X POST 'http://localhost:8000/policies?name=it-desk-policy' \
    -H "Content-Type: application/json" \
    -d '{"principal": {"attributes": {"department": "it"}}, "resource": {"attributes": {"agent-id": "it-desk-agent"}}, "action": "access"}'
    ```

=== "Output"
    ```json
    {
        "name":"it-desk-policy",
        "rules":[
            {
                "effect": "allow",
                "principal_conditions": [{"path": "attributes.department", "operator": "==", "value": "it"}],
                "resource_conditions": [{"path": "attributes.agent-id", "operator": "==", "value": "it-desk-agent"}],
                "actions": ["access"]
            },
        ],
        "default_effect": "deny"
    }
    ```
