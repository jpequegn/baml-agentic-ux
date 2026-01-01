"""
Contract-Net Protocol Implementation

FIPA Contract-Net protocol for task allocation via Call for Proposals (CFP)
and bid evaluation.

Issue #59 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.7)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


# ============================================
# Enums
# ============================================


class TaskPriority(Enum):
    """Priority level for a task."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskConstraintType(Enum):
    """Types of task constraints."""

    MAX_LATENCY = "max_latency"
    MIN_QUALITY = "min_quality"
    MAX_COST = "max_cost"
    DEADLINE = "deadline"
    LOCATION = "location"
    SECURITY = "security"
    RESOURCE = "resource"


class CFPUrgency(Enum):
    """Urgency level for CFP."""

    RELAXED = "relaxed"
    NORMAL = "normal"
    URGENT = "urgent"
    IMMEDIATE = "immediate"


class EvaluationType(Enum):
    """How a criterion is evaluated."""

    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
    TARGET = "target"
    BOOLEAN = "boolean"
    QUALITATIVE = "qualitative"


class CommitmentLevel(Enum):
    """Level of commitment to a proposal."""

    TENTATIVE = "tentative"
    CONDITIONAL = "conditional"
    FIRM = "firm"
    GUARANTEED = "guaranteed"


class ConditionType(Enum):
    """Types of proposal conditions."""

    RESOURCE_AVAILABILITY = "resource_availability"
    CONCURRENT_LOAD = "concurrent_load"
    PREREQUISITE = "prerequisite"
    EXCLUSIVITY = "exclusivity"
    TIMING = "timing"
    DEPENDENCY = "dependency"


class RefusalReason(Enum):
    """Reasons for refusing to bid."""

    LACK_CAPABILITY = "lack_capability"
    CAPACITY_EXCEEDED = "capacity_exceeded"
    CONFLICT_OF_INTEREST = "conflict_of_interest"
    UNACCEPTABLE_TERMS = "unacceptable_terms"
    DEADLINE_UNACHIEVABLE = "deadline_unachievable"
    COST_EXCEEDS_BUDGET = "cost_exceeds_budget"
    POLICY_RESTRICTION = "policy_restriction"
    TECHNICAL_INCOMPATIBILITY = "technical_incompatibility"


class EvaluationRiskLevel(Enum):
    """Risk level from evaluation."""

    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    UNACCEPTABLE = "unacceptable"


class NotificationType(Enum):
    """Types of notifications."""

    AWARD_GRANTED = "award_granted"
    AWARD_DECLINED = "award_declined"
    CFP_CANCELLED = "cfp_cancelled"
    CFP_EXTENDED = "cfp_extended"
    CLARIFICATION = "clarification"


class ExecutionStatus(Enum):
    """Status of task execution."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IssueSeverity(Enum):
    """Severity of an execution issue."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ContractNetStatus(Enum):
    """Status of the Contract-Net protocol."""

    CFP_ISSUED = "cfp_issued"
    COLLECTING_PROPOSALS = "collecting_proposals"
    EVALUATING_BIDS = "evaluating_bids"
    AWARDING_CONTRACT = "awarding_contract"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    CONTRACT_ACTIVE = "contract_active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================
# Task Specification Types
# ============================================


@dataclass
class TaskConstraint:
    """Constraints on task execution."""

    constraint_id: str
    constraint_type: TaskConstraintType
    description: str
    value: str
    required: bool = True


@dataclass
class TaskMetadata:
    """Additional metadata for a task."""

    created_at: str
    created_by: str
    tags: Optional[List[str]] = None
    correlation_id: Optional[str] = None
    parent_task_id: Optional[str] = None


@dataclass
class SchemaDefinition:
    """Schema for task input/output (simplified)."""

    schema_type: str
    description: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    required: Optional[List[str]] = None


@dataclass
class TaskSpecification:
    """Specification of a task for Call for Proposals."""

    task_id: str
    task_type: str
    description: str
    required_capabilities: List[str]
    input_schema: SchemaDefinition
    expected_output_schema: SchemaDefinition
    constraints: List[TaskConstraint] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.NORMAL
    metadata: Optional[TaskMetadata] = None


# ============================================
# Call for Proposals Types
# ============================================


@dataclass
class SelectionCriteria:
    """Criteria for selecting winning proposal."""

    criteria_id: str
    name: str
    description: str
    weight: float
    evaluation_type: EvaluationType
    target_value: Optional[str] = None
    min_acceptable: Optional[str] = None
    max_acceptable: Optional[str] = None


@dataclass
class CFPContext:
    """Context for a Call for Proposals."""

    purpose: str
    urgency: CFPUrgency = CFPUrgency.NORMAL
    budget_hint: Optional[float] = None
    preferred_start: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class AgentIdentity:
    """Agent identity (simplified for this module)."""

    agent_id: str
    name: str
    version: str
    description: str
    provider: Optional[str] = None


@dataclass
class CallForProposals:
    """Call for Proposals issued by a manager agent."""

    cfp_id: str
    issuer: AgentIdentity
    task_specification: TaskSpecification
    deadline: str
    selection_criteria: List[SelectionCriteria]
    target_agents: Optional[List[str]] = None
    min_proposals: Optional[int] = None
    max_proposals: Optional[int] = None
    allow_partial: bool = False
    cfp_context: Optional[CFPContext] = None


# ============================================
# Contract Proposal Types
# ============================================


