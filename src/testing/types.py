"""Conversational Testing Framework Types.

This module provides Python dataclasses for conversation test definitions.

Issue #89 - Task 6.1: Test Definition Types
Part of #29 - Phase 6: Conversational Testing Framework
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ============================================
# Core Enums
# ============================================


class TestCategory(Enum):
    """Category of conversation test."""

    INTENT_RECOGNITION = "intent_recognition"
    ENTITY_EXTRACTION = "entity_extraction"
    DIALOGUE_FLOW = "dialogue_flow"
    ERROR_HANDLING = "error_handling"
    CONTEXT_RETENTION = "context_retention"
    DRIFT_DETECTION = "drift_detection"
    QUALITY_ASSURANCE = "quality_assurance"
    REGRESSION = "regression"
    PERFORMANCE = "performance"


class TestPriority(Enum):
    """Test priority level."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    EXPLORATORY = "exploratory"


class TurnRole(Enum):
    """Role in the conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MatchType(Enum):
    """How to match values."""

    EXACT = "exact"
    CONTAINS = "contains"
    REGEX = "regex"
    SEMANTIC = "semantic"
    EXISTS = "exists"
    TYPE_CHECK = "type_check"


class AssertionType(Enum):
    """Type of assertion."""

    INTENT_MATCH = "intent_match"
    ENTITY_PRESENT = "entity_present"
    ENTITY_VALUE = "entity_value"
    RESPONSE_CONTAINS = "response_contains"
    RESPONSE_NOT_CONTAINS = "response_not_contains"
    RESPONSE_PATTERN = "response_pattern"
    QUALITY_SCORE = "quality_score"
    CONFIDENCE_SCORE = "confidence_score"
    CONTEXT_VALUE = "context_value"
    LATENCY = "latency"
    TOKEN_COUNT = "token_count"
    CUSTOM = "custom"


class AssertionTarget(Enum):
    """What the assertion targets."""

    INTENT = "intent"
    ENTITIES = "entities"
    RESPONSE = "response"
    CONTEXT = "context"
    CONFIDENCE = "confidence"
    COHERENCE = "coherence"
    NATURALNESS = "naturalness"
    ACCURACY = "accuracy"
    LATENCY = "latency"
    TOKENS = "tokens"
    METADATA = "metadata"


class AssertionOperator(Enum):
    """Comparison operator for assertions."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_OR_EQUAL = "greater_or_equal"
    LESS_THAN = "less_than"
    LESS_OR_EQUAL = "less_or_equal"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    MATCHES = "matches"
    NOT_MATCHES = "not_matches"
    SEMANTIC_SIMILAR = "semantic_similar"
    IN_SET = "in_set"
    NOT_IN_SET = "not_in_set"


class AssertionSeverity(Enum):
    """How critical an assertion failure is."""

    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class SuccessCondition(Enum):
    """How test success is determined."""

    ALL_PASS = "all_pass"
    THRESHOLD = "threshold"
    REQUIRED_ONLY = "required_only"
    CUSTOM = "custom"


class ExpertiseLevel(Enum):
    """User expertise level."""

    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class MockResponseType(Enum):
    """Type of mocked response."""

    API_RESPONSE = "api_response"
    DATABASE_RESULT = "database_result"
    EXTERNAL_SERVICE = "external_service"
    ERROR = "error"


class TestStatus(Enum):
    """Overall test status."""

    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"
    TIMEOUT = "timeout"
    PARTIAL = "partial"


class ExecutionOrder(Enum):
    """Test execution order."""

    SEQUENTIAL = "sequential"
    PRIORITY = "priority"
    RANDOM = "random"
    DEPENDENCY = "dependency"


# ============================================
# Test Setup Types
# ============================================


@dataclass
class InitialEntity:
    """Pre-populated entity for test."""

    entity_type: str
    value: str
    slot_name: Optional[str] = None
    confidence: Optional[float] = None


@dataclass
class TestUserProfile:
    """Simulated user profile for testing."""

    user_id: str
    expertise_level: ExpertiseLevel
    preferences: Optional[dict[str, str]] = None
    history_summary: Optional[str] = None
    accessibility_needs: list[str] = field(default_factory=list)


@dataclass
class SystemState:
    """Initial system state for testing."""

    active_capabilities: list[str] = field(default_factory=list)
    disabled_capabilities: list[str] = field(default_factory=list)
    rate_limits: Optional[dict[str, int]] = None
    feature_flags: Optional[dict[str, bool]] = None


@dataclass
class MockResponse:
    """Mocked external response."""

    trigger_pattern: str
    response_type: MockResponseType
    response_data: str
    delay_ms: Optional[int] = None
    fail_after: Optional[int] = None


@dataclass
class TestSetup:
    """Pre-test configuration."""

    initial_context: Optional[dict[str, str]] = None
    initial_entities: list[InitialEntity] = field(default_factory=list)
    user_profile: Optional[TestUserProfile] = None
    system_state: Optional[SystemState] = None
    mock_responses: list[MockResponse] = field(default_factory=list)
    environment_variables: Optional[dict[str, str]] = None


# ============================================
# Test Turn Types
# ============================================


@dataclass
class ExpectedEntity:
    """Expected entity to be extracted."""

    entity_type: str
    required: bool = True
    value: Optional[str] = None
    value_pattern: Optional[str] = None
    slot_name: Optional[str] = None


@dataclass
class ContextRequirement:
    """Context requirement for a turn."""

    key: str
    match_type: MatchType = MatchType.EXISTS
    value_match: Optional[str] = None


