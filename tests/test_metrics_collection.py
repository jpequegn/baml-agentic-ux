"""
Tests for Metrics Collection (Issue #44)
Phase 2: Adaptive Interface Personalization - Task 2.2

Tests validate:
- Interaction recording
- Metrics window calculation
- Frustration detection
- Mastery detection
- Privacy modes
- BAML type generation
"""

import pytest
from src.lui_simulator.metrics import (
    MetricsCollector,
    MetricsStoreConfig,
    InteractionRecord,
    MetricsWindow,
    FrustrationSignals,
    MasterySignals,
    InteractionOutcome,
    TrendDirection,
    SignalSeverity,
    PrivacyMode,
)


# Also test BAML-generated types
from baml_client.types import (
    InteractionOutcome as BAMLInteractionOutcome,
    TrendDirection as BAMLTrendDirection,
    SignalType,
    SignalSeverity as BAMLSignalSeverity,
    PrivacyMode as BAMLPrivacyMode,
    MetricsEventType,
    InteractionRecord as BAMLInteractionRecord,
    MetricsWindow as BAMLMetricsWindow,
    FrustrationSignals as BAMLFrustrationSignals,
    MasterySignals as BAMLMasterySignals,
    MetricsStoreConfig as BAMLMetricsStoreConfig,
    BehavioralAnalysis,
    ExpertiseAdjustment,
)


class TestInteractionOutcomeEnum:
    """Test InteractionOutcome enum values"""

    def test_success_value(self):
        assert InteractionOutcome.SUCCESS.value == "SUCCESS"

    def test_partial_success_value(self):
        assert InteractionOutcome.PARTIAL_SUCCESS.value == "PARTIAL_SUCCESS"

    def test_failure_value(self):
        assert InteractionOutcome.FAILURE.value == "FAILURE"

    def test_abandoned_value(self):
        assert InteractionOutcome.ABANDONED.value == "ABANDONED"

    def test_help_escalation_value(self):
        assert InteractionOutcome.HELP_ESCALATION.value == "HELP_ESCALATION"


class TestTrendDirectionEnum:
    """Test TrendDirection enum values"""

    def test_improving_value(self):
        assert TrendDirection.IMPROVING.value == "IMPROVING"

    def test_stable_value(self):
        assert TrendDirection.STABLE.value == "STABLE"

    def test_declining_value(self):
        assert TrendDirection.DECLINING.value == "DECLINING"


class TestPrivacyModeEnum:
    """Test PrivacyMode enum values"""

    def test_full_value(self):
        assert PrivacyMode.FULL.value == "FULL"

    def test_aggregate_only_value(self):
        assert PrivacyMode.AGGREGATE_ONLY.value == "AGGREGATE_ONLY"

    def test_session_only_value(self):
        assert PrivacyMode.SESSION_ONLY.value == "SESSION_ONLY"

    def test_disabled_value(self):
        assert PrivacyMode.DISABLED.value == "DISABLED"


class TestMetricsCollectorInit:
    """Test MetricsCollector initialization"""

    def test_default_init(self):
        collector = MetricsCollector()
        assert collector.session_id is not None
        assert collector.config.privacy_mode == PrivacyMode.FULL

    def test_custom_session_id(self):
        collector = MetricsCollector(session_id="test-session-123")
        assert collector.session_id == "test-session-123"

    def test_custom_config(self):
        config = MetricsStoreConfig(
            privacy_mode=PrivacyMode.AGGREGATE_ONLY,
            retention_days=30,
        )
        collector = MetricsCollector(config=config)
        assert collector.config.privacy_mode == PrivacyMode.AGGREGATE_ONLY
        assert collector.config.retention_days == 30


