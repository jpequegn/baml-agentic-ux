// Contract-Net Protocol Implementation
// BAML types for FIPA Contract-Net protocol task allocation
// Issue #59 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.7)

// Dependencies:
// - AgentIdentity from agent_identity.baml
// - AgentCapability, SchemaDefinition, CostEstimate from agent_capability.baml

// ============================================
// Task Specification
// ============================================

/// Specification of a task for Call for Proposals
class TaskSpecification {
  task_id string @description("Unique identifier for this task")
  task_type string @description("Type/category of the task")
  description string @description("Human-readable task description")
  required_capabilities string[] @description("IDs of capabilities required to perform the task")
  input_schema SchemaDefinition @description("Schema for task input data")
  expected_output_schema SchemaDefinition @description("Schema for expected output")
  constraints TaskConstraint[] @description("Constraints on task execution")
  priority TaskPriority @description("Priority level of the task")
  metadata TaskMetadata? @description("Additional task metadata")
}

/// Priority level for a task
enum TaskPriority {
  LOW @description("Low priority, can be delayed")
  NORMAL @description("Normal priority")
  HIGH @description("High priority, process quickly")
  CRITICAL @description("Critical, must be processed immediately")
}

/// Constraints on task execution
class TaskConstraint {
  constraint_id string @description("Unique identifier for this constraint")
  constraint_type TaskConstraintType @description("Type of constraint")
  description string @description("Human-readable description")
  value string @description("Constraint value")
  required bool @description("Whether this constraint must be satisfied")
}

/// Types of task constraints
enum TaskConstraintType {
  MAX_LATENCY @description("Maximum execution time allowed")
  MIN_QUALITY @description("Minimum quality score required")
  MAX_COST @description("Maximum cost allowed")
  DEADLINE @description("Must complete by specified time")
  LOCATION @description("Geographical or logical location constraint")
  SECURITY @description("Security/compliance requirement")
  RESOURCE @description("Resource usage constraint")
}

/// Additional metadata for a task
class TaskMetadata {
  created_at string @description("ISO 8601 timestamp of task creation")
  created_by string @description("ID of agent that created the task")
  tags string[]? @description("Tags for categorization")
  correlation_id string? @description("ID for correlating related tasks")
  parent_task_id string? @description("ID of parent task if subtask")
}

// ============================================
// Call for Proposals (CFP)
// ============================================

/// Call for Proposals issued by a manager agent
class CallForProposals {
  cfp_id string @description("Unique identifier for this CFP")
  issuer AgentIdentity @description("Agent issuing the CFP")
  task_specification TaskSpecification @description("Specification of the task")
  deadline string @description("ISO 8601 deadline for submitting proposals")
  selection_criteria SelectionCriteria[] @description("Criteria for evaluating proposals")
  target_agents string[]? @description("Specific agent IDs to send CFP to (null = broadcast)")
  min_proposals int? @description("Minimum number of proposals required")
  max_proposals int? @description("Maximum proposals to accept")
  allow_partial bool @description("Whether partial task completion is acceptable")
  cfp_context CFPContext? @description("Additional context for the CFP")
}

/// Context for a Call for Proposals
class CFPContext {
  purpose string @description("Purpose of the CFP")
  urgency CFPUrgency @description("Urgency level")
  budget_hint float? @description("Approximate budget available")
  preferred_start string? @description("Preferred start time (ISO 8601)")
  notes string? @description("Additional notes for bidders")
}

/// Urgency level for CFP
enum CFPUrgency {
  RELAXED @description("No time pressure, best quality preferred")
  NORMAL @description("Standard priority")
  URGENT @description("Quick turnaround needed")
  IMMEDIATE @description("Must be handled immediately")
}

/// Criteria for selecting winning proposal
class SelectionCriteria {
  criteria_id string @description("Unique identifier for this criterion")
  name string @description("Human-readable name")
  description string @description("Description of what's being evaluated")
  weight float @description("Weight of this criterion (0.0-1.0)")
  evaluation_type EvaluationType @description("How to evaluate this criterion")
  target_value string? @description("Target value if applicable")
  min_acceptable string? @description("Minimum acceptable value")
  max_acceptable string? @description("Maximum acceptable value")
}

