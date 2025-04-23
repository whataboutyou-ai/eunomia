The **Eunomia server** is a standalone service that manages the authorization logic for your AI Agent. It is self-hosted and provides a **REST API** for your application.

In this guide, you'll learn how to **configure** and **run** the Eunomia server.

### Server Parameters

To run the Eunomia server, you must configure the following parameters:

| **Parameter**       | **Description**                                           | **Default Value**                                                        |
| ------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------ |
| `PROJECT_NAME`      | Name of the project                                       | `Eunomia Server`                                                         |
| `DEBUG`             | Flag to enable debug mode                                 | `False`                                                                  |
| `FETCHERS`          | Dictionary of fetchers to use                             | `{"internal": {"SQL_DATABASE_URL": "sqlite:///.db/internal_db.sqlite"}}` |
| `OPA_SERVER_HOST`   | Host address for the Open Policy Agent server             | `127.0.0.1`                                                              |
| `OPA_SERVER_PORT`   | Port for the Open Policy Agent server                     | `8181`                                                                   |
| `OPA_POLICY_FOLDER` | Path to the folder where the Rego policy files are stored | _Required (no default)_                                                  |

All parameters have default values except **`OPA_POLICY_FOLDER`**, which must be provided by the user.

### Configuring and Overwriting Server Parameters

As noted, **`OPA_POLICY_FOLDER`** is the only parameter that does not have a default and must be defined. You can also override the other parameters if needed.

To do this, create a **`.env`** file in the root directory of your project and set the required variables.

Alternatively, you can copy the **`.env.example`** file included with the library, rename it to **`.env`**, and update the **`OPA_POLICY_FOLDER`** variable with the path to your policy files.

For example, if you want to run the Eunomia server on port **8082** instead of the default **8181**, and your policies are located in the directory **`/Users/demo_user/Desktop/eunomia_policies/`**, your **`.env`** file should contain:

```bash
OPA_SERVER_PORT=8082
OPA_POLICY_FOLDER="/Users/demo_user/Desktop/eunomia_policies/"
```

### Running the Server

Once your **`.env`** file is configured, start the Eunomia server by executing the following command:

```bash
eunomia server
```
