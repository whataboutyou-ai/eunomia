from typing import Optional

from eunomia_core import enums, schemas

from eunomia.config import settings
from eunomia.engine.db import crud, db
from eunomia.engine.evaluator import evaluate_policy


class PolicyEngine:
    def __init__(self):
        self.policies: list[schemas.Policy] = []
        db.init_db(settings.ENGINE_SQL_DATABASE_URL)
        self._load_policies()

    def _load_policies(self) -> None:
        """Load policies from the database into memory."""
        with db.SessionLocal() as db_session:
            db_policies = crud.get_all_policies(db=db_session)
            self.policies = [schemas.Policy.model_validate(p) for p in db_policies]

    def add_policy(self, policy: schemas.Policy) -> None:
        """Add a policy to the engine and persist it to the database."""
        with db.SessionLocal() as db_session:
            crud.create_policy(policy, db=db_session)
        self.policies.append(policy)

    def remove_policy(self, policy_name: str) -> bool:
        """Remove a policy by name from the engine and database."""
        with db.SessionLocal() as db_session:
            is_deleted = crud.delete_policy(policy_name, db=db_session)
        if is_deleted:
            self.policies = [p for p in self.policies if p.name != policy_name]
        return is_deleted

    def get_policies(self) -> list[schemas.Policy]:
        """Retrieve all policies from memory."""
        return self.policies

    def get_policy(self, policy_name: str) -> Optional[schemas.Policy]:
        """Retrieve a policy by name from memory."""
        for policy in self.policies:
            if policy.name == policy_name:
                return policy
        return None

    def _evaluate(
        self, request: schemas.CheckRequest
    ) -> list[schemas.PolicyEvaluationResult]:
        """Evaluate all policies against the check request."""
        results = []

        for policy in self.policies:
            result = evaluate_policy(policy, request)
            results.append(result)

        return results

    def evaluate_all(self, request: schemas.CheckRequest) -> schemas.CheckResponse:
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
                if result.effect == enums.PolicyEffect.DENY:
                    explicit_deny = result
                elif result.effect == enums.PolicyEffect.ALLOW:
                    explicit_allow = result
            elif result.effect == enums.PolicyEffect.DENY:
                default_deny = result

        if explicit_deny:
            return schemas.CheckResponse(
                allowed=False,
                reason=f"Rule {explicit_deny.matched_rule.name} denied the action in policy {explicit_deny.policy_name}",
            )
        if explicit_allow:
            return schemas.CheckResponse(
                allowed=True,
                reason=f"Rule {explicit_allow.matched_rule.name} allowed the action in policy {explicit_allow.policy_name}",
            )
        if default_deny:
            return schemas.CheckResponse(
                allowed=False,
                reason="Action denied by default effect",
            )

        return schemas.CheckResponse(
            allowed=False,
            reason="Action denied by default because there are no policies",
        )
