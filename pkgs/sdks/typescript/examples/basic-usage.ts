import { EunomiaClient, EntityType } from "../src";

async function run() {
  // Create a client instance
  const client = new EunomiaClient({
    serverHost: "http://localhost:8000",
    apiKey: process.env.WAY_API_KEY || "your-api-key-here",
  });

  try {
    // Register a principal
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
    const updatedResource = await client.updateEntity({
      uri: resource.uri,
      attributes: {
        classification: "public",
        status: "published",
      },
    });
    console.log("Resource updated");

    // Create policy
    console.log("Creating policy...");
    await client.createPolicy({
      policy: {
        rules: [
          {
            principal: {
              uri: principal.uri,
              attributes: {},
              type: EntityType.Principal,
            },
            resource: {
              uri: resource.uri,
              attributes: {},
              type: EntityType.Resource,
            },
          },
        ],
      },
      filename: "example-policy.json",
    });
    console.log("Policy created");

    // Delete entity
    console.log("Deleting entities...");
    await client.deleteEntity(resource.uri);
    await client.deleteEntity(principal.uri);
    console.log("Entities deleted");
  } catch (error) {
    console.error("Error:", error);
  }
}

run().catch(console.error);
