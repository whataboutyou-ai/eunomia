from jose import jwt

from eunomia.fetchers.base import BaseFetcher, BaseFetcherConfig
from eunomia.fetchers.passport.schemas import PassportJWT


class PassportFetcherConfig(BaseFetcherConfig):
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_default_ttl: int = 120 * 60


class PassportFetcher(BaseFetcher):
    config: PassportFetcherConfig

    def _verify_passport(self, token: str) -> PassportJWT:
        return PassportJWT.model_validate(
            jwt.decode(
                token, self.config.jwt_secret, algorithms=[self.config.jwt_algorithm]
            )
        )

    async def fetch_attributes(self, uri: str) -> dict:
        # TODO: it is receiving a token, not a uri + should be responding with uri and attributes
        passport = self._verify_passport(uri)
        return {**passport.attr, **{"sub": passport.sub}}
