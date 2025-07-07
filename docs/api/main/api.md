The API exposes endpoints to interact with the Eunomia server.

The API is built with [FastAPI][fastapi-docs].

## API Structure

Eunomia provides two distinct API categories:

### Standard API (Public)

The standard API is designed for authorization checks and is meant to be used by your applications and AI agents. These endpoints are publicly accessible and do not require authentication:

- `POST /check`: Check if a principal has permissions to perform an action on a resource
- `POST /check/bulk`: Perform a set of permission checks in a single request

### Admin API (Protected)

The admin API is designed for server configuration and management tasks. These endpoints are prefixed with `/admin` and can optionally be protected with a pre-shared key (PSK) for security:

- `GET /admin/policies`: Get all policies
- `POST /admin/policies`: Create a new policy
- `POST /admin/policies/simple`: Create a simple policy with a single rule
- `GET /admin/policies/{name}`: Get a policy by name
- `DELETE /admin/policies/{name}`: Delete a policy by name

If the `registry` fetcher is enabled (which is by default), the following endpoints are also available:

- `GET /admin/fetchers/registry/entities`: Get entities with pagination
- `GET /admin/fetchers/registry/entities/$count`: Get the total number of entities
- `POST /admin/fetchers/registry/entities`: Register a new entity in the system
- `GET /admin/fetchers/registry/entities/{uri}`: Get an entity by URI
- `PUT /admin/fetchers/registry/entities/{uri}`: Update an existing entity
- `DELETE /admin/fetchers/registry/entities/{uri}`: Delete an entity from the system

#### Admin API Authentication

##### Server-side

To enable Admin API authentication, configure the following environment variable for the Eunomia server:

```bash
ADMIN_API_KEY=your-secure-admin-key-here
```

##### Client-side

When using the Admin API endpoints, include the pre-shared key in the request headers:

```
WAY-API-KEY: your-secure-admin-key-here
```

If you are using one of the Eunomia SDKs, the API key can be provided in the client constructor or as an environment variable and it will be automatically added to the request headers.

[fastapi-docs]: https://fastapi.tiangolo.com/
