from typing import Optional

from eunomia_core.schemas import AccessRequest

from eunomia.engine import schemas
from eunomia.engine.enums import PolicyEffect
from eunomia.engine.evaluator import evaluate_policy


class PolicyEngine:
    def __init__(self):
        self.policies: list[schemas.Policy] = []

    def add_policy(self, policy: schemas.Policy) -> None:
        """Add a policy to the engine."""
        self.policies.append(policy)

    def remove_policy(self, policy_name: str) -> bool:
        """Remove a policy by name."""
        initial_count = len(self.policies)
        self.policies = [p for p in self.policies if p.name != policy_name]
        return len(self.policies) < initial_count

    def get_policy(self, policy_name: str) -> Optional[schemas.Policy]:
        """Retrieve a policy by name."""
        for policy in self.policies:
            if policy.name == policy_name:
                return policy
        return None

    def _evaluate(self, request: AccessRequest) -> list[schemas.PolicyEvaluationResult]:
        """Evaluate all policies against the access request."""
        results = []

        for policy in self.policies:
            result = evaluate_policy(policy, request)
            results.append(result)

        return results

    def evaluate_all(self, request: AccessRequest) -> schemas.PolicyEvaluationResult:
        """
        Evaluate all policies and return a single result.

        If any policy explicitly matches a rule with DENY effect, the result is DENY.
        If any policy explicitly matches a rule with ALLOW effect, the result is ALLOW.
        If no explicit rule matches, and any policy returns a default DENY, the result is DENY.
        If no policies matched or there are no policies, deny by default.
        """
        results = self._evaluate(request)

        explicit_deny, explicit_allow, default_deny = None, None, None
        for result in results:
            if result.matched_rule:
                if result.effect == PolicyEffect.DENY:
                    explicit_deny = result
                elif result.effect == PolicyEffect.ALLOW:
                    explicit_allow = result
            elif result.effect == PolicyEffect.DENY:
                default_deny = result

        if explicit_deny:
            return explicit_deny
        if explicit_allow:
            return explicit_allow
        if default_deny:
            return default_deny

        # If no policies matched or there are no policies, deny by default
        return schemas.PolicyEvaluationResult(
            effect=PolicyEffect.DENY, matched_rule=None, policy_name="default"
        )
