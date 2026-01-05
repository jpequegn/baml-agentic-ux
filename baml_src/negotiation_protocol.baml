// Negotiation Protocol Types
// BAML types for managing agent-to-agent negotiation sessions
// Issue #57 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.5)

// Dependencies:
// - AgentIdentity from agent_identity.baml
// - CapabilityRequirement from agent_capability.baml

// ============================================
// Negotiation Status
// ============================================

/// Status of a negotiation session
enum NegotiationStatus {
  INITIATED @description("Session created, no proposal yet")
  PROPOSAL_SENT @description("Initial proposal has been sent")
  COUNTER_OFFERED @description("A counter-proposal has been made")
  ACCEPTED @description("Negotiation concluded with agreement")
  REJECTED @description("Negotiation concluded without agreement")
  EXPIRED @description("Negotiation timed out")
  CANCELLED @description("Negotiation was cancelled by a party")
  ADAPTED @description("Negotiation resulted in capability adaptation")
}

/// Actions that can be taken in a negotiation
enum NegotiationAction {
  PROPOSE @description("Submit an initial proposal")
  COUNTER @description("Submit a counter-proposal")
  ACCEPT @description("Accept the current proposal")
  REJECT @description("Reject the current proposal")
  WITHDRAW @description("Withdraw from negotiation")
  TIMEOUT @description("System-generated timeout action")
}

// ============================================
// Negotiation Proposal
// ============================================

/// A proposal in a negotiation session
class NegotiationProposal {
  proposal_id string @description("Unique identifier for this proposal")
  capability_requirements CapabilityNegotiationItem[] @description("Capabilities being negotiated")
  terms NegotiationTerms @description("Terms of the proposal")
  constraints ProposalConstraint[]? @description("Additional constraints on the proposal")
  valid_until string @description("ISO 8601 expiry timestamp for this proposal")
}

/// An item representing a capability in negotiation
class CapabilityNegotiationItem {
  capability_id string @description("ID of the capability being negotiated")
  capability_name string @description("Human-readable name")
  requested_level string? @description("Requested capability level (e.g., 'full', 'limited')")
  parameters NegotiationParameter[]? @description("Parameters being negotiated")
  required bool @description("Whether this capability is required or optional")
}

/// A parameter being negotiated
class NegotiationParameter {
  name string @description("Parameter name")
  requested_value string @description("Requested value")
  acceptable_alternatives string[]? @description("Alternative acceptable values")
  min_value string? @description("Minimum acceptable value for numeric params")
  max_value string? @description("Maximum acceptable value for numeric params")
}

/// Terms of a negotiation proposal
class NegotiationTerms {
  duration_hours int? @description("Proposed agreement duration in hours")
  rate_limit_per_minute int? @description("Proposed rate limit")
  priority_level int? @description("Requested priority level (1-10)")
  billing_model string? @description("Billing model (free, per_call, subscription)")
  sla_requirements SLARequirement[]? @description("Service level requirements")
}

/// Service level agreement requirement
class SLARequirement {
  metric string @description("Metric name (e.g., 'response_time_ms', 'availability')")
  target_value float @description("Target value for the metric")
  measurement_window_hours int @description("Window for measuring the metric")
}

/// Additional constraint on a proposal
class ProposalConstraint {
  constraint_type NegotiationConstraintType @description("Type of constraint")
  field string @description("Field the constraint applies to")
  operator NegotiationConstraintOperator @description("Comparison operator")
  value string @description("Constraint value")
}

/// Types of constraints
enum NegotiationConstraintType {
  REQUIRED @description("Must be satisfied")
  PREFERRED @description("Preferred but not required")
  PROHIBITED @description("Must not be present")
}

/// Comparison operators for constraints
enum NegotiationConstraintOperator {
  EQUALS @description("Exact match")
  NOT_EQUALS @description("Must not match")
  GREATER_THAN @description("Greater than value")
  LESS_THAN @description("Less than value")
  CONTAINS @description("Contains value")
  IN @description("Value in list")
}

