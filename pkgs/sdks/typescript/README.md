# Eunomia SDK for TypeScript

This package allows you to integrate [Eunomia][eunomia-github] inside your TypeScript application, providing a client to interact with the Eunomia server.

## Installation

Install the `eunomia-sdk-typescript` package via npm:

```bash
npm install eunomia-sdk-typescript
```

## Usage

Create an instance of the `EunomiaClient` class to interact with the Eunomia server.

```typescript
import { EunomiaClient, EntityType } from "eunomia-sdk-typescript";

const client = new EunomiaClient();
```

You can then call any server endpoint through the client. For example, you can check the access of a principal to a resource:

```typescript
async function checkAccess() {
  const hasAccess = await client.checkAccess({
    principalAttributes: { role: "admin" },
    resourceAttributes: { type: "confidential" },
  });

  console.log(`Has access: ${hasAccess}`);
}
```

## Documentation

For detailed usage, check out the SDK's [documentation][docs].

[eunomia-github]: https://github.com/whataboutyou-ai/eunomia
[docs]: https://whataboutyou-ai.github.io/eunomia/api/sdks/typescript/
