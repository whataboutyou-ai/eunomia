import asyncio

from eunomia_core import enums, schemas

from eunomia.config import settings
from eunomia.engine import PolicyEngine
from eunomia.fetchers import FetcherFactory


class EunomiaServer:
    """
    Core logic of the Eunomia Server.

    This class provides an interface to the policy engine and the attribute fetchers.
    """

    def __init__(self) -> None:
        self.engine = PolicyEngine()
        FetcherFactory.initialize_fetchers(settings.FETCHERS)
        self._fetchers = FetcherFactory.get_all_fetchers()

    async def _fetch_all_attributes(self, entity: schemas.EntityAccess) -> None:
        if entity.attributes is None:
            entity.attributes = {}

        if entity.uri is not None:
            # run all fetchers concurrently
            fetched_results = await asyncio.gather(
                *[
                    fetcher.fetch_attributes(entity.uri)
                    for fetcher in self._fetchers.values()
                    # enforce entity type if configured
                    if fetcher.config.entity_type is None
                    or fetcher.config.entity_type == entity.type
                ]
            )

            for registered_attributes in fetched_results:
                # if any attribute is colliding with the registered attributes, raise an error
                for key, value in registered_attributes.items():
                    if key in entity.attributes and entity.attributes[key] != value:
                        raise ValueError(
                            f"For entity '{entity.uri}', attribute '{key}' has more than one value"
                        )
            entity.attributes.update(registered_attributes)

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
        await asyncio.gather(
            self._fetch_all_attributes(request.principal),
            self._fetch_all_attributes(request.resource),
        )
        return self.engine.evaluate_all(request).effect == enums.PolicyEffect.ALLOW
