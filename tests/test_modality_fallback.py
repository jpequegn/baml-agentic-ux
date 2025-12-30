"""Tests for modality fallback and graceful degradation types."""

from __future__ import annotations

from baml_client.types import (
    # Enums
    ModalityErrorType,
    ErrorSeverity,
    RecoveryTier,
    OverallHealth,
    TransformationType,
    NotificationStyle,
    RecoveryActionType,
    Modality,
    AccessibilityNeed,
    AriaLiveType,
    CognitiveLoad,
    # Classes
    ModalityError,
    ModalityStatus,
    ModalityHealthReport,
    DegradedResponse,
    DegradationTransformation,
    FallbackConfiguration,
    UserNotification,
    RecoveryAction,
    RecoveryResult,
    FallbackSelection,
    PreservePriority,
    TransformedContent,
    RecoverySuggestions,
    DegradationNotice,
    MultiModalResponse,
    AccessibilityMeta,
)


# ============================================
# Enum Tests
# ============================================


class TestModalityErrorTypeEnum:
    """Tests for ModalityErrorType enum."""

    def test_all_values_exist(self) -> None:
        """Test all error type values are defined."""
        assert ModalityErrorType.UNAVAILABLE.value == "UNAVAILABLE"
        assert ModalityErrorType.TIMEOUT.value == "TIMEOUT"
        assert ModalityErrorType.PERMISSION_DENIED.value == "PERMISSION_DENIED"
        assert ModalityErrorType.QUOTA_EXCEEDED.value == "QUOTA_EXCEEDED"
        assert ModalityErrorType.NETWORK_ERROR.value == "NETWORK_ERROR"
        assert ModalityErrorType.SERVICE_ERROR.value == "SERVICE_ERROR"
        assert ModalityErrorType.RESOURCE_EXHAUSTED.value == "RESOURCE_EXHAUSTED"
        assert ModalityErrorType.UNSUPPORTED_CONTENT.value == "UNSUPPORTED_CONTENT"
        assert ModalityErrorType.USER_INTERRUPT.value == "USER_INTERRUPT"
        assert ModalityErrorType.INITIALIZATION_FAILED.value == "INITIALIZATION_FAILED"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(ModalityErrorType) == 10


class TestErrorSeverityEnum:
    """Tests for ErrorSeverity enum."""

    def test_all_values_exist(self) -> None:
        """Test all severity values are defined."""
        assert ErrorSeverity.LOW.value == "LOW"
        assert ErrorSeverity.MEDIUM.value == "MEDIUM"
        assert ErrorSeverity.HIGH.value == "HIGH"
        assert ErrorSeverity.CRITICAL.value == "CRITICAL"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(ErrorSeverity) == 4


class TestRecoveryTierEnum:
    """Tests for RecoveryTier enum."""

    def test_all_values_exist(self) -> None:
        """Test all recovery tier values are defined."""
        assert RecoveryTier.SELF_REPAIR.value == "SELF_REPAIR"
        assert RecoveryTier.GUIDED_REPAIR.value == "GUIDED_REPAIR"
        assert RecoveryTier.ESCALATION.value == "ESCALATION"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(RecoveryTier) == 3


class TestOverallHealthEnum:
    """Tests for OverallHealth enum."""

    def test_all_values_exist(self) -> None:
        """Test all health status values are defined."""
        assert OverallHealth.HEALTHY.value == "HEALTHY"
        assert OverallHealth.DEGRADED.value == "DEGRADED"
        assert OverallHealth.CRITICAL.value == "CRITICAL"
        assert OverallHealth.OFFLINE.value == "OFFLINE"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(OverallHealth) == 4


class TestTransformationTypeEnum:
    """Tests for TransformationType enum."""

    def test_all_values_exist(self) -> None:
        """Test all transformation type values are defined."""
        assert TransformationType.VOICE_TO_TEXT.value == "VOICE_TO_TEXT"
        assert TransformationType.VISUAL_TO_TEXT.value == "VISUAL_TO_TEXT"
        assert TransformationType.TABLE_TO_LIST.value == "TABLE_TO_LIST"
        assert TransformationType.CHART_TO_DESCRIPTION.value == "CHART_TO_DESCRIPTION"
        assert TransformationType.IMAGE_TO_ALT_TEXT.value == "IMAGE_TO_ALT_TEXT"
        assert TransformationType.COMPLEX_TO_SIMPLE.value == "COMPLEX_TO_SIMPLE"
        assert TransformationType.MEDIA_TO_TRANSCRIPT.value == "MEDIA_TO_TRANSCRIPT"
        assert TransformationType.INTERACTIVE_TO_STATIC.value == "INTERACTIVE_TO_STATIC"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(TransformationType) == 8


