The Agent Passport is a built-in [Dynamic Fetcher](../index.md) that enables agent authentication through encrypted JWT tokens. It allows agents to authenticate with Eunomia by presenting a passport token, which contains their attributes and authorization metadata.

## What is the Agent Passport?

The Agent Passport provides:

- **Agent authentication**: Secure JWT-based authentication for AI agents
- **Attribute decryption**: Automatic verification and extraction of agent attributes from tokens
- **Token-based authorization**: Agents present their passport token as their URI during permission checks
- **Admin-controlled issuance**: Controlled passport generation through admin API endpoints

## How it Works

1. **Passport Issuance**: Admins issue encrypted passport tokens for agents through the API
2. **Agent Authentication**: Agents present their passport token as the `uri` parameter during permission checks
3. **Automatic Verification**: The fetcher verifies the token signature and extracts the embedded attributes
4. **Policy Evaluation**: The decrypted attributes are passed to the policy engine for authorization decisions

## Configuration

Configure the Passport fetcher in your Eunomia settings:

```python
FETCHERS = {
    "passport": {
        "jwt_secret": "your-secret-key",
        "jwt_algorithm": "HS256", # optional
        "jwt_issuer": "eunomia", # optional
        "jwt_default_ttl": 7200,  # optional, 2 hours
        "requires_registry": False,  # optional, set to True to require agents to be registered
        "entity_type": None  # optional, set to "principal" to only require principals to use the passport
    }
}
```

When `requires_registry` is enabled, the passport fetcher will only issue tokens for agents that are already registered in the [registry](../registry/index.md) fetcher.

## User Guides

| Guide            | Description                                   | Jump to                                          |
| ---------------- | --------------------------------------------- | ------------------------------------------------ |
| Issue a Passport | Learn how to issue passport tokens for agents | [:material-arrow-right: Page](issue_passport.md) |
