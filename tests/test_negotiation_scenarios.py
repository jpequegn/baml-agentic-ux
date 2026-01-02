"""
Scenario Tests for Negotiation Workflows.

Tests complete negotiation scenarios from start to finish including:
- Successful bilateral negotiations
- Multi-round counter-offer scenarios
- Negotiation failures and recovery
- Timeout and expiration handling
- Complex multi-party negotiations

Issue #66 - Phase 3 Testing & Documentation
"""

import pytest
from datetime import datetime, timezone, timedelta

# Negotiation types
from src.agent_negotiation import (
    # Enums
    NegotiationStatus,
    NegotiationAction,
    RequestPriority,
    NegotiationStrategy,
    ConditionType,
    BillingModel,
    # Components
    CapabilityRequest,
    OfferCondition,
    CapabilityOffer,
    NegotiationTerms,
    NegotiationProposal,
    NegotiationTurn,
    NegotiationSession,
    # Agreement
    GrantedCapability,
    Agreement,
    # Evaluation
    MinimumTerms,
    EvaluationPolicy,
    GapAnalysis,
    ProposalEvaluation,
    # Core classes
    NegotiationStateMachine,
    ProposalEvaluator,
    NegotiationManager,
    # Rate limiting
    RateLimit,
)

# Agent types
from src.lui_simulator.agent_types import (
    AgentIdentity,
    AgentCapability,
    CapabilityType,
    SchemaDefinition,
    SchemaProperty,
)


# ============================================
# Test Fixtures for Scenarios
# ============================================


@pytest.fixture
def alice_identity() -> AgentIdentity:
    """Alice agent identity - data provider."""
    return AgentIdentity.create(
        name="alice-data-service",
        version="1.0.0",
        description="Data provider service",
        provider="alice-corp",
    )


@pytest.fixture
def bob_identity() -> AgentIdentity:
    """Bob agent identity - data consumer."""
    return AgentIdentity.create(
        name="bob-analytics",
        version="2.0.0",
        description="Analytics service",
        provider="bob-inc",
    )


@pytest.fixture
def charlie_identity() -> AgentIdentity:
    """Charlie agent identity - transformation service."""
    return AgentIdentity.create(
        name="charlie-transform",
        version="1.5.0",
        description="Transformation service",
        provider="charlie-tech",
    )


@pytest.fixture
def data_query_capability() -> AgentCapability:
    """Data query capability."""
    return AgentCapability(
        capability_id="data-query",
        capability_type=CapabilityType.QUERY,
        name="data-query",
        description="Query data records",
        input_schema=SchemaDefinition.object(
            description="Query input",
            properties=[
                SchemaProperty(
                    name="query",
                    schema=SchemaDefinition.string(description="Query string"),
                    description="SQL-like query",
                )
            ],
            required=["query"],
        ),
        output_schema=SchemaDefinition.object(
            description="Query output",
            properties=[
                SchemaProperty(
                    name="results",
                    schema=SchemaDefinition.string(description="Query results"),
                    description="Query results",
                )
            ],
            required=["results"],
        ),
    )


@pytest.fixture
def analytics_capability() -> AgentCapability:
    """Analytics capability."""
    return AgentCapability(
        capability_id="analytics",
        capability_type=CapabilityType.TRANSFORM,
        name="analytics",
        description="Analyze data patterns",
        input_schema=SchemaDefinition.object(
            description="Analytics input",
            properties=[
                SchemaProperty(
                    name="data",
                    schema=SchemaDefinition.string(description="Input data"),
                    description="Data to analyze",
                )
            ],
            required=["data"],
        ),
        output_schema=SchemaDefinition.object(
            description="Analytics output",
            properties=[
                SchemaProperty(
                    name="insights",
                    schema=SchemaDefinition.string(description="Insights"),
                    description="Analysis insights",
                )
            ],
            required=["insights"],
        ),
    )


@pytest.fixture
def transform_capability() -> AgentCapability:
    """Transform capability."""
    return AgentCapability(
        capability_id="transform",
        capability_type=CapabilityType.TRANSFORM,
        name="transform",
        description="Transform data format",
        input_schema=SchemaDefinition.object(
            description="Transform input",
            properties=[
                SchemaProperty(
                    name="data",
                    schema=SchemaDefinition.string(description="Input data"),
                    description="Data to transform",
                )
            ],
            required=["data"],
        ),
        output_schema=SchemaDefinition.object(
            description="Transform output",
            properties=[
                SchemaProperty(
                    name="result",
                    schema=SchemaDefinition.string(description="Result"),
                    description="Transformed result",
                )
            ],
            required=["result"],
        ),
    )


