"""Conversation Test Runner.

This module provides the test execution engine for conversation tests.

Issue #91 - Task 6.3: Conversation Test Runner
Part of #29 - Phase 6: Conversational Testing Framework
"""

import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from .quality_scorer import QualityScorer, QualityScorerConfig
from .types import (
    AssertionOperator,
    AssertionResult,
    AssertionSeverity,
    AssertionTarget,
    AssertionType,
    ConversationAssertion,
    ConversationTest,
    ExecutionOrder,
    ExpectedEntity,
    ExtractedEntity,
    FailureSummary,
    QualityScores,
    QualityThresholds,
    SuiteSummary,
    TestExecutionResult,
    TestStatus,
    TestSuite,
    TestSuiteResult,
    TestTurn,
    TurnResult,
    TurnRole,
)


# ============================================
# Response Handler Interface
# ============================================


class ResponseHandler(ABC):
    """Abstract interface for generating responses.

    Implementations can connect to actual LLMs or provide mock responses.
    """

    @abstractmethod
    def generate_response(
        self,
        user_input: str,
        context: dict[str, Any],
        turn_number: int,
    ) -> "ResponseResult":
        """Generate a response for the given input.

        Args:
            user_input: The user's input text
            context: Current conversation context
            turn_number: Current turn number

        Returns:
            ResponseResult with the generated response
        """
        pass


@dataclass
class ResponseResult:
    """Result from a response handler."""

    response: str
    detected_intent: Optional[str] = None
    extracted_entities: list[ExtractedEntity] = field(default_factory=list)
    confidence: float = 1.0
    latency_ms: int = 0
    error: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class MockResponseHandler(ResponseHandler):
    """Mock response handler for testing."""

    def __init__(
        self,
        responses: Optional[dict[int, str]] = None,
        default_response: str = "I understand. How can I help you?",
    ):
        """Initialize mock handler.

        Args:
            responses: Dict mapping turn numbers to responses
            default_response: Default response when no specific response defined
        """
        self.responses = responses or {}
        self.default_response = default_response
        self._call_count = 0

    def generate_response(
        self,
        user_input: str,
        context: dict[str, Any],
        turn_number: int,
    ) -> ResponseResult:
        self._call_count += 1
        response = self.responses.get(turn_number, self.default_response)
        return ResponseResult(
            response=response,
            detected_intent="general",
            confidence=0.9,
            latency_ms=50,
        )


# ============================================
# Runner Configuration
# ============================================


@dataclass
class RunnerConfig:
    """Configuration for the test runner."""

    default_timeout_seconds: int = 30
    stop_on_first_failure: bool = False
    collect_quality_metrics: bool = True
    quality_scorer_config: Optional[QualityScorerConfig] = None
    log_level: str = "INFO"
    parallel_execution: bool = False
    max_retries: int = 0
    retry_delay_ms: int = 1000


# ============================================
# Assertion Evaluator
# ============================================


