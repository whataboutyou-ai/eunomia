After [installing Eunomia](installation.md), you can start using it by following this quickstart example.

## Access Control for Multi-Agent Architecture

Let's assume you have a multi-agent system where an orchestrator routes the user requests to one of the available agents that can perform a specific task. You want to allow a user to access only a specific set of the agents based on their attributes.

Particulary, let's say that access to the _IT Desk Agent_ is restricted to employess in the IT department, while access to the _HR Agent_ is restricted to managers in the HR department.

### Server Setup

First, copy the `.env.example` file to `.env` and set the `OPA_POLICY_FOLDER` variable to the path where you want to store the policies.

Then, let's start the Eunomia server with:

```bash
eunomia server
```

### Policy Configuration

Now, you need to create a policy that will be used to enforce the access control. The policy will contain two rules:

1. Allow access to the resource with identifier `it-desk-agent` to principals with the `department` attribute set to `it`.
2. Allow access to the resource with identifier `hr-agent` to principals with the `department` attribute set to `hr` _AND_ the `role` attribute set to `manager`.

You can use the `POST /create-policy` endpoint for this.

=== "Python"
    ```python
    from eunomia_core.schemas import AccessRequest, Policy, PrincipalAccess, ResourceAccess
    from eunomia_sdk_python import EunomiaClient

    eunomia = EunomiaClient()

    policy = Policy(
        rules=[
            AccessRequest(
                principal=PrincipalAccess(attributes={"department": "it"}),
                resource=ResourceAccess(uri="it-desk-agent"),
            ),
            AccessRequest(
                principal=PrincipalAccess(
                    attributes={"department": "hr", "role": "manager"}
                ),
                resource=ResourceAccess(uri="hr-agent"),
            ),
        ],
    )

    eunomia.create_policy(policy)
    ```

    !!! info
        To use the Python SDK, check out its [documentation](../api/sdks/python.md) for installation instructions.

=== "Curl"
    ```bash
    curl -X POST 'http://localhost:8000/create-policy' \
    -H "Content-Type: application/json" \
    -d '{"rules": [{"principal": {"attributes": {"department": "it"}}, "resource": {"uri": "it-desk-agent"}}, {"principal": {"attributes": {"department": "hr", "role": "manager"}}, "resource": {"uri": "hr-agent"}}]}'
    ```

=== "Output"
    ```json
    {
        "path":"/your-path/policies/policy.rego",
        "message":"Policy created successfully at path"
    }
    ```

The policy will be saved in your filesystem at the path specified in the response. The file will contain the translated policy in OPA Rego language:

```rego
package eunomia

default allow := false

allow if {
	input.principal.attributes.department == "it"
	input.resource.uri == "it-desk-agent"
}

allow if {
	input.principal.attributes.department == "hr"
	input.principal.attributes.role == "manager"
	input.resource.uri == "hr-agent"
}
```

### Policy Enforcement

Now, you can enforce the policies in your application at runtime by checking the access of a given principal to a specific resource.

You can use the `POST /check-access` endpoint for this, passing the principal and resource identifiers and their attributes.

=== "Python"
    ```python
    # allowed access
    eunomia.check_access(
        resource_uri="it-desk-agent", principal_attributes={"department": "it"}
    )
    eunomia.check_access(
        resource_uri="hr-agent",
        principal_attributes={"department": "hr", "role": "manager"},
    )

    # denied access
    eunomia.check_access(
        resource_uri="it-desk-agent", principal_attributes={"department": "sales"}
    )
    eunomia.check_access(
        resource_uri="hr-agent",
        principal_attributes={"department": "hr", "role": "analyst"},
    )
    ```

=== "Curl"
    ```bash
    curl -X POST 'http://localhost:8000/check-access' -H "Content-Type: application/json" -d '{"resource": {"uri": "it-desk-agent"}, "principal": {"attributes": {"department": "it"}}}'
    curl -X POST 'http://localhost:8000/check-access' -H "Content-Type: application/json" -d '{"resource": {"uri": "hr-agent"}, "principal": {"attributes": {"department": "hr", "role": "manager"}}}'
    curl -X POST 'http://localhost:8000/check-access' -H "Content-Type: application/json" -d '{"resource": {"uri": "it-desk-agent"}, "principal": {"attributes": {"department": "sales"}}}'
    curl -X POST 'http://localhost:8000/check-access' -H "Content-Type: application/json" -d '{"resource": {"uri": "hr-agent"}, "principal": {"attributes": {"department": "hr", "role": "analyst"}}}'
    ```

=== "Output"
    ```bash
    true
    true
    false
    false
    ```

Congratulations! You've just made your first steps with Eunomia.

You can now explore the [user guide](user_guide/index.md) to learn more about Eunomia or explore the [API documentation](../api/index.md) for more details on how to use Eunomia in your application.
