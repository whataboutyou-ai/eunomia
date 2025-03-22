---
title: Configure and run the Eunomia Server 
---

The Eunomia server is a standalone service to handle the authorization logic of your AI Agent. The server can be self-hosted, exposing a REST API to your application.

In this guide we will see how to configure the Eunomia server and how to run it. 

### Server parameters
In order to run the Eunomia server, it relies on the following parameters:

| Parameter           | Description                                                     | Default value               |
| ------------------- | --------------------------------------------------------------- | --------------------------- |
| PROJECT_NAME        | Name of the project                                             | `Eunomia Server`            |
| DEBUG               | Flag to enable debug mode                                       | `False`                     |
| LOCAL_DB_HOST       | Database connection string                                      | `sqlite:///db.sqlite`       |
| OPA_SERVER_HOST     | Host address for the Open Policy Agent server                   | `127.0.0.1`                 |
| OPA_SERVER_PORT     | Port for the Open Policy Agent server                           | `8181`                      |
| OPA_POLICY_FOLDER   | Path to the folder where the Rego policy files are stored.      | _Required, no default given_|


All the parameters but OPA_POLICY_FOLDER have a default value and will not require anything more. While OPA_POLICY_FOLDER needs to be given by the user in imput in any case.

### Define and overwrite Server parameters

As mentioned before, the only paramenter the server expect in input is OPA_POLICY_FOLDER, while the others can be as well overwritten, if needed

To define the OPA_POLICY_FOLDER and overwrite other potential fields, this can be done via  `.env` file definition


First, copy the `.env.example` file to `.env` and set the `OPA_POLICY_FOLDER` variable to the path where you want to store the policies.

Then, let's start the Eunomia server with:

```bash
eunomia server
```