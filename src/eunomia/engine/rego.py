"""
Rego Policy Conversion Module

This module provides functionality to convert Eunomia policy definitions into Rego language for use with OPA (Open Policy Agent).

Since Eunomia uses OPA as its policy enforcement engine, policies defined using the Eunomia schema need to be
translated into Rego - OPA's native policy language. This module handles this conversion process.

Example Rego Output:
------------------------
```
package eunomia

default allow := false

# Rule allowing admin access to documents
allow if {
    input.principal.attributes.role == "admin"
    input.resource.attributes.type == "document"
}

# Rule allowing members to access public documents
allow if {
    input.principal.attributes.role == "member"
    input.resource.attributes.type == "document"
    input.resource.attributes.confidentiality == "public"
}
```

Note: In Rego, multiple allow blocks represent OR conditions, while statements within a block
represent AND conditions. The policy evaluates to "allow := true" if any rule block is satisfied.
"""

from eunomia_core import schemas

EQUAL_URI_STMNT = '	input.{type}.uri == "{uri}"'
EQUAL_ATTRIBUTE_STMNT = '	input.{type}.attributes.{key} == "{value}"'
ALLOW_RULE_STMNT = "allow if {{\n{entity_stmts}\n}}"
ALLOW_POLICY_STMNT = "package eunomia\n\ndefault allow := false\n\n{rules}\n"


def entity_to_rego(entity: schemas.EntityAccess) -> str:
    uri_stmt = (
        [EQUAL_URI_STMNT.format(type=entity.type.value, uri=entity.uri)]
        if entity.uri
        else []
    )
    attribute_stmts = [
        EQUAL_ATTRIBUTE_STMNT.format(
            type=entity.type.value, key=attribute.key, value=attribute.value
        )
        for attribute in entity.attributes
    ]
    return "\n".join(uri_stmt + attribute_stmts)


def access_rule_to_rego(rule: schemas.AccessRequest) -> str:
    rego_items = "\n".join(
        [entity_to_rego(rule.principal), entity_to_rego(rule.resource)]
    )
    return ALLOW_RULE_STMNT.format(entity_stmts=rego_items)


def policy_to_rego(policy: schemas.Policy) -> str:
    rego_rules = "\n\n".join([access_rule_to_rego(rule) for rule in policy.rules])
    return ALLOW_POLICY_STMNT.format(rules=rego_rules)
