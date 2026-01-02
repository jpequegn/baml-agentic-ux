"""
Dynamic Composition Module

Enables runtime capability composition where agents can combine their
capabilities to fulfill complex requests through orchestration.

Issue #56 - Phase 3d: Dynamic Composition
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable
import asyncio
import json
import uuid

from src.lui_simulator.agent_types import (
    AgentCapability,
    AgentIdentity,
)


# ============================================
# Enums
# ============================================


class InputSource(Enum):
    """Source of input data for a composition step."""

    LITERAL = "literal"  # Hardcoded value
    PREVIOUS_STEP = "previous_step"  # Output from earlier step
    USER_INPUT = "user_input"  # From original request
    CONTEXT = "context"  # From session context


class BackoffStrategy(Enum):
    """Strategy for retry backoff timing."""

    FIXED = "fixed"  # Fixed delay between retries
    LINEAR = "linear"  # Linearly increasing delay
    EXPONENTIAL = "exponential"  # Exponentially increasing delay


class ExecutionStatus(Enum):
    """Overall status of a composition execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class StepStatus(Enum):
    """Status of an individual composition step."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class RecoveryStrategy(Enum):
    """Strategy for recovering from composition failures."""

    RETRY = "retry"  # Retry the failed step
    ALTERNATIVE_AGENT = "alternative_agent"  # Use different agent
    SKIP = "skip"  # Skip optional step
    ROLLBACK = "rollback"  # Rollback and retry different path
    ABORT = "abort"  # Abort the composition


# ============================================
# Dataclasses - Input and Data Flow
# ============================================


@dataclass
class InputBinding:
    """Binding of input parameters to their sources."""

    parameter_name: str
    source: InputSource
    source_reference: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "parameter_name": self.parameter_name,
            "source": self.source.value,
            "source_reference": self.source_reference,
        }


@dataclass
class DataFlowEdge:
    """Represents data flow between composition steps."""

    from_step: str
    to_step: str
    data_path: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "from_step": self.from_step,
            "to_step": self.to_step,
            "data_path": self.data_path,
        }


# ============================================
# Dataclasses - Retry and Failure Handling
# ============================================


@dataclass
class RetryPolicy:
    """Policy for retrying failed operations."""

    max_retries: int
    backoff_strategy: BackoffStrategy
    retry_on: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "max_retries": self.max_retries,
            "backoff_strategy": self.backoff_strategy.value,
            "retry_on": self.retry_on,
        }


@dataclass
class FailureMode:
    """Potential failure mode in composition plan."""

    step_id: str
    failure_type: str
    impact: str
    mitigation: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "step_id": self.step_id,
            "failure_type": self.failure_type,
            "impact": self.impact,
            "mitigation": self.mitigation,
        }


# ============================================
# Dataclasses - Composition Steps
# ============================================


@dataclass
class CompositionStep:
    """A single step in a composition plan."""

    step_id: str
    agent: AgentIdentity
    capability: AgentCapability
    input_bindings: list[InputBinding]
    output_name: str
    timeout_ms: int
    retry_policy: RetryPolicy | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "step_id": self.step_id,
            "agent": {
                "agent_id": self.agent.agent_id,
                "name": self.agent.name,
                "version": self.agent.version,
            },
            "capability": {
                "capability_id": self.capability.capability_id,
                "name": self.capability.name,
                "type": self.capability.capability_type.value,
            },
            "input_bindings": [b.to_dict() for b in self.input_bindings],
            "output_name": self.output_name,
            "timeout_ms": self.timeout_ms,
            "retry_policy": self.retry_policy.to_dict() if self.retry_policy else None,
        }


# ============================================
# Dataclasses - Composition Plan
# ============================================


@dataclass
class CompositionPlan:
    """Complete plan for composing capabilities across agents."""

    plan_id: str
    goal: str
    steps: list[CompositionStep]
    data_flow: list[DataFlowEdge]
    estimated_latency_ms: int
    failure_modes: list[FailureMode] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "plan_id": self.plan_id,
            "goal": self.goal,
            "steps": [s.to_dict() for s in self.steps],
            "data_flow": [d.to_dict() for d in self.data_flow],
            "estimated_latency_ms": self.estimated_latency_ms,
            "failure_modes": [f.to_dict() for f in self.failure_modes],
        }


# ============================================
# Dataclasses - Execution Results
# ============================================


@dataclass
class StepResult:
    """Result of executing a single composition step."""

    step_id: str
    status: StepStatus
    output: str | None = None
    latency_ms: int = 0
    error: str | None = None
    retries: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "step_id": self.step_id,
            "status": self.status.value,
            "output": self.output,
            "latency_ms": self.latency_ms,
            "error": self.error,
            "retries": self.retries,
        }


@dataclass
class CompositionError:
    """Error that occurred during composition execution."""

    step_id: str
    error_type: str
    message: str
    recoverable: bool
    recovery_suggestion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "step_id": self.step_id,
            "error_type": self.error_type,
            "message": self.message,
            "recoverable": self.recoverable,
            "recovery_suggestion": self.recovery_suggestion,
        }


@dataclass
class CompositionExecution:
    """Complete execution state of a composition plan."""

    execution_id: str
    plan_id: str
    status: ExecutionStatus
    started_at: str
    completed_at: str | None = None
    step_results: list[StepResult] = field(default_factory=list)
    final_output: str | None = None
    error: CompositionError | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "execution_id": self.execution_id,
            "plan_id": self.plan_id,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "step_results": [r.to_dict() for r in self.step_results],
            "final_output": self.final_output,
            "error": self.error.to_dict() if self.error else None,
        }


# ============================================
# Dataclasses - Orchestration Configuration
# ============================================


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern."""

    failure_threshold: int
    recovery_timeout_ms: int
    half_open_requests: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "failure_threshold": self.failure_threshold,
            "recovery_timeout_ms": self.recovery_timeout_ms,
            "half_open_requests": self.half_open_requests,
        }


