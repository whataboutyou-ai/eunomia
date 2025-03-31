# Eunomia TypeScript SDK

A TypeScript client for interacting with the Eunomia server.

## Installation

```bash
npm install eunomia-sdk-typescript
```

## Usage

```typescript
import { EunomiaClient, EntityType } from "eunomia-sdk-typescript";

// Create a client instance
const client = new EunomiaClient({
  serverHost: "http://localhost:8000", // optional
  apiKey: "your-api-key", // optional, defaults to process.env.WAY_API_KEY
});

// Check access
async function checkAccess() {
  const hasAccess = await client.checkAccess({
    principalUri: "user:123",
    resourceUri: "document:456",
    principalAttributes: { role: "admin" },
    resourceAttributes: { type: "confidential" },
  });

  console.log(`Has access: ${hasAccess}`);
}

// Register an entity
async function registerEntity() {
  const entity = await client.registerEntity({
    type: EntityType.Resource,
    attributes: {
      name: "Important Document",
      owner: "department:engineering",
    },
    uri: "document:456", // optional, will be generated if not provided
  });

  console.log(`Entity registered with URI: ${entity.uri}`);
}

// Update an entity
async function updateEntity() {
  const updatedEntity = await client.updateEntity({
    uri: "document:456",
    attributes: {
      classification: "secret",
    },
    override: false, // optional, defaults to false (merge attributes)
  });

  console.log("Entity updated");
}

// Delete an entity
async function deleteEntity() {
  await client.deleteEntity("document:456");
  console.log("Entity deleted");
}

// Create a policy
async function createPolicy() {
  await client.createPolicy({
    policy: {
      rules: [
        {
          principal: {
            uri: "user:123",
            attributes: { role: "admin" },
            type: EntityType.Principal,
          },
          resource: {
            uri: "document:456",
            attributes: { type: "confidential" },
            type: EntityType.Resource,
          },
        },
      ],
    },
    filename: "my-policy.json", // optional
  });

  console.log("Policy created");
}
```

## API Reference

### `EunomiaClient`

The main client class for interacting with the Eunomia server.

#### Constructor

```typescript
new EunomiaClient(options?: {
  serverHost?: string;
  apiKey?: string;
})
```

#### Methods

- `checkAccess`: Check whether a principal has access to a specific resource
- `registerEntity`: Register a new entity with the Eunomia server
- `updateEntity`: Update the attributes of an existing entity
- `deleteEntity`: Delete an entity from the Eunomia server
- `createPolicy`: Create a new policy and save it to the local file system
