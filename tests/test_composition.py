"""
Tests for Dynamic Composition Module

Issue #66 - Phase 3 Testing & Documentation
"""

import asyncio
import json
import pytest
from datetime import datetime, timezone

from src.lui_simulator.agent_types import (
    AgentIdentity,
    AgentCapability,
    CapabilityType,
    SchemaDefinition,
    SchemaProperty,
)
from src.agent_negotiation.composition import (
    # Enums
    InputSource,
    BackoffStrategy,
    ExecutionStatus,
    StepStatus,
    RecoveryStrategy,
    # Dataclasses
    InputBinding,
    DataFlowEdge,
    RetryPolicy,
    FailureMode,
    CompositionStep,
    CompositionPlan,
    StepResult,
    CompositionError,
    CompositionExecution,
    CircuitBreakerConfig,
    OrchestrationConfig,
    RecoveryPlan,
    # Classes
    CompositionPlanner,
    CompositionExecutor,
    CircuitBreaker,
)


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def agent_identity() -> AgentIdentity:
    """Create a test agent identity."""
    return AgentIdentity.create(
        name="test-agent",
        version="1.0.0",
        description="Test agent for composition",
        provider="test",
    )


@pytest.fixture
def simple_capability() -> AgentCapability:
    """Create a simple capability for testing."""
    return AgentCapability.create(
        name="text-process",
        description="Process text input",
        capability_type=CapabilityType.ACTION,
        input_schema=SchemaDefinition.object(
            properties=[
                SchemaProperty(
                    name="text",
                    schema=SchemaDefinition.string(description="Input text"),
                )
            ],
            required=["text"],
        ),
        output_schema=SchemaDefinition.string(description="Processed output"),
    )


@pytest.fixture
def query_capability() -> AgentCapability:
    """Create a query capability for testing."""
    return AgentCapability.create(
        name="data-query",
        description="Query data from storage",
        capability_type=CapabilityType.QUERY,
        input_schema=SchemaDefinition.object(
            properties=[
                SchemaProperty(
                    name="query",
                    schema=SchemaDefinition.string(description="Query string"),
                )
            ],
            required=["query"],
        ),
        output_schema=SchemaDefinition.string(description="Query results"),
    )


@pytest.fixture
def retry_policy() -> RetryPolicy:
    """Create a retry policy."""
    return RetryPolicy(
        max_retries=3,
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        retry_on=["timeout", "rate_limit"],
    )


@pytest.fixture
def circuit_breaker_config() -> CircuitBreakerConfig:
    """Create a circuit breaker configuration."""
    return CircuitBreakerConfig(
        failure_threshold=5,
        recovery_timeout_ms=30000,
        half_open_requests=2,
    )


@pytest.fixture
def orchestration_config(
    circuit_breaker_config: CircuitBreakerConfig,
) -> OrchestrationConfig:
    """Create an orchestration configuration."""
    return OrchestrationConfig(
        parallel_execution=False,
        max_concurrent_steps=3,
        global_timeout_ms=60000,
        circuit_breaker=circuit_breaker_config,
    )


@pytest.fixture
def composition_step(
    agent_identity: AgentIdentity,
    simple_capability: AgentCapability,
    retry_policy: RetryPolicy,
) -> CompositionStep:
    """Create a composition step."""
    return CompositionStep(
        step_id="step-1",
        agent=agent_identity,
        capability=simple_capability,
        input_bindings=[
            InputBinding(
                parameter_name="text",
                source=InputSource.USER_INPUT,
                source_reference="input_text",
            )
        ],
        output_name="output_1",
        timeout_ms=5000,
        retry_policy=retry_policy,
    )


# ============================================
# Test Enums
# ============================================


class TestInputSource:
    """Tests for InputSource enum."""

    def test_all_values(self):
        """Test all input source values exist."""
        assert InputSource.LITERAL.value == "literal"
        assert InputSource.PREVIOUS_STEP.value == "previous_step"
        assert InputSource.USER_INPUT.value == "user_input"
        assert InputSource.CONTEXT.value == "context"


