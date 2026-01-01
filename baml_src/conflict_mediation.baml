// Conflict Mediation System Types
// Mediation for resolving conflicts between negotiating parties and handling deadlocks
// Issue #62 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.10)

// Dependencies:
// - NegotiationProposal from negotiation_protocol.baml
// - ConflictAnalysis, Conflict from conflict_detection.baml
// - NegotiationSession from negotiation_protocol.baml

// ============================================
// Mediation Style Enums
// ============================================

/// Style of mediation to apply
enum MediationStyle {
  FACILITATIVE @description("Help parties find their own solution through dialogue")
  EVALUATIVE @description("Mediator suggests and evaluates potential solutions")
  TRANSFORMATIVE @description("Focus on changing relationship dynamics and understanding")
  DIRECTIVE @description("Mediator provides binding decision when parties cannot agree")
}

/// Strategy for resolving deadlocks
enum ResolutionStrategy {
  TRANSFORM @description("Convert data format to achieve compatibility")
  SUBSET @description("Use common subset of capabilities that both support")
  MEDIATE @description("Third-party mediation to find compromise")
  ESCALATE @description("Escalate to human decision maker")
  ALTERNATIVE @description("Substitute with different but equivalent capability")
  NEGOTIATE_TERMS @description("Adjust terms while keeping core requirements")
  BRIDGE @description("Create adapter or bridge layer between parties")
  SPLIT_DIFFERENCE @description("Average numeric terms between positions")
  PACKAGE_DEAL @description("Trade-offs between multiple issues")
  TIME_SHARE @description("Alternate access or usage periods")
}

/// Outcome status of mediation
enum MediationOutcome {
  RESOLVED @description("All conflicts successfully resolved")
  PARTIALLY_RESOLVED @description("Some conflicts resolved, others remain")
  DEADLOCK @description("No resolution possible, escalation needed")
  DEFERRED @description("Resolution postponed for future discussion")
  WITHDRAWN @description("Party withdrew from mediation")
}

/// Priority level for conflict resolution
enum ConflictPriority {
  CRITICAL @description("Must resolve to proceed")
  HIGH @description("Should resolve soon")
  MEDIUM @description("Can work around temporarily")
  LOW @description("Nice to resolve but not blocking")
}

// ============================================
// Party Position Types
// ============================================

/// Position of a negotiating party
class PartyPosition {
  party_id string @description("Identifier of the party")
  party_name string @description("Human-readable name")
  proposal NegotiationProposalSummary @description("Current proposal from this party")
  priorities string[] @description("Ordered list of priorities")
  constraints PositionConstraint[] @description("Hard constraints that cannot be violated")
  flexibility FlexibilityAssessment @description("Areas where party can be flexible")
}

/// Summary of a negotiation proposal for mediation
class NegotiationProposalSummary {
  proposal_id string @description("Proposal identifier")
  terms TermSummary[] @description("Key terms being proposed")
  capabilities string[] @description("Capabilities being negotiated")
  valid_until string @description("ISO 8601 expiry timestamp")
}

/// Summary of a negotiation term
class TermSummary {
  term_name string @description("Name of the term")
  term_value string @description("Proposed value")
  negotiable bool @description("Whether this term is negotiable")
  min_acceptable string? @description("Minimum acceptable value if negotiable")
  max_acceptable string? @description("Maximum acceptable value if negotiable")
}

/// Constraint on a party's position
class PositionConstraint {
  constraint_id string @description("Unique constraint identifier")
  field string @description("Field the constraint applies to")
  constraint_type string @description("Type of constraint (min, max, equals, etc.)")
  value string @description("Constraint value")
  reason string @description("Why this constraint exists")
  waivable bool @description("Whether constraint can be waived under certain conditions")
}

/// Assessment of flexibility in a position
class FlexibilityAssessment {
  flexible_terms string[] @description("Terms that can be adjusted")
  trade_off_pairs TradeOffPair[] @description("Terms that can be traded off")
  total_flexibility_score float @description("Overall flexibility (0.0-1.0)")
}