class AssertionEvaluator:
    """Evaluates assertions against test results."""

    def evaluate(
        self,
        assertion: ConversationAssertion,
        turn_result: TurnResult,
        context: dict[str, Any],
        quality_scores: Optional[dict[str, Any]] = None,
    ) -> AssertionResult:
        """Evaluate a single assertion.

        Args:
            assertion: The assertion to evaluate
            turn_result: Result of the turn
            context: Current context
            quality_scores: Quality scores if available

        Returns:
            AssertionResult with pass/fail status
        """
        actual_value: Optional[str] = None
        passed = False

        try:
            # Get the actual value based on target
            actual_value = self._get_actual_value(
                assertion.target,
                turn_result,
                context,
                quality_scores,
            )

            # Evaluate based on operator
            passed = self._evaluate_operator(
                assertion.operator,
                actual_value,
                assertion.expected_value,
                assertion.threshold,
                assertion.tolerance,
            )
        except Exception as e:
            return AssertionResult(
                assertion_id=assertion.assertion_id,
                turn_number=turn_result.turn_number,
                assertion_type=assertion.assertion_type,
                passed=False,
                severity=assertion.severity,
                expected_value=assertion.expected_value,
                actual_value=str(e),
                message=f"Error evaluating assertion: {e}",
            )

        return AssertionResult(
            assertion_id=assertion.assertion_id,
            turn_number=turn_result.turn_number,
            assertion_type=assertion.assertion_type,
            passed=passed,
            severity=assertion.severity,
            expected_value=assertion.expected_value,
            actual_value=actual_value,
            message=assertion.message if not passed else None,
        )

    def _get_actual_value(
        self,
        target: AssertionTarget,
        turn_result: TurnResult,
        context: dict[str, Any],
        quality_scores: Optional[dict[str, Any]],
    ) -> Optional[str]:
        """Get the actual value for a given target."""
        if target == AssertionTarget.INTENT:
            return turn_result.detected_intent
        elif target == AssertionTarget.RESPONSE:
            return turn_result.actual_response
        elif target == AssertionTarget.ENTITIES:
            entities = [e.value for e in turn_result.extracted_entities]
            return ",".join(entities) if entities else None
        elif target == AssertionTarget.CONTEXT:
            return str(context) if context else None
        elif target == AssertionTarget.LATENCY:
            return str(turn_result.latency_ms)
        elif target in (
            AssertionTarget.COHERENCE,
            AssertionTarget.NATURALNESS,
            AssertionTarget.ACCURACY,
        ):
            if quality_scores:
                score_key = target.value
                if score_key in quality_scores:
                    return str(quality_scores[score_key].score)
            return None
        elif target == AssertionTarget.CONFIDENCE:
            if quality_scores and "confidence" in quality_scores:
                return str(quality_scores["confidence"])
            return None
        else:
            return None

    def _evaluate_operator(
        self,
        operator: AssertionOperator,
        actual: Optional[str],
        expected: Optional[str],
        threshold: Optional[float],
        tolerance: Optional[float],
    ) -> bool:
        """Evaluate the comparison operator."""
        if actual is None:
            return operator in (
                AssertionOperator.NOT_EQUALS,
                AssertionOperator.NOT_CONTAINS,
            )

        if operator == AssertionOperator.EQUALS:
            if tolerance and expected:
                try:
                    return abs(float(actual) - float(expected)) <= tolerance
                except ValueError:
                    pass
            return actual == expected

        elif operator == AssertionOperator.NOT_EQUALS:
            return actual != expected

        elif operator == AssertionOperator.CONTAINS:
            return expected is not None and expected in actual

        elif operator == AssertionOperator.NOT_CONTAINS:
            return expected is None or expected not in actual

        elif operator == AssertionOperator.MATCHES:
            return expected is not None and bool(re.search(expected, actual))

        elif operator == AssertionOperator.NOT_MATCHES:
            return expected is None or not bool(re.search(expected, actual))

        elif operator == AssertionOperator.GREATER_THAN:
            try:
                compare_val = threshold if threshold is not None else float(expected or 0)
                return float(actual) > compare_val
            except ValueError:
                return False

        elif operator == AssertionOperator.GREATER_OR_EQUAL:
            try:
                compare_val = threshold if threshold is not None else float(expected or 0)
                return float(actual) >= compare_val
            except ValueError:
                return False

        elif operator == AssertionOperator.LESS_THAN:
            try:
                compare_val = threshold if threshold is not None else float(expected or 0)
                return float(actual) < compare_val
            except ValueError:
                return False

        elif operator == AssertionOperator.LESS_OR_EQUAL:
            try:
                compare_val = threshold if threshold is not None else float(expected or 0)
                return float(actual) <= compare_val
            except ValueError:
                return False

        elif operator == AssertionOperator.IN_SET:
            if expected:
                valid_values = [v.strip() for v in expected.split(",")]
                return actual in valid_values
            return False

        elif operator == AssertionOperator.NOT_IN_SET:
            if expected:
                valid_values = [v.strip() for v in expected.split(",")]
                return actual not in valid_values
            return True

        elif operator == AssertionOperator.SEMANTIC_SIMILAR:
            # Simplified semantic similarity - just check word overlap
            if expected:
                actual_words = set(actual.lower().split())
                expected_words = set(expected.lower().split())
                if not actual_words or not expected_words:
                    return False
                overlap = len(actual_words & expected_words)
                similarity = overlap / max(len(actual_words), len(expected_words))
                min_threshold = threshold if threshold is not None else 0.5
                return similarity >= min_threshold
            return False

        return False


