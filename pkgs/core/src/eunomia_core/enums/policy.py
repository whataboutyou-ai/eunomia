from enum import Enum


class PolicyEffect(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


class ConditionOperator(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    # String operators
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "startswith"
    ENDS_WITH = "endswith"
    # Number operators
    GREATER = "gt"
    GREATER_OR_EQUAL = "gte"
    LESS = "lt"
    LESS_OR_EQUAL = "lte"
    # List operators
    IN = "in"
    NOT_IN = "not_in"
    SUBSET = "subset"
    NOT_SUBSET = "not_subset"
    SUPERSET = "superset"
    NOT_SUPERSET = "not_superset"