/// A pair of terms that can be traded off against each other
class TradeOffPair {
  term_a string @description("First term")
  term_b string @description("Second term")
  relationship string @description("How they relate (inverse, proportional, etc.)")
}

// ============================================
// Mediation Request/Response Types
// ============================================

/// Request for mediation
class MediationRequest {
  request_id string @description("Unique request identifier")
  session_id string @description("Negotiation session being mediated")
  conflict ConflictSummaryForMediation @description("Summary of the conflict")
  party_a PartyPosition @description("Position of first party")
  party_b PartyPosition @description("Position of second party")
  mediation_style MediationStyle @description("Style of mediation requested")
  options MediationOptions @description("Options for mediation process")
  context MediationContext? @description("Additional context")
}

/// Summary of conflict for mediation purposes
class ConflictSummaryForMediation {
  conflict_id string @description("Conflict identifier")
  conflict_type string @description("Type of conflict")
  severity string @description("Severity level")
  description string @description("Description of the conflict")
  affected_terms string[] @description("Terms affected by the conflict")
  history ConflictHistoryEntry[]? @description("History of resolution attempts")
}

/// Entry in conflict history
class ConflictHistoryEntry {
  timestamp string @description("When this attempt occurred")
  strategy_tried ResolutionStrategy @description("Strategy that was attempted")
  outcome string @description("What happened")
  notes string? @description("Additional notes")
}

/// Options for the mediation process
class MediationOptions {
  max_iterations int @description("Maximum mediation rounds")
  auto_escalate bool @description("Automatically escalate if deadlock persists")
  escalation_threshold int @description("Turns without progress before escalation")
  allow_partial_resolution bool @description("Accept partial resolution")
  generate_alternatives bool @description("Generate alternative solutions")
  max_alternatives int @description("Maximum alternatives to generate")
  preserve_relationship bool @description("Prioritize maintaining party relationship")
}

/// Context for mediation
class MediationContext {
  urgency ConflictPriority @description("How urgent is resolution")
  business_impact string? @description("Impact if unresolved")
  previous_mediations string[]? @description("IDs of previous mediation attempts")
  relationship_history string? @description("History between parties")
  external_constraints string[]? @description("External factors to consider")
}

// ============================================
// Mediation Result Types
// ============================================

/// Result of mediation attempt
class MediationResult {
  result_id string @description("Unique result identifier")
  request_id string @description("Original request ID")
  outcome MediationOutcome @description("Outcome of mediation")
  resolved bool @description("Whether conflict was resolved")
  compromise_proposal CompromiseProposal? @description("Proposed compromise if any")
  accepted_by string[] @description("Party IDs that accepted the compromise")
  rejected_by string[] @description("Party IDs that rejected the compromise")
  remaining_conflicts ConflictSummaryForMediation[] @description("Conflicts still unresolved")
  mediator_notes string @description("Notes from the mediation process")
  recommendations string[] @description("Recommendations for parties")
  alternatives CompromiseProposal[]? @description("Alternative proposals if generated")
  metrics MediationMetrics @description("Metrics about the mediation")
}

/// A proposed compromise
class CompromiseProposal {
  proposal_id string @description("Unique proposal identifier")
  description string @description("Description of the compromise")
  terms CompromiseTerm[] @description("Terms of the compromise")
  concessions_a Concession[] @description("What party A gives up")
  concessions_b Concession[] @description("What party B gives up")
  gains_a string[] @description("What party A gains")
  gains_b string[] @description("What party B gains")
  fairness_score float @description("How fair the compromise is (0.0-1.0)")
  viability_score float @description("How viable/practical (0.0-1.0)")
}

/// A term in a compromise proposal
class CompromiseTerm {
  term_name string @description("Name of the term")
  original_a string @description("Original value from party A")
  original_b string @description("Original value from party B")
  compromise_value string @description("Proposed compromise value")
  rationale string @description("Why this compromise value")
}