class TestRecordInteraction:
    """Test interaction recording"""

    def test_record_successful_interaction(self):
        collector = MetricsCollector()
        record = collector.record_interaction(
            intent_detected="create_task",
            intent_confidence=0.95,
            parameters_provided=3,
            parameters_required=3,
            outcome=InteractionOutcome.SUCCESS,
            completion_time_ms=1500,
        )
        assert record.intent_detected == "create_task"
        assert record.outcome == InteractionOutcome.SUCCESS
        assert record.completion_time_ms == 1500

    def test_record_with_errors(self):
        collector = MetricsCollector()
        record = collector.record_interaction(
            intent_detected="delete_task",
            intent_confidence=0.8,
            parameters_provided=1,
            parameters_required=2,
            outcome=InteractionOutcome.FAILURE,
            completion_time_ms=3000,
            error_count=2,
            retries=1,
        )
        assert record.error_count == 2
        assert record.retries == 1
        assert record.outcome == InteractionOutcome.FAILURE

    def test_record_with_help(self):
        collector = MetricsCollector()
        record = collector.record_interaction(
            intent_detected="search_tasks",
            intent_confidence=0.6,
            parameters_provided=0,
            parameters_required=1,
            outcome=InteractionOutcome.HELP_ESCALATION,
            completion_time_ms=5000,
            help_requested=True,
            disambiguation_needed=True,
        )
        assert record.help_requested is True
        assert record.disambiguation_needed is True

    def test_record_with_shortcut(self):
        collector = MetricsCollector()
        record = collector.record_interaction(
            intent_detected="quick_add",
            intent_confidence=0.99,
            parameters_provided=2,
            parameters_required=2,
            outcome=InteractionOutcome.SUCCESS,
            completion_time_ms=500,
            used_shortcut=True,
            input_length=15,
        )
        assert record.used_shortcut is True
        assert record.input_length == 15

    def test_consecutive_error_tracking(self):
        collector = MetricsCollector()

        # Record 3 failures
        for _ in range(3):
            collector.record_interaction(
                intent_detected="failing_intent",
                intent_confidence=0.5,
                parameters_provided=0,
                parameters_required=1,
                outcome=InteractionOutcome.FAILURE,
                completion_time_ms=1000,
            )

        assert collector._consecutive_errors == 3
        assert collector._consecutive_successes == 0

    def test_consecutive_success_tracking(self):
        collector = MetricsCollector()

        # Record 5 successes
        for _ in range(5):
            collector.record_interaction(
                intent_detected="good_intent",
                intent_confidence=0.95,
                parameters_provided=1,
                parameters_required=1,
                outcome=InteractionOutcome.SUCCESS,
                completion_time_ms=1000,
            )

        assert collector._consecutive_successes == 5
        assert collector._consecutive_errors == 0

    def test_consecutive_reset_on_success(self):
        collector = MetricsCollector()

        # Record failures then success
        for _ in range(3):
            collector.record_interaction(
                intent_detected="failing",
                intent_confidence=0.5,
                parameters_provided=0,
                parameters_required=1,
                outcome=InteractionOutcome.FAILURE,
                completion_time_ms=1000,
            )

        collector.record_interaction(
            intent_detected="success",
            intent_confidence=0.95,
            parameters_provided=1,
            parameters_required=1,
            outcome=InteractionOutcome.SUCCESS,
            completion_time_ms=1000,
        )

        assert collector._consecutive_errors == 0
        assert collector._consecutive_successes == 1


class TestWindowedMetrics:
    """Test metrics window calculation"""

    def test_empty_window(self):
        collector = MetricsCollector()
        window = collector.get_windowed_metrics()

        assert window.interaction_count == 0
        assert window.success_rate == 0.0
        assert window.success_trend == TrendDirection.STABLE

    def test_window_with_interactions(self):
        collector = MetricsCollector()

        # Add 10 successful interactions
        for i in range(10):
            collector.record_interaction(
                intent_detected=f"intent_{i}",
                intent_confidence=0.9,
                parameters_provided=2,
                parameters_required=2,
                outcome=InteractionOutcome.SUCCESS,
                completion_time_ms=1000 + i * 100,
            )

        window = collector.get_windowed_metrics(10)

        assert window.interaction_count == 10
        assert window.success_rate == 1.0
        assert window.failure_rate == 0.0
        assert window.avg_completion_time_ms > 0

    def test_mixed_outcomes(self):
        collector = MetricsCollector()

        # Add 5 successful, 3 failed, 2 abandoned
        for _ in range(5):
            collector.record_interaction(
                intent_detected="success",
                intent_confidence=0.9,
                parameters_provided=1,
                parameters_required=1,
                outcome=InteractionOutcome.SUCCESS,
                completion_time_ms=1000,
            )
        for _ in range(3):
            collector.record_interaction(
                intent_detected="failure",
                intent_confidence=0.5,
                parameters_provided=0,
                parameters_required=1,
                outcome=InteractionOutcome.FAILURE,
                completion_time_ms=2000,
            )
        for _ in range(2):
            collector.record_interaction(
                intent_detected="abandoned",
                intent_confidence=0.6,
                parameters_provided=0,
                parameters_required=1,
                outcome=InteractionOutcome.ABANDONED,
                completion_time_ms=3000,
            )

        window = collector.get_windowed_metrics(10)

        assert window.interaction_count == 10
        assert window.success_rate == 0.5
        assert window.failure_rate == 0.3
        assert window.abandonment_rate == 0.2

    def test_window_size_limit(self):
        collector = MetricsCollector()

        # Add 30 interactions
        for i in range(30):
            collector.record_interaction(
                intent_detected=f"intent_{i}",
                intent_confidence=0.9,
                parameters_provided=1,
                parameters_required=1,
                outcome=InteractionOutcome.SUCCESS,
                completion_time_ms=1000,
            )

        # Request only 10
        window = collector.get_windowed_metrics(10)
        assert window.interaction_count == 10