@dataclass
class CostEstimate:
    """Estimated cost for task completion."""

    currency: str = "USD"
    per_invocation: float = 0.0
    per_input_unit: Optional[float] = None
    per_output_unit: Optional[float] = None
    unit_type: Optional[str] = None


@dataclass
class ProposalCondition:
    """Condition attached to a proposal."""

    condition_id: str
    condition_type: ConditionType
    description: str
    value: str
    negotiable: bool = True


@dataclass
class ExecutionStep:
    """A step in the execution plan."""

    step_number: int
    description: str
    capability_id: str
    estimated_duration_ms: int
    dependencies: Optional[List[int]] = None


@dataclass
class ExecutionPlan:
    """Proposed execution plan."""

    steps: List[ExecutionStep]
    total_estimated_duration_ms: int
    parallelizable: bool = False
    checkpoints: Optional[List[str]] = None


@dataclass
class AgentCapability:
    """Agent capability (simplified for this module)."""

    capability_id: str
    name: str
    description: str
    capability_type: str


@dataclass
class ContractProposal:
    """A proposal submitted in response to a CFP."""

    proposal_id: str
    cfp_id: str
    proposer: AgentIdentity
    offered_capabilities: List[AgentCapability]
    validity_until: str
    commitment_level: CommitmentLevel = CommitmentLevel.FIRM
    cost: Optional[CostEstimate] = None
    estimated_latency_ms: Optional[int] = None
    quality_score: Optional[float] = None
    conditions: Optional[List[ProposalCondition]] = None
    execution_plan: Optional[ExecutionPlan] = None


# ============================================
# Bid Refusal Types
# ============================================


@dataclass
class BidRefusal:
    """Refusal to submit a bid."""

    refusal_id: str
    cfp_id: str
    refusing_agent: AgentIdentity
    reason: RefusalReason
    explanation: str
    alternative_suggestion: Optional[str] = None
    available_after: Optional[str] = None


# ============================================
# Bid Evaluation Types
# ============================================


@dataclass
class CriteriaScore:
    """Score for a specific criterion."""

    criteria_id: str
    raw_value: str
    normalized_score: float
    weighted_score: float
    notes: Optional[str] = None


@dataclass
class EvaluatedProposal:
    """Evaluation of a single proposal."""

    proposal_id: str
    proposer_id: str
    overall_score: float
    criteria_scores: List[CriteriaScore]
    meets_requirements: bool
    rank: int
    strengths: List[str]
    weaknesses: List[str]
    risk_level: EvaluationRiskLevel
    disqualified: bool = False
    disqualification_reason: Optional[str] = None


@dataclass
class EvaluationSummary:
    """Summary of bid evaluation."""

    total_proposals: int
    qualified_proposals: int
    disqualified_proposals: int
    refusals_received: int
    average_score: float
    score_spread: float
    clear_winner: bool
    recommendation_confidence: float


@dataclass
class BidEvaluation:
    """Evaluation of all bids for a CFP."""

    evaluation_id: str
    cfp_id: str
    evaluated_at: str
    evaluated_proposals: List[EvaluatedProposal]
    recommendation_rationale: str
    evaluation_summary: EvaluationSummary
    recommended_winner: Optional[str] = None


# ============================================
# Contract Award Types
# ============================================


@dataclass
class SLATerms:
    """Service level agreement terms."""

    max_latency_ms: int
    availability_target: float
    quality_threshold: float
    penalty_clause: Optional[str] = None


@dataclass
class AwardedTerms:
    """Terms of the awarded contract."""

    effective_from: str
    effective_until: str
    agreed_cost: Optional[CostEstimate] = None
    agreed_sla: Optional[SLATerms] = None
    modifications: Optional[List[str]] = None
    special_conditions: Optional[List[str]] = None


@dataclass
class AgentNotification:
    """Notification to an agent."""

    agent_id: str
    notification_type: NotificationType
    message: str
    sent_at: str


@dataclass
class ContractAward:
    """Award of a contract to a winning bidder."""

    award_id: str
    cfp_id: str
    winning_proposal_id: str
    awarded_to: AgentIdentity
    awarded_by: AgentIdentity
    awarded_at: str
    contract_terms: AwardedTerms
    acceptance_deadline: str
    rejection_notifications: Optional[List[AgentNotification]] = None


# ============================================
# Contract Confirmation Types
# ============================================


@dataclass
class ExecutionCommitment:
    """Commitment for contract execution."""

    start_time: str
    estimated_completion: str
    progress_reporting_interval_ms: int
    contact_endpoint: str


@dataclass
class ContractConfirmation:
    """Confirmation or rejection of a contract award."""

    confirmation_id: str
    award_id: str
    confirmed: bool
    confirmed_by: AgentIdentity
    confirmed_at: str
    rejection_reason: Optional[str] = None
    counter_terms: Optional[AwardedTerms] = None
    execution_commitment: Optional[ExecutionCommitment] = None


# ============================================
# Execution and Results Types
# ============================================


@dataclass
class ExecutionIssue:
    """Issue encountered during execution."""

    issue_id: str
    severity: IssueSeverity
    description: str
    impact: str
    resolution: Optional[str] = None


@dataclass
class TaskProgressReport:
    """Progress report during task execution."""

    report_id: str
    contract_id: str
    reported_at: str
    progress_percentage: float
    current_step: int
    status: ExecutionStatus
    issues: Optional[List[ExecutionIssue]] = None
    estimated_remaining_ms: Optional[int] = None