// ============================================
// Negotiation Turn
// ============================================

/// A single turn in a negotiation
class NegotiationTurn {
  turn_number int @description("Sequential turn number (1-indexed)")
  actor string @description("Agent ID of the actor taking this action")
  action NegotiationAction @description("Action taken")
  proposal NegotiationProposal? @description("Proposal if action is PROPOSE or COUNTER")
  timestamp string @description("ISO 8601 timestamp of this turn")
  rationale string? @description("Optional explanation for the action")
  metadata TurnMetadata? @description("Additional metadata for this turn")
}

/// Metadata for a negotiation turn
class TurnMetadata {
  response_time_ms int? @description("Time to respond in milliseconds")
  automated bool @description("Whether this was an automated response")
  confidence float? @description("Confidence in the action (0.0-1.0)")
  alternatives_considered int? @description("Number of alternatives considered")
}

// ============================================
// Negotiation Session
// ============================================

/// A complete negotiation session between two agents
class NegotiationSession {
  session_id string @description("Unique identifier for this session")
  initiator AgentIdentity @description("Agent that initiated the negotiation")
  responder AgentIdentity @description("Agent responding to the negotiation")
  status NegotiationStatus @description("Current status of the negotiation")
  created_at string @description("ISO 8601 timestamp of session creation")
  updated_at string @description("ISO 8601 timestamp of last update")
  expires_at string @description("ISO 8601 timestamp when session expires")
  history NegotiationTurn[] @description("Ordered list of turns in this session")
  current_proposal NegotiationProposal? @description("The current active proposal")
  result NegotiationResult? @description("Result if negotiation is complete")
  context NegotiationContext? @description("Additional context for the negotiation")
}

/// Result of a completed negotiation
class NegotiationResult {
  outcome NegotiationOutcome @description("Final outcome")
  agreed_proposal NegotiationProposal? @description("Agreed proposal if successful")
  agreement_id string? @description("ID of resulting agreement/contract")
  effective_from string? @description("When the agreement takes effect")
  effective_until string? @description("When the agreement expires")
  rejection_reasons string[]? @description("Reasons for rejection if applicable")
}

/// Possible negotiation outcomes
enum NegotiationOutcome {
  AGREEMENT @description("Parties reached an agreement")
  NO_AGREEMENT @description("Parties could not reach agreement")
  TIMEOUT @description("Negotiation expired without resolution")
  CANCELLED @description("Negotiation was cancelled")
  PARTIAL_AGREEMENT @description("Partial agreement on some capabilities")
}

/// Context for a negotiation session
class NegotiationContext {
  purpose string @description("Purpose of the negotiation")
  urgency NegotiationUrgencyLevel @description("Urgency level of the request")
  previous_session_id string? @description("ID of related previous session")
  tags string[]? @description("Tags for categorization")
  custom_data string? @description("Custom JSON data")
}

/// Urgency level for a negotiation
enum NegotiationUrgencyLevel {
  LOW @description("No time pressure")
  NORMAL @description("Standard priority")
  HIGH @description("Needs quick resolution")
  CRITICAL @description("Urgent business need")
}

// ============================================
// State Transition Validation
// ============================================

/// Request to transition negotiation state
class StateTransitionRequest {
  session_id string @description("Session to transition")
  requested_status NegotiationStatus @description("Target status")
  actor string @description("Agent requesting the transition")
  action NegotiationAction @description("Action triggering the transition")
  proposal NegotiationProposal? @description("Proposal if applicable")
  rationale string? @description("Reason for the transition")
}

/// Result of a state transition attempt
class StateTransitionResult {
  success bool @description("Whether the transition was allowed")
  previous_status NegotiationStatus @description("Status before transition")
  new_status NegotiationStatus @description("Status after transition (or unchanged)")
  turn_number int @description("Turn number if transition succeeded")
  error StateTransitionError? @description("Error if transition failed")
  warnings string[]? @description("Non-fatal warnings about the transition")
}