class TestBackoffStrategy:
    """Tests for BackoffStrategy enum."""

    def test_all_values(self):
        """Test all backoff strategy values exist."""
        assert BackoffStrategy.FIXED.value == "fixed"
        assert BackoffStrategy.LINEAR.value == "linear"
        assert BackoffStrategy.EXPONENTIAL.value == "exponential"


class TestExecutionStatus:
    """Tests for ExecutionStatus enum."""

    def test_all_values(self):
        """Test all execution status values exist."""
        assert ExecutionStatus.PENDING.value == "pending"
        assert ExecutionStatus.RUNNING.value == "running"
        assert ExecutionStatus.COMPLETED.value == "completed"
        assert ExecutionStatus.FAILED.value == "failed"
        assert ExecutionStatus.CANCELLED.value == "cancelled"
        assert ExecutionStatus.TIMEOUT.value == "timeout"


class TestStepStatus:
    """Tests for StepStatus enum."""

    def test_all_values(self):
        """Test all step status values exist."""
        assert StepStatus.PENDING.value == "pending"
        assert StepStatus.RUNNING.value == "running"
        assert StepStatus.COMPLETED.value == "completed"
        assert StepStatus.FAILED.value == "failed"
        assert StepStatus.SKIPPED.value == "skipped"


class TestRecoveryStrategy:
    """Tests for RecoveryStrategy enum."""

    def test_all_values(self):
        """Test all recovery strategy values exist."""
        assert RecoveryStrategy.RETRY.value == "retry"
        assert RecoveryStrategy.ALTERNATIVE_AGENT.value == "alternative_agent"
        assert RecoveryStrategy.SKIP.value == "skip"
        assert RecoveryStrategy.ROLLBACK.value == "rollback"
        assert RecoveryStrategy.ABORT.value == "abort"


# ============================================
# Test Dataclasses
# ============================================


class TestInputBinding:
    """Tests for InputBinding dataclass."""

    def test_create_binding(self):
        """Test creating an input binding."""
        binding = InputBinding(
            parameter_name="query",
            source=InputSource.USER_INPUT,
            source_reference="user_query",
        )
        assert binding.parameter_name == "query"
        assert binding.source == InputSource.USER_INPUT
        assert binding.source_reference == "user_query"

    def test_to_dict(self):
        """Test InputBinding to_dict method."""
        binding = InputBinding(
            parameter_name="data",
            source=InputSource.PREVIOUS_STEP,
            source_reference="step-1",
        )
        result = binding.to_dict()
        assert result["parameter_name"] == "data"
        assert result["source"] == "previous_step"
        assert result["source_reference"] == "step-1"


class TestDataFlowEdge:
    """Tests for DataFlowEdge dataclass."""

    def test_create_edge(self):
        """Test creating a data flow edge."""
        edge = DataFlowEdge(
            from_step="step-1",
            to_step="step-2",
            data_path="$.output",
        )
        assert edge.from_step == "step-1"
        assert edge.to_step == "step-2"
        assert edge.data_path == "$.output"

    def test_to_dict(self):
        """Test DataFlowEdge to_dict method."""
        edge = DataFlowEdge(
            from_step="step-1",
            to_step="step-2",
            data_path="$.result",
        )
        result = edge.to_dict()
        assert result["from_step"] == "step-1"
        assert result["to_step"] == "step-2"
        assert result["data_path"] == "$.result"


class TestRetryPolicy:
    """Tests for RetryPolicy dataclass."""

    def test_create_policy(self):
        """Test creating a retry policy."""
        policy = RetryPolicy(
            max_retries=5,
            backoff_strategy=BackoffStrategy.LINEAR,
            retry_on=["timeout"],
        )
        assert policy.max_retries == 5
        assert policy.backoff_strategy == BackoffStrategy.LINEAR
        assert "timeout" in policy.retry_on

    def test_to_dict(self):
        """Test RetryPolicy to_dict method."""
        policy = RetryPolicy(
            max_retries=3,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            retry_on=["timeout", "error"],
        )
        result = policy.to_dict()
        assert result["max_retries"] == 3
        assert result["backoff_strategy"] == "exponential"
        assert len(result["retry_on"]) == 2


