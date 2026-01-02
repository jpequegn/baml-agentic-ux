"""
Composition Execution Engine for Agent Negotiation.

Provides execution capabilities for running composition plans with parallel
execution, retry with backoff, circuit breakers, and recovery planning.

Issue #64 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.12)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
import threading
import time
import random
import uuid
import json

from .composition_planner import (
    CompositionPlan,
    CompositionStep,
    StepExecutionType,
    PlanStatus,
)


# ============================================
# Execution Status Enums
# ============================================


class ExecutionStatus(Enum):
    """Status of a composition execution."""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RECOVERING = "recovering"


class StepStatus(Enum):
    """Status of a single step execution."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RETRYING = "retrying"


class RecoveryStrategy(Enum):
    """Strategy for recovering from failures."""
    RETRY = "retry"
    ALTERNATIVE_AGENT = "alternative_agent"
    SKIP = "skip"
    ROLLBACK = "rollback"
    COMPENSATE = "compensate"
    ABORT = "abort"
    PARTIAL_COMPLETE = "partial_complete"


class CircuitBreakerState(Enum):
    """State of a circuit breaker."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class BackoffStrategy(Enum):
    """Type of backoff strategy."""
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    JITTERED = "jittered"


# ============================================
# Configuration Types
# ============================================


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    initial_delay_ms: int = 1000
    max_delay_ms: int = 30000
    backoff_multiplier: float = 2.0
    retryable_errors: list[str] = field(default_factory=lambda: ["TIMEOUT", "TEMPORARY_FAILURE", "NETWORK_ERROR"])


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    success_threshold: int = 3
    recovery_timeout_ms: int = 30000
    half_open_requests: int = 3
    monitored_errors: list[str] = field(default_factory=lambda: ["TIMEOUT", "SERVICE_UNAVAILABLE"])


@dataclass
class OrchestrationConfig:
    """Overall orchestration configuration."""
    parallel_execution: bool = True
    max_concurrent_steps: int = 5
    global_timeout_ms: int = 300000  # 5 minutes
    step_timeout_ms: int = 60000  # 1 minute
    retry_config: Optional[RetryConfig] = None
    circuit_breaker: Optional[CircuitBreakerConfig] = None
    collect_metrics: bool = True
    preserve_partial_results: bool = True


# ============================================
# Step Execution Types
# ============================================


@dataclass
class StepError:
    """Error information for a step."""
    error_code: str
    error_type: str
    message: str
    stack_trace: Optional[str] = None
    retry_possible: bool = True
    cause: Optional[str] = None


@dataclass
class StepMetrics:
    """Metrics for step execution."""
    queue_time_ms: int = 0
    execution_time_ms: int = 0
    serialization_time_ms: int = 0
    network_time_ms: Optional[int] = None
    retries_exhausted: bool = False


@dataclass
class StepResult:
    """Result of executing a single step."""
    step_id: str
    step_name: str
    status: StepStatus
    started_at: str
    completed_at: Optional[str]
    output: Optional[str]
    output_type: Optional[str]
    latency_ms: int
    retries: int
    error: Optional[StepError] = None
    metrics: Optional[StepMetrics] = None


# ============================================
# Composition Execution Types
# ============================================


@dataclass
class CompositionError:
    """Error for the overall composition."""
    error_id: str
    error_type: str
    message: str
    failed_step_id: Optional[str] = None
    cascading_failures: Optional[list[str]] = None
    recoverable: bool = True
    suggested_recovery: Optional[RecoveryStrategy] = None


@dataclass
class ExecutionMetrics:
    """Overall execution metrics."""
    total_duration_ms: int
    steps_completed: int
    steps_failed: int
    steps_skipped: int
    total_retries: int
    parallel_efficiency: float
    circuit_breaker_trips: int


@dataclass
class RecoveryAttempt:
    """Record of a recovery attempt."""
    attempt_id: str
    timestamp: str
    strategy: RecoveryStrategy
    trigger_error: str
    success: bool
    details: str


@dataclass
class CompositionExecution:
    """Complete execution of a composition plan."""
    execution_id: str
    plan_id: str
    plan_version: str
    status: ExecutionStatus
    started_at: str
    completed_at: Optional[str]
    step_results: list[StepResult]
    final_output: Optional[str]
    error: Optional[CompositionError]
    execution_metrics: ExecutionMetrics
    recovery_attempts: Optional[list[RecoveryAttempt]] = None


# ============================================
# Recovery Types
# ============================================


@dataclass
class PlanChange:
    """A change made to recovery plan."""
    change_type: str
    step_id: str
    description: str
    original_value: Optional[str] = None
    new_value: Optional[str] = None


@dataclass
class ModifiedPlan:
    """Modifications to the execution plan for recovery."""
    plan_id: str
    changes: list[PlanChange]
    reason: str


@dataclass
class CompensationAction:
    """Action to compensate for partial execution."""
    action_id: str
    step_id: str
    action_type: str
    description: str
    agent_id: Optional[str] = None
    parameters: Optional[str] = None


@dataclass
class RecoveryPlan:
    """Plan for recovering from a failure."""
    recovery_id: str
    strategy: RecoveryStrategy
    original_error: CompositionError
    modified_plan: Optional[ModifiedPlan]
    resume_from_step: Optional[str]
    skip_steps: list[str]
    compensation_actions: Optional[list[CompensationAction]]
    explanation: str
    confidence: float
    estimated_additional_time_ms: Optional[int] = None


# ============================================
# Execution Request/Response Types
# ============================================


@dataclass
class ExecutionParameter:
    """Named execution parameter."""
    name: str
    value: str
    type: str


@dataclass
class SecretReference:
    """Reference to a secret value."""
    name: str
    source: str
    key: str


@dataclass
class ExecutionInputs:
    """Inputs for composition execution."""
    initial_data: str  # JSON
    parameters: list[ExecutionParameter]
    secrets: Optional[list[SecretReference]] = None


@dataclass
class ExecutionContext:
    """Context for execution."""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    trace_id: Optional[str] = None
    priority: int = 5
    deadline: Optional[str] = None
    tags: Optional[list[str]] = None


@dataclass
class ExecuteCompositionRequest:
    """Request to execute a composition."""
    request_id: str
    plan_id: str
    inputs: ExecutionInputs
    config: OrchestrationConfig
    context: Optional[ExecutionContext] = None


@dataclass
class ExecuteCompositionResponse:
    """Response from composition execution."""
    request_id: str
    execution: CompositionExecution


# ============================================
# Circuit Breaker Types
# ============================================


@dataclass
class CircuitBreakerStatus:
    """Status of a circuit breaker."""
    circuit_id: str
    agent_id: str
    state: CircuitBreakerState
    failure_count: int
    success_count: int
    last_failure_at: Optional[str]
    last_state_change: str
    next_retry_at: Optional[str]


# ============================================
# Execution Order Types
# ============================================


@dataclass
class ResourceRequirements:
    """Resource requirements for execution."""
    max_concurrent_agents: int
    estimated_memory_mb: int
    network_calls: int


@dataclass
class ExecutionWave:
    """A wave of parallel execution."""
    wave_number: int
    step_ids: list[str]
    estimated_duration_ms: int
    resource_requirements: ResourceRequirements


@dataclass
class ExecutionOrder:
    """Planned execution order."""
    waves: list[ExecutionWave]
    critical_path: list[str]
    estimated_duration_ms: int
    parallelism_factor: float


# ============================================
# Step Executor Type
# ============================================


# Type for step executor function
StepExecutor = Callable[[CompositionStep, dict[str, Any]], tuple[bool, Optional[str], Optional[StepError]]]


# ============================================
# Circuit Breaker Implementation
# ============================================


class CircuitBreaker:
    """
    Circuit breaker implementation for protecting against cascading failures.
    """

    def __init__(self, agent_id: str, config: CircuitBreakerConfig):
        self.agent_id = agent_id
        self.config = config
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_at: Optional[datetime] = None
        self.last_state_change = datetime.now()
        self._lock = threading.Lock()

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        with self._lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True

            if self.state == CircuitBreakerState.OPEN:
                # Check if recovery timeout has passed
                if self.last_failure_at:
                    elapsed = (datetime.now() - self.last_failure_at).total_seconds() * 1000
                    if elapsed >= self.config.recovery_timeout_ms:
                        self._transition_to(CircuitBreakerState.HALF_OPEN)
                        return True
                return False

            if self.state == CircuitBreakerState.HALF_OPEN:
                # Allow limited requests
                return self.success_count < self.config.half_open_requests

            return False

    def record_success(self) -> None:
        """Record a successful execution."""
        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self._transition_to(CircuitBreakerState.CLOSED)
            elif self.state == CircuitBreakerState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0

    def record_failure(self, error_type: str) -> None:
        """Record a failed execution."""
        with self._lock:
            if error_type not in self.config.monitored_errors:
                return

            self.failure_count += 1
            self.last_failure_at = datetime.now()

            if self.state == CircuitBreakerState.HALF_OPEN:
                # Any failure in half-open returns to open
                self._transition_to(CircuitBreakerState.OPEN)
            elif self.state == CircuitBreakerState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    self._transition_to(CircuitBreakerState.OPEN)

    def _transition_to(self, new_state: CircuitBreakerState) -> None:
        """Transition to a new state."""
        self.state = new_state
        self.last_state_change = datetime.now()

        if new_state == CircuitBreakerState.CLOSED:
            self.failure_count = 0
            self.success_count = 0
        elif new_state == CircuitBreakerState.HALF_OPEN:
            self.success_count = 0

    def get_status(self) -> CircuitBreakerStatus:
        """Get current status."""
        with self._lock:
            next_retry = None
            if self.state == CircuitBreakerState.OPEN and self.last_failure_at:
                retry_time = self.last_failure_at.timestamp() * 1000 + self.config.recovery_timeout_ms
                next_retry = datetime.fromtimestamp(retry_time / 1000).isoformat()

            return CircuitBreakerStatus(
                circuit_id=f"circuit-{self.agent_id}",
                agent_id=self.agent_id,
                state=self.state,
                failure_count=self.failure_count,
                success_count=self.success_count,
                last_failure_at=self.last_failure_at.isoformat() if self.last_failure_at else None,
                last_state_change=self.last_state_change.isoformat(),
                next_retry_at=next_retry,
            )


# ============================================
# CompositionExecutor Class
# ============================================


class CompositionExecutor:
    """
    Executes composition plans with parallel execution, retry, and circuit breakers.

    Provides capabilities for:
    - Sequential and parallel step execution
    - Retry with configurable backoff strategies
    - Circuit breaker protection against cascading failures
    - Recovery planning for failed executions
    """

    def __init__(
        self,
        step_executor: Optional[StepExecutor] = None,
        default_config: Optional[OrchestrationConfig] = None,
    ):
        """
        Initialize the composition executor.

        Args:
            step_executor: Function to execute individual steps
            default_config: Default orchestration configuration
        """
        self.step_executor = step_executor or self._default_step_executor
        self.default_config = default_config or OrchestrationConfig()
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
        self._execution_history: dict[str, CompositionExecution] = {}
        self._lock = threading.Lock()

    def execute(
        self,
        plan: CompositionPlan,
        inputs: ExecutionInputs,
        config: Optional[OrchestrationConfig] = None,
        context: Optional[ExecutionContext] = None,
    ) -> CompositionExecution:
        """
        Execute a composition plan.

        Args:
            plan: The composition plan to execute
            inputs: Inputs for the execution
            config: Orchestration configuration
            context: Execution context

        Returns:
            CompositionExecution with the results
        """
        config = config or self.default_config
        execution_id = str(uuid.uuid4())
        start_time = datetime.now()

        # Initialize execution
        execution = CompositionExecution(
            execution_id=execution_id,
            plan_id=plan.plan_id,
            plan_version=plan.version,
            status=ExecutionStatus.INITIALIZING,
            started_at=start_time.isoformat(),
            completed_at=None,
            step_results=[],
            final_output=None,
            error=None,
            execution_metrics=ExecutionMetrics(
                total_duration_ms=0,
                steps_completed=0,
                steps_failed=0,
                steps_skipped=0,
                total_retries=0,
                parallel_efficiency=1.0,
                circuit_breaker_trips=0,
            ),
            recovery_attempts=[],
        )

        try:
            # Parse initial data
            step_outputs: dict[str, Any] = {"_initial": json.loads(inputs.initial_data)}
            for param in inputs.parameters:
                step_outputs[f"_param_{param.name}"] = param.value

            # Update status
            execution.status = ExecutionStatus.RUNNING

            # Get execution order
            execution_order = self._plan_execution_order(plan, config)

            # Execute waves
            if config.parallel_execution:
                self._execute_parallel(
                    plan, execution, execution_order, step_outputs, config
                )
            else:
                self._execute_sequential(
                    plan, execution, step_outputs, config
                )

            # Determine final status
            if execution.error:
                execution.status = ExecutionStatus.FAILED
            else:
                execution.status = ExecutionStatus.COMPLETED
                # Get final output from exit points
                exit_outputs = [
                    step_outputs.get(step_id)
                    for step_id in plan.exit_points
                    if step_id in step_outputs
                ]
                if exit_outputs:
                    execution.final_output = json.dumps(exit_outputs[0] if len(exit_outputs) == 1 else exit_outputs)

        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = CompositionError(
                error_id=str(uuid.uuid4()),
                error_type="EXECUTION_ERROR",
                message=str(e),
                recoverable=False,
            )

        # Calculate final metrics
        end_time = datetime.now()
        execution.completed_at = end_time.isoformat()
        execution.execution_metrics.total_duration_ms = int(
            (end_time - start_time).total_seconds() * 1000
        )

        # Calculate parallel efficiency
        if execution_order.estimated_duration_ms > 0:
            actual = execution.execution_metrics.total_duration_ms
            ideal = execution_order.estimated_duration_ms
            execution.execution_metrics.parallel_efficiency = min(1.0, ideal / max(1, actual))

        # Store in history
        self._execution_history[execution_id] = execution

        return execution

    def recover(
        self,
        execution: CompositionExecution,
        plan: CompositionPlan,
        available_agents: Optional[list[dict]] = None,
    ) -> RecoveryPlan:
        """
        Generate a recovery plan for a failed execution.

        Args:
            execution: The failed execution
            plan: The original composition plan
            available_agents: Agents available for recovery

        Returns:
            RecoveryPlan with recovery strategy
        """
        if not execution.error:
            return RecoveryPlan(
                recovery_id=str(uuid.uuid4()),
                strategy=RecoveryStrategy.ABORT,
                original_error=CompositionError(
                    error_id=str(uuid.uuid4()),
                    error_type="NO_ERROR",
                    message="No error to recover from",
                    recoverable=False,
                ),
                modified_plan=None,
                resume_from_step=None,
                skip_steps=[],
                compensation_actions=None,
                explanation="No recovery needed - execution has no error",
                confidence=1.0,
            )

        error = execution.error

        # Analyze the failure
        strategy = self._determine_recovery_strategy(execution, error, plan)

        # Build recovery plan based on strategy
        if strategy == RecoveryStrategy.RETRY:
            return self._plan_retry_recovery(execution, error, plan)

        elif strategy == RecoveryStrategy.SKIP:
            return self._plan_skip_recovery(execution, error, plan)

        elif strategy == RecoveryStrategy.ALTERNATIVE_AGENT:
            return self._plan_alternative_agent_recovery(
                execution, error, plan, available_agents
            )

        elif strategy == RecoveryStrategy.PARTIAL_COMPLETE:
            return self._plan_partial_complete_recovery(execution, error, plan)

        elif strategy == RecoveryStrategy.ROLLBACK:
            return self._plan_rollback_recovery(execution, error, plan)

        else:  # ABORT or COMPENSATE
            return RecoveryPlan(
                recovery_id=str(uuid.uuid4()),
                strategy=RecoveryStrategy.ABORT,
                original_error=error,
                modified_plan=None,
                resume_from_step=None,
                skip_steps=[],
                compensation_actions=self._generate_compensation_actions(execution),
                explanation="Recovery not possible - aborting execution",
                confidence=0.9,
            )

    def get_circuit_breaker_status(self, agent_id: str) -> Optional[CircuitBreakerStatus]:
        """Get the status of a circuit breaker for an agent."""
        breaker = self._circuit_breakers.get(agent_id)
        return breaker.get_status() if breaker else None

    def reset_circuit_breaker(self, agent_id: str) -> bool:
        """Reset a circuit breaker to closed state."""
        breaker = self._circuit_breakers.get(agent_id)
        if breaker:
            breaker._transition_to(CircuitBreakerState.CLOSED)
            return True
        return False

    def get_execution(self, execution_id: str) -> Optional[CompositionExecution]:
        """Get an execution by ID."""
        return self._execution_history.get(execution_id)

    # ============================================
    # Private Helper Methods
    # ============================================

    def _default_step_executor(
        self,
        step: CompositionStep,
        inputs: dict[str, Any],
    ) -> tuple[bool, Optional[str], Optional[StepError]]:
        """Default step executor (simulates execution)."""
        # Simulate execution with step's estimated latency
        latency = step.estimated_latency_ms or 100
        time.sleep(latency / 1000)

        # Simulate occasional failures (5% chance)
        if random.random() < 0.05:
            return False, None, StepError(
                error_code="SIM_FAILURE",
                error_type="TEMPORARY_FAILURE",
                message="Simulated random failure",
                retry_possible=True,
            )

        # Return success with simulated output
        output = {
            "step_id": step.step_id,
            "processed": True,
            "input_keys": list(inputs.keys()),
        }
        return True, json.dumps(output), None

    def _plan_execution_order(
        self,
        plan: CompositionPlan,
        config: OrchestrationConfig,
    ) -> ExecutionOrder:
        """Plan the execution order considering parallelism."""
        # Build dependency graph
        dependencies: dict[str, set[str]] = {s.step_id: set() for s in plan.steps}
        for dep in plan.dependencies:
            if dep.to_step in dependencies:
                dependencies[dep.to_step].add(dep.from_step)

        # Topological sort into waves
        waves: list[ExecutionWave] = []
        remaining = set(dependencies.keys())
        completed: set[str] = set()
        wave_number = 0

        while remaining:
            # Find steps with all dependencies satisfied
            ready = [
                step_id for step_id in remaining
                if dependencies[step_id].issubset(completed)
            ]

            if not ready:
                break  # Circular dependency or error

            # Limit by max concurrent
            if config.parallel_execution:
                ready = ready[:config.max_concurrent_steps]
            else:
                ready = ready[:1]

            # Calculate wave duration
            step_latencies = [
                next((s.estimated_latency_ms or 0 for s in plan.steps if s.step_id == sid), 0)
                for sid in ready
            ]
            wave_duration = max(step_latencies) if step_latencies else 0

            waves.append(ExecutionWave(
                wave_number=wave_number,
                step_ids=ready,
                estimated_duration_ms=wave_duration,
                resource_requirements=ResourceRequirements(
                    max_concurrent_agents=len(ready),
                    estimated_memory_mb=len(ready) * 100,  # Estimate
                    network_calls=len(ready),
                ),
            ))

            for step_id in ready:
                remaining.remove(step_id)
                completed.add(step_id)

            wave_number += 1

        # Calculate totals
        total_duration = sum(w.estimated_duration_ms for w in waves)
        sequential_duration = sum(
            s.estimated_latency_ms or 0 for s in plan.steps
        )
        parallelism_factor = sequential_duration / max(1, total_duration) if sequential_duration > 0 else 1.0

        # Find critical path (simplified: longest path)
        critical_path = self._find_critical_path(plan, dependencies)

        return ExecutionOrder(
            waves=waves,
            critical_path=critical_path,
            estimated_duration_ms=total_duration,
            parallelism_factor=min(parallelism_factor, len(plan.steps)),
        )

    def _find_critical_path(
        self,
        plan: CompositionPlan,
        dependencies: dict[str, set[str]],
    ) -> list[str]:
        """Find the critical path through the plan."""
        if not plan.steps:
            return []

        latencies = {s.step_id: s.estimated_latency_ms or 0 for s in plan.steps}

        # Build forward graph
        forward: dict[str, list[str]] = {s.step_id: [] for s in plan.steps}
        for step_id, deps in dependencies.items():
            for dep in deps:
                if dep in forward:
                    forward[dep].append(step_id)

        # Find longest path from entry
        def longest_path(node: str, memo: dict) -> tuple[int, list[str]]:
            if node in memo:
                return memo[node]

            neighbors = forward.get(node, [])
            if not neighbors:
                return latencies.get(node, 0), [node]

            best_length = 0
            best_path: list[str] = []

            for neighbor in neighbors:
                length, path = longest_path(neighbor, memo)
                if length > best_length:
                    best_length = length
                    best_path = path

            result = (latencies.get(node, 0) + best_length, [node] + best_path)
            memo[node] = result
            return result

        memo: dict = {}
        _, critical = longest_path(plan.entry_point, memo)
        return critical

    def _execute_sequential(
        self,
        plan: CompositionPlan,
        execution: CompositionExecution,
        step_outputs: dict[str, Any],
        config: OrchestrationConfig,
    ) -> None:
        """Execute steps sequentially."""
        for step in plan.steps:
            result = self._execute_step(step, step_outputs, config)
            execution.step_results.append(result)

            if result.status == StepStatus.COMPLETED:
                execution.execution_metrics.steps_completed += 1
                if result.output:
                    try:
                        step_outputs[step.step_id] = json.loads(result.output)
                    except json.JSONDecodeError:
                        step_outputs[step.step_id] = result.output
            elif result.status == StepStatus.FAILED:
                execution.execution_metrics.steps_failed += 1
                execution.error = CompositionError(
                    error_id=str(uuid.uuid4()),
                    error_type="STEP_FAILED",
                    message=f"Step {step.step_id} failed",
                    failed_step_id=step.step_id,
                    recoverable=result.error.retry_possible if result.error else False,
                    suggested_recovery=RecoveryStrategy.RETRY if result.error and result.error.retry_possible else RecoveryStrategy.ABORT,
                )
                break
            elif result.status == StepStatus.SKIPPED:
                execution.execution_metrics.steps_skipped += 1

            execution.execution_metrics.total_retries += result.retries

    def _execute_parallel(
        self,
        plan: CompositionPlan,
        execution: CompositionExecution,
        order: ExecutionOrder,
        step_outputs: dict[str, Any],
        config: OrchestrationConfig,
    ) -> None:
        """Execute steps in parallel according to execution order."""
        step_map = {s.step_id: s for s in plan.steps}

        with ThreadPoolExecutor(max_workers=config.max_concurrent_steps) as executor:
            for wave in order.waves:
                # Submit all steps in wave
                futures: dict[Future, str] = {}

                for step_id in wave.step_ids:
                    step = step_map.get(step_id)
                    if not step:
                        continue

                    # Check if dependencies are satisfied
                    deps_satisfied = all(
                        dep.from_step in step_outputs
                        for dep in plan.dependencies
                        if dep.to_step == step_id
                    )

                    if deps_satisfied:
                        future = executor.submit(
                            self._execute_step, step, step_outputs.copy(), config
                        )
                        futures[future] = step_id

                # Wait for all futures in wave
                for future in as_completed(futures):
                    step_id = futures[future]
                    try:
                        result = future.result()
                        execution.step_results.append(result)

                        if result.status == StepStatus.COMPLETED:
                            execution.execution_metrics.steps_completed += 1
                            if result.output:
                                try:
                                    step_outputs[step_id] = json.loads(result.output)
                                except json.JSONDecodeError:
                                    step_outputs[step_id] = result.output
                        elif result.status == StepStatus.FAILED:
                            execution.execution_metrics.steps_failed += 1
                            if not execution.error:
                                execution.error = CompositionError(
                                    error_id=str(uuid.uuid4()),
                                    error_type="STEP_FAILED",
                                    message=f"Step {step_id} failed",
                                    failed_step_id=step_id,
                                    recoverable=result.error.retry_possible if result.error else False,
                                )
                        elif result.status == StepStatus.SKIPPED:
                            execution.execution_metrics.steps_skipped += 1

                        execution.execution_metrics.total_retries += result.retries

                    except Exception as e:
                        execution.execution_metrics.steps_failed += 1
                        execution.step_results.append(StepResult(
                            step_id=step_id,
                            step_name=step_map.get(step_id, CompositionStep(
                                step_id=step_id,
                                name="Unknown",
                                agent_id="",
                                agent_name="",
                                capability_name="",
                                input_bindings=[],
                                output_name="",
                                execution_type=StepExecutionType.SEQUENTIAL,
                                timeout_ms=0,
                            )).name,
                            status=StepStatus.FAILED,
                            started_at=datetime.now().isoformat(),
                            completed_at=datetime.now().isoformat(),
                            output=None,
                            output_type=None,
                            latency_ms=0,
                            retries=0,
                            error=StepError(
                                error_code="EXECUTION_ERROR",
                                error_type="EXECUTION_ERROR",
                                message=str(e),
                                retry_possible=False,
                            ),
                        ))

                # Check for errors that should stop execution
                if execution.error and not config.preserve_partial_results:
                    break

    def _execute_step(
        self,
        step: CompositionStep,
        inputs: dict[str, Any],
        config: OrchestrationConfig,
    ) -> StepResult:
        """Execute a single step with retry logic."""
        start_time = datetime.now()
        retry_config = config.retry_config or RetryConfig()
        retries = 0
        last_error: Optional[StepError] = None

        # Check circuit breaker
        breaker = self._get_or_create_circuit_breaker(step.agent_id, config)
        if breaker and not breaker.can_execute():
            return StepResult(
                step_id=step.step_id,
                step_name=step.name,
                status=StepStatus.FAILED,
                started_at=start_time.isoformat(),
                completed_at=datetime.now().isoformat(),
                output=None,
                output_type=None,
                latency_ms=0,
                retries=0,
                error=StepError(
                    error_code="CIRCUIT_OPEN",
                    error_type="CIRCUIT_BREAKER",
                    message=f"Circuit breaker is open for agent {step.agent_id}",
                    retry_possible=True,
                ),
            )

        # Build step inputs from bindings
        step_inputs = self._build_step_inputs(step, inputs)

        while retries <= retry_config.max_retries:
            try:
                success, output, error = self.step_executor(step, step_inputs)

                if success:
                    if breaker:
                        breaker.record_success()

                    end_time = datetime.now()
                    return StepResult(
                        step_id=step.step_id,
                        step_name=step.name,
                        status=StepStatus.COMPLETED,
                        started_at=start_time.isoformat(),
                        completed_at=end_time.isoformat(),
                        output=output,
                        output_type="json",
                        latency_ms=int((end_time - start_time).total_seconds() * 1000),
                        retries=retries,
                        metrics=StepMetrics(
                            queue_time_ms=0,
                            execution_time_ms=int((end_time - start_time).total_seconds() * 1000),
                            serialization_time_ms=0,
                        ),
                    )

                last_error = error

                # Record failure
                if breaker and error:
                    breaker.record_failure(error.error_type)

                # Check if retryable
                if not error or not error.retry_possible:
                    break

                if error.error_type not in retry_config.retryable_errors:
                    break

            except Exception as e:
                last_error = StepError(
                    error_code="EXCEPTION",
                    error_type="EXCEPTION",
                    message=str(e),
                    retry_possible=True,
                )

            # Calculate delay for retry
            if retries < retry_config.max_retries:
                delay = self._calculate_backoff_delay(retries, retry_config)
                time.sleep(delay / 1000)

            retries += 1

        # All retries exhausted
        end_time = datetime.now()
        return StepResult(
            step_id=step.step_id,
            step_name=step.name,
            status=StepStatus.FAILED,
            started_at=start_time.isoformat(),
            completed_at=end_time.isoformat(),
            output=None,
            output_type=None,
            latency_ms=int((end_time - start_time).total_seconds() * 1000),
            retries=retries,
            error=last_error,
            metrics=StepMetrics(
                queue_time_ms=0,
                execution_time_ms=int((end_time - start_time).total_seconds() * 1000),
                serialization_time_ms=0,
                retries_exhausted=retries >= retry_config.max_retries,
            ),
        )

    def _build_step_inputs(
        self,
        step: CompositionStep,
        available_outputs: dict[str, Any],
    ) -> dict[str, Any]:
        """Build inputs for a step from its bindings."""
        inputs: dict[str, Any] = {}

        for binding in step.input_bindings:
            value = None

            if binding.source.value == "previous_step":
                # Parse reference like "step_1.output"
                parts = binding.source_reference.split(".")
                if len(parts) >= 1:
                    step_id = parts[0]
                    value = available_outputs.get(step_id)
                    # Navigate nested path if specified
                    for part in parts[1:]:
                        if isinstance(value, dict):
                            value = value.get(part)
                        else:
                            break

            elif binding.source.value == "literal":
                value = binding.source_reference

            elif binding.source.value == "user_input":
                value = available_outputs.get("_initial")

            elif binding.source.value == "context":
                value = available_outputs.get(f"_param_{binding.source_reference}")

            # Use default if no value found
            if value is None and binding.default_value:
                value = binding.default_value

            if value is not None or not binding.required:
                inputs[binding.parameter_name] = value

        return inputs

    def _calculate_backoff_delay(
        self,
        retry_count: int,
        config: RetryConfig,
    ) -> int:
        """Calculate delay before next retry."""
        if config.backoff_strategy == BackoffStrategy.FIXED:
            delay = config.initial_delay_ms

        elif config.backoff_strategy == BackoffStrategy.LINEAR:
            delay = config.initial_delay_ms + (retry_count * config.initial_delay_ms)

        elif config.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = config.initial_delay_ms * (config.backoff_multiplier ** retry_count)

        elif config.backoff_strategy == BackoffStrategy.JITTERED:
            base_delay = config.initial_delay_ms * (config.backoff_multiplier ** retry_count)
            jitter = random.uniform(0.5, 1.5)
            delay = base_delay * jitter

        else:
            delay = config.initial_delay_ms

        return min(int(delay), config.max_delay_ms)

    def _get_or_create_circuit_breaker(
        self,
        agent_id: str,
        config: OrchestrationConfig,
    ) -> Optional[CircuitBreaker]:
        """Get or create a circuit breaker for an agent."""
        if not config.circuit_breaker:
            return None

        with self._lock:
            if agent_id not in self._circuit_breakers:
                self._circuit_breakers[agent_id] = CircuitBreaker(
                    agent_id, config.circuit_breaker
                )
            return self._circuit_breakers[agent_id]

    def _determine_recovery_strategy(
        self,
        execution: CompositionExecution,
        error: CompositionError,
        plan: CompositionPlan,
    ) -> RecoveryStrategy:
        """Determine the best recovery strategy."""
        # If suggested recovery is provided, use it
        if error.suggested_recovery:
            return error.suggested_recovery

        # Analyze the error
        if not error.recoverable:
            return RecoveryStrategy.ABORT

        # Check if retry might help
        failed_step = next(
            (r for r in execution.step_results if r.step_id == error.failed_step_id),
            None
        )
        if failed_step and failed_step.retries < 3:
            return RecoveryStrategy.RETRY

        # Check if we can skip the failed step
        if error.failed_step_id and error.failed_step_id not in plan.exit_points:
            # Check if any steps depend on it
            dependents = [
                d.to_step for d in plan.dependencies
                if d.from_step == error.failed_step_id
            ]
            if not dependents:
                return RecoveryStrategy.SKIP

        # Check if partial results are acceptable
        completed_count = sum(
            1 for r in execution.step_results if r.status == StepStatus.COMPLETED
        )
        if completed_count > len(plan.steps) // 2:
            return RecoveryStrategy.PARTIAL_COMPLETE

        return RecoveryStrategy.ABORT

    def _plan_retry_recovery(
        self,
        execution: CompositionExecution,
        error: CompositionError,
        plan: CompositionPlan,
    ) -> RecoveryPlan:
        """Plan a retry recovery."""
        return RecoveryPlan(
            recovery_id=str(uuid.uuid4()),
            strategy=RecoveryStrategy.RETRY,
            original_error=error,
            modified_plan=None,
            resume_from_step=error.failed_step_id,
            skip_steps=[],
            compensation_actions=None,
            explanation=f"Retry execution from step {error.failed_step_id}",
            confidence=0.7,
            estimated_additional_time_ms=self._estimate_remaining_time(
                plan, execution, error.failed_step_id
            ),
        )

    def _plan_skip_recovery(
        self,
        execution: CompositionExecution,
        error: CompositionError,
        plan: CompositionPlan,
    ) -> RecoveryPlan:
        """Plan a skip recovery."""
        skip_steps = [error.failed_step_id] if error.failed_step_id else []

        return RecoveryPlan(
            recovery_id=str(uuid.uuid4()),
            strategy=RecoveryStrategy.SKIP,
            original_error=error,
            modified_plan=ModifiedPlan(
                plan_id=f"{plan.plan_id}-recovered",
                changes=[
                    PlanChange(
                        change_type="SKIP_STEP",
                        step_id=error.failed_step_id or "",
                        description="Skip failed step and continue",
                    )
                ],
                reason="Step is not critical and can be skipped",
            ),
            resume_from_step=self._find_next_step(plan, error.failed_step_id),
            skip_steps=skip_steps,
            compensation_actions=None,
            explanation=f"Skip step {error.failed_step_id} and continue execution",
            confidence=0.6,
        )

    def _plan_alternative_agent_recovery(
        self,
        execution: CompositionExecution,
        error: CompositionError,
        plan: CompositionPlan,
        available_agents: Optional[list[dict]],
    ) -> RecoveryPlan:
        """Plan an alternative agent recovery."""
        if not available_agents or not error.failed_step_id:
            return self._plan_retry_recovery(execution, error, plan)

        # Find the failed step
        failed_step = next(
            (s for s in plan.steps if s.step_id == error.failed_step_id),
            None
        )
        if not failed_step:
            return self._plan_retry_recovery(execution, error, plan)

        # Find alternative agent
        alt_agent = next(
            (a for a in available_agents
             if a.get("agent_id") != failed_step.agent_id
             and failed_step.capability_name in a.get("capabilities", [])),
            None
        )

        if not alt_agent:
            return self._plan_retry_recovery(execution, error, plan)

        return RecoveryPlan(
            recovery_id=str(uuid.uuid4()),
            strategy=RecoveryStrategy.ALTERNATIVE_AGENT,
            original_error=error,
            modified_plan=ModifiedPlan(
                plan_id=f"{plan.plan_id}-recovered",
                changes=[
                    PlanChange(
                        change_type="CHANGE_AGENT",
                        step_id=error.failed_step_id,
                        description=f"Switch to agent {alt_agent.get('agent_name')}",
                        original_value=failed_step.agent_id,
                        new_value=alt_agent.get("agent_id"),
                    )
                ],
                reason="Use alternative agent for failed step",
            ),
            resume_from_step=error.failed_step_id,
            skip_steps=[],
            compensation_actions=None,
            explanation=f"Retry step {error.failed_step_id} with agent {alt_agent.get('agent_name')}",
            confidence=0.65,
        )

    def _plan_partial_complete_recovery(
        self,
        execution: CompositionExecution,
        error: CompositionError,
        plan: CompositionPlan,
    ) -> RecoveryPlan:
        """Plan a partial completion recovery."""
        completed_steps = [
            r.step_id for r in execution.step_results
            if r.status == StepStatus.COMPLETED
        ]

        return RecoveryPlan(
            recovery_id=str(uuid.uuid4()),
            strategy=RecoveryStrategy.PARTIAL_COMPLETE,
            original_error=error,
            modified_plan=None,
            resume_from_step=None,
            skip_steps=[s.step_id for s in plan.steps if s.step_id not in completed_steps],
            compensation_actions=None,
            explanation=f"Accept partial results from {len(completed_steps)} completed steps",
            confidence=0.5,
        )

    def _plan_rollback_recovery(
        self,
        execution: CompositionExecution,
        error: CompositionError,
        plan: CompositionPlan,
    ) -> RecoveryPlan:
        """Plan a rollback recovery."""
        return RecoveryPlan(
            recovery_id=str(uuid.uuid4()),
            strategy=RecoveryStrategy.ROLLBACK,
            original_error=error,
            modified_plan=None,
            resume_from_step=None,
            skip_steps=[],
            compensation_actions=self._generate_compensation_actions(execution),
            explanation="Rollback all completed steps and abort",
            confidence=0.8,
        )

    def _generate_compensation_actions(
        self,
        execution: CompositionExecution,
    ) -> list[CompensationAction]:
        """Generate compensation actions for completed steps."""
        actions: list[CompensationAction] = []

        for result in reversed(execution.step_results):
            if result.status == StepStatus.COMPLETED:
                actions.append(CompensationAction(
                    action_id=str(uuid.uuid4()),
                    step_id=result.step_id,
                    action_type="UNDO",
                    description=f"Undo effects of step {result.step_name}",
                ))

        return actions

    def _find_next_step(
        self,
        plan: CompositionPlan,
        after_step_id: Optional[str],
    ) -> Optional[str]:
        """Find the next step after a given step."""
        if not after_step_id:
            return None

        # Find steps that depend on the given step
        dependents = [
            d.to_step for d in plan.dependencies
            if d.from_step == after_step_id
        ]

        return dependents[0] if dependents else None

    def _estimate_remaining_time(
        self,
        plan: CompositionPlan,
        execution: CompositionExecution,
        from_step_id: Optional[str],
    ) -> int:
        """Estimate remaining execution time."""
        completed_ids = {r.step_id for r in execution.step_results if r.status == StepStatus.COMPLETED}

        remaining_latency = sum(
            s.estimated_latency_ms or 0
            for s in plan.steps
            if s.step_id not in completed_ids
        )

        return remaining_latency
