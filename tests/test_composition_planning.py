"""
Tests for Composition Planning.

Issue #63 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.11)
"""

import pytest

from src.agent_negotiation.composition_planner import (
    # Enums
    InputSource,
    OptimizationGoal,
    PlanStatus,
    DependencyType,
    FailureSeverity,
    StepExecutionType,
    # Input binding types
    InputBinding,
    CompositionConstraint,
    # Step types
    StepRetryPolicy,
    StepCondition,
    CompositionStep,
    # Data flow types
    DataFlowEdge,
    StepDependency,
    # Failure types
    FailureMode,
    RiskAssessment,
    # Plan types
    PlanMetadata,
    CompositionPlan,
    # Available agent types
    AvailableCapability,
    AvailableAgent,
    # Request/response types
    PlanningPreferences,
    PlanningContext,
    PlanCompositionRequest,
    PlanCompositionResponse,
    # Optimization types
    OptimizationMetrics,
    PlanImprovement,
    OptimizePlanResponse,
    # Validation types
    ValidationError,
    ValidationWarning,
    PlanValidationResult,
    # Planner
    CompositionPlanner,
)


# ============================================
# Test Fixtures
# ============================================


@pytest.fixture
def planner():
    """Create a CompositionPlanner instance."""
    return CompositionPlanner()


@pytest.fixture
def sample_capability_data_processing():
    """Create a sample data processing capability."""
    return AvailableCapability(
        capability_name="data_processing",
        capability_version="1.0",
        description="Process and transform data",
        input_schema='{"type": "object", "properties": {"data": {"type": "string"}}}',
        output_schema='{"type": "object", "properties": {"result": {"type": "string"}}}',
        estimated_latency_ms=500,
        reliability=0.95,
        estimated_cost=0.01,
    )


@pytest.fixture
def sample_capability_analytics():
    """Create a sample analytics capability."""
    return AvailableCapability(
        capability_name="analytics",
        capability_version="1.0",
        description="Analyze data and generate insights",
        input_schema='{"type": "object", "properties": {"data": {"type": "object"}}}',
        output_schema='{"type": "object", "properties": {"insights": {"type": "array"}}}',
        estimated_latency_ms=1000,
        reliability=0.90,
        estimated_cost=0.05,
    )


@pytest.fixture
def sample_capability_storage():
    """Create a sample storage capability."""
    return AvailableCapability(
        capability_name="storage",
        capability_version="1.0",
        description="Store data persistently",
        input_schema='{"type": "object", "properties": {"data": {"type": "object"}}}',
        output_schema='{"type": "object", "properties": {"id": {"type": "string"}}}',
        estimated_latency_ms=200,
        reliability=0.99,
        estimated_cost=0.001,
    )


@pytest.fixture
def sample_agent_processor(sample_capability_data_processing):
    """Create a sample data processor agent."""
    return AvailableAgent(
        agent_id="agent-processor",
        agent_name="Data Processor",
        capabilities=[sample_capability_data_processing],
        trust_score=0.9,
        availability=0.95,
    )


@pytest.fixture
def sample_agent_analyst(sample_capability_analytics):
    """Create a sample analyst agent."""
    return AvailableAgent(
        agent_id="agent-analyst",
        agent_name="Data Analyst",
        capabilities=[sample_capability_analytics],
        trust_score=0.85,
        availability=0.90,
    )


@pytest.fixture
def sample_agent_storage(sample_capability_storage):
    """Create a sample storage agent."""
    return AvailableAgent(
        agent_id="agent-storage",
        agent_name="Storage Service",
        capabilities=[sample_capability_storage],
        trust_score=0.95,
        availability=0.99,
    )


@pytest.fixture
def sample_agents(sample_agent_processor, sample_agent_analyst, sample_agent_storage):
    """Create a list of sample agents."""
    return [sample_agent_processor, sample_agent_analyst, sample_agent_storage]


@pytest.fixture
def sample_plan_request(sample_agents):
    """Create a sample plan composition request."""
    return PlanCompositionRequest(
        request_id="req-001",
        goal="Process data, analyze it for insights, and store the results",
        available_agents=sample_agents,
        constraints=[
            CompositionConstraint(
                constraint_id="c-001",
                constraint_type="latency",
                operator="<",
                value="5000",
                priority=1,
                hard=True,
            ),
        ],
        preferences=PlanningPreferences(
            prefer_parallel=True,
            prefer_fewer_agents=False,
            prefer_trusted_agents=True,
        ),
    )


