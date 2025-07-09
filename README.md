# Eunomia

<div align="center" style="margin-bottom: 1em;">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="./docs/assets/logo-owl-dark.png">
  <img alt="Eunomia Logo" src="./docs/assets/logo-owl.png" width=300>
</picture>

_Authorization layer for AI Agents_

Made with ❤ by the team at [What About You][whataboutyou-website].

[Read the docs][docs] · [Join the Discord][discord]

[![PyPi][pypi-badge]][pypi]
[![CI][ci-badge]][ci]
[![CD][cd-badge]][cd]
[![License][license-badge]][license]
[![Discord][discord-badge]][discord]

</div>

> [!NOTE]
> Try the new [Eunomia MCP Middleware][extension-mcp-github] for adding policy-based authorization to your MCP servers!

## Overview

Eunomia is a standalone authorization layer purpose-built for AI agents. As a framework-agnostic solution, it decouples authorization logic from your agent architecture, enabling cleaner and more maintainable systems.

Built in the open, Eunomia provides enterprise-grade authorization capabilities that power What About You's AI governance platform. The framework seamlessly integrates with [Model Context Protocol (MCP)][mcp-website] primitives, making it easy to add policy-based authorization to your existing agent workflows.

Key features:

- **Framework-agnostic**: Works with any AI agent architecture or framework
- **Decoupled design**: Separates authorization concerns from business logic
- **MCP integration**: Native support for Model Context Protocol workflows
- **Enterprise-ready**: Proven in production environments
- **Developer-focused**: Simple APIs and comprehensive tooling

## Get Started

Eunomia is a standalone server to decouple the authorization logic from the main architecture of your AI Agent.

### Running the Server

Install the `eunomia-ai` package via `pip` and run the server locally with:

```bash
eunomia server
```

Or use the Docker image instead:

```bash
docker run -d -p 8000:8000 --name eunomia ttommitt/eunomia-server:latest
```

### Usage

Check out the [quickstart example][docs-quickstart] in the documentation for a fully working example.

## Other Eunomia packages

### Eunomia SDKs

To interact with the server from your code, you can use the following SDKs:

- [Python][sdk-python-github]
- [Typescript][sdk-typescript-github]

### Eunomia Extensions

Eunomia provides extensions for the following frameworks:

- [MCP Middleware][extension-mcp-github]
- [LangChain][extension-langchain-github]

## Documentation

For more examples and detailed usage, check out the [documentation][docs].

## Changelog

### Migration to v0.3.6

#### Admin API endpoints now require `/admin` prefix

Admin endpoints for policy and entity management have been moved under the `/admin` prefix for better organization and security. Update your requests to use the new endpoints:

**Affected endpoints:**

- All `/policies[...]` endpoints → `/admin/policies[...]`
- All `/fetchers[...]` endpoints → `/admin/fetchers[...]`

**Public endpoints unchanged:**

- All `/check[...]` endpoints remain public

The SDKs have been automatically updated to use the new endpoints.

#### Renamed fetcher: `internal` → `registry`

The `internal` fetcher has been renamed to `registry` for consistency. Update your configuration and endpoints to use the new name.

### Migration to v0.3.5

#### Renamed SDK packages: `eunomia-sdk-python` → `eunomia-sdk` and `eunomia-sdk-typescript` → `eunomia-sdk`

The SDK packages have been renamed to `eunomia-sdk` for consistency. Install the new package and update your imports.

Python:

```python
# Before (v0.3.4)
from eunomia_sdk_python import EunomiaClient

# After (v0.3.5)
from eunomia_sdk import EunomiaClient
```

Typescript:

```typescript
// Before (v0.3.4)
import { EunomiaClient } from "eunomia-sdk-typescript";

// After (v0.3.5)
import { EunomiaClient } from "eunomia-sdk";
```

### Migration to v0.3.3

#### Modified Response for `/check` and `/check/bulk`

The response of `/check` and `/check/bulk` endpoints has changed from `bool` to `eunomia_core.schemas.CheckResponse`.

Update your Python code to use the new response type:

```python
# Before (v0.3.2)
is_allowed = eunomia.check(principal_uri, resource_uri)

# After (v0.3.3)
response = eunomia.check(principal_uri, resource_uri)
is_allowed = response.allowed
```

#### Endpoint Rename: `/policies` → `/policies/simple`

The simple policy creation endpoint has been renamed to `/policies/simple` for consistency.

#### New Endpoint: `/policies`

A new endpoint has been added for creating full policies:

```bash
curl -X POST "http://localhost:8000/policies" \
  -H "Content-Type: application/json" \
  -d '{"version": "1.0", "name": "...", "default_effect": "...", "rules": []}'
```

### Migration to v0.3.2

The following breaking changes were introduced in this version:

#### Endpoint Rename: `/check-access` → `/check`

The authorization endpoint has been renamed for clarity; update your requests to use the new endpoint:

```bash
# Before (v0.3.1)
curl -X POST "http://localhost:8000/check-access" \
  -H "Content-Type: application/json" \
  -d '{"principal": {...}, "action": "...", "resource": {...}}'

# After (v0.3.2)
curl -X POST "http://localhost:8000/check" \
  -H "Content-Type: application/json" \
  -d '{"principal": {...}, "action": "...", "resource": {...}}'
```

#### New Endpoint: `/check/bulk`

A new bulk authorization endpoint has been added for improved performance when checking multiple permissions:

```bash
curl -X POST "http://localhost:8000/check/bulk" \
  -H "Content-Type: application/json" \
  -d '[
    {"principal": {...}, "action": "...", "resource": {...}},
    {"principal": {...}, "action": "...", "resource": {...}}
  ]'
```

[whataboutyou-website]: https://whataboutyou.ai
[mcp-website]: https://modelcontextprotocol.io/
[docs]: https://whataboutyou-ai.github.io/eunomia/
[docs-quickstart]: https://whataboutyou-ai.github.io/eunomia/get_started/quickstart/
[sdk-python-github]: https://github.com/whataboutyou-ai/eunomia/tree/main/pkgs/sdks/python
[extension-mcp-github]: https://github.com/whataboutyou-ai/eunomia/tree/main/pkgs/extensions/mcp
[extension-langchain-github]: https://github.com/whataboutyou-ai/eunomia/tree/main/pkgs/extensions/langchain
[sdk-typescript-github]: https://github.com/whataboutyou-ai/eunomia/tree/main/pkgs/sdks/typescript
[pypi]: https://pypi.python.org/pypi/eunomia-ai
[pypi-badge]: https://img.shields.io/pypi/v/eunomia-ai.svg
[ci]: https://github.com/whataboutyou-ai/eunomia/actions/workflows/ci.yml
[ci-badge]: https://github.com/whataboutyou-ai/eunomia/actions/workflows/ci.yml/badge.svg
[cd]: https://github.com/whataboutyou-ai/eunomia/actions/workflows/cd.yml
[cd-badge]: https://github.com/whataboutyou-ai/eunomia/actions/workflows/cd.yml/badge.svg
[license]: https://github.com/whataboutyou-ai/eunomia/blob/main/LICENSE
[license-badge]: https://img.shields.io/github/license/whataboutyou-ai/eunomia.svg?v
[discord]: https://discord.gg/TyhGZtzg3G
[discord-badge]: https://dcbadge.limes.pink/api/server/TyhGZtzg3G?style=flat&theme=default-inverted
