from eunomia_core import enums, schemas

from eunomia.engine import PolicyEngine


class TestPolicyEngineWithDatabase:
    """Test PolicyEngine functionality with database persistence enabled."""

    def test_initialization(self, engine_with_database: PolicyEngine):
        """Test that engine initializes correctly with database enabled."""
        assert engine_with_database._db_enabled is True
        assert len(engine_with_database.policies) == 0

    def test_add_policy(
        self, engine_with_database: PolicyEngine, sample_policy: schemas.Policy
    ):
        """Test adding policy with database persistence."""
        engine_with_database.add_policy(sample_policy)
        assert len(engine_with_database.policies) == 1
        assert engine_with_database.policies[0].name == sample_policy.name

    def test_remove_policy_success(
        self, engine_with_database: PolicyEngine, sample_policy: schemas.Policy
    ):
        """Test removing existing policy with database persistence."""
        engine_with_database.add_policy(sample_policy)
        assert engine_with_database.remove_policy("test-policy") is True
        assert len(engine_with_database.policies) == 0

    def test_remove_policy_nonexistent(self, engine_with_database: PolicyEngine):
        """Test removing non-existent policy with database persistence."""
        assert engine_with_database.remove_policy("non-existent") is False

    def test_get_policy_by_name(
        self, engine_with_database: PolicyEngine, sample_policy: schemas.Policy
    ):
        """Test retrieving specific policy by name with database persistence."""
        engine_with_database.add_policy(sample_policy)
        retrieved = engine_with_database.get_policy("test-policy")
        assert retrieved is not None
        assert retrieved.name == sample_policy.name
        assert engine_with_database.get_policy("non-existent") is None

    def test_get_all_policies(
        self, engine_with_database: PolicyEngine, sample_policy: schemas.Policy
    ):
        """Test retrieving all policies with database persistence."""
        engine_with_database.add_policy(sample_policy)
        policies = engine_with_database.get_policies()
        assert len(policies) == 1
        assert policies[0].name == sample_policy.name


class TestPolicyEngineWithoutDatabase:
    """Test PolicyEngine functionality with database persistence disabled."""

    def test_initialization(self, engine_without_database: PolicyEngine):
        """Test that engine initializes correctly with database disabled."""
        assert engine_without_database._db_enabled is False
        assert len(engine_without_database.policies) == 0

    def test_add_policy(
        self, engine_without_database: PolicyEngine, sample_policy: schemas.Policy
    ):
        """Test adding policy without database persistence (memory only)."""
        engine_without_database.add_policy(sample_policy)
        assert len(engine_without_database.policies) == 1
        assert engine_without_database.policies[0].name == sample_policy.name

    def test_remove_policy_success(
        self, engine_without_database: PolicyEngine, sample_policy: schemas.Policy
    ):
        """Test removing existing policy without database persistence."""
        engine_without_database.add_policy(sample_policy)
        assert engine_without_database.remove_policy("test-policy") is True
        assert len(engine_without_database.policies) == 0

    def test_remove_policy_nonexistent(self, engine_without_database: PolicyEngine):
        """Test removing non-existent policy without database persistence."""
        result = engine_without_database.remove_policy("non-existent")
        assert result is False

    def test_get_policy_by_name(
        self, engine_without_database: PolicyEngine, sample_policy: schemas.Policy
    ):
        """Test retrieving specific policy by name without database persistence."""
        engine_without_database.add_policy(sample_policy)
        retrieved = engine_without_database.get_policy("test-policy")
        assert retrieved is not None
        assert retrieved.name == sample_policy.name
        assert engine_without_database.get_policy("non-existent") is None

    def test_get_all_policies(
        self, engine_without_database: PolicyEngine, sample_policy: schemas.Policy
    ):
        """Test retrieving all policies without database persistence."""
        engine_without_database.add_policy(sample_policy)
        policies = engine_without_database.get_policies()
        assert len(policies) == 1
        assert policies[0].name == sample_policy.name


class TestPolicyEngineEvaluation:
    """Test PolicyEngine evaluation logic (independent of persistence mode)."""

    def test_evaluate_with_no_policies(
        self,
        engine_with_database: PolicyEngine,
        sample_access_request: schemas.CheckRequest,
    ):
        """Test evaluation when no policies are loaded."""
        result = engine_with_database.evaluate_all(sample_access_request)
        assert result.allowed is False
        assert "default" in result.reason

    def test_evaluate_with_matching_policy(
        self,
        engine_with_database: PolicyEngine,
        sample_policy: schemas.Policy,
        sample_access_request: schemas.CheckRequest,
    ):
        """Test evaluation with a policy that matches the request."""
        engine_with_database.add_policy(sample_policy)
        result = engine_with_database.evaluate_all(sample_access_request)
        assert result.allowed is True
        assert "test-policy" in result.reason

    def test_evaluate_with_non_matching_policy(
        self, engine_with_database: PolicyEngine, sample_policy: schemas.Policy
    ):
        """Test evaluation with a policy that doesn't match the request."""
        non_matching_request = schemas.CheckRequest(
            principal=schemas.PrincipalCheck(
                type=enums.EntityType.principal,
                attributes={"role": "user"},  # Different from required "admin"
            ),
            resource=schemas.ResourceCheck(
                type=enums.EntityType.resource,
                attributes={"name": "test-resource"},
            ),
            action="access",
        )
        engine_with_database.add_policy(sample_policy)
        result = engine_with_database.evaluate_all(non_matching_request)
        assert result.allowed is False

    def test_evaluate_consistency_across_persistence_modes(
        self,
        engine_with_database: PolicyEngine,
        engine_without_database: PolicyEngine,
        sample_policy: schemas.Policy,
        sample_access_request: schemas.CheckRequest,
    ):
        """Test that evaluation results are consistent regardless of persistence mode."""
        # Add same policy to both engines
        engine_with_database.add_policy(sample_policy)
        engine_without_database.add_policy(sample_policy)

        # Evaluate same request on both engines
        result_with_db = engine_with_database.evaluate_all(sample_access_request)
        result_without_db = engine_without_database.evaluate_all(sample_access_request)

        # Results should be identical
        assert result_with_db.allowed == result_without_db.allowed
        assert result_with_db.reason == result_without_db.reason
