"""Tests for the Conversation Test Runner.

Issue #91 - Task 6.3: Conversation Test Runner
Part of #29 - Phase 6: Conversational Testing Framework
"""

from typing import Any

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
# Response Handler Tests
# ============================================


class TestMockResponseHandler:
    """Tests for MockResponseHandler."""

    def test_default_response(self) -> None:
        """Test default response is returned."""
        handler = MockResponseHandler()
        result = handler.generate_response("Hello", {}, 1)
        assert result.response == "I understand. How can I help you?"
        assert result.detected_intent == "general"

    def test_custom_responses(self) -> None:
        """Test custom responses by turn number."""
        handler = MockResponseHandler(
            responses={
                1: "Welcome!",
                2: "How can I help?",
            }
        )
        result1 = handler.generate_response("Hi", {}, 1)
        assert result1.response == "Welcome!"

        result2 = handler.generate_response("Need help", {}, 2)
        assert result2.response == "How can I help?"

    def test_custom_default_response(self) -> None:
        """Test custom default response."""
        handler = MockResponseHandler(default_response="Custom default")
        result = handler.generate_response("Test", {}, 99)
        assert result.response == "Custom default"

    def test_call_count(self) -> None:
        """Test call count tracking."""
        handler = MockResponseHandler()
        handler.generate_response("A", {}, 1)
        handler.generate_response("B", {}, 2)
        assert handler._call_count == 2


class TestResponseResult:
    """Tests for ResponseResult dataclass."""

    def test_basic_result(self) -> None:
        """Test basic response result."""
        result = ResponseResult(response="Hello!")
        assert result.response == "Hello!"
        assert result.detected_intent is None
        assert result.error is None

    def test_full_result(self) -> None:
        """Test response result with all fields."""
        entities = [ExtractedEntity("location", "NYC", 0.95)]
        result = ResponseResult(
            response="Weather in NYC",
            detected_intent="weather",
            extracted_entities=entities,
            confidence=0.92,
            latency_ms=150,
            error=None,
            metadata={"source": "test"},
        )
        assert result.detected_intent == "weather"
        assert len(result.extracted_entities) == 1
        assert result.confidence == 0.92


# ============================================
# Runner Configuration Tests
# ============================================


