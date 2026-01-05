// Composition Planning Types
// Planning and orchestrating multi-agent capability compositions
// Issue #63 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.11)

// Dependencies:
// - AgentCard, AgentCapability from agent_capability.baml
// - RetryPolicy from agent_card.baml

// ============================================
// Input Source Enums
// ============================================

/// Source of input data for a composition step
enum InputSource {
  LITERAL @description("Hardcoded value provided in the plan")
  PREVIOUS_STEP @description("Output from an earlier step in the composition")
  USER_INPUT @description("From the original user request")
  CONTEXT @description("From session or execution context")
  COMPUTED @description("Computed at runtime from multiple sources")
}

/// Type of optimization goal
enum OptimizationGoal {
  MINIMIZE_LATENCY @description("Reduce total execution time")
  MINIMIZE_COST @description("Reduce resource/monetary cost")
  MAXIMIZE_RELIABILITY @description("Increase success probability")
  MAXIMIZE_QUALITY @description("Improve output quality")
  MINIMIZE_STEPS @description("Reduce number of steps")
  BALANCE @description("Balance all factors")
}

/// Status of a composition plan
enum PlanStatus {
  DRAFT @description("Plan is being constructed")
  VALIDATED @description("Plan has been validated")
  OPTIMIZED @description("Plan has been optimized")
  READY @description("Plan is ready for execution")
  EXECUTING @description("Plan is currently executing")
  COMPLETED @description("Plan execution completed")
  FAILED @description("Plan execution failed")
}

/// Type of step dependency
enum DependencyType {
  DATA @description("Data dependency - needs output from previous step")
  CONTROL @description("Control dependency - must wait for completion")
  RESOURCE @description("Resource dependency - needs shared resource")
  ORDERING @description("Pure ordering constraint")
}

/// Severity of a failure mode
enum FailureSeverity {
  CATASTROPHIC @description("Entire composition fails")
  MAJOR @description("Significant degradation")
  MINOR @description("Recoverable with degraded output")
  NEGLIGIBLE @description("Minimal impact")
}

/// Type of step execution
enum StepExecutionType {
  SEQUENTIAL @description("Must wait for previous steps")
  PARALLEL @description("Can run in parallel with other steps")
  CONDITIONAL @description("Execution depends on condition")
  LOOP @description("May execute multiple times")
}

// ============================================
// Input Binding Types
// ============================================

/// Binding for a step input parameter
class InputBinding {
  parameter_name string @description("Name of the parameter to bind")
  source InputSource @description("Source of the input value")
  source_reference string @description("Reference to the source (step_id.output_name, literal value, etc.)")
  transformation string? @description("Optional transformation to apply")
  default_value string? @description("Default value if source is unavailable")
  required bool @description("Whether this binding is required")
}

/// Constraint on composition
class CompositionConstraint {
  constraint_id string @description("Unique constraint identifier")
  constraint_type string @description("Type of constraint (latency, cost, agent, etc.)")
  operator string @description("Comparison operator")
  value string @description("Constraint value")
  priority int @description("Priority (1 = highest)")
  hard bool @description("Whether this is a hard or soft constraint")
}

// ============================================
// Composition Step Types
// ============================================

/// A single step in a composition plan
class CompositionStep {
  step_id string @description("Unique identifier for this step")
  name string @description("Human-readable step name")
  description string? @description("Description of what this step does")
  agent_id string @description("ID of the agent executing this step")
  agent_name string @description("Name of the agent")
  capability_name string @description("Name of the capability to invoke")
  capability_version string? @description("Version of the capability")
  input_bindings InputBinding[] @description("Input parameter bindings")
  output_name string @description("Name for this step's output")
  output_schema string? @description("Expected output schema")
  execution_type StepExecutionType @description("How this step executes")
  timeout_ms int @description("Timeout in milliseconds")
  retry_policy StepRetryPolicy? @description("Retry policy for failures")
  conditions StepCondition[]? @description("Conditions for execution")
  estimated_latency_ms int? @description("Estimated execution time")
  estimated_cost float? @description("Estimated cost")
}

/// Retry policy for a step
class StepRetryPolicy {
  max_retries int @description("Maximum retry attempts")
  initial_delay_ms int @description("Initial delay between retries")
  max_delay_ms int @description("Maximum delay between retries")
  backoff_multiplier float @description("Multiplier for exponential backoff")
  retryable_errors string[] @description("Error types that trigger retry")
}

/// Condition for step execution
class StepCondition {
  condition_id string @description("Unique condition identifier")
  source_step string @description("Step whose output to check")
  field_path string @description("JSONPath to field to check")
  operator string @description("Comparison operator")
  value string @description("Value to compare against")
}

// ============================================
// Data Flow Types
// ============================================

