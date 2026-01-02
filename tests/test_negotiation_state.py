"""
Tests for Negotiation State Machine

Issue #57 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.5)
"""

import pytest
from datetime import datetime, timedelta
from typing import Optional

from src.agent_negotiation import (
    # Enums
    NegotiationStatus,
    NegotiationAction,
    NegotiationOutcome,
    UrgencyLevel,
    RiskLevel,
    StrategyApproach,
    ConstraintType,
    ConstraintOperator,
    TERMINAL_STATES,
    # Proposal types
    NegotiationParameter,
    SLARequirement,
    NegotiationTerms,
    ProposalConstraint,
    CapabilityNegotiationItem,
    NegotiationProposal,
    # Turn types
    TurnMetadata,
    NegotiationTurn,
    # Result types
    NegotiationResult,
    NegotiationContext,
    AgentIdentity,
    # Transition types
    StateTransitionError,
    StateTransitionResult,
    # Risk types
    RiskFactor,
    RiskAssessment,
    # Strategy types
    NegotiationStrategy,
    # State change callback type
    StateChangeCallback,
    # Session class
    NegotiationSession,
    # State machine class
    NegotiationStateMachine,
)


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def initiator() -> AgentIdentity:
    """Create an initiator agent identity."""
    return AgentIdentity(
        agent_id="urn:agent:acme:planner:1.0.0",
        name="Acme Planner",
        version="1.0.0",
        description="A planning agent for task orchestration",
        provider="Acme Corp",
    )


@pytest.fixture
def responder() -> AgentIdentity:
    """Create a responder agent identity."""
    return AgentIdentity(
        agent_id="urn:agent:widgets:executor:2.0.0",
        name="Widget Executor",
        version="2.0.0",
        description="An execution agent for widget operations",
        provider="Widget Inc",
    )


@pytest.fixture
def session(initiator: AgentIdentity, responder: AgentIdentity) -> NegotiationSession:
    """Create a basic negotiation session."""
    return NegotiationSession(
        session_id="test-session-001",
        initiator=initiator,
        responder=responder,
        expires_in_hours=24,
    )


@pytest.fixture
def state_machine(session: NegotiationSession) -> NegotiationStateMachine:
    """Create a state machine for the session."""
    return NegotiationStateMachine(session)


