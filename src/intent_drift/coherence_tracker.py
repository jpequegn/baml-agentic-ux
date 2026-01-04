"""Conversation coherence tracking.

This module provides tools for tracking conversation coherence over time,
detecting drift trends, and determining when context resets are needed.

Issue #83 - Task 5.6: Conversation Coherence Tracker
Part of #28 - Phase 5: Intent Drift Detection
Dependencies: Task 5.1 (Drift Analysis Types)
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from statistics import mean, stdev
from typing import Optional

from .types import (
    CoherenceAnalysis,
    CoherenceTrend,
    DriftAnalysis,
    DriftConversationTurn,
    DriftEvent,
    DriftType,
)


# ============================================
# Coherence Tracking Enums
# ============================================


class DriftTrend(Enum):
    """Specific drift trend patterns in conversation."""

    STABLE = "stable"
    """No significant drift pattern - conversation on track."""

    GRADUAL = "gradual"
    """Slow, steady drift over multiple turns."""

    SUDDEN = "sudden"
    """Abrupt drift in a single turn."""

    RETURNING = "returning"
    """User returning to original topic after drift."""

    OSCILLATING = "oscillating"
    """Alternating between on-topic and off-topic."""


class ContextResetReason(Enum):
    """Reasons for triggering a context reset."""

    ACCUMULATED_DRIFT = "accumulated_drift"
    """Total drift score exceeds threshold."""

    COHERENCE_COLLAPSE = "coherence_collapse"
    """Coherence dropped below critical level."""

    TOPIC_ABANDONMENT = "topic_abandonment"
    """User completely abandoned original topic."""

    USER_REQUEST = "user_request"
    """User explicitly requested reset."""

    TURN_LIMIT = "turn_limit"
    """Maximum turns without recovery reached."""

    REPEATED_DRIFT = "repeated_drift"
    """Same drift type occurring repeatedly."""


# ============================================
# Coherence Tracking Data Classes
# ============================================


@dataclass
class CoherenceTrackerConfig:
    """Configuration for coherence tracking.

    Attributes:
        window_size: Number of turns in sliding window for analysis
        drift_accumulation_threshold: Total drift score to trigger reset
        coherence_collapse_threshold: Coherence below this triggers reset
        sudden_drift_threshold: Score change that indicates sudden drift
        recovery_window: Turns to wait for recovery before reset
        min_turns_for_trend: Minimum turns needed to detect trend
        enable_auto_reset: Whether to auto-suggest context resets
    """

    window_size: int = 5
    drift_accumulation_threshold: float = 2.5
    coherence_collapse_threshold: float = 0.3
    sudden_drift_threshold: float = 0.5
    recovery_window: int = 3
    min_turns_for_trend: int = 3
    enable_auto_reset: bool = True

    def __post_init__(self):
        """Validate configuration values."""
        if self.window_size < 2:
            raise ValueError("window_size must be at least 2")
        if not 0.0 <= self.drift_accumulation_threshold <= 10.0:
            raise ValueError("drift_accumulation_threshold must be between 0.0 and 10.0")
        if not 0.0 <= self.coherence_collapse_threshold <= 1.0:
            raise ValueError("coherence_collapse_threshold must be between 0.0 and 1.0")
        if not 0.0 <= self.sudden_drift_threshold <= 1.0:
            raise ValueError("sudden_drift_threshold must be between 0.0 and 1.0")
        if self.recovery_window < 1:
            raise ValueError("recovery_window must be at least 1")
        if self.min_turns_for_trend < 2:
            raise ValueError("min_turns_for_trend must be at least 2")


@dataclass
class TurnCoherence:
    """Coherence metrics for a single turn.

    Attributes:
        turn_id: Identifier for the turn
        turn_number: Sequential turn number
        coherence_score: Coherence score (0-1)
        drift_score: Drift score for this turn (0-1)
        drift_type: Type of drift if any
        topic_match: How well turn matches conversation topic (0-1)
        intent_match: How well intent matches expected (0-1)
        timestamp: ISO 8601 timestamp
    """

    turn_id: str
    turn_number: int
    coherence_score: float
    drift_score: float
    drift_type: Optional[DriftType] = None
    topic_match: float = 1.0
    intent_match: float = 1.0
    timestamp: Optional[str] = None

    def __post_init__(self):
        """Validate scores are in valid range."""
        if not 0.0 <= self.coherence_score <= 1.0:
            raise ValueError("coherence_score must be between 0.0 and 1.0")
        if not 0.0 <= self.drift_score <= 1.0:
            raise ValueError("drift_score must be between 0.0 and 1.0")
        if not 0.0 <= self.topic_match <= 1.0:
            raise ValueError("topic_match must be between 0.0 and 1.0")
        if not 0.0 <= self.intent_match <= 1.0:
            raise ValueError("intent_match must be between 0.0 and 1.0")


@dataclass
class CoherenceMetrics:
    """Comprehensive coherence metrics for conversation tracking.

    Attributes:
        overall_coherence: Current overall coherence (0-1)
        topic_consistency: How consistent the topic has been (0-1)
        intent_stability: How stable intents are across turns (0-1)
        accumulated_drift: Total drift accumulated over conversation
        average_drift: Average drift score across window
        drift_trend: Current drift trend pattern
        coherence_trend: Direction of coherence change
        turns_since_drift: Number of turns since last drift event
        turns_in_recovery: Turns spent in recovery mode
        volatility: How much coherence varies (standard deviation)
        window_scores: Coherence scores in current window
    """

    overall_coherence: float
    topic_consistency: float
    intent_stability: float
    accumulated_drift: float
    average_drift: float
    drift_trend: DriftTrend
    coherence_trend: CoherenceTrend
    turns_since_drift: int
    turns_in_recovery: int
    volatility: float
    window_scores: list[float] = field(default_factory=list)

    def __post_init__(self):
        """Validate scores are in valid range."""
        if not 0.0 <= self.overall_coherence <= 1.0:
            raise ValueError("overall_coherence must be between 0.0 and 1.0")
        if not 0.0 <= self.topic_consistency <= 1.0:
            raise ValueError("topic_consistency must be between 0.0 and 1.0")
        if not 0.0 <= self.intent_stability <= 1.0:
            raise ValueError("intent_stability must be between 0.0 and 1.0")

    @property
    def is_healthy(self) -> bool:
        """Check if coherence is in healthy range."""
        return (
            self.overall_coherence >= 0.6
            and self.coherence_trend != CoherenceTrend.DEGRADING
            and self.drift_trend not in (DriftTrend.SUDDEN, DriftTrend.GRADUAL)
        )

    @property
    def needs_attention(self) -> bool:
        """Check if coherence needs intervention."""
        return (
            self.overall_coherence < 0.5
            or self.accumulated_drift > 1.5
            or self.volatility > 0.3
        )


@dataclass
class ContextResetTrigger:
    """Information about a context reset trigger.

    Attributes:
        triggered: Whether reset is triggered
        reason: Reason for the trigger
        severity: How urgent the reset is (0-1)
        accumulated_drift: Current accumulated drift
        coherence_at_trigger: Coherence score at trigger
        turns_without_recovery: Turns without successful recovery
        recommendation: Human-readable recommendation
    """

    triggered: bool
    reason: Optional[ContextResetReason] = None
    severity: float = 0.0
    accumulated_drift: float = 0.0
    coherence_at_trigger: float = 1.0
    turns_without_recovery: int = 0
    recommendation: str = ""

    def __post_init__(self):
        """Validate severity is in valid range."""
        if not 0.0 <= self.severity <= 1.0:
            raise ValueError("severity must be between 0.0 and 1.0")


# ============================================
# Main Coherence Tracker Class
# ============================================


class ConversationCoherenceTracker:
    """Tracks conversation coherence and drift accumulation.

    This class provides turn-by-turn tracking of conversation coherence,
    detecting drift trends and determining when context resets are needed.

    Attributes:
        config: Tracker configuration
        turns: History of turn coherence metrics
        drift_scores: Recent drift scores (sliding window)
        drift_events: Recorded drift events
        accumulated_drift: Total accumulated drift
        in_recovery: Whether currently in recovery mode
        last_drift_turn: Turn number of last drift event
        initial_topic: Topic at conversation start
        current_topic: Current conversation topic

    Example:
        >>> tracker = ConversationCoherenceTracker()
        >>> tracker.add_drift_score(0.1)  # Low drift
        >>> tracker.add_drift_score(0.2)  # Still low
        >>> metrics = tracker.get_coherence_metrics()
        >>> print(metrics.drift_trend)  # DriftTrend.STABLE
    """

    def __init__(self, config: Optional[CoherenceTrackerConfig] = None):
        """Initialize the coherence tracker.

        Args:
            config: Optional configuration, uses defaults if not provided
        """
        self.config = config or CoherenceTrackerConfig()
        self.turns: list[TurnCoherence] = []
        self.drift_scores: deque[float] = deque(maxlen=self.config.window_size)
        self.coherence_scores: deque[float] = deque(maxlen=self.config.window_size)
        self.drift_events: list[DriftEvent] = []
        self.accumulated_drift: float = 0.0
        self.in_recovery: bool = False
        self.recovery_start_turn: int = 0
        self.last_drift_turn: int = -1
        self.initial_topic: Optional[str] = None
        self.current_topic: Optional[str] = None
        self._drift_type_counts: dict[DriftType, int] = {}
        self._score_count: int = 0  # Track scores added without full turns

    def add_turn(self, turn: DriftConversationTurn) -> TurnCoherence:
        """Add a conversation turn to tracking.

        Extracts drift information from the turn and updates tracking state.

        Args:
            turn: The conversation turn to add

        Returns:
            TurnCoherence metrics for the added turn
        """
        drift_score = 0.0
        drift_type = None
        coherence_score = 1.0

        if turn.drift_analysis:
            drift_score = turn.drift_analysis.drift_score
            drift_type = turn.drift_analysis.drift_type
            coherence_score = 1.0 - drift_score

        # Update topic tracking
        if self.initial_topic is None and turn.detected_intent:
            self.initial_topic = turn.detected_intent
        if turn.detected_intent:
            self.current_topic = turn.detected_intent

        # Calculate topic and intent match
        topic_match = 1.0
        intent_match = 1.0
        if self.initial_topic and turn.detected_intent:
            topic_match = 1.0 if turn.detected_intent == self.initial_topic else 0.5
            intent_match = 1.0 - drift_score

        turn_coherence = TurnCoherence(
            turn_id=turn.turn_id,
            turn_number=turn.turn_number,
            coherence_score=coherence_score,
            drift_score=drift_score,
            drift_type=drift_type,
            topic_match=topic_match,
            intent_match=intent_match,
            timestamp=turn.timestamp,
        )

        self.turns.append(turn_coherence)
        self._process_drift_score(drift_score, drift_type, turn.turn_number)

        return turn_coherence

    def add_drift_score(self, score: float, drift_type: Optional[DriftType] = None) -> None:
        """Add a drift score directly.

        Useful when processing drift analysis results outside of full turns.

        Args:
            score: Drift score (0-1)
            drift_type: Optional type of drift detected

        Raises:
            ValueError: If score is not between 0.0 and 1.0
        """
        if not 0.0 <= score <= 1.0:
            raise ValueError("score must be between 0.0 and 1.0")

        turn_number = self._get_effective_turn_count()
        self._process_drift_score(score, drift_type, turn_number)
        self._score_count += 1

    def add_drift_analysis(self, analysis: DriftAnalysis) -> None:
        """Add drift analysis results to tracking.

        Args:
            analysis: The drift analysis to incorporate
        """
        self.add_drift_score(analysis.drift_score, analysis.drift_type)

    def _process_drift_score(
        self,
        score: float,
        drift_type: Optional[DriftType],
        turn_number: int,
    ) -> None:
        """Process a drift score and update internal state.

        Args:
            score: The drift score
            drift_type: Type of drift if any
            turn_number: Current turn number
        """
        self.drift_scores.append(score)
        self.coherence_scores.append(1.0 - score)
        self.accumulated_drift += score

        # Check for drift event
        if score >= self.config.sudden_drift_threshold:
            self._record_drift_event(score, drift_type, turn_number)
            self._enter_recovery_mode(turn_number)
        elif score < 0.2 and self.in_recovery:
            self._check_recovery_success(turn_number)

        # Track drift types
        if drift_type and drift_type != DriftType.NONE:
            self._drift_type_counts[drift_type] = self._drift_type_counts.get(drift_type, 0) + 1

    def _record_drift_event(
        self,
        score: float,
        drift_type: Optional[DriftType],
        turn_number: int,
    ) -> None:
        """Record a drift event.

        Args:
            score: Drift score at event
            drift_type: Type of drift
            turn_number: Turn where drift occurred
        """
        event = DriftEvent(
            turn_id=f"turn_{turn_number}",
            drift_type=drift_type or DriftType.AMBIGUOUS,
            drift_score=score,
            recovery_attempted=False,
            recovery_successful=False,
        )
        self.drift_events.append(event)
        self.last_drift_turn = turn_number

    def _get_effective_turn_count(self) -> int:
        """Get the effective turn count (max of turns and score_count).

        Returns:
            The effective turn count
        """
        return max(len(self.turns), self._score_count)

    def _enter_recovery_mode(self, turn_number: int) -> None:
        """Enter recovery mode after drift.

        Args:
            turn_number: Turn where recovery starts
        """
        if not self.in_recovery:
            self.in_recovery = True
            self.recovery_start_turn = turn_number

    def _check_recovery_success(self, turn_number: int) -> None:
        """Check if recovery was successful.

        Args:
            turn_number: Current turn number
        """
        turns_in_recovery = turn_number - self.recovery_start_turn
        if turns_in_recovery >= self.config.recovery_window:
            # Check if recent scores indicate recovery
            recent_scores = list(self.drift_scores)[-self.config.recovery_window :]
            if all(s < 0.3 for s in recent_scores):
                self.in_recovery = False
                # Mark most recent drift event as recovered
                if self.drift_events:
                    self.drift_events[-1].recovery_attempted = True
                    self.drift_events[-1].recovery_successful = True

    def get_coherence_metrics(self) -> CoherenceMetrics:
        """Get current coherence metrics.

        Calculates comprehensive metrics based on conversation history.

        Returns:
            CoherenceMetrics with current state analysis
        """
        if not self.drift_scores:
            return CoherenceMetrics(
                overall_coherence=1.0,
                topic_consistency=1.0,
                intent_stability=1.0,
                accumulated_drift=0.0,
                average_drift=0.0,
                drift_trend=DriftTrend.STABLE,
                coherence_trend=CoherenceTrend.STABLE,
                turns_since_drift=0,
                turns_in_recovery=0,
                volatility=0.0,
                window_scores=[],
            )

        # Calculate basic metrics
        coherence_list = list(self.coherence_scores)
        drift_list = list(self.drift_scores)
        overall_coherence = mean(coherence_list) if coherence_list else 1.0
        average_drift = mean(drift_list) if drift_list else 0.0

        # Calculate volatility (standard deviation)
        volatility = 0.0
        if len(coherence_list) >= 2:
            volatility = stdev(coherence_list)

        # Calculate topic and intent metrics
        topic_consistency = self._calculate_topic_consistency()
        intent_stability = self._calculate_intent_stability()

        # Detect trends
        drift_trend = self._detect_drift_trend()
        coherence_trend = self._detect_coherence_trend()

        # Calculate recovery metrics
        turns_since_drift = self._calculate_turns_since_drift()
        turns_in_recovery = self._calculate_turns_in_recovery()

        return CoherenceMetrics(
            overall_coherence=overall_coherence,
            topic_consistency=topic_consistency,
            intent_stability=intent_stability,
            accumulated_drift=self.accumulated_drift,
            average_drift=average_drift,
            drift_trend=drift_trend,
            coherence_trend=coherence_trend,
            turns_since_drift=turns_since_drift,
            turns_in_recovery=turns_in_recovery,
            volatility=volatility,
            window_scores=coherence_list,
        )

    def _calculate_topic_consistency(self) -> float:
        """Calculate topic consistency score.

        Returns:
            Topic consistency score (0-1)
        """
        if not self.turns:
            return 1.0

        topic_matches = [t.topic_match for t in self.turns]
        return mean(topic_matches)

    def _calculate_intent_stability(self) -> float:
        """Calculate intent stability score.

        Returns:
            Intent stability score (0-1)
        """
        if not self.turns:
            return 1.0

        intent_matches = [t.intent_match for t in self.turns]
        return mean(intent_matches)

    def _calculate_turns_since_drift(self) -> int:
        """Calculate turns since last drift event.

        Returns:
            Number of turns since last drift
        """
        effective_count = self._get_effective_turn_count()
        if self.last_drift_turn < 0:
            return effective_count
        return effective_count - self.last_drift_turn - 1

    def _calculate_turns_in_recovery(self) -> int:
        """Calculate turns spent in recovery mode.

        Returns:
            Number of turns in recovery
        """
        if not self.in_recovery:
            return 0
        return self._get_effective_turn_count() - self.recovery_start_turn

    def _detect_drift_trend(self) -> DriftTrend:
        """Detect the current drift trend pattern.

        Returns:
            DriftTrend indicating the pattern
        """
        drift_list = list(self.drift_scores)

        if len(drift_list) < self.config.min_turns_for_trend:
            return DriftTrend.STABLE

        # Check for sudden drift (large single change)
        if len(drift_list) >= 2:
            last_change = drift_list[-1] - drift_list[-2]
            if last_change >= self.config.sudden_drift_threshold:
                return DriftTrend.SUDDEN

        # Calculate trend over window
        first_half = drift_list[: len(drift_list) // 2]
        second_half = drift_list[len(drift_list) // 2 :]

        first_avg = mean(first_half) if first_half else 0
        second_avg = mean(second_half) if second_half else 0

        # Check for returning (was drifting, now improving)
        if first_avg > 0.4 and second_avg < 0.2:
            return DriftTrend.RETURNING

        # Check for gradual drift
        if second_avg - first_avg > 0.15:
            return DriftTrend.GRADUAL

        # Check for oscillating pattern
        if len(drift_list) >= 4:
            changes = [drift_list[i] - drift_list[i - 1] for i in range(1, len(drift_list))]
            sign_changes = sum(
                1 for i in range(1, len(changes)) if changes[i] * changes[i - 1] < 0
            )
            if sign_changes >= len(changes) // 2:
                return DriftTrend.OSCILLATING

        return DriftTrend.STABLE

    def _detect_coherence_trend(self) -> CoherenceTrend:
        """Detect the coherence trend direction.

        Returns:
            CoherenceTrend indicating direction
        """
        coherence_list = list(self.coherence_scores)

        if len(coherence_list) < self.config.min_turns_for_trend:
            return CoherenceTrend.STABLE

        first_half = coherence_list[: len(coherence_list) // 2]
        second_half = coherence_list[len(coherence_list) // 2 :]

        first_avg = mean(first_half) if first_half else 1.0
        second_avg = mean(second_half) if second_half else 1.0

        diff = second_avg - first_avg

        if diff > 0.1:
            return CoherenceTrend.IMPROVING
        elif diff < -0.1:
            return CoherenceTrend.DEGRADING

        # Check for volatility
        if len(coherence_list) >= 2:
            vol = stdev(coherence_list)
            if vol > 0.25:
                return CoherenceTrend.VOLATILE

        return CoherenceTrend.STABLE

    def should_reset_context(self) -> ContextResetTrigger:
        """Determine if context should be reset.

        Analyzes conversation state to determine if a context reset
        is recommended based on accumulated drift, coherence collapse,
        or other factors.

        Returns:
            ContextResetTrigger with reset decision and details
        """
        if not self.config.enable_auto_reset:
            return ContextResetTrigger(triggered=False)

        metrics = self.get_coherence_metrics()

        # Check accumulated drift threshold
        if self.accumulated_drift >= self.config.drift_accumulation_threshold:
            return ContextResetTrigger(
                triggered=True,
                reason=ContextResetReason.ACCUMULATED_DRIFT,
                severity=min(1.0, self.accumulated_drift / self.config.drift_accumulation_threshold),
                accumulated_drift=self.accumulated_drift,
                coherence_at_trigger=metrics.overall_coherence,
                turns_without_recovery=self._calculate_turns_in_recovery(),
                recommendation="Consider resetting context - accumulated drift exceeds threshold",
            )

        # Check coherence collapse
        if metrics.overall_coherence < self.config.coherence_collapse_threshold:
            return ContextResetTrigger(
                triggered=True,
                reason=ContextResetReason.COHERENCE_COLLAPSE,
                severity=1.0 - metrics.overall_coherence,
                accumulated_drift=self.accumulated_drift,
                coherence_at_trigger=metrics.overall_coherence,
                turns_without_recovery=self._calculate_turns_in_recovery(),
                recommendation="Consider resetting context - coherence has collapsed",
            )

        # Check for repeated drift
        most_common_drift = max(
            self._drift_type_counts.items(),
            key=lambda x: x[1],
            default=(None, 0),
        )
        if most_common_drift[1] >= 3:
            return ContextResetTrigger(
                triggered=True,
                reason=ContextResetReason.REPEATED_DRIFT,
                severity=min(1.0, most_common_drift[1] / 5.0),
                accumulated_drift=self.accumulated_drift,
                coherence_at_trigger=metrics.overall_coherence,
                turns_without_recovery=self._calculate_turns_in_recovery(),
                recommendation=f"Consider resetting context - repeated {most_common_drift[0].value} drift",
            )

        # Check recovery window exceeded
        if self.in_recovery:
            turns_in_recovery = self._calculate_turns_in_recovery()
            if turns_in_recovery > self.config.recovery_window * 2:
                return ContextResetTrigger(
                    triggered=True,
                    reason=ContextResetReason.TURN_LIMIT,
                    severity=min(1.0, turns_in_recovery / (self.config.recovery_window * 3)),
                    accumulated_drift=self.accumulated_drift,
                    coherence_at_trigger=metrics.overall_coherence,
                    turns_without_recovery=turns_in_recovery,
                    recommendation="Consider resetting context - recovery taking too long",
                )

        return ContextResetTrigger(triggered=False)

    def reset(self) -> None:
        """Reset the tracker to initial state.

        Clears all tracking data for a fresh start.
        """
        self.turns.clear()
        self.drift_scores.clear()
        self.coherence_scores.clear()
        self.drift_events.clear()
        self.accumulated_drift = 0.0
        self.in_recovery = False
        self.recovery_start_turn = 0
        self.last_drift_turn = -1
        self.initial_topic = None
        self.current_topic = None
        self._drift_type_counts.clear()
        self._score_count = 0

    def to_coherence_analysis(self) -> CoherenceAnalysis:
        """Convert current state to CoherenceAnalysis.

        Provides compatibility with existing CoherenceAnalysis type.

        Returns:
            CoherenceAnalysis representation of current state
        """
        metrics = self.get_coherence_metrics()
        warnings = []

        if metrics.needs_attention:
            warnings.append("Coherence needs attention")
        if self.in_recovery:
            warnings.append("Currently in recovery mode")
        if metrics.drift_trend == DriftTrend.GRADUAL:
            warnings.append("Gradual drift detected")
        if metrics.drift_trend == DriftTrend.SUDDEN:
            warnings.append("Sudden drift occurred")

        return CoherenceAnalysis(
            coherence_score=metrics.overall_coherence,
            topic_consistency=metrics.topic_consistency,
            intent_stability=metrics.intent_stability,
            coherence_trend=metrics.coherence_trend,
            turn_relevance_scores=metrics.window_scores,
            warnings=warnings,
        )

    @property
    def turn_count(self) -> int:
        """Get number of tracked turns."""
        return len(self.turns)

    @property
    def drift_event_count(self) -> int:
        """Get number of drift events."""
        return len(self.drift_events)

    @property
    def recovery_rate(self) -> float:
        """Get rate of successful recoveries.

        Returns:
            Percentage of drift events with successful recovery
        """
        if not self.drift_events:
            return 1.0

        successful = sum(1 for e in self.drift_events if e.recovery_successful)
        return successful / len(self.drift_events)
