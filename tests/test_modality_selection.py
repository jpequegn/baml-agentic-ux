"""Tests for modality selection types and logic."""

from __future__ import annotations

import pytest

from baml_client.types import (
    # Enums
    ScreenSize,
    NoiseLevel,
    PrivacyLevel,
    ContentType,
    MessageLength,
    MessagePriority,
    Modality,
    AccessibilityNeed,
    # Classes
    DeviceCapabilities,
    EnvironmentContext,
    ModalityContext,
    ModalityRecommendation,
    SelectionFactors,
    ModalitySelectionResult,
    SelectionWeights,
    DefaultSelectionWeights,
    ModalityValidationResult,
    FallbackChain,
)


# ============================================
# Enum Tests
# ============================================


class TestScreenSizeEnum:
    """Tests for ScreenSize enum."""

    def test_all_values_exist(self) -> None:
        """Test all screen size values are defined."""
        assert ScreenSize.NONE.value == "NONE"
        assert ScreenSize.SMALL.value == "SMALL"
        assert ScreenSize.MEDIUM.value == "MEDIUM"
        assert ScreenSize.LARGE.value == "LARGE"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(ScreenSize) == 4


class TestNoiseLevelEnum:
    """Tests for NoiseLevel enum."""

    def test_all_values_exist(self) -> None:
        """Test all noise level values are defined."""
        assert NoiseLevel.QUIET.value == "QUIET"
        assert NoiseLevel.MODERATE.value == "MODERATE"
        assert NoiseLevel.LOUD.value == "LOUD"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(NoiseLevel) == 3


class TestPrivacyLevelEnum:
    """Tests for PrivacyLevel enum."""

    def test_all_values_exist(self) -> None:
        """Test all privacy level values are defined."""
        assert PrivacyLevel.PRIVATE.value == "PRIVATE"
        assert PrivacyLevel.SEMI_PRIVATE.value == "SEMI_PRIVATE"
        assert PrivacyLevel.PUBLIC.value == "PUBLIC"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(PrivacyLevel) == 3


class TestContentTypeEnum:
    """Tests for ContentType enum."""

    def test_all_values_exist(self) -> None:
        """Test all content type values are defined."""
        assert ContentType.CONFIRMATION.value == "CONFIRMATION"
        assert ContentType.ERROR.value == "ERROR"
        assert ContentType.DATA_TABLE.value == "DATA_TABLE"
        assert ContentType.LONG_TEXT.value == "LONG_TEXT"
        assert ContentType.SHORT_RESPONSE.value == "SHORT_RESPONSE"
        assert ContentType.ACTION_REQUIRED.value == "ACTION_REQUIRED"
        assert ContentType.DISAMBIGUATION.value == "DISAMBIGUATION"
        assert ContentType.LIST.value == "LIST"
        assert ContentType.FORM.value == "FORM"
        assert ContentType.MEDIA.value == "MEDIA"
        assert ContentType.NOTIFICATION.value == "NOTIFICATION"
        assert ContentType.PROGRESS.value == "PROGRESS"
        assert ContentType.NAVIGATION.value == "NAVIGATION"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(ContentType) == 13


class TestMessageLengthEnum:
    """Tests for MessageLength enum."""

    def test_all_values_exist(self) -> None:
        """Test all message length values are defined."""
        assert MessageLength.SHORT.value == "SHORT"
        assert MessageLength.MEDIUM.value == "MEDIUM"
        assert MessageLength.LONG.value == "LONG"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(MessageLength) == 3


class TestMessagePriorityEnum:
    """Tests for MessagePriority enum."""

    def test_all_values_exist(self) -> None:
        """Test all priority values are defined."""
        assert MessagePriority.LOW.value == "LOW"
        assert MessagePriority.NORMAL.value == "NORMAL"
        assert MessagePriority.HIGH.value == "HIGH"
        assert MessagePriority.CRITICAL.value == "CRITICAL"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(MessagePriority) == 4


# ============================================
# DeviceCapabilities Tests
# ============================================


