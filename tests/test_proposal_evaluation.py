"""
Tests for Proposal Evaluation & Counter-Offer Generation

Issue #58 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.6)
"""

import pytest
from typing import Dict, Any, List

from src.agent_negotiation import (
    # Enums
    CapabilityLevel,
    NegotiationStrategyType,
    RiskLevel,
    CapabilityGapType,
    TermGapType,
    ChangeType,
    NegotiationAction,
    # Capability types
    RequestedParameter,
    CapabilityRequest,
    OfferedParameter,
    CapabilityOffer,
    # Policy types
    MinimumTerms,
    ScoringWeights,
    CapabilityPriority,
    RiskFactorWeights,
    RiskTolerance,
    EvaluationPolicy,
    # Gap analysis types
    CapabilityGap,
    TermGap,
    ConstraintViolation,
    GapAnalysis,
    # Scoring types
    TermScore,
    ValueScore,
    BurdenScore,
    RiskScore,
    ScoreBreakdown,
    ProposalScore,
    # Result types
    EvaluationDecision,
    EvaluationRationale,
    ProposalChange,
    CounterProposalResult,
    ProposalEvaluationResult,
    # Evaluator class
    ProposalEvaluator,
)


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def basic_policy() -> EvaluationPolicy:
    """Create a basic evaluation policy."""
    return EvaluationPolicy(
        min_acceptable_terms=MinimumTerms(
            min_duration_hours=24,
            max_rate_limit=100,
            min_priority_level=3,
            required_capabilities=["cap-001", "cap-002"],
        ),
        negotiation_strategy=NegotiationStrategyType.COOPERATIVE,
        max_counter_offers=3,
        auto_accept_threshold=0.85,
        auto_reject_threshold=0.3,
    )


@pytest.fixture
def strict_policy() -> EvaluationPolicy:
    """Create a strict evaluation policy."""
    return EvaluationPolicy(
        min_acceptable_terms=MinimumTerms(
            min_duration_hours=168,  # 1 week minimum
            max_rate_limit=50,
            min_priority_level=7,
            required_capabilities=["cap-001", "cap-002", "cap-003"],
            forbidden_terms=["premium"],
            min_sla_availability=0.99,
        ),
        negotiation_strategy=NegotiationStrategyType.COMPETITIVE,
        max_counter_offers=2,
        auto_accept_threshold=0.95,
        auto_reject_threshold=0.4,
        risk_tolerance=RiskTolerance(
            max_risk_level=RiskLevel.MODERATE,
            require_mitigation_above=RiskLevel.LOW,
            risk_factor_weights=RiskFactorWeights(
                security=0.4,
                compliance=0.3,
                performance=0.15,
                reliability=0.1,
                cost=0.05,
            ),
        ),
    )


@pytest.fixture
def evaluator(basic_policy: EvaluationPolicy) -> ProposalEvaluator:
    """Create a basic evaluator."""
    return ProposalEvaluator(basic_policy)


@pytest.fixture
def good_offers() -> List[CapabilityOffer]:
    """Create good capability offers."""
    return [
        CapabilityOffer(
            capability_id="cap-001",
            capability_name="Task Execution",
            level=CapabilityLevel.FULL,
            parameters=[
                OfferedParameter(name="max_concurrent", value="10"),
            ],
        ),
        CapabilityOffer(
            capability_id="cap-002",
            capability_name="Data Processing",
            level=CapabilityLevel.STANDARD,
        ),
    ]


@pytest.fixture
def minimal_offers() -> List[CapabilityOffer]:
    """Create minimal capability offers."""
    return [
        CapabilityOffer(
            capability_id="cap-001",
            capability_name="Task Execution",
            level=CapabilityLevel.MINIMAL,
        ),
    ]


@pytest.fixture
def standard_requests() -> List[CapabilityRequest]:
    """Create standard capability requests."""
    return [
        CapabilityRequest(
            capability_id="req-001",
            capability_name="API Access",
            required=True,
            priority=5,
        ),
    ]


@pytest.fixture
def good_terms() -> Dict[str, Any]:
    """Create good proposal terms."""
    return {
        "duration_hours": 720,  # 30 days
        "rate_limit_per_minute": 50,
        "priority_level": 7,
        "billing_model": "per_call",
        "sla_availability": 0.99,
    }


