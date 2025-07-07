The **Eunomia server** is a standalone service that manages the authorization logic for your AI Agent. It is self-hosted and provides a **REST API** for your application.

In this guide, you'll learn how to **configure** and **run** the Eunomia server.

## Server Configuration

To run the Eunomia server, you must configure the following parameters:

| **Parameter**             | **Description**                                             | **Default Value**                                                       |
| ------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------- |
| `PROJECT_NAME`            | Name of the project                                         | `Eunomia Server`                                                        |
| `DEBUG`                   | Flag to enable debug mode                                   | `False`                                                                 |
| `ENGINE_SQL_DATABASE_URL` | Path to the policy database file                            | `sqlite:///.db/eunomia_db.sqlite`                                       |
| `FETCHERS`                | Dictionary of fetchers to use                               | `{"registry": {"sql_database_url": "sqlite:///.db/eunomia_db.sqlite"}}` |
| `ADMIN_API_KEY`           | Optional pre-shared key for Admin API authentication        | `None`                                                                  |
| `BULK_CHECK_MAX_REQUESTS` | Maximum number of requests allowed in bulk check operations | `100`                                                                   |
| `BULK_CHECK_BATCH_SIZE`   | Batch size for processing bulk check requests               | `10`                                                                    |

All parameters have default values, you can override any of them by setting environment variables, e.g., using a **`.env`** file.

The `registry` fetcher is provided by default to register and fetch metadata from a database.

## Running the Server

### Run Locally

If you have installed the `eunomia-ai` package, you can start the Eunomia server by executing the command in your terminal:

```bash
eunomia server
```

The server will start and listen for requests on address **`127.0.0.1`** and port **`8000`**. You can change the address and port by using the `--host` and `--port` flags:

```bash
eunomia server --host 0.0.0.0 --port 8080
```

You can also enable the automatic reload of the server on file changes by using the `--reload` flag:

```bash
eunomia server --reload
```

### Run with Docker

You can also run the Eunomia server using the Docker image:

```bash
docker run -d -p 8000:8000 --name eunomia ttommitt/eunomia-server:latest
```

Pin to a specific version if needed:

```bash
docker run -d -p 8000:8000 --name eunomia ttommitt/eunomia-server:0.3.5
```

Modify the server configuration by providing environment variables:

```bash
docker run -d -p 8000:8000 --name eunomia \
    -e DEBUG=True \
    -e ENGINE_SQL_DATABASE_URL=postgresql://user:password@host:port/database \
    ttommitt/eunomia-server:latest
```

!!! info
    The Docker image does not come with persistent storage on its own and will lose all data when the container is stopped. To persist the database, you need to mount a volume to the container or connect to an external database.