class TestDeviceCapabilities:
    """Tests for DeviceCapabilities class."""

    def test_create_full_capability_device(self) -> None:
        """Test creating a device with all capabilities."""
        device = DeviceCapabilities(
            has_screen=True,
            has_speaker=True,
            has_microphone=True,
            has_keyboard=True,
            screen_size=ScreenSize.LARGE,
            supports_touch=True,
            supports_voice_commands=True,
            bandwidth_quality="high",
        )

        assert device.has_screen is True
        assert device.has_speaker is True
        assert device.has_microphone is True
        assert device.has_keyboard is True
        assert device.screen_size == ScreenSize.LARGE
        assert device.supports_touch is True
        assert device.supports_voice_commands is True
        assert device.bandwidth_quality == "high"

    def test_create_minimal_device(self) -> None:
        """Test creating a device with minimal capabilities."""
        device = DeviceCapabilities(
            has_screen=False,
            has_speaker=True,
            has_microphone=True,
            has_keyboard=False,
        )

        assert device.has_screen is False
        assert device.has_speaker is True
        assert device.has_microphone is True
        assert device.has_keyboard is False
        assert device.screen_size is None
        assert device.supports_touch is None

    def test_smart_speaker_device(self) -> None:
        """Test creating a smart speaker configuration."""
        device = DeviceCapabilities(
            has_screen=False,
            has_speaker=True,
            has_microphone=True,
            has_keyboard=False,
            screen_size=ScreenSize.NONE,
            supports_touch=False,
            supports_voice_commands=True,
        )

        assert device.has_screen is False
        assert device.screen_size == ScreenSize.NONE
        assert device.supports_voice_commands is True

    def test_smartphone_device(self) -> None:
        """Test creating a smartphone configuration."""
        device = DeviceCapabilities(
            has_screen=True,
            has_speaker=True,
            has_microphone=True,
            has_keyboard=True,
            screen_size=ScreenSize.SMALL,
            supports_touch=True,
            supports_voice_commands=True,
            bandwidth_quality="medium",
        )

        assert device.screen_size == ScreenSize.SMALL
        assert device.supports_touch is True


# ============================================
# EnvironmentContext Tests
# ============================================


class TestEnvironmentContext:
    """Tests for EnvironmentContext class."""

    def test_create_quiet_private_environment(self) -> None:
        """Test creating a quiet private environment."""
        env = EnvironmentContext(
            noise_level=NoiseLevel.QUIET,
            privacy_level=PrivacyLevel.PRIVATE,
            mobility=False,
            hands_free_required=False,
            eyes_free_required=False,
        )

        assert env.noise_level == NoiseLevel.QUIET
        assert env.privacy_level == PrivacyLevel.PRIVATE
        assert env.mobility is False
        assert env.hands_free_required is False
        assert env.eyes_free_required is False

    def test_create_driving_environment(self) -> None:
        """Test creating a driving environment (hands-free, eyes-free)."""
        env = EnvironmentContext(
            noise_level=NoiseLevel.MODERATE,
            privacy_level=PrivacyLevel.PRIVATE,
            mobility=True,
            hands_free_required=True,
            eyes_free_required=True,
        )

        assert env.hands_free_required is True
        assert env.eyes_free_required is True
        assert env.mobility is True

    def test_create_public_environment(self) -> None:
        """Test creating a public environment."""
        env = EnvironmentContext(
            noise_level=NoiseLevel.LOUD,
            privacy_level=PrivacyLevel.PUBLIC,
            mobility=True,
        )

        assert env.noise_level == NoiseLevel.LOUD
        assert env.privacy_level == PrivacyLevel.PUBLIC

    def test_create_minimal_environment(self) -> None:
        """Test creating environment with minimal info."""
        env = EnvironmentContext()

        assert env.noise_level is None
        assert env.privacy_level is None
        assert env.mobility is None

    def test_environment_with_time(self) -> None:
        """Test environment with time of day."""
        env = EnvironmentContext(
            noise_level=NoiseLevel.QUIET,
            privacy_level=PrivacyLevel.PRIVATE,
            time_of_day="night",
        )

        assert env.time_of_day == "night"


