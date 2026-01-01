// Proposal Evaluation & Counter-Offer Generation
// BAML types for evaluating proposals and generating counter-offers
// Issue #58 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.6)

// Dependencies:
// - NegotiationProposal, NegotiationSession, NegotiationAction, NegotiationStrategy from negotiation_protocol.baml
// - AgentCapability from agent_capability.baml

// ============================================
// Capability Request/Offer Types
// ============================================

/// A capability being requested in a proposal
class CapabilityRequest {
  capability_id string @description("ID of the capability being requested")
  capability_name string @description("Human-readable name")
  required bool @description("Whether this capability is required for the proposal")
  parameters RequestedParameter[]? @description("Specific parameter requirements")
  usage_context string? @description("Context in which the capability will be used")
  priority int @description("Priority of this request (1-10, higher = more important)")
}

/// A parameter being requested
class RequestedParameter {
  name string @description("Parameter name")
  value string @description("Requested value")
  negotiable bool @description("Whether this parameter is negotiable")
  min_acceptable string? @description("Minimum acceptable value")
  max_acceptable string? @description("Maximum acceptable value")
}

/// A capability being offered in a proposal
class CapabilityOffer {
  capability_id string @description("ID of the capability being offered")
  capability_name string @description("Human-readable name")
  level CapabilityLevel @description("Level of capability being offered")
  parameters OfferedParameter[]? @description("Specific parameter offerings")
  restrictions string[]? @description("Any restrictions on usage")
  estimated_cost float? @description("Estimated cost per use (0.0-1.0 normalized)")
}

/// Level of capability being offered
enum CapabilityLevel {
  FULL @description("Full, unrestricted access")
  STANDARD @description("Standard access with normal limits")
  LIMITED @description("Limited access with restrictions")
  TRIAL @description("Trial access for evaluation")
  MINIMAL @description("Minimal access, basic functionality only")
}

/// A parameter being offered
class OfferedParameter {
  name string @description("Parameter name")
  value string @description("Offered value")
  fixed bool @description("Whether this value is fixed or negotiable")
  alternatives string[]? @description("Alternative values if negotiable")
}

// ============================================
// Evaluation Policy
// ============================================

/// Policy for evaluating proposals
class EvaluationPolicy {
  min_acceptable_terms MinimumTerms @description("Minimum terms we'll accept")
  negotiation_strategy NegotiationStrategyType @description("Our negotiation approach")
  max_counter_offers int @description("Maximum number of counter-offers before rejection")
  auto_accept_threshold float @description("Score threshold for automatic acceptance (0.0-1.0)")
  auto_reject_threshold float @description("Score threshold for automatic rejection (0.0-1.0)")
  scoring_weights ScoringWeights @description("Weights for different scoring factors")
  capability_priorities CapabilityPriority[]? @description("Prioritized capabilities")
  risk_tolerance RiskTolerance @description("How much risk we're willing to accept")
}

/// Minimum acceptable terms
class MinimumTerms {
  min_duration_hours int? @description("Minimum agreement duration")
  max_rate_limit int? @description("Maximum rate limit we'll accept (calls per minute)")
  min_priority_level int? @description("Minimum priority level (1-10)")
  required_capabilities string[] @description("Capabilities that must be included")
  forbidden_terms string[]? @description("Terms we will not accept")
  min_sla_availability float? @description("Minimum SLA availability (0.0-1.0)")
}

/// Negotiation strategy type
enum NegotiationStrategyType {
  COOPERATIVE @description("Maximize mutual benefit, seek win-win")
  COMPETITIVE @description("Maximize own benefit, drive hard bargain")
  PRINCIPLED @description("Use objective criteria, fair standards")
  ACCOMMODATING @description("Prioritize relationship over terms")
  AVOIDING @description("Minimize conflict, make concessions")
}