class TestFailureMode:
    """Tests for FailureMode dataclass."""

    def test_create_failure_mode(self):
        """Test creating a failure mode."""
        mode = FailureMode(
            step_id="step-1",
            failure_type="timeout",
            impact="Step does not complete",
            mitigation="Retry with backoff",
        )
        assert mode.step_id == "step-1"
        assert mode.failure_type == "timeout"
        assert mode.impact == "Step does not complete"
        assert mode.mitigation == "Retry with backoff"

    def test_to_dict(self):
        """Test FailureMode to_dict method."""
        mode = FailureMode(
            step_id="step-2",
            failure_type="agent_unavailable",
            impact="Cannot reach agent",
            mitigation="Try alternative agent",
        )
        result = mode.to_dict()
        assert result["step_id"] == "step-2"
        assert result["failure_type"] == "agent_unavailable"


class TestCompositionStep:
    """Tests for CompositionStep dataclass."""

    def test_create_step(
        self,
        agent_identity: AgentIdentity,
        simple_capability: AgentCapability,
    ):
        """Test creating a composition step."""
        step = CompositionStep(
            step_id="step-1",
            agent=agent_identity,
            capability=simple_capability,
            input_bindings=[],
            output_name="output_1",
            timeout_ms=5000,
        )
        assert step.step_id == "step-1"
        assert step.agent == agent_identity
        assert step.capability == simple_capability
        assert step.timeout_ms == 5000

    def test_step_with_retry_policy(
        self,
        agent_identity: AgentIdentity,
        simple_capability: AgentCapability,
        retry_policy: RetryPolicy,
    ):
        """Test step with retry policy."""
        step = CompositionStep(
            step_id="step-1",
            agent=agent_identity,
            capability=simple_capability,
            input_bindings=[],
            output_name="output_1",
            timeout_ms=5000,
            retry_policy=retry_policy,
        )
        assert step.retry_policy is not None
        assert step.retry_policy.max_retries == 3

    def test_to_dict(
        self,
        agent_identity: AgentIdentity,
        simple_capability: AgentCapability,
    ):
        """Test CompositionStep to_dict method."""
        step = CompositionStep(
            step_id="step-1",
            agent=agent_identity,
            capability=simple_capability,
            input_bindings=[
                InputBinding(
                    parameter_name="text",
                    source=InputSource.USER_INPUT,
                    source_reference="input",
                )
            ],
            output_name="output_1",
            timeout_ms=5000,
        )
        result = step.to_dict()
        assert result["step_id"] == "step-1"
        assert "agent" in result
        assert "capability" in result
        assert len(result["input_bindings"]) == 1


class TestCompositionPlan:
    """Tests for CompositionPlan dataclass."""

    def test_create_plan(
        self,
        composition_step: CompositionStep,
    ):
        """Test creating a composition plan."""
        plan = CompositionPlan(
            plan_id="plan-1",
            goal="Process and analyze text",
            steps=[composition_step],
            data_flow=[],
            estimated_latency_ms=5000,
        )
        assert plan.plan_id == "plan-1"
        assert plan.goal == "Process and analyze text"
        assert len(plan.steps) == 1

    def test_plan_with_data_flow(
        self,
        composition_step: CompositionStep,
    ):
        """Test plan with data flow edges."""
        plan = CompositionPlan(
            plan_id="plan-1",
            goal="Multi-step processing",
            steps=[composition_step],
            data_flow=[
                DataFlowEdge(
                    from_step="step-1",
                    to_step="step-2",
                    data_path="$.output",
                )
            ],
            estimated_latency_ms=10000,
        )
        assert len(plan.data_flow) == 1

    def test_to_dict(
        self,
        composition_step: CompositionStep,
    ):
        """Test CompositionPlan to_dict method."""
        plan = CompositionPlan(
            plan_id="plan-1",
            goal="Test goal",
            steps=[composition_step],
            data_flow=[],
            estimated_latency_ms=5000,
            failure_modes=[
                FailureMode(
                    step_id="step-1",
                    failure_type="timeout",
                    impact="Delayed response",
                    mitigation="Retry",
                )
            ],
        )
        result = plan.to_dict()
        assert result["plan_id"] == "plan-1"
        assert result["goal"] == "Test goal"
        assert len(result["failure_modes"]) == 1


