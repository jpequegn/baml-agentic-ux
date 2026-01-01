// Composition Execution Engine Types
// Executing composition plans with parallel execution, retry, and circuit breakers
// Issue #64 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.12)

// Dependencies:
// - CompositionPlan, CompositionStep from composition_planning.baml
// - AgentCard from agent_capability.baml

// ============================================
// Execution Status Enums
// ============================================

/// Status of a composition execution
enum ExecutionStatus {
  PENDING @description("Execution not yet started")
  INITIALIZING @description("Preparing to execute")
  RUNNING @description("Execution in progress")
  PAUSED @description("Execution paused")
  COMPLETED @description("Execution completed successfully")
  FAILED @description("Execution failed")
  CANCELLED @description("Execution was cancelled")
  TIMEOUT @description("Execution timed out")
  RECOVERING @description("Attempting recovery from failure")
}

/// Status of a single step execution
enum StepStatus {
  PENDING @description("Step not yet started")
  QUEUED @description("Step waiting to execute")
  RUNNING @description("Step currently executing")
  COMPLETED @description("Step completed successfully")
  FAILED @description("Step failed")
  SKIPPED @description("Step was skipped")
  CANCELLED @description("Step was cancelled")
  TIMEOUT @description("Step timed out")
  RETRYING @description("Step is being retried")
}

/// Strategy for recovering from failures
enum RecoveryStrategy {
  RETRY @description("Retry the failed step")
  ALTERNATIVE_AGENT @description("Use a different agent for the step")
  SKIP @description("Skip the failed step and continue")
  ROLLBACK @description("Rollback to a previous state")
  COMPENSATE @description("Execute compensation actions")
  ABORT @description("Abort the entire execution")
  PARTIAL_COMPLETE @description("Complete with partial results")
}

/// State of a circuit breaker
enum CircuitBreakerState {
  CLOSED @description("Circuit is closed, requests pass through")
  OPEN @description("Circuit is open, requests are blocked")
  HALF_OPEN @description("Circuit is testing if recovery is possible")
}

/// Type of backoff strategy
enum BackoffStrategy {
  FIXED @description("Fixed delay between retries")
  LINEAR @description("Linearly increasing delay")
  EXPONENTIAL @description("Exponentially increasing delay")
  JITTERED @description("Exponential with random jitter")
}

// ============================================
// Configuration Types
// ============================================

/// Configuration for retry behavior
class RetryConfig {
  max_retries int @description("Maximum number of retry attempts")
  backoff_strategy BackoffStrategy @description("Strategy for delay between retries")
  initial_delay_ms int @description("Initial delay in milliseconds")
  max_delay_ms int @description("Maximum delay in milliseconds")
  backoff_multiplier float @description("Multiplier for exponential/linear backoff")
  retryable_errors string[] @description("Error types that trigger retry")
}

/// Configuration for circuit breaker
class CircuitBreakerConfig {
  failure_threshold int @description("Number of failures to open circuit")
  success_threshold int @description("Number of successes to close circuit")
  recovery_timeout_ms int @description("Time before attempting recovery")
  half_open_requests int @description("Number of test requests in half-open state")
  monitored_errors string[] @description("Error types that count as failures")
}

/// Overall orchestration configuration
class OrchestrationConfig {
  parallel_execution bool @description("Enable parallel step execution")
  max_concurrent_steps int @description("Maximum steps running concurrently")
  global_timeout_ms int @description("Global timeout for entire execution")
  step_timeout_ms int @description("Default timeout per step")
  retry_config RetryConfig? @description("Default retry configuration")
  circuit_breaker CircuitBreakerConfig? @description("Circuit breaker configuration")
  collect_metrics bool @description("Whether to collect detailed metrics")
  preserve_partial_results bool @description("Keep results from completed steps on failure")
}

// ============================================
// Step Execution Types
// ============================================

/// Result of executing a single step
class StepResult {
  step_id string @description("ID of the executed step")
  step_name string @description("Name of the step")
  status StepStatus @description("Final status of the step")
  started_at string @description("ISO 8601 start timestamp")
  completed_at string? @description("ISO 8601 completion timestamp")
  output string? @description("Step output as JSON string")
  output_type string? @description("Type of the output")
  latency_ms int @description("Execution time in milliseconds")
  retries int @description("Number of retry attempts")
  error StepError? @description("Error details if failed")
  metrics StepMetrics? @description("Detailed execution metrics")
}

/// Error information for a step
class StepError {
  error_code string @description("Error code")
  error_type string @description("Type of error")
  message string @description("Error message")
  stack_trace string? @description("Stack trace if available")
  retry_possible bool @description("Whether retry might succeed")
  cause string? @description("Underlying cause")
}