@pytest.fixture
def sample_proposal() -> NegotiationProposal:
    """Create a sample proposal."""
    return NegotiationProposal(
        proposal_id="proposal-001",
        capability_requirements=[
            CapabilityNegotiationItem(
                capability_id="cap-task-exec",
                capability_name="Task Execution",
                required=True,
                requested_level="full",
                parameters=[
                    NegotiationParameter(
                        name="max_concurrent",
                        requested_value="10",
                        min_value="5",
                        max_value="20",
                    )
                ],
            ),
        ],
        terms=NegotiationTerms(
            duration_hours=720,  # 30 days
            rate_limit_per_minute=100,
            priority_level=5,
            billing_model="per_call",
        ),
        valid_until=(datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z",
    )


@pytest.fixture
def counter_proposal() -> NegotiationProposal:
    """Create a counter-proposal."""
    return NegotiationProposal(
        proposal_id="proposal-002",
        capability_requirements=[
            CapabilityNegotiationItem(
                capability_id="cap-task-exec",
                capability_name="Task Execution",
                required=True,
                requested_level="limited",
                parameters=[
                    NegotiationParameter(
                        name="max_concurrent",
                        requested_value="7",
                        min_value="5",
                        max_value="10",
                    )
                ],
            ),
        ],
        terms=NegotiationTerms(
            duration_hours=360,  # 15 days
            rate_limit_per_minute=50,
            priority_level=3,
            billing_model="per_call",
        ),
        valid_until=(datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z",
    )


# ============================================
# Test Enums
# ============================================


class TestNegotiationStatus:
    """Tests for NegotiationStatus enum."""

    def test_all_statuses_defined(self):
        """Verify all expected statuses are defined."""
        expected = {
            "INITIATED",
            "PROPOSAL_SENT",
            "COUNTER_OFFERED",
            "ACCEPTED",
            "REJECTED",
            "EXPIRED",
            "CANCELLED",
            "ADAPTED",
        }
        actual = {s.name for s in NegotiationStatus}
        assert actual == expected

    def test_terminal_states(self):
        """Verify terminal states are correctly defined."""
        assert NegotiationStatus.ACCEPTED in TERMINAL_STATES
        assert NegotiationStatus.REJECTED in TERMINAL_STATES
        assert NegotiationStatus.EXPIRED in TERMINAL_STATES
        assert NegotiationStatus.CANCELLED in TERMINAL_STATES
        assert NegotiationStatus.ADAPTED in TERMINAL_STATES
        assert NegotiationStatus.INITIATED not in TERMINAL_STATES
        assert NegotiationStatus.PROPOSAL_SENT not in TERMINAL_STATES
        assert NegotiationStatus.COUNTER_OFFERED not in TERMINAL_STATES


class TestNegotiationAction:
    """Tests for NegotiationAction enum."""

    def test_all_actions_defined(self):
        """Verify all expected actions are defined."""
        expected = {"PROPOSE", "COUNTER", "ACCEPT", "REJECT", "WITHDRAW", "TIMEOUT"}
        actual = {a.name for a in NegotiationAction}
        assert actual == expected


class TestOtherEnums:
    """Tests for other enums."""

    def test_negotiation_outcome(self):
        """Verify NegotiationOutcome enum."""
        assert NegotiationOutcome.AGREEMENT.value == "agreement"
        assert NegotiationOutcome.NO_AGREEMENT.value == "no_agreement"
        assert NegotiationOutcome.TIMEOUT.value == "timeout"
        assert NegotiationOutcome.CANCELLED.value == "cancelled"
        assert NegotiationOutcome.PARTIAL_AGREEMENT.value == "partial_agreement"

    def test_urgency_level(self):
        """Verify UrgencyLevel enum."""
        levels = [UrgencyLevel.LOW, UrgencyLevel.NORMAL, UrgencyLevel.HIGH, UrgencyLevel.CRITICAL]
        assert len(levels) == 4

    def test_risk_level(self):
        """Verify RiskLevel enum."""
        levels = [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert len(levels) == 4

    def test_strategy_approach(self):
        """Verify StrategyApproach enum."""
        approaches = [
            StrategyApproach.COLLABORATIVE,
            StrategyApproach.COMPETITIVE,
            StrategyApproach.ACCOMMODATING,
            StrategyApproach.AVOIDING,
            StrategyApproach.COMPROMISING,
        ]
        assert len(approaches) == 5


# ============================================
# Test Data Classes
# ============================================


class TestNegotiationParameter:
    """Tests for NegotiationParameter dataclass."""

    def test_basic_creation(self):
        """Test creating a negotiation parameter."""
        param = NegotiationParameter(
            name="timeout",
            requested_value="30",
        )
        assert param.name == "timeout"
        assert param.requested_value == "30"
        assert param.acceptable_alternatives is None
        assert param.min_value is None
        assert param.max_value is None

    def test_full_creation(self):
        """Test creating with all fields."""
        param = NegotiationParameter(
            name="rate_limit",
            requested_value="100",
            acceptable_alternatives=["50", "75", "150"],
            min_value="10",
            max_value="200",
        )
        assert param.acceptable_alternatives == ["50", "75", "150"]
        assert param.min_value == "10"
        assert param.max_value == "200"


class TestNegotiationTerms:
    """Tests for NegotiationTerms dataclass."""

    def test_empty_terms(self):
        """Test creating empty terms."""
        terms = NegotiationTerms()
        assert terms.duration_hours is None
        assert terms.rate_limit_per_minute is None
        assert terms.priority_level is None
        assert terms.billing_model is None
        assert terms.sla_requirements is None

    def test_full_terms(self):
        """Test creating full terms."""
        sla = SLARequirement(
            metric="response_time_ms",
            target_value=100.0,
            measurement_window_hours=24,
        )
        terms = NegotiationTerms(
            duration_hours=720,
            rate_limit_per_minute=100,
            priority_level=5,
            billing_model="per_call",
            sla_requirements=[sla],
        )
        assert terms.duration_hours == 720
        assert terms.sla_requirements[0].metric == "response_time_ms"


class TestProposalConstraint:
    """Tests for ProposalConstraint dataclass."""

    def test_required_constraint(self):
        """Test creating a required constraint."""
        constraint = ProposalConstraint(
            constraint_type=ConstraintType.REQUIRED,
            field="protocol",
            operator=ConstraintOperator.EQUALS,
            value="A2A",
        )
        assert constraint.constraint_type == ConstraintType.REQUIRED
        assert constraint.operator == ConstraintOperator.EQUALS

    def test_prohibited_constraint(self):
        """Test creating a prohibited constraint."""
        constraint = ProposalConstraint(
            constraint_type=ConstraintType.PROHIBITED,
            field="data_region",
            operator=ConstraintOperator.IN,
            value="CN,RU",
        )
        assert constraint.constraint_type == ConstraintType.PROHIBITED


class TestNegotiationProposal:
    """Tests for NegotiationProposal dataclass."""

    def test_basic_proposal(self, sample_proposal: NegotiationProposal):
        """Test basic proposal creation."""
        assert sample_proposal.proposal_id == "proposal-001"
        assert len(sample_proposal.capability_requirements) == 1
        assert sample_proposal.capability_requirements[0].capability_id == "cap-task-exec"
        assert sample_proposal.terms.duration_hours == 720


class TestTurnMetadata:
    """Tests for TurnMetadata dataclass."""

    def test_minimal_metadata(self):
        """Test creating minimal metadata."""
        meta = TurnMetadata(automated=False)
        assert meta.automated is False
        assert meta.response_time_ms is None

    def test_full_metadata(self):
        """Test creating full metadata."""
        meta = TurnMetadata(
            automated=True,
            response_time_ms=150,
            confidence=0.95,
            alternatives_considered=3,
        )
        assert meta.automated is True
        assert meta.response_time_ms == 150
        assert meta.confidence == 0.95


class TestNegotiationTurn:
    """Tests for NegotiationTurn dataclass."""

    def test_basic_turn(self):
        """Test creating a basic turn."""
        turn = NegotiationTurn(
            turn_number=1,
            actor="agent-001",
            action=NegotiationAction.PROPOSE,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
        assert turn.turn_number == 1
        assert turn.action == NegotiationAction.PROPOSE
        assert turn.proposal is None


class TestNegotiationContext:
    """Tests for NegotiationContext dataclass."""

    def test_basic_context(self):
        """Test creating basic context."""
        context = NegotiationContext(
            purpose="Task delegation",
            urgency=UrgencyLevel.NORMAL,
        )
        assert context.purpose == "Task delegation"
        assert context.urgency == UrgencyLevel.NORMAL

    def test_full_context(self):
        """Test creating full context."""
        context = NegotiationContext(
            purpose="Emergency response",
            urgency=UrgencyLevel.CRITICAL,
            previous_session_id="prev-session-001",
            tags=["emergency", "high-priority"],
            custom_data='{"incident_id": "INC-123"}',
        )
        assert context.tags == ["emergency", "high-priority"]


# ============================================
# Test NegotiationSession
# ============================================


class TestNegotiationSession:
    """Tests for NegotiationSession class."""

    def test_session_creation(self, session: NegotiationSession):
        """Test basic session creation."""
        assert session.session_id == "test-session-001"
        assert session.status == NegotiationStatus.INITIATED
        assert session.turn_count == 0
        assert session.is_terminal is False
        assert session.current_proposal is None
        assert session.result is None

    def test_session_with_context(
        self, initiator: AgentIdentity, responder: AgentIdentity
    ):
        """Test session with context."""
        context = NegotiationContext(
            purpose="API access",
            urgency=UrgencyLevel.HIGH,
        )
        session = NegotiationSession(
            session_id="ctx-session-001",
            initiator=initiator,
            responder=responder,
            context=context,
        )
        assert session.context is not None
        assert session.context.purpose == "API access"

    def test_session_expiration(
        self, initiator: AgentIdentity, responder: AgentIdentity
    ):
        """Test session expiration detection."""
        # Create session that expires in -1 hours (already expired)
        session = NegotiationSession(
            session_id="expired-session",
            initiator=initiator,
            responder=responder,
            expires_in_hours=-1,
        )
        assert session.is_expired is True

    def test_session_not_expired(self, session: NegotiationSession):
        """Test session is not expired when valid."""
        assert session.is_expired is False

    def test_session_to_dict(self, session: NegotiationSession):
        """Test session serialization."""
        data = session.to_dict()
        assert data["session_id"] == "test-session-001"
        assert data["status"] == "initiated"
        assert data["is_terminal"] is False
        assert data["turn_count"] == 0
        assert "initiator" in data
        assert data["initiator"]["agent_id"] == "urn:agent:acme:planner:1.0.0"


# ============================================
# Test NegotiationStateMachine
# ============================================


class TestStateMachineCreation:
    """Tests for state machine creation."""

    def test_basic_creation(self, state_machine: NegotiationStateMachine):
        """Test basic state machine creation."""
        assert state_machine.session is not None
        assert state_machine.session.status == NegotiationStatus.INITIATED

    def test_initial_allowed_transitions(self, state_machine: NegotiationStateMachine):
        """Test initial allowed transitions."""
        allowed = state_machine.get_allowed_transitions()
        assert NegotiationStatus.PROPOSAL_SENT in allowed
        assert NegotiationStatus.CANCELLED in allowed
        assert NegotiationStatus.EXPIRED in allowed
        assert len(allowed) == 3


class TestValidTransitions:
    """Tests for valid state transition matrix."""

    def test_valid_transitions_from_initiated(self):
        """Verify valid transitions from INITIATED."""
        valid = NegotiationStateMachine.VALID_TRANSITIONS[NegotiationStatus.INITIATED]
        assert NegotiationStatus.PROPOSAL_SENT in valid
        assert NegotiationStatus.CANCELLED in valid
        assert NegotiationStatus.EXPIRED in valid
        assert len(valid) == 3

    def test_valid_transitions_from_proposal_sent(self):
        """Verify valid transitions from PROPOSAL_SENT."""
        valid = NegotiationStateMachine.VALID_TRANSITIONS[NegotiationStatus.PROPOSAL_SENT]
        assert NegotiationStatus.COUNTER_OFFERED in valid
        assert NegotiationStatus.ACCEPTED in valid
        assert NegotiationStatus.REJECTED in valid
        assert NegotiationStatus.EXPIRED in valid

    def test_valid_transitions_from_counter_offered(self):
        """Verify valid transitions from COUNTER_OFFERED."""
        valid = NegotiationStateMachine.VALID_TRANSITIONS[NegotiationStatus.COUNTER_OFFERED]
        assert NegotiationStatus.COUNTER_OFFERED in valid  # Can counter again
        assert NegotiationStatus.ACCEPTED in valid
        assert NegotiationStatus.REJECTED in valid
        assert NegotiationStatus.EXPIRED in valid
        assert NegotiationStatus.ADAPTED in valid

    def test_terminal_states_have_no_transitions(self):
        """Verify terminal states have no outgoing transitions."""
        for status in TERMINAL_STATES:
            valid = NegotiationStateMachine.VALID_TRANSITIONS[status]
            assert len(valid) == 0


class TestCanTransition:
    """Tests for can_transition method."""

    def test_can_transition_valid(self, state_machine: NegotiationStateMachine):
        """Test can_transition returns True for valid transition."""
        assert state_machine.can_transition(NegotiationStatus.PROPOSAL_SENT) is True
        assert state_machine.can_transition(NegotiationStatus.CANCELLED) is True

    def test_can_transition_invalid(self, state_machine: NegotiationStateMachine):
        """Test can_transition returns False for invalid transition."""
        assert state_machine.can_transition(NegotiationStatus.ACCEPTED) is False
        assert state_machine.can_transition(NegotiationStatus.COUNTER_OFFERED) is False

    def test_can_transition_from_terminal(
        self,
        state_machine: NegotiationStateMachine,
        sample_proposal: NegotiationProposal,
    ):
        """Test cannot transition from terminal state."""
        # First make a proposal
        state_machine.propose(
            actor="agent-001",
            proposal=sample_proposal,
        )
        # Then accept
        state_machine.accept(actor="agent-002")
        # Now in terminal state
        assert state_machine.session.status == NegotiationStatus.ACCEPTED
        assert state_machine.can_transition(NegotiationStatus.REJECTED) is False
        assert state_machine.get_allowed_transitions() == []


class TestPropose:
    """Tests for propose method."""

    def test_propose_success(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test successful proposal."""
        result = state_machine.propose(
            actor=initiator.agent_id,
            proposal=sample_proposal,
            rationale="Initial capability request",
        )
        assert result.success is True
        assert result.previous_status == NegotiationStatus.INITIATED
        assert result.new_status == NegotiationStatus.PROPOSAL_SENT
        assert result.turn_number == 1
        assert state_machine.session.current_proposal == sample_proposal
        assert len(state_machine.session.history) == 1

    def test_propose_without_proposal(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
    ):
        """Test propose fails without proposal."""
        result = state_machine.transition(
            target=NegotiationStatus.PROPOSAL_SENT,
            actor=initiator.agent_id,
            action=NegotiationAction.PROPOSE,
            proposal=None,
        )
        assert result.success is False
        assert result.error is not None
        assert result.error.error_code == "PROPOSAL_REQUIRED"

    def test_propose_from_wrong_state(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test propose fails from wrong state."""
        # First make a proposal
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)
        # Try to propose again (should fail)
        result = state_machine.propose(
            actor=initiator.agent_id,
            proposal=sample_proposal,
        )
        assert result.success is False
        assert result.error.error_code == "INVALID_TRANSITION"


class TestCounter:
    """Tests for counter method."""

    def test_counter_success(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        responder: AgentIdentity,
        sample_proposal: NegotiationProposal,
        counter_proposal: NegotiationProposal,
    ):
        """Test successful counter-proposal."""
        # First make a proposal
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)

        # Then counter
        result = state_machine.counter(
            actor=responder.agent_id,
            proposal=counter_proposal,
            rationale="Adjusting rate limits",
        )
        assert result.success is True
        assert result.new_status == NegotiationStatus.COUNTER_OFFERED
        assert result.turn_number == 2
        assert state_machine.session.current_proposal == counter_proposal

    def test_multiple_counters(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        responder: AgentIdentity,
        sample_proposal: NegotiationProposal,
        counter_proposal: NegotiationProposal,
    ):
        """Test multiple counter-proposals."""
        # Propose -> Counter -> Counter
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)
        state_machine.counter(actor=responder.agent_id, proposal=counter_proposal)

        # Another counter
        another_counter = NegotiationProposal(
            proposal_id="proposal-003",
            capability_requirements=counter_proposal.capability_requirements,
            terms=NegotiationTerms(
                duration_hours=500,
                rate_limit_per_minute=75,
            ),
            valid_until=counter_proposal.valid_until,
        )
        result = state_machine.counter(
            actor=initiator.agent_id,
            proposal=another_counter,
        )
        assert result.success is True
        assert result.turn_number == 3
        assert state_machine.session.status == NegotiationStatus.COUNTER_OFFERED

    def test_counter_from_initiated_fails(
        self,
        state_machine: NegotiationStateMachine,
        responder: AgentIdentity,
        counter_proposal: NegotiationProposal,
    ):
        """Test counter fails from INITIATED state."""
        result = state_machine.counter(
            actor=responder.agent_id,
            proposal=counter_proposal,
        )
        assert result.success is False
        assert result.error.error_code == "INVALID_TRANSITION"


class TestAccept:
    """Tests for accept method."""

    def test_accept_after_proposal(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        responder: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test accepting after proposal."""
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)

        result = state_machine.accept(
            actor=responder.agent_id,
            rationale="Terms are acceptable",
        )
        assert result.success is True
        assert result.new_status == NegotiationStatus.ACCEPTED
        assert state_machine.session.is_terminal is True
        assert state_machine.session.result is not None
        assert state_machine.session.result.outcome == NegotiationOutcome.AGREEMENT

    def test_accept_after_counter(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        responder: AgentIdentity,
        sample_proposal: NegotiationProposal,
        counter_proposal: NegotiationProposal,
    ):
        """Test accepting after counter."""
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)
        state_machine.counter(actor=responder.agent_id, proposal=counter_proposal)

        result = state_machine.accept(actor=initiator.agent_id)
        assert result.success is True
        assert result.new_status == NegotiationStatus.ACCEPTED

    def test_accept_from_initiated_fails(
        self,
        state_machine: NegotiationStateMachine,
        responder: AgentIdentity,
    ):
        """Test accept fails from INITIATED state."""
        result = state_machine.accept(actor=responder.agent_id)
        assert result.success is False


class TestReject:
    """Tests for reject method."""

    def test_reject_after_proposal(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        responder: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test rejecting after proposal."""
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)

        result = state_machine.reject(
            actor=responder.agent_id,
            rationale="Terms are unacceptable",
        )
        assert result.success is True
        assert result.new_status == NegotiationStatus.REJECTED
        assert state_machine.session.is_terminal is True
        assert state_machine.session.result is not None
        assert state_machine.session.result.outcome == NegotiationOutcome.NO_AGREEMENT
        assert state_machine.session.result.rejection_reasons == ["Terms are unacceptable"]

    def test_reject_after_counter(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        responder: AgentIdentity,
        sample_proposal: NegotiationProposal,
        counter_proposal: NegotiationProposal,
    ):
        """Test rejecting after counter."""
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)
        state_machine.counter(actor=responder.agent_id, proposal=counter_proposal)

        result = state_machine.reject(actor=initiator.agent_id)
        assert result.success is True
        assert result.new_status == NegotiationStatus.REJECTED


class TestWithdraw:
    """Tests for withdraw method."""

    def test_withdraw_from_initiated(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
    ):
        """Test withdrawing from INITIATED state."""
        result = state_machine.withdraw(
            actor=initiator.agent_id,
            rationale="Changed requirements",
        )
        assert result.success is True
        assert result.new_status == NegotiationStatus.CANCELLED
        assert state_machine.session.is_terminal is True
        assert state_machine.session.result.outcome == NegotiationOutcome.CANCELLED

    def test_withdraw_from_proposal_sent_fails(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test withdraw fails after proposal sent."""
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)

        result = state_machine.withdraw(actor=initiator.agent_id)
        assert result.success is False
        assert result.error.error_code == "INVALID_WITHDRAW"


class TestExpiration:
    """Tests for session expiration handling."""

    def test_expire_if_needed(
        self, initiator: AgentIdentity, responder: AgentIdentity
    ):
        """Test automatic expiration."""
        session = NegotiationSession(
            session_id="expiring-session",
            initiator=initiator,
            responder=responder,
            expires_in_hours=-1,  # Already expired
        )
        state_machine = NegotiationStateMachine(session)

        result = state_machine.expire_if_needed()
        assert result is not None
        assert result.success is True
        assert result.new_status == NegotiationStatus.EXPIRED
        assert session.result.outcome == NegotiationOutcome.TIMEOUT

    def test_no_expire_if_valid(self, state_machine: NegotiationStateMachine):
        """Test no expiration if session is valid."""
        result = state_machine.expire_if_needed()
        assert result is None

    def test_cannot_transition_if_expired(
        self,
        initiator: AgentIdentity,
        responder: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test cannot make normal transition if expired."""
        session = NegotiationSession(
            session_id="expired-session",
            initiator=initiator,
            responder=responder,
            expires_in_hours=-1,
        )
        state_machine = NegotiationStateMachine(session)

        result = state_machine.propose(
            actor=initiator.agent_id,
            proposal=sample_proposal,
        )
        assert result.success is False
        assert result.error.error_code == "SESSION_EXPIRED"


class TestCallbacks:
    """Tests for state change callbacks."""

    def test_callback_on_transition(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test callback is called on state transition."""
        callback_data = []

        def callback(
            old: NegotiationStatus,
            new: NegotiationStatus,
            turn: Optional[NegotiationTurn],
        ):
            callback_data.append((old, new, turn))

        state_machine.register_callback(callback)
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)

        assert len(callback_data) == 1
        assert callback_data[0][0] == NegotiationStatus.INITIATED
        assert callback_data[0][1] == NegotiationStatus.PROPOSAL_SENT
        assert callback_data[0][2].turn_number == 1

    def test_multiple_callbacks(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test multiple callbacks are called."""
        call_count = [0, 0]

        def callback1(old, new, turn):
            call_count[0] += 1

        def callback2(old, new, turn):
            call_count[1] += 1

        state_machine.register_callback(callback1)
        state_machine.register_callback(callback2)
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)

        assert call_count[0] == 1
        assert call_count[1] == 1

    def test_unregister_callback(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test unregistering a callback."""
        call_count = [0]

        def callback(old, new, turn):
            call_count[0] += 1

        state_machine.register_callback(callback)
        state_machine.unregister_callback(callback)
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)

        assert call_count[0] == 0

    def test_callback_error_handled(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test callback errors don't break state machine."""

        def bad_callback(old, new, turn):
            raise ValueError("Callback error")

        state_machine.register_callback(bad_callback)

        # Should not raise
        result = state_machine.propose(
            actor=initiator.agent_id,
            proposal=sample_proposal,
        )
        assert result.success is True


class TestSessionSummary:
    """Tests for get_session_summary method."""

    def test_initial_summary(self, state_machine: NegotiationStateMachine):
        """Test summary for initial state."""
        summary = state_machine.get_session_summary()
        assert summary["session_id"] == "test-session-001"
        assert summary["status"] == "initiated"
        assert summary["turn_count"] == 0
        assert summary["is_terminal"] is False
        assert summary["current_proposal_id"] is None
        assert summary["last_actor"] is None

    def test_summary_after_proposal(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test summary after proposal."""
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)

        summary = state_machine.get_session_summary()
        assert summary["status"] == "proposal_sent"
        assert summary["turn_count"] == 1
        assert summary["current_proposal_id"] == "proposal-001"
        assert summary["last_actor"] == initiator.agent_id
        assert summary["last_action"] == "propose"

    def test_summary_after_acceptance(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        responder: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test summary after acceptance."""
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)
        state_machine.accept(actor=responder.agent_id)

        summary = state_machine.get_session_summary()
        assert summary["status"] == "accepted"
        assert summary["is_terminal"] is True
        assert summary["allowed_transitions"] == []


class TestActionStatusMapping:
    """Tests for action to status mapping."""

    def test_action_status_mismatch(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test action-status mismatch is rejected."""
        result = state_machine.transition(
            target=NegotiationStatus.CANCELLED,  # Wrong target for PROPOSE action
            actor=initiator.agent_id,
            action=NegotiationAction.PROPOSE,
            proposal=sample_proposal,
        )
        assert result.success is False
        assert result.error.error_code == "ACTION_STATUS_MISMATCH"


class TestComplexScenarios:
    """Tests for complex negotiation scenarios."""

    def test_full_negotiation_flow(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        responder: AgentIdentity,
        sample_proposal: NegotiationProposal,
        counter_proposal: NegotiationProposal,
    ):
        """Test complete negotiation flow: propose -> counter -> counter -> accept."""
        # Initiator proposes
        r1 = state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)
        assert r1.success is True

        # Responder counters
        r2 = state_machine.counter(actor=responder.agent_id, proposal=counter_proposal)
        assert r2.success is True

        # Initiator counters again
        final_proposal = NegotiationProposal(
            proposal_id="proposal-final",
            capability_requirements=counter_proposal.capability_requirements,
            terms=NegotiationTerms(
                duration_hours=540,  # Compromise
                rate_limit_per_minute=75,  # Compromise
            ),
            valid_until=sample_proposal.valid_until,
        )
        r3 = state_machine.counter(actor=initiator.agent_id, proposal=final_proposal)
        assert r3.success is True

        # Responder accepts
        r4 = state_machine.accept(actor=responder.agent_id, rationale="Agreed on terms")
        assert r4.success is True

        # Verify final state
        assert state_machine.session.status == NegotiationStatus.ACCEPTED
        assert state_machine.session.turn_count == 4
        assert state_machine.session.result.outcome == NegotiationOutcome.AGREEMENT

    def test_negotiation_rejection_flow(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        responder: AgentIdentity,
        sample_proposal: NegotiationProposal,
        counter_proposal: NegotiationProposal,
    ):
        """Test negotiation ending in rejection."""
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)
        state_machine.counter(actor=responder.agent_id, proposal=counter_proposal)

        result = state_machine.reject(
            actor=initiator.agent_id,
            rationale="Cannot meet counter-proposal terms",
        )
        assert result.success is True
        assert state_machine.session.result.outcome == NegotiationOutcome.NO_AGREEMENT

    def test_early_withdrawal(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
    ):
        """Test early withdrawal before any proposal."""
        result = state_machine.withdraw(
            actor=initiator.agent_id,
            rationale="Requirements changed",
        )
        assert result.success is True
        assert state_machine.session.status == NegotiationStatus.CANCELLED
        assert state_machine.session.turn_count == 1


class TestHistoryTracking:
    """Tests for negotiation history tracking."""

    def test_history_records_all_turns(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        responder: AgentIdentity,
        sample_proposal: NegotiationProposal,
        counter_proposal: NegotiationProposal,
    ):
        """Test that history records all turns."""
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)
        state_machine.counter(actor=responder.agent_id, proposal=counter_proposal)
        state_machine.accept(actor=initiator.agent_id)

        history = state_machine.session.history
        assert len(history) == 3

        assert history[0].turn_number == 1
        assert history[0].action == NegotiationAction.PROPOSE
        assert history[0].actor == initiator.agent_id

        assert history[1].turn_number == 2
        assert history[1].action == NegotiationAction.COUNTER
        assert history[1].actor == responder.agent_id

        assert history[2].turn_number == 3
        assert history[2].action == NegotiationAction.ACCEPT
        assert history[2].actor == initiator.agent_id

    def test_history_includes_timestamps(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test that history includes timestamps."""
        state_machine.propose(actor=initiator.agent_id, proposal=sample_proposal)

        turn = state_machine.session.history[0]
        assert turn.timestamp is not None
        assert "T" in turn.timestamp  # ISO format
        assert turn.timestamp.endswith("Z")

    def test_history_includes_metadata(
        self,
        state_machine: NegotiationStateMachine,
        initiator: AgentIdentity,
        sample_proposal: NegotiationProposal,
    ):
        """Test that history can include metadata."""
        metadata = TurnMetadata(
            automated=False,
            response_time_ms=150,
            confidence=0.9,
        )
        state_machine.transition(
            target=NegotiationStatus.PROPOSAL_SENT,
            actor=initiator.agent_id,
            action=NegotiationAction.PROPOSE,
            proposal=sample_proposal,
            metadata=metadata,
        )

        turn = state_machine.session.history[0]
        assert turn.metadata is not None
        assert turn.metadata.response_time_ms == 150
        assert turn.metadata.confidence == 0.9


class TestRiskAndStrategy:
    """Tests for risk and strategy data types."""

    def test_risk_factor_creation(self):
        """Test creating a risk factor."""
        factor = RiskFactor(
            category="security",
            description="Untrusted agent",
            severity=RiskLevel.HIGH,
            likelihood=0.7,
        )
        assert factor.category == "security"
        assert factor.severity == RiskLevel.HIGH

    def test_risk_assessment_creation(self):
        """Test creating a risk assessment."""
        assessment = RiskAssessment(
            overall_risk=RiskLevel.MODERATE,
            factors=[
                RiskFactor(
                    category="compliance",
                    description="Missing SOC2",
                    severity=RiskLevel.MODERATE,
                    likelihood=0.5,
                )
            ],
            mitigations=["Request compliance documentation"],
        )
        assert assessment.overall_risk == RiskLevel.MODERATE
        assert len(assessment.factors) == 1

    def test_negotiation_strategy_creation(self):
        """Test creating a negotiation strategy."""
        strategy = NegotiationStrategy(
            approach=StrategyApproach.COLLABORATIVE,
            priority_capabilities=["task-exec", "data-access"],
            max_concession_percentage=0.3,
            must_have_terms=["rate_limit >= 50"],
            nice_to_have_terms=["priority_level >= 5"],
            time_sensitivity=0.5,
        )
        assert strategy.approach == StrategyApproach.COLLABORATIVE
        assert len(strategy.priority_capabilities) == 2
        assert strategy.max_concession_percentage == 0.3


class TestAgentIdentity:
    """Tests for AgentIdentity dataclass."""

    def test_minimal_identity(self):
        """Test creating minimal identity."""
        identity = AgentIdentity(
            agent_id="urn:agent:test:agent:1.0.0",
            name="Test Agent",
            version="1.0.0",
            description="A test agent",
        )
        assert identity.agent_id == "urn:agent:test:agent:1.0.0"
        assert identity.provider is None
        assert identity.trust_domain is None

    def test_full_identity(self):
        """Test creating full identity."""
        identity = AgentIdentity(
            agent_id="urn:agent:acme:planner:2.0.0",
            name="Acme Planner Pro",
            version="2.0.0",
            description="Advanced planning agent",
            provider="Acme Corp",
            trust_domain="spiffe://acme.com/agents",
        )
        assert identity.provider == "Acme Corp"
        assert identity.trust_domain == "spiffe://acme.com/agents"


class TestIntegration:
    """Integration tests for the complete negotiation workflow."""

    def test_end_to_end_agreement(self):
        """Test complete end-to-end negotiation reaching agreement."""
        # Setup agents
        initiator = AgentIdentity(
            agent_id="urn:agent:org1:task-manager:1.0.0",
            name="Task Manager",
            version="1.0.0",
            description="Manages complex tasks",
        )
        responder = AgentIdentity(
            agent_id="urn:agent:org2:data-processor:1.0.0",
            name="Data Processor",
            version="1.0.0",
            description="Processes large datasets",
        )

        # Create session with context
        context = NegotiationContext(
            purpose="Data processing delegation",
            urgency=UrgencyLevel.HIGH,
            tags=["data", "batch-processing"],
        )
        session = NegotiationSession(
            session_id="e2e-test-001",
            initiator=initiator,
            responder=responder,
            expires_in_hours=48,
            context=context,
        )
        sm = NegotiationStateMachine(session)

        # Track state changes
        transitions = []
        sm.register_callback(lambda o, n, t: transitions.append((o.value, n.value)))

        # Initial proposal
        proposal = NegotiationProposal(
            proposal_id="p-001",
            capability_requirements=[
                CapabilityNegotiationItem(
                    capability_id="data-process",
                    capability_name="Data Processing",
                    required=True,
                    parameters=[
                        NegotiationParameter(
                            name="batch_size",
                            requested_value="10000",
                            min_value="1000",
                        )
                    ],
                )
            ],
            terms=NegotiationTerms(
                duration_hours=168,
                rate_limit_per_minute=200,
                billing_model="per_call",
            ),
            valid_until=(datetime.utcnow() + timedelta(hours=24)).isoformat() + "Z",
        )
        sm.propose(actor=initiator.agent_id, proposal=proposal)

        # Counter-proposal
        counter = NegotiationProposal(
            proposal_id="p-002",
            capability_requirements=proposal.capability_requirements,
            terms=NegotiationTerms(
                duration_hours=168,
                rate_limit_per_minute=100,  # Lower rate limit
                billing_model="per_call",
            ),
            valid_until=proposal.valid_until,
        )
        sm.counter(actor=responder.agent_id, proposal=counter)

        # Accept counter
        sm.accept(actor=initiator.agent_id, rationale="Rate limit acceptable")

        # Verify final state
        assert session.status == NegotiationStatus.ACCEPTED
        assert session.turn_count == 3
        assert session.result.outcome == NegotiationOutcome.AGREEMENT
        assert len(transitions) == 3
        assert transitions == [
            ("initiated", "proposal_sent"),
            ("proposal_sent", "counter_offered"),
            ("counter_offered", "accepted"),
        ]

        # Verify serialization
        data = session.to_dict()
        assert data["status"] == "accepted"
        assert data["turn_count"] == 3
        assert data["is_terminal"] is True
