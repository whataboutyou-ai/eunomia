The API exposes endpoints to interact with the Eunomia server.

The API is built with [FastAPI][fastapi-docs].

## Running the Server

The server can be served locally with:

```bash
eunomia server
```

## API Endpoints

The API has the following endpoints:

- `POST /check-access`: Check if a principal has access to perform an action on a resource.
- `GET /policies`: Get all policies.
- `POST /policies`: Create a new policy.
- `GET /policies/{name}`: Get a policy by name.
- `DELETE /policies/{name}`: Delete a policy by name.
- `GET /fetchers/internal/entities`: Get entities with pagination.
- `GET /fetchers/internal/entities/$count`: Get the total number of entities.
- `POST /fetchers/internal/entities`: Register a new entity in the system.
- `GET /fetchers/internal/entities/{uri}`: Get an entity by URI.
- `PUT /fetchers/internal/entities/{uri}`: Update an existing entity.
- `DELETE /fetchers/internal/entities/{uri}`: Delete an entity from the system.

For detailed information on the API endpoints, refer to the automatically generated API docs when running the server locally.

[fastapi-docs]: https://fastapi.tiangolo.com/
