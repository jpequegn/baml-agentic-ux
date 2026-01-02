"""
Negotiation State Machine

Manages state transitions for agent-to-agent negotiation sessions.
Issue #57 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.5)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Optional, List, Dict, Any, Set


class NegotiationStatus(Enum):
    """Status of a negotiation session."""
    INITIATED = "initiated"
    PROPOSAL_SENT = "proposal_sent"
    COUNTER_OFFERED = "counter_offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    ADAPTED = "adapted"


class NegotiationAction(Enum):
    """Actions that can be taken in a negotiation."""
    PROPOSE = "propose"
    COUNTER = "counter"
    ACCEPT = "accept"
    REJECT = "reject"
    WITHDRAW = "withdraw"
    TIMEOUT = "timeout"


class NegotiationOutcome(Enum):
    """Possible negotiation outcomes."""
    AGREEMENT = "agreement"
    NO_AGREEMENT = "no_agreement"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    PARTIAL_AGREEMENT = "partial_agreement"


class UrgencyLevel(Enum):
    """Urgency level for a negotiation."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(Enum):
    """Risk level for negotiation."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class StrategyApproach(Enum):
    """Negotiation approach style."""
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"
    ACCOMMODATING = "accommodating"
    AVOIDING = "avoiding"
    COMPROMISING = "compromising"


class ConstraintType(Enum):
    """Types of constraints."""
    REQUIRED = "required"
    PREFERRED = "preferred"
    PROHIBITED = "prohibited"


class ConstraintOperator(Enum):
    """Comparison operators for constraints."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    IN = "in"


# Terminal states - no further transitions allowed
TERMINAL_STATES: Set[NegotiationStatus] = {
    NegotiationStatus.ACCEPTED,
    NegotiationStatus.REJECTED,
    NegotiationStatus.EXPIRED,
    NegotiationStatus.CANCELLED,
    NegotiationStatus.ADAPTED,
}


@dataclass
class NegotiationParameter:
    """A parameter being negotiated."""
    name: str
    requested_value: str
    acceptable_alternatives: Optional[List[str]] = None
    min_value: Optional[str] = None
    max_value: Optional[str] = None


@dataclass
class SLARequirement:
    """Service level agreement requirement."""
    metric: str
    target_value: float
    measurement_window_hours: int


@dataclass
class NegotiationTerms:
    """Terms of a negotiation proposal."""
    duration_hours: Optional[int] = None
    rate_limit_per_minute: Optional[int] = None
    priority_level: Optional[int] = None
    billing_model: Optional[str] = None
    sla_requirements: Optional[List[SLARequirement]] = None


@dataclass
class ProposalConstraint:
    """Additional constraint on a proposal."""
    constraint_type: ConstraintType
    field: str
    operator: ConstraintOperator
    value: str


@dataclass
class CapabilityNegotiationItem:
    """An item representing a capability in negotiation."""
    capability_id: str
    capability_name: str
    required: bool
    requested_level: Optional[str] = None
    parameters: Optional[List[NegotiationParameter]] = None


@dataclass
class NegotiationProposal:
    """A proposal in a negotiation session."""
    proposal_id: str
    capability_requirements: List[CapabilityNegotiationItem]
    terms: NegotiationTerms
    valid_until: str
    constraints: Optional[List[ProposalConstraint]] = None


@dataclass
class TurnMetadata:
    """Metadata for a negotiation turn."""
    automated: bool
    response_time_ms: Optional[int] = None
    confidence: Optional[float] = None
    alternatives_considered: Optional[int] = None


@dataclass
class NegotiationTurn:
    """A single turn in a negotiation."""
    turn_number: int
    actor: str
    action: NegotiationAction
    timestamp: str
    proposal: Optional[NegotiationProposal] = None
    rationale: Optional[str] = None
    metadata: Optional[TurnMetadata] = None


@dataclass
class NegotiationResult:
    """Result of a completed negotiation."""
    outcome: NegotiationOutcome
    agreed_proposal: Optional[NegotiationProposal] = None
    agreement_id: Optional[str] = None
    effective_from: Optional[str] = None
    effective_until: Optional[str] = None
    rejection_reasons: Optional[List[str]] = None