/// How a criterion is evaluated
enum EvaluationType {
  MINIMIZE @description("Lower is better (e.g., cost, latency)")
  MAXIMIZE @description("Higher is better (e.g., quality, coverage)")
  TARGET @description("Closer to target is better")
  BOOLEAN @description("Pass/fail evaluation")
  QUALITATIVE @description("Subjective quality assessment")
}

// ============================================
// Contract Proposal (Bid)
// ============================================

/// A proposal submitted in response to a CFP
class ContractProposal {
  proposal_id string @description("Unique identifier for this proposal")
  cfp_id string @description("ID of the CFP this responds to")
  proposer AgentIdentity @description("Agent submitting the proposal")
  offered_capabilities AgentCapability[] @description("Capabilities offered for the task")
  cost CostEstimate? @description("Estimated cost for task completion")
  estimated_latency_ms int? @description("Estimated execution time in milliseconds")
  quality_score float? @description("Self-assessed quality score (0.0-1.0)")
  validity_until string @description("ISO 8601 expiry for this proposal")
  commitment_level CommitmentLevel @description("Level of commitment to this proposal")
  conditions ProposalCondition[]? @description("Conditions attached to the proposal")
  execution_plan ExecutionPlan? @description("Proposed execution plan")
}

/// Level of commitment to a proposal
enum CommitmentLevel {
  TENTATIVE @description("Preliminary offer, subject to change")
  CONDITIONAL @description("Committed if conditions are met")
  FIRM @description("Fully committed to these terms")
  GUARANTEED @description("Guaranteed with penalties for non-delivery")
}

/// Condition attached to a proposal
class ProposalCondition {
  condition_id string @description("Unique identifier for this condition")
  condition_type ConditionType @description("Type of condition")
  description string @description("Human-readable description")
  value string @description("Condition value")
  negotiable bool @description("Whether this condition is negotiable")
}

/// Types of proposal conditions
enum ConditionType {
  RESOURCE_AVAILABILITY @description("Depends on resource availability")
  CONCURRENT_LOAD @description("Depends on current workload")
  PREREQUISITE @description("Requires prior conditions to be met")
  EXCLUSIVITY @description("Requires exclusive access/contract")
  TIMING @description("Depends on timing constraints")
  DEPENDENCY @description("Depends on other tasks/agents")
}

/// Proposed execution plan
class ExecutionPlan {
  steps ExecutionStep[] @description("Steps in the execution plan")
  total_estimated_duration_ms int @description("Total estimated duration")
  parallelizable bool @description("Whether steps can be parallelized")
  checkpoints string[]? @description("Checkpoints for progress reporting")
}

/// A step in the execution plan
class ExecutionStep {
  step_number int @description("Sequential step number")
  description string @description("What this step does")
  capability_id string @description("Capability used for this step")
  estimated_duration_ms int @description("Estimated duration of this step")
  dependencies int[]? @description("Step numbers this depends on")
}

// ============================================
// Bid Refusal
// ============================================

/// Refusal to submit a bid
class BidRefusal {
  refusal_id string @description("Unique identifier for this refusal")
  cfp_id string @description("ID of the CFP being refused")
  refusing_agent AgentIdentity @description("Agent refusing to bid")
  reason RefusalReason @description("Primary reason for refusal")
  explanation string @description("Human-readable explanation")
  alternative_suggestion string? @description("Suggested alternative if any")
  available_after string? @description("ISO 8601 timestamp when agent may be available")
}

/// Reasons for refusing to bid
enum RefusalReason {
  LACK_CAPABILITY @description("Don't have required capabilities")
  CAPACITY_EXCEEDED @description("At maximum capacity")
  CONFLICT_OF_INTEREST @description("Conflict of interest exists")
  UNACCEPTABLE_TERMS @description("CFP terms are unacceptable")
  DEADLINE_UNACHIEVABLE @description("Cannot meet the deadline")
  COST_EXCEEDS_BUDGET @description("Cannot complete within budget hint")
  POLICY_RESTRICTION @description("Internal policies prevent bidding")
  TECHNICAL_INCOMPATIBILITY @description("Technical incompatibility with task")
}

// ============================================
// Bid Evaluation
// ============================================

