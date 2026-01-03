"""Tests for Conversational Testing Framework Types.

Issue #89 - Task 6.1: Test Definition Types
Part of #29 - Phase 6: Conversational Testing Framework
"""

import pytest
from dataclasses import asdict, fields

from src.testing import (
    # Core Enums
    AssertionOperator,
    AssertionSeverity,
    AssertionTarget,
    AssertionType,
    ExecutionOrder,
    ExpertiseLevel,
    MatchType,
    MockResponseType,
    SuccessCondition,
    TestCategory,
    TestPriority,
    TestStatus,
    TurnRole,
    # Test Setup Types
    InitialEntity,
    MockResponse,
    SystemState,
    TestSetup,
    TestUserProfile,
    # Test Turn Types
    ContextRequirement,
    ConversationAssertion,
    ExpectedEntity,
    TestTurn,
    # Expected Outcome Types
    ExpectedOutcome,
    QualityRequirements,
    # Quality Threshold Types
    QualityThresholds,
    # Core Test Types
    ConversationTest,
    # Test Execution Result Types
    AssertionResult,
    ExtractedEntity,
    FailureSummary,
    QualityScores,
    TestExecutionResult,
    TurnResult,
    # Test Suite Types
    SuiteSummary,
    TestSuite,
    TestSuiteResult,
)


# ============================================
# Enum Tests
# ============================================


class TestEnums:
    """Test all enum definitions."""

    def test_test_category_values(self) -> None:
        """Test TestCategory enum has all expected values."""
        expected = {
            "INTENT_RECOGNITION",
            "ENTITY_EXTRACTION",
            "DIALOGUE_FLOW",
            "ERROR_HANDLING",
            "CONTEXT_RETENTION",
            "DRIFT_DETECTION",
            "QUALITY_ASSURANCE",
            "REGRESSION",
            "PERFORMANCE",
        }
        actual = {member.name for member in TestCategory}
        assert actual == expected

    def test_test_priority_values(self) -> None:
        """Test TestPriority enum has all expected values."""
        expected = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "EXPLORATORY"}
        actual = {member.name for member in TestPriority}
        assert actual == expected

    def test_turn_role_values(self) -> None:
        """Test TurnRole enum has all expected values."""
        expected = {"USER", "ASSISTANT", "SYSTEM"}
        actual = {member.name for member in TurnRole}
        assert actual == expected

    def test_match_type_values(self) -> None:
        """Test MatchType enum has all expected values."""
        expected = {"EXACT", "CONTAINS", "REGEX", "SEMANTIC", "EXISTS", "TYPE_CHECK"}
        actual = {member.name for member in MatchType}
        assert actual == expected

    def test_assertion_type_values(self) -> None:
        """Test AssertionType enum has all expected values."""
        expected = {
            "INTENT_MATCH",
            "ENTITY_PRESENT",
            "ENTITY_VALUE",
            "RESPONSE_CONTAINS",
            "RESPONSE_NOT_CONTAINS",
            "RESPONSE_PATTERN",
            "QUALITY_SCORE",
            "CONFIDENCE_SCORE",
            "CONTEXT_VALUE",
            "LATENCY",
            "TOKEN_COUNT",
            "CUSTOM",
        }
        actual = {member.name for member in AssertionType}
        assert actual == expected

    def test_assertion_target_values(self) -> None:
        """Test AssertionTarget enum has all expected values."""
        expected = {
            "INTENT",
            "ENTITIES",
            "RESPONSE",
            "CONTEXT",
            "CONFIDENCE",
            "COHERENCE",
            "NATURALNESS",
            "ACCURACY",
            "LATENCY",
            "TOKENS",
            "METADATA",
        }
        actual = {member.name for member in AssertionTarget}
        assert actual == expected

    def test_assertion_operator_values(self) -> None:
        """Test AssertionOperator enum has all expected values."""
        expected = {
            "EQUALS",
            "NOT_EQUALS",
            "GREATER_THAN",
            "GREATER_OR_EQUAL",
            "LESS_THAN",
            "LESS_OR_EQUAL",
            "CONTAINS",
            "NOT_CONTAINS",
            "MATCHES",
            "NOT_MATCHES",
            "SEMANTIC_SIMILAR",
            "IN_SET",
            "NOT_IN_SET",
        }
        actual = {member.name for member in AssertionOperator}
        assert actual == expected

    def test_assertion_severity_values(self) -> None:
        """Test AssertionSeverity enum has all expected values."""
        expected = {"CRITICAL", "ERROR", "WARNING", "INFO"}
        actual = {member.name for member in AssertionSeverity}
        assert actual == expected

    def test_success_condition_values(self) -> None:
        """Test SuccessCondition enum has all expected values."""
        expected = {"ALL_PASS", "THRESHOLD", "REQUIRED_ONLY", "CUSTOM"}
        actual = {member.name for member in SuccessCondition}
        assert actual == expected

    def test_expertise_level_values(self) -> None:
        """Test ExpertiseLevel enum has all expected values."""
        expected = {"NOVICE", "INTERMEDIATE", "ADVANCED", "EXPERT"}
        actual = {member.name for member in ExpertiseLevel}
        assert actual == expected

    def test_mock_response_type_values(self) -> None:
        """Test MockResponseType enum has all expected values."""
        expected = {"API_RESPONSE", "DATABASE_RESULT", "EXTERNAL_SERVICE", "ERROR"}
        actual = {member.name for member in MockResponseType}
        assert actual == expected

    def test_test_status_values(self) -> None:
        """Test TestStatus enum has all expected values."""
        expected = {"PASSED", "FAILED", "ERROR", "SKIPPED", "TIMEOUT", "PARTIAL"}
        actual = {member.name for member in TestStatus}
        assert actual == expected

    def test_execution_order_values(self) -> None:
        """Test ExecutionOrder enum has all expected values."""
        expected = {"SEQUENTIAL", "PRIORITY", "RANDOM", "DEPENDENCY"}
        actual = {member.name for member in ExecutionOrder}
        assert actual == expected


