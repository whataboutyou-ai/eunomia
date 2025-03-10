import os

import httpx


class EunomiaClient:
    """A client for interacting with the Eunomia server.

    This client provides methods to register resources and principals,
    check access permissions, and retrieve allowed resources for a principal.

    Parameters
    ----------
    server_host : str, optional
        The base URL of the Eunomia server.
        Defaults to "http://localhost:8000" if not provided.
    api_key : str, optional
        The API key for authenticating with the server.
        Defaults to the environment variable "WAY_API_KEY" if not provided.
    """

    def __init__(
        self, server_host: str | None = None, api_key: str | None = None
    ) -> None:
        self._server_host = (
            server_host if server_host is not None else "http://localhost:8000"
        )
        self._api_key = (
            api_key if api_key is not None else os.getenv("WAY_API_KEY", None)
        )

        headers = {}
        if self._api_key is not None:
            headers["WAY-API-KEY"] = self._api_key

        self.client = httpx.Client(
            base_url=self._server_host,
            headers=headers,
            timeout=60,
        )

    def check_access(self, principal_id: str, resource_id: str) -> bool:
        """Check whether a principal has access to a specific resource.

        Parameters
        ----------
        principal_id : str
            The identifier of the principal.
        resource_id : str
            The identifier of the resource.

        Returns
        -------
        bool
            True if the principal has access to the resource, False otherwise.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        params = {"principal_id": principal_id, "resource_id": resource_id}
        response = self.client.get("/check-access", params=params)
        response.raise_for_status()
        return response.json()

    def register_principal(self, metadatas: dict) -> dict:
        """Register a new principal with the Eunomia server and obtain its Eunomia ID.

        Parameters
        ----------
        metadatas : dict
            A dictionary containing metadata for the principal.

        Returns
        -------
        dict
            The JSON response from the server, including the newly registered principal's Eunomia ID.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        json_body = {"metadata": metadatas}
        response = self.client.post("/register_principal", json=json_body)
        response.raise_for_status()
        return response.json()

    def register_resource(self, metadatas: dict) -> dict:
        """Register a new resource with the Eunomia server and obtain its Eunomia ID.

        Parameters
        ----------
        metadatas : dict
            A dictionary containing metadata for the resource.

        Returns
        -------
        dict
            The JSON response from the server, including the newly registered resource's Eunomia ID.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        json_body = {"metadata": metadatas}
        response = self.client.post("/register_resource", json=json_body)
        response.raise_for_status()
        return response.json()

    # TODO: Change output function once defined Resource
    def allowed_resources(self, principal_id: str) -> list[str]:
        """Retrieve a list of resources that the specified principal has access to.

        Parameters
        ----------
        principal_id : str
            The identifier of the principal.

        Returns
        -------
        list[str]
            A list of resource identifiers that the principal can access.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        params = {"principal_id": principal_id}
        response = self.client.get("/allowed-resources", params=params)
        response.raise_for_status()
        return response.json()
