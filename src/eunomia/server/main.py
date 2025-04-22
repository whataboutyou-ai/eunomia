import logging
import os

import httpx
from eunomia_core import schemas

from eunomia.config import settings
from eunomia.engine.opa import OpaPolicyEngine
from eunomia.engine.rego import policy_to_rego
from eunomia.fetchers import FetcherFactory


class EunomiaServer:
    """
    Core logic of the Eunomia Server.

    This class provides an interface to the Open Policy Agent (OPA) engine
    for making access control decisions and managing resources and principals.
    """

    def __init__(self) -> None:
        self._engine = OpaPolicyEngine()
        FetcherFactory.initialize_fetchers(settings.FETCHERS)
        self._fetchers = FetcherFactory.get_all_fetchers()

    def _get_merged_attributes(self, entity: schemas.EntityAccess) -> dict:
        merged_attributes = {item.key: item.value for item in entity.attributes}

        if entity.uri is not None:
            for fetcher in self._fetchers.values():
                registered_attributes = fetcher.fetch_attributes(entity.uri)

                # if any attribute is colliding with the registered attributes, raise an error
                for key, value in registered_attributes.items():
                    if key in merged_attributes and merged_attributes[key] != value:
                        raise ValueError(
                            f"For entity '{entity.uri}', attribute '{key}' has more than one value"
                        )
                merged_attributes.update(registered_attributes)

        return merged_attributes

    async def check_access(self, request: schemas.AccessRequest) -> bool:
        """
        Check if a principal has access to a specific resource.

        This method first get resource and principals attributes and then
        queries the OPA server to determine if the specified principal
        is allowed to access the specified resource.

        Parameters
        ----------
        request : schemas.AccessRequest
            The access request to check, containing the principal requesting access and the resource being accessed.
            Both entities can be specified either by their registered identifier, by their attributes or by both.

        Returns
        -------
        bool
            True if access is granted, False otherwise.

        Raises
        ------
        httpx.HTTPError
            If communication with the OPA server fails.
        ValueError
            If there is a discrepancy between the provided attributes and the registered attributes.
        """
        principal_attributes = self._get_merged_attributes(request.principal)
        resource_attributes = self._get_merged_attributes(request.resource)

        input_data = {
            "input": {
                "principal": {
                    "uri": request.principal.uri,
                    "attributes": principal_attributes,
                },
                "resource": {
                    "uri": request.resource.uri,
                    "attributes": resource_attributes,
                },
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._engine.url}/{request.action}", json=input_data
            )
            response.raise_for_status()
            result = response.json()
            decision = result.get("result", False)
            return bool(decision)

    def create_policy(self, policy: schemas.Policy, filename: str) -> str:
        """
        Create a new policy and save it to the local file system.

        Parameters
        ----------
        policy : schemas.Policy
            The policy to create, containing a list of access rules.
            Rules are evaluated with OR logic (access is granted if ANY rule matches).
            Within each rule, attributes for both principal and resource are evaluated
            with AND logic (all specified attributes must match).
        filename : str
            The filename of the policy to create.

        Returns
        -------
        str
            The path to the created policy.

        Raises
        ------
        ValueError
            If the policy file already exists.
        """
        if not os.path.exists(self._engine.policy_folder):
            os.makedirs(self._engine.policy_folder)
            logging.info(
                f"Policy folder did not exist, created it at {self._engine.policy_folder}"
            )

        path = os.path.join(self._engine.policy_folder, filename)
        if os.path.exists(path):
            logging.warning(
                f"Policy file '{filename}' already exists at {self._engine.policy_folder}"
            )

        policy_rego = policy_to_rego(policy)
        with open(path, "w") as f:
            f.write(policy_rego)
        return path