# ============================================
# Test Setup Type Tests
# ============================================


class TestInitialEntity:
    """Test InitialEntity dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating InitialEntity with required fields only."""
        entity = InitialEntity(entity_type="date", value="2024-01-15")
        assert entity.entity_type == "date"
        assert entity.value == "2024-01-15"
        assert entity.slot_name is None
        assert entity.confidence is None

    def test_create_full(self) -> None:
        """Test creating InitialEntity with all fields."""
        entity = InitialEntity(
            entity_type="location",
            value="New York",
            slot_name="destination",
            confidence=0.95,
        )
        assert entity.entity_type == "location"
        assert entity.value == "New York"
        assert entity.slot_name == "destination"
        assert entity.confidence == 0.95


class TestTestUserProfile:
    """Test TestUserProfile dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating TestUserProfile with required fields only."""
        profile = TestUserProfile(user_id="user123", expertise_level=ExpertiseLevel.NOVICE)
        assert profile.user_id == "user123"
        assert profile.expertise_level == ExpertiseLevel.NOVICE
        assert profile.preferences is None
        assert profile.history_summary is None
        assert profile.accessibility_needs == []

    def test_create_full(self) -> None:
        """Test creating TestUserProfile with all fields."""
        profile = TestUserProfile(
            user_id="user456",
            expertise_level=ExpertiseLevel.EXPERT,
            preferences={"theme": "dark", "language": "en"},
            history_summary="Power user with 500+ interactions",
            accessibility_needs=["screen_reader", "high_contrast"],
        )
        assert profile.user_id == "user456"
        assert profile.expertise_level == ExpertiseLevel.EXPERT
        assert profile.preferences == {"theme": "dark", "language": "en"}
        assert profile.history_summary == "Power user with 500+ interactions"
        assert profile.accessibility_needs == ["screen_reader", "high_contrast"]


class TestSystemState:
    """Test SystemState dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating SystemState with defaults."""
        state = SystemState()
        assert state.active_capabilities == []
        assert state.disabled_capabilities == []
        assert state.rate_limits is None
        assert state.feature_flags is None

    def test_create_full(self) -> None:
        """Test creating SystemState with all fields."""
        state = SystemState(
            active_capabilities=["weather", "calendar"],
            disabled_capabilities=["payments"],
            rate_limits={"weather": 100, "calendar": 50},
            feature_flags={"new_ui": True, "beta_feature": False},
        )
        assert state.active_capabilities == ["weather", "calendar"]
        assert state.disabled_capabilities == ["payments"]
        assert state.rate_limits == {"weather": 100, "calendar": 50}
        assert state.feature_flags == {"new_ui": True, "beta_feature": False}