@dataclass
class QualityMetrics:
    """Quality metrics for task execution."""

    accuracy: Optional[float] = None
    completeness: Optional[float] = None
    consistency: Optional[float] = None
    custom_metrics: Optional[List[CriteriaScore]] = None


@dataclass
class TaskExecutionResult:
    """Final result of task execution."""

    result_id: str
    contract_id: str
    completed_at: str
    status: ExecutionStatus
    actual_latency_ms: int
    summary: str
    output: Optional[str] = None
    actual_cost: Optional[CostEstimate] = None
    quality_metrics: Optional[QualityMetrics] = None


# ============================================
# Contract-Net Session
# ============================================


@dataclass
class ContractNetSession:
    """Overall state of a Contract-Net interaction."""

    session_id: str
    cfp: CallForProposals
    status: ContractNetStatus
    created_at: str
    updated_at: str
    proposals: List[ContractProposal] = field(default_factory=list)
    refusals: List[BidRefusal] = field(default_factory=list)
    evaluation: Optional[BidEvaluation] = None
    award: Optional[ContractAward] = None
    confirmation: Optional[ContractConfirmation] = None
    progress_reports: List[TaskProgressReport] = field(default_factory=list)
    result: Optional[TaskExecutionResult] = None


# ============================================
# Bid Decision
# ============================================


@dataclass
class BidDecision:
    """Result of bid decision."""

    should_bid: bool
    confidence: float
    reasoning: str
    capability_coverage: float
    refusal_reason: Optional[RefusalReason] = None
    suggested_conditions: Optional[List[str]] = None


# ============================================
# Contract-Net Protocol Manager
# ============================================


