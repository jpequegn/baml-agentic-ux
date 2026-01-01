"""
Tests for Composition Execution Engine.

Issue #64 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.12)
"""

import pytest
import json
import time
from datetime import datetime
from typing import Any, Optional
from concurrent.futures import ThreadPoolExecutor

from src.agent_negotiation.composition_executor import (
    # Enums
    ExecutionStatus,
    StepStatus,
    RecoveryStrategy,
    CircuitBreakerState,
    BackoffStrategy,
    # Configuration types
    RetryConfig,
    CircuitBreakerConfig,
    OrchestrationConfig,
    # Step execution types
    StepError,
    StepMetrics,
    StepResult,
    # Composition execution types
    CompositionError,
    ExecutionMetrics,
    RecoveryAttempt,
    CompositionExecution,
    # Recovery types
    PlanChange,
    ModifiedPlan,
    CompensationAction,
    RecoveryPlan,
    # Request/response types
    ExecutionParameter,
    SecretReference,
    ExecutionInputs,
    ExecutionContext,
    ExecuteCompositionRequest,
    ExecuteCompositionResponse,
    # Circuit breaker types
    CircuitBreakerStatus,
    # Execution order types
    ResourceRequirements,
    ExecutionWave,
    ExecutionOrder,
    # Classes
    CircuitBreaker,
    CompositionExecutor,
)

from src.agent_negotiation.composition_planner import (
    CompositionPlan,
    CompositionStep,
    StepDependency,
    InputBinding,
    InputSource,
    StepExecutionType,
    DependencyType,
    PlanStatus,
    DataFlowEdge,
)


# ============================================
# Helper Functions
# ============================================


def create_test_plan(
    plan_id: str,
    steps: list[CompositionStep],
    dependencies: list[StepDependency] = None,
    entry_point: str = None,
    exit_points: list[str] = None,
    goal: str = "Test plan",
    estimated_latency_ms: int = 100,
) -> CompositionPlan:
    """Helper to create a CompositionPlan with correct fields."""
    if dependencies is None:
        dependencies = []
    if entry_point is None and steps:
        entry_point = steps[0].step_id
    if exit_points is None and steps:
        exit_points = [steps[-1].step_id]

    return CompositionPlan(
        plan_id=plan_id,
        version="1.0.0",
        goal=goal,
        status=PlanStatus.READY,
        steps=steps,
        data_flow=[],
        dependencies=dependencies,
        entry_point=entry_point or "",
        exit_points=exit_points or [],
        estimated_latency_ms=estimated_latency_ms,
    )


# ============================================
# Test Fixtures
# ============================================


@pytest.fixture
def basic_step():
    """Create a basic composition step."""
    return CompositionStep(
        step_id="step_1",
        name="Basic Step",
        agent_id="agent_1",
        agent_name="Test Agent",
        capability_name="process",
        input_bindings=[
            InputBinding(
                parameter_name="data",
                source=InputSource.USER_INPUT,
                source_reference="initial",
                required=True,
            )
        ],
        output_name="result",
        execution_type=StepExecutionType.SEQUENTIAL,
        timeout_ms=5000,
        estimated_latency_ms=100,
    )


@pytest.fixture
def multi_step_plan():
    """Create a multi-step composition plan."""
    steps = [
        CompositionStep(
            step_id="step_1",
            name="Step 1",
            agent_id="agent_1",
            agent_name="Agent 1",
            capability_name="extract",
            input_bindings=[
                InputBinding(
                    parameter_name="input",
                    source=InputSource.USER_INPUT,
                    source_reference="data",
                    required=True,
                )
            ],
            output_name="extracted",
            execution_type=StepExecutionType.SEQUENTIAL,
            timeout_ms=5000,
            estimated_latency_ms=50,
        ),
        CompositionStep(
            step_id="step_2",
            name="Step 2",
            agent_id="agent_2",
            agent_name="Agent 2",
            capability_name="transform",
            input_bindings=[
                InputBinding(
                    parameter_name="data",
                    source=InputSource.PREVIOUS_STEP,
                    source_reference="step_1",
                    required=True,
                )
            ],
            output_name="transformed",
            execution_type=StepExecutionType.SEQUENTIAL,
            timeout_ms=5000,
            estimated_latency_ms=50,
        ),
        CompositionStep(
            step_id="step_3",
            name="Step 3",
            agent_id="agent_3",
            agent_name="Agent 3",
            capability_name="output",
            input_bindings=[
                InputBinding(
                    parameter_name="data",
                    source=InputSource.PREVIOUS_STEP,
                    source_reference="step_2",
                    required=True,
                )
            ],
            output_name="final",
            execution_type=StepExecutionType.SEQUENTIAL,
            timeout_ms=5000,
            estimated_latency_ms=50,
        ),
    ]

    dependencies = [
        StepDependency(
            dependency_id="dep_1",
            from_step="step_1",
            to_step="step_2",
            dependency_type=DependencyType.DATA,
            required=True,
        ),
        StepDependency(
            dependency_id="dep_2",
            from_step="step_2",
            to_step="step_3",
            dependency_type=DependencyType.DATA,
            required=True,
        ),
    ]

    return CompositionPlan(
        plan_id="test-plan-001",
        version="1.0.0",
        goal="Test multi-step execution",
        status=PlanStatus.READY,
        steps=steps,
        data_flow=[],
        dependencies=dependencies,
        entry_point="step_1",
        exit_points=["step_3"],
        estimated_latency_ms=150,
    )