/// Weights for proposal scoring
class ScoringWeights {
  term_attractiveness float @description("Weight for term attractiveness (default: 0.4)")
  offered_value float @description("Weight for value of capabilities offered (default: 0.3)")
  request_burden float @description("Weight for cost of fulfilling requests (default: 0.3)")
}

/// Priority for a specific capability
class CapabilityPriority {
  capability_id string @description("ID of the capability")
  importance float @description("Importance score (0.0-1.0)")
  acceptable_levels CapabilityLevel[] @description("Acceptable capability levels")
}

/// Risk tolerance settings
class RiskTolerance {
  max_risk_level RiskLevel @description("Maximum acceptable risk level")
  require_mitigation_above RiskLevel @description("Require mitigation plans above this level")
  risk_factor_weights RiskFactorWeights? @description("Weights for different risk factors")
}

/// Weights for different risk factors
class RiskFactorWeights {
  security float @description("Weight for security risks")
  compliance float @description("Weight for compliance risks")
  performance float @description("Weight for performance risks")
  reliability float @description("Weight for reliability risks")
  cost float @description("Weight for cost risks")
}

/// Risk level enumeration (imported from negotiation_protocol)
enum RiskLevel {
  LOW @description("Minimal risk")
  MODERATE @description("Some concerns but manageable")
  HIGH @description("Significant concerns")
  CRITICAL @description("Unacceptable risk")
}

// ============================================
// Gap Analysis
// ============================================

/// Analysis of gaps between proposal and requirements
class GapAnalysis {
  has_gaps bool @description("Whether there are any gaps")
  capability_gaps CapabilityGap[] @description("Gaps in capability offerings")
  term_gaps TermGap[] @description("Gaps in terms")
  constraint_violations ConstraintViolation[] @description("Violated constraints")
  overall_gap_score float @description("Overall gap score (0.0 = no gaps, 1.0 = complete mismatch)")
  bridgeable bool @description("Whether gaps are likely bridgeable through negotiation")
  bridge_difficulty float @description("Difficulty of bridging gaps (0.0-1.0)")
}

/// Gap in a specific capability
class CapabilityGap {
  capability_id string @description("ID of the capability with gap")
  capability_name string @description("Human-readable name")
  gap_type CapabilityGapType @description("Type of gap")
  requested_level string? @description("Level we requested")
  offered_level string? @description("Level offered")
  severity float @description("Severity of the gap (0.0-1.0)")
  suggestion string? @description("Suggestion for addressing the gap")
}

/// Type of capability gap
enum CapabilityGapType {
  MISSING @description("Capability not offered")
  INSUFFICIENT_LEVEL @description("Offered level is insufficient")
  PARAMETER_MISMATCH @description("Parameters don't match requirements")
  RESTRICTION_CONFLICT @description("Restrictions conflict with needs")
}

/// Gap in terms
class TermGap {
  term_name string @description("Name of the term")
  gap_type TermGapType @description("Type of gap")
  requested_value string? @description("Value we requested")
  offered_value string? @description("Value offered")
  severity float @description("Severity of the gap (0.0-1.0)")
  negotiable bool @description("Whether this gap is likely negotiable")
}

/// Type of term gap
enum TermGapType {
  BELOW_MINIMUM @description("Value is below our minimum")
  ABOVE_MAXIMUM @description("Value is above our maximum")
  INCOMPATIBLE @description("Value is fundamentally incompatible")
  MISSING @description("Term is not addressed")
}

/// A constraint that was violated
class ConstraintViolation {
  constraint_id string @description("ID of the violated constraint")
  constraint_description string @description("Description of the constraint")
  violation_description string @description("How the constraint was violated")
  severity float @description("Severity (0.0-1.0)")
  waivable bool @description("Whether this constraint can be waived")
}

// ============================================
// Proposal Scoring
// ============================================

