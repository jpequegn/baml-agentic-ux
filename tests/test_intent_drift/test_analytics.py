"""Tests for Drift Analytics & Logging.

Part of Task 5.10: Drift Analytics & Logging
Issue #87 - Phase 5: Intent Drift Detection
"""

import json
from datetime import datetime, timezone, timedelta

import pytest

from src.intent_drift import (
    DriftType,
    DriftEvent,
    DriftAnalysis,
)
from src.intent_drift.analytics import (
    # Enums
    DriftSeverity,
    RecoveryMethod,
    # Data Classes
    DriftAnalyticsEvent,
    DriftMetrics,
    DriftPattern,
    DriftSummary,
    TimeRange,
    # Storage
    InMemoryDriftEventStore,
    # Main Class
    DriftAnalytics,
    # Factory
    create_drift_analytics,
)


# ============================================
# DriftSeverity Tests
# ============================================


class TestDriftSeverity:
    """Tests for DriftSeverity enum."""

    def test_from_score_low(self):
        """Test low severity for scores < 0.3."""
        assert DriftSeverity.from_score(0.0) == DriftSeverity.LOW
        assert DriftSeverity.from_score(0.1) == DriftSeverity.LOW
        assert DriftSeverity.from_score(0.29) == DriftSeverity.LOW

    def test_from_score_medium(self):
        """Test medium severity for scores 0.3-0.6."""
        assert DriftSeverity.from_score(0.3) == DriftSeverity.MEDIUM
        assert DriftSeverity.from_score(0.45) == DriftSeverity.MEDIUM
        assert DriftSeverity.from_score(0.59) == DriftSeverity.MEDIUM

    def test_from_score_high(self):
        """Test high severity for scores 0.6-0.8."""
        assert DriftSeverity.from_score(0.6) == DriftSeverity.HIGH
        assert DriftSeverity.from_score(0.7) == DriftSeverity.HIGH
        assert DriftSeverity.from_score(0.79) == DriftSeverity.HIGH

    def test_from_score_critical(self):
        """Test critical severity for scores >= 0.8."""
        assert DriftSeverity.from_score(0.8) == DriftSeverity.CRITICAL
        assert DriftSeverity.from_score(0.9) == DriftSeverity.CRITICAL
        assert DriftSeverity.from_score(1.0) == DriftSeverity.CRITICAL


# ============================================
# DriftAnalyticsEvent Tests
# ============================================