/// Metrics for step execution
class StepMetrics {
  queue_time_ms int @description("Time spent waiting to execute")
  execution_time_ms int @description("Actual execution time")
  serialization_time_ms int @description("Time for input/output serialization")
  network_time_ms int? @description("Network round-trip time if applicable")
  retries_exhausted bool @description("Whether all retries were used")
}

// ============================================
// Composition Execution Types
// ============================================

/// Complete execution of a composition plan
class CompositionExecution {
  execution_id string @description("Unique execution identifier")
  plan_id string @description("ID of the executed plan")
  plan_version string @description("Version of the plan")
  status ExecutionStatus @description("Current execution status")
  started_at string @description("ISO 8601 start timestamp")
  completed_at string? @description("ISO 8601 completion timestamp")
  step_results StepResult[] @description("Results for each executed step")
  final_output string? @description("Final output from exit points")
  error CompositionError? @description("Error if execution failed")
  execution_metrics ExecutionMetrics @description("Overall execution metrics")
  recovery_attempts RecoveryAttempt[]? @description("Recovery attempts made")
}

/// Error for the overall composition
class CompositionError {
  error_id string @description("Unique error identifier")
  error_type string @description("Type of composition error")
  message string @description("Error message")
  failed_step_id string? @description("Step that caused the failure")
  cascading_failures string[]? @description("Steps that failed due to this error")
  recoverable bool @description("Whether recovery might be possible")
  suggested_recovery RecoveryStrategy? @description("Suggested recovery strategy")
}

/// Overall execution metrics
class ExecutionMetrics {
  total_duration_ms int @description("Total execution time")
  steps_completed int @description("Number of steps completed")
  steps_failed int @description("Number of steps failed")
  steps_skipped int @description("Number of steps skipped")
  total_retries int @description("Total retry attempts across all steps")
  parallel_efficiency float @description("Ratio of ideal vs actual parallel time")
  circuit_breaker_trips int @description("Number of circuit breaker activations")
}

/// Record of a recovery attempt
class RecoveryAttempt {
  attempt_id string @description("Unique attempt identifier")
  timestamp string @description("When recovery was attempted")
  strategy RecoveryStrategy @description("Strategy used")
  trigger_error string @description("Error that triggered recovery")
  success bool @description("Whether recovery succeeded")
  details string @description("Details of the recovery attempt")
}

// ============================================
// Recovery Types
// ============================================

/// Plan for recovering from a failure
class RecoveryPlan {
  recovery_id string @description("Unique recovery plan identifier")
  strategy RecoveryStrategy @description("Recovery strategy to use")
  original_error CompositionError @description("Error being recovered from")
  modified_plan ModifiedPlan? @description("Modified execution plan")
  resume_from_step string? @description("Step ID to resume from")
  skip_steps string[] @description("Steps to skip")
  compensation_actions CompensationAction[]? @description("Actions to undo partial work")
  explanation string @description("Explanation of recovery approach")
  confidence float @description("Confidence in recovery success (0.0-1.0)")
  estimated_additional_time_ms int? @description("Estimated additional time needed")
}

/// Modifications to the execution plan for recovery
class ModifiedPlan {
  plan_id string @description("New plan ID")
  changes PlanChange[] @description("Changes made to the plan")
  reason string @description("Why changes were made")
}

/// A change made to recovery plan
class PlanChange {
  change_type string @description("Type of change")
  step_id string @description("Affected step")
  description string @description("Description of change")
  original_value string? @description("Original value")
  new_value string? @description("New value")
}

/// Action to compensate for partial execution
class CompensationAction {
  action_id string @description("Unique action identifier")
  step_id string @description("Step being compensated")
  action_type string @description("Type of compensation")
  description string @description("What the action does")
  agent_id string? @description("Agent to execute compensation")
  parameters string? @description("Parameters as JSON")
}

// ============================================
// Execution Request/Response Types
// ============================================

/// Request to execute a composition
class ExecuteCompositionRequest {
  request_id string @description("Unique request identifier")
  plan_id string @description("ID of the plan to execute")
  inputs ExecutionInputs @description("Inputs for the execution")
  config OrchestrationConfig @description("Orchestration configuration")
  context ExecutionContext? @description("Execution context")
}

/// Inputs for composition execution
class ExecutionInputs {
  initial_data string @description("Initial input data as JSON")
  parameters ExecutionParameter[] @description("Named parameters")
  secrets SecretReference[]? @description("References to secrets")
}

/// Named execution parameter
class ExecutionParameter {
  name string @description("Parameter name")
  value string @description("Parameter value")
  type string @description("Parameter type")
}

/// Reference to a secret value
class SecretReference {
  name string @description("Secret name")
  source string @description("Secret source (vault, env, etc.)")
  key string @description("Key within the source")
}