# ============================================
# Enum Tests
# ============================================


class TestEnums:
    """Tests for composition planning enums."""

    def test_input_source_values(self):
        """Test InputSource enum values."""
        assert InputSource.LITERAL.value == "literal"
        assert InputSource.PREVIOUS_STEP.value == "previous_step"
        assert InputSource.USER_INPUT.value == "user_input"
        assert InputSource.CONTEXT.value == "context"
        assert InputSource.COMPUTED.value == "computed"

    def test_optimization_goal_values(self):
        """Test OptimizationGoal enum values."""
        assert OptimizationGoal.MINIMIZE_LATENCY.value == "minimize_latency"
        assert OptimizationGoal.MINIMIZE_COST.value == "minimize_cost"
        assert OptimizationGoal.MAXIMIZE_RELIABILITY.value == "maximize_reliability"
        assert OptimizationGoal.BALANCE.value == "balance"

    def test_plan_status_values(self):
        """Test PlanStatus enum values."""
        assert PlanStatus.DRAFT.value == "draft"
        assert PlanStatus.VALIDATED.value == "validated"
        assert PlanStatus.OPTIMIZED.value == "optimized"
        assert PlanStatus.READY.value == "ready"
        assert PlanStatus.EXECUTING.value == "executing"
        assert PlanStatus.COMPLETED.value == "completed"
        assert PlanStatus.FAILED.value == "failed"

    def test_dependency_type_values(self):
        """Test DependencyType enum values."""
        assert DependencyType.DATA.value == "data"
        assert DependencyType.CONTROL.value == "control"
        assert DependencyType.RESOURCE.value == "resource"
        assert DependencyType.ORDERING.value == "ordering"

    def test_failure_severity_values(self):
        """Test FailureSeverity enum values."""
        assert FailureSeverity.CATASTROPHIC.value == "catastrophic"
        assert FailureSeverity.MAJOR.value == "major"
        assert FailureSeverity.MINOR.value == "minor"
        assert FailureSeverity.NEGLIGIBLE.value == "negligible"

    def test_step_execution_type_values(self):
        """Test StepExecutionType enum values."""
        assert StepExecutionType.SEQUENTIAL.value == "sequential"
        assert StepExecutionType.PARALLEL.value == "parallel"
        assert StepExecutionType.CONDITIONAL.value == "conditional"
        assert StepExecutionType.LOOP.value == "loop"


# ============================================
# Type Tests
# ============================================


class TestInputBinding:
    """Tests for InputBinding type."""

    def test_input_binding_creation(self):
        """Test InputBinding creation."""
        binding = InputBinding(
            parameter_name="data",
            source=InputSource.PREVIOUS_STEP,
            source_reference="step_1.output",
            required=True,
        )
        assert binding.parameter_name == "data"
        assert binding.source == InputSource.PREVIOUS_STEP
        assert binding.required is True

    def test_input_binding_with_defaults(self):
        """Test InputBinding with optional fields."""
        binding = InputBinding(
            parameter_name="data",
            source=InputSource.LITERAL,
            source_reference="default_value",
            transformation="uppercase",
            default_value="fallback",
            required=False,
        )
        assert binding.transformation == "uppercase"
        assert binding.default_value == "fallback"


class TestCompositionStep:
    """Tests for CompositionStep type."""

    def test_composition_step_creation(self):
        """Test CompositionStep creation."""
        step = CompositionStep(
            step_id="step_1",
            name="Process Data",
            agent_id="agent-001",
            agent_name="Data Processor",
            capability_name="data_processing",
            input_bindings=[],
            output_name="step_1_output",
            execution_type=StepExecutionType.SEQUENTIAL,
            timeout_ms=5000,
        )
        assert step.step_id == "step_1"
        assert step.name == "Process Data"
        assert step.execution_type == StepExecutionType.SEQUENTIAL

    def test_composition_step_with_retry_policy(self):
        """Test CompositionStep with retry policy."""
        step = CompositionStep(
            step_id="step_1",
            name="Reliable Step",
            agent_id="agent-001",
            agent_name="Agent",
            capability_name="capability",
            input_bindings=[],
            output_name="output",
            execution_type=StepExecutionType.SEQUENTIAL,
            timeout_ms=5000,
            retry_policy=StepRetryPolicy(
                max_retries=3,
                initial_delay_ms=1000,
                max_delay_ms=10000,
                backoff_multiplier=2.0,
                retryable_errors=["TIMEOUT"],
            ),
        )
        assert step.retry_policy is not None
        assert step.retry_policy.max_retries == 3


