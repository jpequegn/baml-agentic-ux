"""
Tests for the Level Transition Logic.
Issue #46 - Phase 2: Adaptive Interface Personalization

Tests cover:
- Level-up transitions (success streaks, rates, shortcut adoption)
- Level-down transitions (errors, help-seeking, frustration)
- Cooldown periods
- Rollback capability
- User notifications
- Policy configuration
"""

import uuid
from datetime import datetime

import pytest

from src.lui_simulator.transitions import (
    ExpertiseLevel,
    TransitionDecision,
    TransitionDirection,
    TransitionManager,
    TransitionPolicy,
)
from src.lui_simulator.metrics import (
    FrustrationSignals,
    InteractionOutcome,
    MetricsWindow,
    SignalSeverity,
    TrendDirection,
)


# ============================================
# Fixtures
# ============================================


def create_metrics_window(
    success_rate: float = 0.8,
    help_rate: float = 0.1,
    shortcut_rate: float = 0.3,
    interaction_count: int = 20,
) -> MetricsWindow:
    """Create a metrics window with specified values."""
    now = datetime.now().isoformat()
    return MetricsWindow(
        window_id=str(uuid.uuid4()),
        window_start=now,
        window_end=now,
        interaction_count=interaction_count,
        success_rate=success_rate,
        partial_success_rate=0.1,
        failure_rate=1 - success_rate - 0.1,
        abandonment_rate=0.0,
        help_rate=help_rate,
        shortcut_rate=shortcut_rate,
        error_rate=0.2,
        disambiguation_rate=0.1,
        avg_completion_time_ms=500.0,
        median_completion_time_ms=450.0,
        p95_completion_time_ms=1000.0,
        avg_input_length=50.0,
        avg_parameters_provided=2.0,
        avg_retries=0.2,
        success_trend=TrendDirection.STABLE,
        efficiency_trend=TrendDirection.STABLE,
        engagement_trend=TrendDirection.STABLE,
    )


def create_frustration_signals(
    is_frustrated: bool = False,
    confidence: float = 0.5,
    severity: SignalSeverity = SignalSeverity.LOW,
) -> FrustrationSignals:
    """Create frustration signals with specified values."""
    return FrustrationSignals(
        is_frustrated=is_frustrated,
        confidence=confidence,
        severity=severity,
        signals=["consecutive_errors", "high_help_rate"] if is_frustrated else [],
        trigger_events=["error_streak"] if is_frustrated else [],
        recommendation="Provide more guidance" if is_frustrated else None,
    )


# ============================================
# TransitionPolicy Tests
# ============================================


class TestTransitionPolicy:
    """Tests for TransitionPolicy configuration."""

    def test_default_policy(self):
        """Test default policy values."""
        policy = TransitionPolicy()

        assert policy.min_consecutive_successes == 5
        assert policy.min_success_rate == 0.8
        assert policy.min_interactions_at_level == 10
        assert policy.max_consecutive_errors == 3
        assert policy.max_help_rate == 0.4
        assert policy.transition_cooldown_hours == 24
        assert policy.gradual_transition is True
        assert policy.enable_rollback is True
        assert policy.rollback_window_hours == 48

    def test_custom_policy(self):
        """Test custom policy values."""
        policy = TransitionPolicy(
            min_consecutive_successes=10,
            min_success_rate=0.9,
            max_consecutive_errors=5,
            transition_cooldown_hours=48,
        )

        assert policy.min_consecutive_successes == 10
        assert policy.min_success_rate == 0.9
        assert policy.max_consecutive_errors == 5
        assert policy.transition_cooldown_hours == 48

    def test_invalid_consecutive_successes(self):
        """Test that invalid consecutive successes raises error."""
        with pytest.raises(ValueError, match="min_consecutive_successes"):
            TransitionPolicy(min_consecutive_successes=0)

    def test_invalid_success_rate(self):
        """Test that invalid success rate raises error."""
        with pytest.raises(ValueError, match="min_success_rate"):
            TransitionPolicy(min_success_rate=1.5)

    def test_invalid_help_rate(self):
        """Test that invalid help rate raises error."""
        with pytest.raises(ValueError, match="max_help_rate"):
            TransitionPolicy(max_help_rate=-0.1)


