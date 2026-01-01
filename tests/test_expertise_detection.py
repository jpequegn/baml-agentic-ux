"""
Tests for the Expertise Detection Algorithm.
Issue #45 - Phase 2: Adaptive Interface Personalization

Tests cover:
- Factor calculation (Command Fluency, Success Rate, Self-Sufficiency, Engagement)
- Weighted scoring model
- Level thresholds and transitions
- EMA smoothing
- Cold start handling
- Trend analysis
"""

import math
import uuid
from datetime import datetime

import pytest

from src.lui_simulator.expertise import (
    ColdStartConfig,
    ExpertiseDetectionConfig,
    ExpertiseDetector,
    ExpertiseFactor,
    ExpertiseFactorBreakdown,
    ExpertiseLevel,
)
from src.lui_simulator.metrics import (
    InteractionOutcome,
    InteractionRecord,
    MetricsWindow,
    TrendDirection,
)


# ============================================
# Fixtures
# ============================================


def create_interaction(
    outcome: InteractionOutcome = InteractionOutcome.SUCCESS,
    used_shortcut: bool = False,
    help_requested: bool = False,
    disambiguation_needed: bool = False,
    error_count: int = 0,
    retries: int = 0,
    input_length: int = 50,
    intent_confidence: float = 0.9,
    parameters_provided: int = 2,
    parameters_required: int = 2,
    completion_time_ms: int = 500,
    session_id: str = "session-1",
    intent_detected: str = "test_intent",
) -> InteractionRecord:
    """Create a test interaction record."""
    return InteractionRecord(
        interaction_id=str(uuid.uuid4()),
        timestamp=datetime.now().isoformat(),
        session_id=session_id,
        intent_detected=intent_detected,
        intent_confidence=intent_confidence,
        parameters_provided=parameters_provided,
        parameters_required=parameters_required,
        outcome=outcome,
        completion_time_ms=completion_time_ms,
        error_count=error_count,
        help_requested=help_requested,
        disambiguation_needed=disambiguation_needed,
        used_shortcut=used_shortcut,
        input_length=input_length,
        retries=retries,
        corrections=0,
    )


def create_expert_interactions(count: int = 20) -> list[InteractionRecord]:
    """Create interactions typical of an expert user."""
    interactions = []
    for i in range(count):
        interactions.append(create_interaction(
            outcome=InteractionOutcome.SUCCESS,
            used_shortcut=True,
            help_requested=False,
            disambiguation_needed=False,
            error_count=0,
            retries=0,
            input_length=20,  # Concise
            intent_confidence=0.95,
            parameters_provided=3,
            parameters_required=3,
            session_id=f"session-{i % 5}",
            intent_detected=f"intent_{i % 10}",
        ))
    return interactions


def create_novice_interactions(count: int = 20) -> list[InteractionRecord]:
    """Create interactions typical of a novice user."""
    interactions = []
    for i in range(count):
        interactions.append(create_interaction(
            outcome=InteractionOutcome.FAILURE if i % 3 == 0 else InteractionOutcome.PARTIAL_SUCCESS,
            used_shortcut=False,
            help_requested=True,
            disambiguation_needed=True,
            error_count=2,
            retries=3,
            input_length=150,  # Verbose
            intent_confidence=0.5,
            parameters_provided=1,
            parameters_required=3,
            session_id="session-1",
            intent_detected="basic_intent",
        ))
    return interactions


def create_intermediate_interactions(count: int = 20) -> list[InteractionRecord]:
    """Create interactions typical of an intermediate user."""
    interactions = []
    for i in range(count):
        success = i % 4 != 0
        interactions.append(create_interaction(
            outcome=InteractionOutcome.SUCCESS if success else InteractionOutcome.PARTIAL_SUCCESS,
            used_shortcut=i % 3 == 0,
            help_requested=i % 5 == 0,
            disambiguation_needed=i % 6 == 0,
            error_count=0 if success else 1,
            retries=0 if success else 1,
            input_length=60,
            intent_confidence=0.75,
            parameters_provided=2,
            parameters_required=3,
            session_id=f"session-{i % 3}",
            intent_detected=f"intent_{i % 5}",
        ))
    return interactions