class TestDataFlowEdge:
    """Tests for DataFlowEdge type."""

    def test_data_flow_edge_creation(self):
        """Test DataFlowEdge creation."""
        edge = DataFlowEdge(
            edge_id="edge-001",
            from_step="step_1",
            from_output="output",
            to_step="step_2",
            to_input="input",
        )
        assert edge.from_step == "step_1"
        assert edge.to_step == "step_2"


class TestCompositionPlan:
    """Tests for CompositionPlan type."""

    def test_composition_plan_creation(self):
        """Test CompositionPlan creation."""
        plan = CompositionPlan(
            plan_id="plan-001",
            version="1.0",
            goal="Process and analyze data",
            status=PlanStatus.DRAFT,
            steps=[],
            data_flow=[],
            dependencies=[],
            entry_point="step_1",
            exit_points=["step_3"],
            estimated_latency_ms=1500,
        )
        assert plan.plan_id == "plan-001"
        assert plan.status == PlanStatus.DRAFT


# ============================================
# CompositionPlanner Tests
# ============================================


class TestCompositionPlannerInit:
    """Tests for CompositionPlanner initialization."""

    def test_default_initialization(self):
        """Test default planner initialization."""
        planner = CompositionPlanner()
        assert planner._plan_cache == {}


class TestPlanComposition:
    """Tests for plan composition."""

    def test_basic_plan_composition(self, planner, sample_plan_request):
        """Test basic plan composition."""
        response = planner.plan(sample_plan_request)

        assert response.request_id == sample_plan_request.request_id
        assert response.plan is not None
        assert response.plan.plan_id is not None
        assert response.plan.goal == sample_plan_request.goal
        assert response.plan.status == PlanStatus.DRAFT

    def test_plan_has_steps(self, planner, sample_plan_request):
        """Test that generated plan has steps."""
        response = planner.plan(sample_plan_request)

        assert len(response.plan.steps) > 0

    def test_plan_has_entry_and_exit_points(self, planner, sample_plan_request):
        """Test that plan has entry and exit points."""
        response = planner.plan(sample_plan_request)

        assert response.plan.entry_point is not None
        assert len(response.plan.exit_points) > 0

    def test_plan_has_estimated_latency(self, planner, sample_plan_request):
        """Test that plan has estimated latency."""
        response = planner.plan(sample_plan_request)

        assert response.plan.estimated_latency_ms > 0

    def test_plan_is_cached(self, planner, sample_plan_request):
        """Test that plan is cached."""
        response = planner.plan(sample_plan_request)

        cached = planner.get_plan(response.plan.plan_id)
        assert cached is not None
        assert cached.plan_id == response.plan.plan_id

    def test_plan_has_dependencies(self, planner, sample_plan_request):
        """Test that plan has dependencies between steps."""
        response = planner.plan(sample_plan_request)

        if len(response.plan.steps) > 1:
            assert len(response.plan.dependencies) > 0

    def test_plan_has_data_flow(self, planner, sample_plan_request):
        """Test that plan has data flow edges."""
        response = planner.plan(sample_plan_request)

        if len(response.plan.steps) > 1:
            assert len(response.plan.data_flow) > 0

    def test_planning_notes_generated(self, planner, sample_plan_request):
        """Test that planning notes are generated."""
        response = planner.plan(sample_plan_request)

        assert len(response.planning_notes) > 0

    def test_generation_time_recorded(self, planner, sample_plan_request):
        """Test that generation time is recorded."""
        response = planner.plan(sample_plan_request)

        assert response.generation_time_ms >= 0