/// Detailed scoring of a proposal
class ProposalScore {
  overall_score float @description("Overall score (0.0-1.0)")
  term_score TermScore @description("Score for terms")
  value_score ValueScore @description("Score for offered value")
  burden_score BurdenScore @description("Score for request burden")
  risk_score RiskScore @description("Score for risk factors")
  breakdown ScoreBreakdown @description("Detailed breakdown")
}

/// Score for proposal terms
class TermScore {
  score float @description("Term attractiveness score (0.0-1.0)")
  duration_score float @description("Score for duration terms")
  rate_limit_score float @description("Score for rate limit terms")
  priority_score float @description("Score for priority terms")
  sla_score float @description("Score for SLA terms")
  billing_score float @description("Score for billing terms")
}

/// Score for offered value
class ValueScore {
  score float @description("Overall value score (0.0-1.0)")
  capability_coverage float @description("How many requested capabilities are covered")
  capability_quality float @description("Quality/level of offered capabilities")
  parameter_match float @description("How well parameters match requests")
}

/// Score for request burden
class BurdenScore {
  score float @description("Overall burden score (0.0-1.0, lower = less burden)")
  fulfillment_difficulty float @description("Difficulty of fulfilling requests")
  resource_cost float @description("Estimated resource cost")
  opportunity_cost float @description("Opportunity cost of commitment")
}

/// Risk score assessment
class RiskScore {
  score float @description("Overall risk score (0.0-1.0, lower = less risk)")
  security_risk float @description("Security-related risks")
  compliance_risk float @description("Compliance-related risks")
  operational_risk float @description("Operational risks")
  reputational_risk float @description("Reputational risks")
}

/// Detailed score breakdown
class ScoreBreakdown {
  strengths string[] @description("Proposal strengths")
  weaknesses string[] @description("Proposal weaknesses")
  opportunities string[] @description("Opportunities for negotiation")
  threats string[] @description("Potential threats/concerns")
}

// ============================================
// Evaluation Result
// ============================================

/// Complete result of proposal evaluation
class ProposalEvaluationResult {
  decision EvaluationDecision @description("Evaluation decision")
  score ProposalScore @description("Detailed scoring")
  gap_analysis GapAnalysis @description("Gap analysis")
  counter_proposal NegotiationProposal? @description("Generated counter-proposal if applicable")
  rationale EvaluationRationale @description("Explanation of decision")
  recommendations string[] @description("Recommendations for next steps")
  confidence float @description("Confidence in this evaluation (0.0-1.0)")
}

/// Evaluation decision
class EvaluationDecision {
  action NegotiationAction @description("Recommended action")
  auto_decided bool @description("Whether decision was made automatically by threshold")
  threshold_triggered string? @description("Which threshold triggered auto-decision")
  requires_human_review bool @description("Whether human review is recommended")
}

/// Rationale for the evaluation decision
class EvaluationRationale {
  summary string @description("Brief summary of decision rationale")
  key_factors string[] @description("Key factors that influenced the decision")
  concerns string[]? @description("Concerns about the proposal")
  positive_aspects string[]? @description("Positive aspects of the proposal")
  trade_offs string[]? @description("Trade-offs considered")
}

// ============================================
// Counter-Proposal Generation
// ============================================

/// Configuration for counter-proposal generation
class CounterProposalConfig {
  strategy NegotiationStrategyType @description("Strategy to use")
  gap_analysis GapAnalysis @description("Gap analysis to address")
  concession_budget float @description("How much we're willing to concede (0.0-1.0)")
  priority_order string[] @description("Order of priority for addressing gaps")
  preserve_terms string[] @description("Terms that should not be changed")
  creative_options bool @description("Whether to suggest creative alternatives")
}

/// Result of counter-proposal generation
class CounterProposalResult {
  proposal NegotiationProposal @description("The generated counter-proposal")
  changes_made ProposalChange[] @description("Changes made from original")
  concessions_offered string[] @description("Concessions we're making")
  concessions_requested string[] @description("Concessions we're requesting")
  expected_acceptance float @description("Expected probability of acceptance (0.0-1.0)")
  rationale string @description("Rationale for this counter-proposal")
}