class TestMockResponse:
    """Test MockResponse dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating MockResponse with required fields only."""
        mock = MockResponse(
            trigger_pattern="get_weather*",
            response_type=MockResponseType.API_RESPONSE,
            response_data='{"temp": 72, "condition": "sunny"}',
        )
        assert mock.trigger_pattern == "get_weather*"
        assert mock.response_type == MockResponseType.API_RESPONSE
        assert mock.response_data == '{"temp": 72, "condition": "sunny"}'
        assert mock.delay_ms is None
        assert mock.fail_after is None

    def test_create_full(self) -> None:
        """Test creating MockResponse with all fields."""
        mock = MockResponse(
            trigger_pattern="api_call*",
            response_type=MockResponseType.ERROR,
            response_data="Connection timeout",
            delay_ms=500,
            fail_after=3,
        )
        assert mock.trigger_pattern == "api_call*"
        assert mock.response_type == MockResponseType.ERROR
        assert mock.response_data == "Connection timeout"
        assert mock.delay_ms == 500
        assert mock.fail_after == 3


class TestTestSetup:
    """Test TestSetup dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating TestSetup with defaults."""
        setup = TestSetup()
        assert setup.initial_context is None
        assert setup.initial_entities == []
        assert setup.user_profile is None
        assert setup.system_state is None
        assert setup.mock_responses == []
        assert setup.environment_variables is None

    def test_create_full(self) -> None:
        """Test creating TestSetup with all fields."""
        setup = TestSetup(
            initial_context={"session_id": "abc123"},
            initial_entities=[InitialEntity(entity_type="date", value="2024-01-15")],
            user_profile=TestUserProfile(
                user_id="user1", expertise_level=ExpertiseLevel.INTERMEDIATE
            ),
            system_state=SystemState(active_capabilities=["weather"]),
            mock_responses=[
                MockResponse(
                    trigger_pattern="*",
                    response_type=MockResponseType.API_RESPONSE,
                    response_data="{}",
                )
            ],
            environment_variables={"DEBUG": "true"},
        )
        assert setup.initial_context == {"session_id": "abc123"}
        assert len(setup.initial_entities) == 1
        assert setup.user_profile is not None
        assert setup.system_state is not None
        assert len(setup.mock_responses) == 1
        assert setup.environment_variables == {"DEBUG": "true"}


# ============================================
# Test Turn Type Tests
# ============================================


class TestExpectedEntity:
    """Test ExpectedEntity dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating ExpectedEntity with required fields only."""
        entity = ExpectedEntity(entity_type="date")
        assert entity.entity_type == "date"
        assert entity.required is True
        assert entity.value is None
        assert entity.value_pattern is None
        assert entity.slot_name is None

    def test_create_full(self) -> None:
        """Test creating ExpectedEntity with all fields."""
        entity = ExpectedEntity(
            entity_type="amount",
            required=False,
            value="100",
            value_pattern=r"\d+",
            slot_name="payment_amount",
        )
        assert entity.entity_type == "amount"
        assert entity.required is False
        assert entity.value == "100"
        assert entity.value_pattern == r"\d+"
        assert entity.slot_name == "payment_amount"


class TestContextRequirement:
    """Test ContextRequirement dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating ContextRequirement with required fields only."""
        req = ContextRequirement(key="user_authenticated")
        assert req.key == "user_authenticated"
        assert req.match_type == MatchType.EXISTS
        assert req.value_match is None

    def test_create_full(self) -> None:
        """Test creating ContextRequirement with all fields."""
        req = ContextRequirement(
            key="session_state",
            match_type=MatchType.EXACT,
            value_match="active",
        )
        assert req.key == "session_state"
        assert req.match_type == MatchType.EXACT
        assert req.value_match == "active"