class TestNotificationStyleEnum:
    """Tests for NotificationStyle enum."""

    def test_all_values_exist(self) -> None:
        """Test all notification style values are defined."""
        assert NotificationStyle.SUBTLE.value == "SUBTLE"
        assert NotificationStyle.INFORMATIVE.value == "INFORMATIVE"
        assert NotificationStyle.PROMINENT.value == "PROMINENT"
        assert NotificationStyle.URGENT.value == "URGENT"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(NotificationStyle) == 4


class TestRecoveryActionTypeEnum:
    """Tests for RecoveryActionType enum."""

    def test_all_values_exist(self) -> None:
        """Test all recovery action type values are defined."""
        assert RecoveryActionType.RETRY.value == "RETRY"
        assert RecoveryActionType.WAIT.value == "WAIT"
        assert RecoveryActionType.REQUEST_PERMISSION.value == "REQUEST_PERMISSION"
        assert RecoveryActionType.SWITCH_SERVICE.value == "SWITCH_SERVICE"
        assert RecoveryActionType.REDUCE_QUALITY.value == "REDUCE_QUALITY"
        assert RecoveryActionType.REFRESH_CONNECTION.value == "REFRESH_CONNECTION"
        assert RecoveryActionType.RESTART_SERVICE.value == "RESTART_SERVICE"
        assert RecoveryActionType.ESCALATE_TO_HUMAN.value == "ESCALATE_TO_HUMAN"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(RecoveryActionType) == 8


# ============================================
# ModalityError Tests
# ============================================


class TestModalityError:
    """Tests for ModalityError class."""

    def test_create_recoverable_error(self) -> None:
        """Test creating a recoverable error."""
        error = ModalityError(
            error_type=ModalityErrorType.TIMEOUT,
            message="TTS service timeout after 5000ms",
            user_message="Voice is taking too long",
            recoverable=True,
            suggested_fallback=Modality.TEXT,
            retry_after_ms=10000,
            error_code="TTS_TIMEOUT",
        )

        assert error.error_type == ModalityErrorType.TIMEOUT
        assert error.recoverable is True
        assert error.suggested_fallback == Modality.TEXT
        assert error.retry_after_ms == 10000

    def test_create_non_recoverable_error(self) -> None:
        """Test creating a non-recoverable error."""
        error = ModalityError(
            error_type=ModalityErrorType.UNAVAILABLE,
            message="No speaker available",
            user_message="Audio is not available on this device",
            recoverable=False,
        )

        assert error.error_type == ModalityErrorType.UNAVAILABLE
        assert error.recoverable is False
        assert error.suggested_fallback is None
        assert error.retry_after_ms is None

    def test_permission_denied_error(self) -> None:
        """Test creating a permission denied error."""
        error = ModalityError(
            error_type=ModalityErrorType.PERMISSION_DENIED,
            message="Microphone access denied",
            user_message="Please allow microphone access to use voice",
            recoverable=True,
            suggested_fallback=Modality.TEXT,
        )

        assert error.error_type == ModalityErrorType.PERMISSION_DENIED
        assert "microphone" in error.user_message.lower()

    def test_network_error(self) -> None:
        """Test creating a network error."""
        error = ModalityError(
            error_type=ModalityErrorType.NETWORK_ERROR,
            message="Connection refused",
            user_message="Network connection lost",
            recoverable=True,
            retry_after_ms=5000,
            error_code="ECONNREFUSED",
        )

        assert error.error_type == ModalityErrorType.NETWORK_ERROR
        assert error.error_code == "ECONNREFUSED"


# ============================================
# ModalityStatus Tests
# ============================================


