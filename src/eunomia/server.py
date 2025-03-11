import uuid
from typing import List

import httpx

from eunomia.db import crud, db, schemas
from eunomia.engine.opa import OpaPolicyEngine


class EunomiaServer:
    """
    Core logic of the Eunomia Server.

    This class provides an interface to the Open Policy Agent (OPA) engine
    for making access control decisions and managing resources and principals.
    """

    def __init__(self) -> None:
        self._engine = OpaPolicyEngine()

    async def check_access(
        self, principal_id: str, resource_id: str, access_method: str = "allow"
    ) -> bool:
        """
        Check if a principal has access to a specific resource.

        This method first get resource and principals metadata and then
        queries the OPA server to determine if the specified principal
        is allowed to access the specified resource.

        Parameters
        ----------
        principal_id : str
            Unique identifier for the principal requesting access.
        resource_id : str
            Unique identifier for the resource being accessed.
        access_method : str, optional
            The type of access to check. Currently only "allow" is supported.

        Returns
        -------
        bool
            True if access is granted, False otherwise.

        Raises
        ------
        NotImplementedError
            If access_method is not "allow".
        httpx.HTTPError
            If communication with the OPA server fails.
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
        raise NotImplementedError("Allowed resources not implemented")

    async def register_resource(
        self, metadata: dict, content: str | None = None
    ) -> str:
        """
        Register a new resource in the system.

        Creates a new resource with the provided metadata and content,
        generating a unique identifier for future reference.

        Parameters
        ----------
        metadata : dict
            Dictionary containing metadata about the resource.
        content : str, optional, default=None
            The content of the resource as a string.

        Returns
        -------
        str
            The generated unique identifier (eunomia_id) for the resource.
        """
        new_resource = schemas.ResourceCreate(metadatas=metadata, content=content)
        db_session = next(db.get_db())
        eunomia_id = str(uuid.uuid4())
        crud.create_resource(new_resource, eunomia_id, db=db_session)
        return eunomia_id

    async def register_principal(self, metadata: dict) -> str:
        """
        Register a new principal in the system.

        Creates a new principal with the provided metadata,
        generating a unique identifier for future reference.

        Parameters
        ----------
        metadata : dict
            Dictionary containing metadata about the principal.

        Returns
        -------
        str
            The generated unique identifier (eunomia_id) for the principal.
        """
        new_principal = schemas.PrincipalCreate(metadatas=metadata)
        db_session = next(db.get_db())
        eunomia_id = str(uuid.uuid4())
        crud.create_principal(new_principal, eunomia_id, db=db_session)
        return eunomia_id