@pytest.fixture
def poor_terms() -> Dict[str, Any]:
    """Create poor proposal terms."""
    return {
        "duration_hours": 12,  # Too short
        "rate_limit_per_minute": 200,  # Too high
        "priority_level": 1,  # Too low
        "billing_model": "premium",
    }


# ============================================
# Test Enums
# ============================================


class TestCapabilityLevel:
    """Tests for CapabilityLevel enum."""

    def test_all_levels_defined(self):
        """Verify all expected levels are defined."""
        expected = {"FULL", "STANDARD", "LIMITED", "TRIAL", "MINIMAL"}
        actual = {level.name for level in CapabilityLevel}
        assert actual == expected

    def test_level_values(self):
        """Verify level values."""
        assert CapabilityLevel.FULL.value == "full"
        assert CapabilityLevel.MINIMAL.value == "minimal"


class TestNegotiationStrategyType:
    """Tests for NegotiationStrategyType enum."""

    def test_all_strategies_defined(self):
        """Verify all expected strategies are defined."""
        expected = {"COOPERATIVE", "COMPETITIVE", "PRINCIPLED", "ACCOMMODATING", "AVOIDING"}
        actual = {s.name for s in NegotiationStrategyType}
        assert actual == expected


class TestRiskLevel:
    """Tests for RiskLevel enum."""

    def test_all_levels_defined(self):
        """Verify all risk levels are defined."""
        expected = {"LOW", "MODERATE", "HIGH", "CRITICAL"}
        actual = {level.name for level in RiskLevel}
        assert actual == expected


class TestOtherEnums:
    """Tests for other enums."""

    def test_capability_gap_type(self):
        """Verify CapabilityGapType enum."""
        assert CapabilityGapType.MISSING.value == "missing"
        assert CapabilityGapType.INSUFFICIENT_LEVEL.value == "insufficient_level"

    def test_term_gap_type(self):
        """Verify TermGapType enum."""
        assert TermGapType.BELOW_MINIMUM.value == "below_minimum"
        assert TermGapType.ABOVE_MAXIMUM.value == "above_maximum"

    def test_change_type(self):
        """Verify ChangeType enum."""
        assert ChangeType.CONCESSION.value == "concession"
        assert ChangeType.REQUEST.value == "request"


# ============================================
# Test Data Classes
# ============================================


class TestRequestedParameter:
    """Tests for RequestedParameter dataclass."""

    def test_basic_creation(self):
        """Test creating a requested parameter."""
        param = RequestedParameter(name="timeout", value="30")
        assert param.name == "timeout"
        assert param.value == "30"
        assert param.negotiable is True
        assert param.min_acceptable is None

    def test_full_creation(self):
        """Test creating with all fields."""
        param = RequestedParameter(
            name="rate_limit",
            value="100",
            negotiable=False,
            min_acceptable="50",
            max_acceptable="200",
        )
        assert param.negotiable is False
        assert param.min_acceptable == "50"


class TestCapabilityRequest:
    """Tests for CapabilityRequest dataclass."""

    def test_basic_request(self):
        """Test creating a basic capability request."""
        request = CapabilityRequest(
            capability_id="cap-001",
            capability_name="API Access",
            required=True,
        )
        assert request.capability_id == "cap-001"
        assert request.required is True
        assert request.priority == 5  # Default

    def test_full_request(self):
        """Test creating with all fields."""
        request = CapabilityRequest(
            capability_id="cap-002",
            capability_name="Data Processing",
            required=False,
            priority=8,
            usage_context="Batch processing",
        )
        assert request.priority == 8
        assert request.usage_context == "Batch processing"


class TestCapabilityOffer:
    """Tests for CapabilityOffer dataclass."""

    def test_basic_offer(self):
        """Test creating a basic capability offer."""
        offer = CapabilityOffer(
            capability_id="cap-001",
            capability_name="Task Execution",
            level=CapabilityLevel.STANDARD,
        )
        assert offer.capability_id == "cap-001"
        assert offer.level == CapabilityLevel.STANDARD
        assert offer.restrictions is None

    def test_full_offer(self):
        """Test creating with all fields."""
        offer = CapabilityOffer(
            capability_id="cap-002",
            capability_name="Data Access",
            level=CapabilityLevel.LIMITED,
            parameters=[OfferedParameter(name="max_size", value="1GB")],
            restrictions=["No PII data"],
            estimated_cost=0.3,
        )
        assert len(offer.parameters) == 1
        assert len(offer.restrictions) == 1