/// A concession made by a party
class Concession {
  term_name string @description("Term being conceded on")
  original_value string @description("Original requested value")
  conceded_value string @description("Value after concession")
  impact string @description("Impact of this concession")
  compensation string? @description("What party gets in return")
}

/// Metrics about the mediation process
class MediationMetrics {
  iterations_used int @description("Number of mediation rounds")
  time_elapsed_ms int @description("Total time in milliseconds")
  proposals_generated int @description("Number of proposals generated")
  proposals_rejected int @description("Number rejected by parties")
  common_ground_found float @description("Percentage of common ground (0.0-1.0)")
  gap_closed float @description("Percentage of gap closed (0.0-1.0)")
}

// ============================================
// Deadlock Resolution Types
// ============================================

/// Request to resolve a deadlock
class DeadlockResolutionRequest {
  request_id string @description("Unique request identifier")
  session_id string @description("Negotiation session ID")
  deadlock_turns int @description("Number of turns in deadlock")
  turn_history TurnSummary[] @description("Recent turn summaries")
  party_positions PartyPosition[] @description("Current positions of all parties")
  previously_tried ResolutionStrategy[] @description("Strategies already attempted")
}

/// Summary of a negotiation turn
class TurnSummary {
  turn_number int @description("Turn number")
  actor string @description("Who took action")
  action string @description("What action was taken")
  key_changes string[] @description("Key changes in this turn")
  progress_made bool @description("Whether progress was made")
}

/// Result of deadlock resolution attempt
class DeadlockResolution {
  resolution_id string @description("Unique resolution identifier")
  request_id string @description("Original request ID")
  resolution_possible bool @description("Whether resolution is possible")
  strategy ResolutionStrategy @description("Recommended strategy")
  proposal CompromiseProposal? @description("Proposed resolution if any")
  explanation string @description("Explanation of the recommendation")
  escalation_needed bool @description("Whether escalation is needed")
  escalation_reason string? @description("Why escalation is needed")
  alternative_strategies AlternativeStrategy[] @description("Other strategies to consider")
  confidence float @description("Confidence in recommendation (0.0-1.0)")
}

/// An alternative strategy option
class AlternativeStrategy {
  strategy ResolutionStrategy @description("The strategy")
  description string @description("How to apply it")
  pros string[] @description("Advantages")
  cons string[] @description("Disadvantages")
  likelihood_of_success float @description("Estimated success rate (0.0-1.0)")
}

// ============================================
// Escalation Types
// ============================================

/// Request for escalation
class EscalationRequest {
  request_id string @description("Unique request identifier")
  session_id string @description("Negotiation session ID")
  reason string @description("Why escalation is needed")
  conflict_summary ConflictSummaryForMediation @description("Conflict being escalated")
  mediation_history MediationResult[] @description("Previous mediation attempts")
  urgency ConflictPriority @description("Urgency of escalation")
  recommended_action string @description("What action is recommended")
}

/// Response to escalation request
class EscalationResponse {
  response_id string @description("Unique response identifier")
  request_id string @description("Original request ID")
  escalation_accepted bool @description("Whether escalation was accepted")
  assigned_to string? @description("Who will handle the escalation")
  expected_resolution_time string? @description("Expected time to resolution")
  interim_action string? @description("Action to take while waiting")
  notes string? @description("Additional notes")
}

// ============================================
// AI Functions
// ============================================

/// Mediate a conflict between two parties
function MediateConflict(
  request MediationRequest
) -> MediationResult {
  client CustomSonnet4
  prompt #"
    Mediate the conflict between the two parties and propose a fair compromise.

    Mediation Request:
    {{ request }}

    Using the {{ request.mediation_style }} mediation style:

    1. Identify common ground between the parties
    2. Find areas where each party can be flexible
    3. Generate compromise proposals that balance both interests
    4. Assess fairness and viability of each proposal
    5. Provide recommendations for resolution

    Consider:
    - Hard constraints that cannot be violated
    - Trade-offs that might be acceptable
    - Creative solutions that address underlying needs
    - Relationship preservation if requested

    {{ ctx.output_format }}
  "#
}

