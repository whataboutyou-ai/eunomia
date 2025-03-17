from eunomia_core import schemas

EQUAL_URI_STMNT = '	input.{type}.uri == "{uri}"'
EQUAL_ATTRIBUTE_STMNT = '	input.{type}.attributes.{key} == "{value}"'
ALLOW_RULE_STMNT = "allow if {{\n{entity_stmts}\n}}"
ALLOW_POLICY_STMNT = "package eunomia\n\ndefault allow := false\n\n{rules}\n"


def entity_to_rego(entity: schemas.EntityRequest) -> str:
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


### Example usage
# policy = schemas.Policy(
#     rules=[
#         schemas.AccessRequest(
#             principal=schemas.PrincipalRequest(
#                 uri="orchestrator",
#                 attributes={"from": "caller"},
#             ),
#             resource=schemas.ResourceRequest(uri="hr-agent"),
#         ),
#         schemas.AccessRequest(
#             principal=schemas.PrincipalRequest(
#                 attributes={"from": "user", "department": "it", "role": "admin"},
#             ),
#             resource=schemas.ResourceRequest(uri="it-agent"),
#         ),
#     ],
# )
# with open("policies/agents_policy.rego", "w") as f:
#     f.write(policy_to_rego(policy))