class TestConversationAssertion:
    """Test ConversationAssertion dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating ConversationAssertion with required fields only."""
        assertion = ConversationAssertion(
            assertion_id="assert-001",
            assertion_type=AssertionType.INTENT_MATCH,
            target=AssertionTarget.INTENT,
            operator=AssertionOperator.EQUALS,
        )
        assert assertion.assertion_id == "assert-001"
        assert assertion.assertion_type == AssertionType.INTENT_MATCH
        assert assertion.target == AssertionTarget.INTENT
        assert assertion.operator == AssertionOperator.EQUALS
        assert assertion.severity == AssertionSeverity.ERROR
        assert assertion.expected_value is None

    def test_create_full(self) -> None:
        """Test creating ConversationAssertion with all fields."""
        assertion = ConversationAssertion(
            assertion_id="assert-002",
            assertion_type=AssertionType.QUALITY_SCORE,
            target=AssertionTarget.COHERENCE,
            operator=AssertionOperator.GREATER_OR_EQUAL,
            severity=AssertionSeverity.CRITICAL,
            expected_value="0.85",
            threshold=0.85,
            tolerance=0.05,
            message="Coherence must be at least 85%",
        )
        assert assertion.assertion_id == "assert-002"
        assert assertion.assertion_type == AssertionType.QUALITY_SCORE
        assert assertion.severity == AssertionSeverity.CRITICAL
        assert assertion.threshold == 0.85
        assert assertion.tolerance == 0.05
        assert assertion.message == "Coherence must be at least 85%"


class TestTestTurn:
    """Test TestTurn dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating TestTurn with required fields only."""
        turn = TestTurn(turn_number=1, role=TurnRole.USER, input="Hello")
        assert turn.turn_number == 1
        assert turn.role == TurnRole.USER
        assert turn.input == "Hello"
        assert turn.expected_intent is None
        assert turn.expected_entities == []
        assert turn.assertions == []
        assert turn.context_requirements == []
        assert turn.delay_ms is None
        assert turn.metadata is None

    def test_create_full(self) -> None:
        """Test creating TestTurn with all fields."""
        turn = TestTurn(
            turn_number=2,
            role=TurnRole.USER,
            input="What's the weather in New York?",
            expected_intent="get_weather",
            expected_entities=[ExpectedEntity(entity_type="location", value="New York")],
            assertions=[
                ConversationAssertion(
                    assertion_id="a1",
                    assertion_type=AssertionType.INTENT_MATCH,
                    target=AssertionTarget.INTENT,
                    operator=AssertionOperator.EQUALS,
                )
            ],
            context_requirements=[ContextRequirement(key="session_active")],
            delay_ms=100,
            metadata={"test_phase": "weather_flow"},
        )
        assert turn.turn_number == 2
        assert turn.expected_intent == "get_weather"
        assert len(turn.expected_entities) == 1
        assert len(turn.assertions) == 1
        assert len(turn.context_requirements) == 1
        assert turn.delay_ms == 100
        assert turn.metadata == {"test_phase": "weather_flow"}


# ============================================
# Expected Outcome Tests
# ============================================


class TestQualityRequirements:
    """Test QualityRequirements dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating QualityRequirements with defaults."""
        reqs = QualityRequirements()
        assert reqs.min_coherence is None
        assert reqs.min_naturalness is None
        assert reqs.min_accuracy is None
        assert reqs.min_relevance is None
        assert reqs.max_drift_score is None
        assert reqs.min_confidence is None

    def test_create_full(self) -> None:
        """Test creating QualityRequirements with all fields."""
        reqs = QualityRequirements(
            min_coherence=0.85,
            min_naturalness=0.80,
            min_accuracy=0.90,
            min_relevance=0.75,
            max_drift_score=0.30,
            min_confidence=0.70,
        )
        assert reqs.min_coherence == 0.85
        assert reqs.min_naturalness == 0.80
        assert reqs.min_accuracy == 0.90
        assert reqs.min_relevance == 0.75
        assert reqs.max_drift_score == 0.30
        assert reqs.min_confidence == 0.70


class TestExpectedOutcome:
    """Test ExpectedOutcome dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating ExpectedOutcome with defaults."""
        outcome = ExpectedOutcome()
        assert outcome.success_condition == SuccessCondition.ALL_PASS
        assert outcome.min_assertions_passed is None
        assert outcome.required_assertions == []
        assert outcome.max_warnings is None
        assert outcome.final_intent is None
        assert outcome.final_context_state is None
        assert outcome.quality_requirements is None

    def test_create_full(self) -> None:
        """Test creating ExpectedOutcome with all fields."""
        outcome = ExpectedOutcome(
            success_condition=SuccessCondition.THRESHOLD,
            min_assertions_passed=8,
            required_assertions=["assert-001", "assert-002"],
            max_warnings=3,
            final_intent="booking_confirmed",
            final_context_state={"booking_status": "confirmed"},
            quality_requirements=QualityRequirements(min_coherence=0.85),
        )
        assert outcome.success_condition == SuccessCondition.THRESHOLD
        assert outcome.min_assertions_passed == 8
        assert outcome.required_assertions == ["assert-001", "assert-002"]
        assert outcome.max_warnings == 3
        assert outcome.final_intent == "booking_confirmed"
        assert outcome.final_context_state == {"booking_status": "confirmed"}
        assert outcome.quality_requirements is not None


