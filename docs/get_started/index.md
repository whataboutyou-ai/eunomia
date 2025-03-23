## What is Eunomia?

Eunomia is a Python library that allows you to decouple the authorization logic from the main architecture of your AI Agent. Eunomia is built as a standalone authorization server that can serve any application.

It is built and maintained by [What About You][whataboutyou-website], while contributions are welcome from the [community](../community/index.md).

!!! warning
    Eunomia is currently under active development and therefore subject to change.

## How to Get Started?

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __Set up in seconds__

    ---

    Install `eunomia` with `pip` and get up and running in seconds

    [:material-arrow-right: Installation](installation.md#install-latest-release)


-   :material-play-speed:{ .lg .middle } __Start with an example__

    ---

    Get started with Eunomia by following the quickstart example

    [:material-arrow-right: Quickstart](quickstart.md)


-   :material-application-brackets-outline:{ .lg .middle } __Integrate within your codebase__

    ---

    Use one of the available SDKs to integrate Eunomia into your project

    [:material-arrow-right: Explore SDKs](../api/sdks/index.md)


-   :material-scale-balance:{ .lg .middle } __Open Source__

    ---

    Eunomia is licensed under Apache 2.0 and available on [GitHub][eunomia-github]

    [:material-arrow-right: License](../community/license.md)

</div>

## Why Eunomia?

Traditional authorization layers, focused on user-resource separation, become obsolete with AI agents. These agents, both autonomous and controllable, necessitate a new permission paradigm.

The ability for agents to access tools—executable actions beyond static data—and initiate interactions with other agents introduced policy requirements that legacy systems couldn't meet. This duality demands dynamic yet deterministic boundaries that adapt to context, reflecting their role as both actor and resource.

We aim to solve this with Eunomia, an open-source, developer-oriented authorization framework that:

- Makes it possible to consider agents as both actors and resources
- Enforces dynamic yet deterministic policies based on static and contextual attributes
- Enables leaner agent architectures with decoupled authorization logic
- Preserves agent decision-making while enforcing security


[eunomia-github]: https://github.com/whataboutyou-ai/eunomia
[whataboutyou-website]: https://whataboutyou.ai
[opa-website]: https://www.openpolicyagent.org/
