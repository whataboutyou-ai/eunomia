The API exposes endpoints to interact with the Eunomia server.

The API is built with [FastAPI][fastapi-docs].

## Running the Server

The server can be served locally with:

```bash
fastapi dev src/eunomia/api/main.py
```

## API Endpoints

The API has the following endpoints:

- `POST /register_resource`: Register a new resource in the system.
- `POST /register_principal`: Register a new principal in the system.
- `GET /check_access`: Check if a principal has access to a resource.

For detailed information on the API endpoints, refer to the automatically generated API docs when running the server locally at [http://localhost:8000/docs](http://localhost:8000/docs){:target="\_blank"}.

[fastapi-docs]: https://fastapi.tiangolo.com/