class TestModalityStatus:
    """Tests for ModalityStatus class."""

    def test_create_healthy_status(self) -> None:
        """Test creating a healthy modality status."""
        status = ModalityStatus(
            modality=Modality.VOICE,
            available=True,
            healthy=True,
            failure_count=0,
            current_tier=RecoveryTier.SELF_REPAIR,
        )

        assert status.modality == Modality.VOICE
        assert status.available is True
        assert status.healthy is True
        assert status.error is None
        assert status.failure_count == 0

    def test_create_failed_status(self) -> None:
        """Test creating a failed modality status."""
        error = ModalityError(
            error_type=ModalityErrorType.SERVICE_ERROR,
            message="Service unavailable",
            user_message="Voice service is down",
            recoverable=True,
        )

        status = ModalityStatus(
            modality=Modality.VOICE,
            available=False,
            healthy=False,
            error=error,
            last_successful_at="2024-01-15T10:30:00Z",
            failure_count=3,
            current_tier=RecoveryTier.ESCALATION,
        )

        assert status.available is False
        assert status.healthy is False
        assert status.error is not None
        assert status.error.error_type == ModalityErrorType.SERVICE_ERROR
        assert status.failure_count == 3
        assert status.current_tier == RecoveryTier.ESCALATION

    def test_recovery_tier_progression(self) -> None:
        """Test recovery tier progression based on failure count."""
        # Tier 1: 0-1 failures
        status1 = ModalityStatus(
            modality=Modality.TEXT,
            available=True,
            healthy=True,
            failure_count=0,
            current_tier=RecoveryTier.SELF_REPAIR,
        )
        assert status1.current_tier == RecoveryTier.SELF_REPAIR

        # Tier 2: 1-2 failures
        status2 = ModalityStatus(
            modality=Modality.TEXT,
            available=True,
            healthy=False,
            failure_count=2,
            current_tier=RecoveryTier.GUIDED_REPAIR,
        )
        assert status2.current_tier == RecoveryTier.GUIDED_REPAIR

        # Tier 3: 3+ failures
        status3 = ModalityStatus(
            modality=Modality.TEXT,
            available=False,
            healthy=False,
            failure_count=4,
            current_tier=RecoveryTier.ESCALATION,
        )
        assert status3.current_tier == RecoveryTier.ESCALATION


# ============================================
# ModalityHealthReport Tests
# ============================================


class TestModalityHealthReport:
    """Tests for ModalityHealthReport class."""

    def test_create_healthy_report(self) -> None:
        """Test creating a healthy system report."""
        statuses = [
            ModalityStatus(
                modality=Modality.TEXT,
                available=True,
                healthy=True,
                failure_count=0,
                current_tier=RecoveryTier.SELF_REPAIR,
            ),
            ModalityStatus(
                modality=Modality.VOICE,
                available=True,
                healthy=True,
                failure_count=0,
                current_tier=RecoveryTier.SELF_REPAIR,
            ),
            ModalityStatus(
                modality=Modality.VISUAL,
                available=True,
                healthy=True,
                failure_count=0,
                current_tier=RecoveryTier.SELF_REPAIR,
            ),
        ]

        report = ModalityHealthReport(
            modalities=statuses,
            recommended_modality=Modality.TEXT,
            overall_health=OverallHealth.HEALTHY,
            generated_at="2024-01-15T10:30:00Z",
        )

        assert len(report.modalities) == 3
        assert report.overall_health == OverallHealth.HEALTHY
        assert report.recommended_modality == Modality.TEXT

    def test_create_degraded_report(self) -> None:
        """Test creating a degraded system report."""
        statuses = [
            ModalityStatus(
                modality=Modality.TEXT,
                available=True,
                healthy=True,
                failure_count=0,
                current_tier=RecoveryTier.SELF_REPAIR,
            ),
            ModalityStatus(
                modality=Modality.VOICE,
                available=False,
                healthy=False,
                failure_count=3,
                current_tier=RecoveryTier.ESCALATION,
            ),
        ]

        report = ModalityHealthReport(
            modalities=statuses,
            recommended_modality=Modality.TEXT,
            overall_health=OverallHealth.DEGRADED,
            generated_at="2024-01-15T10:30:00Z",
        )

        assert report.overall_health == OverallHealth.DEGRADED


# ============================================
# DegradedResponse Tests
# ============================================


