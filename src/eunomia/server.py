import uuid
from typing import List

import httpx

from eunomia.db import crud, db, schemas
from eunomia.engine.opa import OpaPolicyEngine


class EunomiaServer:
    def __init__(self) -> None:
        self._engine = OpaPolicyEngine()

    async def check_access(
        self, principal_id: str, resource_id: str, access_method: str = "allow"
    ) -> bool:
        """
        Check access of the principal specified by principal_id to the resource specified by resource_id.
        This function calls the OPA server and returns the decision.
        """
        if access_method != "allow":
            raise NotImplementedError("Only allow method is supported")

        ## Get principal and resource metadata
        db_session = next(db.get_db())
        resource_metadata = crud.get_resource_metadata(resource_id, db_session)
        principal_metadata = crud.get_principal_metadata(principal_id, db_session)

        input_data = {
            "input": {
                "principal": {
                    "eunomia_id": principal_id,
                    "metadata": principal_metadata,
                },
                "resource": {"eunomia_id": resource_id, "metadata": resource_metadata},
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._engine.url}/{access_method}", json=input_data
            )
            response.raise_for_status()
            result = response.json()
            decision = result.get("result", False)
            return bool(decision)

    async def allowed_resources(self, principal_id: str) -> List[str]:
        """
        Return the resources the principal specified by principal_id has access to.
        This function calls the OPA server and returns the list of resources.
        """
        raise NotImplementedError("Allowed resources not implemented")

    async def register_resource(
        self, resource_metadata: dict, resource_content: str
    ) -> str:
        """
        Register a new resource on the server
        """
        new_resource = schemas.ResourceCreate(
            metadatas=resource_metadata, content=resource_content
        )
        db_session = next(db.get_db())
        eunomia_id = str(uuid.uuid4())
        crud.create_resource(new_resource, eunomia_id, db=db_session)
        return eunomia_id

    async def register_principal(self, principal_metadata: dict) -> str:
        """
        Register a new principal on the server
        """
        new_principal = schemas.PrincipalCreate(metadatas=principal_metadata)
        db_session = next(db.get_db())
        eunomia_id = str(uuid.uuid4())
        crud.create_principal(new_principal, eunomia_id, db=db_session)
        return eunomia_id