class TestGoalAnalysis:
    """Tests for goal analysis."""

    def test_analyze_processing_goal(self, planner):
        """Test analyzing processing-related goals."""
        capabilities = planner._analyze_goal("Process the data")
        assert "data_processing" in capabilities

    def test_analyze_analysis_goal(self, planner):
        """Test analyzing analysis-related goals."""
        capabilities = planner._analyze_goal("Analyze user behavior")
        assert "analytics" in capabilities

    def test_analyze_storage_goal(self, planner):
        """Test analyzing storage-related goals."""
        capabilities = planner._analyze_goal("Store the results")
        assert "storage" in capabilities

    def test_analyze_complex_goal(self, planner):
        """Test analyzing complex multi-capability goals."""
        capabilities = planner._analyze_goal(
            "Process data, analyze for insights, and store results"
        )
        assert "data_processing" in capabilities
        assert "analytics" in capabilities
        assert "storage" in capabilities

    def test_analyze_unknown_goal(self, planner):
        """Test analyzing unknown goals."""
        capabilities = planner._analyze_goal("Do something undefined")
        assert "general_processing" in capabilities


class TestPlanValidation:
    """Tests for plan validation."""

    def test_validate_valid_plan(self, planner, sample_plan_request):
        """Test validating a valid plan."""
        response = planner.plan(sample_plan_request)
        validation = planner.validate(response.plan)

        assert validation.valid is True
        assert len(validation.errors) == 0

    def test_validate_detects_circular_dependency(self, planner):
        """Test that validation detects circular dependencies."""
        # Create a plan with circular dependency
        plan = CompositionPlan(
            plan_id="plan-circular",
            version="1.0",
            goal="Test",
            status=PlanStatus.DRAFT,
            steps=[
                CompositionStep(
                    step_id="step_1",
                    name="Step 1",
                    agent_id="agent-1",
                    agent_name="Agent 1",
                    capability_name="cap1",
                    input_bindings=[],
                    output_name="out1",
                    execution_type=StepExecutionType.SEQUENTIAL,
                    timeout_ms=1000,
                ),
                CompositionStep(
                    step_id="step_2",
                    name="Step 2",
                    agent_id="agent-2",
                    agent_name="Agent 2",
                    capability_name="cap2",
                    input_bindings=[],
                    output_name="out2",
                    execution_type=StepExecutionType.SEQUENTIAL,
                    timeout_ms=1000,
                ),
            ],
            data_flow=[],
            dependencies=[
                StepDependency(
                    dependency_id="dep-1",
                    from_step="step_1",
                    to_step="step_2",
                    dependency_type=DependencyType.DATA,
                    required=True,
                ),
                StepDependency(
                    dependency_id="dep-2",
                    from_step="step_2",
                    to_step="step_1",
                    dependency_type=DependencyType.DATA,
                    required=True,
                ),
            ],
            entry_point="step_1",
            exit_points=["step_2"],
            estimated_latency_ms=2000,
        )

        validation = planner.validate(plan)

        assert validation.valid is False
        assert any(e.error_type == "CIRCULAR_DEPENDENCY" for e in validation.errors)

    def test_validate_detects_missing_exit_point(self, planner):
        """Test that validation detects missing exit points."""
        plan = CompositionPlan(
            plan_id="plan-no-exit",
            version="1.0",
            goal="Test",
            status=PlanStatus.DRAFT,
            steps=[
                CompositionStep(
                    step_id="step_1",
                    name="Step 1",
                    agent_id="agent-1",
                    agent_name="Agent 1",
                    capability_name="cap1",
                    input_bindings=[],
                    output_name="out1",
                    execution_type=StepExecutionType.SEQUENTIAL,
                    timeout_ms=1000,
                ),
            ],
            data_flow=[],
            dependencies=[],
            entry_point="step_1",
            exit_points=[],  # No exit points
            estimated_latency_ms=1000,
        )

        validation = planner.validate(plan)

        assert validation.valid is False
        assert any(e.error_type == "NO_EXIT_POINT" for e in validation.errors)

    def test_validate_generates_suggestions(self, planner, sample_plan_request):
        """Test that validation generates suggestions."""
        response = planner.plan(sample_plan_request)
        validation = planner.validate(response.plan)

        assert isinstance(validation.suggestions, list)


