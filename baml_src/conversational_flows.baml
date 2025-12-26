// Conversational Flow Types
// Models multi-turn conversations and branching dialogues

/// A conversational flow defining a multi-turn interaction pattern
class ConversationalFlow {
  flow_id string @description("Unique identifier for this flow")
  name string @description("Human-readable flow name")
  description string? @description("What this flow accomplishes")
  trigger_intents string[] @description("User intents that start this flow")
  entry_conditions ContextRequirement[]? @description("Conditions to enter this flow")
  steps FlowStep[] @description("Ordered steps in the flow")
  fallback_responses string[] @description("Responses when flow can't proceed")
  timeout_seconds int? @description("Flow timeout in seconds")
  on_timeout_action string? @description("Action when flow times out")
}

/// A single step in a conversational flow
class FlowStep {
  step_id string @description("Unique step identifier")
  step_type FlowStepType
  component_ref string? @description("Reference to LUIComponent.component_id")
  prompt_template string? @description("Template for prompting user")
  action_config ActionConfig? @description("Configuration for ACTION steps")
  branch_config BranchConfig? @description("Configuration for BRANCH steps")
  transitions StepTransition[] @description("Possible next steps")
  error_handling StepErrorHandling?
}

/// Types of flow steps
enum FlowStepType {
  PROMPT @description("Ask user for input")
  ACTION @description("Execute an action/component")
  BRANCH @description("Conditional routing based on context")
  CONFIRM @description("Get user confirmation before proceeding")
  VALIDATE @description("Validate collected data")
  TRANSFORM @description("Transform/process data")
  COMPLETE @description("End the flow successfully")
  CANCEL @description("End the flow due to cancellation")
}

/// Configuration for ACTION steps
class ActionConfig {
  component_id string @description("LUIComponent to invoke")
  parameter_mapping ParameterMapping[] @description("How to map flow context to component params")
  store_result_as string? @description("Variable name to store result")
  retry_on_failure bool
  max_retries int?
}

/// Maps flow context to component parameters
class ParameterMapping {
  parameter_name string @description("Target component parameter")
  source_type ParameterSourceType
  source_value string @description("Source expression or literal value")
}

enum ParameterSourceType {
  CONTEXT @description("From flow context variable")
  USER_INPUT @description("From recent user input")
  LITERAL @description("Static literal value")
  EXPRESSION @description("Computed expression")
}

/// Configuration for BRANCH steps
class BranchConfig {
  evaluation_type BranchEvaluationType
  conditions BranchCondition[]
  default_transition string? @description("Step if no condition matches")
}

enum BranchEvaluationType {
  FIRST_MATCH @description("Use first matching condition")
  BEST_MATCH @description("Use highest confidence match")
  ALL_MATCH @description("Execute all matching branches")
}

class BranchCondition {
  condition_id string
  expression string @description("Condition expression to evaluate")
  description string? @description("Human-readable condition description")
  target_step string @description("Step to go to if condition matches")
}

/// Transition between flow steps
class StepTransition {
  transition_id string?
  condition string? @description("Condition for this transition (null = default)")
  next_step string @description("Target step_id")
  transition_message string? @description("Message to show during transition")
}

/// Error handling for a step
class StepErrorHandling {
  on_error ErrorAction
  retry_count int?
  fallback_step string? @description("Step to go to on unrecoverable error")
  error_message_template string?
}

enum ErrorAction {
  RETRY @description("Retry the step")
  SKIP @description("Skip to next step")
  FALLBACK @description("Go to fallback step")
  ABORT @description("End the flow with error")
  ASK_USER @description("Ask user how to proceed")
}

/// Runtime state of a flow execution
class FlowExecutionState {
  flow_id string
  current_step_id string
  started_at string @description("ISO 8601 timestamp")
  context FlowContext
  history FlowHistoryEntry[]
  status FlowStatus
}

class FlowContext {
  variables map<string, string> @description("Named variables collected during flow")
  user_inputs string[] @description("All user inputs in order")
  extracted_entities ExtractedEntity[]
}

class ExtractedEntity {
  entity_type string
  entity_value string
  confidence float
  source_step string
}

class FlowHistoryEntry {
  step_id string
  timestamp string
  action_taken string
  result string?
}

enum FlowStatus {
  ACTIVE
  WAITING_USER_INPUT
  PROCESSING
  COMPLETED
  CANCELLED
  TIMED_OUT
  ERROR
}
