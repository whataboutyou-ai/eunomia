import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt

from eunomia.fetchers.base import BaseFetcher, BaseFetcherConfig
from eunomia.fetchers.factory import FetcherFactory
from eunomia.fetchers.passport.schemas import PassportJWT
from eunomia.fetchers.registry import RegistryFetcher

logger = logging.getLogger(__name__)


class PassportFetcherConfig(BaseFetcherConfig):
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "eunomia"
    jwt_default_ttl: int = 120 * 60
    requires_registry: bool = False


class PassportFetcher(BaseFetcher):
    config: PassportFetcherConfig
    _registry: RegistryFetcher | None = None

    def post_init(self) -> None:
        if self.config.requires_registry and self._registry is None:
            try:
                self._registry = FetcherFactory.get_fetcher("registry")
            except ValueError:
                raise ValueError(
                    "Passport requires registry but registry fetcher is not initialized"
                )

    def _log_issue_event(
        self,
        uri: str,
        success: bool,
        passport_id: Optional[str] = None,
        error_reason: Optional[str] = None,
    ) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()

        audit_data = {
            "timestamp": timestamp,
            "uri": uri,
            "success": success,
            "passport_id": passport_id,
            "error_reason": error_reason,
        }

        status = "SUCCESS" if success else "FAILURE"
        message = f"Passport issuance {status} for uri '{uri}'"
        if success and passport_id:
            message += f" (passport_id: {passport_id})"
        elif not success and error_reason:
            message += f" (error: {error_reason})"

        logger.info(message, extra={"audit_data": audit_data})

    def issue_passport(
        self, uri: str, attributes: dict = {}, ttl: int | None = None
    ) -> tuple[str, str, int]:
        """
        Issue a passport JWT token for the given URI.

        Parameters
        ----------
            uri: str
                The entity URI
            attributes: dict
                Additional attributes to include in the passport
            ttl: int
                Time to live in seconds (optional)

        Returns
        -------
            tuple[str, str, int]
                Tuple of (token, passport_id, ttl)
        """
        passport_id = None
        try:
            if self.config.requires_registry:
                entity = self._registry.get_entity(uri)
                if entity is None:
                    raise ValueError(
                        f"Passport cannot be issued for non-registered entity '{uri}'"
                    )
                attributes.update(entity.attributes_dict)

            passport_id = f"psp_{uuid.uuid4().hex[:12]}"
            ttl = ttl or self.config.jwt_default_ttl
            now = datetime.now(timezone.utc)

            payload = PassportJWT(
                jti=passport_id,
                iat=int(now.timestamp()),
                exp=int((now + timedelta(seconds=ttl)).timestamp()),
                iss=self.config.jwt_issuer,
                sub=uri,
                attr=attributes,
            )

            token = jwt.encode(
                payload.model_dump(),
                self.config.jwt_secret,
                algorithm=self.config.jwt_algorithm,
            )

            self._log_issue_event(uri=uri, success=True, passport_id=passport_id)

            return token, passport_id, ttl

        except Exception as e:
            self._log_issue_event(
                uri=uri, success=False, passport_id=passport_id, error_reason=str(e)
            )
            raise

    def _verify_passport(self, token: str) -> PassportJWT:
        return PassportJWT.model_validate(
            jwt.decode(
                token,
                self.config.jwt_secret,
                algorithms=[self.config.jwt_algorithm],
                issuer=self.config.jwt_issuer,
            )
        )

    async def fetch_attributes(self, uri: str) -> dict:
        # this fetcher is receiving the access token as uri
        passport = self._verify_passport(uri)
        # currently returns the uri as an additional attribute
        return {**passport.attr, "uri": passport.sub}