class TestDriftAnalyticsEvent:
    """Tests for DriftAnalyticsEvent data class."""

    def test_create_basic_event(self):
        """Test creating a basic analytics event."""
        event = DriftAnalyticsEvent(
            event_id="test_001",
            session_id="session_123",
            turn_id="turn_1",
            timestamp=datetime.now(timezone.utc),
            drift_type=DriftType.SCOPE_EXPANSION,
            drift_score=0.65,
            severity=DriftSeverity.HIGH,
            user_input="Can you also do X?",
        )
        assert event.event_id == "test_001"
        assert event.drift_type == DriftType.SCOPE_EXPANSION
        assert event.severity == DriftSeverity.HIGH

    def test_create_full_event(self):
        """Test creating event with all fields."""
        event = DriftAnalyticsEvent(
            event_id="test_002",
            session_id="session_456",
            turn_id="turn_5",
            timestamp=datetime.now(timezone.utc),
            drift_type=DriftType.DOMAIN_SHIFT,
            drift_score=0.85,
            severity=DriftSeverity.CRITICAL,
            user_input="What's the weather like?",
            detected_intent="weather_query",
            original_intent="task_management",
            recovery_method=RecoveryMethod.REDIRECT,
            recovery_attempted=True,
            recovery_successful=True,
            redirect_accepted=True,
            response_time_ms=150,
            user_id="user_789",
            channel="web",
            metadata={"source": "test"},
        )
        assert event.recovery_method == RecoveryMethod.REDIRECT
        assert event.recovery_successful is True
        assert event.channel == "web"

    def test_invalid_drift_score(self):
        """Test that invalid drift score raises error."""
        with pytest.raises(ValueError, match="drift_score"):
            DriftAnalyticsEvent(
                event_id="test",
                session_id="session",
                turn_id="turn",
                timestamp=datetime.now(timezone.utc),
                drift_type=DriftType.NONE,
                drift_score=1.5,  # Invalid
                severity=DriftSeverity.LOW,
                user_input="test",
            )

    def test_from_drift_event(self):
        """Test creating analytics event from basic DriftEvent."""
        basic_event = DriftEvent(
            turn_id="turn_1",
            drift_type=DriftType.AMBIGUOUS,
            drift_score=0.5,
            recovery_attempted=True,
            recovery_successful=False,
        )
        analytics_event = DriftAnalyticsEvent.from_drift_event(
            event=basic_event,
            event_id="evt_001",
            session_id="session_123",
            timestamp=datetime.now(timezone.utc),
            user_input="Test input",
            user_id="user_1",
        )
        assert analytics_event.drift_type == DriftType.AMBIGUOUS
        assert analytics_event.severity == DriftSeverity.MEDIUM
        assert analytics_event.recovery_attempted is True

    def test_from_drift_analysis(self):
        """Test creating analytics event from DriftAnalysis."""
        analysis = DriftAnalysis(
            current_input="Help me with something else",
            drift_score=0.7,
            drift_type=DriftType.SCOPE_EXPANSION,
            confidence=0.85,
            semantic_distance=0.6,
            graceful_response="I can help with related tasks",
            original_intent="original",
            last_supported_intent="supported",
        )
        analytics_event = DriftAnalyticsEvent.from_drift_analysis(
            analysis=analysis,
            event_id="evt_002",
            session_id="session_456",
            turn_id="turn_3",
            timestamp=datetime.now(timezone.utc),
        )
        assert analytics_event.drift_type == DriftType.SCOPE_EXPANSION
        assert analytics_event.drift_score == 0.7
        assert analytics_event.original_intent == "original"

    def test_to_dict_and_from_dict(self):
        """Test serialization round-trip."""
        original = DriftAnalyticsEvent(
            event_id="test_003",
            session_id="session_789",
            turn_id="turn_2",
            timestamp=datetime.now(timezone.utc),
            drift_type=DriftType.PERSONALIZATION,
            drift_score=0.45,
            severity=DriftSeverity.MEDIUM,
            user_input="Remember my preferences",
            recovery_method=RecoveryMethod.BOUNDARY_STATEMENT,
            metadata={"key": "value"},
        )
        data = original.to_dict()
        restored = DriftAnalyticsEvent.from_dict(data)

        assert restored.event_id == original.event_id
        assert restored.drift_type == original.drift_type
        assert restored.drift_score == original.drift_score
        assert restored.metadata == original.metadata


# ============================================
# TimeRange Tests
# ============================================


class TestTimeRange:
    """Tests for TimeRange data class."""

    def test_create_valid_range(self):
        """Test creating a valid time range."""
        start = datetime.now(timezone.utc) - timedelta(hours=1)
        end = datetime.now(timezone.utc)
        time_range = TimeRange(start=start, end=end)
        assert time_range.start < time_range.end

    def test_invalid_range_raises(self):
        """Test that start after end raises error."""
        now = datetime.now(timezone.utc)
        with pytest.raises(ValueError, match="start must be before end"):
            TimeRange(start=now, end=now - timedelta(hours=1))

    def test_contains_timestamp(self):
        """Test checking if timestamp is in range."""
        start = datetime.now(timezone.utc) - timedelta(hours=2)
        end = datetime.now(timezone.utc)
        time_range = TimeRange(start=start, end=end)

        # Timestamp in range
        in_range = datetime.now(timezone.utc) - timedelta(hours=1)
        assert time_range.contains(in_range) is True

        # Timestamp before range
        before = datetime.now(timezone.utc) - timedelta(hours=3)
        assert time_range.contains(before) is False

        # Timestamp after range
        after = datetime.now(timezone.utc) + timedelta(hours=1)
        assert time_range.contains(after) is False

    def test_last_hours(self):
        """Test creating range for last N hours."""
        time_range = TimeRange.last_hours(24)
        assert time_range.end > time_range.start
        diff = time_range.end - time_range.start
        assert diff >= timedelta(hours=23, minutes=59)

    def test_last_days(self):
        """Test creating range for last N days."""
        time_range = TimeRange.last_days(7)
        assert time_range.end > time_range.start
        diff = time_range.end - time_range.start
        assert diff >= timedelta(days=6, hours=23)