class TestPlanOptimization:
    """Tests for plan optimization."""

    def test_optimize_for_latency(self, planner, sample_plan_request):
        """Test optimizing plan for latency."""
        response = planner.plan(sample_plan_request)
        optimized = planner.optimize(
            response.plan,
            [OptimizationGoal.MINIMIZE_LATENCY],
        )

        assert optimized.optimized_plan is not None
        assert optimized.optimized_plan.status == PlanStatus.OPTIMIZED

    def test_optimize_for_reliability(self, planner, sample_plan_request):
        """Test optimizing plan for reliability."""
        response = planner.plan(sample_plan_request)
        optimized = planner.optimize(
            response.plan,
            [OptimizationGoal.MAXIMIZE_RELIABILITY],
        )

        assert optimized.optimized_plan is not None

    def test_optimize_balanced(self, planner, sample_plan_request):
        """Test balanced optimization."""
        response = planner.plan(sample_plan_request)
        optimized = planner.optimize(
            response.plan,
            [OptimizationGoal.BALANCE],
        )

        assert optimized.optimized_plan is not None

    def test_optimization_tracks_improvements(self, planner, sample_plan_request):
        """Test that optimization tracks improvements."""
        response = planner.plan(sample_plan_request)
        optimized = planner.optimize(
            response.plan,
            [OptimizationGoal.MAXIMIZE_RELIABILITY],
        )

        assert isinstance(optimized.improvements, list)

    def test_optimization_calculates_metrics(self, planner, sample_plan_request):
        """Test that optimization calculates before/after metrics."""
        response = planner.plan(sample_plan_request)
        optimized = planner.optimize(
            response.plan,
            [OptimizationGoal.MINIMIZE_LATENCY],
        )

        assert optimized.metrics_before is not None
        assert optimized.metrics_after is not None
        assert isinstance(optimized.metrics_before.total_latency_ms, int)


class TestRiskAnalysis:
    """Tests for risk analysis."""

    def test_analyze_risks(self, planner, sample_plan_request):
        """Test risk analysis."""
        response = planner.plan(sample_plan_request)
        risk = planner.analyze_risks(response.plan)

        assert risk is not None
        assert 0.0 <= risk.overall_risk_score <= 1.0

    def test_risk_identifies_failure_modes(self, planner, sample_plan_request):
        """Test that risk analysis identifies failure modes."""
        response = planner.plan(sample_plan_request)
        risk = planner.analyze_risks(response.plan)

        assert len(risk.failure_modes) > 0

    def test_risk_finds_critical_path(self, planner, sample_plan_request):
        """Test that risk analysis finds critical path."""
        response = planner.plan(sample_plan_request)
        risk = planner.analyze_risks(response.plan)

        assert isinstance(risk.critical_path, list)

    def test_risk_identifies_single_points_of_failure(self, planner, sample_plan_request):
        """Test that risk analysis identifies single points of failure."""
        response = planner.plan(sample_plan_request)
        risk = planner.analyze_risks(response.plan)

        assert isinstance(risk.single_points_of_failure, list)

    def test_risk_generates_recommendations(self, planner, sample_plan_request):
        """Test that risk analysis generates recommendations."""
        response = planner.plan(sample_plan_request)
        risk = planner.analyze_risks(response.plan)

        assert isinstance(risk.recommendations, list)


class TestExecutionOrder:
    """Tests for execution order calculation."""

    def test_get_execution_order(self, planner, sample_plan_request):
        """Test getting execution order."""
        response = planner.plan(sample_plan_request)
        order = planner.get_execution_order(response.plan)

        assert isinstance(order, list)
        assert len(order) > 0

    def test_execution_order_contains_all_steps(self, planner, sample_plan_request):
        """Test that execution order contains all steps."""
        response = planner.plan(sample_plan_request)
        order = planner.get_execution_order(response.plan)

        all_step_ids = {s.step_id for s in response.plan.steps}
        order_step_ids = {step_id for wave in order for step_id in wave}

        assert all_step_ids == order_step_ids

    def test_execution_order_respects_dependencies(self, planner, sample_plan_request):
        """Test that execution order respects dependencies."""
        response = planner.plan(sample_plan_request)
        order = planner.get_execution_order(response.plan)

        # Build wave index for each step
        wave_index = {}
        for i, wave in enumerate(order):
            for step_id in wave:
                wave_index[step_id] = i

        # Check all dependencies are satisfied
        for dep in response.plan.dependencies:
            if dep.from_step in wave_index and dep.to_step in wave_index:
                assert wave_index[dep.from_step] < wave_index[dep.to_step]