# ============================================
# ModalityContext Tests
# ============================================


class TestModalityContext:
    """Tests for ModalityContext class."""

    def test_create_full_context(self) -> None:
        """Test creating a full modality context."""
        device = DeviceCapabilities(
            has_screen=True,
            has_speaker=True,
            has_microphone=True,
            has_keyboard=True,
            screen_size=ScreenSize.MEDIUM,
        )

        env = EnvironmentContext(
            noise_level=NoiseLevel.QUIET,
            privacy_level=PrivacyLevel.PRIVATE,
        )

        context = ModalityContext(
            available_modalities=[Modality.TEXT, Modality.VOICE, Modality.VISUAL],
            user_preference=Modality.TEXT,
            device_capabilities=device,
            environment_context=env,
            content_type=ContentType.SHORT_RESPONSE,
            message_length=MessageLength.SHORT,
            priority=MessagePriority.NORMAL,
            previous_modality=Modality.TEXT,
            interaction_count=5,
            error_occurred=False,
        )

        assert len(context.available_modalities) == 3
        assert context.user_preference == Modality.TEXT
        assert context.content_type == ContentType.SHORT_RESPONSE
        assert context.message_length == MessageLength.SHORT
        assert context.priority == MessagePriority.NORMAL
        assert context.previous_modality == Modality.TEXT
        assert context.interaction_count == 5
        assert context.error_occurred is False

    def test_create_minimal_context(self) -> None:
        """Test creating a minimal modality context."""
        device = DeviceCapabilities(
            has_screen=True,
            has_speaker=True,
            has_microphone=False,
            has_keyboard=True,
        )

        context = ModalityContext(
            available_modalities=[Modality.TEXT, Modality.VISUAL],
            device_capabilities=device,
            content_type=ContentType.LONG_TEXT,
            message_length=MessageLength.LONG,
            priority=MessagePriority.LOW,
        )

        assert len(context.available_modalities) == 2
        assert context.user_preference is None
        assert context.environment_context is None
        assert context.previous_modality is None

    def test_voice_only_context(self) -> None:
        """Test context for voice-only device."""
        device = DeviceCapabilities(
            has_screen=False,
            has_speaker=True,
            has_microphone=True,
            has_keyboard=False,
            screen_size=ScreenSize.NONE,
        )

        context = ModalityContext(
            available_modalities=[Modality.VOICE],
            device_capabilities=device,
            content_type=ContentType.CONFIRMATION,
            message_length=MessageLength.SHORT,
            priority=MessagePriority.NORMAL,
        )

        assert context.available_modalities == [Modality.VOICE]
        assert context.device_capabilities.has_screen is False

    def test_error_context(self) -> None:
        """Test context when an error occurred."""
        device = DeviceCapabilities(
            has_screen=True,
            has_speaker=True,
            has_microphone=True,
            has_keyboard=True,
        )

        context = ModalityContext(
            available_modalities=[Modality.TEXT, Modality.VOICE, Modality.VISUAL],
            device_capabilities=device,
            content_type=ContentType.ERROR,
            message_length=MessageLength.MEDIUM,
            priority=MessagePriority.HIGH,
            previous_modality=Modality.TEXT,
            error_occurred=True,
        )

        assert context.content_type == ContentType.ERROR
        assert context.error_occurred is True
        assert context.priority == MessagePriority.HIGH


# ============================================
# ModalityRecommendation Tests
# ============================================