/// Evaluation of all bids for a CFP
class BidEvaluation {
  evaluation_id string @description("Unique identifier for this evaluation")
  cfp_id string @description("ID of the CFP being evaluated")
  evaluated_at string @description("ISO 8601 timestamp of evaluation")
  evaluated_proposals EvaluatedProposal[] @description("All evaluated proposals")
  recommended_winner string? @description("Proposal ID of recommended winner")
  recommendation_rationale string @description("Explanation for the recommendation")
  evaluation_summary EvaluationSummary @description("Summary of the evaluation")
}

/// Evaluation of a single proposal
class EvaluatedProposal {
  proposal_id string @description("ID of the proposal")
  proposer_id string @description("ID of the proposing agent")
  overall_score float @description("Overall weighted score (0.0-1.0)")
  criteria_scores CriteriaScore[] @description("Score for each criterion")
  meets_requirements bool @description("Whether all requirements are met")
  disqualified bool @description("Whether proposal is disqualified")
  disqualification_reason string? @description("Reason for disqualification if any")
  rank int @description("Rank among all proposals (1 = best)")
  strengths string[] @description("Identified strengths")
  weaknesses string[] @description("Identified weaknesses")
  risk_level EvaluationRiskLevel @description("Assessed risk level")
}

/// Score for a specific criterion
class CriteriaScore {
  criteria_id string @description("ID of the criterion")
  raw_value string @description("Raw value from proposal")
  normalized_score float @description("Normalized score (0.0-1.0)")
  weighted_score float @description("Score after applying weight")
  notes string? @description("Evaluation notes")
}

/// Summary of bid evaluation
class EvaluationSummary {
  total_proposals int @description("Total proposals received")
  qualified_proposals int @description("Proposals meeting requirements")
  disqualified_proposals int @description("Proposals disqualified")
  refusals_received int @description("Agents that refused to bid")
  average_score float @description("Average score of qualified proposals")
  score_spread float @description("Spread between best and worst score")
  clear_winner bool @description("Whether there's a clear winner")
  recommendation_confidence float @description("Confidence in recommendation (0.0-1.0)")
}

/// Risk level from evaluation
enum EvaluationRiskLevel {
  MINIMAL @description("Very low risk")
  LOW @description("Acceptable risk")
  MODERATE @description("Some concerns")
  HIGH @description("Significant concerns")
  UNACCEPTABLE @description("Risk too high")
}

// ============================================
// Contract Award
// ============================================

/// Award of a contract to a winning bidder
class ContractAward {
  award_id string @description("Unique identifier for this award")
  cfp_id string @description("ID of the original CFP")
  winning_proposal_id string @description("ID of the winning proposal")
  awarded_to AgentIdentity @description("Agent receiving the contract")
  awarded_by AgentIdentity @description("Agent granting the award")
  awarded_at string @description("ISO 8601 timestamp of award")
  contract_terms AwardedTerms @description("Final contract terms")
  acceptance_deadline string @description("ISO 8601 deadline for accepting the award")
  rejection_notifications AgentNotification[]? @description("Notifications to non-winning bidders")
}

/// Terms of the awarded contract
class AwardedTerms {
  effective_from string @description("ISO 8601 start of contract")
  effective_until string @description("ISO 8601 end of contract")
  agreed_cost CostEstimate? @description("Agreed cost")
  agreed_sla SLATerms? @description("Agreed service level terms")
  modifications string[]? @description("Modifications from original proposal")
  special_conditions string[]? @description("Special conditions")
}

/// Service level agreement terms
class SLATerms {
  max_latency_ms int @description("Maximum allowed latency")
  availability_target float @description("Target availability (0.0-1.0)")
  quality_threshold float @description("Minimum quality threshold (0.0-1.0)")
  penalty_clause string? @description("Penalty for SLA breach")
}

/// Notification to an agent
class AgentNotification {
  agent_id string @description("ID of agent being notified")
  notification_type NotificationType @description("Type of notification")
  message string @description("Notification message")
  sent_at string @description("ISO 8601 timestamp when sent")
}

/// Types of notifications
enum NotificationType {
  AWARD_GRANTED @description("Contract has been awarded to you")
  AWARD_DECLINED @description("Your proposal was not selected")
  CFP_CANCELLED @description("The CFP has been cancelled")
  CFP_EXTENDED @description("CFP deadline has been extended")
  CLARIFICATION @description("Clarification provided")
}

// ============================================
// Contract Confirmation
// ============================================

