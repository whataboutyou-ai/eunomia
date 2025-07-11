from fastapi import APIRouter

from eunomia.fetchers.passport import PassportFetcher
from eunomia.fetchers.passport.schemas import (
    PassportIssueRequest,
    PassportIssueResponse,
)


def passport_router_factory(fetcher: PassportFetcher) -> APIRouter:
    router = APIRouter()

    @router.post("/issue", response_model=PassportIssueResponse)
    async def issue_passport(request: PassportIssueRequest):
        token, jti, ttl = fetcher.issue_passport(**request.model_dump())
        return PassportIssueResponse(passport=token, passport_id=jti, expires_in=ttl)

    return router
