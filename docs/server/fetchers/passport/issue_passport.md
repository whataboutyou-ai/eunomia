Passport issuance is an admin operation that creates JWT tokens for agents to authenticate with Eunomia. These tokens can contain the agent's attributes and can be used during permission checks.

## Prerequisites

- Eunomia server running with the Passport fetcher configured
- Admin API access
- If `requires_registry` is enabled, the agent must be registered in the [registry](../registry/index.md) first

## Issue a Passport via API

### Endpoint

```
POST /fetchers/passport/issue
```

### Request Body

```json
{
  "uri": "agent://my-ai-agent",
  "attributes": {
    "role": "assistant",
    "department": "customer-service",
    "capabilities": ["chat", "search"]
  },
  "ttl": 3600
}
```

### Parameters

| Parameter    | Type    | Required | Description                                                          |
| ------------ | ------- | -------- | -------------------------------------------------------------------- |
| `uri`        | string  | Yes      | The unique identifier for the agent                                  |
| `attributes` | object  | No       | Additional attributes to embed in the passport                       |
| `ttl`        | integer | No       | Token lifetime in seconds (defaults to configured `jwt_default_ttl`) |

### Response

```json
{
  "passport": "eyJhbGciOiJIU...",
  "passport_id": "psp_a1b2c3d4e5f6",
  "expires_in": 3600
}
```

## Example Usage

=== "Python"

    ```python
    from eunomia_sdk import EunomiaClient

    eunomia = EunomiaClient()

    response = eunomia.issue_passport(
        uri="agent://customer-service-bot",
        attributes={
            "role": "customer_support",
            "access_level": "standard",
            "department": "support",
        },
        ttl=7200,
    )
    ```

=== "cURL"

    ```bash
    curl -X POST "http://localhost:8421/fetchers/passport/issue" \
        -H "Content-Type: application/json" \
        -d '{
            "uri": "agent://customer-service-bot",
            "attributes": {
                "role": "customer_support",
                "access_level": "standard",
                "department": "support"
            },
            "ttl": 7200
        }'
    ```

=== "Output"

    ```json
    {
        "passport": "eyJhbGciOiJIU...",
        "passport_id": "psp_849fc4eddefa",
        "expires_in": 7200
    }
    ```

## Using the Passport

Once issued, agents can use the passport token as their URI when making permission checks:

```python
# Agent uses the passport token as their URI
result = eunomia.check(
    principal_uri=passport_token,
    resource_uri="customer_data",
    action="read",
)
```

## Registry Integration

When `requires_registry = true` is set in the server settings, the passport issuer will:

1. Check if the agent URI exists in the registry
2. Automatically include registry attributes in the passport
3. Deny issuance if the agent is not registered

```python
# If requires_registry=True, this will fail unless the agent is registered
response = eunomia.issue_passport(uri="agent://unregistered-agent")
```
