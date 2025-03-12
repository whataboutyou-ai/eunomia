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
fastapi dev src/eunomia/api/main.py
```

### Usage

Check out the [quickstart example][docs-quickstart] in the documentation for a fully working example.

## Eunomia SDKs

Different packages are available in this repository for an easier interaction with the server. These packages make the integration of Eunomia inside your AI application as seamless as possible within your favorite development framework.

The following packages are currently available:

- [Python](sdks/python)
- [LangChain](sdks/langchain)
- ...and more coming soon!

## Documentation

For more examples and detailed usage, check out the [documentation][docs].

[whataboutyou-website]: https://whataboutyou.ai
[docs]: https://whataboutyou-ai.github.io/eunomia/
[docs-quickstart]: https://whataboutyou-ai.github.io/eunomia/get_started/quickstart/
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