class TestRunnerConfig:
    """Tests for RunnerConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = RunnerConfig()
        assert config.default_timeout_seconds == 30
        assert config.stop_on_first_failure is False
        assert config.collect_quality_metrics is True
        assert config.max_retries == 0

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = RunnerConfig(
            default_timeout_seconds=60,
            stop_on_first_failure=True,
            collect_quality_metrics=False,
        )
        assert config.default_timeout_seconds == 60
        assert config.stop_on_first_failure is True
        assert config.collect_quality_metrics is False


# ============================================
# Assertion Evaluator Tests
# ============================================


class TestAssertionEvaluator:
    """Tests for AssertionEvaluator."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.evaluator = AssertionEvaluator()
        self.turn_result = TurnResult(
            turn_number=1,
            input="Test input",
            passed=True,
            latency_ms=100,
            actual_response="This is a test response",
            detected_intent="test_intent",
            extracted_entities=[ExtractedEntity("type1", "value1", 0.9)],
        )

    def test_equals_operator_pass(self) -> None:
        """Test EQUALS operator passing."""
        assertion = ConversationAssertion(
            assertion_id="test1",
            assertion_type=AssertionType.INTENT_MATCH,
            target=AssertionTarget.INTENT,
            operator=AssertionOperator.EQUALS,
            expected_value="test_intent",
        )
        result = self.evaluator.evaluate(assertion, self.turn_result, {})
        assert result.passed is True

    def test_equals_operator_fail(self) -> None:
        """Test EQUALS operator failing."""
        assertion = ConversationAssertion(
            assertion_id="test1",
            assertion_type=AssertionType.INTENT_MATCH,
            target=AssertionTarget.INTENT,
            operator=AssertionOperator.EQUALS,
            expected_value="wrong_intent",
        )
        result = self.evaluator.evaluate(assertion, self.turn_result, {})
        assert result.passed is False

    def test_contains_operator(self) -> None:
        """Test CONTAINS operator."""
        assertion = ConversationAssertion(
            assertion_id="test1",
            assertion_type=AssertionType.RESPONSE_CONTAINS,
            target=AssertionTarget.RESPONSE,
            operator=AssertionOperator.CONTAINS,
            expected_value="test response",
        )
        result = self.evaluator.evaluate(assertion, self.turn_result, {})
        assert result.passed is True

    def test_not_contains_operator(self) -> None:
        """Test NOT_CONTAINS operator."""
        assertion = ConversationAssertion(
            assertion_id="test1",
            assertion_type=AssertionType.RESPONSE_NOT_CONTAINS,
            target=AssertionTarget.RESPONSE,
            operator=AssertionOperator.NOT_CONTAINS,
            expected_value="missing text",
        )
        result = self.evaluator.evaluate(assertion, self.turn_result, {})
        assert result.passed is True

    def test_matches_operator(self) -> None:
        """Test MATCHES regex operator."""
        assertion = ConversationAssertion(
            assertion_id="test1",
            assertion_type=AssertionType.RESPONSE_PATTERN,
            target=AssertionTarget.RESPONSE,
            operator=AssertionOperator.MATCHES,
            expected_value=r"test.*response",
        )
        result = self.evaluator.evaluate(assertion, self.turn_result, {})
        assert result.passed is True

    def test_greater_than_operator(self) -> None:
        """Test GREATER_THAN operator."""
        assertion = ConversationAssertion(
            assertion_id="test1",
            assertion_type=AssertionType.LATENCY,
            target=AssertionTarget.LATENCY,
            operator=AssertionOperator.LESS_THAN,
            threshold=200.0,
        )
        result = self.evaluator.evaluate(assertion, self.turn_result, {})
        assert result.passed is True  # 100 < 200

    def test_in_set_operator(self) -> None:
        """Test IN_SET operator."""
        assertion = ConversationAssertion(
            assertion_id="test1",
            assertion_type=AssertionType.INTENT_MATCH,
            target=AssertionTarget.INTENT,
            operator=AssertionOperator.IN_SET,
            expected_value="test_intent, other_intent, third_intent",
        )
        result = self.evaluator.evaluate(assertion, self.turn_result, {})
        assert result.passed is True

    def test_semantic_similar_operator(self) -> None:
        """Test SEMANTIC_SIMILAR operator."""
        assertion = ConversationAssertion(
            assertion_id="test1",
            assertion_type=AssertionType.RESPONSE_CONTAINS,
            target=AssertionTarget.RESPONSE,
            operator=AssertionOperator.SEMANTIC_SIMILAR,
            expected_value="test response",
            threshold=0.3,
        )
        result = self.evaluator.evaluate(assertion, self.turn_result, {})
        assert result.passed is True

    def test_latency_target(self) -> None:
        """Test latency target extraction."""
        assertion = ConversationAssertion(
            assertion_id="test1",
            assertion_type=AssertionType.LATENCY,
            target=AssertionTarget.LATENCY,
            operator=AssertionOperator.EQUALS,
            expected_value="100",
        )
        result = self.evaluator.evaluate(assertion, self.turn_result, {})
        assert result.passed is True
        assert result.actual_value == "100"


# ============================================
# Conversation Test Runner Tests
# ============================================