class TestDegradedResponse:
    """Tests for DegradedResponse class."""

    def test_create_degraded_response(self) -> None:
        """Test creating a degraded response."""
        response = MultiModalResponse(
            response_id="test-001",
            primary_modality=Modality.TEXT,
            accessibility=AccessibilityMeta(
                aria_label="Test response",
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.LOW,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=False,
                reduced_motion_safe=True,
            ),
        )

        degraded = DegradedResponse(
            original_modality=Modality.VOICE,
            actual_modality=Modality.TEXT,
            response=response,
            degradation_notice="Voice unavailable. Here's the text instead.",
            recovery_action="Tap here when voice is ready",
            information_preserved=True,
        )

        assert degraded.original_modality == Modality.VOICE
        assert degraded.actual_modality == Modality.TEXT
        assert degraded.information_preserved is True
        assert "Voice unavailable" in str(degraded.degradation_notice)

    def test_degraded_response_with_information_loss(self) -> None:
        """Test degraded response with some information loss."""
        response = MultiModalResponse(
            response_id="test-002",
            primary_modality=Modality.TEXT,
            accessibility=AccessibilityMeta(
                aria_label="Simplified response",
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.MINIMAL,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=False,
                reduced_motion_safe=True,
            ),
        )

        degraded = DegradedResponse(
            original_modality=Modality.VISUAL,
            actual_modality=Modality.TEXT,
            response=response,
            degradation_notice="Chart simplified to text description.",
            information_preserved=False,
            lost_features=["Interactive tooltips", "Drill-down functionality"],
        )

        assert degraded.information_preserved is False
        assert degraded.lost_features is not None
        assert len(degraded.lost_features) == 2


# ============================================
# DegradationTransformation Tests
# ============================================


class TestDegradationTransformation:
    """Tests for DegradationTransformation class."""

    def test_create_transformation(self) -> None:
        """Test creating a transformation record."""
        transform = DegradationTransformation(
            transformation_type=TransformationType.VOICE_TO_TEXT,
            original_format="SSML voice response",
            target_format="Formatted text with emphasis",
            fidelity=0.95,
            notes="Pauses converted to paragraph breaks",
        )

        assert transform.transformation_type == TransformationType.VOICE_TO_TEXT
        assert transform.fidelity == 0.95

    def test_table_to_list_transformation(self) -> None:
        """Test table to list transformation."""
        transform = DegradationTransformation(
            transformation_type=TransformationType.TABLE_TO_LIST,
            original_format="3-column data table",
            target_format="Bullet list with labels",
            fidelity=0.85,
            notes="Column relationships may be less clear",
        )

        assert transform.transformation_type == TransformationType.TABLE_TO_LIST
        assert transform.fidelity == 0.85


# ============================================
# FallbackConfiguration Tests
# ============================================


class TestFallbackConfiguration:
    """Tests for FallbackConfiguration class."""

    def test_create_voice_fallback_config(self) -> None:
        """Test creating voice fallback configuration."""
        notifications = [
            UserNotification(
                level=1,
                message="Switching to text for now.",
                show_recovery=True,
                style=NotificationStyle.SUBTLE,
            ),
            UserNotification(
                level=2,
                message="Voice still unavailable. Showing visual cards.",
                show_recovery=True,
                style=NotificationStyle.INFORMATIVE,
            ),
        ]

        config = FallbackConfiguration(
            primary_modality=Modality.VOICE,
            fallback_order=[Modality.TEXT, Modality.VISUAL, Modality.HYBRID],
            notifications=notifications,
        )

        assert config.primary_modality == Modality.VOICE
        assert len(config.fallback_order) == 3
        assert config.fallback_order[0] == Modality.TEXT
        assert len(config.notifications) == 2


# ============================================
# RecoveryAction Tests
# ============================================


class TestRecoveryAction:
    """Tests for RecoveryAction class."""

    def test_create_retry_action(self) -> None:
        """Test creating a retry action."""
        action = RecoveryAction(
            action_type=RecoveryActionType.RETRY,
            description="Retry the voice request",
            automatic=True,
            success_likelihood=0.7,
        )

        assert action.action_type == RecoveryActionType.RETRY
        assert action.automatic is True
        assert action.success_likelihood == 0.7
        assert action.user_prompt is None

    def test_create_permission_request_action(self) -> None:
        """Test creating a permission request action."""
        action = RecoveryAction(
            action_type=RecoveryActionType.REQUEST_PERMISSION,
            description="Request microphone access",
            user_prompt="Allow microphone access to enable voice input?",
            automatic=False,
            success_likelihood=0.8,
        )

        assert action.action_type == RecoveryActionType.REQUEST_PERMISSION
        assert action.automatic is False
        assert action.user_prompt is not None

    def test_create_escalation_action(self) -> None:
        """Test creating an escalation action."""
        action = RecoveryAction(
            action_type=RecoveryActionType.ESCALATE_TO_HUMAN,
            description="Connect to support agent",
            user_prompt="Would you like to speak with a support agent?",
            automatic=False,
            success_likelihood=1.0,
        )

        assert action.action_type == RecoveryActionType.ESCALATE_TO_HUMAN
        assert action.success_likelihood == 1.0