@pytest.fixture
def parallel_plan():
    """Create a plan with parallel execution opportunities."""
    steps = [
        CompositionStep(
            step_id="step_1",
            name="Step 1",
            agent_id="agent_1",
            agent_name="Agent 1",
            capability_name="start",
            input_bindings=[
                InputBinding(
                    parameter_name="input",
                    source=InputSource.USER_INPUT,
                    source_reference="data",
                    required=True,
                )
            ],
            output_name="result_1",
            execution_type=StepExecutionType.SEQUENTIAL,
            timeout_ms=5000,
            estimated_latency_ms=100,
        ),
        CompositionStep(
            step_id="step_2a",
            name="Step 2a",
            agent_id="agent_2",
            agent_name="Agent 2",
            capability_name="process_a",
            input_bindings=[
                InputBinding(
                    parameter_name="data",
                    source=InputSource.PREVIOUS_STEP,
                    source_reference="step_1",
                    required=True,
                )
            ],
            output_name="result_2a",
            execution_type=StepExecutionType.PARALLEL,
            timeout_ms=5000,
            estimated_latency_ms=100,
        ),
        CompositionStep(
            step_id="step_2b",
            name="Step 2b",
            agent_id="agent_3",
            agent_name="Agent 3",
            capability_name="process_b",
            input_bindings=[
                InputBinding(
                    parameter_name="data",
                    source=InputSource.PREVIOUS_STEP,
                    source_reference="step_1",
                    required=True,
                )
            ],
            output_name="result_2b",
            execution_type=StepExecutionType.PARALLEL,
            timeout_ms=5000,
            estimated_latency_ms=100,
        ),
        CompositionStep(
            step_id="step_3",
            name="Step 3",
            agent_id="agent_4",
            agent_name="Agent 4",
            capability_name="aggregate",
            input_bindings=[
                InputBinding(
                    parameter_name="a",
                    source=InputSource.PREVIOUS_STEP,
                    source_reference="step_2a",
                    required=True,
                ),
                InputBinding(
                    parameter_name="b",
                    source=InputSource.PREVIOUS_STEP,
                    source_reference="step_2b",
                    required=True,
                ),
            ],
            output_name="final",
            execution_type=StepExecutionType.SEQUENTIAL,
            timeout_ms=5000,
            estimated_latency_ms=100,
        ),
    ]

    dependencies = [
        StepDependency(dependency_id="dep_1", from_step="step_1", to_step="step_2a", dependency_type=DependencyType.DATA, required=True),
        StepDependency(dependency_id="dep_2", from_step="step_1", to_step="step_2b", dependency_type=DependencyType.DATA, required=True),
        StepDependency(dependency_id="dep_3", from_step="step_2a", to_step="step_3", dependency_type=DependencyType.DATA, required=True),
        StepDependency(dependency_id="dep_4", from_step="step_2b", to_step="step_3", dependency_type=DependencyType.DATA, required=True),
    ]

    return CompositionPlan(
        plan_id="parallel-plan-001",
        version="1.0.0",
        goal="Test parallel execution",
        status=PlanStatus.READY,
        steps=steps,
        data_flow=[],
        dependencies=dependencies,
        entry_point="step_1",
        exit_points=["step_3"],
        estimated_latency_ms=300,
    )


@pytest.fixture
def basic_inputs():
    """Create basic execution inputs."""
    return ExecutionInputs(
        initial_data=json.dumps({"message": "Hello, World!"}),
        parameters=[
            ExecutionParameter(name="mode", value="test", type="string"),
        ],
    )


@pytest.fixture
def basic_config():
    """Create basic orchestration config."""
    return OrchestrationConfig(
        parallel_execution=False,
        max_concurrent_steps=5,
        global_timeout_ms=60000,
        step_timeout_ms=5000,
    )


@pytest.fixture
def parallel_config():
    """Create config for parallel execution."""
    return OrchestrationConfig(
        parallel_execution=True,
        max_concurrent_steps=5,
        global_timeout_ms=60000,
        step_timeout_ms=5000,
    )


@pytest.fixture
def retry_config():
    """Create retry configuration."""
    return RetryConfig(
        max_retries=3,
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        initial_delay_ms=100,
        max_delay_ms=5000,
        backoff_multiplier=2.0,
        retryable_errors=["TIMEOUT", "TEMPORARY_FAILURE"],
    )


@pytest.fixture
def circuit_breaker_config():
    """Create circuit breaker configuration."""
    return CircuitBreakerConfig(
        failure_threshold=3,
        success_threshold=2,
        recovery_timeout_ms=5000,
        half_open_requests=2,
        monitored_errors=["TIMEOUT", "SERVICE_UNAVAILABLE"],
    )


def success_executor(step: CompositionStep, inputs: dict) -> tuple[bool, Optional[str], Optional[StepError]]:
    """Step executor that always succeeds."""
    output = {"step_id": step.step_id, "success": True, "inputs": list(inputs.keys())}
    return True, json.dumps(output), None


def failure_executor(step: CompositionStep, inputs: dict) -> tuple[bool, Optional[str], Optional[StepError]]:
    """Step executor that always fails."""
    return False, None, StepError(
        error_code="TEST_FAILURE",
        error_type="TEMPORARY_FAILURE",
        message="Simulated failure for testing",
        retry_possible=True,
    )


def intermittent_executor(fail_count: int = 2):
    """Create an executor that fails a certain number of times before succeeding."""
    attempts = {"count": 0}

    def executor(step: CompositionStep, inputs: dict) -> tuple[bool, Optional[str], Optional[StepError]]:
        attempts["count"] += 1
        if attempts["count"] <= fail_count:
            return False, None, StepError(
                error_code="INTERMITTENT",
                error_type="TEMPORARY_FAILURE",
                message=f"Attempt {attempts['count']} failed",
                retry_possible=True,
            )
        output = {"step_id": step.step_id, "attempt": attempts["count"]}
        return True, json.dumps(output), None

    return executor


