from eunomia_core import schemas

from eunomia.config import settings
from eunomia.engine.opa import OpaPolicyEngine
from eunomia.fetchers import FetcherFactory


class EunomiaServer:
    """
    Core logic of the Eunomia Server.

    This class provides an interface to the policy engine and the attribute fetchers.
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

        This method first fetch resource and principals attributes and then
        queries the policy engine to determine if the specified principal
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
        ValueError
            If there is a discrepancy between the provided attributes and the registered attributes.
        """
        updated_request = request.model_copy(
            update=schemas.AccessRequest(
                principal=request.principal.model_copy(
                    update=schemas.PrincipalAccess(
                        attributes=self._get_merged_attributes(request.principal)
                    )
                ),
                resource=request.resource.model_copy(
                    update=schemas.ResourceAccess(
                        attributes=self._get_merged_attributes(request.resource)
                    )
                ),
            )
        )
        return await self._engine.check_access(updated_request)

    def create_policy(self, policy: schemas.Policy, filename: str) -> str:
        """
        Create a new policy and store it in the engine.

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
        return self._engine.create_policy(policy, filename)