@dataclass
class OrchestrationConfig:
    """Configuration for composition orchestration."""

    parallel_execution: bool = False
    max_concurrent_steps: int = 3
    global_timeout_ms: int = 60000
    circuit_breaker: CircuitBreakerConfig | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "parallel_execution": self.parallel_execution,
            "max_concurrent_steps": self.max_concurrent_steps,
            "global_timeout_ms": self.global_timeout_ms,
            "circuit_breaker": self.circuit_breaker.to_dict() if self.circuit_breaker else None,
        }


# ============================================
# Dataclasses - Recovery Planning
# ============================================


@dataclass
class RecoveryPlan:
    """Plan for recovering from composition failure."""

    strategy: RecoveryStrategy
    modified_plan: CompositionPlan | None = None
    resume_from_step: str | None = None
    skip_steps: list[str] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "strategy": self.strategy.value,
            "modified_plan": self.modified_plan.to_dict() if self.modified_plan else None,
            "resume_from_step": self.resume_from_step,
            "skip_steps": self.skip_steps,
            "explanation": self.explanation,
        }


# ============================================
# CompositionPlanner Class
# ============================================


class CompositionPlanner:
    """
    Plans capability compositions across multiple agents.

    Creates execution plans that sequence agent capabilities,
    establish data flow, and identify potential failure modes.
    """

    def __init__(self, registry: Any = None):
        """
        Initialize the composition planner.

        Args:
            registry: Capability registry for discovering agents
        """
        self.registry = registry

    def plan(
        self,
        goal: str,
        required_capabilities: list[str],
        agent_capabilities: dict[str, list[AgentCapability]],
    ) -> CompositionPlan:
        """
        Create a composition plan to achieve a goal.

        Args:
            goal: Description of what to accomplish
            required_capabilities: List of capability types needed
            agent_capabilities: Map of agent_id to their capabilities

        Returns:
            CompositionPlan with sequenced steps
        """
        steps: list[CompositionStep] = []
        data_flow: list[DataFlowEdge] = []

        # Create steps for each required capability
        for i, cap_type in enumerate(required_capabilities):
            # Find agent with this capability
            agent_id, capability = self._find_capability(cap_type, agent_capabilities)

            if not agent_id or not capability:
                raise ValueError(f"No agent found for capability: {cap_type}")

            # Create agent identity (simplified)
            agent = AgentIdentity(
                agent_id=agent_id,
                name=agent_id.split(":")[-2] if ":" in agent_id else agent_id,
                version="1.0.0",
                description=f"Agent providing {cap_type}",
            )

            step = CompositionStep(
                step_id=f"step-{i+1}",
                agent=agent,
                capability=capability,
                input_bindings=self._create_bindings(i, capability),
                output_name=f"output_{i+1}",
                timeout_ms=5000,
                retry_policy=RetryPolicy(
                    max_retries=3,
                    backoff_strategy=BackoffStrategy.EXPONENTIAL,
                    retry_on=["timeout", "rate_limit"],
                ),
            )
            steps.append(step)

            # Create data flow edge to next step
            if i > 0:
                data_flow.append(
                    DataFlowEdge(
                        from_step=f"step-{i}",
                        to_step=f"step-{i+1}",
                        data_path="$.output",
                    )
                )

        return CompositionPlan(
            plan_id=str(uuid.uuid4()),
            goal=goal,
            steps=steps,
            data_flow=data_flow,
            estimated_latency_ms=sum(s.timeout_ms for s in steps),
            failure_modes=self._analyze_failure_modes(steps),
        )

    def _create_bindings(
        self, step_index: int, capability: AgentCapability
    ) -> list[InputBinding]:
        """
        Create input bindings for a step based on schema.

        Args:
            step_index: Index of the step (0-based)
            capability: Capability being invoked

        Returns:
            List of input bindings
        """
        bindings: list[InputBinding] = []

        # Get properties from input schema
        properties = capability.input_schema.properties or []

        for prop in properties:
            if step_index == 0:
                # First step gets from user input
                bindings.append(
                    InputBinding(
                        parameter_name=prop.name,
                        source=InputSource.USER_INPUT,
                        source_reference=prop.name,
                    )
                )
            else:
                # Subsequent steps get from previous step
                bindings.append(
                    InputBinding(
                        parameter_name=prop.name,
                        source=InputSource.PREVIOUS_STEP,
                        source_reference=f"step-{step_index}",
                    )
                )

        return bindings

    def _analyze_failure_modes(
        self, steps: list[CompositionStep]
    ) -> list[FailureMode]:
        """
        Identify potential failure modes in the plan.

        Args:
            steps: List of composition steps

        Returns:
            List of potential failure modes
        """
        modes: list[FailureMode] = []

        for step in steps:
            # Timeout failure
            modes.append(
                FailureMode(
                    step_id=step.step_id,
                    failure_type="timeout",
                    impact="Step does not complete in time",
                    mitigation="Retry with backoff",
                )
            )

            # Agent unavailable
            modes.append(
                FailureMode(
                    step_id=step.step_id,
                    failure_type="agent_unavailable",
                    impact="Cannot reach agent endpoint",
                    mitigation="Try alternative agent or circuit breaker",
                )
            )

            # Schema mismatch
            modes.append(
                FailureMode(
                    step_id=step.step_id,
                    failure_type="schema_mismatch",
                    impact="Input/output schema incompatibility",
                    mitigation="Apply schema transformation",
                )
            )

        return modes

    def _find_capability(
        self,
        capability_type: str,
        agent_capabilities: dict[str, list[AgentCapability]],
    ) -> tuple[str | None, AgentCapability | None]:
        """
        Find an agent that provides the required capability.

        Args:
            capability_type: Type of capability needed
            agent_capabilities: Map of agent_id to capabilities

        Returns:
            Tuple of (agent_id, capability) or (None, None)
        """
        for agent_id, capabilities in agent_capabilities.items():
            for cap in capabilities:
                if cap.capability_type.value == capability_type:
                    return agent_id, cap
        return None, None


