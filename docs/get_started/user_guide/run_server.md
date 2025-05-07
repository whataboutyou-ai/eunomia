The **Eunomia server** is a standalone service that manages the authorization logic for your AI Agent. It is self-hosted and provides a **REST API** for your application.

In this guide, you'll learn how to **configure** and **run** the Eunomia server.

### Server Parameters

To run the Eunomia server, you must configure the following parameters:

| **Parameter**             | **Description**                  | **Default Value**                                                        |
| ------------------------- | -------------------------------- | ------------------------------------------------------------------------ |
| `PROJECT_NAME`            | Name of the project              | `Eunomia Server`                                                         |
| `DEBUG`                   | Flag to enable debug mode        | `False`                                                                  |
| `ENGINE_SQL_DATABASE_URL` | Path to the policy database file | `sqlite:///.db/engine_db.sqlite`                                         |
| `FETCHERS`                | Dictionary of fetchers to use    | `{"internal": {"SQL_DATABASE_URL": "sqlite:///.db/internal_db.sqlite"}}` |

All parameters have default values, you can override any of them by setting the environment variable in the **`.env`** file.

The _internal_ fetcher is provided by default to register and fetch metadata from a database.

### Running the Server

You can start the Eunomia server by executing the command:

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
