from typing import List

import httpx
from eunomia_core import enums, schemas
from sqlalchemy.orm import Session

from eunomia.db import crud
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
        self,
        principal_uri: str,
        resource_uri: str,
        db: Session,
        access_method: str = "allow",
    ) -> bool:
        """
        Check if a principal has access to a specific resource.

        This method first get resource and principals attributes and then
        queries the OPA server to determine if the specified principal
        is allowed to access the specified resource.

        Parameters
        ----------
        principal_uri : str
            Unique identifier for the principal requesting access.
        resource_uri : str
            Unique identifier for the resource being accessed.
        db : Session
            The SQLAlchemy database session.
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

        ## Get principal and resource attributes
        resource_attributes = crud.get_entity_attributes(resource_uri, db=db)
        principal_attributes = crud.get_entity_attributes(principal_uri, db=db)

        input_data = {
            "input": {
                "principal": {
                    "uri": principal_uri,
                    "attributes": principal_attributes,
                },
                "resource": {
                    "uri": resource_uri,
                    "attributes": resource_attributes,
                },
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

    async def allowed_resources(self, principal_uri: str) -> List[str]:
        raise NotImplementedError("Allowed resources not implemented")

    async def register_resource(self, attributes: dict, db: Session) -> str:
        """
        Register a new resource in the system.

        Creates a new resource with the provided attributes,
        generating a unique identifier for future reference.

        Parameters
        ----------
        attributes : dict
            Dictionary containing attributes about the resource.
        db : Session
            The SQLAlchemy database session.

        Returns
        -------
        str
            The generated unique identifier for the resource.
        """
        resource = schemas.EntityCreate(
            type=enums.EntityType.resource, attributes=attributes
        )
        _ = crud.create_entity(resource, db=db)
        return resource.uri

    async def register_principal(self, attributes: dict, db: Session) -> str:
        """
        Register a new principal in the system.

        Creates a new principal with the provided attributes,
        generating a unique identifier for future reference.

        Parameters
        ----------
        attributes : dict
            Dictionary containing attributes about the principal.
        db : Session
            The SQLAlchemy database session.

        Returns
        -------
        str
            The generated unique identifier for the principal.
        """
        principal = schemas.EntityCreate(
            type=enums.EntityType.principal, attributes=attributes
        )
        _ = crud.create_entity(principal, db=db)
        return principal.uri