# ============================================
# Enum Tests
# ============================================


class TestEnums:
    """Test execution status enums."""

    def test_execution_status_values(self):
        """Test ExecutionStatus enum values."""
        assert ExecutionStatus.PENDING.value == "pending"
        assert ExecutionStatus.RUNNING.value == "running"
        assert ExecutionStatus.COMPLETED.value == "completed"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.TIMEOUT.value == "timeout"
        assert ExecutionStatus.RECOVERING.value == "recovering"

    def test_step_status_values(self):
        """Test StepStatus enum values."""
        assert StepStatus.PENDING.value == "pending"
        assert StepStatus.QUEUED.value == "queued"
        assert StepStatus.RUNNING.value == "running"
        assert StepStatus.COMPLETED.value == "completed"
        assert StepStatus.FAILED.value == "failed"
        assert StepStatus.SKIPPED.value == "skipped"
        assert StepStatus.RETRYING.value == "retrying"

    def test_recovery_strategy_values(self):
        """Test RecoveryStrategy enum values."""
        assert RecoveryStrategy.RETRY.value == "retry"
        assert RecoveryStrategy.SKIP.value == "skip"
        assert RecoveryStrategy.ROLLBACK.value == "rollback"
        assert RecoveryStrategy.ABORT.value == "abort"
        assert RecoveryStrategy.ALTERNATIVE_AGENT.value == "alternative_agent"
        assert RecoveryStrategy.PARTIAL_COMPLETE.value == "partial_complete"

    def test_circuit_breaker_state_values(self):
        """Test CircuitBreakerState enum values."""
        assert CircuitBreakerState.CLOSED.value == "closed"
        assert CircuitBreakerState.OPEN.value == "open"
        assert CircuitBreakerState.HALF_OPEN.value == "half_open"

    def test_backoff_strategy_values(self):
        """Test BackoffStrategy enum values."""
        assert BackoffStrategy.FIXED.value == "fixed"
        assert BackoffStrategy.LINEAR.value == "linear"
        assert BackoffStrategy.EXPONENTIAL.value == "exponential"
        assert BackoffStrategy.JITTERED.value == "jittered"


# ============================================
# Configuration Tests
# ============================================


class TestConfigurations:
    """Test configuration dataclasses."""

    def test_retry_config_defaults(self):
        """Test RetryConfig default values."""
        config = RetryConfig()
        assert config.max_retries == 3
        assert config.backoff_strategy == BackoffStrategy.EXPONENTIAL
        assert config.initial_delay_ms == 1000
        assert config.max_delay_ms == 30000
        assert config.backoff_multiplier == 2.0
        assert "TIMEOUT" in config.retryable_errors

    def test_retry_config_custom(self, retry_config):
        """Test custom RetryConfig."""
        assert retry_config.max_retries == 3
        assert retry_config.initial_delay_ms == 100

    def test_circuit_breaker_config_defaults(self):
        """Test CircuitBreakerConfig default values."""
        config = CircuitBreakerConfig()
        assert config.failure_threshold == 5
        assert config.success_threshold == 3
        assert config.recovery_timeout_ms == 30000
        assert config.half_open_requests == 3

    def test_orchestration_config_defaults(self):
        """Test OrchestrationConfig default values."""
        config = OrchestrationConfig()
        assert config.parallel_execution is True
        assert config.max_concurrent_steps == 5
        assert config.global_timeout_ms == 300000
        assert config.step_timeout_ms == 60000
        assert config.collect_metrics is True
        assert config.preserve_partial_results is True


# ============================================
# Circuit Breaker Tests
# ============================================


