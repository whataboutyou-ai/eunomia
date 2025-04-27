from typing import Optional

from eunomia_core.schemas import AccessRequest

from eunomia.engine.internal.evaluator import evaluate_policy
from eunomia.engine.internal.models import Policy, PolicyEffect, PolicyEvaluationResult


class PolicyEngine:
    def __init__(self):
        self.policies: list[Policy] = []

    def add_policy(self, policy: Policy) -> None:
        """Add a policy to the engine."""
        self.policies.append(policy)

    def remove_policy(self, policy_name: str) -> bool:
        """Remove a policy by name."""
        initial_count = len(self.policies)
        self.policies = [p for p in self.policies if p.name != policy_name]
        return len(self.policies) < initial_count

    def get_policy(self, policy_name: str) -> Optional[Policy]:
        """Retrieve a policy by name."""
        for policy in self.policies:
            if policy.name == policy_name:
                return policy
        return None

    def _evaluate(self, request: AccessRequest) -> list[PolicyEvaluationResult]:
        """Evaluate all policies against the access request."""
        results = []

        for policy in self.policies:
            result = evaluate_policy(policy, request)
            results.append(result)

        return results

    def evaluate_all(self, request: AccessRequest) -> PolicyEvaluationResult:
        """
        Evaluate all policies and return a single result.
        If any policy explicitly DENIES, the result is DENY.
        Otherwise, if at least one policy explicitly ALLOWS, the result is ALLOW.
        If no policies match, the default result is DENY.
        """
        results = self._evaluate(request)

        # If any policy denies, the overall result is deny
        for result in results:
            if result.effect == PolicyEffect.DENY:
                return result

        # If any policy allows, the overall result is allow
        for result in results:
            if result.effect == PolicyEffect.ALLOW:
                return result

        # If no policies matched or there are no policies, deny by default
        return PolicyEvaluationResult(
            effect=PolicyEffect.DENY, matched_rule=None, policy_name="default"
        )
