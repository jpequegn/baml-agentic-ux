"""
Tests for Conversational Testing Framework Types.

Part of Phase 6: Conversational Testing Framework
Issue #110 - Task 6.11: Testing & Documentation
"""

import pytest
from src.testing.types import (
    # Enums
    TestCategory,
    TestPriority,
    TurnRole,
    MatchType,
    AssertionType,
    AssertionTarget,
    AssertionOperator,
    AssertionSeverity,
    SuccessCondition,
    ExpertiseLevel,
    MockResponseType,
    TestStatus,
    ExecutionOrder,
    # Setup Types
    InitialEntity,
    TestUserProfile,
    SystemState,
    MockResponse,
    TestSetup,
    # Turn Types
    ExpectedEntity,
    ContextRequirement,
    ConversationAssertion,
    TestTurn,
    # Outcome Types
    QualityRequirements,
    ExpectedOutcome,
    QualityThresholds,
    # Core Test Types
    ConversationTest,
    # Execution Result Types
    AssertionResult,
    ExtractedEntity,
    QualityScores,
    TurnResult,
    FailureSummary,
    TestExecutionResult,
    # Suite Types
    SuiteSummary,
    TestSuite,
    TestSuiteResult,
)


class TestEnums:
    """Tests for all testing framework enums."""

    def test_test_category_values(self):
        """Test TestCategory enum values."""
        assert TestCategory.INTENT_RECOGNITION.value == "intent_recognition"
        assert TestCategory.ENTITY_EXTRACTION.value == "entity_extraction"
        assert TestCategory.DIALOGUE_FLOW.value == "dialogue_flow"
        assert TestCategory.ERROR_HANDLING.value == "error_handling"
        assert TestCategory.CONTEXT_RETENTION.value == "context_retention"
        assert TestCategory.DRIFT_DETECTION.value == "drift_detection"
        assert TestCategory.QUALITY_ASSURANCE.value == "quality_assurance"
        assert TestCategory.REGRESSION.value == "regression"
        assert TestCategory.PERFORMANCE.value == "performance"

    def test_test_priority_values(self):
        """Test TestPriority enum values."""
        assert TestPriority.CRITICAL.value == "critical"
        assert TestPriority.HIGH.value == "high"
        assert TestPriority.MEDIUM.value == "medium"
        assert TestPriority.LOW.value == "low"
        assert TestPriority.EXPLORATORY.value == "exploratory"

    def test_turn_role_values(self):
        """Test TurnRole enum values."""
        assert TurnRole.USER.value == "user"
        assert TurnRole.ASSISTANT.value == "assistant"
        assert TurnRole.SYSTEM.value == "system"

    def test_match_type_values(self):
        """Test MatchType enum values."""
        assert MatchType.EXACT.value == "exact"
        assert MatchType.CONTAINS.value == "contains"
        assert MatchType.REGEX.value == "regex"
        assert MatchType.SEMANTIC.value == "semantic"
        assert MatchType.EXISTS.value == "exists"
        assert MatchType.TYPE_CHECK.value == "type_check"

    def test_assertion_type_values(self):
        """Test AssertionType enum values."""
        assert AssertionType.INTENT_MATCH.value == "intent_match"
        assert AssertionType.ENTITY_PRESENT.value == "entity_present"
        assert AssertionType.ENTITY_VALUE.value == "entity_value"
        assert AssertionType.RESPONSE_CONTAINS.value == "response_contains"
        assert AssertionType.QUALITY_SCORE.value == "quality_score"
        assert AssertionType.LATENCY.value == "latency"

    def test_assertion_target_values(self):
        """Test AssertionTarget enum values."""
        assert AssertionTarget.INTENT.value == "intent"
        assert AssertionTarget.ENTITIES.value == "entities"
        assert AssertionTarget.RESPONSE.value == "response"
        assert AssertionTarget.CONTEXT.value == "context"
        assert AssertionTarget.CONFIDENCE.value == "confidence"

    def test_assertion_operator_values(self):
        """Test AssertionOperator enum values."""
        assert AssertionOperator.EQUALS.value == "equals"
        assert AssertionOperator.NOT_EQUALS.value == "not_equals"
        assert AssertionOperator.GREATER_THAN.value == "greater_than"
        assert AssertionOperator.CONTAINS.value == "contains"
        assert AssertionOperator.MATCHES.value == "matches"

    def test_assertion_severity_values(self):
        """Test AssertionSeverity enum values."""
        assert AssertionSeverity.CRITICAL.value == "critical"
        assert AssertionSeverity.ERROR.value == "error"
        assert AssertionSeverity.WARNING.value == "warning"
        assert AssertionSeverity.INFO.value == "info"

    def test_success_condition_values(self):
        """Test SuccessCondition enum values."""
        assert SuccessCondition.ALL_PASS.value == "all_pass"
        assert SuccessCondition.THRESHOLD.value == "threshold"
        assert SuccessCondition.REQUIRED_ONLY.value == "required_only"
        assert SuccessCondition.CUSTOM.value == "custom"

    def test_test_status_values(self):
        """Test TestStatus enum values."""
        assert TestStatus.PASSED.value == "passed"
        assert TestStatus.FAILED.value == "failed"
        assert TestStatus.ERROR.value == "error"
        assert TestStatus.SKIPPED.value == "skipped"
        assert TestStatus.TIMEOUT.value == "timeout"
        assert TestStatus.PARTIAL.value == "partial"

    def test_execution_order_values(self):
        """Test ExecutionOrder enum values."""
        assert ExecutionOrder.SEQUENTIAL.value == "sequential"
        assert ExecutionOrder.PRIORITY.value == "priority"
        assert ExecutionOrder.RANDOM.value == "random"
        assert ExecutionOrder.DEPENDENCY.value == "dependency"