class TestCircuitBreaker:
    """Test CircuitBreaker implementation."""

    def test_circuit_starts_closed(self, circuit_breaker_config):
        """Test that circuit breaker starts in closed state."""
        breaker = CircuitBreaker("agent_1", circuit_breaker_config)
        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.can_execute() is True

    def test_circuit_opens_after_failures(self, circuit_breaker_config):
        """Test circuit opens after reaching failure threshold."""
        breaker = CircuitBreaker("agent_1", circuit_breaker_config)

        # Record failures up to threshold
        for _ in range(circuit_breaker_config.failure_threshold):
            breaker.record_failure("TIMEOUT")

        assert breaker.state == CircuitBreakerState.OPEN
        assert breaker.can_execute() is False

    def test_circuit_ignores_non_monitored_errors(self, circuit_breaker_config):
        """Test circuit ignores errors not in monitored list."""
        breaker = CircuitBreaker("agent_1", circuit_breaker_config)

        # Record failures with non-monitored error
        for _ in range(10):
            breaker.record_failure("OTHER_ERROR")

        assert breaker.state == CircuitBreakerState.CLOSED
        assert breaker.can_execute() is True

    def test_circuit_resets_on_success(self, circuit_breaker_config):
        """Test failure count resets on success."""
        breaker = CircuitBreaker("agent_1", circuit_breaker_config)

        # Record some failures
        breaker.record_failure("TIMEOUT")
        breaker.record_failure("TIMEOUT")
        assert breaker.failure_count == 2

        # Success resets count
        breaker.record_success()
        assert breaker.failure_count == 0

    def test_circuit_half_open_transition(self, circuit_breaker_config):
        """Test transition to half-open state."""
        # Use very short timeout for testing
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            recovery_timeout_ms=10,  # 10ms
            half_open_requests=2,
        )
        breaker = CircuitBreaker("agent_1", config)

        # Open the circuit
        breaker.record_failure("TIMEOUT")
        breaker.record_failure("TIMEOUT")
        assert breaker.state == CircuitBreakerState.OPEN

        # Wait for recovery timeout
        time.sleep(0.015)

        # Should transition to half-open
        assert breaker.can_execute() is True
        assert breaker.state == CircuitBreakerState.HALF_OPEN

    def test_circuit_closes_after_successes_in_half_open(self, circuit_breaker_config):
        """Test circuit closes after successful requests in half-open."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            recovery_timeout_ms=10,
            half_open_requests=3,
        )
        breaker = CircuitBreaker("agent_1", config)

        # Open the circuit
        breaker.record_failure("TIMEOUT")
        breaker.record_failure("TIMEOUT")

        # Wait for recovery timeout
        time.sleep(0.015)
        breaker.can_execute()  # Trigger transition to half-open

        # Record successes
        breaker.record_success()
        breaker.record_success()

        assert breaker.state == CircuitBreakerState.CLOSED

    def test_circuit_reopens_on_failure_in_half_open(self, circuit_breaker_config):
        """Test circuit reopens on failure in half-open state."""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            recovery_timeout_ms=10,
            half_open_requests=3,
        )
        breaker = CircuitBreaker("agent_1", config)

        # Open the circuit
        breaker.record_failure("TIMEOUT")
        breaker.record_failure("TIMEOUT")

        # Wait for recovery timeout
        time.sleep(0.015)
        breaker.can_execute()  # Trigger transition to half-open

        # Record a failure
        breaker.record_failure("TIMEOUT")

        assert breaker.state == CircuitBreakerState.OPEN

    def test_get_status(self, circuit_breaker_config):
        """Test getting circuit breaker status."""
        breaker = CircuitBreaker("agent_1", circuit_breaker_config)
        breaker.record_failure("TIMEOUT")

        status = breaker.get_status()

        assert status.circuit_id == "circuit-agent_1"
        assert status.agent_id == "agent_1"
        assert status.state == CircuitBreakerState.CLOSED
        assert status.failure_count == 1


# ============================================
# CompositionExecutor Basic Tests
# ============================================


class TestCompositionExecutorBasics:
    """Test basic CompositionExecutor functionality."""

    def test_executor_initialization(self):
        """Test executor initializes correctly."""
        executor = CompositionExecutor()
        assert executor.step_executor is not None
        assert executor.default_config is not None

    def test_executor_with_custom_config(self, basic_config):
        """Test executor with custom config."""
        executor = CompositionExecutor(default_config=basic_config)
        assert executor.default_config == basic_config

    def test_executor_with_custom_step_executor(self):
        """Test executor with custom step executor."""
        executor = CompositionExecutor(step_executor=success_executor)
        assert executor.step_executor == success_executor


# ============================================
# Sequential Execution Tests
# ============================================


class TestSequentialExecution:
    """Test sequential step execution."""

    def test_single_step_execution(self, basic_step, basic_inputs, basic_config):
        """Test executing a single step."""
        plan = create_test_plan(
            plan_id="single-step",
            steps=[basic_step],
        )

        executor = CompositionExecutor(step_executor=success_executor)
        result = executor.execute(plan, basic_inputs, basic_config)

        assert result.status == ExecutionStatus.COMPLETED
        assert len(result.step_results) == 1
        assert result.step_results[0].status == StepStatus.COMPLETED

    def test_multi_step_sequential_execution(self, multi_step_plan, basic_inputs, basic_config):
        """Test executing multiple steps sequentially."""
        executor = CompositionExecutor(step_executor=success_executor)
        result = executor.execute(multi_step_plan, basic_inputs, basic_config)

        assert result.status == ExecutionStatus.COMPLETED
        assert len(result.step_results) == 3
        assert all(r.status == StepStatus.COMPLETED for r in result.step_results)
        assert result.execution_metrics.steps_completed == 3
        assert result.execution_metrics.steps_failed == 0

    def test_step_failure_stops_sequential_execution(self, multi_step_plan, basic_inputs, basic_config):
        """Test that a step failure stops sequential execution."""
        call_count = {"count": 0}

        def fail_on_second(step, inputs):
            call_count["count"] += 1
            if call_count["count"] == 2:
                return False, None, StepError(
                    error_code="FAIL",
                    error_type="PERMANENT",
                    message="Failed on second step",
                    retry_possible=False,
                )
            return success_executor(step, inputs)

        executor = CompositionExecutor(step_executor=fail_on_second)
        result = executor.execute(multi_step_plan, basic_inputs, basic_config)

        assert result.status == ExecutionStatus.FAILED
        assert result.execution_metrics.steps_completed == 1
        assert result.execution_metrics.steps_failed == 1
        assert result.error is not None
        assert result.error.failed_step_id == "step_2"


# ============================================
# Parallel Execution Tests
# ============================================


class TestParallelExecution:
    """Test parallel step execution."""

    def test_parallel_execution_enabled(self, parallel_plan, basic_inputs, parallel_config):
        """Test parallel execution is used when configured."""
        executor = CompositionExecutor(step_executor=success_executor)
        result = executor.execute(parallel_plan, basic_inputs, parallel_config)

        assert result.status == ExecutionStatus.COMPLETED
        assert len(result.step_results) == 4
        assert result.execution_metrics.steps_completed == 4

    def test_parallel_steps_run_concurrently(self, parallel_plan, basic_inputs, parallel_config):
        """Test that parallel steps actually run concurrently."""
        execution_times = []
        lock = __import__("threading").Lock()

        def timed_executor(step, inputs):
            start = time.time()
            time.sleep(0.01)  # 10ms
            end = time.time()
            with lock:
                execution_times.append((step.step_id, start, end))
            return success_executor(step, inputs)

        executor = CompositionExecutor(step_executor=timed_executor)
        result = executor.execute(parallel_plan, basic_inputs, parallel_config)

        assert result.status == ExecutionStatus.COMPLETED

        # Check that step_2a and step_2b overlapped in time
        step_2a = next((t for t in execution_times if t[0] == "step_2a"), None)
        step_2b = next((t for t in execution_times if t[0] == "step_2b"), None)

        if step_2a and step_2b:
            # They should overlap (one starts before the other ends)
            overlap = (step_2a[1] < step_2b[2]) and (step_2b[1] < step_2a[2])
            assert overlap, "Parallel steps should execute concurrently"

    def test_parallel_failure_allows_other_steps_to_complete(self, parallel_plan, basic_inputs):
        """Test that failure in parallel step allows others to complete with preserve_partial_results."""
        def fail_2a(step, inputs):
            if step.step_id == "step_2a":
                return False, None, StepError(
                    error_code="FAIL",
                    error_type="PERMANENT",
                    message="Step 2a failed",
                    retry_possible=False,
                )
            return success_executor(step, inputs)

        config = OrchestrationConfig(
            parallel_execution=True,
            max_concurrent_steps=5,
            preserve_partial_results=True,
        )

        executor = CompositionExecutor(step_executor=fail_2a)
        result = executor.execute(parallel_plan, basic_inputs, config)

        # Should have error but other steps may have completed
        assert result.error is not None


# ============================================
# Retry Tests
# ============================================


class TestRetryBehavior:
    """Test retry behavior."""

    def test_retry_on_failure(self, basic_step, basic_inputs):
        """Test that retries are attempted on failure."""
        attempts = {"count": 0}

        def counting_fail(step, inputs):
            attempts["count"] += 1
            return False, None, StepError(
                error_code="RETRY",
                error_type="TEMPORARY_FAILURE",
                message=f"Attempt {attempts['count']}",
                retry_possible=True,
            )

        plan = create_test_plan(
            plan_id="retry-test",
            steps=[basic_step],
        )

        config = OrchestrationConfig(
            parallel_execution=False,
            retry_config=RetryConfig(
                max_retries=3,
                backoff_strategy=BackoffStrategy.FIXED,
                initial_delay_ms=1,  # Very short for testing
                max_delay_ms=10,
            ),
        )

        executor = CompositionExecutor(step_executor=counting_fail)
        result = executor.execute(plan, basic_inputs, config)

        assert result.status == ExecutionStatus.FAILED
        assert attempts["count"] == 4  # 1 initial + 3 retries
        assert result.step_results[0].retries == 4

    def test_retry_succeeds_eventually(self, basic_step, basic_inputs):
        """Test that retry can succeed after initial failures."""
        plan = create_test_plan(
            plan_id="retry-success",
            steps=[basic_step],
        )

        config = OrchestrationConfig(
            parallel_execution=False,
            retry_config=RetryConfig(
                max_retries=3,
                backoff_strategy=BackoffStrategy.FIXED,
                initial_delay_ms=1,
                max_delay_ms=10,
            ),
        )

        executor = CompositionExecutor(step_executor=intermittent_executor(2))
        result = executor.execute(plan, basic_inputs, config)

        assert result.status == ExecutionStatus.COMPLETED
        assert result.step_results[0].retries == 2  # Failed twice, succeeded on third

    def test_backoff_strategies(self, retry_config):
        """Test different backoff strategies."""
        executor = CompositionExecutor()

        # Test fixed backoff
        fixed_config = RetryConfig(
            backoff_strategy=BackoffStrategy.FIXED,
            initial_delay_ms=100,
            max_delay_ms=1000,
        )
        delay = executor._calculate_backoff_delay(0, fixed_config)
        assert delay == 100
        delay = executor._calculate_backoff_delay(3, fixed_config)
        assert delay == 100

        # Test linear backoff
        linear_config = RetryConfig(
            backoff_strategy=BackoffStrategy.LINEAR,
            initial_delay_ms=100,
            max_delay_ms=1000,
        )
        delay = executor._calculate_backoff_delay(0, linear_config)
        assert delay == 100
        delay = executor._calculate_backoff_delay(2, linear_config)
        assert delay == 300

        # Test exponential backoff
        exp_config = RetryConfig(
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            initial_delay_ms=100,
            max_delay_ms=10000,
            backoff_multiplier=2.0,
        )
        delay = executor._calculate_backoff_delay(0, exp_config)
        assert delay == 100
        delay = executor._calculate_backoff_delay(3, exp_config)
        assert delay == 800  # 100 * 2^3

    def test_max_delay_cap(self, retry_config):
        """Test that delay is capped at max_delay_ms."""
        executor = CompositionExecutor()

        config = RetryConfig(
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            initial_delay_ms=1000,
            max_delay_ms=5000,
            backoff_multiplier=10.0,
        )

        delay = executor._calculate_backoff_delay(5, config)
        assert delay == 5000  # Capped at max


# ============================================
# Circuit Breaker Integration Tests
# ============================================


class TestCircuitBreakerIntegration:
    """Test circuit breaker integration with executor."""

    def test_circuit_breaker_blocks_execution(self, basic_step, basic_inputs):
        """Test circuit breaker blocks execution when open."""
        plan = create_test_plan(
            plan_id="cb-test",
            steps=[basic_step],
        )

        config = OrchestrationConfig(
            parallel_execution=False,
            circuit_breaker=CircuitBreakerConfig(
                failure_threshold=2,
                monitored_errors=["FAIL"],
            ),
        )

        def fail_with_monitored(step, inputs):
            return False, None, StepError(
                error_code="FAIL",
                error_type="FAIL",
                message="Monitored failure",
                retry_possible=False,
            )

        executor = CompositionExecutor(step_executor=fail_with_monitored)

        # First execution opens the circuit
        executor.execute(plan, basic_inputs, config)
        executor.execute(plan, basic_inputs, config)

        # Check circuit is open
        status = executor.get_circuit_breaker_status("agent_1")
        assert status is not None
        assert status.state == CircuitBreakerState.OPEN

        # Third execution should be blocked
        result = executor.execute(plan, basic_inputs, config)
        assert result.step_results[0].error is not None
        assert result.step_results[0].error.error_type == "CIRCUIT_BREAKER"

    def test_reset_circuit_breaker(self, basic_step, basic_inputs):
        """Test resetting a circuit breaker."""
        plan = create_test_plan(
            plan_id="cb-reset-test",
            steps=[basic_step],
        )

        config = OrchestrationConfig(
            parallel_execution=False,
            circuit_breaker=CircuitBreakerConfig(
                failure_threshold=2,
                monitored_errors=["FAIL"],
            ),
        )

        def fail_always(step, inputs):
            return False, None, StepError(
                error_code="FAIL",
                error_type="FAIL",
                message="Always fails",
                retry_possible=False,
            )

        executor = CompositionExecutor(step_executor=fail_always)

        # Open the circuit
        executor.execute(plan, basic_inputs, config)
        executor.execute(plan, basic_inputs, config)

        # Reset it
        reset_result = executor.reset_circuit_breaker("agent_1")
        assert reset_result is True

        status = executor.get_circuit_breaker_status("agent_1")
        assert status.state == CircuitBreakerState.CLOSED


# ============================================
# Recovery Tests
# ============================================


class TestRecoveryPlanning:
    """Test recovery planning functionality."""

    def test_recover_no_error(self, multi_step_plan, basic_inputs, basic_config):
        """Test recovery when there's no error."""
        executor = CompositionExecutor(step_executor=success_executor)
        result = executor.execute(multi_step_plan, basic_inputs, basic_config)

        recovery = executor.recover(result, multi_step_plan)

        assert recovery.strategy == RecoveryStrategy.ABORT
        assert "No recovery needed" in recovery.explanation

    def test_recover_suggests_retry(self, multi_step_plan, basic_inputs, basic_config):
        """Test recovery suggests retry for retryable errors."""
        call_count = {"count": 0}

        def fail_once(step, inputs):
            call_count["count"] += 1
            if call_count["count"] == 1:
                return False, None, StepError(
                    error_code="TEMP",
                    error_type="TEMPORARY",
                    message="Temporary failure",
                    retry_possible=True,
                )
            return success_executor(step, inputs)

        # Execute with no retries configured
        config = OrchestrationConfig(parallel_execution=False)
        executor = CompositionExecutor(step_executor=fail_once)
        result = executor.execute(multi_step_plan, basic_inputs, config)

        # Should be failed
        assert result.status == ExecutionStatus.FAILED

        # Recovery should suggest retry
        recovery = executor.recover(result, multi_step_plan)
        assert recovery.strategy == RecoveryStrategy.RETRY
        assert recovery.resume_from_step == "step_1"

    def test_recover_suggests_skip(self, basic_inputs, basic_config):
        """Test recovery suggests skip for non-critical steps."""
        # Create a plan where a non-exit step fails
        steps = [
            CompositionStep(
                step_id="step_1",
                name="Main Step",
                agent_id="agent_1",
                agent_name="Agent 1",
                capability_name="main",
                input_bindings=[],
                output_name="result",
                execution_type=StepExecutionType.SEQUENTIAL,
                timeout_ms=5000,
            ),
            CompositionStep(
                step_id="optional",
                name="Optional Step",
                agent_id="agent_2",
                agent_name="Agent 2",
                capability_name="optional",
                input_bindings=[],
                output_name="optional_result",
                execution_type=StepExecutionType.SEQUENTIAL,
                timeout_ms=5000,
            ),
        ]

        plan = create_test_plan(
            plan_id="skip-test",
            steps=steps,
            entry_point="step_1",
            exit_points=["step_1"],  # optional is not an exit point
        )

        # Create execution with error on optional step
        execution = CompositionExecution(
            execution_id="exec-1",
            plan_id="skip-test",
            plan_version="1.0.0",
            status=ExecutionStatus.FAILED,
            started_at=datetime.now().isoformat(),
            completed_at=None,
            step_results=[
                StepResult(
                    step_id="step_1",
                    step_name="Main Step",
                    status=StepStatus.COMPLETED,
                    started_at=datetime.now().isoformat(),
                    completed_at=datetime.now().isoformat(),
                    output=None,
                    output_type=None,
                    latency_ms=100,
                    retries=0,
                ),
                StepResult(
                    step_id="optional",
                    step_name="Optional Step",
                    status=StepStatus.FAILED,
                    started_at=datetime.now().isoformat(),
                    completed_at=datetime.now().isoformat(),
                    output=None,
                    output_type=None,
                    latency_ms=100,
                    retries=3,
                    error=StepError(
                        error_code="FAIL",
                        error_type="FAIL",
                        message="Failed",
                        retry_possible=True,
                    ),
                ),
            ],
            final_output=None,
            error=CompositionError(
                error_id="err-1",
                error_type="STEP_FAILED",
                message="Optional step failed",
                failed_step_id="optional",
                recoverable=True,
            ),
            execution_metrics=ExecutionMetrics(
                total_duration_ms=200,
                steps_completed=1,
                steps_failed=1,
                steps_skipped=0,
                total_retries=3,
                parallel_efficiency=1.0,
                circuit_breaker_trips=0,
            ),
        )

        executor = CompositionExecutor()
        recovery = executor.recover(execution, plan)

        assert recovery.strategy == RecoveryStrategy.SKIP
        assert "optional" in recovery.skip_steps

    def test_recover_alternative_agent(self, basic_inputs):
        """Test recovery suggests alternative agent."""
        step = CompositionStep(
            step_id="step_1",
            name="Test Step",
            agent_id="agent_1",
            agent_name="Agent 1",
            capability_name="process",
            input_bindings=[],
            output_name="result",
            execution_type=StepExecutionType.SEQUENTIAL,
            timeout_ms=5000,
        )

        plan = create_test_plan(
            plan_id="alt-agent-test",
            steps=[step],
        )

        # Create failed execution
        execution = CompositionExecution(
            execution_id="exec-1",
            plan_id="alt-agent-test",
            plan_version="1.0.0",
            status=ExecutionStatus.FAILED,
            started_at=datetime.now().isoformat(),
            completed_at=None,
            step_results=[
                StepResult(
                    step_id="step_1",
                    step_name="Test Step",
                    status=StepStatus.FAILED,
                    started_at=datetime.now().isoformat(),
                    completed_at=datetime.now().isoformat(),
                    output=None,
                    output_type=None,
                    latency_ms=100,
                    retries=3,
                    error=StepError(
                        error_code="FAIL",
                        error_type="FAIL",
                        message="Agent failed",
                        retry_possible=True,
                    ),
                ),
            ],
            final_output=None,
            error=CompositionError(
                error_id="err-1",
                error_type="STEP_FAILED",
                message="Step failed",
                failed_step_id="step_1",
                recoverable=True,
                suggested_recovery=RecoveryStrategy.ALTERNATIVE_AGENT,
            ),
            execution_metrics=ExecutionMetrics(
                total_duration_ms=100,
                steps_completed=0,
                steps_failed=1,
                steps_skipped=0,
                total_retries=3,
                parallel_efficiency=1.0,
                circuit_breaker_trips=0,
            ),
        )

        available_agents = [
            {
                "agent_id": "agent_2",
                "agent_name": "Agent 2",
                "capabilities": ["process"],
                "current_load": 0.5,
            }
        ]

        executor = CompositionExecutor()
        recovery = executor.recover(execution, plan, available_agents)

        assert recovery.strategy == RecoveryStrategy.ALTERNATIVE_AGENT
        assert recovery.modified_plan is not None
        assert len(recovery.modified_plan.changes) > 0


