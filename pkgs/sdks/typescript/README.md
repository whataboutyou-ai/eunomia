# Eunomia SDK for TypeScript

This package allows you to integrate [Eunomia][eunomia-github] inside your TypeScript application, providing a client to interact with the Eunomia server.

## Installation

Install the `eunomia-sdk` package via npm:

```bash
npm install eunomia-sdk
```

## Usage

Create an instance of the `EunomiaClient` class to interact with the Eunomia server.

```typescript
import { EunomiaClient, EntityType } from "eunomia-sdk";

const client = new EunomiaClient();
```

You can then call any server endpoint through the client. For example, you can check the permissions of a principal to perform an action on a resource:

```typescript
async function check() {
  const response = await client.check({
    principalAttributes: { role: "admin" },
    resourceAttributes: { type: "confidential" },
  });

  console.log(`Is allowed: ${response.allowed}`);
}
```

## Documentation

For detailed usage, check out the SDK's [documentation][docs].

[eunomia-github]: https://github.com/whataboutyou-ai/eunomia
[docs]: https://whataboutyou-ai.github.io/eunomia/api/sdks/typescript/