# ============================================
# Quality Thresholds Tests
# ============================================


class TestQualityThresholds:
    """Test QualityThresholds dataclass."""

    def test_default_values(self) -> None:
        """Test QualityThresholds has correct default values."""
        thresholds = QualityThresholds()
        assert thresholds.coherence_threshold == 0.85
        assert thresholds.naturalness_threshold == 0.80
        assert thresholds.accuracy_threshold == 0.90
        assert thresholds.relevance_threshold == 0.75
        assert thresholds.confidence_threshold == 0.70
        assert thresholds.max_drift_threshold == 0.50
        assert thresholds.latency_threshold_ms == 2000
        assert thresholds.strict_mode is False

    def test_custom_values(self) -> None:
        """Test QualityThresholds with custom values."""
        thresholds = QualityThresholds(
            coherence_threshold=0.90,
            naturalness_threshold=0.85,
            accuracy_threshold=0.95,
            relevance_threshold=0.80,
            confidence_threshold=0.75,
            max_drift_threshold=0.40,
            latency_threshold_ms=1000,
            strict_mode=True,
        )
        assert thresholds.coherence_threshold == 0.90
        assert thresholds.naturalness_threshold == 0.85
        assert thresholds.accuracy_threshold == 0.95
        assert thresholds.strict_mode is True


# ============================================
# Core Test Type Tests
# ============================================


class TestConversationTest:
    """Test ConversationTest dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating ConversationTest with required fields only."""
        test = ConversationTest(
            test_id="test-001",
            name="Simple greeting test",
            turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hello")],
            expected_outcome=ExpectedOutcome(),
        )
        assert test.test_id == "test-001"
        assert test.name == "Simple greeting test"
        assert len(test.turns) == 1
        assert test.category == TestCategory.QUALITY_ASSURANCE
        assert test.priority == TestPriority.MEDIUM
        assert test.description is None
        assert test.tags == []

    def test_create_full(self) -> None:
        """Test creating ConversationTest with all fields."""
        test = ConversationTest(
            test_id="test-002",
            name="Weather flow test",
            description="Tests the complete weather inquiry flow",
            category=TestCategory.DIALOGUE_FLOW,
            priority=TestPriority.HIGH,
            tags=["weather", "integration", "core"],
            setup=TestSetup(initial_context={"session_id": "test123"}),
            turns=[
                TestTurn(turn_number=1, role=TurnRole.USER, input="What's the weather?"),
                TestTurn(turn_number=2, role=TurnRole.ASSISTANT, input="Which city?"),
                TestTurn(turn_number=3, role=TurnRole.USER, input="New York"),
            ],
            expected_outcome=ExpectedOutcome(
                final_intent="weather_provided",
                quality_requirements=QualityRequirements(min_coherence=0.85),
            ),
            quality_thresholds=QualityThresholds(coherence_threshold=0.90),
            timeout_seconds=30,
            metadata={"author": "test-team", "version": "1.0"},
        )
        assert test.test_id == "test-002"
        assert test.category == TestCategory.DIALOGUE_FLOW
        assert test.priority == TestPriority.HIGH
        assert len(test.tags) == 3
        assert test.setup is not None
        assert len(test.turns) == 3
        assert test.timeout_seconds == 30
        assert test.metadata == {"author": "test-team", "version": "1.0"}


# ============================================
# Test Execution Result Tests
# ============================================


class TestExtractedEntity:
    """Test ExtractedEntity dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating ExtractedEntity with required fields only."""
        entity = ExtractedEntity(entity_type="date", value="2024-01-15", confidence=0.95)
        assert entity.entity_type == "date"
        assert entity.value == "2024-01-15"
        assert entity.confidence == 0.95
        assert entity.start_offset is None
        assert entity.end_offset is None

    def test_create_full(self) -> None:
        """Test creating ExtractedEntity with all fields."""
        entity = ExtractedEntity(
            entity_type="location",
            value="New York",
            confidence=0.98,
            start_offset=10,
            end_offset=18,
        )
        assert entity.start_offset == 10
        assert entity.end_offset == 18


