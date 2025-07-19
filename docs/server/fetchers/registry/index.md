The Registry fetcher is a built-in [Dynamic Fetcher](../index.md) that stores and retrieves entity attributes in a SQL database. It provides a persistent storage solution for entity metadata that can be accessed during policy evaluation.

## What is the Registry Fetcher?

The Registry fetcher allows you to:

- **Store entity attributes**: Register principals and resources with their metadata
- **Retrieve attributes**: Fetch entity attributes at runtime during authorization checks
- **Manage entities**: Update and delete entity information through REST API endpoints

The Registry fetcher is ideal for scenarios where you want to maintain entity metadata within your Eunomia deployment, providing fast access and full control over your authorization data.

## Configuration

Configure the Registry fetcher in your Eunomia settings:

```python
FETCHERS = {
    "registry": {
        "sql_database_url": "sqlite:///./.db/eunomia_db.sqlite" # or any other SQL database URL
    }
}
```

## User Guides

| Guide                       | Description                                              | Jump to                                                  |
| --------------------------- | -------------------------------------------------------- | -------------------------------------------------------- |
| Register an Entity          | Learn how to register new entities with their attributes | [:material-arrow-right: Page](register_entities.md)      |
| Update and Delete an Entity | Learn how to update or delete existing entities          | [:material-arrow-right: Page](update_delete_entities.md) |
