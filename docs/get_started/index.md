## What is Eunomia?

Eunomia is a Python library that allows you to decouple the authorization logic from the main architecture of your AI Agent. Eunomia is built as a standalone authorization server that can serve any application.

It is built and maintained by [What About You][whataboutyou-website], while contributions are welcome from the [community](../community/index.md).

!!! warning
    Eunomia is currently under active development and therefore subject to change.

## Core Components

<div class="grid cards" markdown>

-   :material-account-multiple:{ .lg .middle } __Principals__

    ---

    Principals are actors (human or AI) performing actions on resources.


-   :material-semantic-web:{ .lg .middle } __Resources__

    ---

    Resources are the targets of actions, including data, tools, and AI agents.

    


-   :material-police-badge:{ .lg .middle } __Attributes__

    ---

    Metadata of Principals and Resources, used in authorization policies.



-   :material-note-edit:{ .lg .middle } __Policies__

    ---

    Policies are rules that explicitly allow or deny Principals' actions on Resources.

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