# ============================================
# CompositionExecutor Class
# ============================================


class CompositionExecutor:
    """
    Executes composition plans with orchestration and error handling.

    Supports sequential and parallel execution modes with circuit breakers,
    retry policies, and comprehensive error recovery.
    """

    def __init__(
        self,
        agent_client: Any,
        config: OrchestrationConfig | None = None,
    ):
        """
        Initialize the composition executor.

        Args:
            agent_client: Client for invoking agent capabilities
            config: Orchestration configuration
        """
        self.agent_client = agent_client
        self.config = config or OrchestrationConfig()
        self._circuit_breakers: dict[str, "CircuitBreaker"] = {}

    async def execute(
        self, plan: CompositionPlan, inputs: dict[str, Any]
    ) -> CompositionExecution:
        """
        Execute a composition plan.

        Args:
            plan: Composition plan to execute
            inputs: User input data

        Returns:
            CompositionExecution with results
        """
        execution = CompositionExecution(
            execution_id=str(uuid.uuid4()),
            plan_id=plan.plan_id,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now(timezone.utc).isoformat(),
        )

        context: dict[str, Any] = {"inputs": inputs, "outputs": {}}

        try:
            if self.config.parallel_execution:
                await self._execute_parallel(plan, context, execution)
            else:
                await self._execute_sequential(plan, context, execution)

            execution.status = ExecutionStatus.COMPLETED
            execution.final_output = json.dumps(context["outputs"])

        except asyncio.TimeoutError:
            execution.status = ExecutionStatus.TIMEOUT
            execution.error = CompositionError(
                step_id="global",
                error_type="timeout",
                message=f"Exceeded global timeout of {self.config.global_timeout_ms}ms",
                recoverable=True,
                recovery_suggestion="Increase timeout or optimize plan",
            )
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = CompositionError(
                step_id="unknown",
                error_type="exception",
                message=str(e),
                recoverable=False,
                recovery_suggestion="Review error and modify plan",
            )

        execution.completed_at = datetime.now(timezone.utc).isoformat()
        return execution

    async def _execute_sequential(
        self,
        plan: CompositionPlan,
        context: dict[str, Any],
        execution: CompositionExecution,
    ) -> None:
        """
        Execute steps sequentially.

        Args:
            plan: Composition plan
            context: Execution context with inputs/outputs
            execution: Execution state to update
        """
        for step in plan.steps:
            result = await self._execute_step(step, context)
            execution.step_results.append(result)

            if result.status == StepStatus.FAILED:
                raise Exception(f"Step {step.step_id} failed: {result.error}")

            if result.output:
                context["outputs"][step.output_name] = json.loads(result.output)

    async def _execute_parallel(
        self,
        plan: CompositionPlan,
        context: dict[str, Any],
        execution: CompositionExecution,
    ) -> None:
        """
        Execute independent steps in parallel.

        Args:
            plan: Composition plan
            context: Execution context with inputs/outputs
            execution: Execution state to update
        """
        # Build dependency graph
        dependencies = self._build_dependency_graph(plan)

        # Group steps by level (no dependencies within level)
        levels = self._topological_sort(plan.steps, dependencies)

        for level in levels:
            # Execute level in parallel
            semaphore = asyncio.Semaphore(self.config.max_concurrent_steps)

            async def limited_task(step: CompositionStep) -> StepResult:
                async with semaphore:
                    return await self._execute_step(step, context)

            results = await asyncio.gather(*[limited_task(step) for step in level])

            for step, result in zip(level, results):
                execution.step_results.append(result)
                if result.status == StepStatus.COMPLETED and result.output:
                    context["outputs"][step.output_name] = json.loads(result.output)
                elif result.status == StepStatus.FAILED:
                    raise Exception(f"Step {step.step_id} failed: {result.error}")

    async def _execute_step(
        self, step: CompositionStep, context: dict[str, Any]
    ) -> StepResult:
        """
        Execute a single step with retry logic.

        Args:
            step: Composition step to execute
            context: Execution context

        Returns:
            StepResult with execution outcome
        """
        start_time = datetime.now(timezone.utc)
        retries = 0

        while True:
            try:
                # Resolve inputs
                inputs = self._resolve_inputs(step.input_bindings, context)

                # Check circuit breaker
                agent_id = step.agent.agent_id
                if agent_id in self._circuit_breakers:
                    cb = self._circuit_breakers[agent_id]
                    if not cb.allow_request():
                        raise Exception(f"Circuit breaker open for {agent_id}")

                # Call agent capability
                output = await asyncio.wait_for(
                    self._invoke_capability(step, inputs),
                    timeout=step.timeout_ms / 1000,
                )

                # Record success
                if agent_id in self._circuit_breakers:
                    self._circuit_breakers[agent_id].record_success()

                latency = int(
                    (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                )

                return StepResult(
                    step_id=step.step_id,
                    status=StepStatus.COMPLETED,
                    output=json.dumps(output),
                    latency_ms=latency,
                    retries=retries,
                )

            except Exception as e:
                # Record failure
                agent_id = step.agent.agent_id
                if agent_id in self._circuit_breakers:
                    self._circuit_breakers[agent_id].record_failure()

                retries += 1

                # Check if we should retry
                if step.retry_policy and retries <= step.retry_policy.max_retries:
                    await self._backoff(retries, step.retry_policy.backoff_strategy)
                    continue

                # No more retries
                latency = int(
                    (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                )

                return StepResult(
                    step_id=step.step_id,
                    status=StepStatus.FAILED,
                    error=str(e),
                    latency_ms=latency,
                    retries=retries,
                )

    def _resolve_inputs(
        self, bindings: list[InputBinding], context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Resolve input bindings to actual values.

        Args:
            bindings: Input bindings to resolve
            context: Execution context

        Returns:
            Dictionary of resolved input values
        """
        inputs: dict[str, Any] = {}

        for binding in bindings:
            if binding.source == InputSource.LITERAL:
                inputs[binding.parameter_name] = binding.source_reference
            elif binding.source == InputSource.USER_INPUT:
                value = context["inputs"].get(binding.source_reference)
                if value is not None:
                    inputs[binding.parameter_name] = value
            elif binding.source == InputSource.PREVIOUS_STEP:
                # Extract step number from reference (e.g., "step-1" -> 1)
                step_num = binding.source_reference.split("-")[-1]
                output_key = f"output_{step_num}"
                step_output = context["outputs"].get(output_key)
                if step_output is not None:
                    inputs[binding.parameter_name] = step_output
            elif binding.source == InputSource.CONTEXT:
                value = context.get(binding.source_reference)
                if value is not None:
                    inputs[binding.parameter_name] = value

        return inputs

    async def _invoke_capability(
        self, step: CompositionStep, inputs: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Invoke agent capability (to be implemented by agent client).

        Args:
            step: Composition step
            inputs: Resolved input values

        Returns:
            Output from capability invocation
        """
        # This would call the actual agent client
        # For now, return a mock response
        if self.agent_client and hasattr(self.agent_client, "invoke"):
            return await self.agent_client.invoke(
                step.agent, step.capability, inputs
            )
        else:
            # Mock response for testing
            return {"result": f"Mock output from {step.step_id}"}

    async def _backoff(self, retry: int, strategy: BackoffStrategy) -> None:
        """
        Wait based on backoff strategy.

        Args:
            retry: Current retry attempt number
            strategy: Backoff strategy to use
        """
        if strategy == BackoffStrategy.FIXED:
            await asyncio.sleep(1.0)
        elif strategy == BackoffStrategy.LINEAR:
            await asyncio.sleep(retry * 1.0)
        elif strategy == BackoffStrategy.EXPONENTIAL:
            await asyncio.sleep(2**retry * 0.1)

    def _build_dependency_graph(
        self, plan: CompositionPlan
    ) -> dict[str, list[str]]:
        """
        Build dependency graph from data flow edges.

        Args:
            plan: Composition plan

        Returns:
            Dictionary mapping step_id to list of dependent step_ids
        """
        dependencies: dict[str, list[str]] = {step.step_id: [] for step in plan.steps}

        for edge in plan.data_flow:
            if edge.to_step in dependencies:
                dependencies[edge.to_step].append(edge.from_step)

        return dependencies

    def _topological_sort(
        self,
        steps: list[CompositionStep],
        dependencies: dict[str, list[str]],
    ) -> list[list[CompositionStep]]:
        """
        Group steps into levels for parallel execution.

        Args:
            steps: List of composition steps
            dependencies: Dependency graph

        Returns:
            List of levels, each containing independent steps
        """
        step_map = {step.step_id: step for step in steps}
        in_degree = {step_id: len(deps) for step_id, deps in dependencies.items()}
        levels: list[list[CompositionStep]] = []

        while in_degree:
            # Find steps with no dependencies
            current_level = [
                step_map[step_id] for step_id, degree in in_degree.items() if degree == 0
            ]

            if not current_level:
                # Circular dependency or error
                break

            levels.append(current_level)

            # Remove current level and update dependencies
            for step in current_level:
                del in_degree[step.step_id]

                # Update dependent steps
                for step_id in dependencies:
                    if step.step_id in dependencies[step_id]:
                        in_degree[step_id] = max(0, in_degree[step_id] - 1)

        return levels


# ============================================
# CircuitBreaker Class
# ============================================


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.

    Implements the circuit breaker pattern with closed, open, and
    half-open states to prevent repeated calls to failing agents.
    """

    def __init__(self, config: CircuitBreakerConfig):
        """
        Initialize circuit breaker.

        Args:
            config: Circuit breaker configuration
        """
        self.config = config
        self.failure_count = 0
        self.last_failure_time: datetime | None = None
        self.state = "closed"  # closed, open, half-open
        self.half_open_attempts = 0

    def allow_request(self) -> bool:
        """
        Check if a request should be allowed through.

        Returns:
            True if request is allowed, False if circuit is open
        """
        if self.state == "closed":
            return True

        if self.state == "open":
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed_ms = (
                    datetime.now(timezone.utc) - self.last_failure_time
                ).total_seconds() * 1000
                if elapsed_ms > self.config.recovery_timeout_ms:
                    self.state = "half-open"
                    self.half_open_attempts = 1  # Count this first request
                    return True
            return False

        # Half-open state: allow limited requests
        if self.half_open_attempts < self.config.half_open_requests:
            self.half_open_attempts += 1
            return True
        return False

    def record_success(self) -> None:
        """Record a successful request."""
        if self.state == "half-open":
            # Enough successes, close the circuit
            if self.half_open_attempts >= self.config.half_open_requests:
                self.state = "closed"
                self.failure_count = 0
                self.half_open_attempts = 0

    def record_failure(self) -> None:
        """Record a failed request."""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)

        if self.state == "half-open":
            # Failure during recovery, open circuit again
            self.state = "open"
        elif self.failure_count >= self.config.failure_threshold:
            # Too many failures, open the circuit
            self.state = "open"

    def reset(self) -> None:
        """Reset the circuit breaker to closed state."""
        self.state = "closed"
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_attempts = 0

    def get_state(self) -> str:
        """
        Get current circuit breaker state.

        Returns:
            Current state: 'closed', 'open', or 'half-open'
        """
        return self.state
