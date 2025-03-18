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
        """
        principal_attributes = {}
        if request.principal.uri is not None:
            principal_attributes.update(
                crud.get_entity_attributes(request.principal.uri, db=db)
            )
        if request.principal.attributes:
            principal_attributes.update(
                {item.key: item.value for item in request.principal.attributes}
            )

        resource_attributes = {}
        if request.resource.uri is not None:
            resource_attributes.update(
                crud.get_entity_attributes(request.resource.uri, db=db)
            )
        if request.resource.attributes:
            resource_attributes.update(
                {item.key: item.value for item in request.resource.attributes}
            )

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
        print(input_data)

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