class ContractNetProtocol:
    """
    Manager for Contract-Net protocol interactions.

    Implements the FIPA Contract-Net protocol flow:
    1. Manager issues CFP with task spec and deadline
    2. Contractors respond with proposals (or refuse)
    3. Manager evaluates bids against criteria
    4. Manager awards contract to best bidder
    5. Contractor confirms and executes
    6. Results reported back
    """

    # Valid status transitions
    VALID_TRANSITIONS: Dict[ContractNetStatus, List[ContractNetStatus]] = {
        ContractNetStatus.CFP_ISSUED: [
            ContractNetStatus.COLLECTING_PROPOSALS,
            ContractNetStatus.CANCELLED,
        ],
        ContractNetStatus.COLLECTING_PROPOSALS: [
            ContractNetStatus.EVALUATING_BIDS,
            ContractNetStatus.FAILED,
            ContractNetStatus.CANCELLED,
        ],
        ContractNetStatus.EVALUATING_BIDS: [
            ContractNetStatus.AWARDING_CONTRACT,
            ContractNetStatus.FAILED,
            ContractNetStatus.CANCELLED,
        ],
        ContractNetStatus.AWARDING_CONTRACT: [
            ContractNetStatus.AWAITING_CONFIRMATION,
            ContractNetStatus.FAILED,
            ContractNetStatus.CANCELLED,
        ],
        ContractNetStatus.AWAITING_CONFIRMATION: [
            ContractNetStatus.CONTRACT_ACTIVE,
            ContractNetStatus.FAILED,
            ContractNetStatus.CANCELLED,
        ],
        ContractNetStatus.CONTRACT_ACTIVE: [
            ContractNetStatus.COMPLETED,
            ContractNetStatus.FAILED,
            ContractNetStatus.CANCELLED,
        ],
        ContractNetStatus.COMPLETED: [],
        ContractNetStatus.FAILED: [],
        ContractNetStatus.CANCELLED: [],
    }

    def __init__(self) -> None:
        """Initialize the Contract-Net protocol manager."""
        self._sessions: Dict[str, ContractNetSession] = {}

    def issue_cfp(
        self,
        issuer: AgentIdentity,
        task_specification: TaskSpecification,
        selection_criteria: List[SelectionCriteria],
        deadline_seconds: int,
        target_agents: Optional[List[str]] = None,
        min_proposals: Optional[int] = None,
        max_proposals: Optional[int] = None,
        allow_partial: bool = False,
        context: Optional[CFPContext] = None,
    ) -> ContractNetSession:
        """
        Issue a Call for Proposals.

        Args:
            issuer: Agent issuing the CFP
            task_specification: Specification of the task
            selection_criteria: Criteria for evaluating proposals
            deadline_seconds: Seconds until deadline
            target_agents: Specific agents to target (None = broadcast)
            min_proposals: Minimum proposals required
            max_proposals: Maximum proposals to accept
            allow_partial: Whether partial completion is acceptable
            context: Additional context

        Returns:
            New ContractNetSession
        """
        now = datetime.utcnow()
        deadline = now + timedelta(seconds=deadline_seconds)

        cfp = CallForProposals(
            cfp_id=f"cfp-{uuid.uuid4().hex[:12]}",
            issuer=issuer,
            task_specification=task_specification,
            deadline=deadline.isoformat() + "Z",
            selection_criteria=selection_criteria,
            target_agents=target_agents,
            min_proposals=min_proposals,
            max_proposals=max_proposals,
            allow_partial=allow_partial,
            cfp_context=context,
        )

        session = ContractNetSession(
            session_id=f"cns-{uuid.uuid4().hex[:12]}",
            cfp=cfp,
            status=ContractNetStatus.CFP_ISSUED,
            created_at=now.isoformat() + "Z",
            updated_at=now.isoformat() + "Z",
        )

        self._sessions[session.session_id] = session
        return session

    def start_collecting_proposals(
        self, session_id: str
    ) -> ContractNetSession:
        """
        Transition to collecting proposals state.

        Args:
            session_id: Session to transition

        Returns:
            Updated session

        Raises:
            ValueError: If transition is not valid
        """
        return self._transition_status(
            session_id, ContractNetStatus.COLLECTING_PROPOSALS
        )

    def submit_proposal(
        self,
        session_id: str,
        proposer: AgentIdentity,
        offered_capabilities: List[AgentCapability],
        validity_seconds: int,
        commitment_level: CommitmentLevel = CommitmentLevel.FIRM,
        cost: Optional[CostEstimate] = None,
        estimated_latency_ms: Optional[int] = None,
        quality_score: Optional[float] = None,
        conditions: Optional[List[ProposalCondition]] = None,
        execution_plan: Optional[ExecutionPlan] = None,
    ) -> ContractProposal:
        """
        Submit a proposal for a CFP.

        Args:
            session_id: Session to submit to
            proposer: Agent submitting the proposal
            offered_capabilities: Capabilities being offered
            validity_seconds: Seconds until proposal expires
            commitment_level: Level of commitment
            cost: Estimated cost
            estimated_latency_ms: Estimated execution time
            quality_score: Self-assessed quality score
            conditions: Conditions attached to proposal
            execution_plan: Proposed execution plan

        Returns:
            Created proposal

        Raises:
            ValueError: If session not found or not accepting proposals
        """
        session = self._get_session(session_id)

        if session.status not in [
            ContractNetStatus.CFP_ISSUED,
            ContractNetStatus.COLLECTING_PROPOSALS,
        ]:
            raise ValueError(
                f"Session {session_id} is not accepting proposals "
                f"(status: {session.status.value})"
            )

        # Check deadline
        deadline = datetime.fromisoformat(
            session.cfp.deadline.replace("Z", "+00:00")
        )
        now = datetime.utcnow().replace(tzinfo=deadline.tzinfo)
        if now > deadline:
            raise ValueError("CFP deadline has passed")

        # Check max proposals
        if (
            session.cfp.max_proposals is not None
            and len(session.proposals) >= session.cfp.max_proposals
        ):
            raise ValueError("Maximum number of proposals reached")

        validity = datetime.utcnow() + timedelta(seconds=validity_seconds)

        proposal = ContractProposal(
            proposal_id=f"prop-{uuid.uuid4().hex[:12]}",
            cfp_id=session.cfp.cfp_id,
            proposer=proposer,
            offered_capabilities=offered_capabilities,
            validity_until=validity.isoformat() + "Z",
            commitment_level=commitment_level,
            cost=cost,
            estimated_latency_ms=estimated_latency_ms,
            quality_score=quality_score,
            conditions=conditions,
            execution_plan=execution_plan,
        )

        session.proposals.append(proposal)
        session.updated_at = datetime.utcnow().isoformat() + "Z"

        return proposal

    def submit_refusal(
        self,
        session_id: str,
        refusing_agent: AgentIdentity,
        reason: RefusalReason,
        explanation: str,
        alternative_suggestion: Optional[str] = None,
        available_after: Optional[str] = None,
    ) -> BidRefusal:
        """
        Submit a refusal to bid.

        Args:
            session_id: Session to refuse
            refusing_agent: Agent refusing
            reason: Primary reason for refusal
            explanation: Detailed explanation
            alternative_suggestion: Suggested alternative
            available_after: When agent may be available

        Returns:
            Created refusal

        Raises:
            ValueError: If session not found or not accepting responses
        """
        session = self._get_session(session_id)

        if session.status not in [
            ContractNetStatus.CFP_ISSUED,
            ContractNetStatus.COLLECTING_PROPOSALS,
        ]:
            raise ValueError(
                f"Session {session_id} is not accepting responses "
                f"(status: {session.status.value})"
            )

        refusal = BidRefusal(
            refusal_id=f"ref-{uuid.uuid4().hex[:12]}",
            cfp_id=session.cfp.cfp_id,
            refusing_agent=refusing_agent,
            reason=reason,
            explanation=explanation,
            alternative_suggestion=alternative_suggestion,
            available_after=available_after,
        )

        session.refusals.append(refusal)
        session.updated_at = datetime.utcnow().isoformat() + "Z"

        return refusal

    def evaluate_bids(self, session_id: str) -> BidEvaluation:
        """
        Evaluate all bids and determine a winner.

        Args:
            session_id: Session to evaluate

        Returns:
            Bid evaluation result

        Raises:
            ValueError: If session not ready for evaluation
        """
        session = self._get_session(session_id)

        # Transition to evaluating state
        self._transition_status(session_id, ContractNetStatus.EVALUATING_BIDS)

        # Check minimum proposals
        if (
            session.cfp.min_proposals is not None
            and len(session.proposals) < session.cfp.min_proposals
        ):
            session.status = ContractNetStatus.FAILED
            session.updated_at = datetime.utcnow().isoformat() + "Z"
            raise ValueError(
                f"Minimum proposals ({session.cfp.min_proposals}) not met. "
                f"Received: {len(session.proposals)}"
            )

        # Evaluate each proposal
        evaluated_proposals: List[EvaluatedProposal] = []
        for proposal in session.proposals:
            evaluated = self._evaluate_proposal(
                proposal, session.cfp.selection_criteria
            )
            evaluated_proposals.append(evaluated)

        # Sort by score (descending)
        evaluated_proposals.sort(key=lambda x: x.overall_score, reverse=True)

        # Assign ranks
        for i, ep in enumerate(evaluated_proposals):
            ep.rank = i + 1

        # Find winner
        qualified = [ep for ep in evaluated_proposals if ep.meets_requirements]
        recommended_winner = qualified[0].proposal_id if qualified else None

        # Calculate summary
        qualified_count = len(qualified)
        disqualified_count = len(
            [ep for ep in evaluated_proposals if ep.disqualified]
        )
        scores = [ep.overall_score for ep in qualified] if qualified else [0.0]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        score_spread = max(scores) - min(scores) if len(scores) > 1 else 0.0

        # Determine if there's a clear winner (>10% margin over second place)
        clear_winner = False
        if len(qualified) >= 2:
            margin = qualified[0].overall_score - qualified[1].overall_score
            clear_winner = margin > 0.1

        summary = EvaluationSummary(
            total_proposals=len(session.proposals),
            qualified_proposals=qualified_count,
            disqualified_proposals=disqualified_count,
            refusals_received=len(session.refusals),
            average_score=avg_score,
            score_spread=score_spread,
            clear_winner=clear_winner,
            recommendation_confidence=0.9 if clear_winner else 0.6,
        )

        # Build rationale
        if recommended_winner:
            winner_eval = next(
                ep
                for ep in evaluated_proposals
                if ep.proposal_id == recommended_winner
            )
            rationale = (
                f"Recommended {recommended_winner} with score "
                f"{winner_eval.overall_score:.2f}. "
                f"Strengths: {', '.join(winner_eval.strengths[:3])}."
            )
        else:
            rationale = "No proposals met all requirements."

        evaluation = BidEvaluation(
            evaluation_id=f"eval-{uuid.uuid4().hex[:12]}",
            cfp_id=session.cfp.cfp_id,
            evaluated_at=datetime.utcnow().isoformat() + "Z",
            evaluated_proposals=evaluated_proposals,
            recommended_winner=recommended_winner,
            recommendation_rationale=rationale,
            evaluation_summary=summary,
        )

        session.evaluation = evaluation
        session.updated_at = datetime.utcnow().isoformat() + "Z"

        return evaluation

    def _evaluate_proposal(
        self,
        proposal: ContractProposal,
        criteria: List[SelectionCriteria],
    ) -> EvaluatedProposal:
        """
        Evaluate a single proposal against selection criteria.

        Args:
            proposal: Proposal to evaluate
            criteria: Selection criteria

        Returns:
            Evaluated proposal
        """
        criteria_scores: List[CriteriaScore] = []
        total_weighted_score = 0.0
        total_weight = sum(c.weight for c in criteria)

        strengths: List[str] = []
        weaknesses: List[str] = []
        meets_requirements = True

        for criterion in criteria:
            raw_value, normalized, notes = self._score_criterion(
                proposal, criterion
            )

            weighted = normalized * (criterion.weight / total_weight)
            total_weighted_score += weighted

            criteria_scores.append(
                CriteriaScore(
                    criteria_id=criterion.criteria_id,
                    raw_value=raw_value,
                    normalized_score=normalized,
                    weighted_score=weighted,
                    notes=notes,
                )
            )

            # Track strengths/weaknesses
            if normalized >= 0.8:
                strengths.append(f"Excellent {criterion.name}")
            elif normalized <= 0.3:
                weaknesses.append(f"Poor {criterion.name}")

            # Check minimum requirements
            if (
                criterion.min_acceptable
                and criterion.evaluation_type == EvaluationType.MAXIMIZE
            ):
                try:
                    if float(raw_value) < float(criterion.min_acceptable):
                        meets_requirements = False
                except ValueError:
                    pass

        # Assess risk
        risk_level = self._assess_risk(proposal, criteria_scores)

        # Check for disqualification
        disqualified = False
        disqualification_reason = None
        if proposal.commitment_level == CommitmentLevel.TENTATIVE:
            disqualified = True
            disqualification_reason = "Tentative commitment not acceptable"
            meets_requirements = False

        return EvaluatedProposal(
            proposal_id=proposal.proposal_id,
            proposer_id=proposal.proposer.agent_id,
            overall_score=total_weighted_score,
            criteria_scores=criteria_scores,
            meets_requirements=meets_requirements,
            rank=0,  # Will be set later
            strengths=strengths,
            weaknesses=weaknesses,
            risk_level=risk_level,
            disqualified=disqualified,
            disqualification_reason=disqualification_reason,
        )

    def _score_criterion(
        self,
        proposal: ContractProposal,
        criterion: SelectionCriteria,
    ) -> tuple[str, float, Optional[str]]:
        """
        Score a proposal against a single criterion.

        Args:
            proposal: Proposal to score
            criterion: Criterion to evaluate

        Returns:
            Tuple of (raw_value, normalized_score, notes)
        """
        raw_value = "0"
        normalized = 0.5
        notes = None

        name_lower = criterion.name.lower()

        if "cost" in name_lower:
            if proposal.cost:
                raw_value = str(proposal.cost.per_invocation)
                # Lower cost is better
                if criterion.evaluation_type == EvaluationType.MINIMIZE:
                    max_val = float(criterion.max_acceptable or "1.0")
                    cost_val = proposal.cost.per_invocation
                    normalized = max(0.0, 1.0 - (cost_val / max_val))
                else:
                    normalized = 0.5

        elif "latency" in name_lower or "time" in name_lower:
            if proposal.estimated_latency_ms:
                raw_value = str(proposal.estimated_latency_ms)
                if criterion.evaluation_type == EvaluationType.MINIMIZE:
                    max_val = float(criterion.max_acceptable or "10000")
                    normalized = max(
                        0.0, 1.0 - (proposal.estimated_latency_ms / max_val)
                    )
                else:
                    normalized = 0.5

        elif "quality" in name_lower:
            if proposal.quality_score is not None:
                raw_value = str(proposal.quality_score)
                normalized = proposal.quality_score
            else:
                raw_value = "0.5"
                normalized = 0.5
                notes = "Quality score not provided, using default"

        elif "capability" in name_lower or "coverage" in name_lower:
            # Score based on number of offered capabilities
            raw_value = str(len(proposal.offered_capabilities))
            normalized = min(1.0, len(proposal.offered_capabilities) / 5.0)

        elif "commitment" in name_lower:
            commitment_scores = {
                CommitmentLevel.TENTATIVE: 0.2,
                CommitmentLevel.CONDITIONAL: 0.5,
                CommitmentLevel.FIRM: 0.8,
                CommitmentLevel.GUARANTEED: 1.0,
            }
            raw_value = proposal.commitment_level.value
            normalized = commitment_scores.get(proposal.commitment_level, 0.5)

        else:
            # Default scoring
            raw_value = "0.5"
            normalized = 0.5
            notes = f"Unknown criterion type: {criterion.name}"

        return raw_value, normalized, notes

    def _assess_risk(
        self,
        proposal: ContractProposal,
        criteria_scores: List[CriteriaScore],
    ) -> EvaluationRiskLevel:
        """
        Assess the risk level of a proposal.

        Args:
            proposal: Proposal to assess
            criteria_scores: Scores for each criterion

        Returns:
            Risk level
        """
        risk_factors = 0

        # Tentative commitment is risky
        if proposal.commitment_level == CommitmentLevel.TENTATIVE:
            risk_factors += 2

        # Conditional commitment has some risk
        if proposal.commitment_level == CommitmentLevel.CONDITIONAL:
            risk_factors += 1

        # Low scores are risky
        low_scores = sum(
            1 for cs in criteria_scores if cs.normalized_score < 0.4
        )
        risk_factors += low_scores

        # Many conditions are risky
        if proposal.conditions and len(proposal.conditions) > 3:
            risk_factors += 1

        # Map risk factors to risk level
        if risk_factors == 0:
            return EvaluationRiskLevel.MINIMAL
        elif risk_factors == 1:
            return EvaluationRiskLevel.LOW
        elif risk_factors <= 3:
            return EvaluationRiskLevel.MODERATE
        elif risk_factors <= 5:
            return EvaluationRiskLevel.HIGH
        else:
            return EvaluationRiskLevel.UNACCEPTABLE

    def award_contract(
        self,
        session_id: str,
        winning_proposal_id: str,
        contract_duration_hours: int = 24,
        acceptance_deadline_hours: int = 1,
        modifications: Optional[List[str]] = None,
        special_conditions: Optional[List[str]] = None,
        sla_terms: Optional[SLATerms] = None,
    ) -> ContractAward:
        """
        Award contract to a winning bidder.

        Args:
            session_id: Session ID
            winning_proposal_id: ID of winning proposal
            contract_duration_hours: Duration of contract
            acceptance_deadline_hours: Hours to accept
            modifications: Modifications to original proposal
            special_conditions: Special conditions
            sla_terms: SLA terms

        Returns:
            Contract award

        Raises:
            ValueError: If session not ready or proposal not found
        """
        session = self._get_session(session_id)

        # Transition to awarding state
        self._transition_status(session_id, ContractNetStatus.AWARDING_CONTRACT)

        # Find winning proposal
        winning_proposal = next(
            (p for p in session.proposals if p.proposal_id == winning_proposal_id),
            None,
        )
        if not winning_proposal:
            raise ValueError(f"Proposal {winning_proposal_id} not found")

        now = datetime.utcnow()
        effective_until = now + timedelta(hours=contract_duration_hours)
        acceptance_deadline = now + timedelta(hours=acceptance_deadline_hours)

        terms = AwardedTerms(
            effective_from=now.isoformat() + "Z",
            effective_until=effective_until.isoformat() + "Z",
            agreed_cost=winning_proposal.cost,
            agreed_sla=sla_terms,
            modifications=modifications,
            special_conditions=special_conditions,
        )

        # Create rejection notifications
        rejection_notifications: List[AgentNotification] = []
        for proposal in session.proposals:
            if proposal.proposal_id != winning_proposal_id:
                rejection_notifications.append(
                    AgentNotification(
                        agent_id=proposal.proposer.agent_id,
                        notification_type=NotificationType.AWARD_DECLINED,
                        message=(
                            f"Your proposal {proposal.proposal_id} was not "
                            f"selected for CFP {session.cfp.cfp_id}."
                        ),
                        sent_at=now.isoformat() + "Z",
                    )
                )

        award = ContractAward(
            award_id=f"award-{uuid.uuid4().hex[:12]}",
            cfp_id=session.cfp.cfp_id,
            winning_proposal_id=winning_proposal_id,
            awarded_to=winning_proposal.proposer,
            awarded_by=session.cfp.issuer,
            awarded_at=now.isoformat() + "Z",
            contract_terms=terms,
            acceptance_deadline=acceptance_deadline.isoformat() + "Z",
            rejection_notifications=rejection_notifications,
        )

        session.award = award
        session.updated_at = now.isoformat() + "Z"

        # Transition to awaiting confirmation
        self._transition_status(
            session_id, ContractNetStatus.AWAITING_CONFIRMATION
        )

        return award

    def confirm_award(
        self,
        session_id: str,
        confirmed: bool,
        confirming_agent: AgentIdentity,
        rejection_reason: Optional[str] = None,
        counter_terms: Optional[AwardedTerms] = None,
        start_time: Optional[str] = None,
        estimated_completion: Optional[str] = None,
        progress_interval_ms: int = 60000,
        contact_endpoint: Optional[str] = None,
    ) -> ContractConfirmation:
        """
        Confirm or reject a contract award.

        Args:
            session_id: Session ID
            confirmed: Whether to accept
            confirming_agent: Agent confirming
            rejection_reason: Reason if rejecting
            counter_terms: Counter-terms if negotiating
            start_time: Planned start time if accepting
            estimated_completion: Estimated completion if accepting
            progress_interval_ms: Progress reporting interval
            contact_endpoint: Contact endpoint for execution

        Returns:
            Contract confirmation

        Raises:
            ValueError: If session not awaiting confirmation
        """
        session = self._get_session(session_id)

        if session.status != ContractNetStatus.AWAITING_CONFIRMATION:
            raise ValueError(
                f"Session {session_id} is not awaiting confirmation "
                f"(status: {session.status.value})"
            )

        now = datetime.utcnow()

        execution_commitment = None
        if confirmed and start_time and estimated_completion:
            execution_commitment = ExecutionCommitment(
                start_time=start_time,
                estimated_completion=estimated_completion,
                progress_reporting_interval_ms=progress_interval_ms,
                contact_endpoint=contact_endpoint or "",
            )

        confirmation = ContractConfirmation(
            confirmation_id=f"conf-{uuid.uuid4().hex[:12]}",
            award_id=session.award.award_id if session.award else "",
            confirmed=confirmed,
            confirmed_by=confirming_agent,
            confirmed_at=now.isoformat() + "Z",
            rejection_reason=rejection_reason,
            counter_terms=counter_terms,
            execution_commitment=execution_commitment,
        )

        session.confirmation = confirmation
        session.updated_at = now.isoformat() + "Z"

        # Transition based on confirmation
        if confirmed:
            self._transition_status(session_id, ContractNetStatus.CONTRACT_ACTIVE)
        else:
            self._transition_status(session_id, ContractNetStatus.FAILED)

        return confirmation

    def report_progress(
        self,
        session_id: str,
        progress_percentage: float,
        current_step: int,
        status: ExecutionStatus = ExecutionStatus.IN_PROGRESS,
        issues: Optional[List[ExecutionIssue]] = None,
        estimated_remaining_ms: Optional[int] = None,
    ) -> TaskProgressReport:
        """
        Report progress on task execution.

        Args:
            session_id: Session ID
            progress_percentage: Completion percentage (0-100)
            current_step: Current step number
            status: Execution status
            issues: Any issues encountered
            estimated_remaining_ms: Estimated time remaining

        Returns:
            Progress report

        Raises:
            ValueError: If session not active
        """
        session = self._get_session(session_id)

        if session.status != ContractNetStatus.CONTRACT_ACTIVE:
            raise ValueError(
                f"Session {session_id} is not active "
                f"(status: {session.status.value})"
            )

        now = datetime.utcnow()

        report = TaskProgressReport(
            report_id=f"prog-{uuid.uuid4().hex[:12]}",
            contract_id=session.award.award_id if session.award else "",
            reported_at=now.isoformat() + "Z",
            progress_percentage=progress_percentage,
            current_step=current_step,
            status=status,
            issues=issues,
            estimated_remaining_ms=estimated_remaining_ms,
        )

        session.progress_reports.append(report)
        session.updated_at = now.isoformat() + "Z"

        return report

    def complete_task(
        self,
        session_id: str,
        status: ExecutionStatus,
        output: Optional[str] = None,
        actual_latency_ms: int = 0,
        summary: str = "",
        actual_cost: Optional[CostEstimate] = None,
        quality_metrics: Optional[QualityMetrics] = None,
    ) -> TaskExecutionResult:
        """
        Complete task execution and report results.

        Args:
            session_id: Session ID
            status: Final status
            output: Task output as JSON string
            actual_latency_ms: Actual execution time
            summary: Human-readable summary
            actual_cost: Actual cost incurred
            quality_metrics: Quality measurements

        Returns:
            Task execution result

        Raises:
            ValueError: If session not active
        """
        session = self._get_session(session_id)

        if session.status != ContractNetStatus.CONTRACT_ACTIVE:
            raise ValueError(
                f"Session {session_id} is not active "
                f"(status: {session.status.value})"
            )

        now = datetime.utcnow()

        result = TaskExecutionResult(
            result_id=f"res-{uuid.uuid4().hex[:12]}",
            contract_id=session.award.award_id if session.award else "",
            completed_at=now.isoformat() + "Z",
            status=status,
            output=output,
            actual_latency_ms=actual_latency_ms,
            summary=summary,
            actual_cost=actual_cost,
            quality_metrics=quality_metrics,
        )

        session.result = result
        session.updated_at = now.isoformat() + "Z"

        # Transition to final state
        if status == ExecutionStatus.COMPLETED:
            self._transition_status(session_id, ContractNetStatus.COMPLETED)
        else:
            self._transition_status(session_id, ContractNetStatus.FAILED)

        return result

    def cancel_session(self, session_id: str, reason: str = "") -> None:
        """
        Cancel a Contract-Net session.

        Args:
            session_id: Session to cancel
            reason: Reason for cancellation

        Raises:
            ValueError: If session cannot be cancelled
        """
        session = self._get_session(session_id)

        if session.status in [
            ContractNetStatus.COMPLETED,
            ContractNetStatus.FAILED,
            ContractNetStatus.CANCELLED,
        ]:
            raise ValueError(
                f"Session {session_id} is already in terminal state "
                f"({session.status.value})"
            )

        self._transition_status(session_id, ContractNetStatus.CANCELLED)

    def get_session(self, session_id: str) -> ContractNetSession:
        """
        Get a session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session

        Raises:
            ValueError: If session not found
        """
        return self._get_session(session_id)

    def decide_to_bid(
        self,
        cfp: CallForProposals,
        agent_identity: AgentIdentity,
        available_capabilities: List[AgentCapability],
        current_workload: float,
        policy_constraints: Optional[List[str]] = None,
    ) -> BidDecision:
        """
        Decide whether to submit a bid for a CFP.

        Args:
            cfp: The CFP to consider
            agent_identity: Our identity
            available_capabilities: Our capabilities
            current_workload: Current workload (0.0-1.0)
            policy_constraints: Any policy constraints

        Returns:
            Bid decision with reasoning
        """
        # Check capability coverage
        required_caps = set(cfp.task_specification.required_capabilities)
        available_cap_ids = {c.capability_id for c in available_capabilities}
        covered_caps = required_caps.intersection(available_cap_ids)
        coverage = len(covered_caps) / len(required_caps) if required_caps else 1.0

        # Check deadline
        deadline = datetime.fromisoformat(cfp.deadline.replace("Z", "+00:00"))
        now = datetime.utcnow().replace(tzinfo=deadline.tzinfo)
        time_remaining = (deadline - now).total_seconds()

        # Decision logic
        should_bid = True
        confidence = 0.8
        reasoning_parts: List[str] = []
        refusal_reason = None
        suggested_conditions: List[str] = []

        # Check capability coverage
        if coverage < 0.5:
            should_bid = False
            refusal_reason = RefusalReason.LACK_CAPABILITY
            reasoning_parts.append(
                f"Insufficient capability coverage ({coverage:.0%})"
            )
        elif coverage < 1.0:
            reasoning_parts.append(
                f"Partial capability coverage ({coverage:.0%})"
            )
            suggested_conditions.append("May require capability adaptation")
            confidence -= 0.1

        # Check workload
        if current_workload > 0.9:
            should_bid = False
            refusal_reason = RefusalReason.CAPACITY_EXCEEDED
            reasoning_parts.append(
                f"Current workload too high ({current_workload:.0%})"
            )
        elif current_workload > 0.7:
            reasoning_parts.append(
                f"Moderate workload ({current_workload:.0%})"
            )
            suggested_conditions.append("Delayed start may be required")
            confidence -= 0.1

        # Check deadline
        if time_remaining < 60:  # Less than 1 minute
            should_bid = False
            refusal_reason = RefusalReason.DEADLINE_UNACHIEVABLE
            reasoning_parts.append("Deadline too close")
        elif time_remaining < 300:  # Less than 5 minutes
            reasoning_parts.append("Tight deadline")
            confidence -= 0.1

        # Check policy constraints
        if policy_constraints:
            for constraint in policy_constraints:
                if "security" in constraint.lower():
                    for tc in cfp.task_specification.constraints:
                        if tc.constraint_type == TaskConstraintType.SECURITY:
                            if "restricted" in tc.value.lower():
                                should_bid = False
                                refusal_reason = RefusalReason.POLICY_RESTRICTION
                                reasoning_parts.append(
                                    f"Policy conflict: {constraint}"
                                )
                                break

        if should_bid and not reasoning_parts:
            reasoning_parts.append("All requirements met")

        return BidDecision(
            should_bid=should_bid,
            confidence=max(0.0, min(1.0, confidence)),
            reasoning="; ".join(reasoning_parts),
            capability_coverage=coverage,
            refusal_reason=refusal_reason,
            suggested_conditions=suggested_conditions if should_bid else None,
        )

    def _get_session(self, session_id: str) -> ContractNetSession:
        """Get session or raise error."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        return session

    def _transition_status(
        self, session_id: str, new_status: ContractNetStatus
    ) -> ContractNetSession:
        """
        Transition session to new status.

        Args:
            session_id: Session to transition
            new_status: Target status

        Returns:
            Updated session

        Raises:
            ValueError: If transition not valid
        """
        session = self._get_session(session_id)

        valid_targets = self.VALID_TRANSITIONS.get(session.status, [])
        if new_status not in valid_targets:
            raise ValueError(
                f"Cannot transition from {session.status.value} to "
                f"{new_status.value}. Valid targets: "
                f"{[s.value for s in valid_targets]}"
            )

        session.status = new_status
        session.updated_at = datetime.utcnow().isoformat() + "Z"

        return session