class TestStepResult:
    """Tests for StepResult dataclass."""

    def test_create_successful_result(self):
        """Test creating a successful step result."""
        result = StepResult(
            step_id="step-1",
            status=StepStatus.COMPLETED,
            output='{"result": "success"}',
            latency_ms=150,
        )
        assert result.step_id == "step-1"
        assert result.status == StepStatus.COMPLETED
        assert result.output is not None
        assert result.latency_ms == 150

    def test_create_failed_result(self):
        """Test creating a failed step result."""
        result = StepResult(
            step_id="step-1",
            status=StepStatus.FAILED,
            error="Connection timeout",
            latency_ms=5000,
            retries=3,
        )
        assert result.status == StepStatus.FAILED
        assert result.error == "Connection timeout"
        assert result.retries == 3

    def test_to_dict(self):
        """Test StepResult to_dict method."""
        result = StepResult(
            step_id="step-1",
            status=StepStatus.COMPLETED,
            output='{"data": "test"}',
            latency_ms=100,
        )
        dict_result = result.to_dict()
        assert dict_result["step_id"] == "step-1"
        assert dict_result["status"] == "completed"


class TestCompositionError:
    """Tests for CompositionError dataclass."""

    def test_create_error(self):
        """Test creating a composition error."""
        error = CompositionError(
            step_id="step-1",
            error_type="timeout",
            message="Step timed out after 5000ms",
            recoverable=True,
            recovery_suggestion="Increase timeout or retry",
        )
        assert error.step_id == "step-1"
        assert error.error_type == "timeout"
        assert error.recoverable is True

    def test_to_dict(self):
        """Test CompositionError to_dict method."""
        error = CompositionError(
            step_id="step-2",
            error_type="exception",
            message="Unexpected error",
            recoverable=False,
        )
        result = error.to_dict()
        assert result["step_id"] == "step-2"
        assert result["recoverable"] is False


