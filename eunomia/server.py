from typing import List

import httpx

from eunomia.config import settings
from eunomia.engine.opa import OpaPolicyEngine


class EunomiaServer:
    def __init__(self) -> None:
        self._engine = OpaPolicyEngine()

    async def check_access(self, principal_id: str, resource_id: str) -> bool:
        """
        Check access of the principal specified by principal_id to the resource specified by resource_id.
        This function calls the OPA server and returns the decision.
        """
        input_data = {
            "input": {"principal_id": principal_id, "resource_id": resource_id}
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self._engine.url, json=input_data)
            response.raise_for_status()
            result = response.json()
            # Assuming your policy returns a JSON structure like: {"result": {"allow": true}}
            decision = result.get("result", {}).get("allow")
            # If the decision is undefined, return False or handle it as needed.
            return bool(decision)

    async def allowed_resources(self, principal_id: str) -> List[str]:
        """
        Return the resources the principal specified by principal_id has access to.
        This function calls the OPA server and returns the list of resources.
        """
        raise NotImplementedError("Allowed resources not implemented")