class TestSetupTypes:
    """Tests for test setup dataclasses."""

    def test_initial_entity_creation(self):
        """Test InitialEntity creation."""
        entity = InitialEntity(
            entity_type="date",
            value="2026-01-06",
            slot_name="appointment_date",
            confidence=0.95,
        )
        assert entity.entity_type == "date"
        assert entity.value == "2026-01-06"
        assert entity.slot_name == "appointment_date"
        assert entity.confidence == 0.95

    def test_initial_entity_defaults(self):
        """Test InitialEntity default values."""
        entity = InitialEntity(
            entity_type="name",
            value="John Doe",
        )
        assert entity.slot_name is None
        assert entity.confidence is None

    def test_test_user_profile_creation(self):
        """Test TestUserProfile creation."""
        profile = TestUserProfile(
            user_id="user_123",
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            preferences={"language": "en", "format": "brief"},
            history_summary="Frequent user of task management",
            accessibility_needs=["screen_reader", "high_contrast"],
        )
        assert profile.user_id == "user_123"
        assert profile.expertise_level == ExpertiseLevel.INTERMEDIATE
        assert profile.preferences["language"] == "en"
        assert "screen_reader" in profile.accessibility_needs

    def test_test_user_profile_defaults(self):
        """Test TestUserProfile default values."""
        profile = TestUserProfile(
            user_id="user_456",
            expertise_level=ExpertiseLevel.NOVICE,
        )
        assert profile.preferences is None
        assert profile.history_summary is None
        assert profile.accessibility_needs == []

    def test_system_state_creation(self):
        """Test SystemState creation."""
        state = SystemState(
            active_capabilities=["task_manager", "calendar"],
            disabled_capabilities=["email"],
            rate_limits={"api_calls": 100},
            feature_flags={"beta_feature": True},
        )
        assert "task_manager" in state.active_capabilities
        assert "email" in state.disabled_capabilities
        assert state.rate_limits["api_calls"] == 100
        assert state.feature_flags["beta_feature"] is True

    def test_mock_response_creation(self):
        """Test MockResponse creation."""
        mock = MockResponse(
            trigger_pattern="get_weather.*",
            response_type=MockResponseType.API_RESPONSE,
            response_data='{"temp": 72, "condition": "sunny"}',
            delay_ms=100,
            fail_after=5,
        )
        assert mock.trigger_pattern == "get_weather.*"
        assert mock.response_type == MockResponseType.API_RESPONSE
        assert mock.delay_ms == 100

    def test_test_setup_creation(self):
        """Test TestSetup creation."""
        setup = TestSetup(
            initial_context={"user_name": "Alice"},
            initial_entities=[
                InitialEntity(entity_type="name", value="Alice")
            ],
            user_profile=TestUserProfile(
                user_id="alice",
                expertise_level=ExpertiseLevel.ADVANCED,
            ),
        )
        assert setup.initial_context["user_name"] == "Alice"
        assert len(setup.initial_entities) == 1
        assert setup.user_profile.user_id == "alice"


