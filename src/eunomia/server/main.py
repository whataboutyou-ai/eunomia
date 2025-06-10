import asyncio

from eunomia_core import schemas

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

    async def _fetch_all_attributes(self, entity: schemas.EntityCheck) -> None:
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

    async def check(self, request: schemas.CheckRequest) -> schemas.CheckResponse:
        """
        Check if a principal has permissions to perform an action on a specific resource.

        This method first fetches resource and principals attributes from all configured
        fetchers and then queries the engine to evaluate policies.

        Parameters
        ----------
        request : schemas.CheckRequest
            The check request containing the principal, the action and the resource.
            Both principal and resource can be specified either by uri, by their attributes
            or a combination of both.

        Returns
        -------
        schemas.CheckResponse
            The response containing the allowed flag and the reason for the decision.

        Raises
        ------
        ValueError
            If there is a discrepancy between the provided attributes and the fetched attributes.
        """
        await asyncio.gather(
            self._fetch_all_attributes(request.principal),
            self._fetch_all_attributes(request.resource),
        )
        return self.engine.evaluate_all(request)