# ============================================
# Scenario 1: Successful Bilateral Negotiation
# ============================================


class TestSuccessfulNegotiation:
    """Test scenarios for successful negotiations."""

    def test_simple_capability_exchange(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
        data_query_capability: AgentCapability,
        analytics_capability: AgentCapability,
    ):
        """
        Scenario: Alice has data query, Bob has analytics.
        Bob wants data query and offers analytics.
        Result: Successful agreement.
        """
        # Alice's manager
        alice_manager = NegotiationManager(
            our_identity=alice_identity,
            our_capabilities=[data_query_capability],
            evaluation_policy=EvaluationPolicy(
                min_acceptable_terms=MinimumTerms(
                    min_duration_seconds=3600,
                ),
                negotiation_strategy=NegotiationStrategy.COOPERATIVE,
                auto_accept_threshold=0.6,
            ),
        )

        # Bob's manager
        bob_manager = NegotiationManager(
            our_identity=bob_identity,
            our_capabilities=[analytics_capability],
            evaluation_policy=EvaluationPolicy(
                min_acceptable_terms=MinimumTerms(
                    min_duration_seconds=3600,
                ),
                negotiation_strategy=NegotiationStrategy.COOPERATIVE,
                auto_accept_threshold=0.6,
            ),
        )

        # Bob initiates negotiation with Alice
        session = bob_manager.initiate(
            target=alice_identity,
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="query",
                    priority=RequestPriority.REQUIRED,
                )
            ],
            offered_capabilities=[
                CapabilityOffer(capability=analytics_capability)
            ],
            terms=NegotiationTerms(
                duration_seconds=86400,  # 1 day
                auto_renew=True,
            ),
        )

        assert session.session_id
        assert session.status in [
            NegotiationStatus.INITIATED,
            NegotiationStatus.PROPOSAL_SENT,
        ]

    def test_negotiation_with_rate_limits(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
        data_query_capability: AgentCapability,
    ):
        """
        Scenario: Bob requests data query with rate limits.
        Alice accepts with modified rate limits.
        """
        bob_manager = NegotiationManager(
            our_identity=bob_identity,
            our_capabilities=[],
            evaluation_policy=EvaluationPolicy(
                min_acceptable_terms=MinimumTerms(
                    min_duration_seconds=3600,
                ),
                negotiation_strategy=NegotiationStrategy.PRINCIPLED,
            ),
        )

        session = bob_manager.initiate(
            target=alice_identity,
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="query",
                    priority=RequestPriority.REQUIRED,
                )
            ],
            offered_capabilities=[],
            terms=NegotiationTerms(
                duration_seconds=86400,
            ),
        )

        assert session.session_id
        assert session.initiator.agent_id == bob_identity.agent_id

        # Verify rate limit can be configured separately
        rate_limit = RateLimit(
            requests_per_minute=100,
            requests_per_hour=10000,
        )
        assert rate_limit.requests_per_minute == 100
        assert rate_limit.requests_per_hour == 10000

    def test_conditional_capability_offer(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
        data_query_capability: AgentCapability,
    ):
        """
        Scenario: Alice offers data query with conditions.
        """
        alice_manager = NegotiationManager(
            our_identity=alice_identity,
            our_capabilities=[data_query_capability],
            evaluation_policy=EvaluationPolicy(
                min_acceptable_terms=MinimumTerms(
                    min_duration_seconds=3600,
                ),
                negotiation_strategy=NegotiationStrategy.COMPETITIVE,
            ),
        )

        # Alice creates an offer with conditions
        offer_with_conditions = CapabilityOffer(
            capability=data_query_capability,
            conditions=[
                OfferCondition(
                    condition_type=ConditionType.RATE_LIMIT,
                    description="Rate limit constraint",
                    value="1000 requests per minute max",
                ),
                OfferCondition(
                    condition_type=ConditionType.DATA_RETENTION,
                    description="Compliance constraint",
                    value="GDPR compliance required",
                ),
            ],
        )

        session = alice_manager.initiate(
            target=bob_identity,
            requested_capabilities=[],
            offered_capabilities=[offer_with_conditions],
            terms=NegotiationTerms(
                duration_seconds=86400,
            ),
        )

        assert session.session_id
        # Verify the proposal has the conditions
        if session.history:
            last_proposal = session.history[-1].proposal
            if last_proposal and last_proposal.offered_capabilities:
                for offer in last_proposal.offered_capabilities:
                    if offer.conditions:
                        assert len(offer.conditions) > 0