class TestTurnResult:
    """Test TurnResult dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating TurnResult with required fields only."""
        result = TurnResult(turn_number=1, input="Hello", passed=True, latency_ms=150)
        assert result.turn_number == 1
        assert result.input == "Hello"
        assert result.passed is True
        assert result.latency_ms == 150
        assert result.actual_response is None
        assert result.detected_intent is None
        assert result.extracted_entities == []

    def test_create_full(self) -> None:
        """Test creating TurnResult with all fields."""
        result = TurnResult(
            turn_number=2,
            input="What's the weather?",
            passed=True,
            latency_ms=200,
            actual_response="The weather in New York is 72°F and sunny.",
            detected_intent="get_weather",
            extracted_entities=[
                ExtractedEntity(entity_type="location", value="New York", confidence=0.95)
            ],
        )
        assert result.actual_response == "The weather in New York is 72°F and sunny."
        assert result.detected_intent == "get_weather"
        assert len(result.extracted_entities) == 1


class TestAssertionResult:
    """Test AssertionResult dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating AssertionResult with required fields only."""
        result = AssertionResult(
            assertion_id="a1",
            turn_number=1,
            assertion_type=AssertionType.INTENT_MATCH,
            passed=True,
            severity=AssertionSeverity.ERROR,
        )
        assert result.assertion_id == "a1"
        assert result.turn_number == 1
        assert result.passed is True

    def test_create_full(self) -> None:
        """Test creating AssertionResult with all fields."""
        result = AssertionResult(
            assertion_id="a2",
            turn_number=2,
            assertion_type=AssertionType.QUALITY_SCORE,
            passed=False,
            severity=AssertionSeverity.CRITICAL,
            expected_value="0.85",
            actual_value="0.72",
            message="Coherence below threshold",
        )
        assert result.passed is False
        assert result.expected_value == "0.85"
        assert result.actual_value == "0.72"
        assert result.message == "Coherence below threshold"


class TestQualityScores:
    """Test QualityScores dataclass."""

    def test_create(self) -> None:
        """Test creating QualityScores."""
        scores = QualityScores(
            coherence=0.88,
            naturalness=0.82,
            accuracy=0.91,
            relevance=0.79,
            avg_confidence=0.85,
            max_drift_score=0.35,
            avg_latency_ms=175.5,
        )
        assert scores.coherence == 0.88
        assert scores.naturalness == 0.82
        assert scores.accuracy == 0.91
        assert scores.relevance == 0.79
        assert scores.avg_confidence == 0.85
        assert scores.max_drift_score == 0.35
        assert scores.avg_latency_ms == 175.5


class TestFailureSummary:
    """Test FailureSummary dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating FailureSummary with required fields only."""
        summary = FailureSummary(
            total_assertions=10,
            passed_count=8,
            failed_count=2,
            first_failure_turn=3,
        )
        assert summary.total_assertions == 10
        assert summary.passed_count == 8
        assert summary.failed_count == 2
        assert summary.first_failure_turn == 3
        assert summary.critical_failures == []
        assert summary.failure_categories == {}

    def test_create_full(self) -> None:
        """Test creating FailureSummary with all fields."""
        summary = FailureSummary(
            total_assertions=10,
            passed_count=7,
            failed_count=3,
            first_failure_turn=2,
            critical_failures=["Intent mismatch at turn 2", "Low coherence at turn 4"],
            failure_categories={"intent": 1, "quality": 2},
        )
        assert len(summary.critical_failures) == 2
        assert summary.failure_categories == {"intent": 1, "quality": 2}