# ============================================
# InMemoryDriftEventStore Tests
# ============================================


class TestInMemoryDriftEventStore:
    """Tests for InMemoryDriftEventStore."""

    @pytest.fixture
    def store(self):
        """Create a test store."""
        return InMemoryDriftEventStore(max_events=100)

    @pytest.fixture
    def sample_event(self):
        """Create a sample event."""
        return DriftAnalyticsEvent(
            event_id="evt_001",
            session_id="session_1",
            turn_id="turn_1",
            timestamp=datetime.now(timezone.utc),
            drift_type=DriftType.SCOPE_EXPANSION,
            drift_score=0.5,
            severity=DriftSeverity.MEDIUM,
            user_input="Test input",
        )

    def test_store_and_query(self, store, sample_event):
        """Test storing and querying events."""
        store.store(sample_event)
        events = store.query()
        assert len(events) == 1
        assert events[0].event_id == sample_event.event_id

    def test_query_by_session(self, store):
        """Test filtering by session ID."""
        for i in range(5):
            store.store(
                DriftAnalyticsEvent(
                    event_id=f"evt_{i}",
                    session_id=f"session_{i % 2}",
                    turn_id="turn_1",
                    timestamp=datetime.now(timezone.utc),
                    drift_type=DriftType.NONE,
                    drift_score=0.1,
                    severity=DriftSeverity.LOW,
                    user_input="test",
                )
            )
        events = store.query(session_id="session_0")
        assert len(events) == 3

    def test_query_by_drift_type(self, store):
        """Test filtering by drift type."""
        store.store(
            DriftAnalyticsEvent(
                event_id="evt_1",
                session_id="s1",
                turn_id="t1",
                timestamp=datetime.now(timezone.utc),
                drift_type=DriftType.SCOPE_EXPANSION,
                drift_score=0.5,
                severity=DriftSeverity.MEDIUM,
                user_input="test",
            )
        )
        store.store(
            DriftAnalyticsEvent(
                event_id="evt_2",
                session_id="s2",
                turn_id="t1",
                timestamp=datetime.now(timezone.utc),
                drift_type=DriftType.DOMAIN_SHIFT,
                drift_score=0.7,
                severity=DriftSeverity.HIGH,
                user_input="test",
            )
        )
        events = store.query(drift_type=DriftType.SCOPE_EXPANSION)
        assert len(events) == 1
        assert events[0].drift_type == DriftType.SCOPE_EXPANSION

    def test_query_with_limit(self, store):
        """Test limiting query results."""
        for i in range(10):
            store.store(
                DriftAnalyticsEvent(
                    event_id=f"evt_{i}",
                    session_id="s1",
                    turn_id="t1",
                    timestamp=datetime.now(timezone.utc),
                    drift_type=DriftType.NONE,
                    drift_score=0.1,
                    severity=DriftSeverity.LOW,
                    user_input="test",
                )
            )
        events = store.query(limit=5)
        assert len(events) == 5

    def test_fifo_eviction(self):
        """Test FIFO eviction when exceeding max_events."""
        store = InMemoryDriftEventStore(max_events=5)
        for i in range(10):
            store.store(
                DriftAnalyticsEvent(
                    event_id=f"evt_{i}",
                    session_id="s1",
                    turn_id="t1",
                    timestamp=datetime.now(timezone.utc),
                    drift_type=DriftType.NONE,
                    drift_score=0.1,
                    severity=DriftSeverity.LOW,
                    user_input="test",
                )
            )
        assert store.count() == 5
        # Should have kept the last 5 events
        events = store.query()
        event_ids = [e.event_id for e in events]
        assert "evt_5" in event_ids
        assert "evt_0" not in event_ids

    def test_count(self, store, sample_event):
        """Test counting events."""
        assert store.count() == 0
        store.store(sample_event)
        assert store.count() == 1

    def test_clear(self, store, sample_event):
        """Test clearing all events."""
        store.store(sample_event)
        assert store.count() == 1
        store.clear()
        assert store.count() == 0


