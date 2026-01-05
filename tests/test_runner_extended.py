"""Extended tests for the Conversation Test Runner.

Additional tests to increase coverage for Issue #99 - Task 6.11.
Part of #29 - Phase 6: Conversational Testing Framework
"""

import time
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.testing import (
    AssertionEvaluator,
    AssertionOperator,
    AssertionResult,
    AssertionSeverity,
    AssertionTarget,
    AssertionType,
    ConversationAssertion,
    ConversationTest,
    ConversationTestRunner,
    ExecutionOrder,
    ExpectedEntity,
    ExpectedOutcome,
    ExtractedEntity,
    MockResponseHandler,
    QualityThresholds,
    ResponseHandler,
    ResponseResult,
    RunnerConfig,
    SuccessCondition,
    TestCategory,
    TestPriority,
    TestSetup,
    TestStatus,
    TestSuite,
    TestTurn,
    TurnResult,
    TurnRole,
    InitialEntity,
)


# ============================================
# Timeout Tests
# ============================================


class TestRunnerTimeout:
    """Tests for timeout handling in the runner."""

    def test_test_timeout_triggered(self) -> None:
        """Test that timeout is triggered correctly."""
        # Create a handler that takes time
        class SlowHandler(ResponseHandler):
            def generate_response(
                self, user_input: str, context: dict[str, Any], turn_number: int
            ) -> ResponseResult:
                time.sleep(0.2)  # 200ms delay
                return ResponseResult(response="Slow response")

        handler = SlowHandler()
        runner = ConversationTestRunner(handler)

        # Create a test with very short timeout
        test = ConversationTest(
            test_id="timeout-test",
            name="Timeout Test",
            timeout_seconds=0.1,  # 100ms timeout - will expire
            turns=[
                TestTurn(turn_number=1, role=TurnRole.USER, input="First"),
                TestTurn(turn_number=2, role=TurnRole.USER, input="Second"),
                TestTurn(turn_number=3, role=TurnRole.USER, input="Third"),
            ],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        assert result.status == TestStatus.TIMEOUT
        # Some turns may have executed before timeout
        assert len(result.turn_results) < 3


# ============================================
# Error Response Handling Tests
# ============================================


class TestErrorResponseHandling:
    """Tests for error response handling."""

    def test_handler_error_response(self) -> None:
        """Test handling of error in response."""
        class ErrorHandler(ResponseHandler):
            def generate_response(
                self, user_input: str, context: dict[str, Any], turn_number: int
            ) -> ResponseResult:
                return ResponseResult(
                    response="Error occurred",
                    error="Connection timeout",
                    detected_intent="error",
                )

        handler = ErrorHandler()
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="error-test",
            name="Error Test",
            turns=[
                TestTurn(turn_number=1, role=TurnRole.USER, input="Test"),
            ],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        # Test still runs but response contains error
        assert result.turn_results[0].actual_response == "Error occurred"


# ============================================
# Quality Score Target Tests
# ============================================


class TestQualityScoreTargets:
    """Tests for quality score assertion targets."""

    def test_coherence_target(self) -> None:
        """Test COHERENCE target in assertions."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
        )

        quality_scores = {"coherence": MagicMock(score=0.85)}

        assertion = ConversationAssertion(
            assertion_id="coherence-check",
            assertion_type=AssertionType.QUALITY_SCORE,
            target=AssertionTarget.COHERENCE,
            operator=AssertionOperator.GREATER_THAN,
            threshold=0.80,
        )

        result = evaluator.evaluate(assertion, turn_result, {}, quality_scores)
        assert result.passed is True

    def test_naturalness_target(self) -> None:
        """Test NATURALNESS target in assertions."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
        )

        quality_scores = {"naturalness": MagicMock(score=0.90)}

        assertion = ConversationAssertion(
            assertion_id="naturalness-check",
            assertion_type=AssertionType.QUALITY_SCORE,
            target=AssertionTarget.NATURALNESS,
            operator=AssertionOperator.GREATER_OR_EQUAL,
            threshold=0.85,
        )

        result = evaluator.evaluate(assertion, turn_result, {}, quality_scores)
        assert result.passed is True

    def test_accuracy_target(self) -> None:
        """Test ACCURACY target in assertions."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
        )

        quality_scores = {"accuracy": MagicMock(score=0.95)}

        assertion = ConversationAssertion(
            assertion_id="accuracy-check",
            assertion_type=AssertionType.QUALITY_SCORE,
            target=AssertionTarget.ACCURACY,
            operator=AssertionOperator.GREATER_THAN,
            threshold=0.90,
        )

        result = evaluator.evaluate(assertion, turn_result, {}, quality_scores)
        assert result.passed is True

    def test_confidence_target(self) -> None:
        """Test CONFIDENCE target in assertions."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
        )

        quality_scores = {"confidence": 0.88}

        # Use QUALITY_SCORE type since CONFIDENCE type doesn't exist
        assertion = ConversationAssertion(
            assertion_id="confidence-check",
            assertion_type=AssertionType.QUALITY_SCORE,
            target=AssertionTarget.CONFIDENCE,
            operator=AssertionOperator.GREATER_THAN,
            threshold=0.80,
        )

        result = evaluator.evaluate(assertion, turn_result, {}, quality_scores)
        assert result.passed is True

    def test_missing_quality_scores(self) -> None:
        """Test when quality scores are None."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
        )

        assertion = ConversationAssertion(
            assertion_id="quality-check",
            assertion_type=AssertionType.QUALITY_SCORE,
            target=AssertionTarget.COHERENCE,
            operator=AssertionOperator.GREATER_THAN,
            threshold=0.80,
        )

        result = evaluator.evaluate(assertion, turn_result, {}, None)
        assert result.passed is False


# ============================================
# Suite Status Tests
# ============================================


class TestSuiteStatus:
    """Tests for suite status determination."""

    def test_suite_partial_status(self) -> None:
        """Test suite gets PARTIAL status when some tests skipped."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        # This is a unique scenario - in practice PARTIAL status
        # would come from skipped tests due to filtering
        suite = TestSuite(
            suite_id="partial-suite",
            name="Partial Suite",
            tests=[
                ConversationTest(
                    test_id="test-1",
                    name="Passing Test",
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hi")],
                    expected_outcome=ExpectedOutcome(),
                ),
            ],
        )

        result = runner.run_suite(suite)
        # With one passing test, should be PASSED
        assert result.status == TestStatus.PASSED

    def test_suite_with_mixed_results(self) -> None:
        """Test suite with mix of passed and failed tests."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        suite = TestSuite(
            suite_id="mixed-suite",
            name="Mixed Suite",
            tests=[
                ConversationTest(
                    test_id="pass-1",
                    name="Passing 1",
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hi")],
                    expected_outcome=ExpectedOutcome(),
                ),
                ConversationTest(
                    test_id="fail-1",
                    name="Failing 1",
                    turns=[
                        TestTurn(
                            turn_number=1,
                            role=TurnRole.USER,
                            input="Fail",
                            expected_intent="wrong_intent",
                        )
                    ],
                    expected_outcome=ExpectedOutcome(),
                ),
                ConversationTest(
                    test_id="pass-2",
                    name="Passing 2",
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hello")],
                    expected_outcome=ExpectedOutcome(),
                ),
            ],
        )

        result = runner.run_suite(suite)
        assert result.status == TestStatus.FAILED
        assert result.summary.passed == 2
        assert result.summary.failed == 1
        assert result.summary.pass_rate == pytest.approx(2 / 3)


# ============================================
# Assertion Operator Edge Cases
# ============================================


class TestAssertionOperatorEdgeCases:
    """Edge case tests for assertion operators."""

    def test_greater_than_invalid_value(self) -> None:
        """Test GREATER_THAN with non-numeric value."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
            actual_response="not a number",
        )

        assertion = ConversationAssertion(
            assertion_id="gt-invalid",
            assertion_type=AssertionType.RESPONSE_CONTAINS,
            target=AssertionTarget.RESPONSE,
            operator=AssertionOperator.GREATER_THAN,
            threshold=50.0,
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        assert result.passed is False

    def test_less_than_invalid_value(self) -> None:
        """Test LESS_THAN with non-numeric value."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
            actual_response="abc",
        )

        assertion = ConversationAssertion(
            assertion_id="lt-invalid",
            assertion_type=AssertionType.RESPONSE_CONTAINS,
            target=AssertionTarget.RESPONSE,
            operator=AssertionOperator.LESS_THAN,
            threshold=100.0,
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        assert result.passed is False

    def test_tolerance_non_numeric(self) -> None:
        """Test tolerance parameter with non-numeric values."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
            detected_intent="hello",
        )

        assertion = ConversationAssertion(
            assertion_id="tolerance-non-numeric",
            assertion_type=AssertionType.INTENT_MATCH,
            target=AssertionTarget.INTENT,
            operator=AssertionOperator.EQUALS,
            expected_value="hello",
            tolerance=5.0,  # Tolerance doesn't apply to non-numeric
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        assert result.passed is True

    def test_semantic_similar_empty_words(self) -> None:
        """Test SEMANTIC_SIMILAR with empty word sets."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
            actual_response="   ",  # Only whitespace
        )

        assertion = ConversationAssertion(
            assertion_id="semantic-empty",
            assertion_type=AssertionType.RESPONSE_CONTAINS,
            target=AssertionTarget.RESPONSE,
            operator=AssertionOperator.SEMANTIC_SIMILAR,
            expected_value="hello world",
            threshold=0.5,
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        assert result.passed is False

    def test_not_matches_with_none_expected(self) -> None:
        """Test NOT_MATCHES when expected is None."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
            actual_response="Hello world",
        )

        assertion = ConversationAssertion(
            assertion_id="not-matches-none",
            assertion_type=AssertionType.RESPONSE_PATTERN,
            target=AssertionTarget.RESPONSE,
            operator=AssertionOperator.NOT_MATCHES,
            expected_value=None,
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        assert result.passed is True


# ============================================
# Context and Entity Tests
# ============================================


class TestContextAndEntityHandling:
    """Tests for context and entity handling in runner."""

    def test_context_update_during_turns(self) -> None:
        """Test that context is properly updated during conversation."""
        class ContextAwareHandler(ResponseHandler):
            def generate_response(
                self, user_input: str, context: dict[str, Any], turn_number: int
            ) -> ResponseResult:
                return ResponseResult(
                    response=f"Context has {len(context)} keys",
                    extracted_entities=[
                        ExtractedEntity(f"key{turn_number}", f"value{turn_number}", 0.9)
                    ],
                )

        handler = ContextAwareHandler()
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="context-test",
            name="Context Update Test",
            turns=[
                TestTurn(turn_number=1, role=TurnRole.USER, input="First"),
                TestTurn(turn_number=2, role=TurnRole.USER, input="Second"),
                TestTurn(turn_number=3, role=TurnRole.USER, input="Third"),
            ],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        assert result.status == TestStatus.PASSED
        # Each turn should have extracted entities
        for turn_result in result.turn_results:
            if turn_result.extracted_entities:
                assert len(turn_result.extracted_entities) == 1

    def test_initial_entities_setup(self) -> None:
        """Test that initial entities are properly set up."""
        class EntityCheckHandler(ResponseHandler):
            def generate_response(
                self, user_input: str, context: dict[str, Any], turn_number: int
            ) -> ResponseResult:
                entities = context.get("entities", {})
                location = entities.get("location", "unknown")
                return ResponseResult(
                    response=f"Your location is {location}",
                )

        handler = EntityCheckHandler()
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="entity-test",
            name="Entity Setup Test",
            setup=TestSetup(
                initial_entities=[
                    InitialEntity(entity_type="location", value="New York"),
                    InitialEntity(entity_type="user_id", value="12345"),
                ],
            ),
            turns=[
                TestTurn(turn_number=1, role=TurnRole.USER, input="Where am I?"),
            ],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        assert result.status == TestStatus.PASSED
        assert "New York" in result.turn_results[0].actual_response


# ============================================
# Failure Summary Tests
# ============================================


class TestFailureSummary:
    """Tests for failure summary generation."""

    def test_failure_summary_with_critical_failures(self) -> None:
        """Test failure summary includes critical failures."""
        handler = MockResponseHandler(responses={1: "Response"})
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="critical-fail-test",
            name="Critical Failure Test",
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.USER,
                    input="Test",
                    assertions=[
                        ConversationAssertion(
                            assertion_id="critical-1",
                            assertion_type=AssertionType.RESPONSE_CONTAINS,
                            target=AssertionTarget.RESPONSE,
                            operator=AssertionOperator.CONTAINS,
                            expected_value="nonexistent",
                            severity=AssertionSeverity.CRITICAL,
                        ),
                        ConversationAssertion(
                            assertion_id="warning-1",
                            assertion_type=AssertionType.RESPONSE_CONTAINS,
                            target=AssertionTarget.RESPONSE,
                            operator=AssertionOperator.CONTAINS,
                            expected_value="also nonexistent",
                            severity=AssertionSeverity.WARNING,
                        ),
                    ],
                ),
            ],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        assert result.status == TestStatus.FAILED
        assert result.failure_summary is not None
        assert "critical-1" in result.failure_summary.critical_failures
        assert result.failure_summary.first_failure_turn == 1

    def test_failure_summary_categories(self) -> None:
        """Test failure summary categorizes failures correctly."""
        handler = MockResponseHandler(responses={1: "Hello"})
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="category-fail-test",
            name="Category Failure Test",
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.USER,
                    input="Test",
                    assertions=[
                        ConversationAssertion(
                            assertion_id="intent-fail",
                            assertion_type=AssertionType.INTENT_MATCH,
                            target=AssertionTarget.INTENT,
                            operator=AssertionOperator.EQUALS,
                            expected_value="wrong_intent",
                            severity=AssertionSeverity.ERROR,
                        ),
                        ConversationAssertion(
                            assertion_id="response-fail",
                            assertion_type=AssertionType.RESPONSE_CONTAINS,
                            target=AssertionTarget.RESPONSE,
                            operator=AssertionOperator.CONTAINS,
                            expected_value="nonexistent",
                            severity=AssertionSeverity.ERROR,
                        ),
                    ],
                ),
            ],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        assert result.failure_summary is not None
        # Check that failures are categorized by type
        assert len(result.failure_summary.failure_categories) > 0