# ============================================
# Conversation Test Runner
# ============================================


class ConversationTestRunner:
    """Executes conversation tests and collects results."""

    def __init__(
        self,
        response_handler: ResponseHandler,
        config: Optional[RunnerConfig] = None,
    ):
        """Initialize the test runner.

        Args:
            response_handler: Handler for generating responses
            config: Runner configuration
        """
        self.response_handler = response_handler
        self.config = config or RunnerConfig()
        self._assertion_evaluator = AssertionEvaluator()
        self._quality_scorer: Optional[QualityScorer] = None
        if self.config.collect_quality_metrics:
            scorer_config = self.config.quality_scorer_config or QualityScorerConfig()
            self._quality_scorer = QualityScorer(scorer_config)
        self._logs: list[str] = []

    def run_test(self, test: ConversationTest) -> TestExecutionResult:
        """Execute a single conversation test.

        Args:
            test: The test to execute

        Returns:
            TestExecutionResult with all results
        """
        self._logs = []
        self._log(f"Starting test: {test.name} ({test.test_id})")
        started_at = datetime.now(timezone.utc)

        # Initialize context from setup
        context: dict[str, Any] = {}
        if test.setup:
            if test.setup.initial_context:
                context.update(test.setup.initial_context)
            if test.setup.initial_entities:
                context["entities"] = {
                    e.entity_type: e.value for e in test.setup.initial_entities
                }

        # Reset quality scorer if used
        if self._quality_scorer:
            self._quality_scorer.reset()

        # Execute turns
        turn_results: list[TurnResult] = []
        assertion_results: list[AssertionResult] = []
        all_passed = True
        error_occurred = False
        timeout_occurred = False

        timeout_seconds = test.timeout_seconds or self.config.default_timeout_seconds
        test_start_time = time.time()

        for turn in test.turns:
            # Check timeout
            elapsed = time.time() - test_start_time
            if elapsed > timeout_seconds:
                timeout_occurred = True
                self._log(f"Test timed out after {elapsed:.1f}s")
                break

            # Execute turn
            turn_result, turn_assertions = self._execute_turn(
                turn, context, test.quality_thresholds
            )
            turn_results.append(turn_result)
            assertion_results.extend(turn_assertions)

            # Update context with extracted entities
            if turn_result.extracted_entities:
                if "entities" not in context:
                    context["entities"] = {}
                for entity in turn_result.extracted_entities:
                    context["entities"][entity.entity_type] = entity.value

            # Track response in context
            context["last_response"] = turn_result.actual_response
            context["last_intent"] = turn_result.detected_intent

            # Check for failures
            if not turn_result.passed:
                all_passed = False
                if self.config.stop_on_first_failure:
                    self._log("Stopping on first failure")
                    break

        completed_at = datetime.now(timezone.utc)
        duration_ms = int((completed_at - started_at).total_seconds() * 1000)

        # Determine status
        status = self._determine_status(
            all_passed, error_occurred, timeout_occurred, test, assertion_results
        )

        # Calculate quality scores
        quality_scores = self._calculate_quality_scores(turn_results)

        # Build failure summary if needed
        failure_summary = None
        if status != TestStatus.PASSED:
            failure_summary = self._build_failure_summary(assertion_results)

        self._log(f"Test completed: {status.value}")

        return TestExecutionResult(
            test_id=test.test_id,
            test_name=test.name,
            status=status,
            started_at=started_at.isoformat(),
            completed_at=completed_at.isoformat(),
            duration_ms=duration_ms,
            quality_scores=quality_scores,
            turn_results=turn_results,
            assertion_results=assertion_results,
            failure_summary=failure_summary,
            logs=self._logs.copy(),
        )

    def run_suite(self, suite: TestSuite) -> TestSuiteResult:
        """Execute a test suite.

        Args:
            suite: The test suite to execute

        Returns:
            TestSuiteResult with all test results
        """
        self._log(f"Starting suite: {suite.name} ({suite.suite_id})")
        started_at = datetime.now(timezone.utc)

        # Order tests
        tests = self._order_tests(suite.tests, suite.execution_order)

        # Execute tests
        test_results: list[TestExecutionResult] = []
        for test in tests:
            # Apply suite defaults if not set on test
            if suite.default_thresholds and not test.quality_thresholds:
                test.quality_thresholds = suite.default_thresholds
            if suite.default_setup and not test.setup:
                test.setup = suite.default_setup

            result = self.run_test(test)
            test_results.append(result)

            # Stop on failure if configured
            if suite.stop_on_failure and result.status != TestStatus.PASSED:
                self._log("Stopping suite on failure")
                break

        completed_at = datetime.now(timezone.utc)
        duration_ms = int((completed_at - started_at).total_seconds() * 1000)

        # Build summary
        summary = self._build_suite_summary(test_results)

        # Determine suite status
        if summary.errors > 0:
            status = TestStatus.ERROR
        elif summary.failed > 0:
            status = TestStatus.FAILED
        elif summary.passed == summary.total_tests:
            status = TestStatus.PASSED
        else:
            status = TestStatus.PARTIAL

        return TestSuiteResult(
            suite_id=suite.suite_id,
            suite_name=suite.name,
            status=status,
            started_at=started_at.isoformat(),
            completed_at=completed_at.isoformat(),
            duration_ms=duration_ms,
            summary=summary,
            test_results=test_results,
        )

    def _execute_turn(
        self,
        turn: TestTurn,
        context: dict[str, Any],
        quality_thresholds: Optional[QualityThresholds],
    ) -> tuple[TurnResult, list[AssertionResult]]:
        """Execute a single conversation turn."""
        self._log(f"Executing turn {turn.turn_number}: {turn.role.value}")

        # Handle delay if specified
        if turn.delay_ms:
            time.sleep(turn.delay_ms / 1000)

        # Skip assistant turns (they're expected responses, not inputs)
        if turn.role == TurnRole.ASSISTANT:
            return TurnResult(
                turn_number=turn.turn_number,
                input=turn.input,
                passed=True,
                latency_ms=0,
                actual_response=turn.input,  # Expected response
                detected_intent=turn.expected_intent,
            ), []

        # Generate response for user turns
        start_time = time.time()
        response_result = self.response_handler.generate_response(
            user_input=turn.input,
            context=context,
            turn_number=turn.turn_number,
        )
        latency_ms = int((time.time() - start_time) * 1000)
        if response_result.latency_ms > 0:
            latency_ms = response_result.latency_ms

        # Build turn result
        turn_result = TurnResult(
            turn_number=turn.turn_number,
            input=turn.input,
            passed=True,  # Will update based on assertions
            latency_ms=latency_ms,
            actual_response=response_result.response,
            detected_intent=response_result.detected_intent,
            extracted_entities=response_result.extracted_entities,
        )

        # Score quality if enabled
        quality_scores = None
        if self._quality_scorer:
            expected_entities = [
                ExpectedEntity(entity_type=e.entity_type, value=e.value)
                for e in turn.expected_entities
            ]
            quality_scores = self._quality_scorer.score_turn(
                turn_result, context, expected_entities
            )

        # Evaluate assertions
        assertion_results: list[AssertionResult] = []
        for assertion in turn.assertions:
            result = self._assertion_evaluator.evaluate(
                assertion, turn_result, context, quality_scores
            )
            assertion_results.append(result)
            if not result.passed and result.severity in (
                AssertionSeverity.CRITICAL,
                AssertionSeverity.ERROR,
            ):
                turn_result.passed = False

        # Check expected intent
        if turn.expected_intent:
            if turn_result.detected_intent != turn.expected_intent:
                turn_result.passed = False
                self._log(
                    f"Intent mismatch: expected {turn.expected_intent}, "
                    f"got {turn_result.detected_intent}"
                )

        return turn_result, assertion_results

    def _determine_status(
        self,
        all_passed: bool,
        error_occurred: bool,
        timeout_occurred: bool,
        test: ConversationTest,
        assertion_results: list[AssertionResult],
    ) -> TestStatus:
        """Determine the test status based on results."""
        if timeout_occurred:
            return TestStatus.TIMEOUT
        if error_occurred:
            return TestStatus.ERROR

        # Check success condition
        success_condition = test.expected_outcome.success_condition

        if success_condition.value == "all_pass":
            return TestStatus.PASSED if all_passed else TestStatus.FAILED

        elif success_condition.value == "required_only":
            required_ids = set(test.expected_outcome.required_assertions)
            for result in assertion_results:
                if result.assertion_id in required_ids and not result.passed:
                    return TestStatus.FAILED
            return TestStatus.PASSED

        elif success_condition.value == "threshold":
            min_passed = test.expected_outcome.min_assertions_passed or 0
            passed_count = sum(1 for r in assertion_results if r.passed)
            return TestStatus.PASSED if passed_count >= min_passed else TestStatus.FAILED

        return TestStatus.PASSED if all_passed else TestStatus.FAILED

    def _calculate_quality_scores(
        self, turn_results: list[TurnResult]
    ) -> QualityScores:
        """Calculate aggregate quality scores from turn results."""
        if self._quality_scorer and turn_results:
            quality = self._quality_scorer.score_conversation(turn_results, [])
            return quality.to_quality_scores()

        # Default scores if no scorer or no turns
        avg_latency = (
            sum(t.latency_ms for t in turn_results) / len(turn_results)
            if turn_results
            else 0
        )
        return QualityScores(
            coherence=0.0,
            naturalness=0.0,
            accuracy=0.0,
            relevance=0.0,
            avg_confidence=0.0,
            max_drift_score=0.0,
            avg_latency_ms=avg_latency,
        )

    def _build_failure_summary(
        self, assertion_results: list[AssertionResult]
    ) -> FailureSummary:
        """Build a summary of test failures."""
        failed_results = [r for r in assertion_results if not r.passed]
        passed_count = len(assertion_results) - len(failed_results)

        critical_failures = [
            r.assertion_id
            for r in failed_results
            if r.severity == AssertionSeverity.CRITICAL
        ]

        failure_categories: dict[str, int] = {}
        for r in failed_results:
            cat = r.assertion_type.value
            failure_categories[cat] = failure_categories.get(cat, 0) + 1

        first_failure_turn = 0
        if failed_results:
            first_failure_turn = min(r.turn_number for r in failed_results)

        return FailureSummary(
            total_assertions=len(assertion_results),
            passed_count=passed_count,
            failed_count=len(failed_results),
            first_failure_turn=first_failure_turn,
            critical_failures=critical_failures,
            failure_categories=failure_categories,
        )

    def _build_suite_summary(
        self, test_results: list[TestExecutionResult]
    ) -> SuiteSummary:
        """Build summary statistics for a test suite."""
        total = len(test_results)
        passed = sum(1 for r in test_results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in test_results if r.status == TestStatus.FAILED)
        errors = sum(1 for r in test_results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in test_results if r.status == TestStatus.SKIPPED)

        pass_rate = passed / total if total > 0 else 0.0
        avg_duration = (
            sum(r.duration_ms for r in test_results) / total if total > 0 else 0.0
        )

        return SuiteSummary(
            total_tests=total,
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=skipped,
            pass_rate=pass_rate,
            avg_duration_ms=avg_duration,
        )

    def _order_tests(
        self, tests: list[ConversationTest], order: ExecutionOrder
    ) -> list[ConversationTest]:
        """Order tests based on execution order."""
        if order == ExecutionOrder.PRIORITY:
            priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "exploratory": 4}
            return sorted(tests, key=lambda t: priority_order.get(t.priority.value, 5))
        elif order == ExecutionOrder.RANDOM:
            import random
            shuffled = tests.copy()
            random.shuffle(shuffled)
            return shuffled
        # Default: sequential
        return tests

    def _log(self, message: str) -> None:
        """Add a log message."""
        timestamp = datetime.now(timezone.utc).isoformat()
        self._logs.append(f"[{timestamp}] {message}")