/// Error details for failed state transition
class StateTransitionError {
  error_code string @description("Machine-readable error code")
  message string @description("Human-readable error message")
  allowed_transitions NegotiationStatus[] @description("Valid target statuses from current state")
  suggestion string? @description("Suggested action to resolve")
}

// ============================================
// Negotiation AI Functions
// ============================================

/// Evaluate a proposal and suggest a response
function EvaluateProposal(
  session: NegotiationSession,
  our_identity: AgentIdentity,
  our_capabilities: string[],
  our_constraints: ProposalConstraint[]?
) -> ProposalEvaluation {
  client CustomSonnet4
  prompt #"
    Evaluate the current proposal in this negotiation session and recommend a response.

    Session:
    {{ session }}

    Our identity: {{ our_identity }}
    Our capabilities: {{ our_capabilities }}
    Our constraints: {{ our_constraints }}

    Analyze the proposal and recommend whether to accept, counter, or reject.
    If countering, suggest specific modifications to the proposal.

    {{ ctx.output_format }}
  "#
}

/// Result of proposal evaluation
class ProposalEvaluation {
  recommended_action NegotiationAction @description("Recommended action")
  confidence float @description("Confidence in recommendation (0.0-1.0)")
  reasoning string @description("Explanation for the recommendation")
  suggested_counter NegotiationProposal? @description("Suggested counter-proposal if applicable")
  risk_assessment RiskAssessment @description("Risk assessment of the proposal")
  compatibility_score float @description("How well the proposal matches our capabilities (0.0-1.0)")
}

/// Risk assessment for a proposal
class RiskAssessment {
  overall_risk RiskLevel @description("Overall risk level")
  factors RiskFactor[] @description("Individual risk factors")
  mitigations string[]? @description("Suggested risk mitigations")
}

/// Risk level for negotiation
enum NegotiationRiskLevel {
  LOW @description("Minimal risk")
  MODERATE @description("Some concerns but manageable")
  HIGH @description("Significant concerns")
  CRITICAL @description("Unacceptable risk")
}

/// Individual risk factor
class RiskFactor {
  category string @description("Risk category")
  description string @description("Description of the risk")
  severity RiskLevel @description("Severity of this factor")
  likelihood float @description("Likelihood of occurrence (0.0-1.0)")
}

/// Generate an optimal counter-proposal
function GenerateCounterProposal(
  session: NegotiationSession,
  our_identity: AgentIdentity,
  our_capabilities: string[],
  negotiation_strategy: NegotiationStrategy
) -> NegotiationProposal {
  client CustomSonnet4
  prompt #"
    Generate an optimal counter-proposal for this negotiation.

    Session: {{ session }}
    Our identity: {{ our_identity }}
    Our capabilities: {{ our_capabilities }}
    Strategy: {{ negotiation_strategy }}

    Create a counter-proposal that:
    1. Moves toward agreement while protecting our interests
    2. Addresses the other party's key concerns
    3. Follows the specified negotiation strategy

    {{ ctx.output_format }}
  "#
}

/// Negotiation strategy configuration
class NegotiationStrategy {
  approach StrategyApproach @description("Overall approach")
  priority_capabilities string[] @description("Capabilities we prioritize")
  max_concession_percentage float @description("Maximum we'll concede (0.0-1.0)")
  must_have_terms string[] @description("Non-negotiable requirements")
  nice_to_have_terms string[] @description("Preferred but negotiable terms")
  time_sensitivity float @description("How time-sensitive we are (0.0-1.0)")
}

/// Negotiation approach style
enum StrategyApproach {
  COLLABORATIVE @description("Seek win-win outcomes")
  COMPETITIVE @description("Maximize our gains")
  ACCOMMODATING @description("Prioritize relationship over terms")
  AVOIDING @description("Minimize conflict")
  COMPROMISING @description("Seek middle ground quickly")
}