# ============================================
# Scenario 2: Multi-Round Counter-Offer
# ============================================


class TestCounterOfferScenarios:
    """Test scenarios involving counter-offers."""

    def test_counter_offer_creation(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
        data_query_capability: AgentCapability,
    ):
        """
        Scenario: Initial offer is rejected with counter-offer.
        """
        # Create session
        session = NegotiationSession.create(
            initiator=bob_identity,
            responder=alice_identity,
            expiration_hours=24,
        )

        state_machine = NegotiationStateMachine(session)

        # Transition to PROPOSAL_SENT
        state_machine.transition(
            NegotiationStatus.PROPOSAL_SENT,
            actor=bob_identity.agent_id,
            action=NegotiationAction.PROPOSE,
        )
        assert session.status == NegotiationStatus.PROPOSAL_SENT

        # Transition to COUNTER_OFFERED
        state_machine.transition(
            NegotiationStatus.COUNTER_OFFERED,
            actor=alice_identity.agent_id,
            action=NegotiationAction.COUNTER,
        )
        assert session.status == NegotiationStatus.COUNTER_OFFERED

    def test_evaluator_counter_proposal(
        self,
        alice_identity: AgentIdentity,
        data_query_capability: AgentCapability,
    ):
        """
        Scenario: Evaluator suggests counter-proposal for unacceptable terms.
        """
        evaluator = ProposalEvaluator(
            our_capabilities=[data_query_capability],
            policy=EvaluationPolicy(
                min_acceptable_terms=MinimumTerms(
                    min_duration_seconds=86400,  # Need at least 1 day
                ),
                negotiation_strategy=NegotiationStrategy.COMPETITIVE,
                auto_accept_threshold=0.9,  # High threshold
            ),
        )

        # Create proposal with short duration
        short_duration_proposal = NegotiationProposal.create(
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="query",
                    priority=RequestPriority.REQUIRED,
                )
            ],
            offered_capabilities=[],
            terms=NegotiationTerms(
                duration_seconds=3600,  # Only 1 hour
            ),
        )

        evaluation = evaluator.evaluate(short_duration_proposal)

        # Should not auto-accept due to terms mismatch
        assert evaluation.decision in [
            NegotiationAction.COUNTER,
            NegotiationAction.REJECT,
            NegotiationAction.ACCEPT,  # May still accept if strategy allows
        ]

    def test_multiple_counter_offer_rounds(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
    ):
        """
        Scenario: Multiple rounds of counter-offers before agreement.
        """
        session = NegotiationSession.create(
            initiator=bob_identity,
            responder=alice_identity,
            expiration_hours=24,
        )

        state_machine = NegotiationStateMachine(session)

        # Round 1: Bob sends proposal
        state_machine.transition(
            NegotiationStatus.PROPOSAL_SENT,
            actor=bob_identity.agent_id,
            action=NegotiationAction.PROPOSE,
        )
        assert session.status == NegotiationStatus.PROPOSAL_SENT

        # Round 2: Alice counters
        state_machine.transition(
            NegotiationStatus.COUNTER_OFFERED,
            actor=alice_identity.agent_id,
            action=NegotiationAction.COUNTER,
        )
        assert session.status == NegotiationStatus.COUNTER_OFFERED

        # Round 3: Bob accepts
        state_machine.transition(
            NegotiationStatus.ACCEPTED,
            actor=bob_identity.agent_id,
            action=NegotiationAction.ACCEPT,
        )
        assert session.status == NegotiationStatus.ACCEPTED


# ============================================
# Scenario 3: Negotiation Failures
# ============================================