# ============================================
# Execution Order Tests
# ============================================


class TestExecutionOrder:
    """Test execution order planning."""

    def test_single_wave_for_sequential(self, multi_step_plan, basic_config):
        """Test that sequential execution creates individual waves."""
        executor = CompositionExecutor()
        order = executor._plan_execution_order(multi_step_plan, basic_config)

        # Each step should be in its own wave since parallel is disabled
        assert len(order.waves) == 3
        for wave in order.waves:
            assert len(wave.step_ids) == 1

    def test_parallel_waves(self, parallel_plan, parallel_config):
        """Test that parallel execution groups steps into waves."""
        executor = CompositionExecutor()
        order = executor._plan_execution_order(parallel_plan, parallel_config)

        # Should have 3 waves: step_1 -> (step_2a, step_2b) -> step_3
        assert len(order.waves) == 3

        # Second wave should have parallel steps
        wave_2 = order.waves[1]
        assert len(wave_2.step_ids) == 2
        assert "step_2a" in wave_2.step_ids
        assert "step_2b" in wave_2.step_ids

    def test_critical_path(self, parallel_plan, parallel_config):
        """Test critical path identification."""
        executor = CompositionExecutor()
        order = executor._plan_execution_order(parallel_plan, parallel_config)

        assert len(order.critical_path) > 0
        assert order.critical_path[0] == "step_1"
        assert order.critical_path[-1] == "step_3"

    def test_parallelism_factor(self, parallel_plan, parallel_config):
        """Test parallelism factor calculation."""
        executor = CompositionExecutor()
        order = executor._plan_execution_order(parallel_plan, parallel_config)

        # With parallelism, factor should be greater than 1
        assert order.parallelism_factor >= 1.0