# ============================================
# RecoveryResult Tests
# ============================================


class TestRecoveryResult:
    """Tests for RecoveryResult class."""

    def test_create_successful_recovery(self) -> None:
        """Test creating a successful recovery result."""
        action = RecoveryAction(
            action_type=RecoveryActionType.RETRY,
            description="Retry request",
            automatic=True,
            success_likelihood=0.7,
        )

        new_status = ModalityStatus(
            modality=Modality.VOICE,
            available=True,
            healthy=True,
            failure_count=0,
            current_tier=RecoveryTier.SELF_REPAIR,
        )

        result = RecoveryResult(
            action=action,
            success=True,
            new_status=new_status,
            time_taken_ms=1500,
        )

        assert result.success is True
        assert result.new_status.healthy is True
        assert result.time_taken_ms == 1500
        assert result.next_action is None

    def test_create_failed_recovery_with_next_action(self) -> None:
        """Test creating a failed recovery with next action."""
        action = RecoveryAction(
            action_type=RecoveryActionType.RETRY,
            description="Retry request",
            automatic=True,
            success_likelihood=0.7,
        )

        next_action = RecoveryAction(
            action_type=RecoveryActionType.SWITCH_SERVICE,
            description="Try backup service",
            automatic=True,
            success_likelihood=0.5,
        )

        new_status = ModalityStatus(
            modality=Modality.VOICE,
            available=False,
            healthy=False,
            failure_count=2,
            current_tier=RecoveryTier.GUIDED_REPAIR,
        )

        result = RecoveryResult(
            action=action,
            success=False,
            new_status=new_status,
            time_taken_ms=5000,
            next_action=next_action,
        )

        assert result.success is False
        assert result.next_action is not None
        assert result.next_action.action_type == RecoveryActionType.SWITCH_SERVICE


# ============================================
# FallbackSelection Tests
# ============================================


class TestFallbackSelection:
    """Tests for FallbackSelection class."""

    def test_create_fallback_selection(self) -> None:
        """Test creating a fallback selection."""
        selection = FallbackSelection(
            selected_modality=Modality.TEXT,
            rationale="Voice unavailable, text is most similar for short content",
            confidence=0.85,
            expected_fidelity=0.95,
            transformations_needed=[TransformationType.VOICE_TO_TEXT],
            alternative=Modality.VISUAL,
        )

        assert selection.selected_modality == Modality.TEXT
        assert selection.confidence == 0.85
        assert selection.expected_fidelity == 0.95
        assert len(selection.transformations_needed) == 1
        assert selection.alternative == Modality.VISUAL

    def test_selection_for_accessibility(self) -> None:
        """Test selection with accessibility considerations."""
        selection = FallbackSelection(
            selected_modality=Modality.VOICE,
            rationale="User has visual impairment, voice is required",
            confidence=1.0,
            expected_fidelity=0.90,
            transformations_needed=[
                TransformationType.VISUAL_TO_TEXT,
                TransformationType.CHART_TO_DESCRIPTION,
            ],
        )

        assert selection.confidence == 1.0
        assert len(selection.transformations_needed) == 2


# ============================================
# PreservePriority Tests
# ============================================


class TestPreservePriority:
    """Tests for PreservePriority class."""

    def test_create_preserve_priority(self) -> None:
        """Test creating preservation priority."""
        priority = PreservePriority(
            critical_elements=["Meeting time", "Attendee names", "Action items"],
            important_elements=["Meeting agenda", "Location details"],
            optional_elements=["Formatting", "Visual styling"],
            acceptable_loss=0.1,
        )

        assert len(priority.critical_elements) == 3
        assert len(priority.important_elements) == 2
        assert len(priority.optional_elements) == 2
        assert priority.acceptable_loss == 0.1


# ============================================
# TransformedContent Tests
# ============================================


