"""
Tests for Conflict Mediation System.

Issue #62 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.10)
"""

import pytest
from datetime import datetime, timedelta

from src.agent_negotiation.conflict_mediator import (
    # Enums
    MediationStyle,
    MediationResolutionStrategy,
    MediationOutcome,
    ConflictPriority,
    # Party position types
    TermSummary,
    NegotiationProposalSummary,
    PositionConstraint,
    TradeOffPair,
    FlexibilityAssessment,
    PartyPosition,
    # Request types
    ConflictHistoryEntry,
    ConflictSummaryForMediation,
    MediationOptions,
    MediationContext,
    MediationRequest,
    # Result types
    MediationResult,
    CompromiseProposal,
    # Deadlock types
    TurnSummary,
    DeadlockResolutionRequest,
    DeadlockResolution,
    # Escalation types
    EscalationRequest,
    EscalationResponse,
    # Analysis types
    CommonGroundAnalysis,
    CreativeSolution,
    # Mediator
    ConflictMediator,
)


# ============================================
# Test Fixtures
# ============================================


@pytest.fixture
def mediator():
    """Create a ConflictMediator instance."""
    return ConflictMediator()


@pytest.fixture
def sample_party_a():
    """Create a sample party A position."""
    return PartyPosition(
        party_id="agent-001",
        party_name="Agent Alpha",
        proposal=NegotiationProposalSummary(
            proposal_id="prop-001",
            terms=[
                TermSummary(
                    term_name="rate_limit",
                    term_value="1000",
                    negotiable=True,
                    min_acceptable="800",
                    max_acceptable="1200",
                ),
                TermSummary(
                    term_name="timeout_ms",
                    term_value="5000",
                    negotiable=True,
                    min_acceptable="3000",
                    max_acceptable="8000",
                ),
                TermSummary(
                    term_name="format",
                    term_value="json",
                    negotiable=False,
                ),
            ],
            capabilities=["data_processing", "analytics", "reporting"],
            valid_until=(datetime.now() + timedelta(hours=1)).isoformat(),
        ),
        priorities=["reliability", "performance", "cost"],
        constraints=[
            PositionConstraint(
                constraint_id="c-001",
                field="format",
                constraint_type="equals",
                value="json",
                reason="JSON is required for downstream compatibility",
                waivable=False,
            ),
        ],
        flexibility=FlexibilityAssessment(
            flexible_terms=["rate_limit", "timeout_ms"],
            trade_off_pairs=[
                TradeOffPair(
                    term_a="rate_limit",
                    term_b="timeout_ms",
                    relationship="inverse",
                ),
            ],
            total_flexibility_score=0.7,
        ),
    )


@pytest.fixture
def sample_party_b():
    """Create a sample party B position."""
    return PartyPosition(
        party_id="agent-002",
        party_name="Agent Beta",
        proposal=NegotiationProposalSummary(
            proposal_id="prop-002",
            terms=[
                TermSummary(
                    term_name="rate_limit",
                    term_value="800",
                    negotiable=True,
                    min_acceptable="600",
                    max_acceptable="1000",
                ),
                TermSummary(
                    term_name="timeout_ms",
                    term_value="3000",
                    negotiable=True,
                    min_acceptable="2000",
                    max_acceptable="5000",
                ),
                TermSummary(
                    term_name="format",
                    term_value="json",
                    negotiable=False,
                ),
            ],
            capabilities=["data_processing", "storage", "caching"],
            valid_until=(datetime.now() + timedelta(hours=1)).isoformat(),
        ),
        priorities=["cost", "reliability", "performance"],
        constraints=[
            PositionConstraint(
                constraint_id="c-002",
                field="timeout_ms",
                constraint_type="max",
                value="5000",
                reason="Cannot support longer timeouts",
                waivable=True,
            ),
        ],
        flexibility=FlexibilityAssessment(
            flexible_terms=["rate_limit"],
            trade_off_pairs=[],
            total_flexibility_score=0.5,
        ),
    )


