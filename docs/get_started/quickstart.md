After [installing Eunomia](installation.md), you can start using it by following this quickstart example.

## Access Control for Multi-Agent Architecture

Let's assume you have a multi-agent system where an orchestrator routes the user requests to one of the available agents that can perform a specific task. You want to allow a user to access only a specific set of the agents based on their attributes.

Particulary, let's say that access to the _IT Desk Agent_ is restricted to employess in the IT department, while access to the _HR Agent_ is restricted to managers in the HR department.

### Server Setup

Start the Eunomia server with:

```bash
eunomia server
```

### Policy Configuration

Now, you need to create a policy that will be used to enforce the access control. The policy will contain two rules:

1. Allow access to the resource with attributes `agent-id == it-desk-agent` to principals with the `department == it`.
2. Allow access to the resource with attributes `agent-id == hr-agent` to principals with the `department == hr` _AND_ the `role == manager`.

You can use the `POST /admin/policies/simple` endpoint for this.

=== "Python"
    ```python
    from eunomia_core.schemas import CheckRequest, PrincipalCheck, ResourceCheck
    from eunomia_sdk import EunomiaClient

    eunomia = EunomiaClient()

    eunomia.create_simple_policy(
        CheckRequest(
            principal=PrincipalCheck(attributes={"department": "it"}),
            resource=ResourceCheck(attributes={"agent-id": "it-desk-agent"}),
            action="access",
        ),
        name="it-desk-policy",
    )

    eunomia.create_simple_policy(
        CheckRequest(
            principal=PrincipalCheck(attributes={"department": "hr", "role": "manager"}),
            resource=ResourceCheck(attributes={"agent-id": "hr-agent"}),
            action="access",
        ),
        name="hr-policy",
    )
    ```

    !!! info
        To use the Python SDK, check out its [documentation](../api/sdks/python.md) for installation instructions.

=== "Curl"
    ```bash
    curl -X POST 'http://localhost:8000/admin/policies/simple?name=it-desk-policy' \
      -H "Content-Type: application/json" \
      -d '{"principal": {"attributes": {"department": "it"}}, "resource": {"attributes": {"agent-id": "it-desk-agent"}}, "action": "access"}'

    curl -X POST 'http://localhost:8000/admin/policies/simple?name=hr-policy' \
      -H "Content-Type: application/json" \
      -d '{"principal": {"attributes": {"department": "hr", "role": "manager"}}, "resource": {"attributes": {"agent-id": "hr-agent"}}, "action": "access"}'
    ```

=== "Output"
    ```json
    {
        "version": "1.0",
        "name":"it-desk-policy",
        "description": null,
        "rules":[
            {
                "name": "it-desk-policy",
                "effect": "allow",
                "principal_conditions": [{"path": "attributes.department", "operator": "==", "value": "it"}],
                "resource_conditions": [{"path": "attributes.agent-id", "operator": "==", "value": "it-desk-agent"}],
                "actions": ["access"]
            }
        ],
        "default_effect": "deny"
    }

    {
        "version": "1.0",
        "name":"hr-policy",
        "description": null,
        "rules":[
            {
                "name": "hr-policy",
                "effect": "allow",
                "principal_conditions": [{"path": "attributes.department", "operator": "==", "value": "hr"}, {"path": "attributes.role", "operator": "==", "value": "manager"}],
                "resource_conditions": [{"path": "attributes.agent-id", "operator": "==", "value": "hr-agent"}],
                "actions": ["access"]
            },
        ],
        "default_effect": "deny"
    }
    ```

### Policy Enforcement

Now, you can enforce the policies in your application at runtime by checking the access of a given principal to a specific resource.

You can use the `POST /check` endpoint for this, passing the principal and resource identifiers and their attributes.

=== "Python"
    ```python
    # allowed access
    eunomia.check(
        resource_attributes={"agent-id": "it-desk-agent"},
        principal_attributes={"department": "it"},
    )
    eunomia.check(
        resource_attributes={"agent-id": "hr-agent"},
        principal_attributes={"department": "hr", "role": "manager"},
    )
    # denied access
    eunomia.check(
        resource_attributes="it-desk-agent",
        principal_attributes={"department": "sales"},
    )
    eunomia.check(
        resource_attributes="hr-agent",
        principal_attributes={"department": "hr", "role": "analyst"},
    )
    ```

=== "Curl"
    ```bash
    # allowed access
    curl -X POST 'http://localhost:8000/check' -H "Content-Type: application/json" -d '{"resource": {"attributes": {"agent-id": "it-desk-agent"}}, "principal": {"attributes": {"department": "it"}}}'
    curl -X POST 'http://localhost:8000/check' -H "Content-Type: application/json" -d '{"resource": {"attributes": {"agent-id": "hr-agent"}}, "principal": {"attributes": {"department": "hr", "role": "manager"}}}'
    # denied access
    curl -X POST 'http://localhost:8000/check' -H "Content-Type: application/json" -d '{"resource": {"attributes": {"agent-id": "it-desk-agent"}}, "principal": {"attributes": {"department": "sales"}}}'
    curl -X POST 'http://localhost:8000/check' -H "Content-Type: application/json" -d '{"resource": {"attributes": {"agent-id": "hr-agent"}}, "principal": {"attributes": {"department": "hr", "role": "analyst"}}}'
    ```

=== "Output"
    ```bash
    # allowed access
    {"allowed":true, "reason":"Rule it-desk-policy allowed the action in policy it-desk-policy"}
    {"allowed":true, "reason":"Rule hr-policy allowed the action in policy hr-policy"}
    # denied access
    {"allowed":false, "reason":"Action denied by default effect"}
    {"allowed":false, "reason":"Action denied by default effect"}
    ```

Congratulations! You've just made your first steps with Eunomia.

You can now explore the [user guide](user_guide/index.md) to learn more about Eunomia or explore the [API documentation](../api/index.md) for more details on how to use Eunomia in your application.