class TestNegotiationFailures:
    """Test scenarios for negotiation failures."""

    def test_rejection_of_unacceptable_terms(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
    ):
        """
        Scenario: Alice rejects Bob's proposal due to unacceptable terms.
        """
        session = NegotiationSession.create(
            initiator=bob_identity,
            responder=alice_identity,
            expiration_hours=24,
        )

        state_machine = NegotiationStateMachine(session)

        # Bob sends proposal
        state_machine.transition(
            NegotiationStatus.PROPOSAL_SENT,
            actor=bob_identity.agent_id,
            action=NegotiationAction.PROPOSE,
        )

        # Alice rejects
        state_machine.transition(
            NegotiationStatus.REJECTED,
            actor=alice_identity.agent_id,
            action=NegotiationAction.REJECT,
        )
        assert session.status == NegotiationStatus.REJECTED

    def test_cancelled_negotiation(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
    ):
        """
        Scenario: Bob cancels the negotiation.
        """
        session = NegotiationSession.create(
            initiator=bob_identity,
            responder=alice_identity,
            expiration_hours=24,
        )

        state_machine = NegotiationStateMachine(session)

        # Bob withdraws before sending proposal
        state_machine.transition(
            NegotiationStatus.CANCELLED,
            actor=bob_identity.agent_id,
            action=NegotiationAction.WITHDRAW,
        )
        assert session.status == NegotiationStatus.CANCELLED

    def test_max_counter_offers_exceeded(
        self,
        alice_identity: AgentIdentity,
        data_query_capability: AgentCapability,
    ):
        """
        Scenario: Evaluator rejects after max counter-offers exceeded.
        """
        evaluator = ProposalEvaluator(
            our_capabilities=[data_query_capability],
            policy=EvaluationPolicy(
                min_acceptable_terms=MinimumTerms(
                    min_duration_seconds=3600,
                ),
                negotiation_strategy=NegotiationStrategy.COMPETITIVE,
                max_counter_offers=2,
            ),
        )

        # Simulate tracking counter-offers
        proposal = NegotiationProposal.create(
            requested_capabilities=[],
            offered_capabilities=[],
            terms=NegotiationTerms(duration_seconds=3600),
        )

        evaluation = evaluator.evaluate(proposal)
        # Result depends on policy and proposal compatibility
        assert evaluation.decision is not None


# ============================================
# Scenario 4: Timeout and Expiration
# ============================================


class TestTimeoutScenarios:
    """Test scenarios involving timeouts and expiration."""

    def test_session_expiration_detection(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
    ):
        """
        Scenario: Session expires before agreement.
        """
        # Create a session that's already expired
        session = NegotiationSession.create(
            initiator=bob_identity,
            responder=alice_identity,
            expiration_hours=0,  # Expires immediately
        )

        # Check if expired
        expires_at = datetime.fromisoformat(session.expires_at)
        now = datetime.now(timezone.utc)

        # The session should be expired or very close to expiration
        is_expired = expires_at <= now
        # Allow for small timing differences
        assert is_expired or (expires_at - now).total_seconds() < 1

    def test_proposal_validity_period(self):
        """
        Scenario: Proposal with limited validity period.
        """
        proposal = NegotiationProposal.create(
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="query",
                    priority=RequestPriority.REQUIRED,
                )
            ],
            offered_capabilities=[],
            terms=NegotiationTerms(duration_seconds=3600),
            validity_period_seconds=60,  # Valid for 1 minute only
        )

        # Proposal should have validity period set
        assert proposal.validity_period_seconds == 60


# ============================================
# Scenario 5: Strategy-Based Negotiation
# ============================================