class TestModalityRecommendation:
    """Tests for ModalityRecommendation class."""

    def test_create_simple_recommendation(self) -> None:
        """Test creating a simple recommendation."""
        rec = ModalityRecommendation(
            primary=Modality.VOICE,
            rationale="Quick confirmation works best with voice",
            confidence=0.9,
            fallback_chain=[Modality.TEXT],
        )

        assert rec.primary == Modality.VOICE
        assert rec.secondary is None
        assert rec.confidence == 0.9
        assert len(rec.fallback_chain) == 1

    def test_create_hybrid_recommendation(self) -> None:
        """Test creating a hybrid recommendation."""
        rec = ModalityRecommendation(
            primary=Modality.VISUAL,
            secondary=Modality.TEXT,
            rationale="Data tables need visual display with text backup",
            confidence=0.85,
            fallback_chain=[Modality.TEXT, Modality.VOICE],
        )

        assert rec.primary == Modality.VISUAL
        assert rec.secondary == Modality.TEXT
        assert len(rec.fallback_chain) == 2

    def test_recommendation_with_accessibility(self) -> None:
        """Test recommendation with accessibility adaptations."""
        rec = ModalityRecommendation(
            primary=Modality.VOICE,
            rationale="User has visual impairment",
            confidence=1.0,
            fallback_chain=[],
            accessibility_adaptations=["Audio descriptions added", "No visual-only content"],
        )

        assert rec.accessibility_adaptations is not None
        assert len(rec.accessibility_adaptations) == 2

    def test_recommendation_with_warnings(self) -> None:
        """Test recommendation with warnings."""
        rec = ModalityRecommendation(
            primary=Modality.VOICE,
            rationale="Voice preferred but environment is noisy",
            confidence=0.6,
            fallback_chain=[Modality.TEXT, Modality.VISUAL],
            warnings=["Noisy environment may affect speech recognition"],
        )

        assert rec.warnings is not None
        assert len(rec.warnings) == 1


# ============================================
# SelectionFactors Tests
# ============================================


class TestSelectionFactors:
    """Tests for SelectionFactors class."""

    def test_create_factors(self) -> None:
        """Test creating selection factors."""
        factors = SelectionFactors(
            content_match=0.9,
            environment_score=0.7,
            device_score=0.8,
            user_preference_score=0.5,
            accessibility_score=1.0,
            overall_score=0.82,
        )

        assert factors.content_match == 0.9
        assert factors.environment_score == 0.7
        assert factors.device_score == 0.8
        assert factors.user_preference_score == 0.5
        assert factors.accessibility_score == 1.0
        assert factors.overall_score == 0.82

    def test_factors_all_high(self) -> None:
        """Test factors with all high scores."""
        factors = SelectionFactors(
            content_match=1.0,
            environment_score=1.0,
            device_score=1.0,
            user_preference_score=1.0,
            accessibility_score=1.0,
            overall_score=1.0,
        )

        assert factors.overall_score == 1.0

    def test_factors_all_low(self) -> None:
        """Test factors with all low scores."""
        factors = SelectionFactors(
            content_match=0.1,
            environment_score=0.2,
            device_score=0.3,
            user_preference_score=0.1,
            accessibility_score=0.0,
            overall_score=0.15,
        )

        assert factors.overall_score == 0.15


# ============================================
# ModalitySelectionResult Tests
# ============================================


class TestModalitySelectionResult:
    """Tests for ModalitySelectionResult class."""

    def test_create_result(self) -> None:
        """Test creating a selection result."""
        rec = ModalityRecommendation(
            primary=Modality.TEXT,
            rationale="Long text content best displayed as text",
            confidence=0.95,
            fallback_chain=[Modality.VISUAL, Modality.VOICE],
        )

        factors = SelectionFactors(
            content_match=0.95,
            environment_score=0.8,
            device_score=0.9,
            user_preference_score=0.7,
            accessibility_score=1.0,
            overall_score=0.88,
        )

        result = ModalitySelectionResult(
            recommendation=rec,
            factors=factors,
            decision_path="Content type LONG_TEXT strongly prefers TEXT modality",
        )

        assert result.recommendation.primary == Modality.TEXT
        assert result.factors.overall_score == 0.88
        assert "LONG_TEXT" in result.decision_path

    def test_result_with_alternatives(self) -> None:
        """Test result with alternative recommendations."""
        primary = ModalityRecommendation(
            primary=Modality.VISUAL,
            rationale="Data table needs visual display",
            confidence=0.9,
            fallback_chain=[Modality.TEXT],
        )

        alt = ModalityRecommendation(
            primary=Modality.HYBRID,
            rationale="Could use hybrid approach",
            confidence=0.7,
            fallback_chain=[Modality.VISUAL, Modality.TEXT],
        )

        factors = SelectionFactors(
            content_match=0.9,
            environment_score=0.8,
            device_score=0.9,
            user_preference_score=0.6,
            accessibility_score=1.0,
            overall_score=0.85,
        )

        result = ModalitySelectionResult(
            recommendation=primary,
            factors=factors,
            alternatives=[alt],
            decision_path="Selected VISUAL over HYBRID due to content match",
        )

        assert result.alternatives is not None
        assert len(result.alternatives) == 1
        assert result.alternatives[0].primary == Modality.HYBRID


