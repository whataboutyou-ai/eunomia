import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt

from eunomia.fetchers.base import BaseFetcher, BaseFetcherConfig
from eunomia.fetchers.passport.schemas import PassportJWT


class PassportFetcherConfig(BaseFetcherConfig):
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "eunomia"
    jwt_default_ttl: int = 120 * 60


class PassportFetcher(BaseFetcher):
    config: PassportFetcherConfig

    def issue_passport(
        self, uri: str, attributes: dict = {}, ttl: int | None = None
    ) -> tuple[str, str, int]:
        jti = f"psp_{uuid.uuid4().hex[:12]}"
        ttl = ttl or self.config.jwt_default_ttl
        now = datetime.now(timezone.utc)

        payload = PassportJWT(
            jti=jti,
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
        return token, jti, ttl

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
        # TODO: it is receiving a token, not a uri + should be responding with uri and attributes
        passport = self._verify_passport(uri)
        return {**passport.attr, **{"sub": passport.sub}}