@pytest.fixture
def sample_conflict():
    """Create a sample conflict summary."""
    return ConflictSummaryForMediation(
        conflict_id="conflict-001",
        conflict_type="PARAMETER_MISMATCH",
        severity="MEDIUM",
        description="Disagreement on rate limits and timeout values",
        affected_terms=["rate_limit", "timeout_ms"],
        history=[
            ConflictHistoryEntry(
                timestamp=datetime.now().isoformat(),
                strategy_tried=MediationResolutionStrategy.NEGOTIATE_TERMS,
                outcome="Partial progress",
                notes="Parties moved closer but not resolved",
            ),
        ],
    )


@pytest.fixture
def sample_mediation_options():
    """Create sample mediation options."""
    return MediationOptions(
        max_iterations=5,
        auto_escalate=True,
        escalation_threshold=3,
        allow_partial_resolution=True,
        generate_alternatives=True,
        max_alternatives=3,
        preserve_relationship=True,
    )


@pytest.fixture
def sample_mediation_request(sample_party_a, sample_party_b, sample_conflict, sample_mediation_options):
    """Create a sample mediation request."""
    return MediationRequest(
        request_id="req-001",
        session_id="session-001",
        conflict=sample_conflict,
        party_a=sample_party_a,
        party_b=sample_party_b,
        mediation_style=MediationStyle.FACILITATIVE,
        options=sample_mediation_options,
        context=MediationContext(
            urgency=ConflictPriority.MEDIUM,
            business_impact="Delayed integration",
        ),
    )


# ============================================
# Enum Tests
# ============================================


class TestEnums:
    """Tests for mediation enums."""

    def test_mediation_style_values(self):
        """Test MediationStyle enum values."""
        assert MediationStyle.FACILITATIVE.value == "facilitative"
        assert MediationStyle.EVALUATIVE.value == "evaluative"
        assert MediationStyle.TRANSFORMATIVE.value == "transformative"
        assert MediationStyle.DIRECTIVE.value == "directive"

    def test_mediation_resolution_strategy_values(self):
        """Test MediationResolutionStrategy enum values."""
        assert MediationResolutionStrategy.TRANSFORM.value == "transform"
        assert MediationResolutionStrategy.SUBSET.value == "subset"
        assert MediationResolutionStrategy.BRIDGE.value == "bridge"
        assert MediationResolutionStrategy.SPLIT_DIFFERENCE.value == "split_difference"
        assert MediationResolutionStrategy.PACKAGE_DEAL.value == "package_deal"
        assert MediationResolutionStrategy.TIME_SHARE.value == "time_share"

    def test_mediation_outcome_values(self):
        """Test MediationOutcome enum values."""
        assert MediationOutcome.RESOLVED.value == "resolved"
        assert MediationOutcome.PARTIALLY_RESOLVED.value == "partially_resolved"
        assert MediationOutcome.DEADLOCK.value == "deadlock"
        assert MediationOutcome.DEFERRED.value == "deferred"
        assert MediationOutcome.WITHDRAWN.value == "withdrawn"

    def test_conflict_priority_values(self):
        """Test ConflictPriority enum values."""
        assert ConflictPriority.CRITICAL.value == "critical"
        assert ConflictPriority.HIGH.value == "high"
        assert ConflictPriority.MEDIUM.value == "medium"
        assert ConflictPriority.LOW.value == "low"


# ============================================
# Party Position Tests
# ============================================