class TestTestExecutionResult:
    """Test TestExecutionResult dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating TestExecutionResult with required fields only."""
        result = TestExecutionResult(
            test_id="test-001",
            test_name="Sample test",
            status=TestStatus.PASSED,
            started_at="2024-01-15T10:00:00Z",
            completed_at="2024-01-15T10:00:05Z",
            duration_ms=5000,
            quality_scores=QualityScores(
                coherence=0.88,
                naturalness=0.82,
                accuracy=0.91,
                relevance=0.79,
                avg_confidence=0.85,
                max_drift_score=0.35,
                avg_latency_ms=175.5,
            ),
        )
        assert result.test_id == "test-001"
        assert result.status == TestStatus.PASSED
        assert result.duration_ms == 5000
        assert result.turn_results == []
        assert result.assertion_results == []
        assert result.failure_summary is None
        assert result.logs == []

    def test_create_full(self) -> None:
        """Test creating TestExecutionResult with all fields."""
        result = TestExecutionResult(
            test_id="test-002",
            test_name="Weather flow",
            status=TestStatus.FAILED,
            started_at="2024-01-15T10:00:00Z",
            completed_at="2024-01-15T10:00:10Z",
            duration_ms=10000,
            quality_scores=QualityScores(
                coherence=0.72,
                naturalness=0.75,
                accuracy=0.80,
                relevance=0.70,
                avg_confidence=0.75,
                max_drift_score=0.45,
                avg_latency_ms=250.0,
            ),
            turn_results=[
                TurnResult(turn_number=1, input="Hello", passed=True, latency_ms=150)
            ],
            assertion_results=[
                AssertionResult(
                    assertion_id="a1",
                    turn_number=1,
                    assertion_type=AssertionType.INTENT_MATCH,
                    passed=False,
                    severity=AssertionSeverity.ERROR,
                )
            ],
            failure_summary=FailureSummary(
                total_assertions=5, passed_count=4, failed_count=1, first_failure_turn=1
            ),
            logs=["Starting test...", "Turn 1 complete", "Test failed"],
        )
        assert result.status == TestStatus.FAILED
        assert len(result.turn_results) == 1
        assert len(result.assertion_results) == 1
        assert result.failure_summary is not None
        assert len(result.logs) == 3


# ============================================
# Test Suite Tests
# ============================================


class TestTestSuite:
    """Test TestSuite dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating TestSuite with required fields only."""
        suite = TestSuite(
            suite_id="suite-001",
            name="Core tests",
            tests=[
                ConversationTest(
                    test_id="test-001",
                    name="Test 1",
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hi")],
                    expected_outcome=ExpectedOutcome(),
                )
            ],
        )
        assert suite.suite_id == "suite-001"
        assert suite.name == "Core tests"
        assert len(suite.tests) == 1
        assert suite.description is None
        assert suite.execution_order == ExecutionOrder.SEQUENTIAL
        assert suite.stop_on_failure is False
        assert suite.parallel_execution is False

    def test_create_full(self) -> None:
        """Test creating TestSuite with all fields."""
        suite = TestSuite(
            suite_id="suite-002",
            name="Integration tests",
            description="Full integration test suite",
            tests=[
                ConversationTest(
                    test_id="test-001",
                    name="Test 1",
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hi")],
                    expected_outcome=ExpectedOutcome(),
                )
            ],
            default_setup=TestSetup(initial_context={"env": "test"}),
            default_thresholds=QualityThresholds(coherence_threshold=0.90),
            execution_order=ExecutionOrder.PRIORITY,
            stop_on_failure=True,
            parallel_execution=True,
            tags=["integration", "nightly"],
        )
        assert suite.description == "Full integration test suite"
        assert suite.execution_order == ExecutionOrder.PRIORITY
        assert suite.stop_on_failure is True
        assert suite.parallel_execution is True
        assert len(suite.tags) == 2


class TestSuiteSummaryDataclass:
    """Test SuiteSummary dataclass."""

    def test_create(self) -> None:
        """Test creating SuiteSummary."""
        summary = SuiteSummary(
            total_tests=10,
            passed=8,
            failed=1,
            errors=1,
            skipped=0,
            pass_rate=0.80,
            avg_duration_ms=5000.0,
            coverage_estimate=0.75,
        )
        assert summary.total_tests == 10
        assert summary.passed == 8
        assert summary.failed == 1
        assert summary.errors == 1
        assert summary.skipped == 0
        assert summary.pass_rate == 0.80
        assert summary.avg_duration_ms == 5000.0
        assert summary.coverage_estimate == 0.75