/// A change made to a proposal
class ProposalChange {
  field string @description("Field that was changed")
  original_value string @description("Original value")
  new_value string @description("New value")
  change_type ChangeType @description("Type of change")
  justification string @description("Why this change was made")
}

/// Type of proposal change
enum ChangeType {
  CONCESSION @description("A concession we're making")
  REQUEST @description("A new request or increased demand")
  CLARIFICATION @description("Clarification of existing terms")
  ADDITION @description("New term or capability added")
  REMOVAL @description("Term or capability removed")
  MODIFICATION @description("Modification of existing term")
}

// ============================================
// AI Functions for Evaluation
// ============================================

/// Evaluate a proposal against policy and capabilities
function EvaluateProposalAgainstPolicy(
  proposal NegotiationProposal,
  session NegotiationSession,
  evaluator_capabilities AgentCapability[],
  evaluation_policy EvaluationPolicy
) -> ProposalEvaluationResult {
  client CustomSonnet4
  prompt #"
    Evaluate this proposal against our policy and capabilities.

    Proposal:
    {{ proposal }}

    Negotiation Session:
    {{ session }}

    Our Capabilities:
    {{ evaluator_capabilities }}

    Evaluation Policy:
    {{ evaluation_policy }}

    Analyze the proposal and provide:
    1. A detailed score based on the scoring weights
    2. A gap analysis identifying any mismatches
    3. A recommended action (accept, counter, reject)
    4. If countering, suggest key changes to make
    5. Clear rationale for the decision

    Consider:
    - Term attractiveness (duration, rate limits, priority, SLA, billing)
    - Value of capabilities offered vs our needs
    - Burden of fulfilling their requests
    - Risk factors and our risk tolerance
    - Whether auto-accept or auto-reject thresholds are met

    {{ ctx.output_format }}
  "#
}

/// Generate an optimal counter-proposal
function GenerateOptimalCounterProposal(
  original_proposal NegotiationProposal,
  gap_analysis GapAnalysis,
  our_capabilities AgentCapability[],
  config CounterProposalConfig
) -> CounterProposalResult {
  client CustomSonnet4
  prompt #"
    Generate an optimal counter-proposal to address the identified gaps.

    Original Proposal:
    {{ original_proposal }}

    Gap Analysis:
    {{ gap_analysis }}

    Our Capabilities:
    {{ our_capabilities }}

    Configuration:
    {{ config }}

    Create a counter-proposal that:
    1. Addresses the most critical gaps first (based on priority_order)
    2. Stays within the concession_budget
    3. Follows the specified negotiation strategy
    4. Preserves any terms listed in preserve_terms
    5. Proposes creative alternatives if creative_options is enabled

    For each change, provide clear justification.
    Estimate the probability that this counter-proposal will be accepted.

    {{ ctx.output_format }}
  "#
}

/// Score a proposal quantitatively
function ScoreProposal(
  proposal NegotiationProposal,
  our_requirements CapabilityRequest[],
  scoring_weights ScoringWeights
) -> ProposalScore {
  client CustomSonnet4
  prompt #"
    Provide a quantitative score for this proposal.

    Proposal:
    {{ proposal }}

    Our Requirements:
    {{ our_requirements }}

    Scoring Weights:
    {{ scoring_weights }}

    Score each dimension from 0.0 to 1.0:
    - Term attractiveness: How favorable are the proposed terms?
    - Offered value: How well do offered capabilities match our needs?
    - Request burden: How costly/difficult are their requests? (lower = better)
    - Risk factors: What are the associated risks? (lower = better)

    Apply the scoring weights to calculate the overall score.
    Provide a SWOT analysis in the breakdown.

    {{ ctx.output_format }}
  "#
}
