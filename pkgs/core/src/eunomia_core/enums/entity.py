from enum import Enum


class EntityType(str, Enum):
    resource = "resource"
    principal = "principal"
