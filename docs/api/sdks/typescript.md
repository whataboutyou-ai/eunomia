Eunomia offers a TypeScript client that enables users to interact with the Eunomia server.

The client allows you to register resources and principals with their metadata to the Eunomia server, verify access control between principals and resources, update entities, and manage policies. These features simplify the integration of the Eunomia server into your TypeScript or JavaScript applications.

## Installation

Install the `eunomia-sdk-typescript` package via npm:

```bash
npm install eunomia-sdk-typescript
```

## Usage

Import the EunomiaClient class and create an instance of it:

```typescript
import { EunomiaClient, EntityType } from "eunomia-sdk-typescript";

const client = new EunomiaClient({
  serverHost: "http://localhost:8000",
});
```

You can then use the client to interact with the Eunomia server:

```typescript
// Register a resource with metadata
const resource = await client.registerEntity({
  type: EntityType.Resource,
  attributes: {
    type: "document",
    classification: "confidential",
  },
  uri: "document:project-plan",
});

// Register a principal with metadata
const principal = await client.registerEntity({
  type: EntityType.Principal,
  attributes: {
    role: "admin",
    department: "engineering",
  },
  uri: "user:john.doe",
});

// Check if a principal has access to a resource
const hasAccess = await client.checkAccess({
  principalUri: principal.uri,
  resourceUri: resource.uri,
});
```

## SDK Docs

### EunomiaClient

A client for interacting with the Eunomia server.

Creates a new `EunomiaClient` instance with the following options:

- `serverHost`: The base URL of the Eunomia server, defaults to "http://localhost:8000"
- `apiKey`: The API key for authentication, defaults to the env variable `WAY_API_KEY`

#### checkAccess

Checks whether a principal has access to a specific resource.

```typescript
async checkAccess(options: {
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