@dataclass
class ConversationAssertion:
    """Flexible assertion for conversation testing."""

    assertion_id: str
    assertion_type: AssertionType
    target: AssertionTarget
    operator: AssertionOperator
    severity: AssertionSeverity = AssertionSeverity.ERROR
    expected_value: Optional[str] = None
    threshold: Optional[float] = None
    tolerance: Optional[float] = None
    message: Optional[str] = None


@dataclass
class TestTurn:
    """Individual conversation turn in a test."""

    turn_number: int
    role: TurnRole
    input: str
    expected_intent: Optional[str] = None
    expected_entities: list[ExpectedEntity] = field(default_factory=list)
    assertions: list[ConversationAssertion] = field(default_factory=list)
    context_requirements: list[ContextRequirement] = field(default_factory=list)
    delay_ms: Optional[int] = None
    metadata: Optional[dict[str, str]] = None


# ============================================
# Expected Outcome Types
# ============================================


@dataclass
class QualityRequirements:
    """Quality score requirements for test success."""

    min_coherence: Optional[float] = None
    min_naturalness: Optional[float] = None
    min_accuracy: Optional[float] = None
    min_relevance: Optional[float] = None
    max_drift_score: Optional[float] = None
    min_confidence: Optional[float] = None


@dataclass
class ExpectedOutcome:
    """Success criteria for a test."""

    success_condition: SuccessCondition = SuccessCondition.ALL_PASS
    min_assertions_passed: Optional[int] = None
    required_assertions: list[str] = field(default_factory=list)
    max_warnings: Optional[int] = None
    final_intent: Optional[str] = None
    final_context_state: Optional[dict[str, str]] = None
    quality_requirements: Optional[QualityRequirements] = None


# ============================================
# Quality Threshold Types
# ============================================


@dataclass
class QualityThresholds:
    """Configurable quality thresholds."""

    coherence_threshold: float = 0.85
    naturalness_threshold: float = 0.80
    accuracy_threshold: float = 0.90
    relevance_threshold: float = 0.75
    confidence_threshold: float = 0.70
    max_drift_threshold: float = 0.50
    latency_threshold_ms: int = 2000
    strict_mode: bool = False


# ============================================
# Core Test Types
# ============================================


@dataclass
class ConversationTest:
    """Main conversation test definition."""

    test_id: str
    name: str
    turns: list[TestTurn]
    expected_outcome: ExpectedOutcome
    category: TestCategory = TestCategory.QUALITY_ASSURANCE
    priority: TestPriority = TestPriority.MEDIUM
    description: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    setup: Optional[TestSetup] = None
    quality_thresholds: Optional[QualityThresholds] = None
    timeout_seconds: Optional[int] = None
    metadata: Optional[dict[str, str]] = None


# ============================================
# Test Execution Result Types
# ============================================


@dataclass
class ExtractedEntity:
    """Entity that was extracted during test."""

    entity_type: str
    value: str
    confidence: float
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None


@dataclass
class TurnResult:
    """Result of a single turn."""

    turn_number: int
    input: str
    passed: bool
    latency_ms: int
    actual_response: Optional[str] = None
    detected_intent: Optional[str] = None
    extracted_entities: list[ExtractedEntity] = field(default_factory=list)


@dataclass
class AssertionResult:
    """Result of a single assertion."""

    assertion_id: str
    turn_number: int
    assertion_type: AssertionType
    passed: bool
    severity: AssertionSeverity
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    message: Optional[str] = None


@dataclass
class QualityScores:
    """Measured quality scores from test."""

    coherence: float
    naturalness: float
    accuracy: float
    relevance: float
    avg_confidence: float
    max_drift_score: float
    avg_latency_ms: float


@dataclass
class FailureSummary:
    """Summary of test failures."""

    total_assertions: int
    passed_count: int
    failed_count: int
    first_failure_turn: int
    critical_failures: list[str] = field(default_factory=list)
    failure_categories: dict[str, int] = field(default_factory=dict)


@dataclass
class TestExecutionResult:
    """Result of executing a conversation test."""

    test_id: str
    test_name: str
    status: TestStatus
    started_at: str
    completed_at: str
    duration_ms: int
    quality_scores: QualityScores
    turn_results: list[TurnResult] = field(default_factory=list)
    assertion_results: list[AssertionResult] = field(default_factory=list)
    failure_summary: Optional[FailureSummary] = None
    logs: list[str] = field(default_factory=list)


# ============================================
# Test Suite Types
# ============================================


@dataclass
class TestSuite:
    """Collection of related tests."""

    suite_id: str
    name: str
    tests: list[ConversationTest]
    description: Optional[str] = None
    default_setup: Optional[TestSetup] = None
    default_thresholds: Optional[QualityThresholds] = None
    execution_order: ExecutionOrder = ExecutionOrder.SEQUENTIAL
    stop_on_failure: bool = False
    parallel_execution: bool = False
    tags: list[str] = field(default_factory=list)


@dataclass
class SuiteSummary:
    """Summary statistics for suite execution."""

    total_tests: int
    passed: int
    failed: int
    errors: int
    skipped: int
    pass_rate: float
    avg_duration_ms: float
    coverage_estimate: Optional[float] = None


@dataclass
class TestSuiteResult:
    """Result of executing a test suite."""

    suite_id: str
    suite_name: str
    status: TestStatus
    started_at: str
    completed_at: str
    duration_ms: int
    summary: SuiteSummary
    test_results: list[TestExecutionResult] = field(default_factory=list)