class TestFrustrationDetection:
    """Test frustration signal detection"""

    def test_no_frustration_with_success(self):
        collector = MetricsCollector()

        # Add 10 successful interactions
        for i in range(10):
            collector.record_interaction(
                intent_detected=f"intent_{i}",
                intent_confidence=0.9,
                parameters_provided=1,
                parameters_required=1,
                outcome=InteractionOutcome.SUCCESS,
                completion_time_ms=1000,
            )

        signals = collector.detect_frustration_signals()
        assert signals.is_frustrated is False
        assert signals.confidence < 0.4

    def test_frustration_on_consecutive_errors(self):
        collector = MetricsCollector()

        # Add 5 consecutive failures
        for i in range(5):
            collector.record_interaction(
                intent_detected="failing_intent",
                intent_confidence=0.5,
                parameters_provided=0,
                parameters_required=1,
                outcome=InteractionOutcome.FAILURE,
                completion_time_ms=2000,
            )

        signals = collector.detect_frustration_signals()
        assert signals.is_frustrated is True
        assert "consecutive errors" in str(signals.signals)
        assert "CONSECUTIVE_ERRORS" in signals.trigger_events

    def test_frustration_on_high_help_rate(self):
        collector = MetricsCollector()

        # Add 10 interactions with 5 help requests (50%)
        for i in range(10):
            collector.record_interaction(
                intent_detected=f"intent_{i}",
                intent_confidence=0.7,
                parameters_provided=1,
                parameters_required=1,
                outcome=InteractionOutcome.PARTIAL_SUCCESS,
                completion_time_ms=2000,
                help_requested=(i < 5),
            )

        signals = collector.detect_frustration_signals()
        # 50% > 40% threshold
        assert "HIGH_HELP_RATE" in signals.trigger_events

    def test_frustration_detection_disabled(self):
        config = MetricsStoreConfig(enable_frustration_detection=False)
        collector = MetricsCollector(config=config)

        # Add failing interactions
        for i in range(5):
            collector.record_interaction(
                intent_detected="failing",
                intent_confidence=0.5,
                parameters_provided=0,
                parameters_required=1,
                outcome=InteractionOutcome.FAILURE,
                completion_time_ms=2000,
            )

        signals = collector.detect_frustration_signals()
        assert signals.is_frustrated is False
        assert signals.confidence == 0.0


