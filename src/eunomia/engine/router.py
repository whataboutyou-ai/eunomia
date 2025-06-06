from eunomia_core import enums, schemas
from fastapi import APIRouter, HTTPException, status

from eunomia.engine import PolicyEngine, utils


def engine_router_factory(engine: PolicyEngine) -> APIRouter:
    router = APIRouter()

    @router.get("/policies", response_model=list[schemas.Policy])
    async def get_policies():
        return engine.get_policies()

    @router.post("/policies", response_model=schemas.Policy)
    async def create_policy(request: schemas.Policy):
        engine.add_policy(request)
        return request

    @router.post("/policies/simple", response_model=schemas.Policy)
    async def create_simple_policy(request: schemas.CheckRequest, name: str):
        policy = utils.create_simple_policy(
            name=name,
            principal_attributes=request.principal.attributes,
            resource_attributes=request.resource.attributes,
            actions=[request.action],
            effect=enums.PolicyEffect.ALLOW,
        )
        engine.add_policy(policy)
        return policy

    @router.get("/policies/{name}", response_model=schemas.Policy)
    async def get_policy(name: str):
        policy = engine.get_policy(name)
        if policy is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found"
            )
        return policy

    @router.delete("/policies/{name}", response_model=bool)
    async def delete_policy(name: str):
        return engine.remove_policy(name)

    return router
