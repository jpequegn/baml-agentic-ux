"""
Metrics Collection for LUI Simulator
Tracks behavioral signals for expertise detection and user adaptation.

Issue #44 - Phase 2: Adaptive Interface Personalization
"""

import uuid
import statistics
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class InteractionOutcome(Enum):
    """Outcome of a user interaction."""
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILURE = "FAILURE"
    ABANDONED = "ABANDONED"
    HELP_ESCALATION = "HELP_ESCALATION"


class TrendDirection(Enum):
    """Direction of a metric trend over time."""
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"


class SignalSeverity(Enum):
    """Severity of a detected signal."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PrivacyMode(Enum):
    """Privacy mode for metrics collection."""
    FULL = "FULL"
    AGGREGATE_ONLY = "AGGREGATE_ONLY"
    SESSION_ONLY = "SESSION_ONLY"
    DISABLED = "DISABLED"


@dataclass
class InteractionRecord:
    """Record of a single user interaction."""
    interaction_id: str
    timestamp: str
    session_id: str
    intent_detected: str
    intent_confidence: float
    parameters_provided: int
    parameters_required: int
    outcome: InteractionOutcome
    completion_time_ms: int
    error_count: int
    help_requested: bool
    disambiguation_needed: bool
    used_shortcut: bool
    input_length: int
    retries: int = 0
    corrections: int = 0


@dataclass
class MetricsWindow:
    """Aggregated metrics over a sliding window."""
    window_id: str
    window_start: str
    window_end: str
    interaction_count: int
    success_rate: float
    partial_success_rate: float
    failure_rate: float
    abandonment_rate: float
    help_rate: float
    shortcut_rate: float
    error_rate: float
    disambiguation_rate: float
    avg_completion_time_ms: float
    median_completion_time_ms: float
    p95_completion_time_ms: float
    avg_input_length: float
    avg_parameters_provided: float
    avg_retries: float
    success_trend: TrendDirection
    efficiency_trend: TrendDirection
    engagement_trend: TrendDirection


@dataclass
class FrustrationSignals:
    """Signals indicating user frustration."""
    is_frustrated: bool
    confidence: float
    severity: SignalSeverity
    signals: list[str] = field(default_factory=list)
    trigger_events: list[str] = field(default_factory=list)
    recommendation: Optional[str] = None


@dataclass
class MasterySignals:
    """Signals indicating user mastery."""
    is_demonstrating_mastery: bool
    confidence: float
    mastery_level: float
    signals: list[str] = field(default_factory=list)
    skills_demonstrated: list[str] = field(default_factory=list)
    ready_for_advancement: bool = False


@dataclass
class MetricsStoreConfig:
    """Configuration for metrics storage."""
    privacy_mode: PrivacyMode = PrivacyMode.FULL
    retention_days: int = 90
    aggregate_window_size: int = 20
    enable_frustration_detection: bool = True
    enable_mastery_detection: bool = True
    anonymize_intents: bool = False


class MetricsCollector:
    """
    Collects and analyzes behavioral metrics for user adaptation.

    Tracks:
    - Command fluency (completion speed, shortcut usage)
    - Error patterns (error rate, recovery speed)
    - Help-seeking behavior (documentation access, tooltip engagement)
    - Parameter provision (completeness vs. defaults usage)
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        config: Optional[MetricsStoreConfig] = None,
    ):
        """
        Initialize the metrics collector.

        Args:
            session_id: Unique session identifier (generated if not provided)
            config: Configuration for metrics storage
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.config = config or MetricsStoreConfig()

        # Interaction history (bounded by window size for memory efficiency)
        self._interactions: deque[InteractionRecord] = deque(
            maxlen=self.config.aggregate_window_size * 3
        )

        # Historical windows for trend analysis
        self._historical_windows: deque[MetricsWindow] = deque(maxlen=10)

        # Session-level counters
        self._session_start = datetime.utcnow().isoformat() + "Z"
        self._consecutive_errors = 0
        self._consecutive_successes = 0

    def record_interaction(
        self,
        intent_detected: str,
        intent_confidence: float,
        parameters_provided: int,
        parameters_required: int,
        outcome: InteractionOutcome,
        completion_time_ms: int,
        error_count: int = 0,
        help_requested: bool = False,
        disambiguation_needed: bool = False,
        used_shortcut: bool = False,
        input_length: int = 0,
        retries: int = 0,
        corrections: int = 0,
    ) -> InteractionRecord:
        """
        Record a new interaction.

        Args:
            intent_detected: The detected intent name
            intent_confidence: Confidence score (0.0-1.0)
            parameters_provided: Number of parameters provided
            parameters_required: Number of required parameters
            outcome: Outcome of the interaction
            completion_time_ms: Time to complete in milliseconds
            error_count: Number of errors during interaction
            help_requested: Whether help was requested
            disambiguation_needed: Whether clarification was needed
            used_shortcut: Whether a shortcut was used
            input_length: Length of user input
            retries: Number of retry attempts
            corrections: Number of corrections made

        Returns:
            The recorded interaction
        """
        if self.config.privacy_mode == PrivacyMode.DISABLED:
            # Return a stub record but don't store
            return InteractionRecord(
                interaction_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow().isoformat() + "Z",
                session_id=self.session_id,
                intent_detected=intent_detected if not self.config.anonymize_intents else "ANONYMIZED",
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
                corrections=corrections,
            )

        # Create the record
        intent_name = intent_detected
        if self.config.anonymize_intents:
            intent_name = f"INTENT_{hash(intent_detected) % 10000:04d}"

        record = InteractionRecord(
            interaction_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat() + "Z",
            session_id=self.session_id,
            intent_detected=intent_name,
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
            corrections=corrections,
        )

        # Update consecutive counters
        if outcome == InteractionOutcome.SUCCESS:
            self._consecutive_successes += 1
            self._consecutive_errors = 0
        elif outcome in (InteractionOutcome.FAILURE, InteractionOutcome.ABANDONED):
            self._consecutive_errors += 1
            self._consecutive_successes = 0
        else:
            # Partial success or help escalation - reset both
            self._consecutive_errors = 0
            self._consecutive_successes = 0

        # Store based on privacy mode
        if self.config.privacy_mode != PrivacyMode.AGGREGATE_ONLY:
            self._interactions.append(record)

        return record

    def get_windowed_metrics(
        self,
        window_size: Optional[int] = None,
    ) -> MetricsWindow:
        """
        Calculate aggregated metrics over a sliding window.

        Args:
            window_size: Number of recent interactions to include
                        (defaults to config.aggregate_window_size)

        Returns:
            Aggregated metrics for the window
        """
        window_size = window_size or self.config.aggregate_window_size
        interactions = list(self._interactions)[-window_size:]

        if not interactions:
            return self._empty_window()

        # Calculate rates
        count = len(interactions)
        success_count = sum(1 for i in interactions if i.outcome == InteractionOutcome.SUCCESS)
        partial_count = sum(1 for i in interactions if i.outcome == InteractionOutcome.PARTIAL_SUCCESS)
        failure_count = sum(1 for i in interactions if i.outcome == InteractionOutcome.FAILURE)
        abandoned_count = sum(1 for i in interactions if i.outcome == InteractionOutcome.ABANDONED)
        help_count = sum(1 for i in interactions if i.help_requested)
        shortcut_count = sum(1 for i in interactions if i.used_shortcut)
        disambiguation_count = sum(1 for i in interactions if i.disambiguation_needed)
        total_errors = sum(i.error_count for i in interactions)

        # Calculate time metrics
        times = [i.completion_time_ms for i in interactions]
        sorted_times = sorted(times)

        # Calculate trends
        success_trend = self._calculate_trend([i.outcome == InteractionOutcome.SUCCESS for i in interactions])
        efficiency_trend = self._calculate_efficiency_trend(interactions)
        engagement_trend = TrendDirection.STABLE  # Would need inter-session data

        return MetricsWindow(
            window_id=str(uuid.uuid4()),
            window_start=interactions[0].timestamp,
            window_end=interactions[-1].timestamp,
            interaction_count=count,
            success_rate=success_count / count,
            partial_success_rate=partial_count / count,
            failure_rate=failure_count / count,
            abandonment_rate=abandoned_count / count,
            help_rate=help_count / count,
            shortcut_rate=shortcut_count / count,
            error_rate=total_errors / count,
            disambiguation_rate=disambiguation_count / count,
            avg_completion_time_ms=statistics.mean(times),
            median_completion_time_ms=statistics.median(times),
            p95_completion_time_ms=sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 1 else sorted_times[0],
            avg_input_length=statistics.mean(i.input_length for i in interactions),
            avg_parameters_provided=statistics.mean(i.parameters_provided for i in interactions),
            avg_retries=statistics.mean(i.retries for i in interactions),
            success_trend=success_trend,
            efficiency_trend=efficiency_trend,
            engagement_trend=engagement_trend,
        )

    def detect_frustration_signals(self) -> FrustrationSignals:
        """
        Detect signs of user frustration based on behavioral patterns.

        Checks for:
        - 3+ consecutive errors
        - Rapid retry pattern
        - Declining success rate
        - Help rate > 40%
        - High abandonment rate

        Returns:
            FrustrationSignals with detection results
        """
        if not self.config.enable_frustration_detection:
            return FrustrationSignals(
                is_frustrated=False,
                confidence=0.0,
                severity=SignalSeverity.LOW,
            )

        signals: list[str] = []
        trigger_events: list[str] = []
        confidence_factors: list[float] = []

        # Check consecutive errors
        if self._consecutive_errors >= 3:
            signals.append(f"{self._consecutive_errors} consecutive errors")
            trigger_events.append("CONSECUTIVE_ERRORS")
            confidence_factors.append(min(0.3 + (self._consecutive_errors - 3) * 0.1, 0.5))

        # Get recent metrics
        if len(self._interactions) >= 5:
            metrics = self.get_windowed_metrics(min(20, len(self._interactions)))

            # Check help rate
            if metrics.help_rate > 0.4:
                signals.append(f"High help rate: {metrics.help_rate:.1%}")
                trigger_events.append("HIGH_HELP_RATE")
                confidence_factors.append(0.25)

            # Check abandonment rate
            if metrics.abandonment_rate > 0.2:
                signals.append(f"High abandonment rate: {metrics.abandonment_rate:.1%}")
                trigger_events.append("HIGH_ABANDONMENT")
                confidence_factors.append(0.2)

            # Check success trend
            if metrics.success_trend == TrendDirection.DECLINING:
                signals.append("Declining success rate")
                trigger_events.append("DECLINING_SUCCESS")
                confidence_factors.append(0.2)

            # Check retry pattern
            if metrics.avg_retries > 1.5:
                signals.append(f"High retry rate: {metrics.avg_retries:.1f} avg")
                trigger_events.append("HIGH_RETRIES")
                confidence_factors.append(0.15)

            # Check error rate
            if metrics.error_rate > 1.0:
                signals.append(f"High error rate: {metrics.error_rate:.1f} per interaction")
                trigger_events.append("HIGH_ERROR_RATE")
                confidence_factors.append(0.2)

        # Calculate overall confidence
        confidence = min(sum(confidence_factors), 1.0) if confidence_factors else 0.0

        # Determine severity
        if confidence >= 0.7:
            severity = SignalSeverity.CRITICAL
        elif confidence >= 0.5:
            severity = SignalSeverity.HIGH
        elif confidence >= 0.3:
            severity = SignalSeverity.MEDIUM
        else:
            severity = SignalSeverity.LOW

        # Generate recommendation
        recommendation = None
        if confidence >= 0.5:
            if "CONSECUTIVE_ERRORS" in trigger_events:
                recommendation = "Consider offering guided assistance or reducing complexity"
            elif "HIGH_HELP_RATE" in trigger_events:
                recommendation = "Consider switching to a more tutorial-focused interaction mode"
            elif "HIGH_ABANDONMENT" in trigger_events:
                recommendation = "Consider simplifying the current workflow"

        return FrustrationSignals(
            is_frustrated=confidence >= 0.4,
            confidence=confidence,
            severity=severity,
            signals=signals,
            trigger_events=trigger_events,
            recommendation=recommendation,
        )

    def detect_mastery_signals(self) -> MasterySignals:
        """
        Detect signs of user mastery based on behavioral patterns.

        Checks for:
        - High success rate (>90%)
        - Shortcut usage (>50%)
        - Fast completion times
        - Complete parameter provision
        - No help requests

        Returns:
            MasterySignals with detection results
        """
        if not self.config.enable_mastery_detection:
            return MasterySignals(
                is_demonstrating_mastery=False,
                confidence=0.0,
                mastery_level=0.0,
            )

        if len(self._interactions) < 10:
            return MasterySignals(
                is_demonstrating_mastery=False,
                confidence=0.0,
                mastery_level=0.0,
                signals=["Insufficient data (need 10+ interactions)"],
            )

        signals: list[str] = []
        skills: list[str] = []
        mastery_factors: list[float] = []

        metrics = self.get_windowed_metrics(min(20, len(self._interactions)))

        # Check success rate
        if metrics.success_rate >= 0.9:
            signals.append(f"High success rate: {metrics.success_rate:.1%}")
            skills.append("consistent_execution")
            mastery_factors.append(0.25)
        elif metrics.success_rate >= 0.8:
            mastery_factors.append(0.15)

        # Check shortcut usage
        if metrics.shortcut_rate >= 0.5:
            signals.append(f"High shortcut usage: {metrics.shortcut_rate:.1%}")
            skills.append("shortcut_proficiency")
            mastery_factors.append(0.2)
        elif metrics.shortcut_rate >= 0.3:
            mastery_factors.append(0.1)

        # Check help rate (low is good)
        if metrics.help_rate <= 0.1:
            signals.append(f"Low help dependence: {metrics.help_rate:.1%}")
            skills.append("self_sufficiency")
            mastery_factors.append(0.15)

        # Check error rate (low is good)
        if metrics.error_rate <= 0.2:
            signals.append(f"Low error rate: {metrics.error_rate:.1f}")
            skills.append("accuracy")
            mastery_factors.append(0.15)

        # Check efficiency trend
        if metrics.efficiency_trend == TrendDirection.IMPROVING:
            signals.append("Improving efficiency")
            skills.append("learning_progress")
            mastery_factors.append(0.1)

        # Check consecutive successes
        if self._consecutive_successes >= 5:
            signals.append(f"{self._consecutive_successes} consecutive successes")
            skills.append("streak_performance")
            mastery_factors.append(0.15)

        # Calculate mastery level and confidence
        mastery_level = min(sum(mastery_factors), 1.0) if mastery_factors else 0.0
        confidence = min(mastery_level + 0.2, 1.0) if mastery_level > 0.3 else mastery_level

        # Ready for advancement if mastery level is high enough
        ready_for_advancement = mastery_level >= 0.7 and metrics.success_rate >= 0.85

        return MasterySignals(
            is_demonstrating_mastery=mastery_level >= 0.5,
            confidence=confidence,
            mastery_level=mastery_level,
            signals=signals,
            skills_demonstrated=skills,
            ready_for_advancement=ready_for_advancement,
        )

    def get_recent_interactions(self, count: int = 10) -> list[InteractionRecord]:
        """
        Get the most recent interactions.

        Args:
            count: Number of interactions to return

        Returns:
            List of recent interactions (newest last)
        """
        return list(self._interactions)[-count:]

    def get_session_stats(self) -> dict:
        """
        Get statistics for the current session.

        Returns:
            Dictionary with session statistics
        """
        interactions = list(self._interactions)

        if not interactions:
            return {
                "session_id": self.session_id,
                "session_start": self._session_start,
                "interaction_count": 0,
                "success_count": 0,
                "failure_count": 0,
                "consecutive_errors": 0,
                "consecutive_successes": 0,
            }

        return {
            "session_id": self.session_id,
            "session_start": self._session_start,
            "interaction_count": len(interactions),
            "success_count": sum(1 for i in interactions if i.outcome == InteractionOutcome.SUCCESS),
            "failure_count": sum(1 for i in interactions if i.outcome in (InteractionOutcome.FAILURE, InteractionOutcome.ABANDONED)),
            "help_count": sum(1 for i in interactions if i.help_requested),
            "shortcut_count": sum(1 for i in interactions if i.used_shortcut),
            "consecutive_errors": self._consecutive_errors,
            "consecutive_successes": self._consecutive_successes,
            "total_errors": sum(i.error_count for i in interactions),
            "avg_completion_time_ms": statistics.mean(i.completion_time_ms for i in interactions) if interactions else 0,
        }

    def reset_session(self) -> None:
        """Reset the session, clearing all stored interactions."""
        self.session_id = str(uuid.uuid4())
        self._session_start = datetime.utcnow().isoformat() + "Z"
        self._interactions.clear()
        self._consecutive_errors = 0
        self._consecutive_successes = 0

    def _empty_window(self) -> MetricsWindow:
        """Create an empty metrics window."""
        now = datetime.utcnow().isoformat() + "Z"
        return MetricsWindow(
            window_id=str(uuid.uuid4()),
            window_start=now,
            window_end=now,
            interaction_count=0,
            success_rate=0.0,
            partial_success_rate=0.0,
            failure_rate=0.0,
            abandonment_rate=0.0,
            help_rate=0.0,
            shortcut_rate=0.0,
            error_rate=0.0,
            disambiguation_rate=0.0,
            avg_completion_time_ms=0.0,
            median_completion_time_ms=0.0,
            p95_completion_time_ms=0.0,
            avg_input_length=0.0,
            avg_parameters_provided=0.0,
            avg_retries=0.0,
            success_trend=TrendDirection.STABLE,
            efficiency_trend=TrendDirection.STABLE,
            engagement_trend=TrendDirection.STABLE,
        )

    def _calculate_trend(self, values: list[bool]) -> TrendDirection:
        """
        Calculate trend direction for a series of boolean values.

        Args:
            values: List of boolean values (True = success)

        Returns:
            TrendDirection based on recent vs. older values
        """
        if len(values) < 6:
            return TrendDirection.STABLE

        # Compare first half to second half
        mid = len(values) // 2
        first_half_rate = sum(values[:mid]) / mid
        second_half_rate = sum(values[mid:]) / (len(values) - mid)

        diff = second_half_rate - first_half_rate
        if diff > 0.1:
            return TrendDirection.IMPROVING
        elif diff < -0.1:
            return TrendDirection.DECLINING
        return TrendDirection.STABLE

    def _calculate_efficiency_trend(self, interactions: list[InteractionRecord]) -> TrendDirection:
        """
        Calculate efficiency trend based on completion times.

        Args:
            interactions: List of interactions to analyze

        Returns:
            TrendDirection based on completion time changes
        """
        if len(interactions) < 6:
            return TrendDirection.STABLE

        times = [i.completion_time_ms for i in interactions]
        mid = len(times) // 2
        first_half_avg = statistics.mean(times[:mid])
        second_half_avg = statistics.mean(times[mid:])

        # Faster is better, so if second half is faster, it's improving
        ratio = second_half_avg / first_half_avg if first_half_avg > 0 else 1.0
        if ratio < 0.85:  # 15% faster
            return TrendDirection.IMPROVING
        elif ratio > 1.15:  # 15% slower
            return TrendDirection.DECLINING
        return TrendDirection.STABLE
