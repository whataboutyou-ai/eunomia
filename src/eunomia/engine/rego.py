from pydantic import BaseModel

REGO_ALLOW_POLICY = """\
package eunomia\n
default allow := false\n
{rules}"""

REGO_ALLOW_RULE = """\
allow if {{
{item_attributes}
}}"""

REGO_EQUAL_ITEM_ATTRIBUTE = """\
input.{type}.{attribute_name} == "{attribute_value}"\
"""


class Item(BaseModel):
    type: str
    attributes: dict[str, str]

    def to_rego(self) -> str:
        return "\n".join(
            [
                REGO_EQUAL_ITEM_ATTRIBUTE.format(
                    type=self.type, attribute_name=name, attribute_value=value
                )
                for name, value in self.attributes.items()
            ]
        )


class Rule(BaseModel):
    items: list[Item]

    def to_rego(self) -> str:
        rego_items = "\n".join([item.to_rego() for item in self.items])
        return REGO_ALLOW_RULE.format(item_attributes=rego_items)


class Policy(BaseModel):
    rules: list[Rule]

    def to_rego(self) -> str:
        rego_rules = "\n\n".join([rule.to_rego() for rule in self.rules])
        return REGO_ALLOW_POLICY.format(rules=rego_rules)


### Example usage
# policy = Policy(
#     rules=[
#         Rule(
#             items=[
#                 Item(type="caller", attributes={"id": "orchestrator"}),
#                 Item(type="user", attributes={"department": "hr"}),
#                 Item(type="resource", attributes={"id": "hr-agent"}),
#             ]
#         ),
#         Rule(
#             items=[
#                 Item(type="caller", attributes={"id": "orchestrator"}),
#                 Item(type="user", attributes={"department": "it", "role": "admin"}),
#                 Item(type="resource", attributes={"id": "it-agent"}),
#             ],
#         ),
#     ],
# )
# with open("policies/agents_policy.rego", "w") as f:
#     f.write(policy.to_rego())