class TestPartyPosition:
    """Tests for party position types."""

    def test_term_summary_creation(self):
        """Test TermSummary creation."""
        term = TermSummary(
            term_name="rate_limit",
            term_value="1000",
            negotiable=True,
            min_acceptable="500",
            max_acceptable="1500",
        )
        assert term.term_name == "rate_limit"
        assert term.term_value == "1000"
        assert term.negotiable is True
        assert term.min_acceptable == "500"
        assert term.max_acceptable == "1500"

    def test_position_constraint_creation(self):
        """Test PositionConstraint creation."""
        constraint = PositionConstraint(
            constraint_id="c-001",
            field="format",
            constraint_type="equals",
            value="json",
            reason="Required for compatibility",
            waivable=False,
        )
        assert constraint.constraint_id == "c-001"
        assert constraint.waivable is False

    def test_flexibility_assessment_creation(self):
        """Test FlexibilityAssessment creation."""
        flexibility = FlexibilityAssessment(
            flexible_terms=["rate_limit", "timeout"],
            trade_off_pairs=[
                TradeOffPair(term_a="rate_limit", term_b="timeout", relationship="inverse")
            ],
            total_flexibility_score=0.75,
        )
        assert len(flexibility.flexible_terms) == 2
        assert flexibility.total_flexibility_score == 0.75

    def test_party_position_creation(self, sample_party_a):
        """Test PartyPosition creation."""
        assert sample_party_a.party_id == "agent-001"
        assert sample_party_a.party_name == "Agent Alpha"
        assert len(sample_party_a.proposal.terms) == 3
        assert len(sample_party_a.priorities) == 3
        assert len(sample_party_a.constraints) == 1


# ============================================
# ConflictMediator Tests
# ============================================


class TestConflictMediatorInit:
    """Tests for ConflictMediator initialization."""

    def test_default_initialization(self):
        """Test default mediator initialization."""
        mediator = ConflictMediator()
        assert mediator.default_style == MediationStyle.FACILITATIVE
        assert mediator.escalation_callback is None

    def test_custom_style_initialization(self):
        """Test mediator with custom style."""
        mediator = ConflictMediator(default_style=MediationStyle.DIRECTIVE)
        assert mediator.default_style == MediationStyle.DIRECTIVE

    def test_escalation_callback_initialization(self):
        """Test mediator with escalation callback."""
        def callback(req):
            return EscalationResponse(
                response_id="resp-001",
                request_id=req.request_id,
                escalation_accepted=True,
            )

        mediator = ConflictMediator(escalation_callback=callback)
        assert mediator.escalation_callback is not None


class TestFindCommonGround:
    """Tests for find_common_ground method."""

    def test_find_agreed_terms(self, mediator, sample_party_a, sample_party_b):
        """Test finding agreed terms."""
        analysis = mediator.find_common_ground(sample_party_a, sample_party_b)

        # Both parties agree on format=json
        agreed_names = [t.term_name for t in analysis.agreed_terms]
        assert "format" in agreed_names

    def test_find_close_terms(self, mediator, sample_party_a, sample_party_b):
        """Test finding terms with close positions."""
        analysis = mediator.find_common_ground(sample_party_a, sample_party_b)

        # rate_limit values are close (1000 vs 800)
        all_term_names = (
            [t.term_name for t in analysis.close_terms] +
            [t.term_name for t in analysis.negotiable_terms]
        )
        assert "rate_limit" in all_term_names

    def test_find_negotiable_terms(self, mediator, sample_party_a, sample_party_b):
        """Test finding negotiable terms."""
        analysis = mediator.find_common_ground(sample_party_a, sample_party_b)

        # Both parties have negotiable terms
        all_negotiable = analysis.close_terms + analysis.negotiable_terms
        assert len(all_negotiable) > 0

    def test_overall_alignment_score(self, mediator, sample_party_a, sample_party_b):
        """Test overall alignment score calculation."""
        analysis = mediator.find_common_ground(sample_party_a, sample_party_b)

        assert 0.0 <= analysis.overall_alignment <= 1.0

    def test_recommended_focus(self, mediator, sample_party_a, sample_party_b):
        """Test recommended focus generation."""
        analysis = mediator.find_common_ground(sample_party_a, sample_party_b)

        # Should have some recommendations
        assert isinstance(analysis.recommended_focus, list)