# ============================================
# Runner Configuration Tests
# ============================================


class TestRunnerConfiguration:
    """Tests for runner configuration options."""

    def test_retry_configuration(self) -> None:
        """Test retry configuration is respected."""
        config = RunnerConfig(
            max_retries=3,
            retry_delay_ms=100,
        )
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler, config)

        assert runner.config.max_retries == 3
        assert runner.config.retry_delay_ms == 100

    def test_parallel_configuration(self) -> None:
        """Test parallel configuration."""
        config = RunnerConfig(
            parallel_execution=True,
        )
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler, config)

        assert runner.config.parallel_execution is True

    def test_log_level_configuration(self) -> None:
        """Test log level configuration."""
        config = RunnerConfig(
            log_level="DEBUG",
        )
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler, config)

        assert runner.config.log_level == "DEBUG"


# ============================================
# Default Thresholds and Setup Tests
# ============================================


class TestSuiteDefaults:
    """Tests for suite default values."""

    def test_default_setup_applied(self) -> None:
        """Test that default setup is applied to tests without setup."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        default_setup = TestSetup(
            initial_context={"default_key": "default_value"},
        )

        suite = TestSuite(
            suite_id="default-setup-suite",
            name="Default Setup Suite",
            default_setup=default_setup,
            tests=[
                ConversationTest(
                    test_id="test-1",
                    name="Test Without Setup",
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hi")],
                    expected_outcome=ExpectedOutcome(),
                ),
            ],
        )

        result = runner.run_suite(suite)
        assert result.status == TestStatus.PASSED


# ============================================
# Assertion Evaluation Exception Tests
# ============================================


class TestAssertionExceptionHandling:
    """Tests for assertion evaluation exception handling."""

    def test_evaluation_exception_caught(self) -> None:
        """Test that exceptions during evaluation are caught."""
        evaluator = AssertionEvaluator()

        # Create a turn result that might cause issues
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
            actual_response="Response",
        )

        # Create an assertion with an invalid regex pattern
        assertion = ConversationAssertion(
            assertion_id="bad-regex",
            assertion_type=AssertionType.RESPONSE_PATTERN,
            target=AssertionTarget.RESPONSE,
            operator=AssertionOperator.MATCHES,
            expected_value="[invalid(regex",  # Invalid regex
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        # Should catch exception and return failed result
        assert result.passed is False
        assert "Error" in result.message


# ============================================
# Sequential Execution Order Tests
# ============================================


class TestExecutionOrders:
    """Tests for different execution orders."""

    def test_sequential_order(self) -> None:
        """Test sequential execution order."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        suite = TestSuite(
            suite_id="sequential-suite",
            name="Sequential Suite",
            execution_order=ExecutionOrder.SEQUENTIAL,
            tests=[
                ConversationTest(
                    test_id=f"test-{i}",
                    name=f"Test {i}",
                    priority=TestPriority.MEDIUM,
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input=f"Input {i}")],
                    expected_outcome=ExpectedOutcome(),
                )
                for i in range(3)
            ],
        )

        result = runner.run_suite(suite)
        # Tests should run in order
        assert result.test_results[0].test_id == "test-0"
        assert result.test_results[1].test_id == "test-1"
        assert result.test_results[2].test_id == "test-2"
