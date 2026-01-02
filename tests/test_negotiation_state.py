"""
Tests for Negotiation State Machine

Issue #66 - Phase 3 Testing & Documentation
"""

import pytest
from datetime import datetime, timezone, timedelta

from src.lui_simulator.agent_types import (
    AgentIdentity,
    AgentCapability,
    CapabilityType,
    SchemaDefinition,
    SchemaType,
    CapabilityConstraint,
    ConstraintCategory,
    ConstraintEnforcement,
)
from src.agent_negotiation.negotiation_state import (
    # Enums
    NegotiationStatus,
    NegotiationAction,
    RequestPriority,
    ConditionType,
    BillingModel,
    NegotiationStrategy,
    # Dataclasses
    RateLimit,
    CapabilityRequest,
    OfferCondition,
    CapabilityOffer,
    NegotiationTerms,
    NegotiationProposal,
    NegotiationTurn,
    NegotiationSession,
    GrantedCapability,
    Agreement,
    MinimumTerms,
    EvaluationPolicy,
    GapAnalysis,
    ProposalEvaluation,
    # Classes
    NegotiationStateMachine,
    ProposalEvaluator,
    NegotiationManager,
)


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def agent_identity_initiator() -> AgentIdentity:
    """Create initiator agent identity."""
    return AgentIdentity.create(
        name="initiator-agent",
        version="1.0.0",
        description="Test initiator agent",
        provider="test",
    )


@pytest.fixture
def agent_identity_responder() -> AgentIdentity:
    """Create responder agent identity."""
    return AgentIdentity.create(
        name="responder-agent",
        version="1.0.0",
        description="Test responder agent",
        provider="test",
    )


@pytest.fixture
def simple_capability() -> AgentCapability:
    """Create a simple test capability."""
    return AgentCapability.create(
        name="text-analysis",
        description="Analyze text content",
        capability_type=CapabilityType.ACTION,
        input_schema=SchemaDefinition.string(description="Input text"),
        output_schema=SchemaDefinition.string(description="Analysis result"),
    )


@pytest.fixture
def query_capability() -> AgentCapability:
    """Create a query capability."""
    return AgentCapability.create(
        name="data-query",
        description="Query data from database",
        capability_type=CapabilityType.QUERY,
        input_schema=SchemaDefinition.string(description="Query"),
        output_schema=SchemaDefinition.string(description="Results"),
    )


@pytest.fixture
def negotiation_terms() -> NegotiationTerms:
    """Create standard negotiation terms."""
    return NegotiationTerms(
        duration_seconds=3600,
        auto_renew=False,
        termination_conditions=["mutual_agreement", "expiration"],
        dispute_resolution="arbitration",
    )


@pytest.fixture
def capability_request(simple_capability: AgentCapability) -> CapabilityRequest:
    """Create a capability request."""
    return CapabilityRequest(
        capability_type="action",
        required_schema=None,
        constraints=[],
        priority=RequestPriority.REQUIRED,
    )


@pytest.fixture
def capability_offer(simple_capability: AgentCapability) -> CapabilityOffer:
    """Create a capability offer."""
    return CapabilityOffer(
        capability=simple_capability,
        conditions=[
            OfferCondition(
                condition_type=ConditionType.RATE_LIMIT,
                description="Rate limit of 100 requests per minute",
                value="100/min",
            )
        ],
        rate_limit=RateLimit(requests_per_minute=100),
    )


@pytest.fixture
def negotiation_session(
    agent_identity_initiator: AgentIdentity,
    agent_identity_responder: AgentIdentity,
) -> NegotiationSession:
    """Create a negotiation session."""
    return NegotiationSession.create(
        initiator=agent_identity_initiator,
        responder=agent_identity_responder,
        expiration_hours=24,
    )


@pytest.fixture
def minimum_terms() -> MinimumTerms:
    """Create minimum acceptable terms."""
    return MinimumTerms(
        min_duration_seconds=1800,
        max_rate_limit=RateLimit(requests_per_minute=500),
        required_conditions=[ConditionType.RATE_LIMIT],
    )


@pytest.fixture
def evaluation_policy(minimum_terms: MinimumTerms) -> EvaluationPolicy:
    """Create an evaluation policy."""
    return EvaluationPolicy(
        min_acceptable_terms=minimum_terms,
        negotiation_strategy=NegotiationStrategy.COOPERATIVE,
        max_counter_offers=3,
        auto_accept_threshold=0.85,
    )


# ============================================
# Test Enums
# ============================================