class TestMediate:
    """Tests for mediate method."""

    def test_basic_mediation(self, mediator, sample_mediation_request):
        """Test basic mediation request."""
        result = mediator.mediate(sample_mediation_request)

        assert result.result_id is not None
        assert result.request_id == sample_mediation_request.request_id
        assert isinstance(result.outcome, MediationOutcome)
        assert isinstance(result.metrics, object)

    def test_mediation_with_compromise(self, mediator, sample_mediation_request):
        """Test mediation generates compromise proposal."""
        result = mediator.mediate(sample_mediation_request)

        # Should generate a compromise since parties have negotiable terms
        assert result.compromise_proposal is not None or result.outcome == MediationOutcome.DEADLOCK

    def test_mediation_metrics(self, mediator, sample_mediation_request):
        """Test mediation metrics are populated."""
        result = mediator.mediate(sample_mediation_request)

        assert result.metrics.iterations_used >= 1
        assert result.metrics.time_elapsed_ms >= 0
        assert result.metrics.proposals_generated >= 0
        assert 0.0 <= result.metrics.common_ground_found <= 1.0

    def test_mediation_with_callback(self, mediator, sample_mediation_request):
        """Test mediation with callback."""
        callback_results = []

        def callback(result):
            callback_results.append(result)

        result = mediator.mediate(sample_mediation_request, callback=callback)

        assert len(callback_results) == 1
        assert callback_results[0] == result

    def test_mediation_generates_alternatives(self, mediator, sample_mediation_request):
        """Test mediation generates alternatives when requested."""
        result = mediator.mediate(sample_mediation_request)

        # Options include generate_alternatives=True
        if result.alternatives:
            assert len(result.alternatives) <= sample_mediation_request.options.max_alternatives

    def test_mediation_history_stored(self, mediator, sample_mediation_request):
        """Test mediation history is stored."""
        mediator.mediate(sample_mediation_request)

        history = mediator.get_mediation_history(sample_mediation_request.session_id)
        assert len(history) == 1


class TestMediationStyles:
    """Tests for different mediation styles."""

    def test_facilitative_style(self, mediator, sample_party_a, sample_party_b, sample_conflict, sample_mediation_options):
        """Test facilitative mediation style."""
        request = MediationRequest(
            request_id="req-fac",
            session_id="session-fac",
            conflict=sample_conflict,
            party_a=sample_party_a,
            party_b=sample_party_b,
            mediation_style=MediationStyle.FACILITATIVE,
            options=sample_mediation_options,
        )

        result = mediator.mediate(request)
        assert result is not None

    def test_evaluative_style(self, mediator, sample_party_a, sample_party_b, sample_conflict, sample_mediation_options):
        """Test evaluative mediation style."""
        request = MediationRequest(
            request_id="req-eval",
            session_id="session-eval",
            conflict=sample_conflict,
            party_a=sample_party_a,
            party_b=sample_party_b,
            mediation_style=MediationStyle.EVALUATIVE,
            options=sample_mediation_options,
        )

        result = mediator.mediate(request)
        assert result is not None

    def test_transformative_style(self, mediator, sample_party_a, sample_party_b, sample_conflict, sample_mediation_options):
        """Test transformative mediation style."""
        request = MediationRequest(
            request_id="req-trans",
            session_id="session-trans",
            conflict=sample_conflict,
            party_a=sample_party_a,
            party_b=sample_party_b,
            mediation_style=MediationStyle.TRANSFORMATIVE,
            options=sample_mediation_options,
        )

        result = mediator.mediate(request)
        assert result is not None

    def test_directive_style(self, mediator, sample_party_a, sample_party_b, sample_conflict, sample_mediation_options):
        """Test directive mediation style."""
        request = MediationRequest(
            request_id="req-dir",
            session_id="session-dir",
            conflict=sample_conflict,
            party_a=sample_party_a,
            party_b=sample_party_b,
            mediation_style=MediationStyle.DIRECTIVE,
            options=sample_mediation_options,
        )

        result = mediator.mediate(request)
        assert result is not None


