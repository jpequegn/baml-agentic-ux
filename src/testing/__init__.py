"""Conversational Testing Framework.

This module provides tools for defining and executing conversation tests.

Issue #89 - Task 6.1: Test Definition Types
Issue #90 - Task 6.2: Test Loader & Validator
Issue #91 - Task 6.3: Conversation Test Runner
Issue #92 - Task 6.4: Quality Scorer
Part of #29 - Phase 6: Conversational Testing Framework
"""

from .loader import (
    # Validation Types
    LoaderConfig,
    TestTemplate,
    ValidationError,
    ValidationResult,
    ValidationSeverity,
    # Main Loader
    ConversationTestLoader,
)
from .quality_scorer import (
    # Score Breakdowns
    CoherenceBreakdown,
    ContextRetentionBreakdown,
    ConversationQuality,
    DimensionScore,
    NaturalnessBreakdown,
    # Enums and Config
    QualityDimension,
    QualityScorerConfig,
    # Main Scorer
    QualityScorer,
)
from .runner import (
    # Response Handler Types
    MockResponseHandler,
    ResponseHandler,
    ResponseResult,
    # Configuration
    RunnerConfig,
    # Main Runner
    AssertionEvaluator,
    ConversationTestRunner,
)
from .types import (
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

__all__ = [
    # Loader Types
    "LoaderConfig",
    "TestTemplate",
    "ValidationError",
    "ValidationResult",
    "ValidationSeverity",
    "ConversationTestLoader",
    # Quality Scorer Types
    "CoherenceBreakdown",
    "ContextRetentionBreakdown",
    "ConversationQuality",
    "DimensionScore",
    "NaturalnessBreakdown",
    "QualityDimension",
    "QualityScorerConfig",
    "QualityScorer",
    # Runner Types
    "MockResponseHandler",
    "ResponseHandler",
    "ResponseResult",
    "RunnerConfig",
    "AssertionEvaluator",
    "ConversationTestRunner",
    # Core Enums
    "AssertionOperator",
    "AssertionSeverity",
    "AssertionTarget",
    "AssertionType",
    "ExecutionOrder",
    "ExpertiseLevel",
    "MatchType",
    "MockResponseType",
    "SuccessCondition",
    "TestCategory",
    "TestPriority",
    "TestStatus",
    "TurnRole",
    # Test Setup Types
    "InitialEntity",
    "MockResponse",
    "SystemState",
    "TestSetup",
    "TestUserProfile",
    # Test Turn Types
    "ContextRequirement",
    "ConversationAssertion",
    "ExpectedEntity",
    "TestTurn",
    # Expected Outcome Types
    "ExpectedOutcome",
    "QualityRequirements",
    # Quality Threshold Types
    "QualityThresholds",
    # Core Test Types
    "ConversationTest",
    # Test Execution Result Types
    "AssertionResult",
    "ExtractedEntity",
    "FailureSummary",
    "QualityScores",
    "TestExecutionResult",
    "TurnResult",
    # Test Suite Types
    "SuiteSummary",
    "TestSuite",
    "TestSuiteResult",
]
