import os

import httpx
from eunomia_core import enums, schemas


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

    def check_access(
        self,
        principal_uri: str | None = None,
        resource_uri: str | None = None,
        principal_attributes: dict = {},
        resource_attributes: dict = {},
    ) -> bool:
        """Check whether a principal has access to a specific resource.

        Parameters
        ----------
        principal_uri : str, optional
            The identifier of the principal. Can be provided for registered principals to automatically retrieve attributes.
        resource_uri : str, optional
            The identifier of the resource. Can be provided for registered resources to automatically retrieve attributes.
        principal_attributes : dict, optional
            The attributes of the principal. Shall be provided if the principal is not registered.
        resource_attributes : dict, optional
            The attributes of the resource. Shall be provided if the resource is not registered.

        Returns
        -------
        bool
            True if the principal has access to the resource, False otherwise.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        request = schemas.AccessRequest(
            principal=schemas.PrincipalRequest(
                uri=principal_uri, attributes=principal_attributes
            ),
            resource=schemas.ResourceRequest(
                uri=resource_uri, attributes=resource_attributes
            ),
        )
        response = self.client.post("/check-access", json=request.model_dump())
        response.raise_for_status()
        return bool(response.json())

    def register_entity(
        self, type: enums.EntityType, attributes: dict, uri: str | None = None
    ) -> schemas.EntityResponse:
        """Register a new entity with the Eunomia server.

        This method registers a new entity with its attributes to the Eunomia server.
        If no uri identifier is provided, the server will generate a random UUID.

        Parameters
        ----------
        type : enums.EntityType
            The type of entity to register. Either "resource", "principal" or "any".
        attributes : dict
            The attributes to associate with the entity.
        uri : str | None, optional
            The uri for the entity. If not provided, the server will generate a random UUID.

        Returns
        -------
        schemas.EntityResponse
            The newly registered entity.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        entity = schemas.EntityRequest(type=type, attributes=attributes, uri=uri)
        response = self.client.post("/register-entity", json=entity.model_dump())
        response.raise_for_status()
        return schemas.EntityResponse.model_validate(response.json())
