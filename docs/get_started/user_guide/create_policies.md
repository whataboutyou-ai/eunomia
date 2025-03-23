To enforce access control, you need to create policies that specify the rules for granting or denying access. In general, a policy is a collection of rules that define under which conditions a principal is allowed to access a resource based on their attributes. 
 
There are two ways to define policies:

- **Via the API call:** Use the endpoint to create a policy from a JSON payload
- **Manually:** Write the policy directly in [Rego][rego-website] and place it in the `OPA_POLICY_FOLDER` directory

## Create a Policy via API call

You can create policies using the **`POST /create-policy`** endpoint. The policy you define will be converted into OPA Rego language and saved to your filesystem in the location specified by the response.

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


The generated Rego policy file will include rules similar to the following:

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

## Create a Policy manually

You can define your policies directly by creating Rego files in the `OPA_POLICY_FOLDER`. 
In this case, ensure that your Rego files start with `package eunomia` and include your `allow` (and optionally `deny`) rules appropriately.

[rego-website]: https://www.openpolicyagent.org/docs/latest/policy-language/