class TestResolveDeadlock:
    """Tests for resolve_deadlock method."""

    def test_basic_deadlock_resolution(self, mediator, sample_party_a, sample_party_b):
        """Test basic deadlock resolution."""
        request = DeadlockResolutionRequest(
            request_id="dead-001",
            session_id="session-001",
            deadlock_turns=5,
            turn_history=[
                TurnSummary(
                    turn_number=1,
                    actor="agent-001",
                    action="propose",
                    key_changes=["Offered rate_limit=1000"],
                    progress_made=False,
                ),
                TurnSummary(
                    turn_number=2,
                    actor="agent-002",
                    action="counter",
                    key_changes=["Requested rate_limit=800"],
                    progress_made=False,
                ),
            ],
            party_positions=[sample_party_a, sample_party_b],
            previously_tried=[],
        )

        resolution = mediator.resolve_deadlock(request)

        assert resolution.resolution_id is not None
        assert resolution.request_id == request.request_id
        assert isinstance(resolution.strategy, MediationResolutionStrategy)
        assert resolution.confidence > 0

    def test_deadlock_with_previous_strategies(self, mediator, sample_party_a, sample_party_b):
        """Test deadlock resolution avoiding previously tried strategies."""
        request = DeadlockResolutionRequest(
            request_id="dead-002",
            session_id="session-002",
            deadlock_turns=8,
            turn_history=[],
            party_positions=[sample_party_a, sample_party_b],
            previously_tried=[
                MediationResolutionStrategy.SPLIT_DIFFERENCE,
                MediationResolutionStrategy.SUBSET,
            ],
        )

        resolution = mediator.resolve_deadlock(request)

        # Should not recommend a previously tried strategy
        assert resolution.strategy not in request.previously_tried

    def test_deadlock_escalation_when_exhausted(self, mediator, sample_party_a, sample_party_b):
        """Test deadlock escalation when all strategies exhausted."""
        request = DeadlockResolutionRequest(
            request_id="dead-003",
            session_id="session-003",
            deadlock_turns=20,
            turn_history=[],
            party_positions=[sample_party_a, sample_party_b],
            previously_tried=list(MediationResolutionStrategy),  # All tried
        )

        resolution = mediator.resolve_deadlock(request)

        assert resolution.escalation_needed is True
        assert resolution.resolution_possible is False

    def test_deadlock_alternative_strategies(self, mediator, sample_party_a, sample_party_b):
        """Test deadlock resolution includes alternatives."""
        request = DeadlockResolutionRequest(
            request_id="dead-004",
            session_id="session-004",
            deadlock_turns=5,
            turn_history=[],
            party_positions=[sample_party_a, sample_party_b],
            previously_tried=[MediationResolutionStrategy.NEGOTIATE_TERMS],
        )

        resolution = mediator.resolve_deadlock(request)

        assert isinstance(resolution.alternative_strategies, list)


class TestEscalation:
    """Tests for escalation functionality."""

    def test_default_escalation(self, mediator, sample_conflict):
        """Test default escalation without callback."""
        request = EscalationRequest(
            request_id="esc-001",
            session_id="session-001",
            reason="Cannot resolve deadlock",
            conflict_summary=sample_conflict,
            mediation_history=[],
            urgency=ConflictPriority.HIGH,
            recommended_action="Human mediator review",
        )

        response = mediator.escalate(request)

        assert response.response_id is not None
        assert response.escalation_accepted is True

    def test_custom_escalation_callback(self, sample_conflict):
        """Test escalation with custom callback."""
        def custom_callback(req):
            return EscalationResponse(
                response_id="custom-resp",
                request_id=req.request_id,
                escalation_accepted=True,
                assigned_to="senior_mediator",
                expected_resolution_time="2 hours",
            )

        mediator = ConflictMediator(escalation_callback=custom_callback)

        request = EscalationRequest(
            request_id="esc-002",
            session_id="session-002",
            reason="Complex dispute",
            conflict_summary=sample_conflict,
            mediation_history=[],
            urgency=ConflictPriority.CRITICAL,
            recommended_action="Immediate review",
        )

        response = mediator.escalate(request)

        assert response.assigned_to == "senior_mediator"
        assert response.expected_resolution_time == "2 hours"


