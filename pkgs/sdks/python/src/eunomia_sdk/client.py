import os

import httpx
from eunomia_core import enums, schemas


class EunomiaClient:
    """
    A client for interacting with the Eunomia server.

    This client provides methods to register resources and principals,
    and to check permissions.

    Parameters
    ----------
    endpoint : str, optional
        The base URL endpoint of the Eunomia server.
        Defaults to "http://localhost:8000" if not provided.
    api_key : str, optional
        The API key for authenticating with the server.
        Defaults to the environment variable "WAY_API_KEY" if not provided.
    """

    def __init__(self, endpoint: str | None = None, api_key: str | None = None) -> None:
        self._endpoint = endpoint if endpoint is not None else "http://localhost:8000"
        self._api_key = (
            api_key if api_key is not None else os.getenv("WAY_API_KEY", None)
        )

        headers = {}
        if self._api_key is not None:
            headers["WAY-API-KEY"] = self._api_key

        self.client = httpx.Client(base_url=self._endpoint, headers=headers, timeout=60)

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

    def check(
        self,
        principal_uri: str | None = None,
        resource_uri: str | None = None,
        principal_attributes: dict = {},
        resource_attributes: dict = {},
        action: str = "access",
    ) -> schemas.CheckResponse:
        """
        Check whether a principal has permissions to perform an action on a specific resource.

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
        action : str, optional
            The action to check permissions for. Defaults to "access".

        Returns
        -------
        schemas.CheckResponse
            The response containing the allowed flag and the reason for the decision.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        request = schemas.CheckRequest(
            principal=schemas.PrincipalCheck(
                uri=principal_uri, attributes=principal_attributes
            ),
            resource=schemas.ResourceCheck(
                uri=resource_uri, attributes=resource_attributes
            ),
            action=action,
        )
        response = self.client.post("/check", json=request.model_dump())
        self._handle_response(response)
        return schemas.CheckResponse.model_validate(response.json())

    def bulk_check(
        self, check_requests: list[schemas.CheckRequest]
    ) -> list[schemas.CheckResponse]:
        """
        Perform a set of permission checks in a single request.

        Parameters
        ----------
        check_requests : list[schemas.CheckRequest]
            The list of check requests to perform.

        Returns
        -------
        list[schemas.CheckResponse]
            The list of results of the check requests.
        """
        response = self.client.post(
            "/check/bulk",
            json=[
                schemas.CheckRequest.model_validate(request).model_dump()
                for request in check_requests
            ],
        )
        self._handle_response(response)
        return [
            schemas.CheckResponse.model_validate(result) for result in response.json()
        ]

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
            "/admin/fetchers/registry/entities", json=entity.model_dump()
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
            f"/admin/fetchers/registry/entities/{uri}",
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
        response = self.client.delete(f"/admin/fetchers/registry/entities/{uri}")
        self._handle_response(response)
        return response.json()

    def create_policy(self, request: schemas.Policy) -> schemas.Policy:
        """
        Create a new policy and store it in the Eunomia server.

        Parameters
        ----------
        request : schemas.Policy
            The policy to create.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        response = self.client.post("/admin/policies", json=request.model_dump())
        self._handle_response(response)
        return schemas.Policy.model_validate(response.json())

    def create_simple_policy(
        self, request: schemas.CheckRequest, name: str
    ) -> schemas.Policy:
        """
        Create a new simple policy with a single rule and store it in the Eunomia server.

        Parameters
        ----------
        request : schemas.CheckRequest
            The request to create the policy from.
        name : str
            The name of the policy.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        response = self.client.post(
            "/admin/policies/simple", json=request.model_dump(), params={"name": name}
        )
        self._handle_response(response)
        return schemas.Policy.model_validate(response.json())

    def get_policies(self) -> list[schemas.Policy]:
        """
        Get all policies from the Eunomia server.

        Returns
        -------
        list[schemas.Policy]
            The list of all policies.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        response = self.client.get("/admin/policies")
        self._handle_response(response)
        return [schemas.Policy.model_validate(policy) for policy in response.json()]

    def delete_policy(self, name: str) -> bool:
        """
        Delete a policy from the Eunomia server.

        Parameters
        ----------
        name : str
            The name of the policy to delete.

        Returns
        -------
        bool
            True if the policy was successfully deleted.

        Raises
        ------
        httpx.HTTPStatusError
            If the HTTP request returns an unsuccessful status code.
        """
        response = self.client.delete(f"/admin/policies/{name}")
        self._handle_response(response)
        return response.json()