class TestTurnTypes:
    """Tests for conversation turn dataclasses."""

    def test_expected_entity_creation(self):
        """Test ExpectedEntity creation."""
        entity = ExpectedEntity(
            entity_type="date",
            required=True,
            value="tomorrow",
            slot_name="due_date",
        )
        assert entity.entity_type == "date"
        assert entity.required is True
        assert entity.value == "tomorrow"

    def test_context_requirement_creation(self):
        """Test ContextRequirement creation."""
        req = ContextRequirement(
            key="user_id",
            match_type=MatchType.EXISTS,
        )
        assert req.key == "user_id"
        assert req.match_type == MatchType.EXISTS

    def test_context_requirement_with_value(self):
        """Test ContextRequirement with value match."""
        req = ContextRequirement(
            key="status",
            match_type=MatchType.EXACT,
            value_match="active",
        )
        assert req.value_match == "active"

    def test_conversation_assertion_creation(self):
        """Test ConversationAssertion creation."""
        assertion = ConversationAssertion(
            assertion_id="check_intent",
            assertion_type=AssertionType.INTENT_MATCH,
            target=AssertionTarget.INTENT,
            operator=AssertionOperator.EQUALS,
            expected_value="create_task",
            severity=AssertionSeverity.CRITICAL,
        )
        assert assertion.assertion_id == "check_intent"
        assert assertion.assertion_type == AssertionType.INTENT_MATCH
        assert assertion.expected_value == "create_task"

    def test_conversation_assertion_with_threshold(self):
        """Test ConversationAssertion with threshold."""
        assertion = ConversationAssertion(
            assertion_id="check_confidence",
            assertion_type=AssertionType.CONFIDENCE_SCORE,
            target=AssertionTarget.CONFIDENCE,
            operator=AssertionOperator.GREATER_OR_EQUAL,
            threshold=0.8,
            tolerance=0.05,
        )
        assert assertion.threshold == 0.8
        assert assertion.tolerance == 0.05

    def test_test_turn_creation(self):
        """Test TestTurn creation."""
        turn = TestTurn(
            turn_number=1,
            role=TurnRole.USER,
            input="Create a task for tomorrow",
            expected_intent="create_task",
            expected_entities=[
                ExpectedEntity(entity_type="date", required=True)
            ],
        )
        assert turn.turn_number == 1
        assert turn.role == TurnRole.USER
        assert turn.expected_intent == "create_task"
        assert len(turn.expected_entities) == 1


