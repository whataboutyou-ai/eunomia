import os

import httpx
from eunomia_core import enums, schemas


class EunomiaClient:
    """
    A client for interacting with the Eunomia server.

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

    def _handle_response(self, response: httpx.Response) -> None:
        try:
            response.raise_for_status()
            return
        except httpx.HTTPStatusError as e:
            raise httpx.HTTPStatusError(
                f"{e}\nResponse: {e.response.text}",
                request=e.request,
                response=e.response,
            ) from None

    def check_access(
        self,
        principal_uri: str | None = None,
        resource_uri: str | None = None,
        principal_attributes: dict = {},
        resource_attributes: dict = {},
    ) -> bool:
        """
        Check whether a principal has access to a specific resource.

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
            principal=schemas.PrincipalAccess(
                uri=principal_uri, attributes=principal_attributes
            ),
            resource=schemas.ResourceAccess(
                uri=resource_uri, attributes=resource_attributes
            ),
        )
        response = self.client.post("/check-access", json=request.model_dump())
        self._handle_response(response)
        return bool(response.json())

    def register_entity(
        self, type: enums.EntityType, attributes: dict, uri: str | None = None
    ) -> schemas.EntityInDb:
        """
        Register a new entity with the Eunomia server.

        This method registers a new entity with its attributes to the Eunomia server.
        If no uri identifier is provided, the server will generate a random UUID.

        Parameters
        ----------
        type : enums.EntityType
            The type of entity to register. Either "resource" or "principal".
        attributes : dict
            The attributes to associate with the entity.
        uri : str | None, optional
            The uri for the entity. If not provided, the server will generate a random UUID.

        Returns
        -------
        schemas.EntityInDb
            The newly registered entity.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        entity = schemas.EntityCreate(type=type, attributes=attributes, uri=uri)
        response = self.client.post(
            "/fetchers/internal/entities", json=entity.model_dump()
        )
        self._handle_response(response)
        return schemas.EntityInDb.model_validate(response.json())

    def update_entity(
        self, uri: str, attributes: dict, override: bool = False
    ) -> schemas.EntityInDb:
        """
        Update the attributes of an existing entity.

        Parameters
        ----------
        uri : str
            The uri of the entity to update.
        attributes : dict
            The attributes to update.
        override : bool, default=False
            If True, the existing attributes are deleted and the new attributes are added.
            If False, the existing attributes are maintaned or updated in case of overlap,
            and the additional new attributes are added.

        Returns
        -------
        schemas.EntityInDb
            The updated entity.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        entity = schemas.EntityUpdate(uri=uri, attributes=attributes)
        response = self.client.put(
            f"/fetchers/internal/entities/{uri}",
            json=entity.model_dump(),
            params={"override": override},
        )
        self._handle_response(response)
        return schemas.EntityInDb.model_validate(response.json())

    def delete_entity(self, uri: str) -> bool:
        """
        Delete an entity from the Eunomia server.

        Parameters
        ----------
        uri : str
            The uri of the entity to delete.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        response = self.client.delete(f"/fetchers/internal/entities/{uri}")
        self._handle_response(response)
        return response.json()

    def create_policy(
        self, request: schemas.AccessRequest, name: str
    ) -> schemas.Policy:
        """
        Create a new policy and store it in the Eunomia server.

        Parameters
        ----------
        request : schemas.AccessRequest
            The request to create the policy from.
        name : str
            The name of the policy.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        response = self.client.post(
            "/policies", json=request.model_dump(), params={"name": name}
        )
        self._handle_response(response)
        return schemas.Policy.model_validate(response.json())
