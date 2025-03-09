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

        headers = {}
        if self.api_key is not None:
            headers["WAY-API-KEY"] = self.api_key

        self.client = httpx.Client(
            base_url=self.server_host,
            headers=headers,
            timeout=60,
        )

    def check_access(self, principal_id: str, resource_id: str) -> bool:
        """Check access of the principal specified by the principal_id to the resource specified by the resource_id"""
        params = {"principal_id": principal_id, "resource_id": resource_id}
        response = self.client.get("/check-access", params=params)
        response.raise_for_status()
        return response.json()

    def register_principal(self, metadatas: dict) -> dict:
        """Register a new principal to the server and obtain a eunomia ID for the principal"""
        json_body = {"metadata": metadatas}
        response = self.client.post("/register_principal", json=json_body)
        response.raise_for_status()
        return response.json()

    def register_resource(self, metadatas: dict) -> dict:
        """Register a new resource to the server and obtain a eunomia ID for the resource"""
        json_body = {"metadata": metadatas}
        response = self.client.post("/register_resource", json=json_body)
        response.raise_for_status()
        return response.json()

    # TODO: Change output function once defined Resource
    def allowed_resources(self, principal_id: str) -> list[str]:
        """Return the resources the principal specified by the principal_id has access to"""
        params = {
            "principal_id": principal_id,
        }
        response = self.client.get("/allowed-resources", params=params)
        response.raise_for_status()
        return response.json()