class TestOutcomeTypes:
    """Tests for expected outcome dataclasses."""

    def test_quality_requirements_creation(self):
        """Test QualityRequirements creation."""
        reqs = QualityRequirements(
            min_coherence=0.8,
            min_naturalness=0.7,
            min_accuracy=0.9,
            max_drift_score=0.2,
        )
        assert reqs.min_coherence == 0.8
        assert reqs.min_naturalness == 0.7
        assert reqs.max_drift_score == 0.2

    def test_quality_thresholds_creation(self):
        """Test QualityThresholds creation with actual interface."""
        thresholds = QualityThresholds(
            coherence_threshold=0.90,
            naturalness_threshold=0.85,
            accuracy_threshold=0.95,
            relevance_threshold=0.80,
            confidence_threshold=0.75,
            max_drift_threshold=0.40,
            latency_threshold_ms=1500,
            strict_mode=True,
        )
        assert thresholds.coherence_threshold == 0.90
        assert thresholds.naturalness_threshold == 0.85
        assert thresholds.accuracy_threshold == 0.95
        assert thresholds.latency_threshold_ms == 1500
        assert thresholds.strict_mode is True

    def test_quality_thresholds_defaults(self):
        """Test QualityThresholds default values."""
        thresholds = QualityThresholds()
        assert thresholds.coherence_threshold == 0.85
        assert thresholds.naturalness_threshold == 0.80
        assert thresholds.accuracy_threshold == 0.90
        assert thresholds.relevance_threshold == 0.75
        assert thresholds.confidence_threshold == 0.70
        assert thresholds.max_drift_threshold == 0.50
        assert thresholds.latency_threshold_ms == 2000
        assert thresholds.strict_mode is False

    def test_expected_outcome_creation(self):
        """Test ExpectedOutcome creation."""
        outcome = ExpectedOutcome(
            success_condition=SuccessCondition.ALL_PASS,
            required_assertions=["intent_match", "entity_present"],
            quality_requirements=QualityRequirements(min_coherence=0.8),
        )
        assert outcome.success_condition == SuccessCondition.ALL_PASS
        assert "intent_match" in outcome.required_assertions


class TestCoreTestTypes:
    """Tests for ConversationTest dataclass."""

    def test_conversation_test_creation(self):
        """Test ConversationTest creation with required expected_outcome."""
        test = ConversationTest(
            test_id="test_create_task_001",
            name="Basic task creation",
            description="Test basic task creation flow",
            category=TestCategory.INTENT_RECOGNITION,
            priority=TestPriority.HIGH,
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.USER,
                    input="Create a task",
                    expected_intent="create_task",
                ),
            ],
            expected_outcome=ExpectedOutcome(
                success_condition=SuccessCondition.ALL_PASS,
            ),
        )
        assert test.test_id == "test_create_task_001"
        assert test.category == TestCategory.INTENT_RECOGNITION
        assert test.priority == TestPriority.HIGH
        assert len(test.turns) == 1
        assert test.expected_outcome is not None

    def test_conversation_test_with_setup(self):
        """Test ConversationTest with setup configuration."""
        test = ConversationTest(
            test_id="test_with_setup",
            name="Test with setup",
            description="Test with initial setup",
            category=TestCategory.CONTEXT_RETENTION,
            priority=TestPriority.MEDIUM,
            setup=TestSetup(
                initial_context={"user": "test_user"},
            ),
            turns=[
                TestTurn(turn_number=1, role=TurnRole.USER, input="Hello"),
            ],
            expected_outcome=ExpectedOutcome(),
        )
        assert test.setup is not None
        assert test.setup.initial_context["user"] == "test_user"

    def test_conversation_test_with_quality_thresholds(self):
        """Test ConversationTest with quality thresholds."""
        test = ConversationTest(
            test_id="test_quality",
            name="Quality test",
            turns=[
                TestTurn(turn_number=1, role=TurnRole.USER, input="Hello"),
            ],
            expected_outcome=ExpectedOutcome(),
            quality_thresholds=QualityThresholds(
                coherence_threshold=0.95,
                strict_mode=True,
            ),
        )
        assert test.quality_thresholds is not None
        assert test.quality_thresholds.coherence_threshold == 0.95


