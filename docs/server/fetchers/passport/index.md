The Agent Passport enables **trusted agent governance** by providing cryptographically verified agent identities. Agents present signed JWT tokens that prove their identity and attributes, allowing Eunomia to make authorization decisions based on verified agent information rather than self-reported claims.

## What is the Agent Passport?

Agent Passport provides **verified agent identity** for governance through:

- **Cryptographically Signed Identity**: JWT tokens prove agent authenticity through digital signatures
- **Tamper-Proof Attributes**: Agent attributes are embedded in signed tokens, preventing false claims
- **Verified Authorization Context**: Policies can trust agent identity and attributes for authorization decisions
- **Admin-Controlled Identity**: Controlled token issuance ensures only authorized agents receive identity tokens

Technically, Agent Passport implements this as a [Dynamic Fetcher](../index.md) that decodes JWT tokens to extract verified agent attributes during policy evaluation.

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