/// Context for execution
class ExecutionContext {
  session_id string? @description("Session identifier")
  user_id string? @description("User identifier")
  trace_id string? @description("Distributed trace ID")
  priority int @description("Execution priority (1=highest)")
  deadline string? @description("ISO 8601 deadline")
  tags string[]? @description("Tags for categorization")
}

/// Response from composition execution
class ExecuteCompositionResponse {
  request_id string @description("Original request ID")
  execution CompositionExecution @description("Execution result")
}

/// Request to recover from a failure
class RecoverFromFailureRequest {
  request_id string @description("Unique request identifier")
  execution CompositionExecution @description("Failed execution")
  error CompositionError @description("Error to recover from")
  available_agents AvailableAgentInfo[] @description("Agents available for recovery")
  preferences RecoveryPreferences? @description("Recovery preferences")
}

/// Information about an available agent for recovery
class AvailableAgentInfo {
  agent_id string @description("Agent identifier")
  agent_name string @description("Agent name")
  capabilities string[] @description("Available capabilities")
  current_load float @description("Current load (0.0-1.0)")
}

/// Preferences for recovery
class RecoveryPreferences {
  prefer_fast_recovery bool @description("Prioritize speed over completeness")
  allow_partial_results bool @description("Accept partial results")
  max_recovery_attempts int @description("Maximum recovery attempts")
  rollback_on_failure bool @description("Rollback if recovery fails")
}

/// Response from recovery planning
class RecoverFromFailureResponse {
  request_id string @description("Original request ID")
  recovery_plan RecoveryPlan @description("Generated recovery plan")
  alternatives RecoveryPlan[]? @description("Alternative recovery plans")
}

// ============================================
// Circuit Breaker Types
// ============================================

/// Status of a circuit breaker
class CircuitBreakerStatus {
  circuit_id string @description("Circuit identifier")
  agent_id string @description("Agent being protected")
  state CircuitBreakerState @description("Current state")
  failure_count int @description("Current failure count")
  success_count int @description("Current success count (in half-open)")
  last_failure_at string? @description("Last failure timestamp")
  last_state_change string @description("Last state change timestamp")
  next_retry_at string? @description("When retry will be attempted (if open)")
}

// ============================================
// AI Functions
// ============================================

/// Execute a composition plan
function ExecuteComposition(
  plan string,
  inputs string,
  config string
) -> CompositionExecution {
  client CustomSonnet4
  prompt #"
    Execute this composition plan with the provided inputs.

    Plan:
    {{ plan }}

    Inputs:
    {{ inputs }}

    Configuration:
    {{ config }}

    Execute each step according to the plan:
    1. Respect step dependencies
    2. Run parallel steps concurrently where allowed
    3. Apply retry policies on failures
    4. Track execution metrics
    5. Collect outputs for data flow

    {{ ctx.output_format }}
  "#
}

/// Generate a recovery plan for a failed execution
function RecoverFromFailure(
  execution string,
  error string,
  available_agents string
) -> RecoveryPlan {
  client CustomSonnet4
  prompt #"
    Generate a recovery plan for this failed execution.

    Failed Execution:
    {{ execution }}

    Error:
    {{ error }}

    Available Agents:
    {{ available_agents }}

    Analyze the failure and create a recovery plan that:
    1. Identifies the root cause
    2. Determines if recovery is possible
    3. Chooses the best recovery strategy
    4. Plans any necessary compensating actions
    5. Modifies the plan if needed

    {{ ctx.output_format }}
  "#
}

/// Determine optimal execution order considering parallelism
function PlanExecutionOrder(
  plan string,
  config string
) -> ExecutionOrder {
  client CustomSonnet4
  prompt #"
    Plan the optimal execution order for this composition.

    Plan:
    {{ plan }}

    Configuration:
    {{ config }}

    Determine:
    1. Which steps can run in parallel
    2. The optimal execution waves
    3. Resource allocation for parallel execution
    4. Critical path through the plan

    {{ ctx.output_format }}
  "#
}

/// Planned execution order
class ExecutionOrder {
  waves ExecutionWave[] @description("Execution waves")
  critical_path string[] @description("Steps on critical path")
  estimated_duration_ms int @description("Estimated total duration")
  parallelism_factor float @description("Degree of parallelism achieved")
}

/// A wave of parallel execution
class ExecutionWave {
  wave_number int @description("Wave order number")
  step_ids string[] @description("Steps to execute in this wave")
  estimated_duration_ms int @description("Estimated wave duration")
  resource_requirements ResourceRequirements @description("Resources needed")
}

/// Resource requirements for execution
class ResourceRequirements {
  max_concurrent_agents int @description("Maximum agents needed")
  estimated_memory_mb int @description("Estimated memory usage")
  network_calls int @description("Number of network calls")
}
