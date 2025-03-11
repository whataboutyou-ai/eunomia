After [installing Eunomia](installation.md), you can start using it by following this quickstart example.

## Access control for multi-agent architecture

Let's assume you have a multi-agent system where an orchestrator routes the user requests to one of the agents that can perform a specific task. You want to allow a user to access only a specific set of the agents based on their attributes.

You first need to **configure** the policies with the Eunomia server. Then, you need to connect your application to the Eunomia server in order to **enforce** the policies at runtime.

### Configuration

#### Policy definition

First, you need to configure the policies with the Eunomia server. You can write the policies in a file using [Rego][rego-docs].

Create a `policies/agents.rego` file:

```rego
package eunomia

default allow := false

allow if {
    # allow anyone to access faq agent
    input.resource.metadata.agent_id == "faq"
}

allow if {
    # allow hr department to access hr agent
    input.principal.metadata.department == "hr"
    input.resource.metadata.agent_id == "hr"
}
```

Then copy the `env.example` file to `.env` and set the `OPA_POLICY_PATH` variable to the path of the `policies/` folder.

#### Register resources and principals

You can now start the Eunomia server:

```bash
fastapi dev src/eunomia/api/main.py
```

Register the resources and principals you want to use with the Eunomia server (to use the Python SDK, check out its [documentation](../sdks/python.md) for installation instructions):

=== "Python"
    ```python
    from eunomia_sdk_python import EunomiaClient
    
    eunomia = EunomiaClient()

    eunomia.register_resource(metadatas={"agent_id": "faq"})
    eunomia.register_resource(metadatas={"agent_id": "hr"})
    eunomia.register_principal(metadatas={"department": "hr"})
    eunomia.register_principal(metadatas={"department": "sales"})
    ```

=== "Curl"
    ```bash
    curl -X POST http://localhost:8000/register_resource -H "Content-Type: application/json" -d '{"metadata": {"agent_id": "faq"}}'
    curl -X POST http://localhost:8000/register_resource -H "Content-Type: application/json" -d '{"metadata": {"agent_id": "hr"}}'
    curl -X POST http://localhost:8000/register_principal -H "Content-Type: application/json" -d '{"metadata": {"department": "hr"}}'
    curl -X POST http://localhost:8000/register_principal -H "Content-Type: application/json" -d '{"metadata": {"department": "sales"}}'
    ```

=== "Output"
    ```bash
    {"status": "success", "eunomia_id": "76d66319-cfb2-4f12-a30a-689dc9dd58b0"}
    {"status": "success", "eunomia_id": "e86e248b-2b51-4d34-abb3-3302c047cb72"}
    {"status": "success", "eunomia_id": "c194e9e4-1086-4d9b-89cb-2236e5158d36"}
    {"status": "success", "eunomia_id": "4f609741-7800-44f6-a1d6-640d6fe9bf01"}
    ```

### Enforcement

Now, you can enforce the policies in your application at runtime:

=== "Python"
    ```python
    from eunomia_sdk_python import EunomiaClient
    
    eunomia = EunomiaClient()

    faq_agent_id = "76d66319-cfb2-4f12-a30a-689dc9dd58b0"
    hr_agent_id = "e86e248b-2b51-4d34-abb3-3302c047cb72"
    hr_user_id = "c194e9e4-1086-4d9b-89cb-2236e5158d36"
    sales_user_id = "4f609741-7800-44f6-a1d6-640d6fe9bf01"

    eunomia.check_access(hr_user_id, faq_agent_id)
    eunomia.check_access(hr_user_id, hr_agent_id)
    eunomia.check_access(sales_user_id, faq_agent_id)
    eunomia.check_access(sales_user_id, hr_agent_id)
    ```

=== "Output"
    ```bash
    True
    True
    True
    False
    ```

Congratulations! You've just made your first steps with Eunomia.

You can now continue to the detailed [server documentation](../server/index.md) or explore the available [SDKs](../sdks/index.md) to discover how to best integrate Eunomia into your application.

[rego-docs]: https://www.openpolicyagent.org/docs/latest/policy-language/