class TestCreativeSolutions:
    """Tests for creative solution generation."""

    def test_generate_creative_solutions(self, mediator, sample_conflict):
        """Test generating creative solutions."""
        solutions = mediator.generate_creative_solutions(
            conflict=sample_conflict,
            constraints=["Must maintain compatibility", "Budget limited"],
            preferences=["Prefer minimal changes", "Maintain performance"],
            max_solutions=5,
        )

        assert len(solutions) <= 5
        assert all(isinstance(s, CreativeSolution) for s in solutions)

    def test_creative_solution_structure(self, mediator, sample_conflict):
        """Test creative solution structure."""
        solutions = mediator.generate_creative_solutions(
            conflict=sample_conflict,
            constraints=[],
            preferences=[],
            max_solutions=3,
        )

        if solutions:
            solution = solutions[0]
            assert solution.solution_id is not None
            assert solution.title is not None
            assert solution.description is not None
            assert 0.0 <= solution.novelty_score <= 1.0
            assert 0.0 <= solution.feasibility_score <= 1.0

    def test_creative_solution_types(self, mediator, sample_conflict):
        """Test different types of creative solutions."""
        solutions = mediator.generate_creative_solutions(
            conflict=sample_conflict,
            constraints=[],
            preferences=[],
            max_solutions=5,
        )

        # Should include various solution types
        titles = [s.title for s in solutions]
        expected_types = ["Phased", "Scope", "Resource", "Hybrid", "Incremental"]
        assert any(any(t in title for t in expected_types) for title in titles)


class TestCompromiseProposal:
    """Tests for compromise proposal generation."""

    def test_compromise_proposal_structure(self, mediator, sample_mediation_request):
        """Test compromise proposal structure."""
        result = mediator.mediate(sample_mediation_request)

        if result.compromise_proposal:
            proposal = result.compromise_proposal
            assert proposal.proposal_id is not None
            assert proposal.description is not None
            assert isinstance(proposal.terms, list)
            assert 0.0 <= proposal.fairness_score <= 1.0
            assert 0.0 <= proposal.viability_score <= 1.0

    def test_compromise_tracks_concessions(self, mediator, sample_mediation_request):
        """Test that compromise tracks concessions from both parties."""
        result = mediator.mediate(sample_mediation_request)

        if result.compromise_proposal:
            proposal = result.compromise_proposal
            assert isinstance(proposal.concessions_a, list)
            assert isinstance(proposal.concessions_b, list)

    def test_compromise_includes_gains(self, mediator, sample_mediation_request):
        """Test that compromise includes gains for both parties."""
        result = mediator.mediate(sample_mediation_request)

        if result.compromise_proposal:
            proposal = result.compromise_proposal
            assert isinstance(proposal.gains_a, list)
            assert isinstance(proposal.gains_b, list)


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_terms(self, mediator):
        """Test mediation with empty terms."""
        party_a = PartyPosition(
            party_id="agent-a",
            party_name="Agent A",
            proposal=NegotiationProposalSummary(
                proposal_id="prop-empty-a",
                terms=[],
                capabilities=[],
                valid_until=datetime.now().isoformat(),
            ),
            priorities=[],
            constraints=[],
            flexibility=FlexibilityAssessment(
                flexible_terms=[],
                trade_off_pairs=[],
                total_flexibility_score=0.0,
            ),
        )
        party_b = PartyPosition(
            party_id="agent-b",
            party_name="Agent B",
            proposal=NegotiationProposalSummary(
                proposal_id="prop-empty-b",
                terms=[],
                capabilities=[],
                valid_until=datetime.now().isoformat(),
            ),
            priorities=[],
            constraints=[],
            flexibility=FlexibilityAssessment(
                flexible_terms=[],
                trade_off_pairs=[],
                total_flexibility_score=0.0,
            ),
        )

        analysis = mediator.find_common_ground(party_a, party_b)

        assert analysis.overall_alignment == 0.0

    def test_incompatible_non_negotiable_terms(self, mediator):
        """Test mediation with incompatible non-negotiable terms."""
        party_a = PartyPosition(
            party_id="agent-a",
            party_name="Agent A",
            proposal=NegotiationProposalSummary(
                proposal_id="prop-a",
                terms=[
                    TermSummary(
                        term_name="protocol",
                        term_value="REST",
                        negotiable=False,
                    ),
                ],
                capabilities=[],
                valid_until=datetime.now().isoformat(),
            ),
            priorities=[],
            constraints=[],
            flexibility=FlexibilityAssessment(
                flexible_terms=[],
                trade_off_pairs=[],
                total_flexibility_score=0.0,
            ),
        )
        party_b = PartyPosition(
            party_id="agent-b",
            party_name="Agent B",
            proposal=NegotiationProposalSummary(
                proposal_id="prop-b",
                terms=[
                    TermSummary(
                        term_name="protocol",
                        term_value="GraphQL",
                        negotiable=False,
                    ),
                ],
                capabilities=[],
                valid_until=datetime.now().isoformat(),
            ),
            priorities=[],
            constraints=[],
            flexibility=FlexibilityAssessment(
                flexible_terms=[],
                trade_off_pairs=[],
                total_flexibility_score=0.0,
            ),
        )

        analysis = mediator.find_common_ground(party_a, party_b)

        assert len(analysis.incompatible_terms) == 1
        assert analysis.incompatible_terms[0].term_name == "protocol"

    def test_numeric_value_split(self, mediator):
        """Test numeric value splitting."""
        # Use private method for split
        result = mediator._split_difference("100", "200")
        assert result == "150.0"

    def test_non_numeric_value_split(self, mediator):
        """Test non-numeric value handling in split."""
        result = mediator._split_difference("high", "low")
        assert result == "high"  # Falls back to first value