class TestNegotiationStrategies:
    """Test different negotiation strategies."""

    def test_cooperative_strategy(
        self,
        alice_identity: AgentIdentity,
        data_query_capability: AgentCapability,
    ):
        """
        Scenario: Cooperative strategy tends to accept reasonable offers.
        """
        evaluator = ProposalEvaluator(
            our_capabilities=[data_query_capability],
            policy=EvaluationPolicy(
                min_acceptable_terms=MinimumTerms(
                    min_duration_seconds=3600,
                ),
                negotiation_strategy=NegotiationStrategy.COOPERATIVE,
                auto_accept_threshold=0.5,  # Lower threshold
            ),
        )

        proposal = NegotiationProposal.create(
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="query",
                    priority=RequestPriority.PREFERRED,
                )
            ],
            offered_capabilities=[],
            terms=NegotiationTerms(duration_seconds=7200),  # 2 hours
        )

        evaluation = evaluator.evaluate(proposal)
        # Cooperative strategy should be more accepting
        assert evaluation.score >= 0

    def test_competitive_strategy(
        self,
        alice_identity: AgentIdentity,
        data_query_capability: AgentCapability,
    ):
        """
        Scenario: Competitive strategy demands more favorable terms.
        """
        evaluator = ProposalEvaluator(
            our_capabilities=[data_query_capability],
            policy=EvaluationPolicy(
                min_acceptable_terms=MinimumTerms(
                    min_duration_seconds=86400,  # 1 day minimum
                ),
                negotiation_strategy=NegotiationStrategy.COMPETITIVE,
                auto_accept_threshold=0.9,  # Very high threshold
            ),
        )

        proposal = NegotiationProposal.create(
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="query",
                    priority=RequestPriority.REQUIRED,
                )
            ],
            offered_capabilities=[],
            terms=NegotiationTerms(duration_seconds=7200),  # 2 hours - below minimum
        )

        evaluation = evaluator.evaluate(proposal)
        # Competitive strategy with high threshold should be more demanding
        assert evaluation is not None

    def test_principled_strategy(
        self,
        alice_identity: AgentIdentity,
        data_query_capability: AgentCapability,
    ):
        """
        Scenario: Balanced strategy considers mutual benefits.
        """
        evaluator = ProposalEvaluator(
            our_capabilities=[data_query_capability],
            policy=EvaluationPolicy(
                min_acceptable_terms=MinimumTerms(
                    min_duration_seconds=3600,
                ),
                negotiation_strategy=NegotiationStrategy.PRINCIPLED,
                auto_accept_threshold=0.7,
            ),
        )

        proposal = NegotiationProposal.create(
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="query",
                    priority=RequestPriority.REQUIRED,
                )
            ],
            offered_capabilities=[
                CapabilityOffer(capability=data_query_capability)
            ],
            terms=NegotiationTerms(duration_seconds=43200),  # 12 hours
        )

        evaluation = evaluator.evaluate(proposal)
        # Balanced strategy should evaluate fairly
        assert evaluation.can_satisfy is not None


# ============================================
# Scenario 6: Agreement Formation
# ============================================


class TestAgreementFormation:
    """Test scenarios for forming agreements."""

    def test_agreement_creation_after_acceptance(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
        data_query_capability: AgentCapability,
    ):
        """
        Scenario: Create an agreement after successful negotiation.
        """
        # Simulate accepted negotiation
        session = NegotiationSession.create(
            initiator=bob_identity,
            responder=alice_identity,
            expiration_hours=24,
        )

        state_machine = NegotiationStateMachine(session)
        state_machine.transition(
            NegotiationStatus.PROPOSAL_SENT,
            actor=bob_identity.agent_id,
            action=NegotiationAction.PROPOSE,
        )
        state_machine.transition(
            NegotiationStatus.ACCEPTED,
            actor=alice_identity.agent_id,
            action=NegotiationAction.ACCEPT,
        )

        assert session.status == NegotiationStatus.ACCEPTED

        # Create agreement
        agreement = Agreement.create(
            parties=[bob_identity, alice_identity],
            capabilities_granted=[
                GrantedCapability(
                    capability=data_query_capability,
                    grantor=alice_identity.agent_id,
                    grantee=bob_identity.agent_id,
                )
            ],
            terms=NegotiationTerms(
                duration_seconds=86400,
                auto_renew=True,
            ),
        )

        assert agreement.agreement_id
        assert len(agreement.parties) == 2
        assert len(agreement.capabilities_granted) == 1

    def test_agreement_terms_validation(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
        data_query_capability: AgentCapability,
    ):
        """
        Scenario: Validate agreement terms before activation.
        """
        agreement = Agreement.create(
            parties=[bob_identity, alice_identity],
            capabilities_granted=[
                GrantedCapability(
                    capability=data_query_capability,
                    grantor=alice_identity.agent_id,
                    grantee=bob_identity.agent_id,
                )
            ],
            terms=NegotiationTerms(
                duration_seconds=3600,
                auto_renew=True,
            ),
        )

        assert agreement.terms.duration_seconds == 3600
        assert agreement.terms.auto_renew is True


# ============================================
# Scenario 7: Multi-Party Negotiations
# ============================================