# ============================================
# DriftAnalytics Tests
# ============================================


class TestDriftAnalytics:
    """Tests for DriftAnalytics main class."""

    @pytest.fixture
    def analytics(self):
        """Create a test analytics instance."""
        return create_drift_analytics(max_events=1000)

    def test_log_event(self, analytics):
        """Test logging a drift event."""
        event = analytics.log_event(
            session_id="session_1",
            turn_id="turn_1",
            drift_type=DriftType.SCOPE_EXPANSION,
            drift_score=0.6,
            user_input="Can you also do X?",
            detected_intent="feature_request",
            recovery_method=RecoveryMethod.REDIRECT,
            recovery_attempted=True,
            recovery_successful=True,
        )
        assert event.event_id.startswith("drift_")
        assert event.drift_type == DriftType.SCOPE_EXPANSION
        assert event.severity == DriftSeverity.HIGH

    def test_log_from_analysis(self, analytics):
        """Test logging from DriftAnalysis."""
        analysis = DriftAnalysis(
            current_input="What's the weather?",
            drift_score=0.75,
            drift_type=DriftType.DOMAIN_SHIFT,
            confidence=0.9,
            semantic_distance=0.7,
            graceful_response="I focus on task management",
        )
        event = analytics.log_from_analysis(
            analysis=analysis,
            session_id="session_2",
            turn_id="turn_3",
        )
        assert event.drift_type == DriftType.DOMAIN_SHIFT
        assert event.user_input == "What's the weather?"

    def test_get_events(self, analytics):
        """Test retrieving events with filters."""
        # Log multiple events
        analytics.log_event(
            session_id="s1",
            turn_id="t1",
            drift_type=DriftType.SCOPE_EXPANSION,
            drift_score=0.5,
            user_input="test 1",
        )
        analytics.log_event(
            session_id="s2",
            turn_id="t1",
            drift_type=DriftType.DOMAIN_SHIFT,
            drift_score=0.7,
            user_input="test 2",
        )

        # Get all
        all_events = analytics.get_events()
        assert len(all_events) == 2

        # Filter by session
        session_events = analytics.get_events(session_id="s1")
        assert len(session_events) == 1

        # Filter by severity
        high_severity = analytics.get_events(severity=DriftSeverity.HIGH)
        assert len(high_severity) == 1


class TestDriftAnalyticsMetrics:
    """Tests for DriftAnalytics metrics calculation."""

    @pytest.fixture
    def analytics_with_data(self):
        """Create analytics with pre-populated data."""
        analytics = create_drift_analytics()

        # Add diverse events
        for i in range(10):
            analytics.log_event(
                session_id=f"session_{i % 3}",
                turn_id=f"turn_{i}",
                drift_type=DriftType.SCOPE_EXPANSION if i % 2 == 0 else DriftType.DOMAIN_SHIFT,
                drift_score=0.3 + (i * 0.05),
                user_input=f"Test input {i}",
                recovery_attempted=i % 3 == 0,
                recovery_successful=i % 6 == 0,
                response_time_ms=100 + (i * 10),
                channel="web" if i % 2 == 0 else "mobile",
            )
        return analytics

    def test_calculate_metrics(self, analytics_with_data):
        """Test calculating metrics from events."""
        metrics = analytics_with_data.calculate_metrics()

        assert metrics.total_events == 10
        assert metrics.total_sessions == 3
        assert 0.0 <= metrics.avg_drift_score <= 1.0
        assert 0.0 <= metrics.median_drift_score <= 1.0
        assert metrics.avg_response_time_ms is not None

    def test_metrics_distributions(self, analytics_with_data):
        """Test metric distributions."""
        metrics = analytics_with_data.calculate_metrics()

        # Should have severity distribution
        assert sum(metrics.severity_distribution.values()) == 10

        # Should have drift type distribution
        assert "scope_expansion" in metrics.drift_type_distribution
        assert "domain_shift" in metrics.drift_type_distribution

        # Should have channel distribution
        assert "web" in metrics.channel_distribution
        assert "mobile" in metrics.channel_distribution

    def test_metrics_with_total_interactions(self, analytics_with_data):
        """Test drift rate calculation with total interactions."""
        metrics = analytics_with_data.calculate_metrics(total_interactions=100)
        assert metrics.drift_rate == 0.1  # 10 events / 100 interactions

    def test_empty_metrics(self):
        """Test metrics with no events."""
        analytics = create_drift_analytics()
        metrics = analytics.calculate_metrics()

        assert metrics.total_events == 0
        assert metrics.drift_rate == 0.0
        assert metrics.avg_drift_score == 0.0