class TestMasteryDetection:
    """Test mastery signal detection"""

    def test_no_mastery_insufficient_data(self):
        collector = MetricsCollector()

        # Only 5 interactions
        for i in range(5):
            collector.record_interaction(
                intent_detected=f"intent_{i}",
                intent_confidence=0.95,
                parameters_provided=1,
                parameters_required=1,
                outcome=InteractionOutcome.SUCCESS,
                completion_time_ms=500,
                used_shortcut=True,
            )

        signals = collector.detect_mastery_signals()
        assert signals.is_demonstrating_mastery is False
        assert "Insufficient data" in str(signals.signals)

    def test_mastery_with_high_performance(self):
        collector = MetricsCollector()

        # Add 15 successful, fast interactions with shortcuts
        for i in range(15):
            collector.record_interaction(
                intent_detected=f"intent_{i}",
                intent_confidence=0.98,
                parameters_provided=2,
                parameters_required=2,
                outcome=InteractionOutcome.SUCCESS,
                completion_time_ms=500,
                used_shortcut=(i % 2 == 0),  # 50% shortcuts
                help_requested=False,
            )

        signals = collector.detect_mastery_signals()
        assert signals.is_demonstrating_mastery is True
        assert signals.mastery_level > 0.5
        assert "consistent_execution" in signals.skills_demonstrated

    def test_mastery_with_shortcuts(self):
        collector = MetricsCollector()

        # Add 12 interactions with high shortcut usage
        for i in range(12):
            collector.record_interaction(
                intent_detected=f"intent_{i}",
                intent_confidence=0.95,
                parameters_provided=1,
                parameters_required=1,
                outcome=InteractionOutcome.SUCCESS,
                completion_time_ms=800,
                used_shortcut=True,  # 100% shortcuts
            )

        signals = collector.detect_mastery_signals()
        assert "shortcut_proficiency" in signals.skills_demonstrated

    def test_ready_for_advancement(self):
        collector = MetricsCollector()

        # Add 15 excellent interactions
        for i in range(15):
            collector.record_interaction(
                intent_detected=f"intent_{i}",
                intent_confidence=0.99,
                parameters_provided=2,
                parameters_required=2,
                outcome=InteractionOutcome.SUCCESS,
                completion_time_ms=400,
                used_shortcut=True,
                help_requested=False,
            )

        signals = collector.detect_mastery_signals()
        assert signals.ready_for_advancement is True
        assert signals.mastery_level >= 0.7

    def test_mastery_detection_disabled(self):
        config = MetricsStoreConfig(enable_mastery_detection=False)
        collector = MetricsCollector(config=config)

        for i in range(15):
            collector.record_interaction(
                intent_detected=f"intent_{i}",
                intent_confidence=0.99,
                parameters_provided=2,
                parameters_required=2,
                outcome=InteractionOutcome.SUCCESS,
                completion_time_ms=400,
                used_shortcut=True,
            )

        signals = collector.detect_mastery_signals()
        assert signals.is_demonstrating_mastery is False
        assert signals.mastery_level == 0.0


class TestPrivacyModes:
    """Test privacy-aware metrics collection"""

    def test_full_privacy_stores_all(self):
        config = MetricsStoreConfig(privacy_mode=PrivacyMode.FULL)
        collector = MetricsCollector(config=config)

        collector.record_interaction(
            intent_detected="test_intent",
            intent_confidence=0.9,
            parameters_provided=1,
            parameters_required=1,
            outcome=InteractionOutcome.SUCCESS,
            completion_time_ms=1000,
        )

        assert len(collector._interactions) == 1
        assert collector._interactions[0].intent_detected == "test_intent"

    def test_disabled_privacy_no_storage(self):
        config = MetricsStoreConfig(privacy_mode=PrivacyMode.DISABLED)
        collector = MetricsCollector(config=config)

        record = collector.record_interaction(
            intent_detected="test_intent",
            intent_confidence=0.9,
            parameters_provided=1,
            parameters_required=1,
            outcome=InteractionOutcome.SUCCESS,
            completion_time_ms=1000,
        )

        # Record is returned but not stored
        assert record is not None
        assert len(collector._interactions) == 0

    def test_anonymize_intents(self):
        config = MetricsStoreConfig(anonymize_intents=True)
        collector = MetricsCollector(config=config)

        collector.record_interaction(
            intent_detected="sensitive_operation",
            intent_confidence=0.9,
            parameters_provided=1,
            parameters_required=1,
            outcome=InteractionOutcome.SUCCESS,
            completion_time_ms=1000,
        )

        # Intent should be anonymized
        assert collector._interactions[0].intent_detected.startswith("INTENT_")
        assert "sensitive_operation" not in collector._interactions[0].intent_detected


class TestSessionManagement:
    """Test session management"""

    def test_get_session_stats(self):
        collector = MetricsCollector(session_id="test-session")

        for i in range(5):
            collector.record_interaction(
                intent_detected=f"intent_{i}",
                intent_confidence=0.9,
                parameters_provided=1,
                parameters_required=1,
                outcome=InteractionOutcome.SUCCESS if i < 3 else InteractionOutcome.FAILURE,
                completion_time_ms=1000,
            )

        stats = collector.get_session_stats()
        assert stats["session_id"] == "test-session"
        assert stats["interaction_count"] == 5
        assert stats["success_count"] == 3
        assert stats["failure_count"] == 2

    def test_reset_session(self):
        collector = MetricsCollector(session_id="original-session")

        collector.record_interaction(
            intent_detected="test",
            intent_confidence=0.9,
            parameters_provided=1,
            parameters_required=1,
            outcome=InteractionOutcome.SUCCESS,
            completion_time_ms=1000,
        )

        collector.reset_session()

        assert collector.session_id != "original-session"
        assert len(collector._interactions) == 0
        assert collector._consecutive_errors == 0
        assert collector._consecutive_successes == 0

    def test_get_recent_interactions(self):
        collector = MetricsCollector()

        for i in range(15):
            collector.record_interaction(
                intent_detected=f"intent_{i}",
                intent_confidence=0.9,
                parameters_provided=1,
                parameters_required=1,
                outcome=InteractionOutcome.SUCCESS,
                completion_time_ms=1000,
            )

        recent = collector.get_recent_interactions(5)
        assert len(recent) == 5
        # Should be the last 5 interactions
        assert recent[0].intent_detected == "intent_10"
        assert recent[4].intent_detected == "intent_14"