class TestCompositionExecution:
    """Tests for CompositionExecution dataclass."""

    def test_create_execution(self):
        """Test creating a composition execution."""
        execution = CompositionExecution(
            execution_id="exec-1",
            plan_id="plan-1",
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        assert execution.execution_id == "exec-1"
        assert execution.status == ExecutionStatus.RUNNING
        assert execution.completed_at is None

    def test_completed_execution(self):
        """Test a completed execution."""
        execution = CompositionExecution(
            execution_id="exec-1",
            plan_id="plan-1",
            status=ExecutionStatus.COMPLETED,
            started_at=datetime.now(timezone.utc).isoformat(),
            completed_at=datetime.now(timezone.utc).isoformat(),
            step_results=[
                StepResult(
                    step_id="step-1",
                    status=StepStatus.COMPLETED,
                    output='{"result": "done"}',
                    latency_ms=100,
                )
            ],
            final_output='{"result": "done"}',
        )
        assert execution.status == ExecutionStatus.COMPLETED
        assert execution.final_output is not None
        assert len(execution.step_results) == 1

    def test_to_dict(self):
        """Test CompositionExecution to_dict method."""
        execution = CompositionExecution(
            execution_id="exec-1",
            plan_id="plan-1",
            status=ExecutionStatus.COMPLETED,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        result = execution.to_dict()
        assert result["execution_id"] == "exec-1"
        assert result["status"] == "completed"


class TestOrchestrationConfig:
    """Tests for OrchestrationConfig dataclass."""

    def test_default_config(self):
        """Test default orchestration config."""
        config = OrchestrationConfig()
        assert config.parallel_execution is False
        assert config.max_concurrent_steps == 3
        assert config.global_timeout_ms == 60000
        assert config.circuit_breaker is None

    def test_custom_config(
        self,
        circuit_breaker_config: CircuitBreakerConfig,
    ):
        """Test custom orchestration config."""
        config = OrchestrationConfig(
            parallel_execution=True,
            max_concurrent_steps=5,
            global_timeout_ms=120000,
            circuit_breaker=circuit_breaker_config,
        )
        assert config.parallel_execution is True
        assert config.max_concurrent_steps == 5
        assert config.circuit_breaker is not None

    def test_to_dict(self):
        """Test OrchestrationConfig to_dict method."""
        config = OrchestrationConfig(
            parallel_execution=True,
            max_concurrent_steps=4,
            global_timeout_ms=30000,
        )
        result = config.to_dict()
        assert result["parallel_execution"] is True
        assert result["max_concurrent_steps"] == 4


class TestRecoveryPlan:
    """Tests for RecoveryPlan dataclass."""

    def test_create_recovery_plan(self):
        """Test creating a recovery plan."""
        plan = RecoveryPlan(
            strategy=RecoveryStrategy.RETRY,
            resume_from_step="step-2",
            explanation="Retrying from failed step",
        )
        assert plan.strategy == RecoveryStrategy.RETRY
        assert plan.resume_from_step == "step-2"

    def test_skip_strategy(self):
        """Test skip recovery strategy."""
        plan = RecoveryPlan(
            strategy=RecoveryStrategy.SKIP,
            skip_steps=["step-3", "step-4"],
            explanation="Skipping optional steps",
        )
        assert plan.strategy == RecoveryStrategy.SKIP
        assert len(plan.skip_steps) == 2

    def test_to_dict(self):
        """Test RecoveryPlan to_dict method."""
        plan = RecoveryPlan(
            strategy=RecoveryStrategy.ALTERNATIVE_AGENT,
            explanation="Using backup agent",
        )
        result = plan.to_dict()
        assert result["strategy"] == "alternative_agent"


# ============================================
# Test CompositionPlanner
# ============================================


class TestCompositionPlanner:
    """Tests for CompositionPlanner class."""

    def test_create_planner(self):
        """Test creating a composition planner."""
        planner = CompositionPlanner()
        assert planner.registry is None

    def test_create_planner_with_registry(self):
        """Test creating planner with registry."""
        mock_registry = {"agents": []}
        planner = CompositionPlanner(registry=mock_registry)
        assert planner.registry == mock_registry

    def test_plan_single_capability(
        self,
        simple_capability: AgentCapability,
    ):
        """Test planning with a single capability."""
        planner = CompositionPlanner()
        agent_capabilities = {
            "urn:agent:test:agent-1:1.0.0": [simple_capability],
        }
        plan = planner.plan(
            goal="Process text",
            required_capabilities=["action"],
            agent_capabilities=agent_capabilities,
        )
        assert plan is not None
        assert plan.goal == "Process text"
        assert len(plan.steps) == 1
        assert plan.steps[0].step_id == "step-1"

    def test_plan_multiple_capabilities(
        self,
        simple_capability: AgentCapability,
        query_capability: AgentCapability,
    ):
        """Test planning with multiple capabilities."""
        planner = CompositionPlanner()
        agent_capabilities = {
            "urn:agent:test:agent-1:1.0.0": [simple_capability],
            "urn:agent:test:agent-2:1.0.0": [query_capability],
        }
        plan = planner.plan(
            goal="Query and process",
            required_capabilities=["action", "query"],
            agent_capabilities=agent_capabilities,
        )
        assert len(plan.steps) == 2
        # Should have data flow edge from step-1 to step-2
        assert len(plan.data_flow) == 1
        assert plan.data_flow[0].from_step == "step-1"
        assert plan.data_flow[0].to_step == "step-2"

    def test_plan_missing_capability(self):
        """Test planning with missing capability raises error."""
        planner = CompositionPlanner()
        agent_capabilities = {}
        with pytest.raises(ValueError, match="No agent found"):
            planner.plan(
                goal="Process data",
                required_capabilities=["nonexistent"],
                agent_capabilities=agent_capabilities,
            )

    def test_plan_failure_modes(
        self,
        simple_capability: AgentCapability,
    ):
        """Test that plan includes failure mode analysis."""
        planner = CompositionPlanner()
        agent_capabilities = {
            "urn:agent:test:agent-1:1.0.0": [simple_capability],
        }
        plan = planner.plan(
            goal="Process text",
            required_capabilities=["action"],
            agent_capabilities=agent_capabilities,
        )
        # Should have failure modes for the step
        assert len(plan.failure_modes) > 0
        failure_types = {fm.failure_type for fm in plan.failure_modes}
        assert "timeout" in failure_types
        assert "agent_unavailable" in failure_types

    def test_plan_estimated_latency(
        self,
        simple_capability: AgentCapability,
        query_capability: AgentCapability,
    ):
        """Test that plan calculates estimated latency."""
        planner = CompositionPlanner()
        agent_capabilities = {
            "urn:agent:test:agent-1:1.0.0": [simple_capability],
            "urn:agent:test:agent-2:1.0.0": [query_capability],
        }
        plan = planner.plan(
            goal="Multi-step",
            required_capabilities=["action", "query"],
            agent_capabilities=agent_capabilities,
        )
        # Latency should be sum of step timeouts
        assert plan.estimated_latency_ms == 10000  # 2 x 5000ms default


# ============================================
# Test CompositionExecutor
# ============================================


class TestCompositionExecutor:
    """Tests for CompositionExecutor class."""

    def test_create_executor(self):
        """Test creating a composition executor."""
        executor = CompositionExecutor(agent_client=None)
        assert executor.agent_client is None
        assert executor.config is not None

    def test_create_executor_with_config(
        self,
        orchestration_config: OrchestrationConfig,
    ):
        """Test creating executor with custom config."""
        executor = CompositionExecutor(
            agent_client=None,
            config=orchestration_config,
        )
        assert executor.config == orchestration_config

    @pytest.mark.asyncio
    async def test_execute_simple_plan(
        self,
        composition_step: CompositionStep,
    ):
        """Test executing a simple plan."""
        executor = CompositionExecutor(agent_client=None)
        plan = CompositionPlan(
            plan_id="plan-1",
            goal="Test execution",
            steps=[composition_step],
            data_flow=[],
            estimated_latency_ms=5000,
        )
        execution = await executor.execute(
            plan,
            inputs={"input_text": "Hello world"},
        )
        assert execution is not None
        assert execution.plan_id == "plan-1"
        assert execution.status == ExecutionStatus.COMPLETED
        assert len(execution.step_results) == 1

    @pytest.mark.asyncio
    async def test_execute_with_mock_client(
        self,
        composition_step: CompositionStep,
    ):
        """Test execution with a mock agent client."""

        class MockClient:
            async def invoke(self, agent, capability, inputs):
                return {"result": f"processed: {inputs.get('text', '')}"}

        executor = CompositionExecutor(agent_client=MockClient())
        plan = CompositionPlan(
            plan_id="plan-1",
            goal="Test with client",
            steps=[composition_step],
            data_flow=[],
            estimated_latency_ms=5000,
        )
        execution = await executor.execute(
            plan,
            inputs={"input_text": "test"},
        )
        assert execution.status == ExecutionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_execute_parallel(
        self,
        agent_identity: AgentIdentity,
        simple_capability: AgentCapability,
        query_capability: AgentCapability,
    ):
        """Test parallel execution."""
        config = OrchestrationConfig(
            parallel_execution=True,
            max_concurrent_steps=3,
        )
        executor = CompositionExecutor(agent_client=None, config=config)

        # Create two independent steps (no data flow between them)
        step1 = CompositionStep(
            step_id="step-1",
            agent=agent_identity,
            capability=simple_capability,
            input_bindings=[
                InputBinding(
                    parameter_name="text",
                    source=InputSource.USER_INPUT,
                    source_reference="text_input",
                )
            ],
            output_name="output_1",
            timeout_ms=5000,
        )
        step2 = CompositionStep(
            step_id="step-2",
            agent=agent_identity,
            capability=query_capability,
            input_bindings=[
                InputBinding(
                    parameter_name="query",
                    source=InputSource.USER_INPUT,
                    source_reference="query_input",
                )
            ],
            output_name="output_2",
            timeout_ms=5000,
        )

        plan = CompositionPlan(
            plan_id="plan-1",
            goal="Parallel test",
            steps=[step1, step2],
            data_flow=[],  # No dependencies
            estimated_latency_ms=5000,
        )
        execution = await executor.execute(
            plan,
            inputs={"text_input": "hello", "query_input": "search"},
        )
        assert execution.status == ExecutionStatus.COMPLETED
        assert len(execution.step_results) == 2


# ============================================
# Test CircuitBreaker
# ============================================


class TestCircuitBreaker:
    """Tests for CircuitBreaker class."""

    def test_create_circuit_breaker(
        self,
        circuit_breaker_config: CircuitBreakerConfig,
    ):
        """Test creating a circuit breaker."""
        cb = CircuitBreaker(circuit_breaker_config)
        assert cb.config == circuit_breaker_config
        assert cb.state == "closed"
        assert cb.failure_count == 0

    def test_allow_request_closed(
        self,
        circuit_breaker_config: CircuitBreakerConfig,
    ):
        """Test that closed circuit allows requests."""
        cb = CircuitBreaker(circuit_breaker_config)
        assert cb.allow_request() is True

    def test_record_success(
        self,
        circuit_breaker_config: CircuitBreakerConfig,
    ):
        """Test recording success."""
        cb = CircuitBreaker(circuit_breaker_config)
        cb.record_success()
        assert cb.state == "closed"
        assert cb.failure_count == 0

    def test_record_failure_below_threshold(
        self,
        circuit_breaker_config: CircuitBreakerConfig,
    ):
        """Test recording failures below threshold."""
        cb = CircuitBreaker(circuit_breaker_config)
        for _ in range(4):  # Below threshold of 5
            cb.record_failure()
        assert cb.state == "closed"
        assert cb.failure_count == 4

    def test_record_failure_opens_circuit(
        self,
        circuit_breaker_config: CircuitBreakerConfig,
    ):
        """Test that enough failures open the circuit."""
        cb = CircuitBreaker(circuit_breaker_config)
        for _ in range(5):  # At threshold
            cb.record_failure()
        assert cb.state == "open"
        assert cb.allow_request() is False

    def test_half_open_transition(self):
        """Test transition to half-open state after recovery timeout."""
        # Use very short recovery timeout for testing
        config = CircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout_ms=1,  # 1ms for fast test
            half_open_requests=1,
        )
        cb = CircuitBreaker(config)
        cb.record_failure()
        assert cb.state == "open"

        # Wait a tiny bit for timeout
        import time
        time.sleep(0.01)

        # Should transition to half-open on next allow_request
        assert cb.allow_request() is True
        assert cb.state == "half-open"

    def test_half_open_success_closes(self):
        """Test that success in half-open state closes circuit."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout_ms=1,
            half_open_requests=1,
        )
        cb = CircuitBreaker(config)
        cb.record_failure()

        import time
        time.sleep(0.01)

        cb.allow_request()  # Transition to half-open
        cb.record_success()
        assert cb.state == "closed"

    def test_half_open_failure_opens(self):
        """Test that failure in half-open state reopens circuit."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout_ms=1,
            half_open_requests=2,
        )
        cb = CircuitBreaker(config)
        cb.record_failure()

        import time
        time.sleep(0.01)

        cb.allow_request()  # Transition to half-open
        cb.record_failure()  # Fail during half-open
        assert cb.state == "open"

    def test_reset(
        self,
        circuit_breaker_config: CircuitBreakerConfig,
    ):
        """Test resetting circuit breaker."""
        cb = CircuitBreaker(circuit_breaker_config)
        for _ in range(5):
            cb.record_failure()
        assert cb.state == "open"

        cb.reset()
        assert cb.state == "closed"
        assert cb.failure_count == 0
        assert cb.allow_request() is True

    def test_get_state(
        self,
        circuit_breaker_config: CircuitBreakerConfig,
    ):
        """Test getting circuit breaker state."""
        cb = CircuitBreaker(circuit_breaker_config)
        assert cb.get_state() == "closed"

        for _ in range(5):
            cb.record_failure()
        assert cb.get_state() == "open"