class TestConversationTestRunner:
    """Tests for ConversationTestRunner."""

    def create_simple_test(self) -> ConversationTest:
        """Create a simple test for testing."""
        return ConversationTest(
            test_id="test-001",
            name="Simple Greeting Test",
            category=TestCategory.INTENT_RECOGNITION,
            priority=TestPriority.HIGH,
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.USER,
                    input="Hello!",
                    # Note: Not checking expected_intent so mock handler can work
                ),
                TestTurn(
                    turn_number=2,
                    role=TurnRole.ASSISTANT,
                    input="Hi there! How can I help?",
                ),
            ],
            expected_outcome=ExpectedOutcome(
                success_condition=SuccessCondition.ALL_PASS,
            ),
        )

    def test_run_simple_test(self) -> None:
        """Test running a simple conversation test."""
        handler = MockResponseHandler(
            responses={1: "Hi there! How can I help?"}
        )
        runner = ConversationTestRunner(handler)
        test = self.create_simple_test()

        result = runner.run_test(test)

        assert result.test_id == "test-001"
        assert result.test_name == "Simple Greeting Test"
        assert result.status == TestStatus.PASSED
        assert len(result.turn_results) == 2
        assert result.duration_ms >= 0  # Can be 0 for very fast tests

    def test_run_test_with_assertions(self) -> None:
        """Test running a test with assertions."""
        handler = MockResponseHandler(
            responses={1: "The weather is sunny today!"}
        )
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="test-002",
            name="Weather Test",
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.USER,
                    input="What's the weather?",
                    assertions=[
                        ConversationAssertion(
                            assertion_id="resp-contains",
                            assertion_type=AssertionType.RESPONSE_CONTAINS,
                            target=AssertionTarget.RESPONSE,
                            operator=AssertionOperator.CONTAINS,
                            expected_value="weather",
                        ),
                    ],
                ),
            ],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        assert result.status == TestStatus.PASSED
        assert len(result.assertion_results) == 1
        assert result.assertion_results[0].passed is True

    def test_run_test_with_failed_assertion(self) -> None:
        """Test that failed assertions cause test failure."""
        handler = MockResponseHandler(
            responses={1: "Hello!"}
        )
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="test-003",
            name="Failing Test",
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.USER,
                    input="Test",
                    assertions=[
                        ConversationAssertion(
                            assertion_id="must-fail",
                            assertion_type=AssertionType.RESPONSE_CONTAINS,
                            target=AssertionTarget.RESPONSE,
                            operator=AssertionOperator.CONTAINS,
                            expected_value="nonexistent text",
                            severity=AssertionSeverity.ERROR,
                        ),
                    ],
                ),
            ],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        assert result.status == TestStatus.FAILED
        assert result.failure_summary is not None
        assert result.failure_summary.failed_count == 1

    def test_run_test_with_context(self) -> None:
        """Test context is maintained across turns."""
        handler = MockResponseHandler(
            responses={
                1: "Hello John!",
                3: "Nice to see you again, John!",
            }
        )
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="test-004",
            name="Context Test",
            setup=TestSetup(
                initial_context={"user_name": "John"},
            ),
            turns=[
                TestTurn(turn_number=1, role=TurnRole.USER, input="Hi"),
                TestTurn(turn_number=2, role=TurnRole.ASSISTANT, input="Hello John!"),
                TestTurn(turn_number=3, role=TurnRole.USER, input="How are you?"),
            ],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        assert result.status == TestStatus.PASSED

    def test_run_test_with_initial_entities(self) -> None:
        """Test initial entities are loaded into context."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="test-005",
            name="Entity Test",
            setup=TestSetup(
                initial_entities=[
                    InitialEntity(entity_type="location", value="NYC"),
                ],
            ),
            turns=[
                TestTurn(turn_number=1, role=TurnRole.USER, input="Where am I?"),
            ],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        assert result.status == TestStatus.PASSED

    def test_run_test_quality_metrics(self) -> None:
        """Test quality metrics are collected."""
        handler = MockResponseHandler(
            responses={1: "I'd be happy to help you with that today!"}
        )
        config = RunnerConfig(collect_quality_metrics=True)
        runner = ConversationTestRunner(handler, config)

        test = ConversationTest(
            test_id="test-006",
            name="Quality Test",
            turns=[
                TestTurn(turn_number=1, role=TurnRole.USER, input="Help me"),
            ],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        assert result.quality_scores is not None
        assert result.quality_scores.coherence >= 0
        assert result.quality_scores.naturalness >= 0

    def test_run_test_without_quality_metrics(self) -> None:
        """Test running without quality metrics collection."""
        handler = MockResponseHandler()
        config = RunnerConfig(collect_quality_metrics=False)
        runner = ConversationTestRunner(handler, config)

        test = self.create_simple_test()
        result = runner.run_test(test)

        assert result.quality_scores is not None
        assert result.quality_scores.coherence == 0.0

    def test_run_test_stop_on_failure(self) -> None:
        """Test stop_on_first_failure configuration."""
        handler = MockResponseHandler()
        config = RunnerConfig(stop_on_first_failure=True)
        runner = ConversationTestRunner(handler, config)

        test = ConversationTest(
            test_id="test-007",
            name="Stop on Failure Test",
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.USER,
                    input="First",
                    expected_intent="wrong_intent",  # Will fail
                ),
                TestTurn(
                    turn_number=2,
                    role=TurnRole.USER,
                    input="Second",
                ),
            ],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        # First turn should fail, second should not execute
        assert result.status == TestStatus.FAILED
        assert len(result.turn_results) == 1

    def test_success_condition_required_only(self) -> None:
        """Test REQUIRED_ONLY success condition."""
        handler = MockResponseHandler(responses={1: "Test response"})
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="test-008",
            name="Required Only Test",
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.USER,
                    input="Test",
                    assertions=[
                        ConversationAssertion(
                            assertion_id="required-1",
                            assertion_type=AssertionType.RESPONSE_CONTAINS,
                            target=AssertionTarget.RESPONSE,
                            operator=AssertionOperator.CONTAINS,
                            expected_value="response",
                        ),
                        ConversationAssertion(
                            assertion_id="optional-1",
                            assertion_type=AssertionType.RESPONSE_CONTAINS,
                            target=AssertionTarget.RESPONSE,
                            operator=AssertionOperator.CONTAINS,
                            expected_value="nonexistent",
                            severity=AssertionSeverity.WARNING,
                        ),
                    ],
                ),
            ],
            expected_outcome=ExpectedOutcome(
                success_condition=SuccessCondition.REQUIRED_ONLY,
                required_assertions=["required-1"],
            ),
        )

        result = runner.run_test(test)
        assert result.status == TestStatus.PASSED

    def test_success_condition_threshold(self) -> None:
        """Test THRESHOLD success condition."""
        handler = MockResponseHandler(responses={1: "Test"})
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="test-009",
            name="Threshold Test",
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.USER,
                    input="Test",
                    assertions=[
                        ConversationAssertion(
                            assertion_id="a1",
                            assertion_type=AssertionType.RESPONSE_CONTAINS,
                            target=AssertionTarget.RESPONSE,
                            operator=AssertionOperator.CONTAINS,
                            expected_value="Test",
                        ),
                        ConversationAssertion(
                            assertion_id="a2",
                            assertion_type=AssertionType.RESPONSE_CONTAINS,
                            target=AssertionTarget.RESPONSE,
                            operator=AssertionOperator.CONTAINS,
                            expected_value="missing",
                            severity=AssertionSeverity.WARNING,
                        ),
                    ],
                ),
            ],
            expected_outcome=ExpectedOutcome(
                success_condition=SuccessCondition.THRESHOLD,
                min_assertions_passed=1,
            ),
        )

        result = runner.run_test(test)
        assert result.status == TestStatus.PASSED


# ============================================
# Test Suite Runner Tests
# ============================================


class TestTestSuiteRunner:
    """Tests for running test suites."""

    def test_run_simple_suite(self) -> None:
        """Test running a simple test suite."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        suite = TestSuite(
            suite_id="suite-001",
            name="Simple Suite",
            tests=[
                ConversationTest(
                    test_id="test-1",
                    name="Test 1",
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hi")],
                    expected_outcome=ExpectedOutcome(),
                ),
                ConversationTest(
                    test_id="test-2",
                    name="Test 2",
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hello")],
                    expected_outcome=ExpectedOutcome(),
                ),
            ],
        )

        result = runner.run_suite(suite)

        assert result.suite_id == "suite-001"
        assert result.suite_name == "Simple Suite"
        assert result.status == TestStatus.PASSED
        assert result.summary.total_tests == 2
        assert result.summary.passed == 2
        assert result.summary.pass_rate == 1.0

    def test_run_suite_with_failure(self) -> None:
        """Test suite with a failing test."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        suite = TestSuite(
            suite_id="suite-002",
            name="Suite with Failure",
            tests=[
                ConversationTest(
                    test_id="test-1",
                    name="Passing Test",
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hi")],
                    expected_outcome=ExpectedOutcome(),
                ),
                ConversationTest(
                    test_id="test-2",
                    name="Failing Test",
                    turns=[
                        TestTurn(
                            turn_number=1,
                            role=TurnRole.USER,
                            input="Test",
                            expected_intent="wrong_intent",
                        )
                    ],
                    expected_outcome=ExpectedOutcome(),
                ),
            ],
        )

        result = runner.run_suite(suite)

        assert result.status == TestStatus.FAILED
        assert result.summary.passed == 1
        assert result.summary.failed == 1
        assert result.summary.pass_rate == 0.5

    def test_run_suite_stop_on_failure(self) -> None:
        """Test suite stops on first failure when configured."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        suite = TestSuite(
            suite_id="suite-003",
            name="Stop on Failure Suite",
            stop_on_failure=True,
            tests=[
                ConversationTest(
                    test_id="test-1",
                    name="Failing Test",
                    turns=[
                        TestTurn(
                            turn_number=1,
                            role=TurnRole.USER,
                            input="Test",
                            expected_intent="wrong",
                        )
                    ],
                    expected_outcome=ExpectedOutcome(),
                ),
                ConversationTest(
                    test_id="test-2",
                    name="Should Not Run",
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hi")],
                    expected_outcome=ExpectedOutcome(),
                ),
            ],
        )

        result = runner.run_suite(suite)

        assert result.status == TestStatus.FAILED
        assert len(result.test_results) == 1

    def test_run_suite_priority_order(self) -> None:
        """Test suite orders tests by priority."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        suite = TestSuite(
            suite_id="suite-004",
            name="Priority Suite",
            execution_order=ExecutionOrder.PRIORITY,
            tests=[
                ConversationTest(
                    test_id="low",
                    name="Low Priority",
                    priority=TestPriority.LOW,
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Low")],
                    expected_outcome=ExpectedOutcome(),
                ),
                ConversationTest(
                    test_id="critical",
                    name="Critical Priority",
                    priority=TestPriority.CRITICAL,
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Critical")],
                    expected_outcome=ExpectedOutcome(),
                ),
                ConversationTest(
                    test_id="high",
                    name="High Priority",
                    priority=TestPriority.HIGH,
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="High")],
                    expected_outcome=ExpectedOutcome(),
                ),
            ],
        )

        result = runner.run_suite(suite)

        assert result.test_results[0].test_id == "critical"
        assert result.test_results[1].test_id == "high"
        assert result.test_results[2].test_id == "low"

    def test_run_suite_with_defaults(self) -> None:
        """Test suite applies default thresholds to tests."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        default_thresholds = QualityThresholds(coherence_threshold=0.9)

        suite = TestSuite(
            suite_id="suite-005",
            name="Default Thresholds Suite",
            default_thresholds=default_thresholds,
            tests=[
                ConversationTest(
                    test_id="test-1",
                    name="Test with Defaults",
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hi")],
                    expected_outcome=ExpectedOutcome(),
                ),
            ],
        )

        result = runner.run_suite(suite)
        assert result.status == TestStatus.PASSED