class TestExecutionResultTypes:
    """Tests for test execution result dataclasses."""

    def test_assertion_result_passed(self):
        """Test AssertionResult for passed assertion with full interface."""
        result = AssertionResult(
            assertion_id="check_intent",
            turn_number=1,
            assertion_type=AssertionType.INTENT_MATCH,
            passed=True,
            severity=AssertionSeverity.ERROR,
            actual_value="create_task",
            expected_value="create_task",
            message="Intent matched correctly",
        )
        assert result.passed is True
        assert result.actual_value == result.expected_value
        assert result.turn_number == 1
        assert result.assertion_type == AssertionType.INTENT_MATCH

    def test_assertion_result_failed(self):
        """Test AssertionResult for failed assertion."""
        result = AssertionResult(
            assertion_id="check_confidence",
            turn_number=2,
            assertion_type=AssertionType.CONFIDENCE_SCORE,
            passed=False,
            severity=AssertionSeverity.WARNING,
            actual_value="0.65",
            expected_value="0.80",
            message="Confidence below threshold",
        )
        assert result.passed is False
        assert result.severity == AssertionSeverity.WARNING

    def test_extracted_entity_creation(self):
        """Test ExtractedEntity creation with actual interface."""
        entity = ExtractedEntity(
            entity_type="date",
            value="2026-01-07",
            confidence=0.92,
            start_offset=10,
            end_offset=20,
        )
        assert entity.entity_type == "date"
        assert entity.confidence == 0.92
        assert entity.start_offset == 10
        assert entity.end_offset == 20

    def test_extracted_entity_defaults(self):
        """Test ExtractedEntity default values."""
        entity = ExtractedEntity(
            entity_type="name",
            value="John",
            confidence=0.95,
        )
        assert entity.start_offset is None
        assert entity.end_offset is None

    def test_quality_scores_creation(self):
        """Test QualityScores creation with full interface."""
        scores = QualityScores(
            coherence=0.85,
            naturalness=0.80,
            accuracy=0.92,
            relevance=0.88,
            avg_confidence=0.90,
            max_drift_score=0.15,
            avg_latency_ms=150.5,
        )
        assert scores.coherence == 0.85
        assert scores.accuracy == 0.92
        assert scores.avg_confidence == 0.90
        assert scores.max_drift_score == 0.15
        assert scores.avg_latency_ms == 150.5

    def test_turn_result_creation(self):
        """Test TurnResult creation with actual interface."""
        result = TurnResult(
            turn_number=1,
            input="Create a task for tomorrow",
            passed=True,
            latency_ms=120,
            actual_response="I'll create a task for tomorrow.",
            detected_intent="create_task",
            extracted_entities=[
                ExtractedEntity(
                    entity_type="date",
                    value="tomorrow",
                    confidence=0.9,
                )
            ],
        )
        assert result.turn_number == 1
        assert result.input == "Create a task for tomorrow"
        assert result.passed is True
        assert result.latency_ms == 120
        assert result.detected_intent == "create_task"
        assert len(result.extracted_entities) == 1

    def test_turn_result_defaults(self):
        """Test TurnResult default values."""
        result = TurnResult(
            turn_number=1,
            input="Hello",
            passed=True,
            latency_ms=50,
        )
        assert result.actual_response is None
        assert result.detected_intent is None
        assert result.extracted_entities == []

    def test_failure_summary_creation(self):
        """Test FailureSummary creation."""
        summary = FailureSummary(
            total_assertions=10,
            passed_count=7,
            failed_count=3,
            first_failure_turn=2,
            critical_failures=["intent_mismatch", "entity_missing"],
            failure_categories={"intent": 1, "entity": 2},
        )
        assert summary.total_assertions == 10
        assert summary.passed_count == 7
        assert summary.failed_count == 3
        assert summary.first_failure_turn == 2
        assert len(summary.critical_failures) == 2

    def test_test_execution_result_passed(self):
        """Test TestExecutionResult for passed test with full interface."""
        quality_scores = QualityScores(
            coherence=0.90,
            naturalness=0.85,
            accuracy=0.95,
            relevance=0.88,
            avg_confidence=0.92,
            max_drift_score=0.10,
            avg_latency_ms=100.0,
        )
        result = TestExecutionResult(
            test_id="test_001",
            test_name="Basic greeting test",
            status=TestStatus.PASSED,
            started_at="2026-01-06T10:00:00Z",
            completed_at="2026-01-06T10:00:01Z",
            duration_ms=150,
            quality_scores=quality_scores,
            turn_results=[
                TurnResult(
                    turn_number=1,
                    input="Hello",
                    passed=True,
                    latency_ms=150,
                    detected_intent="greet",
                )
            ],
            assertion_results=[
                AssertionResult(
                    assertion_id="intent_check",
                    turn_number=1,
                    assertion_type=AssertionType.INTENT_MATCH,
                    passed=True,
                    severity=AssertionSeverity.ERROR,
                )
            ],
        )
        assert result.status == TestStatus.PASSED
        assert result.test_name == "Basic greeting test"
        assert result.duration_ms == 150
        assert result.quality_scores.coherence == 0.90

    def test_test_execution_result_failed(self):
        """Test TestExecutionResult for failed test."""
        quality_scores = QualityScores(
            coherence=0.70,
            naturalness=0.65,
            accuracy=0.60,
            relevance=0.55,
            avg_confidence=0.50,
            max_drift_score=0.45,
            avg_latency_ms=200.0,
        )
        failure = FailureSummary(
            total_assertions=5,
            passed_count=2,
            failed_count=3,
            first_failure_turn=1,
        )
        result = TestExecutionResult(
            test_id="test_002",
            test_name="Failed test",
            status=TestStatus.FAILED,
            started_at="2026-01-06T10:00:00Z",
            completed_at="2026-01-06T10:00:02Z",
            duration_ms=2000,
            quality_scores=quality_scores,
            failure_summary=failure,
        )
        assert result.status == TestStatus.FAILED
        assert result.failure_summary is not None
        assert result.failure_summary.failed_count == 3


