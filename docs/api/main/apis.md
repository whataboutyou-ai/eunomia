The API exposes endpoints to interact with the Eunomia server.

The API is built with [FastAPI][fastapi-docs].

## Running the Server

The server can be served locally with:

```bash
eunomia server
```

## API Endpoints

The API has the following endpoints:

- `POST /check-access`: Check if a principal has access to a resource.
- `POST /fetchers/internal/register-entity`: Register a new entity in the system.
- `POST /fetchers/internal/update-entity`: Update an existing entity.
- `POST /fetchers/internal/delete-entity`: Delete an entity from the system.
- `GET /policies`: Get all policies.
- `POST /policies`: Create a new policy.
- `GET /policies/{name}`: Get a policy by name.
- `DELETE /policies/{name}`: Delete a policy by name.

For detailed information on the API endpoints, refer to the automatically generated API docs when running the server locally at [http://localhost:8000/docs](http://localhost:8000/docs){:target="\_blank"}.

[fastapi-docs]: https://fastapi.tiangolo.com/