class TestTestSuiteResult:
    """Test TestSuiteResult dataclass."""

    def test_create_minimal(self) -> None:
        """Test creating TestSuiteResult with required fields only."""
        result = TestSuiteResult(
            suite_id="suite-001",
            suite_name="Core tests",
            status=TestStatus.PASSED,
            started_at="2024-01-15T10:00:00Z",
            completed_at="2024-01-15T10:01:00Z",
            duration_ms=60000,
            summary=SuiteSummary(
                total_tests=5,
                passed=5,
                failed=0,
                errors=0,
                skipped=0,
                pass_rate=1.0,
                avg_duration_ms=12000.0,
            ),
        )
        assert result.suite_id == "suite-001"
        assert result.status == TestStatus.PASSED
        assert result.duration_ms == 60000
        assert result.test_results == []

    def test_create_full(self) -> None:
        """Test creating TestSuiteResult with all fields."""
        result = TestSuiteResult(
            suite_id="suite-002",
            suite_name="Integration tests",
            status=TestStatus.PARTIAL,
            started_at="2024-01-15T10:00:00Z",
            completed_at="2024-01-15T10:05:00Z",
            duration_ms=300000,
            summary=SuiteSummary(
                total_tests=10,
                passed=8,
                failed=2,
                errors=0,
                skipped=0,
                pass_rate=0.80,
                avg_duration_ms=30000.0,
            ),
            test_results=[
                TestExecutionResult(
                    test_id="test-001",
                    test_name="Test 1",
                    status=TestStatus.PASSED,
                    started_at="2024-01-15T10:00:00Z",
                    completed_at="2024-01-15T10:00:30Z",
                    duration_ms=30000,
                    quality_scores=QualityScores(
                        coherence=0.88,
                        naturalness=0.82,
                        accuracy=0.91,
                        relevance=0.79,
                        avg_confidence=0.85,
                        max_drift_score=0.35,
                        avg_latency_ms=175.5,
                    ),
                )
            ],
        )
        assert result.status == TestStatus.PARTIAL
        assert len(result.test_results) == 1


# ============================================
# Serialization Tests
# ============================================


class TestSerialization:
    """Test that dataclasses can be serialized."""

    def test_quality_thresholds_to_dict(self) -> None:
        """Test QualityThresholds can be converted to dict."""
        thresholds = QualityThresholds()
        data = asdict(thresholds)
        assert data["coherence_threshold"] == 0.85
        assert data["strict_mode"] is False

    def test_conversation_test_to_dict(self) -> None:
        """Test ConversationTest can be converted to dict."""
        test = ConversationTest(
            test_id="test-001",
            name="Test",
            turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hello")],
            expected_outcome=ExpectedOutcome(),
        )
        data = asdict(test)
        assert data["test_id"] == "test-001"
        assert data["name"] == "Test"
        assert len(data["turns"]) == 1
        assert data["turns"][0]["role"] == TurnRole.USER

    def test_test_execution_result_to_dict(self) -> None:
        """Test TestExecutionResult can be converted to dict."""
        result = TestExecutionResult(
            test_id="test-001",
            test_name="Test",
            status=TestStatus.PASSED,
            started_at="2024-01-15T10:00:00Z",
            completed_at="2024-01-15T10:00:05Z",
            duration_ms=5000,
            quality_scores=QualityScores(
                coherence=0.88,
                naturalness=0.82,
                accuracy=0.91,
                relevance=0.79,
                avg_confidence=0.85,
                max_drift_score=0.35,
                avg_latency_ms=175.5,
            ),
        )
        data = asdict(result)
        assert data["test_id"] == "test-001"
        assert data["status"] == TestStatus.PASSED
        assert data["quality_scores"]["coherence"] == 0.88


# ============================================
# Field Validation Tests
# ============================================


class TestFieldValidation:
    """Test dataclass field definitions."""

    def test_conversation_test_has_required_fields(self) -> None:
        """Test ConversationTest has all expected fields."""
        field_names = {f.name for f in fields(ConversationTest)}
        expected = {
            "test_id",
            "name",
            "description",
            "category",
            "priority",
            "tags",
            "setup",
            "turns",
            "expected_outcome",
            "quality_thresholds",
            "timeout_seconds",
            "metadata",
        }
        assert expected.issubset(field_names)

    def test_test_turn_has_required_fields(self) -> None:
        """Test TestTurn has all expected fields."""
        field_names = {f.name for f in fields(TestTurn)}
        expected = {
            "turn_number",
            "role",
            "input",
            "expected_intent",
            "expected_entities",
            "assertions",
            "context_requirements",
            "delay_ms",
            "metadata",
        }
        assert expected.issubset(field_names)

    def test_quality_thresholds_has_required_fields(self) -> None:
        """Test QualityThresholds has all expected fields."""
        field_names = {f.name for f in fields(QualityThresholds)}
        expected = {
            "coherence_threshold",
            "naturalness_threshold",
            "accuracy_threshold",
            "relevance_threshold",
            "confidence_threshold",
            "max_drift_threshold",
            "latency_threshold_ms",
            "strict_mode",
        }
        assert expected.issubset(field_names)
