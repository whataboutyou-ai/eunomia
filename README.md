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

Traditional authorization layers, focused on user-resource separation, become obsolete with AI agents. These agents, both autonomous and controllable, necessitate a new permission paradigm.

The ability for agents to access tools—executable actions beyond static data—and initiate interactions with other agents introduced policy requirements that legacy systems couldn't meet. This duality demands dynamic yet deterministic boundaries that adapt to context, reflecting their role as both actor and resource.

We aim to solve this with Eunomia, an open-source, developer-oriented authorization framework that:

- Makes it possible to consider agents as both actors and resources
- Enforces dynamic yet deterministic policies based on static and contextual attributes
- Enables leaner agent architectures with decoupled authorization logic
- Preserves agent decision-making while enforcing security

## Get Started

Eunomia is a standalone server to decouple the authorization logic from the main architecture of your AI Agent.

### Installation

Install the `eunomia` package via pip:

```bash
pip install eunomia-ai
```

### Running the Server

The server can be served locally with:

```bash
eunomia server
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

### Migration to v0.3.3

#### Endpoint Rename: `/policies` → `/policies/simple`

The simple policy creation endpoint has been renamed to `/policies/simple` for consistency.

#### New Endpoint: `/policies`

A new endpoint has been added for creating full policies:

```bash
curl -X POST "http://localhost:8000/policies" \
  -H "Content-Type: application/json" \
  -d '{"version": "1.0", "name": "...", "default_action": "...", "rules": []}'
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
[discord-badge]: https://dcbadge.vercel.app/api/server/TyhGZtzg3G?style=flat&theme=default-inverted