/// Edge in the data flow graph
class DataFlowEdge {
  edge_id string @description("Unique edge identifier")
  from_step string @description("Source step ID")
  from_output string @description("Output field from source")
  to_step string @description("Target step ID")
  to_input string @description("Input parameter on target")
  transformation string? @description("Transformation to apply")
  data_type string? @description("Expected data type")
}

/// Dependency between steps
class StepDependency {
  dependency_id string @description("Unique dependency identifier")
  from_step string @description("Step that must complete first")
  to_step string @description("Step that depends on the other")
  dependency_type DependencyType @description("Type of dependency")
  required bool @description("Whether dependency is required")
}

// ============================================
// Failure Mode Types
// ============================================

/// Identified failure mode in a composition
class FailureMode {
  failure_id string @description("Unique failure identifier")
  step_id string @description("Step where failure can occur")
  failure_type string @description("Type of failure")
  probability float @description("Estimated probability (0.0-1.0)")
  severity FailureSeverity @description("Impact severity")
  impact string @description("Description of impact")
  mitigation string @description("Mitigation strategy")
  fallback_step string? @description("Alternative step to execute")
}

/// Risk assessment for a composition
class RiskAssessmentForComposition {
  overall_risk_score float @description("Overall risk score (0.0-1.0)")
  failure_modes FailureMode[] @description("Identified failure modes")
  critical_path string[] @description("Steps on the critical path")
  single_points_of_failure string[] @description("Steps with no fallback")
  recommendations string[] @description("Risk mitigation recommendations")
}

// ============================================
// Composition Plan Types
// ============================================

/// Complete composition plan
class CompositionPlan {
  plan_id string @description("Unique plan identifier")
  version string @description("Plan version")
  goal string @description("High-level goal description")
  status PlanStatus @description("Current plan status")
  steps CompositionStep[] @description("Ordered list of steps")
  data_flow DataFlowEdge[] @description("Data flow graph")
  dependencies StepDependency[] @description("Step dependencies")
  entry_point string @description("First step to execute")
  exit_points string[] @description("Final output steps")
  estimated_latency_ms int @description("Total estimated latency")
  estimated_cost float? @description("Total estimated cost")
  risk_assessment RiskAssessmentForComposition? @description("Risk analysis")
  metadata PlanMetadataForComposition? @description("Additional metadata")
}

/// Metadata for a composition plan
class PlanMetadataForComposition {
  created_at string @description("ISO 8601 creation timestamp")
  created_by string? @description("Creator identifier")
  last_modified string? @description("Last modification timestamp")
  tags string[]? @description("Tags for categorization")
  notes string? @description("Additional notes")
}

// ============================================
// Planning Request/Response Types
// ============================================

/// Request to create a composition plan
class PlanCompositionRequest {
  request_id string @description("Unique request identifier")
  goal string @description("Goal to achieve")
  available_agents AvailableAgent[] @description("Agents available for composition")
  constraints CompositionConstraint[] @description("Constraints to satisfy")
  preferences PlanningPreferences? @description("Planning preferences")
  context PlanningContext? @description("Additional context")
}

/// Available agent for composition
class AvailableAgent {
  agent_id string @description("Agent identifier")
  agent_name string @description("Agent name")
  capabilities AvailableCapability[] @description("Capabilities offered")
  trust_score float @description("Trust score (0.0-1.0)")
  availability float @description("Availability (0.0-1.0)")
}

/// Available capability from an agent
class AvailableCapability {
  capability_name string @description("Capability name")
  capability_version string @description("Capability version")
  description string @description("What the capability does")
  input_schema string @description("Input schema as JSON")
  output_schema string @description("Output schema as JSON")
  estimated_latency_ms int @description("Estimated latency")
  estimated_cost float? @description("Estimated cost per call")
  reliability float @description("Historical reliability (0.0-1.0)")
}

/// Preferences for plan generation
class PlanningPreferences {
  prefer_parallel bool @description("Prefer parallel execution")
  prefer_fewer_agents bool @description("Prefer using fewer agents")
  prefer_trusted_agents bool @description("Prefer agents with higher trust")
  max_steps int? @description("Maximum number of steps")
  max_depth int? @description("Maximum plan depth")
}

/// Context for planning
class PlanningContext {
  session_id string? @description("Session identifier")
  user_id string? @description("User identifier")
  previous_plans string[]? @description("IDs of related previous plans")
  domain_hints string[]? @description("Domain-specific hints")
}

/// Response from plan composition
class PlanCompositionResponse {
  request_id string @description("Original request ID")
  plan CompositionPlan @description("Generated composition plan")
  alternatives CompositionPlan[]? @description("Alternative plans")
  planning_notes string[] @description("Notes about planning decisions")
  generation_time_ms int @description("Time to generate plan")
}

// ============================================
// Optimization Types
// ============================================