# ============================================
# Metrics Tests
# ============================================


class TestExecutionMetrics:
    """Test execution metrics collection."""

    def test_metrics_collected(self, multi_step_plan, basic_inputs, basic_config):
        """Test that execution metrics are collected."""
        executor = CompositionExecutor(step_executor=success_executor)
        result = executor.execute(multi_step_plan, basic_inputs, basic_config)

        # Duration can be 0 if execution is very fast
        assert result.execution_metrics.total_duration_ms >= 0
        assert result.execution_metrics.steps_completed == 3
        assert result.execution_metrics.steps_failed == 0
        assert result.execution_metrics.steps_skipped == 0

    def test_step_metrics(self, basic_step, basic_inputs, basic_config):
        """Test step-level metrics."""
        plan = create_test_plan(
            plan_id="metrics-test",
            steps=[basic_step],
        )

        executor = CompositionExecutor(step_executor=success_executor)
        result = executor.execute(plan, basic_inputs, basic_config)

        step_result = result.step_results[0]
        assert step_result.latency_ms >= 0
        assert step_result.metrics is not None
        assert step_result.metrics.execution_time_ms >= 0

    def test_retry_metrics(self, basic_step, basic_inputs):
        """Test retry metrics are tracked."""
        plan = create_test_plan(
            plan_id="retry-metrics-test",
            steps=[basic_step],
        )

        config = OrchestrationConfig(
            parallel_execution=False,
            retry_config=RetryConfig(
                max_retries=2,
                backoff_strategy=BackoffStrategy.FIXED,
                initial_delay_ms=1,
                max_delay_ms=10,
            ),
        )

        # Use executor that fails twice then succeeds
        executor = CompositionExecutor(step_executor=intermittent_executor(2))
        result = executor.execute(plan, basic_inputs, config)

        assert result.execution_metrics.total_retries == 2