class TestBAMLEnums:
    """Test BAML-generated enum values"""

    def test_baml_interaction_outcome(self):
        assert BAMLInteractionOutcome.SUCCESS.value == "SUCCESS"
        assert BAMLInteractionOutcome.PARTIAL_SUCCESS.value == "PARTIAL_SUCCESS"
        assert BAMLInteractionOutcome.FAILURE.value == "FAILURE"
        assert BAMLInteractionOutcome.ABANDONED.value == "ABANDONED"
        assert BAMLInteractionOutcome.HELP_ESCALATION.value == "HELP_ESCALATION"

    def test_baml_trend_direction(self):
        assert BAMLTrendDirection.IMPROVING.value == "IMPROVING"
        assert BAMLTrendDirection.STABLE.value == "STABLE"
        assert BAMLTrendDirection.DECLINING.value == "DECLINING"

    def test_baml_signal_type(self):
        assert SignalType.FRUSTRATION.value == "FRUSTRATION"
        assert SignalType.MASTERY.value == "MASTERY"
        assert SignalType.LEARNING.value == "LEARNING"
        assert SignalType.CONFUSION.value == "CONFUSION"
        assert SignalType.ENGAGEMENT.value == "ENGAGEMENT"

    def test_baml_signal_severity(self):
        assert BAMLSignalSeverity.LOW.value == "LOW"
        assert BAMLSignalSeverity.MEDIUM.value == "MEDIUM"
        assert BAMLSignalSeverity.HIGH.value == "HIGH"
        assert BAMLSignalSeverity.CRITICAL.value == "CRITICAL"

    def test_baml_privacy_mode(self):
        assert BAMLPrivacyMode.FULL.value == "FULL"
        assert BAMLPrivacyMode.AGGREGATE_ONLY.value == "AGGREGATE_ONLY"
        assert BAMLPrivacyMode.SESSION_ONLY.value == "SESSION_ONLY"
        assert BAMLPrivacyMode.DISABLED.value == "DISABLED"

    def test_baml_metrics_event_type(self):
        assert MetricsEventType.INTERACTION_START.value == "INTERACTION_START"
        assert MetricsEventType.INTERACTION_END.value == "INTERACTION_END"
        assert MetricsEventType.HELP_REQUEST.value == "HELP_REQUEST"
        assert MetricsEventType.ERROR_OCCURRED.value == "ERROR_OCCURRED"
        assert MetricsEventType.SHORTCUT_USED.value == "SHORTCUT_USED"
        assert MetricsEventType.RETRY_ATTEMPTED.value == "RETRY_ATTEMPTED"
        assert MetricsEventType.SESSION_START.value == "SESSION_START"
        assert MetricsEventType.SESSION_END.value == "SESSION_END"
        assert MetricsEventType.WINDOW_COMPLETE.value == "WINDOW_COMPLETE"