class TestNegotiationStatus:
    """Tests for NegotiationStatus enum."""

    def test_all_status_values(self):
        """Test all negotiation status values exist."""
        assert NegotiationStatus.INITIATED.value == "initiated"
        assert NegotiationStatus.PROPOSAL_SENT.value == "proposal_sent"
        assert NegotiationStatus.COUNTER_OFFERED.value == "counter_offered"
        assert NegotiationStatus.ACCEPTED.value == "accepted"
        assert NegotiationStatus.REJECTED.value == "rejected"
        assert NegotiationStatus.EXPIRED.value == "expired"
        assert NegotiationStatus.CANCELLED.value == "cancelled"
        assert NegotiationStatus.ADAPTED.value == "adapted"


class TestNegotiationAction:
    """Tests for NegotiationAction enum."""

    def test_all_action_values(self):
        """Test all negotiation action values exist."""
        assert NegotiationAction.PROPOSE.value == "propose"
        assert NegotiationAction.COUNTER.value == "counter"
        assert NegotiationAction.ACCEPT.value == "accept"
        assert NegotiationAction.REJECT.value == "reject"
        assert NegotiationAction.WITHDRAW.value == "withdraw"
        assert NegotiationAction.TIMEOUT.value == "timeout"


class TestRequestPriority:
    """Tests for RequestPriority enum."""

    def test_all_priority_values(self):
        """Test all request priority values exist."""
        assert RequestPriority.REQUIRED.value == "required"
        assert RequestPriority.PREFERRED.value == "preferred"
        assert RequestPriority.OPTIONAL.value == "optional"


class TestConditionType:
    """Tests for ConditionType enum."""

    def test_all_condition_types(self):
        """Test all condition types exist."""
        assert ConditionType.AUTHENTICATION_REQUIRED.value == "authentication_required"
        assert ConditionType.RATE_LIMIT.value == "rate_limit"
        assert ConditionType.DATA_RETENTION.value == "data_retention"
        assert ConditionType.AUDIT_LOGGING.value == "audit_logging"
        assert ConditionType.GEOGRAPHIC_RESTRICTION.value == "geographic_restriction"
        assert ConditionType.TIME_WINDOW.value == "time_window"
        assert ConditionType.COST_LIMIT.value == "cost_limit"
        assert ConditionType.QUALITY_THRESHOLD.value == "quality_threshold"


class TestBillingModel:
    """Tests for BillingModel enum."""

    def test_all_billing_models(self):
        """Test all billing model values exist."""
        assert BillingModel.PER_REQUEST.value == "per_request"
        assert BillingModel.PER_TOKEN.value == "per_token"
        assert BillingModel.FLAT_RATE.value == "flat_rate"
        assert BillingModel.TIERED.value == "tiered"
        assert BillingModel.PAY_AS_YOU_GO.value == "pay_as_you_go"
        assert BillingModel.SUBSCRIPTION.value == "subscription"


class TestNegotiationStrategy:
    """Tests for NegotiationStrategy enum."""

    def test_all_strategies(self):
        """Test all negotiation strategies exist."""
        assert NegotiationStrategy.COOPERATIVE.value == "cooperative"
        assert NegotiationStrategy.COMPETITIVE.value == "competitive"
        assert NegotiationStrategy.PRINCIPLED.value == "principled"
        assert NegotiationStrategy.ACCOMMODATING.value == "accommodating"


# ============================================
# Test Dataclasses
# ============================================


class TestRateLimit:
    """Tests for RateLimit dataclass."""

    def test_create_rate_limit(self):
        """Test creating a rate limit."""
        rate_limit = RateLimit(
            requests_per_second=10,
            requests_per_minute=100,
            requests_per_hour=1000,
            burst_limit=50,
        )
        assert rate_limit.requests_per_second == 10
        assert rate_limit.requests_per_minute == 100
        assert rate_limit.requests_per_hour == 1000
        assert rate_limit.burst_limit == 50

    def test_to_dict(self):
        """Test RateLimit to_dict method."""
        rate_limit = RateLimit(
            requests_per_second=10,
            requests_per_minute=100,
        )
        result = rate_limit.to_dict()
        assert result["requests_per_second"] == 10
        assert result["requests_per_minute"] == 100
        assert "requests_per_hour" not in result  # None values excluded

    def test_default_values(self):
        """Test RateLimit default values."""
        rate_limit = RateLimit()
        assert rate_limit.requests_per_second is None
        assert rate_limit.requests_per_minute is None