# ============================================
# Execution History Tests
# ============================================


class TestExecutionHistory:
    """Test execution history management."""

    def test_execution_stored_in_history(self, basic_step, basic_inputs, basic_config):
        """Test executions are stored in history."""
        plan = create_test_plan(
            plan_id="history-test",
            steps=[basic_step],
        )

        executor = CompositionExecutor(step_executor=success_executor)
        result = executor.execute(plan, basic_inputs, basic_config)

        # Should be able to retrieve by ID
        retrieved = executor.get_execution(result.execution_id)
        assert retrieved is not None
        assert retrieved.execution_id == result.execution_id

    def test_get_nonexistent_execution(self):
        """Test getting an execution that doesn't exist."""
        executor = CompositionExecutor()
        result = executor.get_execution("nonexistent-id")
        assert result is None


# ============================================
# Input Binding Tests
# ============================================


class TestInputBindings:
    """Test input binding resolution."""

    def test_user_input_binding(self, basic_inputs, basic_config):
        """Test binding from user input."""
        step = CompositionStep(
            step_id="step_1",
            name="Test Step",
            agent_id="agent_1",
            agent_name="Agent 1",
            capability_name="process",
            input_bindings=[
                InputBinding(
                    parameter_name="data",
                    source=InputSource.USER_INPUT,
                    source_reference="initial",
                    required=True,
                )
            ],
            output_name="result",
            execution_type=StepExecutionType.SEQUENTIAL,
            timeout_ms=5000,
        )

        received_inputs = {}

        def capture_inputs(step, inputs):
            received_inputs.update(inputs)
            return success_executor(step, inputs)

        plan = create_test_plan(
            plan_id="binding-test",
            steps=[step],
        )

        executor = CompositionExecutor(step_executor=capture_inputs)
        executor.execute(plan, basic_inputs, basic_config)

        assert "data" in received_inputs

    def test_context_binding(self, basic_config):
        """Test binding from context parameters."""
        step = CompositionStep(
            step_id="step_1",
            name="Test Step",
            agent_id="agent_1",
            agent_name="Agent 1",
            capability_name="process",
            input_bindings=[
                InputBinding(
                    parameter_name="mode",
                    source=InputSource.CONTEXT,
                    source_reference="mode",
                    required=True,
                )
            ],
            output_name="result",
            execution_type=StepExecutionType.SEQUENTIAL,
            timeout_ms=5000,
        )

        received_inputs = {}

        def capture_inputs(step, inputs):
            received_inputs.update(inputs)
            return success_executor(step, inputs)

        plan = create_test_plan(
            plan_id="context-binding-test",
            steps=[step],
        )

        inputs = ExecutionInputs(
            initial_data="{}",
            parameters=[
                ExecutionParameter(name="mode", value="test", type="string"),
            ],
        )

        executor = CompositionExecutor(step_executor=capture_inputs)
        executor.execute(plan, inputs, basic_config)

        assert "mode" in received_inputs
        assert received_inputs["mode"] == "test"

    def test_previous_step_binding(self, basic_inputs, basic_config):
        """Test binding from previous step output."""
        steps = [
            CompositionStep(
                step_id="step_1",
                name="Step 1",
                agent_id="agent_1",
                agent_name="Agent 1",
                capability_name="produce",
                input_bindings=[],
                output_name="result",
                execution_type=StepExecutionType.SEQUENTIAL,
                timeout_ms=5000,
            ),
            CompositionStep(
                step_id="step_2",
                name="Step 2",
                agent_id="agent_2",
                agent_name="Agent 2",
                capability_name="consume",
                input_bindings=[
                    InputBinding(
                        parameter_name="from_step_1",
                        source=InputSource.PREVIOUS_STEP,
                        source_reference="step_1",
                        required=True,
                    )
                ],
                output_name="final",
                execution_type=StepExecutionType.SEQUENTIAL,
                timeout_ms=5000,
            ),
        ]

        plan = create_test_plan(
            plan_id="step-binding-test",
            steps=steps,
            dependencies=[
                StepDependency(
                    dependency_id="dep_1",
                    from_step="step_1",
                    to_step="step_2",
                    dependency_type=DependencyType.DATA,
                    required=True,
                ),
            ],
        )

        step_2_inputs = {}

        def capture_step_2(step, inputs):
            if step.step_id == "step_2":
                step_2_inputs.update(inputs)
            return success_executor(step, inputs)

        executor = CompositionExecutor(step_executor=capture_step_2)
        executor.execute(plan, basic_inputs, basic_config)

        assert "from_step_1" in step_2_inputs


# ============================================
# Module Import Tests
# ============================================


class TestModuleExports:
    """Test that all types are properly exported from the module."""

    def test_imports_from_module(self):
        """Test imports from agent_negotiation module."""
        from src.agent_negotiation import (
            CompositionExecutionStatus,
            StepStatus,
            RecoveryStrategy,
            CircuitBreakerState,
            BackoffStrategy,
            RetryConfig,
            CircuitBreakerConfig,
            OrchestrationConfig,
            StepError,
            StepMetrics,
            StepResult,
            CompositionError,
            ExecutionMetrics,
            RecoveryAttempt,
            CompositionExecution,
            PlanChange,
            ModifiedPlan,
            CompensationAction,
            RecoveryPlan,
            ExecutionParameter,
            SecretReference,
            ExecutionInputs,
            CompositionExecutionContext,
            ExecuteCompositionRequest,
            ExecuteCompositionResponse,
            CircuitBreakerStatus,
            ResourceRequirements,
            ExecutionWave,
            ExecutionOrder,
            CircuitBreaker,
            CompositionExecutor,
        )

        # Just verify they're importable - instantiation tests are elsewhere
        assert CompositionExecutionStatus is not None
        assert CompositionExecutor is not None