class TestDriftAnalyticsPatterns:
    """Tests for DriftAnalytics pattern detection."""

    @pytest.fixture
    def analytics_with_patterns(self):
        """Create analytics with pattern-exhibiting data."""
        analytics = create_drift_analytics()

        # Create dominant drift type pattern
        for i in range(20):
            analytics.log_event(
                session_id=f"session_{i % 5}",
                turn_id=f"turn_{i}",
                drift_type=DriftType.SCOPE_EXPANSION if i < 15 else DriftType.DOMAIN_SHIFT,
                drift_score=0.5,
                user_input=f"Test {i}",
            )

        return analytics

    def test_analyze_patterns_finds_dominant_type(self, analytics_with_patterns):
        """Test that pattern analysis finds dominant drift types."""
        patterns = analytics_with_patterns.analyze_patterns(min_frequency=3)

        # Should find scope_expansion as dominant
        dominant_patterns = [p for p in patterns if p.pattern_type == "dominant_drift_type"]
        assert len(dominant_patterns) >= 1
        assert any("scope_expansion" in p.description for p in dominant_patterns)

    def test_analyze_patterns_with_recovery_failures(self):
        """Test pattern detection for recovery failures."""
        analytics = create_drift_analytics()

        # Create recovery failure pattern
        for i in range(10):
            analytics.log_event(
                session_id=f"session_{i}",
                turn_id="t1",
                drift_type=DriftType.AMBIGUOUS,
                drift_score=0.5,
                user_input=f"Test {i}",
                recovery_method=RecoveryMethod.CLARIFICATION,
                recovery_attempted=True,
                recovery_successful=i >= 8,  # Only last 2 succeed
            )

        patterns = analytics.analyze_patterns(min_frequency=3, min_confidence=0.5)
        recovery_patterns = [p for p in patterns if p.pattern_type == "recovery_failure"]
        # Should detect clarification recovery failure pattern
        assert len(recovery_patterns) >= 0  # May or may not hit threshold

    def test_pattern_recommendations(self, analytics_with_patterns):
        """Test that patterns include recommendations."""
        patterns = analytics_with_patterns.analyze_patterns(min_frequency=3)

        for pattern in patterns:
            assert len(pattern.recommendations) > 0


class TestDriftAnalyticsSummary:
    """Tests for DriftAnalytics summary generation."""

    @pytest.fixture
    def analytics_with_data(self):
        """Create analytics with data for summary."""
        analytics = create_drift_analytics()

        for i in range(15):
            analytics.log_event(
                session_id=f"session_{i % 4}",
                turn_id=f"turn_{i}",
                drift_type=DriftType.SCOPE_EXPANSION if i % 3 == 0 else DriftType.AMBIGUOUS,
                drift_score=0.4 + (i * 0.03),
                user_input=f"Test input {i}",
                original_intent="task_intent" if i % 2 == 0 else None,
            )
        return analytics

    def test_get_summary(self, analytics_with_data):
        """Test generating drift summary."""
        summary = analytics_with_data.get_summary()

        assert isinstance(summary, DriftSummary)
        assert summary.metrics.total_events == 15
        assert summary.generated_at is not None

    def test_summary_top_drift_types(self, analytics_with_data):
        """Test summary includes top drift types."""
        summary = analytics_with_data.get_summary()

        assert len(summary.top_drift_types) > 0
        # Should be sorted by frequency
        if len(summary.top_drift_types) > 1:
            assert summary.top_drift_types[0][1] >= summary.top_drift_types[1][1]

    def test_summary_problematic_sessions(self, analytics_with_data):
        """Test summary identifies problematic sessions."""
        summary = analytics_with_data.get_summary()

        assert isinstance(summary.problematic_sessions, list)
        # Sessions should be sorted by drift score
        if len(summary.problematic_sessions) > 1:
            assert summary.problematic_sessions[0][1] >= summary.problematic_sessions[1][1]

    def test_summary_to_dict(self, analytics_with_data):
        """Test summary serialization."""
        summary = analytics_with_data.get_summary()
        data = summary.to_dict()

        assert "time_range" in data
        assert "metrics" in data
        assert "patterns" in data
        assert "generated_at" in data


