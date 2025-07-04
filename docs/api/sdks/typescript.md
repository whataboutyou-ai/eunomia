Eunomia offers a TypeScript client that enables users to interact with the Eunomia server.

The client allows you to register resources and principals with their metadata to the Eunomia server, verify access control between principals and resources, update entities, and manage policies. These features simplify the integration of the Eunomia server into your TypeScript or JavaScript applications.

## Installation

Install the `eunomia-sdk` package via npm:

```bash
npm install eunomia-sdk
```

## Usage

### Standard API

Use the standard API for authorization checks in your application:

```typescript
import { EunomiaClient } from "eunomia-sdk";

const client = new EunomiaClient({
  endpoint: "http://localhost:8000"
});

// Check if a principal has permissions to perform an action on a resource
const response = await client.check({
  principalUri: "user:123",
  resourceUri: "document:456",
  action: "read",
});

console.log(`Is allowed: ${response.allowed}`);
```

```typescript
import { EunomiaClient, EntityType } from "eunomia-sdk";

// For admin API usage authentication via API key might be required
const client = new EunomiaClient({
  endpoint: "http://localhost:8000",
  apiKey: "my-api-key",
});

// Register a resource with metadata
const resource = await client.registerEntity({
  type: EntityType.Resource,
  uri: "document:456",
  attributes: {
    name: "sensitive_document",
    type: "document",
    classification: "confidential",
  },
  
});

// Register a principal with metadata
const principal = await client.registerEntity({
  type: EntityType.Principal,
  uri: "user:123",
  attributes: {
    name: "user_123",
    role: "analyst",
    department: "research",
  },
});
```

## Docs

### EunomiaClient

A client for interacting with the Eunomia server.

Creates a new `EunomiaClient` instance with the following options:

- `endpoint`: The base URL endpoint of the Eunomia server, defaults to "http://localhost:8000"
- `apiKey`: The API key for authentication, defaults to the env variable `WAY_API_KEY`

#### check

Checks whether a principal has permissions to perform an action on a resource.

```typescript
async check(options: {
  principalUri?: string;
  resourceUri?: string;
  principalAttributes?: Record<string, string>;
  resourceAttributes?: Record<string, string>;
}): Promise<boolean>
```

#### registerEntity

Registers a new entity with the Eunomia server.

```typescript
async registerEntity(options: {
  type: EntityType;
  attributes: Record<string, string>;
  uri?: string;
}): Promise<EntityInDb>
```

#### updateEntity

Updates the attributes of an existing entity. If override is true, all existing attributes are replaced; otherwise, they are merged.

```typescript
async updateEntity(options: {
  uri: string;
  attributes: Record<string, string>;
  override?: boolean;
}): Promise<EntityInDb>
```

#### deleteEntity

Deletes an entity from the Eunomia server.

```typescript
async deleteEntity(options: { uri: string }): Promise<void>
```

#### createPolicy

Creates a new policy and saves it to the local file system.

```typescript
async createPolicy(options: {
  policy: Policy;
  filename?: string;
}): Promise<void>
```
