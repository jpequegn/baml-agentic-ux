"""Conversational Testing Framework.

This module provides tools for defining and executing conversation tests.

Issue #89 - Task 6.1: Test Definition Types
Part of #29 - Phase 6: Conversational Testing Framework
"""

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
