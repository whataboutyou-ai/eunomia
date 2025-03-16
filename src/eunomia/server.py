import uuid
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
        principal: schemas.PrincipalRequest,
        resource: schemas.ResourceRequest,
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
        principal : schemas.PrincipalRequest
            The principal requesting access, either through it's registered identifier or its attributes.
        resource : schemas.ResourceRequest
            The resource being accessed, either through it's registered identifier or its attributes.
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

        principal_attributes = {}
        if principal.attributes:
            principal_attributes.update(
                {item.key: item.value for item in principal.attributes}
            )
        if principal.uri is not None:
            principal_attributes.update(
                crud.get_entity_attributes(principal.uri, db=db)
            )

        resource_attributes = {}
        if resource.attributes:
            resource_attributes.update(
                {item.key: item.value for item in resource.attributes}
            )
        if resource.uri is not None:
            resource_attributes.update(crud.get_entity_attributes(resource.uri, db=db))

        input_data = {
            "input": {
                "principal": {
                    "uri": principal.uri,
                    "attributes": principal_attributes,
                },
                "resource": {
                    "uri": resource.uri,
                    "attributes": resource_attributes,
                },
            }
        }
        print(input_data)

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
        self, entity: schemas.EntityRequest, db: Session
    ) -> models.Entity:
        """
        Register a new entity in the system.

        Creates a new entity with the provided attributes,
        generating a unique identifier for future reference,
        if not provided.

        Parameters
        ----------
        entity : schemas.EntityRequest
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
        if entity.uri is None:
            entity.uri = str(uuid.uuid4())
        else:
            db_entity = crud.get_entity(entity.uri, db=db)
            if db_entity is not None:
                raise ValueError(
                    f"Entity with uri '{entity.uri}' is already registered"
                )

        db_entity = crud.create_entity(entity, db=db)
        return db_entity