/// Resolve a deadlock in negotiation
function ResolveDeadlock(
  request DeadlockResolutionRequest
) -> DeadlockResolution {
  client CustomSonnet4
  prompt #"
    Analyze this negotiation deadlock and recommend a resolution strategy.

    Deadlock Information:
    {{ request }}

    The negotiation has been stuck for {{ request.deadlock_turns }} turns.

    Analyze:
    1. Root cause of the deadlock
    2. What strategies have been tried and why they failed
    3. Remaining options for resolution
    4. Whether escalation is necessary

    Recommend the most promising strategy and explain why it might succeed
    where previous attempts failed.

    {{ ctx.output_format }}
  "#
}

/// Find common ground between party positions
function FindCommonGround(
  party_a PartyPosition,
  party_b PartyPosition
) -> CommonGroundAnalysis {
  client CustomSonnet4
  prompt #"
    Analyze the positions of both parties and identify common ground.

    Party A Position:
    {{ party_a }}

    Party B Position:
    {{ party_b }}

    Identify:
    1. Terms where both parties already agree
    2. Terms where positions are close and compromise is easy
    3. Terms where positions are far apart but negotiable
    4. Terms where positions are incompatible

    {{ ctx.output_format }}
  "#
}

/// Analysis of common ground between parties
class CommonGroundAnalysis {
  agreed_terms AgreedTerm[] @description("Terms where parties agree")
  close_terms CloseTerm[] @description("Terms where positions are close")
  negotiable_terms NegotiableTerm[] @description("Terms that are negotiable")
  incompatible_terms IncompatibleTerm[] @description("Terms that are incompatible")
  overall_alignment float @description("Overall alignment score (0.0-1.0)")
  recommended_focus string[] @description("Terms to focus mediation on")
}

/// A term where parties agree
class AgreedTerm {
  term_name string @description("Name of the term")
  agreed_value string @description("Value both parties accept")
}

/// A term where positions are close
class CloseTerm {
  term_name string @description("Name of the term")
  value_a string @description("Party A's value")
  value_b string @description("Party B's value")
  gap_assessment string @description("Assessment of the gap")
  suggested_compromise string @description("Suggested compromise value")
}

/// A term that is negotiable
class NegotiableTerm {
  term_name string @description("Name of the term")
  value_a string @description("Party A's value")
  value_b string @description("Party B's value")
  flexibility_a string @description("Party A's flexibility")
  flexibility_b string @description("Party B's flexibility")
  trade_off_potential string @description("Potential for trade-off")
}

/// A term where positions are incompatible
class IncompatibleTerm {
  term_name string @description("Name of the term")
  value_a string @description("Party A's value")
  value_b string @description("Party B's value")
  reason string @description("Why they are incompatible")
  possible_workarounds string[] @description("Possible workarounds")
}

/// Generate creative solutions for a conflict
function GenerateCreativeSolutions(
  conflict ConflictSummaryForMediation,
  constraints string[],
  preferences string[]
) -> CreativeSolution[] {
  client CustomSonnet4
  prompt #"
    Generate creative solutions to resolve this conflict.

    Conflict:
    {{ conflict }}

    Constraints that must be respected:
    {{ constraints }}

    Preferences to consider:
    {{ preferences }}

    Think outside the box to find novel solutions that:
    1. Address the underlying needs of both parties
    2. Create value rather than just dividing it
    3. Find synergies between seemingly opposed positions
    4. Use time, scope, or other dimensions creatively

    {{ ctx.output_format }}
  "#
}

/// A creative solution to a conflict
class CreativeSolution {
  solution_id string @description("Unique solution identifier")
  title string @description("Brief title")
  description string @description("Detailed description")
  how_it_works string @description("How the solution works")
  benefits_party_a string[] @description("Benefits for party A")
  benefits_party_b string[] @description("Benefits for party B")
  implementation_steps string[] @description("Steps to implement")
  risks string[] @description("Potential risks")
  novelty_score float @description("How novel/creative (0.0-1.0)")
  feasibility_score float @description("How feasible (0.0-1.0)")
}
