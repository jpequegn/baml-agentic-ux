"""Drift Analytics & Logging for Intent Drift Detection.

This module provides comprehensive analytics and logging for tracking intent drift
patterns across conversations and sessions. It enables:
- Event logging with rich contextual information
- Metrics calculation (drift rates, recovery rates, severity distribution)
- Pattern analysis (common drift types, temporal patterns, user segments)
- Export capabilities (JSON, CSV)

Issue #87 - Task 5.10: Drift Analytics & Logging
Part of #28 - Phase 5: Intent Drift Detection
"""

from __future__ import annotations

import csv
import json
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
from io import StringIO
from typing import Any, Callable, Optional, Protocol, TypeVar

from src.intent_drift.types import (
    DriftType,
    DriftEvent,
    DriftAnalysis,
    RecommendedAction,
)


# ============================================
# Analytics Event Types
# ============================================


class RecoveryMethod(Enum):
    """Methods used to recover from drift."""

    NONE = "none"
    """No recovery attempted."""

    CLARIFICATION = "clarification"
    """Asked user for clarification."""

    REDIRECT = "redirect"
    """Redirected to supported capability."""

    PARTIAL_HELP = "partial_help"
    """Provided partial assistance."""

    ESCALATION = "escalation"
    """Escalated to human/other system."""

    BOUNDARY_STATEMENT = "boundary_statement"
    """Stated capability boundaries."""


class DriftSeverity(Enum):
    """Severity levels for drift events."""

    LOW = "low"
    """Minor drift, easily recoverable (score < 0.3)."""

    MEDIUM = "medium"
    """Moderate drift, may need intervention (0.3 <= score < 0.6)."""

    HIGH = "high"
    """Significant drift, likely needs intervention (0.6 <= score < 0.8)."""

    CRITICAL = "critical"
    """Severe drift, requires intervention (score >= 0.8)."""

    @classmethod
    def from_score(cls, score: float) -> DriftSeverity:
        """Get severity level from drift score.

        Args:
            score: Drift score (0-1)

        Returns:
            Appropriate severity level
        """
        if score < 0.3:
            return cls.LOW
        elif score < 0.6:
            return cls.MEDIUM
        elif score < 0.8:
            return cls.HIGH
        else:
            return cls.CRITICAL