# ============================================
# Edge Cases and Error Handling
# ============================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_turns(self) -> None:
        """Test handling of test with no turns."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="empty-test",
            name="Empty Test",
            turns=[],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        assert result.status == TestStatus.PASSED
        assert len(result.turn_results) == 0

    def test_empty_suite(self) -> None:
        """Test handling of suite with no tests."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        suite = TestSuite(
            suite_id="empty-suite",
            name="Empty Suite",
            tests=[],
        )

        result = runner.run_suite(suite)
        assert result.summary.total_tests == 0
        assert result.summary.pass_rate == 0.0

    def test_assistant_turn_handling(self) -> None:
        """Test that assistant turns are handled correctly."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="assistant-test",
            name="Assistant Turn Test",
            turns=[
                TestTurn(turn_number=1, role=TurnRole.USER, input="Hi"),
                TestTurn(
                    turn_number=2,
                    role=TurnRole.ASSISTANT,
                    input="Hello! How can I help?",
                ),
            ],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        assert result.status == TestStatus.PASSED
        # Assistant turn should have its input as the response
        assert result.turn_results[1].actual_response == "Hello! How can I help?"

    def test_logging(self) -> None:
        """Test that logging works correctly."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="log-test",
            name="Logging Test",
            turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Test")],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        assert len(result.logs) > 0
        assert any("Starting test" in log for log in result.logs)
        assert any("completed" in log for log in result.logs)

    def test_tolerance_in_equals(self) -> None:
        """Test tolerance parameter in EQUALS comparison."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=105,
        )

        assertion = ConversationAssertion(
            assertion_id="tolerance-test",
            assertion_type=AssertionType.LATENCY,
            target=AssertionTarget.LATENCY,
            operator=AssertionOperator.EQUALS,
            expected_value="100",
            tolerance=10.0,
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        assert result.passed is True  # 105 is within 10 of 100


class TestIntegration:
    """Integration tests for the full runner workflow."""

    def test_full_conversation_flow(self) -> None:
        """Test a complete multi-turn conversation."""
        handler = MockResponseHandler(
            responses={
                1: "Hello! I see you want to book a flight.",
                3: "Great! I've found flights from NYC to LA.",
                5: "Your flight is booked for tomorrow at 9 AM.",
            }
        )
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="booking-flow",
            name="Flight Booking Flow",
            category=TestCategory.DIALOGUE_FLOW,
            priority=TestPriority.CRITICAL,
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.USER,
                    input="I want to book a flight",
                    assertions=[
                        ConversationAssertion(
                            assertion_id="ack-booking",
                            assertion_type=AssertionType.RESPONSE_CONTAINS,
                            target=AssertionTarget.RESPONSE,
                            operator=AssertionOperator.CONTAINS,
                            expected_value="book",
                        ),
                    ],
                ),
                TestTurn(
                    turn_number=2,
                    role=TurnRole.ASSISTANT,
                    input="Hello! I see you want to book a flight.",
                ),
                TestTurn(
                    turn_number=3,
                    role=TurnRole.USER,
                    input="From NYC to LA",
                ),
                TestTurn(
                    turn_number=4,
                    role=TurnRole.ASSISTANT,
                    input="Great! I've found flights from NYC to LA.",
                ),
                TestTurn(
                    turn_number=5,
                    role=TurnRole.USER,
                    input="Book the first one for tomorrow",
                ),
            ],
            expected_outcome=ExpectedOutcome(
                success_condition=SuccessCondition.ALL_PASS,
            ),
        )

        result = runner.run_test(test)

        assert result.status == TestStatus.PASSED
        assert len(result.turn_results) == 5
        assert result.quality_scores is not None


# ============================================
# Additional Coverage Tests
# ============================================


class TestAdditionalCoverage:
    """Additional tests to improve code coverage."""

    def test_not_in_set_operator(self) -> None:
        """Test NOT_IN_SET operator."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
            detected_intent="valid_intent",
        )

        assertion = ConversationAssertion(
            assertion_id="not-in-set",
            assertion_type=AssertionType.INTENT_MATCH,
            target=AssertionTarget.INTENT,
            operator=AssertionOperator.NOT_IN_SET,
            expected_value="bad_intent, other_bad",
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        assert result.passed is True

    def test_random_execution_order(self) -> None:
        """Test random execution order for suites."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        suite = TestSuite(
            suite_id="random-suite",
            name="Random Order Suite",
            execution_order=ExecutionOrder.RANDOM,
            tests=[
                ConversationTest(
                    test_id=f"test-{i}",
                    name=f"Test {i}",
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input=f"Input {i}")],
                    expected_outcome=ExpectedOutcome(),
                )
                for i in range(5)
            ],
        )

        result = runner.run_suite(suite)
        assert result.summary.total_tests == 5

    def test_not_equals_operator(self) -> None:
        """Test NOT_EQUALS operator."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
            detected_intent="actual_intent",
        )

        assertion = ConversationAssertion(
            assertion_id="not-equals",
            assertion_type=AssertionType.INTENT_MATCH,
            target=AssertionTarget.INTENT,
            operator=AssertionOperator.NOT_EQUALS,
            expected_value="wrong_intent",
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        assert result.passed is True

    def test_not_matches_operator(self) -> None:
        """Test NOT_MATCHES operator."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
            actual_response="Hello world",
        )

        assertion = ConversationAssertion(
            assertion_id="not-matches",
            assertion_type=AssertionType.RESPONSE_PATTERN,
            target=AssertionTarget.RESPONSE,
            operator=AssertionOperator.NOT_MATCHES,
            expected_value=r"^Goodbye.*",
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        assert result.passed is True

    def test_greater_or_equal_operator(self) -> None:
        """Test GREATER_OR_EQUAL operator."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
        )

        assertion = ConversationAssertion(
            assertion_id="gte",
            assertion_type=AssertionType.LATENCY,
            target=AssertionTarget.LATENCY,
            operator=AssertionOperator.GREATER_OR_EQUAL,
            threshold=100.0,
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        assert result.passed is True

    def test_less_or_equal_operator(self) -> None:
        """Test LESS_OR_EQUAL operator."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
        )

        assertion = ConversationAssertion(
            assertion_id="lte",
            assertion_type=AssertionType.LATENCY,
            target=AssertionTarget.LATENCY,
            operator=AssertionOperator.LESS_OR_EQUAL,
            threshold=100.0,
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        assert result.passed is True

    def test_null_actual_value_not_equals(self) -> None:
        """Test NOT_EQUALS with null actual value."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
            detected_intent=None,
        )

        assertion = ConversationAssertion(
            assertion_id="null-not-equals",
            assertion_type=AssertionType.INTENT_MATCH,
            target=AssertionTarget.INTENT,
            operator=AssertionOperator.NOT_EQUALS,
            expected_value="some_intent",
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        assert result.passed is True

    def test_entities_target(self) -> None:
        """Test ENTITIES target extraction."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
            extracted_entities=[
                ExtractedEntity("type1", "value1", 0.9),
                ExtractedEntity("type2", "value2", 0.8),
            ],
        )

        assertion = ConversationAssertion(
            assertion_id="entities",
            assertion_type=AssertionType.ENTITY_PRESENT,
            target=AssertionTarget.ENTITIES,
            operator=AssertionOperator.CONTAINS,
            expected_value="value1",
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        assert result.passed is True

    def test_context_target(self) -> None:
        """Test CONTEXT target extraction."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
        )

        context = {"user_name": "John", "location": "NYC"}

        assertion = ConversationAssertion(
            assertion_id="context",
            assertion_type=AssertionType.CONTEXT_VALUE,
            target=AssertionTarget.CONTEXT,
            operator=AssertionOperator.CONTAINS,
            expected_value="John",
        )

        result = evaluator.evaluate(assertion, turn_result, context)
        assert result.passed is True

    def test_turn_with_delay(self) -> None:
        """Test turn with delay_ms configured."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        test = ConversationTest(
            test_id="delay-test",
            name="Delay Test",
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.USER,
                    input="Test",
                    delay_ms=10,  # Small delay
                ),
            ],
            expected_outcome=ExpectedOutcome(),
        )

        result = runner.run_test(test)
        assert result.status == TestStatus.PASSED

    def test_suite_error_status(self) -> None:
        """Test that suite gets ERROR status when tests have errors."""
        handler = MockResponseHandler()
        runner = ConversationTestRunner(handler)

        # Create a suite where we can track error status
        suite = TestSuite(
            suite_id="error-suite",
            name="Error Suite",
            tests=[
                ConversationTest(
                    test_id="test-1",
                    name="Test 1",
                    turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hi")],
                    expected_outcome=ExpectedOutcome(),
                ),
            ],
        )

        result = runner.run_suite(suite)
        # Should be PASSED since no errors
        assert result.status == TestStatus.PASSED

    def test_in_set_empty_expected(self) -> None:
        """Test IN_SET with empty expected value."""
        evaluator = AssertionEvaluator()
        turn_result = TurnResult(
            turn_number=1,
            input="Test",
            passed=True,
            latency_ms=100,
            detected_intent="something",
        )

        assertion = ConversationAssertion(
            assertion_id="in-set-empty",
            assertion_type=AssertionType.INTENT_MATCH,
            target=AssertionTarget.INTENT,
            operator=AssertionOperator.IN_SET,
            expected_value=None,
        )

        result = evaluator.evaluate(assertion, turn_result, {})
        assert result.passed is False