# ============================================
# SelectionWeights Tests
# ============================================


class TestSelectionWeights:
    """Tests for SelectionWeights class."""

    def test_create_weights(self) -> None:
        """Test creating selection weights."""
        weights = SelectionWeights(
            accessibility=1.0,
            content_match=0.35,
            environment=0.25,
            device=0.20,
            user_preference=0.15,
            continuity=0.05,
        )

        assert weights.accessibility == 1.0
        assert weights.content_match == 0.35
        assert weights.environment == 0.25
        assert weights.device == 0.20
        assert weights.user_preference == 0.15
        assert weights.continuity == 0.05

    def test_weights_sum_to_one(self) -> None:
        """Test that non-accessibility weights sum to 1."""
        weights = SelectionWeights(
            accessibility=1.0,
            content_match=0.35,
            environment=0.25,
            device=0.20,
            user_preference=0.15,
            continuity=0.05,
        )

        non_accessibility_sum = (
            weights.content_match
            + weights.environment
            + weights.device
            + weights.user_preference
            + weights.continuity
        )

        assert abs(non_accessibility_sum - 1.0) < 0.001


class TestDefaultSelectionWeights:
    """Tests for DefaultSelectionWeights class."""

    def test_create_default_weights(self) -> None:
        """Test creating default selection weights."""
        defaults = DefaultSelectionWeights(
            accessibility=1.0,
            content_match=0.35,
            environment=0.25,
            device=0.20,
            user_preference=0.15,
            continuity=0.05,
        )

        assert defaults.accessibility == 1.0
        assert defaults.content_match == 0.35


# ============================================
# ModalityValidationResult Tests
# ============================================


class TestModalityValidationResult:
    """Tests for ModalityValidationResult class."""

    def test_create_valid_result(self) -> None:
        """Test creating a valid validation result."""
        result = ModalityValidationResult(
            is_valid=True,
            is_optimal=True,
            accessibility_compliant=True,
        )

        assert result.is_valid is True
        assert result.is_optimal is True
        assert result.accessibility_compliant is True
        assert result.issues is None
        assert result.suggestions is None

    def test_create_invalid_result(self) -> None:
        """Test creating an invalid validation result."""
        result = ModalityValidationResult(
            is_valid=False,
            is_optimal=False,
            accessibility_compliant=False,
            issues=["Voice modality not available on device", "User has hearing impairment"],
            suggestions=["Use TEXT modality instead"],
            recommended_alternative=Modality.TEXT,
        )

        assert result.is_valid is False
        assert result.issues is not None
        assert len(result.issues) == 2
        assert result.recommended_alternative == Modality.TEXT

    def test_valid_but_not_optimal(self) -> None:
        """Test result that is valid but not optimal."""
        result = ModalityValidationResult(
            is_valid=True,
            is_optimal=False,
            accessibility_compliant=True,
            suggestions=["VISUAL would be better for this data table"],
            recommended_alternative=Modality.VISUAL,
        )

        assert result.is_valid is True
        assert result.is_optimal is False
        assert result.recommended_alternative == Modality.VISUAL


# ============================================
# FallbackChain Tests
# ============================================