@dataclass
class DriftAnalyticsEvent:
    """Extended drift event for analytics tracking.

    Extends the basic DriftEvent with additional context needed for
    comprehensive analytics and pattern detection.

    Attributes:
        event_id: Unique event identifier
        session_id: Session where drift occurred
        turn_id: Turn identifier within session
        timestamp: When the drift was detected (ISO 8601)
        drift_type: Type of drift detected
        drift_score: Severity score (0-1)
        severity: Categorized severity level
        user_input: The user input that caused drift
        detected_intent: Intent detected (if any)
        original_intent: Original/expected intent
        recovery_method: Method used for recovery
        recovery_attempted: Whether recovery was tried
        recovery_successful: Whether recovery succeeded
        redirect_accepted: Whether redirect was accepted by user
        response_time_ms: Time to detect and respond
        user_id: Optional user identifier for segmentation
        channel: Optional channel (web, mobile, api)
        metadata: Additional custom metadata
    """

    event_id: str
    session_id: str
    turn_id: str
    timestamp: datetime
    drift_type: DriftType
    drift_score: float
    severity: DriftSeverity
    user_input: str
    detected_intent: Optional[str] = None
    original_intent: Optional[str] = None
    recovery_method: RecoveryMethod = RecoveryMethod.NONE
    recovery_attempted: bool = False
    recovery_successful: bool = False
    redirect_accepted: Optional[bool] = None
    response_time_ms: Optional[int] = None
    user_id: Optional[str] = None
    channel: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate drift score range."""
        if not 0.0 <= self.drift_score <= 1.0:
            raise ValueError("drift_score must be between 0.0 and 1.0")

    @classmethod
    def from_drift_event(
        cls,
        event: DriftEvent,
        event_id: str,
        session_id: str,
        timestamp: datetime,
        user_input: str,
        **kwargs: Any,
    ) -> DriftAnalyticsEvent:
        """Create analytics event from basic DriftEvent.

        Args:
            event: Basic DriftEvent
            event_id: Unique event ID
            session_id: Session identifier
            timestamp: Event timestamp
            user_input: User input text
            **kwargs: Additional fields

        Returns:
            DriftAnalyticsEvent with extended fields
        """
        return cls(
            event_id=event_id,
            session_id=session_id,
            turn_id=event.turn_id,
            timestamp=timestamp,
            drift_type=event.drift_type,
            drift_score=event.drift_score,
            severity=DriftSeverity.from_score(event.drift_score),
            user_input=user_input,
            recovery_attempted=event.recovery_attempted,
            recovery_successful=event.recovery_successful,
            **kwargs,
        )

    @classmethod
    def from_drift_analysis(
        cls,
        analysis: DriftAnalysis,
        event_id: str,
        session_id: str,
        turn_id: str,
        timestamp: datetime,
        **kwargs: Any,
    ) -> DriftAnalyticsEvent:
        """Create analytics event from DriftAnalysis.

        Args:
            analysis: DriftAnalysis result
            event_id: Unique event ID
            session_id: Session identifier
            turn_id: Turn identifier
            timestamp: Event timestamp
            **kwargs: Additional fields

        Returns:
            DriftAnalyticsEvent with extended fields
        """
        return cls(
            event_id=event_id,
            session_id=session_id,
            turn_id=turn_id,
            timestamp=timestamp,
            drift_type=analysis.drift_type,
            drift_score=analysis.drift_score,
            severity=DriftSeverity.from_score(analysis.drift_score),
            user_input=analysis.current_input,
            original_intent=analysis.original_intent,
            detected_intent=analysis.last_supported_intent,
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "turn_id": self.turn_id,
            "timestamp": self.timestamp.isoformat(),
            "drift_type": self.drift_type.value,
            "drift_score": self.drift_score,
            "severity": self.severity.value,
            "user_input": self.user_input,
            "detected_intent": self.detected_intent,
            "original_intent": self.original_intent,
            "recovery_method": self.recovery_method.value,
            "recovery_attempted": self.recovery_attempted,
            "recovery_successful": self.recovery_successful,
            "redirect_accepted": self.redirect_accepted,
            "response_time_ms": self.response_time_ms,
            "user_id": self.user_id,
            "channel": self.channel,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DriftAnalyticsEvent:
        """Create from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            DriftAnalyticsEvent instance
        """
        return cls(
            event_id=data["event_id"],
            session_id=data["session_id"],
            turn_id=data["turn_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            drift_type=DriftType(data["drift_type"]),
            drift_score=data["drift_score"],
            severity=DriftSeverity(data["severity"]),
            user_input=data["user_input"],
            detected_intent=data.get("detected_intent"),
            original_intent=data.get("original_intent"),
            recovery_method=RecoveryMethod(
                data.get("recovery_method", RecoveryMethod.NONE.value)
            ),
            recovery_attempted=data.get("recovery_attempted", False),
            recovery_successful=data.get("recovery_successful", False),
            redirect_accepted=data.get("redirect_accepted"),
            response_time_ms=data.get("response_time_ms"),
            user_id=data.get("user_id"),
            channel=data.get("channel"),
            metadata=data.get("metadata", {}),
        )


# ============================================
# Analytics Metrics Types
# ============================================


@dataclass
class DriftMetrics:
    """Calculated metrics for drift analytics.

    Attributes:
        total_events: Total drift events in period
        total_sessions: Unique sessions with drift
        drift_rate: Percentage of interactions with drift
        recovery_rate: Percentage of successful recoveries
        avg_drift_score: Average drift score
        median_drift_score: Median drift score
        avg_response_time_ms: Average response time
        severity_distribution: Count by severity level
        drift_type_distribution: Count by drift type
        recovery_method_distribution: Count by recovery method
        channel_distribution: Count by channel
        hourly_distribution: Events by hour of day
    """

    total_events: int
    total_sessions: int
    drift_rate: float
    recovery_rate: float
    avg_drift_score: float
    median_drift_score: float
    avg_response_time_ms: Optional[float]
    severity_distribution: dict[str, int]
    drift_type_distribution: dict[str, int]
    recovery_method_distribution: dict[str, int]
    channel_distribution: dict[str, int]
    hourly_distribution: dict[int, int]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_events": self.total_events,
            "total_sessions": self.total_sessions,
            "drift_rate": self.drift_rate,
            "recovery_rate": self.recovery_rate,
            "avg_drift_score": self.avg_drift_score,
            "median_drift_score": self.median_drift_score,
            "avg_response_time_ms": self.avg_response_time_ms,
            "severity_distribution": self.severity_distribution,
            "drift_type_distribution": self.drift_type_distribution,
            "recovery_method_distribution": self.recovery_method_distribution,
            "channel_distribution": self.channel_distribution,
            "hourly_distribution": self.hourly_distribution,
        }


@dataclass
class DriftPattern:
    """Detected drift pattern.

    Attributes:
        pattern_id: Unique pattern identifier
        pattern_type: Type of pattern (e.g., "temporal", "user_segment", "intent_sequence")
        description: Human-readable description
        frequency: How often pattern occurs
        confidence: Confidence in pattern detection (0-1)
        affected_sessions: Number of sessions showing pattern
        sample_events: Sample event IDs demonstrating pattern
        recommendations: Suggested actions to address pattern
    """

    pattern_id: str
    pattern_type: str
    description: str
    frequency: int
    confidence: float
    affected_sessions: int
    sample_events: list[str]
    recommendations: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "description": self.description,
            "frequency": self.frequency,
            "confidence": self.confidence,
            "affected_sessions": self.affected_sessions,
            "sample_events": self.sample_events,
            "recommendations": self.recommendations,
        }


@dataclass
class TimeRange:
    """Time range for filtering analytics.

    Attributes:
        start: Start of time range
        end: End of time range
    """

    start: datetime
    end: datetime

    def __post_init__(self):
        """Validate time range."""
        if self.start > self.end:
            raise ValueError("start must be before end")

    def contains(self, timestamp: datetime) -> bool:
        """Check if timestamp falls within range.

        Args:
            timestamp: Timestamp to check

        Returns:
            True if timestamp is within range
        """
        return self.start <= timestamp <= self.end

    @classmethod
    def last_hours(cls, hours: int) -> TimeRange:
        """Create range for last N hours.

        Args:
            hours: Number of hours

        Returns:
            TimeRange for last N hours
        """
        end = datetime.now(timezone.utc)
        start = end - timedelta(hours=hours)
        return cls(start=start, end=end)

    @classmethod
    def last_days(cls, days: int) -> TimeRange:
        """Create range for last N days.

        Args:
            days: Number of days

        Returns:
            TimeRange for last N days
        """
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)
        return cls(start=start, end=end)


@dataclass
class DriftSummary:
    """Comprehensive drift analytics summary.

    Attributes:
        time_range: Time range covered
        metrics: Calculated metrics
        patterns: Detected patterns
        top_drift_types: Most common drift types
        top_intents_affected: Intents most affected by drift
        problematic_sessions: Sessions with high drift rates
        generated_at: When summary was generated
    """

    time_range: TimeRange
    metrics: DriftMetrics
    patterns: list[DriftPattern]
    top_drift_types: list[tuple[str, int]]
    top_intents_affected: list[tuple[str, int]]
    problematic_sessions: list[tuple[str, float]]
    generated_at: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "time_range": {
                "start": self.time_range.start.isoformat(),
                "end": self.time_range.end.isoformat(),
            },
            "metrics": self.metrics.to_dict(),
            "patterns": [p.to_dict() for p in self.patterns],
            "top_drift_types": self.top_drift_types,
            "top_intents_affected": self.top_intents_affected,
            "problematic_sessions": self.problematic_sessions,
            "generated_at": self.generated_at.isoformat(),
        }


# ============================================
# Storage Protocol
# ============================================


class DriftEventStore(Protocol):
    """Protocol for drift event storage backends."""

    def store(self, event: DriftAnalyticsEvent) -> None:
        """Store a drift event."""
        ...

    def query(
        self,
        time_range: Optional[TimeRange] = None,
        session_id: Optional[str] = None,
        drift_type: Optional[DriftType] = None,
        severity: Optional[DriftSeverity] = None,
        limit: Optional[int] = None,
    ) -> list[DriftAnalyticsEvent]:
        """Query stored events with filters."""
        ...

    def count(self, time_range: Optional[TimeRange] = None) -> int:
        """Count events in time range."""
        ...

    def clear(self) -> None:
        """Clear all stored events."""
        ...


# ============================================
# In-Memory Store Implementation
# ============================================


class InMemoryDriftEventStore:
    """In-memory implementation of drift event storage.

    Suitable for development, testing, and single-instance deployments.
    For production, use a persistent storage backend.
    """

    def __init__(self, max_events: int = 10000):
        """Initialize in-memory store.

        Args:
            max_events: Maximum events to store (FIFO eviction)
        """
        self._events: list[DriftAnalyticsEvent] = []
        self._max_events = max_events

    def store(self, event: DriftAnalyticsEvent) -> None:
        """Store a drift event.

        Args:
            event: Event to store
        """
        self._events.append(event)
        # FIFO eviction if over limit
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events :]

    def query(
        self,
        time_range: Optional[TimeRange] = None,
        session_id: Optional[str] = None,
        drift_type: Optional[DriftType] = None,
        severity: Optional[DriftSeverity] = None,
        limit: Optional[int] = None,
    ) -> list[DriftAnalyticsEvent]:
        """Query stored events with filters.

        Args:
            time_range: Filter by time range
            session_id: Filter by session
            drift_type: Filter by drift type
            severity: Filter by severity
            limit: Maximum events to return

        Returns:
            Matching events
        """
        results = self._events

        if time_range:
            results = [e for e in results if time_range.contains(e.timestamp)]
        if session_id:
            results = [e for e in results if e.session_id == session_id]
        if drift_type:
            results = [e for e in results if e.drift_type == drift_type]
        if severity:
            results = [e for e in results if e.severity == severity]

        # Sort by timestamp descending (most recent first)
        results = sorted(results, key=lambda e: e.timestamp, reverse=True)

        if limit:
            results = results[:limit]

        return results

    def count(self, time_range: Optional[TimeRange] = None) -> int:
        """Count events in time range.

        Args:
            time_range: Optional time range filter

        Returns:
            Event count
        """
        if time_range:
            return len([e for e in self._events if time_range.contains(e.timestamp)])
        return len(self._events)

    def clear(self) -> None:
        """Clear all stored events."""
        self._events.clear()

    @property
    def events(self) -> list[DriftAnalyticsEvent]:
        """Get all events (for testing)."""
        return self._events.copy()


# ============================================
# Main Analytics Class
# ============================================


class DriftAnalytics:
    """Main analytics engine for drift tracking and analysis.

    Provides:
    - Event logging with contextual information
    - Metrics calculation
    - Pattern detection
    - Export to JSON/CSV
    """

    def __init__(
        self,
        store: Optional[DriftEventStore] = None,
        total_interactions: Optional[Callable[[], int]] = None,
    ):
        """Initialize drift analytics.

        Args:
            store: Event storage backend (defaults to in-memory)
            total_interactions: Callable returning total interactions for rate calculation
        """
        self._store = store or InMemoryDriftEventStore()
        self._total_interactions = total_interactions
        self._event_counter = 0

    def _generate_event_id(self) -> str:
        """Generate unique event ID.

        Returns:
            Unique event identifier
        """
        self._event_counter += 1
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"drift_{timestamp}_{self._event_counter:06d}"

    def log_event(
        self,
        session_id: str,
        turn_id: str,
        drift_type: DriftType,
        drift_score: float,
        user_input: str,
        detected_intent: Optional[str] = None,
        original_intent: Optional[str] = None,
        recovery_method: RecoveryMethod = RecoveryMethod.NONE,
        recovery_attempted: bool = False,
        recovery_successful: bool = False,
        redirect_accepted: Optional[bool] = None,
        response_time_ms: Optional[int] = None,
        user_id: Optional[str] = None,
        channel: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> DriftAnalyticsEvent:
        """Log a drift event.

        Args:
            session_id: Session identifier
            turn_id: Turn identifier
            drift_type: Type of drift
            drift_score: Drift severity score (0-1)
            user_input: User input text
            detected_intent: Detected intent if any
            original_intent: Expected/original intent
            recovery_method: Method used for recovery
            recovery_attempted: Whether recovery was tried
            recovery_successful: Whether recovery succeeded
            redirect_accepted: Whether redirect was accepted
            response_time_ms: Response time in ms
            user_id: Optional user ID
            channel: Optional channel
            metadata: Additional metadata

        Returns:
            Created analytics event
        """
        event = DriftAnalyticsEvent(
            event_id=self._generate_event_id(),
            session_id=session_id,
            turn_id=turn_id,
            timestamp=datetime.now(timezone.utc),
            drift_type=drift_type,
            drift_score=drift_score,
            severity=DriftSeverity.from_score(drift_score),
            user_input=user_input,
            detected_intent=detected_intent,
            original_intent=original_intent,
            recovery_method=recovery_method,
            recovery_attempted=recovery_attempted,
            recovery_successful=recovery_successful,
            redirect_accepted=redirect_accepted,
            response_time_ms=response_time_ms,
            user_id=user_id,
            channel=channel,
            metadata=metadata or {},
        )
        self._store.store(event)
        return event

    def log_from_analysis(
        self,
        analysis: DriftAnalysis,
        session_id: str,
        turn_id: str,
        recovery_method: RecoveryMethod = RecoveryMethod.NONE,
        recovery_attempted: bool = False,
        recovery_successful: bool = False,
        redirect_accepted: Optional[bool] = None,
        response_time_ms: Optional[int] = None,
        user_id: Optional[str] = None,
        channel: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> DriftAnalyticsEvent:
        """Log event from DriftAnalysis result.

        Args:
            analysis: DriftAnalysis result
            session_id: Session identifier
            turn_id: Turn identifier
            recovery_method: Method used for recovery
            recovery_attempted: Whether recovery was tried
            recovery_successful: Whether recovery succeeded
            redirect_accepted: Whether redirect was accepted
            response_time_ms: Response time in ms
            user_id: Optional user ID
            channel: Optional channel
            metadata: Additional metadata

        Returns:
            Created analytics event
        """
        return self.log_event(
            session_id=session_id,
            turn_id=turn_id,
            drift_type=analysis.drift_type,
            drift_score=analysis.drift_score,
            user_input=analysis.current_input,
            detected_intent=analysis.last_supported_intent,
            original_intent=analysis.original_intent,
            recovery_method=recovery_method,
            recovery_attempted=recovery_attempted,
            recovery_successful=recovery_successful,
            redirect_accepted=redirect_accepted,
            response_time_ms=response_time_ms,
            user_id=user_id,
            channel=channel,
            metadata=metadata,
        )

    def get_events(
        self,
        time_range: Optional[TimeRange] = None,
        session_id: Optional[str] = None,
        drift_type: Optional[DriftType] = None,
        severity: Optional[DriftSeverity] = None,
        limit: Optional[int] = None,
    ) -> list[DriftAnalyticsEvent]:
        """Get drift events with optional filters.

        Args:
            time_range: Filter by time range
            session_id: Filter by session
            drift_type: Filter by drift type
            severity: Filter by severity
            limit: Maximum events to return

        Returns:
            List of matching events
        """
        return self._store.query(
            time_range=time_range,
            session_id=session_id,
            drift_type=drift_type,
            severity=severity,
            limit=limit,
        )

    def calculate_metrics(
        self,
        time_range: Optional[TimeRange] = None,
        total_interactions: Optional[int] = None,
    ) -> DriftMetrics:
        """Calculate drift metrics for time period.

        Args:
            time_range: Time range to analyze
            total_interactions: Total interactions in period (for rate calc)

        Returns:
            Calculated metrics
        """
        events = self._store.query(time_range=time_range)

        if not events:
            return DriftMetrics(
                total_events=0,
                total_sessions=0,
                drift_rate=0.0,
                recovery_rate=0.0,
                avg_drift_score=0.0,
                median_drift_score=0.0,
                avg_response_time_ms=None,
                severity_distribution={},
                drift_type_distribution={},
                recovery_method_distribution={},
                channel_distribution={},
                hourly_distribution={},
            )

        # Basic counts
        total_events = len(events)
        sessions = set(e.session_id for e in events)
        total_sessions = len(sessions)

        # Drift rate
        if total_interactions is None and self._total_interactions:
            total_interactions = self._total_interactions()
        drift_rate = (
            total_events / total_interactions if total_interactions else 0.0
        )

        # Recovery rate
        recovery_attempts = [e for e in events if e.recovery_attempted]
        recovery_successes = [e for e in recovery_attempts if e.recovery_successful]
        recovery_rate = (
            len(recovery_successes) / len(recovery_attempts)
            if recovery_attempts
            else 0.0
        )

        # Drift scores
        scores = [e.drift_score for e in events]
        avg_score = statistics.mean(scores)
        median_score = statistics.median(scores)

        # Response times
        response_times = [e.response_time_ms for e in events if e.response_time_ms]
        avg_response_time = (
            statistics.mean(response_times) if response_times else None
        )

        # Distributions
        severity_dist = Counter(e.severity.value for e in events)
        drift_type_dist = Counter(e.drift_type.value for e in events)
        recovery_method_dist = Counter(e.recovery_method.value for e in events)
        channel_dist = Counter(e.channel or "unknown" for e in events)
        hourly_dist = Counter(e.timestamp.hour for e in events)

        return DriftMetrics(
            total_events=total_events,
            total_sessions=total_sessions,
            drift_rate=drift_rate,
            recovery_rate=recovery_rate,
            avg_drift_score=avg_score,
            median_drift_score=median_score,
            avg_response_time_ms=avg_response_time,
            severity_distribution=dict(severity_dist),
            drift_type_distribution=dict(drift_type_dist),
            recovery_method_distribution=dict(recovery_method_dist),
            channel_distribution=dict(channel_dist),
            hourly_distribution=dict(hourly_dist),
        )

    def analyze_patterns(
        self,
        time_range: Optional[TimeRange] = None,
        min_frequency: int = 3,
        min_confidence: float = 0.6,
    ) -> list[DriftPattern]:
        """Detect drift patterns in events.

        Analyzes events to find recurring patterns such as:
        - Common drift type sequences
        - Time-of-day patterns
        - Session patterns (e.g., drift escalation)
        - Intent-specific patterns

        Args:
            time_range: Time range to analyze
            min_frequency: Minimum occurrences to consider a pattern
            min_confidence: Minimum confidence threshold

        Returns:
            List of detected patterns
        """
        events = self._store.query(time_range=time_range)
        patterns: list[DriftPattern] = []
        pattern_counter = 0

        if len(events) < min_frequency:
            return patterns

        # Pattern 1: Dominant drift types
        drift_type_counts = Counter(e.drift_type for e in events)
        total = len(events)

        for drift_type, count in drift_type_counts.most_common(3):
            if count >= min_frequency:
                ratio = count / total
                if ratio >= 0.2:  # At least 20% of events
                    pattern_counter += 1
                    affected_sessions = len(
                        set(e.session_id for e in events if e.drift_type == drift_type)
                    )
                    sample_events = [
                        e.event_id for e in events if e.drift_type == drift_type
                    ][:5]

                    recommendations = self._get_drift_type_recommendations(drift_type)

                    patterns.append(
                        DriftPattern(
                            pattern_id=f"pattern_{pattern_counter:04d}",
                            pattern_type="dominant_drift_type",
                            description=f"{drift_type.value} drift accounts for {ratio:.0%} of events",
                            frequency=count,
                            confidence=min(ratio + 0.3, 1.0),
                            affected_sessions=affected_sessions,
                            sample_events=sample_events,
                            recommendations=recommendations,
                        )
                    )

        # Pattern 2: Time-based patterns (high drift hours)
        hourly_counts = Counter(e.timestamp.hour for e in events)
        avg_hourly = total / 24 if total > 24 else 1

        for hour, count in hourly_counts.items():
            if count >= min_frequency and count >= avg_hourly * 2:
                pattern_counter += 1
                affected_sessions = len(
                    set(e.session_id for e in events if e.timestamp.hour == hour)
                )
                sample_events = [
                    e.event_id for e in events if e.timestamp.hour == hour
                ][:5]

                patterns.append(
                    DriftPattern(
                        pattern_id=f"pattern_{pattern_counter:04d}",
                        pattern_type="temporal",
                        description=f"Elevated drift at hour {hour:02d}:00 ({count} events, {count/avg_hourly:.1f}x average)",
                        frequency=count,
                        confidence=min((count / avg_hourly) / 3, 1.0),
                        affected_sessions=affected_sessions,
                        sample_events=sample_events,
                        recommendations=[
                            f"Investigate user behavior patterns at hour {hour:02d}:00",
                            "Consider additional guidance during peak drift times",
                        ],
                    )
                )

        # Pattern 3: Recovery failure patterns
        failed_recoveries = [
            e for e in events if e.recovery_attempted and not e.recovery_successful
        ]
        if len(failed_recoveries) >= min_frequency:
            by_method = Counter(e.recovery_method for e in failed_recoveries)

            for method, count in by_method.most_common(2):
                if count >= min_frequency:
                    pattern_counter += 1
                    total_attempts = len(
                        [e for e in events if e.recovery_method == method]
                    )
                    failure_rate = count / total_attempts if total_attempts else 0
                    affected_sessions = len(
                        set(e.session_id for e in failed_recoveries if e.recovery_method == method)
                    )
                    sample_events = [
                        e.event_id
                        for e in failed_recoveries
                        if e.recovery_method == method
                    ][:5]

                    patterns.append(
                        DriftPattern(
                            pattern_id=f"pattern_{pattern_counter:04d}",
                            pattern_type="recovery_failure",
                            description=f"{method.value} recovery failing {failure_rate:.0%} of attempts",
                            frequency=count,
                            confidence=failure_rate,
                            affected_sessions=affected_sessions,
                            sample_events=sample_events,
                            recommendations=[
                                f"Review {method.value} recovery strategy",
                                "Consider alternative recovery approaches",
                                "Analyze failed recovery user inputs for patterns",
                            ],
                        )
                    )

        # Pattern 4: Session drift escalation (drift getting worse in session)
        session_events: dict[str, list[DriftAnalyticsEvent]] = defaultdict(list)
        for event in events:
            session_events[event.session_id].append(event)

        escalating_sessions = []
        for session_id, session_evts in session_events.items():
            if len(session_evts) >= 2:
                sorted_evts = sorted(session_evts, key=lambda e: e.timestamp)
                scores = [e.drift_score for e in sorted_evts]
                # Check if scores are increasing
                if all(scores[i] <= scores[i + 1] for i in range(len(scores) - 1)):
                    if scores[-1] - scores[0] >= 0.3:  # Significant escalation
                        escalating_sessions.append(session_id)

        if len(escalating_sessions) >= min_frequency:
            pattern_counter += 1
            sample_events = []
            for sid in escalating_sessions[:3]:
                sample_events.extend([e.event_id for e in session_events[sid][:2]])

            patterns.append(
                DriftPattern(
                    pattern_id=f"pattern_{pattern_counter:04d}",
                    pattern_type="drift_escalation",
                    description=f"Drift escalation detected in {len(escalating_sessions)} sessions",
                    frequency=len(escalating_sessions),
                    confidence=min(len(escalating_sessions) / len(session_events), 1.0),
                    affected_sessions=len(escalating_sessions),
                    sample_events=sample_events[:5],
                    recommendations=[
                        "Implement early intervention for drift",
                        "Consider proactive clarification before escalation",
                        "Review session flows that lead to escalation",
                    ],
                )
            )

        # Filter by confidence
        patterns = [p for p in patterns if p.confidence >= min_confidence]

        return patterns

    def _get_drift_type_recommendations(self, drift_type: DriftType) -> list[str]:
        """Get recommendations for addressing a drift type.

        Args:
            drift_type: The drift type

        Returns:
            List of recommendations
        """
        recommendations = {
            DriftType.SCOPE_EXPANSION: [
                "Review capability boundaries and consider expanding",
                "Improve redirect suggestions for common scope expansions",
                "Add clarification prompts for boundary cases",
            ],
            DriftType.DOMAIN_SHIFT: [
                "Analyze common domain shifts to identify training gaps",
                "Improve domain classification for clearer boundaries",
                "Consider partnerships for out-of-domain referrals",
            ],
            DriftType.ABSTRACTION_CLIMB: [
                "Add grounding prompts to make abstract requests concrete",
                "Provide examples to help users specify needs",
                "Consider supporting higher-level queries with guided flows",
            ],
            DriftType.PERSONALIZATION: [
                "Identify common personalization requests",
                "Consider adding user preference storage",
                "Improve messaging about data requirements",
            ],
            DriftType.TEMPORAL_DRIFT: [
                "Clearly communicate knowledge cutoff dates",
                "Add real-time data integrations where possible",
                "Improve temporal reference handling",
            ],
            DriftType.AMBIGUOUS: [
                "Improve clarification question quality",
                "Add more specific prompts for common ambiguities",
                "Consider multi-intent handling capabilities",
            ],
            DriftType.NONE: [],
        }
        return recommendations.get(drift_type, ["Investigate drift patterns further"])

    def get_summary(
        self,
        time_range: Optional[TimeRange] = None,
        total_interactions: Optional[int] = None,
    ) -> DriftSummary:
        """Generate comprehensive drift summary.

        Args:
            time_range: Time range to analyze
            total_interactions: Total interactions for rate calculation

        Returns:
            Complete drift summary
        """
        if time_range is None:
            time_range = TimeRange.last_days(7)

        events = self._store.query(time_range=time_range)
        metrics = self.calculate_metrics(
            time_range=time_range, total_interactions=total_interactions
        )
        patterns = self.analyze_patterns(time_range=time_range)

        # Top drift types
        drift_type_counts = Counter(e.drift_type.value for e in events)
        top_drift_types = drift_type_counts.most_common(5)

        # Top affected intents
        intent_counts = Counter(
            e.original_intent for e in events if e.original_intent
        )
        top_intents = intent_counts.most_common(5)

        # Problematic sessions (high drift rate or severity)
        session_events: dict[str, list[DriftAnalyticsEvent]] = defaultdict(list)
        for event in events:
            session_events[event.session_id].append(event)

        session_scores = []
        for session_id, session_evts in session_events.items():
            avg_score = statistics.mean(e.drift_score for e in session_evts)
            session_scores.append((session_id, avg_score))

        session_scores.sort(key=lambda x: x[1], reverse=True)
        problematic_sessions = session_scores[:10]

        return DriftSummary(
            time_range=time_range,
            metrics=metrics,
            patterns=patterns,
            top_drift_types=top_drift_types,
            top_intents_affected=top_intents,
            problematic_sessions=problematic_sessions,
            generated_at=datetime.now(timezone.utc),
        )

    # ============================================
    # Export Methods
    # ============================================

    def export_json(
        self,
        time_range: Optional[TimeRange] = None,
        include_summary: bool = True,
        indent: int = 2,
    ) -> str:
        """Export events and summary to JSON.

        Args:
            time_range: Time range to export
            include_summary: Whether to include summary
            indent: JSON indentation

        Returns:
            JSON string
        """
        events = self._store.query(time_range=time_range)

        data: dict[str, Any] = {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "event_count": len(events),
            "events": [e.to_dict() for e in events],
        }

        if include_summary and events:
            summary = self.get_summary(time_range=time_range)
            data["summary"] = summary.to_dict()

        return json.dumps(data, indent=indent)

    def export_csv(
        self,
        time_range: Optional[TimeRange] = None,
    ) -> str:
        """Export events to CSV format.

        Args:
            time_range: Time range to export

        Returns:
            CSV string
        """
        events = self._store.query(time_range=time_range)

        output = StringIO()
        fieldnames = [
            "event_id",
            "session_id",
            "turn_id",
            "timestamp",
            "drift_type",
            "drift_score",
            "severity",
            "user_input",
            "detected_intent",
            "original_intent",
            "recovery_method",
            "recovery_attempted",
            "recovery_successful",
            "redirect_accepted",
            "response_time_ms",
            "user_id",
            "channel",
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for event in events:
            row = event.to_dict()
            # Flatten enums to strings
            row["timestamp"] = event.timestamp.isoformat()
            row["drift_type"] = event.drift_type.value
            row["severity"] = event.severity.value
            row["recovery_method"] = event.recovery_method.value
            writer.writerow(row)

        return output.getvalue()

    def clear(self) -> None:
        """Clear all stored events."""
        self._store.clear()


# ============================================
# Factory Functions
# ============================================


def create_drift_analytics(
    store: Optional[DriftEventStore] = None,
    max_events: int = 10000,
    total_interactions: Optional[Callable[[], int]] = None,
) -> DriftAnalytics:
    """Create a DriftAnalytics instance.

    Args:
        store: Optional custom storage backend
        max_events: Max events for in-memory store
        total_interactions: Callable returning total interactions

    Returns:
        Configured DriftAnalytics instance
    """
    if store is None:
        store = InMemoryDriftEventStore(max_events=max_events)
    return DriftAnalytics(store=store, total_interactions=total_interactions)