@dataclass
class NegotiationContext:
    """Context for a negotiation session."""
    purpose: str
    urgency: UrgencyLevel
    previous_session_id: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_data: Optional[str] = None


@dataclass
class AgentIdentity:
    """Identity information for an agent."""
    agent_id: str
    name: str
    version: str
    description: str
    provider: Optional[str] = None
    trust_domain: Optional[str] = None


@dataclass
class StateTransitionError:
    """Error details for failed state transition."""
    error_code: str
    message: str
    allowed_transitions: List[NegotiationStatus]
    suggestion: Optional[str] = None


@dataclass
class StateTransitionResult:
    """Result of a state transition attempt."""
    success: bool
    previous_status: NegotiationStatus
    new_status: NegotiationStatus
    turn_number: int
    error: Optional[StateTransitionError] = None
    warnings: Optional[List[str]] = None


@dataclass
class RiskFactor:
    """Individual risk factor."""
    category: str
    description: str
    severity: RiskLevel
    likelihood: float


@dataclass
class RiskAssessment:
    """Risk assessment for a proposal."""
    overall_risk: RiskLevel
    factors: List[RiskFactor]
    mitigations: Optional[List[str]] = None


@dataclass
class NegotiationStrategy:
    """Negotiation strategy configuration."""
    approach: StrategyApproach
    priority_capabilities: List[str]
    max_concession_percentage: float
    must_have_terms: List[str]
    nice_to_have_terms: List[str]
    time_sensitivity: float


# Type alias for state change callbacks
StateChangeCallback = Callable[
    [NegotiationStatus, NegotiationStatus, Optional[NegotiationTurn]], None
]


class NegotiationSession:
    """A complete negotiation session between two agents."""

    def __init__(
        self,
        session_id: str,
        initiator: AgentIdentity,
        responder: AgentIdentity,
        expires_in_hours: int = 24,
        context: Optional[NegotiationContext] = None,
    ):
        self.session_id = session_id
        self.initiator = initiator
        self.responder = responder
        now = datetime.utcnow()
        self.created_at = now.isoformat() + "Z"
        self.updated_at = now.isoformat() + "Z"
        self.expires_at = (now + timedelta(hours=expires_in_hours)).isoformat() + "Z"
        self.status = NegotiationStatus.INITIATED
        self.history: List[NegotiationTurn] = []
        self.current_proposal: Optional[NegotiationProposal] = None
        self.result: Optional[NegotiationResult] = None
        self.context = context

    @property
    def turn_count(self) -> int:
        """Get the number of turns in this session."""
        return len(self.history)

    @property
    def is_terminal(self) -> bool:
        """Check if the session is in a terminal state."""
        return self.status in TERMINAL_STATES

    @property
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        if self.status == NegotiationStatus.EXPIRED:
            return True
        expires = datetime.fromisoformat(self.expires_at.rstrip("Z"))
        return datetime.utcnow() > expires

    def to_dict(self) -> Dict[str, Any]:
        """Serialize session to dictionary."""
        return {
            "session_id": self.session_id,
            "initiator": {
                "agent_id": self.initiator.agent_id,
                "name": self.initiator.name,
                "version": self.initiator.version,
                "description": self.initiator.description,
                "provider": self.initiator.provider,
                "trust_domain": self.initiator.trust_domain,
            },
            "responder": {
                "agent_id": self.responder.agent_id,
                "name": self.responder.name,
                "version": self.responder.version,
                "description": self.responder.description,
                "provider": self.responder.provider,
                "trust_domain": self.responder.trust_domain,
            },
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "history": [
                {
                    "turn_number": t.turn_number,
                    "actor": t.actor,
                    "action": t.action.value,
                    "timestamp": t.timestamp,
                    "rationale": t.rationale,
                }
                for t in self.history
            ],
            "is_terminal": self.is_terminal,
            "turn_count": self.turn_count,
        }