# ============================================
# Test Input Resolution
# ============================================


class TestInputResolution:
    """Tests for input binding resolution."""

    @pytest.mark.asyncio
    async def test_resolve_user_input(
        self,
        composition_step: CompositionStep,
    ):
        """Test resolving USER_INPUT bindings."""
        executor = CompositionExecutor(agent_client=None)
        plan = CompositionPlan(
            plan_id="plan-1",
            goal="Test input resolution",
            steps=[composition_step],
            data_flow=[],
            estimated_latency_ms=5000,
        )
        execution = await executor.execute(
            plan,
            inputs={"input_text": "test value"},
        )
        assert execution.status == ExecutionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_resolve_literal_input(
        self,
        agent_identity: AgentIdentity,
        simple_capability: AgentCapability,
    ):
        """Test resolving LITERAL bindings."""
        step = CompositionStep(
            step_id="step-1",
            agent=agent_identity,
            capability=simple_capability,
            input_bindings=[
                InputBinding(
                    parameter_name="text",
                    source=InputSource.LITERAL,
                    source_reference="hardcoded value",
                )
            ],
            output_name="output_1",
            timeout_ms=5000,
        )
        executor = CompositionExecutor(agent_client=None)
        plan = CompositionPlan(
            plan_id="plan-1",
            goal="Test literal",
            steps=[step],
            data_flow=[],
            estimated_latency_ms=5000,
        )
        execution = await executor.execute(plan, inputs={})
        assert execution.status == ExecutionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_resolve_previous_step_input(
        self,
        agent_identity: AgentIdentity,
        simple_capability: AgentCapability,
    ):
        """Test resolving PREVIOUS_STEP bindings."""
        step1 = CompositionStep(
            step_id="step-1",
            agent=agent_identity,
            capability=simple_capability,
            input_bindings=[
                InputBinding(
                    parameter_name="text",
                    source=InputSource.USER_INPUT,
                    source_reference="initial_input",
                )
            ],
            output_name="output_1",
            timeout_ms=5000,
        )
        step2 = CompositionStep(
            step_id="step-2",
            agent=agent_identity,
            capability=simple_capability,
            input_bindings=[
                InputBinding(
                    parameter_name="text",
                    source=InputSource.PREVIOUS_STEP,
                    source_reference="step-1",
                )
            ],
            output_name="output_2",
            timeout_ms=5000,
        )
        executor = CompositionExecutor(agent_client=None)
        plan = CompositionPlan(
            plan_id="plan-1",
            goal="Test chained",
            steps=[step1, step2],
            data_flow=[
                DataFlowEdge(
                    from_step="step-1",
                    to_step="step-2",
                    data_path="$.output",
                )
            ],
            estimated_latency_ms=10000,
        )
        execution = await executor.execute(
            plan,
            inputs={"initial_input": "first value"},
        )
        assert execution.status == ExecutionStatus.COMPLETED
        assert len(execution.step_results) == 2