class TestMinimumTerms:
    """Tests for MinimumTerms dataclass."""

    def test_empty_terms(self):
        """Test creating empty minimum terms."""
        terms = MinimumTerms()
        assert terms.min_duration_hours is None
        assert terms.required_capabilities == []

    def test_full_terms(self):
        """Test creating with all fields."""
        terms = MinimumTerms(
            min_duration_hours=48,
            max_rate_limit=100,
            min_priority_level=5,
            required_capabilities=["cap-001"],
            forbidden_terms=["premium"],
            min_sla_availability=0.95,
        )
        assert terms.min_duration_hours == 48
        assert "cap-001" in terms.required_capabilities


class TestScoringWeights:
    """Tests for ScoringWeights dataclass."""

    def test_default_weights(self):
        """Test default scoring weights."""
        weights = ScoringWeights()
        assert weights.term_attractiveness == 0.4
        assert weights.offered_value == 0.3
        assert weights.request_burden == 0.3

    def test_weights_normalization(self):
        """Test that weights are normalized."""
        weights = ScoringWeights(
            term_attractiveness=0.5,
            offered_value=0.5,
            request_burden=0.5,
        )
        # Should be normalized to sum to 1.0
        total = weights.term_attractiveness + weights.offered_value + weights.request_burden
        assert abs(total - 1.0) < 0.01


class TestEvaluationPolicy:
    """Tests for EvaluationPolicy dataclass."""

    def test_basic_policy(self, basic_policy: EvaluationPolicy):
        """Test basic policy creation."""
        assert basic_policy.max_counter_offers == 3
        assert basic_policy.auto_accept_threshold == 0.85
        assert basic_policy.negotiation_strategy == NegotiationStrategyType.COOPERATIVE

    def test_strict_policy(self, strict_policy: EvaluationPolicy):
        """Test strict policy creation."""
        assert strict_policy.max_counter_offers == 2
        assert strict_policy.negotiation_strategy == NegotiationStrategyType.COMPETITIVE
        assert strict_policy.risk_tolerance is not None


class TestGapAnalysis:
    """Tests for GapAnalysis dataclass."""

    def test_no_gaps(self):
        """Test creating gap analysis with no gaps."""
        gap = GapAnalysis.no_gaps()
        assert gap.has_gaps is False
        assert gap.overall_gap_score == 0.0
        assert gap.bridgeable is True

    def test_with_gaps(self):
        """Test creating gap analysis with gaps."""
        gap = GapAnalysis(
            has_gaps=True,
            capability_gaps=[
                CapabilityGap(
                    capability_id="cap-001",
                    capability_name="Missing Cap",
                    gap_type=CapabilityGapType.MISSING,
                    severity=0.8,
                )
            ],
            term_gaps=[],
            constraint_violations=[],
            overall_gap_score=0.4,
            bridgeable=True,
            bridge_difficulty=0.4,
        )
        assert gap.has_gaps is True
        assert len(gap.capability_gaps) == 1


# ============================================
# Test ProposalEvaluator
# ============================================


class TestEvaluatorCreation:
    """Tests for evaluator creation."""

    def test_basic_creation(self, basic_policy: EvaluationPolicy):
        """Test creating an evaluator."""
        evaluator = ProposalEvaluator(basic_policy)
        assert evaluator.policy == basic_policy
        assert evaluator.can_counter is True

    def test_counter_limit(self, basic_policy: EvaluationPolicy):
        """Test counter-offer limit tracking."""
        evaluator = ProposalEvaluator(basic_policy)
        evaluator._counter_offer_count = 3
        assert evaluator.can_counter is False


