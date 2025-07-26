import logging
from enum import Enum

from eunomia_core import schemas
from eunomia_sdk import EunomiaClient

from eunomia.server import EunomiaServer

logger = logging.getLogger(__name__)


class EunomiaMode(Enum):
    CLIENT = "client"
    SERVER = "server"


class EunomiaBridge:
    _client: EunomiaClient | None = None
    _server: EunomiaServer | None = None

    def __init__(
        self,
        mode: EunomiaMode,
        client: EunomiaClient | None = None,
        server: EunomiaServer | None = None,
    ):
        self.mode = mode
        if mode == EunomiaMode.CLIENT:
            self._client = client or EunomiaClient()
        elif mode == EunomiaMode.SERVER:
            self._server = server or EunomiaServer()
        else:
            raise ValueError(f"Invalid mode: {mode}")

    async def check(self, request: schemas.CheckRequest) -> schemas.CheckResponse:
        if self.mode == EunomiaMode.CLIENT:
            return self._client.check(
                principal_uri=request.principal.uri,
                principal_attributes=request.principal.attributes,
                resource_uri=request.resource.uri,
                resource_attributes=request.resource.attributes,
                action=request.action,
            )
        else:
            return await self._server.check(request)

    async def bulk_check(
        self, requests: list[schemas.CheckRequest]
    ) -> list[schemas.CheckResponse]:
        if self.mode == EunomiaMode.CLIENT:
            return self._client.bulk_check(requests)
        else:
            return await self._server.bulk_check(requests)
