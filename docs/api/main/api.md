The API exposes endpoints to interact with the Eunomia server.

The API is built with [FastAPI][fastapi-docs].

## Running the Server

The server can be served locally with:

```bash
eunomia server
```

## API Endpoints

The API has the following endpoints:

- `POST /check`: Check if a principal has permissions to perform an action on a resource.
- `POST /check/bulk`: Perform a set of permission checks in a single request.
- `GET /admin/policies`: Get all policies.
- `POST /admin/policies`: Create a new policy.
- `POST /admin/policies/simple`: Create a simple policy with a single rule.
- `GET /admin/policies/{name}`: Get a policy by name.
- `DELETE /admin/policies/{name}`: Delete a policy by name.
- `GET /admin/fetchers/internal/entities`: Get entities with pagination.
- `GET /admin/fetchers/internal/entities/$count`: Get the total number of entities.
- `POST /admin/fetchers/internal/entities`: Register a new entity in the system.
- `GET /admin/fetchers/internal/entities/{uri}`: Get an entity by URI.
- `PUT /admin/fetchers/internal/entities/{uri}`: Update an existing entity.
- `DELETE /admin/fetchers/internal/entities/{uri}`: Delete an entity from the system.

For detailed information on the API endpoints, refer to the automatically generated API docs when running the server locally.

[fastapi-docs]: https://fastapi.tiangolo.com/