/// Confirmation or rejection of a contract award
class ContractConfirmation {
  confirmation_id string @description("Unique identifier for this confirmation")
  award_id string @description("ID of the award being confirmed/rejected")
  confirmed bool @description("Whether the award is accepted")
  confirmed_by AgentIdentity @description("Agent confirming/rejecting")
  confirmed_at string @description("ISO 8601 timestamp")
  rejection_reason string? @description("Reason if rejecting")
  counter_terms AwardedTerms? @description("Counter-terms if negotiating")
  execution_commitment ExecutionCommitment? @description("Commitment details if accepting")
}

/// Commitment for contract execution
class ExecutionCommitment {
  start_time string @description("ISO 8601 planned start time")
  estimated_completion string @description("ISO 8601 estimated completion")
  progress_reporting_interval_ms int @description("How often to report progress")
  contact_endpoint string @description("Endpoint for communication during execution")
}

// ============================================
// Execution and Results
// ============================================

/// Progress report during task execution
class TaskProgressReport {
  report_id string @description("Unique identifier for this report")
  contract_id string @description("ID of the contract")
  reported_at string @description("ISO 8601 timestamp")
  progress_percentage float @description("Completion percentage (0.0-100.0)")
  current_step int @description("Current step number")
  status ContractExecutionStatus @description("Current execution status")
  issues ExecutionIssue[]? @description("Any issues encountered")
  estimated_remaining_ms int? @description("Estimated time remaining")
}

/// Status of task execution
enum ContractExecutionStatus {
  NOT_STARTED @description("Execution has not begun")
  IN_PROGRESS @description("Execution is ongoing")
  PAUSED @description("Execution is paused")
  COMPLETED @description("Execution completed successfully")
  FAILED @description("Execution failed")
  CANCELLED @description("Execution was cancelled")
}

/// Issue encountered during execution
class ExecutionIssue {
  issue_id string @description("Unique identifier for this issue")
  severity ContractIssueSeverity @description("Severity of the issue")
  description string @description("Description of the issue")
  impact string @description("Impact on task completion")
  resolution string? @description("Resolution if resolved")
}

/// Severity of an execution issue
enum ContractIssueSeverity {
  INFO @description("Informational, no impact")
  WARNING @description("Minor issue, task can continue")
  ERROR @description("Significant issue, may impact completion")
  CRITICAL @description("Critical issue, task may fail")
}

/// Final result of task execution
class TaskExecutionResult {
  result_id string @description("Unique identifier for this result")
  contract_id string @description("ID of the contract")
  completed_at string @description("ISO 8601 completion timestamp")
  status ContractExecutionStatus @description("Final status")
  output string? @description("Task output as JSON string")
  actual_cost CostEstimate? @description("Actual cost incurred")
  actual_latency_ms int @description("Actual execution time")
  quality_metrics ContractQualityMetrics? @description("Quality measurements")
  summary string @description("Human-readable summary of results")
}

/// Quality metrics for task execution
class ContractQualityMetrics {
  accuracy float? @description("Accuracy score (0.0-1.0)")
  completeness float? @description("Completeness score (0.0-1.0)")
  consistency float? @description("Consistency score (0.0-1.0)")
  custom_metrics CriteriaScore[]? @description("Custom quality metrics")
}

// ============================================
// Contract-Net Protocol State
// ============================================

/// Overall state of a Contract-Net interaction
class ContractNetSession {
  session_id string @description("Unique identifier for this session")
  cfp CallForProposals @description("The Call for Proposals")
  proposals ContractProposal[] @description("Received proposals")
  refusals BidRefusal[] @description("Received refusals")
  evaluation BidEvaluation? @description("Bid evaluation if completed")
  award ContractAward? @description("Contract award if made")
  confirmation ContractConfirmation? @description("Award confirmation if received")
  progress_reports TaskProgressReport[] @description("Progress reports during execution")
  result TaskExecutionResult? @description("Final result if completed")
  status ContractNetStatus @description("Current protocol status")
  created_at string @description("ISO 8601 creation timestamp")
  updated_at string @description("ISO 8601 last update timestamp")
}

