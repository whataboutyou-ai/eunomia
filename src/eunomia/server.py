import uuid
from typing import List

import httpx
from eunomia_core import schemas
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

    def _get_merged_attributes(self, entity: schemas.EntityAccess, db: Session) -> dict:
        attributes = {}

        if entity.uri is not None:
            registered_attributes = crud.get_entity_attributes(entity.uri, db=db)
            # if any attribute is colliding with the registered attributes, raise an error
            for attribute in entity.attributes:
                if (
                    attribute.key in registered_attributes
                    and registered_attributes[attribute.key] != attribute.value
                ):
                    raise ValueError(
                        f"For entity '{entity.uri}', attribute '{attribute.key}' has a collision with the registered attributes"
                    )
            attributes.update(registered_attributes)

        if entity.attributes:
            attributes.update({item.key: item.value for item in entity.attributes})
        return attributes

    async def check_access(self, request: schemas.AccessRequest, db: Session) -> bool:
        """
        Check if a principal has access to a specific resource.

        This method first get resource and principals attributes and then
        queries the OPA server to determine if the specified principal
        is allowed to access the specified resource.

        Parameters
        ----------
        request : schemas.AccessRequest
            The access request to check, containing the principal requesting access and the resource being accessed.
            Both entities can be specified either by their registered identifier, by their attributes or by both.
        db : Session
            The SQLAlchemy database session.

        Returns
        -------
        bool
            True if access is granted, False otherwise.

        Raises
        ------
        httpx.HTTPError
            If communication with the OPA server fails.
        ValueError
            If there is a discrepancy between the provided attributes and the registered attributes.
        """
        principal_attributes = self._get_merged_attributes(request.principal, db=db)
        resource_attributes = self._get_merged_attributes(request.resource, db=db)

        input_data = {
            "input": {
                "principal": {
                    "uri": request.principal.uri,
                    "attributes": principal_attributes,
                },
                "resource": {
                    "uri": request.resource.uri,
                    "attributes": resource_attributes,
                },
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._engine.url}/{request.action}", json=input_data
            )
            response.raise_for_status()
            result = response.json()
            decision = result.get("result", False)
            return bool(decision)

    async def allowed_resources(self, principal_uri: str) -> List[str]:
        raise NotImplementedError("Allowed resources not implemented")

    def register_entity(
        self, entity: schemas.EntityCreate, db: Session
    ) -> schemas.EntityInDb:
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
        schemas.EntityInDb
            The generated entity as a Pydantic model.

        Raises
        ------
        ValueError
            If the entity is already registered.
        """
        if entity.uri is None:
            entity.uri = str(uuid.uuid4())

        db_entity = crud.get_entity(entity.uri, db=db)
        if db_entity is not None:
            raise ValueError(f"Entity with uri '{entity.uri}' is already registered")

        db_entity = crud.create_entity(entity, db=db)
        return schemas.EntityInDb.model_validate(db_entity)