class TestBAMLTypeConstruction:
    """Test BAML-generated type construction"""

    def test_baml_interaction_record(self):
        record = BAMLInteractionRecord(
            interaction_id="test-123",
            timestamp="2024-01-15T10:00:00Z",
            session_id="session-456",
            intent_detected="create_task",
            intent_confidence=0.95,
            parameters_provided=2,
            parameters_required=2,
            outcome=BAMLInteractionOutcome.SUCCESS,
            completion_time_ms=1500,
            error_count=0,
            help_requested=False,
            disambiguation_needed=False,
            used_shortcut=True,
            input_length=25,
            retries=0,
            corrections=0,
        )
        assert record.interaction_id == "test-123"
        assert record.outcome == BAMLInteractionOutcome.SUCCESS

    def test_baml_metrics_window(self):
        window = BAMLMetricsWindow(
            window_id="window-123",
            window_start="2024-01-15T10:00:00Z",
            window_end="2024-01-15T11:00:00Z",
            interaction_count=20,
            success_rate=0.85,
            partial_success_rate=0.05,
            failure_rate=0.05,
            abandonment_rate=0.05,
            help_rate=0.1,
            shortcut_rate=0.4,
            error_rate=0.2,
            disambiguation_rate=0.15,
            avg_completion_time_ms=1500.0,
            median_completion_time_ms=1200.0,
            p95_completion_time_ms=3000.0,
            avg_input_length=30.0,
            avg_parameters_provided=1.5,
            avg_retries=0.1,
            success_trend=BAMLTrendDirection.IMPROVING,
            efficiency_trend=BAMLTrendDirection.STABLE,
            engagement_trend=BAMLTrendDirection.STABLE,
        )
        assert window.interaction_count == 20
        assert window.success_rate == 0.85

    def test_baml_frustration_signals(self):
        signals = BAMLFrustrationSignals(
            is_frustrated=True,
            confidence=0.75,
            severity=BAMLSignalSeverity.HIGH,
            signals=["3 consecutive errors", "High help rate"],
            trigger_events=["CONSECUTIVE_ERRORS", "HIGH_HELP_RATE"],
            recommendation="Consider offering guided assistance",
        )
        assert signals.is_frustrated is True
        assert signals.severity == BAMLSignalSeverity.HIGH

    def test_baml_mastery_signals(self):
        signals = BAMLMasterySignals(
            is_demonstrating_mastery=True,
            confidence=0.85,
            mastery_level=0.8,
            signals=["High success rate", "Frequent shortcut usage"],
            skills_demonstrated=["command_efficiency", "shortcut_proficiency"],
            ready_for_advancement=True,
        )
        assert signals.is_demonstrating_mastery is True
        assert signals.ready_for_advancement is True

    def test_baml_metrics_store_config(self):
        config = BAMLMetricsStoreConfig(
            privacy_mode=BAMLPrivacyMode.AGGREGATE_ONLY,
            retention_days=30,
            aggregate_window_size=25,
            enable_frustration_detection=True,
            enable_mastery_detection=True,
            anonymize_intents=False,
        )
        assert config.privacy_mode == BAMLPrivacyMode.AGGREGATE_ONLY
        assert config.retention_days == 30


class TestTrendCalculation:
    """Test trend calculation logic"""

    def test_improving_trend(self):
        collector = MetricsCollector()

        # First half failures, second half successes
        for _ in range(5):
            collector.record_interaction(
                intent_detected="intent",
                intent_confidence=0.5,
                parameters_provided=0,
                parameters_required=1,
                outcome=InteractionOutcome.FAILURE,
                completion_time_ms=2000,
            )
        for _ in range(5):
            collector.record_interaction(
                intent_detected="intent",
                intent_confidence=0.9,
                parameters_provided=1,
                parameters_required=1,
                outcome=InteractionOutcome.SUCCESS,
                completion_time_ms=1000,
            )

        window = collector.get_windowed_metrics(10)
        assert window.success_trend == TrendDirection.IMPROVING

    def test_declining_trend(self):
        collector = MetricsCollector()

        # First half successes, second half failures
        for _ in range(5):
            collector.record_interaction(
                intent_detected="intent",
                intent_confidence=0.9,
                parameters_provided=1,
                parameters_required=1,
                outcome=InteractionOutcome.SUCCESS,
                completion_time_ms=1000,
            )
        for _ in range(5):
            collector.record_interaction(
                intent_detected="intent",
                intent_confidence=0.5,
                parameters_provided=0,
                parameters_required=1,
                outcome=InteractionOutcome.FAILURE,
                completion_time_ms=2000,
            )

        window = collector.get_windowed_metrics(10)
        assert window.success_trend == TrendDirection.DECLINING

    def test_stable_trend(self):
        collector = MetricsCollector()

        # All successful - stable high performance
        for i in range(10):
            collector.record_interaction(
                intent_detected="intent",
                intent_confidence=0.9,
                parameters_provided=1,
                parameters_required=1,
                outcome=InteractionOutcome.SUCCESS,
                completion_time_ms=1500,
            )

        window = collector.get_windowed_metrics(10)
        assert window.success_trend == TrendDirection.STABLE