# ============================================
# TransitionManager Initialization Tests
# ============================================


class TestTransitionManagerInit:
    """Tests for TransitionManager initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        manager = TransitionManager()

        assert manager.policy.min_consecutive_successes == 5
        assert len(manager.transition_history) == 0
        assert manager.last_transition is None

    def test_initialization_with_policy(self):
        """Test initialization with custom policy."""
        policy = TransitionPolicy(min_consecutive_successes=10)
        manager = TransitionManager(policy=policy)

        assert manager.policy.min_consecutive_successes == 10

    def test_reset_clears_state(self):
        """Test that reset clears all state."""
        manager = TransitionManager()

        # Record some interactions
        for _ in range(10):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        manager.reset()

        stats = manager.get_transition_stats()
        assert stats["consecutive_successes"] == 0
        assert stats["interactions_at_current_level"] == 0


# ============================================
# Interaction Recording Tests
# ============================================


class TestInteractionRecording:
    """Tests for recording interactions."""

    def test_success_increments_streak(self):
        """Test that success increments consecutive success counter."""
        manager = TransitionManager()

        for i in range(5):
            manager.record_interaction(InteractionOutcome.SUCCESS)
            stats = manager.get_transition_stats()
            assert stats["consecutive_successes"] == i + 1
            assert stats["consecutive_errors"] == 0

    def test_failure_increments_error_streak(self):
        """Test that failure increments consecutive error counter."""
        manager = TransitionManager()

        for i in range(3):
            manager.record_interaction(InteractionOutcome.FAILURE)
            stats = manager.get_transition_stats()
            assert stats["consecutive_errors"] == i + 1
            assert stats["consecutive_successes"] == 0

    def test_success_resets_error_streak(self):
        """Test that success resets error streak."""
        manager = TransitionManager()

        manager.record_interaction(InteractionOutcome.FAILURE)
        manager.record_interaction(InteractionOutcome.FAILURE)
        manager.record_interaction(InteractionOutcome.SUCCESS)

        stats = manager.get_transition_stats()
        assert stats["consecutive_errors"] == 0
        assert stats["consecutive_successes"] == 1

    def test_failure_resets_success_streak(self):
        """Test that failure resets success streak."""
        manager = TransitionManager()

        manager.record_interaction(InteractionOutcome.SUCCESS)
        manager.record_interaction(InteractionOutcome.SUCCESS)
        manager.record_interaction(InteractionOutcome.FAILURE)

        stats = manager.get_transition_stats()
        assert stats["consecutive_successes"] == 0
        assert stats["consecutive_errors"] == 1

    def test_partial_success_resets_error_streak(self):
        """Test that partial success resets error streak."""
        manager = TransitionManager()

        manager.record_interaction(InteractionOutcome.FAILURE)
        manager.record_interaction(InteractionOutcome.PARTIAL_SUCCESS)

        stats = manager.get_transition_stats()
        assert stats["consecutive_errors"] == 0

    def test_help_escalation_resets_success_streak(self):
        """Test that help escalation resets success streak."""
        manager = TransitionManager()

        manager.record_interaction(InteractionOutcome.SUCCESS)
        manager.record_interaction(InteractionOutcome.SUCCESS)
        manager.record_interaction(InteractionOutcome.HELP_ESCALATION)

        stats = manager.get_transition_stats()
        assert stats["consecutive_successes"] == 0


# ============================================
# Level Up Tests
# ============================================


class TestLevelUp:
    """Tests for level-up transitions."""

    def test_level_up_with_all_criteria_met(self):
        """Test level up when all criteria are met."""
        manager = TransitionManager()

        # Build success streak
        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(
            success_rate=0.9,
            help_rate=0.05,
            shortcut_rate=0.4,
            interaction_count=20,
        )

        decision = manager.check_level_up(
            current_level=ExpertiseLevel.BEGINNER,
            metrics_window=metrics,
        )

        assert decision.should_transition is True
        assert decision.direction == TransitionDirection.LEVEL_UP
        assert decision.from_level == ExpertiseLevel.BEGINNER
        assert decision.to_level == ExpertiseLevel.INTERMEDIATE
        assert decision.user_notification is not None

    def test_level_up_blocked_by_low_success_rate(self):
        """Test level up blocked by low success rate."""
        manager = TransitionManager()

        # Only 3 consecutive successes (not enough for streak criterion)
        for _ in range(10):
            manager.record_interaction(InteractionOutcome.SUCCESS)
        for _ in range(2):
            manager.record_interaction(InteractionOutcome.FAILURE)  # Break streak
        for _ in range(3):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(
            success_rate=0.5,  # Too low
            help_rate=0.05,
            shortcut_rate=0.4,
        )

        decision = manager.check_level_up(
            current_level=ExpertiseLevel.BEGINNER,
            metrics_window=metrics,
        )

        # With only 3 consecutive successes and low success rate, shouldn't transition
        # Criteria: streak(no) + success_rate(no) + help_rate(yes) + shortcuts(yes) = 2/4
        assert decision.should_transition is False

    def test_level_up_blocked_by_high_help_rate(self):
        """Test level up blocked by high help rate."""
        manager = TransitionManager()

        # Only 3 consecutive successes (not enough for streak criterion)
        for _ in range(10):
            manager.record_interaction(InteractionOutcome.SUCCESS)
        for _ in range(2):
            manager.record_interaction(InteractionOutcome.FAILURE)
        for _ in range(3):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(
            success_rate=0.7,  # Below threshold
            help_rate=0.3,  # Too high (> 10%)
            shortcut_rate=0.4,
        )

        decision = manager.check_level_up(
            current_level=ExpertiseLevel.BEGINNER,
            metrics_window=metrics,
        )

        # Criteria: streak(no) + success_rate(no) + help_rate(no) + shortcuts(yes) = 1/4
        assert decision.should_transition is False

    def test_level_up_blocked_by_insufficient_interactions(self):
        """Test level up blocked by insufficient interactions at level."""
        manager = TransitionManager()

        # Only 5 interactions (need 10)
        for _ in range(5):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9)

        decision = manager.check_level_up(
            current_level=ExpertiseLevel.BEGINNER,
            metrics_window=metrics,
        )

        assert decision.should_transition is False
        assert "interactions at current level" in decision.rationale.lower()

    def test_level_up_blocked_at_expert_level(self):
        """Test that level up is blocked at expert level."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        decision = manager.check_level_up(
            current_level=ExpertiseLevel.EXPERT,
        )

        assert decision.should_transition is False
        assert "maximum" in decision.rationale.lower()

    def test_level_up_blocked_by_cooldown(self):
        """Test that level up is blocked during cooldown."""
        manager = TransitionManager()

        # First transition
        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision1 = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)
        manager.execute_transition(decision1)

        # Try again immediately - should be blocked
        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        decision2 = manager.check_level_up(ExpertiseLevel.INTERMEDIATE, metrics)

        assert decision2.should_transition is False
        assert decision2.cooldown_active is True

    def test_gradual_level_up(self):
        """Test that level up is gradual (one level at a time)."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.95, help_rate=0.02)

        # From NOVICE should go to BEGINNER, not skip levels
        decision = manager.check_level_up(ExpertiseLevel.NOVICE, metrics)

        assert decision.to_level == ExpertiseLevel.BEGINNER


# ============================================
# Level Down Tests
# ============================================


class TestLevelDown:
    """Tests for level-down transitions."""

    def test_level_down_on_consecutive_errors(self):
        """Test level down triggered by consecutive errors."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        # Now fail consecutively
        for _ in range(3):
            manager.record_interaction(InteractionOutcome.FAILURE)

        decision = manager.check_level_down(
            current_level=ExpertiseLevel.INTERMEDIATE,
        )

        assert decision.should_transition is True
        assert decision.direction == TransitionDirection.LEVEL_DOWN
        assert decision.to_level == ExpertiseLevel.BEGINNER
        assert "consecutive" in str(decision.evidence).lower()

    def test_level_down_on_high_help_rate(self):
        """Test level down triggered by high help rate."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(
            success_rate=0.5,
            help_rate=0.5,  # > 40% threshold
        )

        decision = manager.check_level_down(
            current_level=ExpertiseLevel.INTERMEDIATE,
            metrics_window=metrics,
        )

        assert decision.should_transition is True
        assert decision.direction == TransitionDirection.LEVEL_DOWN

    def test_level_down_on_frustration(self):
        """Test level down triggered by frustration signals."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        frustration = create_frustration_signals(
            is_frustrated=True,
            confidence=0.8,  # Above threshold
            severity=SignalSeverity.HIGH,
        )

        decision = manager.check_level_down(
            current_level=ExpertiseLevel.INTERMEDIATE,
            frustration_signals=frustration,
        )

        assert decision.should_transition is True
        assert "frustration" in str(decision.evidence).lower()

    def test_level_down_on_user_request(self):
        """Test level down when user explicitly requests help."""
        manager = TransitionManager()

        decision = manager.check_level_down(
            current_level=ExpertiseLevel.INTERMEDIATE,
            user_requested=True,
        )

        assert decision.should_transition is True
        assert decision.confidence == 1.0
        assert "user" in decision.rationale.lower()

    def test_level_down_blocked_at_novice(self):
        """Test that level down is blocked at novice level."""
        manager = TransitionManager()

        for _ in range(3):
            manager.record_interaction(InteractionOutcome.FAILURE)

        decision = manager.check_level_down(
            current_level=ExpertiseLevel.NOVICE,
        )

        assert decision.should_transition is False
        assert "minimum" in decision.rationale.lower()

    def test_level_down_skips_cooldown_for_user_request(self):
        """Test that user-requested level down skips cooldown."""
        manager = TransitionManager()

        # First transition
        for _ in range(3):
            manager.record_interaction(InteractionOutcome.FAILURE)

        decision1 = manager.check_level_down(ExpertiseLevel.INTERMEDIATE)
        if decision1.should_transition:
            manager.execute_transition(decision1)

        # User request should skip cooldown
        decision2 = manager.check_level_down(
            current_level=ExpertiseLevel.BEGINNER,
            user_requested=True,
        )

        # Should not be blocked by cooldown
        assert decision2.should_transition is True
        assert decision2.cooldown_active is False