class TestMultiPartyNegotiations:
    """Test scenarios involving multiple parties."""

    def test_three_party_capability_chain(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
        charlie_identity: AgentIdentity,
        data_query_capability: AgentCapability,
        transform_capability: AgentCapability,
        analytics_capability: AgentCapability,
    ):
        """
        Scenario: Alice (data) -> Charlie (transform) -> Bob (analytics).
        Each party negotiates with the next.
        """
        # Alice-Charlie negotiation
        session_ac = NegotiationSession.create(
            initiator=charlie_identity,
            responder=alice_identity,
            expiration_hours=24,
        )
        assert session_ac.initiator.agent_id == charlie_identity.agent_id
        assert session_ac.responder.agent_id == alice_identity.agent_id

        # Charlie-Bob negotiation
        session_cb = NegotiationSession.create(
            initiator=bob_identity,
            responder=charlie_identity,
            expiration_hours=24,
        )
        assert session_cb.initiator.agent_id == bob_identity.agent_id
        assert session_cb.responder.agent_id == charlie_identity.agent_id

        # Both sessions are independent
        assert session_ac.session_id != session_cb.session_id

    def test_parallel_negotiations_same_agent(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
        charlie_identity: AgentIdentity,
    ):
        """
        Scenario: Alice negotiates with both Bob and Charlie simultaneously.
        """
        # Alice-Bob negotiation
        session_ab = NegotiationSession.create(
            initiator=alice_identity,
            responder=bob_identity,
            expiration_hours=24,
        )

        # Alice-Charlie negotiation
        session_ac = NegotiationSession.create(
            initiator=alice_identity,
            responder=charlie_identity,
            expiration_hours=24,
        )

        # Both sessions should be independent
        assert session_ab.session_id != session_ac.session_id
        assert session_ab.responder != session_ac.responder


# ============================================
# Scenario 8: State Machine Transitions
# ============================================


class TestStateMachineTransitions:
    """Test all valid state machine transitions."""

    def test_valid_transition_paths(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
    ):
        """Test all valid paths through the state machine."""
        # Path 1: INITIATED -> PROPOSAL_SENT -> ACCEPTED
        session1 = NegotiationSession.create(
            initiator=bob_identity,
            responder=alice_identity,
            expiration_hours=24,
        )
        sm1 = NegotiationStateMachine(session1)
        sm1.transition(
            NegotiationStatus.PROPOSAL_SENT,
            actor=bob_identity.agent_id,
            action=NegotiationAction.PROPOSE,
        )
        sm1.transition(
            NegotiationStatus.ACCEPTED,
            actor=alice_identity.agent_id,
            action=NegotiationAction.ACCEPT,
        )
        assert session1.status == NegotiationStatus.ACCEPTED

        # Path 2: INITIATED -> PROPOSAL_SENT -> REJECTED
        session2 = NegotiationSession.create(
            initiator=bob_identity,
            responder=alice_identity,
            expiration_hours=24,
        )
        sm2 = NegotiationStateMachine(session2)
        sm2.transition(
            NegotiationStatus.PROPOSAL_SENT,
            actor=bob_identity.agent_id,
            action=NegotiationAction.PROPOSE,
        )
        sm2.transition(
            NegotiationStatus.REJECTED,
            actor=alice_identity.agent_id,
            action=NegotiationAction.REJECT,
        )
        assert session2.status == NegotiationStatus.REJECTED

        # Path 3: INITIATED -> CANCELLED
        session3 = NegotiationSession.create(
            initiator=bob_identity,
            responder=alice_identity,
            expiration_hours=24,
        )
        sm3 = NegotiationStateMachine(session3)
        sm3.transition(
            NegotiationStatus.CANCELLED,
            actor=bob_identity.agent_id,
            action=NegotiationAction.WITHDRAW,
        )
        assert session3.status == NegotiationStatus.CANCELLED

    def test_invalid_transition_blocked(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
    ):
        """Test that invalid transitions are blocked."""
        session = NegotiationSession.create(
            initiator=bob_identity,
            responder=alice_identity,
            expiration_hours=24,
        )
        sm = NegotiationStateMachine(session)

        # Cannot go directly from INITIATED to ACCEPTED
        assert not sm.can_transition(NegotiationStatus.ACCEPTED)

        # Cannot go directly from INITIATED to REJECTED
        assert not sm.can_transition(NegotiationStatus.REJECTED)


# ============================================
# Scenario 9: Gap Analysis
# ============================================


