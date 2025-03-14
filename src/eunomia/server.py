from typing import List

import httpx
from eunomia_core import schemas
from sqlalchemy.orm import Session

from eunomia.db import crud, models
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

    def register_entity(
        self, entity: schemas.EntityCreate, db: Session
    ) -> models.Entity:
        """
        Register a new entity in the system.

        Creates a new entity with the provided attributes,
        generating a unique identifier for future reference,
        if not provided.

        Parameters
        ----------
        entity : schemas.EntityCreate
            Pydantic model containing attributes about the entity.
        db : Session
            The SQLAlchemy database session.

        Returns
        -------
        models.Entity
            The generated entity.

        Raises
        ------
        ValueError
            If the entity is already registered.
        """
        db_entity = crud.get_entity(entity.uri, db=db)
        if db_entity is not None:
            raise ValueError(f"Entity with uri '{entity.uri}' is already registered")
        db_entity = crud.create_entity(entity, db=db)
        return db_entity