/// Request to optimize a plan
class OptimizePlanRequest {
  request_id string @description("Unique request identifier")
  plan CompositionPlan @description("Plan to optimize")
  optimization_goals OptimizationGoal[] @description("Goals for optimization")
  constraints CompositionConstraint[]? @description("Additional constraints")
}

/// Result of plan optimization
class OptimizePlanResponse {
  request_id string @description("Original request ID")
  original_plan CompositionPlan @description("Original plan")
  optimized_plan CompositionPlan @description("Optimized plan")
  improvements PlanImprovement[] @description("Improvements made")
  metrics_before OptimizationMetrics @description("Metrics before optimization")
  metrics_after OptimizationMetrics @description("Metrics after optimization")
}

/// Improvement made during optimization
class PlanImprovement {
  improvement_id string @description("Unique improvement identifier")
  improvement_type string @description("Type of improvement")
  description string @description("Description of change")
  affected_steps string[] @description("Steps affected")
  metric_improved string @description("Which metric improved")
  improvement_amount string @description("Amount of improvement")
}

/// Metrics for optimization comparison
class OptimizationMetrics {
  total_latency_ms int @description("Total estimated latency")
  total_cost float @description("Total estimated cost")
  step_count int @description("Number of steps")
  parallel_steps int @description("Steps that can run in parallel")
  risk_score float @description("Overall risk score")
  reliability float @description("Estimated reliability")
}

// ============================================
// Validation Types
// ============================================

/// Result of plan validation
class PlanValidation {
  valid bool @description("Whether plan is valid")
  errors ValidationError[] @description("Validation errors")
  warnings ValidationWarning[] @description("Validation warnings")
  suggestions string[] @description("Improvement suggestions")
}

/// Validation error
class ValidationError {
  error_id string @description("Unique error identifier")
  error_type string @description("Type of error")
  message string @description("Error message")
  step_id string? @description("Affected step if applicable")
  field string? @description("Affected field if applicable")
}

/// Validation warning
class ValidationWarning {
  warning_id string @description("Unique warning identifier")
  warning_type string @description("Type of warning")
  message string @description("Warning message")
  step_id string? @description("Affected step if applicable")
  recommendation string? @description("Recommended action")
}

// ============================================
// AI Functions
// ============================================

/// Plan a composition to achieve a goal
function PlanComposition(
  goal: string,
  available_agents: string,
  constraints: string?
) -> CompositionPlan {
  client CustomSonnet4
  prompt #"
    Create a composition plan to achieve the specified goal using the available agents.

    Goal:
    {{ goal }}

    Available Agents and Capabilities:
    {{ available_agents }}

    {% if constraints %}
    Constraints:
    {{ constraints }}
    {% endif %}

    Planning Steps:
    1. Analyze the goal and identify required capabilities
    2. Match capabilities to available agents
    3. Order steps based on data dependencies
    4. Connect outputs to inputs via data flow
    5. Identify potential failure modes
    6. Estimate latency and cost

    Ensure:
    - No circular dependencies
    - All required inputs are satisfied
    - Failure modes have mitigations
    - Plan is executable end-to-end

    {{ ctx.output_format }}
  "#
}

/// Optimize an existing composition plan
function OptimizePlan(
  plan: string,
  optimization_goals: string
) -> CompositionPlan {
  client CustomSonnet4
  prompt #"
    Optimize this composition plan according to the specified goals.

    Current Plan:
    {{ plan }}

    Optimization Goals:
    {{ optimization_goals }}

    Consider:
    1. Parallelization opportunities
    2. Step consolidation
    3. Agent substitution for better performance
    4. Data flow optimization
    5. Failure mode reduction

    Preserve:
    - Correct data dependencies
    - Required functionality
    - Hard constraints

    {{ ctx.output_format }}
  "#
}

/// Validate a composition plan
function ValidatePlan(
  plan: string
) -> PlanValidation {
  client CustomSonnet4
  prompt #"
    Validate this composition plan for correctness and completeness.

    Plan:
    {{ plan }}

    Check for:
    1. Circular dependencies
    2. Missing input bindings
    3. Unreachable steps
    4. Type mismatches
    5. Timeout issues
    6. Resource conflicts

    {{ ctx.output_format }}
  "#
}

/// Analyze failure modes in a plan
function AnalyzeFailureModes(
  plan: string
) -> RiskAssessmentForComposition {
  client CustomSonnet4
  prompt #"
    Analyze potential failure modes in this composition plan.

    Plan:
    {{ plan }}

    For each step:
    1. Identify what could go wrong
    2. Estimate probability
    3. Assess impact severity
    4. Suggest mitigation strategies
    5. Identify fallback options

    Also identify:
    - Critical path (steps that must succeed)
    - Single points of failure
    - Cascading failure risks

    {{ ctx.output_format }}
  "#
}