class TestCapabilityRequest:
    """Tests for CapabilityRequest dataclass."""

    def test_create_request(self):
        """Test creating a capability request."""
        request = CapabilityRequest(
            capability_type="action",
            priority=RequestPriority.REQUIRED,
        )
        assert request.capability_type == "action"
        assert request.priority == RequestPriority.REQUIRED
        assert request.constraints == []

    def test_to_dict(self):
        """Test CapabilityRequest to_dict method."""
        request = CapabilityRequest(
            capability_type="query",
            priority=RequestPriority.PREFERRED,
        )
        result = request.to_dict()
        assert result["capability_type"] == "query"
        assert result["priority"] == "preferred"


class TestOfferCondition:
    """Tests for OfferCondition dataclass."""

    def test_create_condition(self):
        """Test creating an offer condition."""
        condition = OfferCondition(
            condition_type=ConditionType.RATE_LIMIT,
            description="Max 100 requests per minute",
            value="100/min",
        )
        assert condition.condition_type == ConditionType.RATE_LIMIT
        assert condition.description == "Max 100 requests per minute"
        assert condition.value == "100/min"

    def test_to_dict(self):
        """Test OfferCondition to_dict method."""
        condition = OfferCondition(
            condition_type=ConditionType.AUDIT_LOGGING,
            description="All requests must be logged",
            value="required",
        )
        result = condition.to_dict()
        assert result["condition_type"] == "audit_logging"
        assert result["description"] == "All requests must be logged"


class TestCapabilityOffer:
    """Tests for CapabilityOffer dataclass."""

    def test_create_offer(self, simple_capability: AgentCapability):
        """Test creating a capability offer."""
        offer = CapabilityOffer(
            capability=simple_capability,
            conditions=[],
        )
        assert offer.capability == simple_capability
        assert offer.conditions == []
        assert offer.rate_limit is None

    def test_offer_with_conditions(self, simple_capability: AgentCapability):
        """Test offer with conditions and rate limit."""
        condition = OfferCondition(
            condition_type=ConditionType.RATE_LIMIT,
            description="Rate limit",
            value="100/min",
        )
        rate_limit = RateLimit(requests_per_minute=100)
        offer = CapabilityOffer(
            capability=simple_capability,
            conditions=[condition],
            rate_limit=rate_limit,
        )
        assert len(offer.conditions) == 1
        assert offer.rate_limit.requests_per_minute == 100


class TestNegotiationTerms:
    """Tests for NegotiationTerms dataclass."""

    def test_create_terms(self):
        """Test creating negotiation terms."""
        terms = NegotiationTerms(
            duration_seconds=7200,
            auto_renew=True,
            termination_conditions=["expiration"],
            dispute_resolution="arbitration",
        )
        assert terms.duration_seconds == 7200
        assert terms.auto_renew is True
        assert "expiration" in terms.termination_conditions

    def test_to_dict(self):
        """Test NegotiationTerms to_dict method."""
        terms = NegotiationTerms(
            duration_seconds=3600,
            auto_renew=False,
        )
        result = terms.to_dict()
        assert result["duration_seconds"] == 3600
        assert result["auto_renew"] is False


class TestNegotiationProposal:
    """Tests for NegotiationProposal dataclass."""

    def test_create_proposal(
        self,
        capability_request: CapabilityRequest,
        capability_offer: CapabilityOffer,
        negotiation_terms: NegotiationTerms,
    ):
        """Test creating a proposal using factory method."""
        proposal = NegotiationProposal.create(
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
            validity_period_seconds=3600,
        )
        assert proposal.proposal_id is not None
        assert len(proposal.requested_capabilities) == 1
        assert len(proposal.offered_capabilities) == 1
        assert proposal.validity_period_seconds == 3600

    def test_to_dict(
        self,
        capability_request: CapabilityRequest,
        capability_offer: CapabilityOffer,
        negotiation_terms: NegotiationTerms,
    ):
        """Test NegotiationProposal to_dict method."""
        proposal = NegotiationProposal.create(
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
        )
        result = proposal.to_dict()
        assert "proposal_id" in result
        assert "requested_capabilities" in result
        assert "offered_capabilities" in result
        assert "terms" in result


