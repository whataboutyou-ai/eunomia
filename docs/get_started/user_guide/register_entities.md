In the [Quickstart](../index.md) guide, we showed how to use the `POST /check` endpoint to verify if a given principal can perform an action on a specific resource by passing their identifiers and attributes. While this approach is straightforward, it requires sending all attributes with each check request. For more complex scenarios, it can be more efficient to pre-register the attributes of principals and resources, and then reference them by their identifier at runtime.

## Register a New Entity

You can register a new entity using the `POST /admin/fetchers/registry/entities` endpoint. This endpoint accepts a **POST** request with a JSON payload that follows the **EntityCreate** schema. Upon successful registration, the server returns the entity's information as defined by the **EntityInDb** model.

### Payload Requirements

Your JSON payload must include the following fields:

- **`attributes`** (required):  
  An array of attribute objects. Each attribute must include:

  - **`key`** (_string_): The attribute's key.
  - **`value`** (_string_): The attribute's value.

  _Note: The attributes array must not be empty, and duplicate keys are not allowed._

- **`type`** (required):  
  The type of the entity, defined by the **EntityType** enum (i.e., `principal` or `resource`).

- **`uri`** (optional):  
  A unique identifier for the entity. If omitted, the server will generate one automatically. This identifier is used later to check permissions for the entity.

### Response Details

On success, the server responds with a JSON object that includes the **`uri`** of the entity, which can be stored locally and used at a later stage.

## Example Usage

=== "Python"
    ```python
    from eunomia_core import enums
    from eunomia_sdk import EunomiaClient

    eunomia = EunomiaClient()

    # Register a resource with metadata
    resource = eunomia.register_entity(
        type=enums.EntityType.resource,
        attributes={
            "name": "sensitive_document",
            "type": "document",
            "classification": "confidential"
        }
    )
    print("Resource:", resource)

    # Register a principal with metadata
    principal = eunomia.register_entity(
        type=enums.EntityType.principal,
        attributes={
            "name": "user_123",
            "role": "analyst",
            "department": "research"
        }
    )
    print("Principal:", principal)
    ```

=== "Curl"
    ```bash
    curl -X POST 'http://localhost:8000/admin/fetchers/registry/entities' \
         -H "Content-Type: application/json" \
         -d '{
               "type": "resource",
               "attributes": {
                 "name": "sensitive_document",
                 "type": "document",
                 "classification": "confidential"
               }
             }'

    curl -X POST 'http://localhost:8000/admin/fetchers/registry/entities' \
         -H "Content-Type: application/json" \
         -d '{
               "type": "principal",
               "attributes": {
                 "name": "user_123",
                 "role": "analyst",
                 "department": "research"
               }
             }'
    ```

=== "Output"
    ```bash
    # Example JSON response for a resource
    {
      "uri": "generated-uri-123",
      "attributes": [
          {
            "key": "name",
            "value": "sensitive_document",
            "registered_at": "2025-03-22T10:00:00Z",
            "updated_at": "2025-03-22T10:00:00Z"
          },
          {
            "key": "type",
            "value": "document",
            "registered_at": "2025-03-22T10:00:00Z",
            "updated_at": "2025-03-22T10:00:00Z"
          },
          {
            "key": "classification",
            "value": "confidential",
            "registered_at": "2025-03-22T10:00:00Z",
            "updated_at": "2025-03-22T10:00:00Z"
          }
      ],
      "registered_at": "2025-03-22T10:00:00Z"
    }

    # Example JSON response for a principal
    {
      "uri": "generated-uri-456",
      "attributes": [
          {
            "key": "name",
            "value": "user_123",
            "registered_at": "2025-03-22T10:01:00Z",
            "updated_at": "2025-03-22T10:01:00Z"
          },
          {
            "key": "role",
            "value": "analyst",
            "registered_at": "2025-03-22T10:01:00Z",
            "updated_at": "2025-03-22T10:01:00Z"
          },
          {
            "key": "department",
            "value": "research",
            "registered_at": "2025-03-22T10:01:00Z",
            "updated_at": "2025-03-22T10:01:00Z"
          }
      ],
      "registered_at": "2025-03-22T10:01:00Z"
    }
    ```
