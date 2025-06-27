from eunomia_core import enums, schemas
from eunomia_sdk.client import EunomiaClient


def run():
    client = EunomiaClient(endpoint="http://localhost:8000")

    try:
        # Register a principal
        print("Registering principal...")
        principal = client.register_entity(
            type=enums.EntityType.principal,
            attributes={
                "role": "admin",
                "department": "engineering",
            },
            uri="user:john.doe",
        )
        print(f"Principal registered: {principal.uri}")

        # Register a resource
        print("Registering resource...")
        resource = client.register_entity(
            type=enums.EntityType.resource,
            attributes={
                "type": "document",
                "classification": "confidential",
            },
            uri="document:project-plan",
        )
        print(f"Resource registered: {resource.uri}")

        # Check permissions
        print("Checking permissions...")
        is_allowed = client.check(
            principal_uri=principal.uri,
            resource_uri=resource.uri,
        )
        print(f"Is allowed: {is_allowed}")

        # Update entity
        print("Updating entity...")
        _ = client.update_entity(
            uri=resource.uri,
            attributes={
                "classification": "public",
                "status": "published",
            },
        )
        print("Resource updated")

        # Delete entity
        print("Deleting entity...")
        client.delete_entity(principal.uri)
        print("Entities deleted")

        # Create policy
        print("Creating policy...")
        request = schemas.CheckRequest(
            principal=schemas.PrincipalCheck(
                attributes={"role": "admin", "department": "engineering"}
            ),
            resource=schemas.ResourceCheck(
                attributes={"type": "document", "classification": "confidential"}
            ),
            action="read",
        )
        policy = client.create_simple_policy(request=request, name="policy-example")
        print(f"Policy created: {policy.name}")

    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    run()