class TestNegotiationTurn:
    """Tests for NegotiationTurn dataclass."""

    def test_create_turn(self):
        """Test creating a negotiation turn."""
        turn = NegotiationTurn(
            turn_number=1,
            actor="agent-1",
            action=NegotiationAction.PROPOSE,
            timestamp=datetime.now(timezone.utc).isoformat(),
            rationale="Initial proposal",
        )
        assert turn.turn_number == 1
        assert turn.actor == "agent-1"
        assert turn.action == NegotiationAction.PROPOSE

    def test_to_dict(self):
        """Test NegotiationTurn to_dict method."""
        turn = NegotiationTurn(
            turn_number=2,
            actor="agent-2",
            action=NegotiationAction.COUNTER,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        result = turn.to_dict()
        assert result["turn_number"] == 2
        assert result["action"] == "counter"


class TestNegotiationSession:
    """Tests for NegotiationSession dataclass."""

    def test_create_session(
        self,
        agent_identity_initiator: AgentIdentity,
        agent_identity_responder: AgentIdentity,
    ):
        """Test creating a negotiation session."""
        session = NegotiationSession.create(
            initiator=agent_identity_initiator,
            responder=agent_identity_responder,
            expiration_hours=48,
        )
        assert session.session_id is not None
        assert session.initiator == agent_identity_initiator
        assert session.responder == agent_identity_responder
        assert session.status == NegotiationStatus.INITIATED
        assert session.history == []

    def test_session_expiration(
        self,
        agent_identity_initiator: AgentIdentity,
        agent_identity_responder: AgentIdentity,
    ):
        """Test session expiration is set correctly."""
        session = NegotiationSession.create(
            initiator=agent_identity_initiator,
            responder=agent_identity_responder,
            expiration_hours=1,
        )
        expires_at = datetime.fromisoformat(session.expires_at.replace("Z", "+00:00"))
        created_at = datetime.fromisoformat(session.created_at.replace("Z", "+00:00"))
        diff = expires_at - created_at
        # Should be approximately 1 hour
        assert 3500 < diff.total_seconds() < 3700


class TestAgreement:
    """Tests for Agreement dataclass."""

    def test_create_agreement(
        self,
        agent_identity_initiator: AgentIdentity,
        agent_identity_responder: AgentIdentity,
        simple_capability: AgentCapability,
        negotiation_terms: NegotiationTerms,
    ):
        """Test creating an agreement."""
        granted = GrantedCapability(
            capability=simple_capability,
            grantee=agent_identity_initiator.agent_id,
            grantor=agent_identity_responder.agent_id,
        )
        agreement = Agreement.create(
            parties=[agent_identity_initiator, agent_identity_responder],
            capabilities_granted=[granted],
            terms=negotiation_terms,
            signature_method="none",
        )
        assert agreement.agreement_id is not None
        assert len(agreement.parties) == 2
        assert len(agreement.capabilities_granted) == 1


# ============================================
# Test State Machine
# ============================================


class TestNegotiationStateMachine:
    """Tests for NegotiationStateMachine class."""

    def test_create_state_machine(self, negotiation_session: NegotiationSession):
        """Test creating a state machine."""
        sm = NegotiationStateMachine(negotiation_session)
        assert sm.session == negotiation_session
        assert sm.session.status == NegotiationStatus.INITIATED

    def test_can_transition_valid(self, negotiation_session: NegotiationSession):
        """Test checking valid transitions."""
        sm = NegotiationStateMachine(negotiation_session)
        # From INITIATED, can go to PROPOSAL_SENT
        assert sm.can_transition(NegotiationStatus.PROPOSAL_SENT) is True
        # From INITIATED, can go to CANCELLED
        assert sm.can_transition(NegotiationStatus.CANCELLED) is True

    def test_can_transition_invalid(self, negotiation_session: NegotiationSession):
        """Test checking invalid transitions."""
        sm = NegotiationStateMachine(negotiation_session)
        # From INITIATED, cannot go directly to ACCEPTED
        assert sm.can_transition(NegotiationStatus.ACCEPTED) is False
        # From INITIATED, cannot go to COUNTER_OFFERED
        assert sm.can_transition(NegotiationStatus.COUNTER_OFFERED) is False

    def test_transition_success(
        self,
        negotiation_session: NegotiationSession,
        agent_identity_initiator: AgentIdentity,
    ):
        """Test successful state transition."""
        sm = NegotiationStateMachine(negotiation_session)
        result = sm.transition(
            target=NegotiationStatus.PROPOSAL_SENT,
            actor=agent_identity_initiator.agent_id,
            action=NegotiationAction.PROPOSE,
            rationale="Initial proposal",
        )
        assert result is True
        assert sm.session.status == NegotiationStatus.PROPOSAL_SENT
        assert len(sm.session.history) == 1

    def test_transition_failure(
        self,
        negotiation_session: NegotiationSession,
        agent_identity_initiator: AgentIdentity,
    ):
        """Test failed state transition."""
        sm = NegotiationStateMachine(negotiation_session)
        result = sm.transition(
            target=NegotiationStatus.ACCEPTED,  # Invalid from INITIATED
            actor=agent_identity_initiator.agent_id,
            action=NegotiationAction.ACCEPT,
        )
        assert result is False
        assert sm.session.status == NegotiationStatus.INITIATED  # Unchanged
        assert len(sm.session.history) == 0

    def test_transition_records_history(
        self,
        negotiation_session: NegotiationSession,
        agent_identity_initiator: AgentIdentity,
    ):
        """Test that transitions record history correctly."""
        sm = NegotiationStateMachine(negotiation_session)
        sm.transition(
            target=NegotiationStatus.PROPOSAL_SENT,
            actor=agent_identity_initiator.agent_id,
            action=NegotiationAction.PROPOSE,
            rationale="Test rationale",
        )
        assert len(sm.session.history) == 1
        turn = sm.session.history[0]
        assert turn.turn_number == 1
        assert turn.actor == agent_identity_initiator.agent_id
        assert turn.rationale == "Test rationale"

    def test_is_terminal_false(self, negotiation_session: NegotiationSession):
        """Test is_terminal returns False for non-terminal states."""
        sm = NegotiationStateMachine(negotiation_session)
        assert sm.is_terminal() is False

    def test_is_terminal_true(
        self,
        negotiation_session: NegotiationSession,
        agent_identity_initiator: AgentIdentity,
        agent_identity_responder: AgentIdentity,
    ):
        """Test is_terminal returns True for terminal states."""
        sm = NegotiationStateMachine(negotiation_session)
        # Transition to PROPOSAL_SENT
        sm.transition(
            target=NegotiationStatus.PROPOSAL_SENT,
            actor=agent_identity_initiator.agent_id,
            action=NegotiationAction.PROPOSE,
        )
        # Transition to ACCEPTED (terminal)
        sm.transition(
            target=NegotiationStatus.ACCEPTED,
            actor=agent_identity_responder.agent_id,
            action=NegotiationAction.ACCEPT,
        )
        assert sm.is_terminal() is True

    def test_on_transition_callback(
        self,
        negotiation_session: NegotiationSession,
        agent_identity_initiator: AgentIdentity,
    ):
        """Test transition callbacks are invoked."""
        sm = NegotiationStateMachine(negotiation_session)
        callback_invoked = []

        def callback(old_status, new_status, turn):
            callback_invoked.append((old_status, new_status))

        sm.on_transition(callback)
        sm.transition(
            target=NegotiationStatus.PROPOSAL_SENT,
            actor=agent_identity_initiator.agent_id,
            action=NegotiationAction.PROPOSE,
        )
        assert len(callback_invoked) == 1
        assert callback_invoked[0] == (
            NegotiationStatus.INITIATED,
            NegotiationStatus.PROPOSAL_SENT,
        )

    def test_get_latest_proposal_none(self, negotiation_session: NegotiationSession):
        """Test get_latest_proposal returns None when no proposals."""
        sm = NegotiationStateMachine(negotiation_session)
        assert sm.get_latest_proposal() is None

    def test_get_latest_proposal(
        self,
        negotiation_session: NegotiationSession,
        agent_identity_initiator: AgentIdentity,
        capability_request: CapabilityRequest,
        capability_offer: CapabilityOffer,
        negotiation_terms: NegotiationTerms,
    ):
        """Test get_latest_proposal returns the most recent proposal."""
        sm = NegotiationStateMachine(negotiation_session)
        proposal = NegotiationProposal.create(
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
        )
        sm.transition(
            target=NegotiationStatus.PROPOSAL_SENT,
            actor=agent_identity_initiator.agent_id,
            action=NegotiationAction.PROPOSE,
            proposal=proposal,
        )
        latest = sm.get_latest_proposal()
        assert latest is not None
        assert latest.proposal_id == proposal.proposal_id

    def test_full_negotiation_flow(
        self,
        negotiation_session: NegotiationSession,
        agent_identity_initiator: AgentIdentity,
        agent_identity_responder: AgentIdentity,
        capability_request: CapabilityRequest,
        capability_offer: CapabilityOffer,
        negotiation_terms: NegotiationTerms,
    ):
        """Test a complete negotiation flow from start to acceptance."""
        sm = NegotiationStateMachine(negotiation_session)

        # Step 1: Initiator sends proposal
        proposal = NegotiationProposal.create(
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
        )
        sm.transition(
            target=NegotiationStatus.PROPOSAL_SENT,
            actor=agent_identity_initiator.agent_id,
            action=NegotiationAction.PROPOSE,
            proposal=proposal,
        )
        assert sm.session.status == NegotiationStatus.PROPOSAL_SENT

        # Step 2: Responder sends counter-offer
        counter_proposal = NegotiationProposal.create(
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=NegotiationTerms(duration_seconds=7200, auto_renew=True),
        )
        sm.transition(
            target=NegotiationStatus.COUNTER_OFFERED,
            actor=agent_identity_responder.agent_id,
            action=NegotiationAction.COUNTER,
            proposal=counter_proposal,
        )
        assert sm.session.status == NegotiationStatus.COUNTER_OFFERED

        # Step 3: Initiator accepts
        sm.transition(
            target=NegotiationStatus.ACCEPTED,
            actor=agent_identity_initiator.agent_id,
            action=NegotiationAction.ACCEPT,
            rationale="Terms acceptable",
        )
        assert sm.session.status == NegotiationStatus.ACCEPTED
        assert sm.is_terminal() is True
        assert len(sm.session.history) == 3


# ============================================
# Test Proposal Evaluator
# ============================================


class TestProposalEvaluator:
    """Tests for ProposalEvaluator class."""

    def test_create_evaluator(
        self,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
    ):
        """Test creating a proposal evaluator."""
        evaluator = ProposalEvaluator(
            our_capabilities=[simple_capability],
            policy=evaluation_policy,
        )
        assert evaluator.our_capabilities == [simple_capability]
        assert evaluator.policy == evaluation_policy

    def test_evaluate_acceptable_proposal(
        self,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
        capability_offer: CapabilityOffer,
    ):
        """Test evaluating an acceptable proposal."""
        evaluator = ProposalEvaluator(
            our_capabilities=[simple_capability],
            policy=evaluation_policy,
        )
        # Create a proposal requesting a capability we have
        request = CapabilityRequest(
            capability_type="action",
            priority=RequestPriority.REQUIRED,
        )
        terms = NegotiationTerms(
            duration_seconds=3600,
            auto_renew=True,
            termination_conditions=["expiration"],
        )
        proposal = NegotiationProposal.create(
            requested_capabilities=[request],
            offered_capabilities=[capability_offer, capability_offer, capability_offer],
            terms=terms,
        )

        # Set high auto_accept_threshold to force counter-offer
        evaluation_policy.auto_accept_threshold = 0.99
        evaluation = evaluator.evaluate(proposal)

        assert evaluation.can_satisfy is True
        assert evaluation.score >= 0.0
        assert evaluation.score <= 1.0

    def test_evaluate_unsatisfiable_proposal(
        self,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
        capability_offer: CapabilityOffer,
    ):
        """Test evaluating a proposal we cannot satisfy."""
        evaluator = ProposalEvaluator(
            our_capabilities=[simple_capability],
            policy=evaluation_policy,
        )
        # Request a capability we don't have
        request = CapabilityRequest(
            capability_type="nonexistent-capability",
            priority=RequestPriority.REQUIRED,
        )
        proposal = NegotiationProposal.create(
            requested_capabilities=[request],
            offered_capabilities=[capability_offer],
            terms=NegotiationTerms(duration_seconds=3600),
        )
        evaluation = evaluator.evaluate(proposal)

        assert evaluation.can_satisfy is False
        assert evaluation.decision == NegotiationAction.REJECT
        assert evaluation.gap_analysis is not None

    def test_evaluate_auto_accept(
        self,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
        capability_offer: CapabilityOffer,
    ):
        """Test that high-scoring proposals are auto-accepted."""
        # Lower the threshold significantly
        evaluation_policy.auto_accept_threshold = 0.3
        evaluator = ProposalEvaluator(
            our_capabilities=[simple_capability],
            policy=evaluation_policy,
        )
        # Create a good proposal
        request = CapabilityRequest(
            capability_type="action",
            priority=RequestPriority.OPTIONAL,
        )
        terms = NegotiationTerms(
            duration_seconds=7200,  # Longer than minimum
            auto_renew=True,
            termination_conditions=["expiration"],
        )
        proposal = NegotiationProposal.create(
            requested_capabilities=[request],
            offered_capabilities=[capability_offer, capability_offer, capability_offer],
            terms=terms,
        )
        evaluation = evaluator.evaluate(proposal)

        assert evaluation.decision == NegotiationAction.ACCEPT
        assert evaluation.score >= evaluation_policy.auto_accept_threshold

    def test_generate_counter_proposal(
        self,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
        capability_offer: CapabilityOffer,
    ):
        """Test generating a counter-proposal."""
        evaluator = ProposalEvaluator(
            our_capabilities=[simple_capability],
            policy=evaluation_policy,
        )
        request = CapabilityRequest(
            capability_type="action",
            priority=RequestPriority.REQUIRED,
        )
        original = NegotiationProposal.create(
            requested_capabilities=[request],
            offered_capabilities=[capability_offer],
            terms=NegotiationTerms(duration_seconds=600),  # Short duration
        )
        gaps = GapAnalysis(suggested_modifications=["Increase duration"])

        counter = evaluator.generate_counter_proposal(original, gaps)

        assert counter is not None
        assert counter.proposal_id != original.proposal_id
        # Counter should adjust duration to minimum
        assert counter.terms.duration_seconds >= evaluation_policy.min_acceptable_terms.min_duration_seconds


# ============================================
# Test Negotiation Manager
# ============================================


class TestNegotiationManager:
    """Tests for NegotiationManager class."""

    def test_create_manager(
        self,
        agent_identity_initiator: AgentIdentity,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
    ):
        """Test creating a negotiation manager."""
        manager = NegotiationManager(
            our_identity=agent_identity_initiator,
            our_capabilities=[simple_capability],
            evaluation_policy=evaluation_policy,
        )
        assert manager.identity == agent_identity_initiator
        assert len(manager.capabilities) == 1

    def test_initiate_negotiation(
        self,
        agent_identity_initiator: AgentIdentity,
        agent_identity_responder: AgentIdentity,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
        capability_request: CapabilityRequest,
        capability_offer: CapabilityOffer,
        negotiation_terms: NegotiationTerms,
    ):
        """Test initiating a negotiation."""
        manager = NegotiationManager(
            our_identity=agent_identity_initiator,
            our_capabilities=[simple_capability],
            evaluation_policy=evaluation_policy,
        )
        session = manager.initiate(
            target=agent_identity_responder,
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
        )

        assert session is not None
        assert session.status == NegotiationStatus.PROPOSAL_SENT
        assert session.initiator == agent_identity_initiator
        assert session.responder == agent_identity_responder
        assert len(session.history) == 1

    def test_get_session(
        self,
        agent_identity_initiator: AgentIdentity,
        agent_identity_responder: AgentIdentity,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
        capability_request: CapabilityRequest,
        capability_offer: CapabilityOffer,
        negotiation_terms: NegotiationTerms,
    ):
        """Test getting a session by ID."""
        manager = NegotiationManager(
            our_identity=agent_identity_initiator,
            our_capabilities=[simple_capability],
            evaluation_policy=evaluation_policy,
        )
        session = manager.initiate(
            target=agent_identity_responder,
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
        )

        retrieved = manager.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id

    def test_get_session_not_found(
        self,
        agent_identity_initiator: AgentIdentity,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
    ):
        """Test getting a non-existent session."""
        manager = NegotiationManager(
            our_identity=agent_identity_initiator,
            our_capabilities=[simple_capability],
            evaluation_policy=evaluation_policy,
        )
        retrieved = manager.get_session("nonexistent-id")
        assert retrieved is None

    def test_list_sessions(
        self,
        agent_identity_initiator: AgentIdentity,
        agent_identity_responder: AgentIdentity,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
        capability_request: CapabilityRequest,
        capability_offer: CapabilityOffer,
        negotiation_terms: NegotiationTerms,
    ):
        """Test listing all sessions."""
        manager = NegotiationManager(
            our_identity=agent_identity_initiator,
            our_capabilities=[simple_capability],
            evaluation_policy=evaluation_policy,
        )
        # Create two sessions
        manager.initiate(
            target=agent_identity_responder,
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
        )
        manager.initiate(
            target=agent_identity_responder,
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
        )

        sessions = manager.list_sessions()
        assert len(sessions) == 2

    def test_list_sessions_with_filter(
        self,
        agent_identity_initiator: AgentIdentity,
        agent_identity_responder: AgentIdentity,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
        capability_request: CapabilityRequest,
        capability_offer: CapabilityOffer,
        negotiation_terms: NegotiationTerms,
    ):
        """Test listing sessions with status filter."""
        manager = NegotiationManager(
            our_identity=agent_identity_initiator,
            our_capabilities=[simple_capability],
            evaluation_policy=evaluation_policy,
        )
        manager.initiate(
            target=agent_identity_responder,
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
        )

        # Filter by PROPOSAL_SENT (should find 1)
        proposal_sent = manager.list_sessions(status_filter=NegotiationStatus.PROPOSAL_SENT)
        assert len(proposal_sent) == 1

        # Filter by ACCEPTED (should find 0)
        accepted = manager.list_sessions(status_filter=NegotiationStatus.ACCEPTED)
        assert len(accepted) == 0

    def test_receive_proposal_accept(
        self,
        agent_identity_initiator: AgentIdentity,
        agent_identity_responder: AgentIdentity,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
        capability_request: CapabilityRequest,
        capability_offer: CapabilityOffer,
        negotiation_terms: NegotiationTerms,
    ):
        """Test receiving and auto-accepting a proposal."""
        # Lower threshold for auto-accept
        evaluation_policy.auto_accept_threshold = 0.3
        manager = NegotiationManager(
            our_identity=agent_identity_initiator,
            our_capabilities=[simple_capability],
            evaluation_policy=evaluation_policy,
        )
        session = manager.initiate(
            target=agent_identity_responder,
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
        )

        # Create incoming proposal with good terms
        incoming_proposal = NegotiationProposal.create(
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="action",
                    priority=RequestPriority.OPTIONAL,
                )
            ],
            offered_capabilities=[capability_offer, capability_offer, capability_offer],
            terms=NegotiationTerms(
                duration_seconds=7200,
                auto_renew=True,
                termination_conditions=["expiration"],
            ),
        )
        evaluation = manager.receive_proposal(session.session_id, incoming_proposal)

        assert evaluation is not None
        assert evaluation.decision == NegotiationAction.ACCEPT

    def test_receive_proposal_reject(
        self,
        agent_identity_initiator: AgentIdentity,
        agent_identity_responder: AgentIdentity,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
        capability_request: CapabilityRequest,
        capability_offer: CapabilityOffer,
        negotiation_terms: NegotiationTerms,
    ):
        """Test receiving and rejecting a proposal."""
        manager = NegotiationManager(
            our_identity=agent_identity_initiator,
            our_capabilities=[simple_capability],
            evaluation_policy=evaluation_policy,
        )
        session = manager.initiate(
            target=agent_identity_responder,
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
        )

        # Create incoming proposal requesting capability we don't have
        incoming_proposal = NegotiationProposal.create(
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="nonexistent",
                    priority=RequestPriority.REQUIRED,
                )
            ],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
        )
        evaluation = manager.receive_proposal(session.session_id, incoming_proposal)

        assert evaluation.decision == NegotiationAction.REJECT
        assert evaluation.can_satisfy is False

    def test_receive_proposal_unknown_session(
        self,
        agent_identity_initiator: AgentIdentity,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
        capability_request: CapabilityRequest,
        capability_offer: CapabilityOffer,
        negotiation_terms: NegotiationTerms,
    ):
        """Test receiving proposal for unknown session raises error."""
        manager = NegotiationManager(
            our_identity=agent_identity_initiator,
            our_capabilities=[simple_capability],
            evaluation_policy=evaluation_policy,
        )
        proposal = NegotiationProposal.create(
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
        )

        with pytest.raises(ValueError, match="Unknown session"):
            manager.receive_proposal("nonexistent-id", proposal)

    def test_finalize_agreement(
        self,
        agent_identity_initiator: AgentIdentity,
        agent_identity_responder: AgentIdentity,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
        capability_request: CapabilityRequest,
        capability_offer: CapabilityOffer,
        negotiation_terms: NegotiationTerms,
    ):
        """Test finalizing an accepted negotiation into an agreement."""
        evaluation_policy.auto_accept_threshold = 0.3
        manager = NegotiationManager(
            our_identity=agent_identity_initiator,
            our_capabilities=[simple_capability],
            evaluation_policy=evaluation_policy,
        )
        session = manager.initiate(
            target=agent_identity_responder,
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
        )

        # Accept proposal
        incoming_proposal = NegotiationProposal.create(
            requested_capabilities=[
                CapabilityRequest(capability_type="action", priority=RequestPriority.OPTIONAL)
            ],
            offered_capabilities=[capability_offer, capability_offer, capability_offer],
            terms=NegotiationTerms(duration_seconds=7200, auto_renew=True),
        )
        manager.receive_proposal(session.session_id, incoming_proposal)

        # Finalize
        agreement = manager.finalize(session.session_id)

        assert agreement is not None
        assert len(agreement.parties) == 2
        assert agreement.terms is not None

    def test_finalize_not_accepted_raises(
        self,
        agent_identity_initiator: AgentIdentity,
        agent_identity_responder: AgentIdentity,
        simple_capability: AgentCapability,
        evaluation_policy: EvaluationPolicy,
        capability_request: CapabilityRequest,
        capability_offer: CapabilityOffer,
        negotiation_terms: NegotiationTerms,
    ):
        """Test finalize raises error if session not in ACCEPTED state."""
        manager = NegotiationManager(
            our_identity=agent_identity_initiator,
            our_capabilities=[simple_capability],
            evaluation_policy=evaluation_policy,
        )
        session = manager.initiate(
            target=agent_identity_responder,
            requested_capabilities=[capability_request],
            offered_capabilities=[capability_offer],
            terms=negotiation_terms,
        )

        with pytest.raises(ValueError, match="not in ACCEPTED state"):
            manager.finalize(session.session_id)