class TestFallbackChain:
    """Tests for FallbackChain class."""

    def test_create_fallback_chain(self) -> None:
        """Test creating a fallback chain."""
        chain = FallbackChain(
            chain=[Modality.VISUAL, Modality.TEXT, Modality.VOICE],
            degradation_notes=[
                "VISUAL: Full table display",
                "TEXT: Formatted text representation",
                "VOICE: Read key values only",
            ],
            minimum_viable=Modality.VOICE,
        )

        assert len(chain.chain) == 3
        assert chain.chain[0] == Modality.VISUAL
        assert len(chain.degradation_notes) == 3
        assert chain.minimum_viable == Modality.VOICE

    def test_single_fallback(self) -> None:
        """Test chain with single fallback."""
        chain = FallbackChain(
            chain=[Modality.TEXT],
            degradation_notes=["TEXT: Simple text output"],
            minimum_viable=Modality.TEXT,
        )

        assert len(chain.chain) == 1
        assert chain.minimum_viable == Modality.TEXT


# ============================================
# Integration Tests
# ============================================


class TestModalitySelectionIntegration:
    """Integration tests for modality selection scenarios."""

    def test_confirmation_scenario(self) -> None:
        """Test selecting modality for a confirmation message."""
        device = DeviceCapabilities(
            has_screen=True,
            has_speaker=True,
            has_microphone=True,
            has_keyboard=True,
            screen_size=ScreenSize.MEDIUM,
        )

        context = ModalityContext(
            available_modalities=[Modality.TEXT, Modality.VOICE, Modality.VISUAL],
            device_capabilities=device,
            content_type=ContentType.CONFIRMATION,
            message_length=MessageLength.SHORT,
            priority=MessagePriority.NORMAL,
        )

        # Voice is expected for confirmations
        assert ContentType.CONFIRMATION in [
            ContentType.CONFIRMATION,
            ContentType.SHORT_RESPONSE,
        ]
        assert Modality.VOICE in context.available_modalities

    def test_error_with_accessibility_scenario(self) -> None:
        """Test selecting modality for error with visual impairment."""
        device = DeviceCapabilities(
            has_screen=True,
            has_speaker=True,
            has_microphone=True,
            has_keyboard=True,
            screen_size=ScreenSize.LARGE,
        )

        context = ModalityContext(
            available_modalities=[Modality.TEXT, Modality.VOICE, Modality.VISUAL],
            device_capabilities=device,
            content_type=ContentType.ERROR,
            message_length=MessageLength.MEDIUM,
            priority=MessagePriority.HIGH,
        )

        # For visual impairment, VOICE should be preferred
        accessibility_needs = [AccessibilityNeed.VISUAL]

        assert AccessibilityNeed.VISUAL in accessibility_needs
        assert Modality.VOICE in context.available_modalities

    def test_data_table_scenario(self) -> None:
        """Test selecting modality for data table."""
        device = DeviceCapabilities(
            has_screen=True,
            has_speaker=True,
            has_microphone=False,
            has_keyboard=True,
            screen_size=ScreenSize.LARGE,
        )

        context = ModalityContext(
            available_modalities=[Modality.TEXT, Modality.VISUAL, Modality.HYBRID],
            device_capabilities=device,
            content_type=ContentType.DATA_TABLE,
            message_length=MessageLength.LONG,
            priority=MessagePriority.LOW,
        )

        # VISUAL is expected for data tables
        assert context.content_type == ContentType.DATA_TABLE
        assert Modality.VISUAL in context.available_modalities
        assert context.device_capabilities.screen_size == ScreenSize.LARGE

    def test_loud_environment_scenario(self) -> None:
        """Test modality selection in loud environment."""
        device = DeviceCapabilities(
            has_screen=True,
            has_speaker=True,
            has_microphone=True,
            has_keyboard=True,
            screen_size=ScreenSize.SMALL,
        )

        env = EnvironmentContext(
            noise_level=NoiseLevel.LOUD,
            privacy_level=PrivacyLevel.PUBLIC,
            mobility=True,
        )

        context = ModalityContext(
            available_modalities=[Modality.TEXT, Modality.VOICE, Modality.VISUAL],
            user_preference=Modality.VOICE,
            device_capabilities=device,
            environment_context=env,
            content_type=ContentType.SHORT_RESPONSE,
            message_length=MessageLength.SHORT,
            priority=MessagePriority.NORMAL,
        )

        # In loud environment, TEXT/VISUAL should be preferred over VOICE
        assert context.environment_context is not None
        assert context.environment_context.noise_level == NoiseLevel.LOUD
        # Despite user preference for VOICE, environment suggests TEXT/VISUAL

    def test_driving_scenario(self) -> None:
        """Test modality selection while driving."""
        device = DeviceCapabilities(
            has_screen=True,
            has_speaker=True,
            has_microphone=True,
            has_keyboard=False,
            screen_size=ScreenSize.MEDIUM,
        )

        env = EnvironmentContext(
            noise_level=NoiseLevel.MODERATE,
            privacy_level=PrivacyLevel.PRIVATE,
            mobility=True,
            hands_free_required=True,
            eyes_free_required=True,
        )

        context = ModalityContext(
            available_modalities=[Modality.TEXT, Modality.VOICE, Modality.VISUAL],
            device_capabilities=device,
            environment_context=env,
            content_type=ContentType.NAVIGATION,
            message_length=MessageLength.SHORT,
            priority=MessagePriority.NORMAL,
        )

        # VOICE is required for hands-free, eyes-free scenarios
        assert context.environment_context is not None
        assert context.environment_context.hands_free_required is True
        assert context.environment_context.eyes_free_required is True
        assert Modality.VOICE in context.available_modalities

    def test_smart_speaker_scenario(self) -> None:
        """Test modality selection for smart speaker."""
        device = DeviceCapabilities(
            has_screen=False,
            has_speaker=True,
            has_microphone=True,
            has_keyboard=False,
            screen_size=ScreenSize.NONE,
            supports_voice_commands=True,
        )

        context = ModalityContext(
            available_modalities=[Modality.VOICE],
            device_capabilities=device,
            content_type=ContentType.SHORT_RESPONSE,
            message_length=MessageLength.SHORT,
            priority=MessagePriority.NORMAL,
        )

        # Only VOICE is available
        assert len(context.available_modalities) == 1
        assert context.available_modalities[0] == Modality.VOICE
        assert context.device_capabilities.has_screen is False

    def test_modality_continuity_scenario(self) -> None:
        """Test preference for staying in same modality."""
        device = DeviceCapabilities(
            has_screen=True,
            has_speaker=True,
            has_microphone=True,
            has_keyboard=True,
        )

        context = ModalityContext(
            available_modalities=[Modality.TEXT, Modality.VOICE, Modality.VISUAL],
            device_capabilities=device,
            content_type=ContentType.SHORT_RESPONSE,
            message_length=MessageLength.SHORT,
            priority=MessagePriority.NORMAL,
            previous_modality=Modality.TEXT,
            error_occurred=True,
        )

        # When error occurred, prefer to stay in same modality
        assert context.previous_modality == Modality.TEXT
        assert context.error_occurred is True


class TestTypeImports:
    """Tests to verify all modality selection types are importable."""

    def test_all_enums_importable(self) -> None:
        """Test all enum imports work."""
        assert ScreenSize is not None
        assert NoiseLevel is not None
        assert PrivacyLevel is not None
        assert ContentType is not None
        assert MessageLength is not None
        assert MessagePriority is not None

    def test_all_classes_importable(self) -> None:
        """Test all class imports work."""
        assert DeviceCapabilities is not None
        assert EnvironmentContext is not None
        assert ModalityContext is not None
        assert ModalityRecommendation is not None
        assert SelectionFactors is not None
        assert ModalitySelectionResult is not None
        assert SelectionWeights is not None
        assert DefaultSelectionWeights is not None
        assert ModalityValidationResult is not None
        assert FallbackChain is not None