# ============================================
# Transition Execution Tests
# ============================================


class TestTransitionExecution:
    """Tests for executing transitions."""

    def test_execute_level_up(self):
        """Test executing a level-up transition."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)

        result = manager.execute_transition(decision)

        assert result.success is True
        assert result.previous_level == ExpertiseLevel.BEGINNER
        assert result.new_level == ExpertiseLevel.INTERMEDIATE
        assert result.direction == TransitionDirection.LEVEL_UP
        assert result.rollback_token is not None

    def test_execute_level_down(self):
        """Test executing a level-down transition."""
        manager = TransitionManager()

        for _ in range(3):
            manager.record_interaction(InteractionOutcome.FAILURE)

        decision = manager.check_level_down(ExpertiseLevel.INTERMEDIATE)

        result = manager.execute_transition(decision)

        assert result.success is True
        assert result.previous_level == ExpertiseLevel.INTERMEDIATE
        assert result.new_level == ExpertiseLevel.BEGINNER
        assert result.direction == TransitionDirection.LEVEL_DOWN

    def test_execution_resets_counters(self):
        """Test that executing a transition resets counters."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)
        manager.execute_transition(decision)

        stats = manager.get_transition_stats()
        assert stats["consecutive_successes"] == 0
        assert stats["interactions_at_current_level"] == 0

    def test_execution_updates_history(self):
        """Test that execution updates transition history."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)
        manager.execute_transition(decision)

        assert len(manager.transition_history) == 1
        assert manager.last_transition is not None
        assert manager.last_transition.to_level == ExpertiseLevel.INTERMEDIATE

    def test_cannot_execute_no_transition(self):
        """Test that executing a no-transition decision raises error."""
        manager = TransitionManager()

        decision = TransitionDecision(
            should_transition=False,
            direction=None,
            from_level=ExpertiseLevel.BEGINNER,
            to_level=None,
            confidence=1.0,
            rationale="Test",
        )

        with pytest.raises(ValueError):
            manager.execute_transition(decision)


# ============================================
# Rollback Tests
# ============================================


class TestRollback:
    """Tests for rollback functionality."""

    def test_rollback_with_token(self):
        """Test rollback using rollback token."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)
        result = manager.execute_transition(decision)

        rollback = manager.rollback_transition(rollback_token=result.rollback_token)

        assert rollback.success is True
        assert rollback.restored_level == ExpertiseLevel.BEGINNER

    def test_rollback_latest(self):
        """Test rollback of the latest transition."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)
        manager.execute_transition(decision)

        rollback = manager.rollback_transition()

        assert rollback.success is True
        assert rollback.restored_level == ExpertiseLevel.BEGINNER

    def test_rollback_marks_record(self):
        """Test that rollback marks the transition record."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)
        manager.execute_transition(decision)

        manager.rollback_transition()

        assert manager.last_transition.was_rolled_back is True

    def test_rollback_invalid_token(self):
        """Test rollback with invalid token."""
        manager = TransitionManager()

        rollback = manager.rollback_transition(rollback_token="invalid-token")

        assert rollback.success is False
        assert rollback.reason_failed is not None
        assert "invalid" in rollback.reason_failed.lower() or "expired" in rollback.reason_failed.lower()

    def test_rollback_disabled_by_policy(self):
        """Test rollback when disabled by policy."""
        policy = TransitionPolicy(enable_rollback=False)
        manager = TransitionManager(policy=policy)

        rollback = manager.rollback_transition()

        assert rollback.success is False
        assert "disabled" in rollback.message.lower()

    def test_rollback_already_rolled_back(self):
        """Test rollback of already rolled-back transition."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)
        manager.execute_transition(decision)

        manager.rollback_transition()
        rollback2 = manager.rollback_transition()

        assert rollback2.success is False
        assert "already" in rollback2.reason_failed.lower()

    def test_rollback_no_history(self):
        """Test rollback with no transition history."""
        manager = TransitionManager()

        rollback = manager.rollback_transition()

        assert rollback.success is False
        assert "no transitions" in rollback.message.lower()


# ============================================
# Cooldown Tests
# ============================================


class TestCooldown:
    """Tests for cooldown functionality."""

    def test_cooldown_after_transition(self):
        """Test that cooldown is active after transition."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)
        manager.execute_transition(decision)

        stats = manager.get_transition_stats()
        assert stats["cooldown_active"] is True

    def test_clear_cooldown(self):
        """Test clearing cooldown manually."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)
        manager.execute_transition(decision)

        manager.clear_cooldown()

        stats = manager.get_transition_stats()
        assert stats["cooldown_active"] is False

    def test_custom_cooldown_hours(self):
        """Test custom cooldown duration."""
        policy = TransitionPolicy(transition_cooldown_hours=1)
        manager = TransitionManager(policy=policy)

        assert manager.policy.transition_cooldown_hours == 1


# ============================================
# Notification Tests
# ============================================


class TestNotifications:
    """Tests for user notifications."""

    def test_level_up_notification_beginner_to_intermediate(self):
        """Test level-up notification from beginner to intermediate."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)

        assert decision.user_notification is not None
        assert "shortcut" in decision.user_notification.lower()

    def test_level_up_notification_intermediate_to_advanced(self):
        """Test level-up notification from intermediate to advanced."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.95, help_rate=0.02, shortcut_rate=0.5)
        decision = manager.check_level_up(ExpertiseLevel.INTERMEDIATE, metrics)

        if decision.should_transition:
            assert "concise" in decision.user_notification.lower()

    def test_level_down_notification_supportive(self):
        """Test that level-down notification is supportive."""
        manager = TransitionManager()

        for _ in range(3):
            manager.record_interaction(InteractionOutcome.FAILURE)

        decision = manager.check_level_down(ExpertiseLevel.INTERMEDIATE)

        if decision.should_transition:
            assert decision.notification_tone == "supportive"
            assert "guidance" in decision.user_notification.lower()


# ============================================
# Stats and History Tests
# ============================================


class TestStatsAndHistory:
    """Tests for transition statistics and history."""

    def test_get_transition_stats(self):
        """Test getting transition statistics."""
        manager = TransitionManager()

        for _ in range(10):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        stats = manager.get_transition_stats()

        assert stats["total_transitions"] == 0
        assert stats["consecutive_successes"] == 10
        assert stats["interactions_at_current_level"] == 10

    def test_stats_after_multiple_transitions(self):
        """Test statistics after multiple transitions."""
        manager = TransitionManager()

        # First transition
        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)
        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision1 = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)
        manager.execute_transition(decision1)
        manager.clear_cooldown()

        # Second transition (level down)
        for _ in range(3):
            manager.record_interaction(InteractionOutcome.FAILURE)
        decision2 = manager.check_level_down(ExpertiseLevel.INTERMEDIATE)
        if decision2.should_transition:
            manager.execute_transition(decision2)

        stats = manager.get_transition_stats()

        assert stats["total_transitions"] >= 1
        assert stats["level_ups"] >= 1

    def test_transition_history_order(self):
        """Test that transition history is in correct order."""
        manager = TransitionManager()

        # Multiple transitions
        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)
        manager.execute_transition(decision)

        history = manager.transition_history

        assert len(history) == 1
        assert history[0].from_level == ExpertiseLevel.BEGINNER
        assert history[0].to_level == ExpertiseLevel.INTERMEDIATE


# ============================================
# Edge Cases
# ============================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_all_levels_have_notifications(self):
        """Test that all level transitions have notifications."""
        manager = TransitionManager()

        levels = [
            ExpertiseLevel.NOVICE,
            ExpertiseLevel.BEGINNER,
            ExpertiseLevel.INTERMEDIATE,
            ExpertiseLevel.ADVANCED,
        ]

        for level in levels:
            manager.reset()
            for _ in range(15):
                manager.record_interaction(InteractionOutcome.SUCCESS)

            metrics = create_metrics_window(
                success_rate=0.95, help_rate=0.02, shortcut_rate=0.5
            )
            decision = manager.check_level_up(level, metrics)

            if decision.should_transition:
                assert decision.user_notification is not None

    def test_zero_cooldown_policy(self):
        """Test with zero cooldown hours."""
        policy = TransitionPolicy(transition_cooldown_hours=0)
        manager = TransitionManager(policy=policy)

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)
        manager.execute_transition(decision)

        # Should not be in cooldown with zero hours
        stats = manager.get_transition_stats()
        assert stats["cooldown_active"] is False

    def test_frustration_below_threshold_no_level_down(self):
        """Test that low-confidence frustration doesn't trigger level down."""
        manager = TransitionManager()

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        frustration = create_frustration_signals(
            is_frustrated=True,
            confidence=0.3,  # Below threshold of 0.7
        )

        decision = manager.check_level_down(
            current_level=ExpertiseLevel.INTERMEDIATE,
            frustration_signals=frustration,
        )

        # Low confidence frustration alone shouldn't trigger level down
        if decision.should_transition:
            # Should only be due to other factors, not frustration
            assert "frustration detected but low confidence" in str(decision.evidence).lower()

    def test_require_user_confirmation(self):
        """Test require user confirmation policy."""
        policy = TransitionPolicy(require_user_confirmation=True)
        manager = TransitionManager(policy=policy)

        for _ in range(15):
            manager.record_interaction(InteractionOutcome.SUCCESS)

        metrics = create_metrics_window(success_rate=0.9, help_rate=0.05)
        decision = manager.check_level_up(ExpertiseLevel.BEGINNER, metrics)

        if decision.should_transition:
            assert decision.requires_confirmation is True