class TestSuiteTypes:
    """Tests for test suite dataclasses."""

    def test_suite_summary_creation(self):
        """Test SuiteSummary creation with actual interface."""
        summary = SuiteSummary(
            total_tests=10,
            passed=8,
            failed=1,
            errors=1,
            skipped=0,
            pass_rate=0.8,
            avg_duration_ms=500.0,
            coverage_estimate=0.75,
        )
        assert summary.total_tests == 10
        assert summary.passed == 8
        assert summary.pass_rate == 0.8
        assert summary.avg_duration_ms == 500.0
        assert summary.coverage_estimate == 0.75

    def test_suite_summary_defaults(self):
        """Test SuiteSummary with default optional values."""
        summary = SuiteSummary(
            total_tests=5,
            passed=5,
            failed=0,
            errors=0,
            skipped=0,
            pass_rate=1.0,
            avg_duration_ms=100.0,
        )
        assert summary.coverage_estimate is None

    def test_test_suite_creation(self):
        """Test TestSuite creation."""
        suite = TestSuite(
            suite_id="suite_001",
            name="Task Management Tests",
            description="Tests for task management features",
            tests=[
                ConversationTest(
                    test_id="test_001",
                    name="Create task",
                    description="Test task creation",
                    category=TestCategory.INTENT_RECOGNITION,
                    priority=TestPriority.HIGH,
                    turns=[
                        TestTurn(turn_number=1, role=TurnRole.USER, input="Create task")
                    ],
                    expected_outcome=ExpectedOutcome(),
                ),
            ],
        )
        assert suite.suite_id == "suite_001"
        assert len(suite.tests) == 1

    def test_test_suite_with_options(self):
        """Test TestSuite with execution options."""
        suite = TestSuite(
            suite_id="suite_002",
            name="Parallel Suite",
            tests=[],
            execution_order=ExecutionOrder.PRIORITY,
            stop_on_failure=True,
            parallel_execution=True,
            tags=["smoke", "regression"],
        )
        assert suite.execution_order == ExecutionOrder.PRIORITY
        assert suite.stop_on_failure is True
        assert suite.parallel_execution is True
        assert "smoke" in suite.tags

    def test_test_suite_result_creation(self):
        """Test TestSuiteResult creation with full interface."""
        summary = SuiteSummary(
            total_tests=5,
            passed=4,
            failed=1,
            errors=0,
            skipped=0,
            pass_rate=0.8,
            avg_duration_ms=250.0,
        )
        suite_result = TestSuiteResult(
            suite_id="suite_001",
            suite_name="Test Suite",
            status=TestStatus.PARTIAL,
            started_at="2026-01-06T10:00:00Z",
            completed_at="2026-01-06T10:00:05Z",
            duration_ms=5000,
            summary=summary,
            test_results=[],
        )
        assert suite_result.suite_id == "suite_001"
        assert suite_result.suite_name == "Test Suite"
        assert suite_result.status == TestStatus.PARTIAL
        assert suite_result.summary.pass_rate == 0.8
        assert suite_result.duration_ms == 5000