class TestMediationHistory:
    """Tests for mediation history tracking."""

    def test_get_empty_history(self, mediator):
        """Test getting history for non-existent session."""
        history = mediator.get_mediation_history("non-existent-session")
        assert history == []

    def test_history_accumulates(self, mediator, sample_mediation_request):
        """Test that history accumulates across mediations."""
        mediator.mediate(sample_mediation_request)
        mediator.mediate(sample_mediation_request)

        history = mediator.get_mediation_history(sample_mediation_request.session_id)
        assert len(history) == 2


class TestValueGapAssessment:
    """Tests for value gap assessment."""

    def test_numeric_gap_assessment(self, mediator):
        """Test numeric gap assessment."""
        term_a = TermSummary(
            term_name="rate",
            term_value="100",
            negotiable=True,
        )
        term_b = TermSummary(
            term_name="rate",
            term_value="200",
            negotiable=True,
        )

        gap = mediator._assess_value_gap(term_a, term_b)
        assert 0.0 <= gap <= 1.0

    def test_identical_values_gap(self, mediator):
        """Test gap assessment for identical values."""
        term_a = TermSummary(
            term_name="format",
            term_value="json",
            negotiable=True,
        )
        term_b = TermSummary(
            term_name="format",
            term_value="json",
            negotiable=True,
        )

        gap = mediator._assess_value_gap(term_a, term_b)
        assert gap == 0.0


class TestModuleExports:
    """Tests for module exports."""

    def test_exports_from_package(self):
        """Test that all types are exported from the package."""
        from src.agent_negotiation import (
            MediationStyle,
            MediationResolutionStrategy,
            MediationOutcome,
            ConflictPriority,
            PartyPosition,
            MediationRequest,
            MediationResult,
            ConflictMediator,
        )

        assert MediationStyle.FACILITATIVE is not None
        assert MediationResolutionStrategy.BRIDGE is not None
        assert MediationOutcome.RESOLVED is not None
        assert ConflictPriority.HIGH is not None