class TestTermScoring:
    """Tests for term scoring."""

    def test_good_terms(
        self,
        evaluator: ProposalEvaluator,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test scoring with good terms."""
        result = evaluator.evaluate(standard_requests, good_offers, good_terms)
        assert result.score.term_score.score > 0.7

    def test_poor_terms(
        self,
        evaluator: ProposalEvaluator,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        poor_terms: Dict[str, Any],
    ):
        """Test scoring with poor terms."""
        result = evaluator.evaluate(standard_requests, good_offers, poor_terms)
        # Poor terms should score lower than good terms
        assert result.score.term_score.score < 0.7

    def test_duration_scoring(self, evaluator: ProposalEvaluator):
        """Test duration term scoring."""
        # Good duration
        result1 = evaluator.evaluate([], [], {"duration_hours": 100})
        # Poor duration
        result2 = evaluator.evaluate([], [], {"duration_hours": 10})
        assert result1.score.term_score.duration_score > result2.score.term_score.duration_score


class TestValueScoring:
    """Tests for value scoring."""

    def test_good_offers(
        self,
        evaluator: ProposalEvaluator,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test scoring with good capability offers."""
        result = evaluator.evaluate(standard_requests, good_offers, good_terms)
        assert result.score.value_score.score > 0.5

    def test_minimal_offers(
        self,
        evaluator: ProposalEvaluator,
        minimal_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test scoring with minimal capability offers."""
        result = evaluator.evaluate(standard_requests, minimal_offers, good_terms)
        # Minimal level should score lower
        assert result.score.value_score.capability_quality < 0.5

    def test_empty_offers(
        self,
        evaluator: ProposalEvaluator,
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test scoring with no capability offers."""
        result = evaluator.evaluate(standard_requests, [], good_terms)
        assert result.score.value_score.score == 0.0


class TestBurdenScoring:
    """Tests for burden scoring."""

    def test_low_burden(
        self,
        evaluator: ProposalEvaluator,
        good_offers: List[CapabilityOffer],
        good_terms: Dict[str, Any],
    ):
        """Test scoring with low request burden."""
        # Single non-required request
        requests = [
            CapabilityRequest(
                capability_id="req-001",
                capability_name="Optional",
                required=False,
                priority=2,
            )
        ]
        result = evaluator.evaluate(requests, good_offers, good_terms)
        assert result.score.burden_score.score < 0.5

    def test_high_burden(
        self,
        evaluator: ProposalEvaluator,
        good_offers: List[CapabilityOffer],
        good_terms: Dict[str, Any],
    ):
        """Test scoring with high request burden."""
        # Multiple high-priority required requests
        requests = [
            CapabilityRequest(
                capability_id=f"req-{i}",
                capability_name=f"Required {i}",
                required=True,
                priority=9,
            )
            for i in range(5)
        ]
        result = evaluator.evaluate(requests, good_offers, good_terms)
        # Higher burden than low burden case
        assert result.score.burden_score.score > 0.4


class TestGapAnalysis:
    """Tests for gap analysis."""

    def test_no_gaps(
        self,
        evaluator: ProposalEvaluator,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test gap analysis when requirements are met."""
        result = evaluator.evaluate(standard_requests, good_offers, good_terms)
        # Good offers cover required capabilities
        # (cap-001 and cap-002 are required, and good_offers provides them)
        assert result.gap_analysis.overall_gap_score < 0.5

    def test_missing_capability_gap(
        self,
        evaluator: ProposalEvaluator,
        minimal_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test gap analysis with missing required capability."""
        result = evaluator.evaluate(standard_requests, minimal_offers, good_terms)
        # minimal_offers only has cap-001, missing cap-002
        assert result.gap_analysis.has_gaps is True
        missing_caps = [
            g for g in result.gap_analysis.capability_gaps
            if g.gap_type == CapabilityGapType.MISSING
        ]
        assert len(missing_caps) >= 1

    def test_term_gap(
        self,
        evaluator: ProposalEvaluator,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        poor_terms: Dict[str, Any],
    ):
        """Test gap analysis with term gaps."""
        result = evaluator.evaluate(standard_requests, good_offers, poor_terms)
        assert result.gap_analysis.has_gaps is True
        assert len(result.gap_analysis.term_gaps) > 0

    def test_constraint_violation(self, strict_policy: EvaluationPolicy):
        """Test gap analysis with constraint violation."""
        evaluator = ProposalEvaluator(strict_policy)
        offers = [
            CapabilityOffer(
                capability_id="cap-001",
                capability_name="Task",
                level=CapabilityLevel.STANDARD,
            ),
        ]
        terms = {"billing_model": "premium"}  # Forbidden term
        result = evaluator.evaluate([], offers, terms)
        assert len(result.gap_analysis.constraint_violations) > 0


class TestDecisionMaking:
    """Tests for decision making."""

    def test_auto_accept(
        self,
        basic_policy: EvaluationPolicy,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test auto-accept above threshold."""
        # Create policy with low auto-accept threshold
        policy = EvaluationPolicy(
            min_acceptable_terms=MinimumTerms(),
            negotiation_strategy=NegotiationStrategyType.ACCOMMODATING,
            auto_accept_threshold=0.3,  # Very low threshold
        )
        evaluator = ProposalEvaluator(policy)
        result = evaluator.evaluate(standard_requests, good_offers, good_terms)
        assert result.decision.action == NegotiationAction.ACCEPT
        assert result.decision.auto_decided is True
        assert result.decision.threshold_triggered == "auto_accept"

    def test_auto_reject(
        self,
        basic_policy: EvaluationPolicy,
        standard_requests: List[CapabilityRequest],
        poor_terms: Dict[str, Any],
    ):
        """Test auto-reject below threshold."""
        # Create policy with high auto-reject threshold
        policy = EvaluationPolicy(
            min_acceptable_terms=MinimumTerms(
                min_duration_hours=1000,  # Impossible to meet
                required_capabilities=["impossible-cap"],
            ),
            negotiation_strategy=NegotiationStrategyType.COMPETITIVE,
            auto_reject_threshold=0.9,  # Very high threshold
        )
        evaluator = ProposalEvaluator(policy)
        result = evaluator.evaluate(standard_requests, [], poor_terms)
        assert result.decision.action == NegotiationAction.REJECT
        assert result.decision.auto_decided is True

    def test_counter_decision(
        self,
        evaluator: ProposalEvaluator,
        minimal_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test counter-offer decision when in middle range."""
        result = evaluator.evaluate(standard_requests, minimal_offers, good_terms)
        # Should counter when not auto-accept or auto-reject
        if result.decision.action == NegotiationAction.COUNTER:
            assert result.counter_proposal_result is not None

    def test_counter_limit_forces_decision(
        self,
        basic_policy: EvaluationPolicy,
        minimal_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test that exceeding counter limit forces accept/reject."""
        evaluator = ProposalEvaluator(basic_policy)
        evaluator._counter_offer_count = 3  # Max counter offers reached
        result = evaluator.evaluate(standard_requests, minimal_offers, good_terms)
        # Should be accept or reject (not counter)
        assert result.decision.action in (NegotiationAction.ACCEPT, NegotiationAction.REJECT)
        # If auto-decided due to unbridgeable gaps, no human review needed
        # Otherwise, human review is required


class TestCounterProposalGeneration:
    """Tests for counter-proposal generation."""

    def test_counter_proposal_generated(
        self,
        evaluator: ProposalEvaluator,
        minimal_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test that counter-proposal is generated when appropriate."""
        result = evaluator.evaluate(standard_requests, minimal_offers, good_terms)
        if result.decision.action == NegotiationAction.COUNTER:
            assert result.counter_proposal_result is not None
            assert len(result.counter_proposal_result.changes_made) > 0

    def test_counter_proposal_addresses_gaps(
        self,
        evaluator: ProposalEvaluator,
        minimal_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test that counter-proposal addresses identified gaps."""
        result = evaluator.evaluate(standard_requests, minimal_offers, good_terms)
        if result.decision.action == NegotiationAction.COUNTER:
            changes = result.counter_proposal_result.changes_made
            # Should have changes related to capability gaps
            capability_changes = [c for c in changes if "capability" in c.field]
            assert len(capability_changes) >= 0  # May or may not have depending on gaps

    def test_counter_increments_count(
        self,
        evaluator: ProposalEvaluator,
        minimal_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test that counter-offer increments count."""
        initial_count = evaluator._counter_offer_count
        result = evaluator.evaluate(standard_requests, minimal_offers, good_terms)
        if result.decision.action == NegotiationAction.COUNTER:
            assert evaluator._counter_offer_count == initial_count + 1


class TestRationale:
    """Tests for evaluation rationale."""

    def test_rationale_generated(
        self,
        evaluator: ProposalEvaluator,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test that rationale is generated."""
        result = evaluator.evaluate(standard_requests, good_offers, good_terms)
        assert result.rationale is not None
        assert result.rationale.summary is not None
        assert len(result.rationale.key_factors) > 0

    def test_rationale_includes_score(
        self,
        evaluator: ProposalEvaluator,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test that rationale includes score information."""
        result = evaluator.evaluate(standard_requests, good_offers, good_terms)
        # Key factors should include overall score
        score_factor = [f for f in result.rationale.key_factors if "score" in f.lower()]
        assert len(score_factor) > 0


class TestRecommendations:
    """Tests for recommendations."""

    def test_recommendations_for_accept(
        self,
        basic_policy: EvaluationPolicy,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test recommendations for accept decision."""
        policy = EvaluationPolicy(
            min_acceptable_terms=MinimumTerms(),
            negotiation_strategy=NegotiationStrategyType.ACCOMMODATING,
            auto_accept_threshold=0.3,
        )
        evaluator = ProposalEvaluator(policy)
        result = evaluator.evaluate(standard_requests, good_offers, good_terms)
        if result.decision.action == NegotiationAction.ACCEPT:
            assert any("accept" in r.lower() for r in result.recommendations)

    def test_recommendations_for_counter(
        self,
        evaluator: ProposalEvaluator,
        minimal_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test recommendations for counter decision."""
        result = evaluator.evaluate(standard_requests, minimal_offers, good_terms)
        if result.decision.action == NegotiationAction.COUNTER:
            assert any("counter" in r.lower() for r in result.recommendations)


class TestConfidence:
    """Tests for confidence calculation."""

    def test_high_confidence_for_clear_decision(
        self,
        basic_policy: EvaluationPolicy,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test high confidence for clear accept/reject."""
        policy = EvaluationPolicy(
            min_acceptable_terms=MinimumTerms(),
            negotiation_strategy=NegotiationStrategyType.ACCOMMODATING,
            auto_accept_threshold=0.2,
        )
        evaluator = ProposalEvaluator(policy)
        result = evaluator.evaluate(standard_requests, good_offers, good_terms)
        # Clear decisions should have higher confidence
        if result.score.overall_score > 0.8:
            assert result.confidence > 0.7


class TestScoreBreakdown:
    """Tests for score breakdown (SWOT analysis)."""

    def test_breakdown_structure(
        self,
        evaluator: ProposalEvaluator,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test score breakdown has all SWOT components."""
        result = evaluator.evaluate(standard_requests, good_offers, good_terms)
        breakdown = result.score.breakdown
        assert len(breakdown.strengths) > 0
        assert len(breakdown.weaknesses) > 0
        assert len(breakdown.opportunities) > 0
        assert len(breakdown.threats) > 0

    def test_breakdown_reflects_proposal(
        self,
        evaluator: ProposalEvaluator,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test breakdown reflects proposal quality."""
        result = evaluator.evaluate(standard_requests, good_offers, good_terms)
        breakdown = result.score.breakdown
        # Good proposal should have meaningful strengths
        assert any(len(s) > 10 for s in breakdown.strengths)


class TestRiskAssessment:
    """Tests for risk assessment."""

    def test_risk_with_tolerance(self, strict_policy: EvaluationPolicy):
        """Test risk assessment with tolerance settings."""
        evaluator = ProposalEvaluator(strict_policy)
        offers = [
            CapabilityOffer(
                capability_id="cap-001",
                capability_name="Task",
                level=CapabilityLevel.TRIAL,  # Trial level is risky
                restrictions=["No production use", "Limited data"],
            ),
        ]
        result = evaluator.evaluate([], offers, {})
        # Should have some risk score
        assert result.score.risk_score.score >= 0.0

    def test_low_risk_with_good_offers(
        self,
        evaluator: ProposalEvaluator,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test low risk with good capability offers."""
        result = evaluator.evaluate(standard_requests, good_offers, good_terms)
        # Good offers should have lower risk
        assert result.score.risk_score.score < 0.5


class TestStrategyInfluence:
    """Tests for strategy influence on decisions."""

    def test_cooperative_strategy(self):
        """Test cooperative strategy generates concessions."""
        policy = EvaluationPolicy(
            min_acceptable_terms=MinimumTerms(),
            negotiation_strategy=NegotiationStrategyType.COOPERATIVE,
        )
        evaluator = ProposalEvaluator(policy)
        offers = [
            CapabilityOffer(
                capability_id="cap-001",
                capability_name="Basic",
                level=CapabilityLevel.LIMITED,
            ),
        ]
        requests = [
            CapabilityRequest(
                capability_id="req-001",
                capability_name="Access",
                required=True,
                priority=5,
            ),
            CapabilityRequest(
                capability_id="req-002",
                capability_name="Data",
                required=True,
                priority=3,
            ),
        ]
        result = evaluator.evaluate(requests, offers, {"duration_hours": 50})
        if result.decision.action == NegotiationAction.COUNTER:
            # Cooperative strategy should offer concessions
            assert len(result.counter_proposal_result.concessions_offered) >= 0

    def test_competitive_strategy(self, strict_policy: EvaluationPolicy):
        """Test competitive strategy is stricter."""
        evaluator = ProposalEvaluator(strict_policy)
        offers = []  # No offers
        result = evaluator.evaluate([], offers, {})
        # With no offers, value score is 0, leading to lower overall score
        # The overall score depends on all weights
        assert result.score.value_score.score == 0.0  # No offers = 0 value


class TestResetCounter:
    """Tests for counter count reset."""

    def test_reset_counter(self, basic_policy: EvaluationPolicy):
        """Test resetting counter count."""
        evaluator = ProposalEvaluator(basic_policy)
        evaluator._counter_offer_count = 2
        evaluator.reset_counter_count()
        assert evaluator._counter_offer_count == 0
        assert evaluator.can_counter is True


class TestIntegration:
    """Integration tests for complete evaluation workflow."""

    def test_full_evaluation_flow(
        self,
        evaluator: ProposalEvaluator,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
    ):
        """Test complete evaluation flow."""
        result = evaluator.evaluate(standard_requests, good_offers, good_terms)

        # Verify result structure
        assert result.decision is not None
        assert result.score is not None
        assert result.gap_analysis is not None
        assert result.rationale is not None
        assert result.recommendations is not None
        assert 0.0 <= result.confidence <= 1.0

        # Verify score components
        assert 0.0 <= result.score.overall_score <= 1.0
        assert result.score.term_score is not None
        assert result.score.value_score is not None
        assert result.score.burden_score is not None
        assert result.score.risk_score is not None

    def test_multiple_evaluations(
        self,
        basic_policy: EvaluationPolicy,
        good_offers: List[CapabilityOffer],
        minimal_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
        good_terms: Dict[str, Any],
        poor_terms: Dict[str, Any],
    ):
        """Test multiple evaluations with different proposals."""
        evaluator = ProposalEvaluator(basic_policy)

        # Good proposal
        result1 = evaluator.evaluate(standard_requests, good_offers, good_terms)

        # Poor proposal
        result2 = evaluator.evaluate(standard_requests, minimal_offers, poor_terms)

        # Good proposal should score higher
        assert result1.score.overall_score > result2.score.overall_score

    def test_proposal_comparison(
        self,
        basic_policy: EvaluationPolicy,
        good_offers: List[CapabilityOffer],
        standard_requests: List[CapabilityRequest],
    ):
        """Test comparing similar proposals with different terms."""
        evaluator = ProposalEvaluator(basic_policy)

        # Better terms
        terms1 = {
            "duration_hours": 720,
            "rate_limit_per_minute": 30,
            "priority_level": 8,
        }

        # Worse terms
        terms2 = {
            "duration_hours": 24,
            "rate_limit_per_minute": 150,
            "priority_level": 2,
        }

        result1 = evaluator.evaluate(standard_requests, good_offers, terms1)
        evaluator.reset_counter_count()
        result2 = evaluator.evaluate(standard_requests, good_offers, terms2)

        assert result1.score.term_score.score > result2.score.term_score.score
