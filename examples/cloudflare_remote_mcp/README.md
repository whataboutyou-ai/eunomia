# Cloudflare Remote MCP with Eunomia Authorization

This example demonstrates integrating [Eunomia][eunomia-github] authorization with a remote [MCP][mcp-github] server deployed as a [Cloudflare Worker][cloudflare-worker-github].

## Overview

The example extends Cloudflare's demo on a [remote MCP server with GitHub OAuth][cloudflare-demo-github] by adding fine-grained access control to tools using Eunomia. It shows how to:

- Authorize access to specific tools within an MCP server based on authenticated user attributes
- Use Eunomia policies to define access rules
- Integrate authorization checks within an MCP server deployed as a Cloudflare Worker, decoupling the authorization logic from the MCP server implementation

## Usage

This example is not self-runnable and should be viewed as an extension to Cloudflare's original demo. Please refer to the [original demo][cloudflare-demo-github] for complete setup and running instructions.

To add Eunomia to the demo:

- Intall the SDK: `npm install eunomia-sdk-typescript`
- Substitute the `index.ts` file of the original demo with the one provided here
- Set up and run the Eunomia server - if you need instructions, you can find them [here][eunomia-docs]

## How it works

The implementation uses Eunomia to check if a user has access to specific tools based on their email:

1. During MCP initialization, the server performs an authorization check
2. The policy in `allow_tool.rego` defines the users that can access the image generation tool
3. Only authorized users will see and be able to use the protected tool

This way the authorization logic is completely decoupled from the MCP server implementation.

> [!NOTE]
> The example includes a simple policy that restricts access to the image generation tool based on user email. This policy can easily be extended to include more complex access control scenarios.

[eunomia-github]: https://github.com/whataboutyou-ai/eunomia
[eunomia-docs]: https://whataboutyou-ai.github.io/eunomia/get_started/user_guide/run_server/
[mcp-github]: https://github.com/modelcontextprotocol
[cloudflare-worker-github]: https://github.com/cloudflare/workers-sdk
[cloudflare-demo-github]: https://github.com/cloudflare/ai/tree/main/demos/remote-mcp-github-oauth