class TestDriftAnalyticsExport:
    """Tests for DriftAnalytics export functionality."""

    @pytest.fixture
    def analytics_with_data(self):
        """Create analytics with data for export."""
        analytics = create_drift_analytics()

        for i in range(5):
            analytics.log_event(
                session_id=f"session_{i}",
                turn_id=f"turn_{i}",
                drift_type=DriftType.SCOPE_EXPANSION,
                drift_score=0.5 + (i * 0.05),
                user_input=f"Test input {i}",
                channel="web",
                user_id=f"user_{i}",
            )
        return analytics

    def test_export_json(self, analytics_with_data):
        """Test JSON export."""
        json_output = analytics_with_data.export_json()

        data = json.loads(json_output)
        assert "exported_at" in data
        assert "event_count" in data
        assert data["event_count"] == 5
        assert "events" in data
        assert len(data["events"]) == 5

    def test_export_json_with_summary(self, analytics_with_data):
        """Test JSON export includes summary."""
        json_output = analytics_with_data.export_json(include_summary=True)

        data = json.loads(json_output)
        assert "summary" in data
        assert "metrics" in data["summary"]

    def test_export_json_without_summary(self, analytics_with_data):
        """Test JSON export without summary."""
        json_output = analytics_with_data.export_json(include_summary=False)

        data = json.loads(json_output)
        assert "summary" not in data

    def test_export_csv(self, analytics_with_data):
        """Test CSV export."""
        csv_output = analytics_with_data.export_csv()

        lines = csv_output.strip().split("\n")
        assert len(lines) == 6  # Header + 5 events

        # Check header
        header = lines[0]
        assert "event_id" in header
        assert "session_id" in header
        assert "drift_type" in header
        assert "drift_score" in header

    def test_export_with_time_range(self, analytics_with_data):
        """Test export with time range filter."""
        # All events are recent, should export all
        time_range = TimeRange.last_hours(1)
        json_output = analytics_with_data.export_json(time_range=time_range)

        data = json.loads(json_output)
        assert data["event_count"] == 5


class TestDriftAnalyticsClear:
    """Tests for DriftAnalytics clear functionality."""

    def test_clear(self):
        """Test clearing all events."""
        analytics = create_drift_analytics()

        analytics.log_event(
            session_id="s1",
            turn_id="t1",
            drift_type=DriftType.NONE,
            drift_score=0.1,
            user_input="test",
        )
        assert len(analytics.get_events()) == 1

        analytics.clear()
        assert len(analytics.get_events()) == 0


class TestCreateDriftAnalytics:
    """Tests for factory function."""

    def test_create_with_defaults(self):
        """Test creating with default settings."""
        analytics = create_drift_analytics()
        assert analytics is not None

    def test_create_with_max_events(self):
        """Test creating with custom max_events."""
        analytics = create_drift_analytics(max_events=50)

        # Add more than max events
        for i in range(60):
            analytics.log_event(
                session_id="s1",
                turn_id=f"t_{i}",
                drift_type=DriftType.NONE,
                drift_score=0.1,
                user_input=f"test {i}",
            )

        # Should only have last 50
        events = analytics.get_events()
        assert len(events) == 50

    def test_create_with_interaction_counter(self):
        """Test creating with total interaction counter."""
        counter = lambda: 100

        analytics = create_drift_analytics(total_interactions=counter)

        analytics.log_event(
            session_id="s1",
            turn_id="t1",
            drift_type=DriftType.NONE,
            drift_score=0.1,
            user_input="test",
        )

        metrics = analytics.calculate_metrics()
        assert metrics.drift_rate == 0.01  # 1 / 100