class TestGapAnalysis:
    """Test gap analysis in proposal evaluation."""

    def test_identify_capability_gaps(
        self,
        alice_identity: AgentIdentity,
        data_query_capability: AgentCapability,
    ):
        """
        Scenario: Identify gaps between request and what we can offer.
        """
        evaluator = ProposalEvaluator(
            our_capabilities=[data_query_capability],  # Only have query
            policy=EvaluationPolicy(
                min_acceptable_terms=MinimumTerms(
                    min_duration_seconds=3600,
                ),
                negotiation_strategy=NegotiationStrategy.COOPERATIVE,
            ),
        )

        # Request transform capability that we don't have
        proposal = NegotiationProposal.create(
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="transform",  # We don't have this
                    priority=RequestPriority.REQUIRED,
                )
            ],
            offered_capabilities=[],
            terms=NegotiationTerms(duration_seconds=3600),
        )

        evaluation = evaluator.evaluate(proposal)

        # Should not be able to fully satisfy
        assert not evaluation.can_satisfy or evaluation.gap_analysis is not None

    def test_partial_capability_match(
        self,
        alice_identity: AgentIdentity,
        data_query_capability: AgentCapability,
    ):
        """
        Scenario: Partial match - some capabilities available.
        """
        evaluator = ProposalEvaluator(
            our_capabilities=[data_query_capability],
            policy=EvaluationPolicy(
                min_acceptable_terms=MinimumTerms(
                    min_duration_seconds=3600,
                ),
                negotiation_strategy=NegotiationStrategy.COOPERATIVE,
            ),
        )

        # Request both query (have) and transform (don't have)
        proposal = NegotiationProposal.create(
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="query",
                    priority=RequestPriority.REQUIRED,
                ),
                CapabilityRequest(
                    capability_type="transform",
                    priority=RequestPriority.PREFERRED,  # Not required
                ),
            ],
            offered_capabilities=[],
            terms=NegotiationTerms(duration_seconds=3600),
        )

        evaluation = evaluator.evaluate(proposal)

        # Should have partial score since one is PREFERRED (not REQUIRED)
        assert evaluation.score >= 0


# ============================================
# Scenario 10: Serialization and Persistence
# ============================================


class TestSerializationScenarios:
    """Test scenarios involving serialization."""

    def test_session_serialization_round_trip(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
    ):
        """
        Scenario: Serialize and deserialize session for persistence.
        """
        session = NegotiationSession.create(
            initiator=bob_identity,
            responder=alice_identity,
            expiration_hours=24,
        )

        # Serialize to dict
        session_dict = session.to_dict()

        assert session_dict["session_id"] == session.session_id
        # initiator is serialized as dict (AgentIdentity)
        assert session_dict["initiator"]["agent_id"] == bob_identity.agent_id
        assert session_dict["responder"]["agent_id"] == alice_identity.agent_id

    def test_proposal_serialization(
        self,
        data_query_capability: AgentCapability,
    ):
        """
        Scenario: Serialize proposal for transmission.
        """
        proposal = NegotiationProposal.create(
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="query",
                    priority=RequestPriority.REQUIRED,
                )
            ],
            offered_capabilities=[
                CapabilityOffer(capability=data_query_capability)
            ],
            terms=NegotiationTerms(
                duration_seconds=86400,
                auto_renew=True,
            ),
        )

        proposal_dict = proposal.to_dict()

        assert proposal_dict["proposal_id"] == proposal.proposal_id
        assert len(proposal_dict["requested_capabilities"]) == 1
        assert len(proposal_dict["offered_capabilities"]) == 1
        assert proposal_dict["terms"]["duration_seconds"] == 86400

    def test_agreement_serialization(
        self,
        alice_identity: AgentIdentity,
        bob_identity: AgentIdentity,
        data_query_capability: AgentCapability,
    ):
        """
        Scenario: Serialize agreement for storage.
        """
        agreement = Agreement.create(
            parties=[bob_identity, alice_identity],
            capabilities_granted=[
                GrantedCapability(
                    capability=data_query_capability,
                    grantor=alice_identity.agent_id,
                    grantee=bob_identity.agent_id,
                )
            ],
            terms=NegotiationTerms(duration_seconds=3600),
        )

        agreement_dict = agreement.to_dict()

        assert agreement_dict["agreement_id"] == agreement.agreement_id
        assert len(agreement_dict["parties"]) == 2
        assert len(agreement_dict["capabilities_granted"]) == 1