class NegotiationStateMachine:
    """
    State machine for managing negotiation session transitions.

    Enforces valid state transitions and maintains session history.

    Valid Transitions:
        INITIATED → PROPOSAL_SENT, CANCELLED, EXPIRED
        PROPOSAL_SENT → COUNTER_OFFERED, ACCEPTED, REJECTED, EXPIRED
        COUNTER_OFFERED → COUNTER_OFFERED, ACCEPTED, REJECTED, EXPIRED, ADAPTED

    Terminal states (no outgoing transitions):
        ACCEPTED, REJECTED, EXPIRED, CANCELLED, ADAPTED
    """

    # Valid state transitions
    VALID_TRANSITIONS: Dict[NegotiationStatus, List[NegotiationStatus]] = {
        NegotiationStatus.INITIATED: [
            NegotiationStatus.PROPOSAL_SENT,
            NegotiationStatus.CANCELLED,
            NegotiationStatus.EXPIRED,  # Session can expire before proposal
        ],
        NegotiationStatus.PROPOSAL_SENT: [
            NegotiationStatus.COUNTER_OFFERED,
            NegotiationStatus.ACCEPTED,
            NegotiationStatus.REJECTED,
            NegotiationStatus.EXPIRED,
        ],
        NegotiationStatus.COUNTER_OFFERED: [
            NegotiationStatus.COUNTER_OFFERED,  # Can have multiple counters
            NegotiationStatus.ACCEPTED,
            NegotiationStatus.REJECTED,
            NegotiationStatus.EXPIRED,
            NegotiationStatus.ADAPTED,
        ],
        # Terminal states have no outgoing transitions
        NegotiationStatus.ACCEPTED: [],
        NegotiationStatus.REJECTED: [],
        NegotiationStatus.EXPIRED: [],
        NegotiationStatus.CANCELLED: [],
        NegotiationStatus.ADAPTED: [],
    }

    # Map of actions to their resulting states
    ACTION_TO_STATUS: Dict[NegotiationAction, NegotiationStatus] = {
        NegotiationAction.PROPOSE: NegotiationStatus.PROPOSAL_SENT,
        NegotiationAction.COUNTER: NegotiationStatus.COUNTER_OFFERED,
        NegotiationAction.ACCEPT: NegotiationStatus.ACCEPTED,
        NegotiationAction.REJECT: NegotiationStatus.REJECTED,
        NegotiationAction.WITHDRAW: NegotiationStatus.CANCELLED,
        NegotiationAction.TIMEOUT: NegotiationStatus.EXPIRED,
    }

    def __init__(self, session: NegotiationSession):
        """
        Initialize state machine with a negotiation session.

        Args:
            session: The negotiation session to manage
        """
        self.session = session
        self._callbacks: List[StateChangeCallback] = []

    def register_callback(self, callback: StateChangeCallback) -> None:
        """
        Register a callback to be called on state changes.

        Args:
            callback: Function to call with (old_status, new_status, turn)
        """
        self._callbacks.append(callback)

    def unregister_callback(self, callback: StateChangeCallback) -> None:
        """
        Remove a previously registered callback.

        Args:
            callback: The callback to remove
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def can_transition(self, target: NegotiationStatus) -> bool:
        """
        Check if a transition to the target state is valid.

        Args:
            target: The target state to transition to

        Returns:
            True if the transition is valid, False otherwise
        """
        # Check expiration first
        if self.session.is_expired and target != NegotiationStatus.EXPIRED:
            return False

        # Check if we're already in a terminal state
        if self.session.is_terminal:
            return False

        # Check valid transitions
        allowed = self.VALID_TRANSITIONS.get(self.session.status, [])
        return target in allowed

    def get_allowed_transitions(self) -> List[NegotiationStatus]:
        """
        Get list of valid target states from current state.

        Returns:
            List of valid target NegotiationStatus values
        """
        if self.session.is_terminal:
            return []
        if self.session.is_expired:
            return [NegotiationStatus.EXPIRED]
        return self.VALID_TRANSITIONS.get(self.session.status, [])

    def transition(
        self,
        target: NegotiationStatus,
        actor: str,
        action: NegotiationAction,
        proposal: Optional[NegotiationProposal] = None,
        rationale: Optional[str] = None,
        metadata: Optional[TurnMetadata] = None,
    ) -> StateTransitionResult:
        """
        Attempt to transition the session to a new state.

        Args:
            target: Target state to transition to
            actor: Agent ID of the actor taking this action
            action: The action being taken
            proposal: Proposal if action is PROPOSE or COUNTER
            rationale: Optional explanation for the action
            metadata: Optional turn metadata

        Returns:
            StateTransitionResult with success status and details
        """
        previous_status = self.session.status

        # Validate proposal is provided for PROPOSE/COUNTER actions
        if action in (NegotiationAction.PROPOSE, NegotiationAction.COUNTER):
            if proposal is None:
                return StateTransitionResult(
                    success=False,
                    previous_status=previous_status,
                    new_status=previous_status,
                    turn_number=self.session.turn_count,
                    error=StateTransitionError(
                        error_code="PROPOSAL_REQUIRED",
                        message=f"A proposal is required for action {action.value}",
                        allowed_transitions=self.get_allowed_transitions(),
                        suggestion="Provide a NegotiationProposal with the action",
                    ),
                )

        # Check expiration
        if self.session.is_expired and target != NegotiationStatus.EXPIRED:
            return StateTransitionResult(
                success=False,
                previous_status=previous_status,
                new_status=previous_status,
                turn_number=self.session.turn_count,
                error=StateTransitionError(
                    error_code="SESSION_EXPIRED",
                    message="Session has expired",
                    allowed_transitions=[NegotiationStatus.EXPIRED],
                    suggestion="Transition to EXPIRED state or create a new session",
                ),
            )

        # Validate transition
        if not self.can_transition(target):
            return StateTransitionResult(
                success=False,
                previous_status=previous_status,
                new_status=previous_status,
                turn_number=self.session.turn_count,
                error=StateTransitionError(
                    error_code="INVALID_TRANSITION",
                    message=f"Cannot transition from {previous_status.value} to {target.value}",
                    allowed_transitions=self.get_allowed_transitions(),
                    suggestion="Choose a valid target state from the allowed transitions",
                ),
            )

        # Validate action matches expected target
        expected_target = self.ACTION_TO_STATUS.get(action)
        if expected_target is not None and expected_target != target:
            return StateTransitionResult(
                success=False,
                previous_status=previous_status,
                new_status=previous_status,
                turn_number=self.session.turn_count,
                error=StateTransitionError(
                    error_code="ACTION_STATUS_MISMATCH",
                    message=f"Action {action.value} should result in {expected_target.value}, not {target.value}",
                    allowed_transitions=self.get_allowed_transitions(),
                    suggestion=f"Use target status {expected_target.value} with action {action.value}",
                ),
                warnings=[f"Action-status mismatch: {action.value} -> {target.value}"],
            )

        # Create turn
        now = datetime.utcnow()
        turn = NegotiationTurn(
            turn_number=self.session.turn_count + 1,
            actor=actor,
            action=action,
            timestamp=now.isoformat() + "Z",
            proposal=proposal,
            rationale=rationale,
            metadata=metadata,
        )

        # Update session
        self.session.status = target
        self.session.updated_at = now.isoformat() + "Z"
        self.session.history.append(turn)

        # Update current proposal if applicable
        if proposal is not None:
            self.session.current_proposal = proposal

        # Set result for terminal states
        if target in TERMINAL_STATES:
            self._set_result(target, proposal, rationale)

        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(previous_status, target, turn)
            except Exception:
                pass  # Don't let callback errors break the state machine

        return StateTransitionResult(
            success=True,
            previous_status=previous_status,
            new_status=target,
            turn_number=turn.turn_number,
        )

    def _set_result(
        self,
        status: NegotiationStatus,
        proposal: Optional[NegotiationProposal],
        rationale: Optional[str],
    ) -> None:
        """Set the negotiation result based on terminal status."""
        outcome_map = {
            NegotiationStatus.ACCEPTED: NegotiationOutcome.AGREEMENT,
            NegotiationStatus.REJECTED: NegotiationOutcome.NO_AGREEMENT,
            NegotiationStatus.EXPIRED: NegotiationOutcome.TIMEOUT,
            NegotiationStatus.CANCELLED: NegotiationOutcome.CANCELLED,
            NegotiationStatus.ADAPTED: NegotiationOutcome.PARTIAL_AGREEMENT,
        }

        outcome = outcome_map.get(status, NegotiationOutcome.NO_AGREEMENT)

        self.session.result = NegotiationResult(
            outcome=outcome,
            agreed_proposal=proposal if status == NegotiationStatus.ACCEPTED else None,
            rejection_reasons=[rationale] if status == NegotiationStatus.REJECTED and rationale else None,
        )

    def expire_if_needed(self) -> Optional[StateTransitionResult]:
        """
        Check if session should be expired and transition if so.

        Returns:
            StateTransitionResult if expired, None otherwise
        """
        if self.session.is_expired and self.session.status != NegotiationStatus.EXPIRED:
            return self.transition(
                target=NegotiationStatus.EXPIRED,
                actor="system",
                action=NegotiationAction.TIMEOUT,
                rationale="Session expired due to timeout",
                metadata=TurnMetadata(automated=True),
            )
        return None

    def propose(
        self,
        actor: str,
        proposal: NegotiationProposal,
        rationale: Optional[str] = None,
    ) -> StateTransitionResult:
        """
        Submit an initial proposal.

        Args:
            actor: Agent ID making the proposal
            proposal: The proposal to submit
            rationale: Optional explanation

        Returns:
            StateTransitionResult with success status
        """
        return self.transition(
            target=NegotiationStatus.PROPOSAL_SENT,
            actor=actor,
            action=NegotiationAction.PROPOSE,
            proposal=proposal,
            rationale=rationale,
        )

    def counter(
        self,
        actor: str,
        proposal: NegotiationProposal,
        rationale: Optional[str] = None,
    ) -> StateTransitionResult:
        """
        Submit a counter-proposal.

        Args:
            actor: Agent ID making the counter
            proposal: The counter-proposal
            rationale: Optional explanation

        Returns:
            StateTransitionResult with success status
        """
        return self.transition(
            target=NegotiationStatus.COUNTER_OFFERED,
            actor=actor,
            action=NegotiationAction.COUNTER,
            proposal=proposal,
            rationale=rationale,
        )

    def accept(
        self,
        actor: str,
        rationale: Optional[str] = None,
    ) -> StateTransitionResult:
        """
        Accept the current proposal.

        Args:
            actor: Agent ID accepting
            rationale: Optional explanation

        Returns:
            StateTransitionResult with success status
        """
        return self.transition(
            target=NegotiationStatus.ACCEPTED,
            actor=actor,
            action=NegotiationAction.ACCEPT,
            proposal=self.session.current_proposal,
            rationale=rationale,
        )

    def reject(
        self,
        actor: str,
        rationale: Optional[str] = None,
    ) -> StateTransitionResult:
        """
        Reject the current proposal.

        Args:
            actor: Agent ID rejecting
            rationale: Explanation for rejection

        Returns:
            StateTransitionResult with success status
        """
        return self.transition(
            target=NegotiationStatus.REJECTED,
            actor=actor,
            action=NegotiationAction.REJECT,
            rationale=rationale,
        )

    def withdraw(
        self,
        actor: str,
        rationale: Optional[str] = None,
    ) -> StateTransitionResult:
        """
        Withdraw from the negotiation.

        Args:
            actor: Agent ID withdrawing
            rationale: Optional explanation

        Returns:
            StateTransitionResult with success status
        """
        # Withdraw can only happen from INITIATED state
        if self.session.status != NegotiationStatus.INITIATED:
            return StateTransitionResult(
                success=False,
                previous_status=self.session.status,
                new_status=self.session.status,
                turn_number=self.session.turn_count,
                error=StateTransitionError(
                    error_code="INVALID_WITHDRAW",
                    message="Can only withdraw from INITIATED state",
                    allowed_transitions=self.get_allowed_transitions(),
                    suggestion="Use reject instead to end the negotiation",
                ),
            )

        return self.transition(
            target=NegotiationStatus.CANCELLED,
            actor=actor,
            action=NegotiationAction.WITHDRAW,
            rationale=rationale,
        )

    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current session state.

        Returns:
            Dictionary with session summary
        """
        return {
            "session_id": self.session.session_id,
            "status": self.session.status.value,
            "turn_count": self.session.turn_count,
            "is_terminal": self.session.is_terminal,
            "is_expired": self.session.is_expired,
            "allowed_transitions": [s.value for s in self.get_allowed_transitions()],
            "current_proposal_id": (
                self.session.current_proposal.proposal_id
                if self.session.current_proposal
                else None
            ),
            "last_actor": (
                self.session.history[-1].actor if self.session.history else None
            ),
            "last_action": (
                self.session.history[-1].action.value if self.session.history else None
            ),
        }