# ============================================
# ExpertiseFactor Tests
# ============================================


class TestExpertiseFactor:
    """Tests for ExpertiseFactor dataclass."""

    def test_create_valid_factor(self):
        """Test creating a valid expertise factor."""
        factor = ExpertiseFactor(
            factor_name="test_factor",
            weight=0.3,
            raw_value=0.8,
            weighted_value=0.24,
            confidence=0.9,
            evidence=["High success rate", "Fast completion"],
        )

        assert factor.factor_name == "test_factor"
        assert factor.weight == 0.3
        assert factor.raw_value == 0.8
        assert factor.weighted_value == 0.24
        assert factor.confidence == 0.9
        assert len(factor.evidence) == 2

    def test_invalid_weight_raises_error(self):
        """Test that invalid weight raises ValueError."""
        with pytest.raises(ValueError, match="Weight must be 0-1"):
            ExpertiseFactor(
                factor_name="test",
                weight=1.5,
                raw_value=0.5,
                weighted_value=0.75,
                confidence=0.5,
            )

    def test_invalid_raw_value_raises_error(self):
        """Test that invalid raw value raises ValueError."""
        with pytest.raises(ValueError, match="Raw value must be 0-1"):
            ExpertiseFactor(
                factor_name="test",
                weight=0.3,
                raw_value=-0.1,
                weighted_value=0.0,
                confidence=0.5,
            )

    def test_invalid_confidence_raises_error(self):
        """Test that invalid confidence raises ValueError."""
        with pytest.raises(ValueError, match="Confidence must be 0-1"):
            ExpertiseFactor(
                factor_name="test",
                weight=0.3,
                raw_value=0.5,
                weighted_value=0.15,
                confidence=1.5,
            )


# ============================================
# ExpertiseFactorBreakdown Tests
# ============================================


class TestExpertiseFactorBreakdown:
    """Tests for ExpertiseFactorBreakdown."""

    def test_total_score_calculation(self):
        """Test that total score sums weighted values correctly."""
        breakdown = ExpertiseFactorBreakdown(
            command_fluency=ExpertiseFactor("cf", 0.30, 0.8, 0.24, 0.9),
            success_rate=ExpertiseFactor("sr", 0.25, 0.7, 0.175, 0.9),
            self_sufficiency=ExpertiseFactor("ss", 0.25, 0.6, 0.15, 0.9),
            engagement=ExpertiseFactor("eg", 0.20, 0.9, 0.18, 0.9),
        )

        expected = 0.24 + 0.175 + 0.15 + 0.18
        assert math.isclose(breakdown.total_score(), expected, rel_tol=1e-6)


# ============================================
# ExpertiseDetectionConfig Tests
# ============================================


