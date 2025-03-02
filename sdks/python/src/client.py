import os

import httpx


class EunomiaClient:
    def __init__(self, api_key: str = None, server_host: str = None) -> None:
        self.api_key = (
            api_key if api_key is not None else os.getenv("WAY_API_KEY", None)
        )
        self.server_host = (
            server_host if server_host is not None else "http://localhost:8000"
        )

        self.client = httpx.Client(
            base_url=self.server_host,
            headers={"WAY-API-KEY": self.api_key},
            timeout=60,
        )

    def check_access(self, principal_id: str, resource_id: str) -> bool:
        """Check access of the principal specified by the principal_id to the resource specified by the resource_id"""
        response = self.client.get("/check_access/")
        response.raise_for_status()
        return response.json()

    def allowed_resources(self, principal_id: str) -> list[str]:
        """Return the resources the principal specified by the principal_id has access to"""
        response = self.client.get("/allowed_resources/")
        response.raise_for_status()
        return response.json()
