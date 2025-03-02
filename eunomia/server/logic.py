import httpx
from typing import List
from eunomia.server.config import settings

async def check_access_logic(principal_id: str, resource_id: str) -> bool:
    """
    Check access of the principal specified by principal_id to the resource specified by resource_id.
    This function calls the OPA server and returns the decision.
    """
    input_data = {
        "input": {
            "principal_id": principal_id,
            "resource_id": resource_id
        }
    }
    async with httpx.AsyncClient() as client:
        # Call the decision endpoint for check_access.
        # Adjust the URL path ('/v1/data/example/check_access') to match your policy.
        response = await client.post(
            f"http://{settings.OPA_SERVER_URL}:{settings.OPA_SERVER_PORT}/v1/data/example/check_access",
            json=input_data
        )
        response.raise_for_status()
        result = response.json()
        # Assuming your policy returns a JSON structure like: {"result": {"allow": true}}
        decision = result.get("result", {}).get("allow")
        # If the decision is undefined, return False or handle it as needed.
        return bool(decision)




async def allowed_resources_logic(principal_id: str) -> List[str]:
    """
    Return the resources the principal specified by principal_id has access to.
    This function calls the OPA server and returns the list of resources.
    """
    input_data = {
        "input": {
            "principal_id": principal_id
        }
    }
    async with httpx.AsyncClient() as client:
        # Call the decision endpoint for allowed_resources.
        # Adjust the URL path ('/v1/data/example/allowed_resources') to match your policy.
        response = await client.post(
            f"http://{settings.OPA_SERVER_URL}:{settings.OPA_SERVER_PORT}/v1/data/example/allowed_resources",
            json=input_data
        )
        response.raise_for_status()
        result = response.json()
        # Assuming your policy returns a structure like: {"result": ["resource1", "resource2"]}
        allowed = result.get("result", [])
        if not isinstance(allowed, list):
            raise ValueError("Unexpected response format from OPA.")
        return allowed