class TestCapabilityMatching:
    """Tests for capability matching."""

    def test_capability_matches_exact(self, planner):
        """Test exact capability matching."""
        assert planner._capability_matches("data_processing", "data_processing")

    def test_capability_matches_partial(self, planner):
        """Test partial capability matching."""
        assert planner._capability_matches("data_processing", "process")
        assert planner._capability_matches("analytics_service", "analytics")

    def test_capability_matches_synonyms(self, planner):
        """Test capability matching with synonyms."""
        assert planner._capability_matches("transform_data", "data_processing")
        assert planner._capability_matches("analysis", "analytics")


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_agents_list(self, planner):
        """Test planning with empty agents list."""
        request = PlanCompositionRequest(
            request_id="req-empty",
            goal="Do something",
            available_agents=[],
            constraints=[],
        )

        response = planner.plan(request)

        # Should still create a plan, but with no steps
        assert response.plan is not None

    def test_plan_with_single_step(self, planner, sample_agent_processor):
        """Test planning with a single-step goal."""
        request = PlanCompositionRequest(
            request_id="req-single",
            goal="Process data",
            available_agents=[sample_agent_processor],
            constraints=[],
        )

        response = planner.plan(request)

        assert len(response.plan.steps) >= 1
        assert response.plan.entry_point == response.plan.exit_points[0]

    def test_get_nonexistent_plan(self, planner):
        """Test getting a non-existent plan."""
        result = planner.get_plan("nonexistent-plan-id")
        assert result is None


class TestModuleExports:
    """Tests for module exports."""

    def test_exports_from_package(self):
        """Test that all types are exported from the package."""
        from src.agent_negotiation import (
            InputSource,
            OptimizationGoal,
            PlanStatus,
            CompositionStep,
            CompositionPlan,
            CompositionPlanner,
        )

        assert InputSource.LITERAL is not None
        assert OptimizationGoal.MINIMIZE_LATENCY is not None
        assert PlanStatus.READY is not None


class TestStepRetryPolicy:
    """Tests for StepRetryPolicy."""

    def test_retry_policy_creation(self):
        """Test StepRetryPolicy creation."""
        policy = StepRetryPolicy(
            max_retries=3,
            initial_delay_ms=1000,
            max_delay_ms=30000,
            backoff_multiplier=2.0,
            retryable_errors=["TIMEOUT", "NETWORK_ERROR"],
        )
        assert policy.max_retries == 3
        assert policy.backoff_multiplier == 2.0
        assert len(policy.retryable_errors) == 2


class TestAvailableAgent:
    """Tests for AvailableAgent type."""

    def test_available_agent_creation(self, sample_capability_data_processing):
        """Test AvailableAgent creation."""
        agent = AvailableAgent(
            agent_id="agent-001",
            agent_name="Test Agent",
            capabilities=[sample_capability_data_processing],
            trust_score=0.9,
            availability=0.95,
        )
        assert agent.agent_id == "agent-001"
        assert len(agent.capabilities) == 1
        assert agent.trust_score == 0.9


class TestPlanningPreferences:
    """Tests for PlanningPreferences."""

    def test_default_preferences(self):
        """Test default planning preferences."""
        prefs = PlanningPreferences()
        assert prefs.prefer_parallel is True
        assert prefs.prefer_fewer_agents is False
        assert prefs.prefer_trusted_agents is True

    def test_custom_preferences(self):
        """Test custom planning preferences."""
        prefs = PlanningPreferences(
            prefer_parallel=False,
            prefer_fewer_agents=True,
            max_steps=10,
            max_depth=5,
        )
        assert prefs.prefer_parallel is False
        assert prefs.max_steps == 10


class TestFailureMode:
    """Tests for FailureMode type."""

    def test_failure_mode_creation(self):
        """Test FailureMode creation."""
        failure = FailureMode(
            failure_id="fail-001",
            step_id="step_1",
            failure_type="TIMEOUT",
            probability=0.05,
            severity=FailureSeverity.MAJOR,
            impact="Step fails to complete",
            mitigation="Retry with exponential backoff",
        )
        assert failure.failure_id == "fail-001"
        assert failure.severity == FailureSeverity.MAJOR
        assert failure.probability == 0.05
