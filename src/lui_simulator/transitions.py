"""
Level Transition Logic for LUI Simulator.
Manages smooth, non-jarring expertise level transitions.

Issue #46 - Phase 2: Adaptive Interface Personalization

Key Features:
- Level-up based on success streaks, success rate, and shortcut adoption
- Level-down based on errors, help-seeking, and frustration signals
- Cooldown periods to prevent oscillation
- Rollback capability for recent transitions
- User-friendly notifications
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from .expertise import ExpertiseLevel
from .metrics import (
    FrustrationSignals,
    InteractionOutcome,
    MetricsWindow,
    SignalSeverity,
)


class TransitionDirection(Enum):
    """Direction of an expertise level transition."""
    LEVEL_UP = "LEVEL_UP"
    LEVEL_DOWN = "LEVEL_DOWN"
    LATERAL = "LATERAL"


@dataclass
class TransitionPolicy:
    """Policy configuration for level transitions."""
    # Level Up Criteria
    min_consecutive_successes: int = 5
    min_success_rate: float = 0.8
    min_interactions_at_level: int = 10
    min_shortcut_rate: float = 0.3

    # Level Down Criteria
    max_consecutive_errors: int = 3
    max_help_rate: float = 0.4
    frustration_confidence_threshold: float = 0.7

    # Stability Controls
    transition_cooldown_hours: int = 24
    gradual_transition: bool = True
    require_user_confirmation: bool = False

    # Rollback Settings
    enable_rollback: bool = True
    rollback_window_hours: int = 48

    def __post_init__(self):
        """Validate policy values."""
        if self.min_consecutive_successes < 1:
            raise ValueError("min_consecutive_successes must be >= 1")
        if not 0 <= self.min_success_rate <= 1:
            raise ValueError("min_success_rate must be 0-1")
        if not 0 <= self.max_help_rate <= 1:
            raise ValueError("max_help_rate must be 0-1")
        if self.transition_cooldown_hours < 0:
            raise ValueError("transition_cooldown_hours must be >= 0")


@dataclass
class TransitionDecision:
    """Decision about whether to transition and how."""
    should_transition: bool
    direction: Optional[TransitionDirection]
    from_level: ExpertiseLevel
    to_level: Optional[ExpertiseLevel]
    confidence: float
    rationale: str
    evidence: list[str] = field(default_factory=list)
    user_notification: Optional[str] = None
    notification_tone: Optional[str] = None
    rollback_available: bool = True
    requires_confirmation: bool = False
    cooldown_active: bool = False


@dataclass
class TransitionResult:
    """Result of executing a transition."""
    success: bool
    transition_id: str
    executed_at: str
    previous_level: ExpertiseLevel
    new_level: ExpertiseLevel
    direction: TransitionDirection
    rollback_token: Optional[str] = None
    rollback_expires_at: Optional[str] = None
    notification_sent: bool = False
    notification_message: Optional[str] = None


@dataclass
class TransitionRecord:
    """Record of a past transition."""
    transition_id: str
    user_id: str
    timestamp: str
    direction: TransitionDirection
    from_level: ExpertiseLevel
    to_level: ExpertiseLevel
    rationale: str
    was_rolled_back: bool = False
    triggered_by: str = "auto"


@dataclass
class RollbackResult:
    """Result of a rollback attempt."""
    success: bool
    message: str
    restored_level: Optional[ExpertiseLevel] = None
    reason_failed: Optional[str] = None


# Notification templates for different transitions
TRANSITION_NOTIFICATIONS = {
    (ExpertiseLevel.NOVICE, ExpertiseLevel.BEGINNER):
        "Great start! You're ready for some handy tips.",
    (ExpertiseLevel.BEGINNER, ExpertiseLevel.INTERMEDIATE):
        "You're getting the hang of this! I'll show you some shortcuts.",
    (ExpertiseLevel.INTERMEDIATE, ExpertiseLevel.ADVANCED):
        "Nice progress! I'll be more concise now.",
    (ExpertiseLevel.ADVANCED, ExpertiseLevel.EXPERT):
        "You're a pro! Enabling power-user features.",
}

LEVEL_DOWN_NOTIFICATION = "I'll provide more guidance to help you out."
ROLLBACK_SUCCESS_NOTIFICATION = "No problem! I've restored your previous settings."
COOLDOWN_ACTIVE_NOTIFICATION = "Let's give it a bit more time before changing levels."


class TransitionManager:
    """
    Manages expertise level transitions with smooth, non-jarring changes.

    Handles:
    - Level-up transitions based on success metrics
    - Level-down transitions based on error/frustration signals
    - Cooldown periods to prevent oscillation
    - Rollback capability for recent transitions
    - User-friendly notifications
    """

    # Level ordering for determining next/previous levels
    LEVEL_ORDER = [
        ExpertiseLevel.NOVICE,
        ExpertiseLevel.BEGINNER,
        ExpertiseLevel.INTERMEDIATE,
        ExpertiseLevel.ADVANCED,
        ExpertiseLevel.EXPERT,
    ]

    def __init__(self, policy: Optional[TransitionPolicy] = None):
        """
        Initialize the transition manager.

        Args:
            policy: Transition policy configuration. Uses defaults if not provided.
        """
        self.policy = policy or TransitionPolicy()
        self._transition_history: list[TransitionRecord] = []
        self._pending_rollbacks: dict[str, TransitionRecord] = {}
        self._last_transition_time: Optional[datetime] = None
        self._interactions_at_current_level: int = 0
        self._consecutive_successes: int = 0
        self._consecutive_errors: int = 0

    @property
    def transition_history(self) -> list[TransitionRecord]:
        """Get the history of transitions."""
        return list(self._transition_history)

    @property
    def last_transition(self) -> Optional[TransitionRecord]:
        """Get the most recent transition."""
        return self._transition_history[-1] if self._transition_history else None

    def record_interaction(self, outcome: InteractionOutcome) -> None:
        """
        Record an interaction outcome to track streaks.

        Args:
            outcome: The outcome of the interaction.
        """
        self._interactions_at_current_level += 1

        if outcome == InteractionOutcome.SUCCESS:
            self._consecutive_successes += 1
            self._consecutive_errors = 0
        elif outcome in (InteractionOutcome.FAILURE, InteractionOutcome.ABANDONED):
            self._consecutive_errors += 1
            self._consecutive_successes = 0
        elif outcome == InteractionOutcome.PARTIAL_SUCCESS:
            # Partial success breaks error streak but doesn't fully reset success
            self._consecutive_errors = 0
            # Only count as half a success for streak purposes
            pass
        elif outcome == InteractionOutcome.HELP_ESCALATION:
            # Help escalation breaks success streak
            self._consecutive_successes = 0

    def check_level_up(
        self,
        current_level: ExpertiseLevel,
        metrics_window: Optional[MetricsWindow] = None,
        user_id: str = "anonymous",
    ) -> TransitionDecision:
        """
        Check if a level-up transition should occur.

        Args:
            current_level: Current expertise level.
            metrics_window: Aggregated metrics for evaluation.
            user_id: User identifier for tracking.

        Returns:
            TransitionDecision with recommendation.
        """
        evidence = []

        # Check cooldown
        if self._is_cooldown_active():
            return TransitionDecision(
                should_transition=False,
                direction=None,
                from_level=current_level,
                to_level=None,
                confidence=1.0,
                rationale="Transition cooldown is active",
                evidence=["Recent transition within cooldown period"],
                cooldown_active=True,
                user_notification=COOLDOWN_ACTIVE_NOTIFICATION,
            )

        # Check if already at max level
        if current_level == ExpertiseLevel.EXPERT:
            return TransitionDecision(
                should_transition=False,
                direction=None,
                from_level=current_level,
                to_level=None,
                confidence=1.0,
                rationale="Already at maximum expertise level",
                evidence=["User is at EXPERT level"],
            )

        # Check minimum interactions at current level
        if self._interactions_at_current_level < self.policy.min_interactions_at_level:
            evidence.append(
                f"Only {self._interactions_at_current_level}/{self.policy.min_interactions_at_level} "
                f"interactions at current level"
            )
            return TransitionDecision(
                should_transition=False,
                direction=None,
                from_level=current_level,
                to_level=None,
                confidence=0.8,
                rationale="Insufficient interactions at current level",
                evidence=evidence,
            )

        # Evaluate level-up criteria
        criteria_met = 0
        total_criteria = 4

        # Criterion 1: Consecutive successes
        if self._consecutive_successes >= self.policy.min_consecutive_successes:
            criteria_met += 1
            evidence.append(
                f"Consecutive successes: {self._consecutive_successes} "
                f"(min: {self.policy.min_consecutive_successes})"
            )
        else:
            evidence.append(
                f"Consecutive successes: {self._consecutive_successes} "
                f"(need: {self.policy.min_consecutive_successes})"
            )

        # Criteria from metrics window
        if metrics_window:
            # Criterion 2: Success rate
            if metrics_window.success_rate >= self.policy.min_success_rate:
                criteria_met += 1
                evidence.append(f"Success rate: {metrics_window.success_rate:.1%} (min: {self.policy.min_success_rate:.1%})")
            else:
                evidence.append(f"Success rate: {metrics_window.success_rate:.1%} (need: {self.policy.min_success_rate:.1%})")

            # Criterion 3: Low help rate
            if metrics_window.help_rate < 0.1:  # < 10%
                criteria_met += 1
                evidence.append(f"Help rate: {metrics_window.help_rate:.1%} (target: <10%)")
            else:
                evidence.append(f"Help rate: {metrics_window.help_rate:.1%} (need: <10%)")

            # Criterion 4: Shortcut adoption (for intermediate+ transitions)
            if current_level in (ExpertiseLevel.INTERMEDIATE, ExpertiseLevel.ADVANCED):
                if metrics_window.shortcut_rate >= self.policy.min_shortcut_rate:
                    criteria_met += 1
                    evidence.append(f"Shortcut rate: {metrics_window.shortcut_rate:.1%} (min: {self.policy.min_shortcut_rate:.1%})")
                else:
                    evidence.append(f"Shortcut rate: {metrics_window.shortcut_rate:.1%} (need: {self.policy.min_shortcut_rate:.1%})")
            else:
                # Lower levels don't require shortcuts
                criteria_met += 1
                evidence.append("Shortcut adoption not required at this level")
        else:
            # Without metrics window, rely on streak
            evidence.append("No metrics window available - using streak data only")
            # Give partial credit if we have good streak
            if self._consecutive_successes >= self.policy.min_consecutive_successes:
                criteria_met += 2

        # Calculate confidence and decide
        confidence = criteria_met / total_criteria
        should_transition = criteria_met >= 3  # Need at least 3 of 4 criteria

        if should_transition:
            next_level = self._get_next_level(current_level)
            notification = self._get_level_up_notification(current_level, next_level)

            return TransitionDecision(
                should_transition=True,
                direction=TransitionDirection.LEVEL_UP,
                from_level=current_level,
                to_level=next_level,
                confidence=confidence,
                rationale=f"Met {criteria_met}/{total_criteria} level-up criteria",
                evidence=evidence,
                user_notification=notification,
                notification_tone="encouraging",
                rollback_available=self.policy.enable_rollback,
                requires_confirmation=self.policy.require_user_confirmation,
            )
        else:
            return TransitionDecision(
                should_transition=False,
                direction=None,
                from_level=current_level,
                to_level=None,
                confidence=confidence,
                rationale=f"Only met {criteria_met}/{total_criteria} level-up criteria",
                evidence=evidence,
            )

    def check_level_down(
        self,
        current_level: ExpertiseLevel,
        frustration_signals: Optional[FrustrationSignals] = None,
        metrics_window: Optional[MetricsWindow] = None,
        user_requested: bool = False,
        user_id: str = "anonymous",
    ) -> TransitionDecision:
        """
        Check if a level-down transition should occur.

        Args:
            current_level: Current expertise level.
            frustration_signals: Detected frustration signals.
            metrics_window: Aggregated metrics for evaluation.
            user_requested: Whether user explicitly requested more help.
            user_id: User identifier for tracking.

        Returns:
            TransitionDecision with recommendation.
        """
        evidence = []

        # Check cooldown (unless user explicitly requested)
        if not user_requested and self._is_cooldown_active():
            return TransitionDecision(
                should_transition=False,
                direction=None,
                from_level=current_level,
                to_level=None,
                confidence=1.0,
                rationale="Transition cooldown is active",
                evidence=["Recent transition within cooldown period"],
                cooldown_active=True,
            )

        # Check if already at minimum level
        if current_level == ExpertiseLevel.NOVICE:
            return TransitionDecision(
                should_transition=False,
                direction=None,
                from_level=current_level,
                to_level=None,
                confidence=1.0,
                rationale="Already at minimum expertise level",
                evidence=["User is at NOVICE level"],
            )

        # User explicit request takes priority
        if user_requested:
            prev_level = self._get_previous_level(current_level)
            return TransitionDecision(
                should_transition=True,
                direction=TransitionDirection.LEVEL_DOWN,
                from_level=current_level,
                to_level=prev_level,
                confidence=1.0,
                rationale="User explicitly requested more help",
                evidence=["User preference override"],
                user_notification=LEVEL_DOWN_NOTIFICATION,
                notification_tone="supportive",
                rollback_available=self.policy.enable_rollback,
                requires_confirmation=False,
            )

        # Evaluate level-down criteria
        triggers_detected = 0
        total_triggers = 3

        # Trigger 1: Consecutive errors
        if self._consecutive_errors >= self.policy.max_consecutive_errors:
            triggers_detected += 1
            evidence.append(
                f"Consecutive errors: {self._consecutive_errors} "
                f"(threshold: {self.policy.max_consecutive_errors})"
            )
        else:
            evidence.append(
                f"Consecutive errors: {self._consecutive_errors} "
                f"(threshold: {self.policy.max_consecutive_errors})"
            )

        # Trigger 2: High help rate
        if metrics_window and metrics_window.help_rate > self.policy.max_help_rate:
            triggers_detected += 1
            evidence.append(
                f"Help rate: {metrics_window.help_rate:.1%} "
                f"(max: {self.policy.max_help_rate:.1%})"
            )
        elif metrics_window:
            evidence.append(
                f"Help rate: {metrics_window.help_rate:.1%} "
                f"(max: {self.policy.max_help_rate:.1%})"
            )

        # Trigger 3: Frustration detected
        if frustration_signals and frustration_signals.is_frustrated:
            if frustration_signals.confidence >= self.policy.frustration_confidence_threshold:
                triggers_detected += 1
                evidence.append(
                    f"Frustration detected: confidence {frustration_signals.confidence:.1%} "
                    f"(threshold: {self.policy.frustration_confidence_threshold:.1%})"
                )
                if frustration_signals.signals:
                    evidence.append(f"Frustration signals: {', '.join(frustration_signals.signals[:3])}")
            else:
                evidence.append(
                    f"Frustration detected but low confidence: {frustration_signals.confidence:.1%}"
                )

        # Need at least 1 strong trigger for level down
        # (we want to be conservative about lowering levels)
        should_transition = triggers_detected >= 1

        if should_transition:
            prev_level = self._get_previous_level(current_level)
            confidence = triggers_detected / total_triggers

            # Adjust confidence based on severity
            if frustration_signals and frustration_signals.severity == SignalSeverity.CRITICAL:
                confidence = min(1.0, confidence + 0.2)

            return TransitionDecision(
                should_transition=True,
                direction=TransitionDirection.LEVEL_DOWN,
                from_level=current_level,
                to_level=prev_level,
                confidence=confidence,
                rationale=f"Detected {triggers_detected} level-down trigger(s)",
                evidence=evidence,
                user_notification=LEVEL_DOWN_NOTIFICATION,
                notification_tone="supportive",
                rollback_available=self.policy.enable_rollback,
                requires_confirmation=self.policy.require_user_confirmation,
            )
        else:
            return TransitionDecision(
                should_transition=False,
                direction=None,
                from_level=current_level,
                to_level=None,
                confidence=0.0,
                rationale="No level-down triggers detected",
                evidence=evidence,
            )

    def execute_transition(
        self,
        decision: TransitionDecision,
        user_id: str = "anonymous",
    ) -> TransitionResult:
        """
        Execute a transition decision.

        Args:
            decision: The transition decision to execute.
            user_id: User identifier for tracking.

        Returns:
            TransitionResult with execution details.
        """
        if not decision.should_transition or decision.to_level is None or decision.direction is None:
            raise ValueError("Cannot execute a decision that says not to transition")

        now = datetime.now()
        transition_id = str(uuid.uuid4())
        direction = decision.direction
        to_level = decision.to_level

        # Create transition record
        record = TransitionRecord(
            transition_id=transition_id,
            user_id=user_id,
            timestamp=now.isoformat() + "Z",
            direction=direction,
            from_level=decision.from_level,
            to_level=to_level,
            rationale=decision.rationale,
            was_rolled_back=False,
            triggered_by="auto" if not decision.requires_confirmation else "confirmed",
        )

        # Store in history
        self._transition_history.append(record)

        # Store for potential rollback
        rollback_token = None
        rollback_expires_at = None
        if decision.rollback_available:
            rollback_token = str(uuid.uuid4())
            rollback_expires = now + timedelta(hours=self.policy.rollback_window_hours)
            rollback_expires_at = rollback_expires.isoformat() + "Z"
            self._pending_rollbacks[rollback_token] = record

        # Update state
        self._last_transition_time = now
        self._interactions_at_current_level = 0
        self._consecutive_successes = 0
        self._consecutive_errors = 0

        return TransitionResult(
            success=True,
            transition_id=transition_id,
            executed_at=now.isoformat() + "Z",
            previous_level=decision.from_level,
            new_level=to_level,
            direction=direction,
            rollback_token=rollback_token,
            rollback_expires_at=rollback_expires_at,
            notification_sent=decision.user_notification is not None,
            notification_message=decision.user_notification,
        )

    def rollback_transition(
        self,
        rollback_token: Optional[str] = None,
        user_id: str = "anonymous",
    ) -> RollbackResult:
        """
        Rollback a recent transition.

        Args:
            rollback_token: Token from the original transition, or None for latest.
            user_id: User identifier for tracking.

        Returns:
            RollbackResult with rollback details.
        """
        if not self.policy.enable_rollback:
            return RollbackResult(
                success=False,
                message="Rollback is disabled by policy",
                reason_failed="Rollback disabled",
            )

        # Find the transition to rollback
        record = None
        if rollback_token:
            record = self._pending_rollbacks.get(rollback_token)
            if not record:
                return RollbackResult(
                    success=False,
                    message="Rollback token not found or expired",
                    reason_failed="Invalid or expired token",
                )
        else:
            # Rollback the latest transition
            if not self._transition_history:
                return RollbackResult(
                    success=False,
                    message="No transitions to rollback",
                    reason_failed="No transition history",
                )
            record = self._transition_history[-1]
            if record.was_rolled_back:
                return RollbackResult(
                    success=False,
                    message="Most recent transition was already rolled back",
                    reason_failed="Already rolled back",
                )

        # Check if rollback window has expired
        transition_time = datetime.fromisoformat(record.timestamp.rstrip("Z"))
        rollback_deadline = transition_time + timedelta(hours=self.policy.rollback_window_hours)
        if datetime.now() > rollback_deadline:
            return RollbackResult(
                success=False,
                message="Rollback window has expired",
                reason_failed=f"Rollback expired after {self.policy.rollback_window_hours} hours",
            )

        # Mark as rolled back
        record.was_rolled_back = True

        # Clean up pending rollback tokens for this transition
        tokens_to_remove = [
            token for token, rec in self._pending_rollbacks.items()
            if rec.transition_id == record.transition_id
        ]
        for token in tokens_to_remove:
            del self._pending_rollbacks[token]

        # Reset counters
        self._interactions_at_current_level = 0
        self._consecutive_successes = 0
        self._consecutive_errors = 0

        return RollbackResult(
            success=True,
            message=ROLLBACK_SUCCESS_NOTIFICATION,
            restored_level=record.from_level,
        )

    def _is_cooldown_active(self) -> bool:
        """Check if transition cooldown is currently active."""
        if self._last_transition_time is None:
            return False

        cooldown_end = self._last_transition_time + timedelta(
            hours=self.policy.transition_cooldown_hours
        )
        return datetime.now() < cooldown_end

    def _get_next_level(self, current: ExpertiseLevel) -> ExpertiseLevel:
        """Get the next expertise level (for level up)."""
        try:
            current_idx = self.LEVEL_ORDER.index(current)
            if current_idx < len(self.LEVEL_ORDER) - 1:
                return self.LEVEL_ORDER[current_idx + 1]
        except ValueError:
            pass
        return current

    def _get_previous_level(self, current: ExpertiseLevel) -> ExpertiseLevel:
        """Get the previous expertise level (for level down)."""
        try:
            current_idx = self.LEVEL_ORDER.index(current)
            if current_idx > 0:
                return self.LEVEL_ORDER[current_idx - 1]
        except ValueError:
            pass
        return current

    def _get_level_up_notification(
        self,
        from_level: ExpertiseLevel,
        to_level: ExpertiseLevel,
    ) -> str:
        """Get the appropriate level-up notification message."""
        key = (from_level, to_level)
        if key in TRANSITION_NOTIFICATIONS:
            return TRANSITION_NOTIFICATIONS[key]

        # Generic level-up message
        return f"Great progress! Moving you to {to_level.value.lower()} mode."

    def reset(self) -> None:
        """Reset the transition manager state."""
        self._transition_history.clear()
        self._pending_rollbacks.clear()
        self._last_transition_time = None
        self._interactions_at_current_level = 0
        self._consecutive_successes = 0
        self._consecutive_errors = 0

    def clear_cooldown(self) -> None:
        """Clear the transition cooldown (for testing)."""
        self._last_transition_time = None

    def get_transition_stats(self) -> dict:
        """Get statistics about transitions."""
        level_ups = sum(
            1 for t in self._transition_history
            if t.direction == TransitionDirection.LEVEL_UP and not t.was_rolled_back
        )
        level_downs = sum(
            1 for t in self._transition_history
            if t.direction == TransitionDirection.LEVEL_DOWN and not t.was_rolled_back
        )
        rollbacks = sum(
            1 for t in self._transition_history
            if t.was_rolled_back
        )

        return {
            "total_transitions": len(self._transition_history),
            "level_ups": level_ups,
            "level_downs": level_downs,
            "rollbacks": rollbacks,
            "interactions_at_current_level": self._interactions_at_current_level,
            "consecutive_successes": self._consecutive_successes,
            "consecutive_errors": self._consecutive_errors,
            "cooldown_active": self._is_cooldown_active(),
        }
