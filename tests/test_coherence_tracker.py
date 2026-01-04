"""Tests for the Conversation Coherence Tracker.

Issue #83 - Task 5.6: Conversation Coherence Tracker
Part of #28 - Phase 5: Intent Drift Detection
"""

import pytest

from src.intent_drift import (
    CoherenceAnalysis,
    CoherenceTrend,
    DriftAnalysis,
    DriftConversationTurn,
    DriftType,
)
from src.intent_drift.coherence_tracker import (
    CoherenceMetrics,
    CoherenceTrackerConfig,
    ContextResetReason,
    ContextResetTrigger,
    ConversationCoherenceTracker,
    DriftTrend,
    TurnCoherence,
)


# ============================================
# Configuration Tests
# ============================================


class TestCoherenceTrackerConfig:
    """Tests for CoherenceTrackerConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = CoherenceTrackerConfig()
        assert config.window_size == 5
        assert config.drift_accumulation_threshold == 2.5
        assert config.coherence_collapse_threshold == 0.3
        assert config.sudden_drift_threshold == 0.5
        assert config.recovery_window == 3
        assert config.min_turns_for_trend == 3
        assert config.enable_auto_reset is True

    def test_custom_values(self):
        """Test custom configuration values."""
        config = CoherenceTrackerConfig(
            window_size=10,
            drift_accumulation_threshold=5.0,
            coherence_collapse_threshold=0.2,
            sudden_drift_threshold=0.4,
            recovery_window=5,
            min_turns_for_trend=4,
            enable_auto_reset=False,
        )
        assert config.window_size == 10
        assert config.drift_accumulation_threshold == 5.0
        assert config.coherence_collapse_threshold == 0.2
        assert config.sudden_drift_threshold == 0.4
        assert config.recovery_window == 5
        assert config.min_turns_for_trend == 4
        assert config.enable_auto_reset is False

    def test_invalid_window_size(self):
        """Test validation of window_size."""
        with pytest.raises(ValueError, match="window_size must be at least 2"):
            CoherenceTrackerConfig(window_size=1)

    def test_invalid_drift_threshold(self):
        """Test validation of drift_accumulation_threshold."""
        with pytest.raises(ValueError, match="drift_accumulation_threshold"):
            CoherenceTrackerConfig(drift_accumulation_threshold=15.0)

    def test_invalid_coherence_threshold(self):
        """Test validation of coherence_collapse_threshold."""
        with pytest.raises(ValueError, match="coherence_collapse_threshold"):
            CoherenceTrackerConfig(coherence_collapse_threshold=1.5)

    def test_invalid_sudden_drift_threshold(self):
        """Test validation of sudden_drift_threshold."""
        with pytest.raises(ValueError, match="sudden_drift_threshold"):
            CoherenceTrackerConfig(sudden_drift_threshold=-0.1)

    def test_invalid_recovery_window(self):
        """Test validation of recovery_window."""
        with pytest.raises(ValueError, match="recovery_window must be at least 1"):
            CoherenceTrackerConfig(recovery_window=0)

    def test_invalid_min_turns_for_trend(self):
        """Test validation of min_turns_for_trend."""
        with pytest.raises(ValueError, match="min_turns_for_trend must be at least 2"):
            CoherenceTrackerConfig(min_turns_for_trend=1)


# ============================================
# TurnCoherence Tests
# ============================================


class TestTurnCoherence:
    """Tests for TurnCoherence dataclass."""

    def test_basic_creation(self):
        """Test basic TurnCoherence creation."""
        turn = TurnCoherence(
            turn_id="turn_1",
            turn_number=1,
            coherence_score=0.8,
            drift_score=0.2,
        )
        assert turn.turn_id == "turn_1"
        assert turn.turn_number == 1
        assert turn.coherence_score == 0.8
        assert turn.drift_score == 0.2
        assert turn.drift_type is None
        assert turn.topic_match == 1.0
        assert turn.intent_match == 1.0

    def test_with_drift_type(self):
        """Test TurnCoherence with drift type."""
        turn = TurnCoherence(
            turn_id="turn_2",
            turn_number=2,
            coherence_score=0.4,
            drift_score=0.6,
            drift_type=DriftType.SCOPE_EXPANSION,
        )
        assert turn.drift_type == DriftType.SCOPE_EXPANSION

    def test_invalid_coherence_score(self):
        """Test validation of coherence_score."""
        with pytest.raises(ValueError, match="coherence_score must be between"):
            TurnCoherence(
                turn_id="turn_1",
                turn_number=1,
                coherence_score=1.5,
                drift_score=0.2,
            )

    def test_invalid_drift_score(self):
        """Test validation of drift_score."""
        with pytest.raises(ValueError, match="drift_score must be between"):
            TurnCoherence(
                turn_id="turn_1",
                turn_number=1,
                coherence_score=0.8,
                drift_score=-0.1,
            )

    def test_invalid_topic_match(self):
        """Test validation of topic_match."""
        with pytest.raises(ValueError, match="topic_match must be between"):
            TurnCoherence(
                turn_id="turn_1",
                turn_number=1,
                coherence_score=0.8,
                drift_score=0.2,
                topic_match=1.5,
            )

    def test_invalid_intent_match(self):
        """Test validation of intent_match."""
        with pytest.raises(ValueError, match="intent_match must be between"):
            TurnCoherence(
                turn_id="turn_1",
                turn_number=1,
                coherence_score=0.8,
                drift_score=0.2,
                intent_match=-0.1,
            )


# ============================================
# CoherenceMetrics Tests
# ============================================


class TestCoherenceMetrics:
    """Tests for CoherenceMetrics dataclass."""

    def test_basic_creation(self):
        """Test basic CoherenceMetrics creation."""
        metrics = CoherenceMetrics(
            overall_coherence=0.8,
            topic_consistency=0.9,
            intent_stability=0.85,
            accumulated_drift=0.5,
            average_drift=0.1,
            drift_trend=DriftTrend.STABLE,
            coherence_trend=CoherenceTrend.STABLE,
            turns_since_drift=5,
            turns_in_recovery=0,
            volatility=0.05,
        )
        assert metrics.overall_coherence == 0.8
        assert metrics.drift_trend == DriftTrend.STABLE

    def test_is_healthy_true(self):
        """Test is_healthy property when healthy."""
        metrics = CoherenceMetrics(
            overall_coherence=0.8,
            topic_consistency=0.9,
            intent_stability=0.85,
            accumulated_drift=0.5,
            average_drift=0.1,
            drift_trend=DriftTrend.STABLE,
            coherence_trend=CoherenceTrend.STABLE,
            turns_since_drift=5,
            turns_in_recovery=0,
            volatility=0.05,
        )
        assert metrics.is_healthy is True

    def test_is_healthy_false_low_coherence(self):
        """Test is_healthy property with low coherence."""
        metrics = CoherenceMetrics(
            overall_coherence=0.4,
            topic_consistency=0.5,
            intent_stability=0.45,
            accumulated_drift=1.5,
            average_drift=0.3,
            drift_trend=DriftTrend.STABLE,
            coherence_trend=CoherenceTrend.STABLE,
            turns_since_drift=2,
            turns_in_recovery=0,
            volatility=0.1,
        )
        assert metrics.is_healthy is False

    def test_is_healthy_false_degrading(self):
        """Test is_healthy property with degrading trend."""
        metrics = CoherenceMetrics(
            overall_coherence=0.7,
            topic_consistency=0.8,
            intent_stability=0.75,
            accumulated_drift=0.8,
            average_drift=0.2,
            drift_trend=DriftTrend.STABLE,
            coherence_trend=CoherenceTrend.DEGRADING,
            turns_since_drift=3,
            turns_in_recovery=0,
            volatility=0.1,
        )
        assert metrics.is_healthy is False

    def test_is_healthy_false_sudden_drift(self):
        """Test is_healthy property with sudden drift."""
        metrics = CoherenceMetrics(
            overall_coherence=0.7,
            topic_consistency=0.8,
            intent_stability=0.75,
            accumulated_drift=0.8,
            average_drift=0.2,
            drift_trend=DriftTrend.SUDDEN,
            coherence_trend=CoherenceTrend.STABLE,
            turns_since_drift=0,
            turns_in_recovery=1,
            volatility=0.1,
        )
        assert metrics.is_healthy is False

    def test_needs_attention_true(self):
        """Test needs_attention property when attention needed."""
        metrics = CoherenceMetrics(
            overall_coherence=0.4,
            topic_consistency=0.5,
            intent_stability=0.45,
            accumulated_drift=2.0,
            average_drift=0.4,
            drift_trend=DriftTrend.GRADUAL,
            coherence_trend=CoherenceTrend.DEGRADING,
            turns_since_drift=1,
            turns_in_recovery=2,
            volatility=0.4,
        )
        assert metrics.needs_attention is True

    def test_needs_attention_false(self):
        """Test needs_attention property when no attention needed."""
        metrics = CoherenceMetrics(
            overall_coherence=0.9,
            topic_consistency=0.95,
            intent_stability=0.92,
            accumulated_drift=0.2,
            average_drift=0.05,
            drift_trend=DriftTrend.STABLE,
            coherence_trend=CoherenceTrend.STABLE,
            turns_since_drift=10,
            turns_in_recovery=0,
            volatility=0.02,
        )
        assert metrics.needs_attention is False

    def test_invalid_overall_coherence(self):
        """Test validation of overall_coherence."""
        with pytest.raises(ValueError, match="overall_coherence must be between"):
            CoherenceMetrics(
                overall_coherence=1.5,
                topic_consistency=0.9,
                intent_stability=0.85,
                accumulated_drift=0.5,
                average_drift=0.1,
                drift_trend=DriftTrend.STABLE,
                coherence_trend=CoherenceTrend.STABLE,
                turns_since_drift=5,
                turns_in_recovery=0,
                volatility=0.05,
            )


# ============================================
# ContextResetTrigger Tests
# ============================================


class TestContextResetTrigger:
    """Tests for ContextResetTrigger dataclass."""

    def test_not_triggered(self):
        """Test not triggered state."""
        trigger = ContextResetTrigger(triggered=False)
        assert trigger.triggered is False
        assert trigger.reason is None
        assert trigger.severity == 0.0

    def test_triggered_with_reason(self):
        """Test triggered state with reason."""
        trigger = ContextResetTrigger(
            triggered=True,
            reason=ContextResetReason.ACCUMULATED_DRIFT,
            severity=0.8,
            accumulated_drift=2.0,
            coherence_at_trigger=0.4,
            turns_without_recovery=5,
            recommendation="Reset context due to accumulated drift",
        )
        assert trigger.triggered is True
        assert trigger.reason == ContextResetReason.ACCUMULATED_DRIFT
        assert trigger.severity == 0.8

    def test_invalid_severity(self):
        """Test validation of severity."""
        with pytest.raises(ValueError, match="severity must be between"):
            ContextResetTrigger(triggered=True, severity=1.5)


# ============================================
# ConversationCoherenceTracker Tests
# ============================================


class TestConversationCoherenceTrackerInit:
    """Tests for ConversationCoherenceTracker initialization."""

    def test_default_init(self):
        """Test default initialization."""
        tracker = ConversationCoherenceTracker()
        assert tracker.config.window_size == 5
        assert tracker.turn_count == 0
        assert tracker.drift_event_count == 0
        assert tracker.accumulated_drift == 0.0
        assert tracker.in_recovery is False

    def test_custom_config(self):
        """Test initialization with custom config."""
        config = CoherenceTrackerConfig(window_size=10)
        tracker = ConversationCoherenceTracker(config=config)
        assert tracker.config.window_size == 10


class TestAddDriftScore:
    """Tests for add_drift_score method."""

    def test_add_single_score(self):
        """Test adding a single drift score."""
        tracker = ConversationCoherenceTracker()
        tracker.add_drift_score(0.2)
        assert tracker.accumulated_drift == 0.2
        assert len(tracker.drift_scores) == 1

    def test_add_multiple_scores(self):
        """Test adding multiple drift scores."""
        tracker = ConversationCoherenceTracker()
        tracker.add_drift_score(0.1)
        tracker.add_drift_score(0.2)
        tracker.add_drift_score(0.15)
        assert tracker.accumulated_drift == pytest.approx(0.45)
        assert len(tracker.drift_scores) == 3

    def test_add_high_score_triggers_recovery(self):
        """Test that high drift score triggers recovery mode."""
        tracker = ConversationCoherenceTracker()
        tracker.add_drift_score(0.6)  # Above sudden_drift_threshold
        assert tracker.in_recovery is True
        assert len(tracker.drift_events) == 1

    def test_invalid_score(self):
        """Test validation of drift score."""
        tracker = ConversationCoherenceTracker()
        with pytest.raises(ValueError, match="score must be between"):
            tracker.add_drift_score(1.5)

    def test_add_score_with_drift_type(self):
        """Test adding score with drift type."""
        tracker = ConversationCoherenceTracker()
        tracker.add_drift_score(0.6, DriftType.DOMAIN_SHIFT)
        assert tracker.drift_events[0].drift_type == DriftType.DOMAIN_SHIFT


class TestAddTurn:
    """Tests for add_turn method."""

    def test_add_turn_no_drift(self):
        """Test adding turn without drift."""
        tracker = ConversationCoherenceTracker()
        turn = DriftConversationTurn(
            turn_id="turn_1",
            turn_number=1,
            user_input="Hello",
            timestamp="2024-01-01T00:00:00Z",
            detected_intent="greeting",
        )
        result = tracker.add_turn(turn)
        assert result.coherence_score == 1.0
        assert result.drift_score == 0.0
        assert tracker.initial_topic == "greeting"
        assert tracker.current_topic == "greeting"

    def test_add_turn_with_drift(self):
        """Test adding turn with drift analysis."""
        tracker = ConversationCoherenceTracker()
        drift_analysis = DriftAnalysis(
            current_input="Tell me about philosophy",
            drift_score=0.6,
            drift_type=DriftType.ABSTRACTION_CLIMB,
            confidence=0.8,
            semantic_distance=0.7,
            graceful_response="Let me redirect you",
        )
        turn = DriftConversationTurn(
            turn_id="turn_1",
            turn_number=1,
            user_input="Tell me about philosophy",
            timestamp="2024-01-01T00:00:00Z",
            drift_analysis=drift_analysis,
        )
        result = tracker.add_turn(turn)
        assert result.coherence_score == pytest.approx(0.4)
        assert result.drift_score == 0.6
        assert result.drift_type == DriftType.ABSTRACTION_CLIMB
        assert tracker.in_recovery is True

    def test_add_multiple_turns(self):
        """Test adding multiple turns."""
        tracker = ConversationCoherenceTracker()
        for i in range(5):
            turn = DriftConversationTurn(
                turn_id=f"turn_{i}",
                turn_number=i,
                user_input=f"Message {i}",
                timestamp="2024-01-01T00:00:00Z",
                detected_intent="greeting",
            )
            tracker.add_turn(turn)
        assert tracker.turn_count == 5


class TestAddDriftAnalysis:
    """Tests for add_drift_analysis method."""

    def test_add_drift_analysis(self):
        """Test adding drift analysis directly."""
        tracker = ConversationCoherenceTracker()
        analysis = DriftAnalysis(
            current_input="Test input",
            drift_score=0.3,
            drift_type=DriftType.SCOPE_EXPANSION,
            confidence=0.9,
            semantic_distance=0.4,
            graceful_response="Redirect",
        )
        tracker.add_drift_analysis(analysis)
        assert tracker.accumulated_drift == 0.3


class TestGetCoherenceMetrics:
    """Tests for get_coherence_metrics method."""

    def test_empty_tracker(self):
        """Test metrics for empty tracker."""
        tracker = ConversationCoherenceTracker()
        metrics = tracker.get_coherence_metrics()
        assert metrics.overall_coherence == 1.0
        assert metrics.drift_trend == DriftTrend.STABLE
        assert metrics.coherence_trend == CoherenceTrend.STABLE

    def test_metrics_after_scores(self):
        """Test metrics after adding scores."""
        tracker = ConversationCoherenceTracker()
        for _ in range(5):
            tracker.add_drift_score(0.1)
        metrics = tracker.get_coherence_metrics()
        assert metrics.overall_coherence == pytest.approx(0.9)
        assert metrics.average_drift == pytest.approx(0.1)
        assert metrics.accumulated_drift == pytest.approx(0.5)

    def test_metrics_volatility(self):
        """Test volatility calculation."""
        tracker = ConversationCoherenceTracker()
        # Add alternating scores to create volatility
        tracker.add_drift_score(0.1)
        tracker.add_drift_score(0.5)
        tracker.add_drift_score(0.1)
        tracker.add_drift_score(0.5)
        metrics = tracker.get_coherence_metrics()
        assert metrics.volatility > 0.1  # Should have noticeable volatility


class TestDriftTrendDetection:
    """Tests for drift trend detection."""

    def test_stable_trend(self):
        """Test detection of stable trend."""
        tracker = ConversationCoherenceTracker()
        for _ in range(5):
            tracker.add_drift_score(0.1)
        metrics = tracker.get_coherence_metrics()
        assert metrics.drift_trend == DriftTrend.STABLE

    def test_sudden_drift(self):
        """Test detection of sudden drift."""
        tracker = ConversationCoherenceTracker()
        tracker.add_drift_score(0.1)
        tracker.add_drift_score(0.1)
        tracker.add_drift_score(0.7)  # Sudden jump
        metrics = tracker.get_coherence_metrics()
        assert metrics.drift_trend == DriftTrend.SUDDEN

    def test_gradual_drift(self):
        """Test detection of gradual drift."""
        tracker = ConversationCoherenceTracker()
        tracker.add_drift_score(0.1)
        tracker.add_drift_score(0.15)
        tracker.add_drift_score(0.2)
        tracker.add_drift_score(0.35)
        tracker.add_drift_score(0.4)
        tracker.add_drift_score(0.45)
        metrics = tracker.get_coherence_metrics()
        assert metrics.drift_trend == DriftTrend.GRADUAL

    def test_returning_trend(self):
        """Test detection of returning trend."""
        tracker = ConversationCoherenceTracker()
        # Start with drift
        tracker.add_drift_score(0.5)
        tracker.add_drift_score(0.6)
        tracker.add_drift_score(0.5)
        # Then recover
        tracker.add_drift_score(0.1)
        tracker.add_drift_score(0.1)
        tracker.add_drift_score(0.05)
        metrics = tracker.get_coherence_metrics()
        assert metrics.drift_trend == DriftTrend.RETURNING

    def test_oscillating_trend(self):
        """Test detection of oscillating trend."""
        tracker = ConversationCoherenceTracker()
        tracker.add_drift_score(0.1)
        tracker.add_drift_score(0.4)
        tracker.add_drift_score(0.1)
        tracker.add_drift_score(0.4)
        tracker.add_drift_score(0.1)
        tracker.add_drift_score(0.4)
        metrics = tracker.get_coherence_metrics()
        assert metrics.drift_trend == DriftTrend.OSCILLATING


class TestCoherenceTrendDetection:
    """Tests for coherence trend detection."""

    def test_stable_coherence(self):
        """Test detection of stable coherence."""
        tracker = ConversationCoherenceTracker()
        for _ in range(5):
            tracker.add_drift_score(0.2)
        metrics = tracker.get_coherence_metrics()
        assert metrics.coherence_trend == CoherenceTrend.STABLE

    def test_improving_coherence(self):
        """Test detection of improving coherence."""
        tracker = ConversationCoherenceTracker()
        tracker.add_drift_score(0.5)
        tracker.add_drift_score(0.4)
        tracker.add_drift_score(0.3)
        tracker.add_drift_score(0.2)
        tracker.add_drift_score(0.1)
        tracker.add_drift_score(0.1)
        metrics = tracker.get_coherence_metrics()
        assert metrics.coherence_trend == CoherenceTrend.IMPROVING

    def test_degrading_coherence(self):
        """Test detection of degrading coherence."""
        tracker = ConversationCoherenceTracker()
        tracker.add_drift_score(0.1)
        tracker.add_drift_score(0.2)
        tracker.add_drift_score(0.3)
        tracker.add_drift_score(0.4)
        tracker.add_drift_score(0.5)
        tracker.add_drift_score(0.5)
        metrics = tracker.get_coherence_metrics()
        assert metrics.coherence_trend == CoherenceTrend.DEGRADING

    def test_volatile_coherence(self):
        """Test detection of volatile coherence."""
        tracker = ConversationCoherenceTracker()
        tracker.add_drift_score(0.0)
        tracker.add_drift_score(0.6)
        tracker.add_drift_score(0.0)
        tracker.add_drift_score(0.6)
        metrics = tracker.get_coherence_metrics()
        assert metrics.coherence_trend == CoherenceTrend.VOLATILE


class TestContextResetTriggers:
    """Tests for context reset trigger detection."""

    def test_no_reset_needed(self):
        """Test when no reset is needed."""
        tracker = ConversationCoherenceTracker()
        for _ in range(3):
            tracker.add_drift_score(0.1)
        trigger = tracker.should_reset_context()
        assert trigger.triggered is False

    def test_accumulated_drift_trigger(self):
        """Test reset triggered by accumulated drift."""
        config = CoherenceTrackerConfig(drift_accumulation_threshold=1.0)
        tracker = ConversationCoherenceTracker(config=config)
        # Add enough drift to exceed threshold
        tracker.add_drift_score(0.4)
        tracker.add_drift_score(0.4)
        tracker.add_drift_score(0.4)
        trigger = tracker.should_reset_context()
        assert trigger.triggered is True
        assert trigger.reason == ContextResetReason.ACCUMULATED_DRIFT

    def test_coherence_collapse_trigger(self):
        """Test reset triggered by coherence collapse."""
        # Use high threshold so accumulated drift doesn't trigger first
        config = CoherenceTrackerConfig(
            coherence_collapse_threshold=0.4,
            drift_accumulation_threshold=10.0,  # Very high so it doesn't trigger first
        )
        tracker = ConversationCoherenceTracker(config=config)
        # Add high drift scores to collapse coherence
        for _ in range(5):
            tracker.add_drift_score(0.7)
        trigger = tracker.should_reset_context()
        assert trigger.triggered is True
        assert trigger.reason == ContextResetReason.COHERENCE_COLLAPSE

    def test_repeated_drift_trigger(self):
        """Test reset triggered by repeated drift type."""
        tracker = ConversationCoherenceTracker()
        # Add multiple drift events of same type
        for _ in range(3):
            tracker.add_drift_score(0.6, DriftType.DOMAIN_SHIFT)
        trigger = tracker.should_reset_context()
        assert trigger.triggered is True
        assert trigger.reason == ContextResetReason.REPEATED_DRIFT

    def test_turn_limit_trigger(self):
        """Test reset triggered by turn limit in recovery."""
        config = CoherenceTrackerConfig(
            recovery_window=2,
            drift_accumulation_threshold=10.0,  # High so it doesn't trigger first
            coherence_collapse_threshold=0.1,  # Low so it doesn't trigger first
        )
        tracker = ConversationCoherenceTracker(config=config)
        # Enter recovery mode with moderate drift
        tracker.add_drift_score(0.6)
        # Stay in recovery too long with moderate drift (not low enough to recover)
        for _ in range(6):
            tracker.add_drift_score(0.35)
        trigger = tracker.should_reset_context()
        assert trigger.triggered is True
        assert trigger.reason == ContextResetReason.TURN_LIMIT

    def test_auto_reset_disabled(self):
        """Test that auto reset can be disabled."""
        config = CoherenceTrackerConfig(
            enable_auto_reset=False,
            drift_accumulation_threshold=1.0,
        )
        tracker = ConversationCoherenceTracker(config=config)
        # Add enough drift to normally trigger
        tracker.add_drift_score(0.5)
        tracker.add_drift_score(0.5)
        tracker.add_drift_score(0.5)
        trigger = tracker.should_reset_context()
        assert trigger.triggered is False


class TestReset:
    """Tests for reset method."""

    def test_reset_clears_state(self):
        """Test that reset clears all state."""
        tracker = ConversationCoherenceTracker()
        # Add some state
        tracker.add_drift_score(0.3)
        tracker.add_drift_score(0.6)
        turn = DriftConversationTurn(
            turn_id="turn_1",
            turn_number=1,
            user_input="Test",
            timestamp="2024-01-01T00:00:00Z",
            detected_intent="test",
        )
        tracker.add_turn(turn)

        # Reset
        tracker.reset()

        assert tracker.turn_count == 0
        assert tracker.drift_event_count == 0
        assert tracker.accumulated_drift == 0.0
        assert tracker.in_recovery is False
        assert tracker.initial_topic is None
        assert tracker.current_topic is None
        assert len(tracker.drift_scores) == 0


class TestToCoherenceAnalysis:
    """Tests for to_coherence_analysis method."""

    def test_conversion(self):
        """Test conversion to CoherenceAnalysis."""
        tracker = ConversationCoherenceTracker()
        for _ in range(3):
            tracker.add_drift_score(0.1)
        analysis = tracker.to_coherence_analysis()
        assert isinstance(analysis, CoherenceAnalysis)
        assert analysis.coherence_score == pytest.approx(0.9)
        assert analysis.coherence_trend == CoherenceTrend.STABLE

    def test_conversion_with_warnings(self):
        """Test conversion includes warnings when needed."""
        tracker = ConversationCoherenceTracker()
        tracker.add_drift_score(0.7)  # High drift to trigger recovery
        analysis = tracker.to_coherence_analysis()
        assert "Currently in recovery mode" in analysis.warnings
        assert "Coherence needs attention" in analysis.warnings


class TestRecoveryRate:
    """Tests for recovery_rate property."""

    def test_full_recovery_rate(self):
        """Test 100% recovery rate."""
        tracker = ConversationCoherenceTracker()
        assert tracker.recovery_rate == 1.0  # No events = perfect

    def test_partial_recovery_rate(self):
        """Test partial recovery rate calculation."""
        config = CoherenceTrackerConfig(recovery_window=2)  # Small window for faster recovery
        tracker = ConversationCoherenceTracker(config=config)
        # Enter recovery mode
        tracker.add_drift_score(0.6)
        # Simulate successful recovery with enough low-drift turns
        for _ in range(5):
            tracker.add_drift_score(0.1)
        # Rate should reflect successful recovery
        assert tracker.recovery_rate == 1.0

    def test_no_recovery(self):
        """Test when no recovery occurred."""
        tracker = ConversationCoherenceTracker()
        # Multiple drift events without recovery
        tracker.add_drift_score(0.6)
        tracker.add_drift_score(0.6)
        tracker.add_drift_score(0.6)
        assert tracker.recovery_rate == 0.0


class TestSlidingWindow:
    """Tests for sliding window behavior."""

    def test_window_size_limit(self):
        """Test that window respects size limit."""
        config = CoherenceTrackerConfig(window_size=3)
        tracker = ConversationCoherenceTracker(config=config)
        # Add more scores than window size
        for i in range(5):
            tracker.add_drift_score(0.1 * (i + 1))
        # Should only have last 3 scores
        assert len(tracker.drift_scores) == 3

    def test_window_values(self):
        """Test that window contains correct values."""
        config = CoherenceTrackerConfig(window_size=3)
        tracker = ConversationCoherenceTracker(config=config)
        tracker.add_drift_score(0.1)
        tracker.add_drift_score(0.2)
        tracker.add_drift_score(0.3)
        tracker.add_drift_score(0.4)  # Should push out 0.1
        scores = list(tracker.drift_scores)
        assert scores == pytest.approx([0.2, 0.3, 0.4])


class TestEdgeCases:
    """Tests for edge cases."""

    def test_single_turn(self):
        """Test with single turn."""
        tracker = ConversationCoherenceTracker()
        tracker.add_drift_score(0.3)
        metrics = tracker.get_coherence_metrics()
        assert metrics.overall_coherence == pytest.approx(0.7)
        assert metrics.drift_trend == DriftTrend.STABLE

    def test_all_zero_drift(self):
        """Test with no drift at all."""
        tracker = ConversationCoherenceTracker()
        for _ in range(10):
            tracker.add_drift_score(0.0)
        metrics = tracker.get_coherence_metrics()
        assert metrics.overall_coherence == 1.0
        assert metrics.accumulated_drift == 0.0
        assert metrics.drift_trend == DriftTrend.STABLE

    def test_all_max_drift(self):
        """Test with maximum drift on all turns."""
        tracker = ConversationCoherenceTracker()
        for _ in range(5):
            tracker.add_drift_score(1.0)
        metrics = tracker.get_coherence_metrics()
        assert metrics.overall_coherence == 0.0
        assert metrics.accumulated_drift == 5.0

    def test_topic_tracking(self):
        """Test topic tracking across turns."""
        tracker = ConversationCoherenceTracker()
        turn1 = DriftConversationTurn(
            turn_id="t1",
            turn_number=1,
            user_input="Hello",
            timestamp="2024-01-01T00:00:00Z",
            detected_intent="greeting",
        )
        turn2 = DriftConversationTurn(
            turn_id="t2",
            turn_number=2,
            user_input="What's the weather?",
            timestamp="2024-01-01T00:01:00Z",
            detected_intent="weather",
        )
        tracker.add_turn(turn1)
        tracker.add_turn(turn2)
        assert tracker.initial_topic == "greeting"
        assert tracker.current_topic == "weather"


# ============================================
# Enum Tests
# ============================================


class TestEnums:
    """Tests for enum values."""

    def test_drift_trend_values(self):
        """Test DriftTrend enum values."""
        assert DriftTrend.STABLE.value == "stable"
        assert DriftTrend.GRADUAL.value == "gradual"
        assert DriftTrend.SUDDEN.value == "sudden"
        assert DriftTrend.RETURNING.value == "returning"
        assert DriftTrend.OSCILLATING.value == "oscillating"

    def test_context_reset_reason_values(self):
        """Test ContextResetReason enum values."""
        assert ContextResetReason.ACCUMULATED_DRIFT.value == "accumulated_drift"
        assert ContextResetReason.COHERENCE_COLLAPSE.value == "coherence_collapse"
        assert ContextResetReason.TOPIC_ABANDONMENT.value == "topic_abandonment"
        assert ContextResetReason.USER_REQUEST.value == "user_request"
        assert ContextResetReason.TURN_LIMIT.value == "turn_limit"
        assert ContextResetReason.REPEATED_DRIFT.value == "repeated_drift"