/// Status of the Contract-Net protocol
enum ContractNetStatus {
  CFP_ISSUED @description("CFP has been issued, awaiting proposals")
  COLLECTING_PROPOSALS @description("Collecting proposals from agents")
  EVALUATING_BIDS @description("Evaluating received proposals")
  AWARDING_CONTRACT @description("Awarding contract to winner")
  AWAITING_CONFIRMATION @description("Waiting for winner to confirm")
  CONTRACT_ACTIVE @description("Contract is being executed")
  COMPLETED @description("Task completed successfully")
  FAILED @description("Protocol failed (no proposals, rejection, etc.)")
  CANCELLED @description("Protocol was cancelled")
}

// ============================================
// AI Functions for Contract-Net
// ============================================

/// Issue a Call for Proposals
function IssueCallForProposals(
  issuer: AgentIdentity,
  task: TaskSpecification,
  target_agents: string[]?,
  deadline_seconds: int,
  selection_criteria: SelectionCriteria[]
) -> CallForProposals {
  client CustomSonnet4
  prompt #"
    Create a Call for Proposals (CFP) for the given task.

    Issuer: {{ issuer }}
    Task Specification: {{ task }}
    Target Agents: {{ target_agents }}
    Deadline (seconds from now): {{ deadline_seconds }}
    Selection Criteria: {{ selection_criteria }}

    Generate a well-structured CFP that:
    1. Clearly describes the task requirements
    2. Specifies how proposals will be evaluated
    3. Sets appropriate deadlines
    4. Provides enough context for agents to bid effectively

    {{ ctx.output_format }}
  "#
}

/// Evaluate all bids for a CFP
function EvaluateBids(
  cfp: CallForProposals,
  proposals: ContractProposal[],
  refusals: BidRefusal[]?
) -> BidEvaluation {
  client CustomSonnet4
  prompt #"
    Evaluate all proposals submitted for this Call for Proposals.

    CFP: {{ cfp }}
    Proposals Received: {{ proposals }}
    Refusals Received: {{ refusals }}

    For each proposal:
    1. Score against each selection criterion
    2. Identify strengths and weaknesses
    3. Assess risk level
    4. Determine if it meets minimum requirements

    Then:
    1. Rank all qualified proposals
    2. Recommend a winner (or indicate no suitable proposals)
    3. Provide detailed rationale for the recommendation

    {{ ctx.output_format }}
  "#
}

/// Generate a contract proposal for a CFP
function GenerateContractProposal(
  cfp: CallForProposals,
  proposer: AgentIdentity,
  available_capabilities: AgentCapability[],
  cost_constraints: CostEstimate?
) -> ContractProposal {
  client CustomSonnet4
  prompt #"
    Generate a competitive contract proposal for this CFP.

    CFP: {{ cfp }}
    Proposer: {{ proposer }}
    Available Capabilities: {{ available_capabilities }}
    Cost Constraints: {{ cost_constraints }}

    Create a proposal that:
    1. Addresses all required capabilities from the CFP
    2. Proposes realistic cost and time estimates
    3. Highlights competitive advantages
    4. Includes an execution plan
    5. Sets appropriate conditions if needed

    {{ ctx.output_format }}
  "#
}

/// Decide whether to submit a bid or refuse
function DecideToBid(
  cfp: CallForProposals,
  agent_identity: AgentIdentity,
  available_capabilities: AgentCapability[],
  current_workload: float,
  policy_constraints: string[]?
) -> BidDecision {
  client CustomSonnet4
  prompt #"
    Decide whether to submit a bid for this CFP.

    CFP: {{ cfp }}
    Our Identity: {{ agent_identity }}
    Available Capabilities: {{ available_capabilities }}
    Current Workload (0.0-1.0): {{ current_workload }}
    Policy Constraints: {{ policy_constraints }}

    Analyze:
    1. Do we have the required capabilities?
    2. Can we meet the deadline?
    3. Is the workload manageable?
    4. Are there any policy conflicts?

    Recommend whether to bid or refuse, with detailed reasoning.

    {{ ctx.output_format }}
  "#
}

/// Result of bid decision
class BidDecision {
  should_bid bool @description("Whether to submit a bid")
  confidence float @description("Confidence in this decision (0.0-1.0)")
  reasoning string @description("Explanation for the decision")
  capability_coverage float @description("How well we cover required capabilities (0.0-1.0)")
  refusal_reason RefusalReason? @description("If not bidding, the primary reason")
  suggested_conditions string[]? @description("Conditions to attach if bidding")
}
