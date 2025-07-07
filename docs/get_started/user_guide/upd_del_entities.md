In addition to registering entities, you can update or delete them using dedicated API endpoints. This section explains how to update an entity's attributes and remove an entity entirely.

## Update an Entity

The **`PUT /admin/fetchers/registry/entities/{uri}`** endpoint allows you to update an already registered entity. The JSON payload must conform to the **EntityUpdate** schema. In this schema:

- **`uri`** (required):  
  The unique identifier for the entity that you want to update.
- **`attributes`** (required):  
  An array of attribute objects to update. Each attribute must include a **`key`** and a **`value`**

- **`override`** (default: `False`), controls whether the update should completely override existing attributes or merge with them. If override is set to `True`, only the attributes and the respective values present in the `attributes` array will be present in the new updated entity. All the previous attributes will be overwritten.

## Delete an Entity

The **`DELETE /admin/fetchers/registry/entities/{uri}`** endpoint allows you to delete an entity by providing its unique **`uri`**.

## Example Usage

=== "Python"
    ```python
    from eunomia_sdk import EunomiaClient

    eunomia = EunomiaClient()

    # Update an entity's attributes
    updated_entity = eunomia.update_entity(
        type="resource",  # Optional: if not provided, defaults to "any"
        attributes={
            "name": "sensitive_document_updated",
            "type": "document",
            "classification": "confidential"
        },
        uri="generated-uri-123"  # The unique identifier of the entity to update
    )
    print("Updated Entity:", updated_entity)

    # Delete an entity
    delete_response = eunomia.delete_entity(uri="generated-uri-123")
    print("Delete Response:", delete_response)
    ```

=== "Curl"
    ```bash
    # Update an entity
    curl -X PUT 'http://localhost:8000/admin/fetchers/registry/entities/generated-uri-123' \
         -H "Content-Type: application/json" \
         -d '{
               "uri": "generated-uri-123",
               "type": "any",
               "attributes": {
                 "name": "sensitive_document_updated",
                 "type": "document",
                 "classification": "confidential"
               }
             }'

    # Delete an entity
    curl -X DELETE 'http://localhost:8000/admin/fetchers/registry/entities/generated-uri-123' \
         -H "Content-Type: application/json" \
         -d '{"uri": "generated-uri-123"}'
    ```

=== "Output"
    ```bash
    # Example JSON response for an updated entity
    {
      "uri": "generated-uri-123",
      "attributes": [
          {
            "key": "name",
            "value": "sensitive_document_updated",
            "registered_at": "2025-03-22T10:00:00Z",
            "updated_at": "2025-03-22T11:00:00Z"
          },
          {
            "key": "type",
            "value": "document",
            "registered_at": "2025-03-22T10:00:00Z",
            "updated_at": "2025-03-22T11:00:00Z"
          },
          {
            "key": "classification",
            "value": "confidential",
            "registered_at": "2025-03-22T10:00:00Z",
            "updated_at": "2025-03-22T11:00:00Z"
          }
      ],
      "registered_at": "2025-03-22T10:00:00Z"
    }

    # Example JSON response for a deleted entity
    {
      "uri": "generated-uri-123",
      "message": "Entity deleted successfully"
    }
    ```
