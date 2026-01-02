"""
Composition Planning for Agent Negotiation.

Provides capability composition planning for combining multiple agent capabilities
to achieve complex goals through orchestrated multi-agent workflows.

Issue #63 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.11)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime
import uuid


# ============================================
# Input Source Enums
# ============================================


class InputSource(Enum):
    """Source of input data for a composition step."""
    LITERAL = "literal"  # Hardcoded value provided in the plan
    PREVIOUS_STEP = "previous_step"  # Output from an earlier step
    USER_INPUT = "user_input"  # From the original user request
    CONTEXT = "context"  # From session or execution context
    COMPUTED = "computed"  # Computed at runtime from multiple sources


class OptimizationGoal(Enum):
    """Type of optimization goal."""
    MINIMIZE_LATENCY = "minimize_latency"
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_RELIABILITY = "maximize_reliability"
    MAXIMIZE_QUALITY = "maximize_quality"
    MINIMIZE_STEPS = "minimize_steps"
    BALANCE = "balance"


class PlanStatus(Enum):
    """Status of a composition plan."""
    DRAFT = "draft"
    VALIDATED = "validated"
    OPTIMIZED = "optimized"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class DependencyType(Enum):
    """Type of step dependency."""
    DATA = "data"  # Data dependency - needs output from previous step
    CONTROL = "control"  # Control dependency - must wait for completion
    RESOURCE = "resource"  # Resource dependency - needs shared resource
    ORDERING = "ordering"  # Pure ordering constraint


class FailureSeverity(Enum):
    """Severity of a failure mode."""
    CATASTROPHIC = "catastrophic"  # Entire composition fails
    MAJOR = "major"  # Significant degradation
    MINOR = "minor"  # Recoverable with degraded output
    NEGLIGIBLE = "negligible"  # Minimal impact


class StepExecutionType(Enum):
    """Type of step execution."""
    SEQUENTIAL = "sequential"  # Must wait for previous steps
    PARALLEL = "parallel"  # Can run in parallel with other steps
    CONDITIONAL = "conditional"  # Execution depends on condition
    LOOP = "loop"  # May execute multiple times


# ============================================
# Input Binding Types
# ============================================


@dataclass
class InputBinding:
    """Binding for a step input parameter."""
    parameter_name: str
    source: InputSource
    source_reference: str  # step_id.output_name, literal value, etc.
    transformation: Optional[str] = None
    default_value: Optional[str] = None
    required: bool = True


@dataclass
class CompositionConstraint:
    """Constraint on composition."""
    constraint_id: str
    constraint_type: str  # latency, cost, agent, etc.
    operator: str  # <, <=, =, >=, >, !=
    value: str
    priority: int  # 1 = highest
    hard: bool  # Whether this is a hard constraint


# ============================================
# Composition Step Types
# ============================================


@dataclass
class StepRetryPolicy:
    """Retry policy for a step."""
    max_retries: int
    initial_delay_ms: int
    max_delay_ms: int
    backoff_multiplier: float
    retryable_errors: list[str]


@dataclass
class StepCondition:
    """Condition for step execution."""
    condition_id: str
    source_step: str
    field_path: str  # JSONPath to field to check
    operator: str
    value: str


@dataclass
class CompositionStep:
    """A single step in a composition plan."""
    step_id: str
    name: str
    agent_id: str
    agent_name: str
    capability_name: str
    input_bindings: list[InputBinding]
    output_name: str
    execution_type: StepExecutionType
    timeout_ms: int
    description: Optional[str] = None
    capability_version: Optional[str] = None
    output_schema: Optional[str] = None
    retry_policy: Optional[StepRetryPolicy] = None
    conditions: Optional[list[StepCondition]] = None
    estimated_latency_ms: Optional[int] = None
    estimated_cost: Optional[float] = None


# ============================================
# Data Flow Types
# ============================================


@dataclass
class DataFlowEdge:
    """Edge in the data flow graph."""
    edge_id: str
    from_step: str
    from_output: str
    to_step: str
    to_input: str
    transformation: Optional[str] = None
    data_type: Optional[str] = None


@dataclass
class StepDependency:
    """Dependency between steps."""
    dependency_id: str
    from_step: str  # Step that must complete first
    to_step: str  # Step that depends on the other
    dependency_type: DependencyType
    required: bool


# ============================================
# Failure Mode Types
# ============================================


@dataclass
class FailureMode:
    """Identified failure mode in a composition."""
    failure_id: str
    step_id: str
    failure_type: str
    probability: float  # 0.0-1.0
    severity: FailureSeverity
    impact: str
    mitigation: str
    fallback_step: Optional[str] = None


@dataclass
class RiskAssessment:
    """Risk assessment for a composition."""
    overall_risk_score: float  # 0.0-1.0
    failure_modes: list[FailureMode]
    critical_path: list[str]  # Steps on the critical path
    single_points_of_failure: list[str]
    recommendations: list[str]


# ============================================
# Composition Plan Types
# ============================================


@dataclass
class PlanMetadata:
    """Metadata for a composition plan."""
    created_at: str  # ISO 8601
    created_by: Optional[str] = None
    last_modified: Optional[str] = None
    tags: Optional[list[str]] = None
    notes: Optional[str] = None


@dataclass
class CompositionPlan:
    """Complete composition plan."""
    plan_id: str
    version: str
    goal: str
    status: PlanStatus
    steps: list[CompositionStep]
    data_flow: list[DataFlowEdge]
    dependencies: list[StepDependency]
    entry_point: str
    exit_points: list[str]
    estimated_latency_ms: int
    estimated_cost: Optional[float] = None
    risk_assessment: Optional[RiskAssessment] = None
    metadata: Optional[PlanMetadata] = None


# ============================================
# Available Agent Types
# ============================================


@dataclass
class AvailableCapability:
    """Available capability from an agent."""
    capability_name: str
    capability_version: str
    description: str
    input_schema: str  # JSON
    output_schema: str  # JSON
    estimated_latency_ms: int
    reliability: float  # 0.0-1.0
    estimated_cost: Optional[float] = None


@dataclass
class AvailableAgent:
    """Available agent for composition."""
    agent_id: str
    agent_name: str
    capabilities: list[AvailableCapability]
    trust_score: float  # 0.0-1.0
    availability: float  # 0.0-1.0


# ============================================
# Planning Request/Response Types
# ============================================


@dataclass
class PlanningPreferences:
    """Preferences for plan generation."""
    prefer_parallel: bool = True
    prefer_fewer_agents: bool = False
    prefer_trusted_agents: bool = True
    max_steps: Optional[int] = None
    max_depth: Optional[int] = None


@dataclass
class PlanningContext:
    """Context for planning."""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    previous_plans: Optional[list[str]] = None
    domain_hints: Optional[list[str]] = None


@dataclass
class PlanCompositionRequest:
    """Request to create a composition plan."""
    request_id: str
    goal: str
    available_agents: list[AvailableAgent]
    constraints: list[CompositionConstraint]
    preferences: Optional[PlanningPreferences] = None
    context: Optional[PlanningContext] = None


@dataclass
class PlanCompositionResponse:
    """Response from plan composition."""
    request_id: str
    plan: CompositionPlan
    alternatives: Optional[list[CompositionPlan]] = None
    planning_notes: list[str] = field(default_factory=list)
    generation_time_ms: int = 0


# ============================================
# Optimization Types
# ============================================


@dataclass
class OptimizationMetrics:
    """Metrics for optimization comparison."""
    total_latency_ms: int
    total_cost: float
    step_count: int
    parallel_steps: int
    risk_score: float
    reliability: float


@dataclass
class PlanImprovement:
    """Improvement made during optimization."""
    improvement_id: str
    improvement_type: str
    description: str
    affected_steps: list[str]
    metric_improved: str
    improvement_amount: str


@dataclass
class OptimizePlanResponse:
    """Result of plan optimization."""
    request_id: str
    original_plan: CompositionPlan
    optimized_plan: CompositionPlan
    improvements: list[PlanImprovement]
    metrics_before: OptimizationMetrics
    metrics_after: OptimizationMetrics


# ============================================
# Validation Types
# ============================================


@dataclass
class ValidationError:
    """Validation error."""
    error_id: str
    error_type: str
    message: str
    step_id: Optional[str] = None
    field: Optional[str] = None


@dataclass
class ValidationWarning:
    """Validation warning."""
    warning_id: str
    warning_type: str
    message: str
    step_id: Optional[str] = None
    recommendation: Optional[str] = None


@dataclass
class PlanValidationResult:
    """Result of plan validation."""
    valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationWarning]
    suggestions: list[str]


# ============================================
# CompositionPlanner Class
# ============================================


class CompositionPlanner:
    """
    Plans compositions of multiple agent capabilities.

    Provides capabilities for:
    - Creating composition plans from goals
    - Validating plans for correctness
    - Optimizing plans for various goals
    - Analyzing failure modes and risks
    """

    def __init__(self):
        """Initialize the composition planner."""
        self._plan_cache: dict[str, CompositionPlan] = {}

    def plan(
        self,
        request: PlanCompositionRequest,
    ) -> PlanCompositionResponse:
        """
        Create a composition plan to achieve the specified goal.

        Args:
            request: The plan composition request

        Returns:
            PlanCompositionResponse with the generated plan
        """
        start_time = datetime.now()

        # Analyze goal to identify required capabilities
        required_capabilities = self._analyze_goal(request.goal)

        # Match capabilities to available agents
        capability_assignments = self._assign_capabilities(
            required_capabilities,
            request.available_agents,
            request.preferences,
        )

        # Build steps from assignments
        steps = self._build_steps(capability_assignments, request.preferences)

        # Determine execution order and dependencies
        dependencies = self._analyze_dependencies(steps)

        # Build data flow graph
        data_flow = self._build_data_flow(steps, dependencies)

        # Identify entry and exit points
        entry_point, exit_points = self._identify_endpoints(steps, dependencies)

        # Estimate total latency
        estimated_latency = self._estimate_total_latency(steps, dependencies)

        # Estimate total cost
        estimated_cost = self._estimate_total_cost(steps)

        # Apply constraints
        steps, dependencies = self._apply_constraints(
            steps, dependencies, request.constraints
        )

        # Build the plan
        plan = CompositionPlan(
            plan_id=str(uuid.uuid4()),
            version="1.0",
            goal=request.goal,
            status=PlanStatus.DRAFT,
            steps=steps,
            data_flow=data_flow,
            dependencies=dependencies,
            entry_point=entry_point,
            exit_points=exit_points,
            estimated_latency_ms=estimated_latency,
            estimated_cost=estimated_cost,
            metadata=PlanMetadata(
                created_at=datetime.now().isoformat(),
            ),
        )

        # Cache the plan
        self._plan_cache[plan.plan_id] = plan

        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        return PlanCompositionResponse(
            request_id=request.request_id,
            plan=plan,
            planning_notes=self._generate_planning_notes(plan, request),
            generation_time_ms=elapsed_ms,
        )

    def validate(
        self,
        plan: CompositionPlan,
    ) -> PlanValidationResult:
        """
        Validate a composition plan for correctness.

        Args:
            plan: The plan to validate

        Returns:
            PlanValidationResult with errors and warnings
        """
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []
        suggestions: list[str] = []

        # Check for circular dependencies
        circular = self._detect_circular_dependencies(plan)
        if circular:
            errors.append(ValidationError(
                error_id=str(uuid.uuid4()),
                error_type="CIRCULAR_DEPENDENCY",
                message=f"Circular dependency detected: {' -> '.join(circular)}",
            ))

        # Check input bindings
        binding_errors = self._validate_input_bindings(plan)
        errors.extend(binding_errors)

        # Check for unreachable steps
        unreachable = self._find_unreachable_steps(plan)
        for step_id in unreachable:
            warnings.append(ValidationWarning(
                warning_id=str(uuid.uuid4()),
                warning_type="UNREACHABLE_STEP",
                message=f"Step {step_id} is unreachable from entry point",
                step_id=step_id,
                recommendation="Remove the step or add a dependency",
            ))

        # Check timeouts
        timeout_warnings = self._validate_timeouts(plan)
        warnings.extend(timeout_warnings)

        # Check for missing exit points
        if not plan.exit_points:
            errors.append(ValidationError(
                error_id=str(uuid.uuid4()),
                error_type="NO_EXIT_POINT",
                message="Plan has no exit points defined",
            ))

        # Generate suggestions
        if len(plan.steps) > 10:
            suggestions.append("Consider breaking into smaller sub-plans")

        parallel_count = sum(
            1 for s in plan.steps if s.execution_type == StepExecutionType.PARALLEL
        )
        if parallel_count == 0 and len(plan.steps) > 3:
            suggestions.append("Consider parallelizing independent steps")

        return PlanValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
        )

    def optimize(
        self,
        plan: CompositionPlan,
        goals: list[OptimizationGoal],
    ) -> OptimizePlanResponse:
        """
        Optimize a plan according to specified goals.

        Args:
            plan: The plan to optimize
            goals: Optimization goals

        Returns:
            OptimizePlanResponse with optimized plan
        """
        # Calculate metrics before optimization
        metrics_before = self._calculate_metrics(plan)

        # Create a copy for optimization
        optimized_plan = self._deep_copy_plan(plan)
        improvements: list[PlanImprovement] = []

        for goal in goals:
            if goal == OptimizationGoal.MINIMIZE_LATENCY:
                new_improvements = self._optimize_latency(optimized_plan)
                improvements.extend(new_improvements)

            elif goal == OptimizationGoal.MINIMIZE_COST:
                new_improvements = self._optimize_cost(optimized_plan)
                improvements.extend(new_improvements)

            elif goal == OptimizationGoal.MAXIMIZE_RELIABILITY:
                new_improvements = self._optimize_reliability(optimized_plan)
                improvements.extend(new_improvements)

            elif goal == OptimizationGoal.MINIMIZE_STEPS:
                new_improvements = self._optimize_step_count(optimized_plan)
                improvements.extend(new_improvements)

            elif goal == OptimizationGoal.BALANCE:
                # Apply all optimizations with lower intensity
                improvements.extend(self._optimize_latency(optimized_plan, aggressive=False))
                improvements.extend(self._optimize_cost(optimized_plan, aggressive=False))

        # Update plan status
        optimized_plan.status = PlanStatus.OPTIMIZED

        # Calculate metrics after optimization
        metrics_after = self._calculate_metrics(optimized_plan)

        return OptimizePlanResponse(
            request_id=str(uuid.uuid4()),
            original_plan=plan,
            optimized_plan=optimized_plan,
            improvements=improvements,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
        )

    def analyze_risks(
        self,
        plan: CompositionPlan,
    ) -> RiskAssessment:
        """
        Analyze failure modes and risks in a plan.

        Args:
            plan: The plan to analyze

        Returns:
            RiskAssessment with failure modes and recommendations
        """
        failure_modes: list[FailureMode] = []

        # Analyze each step for failure modes
        for step in plan.steps:
            step_failures = self._analyze_step_failures(step)
            failure_modes.extend(step_failures)

        # Find critical path
        critical_path = self._find_critical_path(plan)

        # Find single points of failure
        single_points = self._find_single_points_of_failure(plan)

        # Calculate overall risk score
        risk_score = self._calculate_risk_score(failure_modes, critical_path, single_points)

        # Generate recommendations
        recommendations = self._generate_risk_recommendations(
            failure_modes, critical_path, single_points
        )

        return RiskAssessment(
            overall_risk_score=risk_score,
            failure_modes=failure_modes,
            critical_path=critical_path,
            single_points_of_failure=single_points,
            recommendations=recommendations,
        )

    def get_plan(self, plan_id: str) -> Optional[CompositionPlan]:
        """Get a cached plan by ID."""
        return self._plan_cache.get(plan_id)

    def get_execution_order(
        self,
        plan: CompositionPlan,
    ) -> list[list[str]]:
        """
        Get the execution order of steps as waves of parallelizable steps.

        Args:
            plan: The plan to analyze

        Returns:
            List of step ID lists, where each inner list can execute in parallel
        """
        return self._topological_sort_with_waves(plan)

    # ============================================
    # Private Helper Methods
    # ============================================

    def _analyze_goal(self, goal: str) -> list[str]:
        """Analyze goal to identify required capabilities."""
        # Simple keyword-based capability inference
        capabilities = []

        goal_lower = goal.lower()

        if any(word in goal_lower for word in ["process", "transform", "convert"]):
            capabilities.append("data_processing")

        if any(word in goal_lower for word in ["analyze", "analysis", "insight"]):
            capabilities.append("analytics")

        if any(word in goal_lower for word in ["store", "save", "persist"]):
            capabilities.append("storage")

        if any(word in goal_lower for word in ["send", "notify", "alert"]):
            capabilities.append("notification")

        if any(word in goal_lower for word in ["fetch", "retrieve", "get", "query"]):
            capabilities.append("data_retrieval")

        if any(word in goal_lower for word in ["validate", "verify", "check"]):
            capabilities.append("validation")

        if any(word in goal_lower for word in ["generate", "create", "produce"]):
            capabilities.append("generation")

        if any(word in goal_lower for word in ["summarize", "summary", "aggregate"]):
            capabilities.append("summarization")

        # Default capability if none matched
        if not capabilities:
            capabilities.append("general_processing")

        return capabilities

    def _assign_capabilities(
        self,
        required_capabilities: list[str],
        available_agents: list[AvailableAgent],
        preferences: Optional[PlanningPreferences],
    ) -> list[tuple[str, AvailableAgent, AvailableCapability]]:
        """Assign required capabilities to available agents."""
        assignments: list[tuple[str, AvailableAgent, AvailableCapability]] = []

        for req_cap in required_capabilities:
            best_agent = None
            best_capability = None
            best_score = -1.0

            for agent in available_agents:
                for cap in agent.capabilities:
                    # Check if capability matches
                    if not self._capability_matches(cap.capability_name, req_cap):
                        continue

                    # Score this option
                    score = self._score_assignment(agent, cap, preferences)

                    if score > best_score:
                        best_score = score
                        best_agent = agent
                        best_capability = cap

            if best_agent and best_capability:
                assignments.append((req_cap, best_agent, best_capability))

        return assignments

    def _capability_matches(self, cap_name: str, required: str) -> bool:
        """Check if a capability name matches the required capability."""
        cap_lower = cap_name.lower()
        req_lower = required.lower()

        # Exact match
        if cap_lower == req_lower:
            return True

        # Partial match
        if req_lower in cap_lower or cap_lower in req_lower:
            return True

        # Common synonyms
        synonyms = {
            "data_processing": ["transform", "process", "convert"],
            "analytics": ["analyze", "analysis", "insight"],
            "storage": ["store", "save", "persist", "database"],
            "notification": ["notify", "alert", "send", "email"],
            "data_retrieval": ["fetch", "get", "query", "retrieve"],
            "validation": ["validate", "verify", "check"],
            "generation": ["generate", "create", "produce"],
            "summarization": ["summarize", "aggregate", "summary"],
        }

        for key, values in synonyms.items():
            if req_lower == key or req_lower in values:
                if cap_lower == key or any(v in cap_lower for v in values):
                    return True

        return False

    def _score_assignment(
        self,
        agent: AvailableAgent,
        capability: AvailableCapability,
        preferences: Optional[PlanningPreferences],
    ) -> float:
        """Score an agent/capability assignment."""
        score = 0.0

        # Base reliability score
        score += capability.reliability * 0.3

        # Trust score
        score += agent.trust_score * 0.3

        # Availability
        score += agent.availability * 0.2

        # Latency (lower is better, normalize)
        latency_score = max(0, 1.0 - capability.estimated_latency_ms / 10000)
        score += latency_score * 0.2

        # Apply preferences
        if preferences:
            if preferences.prefer_trusted_agents:
                score += agent.trust_score * 0.1

        return score

    def _build_steps(
        self,
        assignments: list[tuple[str, AvailableAgent, AvailableCapability]],
        preferences: Optional[PlanningPreferences],
    ) -> list[CompositionStep]:
        """Build composition steps from capability assignments."""
        steps: list[CompositionStep] = []

        for i, (req_cap, agent, capability) in enumerate(assignments):
            step_id = f"step_{i + 1}"

            # Determine execution type
            exec_type = StepExecutionType.SEQUENTIAL
            if preferences and preferences.prefer_parallel:
                # Will be updated during dependency analysis
                exec_type = StepExecutionType.SEQUENTIAL

            step = CompositionStep(
                step_id=step_id,
                name=f"{capability.capability_name}",
                description=capability.description,
                agent_id=agent.agent_id,
                agent_name=agent.agent_name,
                capability_name=capability.capability_name,
                capability_version=capability.capability_version,
                input_bindings=[],  # Will be filled during data flow analysis
                output_name=f"{step_id}_output",
                output_schema=capability.output_schema,
                execution_type=exec_type,
                timeout_ms=capability.estimated_latency_ms * 3,  # 3x latency as timeout
                estimated_latency_ms=capability.estimated_latency_ms,
                estimated_cost=capability.estimated_cost,
                retry_policy=StepRetryPolicy(
                    max_retries=3,
                    initial_delay_ms=1000,
                    max_delay_ms=10000,
                    backoff_multiplier=2.0,
                    retryable_errors=["TIMEOUT", "TEMPORARY_FAILURE"],
                ),
            )
            steps.append(step)

        return steps

    def _analyze_dependencies(
        self,
        steps: list[CompositionStep],
    ) -> list[StepDependency]:
        """Analyze dependencies between steps."""
        dependencies: list[StepDependency] = []

        # Simple sequential dependencies for now
        for i in range(1, len(steps)):
            dep = StepDependency(
                dependency_id=str(uuid.uuid4()),
                from_step=steps[i - 1].step_id,
                to_step=steps[i].step_id,
                dependency_type=DependencyType.DATA,
                required=True,
            )
            dependencies.append(dep)

        return dependencies

    def _build_data_flow(
        self,
        steps: list[CompositionStep],
        dependencies: list[StepDependency],
    ) -> list[DataFlowEdge]:
        """Build data flow graph from steps and dependencies."""
        edges: list[DataFlowEdge] = []

        for dep in dependencies:
            if dep.dependency_type == DependencyType.DATA:
                # Find the steps
                from_step = next((s for s in steps if s.step_id == dep.from_step), None)
                to_step = next((s for s in steps if s.step_id == dep.to_step), None)

                if from_step and to_step:
                    edge = DataFlowEdge(
                        edge_id=str(uuid.uuid4()),
                        from_step=from_step.step_id,
                        from_output=from_step.output_name,
                        to_step=to_step.step_id,
                        to_input="input",  # Generic input name
                    )
                    edges.append(edge)

                    # Update input bindings on the target step
                    to_step.input_bindings.append(InputBinding(
                        parameter_name="input",
                        source=InputSource.PREVIOUS_STEP,
                        source_reference=f"{from_step.step_id}.{from_step.output_name}",
                        required=True,
                    ))

        return edges

    def _identify_endpoints(
        self,
        steps: list[CompositionStep],
        dependencies: list[StepDependency],
    ) -> tuple[str, list[str]]:
        """Identify entry and exit points of the plan."""
        if not steps:
            return "", []

        # Entry point: step with no incoming dependencies
        incoming = {dep.to_step for dep in dependencies}
        entry_points = [s.step_id for s in steps if s.step_id not in incoming]
        entry_point = entry_points[0] if entry_points else steps[0].step_id

        # Exit points: steps with no outgoing dependencies
        outgoing = {dep.from_step for dep in dependencies}
        exit_points = [s.step_id for s in steps if s.step_id not in outgoing]

        if not exit_points:
            exit_points = [steps[-1].step_id]

        return entry_point, exit_points

    def _estimate_total_latency(
        self,
        steps: list[CompositionStep],
        dependencies: list[StepDependency],
    ) -> int:
        """Estimate total plan latency."""
        # For sequential execution, sum all latencies
        total = sum(s.estimated_latency_ms or 0 for s in steps)
        return total

    def _estimate_total_cost(
        self,
        steps: list[CompositionStep],
    ) -> Optional[float]:
        """Estimate total plan cost."""
        costs = [s.estimated_cost for s in steps if s.estimated_cost is not None]
        return sum(costs) if costs else None

    def _apply_constraints(
        self,
        steps: list[CompositionStep],
        dependencies: list[StepDependency],
        constraints: list[CompositionConstraint],
    ) -> tuple[list[CompositionStep], list[StepDependency]]:
        """Apply constraints to the plan."""
        # For now, just return as-is (constraints would filter/modify in real impl)
        return steps, dependencies

    def _generate_planning_notes(
        self,
        plan: CompositionPlan,
        request: PlanCompositionRequest,
    ) -> list[str]:
        """Generate notes about planning decisions."""
        notes = []

        notes.append(f"Generated {len(plan.steps)} steps for goal: {plan.goal}")
        notes.append(f"Estimated total latency: {plan.estimated_latency_ms}ms")

        if plan.estimated_cost:
            notes.append(f"Estimated total cost: {plan.estimated_cost}")

        agent_count = len(set(s.agent_id for s in plan.steps))
        notes.append(f"Using {agent_count} agents")

        return notes

    def _detect_circular_dependencies(
        self,
        plan: CompositionPlan,
    ) -> Optional[list[str]]:
        """Detect circular dependencies in the plan."""
        # Build adjacency list
        graph: dict[str, list[str]] = {s.step_id: [] for s in plan.steps}
        for dep in plan.dependencies:
            if dep.from_step in graph:
                graph[dep.from_step].append(dep.to_step)

        # DFS for cycle detection
        visited: set[str] = set()
        rec_stack: set[str] = set()
        path: list[str] = []

        def dfs(node: str) -> Optional[list[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    result = dfs(neighbor)
                    if result:
                        return result
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]

            path.pop()
            rec_stack.remove(node)
            return None

        for step_id in graph:
            if step_id not in visited:
                cycle = dfs(step_id)
                if cycle:
                    return cycle

        return None

    def _validate_input_bindings(
        self,
        plan: CompositionPlan,
    ) -> list[ValidationError]:
        """Validate all input bindings are satisfied."""
        errors: list[ValidationError] = []
        step_outputs = {s.step_id: s.output_name for s in plan.steps}

        for step in plan.steps:
            for binding in step.input_bindings:
                if binding.source == InputSource.PREVIOUS_STEP:
                    # Check that source step exists
                    parts = binding.source_reference.split(".")
                    if len(parts) >= 1:
                        source_step = parts[0]
                        if source_step not in step_outputs:
                            errors.append(ValidationError(
                                error_id=str(uuid.uuid4()),
                                error_type="INVALID_BINDING",
                                message=f"Input binding references non-existent step: {source_step}",
                                step_id=step.step_id,
                                field=binding.parameter_name,
                            ))

        return errors

    def _find_unreachable_steps(
        self,
        plan: CompositionPlan,
    ) -> list[str]:
        """Find steps that are unreachable from the entry point."""
        if not plan.steps:
            return []

        # Build reverse adjacency (what can reach what)
        reachable: set[str] = set()
        to_visit = [plan.entry_point]

        # Build forward adjacency
        forward: dict[str, list[str]] = {s.step_id: [] for s in plan.steps}
        for dep in plan.dependencies:
            if dep.from_step in forward:
                forward[dep.from_step].append(dep.to_step)

        # BFS from entry point
        while to_visit:
            current = to_visit.pop(0)
            if current in reachable:
                continue
            reachable.add(current)
            to_visit.extend(forward.get(current, []))

        # Find unreachable
        all_steps = {s.step_id for s in plan.steps}
        return list(all_steps - reachable)

    def _validate_timeouts(
        self,
        plan: CompositionPlan,
    ) -> list[ValidationWarning]:
        """Validate step timeouts are reasonable."""
        warnings: list[ValidationWarning] = []

        for step in plan.steps:
            if step.estimated_latency_ms and step.timeout_ms:
                if step.timeout_ms < step.estimated_latency_ms:
                    warnings.append(ValidationWarning(
                        warning_id=str(uuid.uuid4()),
                        warning_type="SHORT_TIMEOUT",
                        message=f"Timeout ({step.timeout_ms}ms) is less than estimated latency ({step.estimated_latency_ms}ms)",
                        step_id=step.step_id,
                        recommendation="Increase timeout to at least 2x estimated latency",
                    ))

        return warnings

    def _calculate_metrics(
        self,
        plan: CompositionPlan,
    ) -> OptimizationMetrics:
        """Calculate metrics for a plan."""
        parallel_count = sum(
            1 for s in plan.steps if s.execution_type == StepExecutionType.PARALLEL
        )

        # Calculate reliability
        reliabilities = []
        for step in plan.steps:
            if step.retry_policy:
                # Simple reliability model
                base_reliability = 0.95
                with_retries = 1 - (1 - base_reliability) ** (step.retry_policy.max_retries + 1)
                reliabilities.append(with_retries)
            else:
                reliabilities.append(0.95)

        overall_reliability = 1.0
        for r in reliabilities:
            overall_reliability *= r

        return OptimizationMetrics(
            total_latency_ms=plan.estimated_latency_ms,
            total_cost=plan.estimated_cost or 0.0,
            step_count=len(plan.steps),
            parallel_steps=parallel_count,
            risk_score=0.3,  # Placeholder
            reliability=overall_reliability,
        )

    def _deep_copy_plan(self, plan: CompositionPlan) -> CompositionPlan:
        """Create a deep copy of a plan."""
        # Simple copy - in production use copy.deepcopy
        import copy
        return copy.deepcopy(plan)

    def _optimize_latency(
        self,
        plan: CompositionPlan,
        aggressive: bool = True,
    ) -> list[PlanImprovement]:
        """Optimize plan for latency."""
        improvements: list[PlanImprovement] = []

        # Find steps that can be parallelized
        parallelizable = self._find_parallelizable_steps(plan)

        for step_ids in parallelizable:
            if len(step_ids) > 1:
                for step_id in step_ids:
                    step = next((s for s in plan.steps if s.step_id == step_id), None)
                    if step and step.execution_type == StepExecutionType.SEQUENTIAL:
                        step.execution_type = StepExecutionType.PARALLEL
                        improvements.append(PlanImprovement(
                            improvement_id=str(uuid.uuid4()),
                            improvement_type="PARALLELIZATION",
                            description=f"Parallelized step {step_id}",
                            affected_steps=[step_id],
                            metric_improved="latency",
                            improvement_amount="potential 50% reduction",
                        ))

        # Recalculate latency
        plan.estimated_latency_ms = self._calculate_parallel_latency(plan)

        return improvements

    def _optimize_cost(
        self,
        plan: CompositionPlan,
        aggressive: bool = True,
    ) -> list[PlanImprovement]:
        """Optimize plan for cost."""
        # Placeholder - would involve agent substitution
        return []

    def _optimize_reliability(
        self,
        plan: CompositionPlan,
    ) -> list[PlanImprovement]:
        """Optimize plan for reliability."""
        improvements: list[PlanImprovement] = []

        for step in plan.steps:
            if not step.retry_policy:
                step.retry_policy = StepRetryPolicy(
                    max_retries=3,
                    initial_delay_ms=1000,
                    max_delay_ms=10000,
                    backoff_multiplier=2.0,
                    retryable_errors=["TIMEOUT", "TEMPORARY_FAILURE"],
                )
                improvements.append(PlanImprovement(
                    improvement_id=str(uuid.uuid4()),
                    improvement_type="ADD_RETRY",
                    description=f"Added retry policy to step {step.step_id}",
                    affected_steps=[step.step_id],
                    metric_improved="reliability",
                    improvement_amount="~15% improvement",
                ))

        return improvements

    def _optimize_step_count(
        self,
        plan: CompositionPlan,
    ) -> list[PlanImprovement]:
        """Optimize plan by reducing step count."""
        # Placeholder - would merge compatible steps
        return []

    def _find_parallelizable_steps(
        self,
        plan: CompositionPlan,
    ) -> list[list[str]]:
        """Find groups of steps that can run in parallel."""
        return self._topological_sort_with_waves(plan)

    def _calculate_parallel_latency(
        self,
        plan: CompositionPlan,
    ) -> int:
        """Calculate latency considering parallel execution."""
        waves = self._topological_sort_with_waves(plan)
        total_latency = 0

        for wave in waves:
            # Wave latency is the max of steps in the wave
            wave_latency = 0
            for step_id in wave:
                step = next((s for s in plan.steps if s.step_id == step_id), None)
                if step and step.estimated_latency_ms:
                    wave_latency = max(wave_latency, step.estimated_latency_ms)
            total_latency += wave_latency

        return total_latency

    def _topological_sort_with_waves(
        self,
        plan: CompositionPlan,
    ) -> list[list[str]]:
        """Topologically sort steps into waves that can execute in parallel."""
        if not plan.steps:
            return []

        # Build in-degree map
        in_degree: dict[str, int] = {s.step_id: 0 for s in plan.steps}
        forward: dict[str, list[str]] = {s.step_id: [] for s in plan.steps}

        for dep in plan.dependencies:
            if dep.to_step in in_degree:
                in_degree[dep.to_step] += 1
            if dep.from_step in forward:
                forward[dep.from_step].append(dep.to_step)

        # Kahn's algorithm with waves
        waves: list[list[str]] = []
        current_wave = [s for s in in_degree if in_degree[s] == 0]

        while current_wave:
            waves.append(current_wave)
            next_wave: list[str] = []

            for step_id in current_wave:
                for neighbor in forward.get(step_id, []):
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_wave.append(neighbor)

            current_wave = next_wave

        return waves

    def _analyze_step_failures(
        self,
        step: CompositionStep,
    ) -> list[FailureMode]:
        """Analyze potential failure modes for a step."""
        failures: list[FailureMode] = []

        # Timeout failure
        failures.append(FailureMode(
            failure_id=str(uuid.uuid4()),
            step_id=step.step_id,
            failure_type="TIMEOUT",
            probability=0.05,
            severity=FailureSeverity.MAJOR,
            impact=f"Step {step.name} times out after {step.timeout_ms}ms",
            mitigation="Retry with exponential backoff",
        ))

        # Agent unavailable
        failures.append(FailureMode(
            failure_id=str(uuid.uuid4()),
            step_id=step.step_id,
            failure_type="AGENT_UNAVAILABLE",
            probability=0.02,
            severity=FailureSeverity.MAJOR,
            impact=f"Agent {step.agent_name} is unavailable",
            mitigation="Use alternative agent or retry later",
        ))

        # Invalid input
        failures.append(FailureMode(
            failure_id=str(uuid.uuid4()),
            step_id=step.step_id,
            failure_type="INVALID_INPUT",
            probability=0.03,
            severity=FailureSeverity.MINOR,
            impact="Input validation fails",
            mitigation="Validate input before execution",
        ))

        return failures

    def _find_critical_path(
        self,
        plan: CompositionPlan,
    ) -> list[str]:
        """Find the critical path through the plan."""
        # Simple implementation: longest path by latency
        if not plan.steps:
            return []

        # Build graph
        graph: dict[str, list[str]] = {s.step_id: [] for s in plan.steps}
        for dep in plan.dependencies:
            if dep.from_step in graph:
                graph[dep.from_step].append(dep.to_step)

        # Find longest path from entry to each exit
        latencies = {s.step_id: s.estimated_latency_ms or 0 for s in plan.steps}

        def longest_path(node: str, memo: dict) -> tuple[int, list[str]]:
            if node in memo:
                return memo[node]

            neighbors = graph.get(node, [])
            if not neighbors:
                return latencies[node], [node]

            best_length = 0
            best_path: list[str] = []

            for neighbor in neighbors:
                length, path = longest_path(neighbor, memo)
                if length > best_length:
                    best_length = length
                    best_path = path

            result = (latencies[node] + best_length, [node] + best_path)
            memo[node] = result
            return result

        memo: dict = {}
        _, critical = longest_path(plan.entry_point, memo)
        return critical

    def _find_single_points_of_failure(
        self,
        plan: CompositionPlan,
    ) -> list[str]:
        """Find steps that are single points of failure."""
        # Steps that all exit points depend on
        single_points: list[str] = []

        for step in plan.steps:
            # Check if this step is on all paths to exit
            # Simple heuristic: if step has no alternatives
            alternatives = [
                s for s in plan.steps
                if s.step_id != step.step_id and s.capability_name == step.capability_name
            ]
            if not alternatives:
                single_points.append(step.step_id)

        return single_points

    def _calculate_risk_score(
        self,
        failure_modes: list[FailureMode],
        critical_path: list[str],
        single_points: list[str],
    ) -> float:
        """Calculate overall risk score."""
        if not failure_modes:
            return 0.0

        # Weight by severity
        severity_weights = {
            FailureSeverity.CATASTROPHIC: 1.0,
            FailureSeverity.MAJOR: 0.7,
            FailureSeverity.MINOR: 0.3,
            FailureSeverity.NEGLIGIBLE: 0.1,
        }

        # Calculate weighted risk
        total_risk = sum(
            fm.probability * severity_weights[fm.severity]
            for fm in failure_modes
        )

        # Increase risk for critical path and single points
        critical_risk = len(set(critical_path) & set(single_points)) * 0.1

        return min(1.0, total_risk + critical_risk)

    def _generate_risk_recommendations(
        self,
        failure_modes: list[FailureMode],
        critical_path: list[str],
        single_points: list[str],
    ) -> list[str]:
        """Generate risk mitigation recommendations."""
        recommendations: list[str] = []

        if single_points:
            recommendations.append(
                f"Add fallback agents for single points of failure: {', '.join(single_points)}"
            )

        catastrophic = [
            fm for fm in failure_modes
            if fm.severity == FailureSeverity.CATASTROPHIC
        ]
        if catastrophic:
            recommendations.append(
                "Implement circuit breakers for catastrophic failure modes"
            )

        if len(critical_path) > 5:
            recommendations.append(
                "Consider parallelizing steps to reduce critical path length"
            )

        high_prob = [fm for fm in failure_modes if fm.probability > 0.1]
        if high_prob:
            recommendations.append(
                f"Review high-probability failures in: {', '.join(set(fm.step_id for fm in high_prob))}"
            )

        return recommendations