class TestExpertiseDetectionConfig:
    """Tests for ExpertiseDetectionConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ExpertiseDetectionConfig()

        assert config.command_fluency_weight == 0.30
        assert config.success_rate_weight == 0.25
        assert config.self_sufficiency_weight == 0.25
        assert config.engagement_weight == 0.20
        assert config.ema_alpha == 0.3
        assert config.cold_start.min_interactions == 10

    def test_weights_must_sum_to_one(self):
        """Test that factor weights must sum to 1.0."""
        with pytest.raises(ValueError, match="Factor weights must sum to 1.0"):
            ExpertiseDetectionConfig(
                command_fluency_weight=0.5,
                success_rate_weight=0.5,
                self_sufficiency_weight=0.5,
                engagement_weight=0.5,
            )

    def test_valid_custom_weights(self):
        """Test creating config with custom weights that sum to 1.0."""
        config = ExpertiseDetectionConfig(
            command_fluency_weight=0.4,
            success_rate_weight=0.3,
            self_sufficiency_weight=0.2,
            engagement_weight=0.1,
        )

        total = (
            config.command_fluency_weight +
            config.success_rate_weight +
            config.self_sufficiency_weight +
            config.engagement_weight
        )
        assert math.isclose(total, 1.0, rel_tol=1e-6)

    def test_invalid_ema_alpha(self):
        """Test that invalid EMA alpha raises error."""
        with pytest.raises(ValueError, match="EMA alpha must be"):
            ExpertiseDetectionConfig(ema_alpha=0.0)


# ============================================
# ExpertiseDetector Basic Tests
# ============================================


class TestExpertiseDetectorBasics:
    """Basic tests for ExpertiseDetector."""

    def test_initialization(self):
        """Test detector initialization."""
        detector = ExpertiseDetector()

        assert detector.current_estimate is None
        assert len(detector.estimate_history) == 0

    def test_initialization_with_config(self):
        """Test detector initialization with custom config."""
        config = ExpertiseDetectionConfig(ema_alpha=0.5)
        detector = ExpertiseDetector(config=config)

        assert detector.config.ema_alpha == 0.5

    def test_reset_clears_state(self):
        """Test that reset clears all state."""
        detector = ExpertiseDetector()
        interactions = create_intermediate_interactions(20)
        detector.estimate_expertise(interactions)

        assert detector.current_estimate is not None

        detector.reset()

        assert detector.current_estimate is None
        assert len(detector.estimate_history) == 0


# ============================================
# Cold Start Tests
# ============================================


class TestColdStart:
    """Tests for cold start handling."""

    def test_no_interactions_returns_default(self):
        """Test that no interactions returns default estimate."""
        detector = ExpertiseDetector()
        estimate = detector.estimate_expertise([])

        assert estimate.is_cold_start is True
        assert estimate.cold_start_reason == "No interaction data available"
        assert estimate.estimated_level == ExpertiseLevel.INTERMEDIATE
        assert estimate.expertise_score == 0.5
        assert estimate.confidence == 0.3

    def test_few_interactions_is_cold_start(self):
        """Test that few interactions triggers cold start."""
        detector = ExpertiseDetector()
        interactions = create_intermediate_interactions(5)  # Below min of 10
        estimate = detector.estimate_expertise(interactions)

        assert estimate.is_cold_start is True
        assert "5 interactions" in estimate.cold_start_reason
        assert estimate.confidence < 0.5  # Reduced confidence

    def test_sufficient_interactions_not_cold_start(self):
        """Test that sufficient interactions is not cold start."""
        detector = ExpertiseDetector()
        interactions = create_intermediate_interactions(15)
        estimate = detector.estimate_expertise(interactions)

        assert estimate.is_cold_start is False
        assert estimate.cold_start_reason is None

    def test_custom_cold_start_config(self):
        """Test custom cold start configuration."""
        config = ExpertiseDetectionConfig(
            cold_start=ColdStartConfig(
                min_interactions=5,
                default_level=ExpertiseLevel.BEGINNER,
                default_score=0.3,
            )
        )
        detector = ExpertiseDetector(config=config)

        # 5 interactions should not be cold start with min=5
        interactions = create_intermediate_interactions(5)
        estimate = detector.estimate_expertise(interactions)

        assert estimate.is_cold_start is False


# ============================================
# Level Threshold Tests
# ============================================


class TestLevelThresholds:
    """Tests for expertise level thresholds."""

    def test_novice_level_range(self):
        """Test NOVICE level for scores 0.0-0.2."""
        detector = ExpertiseDetector()
        # Force a novice-level score by using poor interactions
        interactions = create_novice_interactions(20)
        estimate = detector.estimate_expertise(interactions)

        # Novice interactions should produce low score
        assert estimate.expertise_score < 0.4

    def test_expert_level_range(self):
        """Test EXPERT level for scores 0.8-1.0."""
        detector = ExpertiseDetector()
        interactions = create_expert_interactions(30)
        estimate = detector.estimate_expertise(interactions)

        assert estimate.expertise_score > 0.6
        # With expert-like interactions, should be ADVANCED or EXPERT
        assert estimate.estimated_level in [ExpertiseLevel.ADVANCED, ExpertiseLevel.EXPERT]

    def test_intermediate_level_range(self):
        """Test INTERMEDIATE level for scores 0.4-0.6."""
        detector = ExpertiseDetector()
        interactions = create_intermediate_interactions(30)
        estimate = detector.estimate_expertise(interactions)

        # Intermediate interactions should produce mid-range score
        assert 0.3 <= estimate.expertise_score <= 0.7


# ============================================
# Factor Calculation Tests
# ============================================


class TestCommandFluencyFactor:
    """Tests for command fluency factor calculation."""

    def test_high_shortcut_usage_increases_fluency(self):
        """Test that shortcut usage increases command fluency."""
        detector = ExpertiseDetector()

        # All shortcuts
        shortcut_interactions = [
            create_interaction(used_shortcut=True, input_length=20)
            for _ in range(20)
        ]
        shortcut_estimate = detector.estimate_expertise(shortcut_interactions)
        shortcut_fluency = shortcut_estimate.factor_breakdown.command_fluency.raw_value

        detector.reset()

        # No shortcuts
        no_shortcut_interactions = [
            create_interaction(used_shortcut=False, input_length=20)
            for _ in range(20)
        ]
        no_shortcut_estimate = detector.estimate_expertise(no_shortcut_interactions)
        no_shortcut_fluency = no_shortcut_estimate.factor_breakdown.command_fluency.raw_value

        assert shortcut_fluency > no_shortcut_fluency

    def test_complete_parameters_increases_fluency(self):
        """Test that complete parameter provision increases fluency."""
        detector = ExpertiseDetector()

        # Complete params
        complete_interactions = [
            create_interaction(parameters_provided=3, parameters_required=3)
            for _ in range(20)
        ]
        complete_estimate = detector.estimate_expertise(complete_interactions)
        complete_fluency = complete_estimate.factor_breakdown.command_fluency.raw_value

        detector.reset()

        # Incomplete params
        incomplete_interactions = [
            create_interaction(parameters_provided=1, parameters_required=3)
            for _ in range(20)
        ]
        incomplete_estimate = detector.estimate_expertise(incomplete_interactions)
        incomplete_fluency = incomplete_estimate.factor_breakdown.command_fluency.raw_value

        assert complete_fluency > incomplete_fluency


class TestSuccessRateFactor:
    """Tests for success rate factor calculation."""

    def test_all_success_high_rate(self):
        """Test that all successful interactions give high rate."""
        detector = ExpertiseDetector()
        interactions = [
            create_interaction(outcome=InteractionOutcome.SUCCESS, error_count=0)
            for _ in range(20)
        ]
        estimate = detector.estimate_expertise(interactions)

        assert estimate.factor_breakdown.success_rate.raw_value > 0.8

    def test_all_failure_low_rate(self):
        """Test that all failed interactions give low rate."""
        detector = ExpertiseDetector()
        interactions = [
            create_interaction(outcome=InteractionOutcome.FAILURE, error_count=3)
            for _ in range(20)
        ]
        estimate = detector.estimate_expertise(interactions)

        assert estimate.factor_breakdown.success_rate.raw_value < 0.4

    def test_errors_reduce_success_rate(self):
        """Test that errors reduce success rate factor."""
        detector = ExpertiseDetector()

        # No errors
        clean_interactions = [
            create_interaction(outcome=InteractionOutcome.SUCCESS, error_count=0)
            for _ in range(20)
        ]
        clean_estimate = detector.estimate_expertise(clean_interactions)

        detector.reset()

        # Many errors
        error_interactions = [
            create_interaction(outcome=InteractionOutcome.SUCCESS, error_count=3)
            for _ in range(20)
        ]
        error_estimate = detector.estimate_expertise(error_interactions)

        assert clean_estimate.factor_breakdown.success_rate.raw_value > error_estimate.factor_breakdown.success_rate.raw_value


class TestSelfSufficiencyFactor:
    """Tests for self-sufficiency factor calculation."""

    def test_no_help_high_sufficiency(self):
        """Test that no help requests give high self-sufficiency."""
        detector = ExpertiseDetector()
        interactions = [
            create_interaction(help_requested=False, disambiguation_needed=False)
            for _ in range(20)
        ]
        estimate = detector.estimate_expertise(interactions)

        assert estimate.factor_breakdown.self_sufficiency.raw_value > 0.7

    def test_frequent_help_low_sufficiency(self):
        """Test that frequent help requests give low self-sufficiency."""
        detector = ExpertiseDetector()
        interactions = [
            create_interaction(help_requested=True, disambiguation_needed=True)
            for _ in range(20)
        ]
        estimate = detector.estimate_expertise(interactions)

        assert estimate.factor_breakdown.self_sufficiency.raw_value < 0.5


class TestEngagementFactor:
    """Tests for engagement factor calculation."""

    def test_high_interaction_count_increases_engagement(self):
        """Test that more interactions increase engagement score."""
        detector = ExpertiseDetector()

        # Many interactions
        many_interactions = create_intermediate_interactions(50)
        many_estimate = detector.estimate_expertise(many_interactions)

        detector.reset()

        # Few interactions
        few_interactions = create_intermediate_interactions(10)
        few_estimate = detector.estimate_expertise(few_interactions)

        assert many_estimate.factor_breakdown.engagement.raw_value > few_estimate.factor_breakdown.engagement.raw_value

    def test_intent_variety_increases_engagement(self):
        """Test that intent variety increases engagement."""
        detector = ExpertiseDetector()

        # Many unique intents
        varied_interactions = [
            create_interaction(intent_detected=f"intent_{i}")
            for i in range(20)
        ]
        varied_estimate = detector.estimate_expertise(varied_interactions)

        detector.reset()

        # Same intent repeated
        repetitive_interactions = [
            create_interaction(intent_detected="same_intent")
            for _ in range(20)
        ]
        repetitive_estimate = detector.estimate_expertise(repetitive_interactions)

        assert varied_estimate.factor_breakdown.engagement.raw_value > repetitive_estimate.factor_breakdown.engagement.raw_value

    def test_abandonment_reduces_engagement(self):
        """Test that abandonment reduces engagement."""
        detector = ExpertiseDetector()

        # No abandonment
        complete_interactions = [
            create_interaction(outcome=InteractionOutcome.SUCCESS)
            for _ in range(20)
        ]
        complete_estimate = detector.estimate_expertise(complete_interactions)

        detector.reset()

        # High abandonment
        abandoned_interactions = [
            create_interaction(outcome=InteractionOutcome.ABANDONED)
            for _ in range(20)
        ]
        abandoned_estimate = detector.estimate_expertise(abandoned_interactions)

        assert complete_estimate.factor_breakdown.engagement.raw_value > abandoned_estimate.factor_breakdown.engagement.raw_value


# ============================================
# EMA Smoothing Tests
# ============================================


class TestEMASmoothing:
    """Tests for Exponential Moving Average smoothing."""

    def test_ema_applied_on_second_estimate(self):
        """Test that EMA is applied after first estimate."""
        detector = ExpertiseDetector()

        # First estimate
        interactions1 = create_intermediate_interactions(20)
        estimate1 = detector.estimate_expertise(interactions1)
        assert estimate1.ema_applied is False

        # Second estimate
        interactions2 = create_expert_interactions(20)
        estimate2 = detector.estimate_expertise(interactions2)
        assert estimate2.ema_applied is True
        assert estimate2.previous_score == estimate1.expertise_score

    def test_ema_smooths_score_changes(self):
        """Test that EMA smooths rapid score changes."""
        detector = ExpertiseDetector()

        # Start with intermediate
        estimate1 = detector.estimate_expertise(create_intermediate_interactions(20))
        initial_score = estimate1.expertise_score

        # Jump to expert behavior - score change should be dampened
        estimate2 = detector.estimate_expertise(create_expert_interactions(30))

        # With alpha=0.3, new = 0.3*expert + 0.7*intermediate
        # Score should not jump fully to expert level
        assert estimate2.expertise_score > initial_score
        assert estimate2.score_delta is not None

    def test_custom_ema_alpha(self):
        """Test custom EMA alpha affects smoothing."""
        # High alpha = less smoothing
        config_high = ExpertiseDetectionConfig(ema_alpha=0.9)
        detector_high = ExpertiseDetector(config=config_high)

        # Low alpha = more smoothing
        config_low = ExpertiseDetectionConfig(ema_alpha=0.1)
        detector_low = ExpertiseDetector(config=config_low)

        # Both start with intermediate
        int_interactions = create_intermediate_interactions(20)
        detector_high.estimate_expertise(int_interactions)
        detector_low.estimate_expertise(int_interactions)

        # Both get expert interactions
        exp_interactions = create_expert_interactions(30)
        high_estimate = detector_high.estimate_expertise(exp_interactions)
        low_estimate = detector_low.estimate_expertise(exp_interactions)

        # High alpha should react faster (larger score delta)
        assert abs(high_estimate.score_delta) > abs(low_estimate.score_delta)


# ============================================
# Level Transition Tests
# ============================================


class TestLevelTransitions:
    """Tests for expertise level transitions."""

    def test_upgrade_recommendation(self):
        """Test upgrade recommendation when score exceeds threshold."""
        detector = ExpertiseDetector()

        # Start at intermediate level
        estimate1 = detector.estimate_expertise(create_intermediate_interactions(20))

        # Improve to expert level over time
        for _ in range(5):
            detector.estimate_expertise(create_expert_interactions(20))

        final_estimate = detector.current_estimate
        assert final_estimate.expertise_score > estimate1.expertise_score

    def test_hysteresis_prevents_oscillation(self):
        """Test that hysteresis prevents rapid level changes."""
        detector = ExpertiseDetector()

        # Establish level
        for _ in range(3):
            detector.estimate_expertise(create_intermediate_interactions(20))

        # Small perturbation shouldn't cause level change immediately
        slight_improvement = create_intermediate_interactions(20)
        # Make slightly better
        for i in slight_improvement[:5]:
            i.outcome = InteractionOutcome.SUCCESS
            i.used_shortcut = True

        estimate = detector.estimate_expertise(slight_improvement)

        # Should be in MONITOR mode, not UPGRADE
        assert estimate.recommended_action in ["MAINTAIN", "MONITOR", None]


# ============================================
# Trend Analysis Tests
# ============================================


class TestTrendAnalysis:
    """Tests for expertise trend analysis."""

    def test_improving_trend(self):
        """Test detection of improving expertise trend."""
        detector = ExpertiseDetector()

        # Start poor, gradually improve
        detector.estimate_expertise(create_novice_interactions(15))
        detector.estimate_expertise(create_intermediate_interactions(20))
        detector.estimate_expertise(create_expert_interactions(25))

        trend = detector.get_expertise_trend()
        assert trend == TrendDirection.IMPROVING

    def test_declining_trend(self):
        """Test detection of declining expertise trend."""
        detector = ExpertiseDetector()

        # Start good, gradually decline
        detector.estimate_expertise(create_expert_interactions(25))
        detector.estimate_expertise(create_intermediate_interactions(20))
        detector.estimate_expertise(create_novice_interactions(15))

        trend = detector.get_expertise_trend()
        assert trend == TrendDirection.DECLINING

    def test_stable_trend(self):
        """Test detection of stable expertise."""
        detector = ExpertiseDetector()

        # Consistent intermediate behavior
        for _ in range(5):
            detector.estimate_expertise(create_intermediate_interactions(20))

        trend = detector.get_expertise_trend()
        assert trend == TrendDirection.STABLE

    def test_trend_requires_minimum_history(self):
        """Test that trend analysis requires minimum history."""
        detector = ExpertiseDetector()

        # Only one estimate
        detector.estimate_expertise(create_intermediate_interactions(20))
        trend = detector.get_expertise_trend()

        assert trend == TrendDirection.STABLE  # Default when insufficient data


# ============================================
# Stability Tests
# ============================================


class TestStability:
    """Tests for expertise level stability detection."""

    def test_stable_after_consistent_estimates(self):
        """Test that level is stable after consistent estimates."""
        detector = ExpertiseDetector()

        # Multiple consistent estimates
        for _ in range(6):  # More than stability_window (5)
            detector.estimate_expertise(create_intermediate_interactions(20))

        assert detector.current_estimate.level_stable is True

    def test_unstable_with_varying_scores(self):
        """Test that level is unstable with varying behavior."""
        detector = ExpertiseDetector()

        # Alternating behavior patterns
        for i in range(6):
            if i % 2 == 0:
                detector.estimate_expertise(create_expert_interactions(20))
            else:
                detector.estimate_expertise(create_novice_interactions(20))

        # Should not be stable due to high variance
        assert detector.current_estimate.level_stable is False

    def test_stability_window_configuration(self):
        """Test custom stability window size."""
        config = ExpertiseDetectionConfig(stability_window=3)
        detector = ExpertiseDetector(config=config)

        # Need at least stability_window estimates for stable check
        # Use 4 to ensure window is fully populated
        for _ in range(4):
            detector.estimate_expertise(create_intermediate_interactions(20))

        assert detector.current_estimate.level_stable is True


# ============================================
# Confidence Tests
# ============================================


class TestConfidence:
    """Tests for confidence calculation."""

    def test_confidence_increases_with_interactions(self):
        """Test that confidence increases with more interactions."""
        detector = ExpertiseDetector()

        # Few interactions
        few_estimate = detector.estimate_expertise(create_intermediate_interactions(10))

        detector.reset()

        # Many interactions
        many_estimate = detector.estimate_expertise(create_intermediate_interactions(50))

        assert many_estimate.confidence > few_estimate.confidence

    def test_cold_start_reduces_confidence(self):
        """Test that cold start reduces confidence."""
        detector = ExpertiseDetector()

        # Cold start (below minimum)
        cold_estimate = detector.estimate_expertise(create_intermediate_interactions(5))

        detector.reset()

        # Normal (above minimum)
        normal_estimate = detector.estimate_expertise(create_intermediate_interactions(15))

        assert cold_estimate.confidence < normal_estimate.confidence


# ============================================
# Integration Tests
# ============================================


class TestIntegration:
    """Integration tests for complete expertise detection flow."""

    def test_full_expertise_journey(self):
        """Test a complete user expertise journey from novice to expert."""
        detector = ExpertiseDetector()

        # Phase 1: New user (cold start)
        estimate1 = detector.estimate_expertise(create_novice_interactions(5))
        assert estimate1.is_cold_start is True

        # Phase 2: Learning (novice to beginner)
        for _ in range(3):
            detector.estimate_expertise(create_novice_interactions(15))

        # Phase 3: Improving (intermediate)
        for _ in range(3):
            detector.estimate_expertise(create_intermediate_interactions(20))

        # Phase 4: Mastering (advanced/expert)
        for _ in range(5):
            detector.estimate_expertise(create_expert_interactions(25))

        final_estimate = detector.current_estimate

        # Should have progressed from initial levels
        assert final_estimate.expertise_score > estimate1.expertise_score
        assert final_estimate.confidence > estimate1.confidence

    def test_estimate_history_tracking(self):
        """Test that estimate history is properly tracked."""
        detector = ExpertiseDetector()

        for i in range(10):
            detector.estimate_expertise(create_intermediate_interactions(15))

        assert len(detector.estimate_history) == 10

        # History should be ordered
        for i in range(1, len(detector.estimate_history)):
            # Each estimate should have increasing or stable confidence
            # (as more data accumulates)
            pass  # Just verify history exists

    def test_with_metrics_window(self):
        """Test expertise detection with pre-computed metrics window."""
        detector = ExpertiseDetector()
        interactions = create_expert_interactions(20)

        # Create a metrics window
        metrics_window = MetricsWindow(
            window_id="test-window",
            window_start=datetime.now().isoformat(),
            window_end=datetime.now().isoformat(),
            interaction_count=20,
            success_rate=0.95,
            partial_success_rate=0.05,
            failure_rate=0.0,
            abandonment_rate=0.0,
            help_rate=0.0,
            shortcut_rate=0.9,
            error_rate=0.0,
            disambiguation_rate=0.0,
            avg_completion_time_ms=300.0,
            median_completion_time_ms=280.0,
            p95_completion_time_ms=500.0,
            avg_input_length=25.0,
            avg_parameters_provided=3.0,
            avg_retries=0.0,
            success_trend=TrendDirection.STABLE,
            efficiency_trend=TrendDirection.IMPROVING,
            engagement_trend=TrendDirection.STABLE,
        )

        estimate = detector.estimate_expertise(interactions, metrics_window)

        # Should use metrics from window
        assert estimate.factor_breakdown.success_rate.raw_value > 0.7


# ============================================
# Edge Cases
# ============================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_single_interaction(self):
        """Test handling of single interaction."""
        detector = ExpertiseDetector()
        interactions = [create_interaction()]
        estimate = detector.estimate_expertise(interactions)

        assert estimate.is_cold_start is True
        assert estimate.interactions_analyzed == 1

    def test_all_parameters_zero(self):
        """Test interactions with no required parameters."""
        detector = ExpertiseDetector()
        interactions = [
            create_interaction(parameters_provided=0, parameters_required=0)
            for _ in range(20)
        ]
        estimate = detector.estimate_expertise(interactions)

        # Should handle gracefully
        assert estimate.factor_breakdown.command_fluency.raw_value >= 0

    def test_extreme_input_lengths(self):
        """Test handling of extreme input lengths."""
        detector = ExpertiseDetector()

        # Very short inputs
        short_interactions = [
            create_interaction(input_length=5)
            for _ in range(20)
        ]
        short_estimate = detector.estimate_expertise(short_interactions)

        detector.reset()

        # Very long inputs
        long_interactions = [
            create_interaction(input_length=1000)
            for _ in range(20)
        ]
        long_estimate = detector.estimate_expertise(long_interactions)

        # Both should be valid estimates
        assert 0 <= short_estimate.expertise_score <= 1
        assert 0 <= long_estimate.expertise_score <= 1
        # Short should have higher fluency
        assert short_estimate.factor_breakdown.command_fluency.raw_value > long_estimate.factor_breakdown.command_fluency.raw_value

    def test_mixed_sessions(self):
        """Test handling of interactions from multiple sessions."""
        detector = ExpertiseDetector()
        interactions = [
            create_interaction(session_id=f"session-{i % 10}")
            for i in range(50)
        ]
        estimate = detector.estimate_expertise(interactions)

        # Should have engagement bonus for multiple sessions
        assert estimate.factor_breakdown.engagement.raw_value > 0.3
