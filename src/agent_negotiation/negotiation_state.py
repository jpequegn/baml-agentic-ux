"""
Negotiation State Management

Implementation of negotiation state machine, session management, and proposal evaluation
for agent-to-agent capability negotiation based on Contract-Net protocol.

Issue #56 - Phase 3b: Basic Negotiation Protocol
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable
import uuid

from src.lui_simulator.agent_types import (
    AgentCapability,
    AgentIdentity,
    CapabilityConstraint,
    SchemaDefinition,
)


# ============================================
# Negotiation Enums
# ============================================


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
    """Actions that can be taken during negotiation."""

    PROPOSE = "propose"
    COUNTER = "counter"
    ACCEPT = "accept"
    REJECT = "reject"
    WITHDRAW = "withdraw"
    TIMEOUT = "timeout"


class RequestPriority(Enum):
    """Priority of a capability request."""

    REQUIRED = "required"  # Must have
    PREFERRED = "preferred"  # Want but negotiable
    OPTIONAL = "optional"  # Nice to have


class ConditionType(Enum):
    """Types of conditions in offers."""

    AUTHENTICATION_REQUIRED = "authentication_required"
    RATE_LIMIT = "rate_limit"
    DATA_RETENTION = "data_retention"
    AUDIT_LOGGING = "audit_logging"
    GEOGRAPHIC_RESTRICTION = "geographic_restriction"
    TIME_WINDOW = "time_window"
    COST_LIMIT = "cost_limit"
    QUALITY_THRESHOLD = "quality_threshold"


class BillingModel(Enum):
    """Billing models for capability usage."""

    PER_REQUEST = "per_request"
    PER_TOKEN = "per_token"
    FLAT_RATE = "flat_rate"
    TIERED = "tiered"
    PAY_AS_YOU_GO = "pay_as_you_go"
    SUBSCRIPTION = "subscription"


class NegotiationStrategy(Enum):
    """Negotiation strategies for proposal evaluation."""

    COOPERATIVE = "cooperative"  # Maximize mutual benefit
    COMPETITIVE = "competitive"  # Maximize own benefit
    PRINCIPLED = "principled"  # Fair, objective criteria
    ACCOMMODATING = "accommodating"  # Prioritize relationship


# ============================================
# Rate Limiting
# ============================================


@dataclass
class RateLimit:
    """Rate limiting configuration."""

    requests_per_second: int | None = None
    requests_per_minute: int | None = None
    requests_per_hour: int | None = None
    burst_limit: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {}
        if self.requests_per_second is not None:
            result["requests_per_second"] = self.requests_per_second
        if self.requests_per_minute is not None:
            result["requests_per_minute"] = self.requests_per_minute
        if self.requests_per_hour is not None:
            result["requests_per_hour"] = self.requests_per_hour
        if self.burst_limit is not None:
            result["burst_limit"] = self.burst_limit
        return result


# ============================================
# Negotiation Components
# ============================================


@dataclass
class CapabilityRequest:
    """Request for a specific capability."""

    capability_type: str
    required_schema: SchemaDefinition | None = None
    constraints: list[CapabilityConstraint] = field(default_factory=list)
    priority: RequestPriority = RequestPriority.REQUIRED

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "capability_type": self.capability_type,
            "required_schema": (
                self.required_schema.__dict__ if self.required_schema else None
            ),
            "constraints": [c.__dict__ for c in self.constraints],
            "priority": self.priority.value,
        }


@dataclass
class OfferCondition:
    """A condition attached to a capability offer."""

    condition_type: ConditionType
    description: str
    value: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "condition_type": self.condition_type.value,
            "description": self.description,
            "value": self.value,
        }


@dataclass
class CapabilityOffer:
    """Offer of a capability with conditions."""

    capability: AgentCapability
    conditions: list[OfferCondition] = field(default_factory=list)
    rate_limit: RateLimit | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "capability": self.capability.__dict__,
            "conditions": [c.to_dict() for c in self.conditions],
            "rate_limit": self.rate_limit.to_dict() if self.rate_limit else None,
        }


@dataclass
class NegotiationTerms:
    """Terms and conditions for the negotiation agreement."""

    duration_seconds: int
    auto_renew: bool = False
    termination_conditions: list[str] = field(default_factory=list)
    dispute_resolution: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "duration_seconds": self.duration_seconds,
            "auto_renew": self.auto_renew,
            "termination_conditions": self.termination_conditions,
        }
        if self.dispute_resolution:
            result["dispute_resolution"] = self.dispute_resolution
        return result


@dataclass
class NegotiationProposal:
    """A proposal in a negotiation session."""

    proposal_id: str
    requested_capabilities: list[CapabilityRequest]
    offered_capabilities: list[CapabilityOffer]
    terms: NegotiationTerms
    validity_period_seconds: int = 3600

    @classmethod
    def create(
        cls,
        requested_capabilities: list[CapabilityRequest],
        offered_capabilities: list[CapabilityOffer],
        terms: NegotiationTerms,
        validity_period_seconds: int = 3600,
    ) -> "NegotiationProposal":
        """Create a new proposal with auto-generated ID."""
        return cls(
            proposal_id=str(uuid.uuid4()),
            requested_capabilities=requested_capabilities,
            offered_capabilities=offered_capabilities,
            terms=terms,
            validity_period_seconds=validity_period_seconds,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "proposal_id": self.proposal_id,
            "requested_capabilities": [r.to_dict() for r in self.requested_capabilities],
            "offered_capabilities": [o.to_dict() for o in self.offered_capabilities],
            "terms": self.terms.to_dict(),
            "validity_period_seconds": self.validity_period_seconds,
        }


@dataclass
class NegotiationTurn:
    """A single turn in the negotiation history."""

    turn_number: int
    actor: str  # Agent ID
    action: NegotiationAction
    timestamp: str
    proposal: NegotiationProposal | None = None
    rationale: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "turn_number": self.turn_number,
            "actor": self.actor,
            "action": self.action.value,
            "timestamp": self.timestamp,
        }
        if self.proposal:
            result["proposal"] = self.proposal.to_dict()
        if self.rationale:
            result["rationale"] = self.rationale
        return result


@dataclass
class NegotiationSession:
    """A negotiation session between two agents."""

    session_id: str
    initiator: AgentIdentity
    responder: AgentIdentity
    status: NegotiationStatus
    created_at: str
    updated_at: str
    expires_at: str
    history: list[NegotiationTurn] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        initiator: AgentIdentity,
        responder: AgentIdentity,
        expiration_hours: int = 24,
    ) -> "NegotiationSession":
        """Create a new negotiation session."""
        now = datetime.now(timezone.utc)
        return cls(
            session_id=str(uuid.uuid4()),
            initiator=initiator,
            responder=responder,
            status=NegotiationStatus.INITIATED,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            expires_at=(now + timedelta(hours=expiration_hours)).isoformat(),
            history=[],
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "initiator": self.initiator.__dict__,
            "responder": self.responder.__dict__,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "expires_at": self.expires_at,
            "history": [turn.to_dict() for turn in self.history],
        }


# ============================================
# Agreement Types
# ============================================


@dataclass
class GrantedCapability:
    """A capability granted as part of an agreement."""

    capability: AgentCapability
    grantee: str  # Agent ID receiving access
    grantor: str  # Agent ID providing access
    access_token: str | None = None
    conditions: list[OfferCondition] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "capability": self.capability.__dict__,
            "grantee": self.grantee,
            "grantor": self.grantor,
            "conditions": [c.to_dict() for c in self.conditions],
        }
        if self.access_token:
            result["access_token"] = self.access_token
        return result


@dataclass
class Agreement:
    """A finalized agreement between agents."""

    agreement_id: str
    parties: list[AgentIdentity]
    capabilities_granted: list[GrantedCapability]
    terms: NegotiationTerms
    signature_method: str
    created_at: str
    expires_at: str

    @classmethod
    def create(
        cls,
        parties: list[AgentIdentity],
        capabilities_granted: list[GrantedCapability],
        terms: NegotiationTerms,
        signature_method: str = "none",
    ) -> "Agreement":
        """Create a new agreement with auto-generated ID."""
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=terms.duration_seconds)

        return cls(
            agreement_id=str(uuid.uuid4()),
            parties=parties,
            capabilities_granted=capabilities_granted,
            terms=terms,
            signature_method=signature_method,
            created_at=now.isoformat(),
            expires_at=expires.isoformat(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "agreement_id": self.agreement_id,
            "parties": [p.__dict__ for p in self.parties],
            "capabilities_granted": [c.to_dict() for c in self.capabilities_granted],
            "terms": self.terms.to_dict(),
            "signature_method": self.signature_method,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
        }


# ============================================
# Negotiation State Machine
# ============================================


class NegotiationStateMachine:
    """
    State machine for managing negotiation sessions.

    Implements Contract-Net inspired protocol with strict state transition rules.
    Tracks all state changes and provides event hooks for monitoring.
    """

    VALID_TRANSITIONS: dict[NegotiationStatus, list[NegotiationStatus]] = {
        NegotiationStatus.INITIATED: [
            NegotiationStatus.PROPOSAL_SENT,
            NegotiationStatus.CANCELLED,
        ],
        NegotiationStatus.PROPOSAL_SENT: [
            NegotiationStatus.COUNTER_OFFERED,
            NegotiationStatus.ACCEPTED,
            NegotiationStatus.REJECTED,
            NegotiationStatus.EXPIRED,
        ],
        NegotiationStatus.COUNTER_OFFERED: [
            NegotiationStatus.COUNTER_OFFERED,  # Multiple counter-offers
            NegotiationStatus.ACCEPTED,
            NegotiationStatus.REJECTED,
            NegotiationStatus.EXPIRED,
            NegotiationStatus.ADAPTED,
        ],
        NegotiationStatus.ACCEPTED: [],  # Terminal state
        NegotiationStatus.REJECTED: [],  # Terminal state
        NegotiationStatus.EXPIRED: [],  # Terminal state
        NegotiationStatus.CANCELLED: [],  # Terminal state
        NegotiationStatus.ADAPTED: [
            NegotiationStatus.PROPOSAL_SENT,
            NegotiationStatus.ACCEPTED,
        ],
    }

    def __init__(self, session: NegotiationSession):
        """Initialize state machine with a negotiation session."""
        self.session = session
        self._on_transition_callbacks: list[
            Callable[[NegotiationStatus, NegotiationStatus, NegotiationTurn], None]
        ] = []

    def can_transition(self, target: NegotiationStatus) -> bool:
        """
        Check if transition to target status is valid.

        Args:
            target: Target status to transition to

        Returns:
            True if transition is allowed, False otherwise
        """
        valid_targets = self.VALID_TRANSITIONS.get(self.session.status, [])
        return target in valid_targets

    def transition(
        self,
        target: NegotiationStatus,
        actor: str,
        action: NegotiationAction,
        proposal: NegotiationProposal | None = None,
        rationale: str | None = None,
    ) -> bool:
        """
        Execute state transition with turn recording.

        Args:
            target: Target status
            actor: Agent ID performing the action
            action: Negotiation action being performed
            proposal: Optional proposal being made
            rationale: Optional explanation for the action

        Returns:
            True if transition was successful, False if invalid
        """
        if not self.can_transition(target):
            return False

        # Record turn
        turn = NegotiationTurn(
            turn_number=len(self.session.history) + 1,
            actor=actor,
            action=action,
            proposal=proposal,
            timestamp=datetime.now(timezone.utc).isoformat(),
            rationale=rationale,
        )
        self.session.history.append(turn)

        # Update session
        old_status = self.session.status
        self.session.status = target
        self.session.updated_at = datetime.now(timezone.utc).isoformat()

        # Notify callbacks
        for callback in self._on_transition_callbacks:
            callback(old_status, target, turn)

        return True

    def on_transition(
        self,
        callback: Callable[[NegotiationStatus, NegotiationStatus, NegotiationTurn], None],
    ) -> None:
        """
        Register callback for state transitions.

        Args:
            callback: Function to call when transitions occur
        """
        self._on_transition_callbacks.append(callback)

    def is_terminal(self) -> bool:
        """Check if session is in a terminal state."""
        return len(self.VALID_TRANSITIONS.get(self.session.status, [])) == 0

    def get_latest_proposal(self) -> NegotiationProposal | None:
        """Get the most recent proposal from the session history."""
        for turn in reversed(self.session.history):
            if turn.proposal:
                return turn.proposal
        return None


# ============================================
# Proposal Evaluation
# ============================================


@dataclass
class MinimumTerms:
    """Minimum acceptable terms for negotiation."""

    min_duration_seconds: int
    max_rate_limit: RateLimit | None = None
    required_conditions: list[ConditionType] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "min_duration_seconds": self.min_duration_seconds,
            "max_rate_limit": self.max_rate_limit.to_dict() if self.max_rate_limit else None,
            "required_conditions": [c.value for c in self.required_conditions],
        }


@dataclass
class EvaluationPolicy:
    """Policy for evaluating negotiation proposals."""

    min_acceptable_terms: MinimumTerms
    negotiation_strategy: NegotiationStrategy
    max_counter_offers: int = 3
    auto_accept_threshold: float = 0.9

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "min_acceptable_terms": self.min_acceptable_terms.to_dict(),
            "negotiation_strategy": self.negotiation_strategy.value,
            "max_counter_offers": self.max_counter_offers,
            "auto_accept_threshold": self.auto_accept_threshold,
        }


@dataclass
class GapAnalysis:
    """Analysis of gaps between proposal and requirements."""

    unmet_requirements: list[str] = field(default_factory=list)
    constraint_violations: list[str] = field(default_factory=list)
    suggested_modifications: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "unmet_requirements": self.unmet_requirements,
            "constraint_violations": self.constraint_violations,
            "suggested_modifications": self.suggested_modifications,
        }


@dataclass
class ProposalEvaluation:
    """Result of evaluating a negotiation proposal."""

    decision: NegotiationAction
    score: float
    can_satisfy: bool
    rationale: str
    gap_analysis: GapAnalysis | None = None
    counter_proposal: NegotiationProposal | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "decision": self.decision.value,
            "score": self.score,
            "can_satisfy": self.can_satisfy,
            "rationale": self.rationale,
        }
        if self.gap_analysis:
            result["gap_analysis"] = self.gap_analysis.to_dict()
        if self.counter_proposal:
            result["counter_proposal"] = self.counter_proposal.to_dict()
        return result


class ProposalEvaluator:
    """
    Evaluates negotiation proposals and generates counter-proposals.

    Uses configurable evaluation policy to determine whether to accept,
    reject, or counter-offer based on capability requirements and constraints.
    """

    def __init__(
        self,
        our_capabilities: list[AgentCapability],
        policy: EvaluationPolicy,
    ):
        """
        Initialize proposal evaluator.

        Args:
            our_capabilities: Capabilities we can offer
            policy: Evaluation policy to use
        """
        self.our_capabilities = our_capabilities
        self.policy = policy

    def evaluate(self, proposal: NegotiationProposal) -> ProposalEvaluation:
        """
        Evaluate a proposal and determine response.

        Args:
            proposal: Proposal to evaluate

        Returns:
            ProposalEvaluation with decision and rationale
        """
        # Check if we can satisfy the requested capabilities
        can_satisfy, gaps = self._can_satisfy_requests(proposal.requested_capabilities)

        # Score the proposal
        score = self._score_proposal(proposal)

        # Decide based on policy
        if not can_satisfy:
            return ProposalEvaluation(
                decision=NegotiationAction.REJECT,
                score=score,
                can_satisfy=False,
                rationale="Cannot satisfy required capabilities",
                gap_analysis=gaps,
            )

        if score >= self.policy.auto_accept_threshold:
            return ProposalEvaluation(
                decision=NegotiationAction.ACCEPT,
                score=score,
                can_satisfy=True,
                rationale=f"Proposal meets acceptance threshold ({score:.2f} >= {self.policy.auto_accept_threshold})",
            )

        # Generate counter-proposal
        counter = self._generate_counter_proposal(proposal, gaps)

        return ProposalEvaluation(
            decision=NegotiationAction.COUNTER,
            score=score,
            can_satisfy=True,
            counter_proposal=counter,
            gap_analysis=gaps,
            rationale=f"Proposal below threshold ({score:.2f}), offering counter-proposal",
        )

    def generate_counter_proposal(
        self,
        original: NegotiationProposal,
        gaps: GapAnalysis,
    ) -> NegotiationProposal:
        """
        Generate a counter-proposal addressing identified gaps.

        Args:
            original: Original proposal
            gaps: Identified gaps in the proposal

        Returns:
            New counter-proposal
        """
        return self._generate_counter_proposal(original, gaps)

    def _can_satisfy_requests(
        self, requests: list[CapabilityRequest]
    ) -> tuple[bool, GapAnalysis]:
        """Check if we can satisfy the requested capabilities."""
        our_types = {c.capability_type.value for c in self.our_capabilities}
        gaps = GapAnalysis()

        for req in requests:
            if req.priority == RequestPriority.REQUIRED:
                if req.capability_type not in our_types:
                    gaps.unmet_requirements.append(
                        f"Required capability '{req.capability_type}' not available"
                    )

        can_satisfy = len(gaps.unmet_requirements) == 0
        return can_satisfy, gaps

    def _score_proposal(self, proposal: NegotiationProposal) -> float:
        """Score a proposal based on policy."""
        score = 0.0

        # Term attractiveness (40%)
        term_score = self._score_terms(proposal.terms)
        score += 0.4 * term_score

        # Offered capabilities value (30%)
        offer_score = self._score_offers(proposal.offered_capabilities)
        score += 0.3 * offer_score

        # Request burden (30%)
        request_burden = self._score_request_burden(proposal.requested_capabilities)
        score += 0.3 * (1.0 - request_burden)  # Lower burden = higher score

        return score

    def _score_terms(self, terms: NegotiationTerms) -> float:
        """Score the negotiation terms."""
        score = 0.0

        # Check duration
        min_duration = self.policy.min_acceptable_terms.min_duration_seconds
        if terms.duration_seconds >= min_duration:
            score += 0.5
        else:
            # Penalty for short duration
            ratio = terms.duration_seconds / min_duration
            score += 0.5 * ratio

        # Auto-renewal is generally positive
        if terms.auto_renew:
            score += 0.3

        # Having termination conditions is good
        if terms.termination_conditions:
            score += 0.2

        return min(1.0, score)

    def _score_offers(self, offers: list[CapabilityOffer]) -> float:
        """Score the offered capabilities."""
        if not offers:
            return 0.0

        # Simple scoring: each offer has value
        base_score = min(1.0, len(offers) / 3)  # Normalize to ~3 capabilities

        # Penalty for restrictive conditions
        total_conditions = sum(len(offer.conditions) for offer in offers)
        condition_penalty = min(0.3, total_conditions * 0.05)

        return max(0.0, base_score - condition_penalty)

    def _score_request_burden(self, requests: list[CapabilityRequest]) -> float:
        """Score the burden of requested capabilities."""
        if not requests:
            return 0.0

        required_count = sum(1 for r in requests if r.priority == RequestPriority.REQUIRED)
        total_count = len(requests)

        # Higher ratio of required = higher burden
        burden = required_count / total_count if total_count > 0 else 0.0

        return burden

    def _generate_counter_proposal(
        self,
        original: NegotiationProposal,
        gaps: GapAnalysis,
    ) -> NegotiationProposal:
        """Generate a counter-proposal."""
        # Simplify requests - keep only what we can satisfy
        our_types = {c.capability_type.value for c in self.our_capabilities}

        counter_requests = [
            req
            for req in original.requested_capabilities
            if req.capability_type in our_types or req.priority != RequestPriority.REQUIRED
        ]

        # Offer our capabilities that match their needs
        counter_offers = []
        for cap in self.our_capabilities:
            # Check if this capability matches any request
            matching = any(
                req.capability_type == cap.capability_type.value
                for req in original.requested_capabilities
            )
            if matching:
                counter_offers.append(CapabilityOffer(capability=cap))

        # Adjust terms if needed
        min_duration = self.policy.min_acceptable_terms.min_duration_seconds
        counter_duration = max(original.terms.duration_seconds, min_duration)

        counter_terms = NegotiationTerms(
            duration_seconds=counter_duration,
            auto_renew=original.terms.auto_renew,
            termination_conditions=original.terms.termination_conditions,
            dispute_resolution=original.terms.dispute_resolution,
        )

        return NegotiationProposal.create(
            requested_capabilities=counter_requests,
            offered_capabilities=counter_offers,
            terms=counter_terms,
            validity_period_seconds=original.validity_period_seconds,
        )


# ============================================
# Negotiation Manager
# ============================================


class NegotiationManager:
    """
    Manages multiple negotiation sessions and provides high-level negotiation operations.

    Handles session lifecycle, proposal evaluation, and agreement finalization.
    """

    def __init__(
        self,
        our_identity: AgentIdentity,
        our_capabilities: list[AgentCapability],
        evaluation_policy: EvaluationPolicy,
    ):
        """
        Initialize negotiation manager.

        Args:
            our_identity: Our agent identity
            our_capabilities: Capabilities we can offer
            evaluation_policy: Policy for evaluating proposals
        """
        self.identity = our_identity
        self.capabilities = our_capabilities
        self.policy = evaluation_policy
        self._sessions: dict[str, NegotiationStateMachine] = {}
        self._evaluator = ProposalEvaluator(our_capabilities, evaluation_policy)

    def initiate(
        self,
        target: AgentIdentity,
        requested_capabilities: list[CapabilityRequest],
        offered_capabilities: list[CapabilityOffer],
        terms: NegotiationTerms,
    ) -> NegotiationSession:
        """
        Start a new negotiation session.

        Args:
            target: Agent to negotiate with
            requested_capabilities: What we want from them
            offered_capabilities: What we offer in return
            terms: Proposed terms

        Returns:
            Created negotiation session
        """
        # Create session
        session = NegotiationSession.create(self.identity, target)

        # Create initial proposal
        proposal = NegotiationProposal.create(
            requested_capabilities=requested_capabilities,
            offered_capabilities=offered_capabilities,
            terms=terms,
        )

        # Create state machine and transition to PROPOSAL_SENT
        sm = NegotiationStateMachine(session)
        sm.transition(
            NegotiationStatus.PROPOSAL_SENT,
            self.identity.agent_id,
            NegotiationAction.PROPOSE,
            proposal=proposal,
            rationale="Initial proposal",
        )

        self._sessions[session.session_id] = sm
        return session

    def receive_proposal(
        self,
        session_id: str,
        proposal: NegotiationProposal,
    ) -> ProposalEvaluation:
        """
        Evaluate and respond to a received proposal.

        Args:
            session_id: Session ID
            proposal: Received proposal

        Returns:
            ProposalEvaluation with decision

        Raises:
            ValueError: If session not found
        """
        sm = self._sessions.get(session_id)
        if not sm:
            raise ValueError(f"Unknown session: {session_id}")

        # Evaluate proposal
        evaluation = self._evaluator.evaluate(proposal)

        # Execute appropriate transition
        if evaluation.decision == NegotiationAction.ACCEPT:
            sm.transition(
                NegotiationStatus.ACCEPTED,
                self.identity.agent_id,
                NegotiationAction.ACCEPT,
                rationale=evaluation.rationale,
            )
        elif evaluation.decision == NegotiationAction.REJECT:
            sm.transition(
                NegotiationStatus.REJECTED,
                self.identity.agent_id,
                NegotiationAction.REJECT,
                rationale=evaluation.rationale,
            )
        elif evaluation.decision == NegotiationAction.COUNTER:
            sm.transition(
                NegotiationStatus.COUNTER_OFFERED,
                self.identity.agent_id,
                NegotiationAction.COUNTER,
                proposal=evaluation.counter_proposal,
                rationale=evaluation.rationale,
            )

        return evaluation

    def finalize(self, session_id: str) -> Agreement:
        """
        Finalize an accepted negotiation into an agreement.

        Args:
            session_id: Session ID to finalize

        Returns:
            Finalized agreement

        Raises:
            ValueError: If session not found or not in ACCEPTED state
        """
        sm = self._sessions.get(session_id)
        if not sm:
            raise ValueError(f"Unknown session: {session_id}")

        if sm.session.status != NegotiationStatus.ACCEPTED:
            raise ValueError(
                f"Session not in ACCEPTED state (current: {sm.session.status.value})"
            )

        # Get the accepted proposal
        accepted_proposal = sm.get_latest_proposal()
        if not accepted_proposal:
            raise ValueError("No proposal found in session history")

        # Create granted capabilities
        capabilities_granted = self._create_grants(
            sm.session.initiator.agent_id,
            sm.session.responder.agent_id,
            accepted_proposal,
        )

        # Create agreement
        agreement = Agreement.create(
            parties=[sm.session.initiator, sm.session.responder],
            capabilities_granted=capabilities_granted,
            terms=accepted_proposal.terms,
            signature_method="none",  # TODO: Implement signing
        )

        return agreement

    def get_session(self, session_id: str) -> NegotiationSession | None:
        """Get a negotiation session by ID."""
        sm = self._sessions.get(session_id)
        return sm.session if sm else None

    def list_sessions(
        self, status_filter: NegotiationStatus | None = None
    ) -> list[NegotiationSession]:
        """List all sessions, optionally filtered by status."""
        sessions = [sm.session for sm in self._sessions.values()]

        if status_filter:
            sessions = [s for s in sessions if s.status == status_filter]

        return sessions

    def _create_grants(
        self,
        initiator_id: str,
        responder_id: str,
        proposal: NegotiationProposal,
    ) -> list[GrantedCapability]:
        """Create granted capabilities from accepted proposal."""
        grants = []

        # Capabilities granted to initiator (from responder's offers)
        for offer in proposal.offered_capabilities:
            grants.append(
                GrantedCapability(
                    capability=offer.capability,
                    grantee=initiator_id,
                    grantor=responder_id,
                    conditions=offer.conditions,
                    access_token=str(uuid.uuid4()),  # Generate access token
                )
            )

        return grants
