/* eslint-disable no-console */
import { AccessRequest, EntityType, EunomiaClient } from "eunomia-sdk-typescript";

async function run(): Promise<void> {
  const client = new EunomiaClient({
    serverHost: "http://localhost:8000",
  });

  try {
    // // Register a principal
    console.log("Registering principal...");
    const principal = await client.registerEntity({
      type: EntityType.Principal,
      attributes: {
        role: "admin",
        department: "engineering",
      },
      uri: "user:john.doe",
    });
    console.log(`Principal registered: ${principal.uri}`);

    // Register a resource
    console.log("Registering resource...");
    const resource = await client.registerEntity({
      type: EntityType.Resource,
      attributes: {
        type: "document",
        classification: "confidential",
      },
      uri: "document:project-plan",
    });
    console.log(`Resource registered: ${resource.uri}`);

    // Check access
    console.log("Checking access...");
    const hasAccess = await client.checkAccess({
      principalUri: principal.uri,
      resourceUri: resource.uri,
    });
    console.log(`Has access: ${hasAccess}`);

    // Update entity
    console.log("Updating entity...");
    await client.updateEntity({
      uri: resource.uri,
      attributes: {
        classification: "public",
        status: "published",
      },
    });
    console.log("Resource updated");

    // Delete entity
    console.log("Deleting entity...");
    await client.deleteEntity(principal.uri);
    console.log("Entities deleted");

    // Create policy
    console.log("Creating policy...");
    const request: AccessRequest = {
      principal: {
        type: EntityType.Principal,
        attributes: {
          role: "admin",
          department: "engineering",
        },
      },
      resource: {
        type: EntityType.Resource,
        attributes: {
          type: "document",
          classification: "confidential",
        },
      },
      action: "access",
    };
    const policy = await client.createPolicy(request, "policy-example");
    console.log(`Policy created: ${policy.name}`);
  } catch (error) {
    console.error("Error:", error);
  }
}

run().catch(console.error);
