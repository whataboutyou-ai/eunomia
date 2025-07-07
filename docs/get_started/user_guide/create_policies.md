To enforce access control, you need to create policies that specify the rules for granting or denying actions. In general, a policy is a collection of rules that define under which conditions a principal is allowed to perform an action on a resource based on their attributes.

## Create a Policy

You can create policies using the **`POST /admin/policies/simple`** endpoint. The policy will be stored in the database specified in the **`ENGINE_SQL_DATABASE_URL`** environment variable.

Your request JSON payload should include a rule defined by the **`CheckRequest`** schema, which includes:

- **`principal`**: The conditions (attributes) that the principal performing the action must meet.
- **`resource`**: The conditions (attributes) that the resource being acted on must meet.
- **`action`**: (Optional) The action that the principal is trying to perform on the resource.

=== "Python"
    ```python
    from eunomia_core.schemas import CheckRequest, PrincipalCheck, ResourceCheck
    from eunomia_sdk import EunomiaClient

    eunomia = EunomiaClient()

    policy = eunomia.create_simple_policy(
        CheckRequest(
            principal=PrincipalCheck(attributes={"department": "it"}),
            resource=ResourceCheck(attributes={"agent-id": "it-desk-agent"}),
            action="access",
        ),
        name="it-desk-policy",
    )
    ```

    !!! info
        To use the Python SDK, check out its [documentation](../../api/sdks/python.md) for installation instructions.

=== "Curl"
    ```bash
    curl -X POST 'http://localhost:8000/admin/policies/simple?name=it-desk-policy' \
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