class TestTransformedContent:
    """Tests for TransformedContent class."""

    def test_create_transformed_content(self) -> None:
        """Test creating transformed content."""
        response = MultiModalResponse(
            response_id="transformed-001",
            primary_modality=Modality.TEXT,
            accessibility=AccessibilityMeta(
                aria_label="Transformed content",
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.LOW,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=False,
                reduced_motion_safe=True,
            ),
        )

        transformed = TransformedContent(
            content=response,
            transformations_applied=[
                TransformationType.VOICE_TO_TEXT,
                TransformationType.COMPLEX_TO_SIMPLE,
            ],
            fidelity=0.92,
            notes="Prosody converted to text emphasis",
        )

        assert len(transformed.transformations_applied) == 2
        assert transformed.fidelity == 0.92
        assert transformed.lost_elements is None

    def test_transformed_content_with_loss(self) -> None:
        """Test transformed content with some information loss."""
        response = MultiModalResponse(
            response_id="transformed-002",
            primary_modality=Modality.TEXT,
            accessibility=AccessibilityMeta(
                aria_label="Simplified content",
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.MINIMAL,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=False,
                reduced_motion_safe=True,
            ),
        )

        transformed = TransformedContent(
            content=response,
            transformations_applied=[TransformationType.CHART_TO_DESCRIPTION],
            fidelity=0.75,
            lost_elements=["Interactive zoom", "Data point tooltips", "Trend lines"],
            notes="Chart converted to text summary",
        )

        assert transformed.fidelity == 0.75
        assert transformed.lost_elements is not None
        assert len(transformed.lost_elements) == 3


# ============================================
# RecoverySuggestions Tests
# ============================================


class TestRecoverySuggestions:
    """Tests for RecoverySuggestions class."""

    def test_create_recovery_suggestions(self) -> None:
        """Test creating recovery suggestions."""
        primary = RecoveryAction(
            action_type=RecoveryActionType.RETRY,
            description="Retry connection",
            automatic=True,
            success_likelihood=0.7,
        )

        alternatives = [
            RecoveryAction(
                action_type=RecoveryActionType.SWITCH_SERVICE,
                description="Try backup service",
                automatic=True,
                success_likelihood=0.5,
            ),
        ]

        suggestions = RecoverySuggestions(
            current_tier=RecoveryTier.GUIDED_REPAIR,
            primary_action=primary,
            alternative_actions=alternatives,
            user_message="Connection is slow. Trying to reconnect...",
            automatic_actions=[primary],
            requires_user_input=False,
        )

        assert suggestions.current_tier == RecoveryTier.GUIDED_REPAIR
        assert suggestions.primary_action.action_type == RecoveryActionType.RETRY
        assert len(suggestions.alternative_actions) == 1
        assert suggestions.requires_user_input is False

    def test_escalation_suggestions(self) -> None:
        """Test creating escalation suggestions."""
        primary = RecoveryAction(
            action_type=RecoveryActionType.ESCALATE_TO_HUMAN,
            description="Connect to support",
            user_prompt="Would you like help from a support agent?",
            automatic=False,
            success_likelihood=1.0,
        )

        suggestions = RecoverySuggestions(
            current_tier=RecoveryTier.ESCALATION,
            primary_action=primary,
            alternative_actions=[],
            user_message="We're having trouble. Would you like to speak with someone?",
            automatic_actions=[],
            requires_user_input=True,
        )

        assert suggestions.current_tier == RecoveryTier.ESCALATION
        assert suggestions.requires_user_input is True


# ============================================
# DegradationNotice Tests
# ============================================


class TestDegradationNotice:
    """Tests for DegradationNotice class."""

    def test_create_subtle_notice(self) -> None:
        """Test creating a subtle notice."""
        notice = DegradationNotice(
            main_message="Switching to text for now.",
            recovery_hint="Voice will be back shortly.",
            style=NotificationStyle.SUBTLE,
            show_immediately=True,
            dismissible=True,
        )

        assert notice.style == NotificationStyle.SUBTLE
        assert notice.show_immediately is True
        assert notice.dismissible is True

    def test_create_prominent_notice(self) -> None:
        """Test creating a prominent notice."""
        notice = DegradationNotice(
            main_message="Voice is not available on this device.",
            style=NotificationStyle.PROMINENT,
            show_immediately=True,
            dismissible=False,
        )

        assert notice.style == NotificationStyle.PROMINENT
        assert notice.recovery_hint is None
        assert notice.dismissible is False


# ============================================
# Integration Tests
# ============================================


class TestFallbackIntegration:
    """Integration tests for fallback scenarios."""

    def test_voice_to_text_fallback_scenario(self) -> None:
        """Test complete voice to text fallback scenario."""
        # 1. Voice error occurs
        error = ModalityError(
            error_type=ModalityErrorType.TIMEOUT,
            message="TTS timeout",
            user_message="Voice is taking too long",
            recoverable=True,
            suggested_fallback=Modality.TEXT,
            retry_after_ms=5000,
        )

        # 2. Fallback selected
        selection = FallbackSelection(
            selected_modality=Modality.TEXT,
            rationale="Voice timeout, text is quick alternative",
            confidence=0.9,
            expected_fidelity=0.95,
            transformations_needed=[TransformationType.VOICE_TO_TEXT],
            alternative=Modality.VISUAL,
        )

        # 3. Response degraded
        response = MultiModalResponse(
            response_id="fallback-001",
            primary_modality=Modality.TEXT,
            accessibility=AccessibilityMeta(
                aria_label="Fallback response",
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.LOW,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=False,
                reduced_motion_safe=True,
            ),
        )

        degraded = DegradedResponse(
            original_modality=Modality.VOICE,
            actual_modality=Modality.TEXT,
            response=response,
            degradation_notice="Voice is slow. Here's the text.",
            recovery_action="Voice will be back shortly",
            information_preserved=True,
        )

        # Assertions
        assert error.recoverable is True
        assert selection.selected_modality == Modality.TEXT
        assert degraded.information_preserved is True

    def test_visual_to_voice_accessibility_scenario(self) -> None:
        """Test visual to voice fallback for accessibility."""
        # User has visual impairment - this context drives the selection
        _ = AccessibilityNeed.VISUAL

        # Visual modality unavailable - error informs selection
        _ = ModalityError(
            error_type=ModalityErrorType.UNAVAILABLE,
            message="No display",
            user_message="Display not available",
            recoverable=False,
            suggested_fallback=Modality.VOICE,
        )

        # Must use voice for accessibility
        selection = FallbackSelection(
            selected_modality=Modality.VOICE,
            rationale="User has visual impairment, voice required",
            confidence=1.0,
            expected_fidelity=0.80,
            transformations_needed=[
                TransformationType.VISUAL_TO_TEXT,
                TransformationType.TABLE_TO_LIST,
            ],
        )

        assert selection.confidence == 1.0
        assert Modality.VOICE == selection.selected_modality

    def test_escalation_after_multiple_failures(self) -> None:
        """Test escalation after multiple failures."""
        # Track failure progression
        statuses = []

        # First failure - self repair
        statuses.append(
            ModalityStatus(
                modality=Modality.VOICE,
                available=True,
                healthy=False,
                failure_count=1,
                current_tier=RecoveryTier.SELF_REPAIR,
            )
        )

        # Second failure - guided repair
        statuses.append(
            ModalityStatus(
                modality=Modality.VOICE,
                available=True,
                healthy=False,
                failure_count=2,
                current_tier=RecoveryTier.GUIDED_REPAIR,
            )
        )

        # Third failure - escalation
        statuses.append(
            ModalityStatus(
                modality=Modality.VOICE,
                available=False,
                healthy=False,
                failure_count=3,
                current_tier=RecoveryTier.ESCALATION,
            )
        )

        assert statuses[0].current_tier == RecoveryTier.SELF_REPAIR
        assert statuses[1].current_tier == RecoveryTier.GUIDED_REPAIR
        assert statuses[2].current_tier == RecoveryTier.ESCALATION


class TestTypeImports:
    """Tests to verify all fallback types are importable."""

    def test_all_enums_importable(self) -> None:
        """Test all enum imports work."""
        assert ModalityErrorType is not None
        assert ErrorSeverity is not None
        assert RecoveryTier is not None
        assert OverallHealth is not None
        assert TransformationType is not None
        assert NotificationStyle is not None
        assert RecoveryActionType is not None

    def test_all_classes_importable(self) -> None:
        """Test all class imports work."""
        assert ModalityError is not None
        assert ModalityStatus is not None
        assert ModalityHealthReport is not None
        assert DegradedResponse is not None
        assert DegradationTransformation is not None
        assert FallbackConfiguration is not None
        assert UserNotification is not None
        assert RecoveryAction is not None
        assert RecoveryResult is not None
        assert FallbackSelection is not None
        assert PreservePriority is not None
        assert TransformedContent is not None
        assert RecoverySuggestions is not None
        assert DegradationNotice is not None
