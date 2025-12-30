"""Comprehensive Multi-Modal Integration Tests (Issue #42).

This module provides integration tests that verify the complete multi-modal system
works together correctly. It focuses on integration scenarios across all multi-modal
features implemented in Issues #35-#41.

Individual unit tests for specific components are in:
- test_ssml.py - SSML generation and validation
- test_modality_selection.py - Modality recommendation logic
- test_modality_fallback.py - Graceful degradation
- test_accessibility_compliance.py - WCAG 2.2 validation
- test_visual_elements.py - Adaptive Cards and visuals
"""

from __future__ import annotations

from baml_client.types import (
    # Core modality types
    Modality,
    MultiModalResponse,
    # Visual types
    MultiModalVisualType,
    MultiModalVisualElement,
    Dimensions,
    # Voice types
    VoiceResponse,
    VoiceConfig,
    VoiceGender,
    VoiceSpeakingStyle,
    # Text types
    TextResponse,
    TextFormat,
    # Action types
    MultiModalAction,
    InteractionType,
    # Accessibility types
    AccessibilityMeta,
    AriaLiveType,
    ReadingLevel,
    CognitiveLoad,
    # Timing types
    ResponseTiming,
    ResponseSequence,
    # SSML types
    SSMLElementType,
    SSMLBreakStrength,
    SSMLProsodyRate,
    SSMLProsodyPitch,
    SSMLProsodyVolume,
    # Modality selection types
    ScreenSize,
    NoiseLevel,
    PrivacyLevel,
    ContentType,
    MessageLength,
    MessagePriority,
    # Modality fallback types
    ModalityErrorType,
    ErrorSeverity,
    RecoveryTier,
    NotificationStyle,
    # Adaptive Cards types
    CardElementType,
    CardActionType,
    ContainerStyle,
    TextColor,
    HorizontalAlignment,
    # Accessibility validation types
    WCAGLevel,
    WCAGCategory,
    ViolationSeverity,
    AccessibilityNeed,
    # Multi-modal generation types
    ResponseLength,
    EmpathyLevel,
    EmojiUsage,
)


# ============================================
# Enum Tests
# ============================================


class TestModalityEnums:
    """Test core modality enum values."""

    def test_modality_values(self) -> None:
        """Test all modality enum values exist."""
        assert Modality.TEXT.value == "TEXT"
        assert Modality.VOICE.value == "VOICE"
        assert Modality.VISUAL.value == "VISUAL"
        assert Modality.HYBRID.value == "HYBRID"
        assert len(Modality) == 4

    def test_visual_element_types(self) -> None:
        """Test visual element types exist."""
        assert MultiModalVisualType.CARD.value == "CARD"
        assert MultiModalVisualType.IMAGE.value == "IMAGE"
        assert MultiModalVisualType.TABLE.value == "TABLE"
        assert MultiModalVisualType.CHART.value == "CHART"
        assert MultiModalVisualType.LIST.value == "LIST"
        assert MultiModalVisualType.CODE_BLOCK.value == "CODE_BLOCK"

    def test_interaction_types(self) -> None:
        """Test interaction/action types exist."""
        assert InteractionType.BUTTON.value == "BUTTON"
        assert InteractionType.LINK.value == "LINK"
        assert InteractionType.VOICE_COMMAND.value == "VOICE_COMMAND"
        assert InteractionType.KEYBOARD.value == "KEYBOARD"
        assert InteractionType.GESTURE.value == "GESTURE"

    def test_text_format_values(self) -> None:
        """Test text format enum values."""
        assert TextFormat.PLAIN.value == "PLAIN"
        assert TextFormat.MARKDOWN.value == "MARKDOWN"
        assert TextFormat.HTML.value == "HTML"


class TestSSMLEnums:
    """Test SSML-related enum values."""

    def test_ssml_element_types(self) -> None:
        """Test SSML element types exist."""
        assert SSMLElementType.SPEAK.value == "SPEAK"
        assert SSMLElementType.BREAK.value == "BREAK"
        assert SSMLElementType.PROSODY.value == "PROSODY"
        assert SSMLElementType.EMPHASIS.value == "EMPHASIS"
        assert SSMLElementType.SAY_AS.value == "SAY_AS"
        assert SSMLElementType.PHONEME.value == "PHONEME"

    def test_ssml_break_strength(self) -> None:
        """Test SSML break strength values."""
        assert SSMLBreakStrength.NONE.value == "NONE"
        assert SSMLBreakStrength.X_WEAK.value == "X_WEAK"
        assert SSMLBreakStrength.WEAK.value == "WEAK"
        assert SSMLBreakStrength.MEDIUM.value == "MEDIUM"
        assert SSMLBreakStrength.STRONG.value == "STRONG"
        assert SSMLBreakStrength.X_STRONG.value == "X_STRONG"

    def test_ssml_prosody_rate(self) -> None:
        """Test SSML prosody rate values."""
        assert SSMLProsodyRate.X_SLOW.value == "X_SLOW"
        assert SSMLProsodyRate.SLOW.value == "SLOW"
        assert SSMLProsodyRate.MEDIUM.value == "MEDIUM"
        assert SSMLProsodyRate.FAST.value == "FAST"
        assert SSMLProsodyRate.X_FAST.value == "X_FAST"

    def test_ssml_prosody_pitch(self) -> None:
        """Test SSML prosody pitch values."""
        assert SSMLProsodyPitch.X_LOW.value == "X_LOW"
        assert SSMLProsodyPitch.LOW.value == "LOW"
        assert SSMLProsodyPitch.MEDIUM.value == "MEDIUM"
        assert SSMLProsodyPitch.HIGH.value == "HIGH"
        assert SSMLProsodyPitch.X_HIGH.value == "X_HIGH"

    def test_ssml_prosody_volume(self) -> None:
        """Test SSML prosody volume values."""
        assert SSMLProsodyVolume.SILENT.value == "SILENT"
        assert SSMLProsodyVolume.X_SOFT.value == "X_SOFT"
        assert SSMLProsodyVolume.SOFT.value == "SOFT"
        assert SSMLProsodyVolume.MEDIUM.value == "MEDIUM"
        assert SSMLProsodyVolume.LOUD.value == "LOUD"
        assert SSMLProsodyVolume.X_LOUD.value == "X_LOUD"


class TestModalitySelectionEnums:
    """Test modality selection enum values."""

    def test_screen_size_values(self) -> None:
        """Test screen size enum values."""
        assert ScreenSize.NONE.value == "NONE"
        assert ScreenSize.SMALL.value == "SMALL"
        assert ScreenSize.MEDIUM.value == "MEDIUM"
        assert ScreenSize.LARGE.value == "LARGE"

    def test_noise_level_values(self) -> None:
        """Test noise level enum values."""
        assert NoiseLevel.QUIET.value == "QUIET"
        assert NoiseLevel.MODERATE.value == "MODERATE"
        assert NoiseLevel.LOUD.value == "LOUD"

    def test_privacy_level_values(self) -> None:
        """Test privacy level enum values."""
        assert PrivacyLevel.PRIVATE.value == "PRIVATE"
        assert PrivacyLevel.SEMI_PRIVATE.value == "SEMI_PRIVATE"
        assert PrivacyLevel.PUBLIC.value == "PUBLIC"

    def test_content_type_values(self) -> None:
        """Test content type enum values."""
        assert ContentType.CONFIRMATION.value == "CONFIRMATION"
        assert ContentType.ERROR.value == "ERROR"
        assert ContentType.DATA_TABLE.value == "DATA_TABLE"
        assert ContentType.LONG_TEXT.value == "LONG_TEXT"
        assert ContentType.NOTIFICATION.value == "NOTIFICATION"

    def test_message_length_values(self) -> None:
        """Test message length enum values."""
        assert MessageLength.SHORT.value == "SHORT"
        assert MessageLength.MEDIUM.value == "MEDIUM"
        assert MessageLength.LONG.value == "LONG"

    def test_message_priority_values(self) -> None:
        """Test message priority enum values."""
        assert MessagePriority.LOW.value == "LOW"
        assert MessagePriority.NORMAL.value == "NORMAL"
        assert MessagePriority.HIGH.value == "HIGH"
        assert MessagePriority.CRITICAL.value == "CRITICAL"


class TestFallbackEnums:
    """Test fallback/degradation enum values."""

    def test_error_type_values(self) -> None:
        """Test modality error type values."""
        assert ModalityErrorType.UNAVAILABLE.value == "UNAVAILABLE"
        assert ModalityErrorType.NETWORK_ERROR.value == "NETWORK_ERROR"
        assert ModalityErrorType.PERMISSION_DENIED.value == "PERMISSION_DENIED"
        assert ModalityErrorType.TIMEOUT.value == "TIMEOUT"

    def test_error_severity_values(self) -> None:
        """Test error severity enum values."""
        assert ErrorSeverity.LOW.value == "LOW"
        assert ErrorSeverity.MEDIUM.value == "MEDIUM"
        assert ErrorSeverity.HIGH.value == "HIGH"
        assert ErrorSeverity.CRITICAL.value == "CRITICAL"

    def test_recovery_tier_values(self) -> None:
        """Test recovery tier enum values."""
        assert RecoveryTier.SELF_REPAIR.value == "SELF_REPAIR"
        assert RecoveryTier.GUIDED_REPAIR.value == "GUIDED_REPAIR"
        assert RecoveryTier.ESCALATION.value == "ESCALATION"

    def test_notification_style_values(self) -> None:
        """Test notification style enum values."""
        assert NotificationStyle.SUBTLE.value == "SUBTLE"
        assert NotificationStyle.INFORMATIVE.value == "INFORMATIVE"
        assert NotificationStyle.PROMINENT.value == "PROMINENT"
        assert NotificationStyle.URGENT.value == "URGENT"


class TestAdaptiveCardEnums:
    """Test Adaptive Card enum values."""

    def test_card_element_types(self) -> None:
        """Test card element type values."""
        assert CardElementType.TEXT_BLOCK.value == "TEXT_BLOCK"
        assert CardElementType.IMAGE.value == "IMAGE"
        assert CardElementType.CONTAINER.value == "CONTAINER"
        assert CardElementType.COLUMN_SET.value == "COLUMN_SET"
        assert CardElementType.FACT_SET.value == "FACT_SET"

    def test_card_action_types(self) -> None:
        """Test card action type values."""
        assert CardActionType.OPEN_URL.value == "OPEN_URL"
        assert CardActionType.SUBMIT.value == "SUBMIT"
        assert CardActionType.SHOW_CARD.value == "SHOW_CARD"

    def test_container_style_values(self) -> None:
        """Test container style enum values."""
        assert ContainerStyle.DEFAULT.value == "DEFAULT"
        assert ContainerStyle.EMPHASIS.value == "EMPHASIS"
        assert ContainerStyle.GOOD.value == "GOOD"
        assert ContainerStyle.ATTENTION.value == "ATTENTION"
        assert ContainerStyle.WARNING.value == "WARNING"

    def test_text_color_values(self) -> None:
        """Test text color enum values."""
        assert TextColor.DEFAULT.value == "DEFAULT"
        assert TextColor.DARK.value == "DARK"
        assert TextColor.LIGHT.value == "LIGHT"
        assert TextColor.ACCENT.value == "ACCENT"
        assert TextColor.GOOD.value == "GOOD"
        assert TextColor.WARNING.value == "WARNING"
        assert TextColor.ATTENTION.value == "ATTENTION"

    def test_horizontal_alignment_values(self) -> None:
        """Test horizontal alignment enum values."""
        assert HorizontalAlignment.LEFT.value == "LEFT"
        assert HorizontalAlignment.CENTER.value == "CENTER"
        assert HorizontalAlignment.RIGHT.value == "RIGHT"


class TestAccessibilityEnums:
    """Test accessibility enum values."""

    def test_aria_live_values(self) -> None:
        """Test ARIA live region values."""
        assert AriaLiveType.OFF.value == "OFF"
        assert AriaLiveType.POLITE.value == "POLITE"
        assert AriaLiveType.ASSERTIVE.value == "ASSERTIVE"

    def test_reading_level_values(self) -> None:
        """Test reading level enum values."""
        assert ReadingLevel.ELEMENTARY.value == "ELEMENTARY"
        assert ReadingLevel.MIDDLE_SCHOOL.value == "MIDDLE_SCHOOL"
        assert ReadingLevel.HIGH_SCHOOL.value == "HIGH_SCHOOL"
        assert ReadingLevel.COLLEGE.value == "COLLEGE"

    def test_cognitive_load_values(self) -> None:
        """Test cognitive load enum values."""
        assert CognitiveLoad.MINIMAL.value == "MINIMAL"
        assert CognitiveLoad.LOW.value == "LOW"
        assert CognitiveLoad.MODERATE.value == "MODERATE"
        assert CognitiveLoad.HIGH.value == "HIGH"

    def test_wcag_level_values(self) -> None:
        """Test WCAG level enum values."""
        assert WCAGLevel.A.value == "A"
        assert WCAGLevel.AA.value == "AA"
        assert WCAGLevel.AAA.value == "AAA"

    def test_wcag_category_values(self) -> None:
        """Test WCAG category enum values."""
        assert WCAGCategory.PERCEIVABLE.value == "PERCEIVABLE"
        assert WCAGCategory.OPERABLE.value == "OPERABLE"
        assert WCAGCategory.UNDERSTANDABLE.value == "UNDERSTANDABLE"
        assert WCAGCategory.ROBUST.value == "ROBUST"

    def test_violation_severity_values(self) -> None:
        """Test violation severity enum values."""
        assert ViolationSeverity.CRITICAL.value == "CRITICAL"
        assert ViolationSeverity.SERIOUS.value == "SERIOUS"
        assert ViolationSeverity.MODERATE.value == "MODERATE"
        assert ViolationSeverity.MINOR.value == "MINOR"

    def test_accessibility_need_values(self) -> None:
        """Test accessibility need enum values."""
        assert AccessibilityNeed.VISUAL.value == "VISUAL"
        assert AccessibilityNeed.AUDITORY.value == "AUDITORY"
        assert AccessibilityNeed.MOTOR.value == "MOTOR"
        assert AccessibilityNeed.COGNITIVE.value == "COGNITIVE"


class TestGenerationEnums:
    """Test generation-related enum values."""

    def test_response_length_values(self) -> None:
        """Test response length enum values."""
        assert ResponseLength.VERY_SHORT.value == "VERY_SHORT"
        assert ResponseLength.SHORT.value == "SHORT"
        assert ResponseLength.MEDIUM.value == "MEDIUM"
        assert ResponseLength.LONG.value == "LONG"
        assert ResponseLength.DETAILED.value == "DETAILED"

    def test_empathy_level_values(self) -> None:
        """Test empathy level enum values."""
        assert EmpathyLevel.LOW.value == "LOW"
        assert EmpathyLevel.MODERATE.value == "MODERATE"
        assert EmpathyLevel.HIGH.value == "HIGH"

    def test_emoji_usage_values(self) -> None:
        """Test emoji usage enum values."""
        assert EmojiUsage.NONE.value == "NONE"
        assert EmojiUsage.MINIMAL.value == "MINIMAL"
        assert EmojiUsage.MODERATE.value == "MODERATE"
        assert EmojiUsage.EXPRESSIVE.value == "EXPRESSIVE"


class TestVoiceEnums:
    """Test voice-related enum values."""

    def test_voice_gender_values(self) -> None:
        """Test voice gender enum values."""
        assert VoiceGender.MALE.value == "MALE"
        assert VoiceGender.FEMALE.value == "FEMALE"
        assert VoiceGender.NEUTRAL.value == "NEUTRAL"

    def test_voice_speaking_style_values(self) -> None:
        """Test voice speaking style enum values."""
        assert VoiceSpeakingStyle.NEUTRAL.value == "NEUTRAL"
        assert VoiceSpeakingStyle.FRIENDLY.value == "FRIENDLY"
        assert VoiceSpeakingStyle.PROFESSIONAL.value == "PROFESSIONAL"
        assert VoiceSpeakingStyle.EMPATHETIC.value == "EMPATHETIC"


# ============================================
# Integration Type Tests
# ============================================


class TestMultiModalResponseConstruction:
    """Test MultiModalResponse type construction."""

    def test_text_only_response(self) -> None:
        """Test creating a text-only response."""
        response = MultiModalResponse(
            response_id="text-001",
            primary_modality=Modality.TEXT,
            text=TextResponse(
                content="Hello, world!",
                format=TextFormat.PLAIN,
            ),
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.MINIMAL,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        assert response.response_id == "text-001"
        assert response.primary_modality == Modality.TEXT
        assert response.text is not None
        assert response.text.content == "Hello, world!"

    def test_voice_only_response(self) -> None:
        """Test creating a voice-only response."""
        response = MultiModalResponse(
            response_id="voice-001",
            primary_modality=Modality.VOICE,
            voice=VoiceResponse(
                text="Hello, welcome to the assistant.",
                language="en-US",
            ),
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.LOW,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        assert response.response_id == "voice-001"
        assert response.primary_modality == Modality.VOICE
        assert response.voice is not None
        assert response.voice.text == "Hello, welcome to the assistant."

    def test_visual_only_response(self) -> None:
        """Test creating a visual-only response."""
        response = MultiModalResponse(
            response_id="visual-001",
            primary_modality=Modality.VISUAL,
            visuals=[
                MultiModalVisualElement(
                    element_type=MultiModalVisualType.IMAGE,
                    content="https://example.com/image.png",
                    alt_text="A sample image",
                    priority=1,
                    interactive=False,
                ),
            ],
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.LOW,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        assert response.response_id == "visual-001"
        assert response.primary_modality == Modality.VISUAL
        assert response.visuals is not None
        assert len(response.visuals) == 1

    def test_hybrid_response(self) -> None:
        """Test creating a hybrid multi-modal response."""
        response = MultiModalResponse(
            response_id="hybrid-001",
            primary_modality=Modality.HYBRID,
            text=TextResponse(
                content="Your meeting has been scheduled.",
                format=TextFormat.PLAIN,
            ),
            voice=VoiceResponse(
                text="Your meeting has been scheduled for tomorrow.",
                language="en-US",
            ),
            visuals=[
                MultiModalVisualElement(
                    element_type=MultiModalVisualType.CARD,
                    content="Meeting confirmation card",
                    alt_text="Meeting scheduled for tomorrow at 2 PM",
                    priority=1,
                    interactive=True,
                ),
            ],
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.LOW,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        assert response.response_id == "hybrid-001"
        assert response.primary_modality == Modality.HYBRID
        assert response.text is not None
        assert response.voice is not None
        assert response.visuals is not None

    def test_response_with_actions(self) -> None:
        """Test creating a response with actions."""
        response = MultiModalResponse(
            response_id="action-001",
            primary_modality=Modality.TEXT,
            text=TextResponse(
                content="Would you like to proceed?",
                format=TextFormat.PLAIN,
            ),
            actions=[
                MultiModalAction(
                    action_id="confirm",
                    interaction_type=InteractionType.BUTTON,
                    label="Yes, proceed",
                    is_primary=True,
                    is_destructive=False,
                    requires_confirmation=False,
                    disabled=False,
                ),
                MultiModalAction(
                    action_id="cancel",
                    interaction_type=InteractionType.BUTTON,
                    label="Cancel",
                    is_primary=False,
                    is_destructive=False,
                    requires_confirmation=False,
                    disabled=False,
                ),
            ],
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.LOW,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        assert response.actions is not None
        assert len(response.actions) == 2
        assert response.actions[0].label == "Yes, proceed"
        assert response.actions[0].is_primary is True


class TestAccessibilityMetaConstruction:
    """Test AccessibilityMeta construction."""

    def test_minimal_accessibility_meta(self) -> None:
        """Test creating minimal accessibility metadata."""
        meta = AccessibilityMeta(
            aria_live=AriaLiveType.OFF,
            cognitive_load=CognitiveLoad.LOW,
            supports_screen_reader=True,
            supports_keyboard_nav=True,
            high_contrast_available=False,
            reduced_motion_safe=True,
        )

        assert meta.aria_live == AriaLiveType.OFF
        assert meta.cognitive_load == CognitiveLoad.LOW
        assert meta.supports_screen_reader is True

    def test_full_accessibility_meta(self) -> None:
        """Test creating full accessibility metadata."""
        meta = AccessibilityMeta(
            aria_label="Navigation menu",
            aria_live=AriaLiveType.POLITE,
            reading_level=ReadingLevel.MIDDLE_SCHOOL,
            cognitive_load=CognitiveLoad.LOW,
            supports_screen_reader=True,
            supports_keyboard_nav=True,
            high_contrast_available=True,
            reduced_motion_safe=True,
        )

        assert meta.aria_label == "Navigation menu"
        assert meta.reading_level == ReadingLevel.MIDDLE_SCHOOL


class TestDimensionsConstruction:
    """Test Dimensions type construction."""

    def test_basic_dimensions(self) -> None:
        """Test creating basic dimensions."""
        dims = Dimensions(
            width="100%",
            height="auto",
        )

        assert dims.width == "100%"
        assert dims.height == "auto"

    def test_dimensions_with_constraints(self) -> None:
        """Test creating dimensions with constraints."""
        dims = Dimensions(
            width="100%",
            height="auto",
            min_width="300px",
            max_width="800px",
            aspect_ratio="16:9",
        )

        assert dims.min_width == "300px"
        assert dims.max_width == "800px"
        assert dims.aspect_ratio == "16:9"


# ============================================
# Cross-Feature Integration Tests
# ============================================


class TestMultiModalIntegration:
    """Integration tests verifying multi-modal features work together."""

    def test_response_for_blind_user(self) -> None:
        """Test response configuration for visually impaired users."""
        # A response for a blind user should prioritize voice and text
        response = MultiModalResponse(
            response_id="blind-user-001",
            primary_modality=Modality.VOICE,
            text=TextResponse(
                content="You have 3 unread messages.",
                format=TextFormat.PLAIN,
            ),
            voice=VoiceResponse(
                text="You have three unread messages.",
                language="en-US",
                ssml='<speak>You have <say-as interpret-as="cardinal">3</say-as> unread messages.</speak>',
            ),
            accessibility=AccessibilityMeta(
                aria_label="Unread message count",
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.MINIMAL,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        # Verify voice is prioritized
        assert response.primary_modality == Modality.VOICE
        # Verify text is available as fallback/screen reader content
        assert response.text is not None
        # Verify SSML provides enhanced speech
        assert response.voice is not None
        assert response.voice.ssml is not None
        assert "say-as" in response.voice.ssml
        # Verify accessibility features
        assert response.accessibility.supports_screen_reader is True

    def test_response_for_deaf_user(self) -> None:
        """Test response configuration for hearing impaired users."""
        # A response for a deaf user should prioritize text and visual
        response = MultiModalResponse(
            response_id="deaf-user-001",
            primary_modality=Modality.TEXT,
            text=TextResponse(
                content="Meeting scheduled for tomorrow at 2 PM.",
                formatted_content="**Meeting scheduled** for tomorrow at 2 PM.",
                format=TextFormat.MARKDOWN,
            ),
            visuals=[
                MultiModalVisualElement(
                    element_type=MultiModalVisualType.CARD,
                    content="Meeting details card",
                    alt_text="Meeting confirmation showing date and time",
                    priority=1,
                    interactive=True,
                ),
            ],
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.LOW,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        # Verify text is prioritized
        assert response.primary_modality == Modality.TEXT
        # Verify visual content is available
        assert response.visuals is not None
        assert len(response.visuals) == 1
        # Verify no voice-only content
        assert response.voice is None

    def test_response_in_noisy_environment(self) -> None:
        """Test response for noisy environment."""
        # In noisy environments, visual and text should be preferred
        response = MultiModalResponse(
            response_id="noisy-env-001",
            primary_modality=Modality.VISUAL,
            text=TextResponse(
                content="Order confirmed: #12345",
                format=TextFormat.PLAIN,
            ),
            visuals=[
                MultiModalVisualElement(
                    element_type=MultiModalVisualType.CARD,
                    content="Order confirmation card",
                    alt_text="Order #12345 confirmed",
                    priority=1,
                    interactive=False,
                ),
            ],
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.ASSERTIVE,
                cognitive_load=CognitiveLoad.MINIMAL,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        # Visual should be primary in noisy environments
        assert response.primary_modality == Modality.VISUAL
        # Text should be available
        assert response.text is not None
        # ARIA live should be assertive for important notifications
        assert response.accessibility.aria_live == AriaLiveType.ASSERTIVE

    def test_response_in_private_environment(self) -> None:
        """Test response for private environment."""
        # In private environments, voice is acceptable
        response = MultiModalResponse(
            response_id="private-env-001",
            primary_modality=Modality.VOICE,
            voice=VoiceResponse(
                text="Your balance is five thousand dollars.",
                language="en-US",
            ),
            text=TextResponse(
                content="Your balance is $5,000.00",
                format=TextFormat.PLAIN,
            ),
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.MINIMAL,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        # Voice can be primary in private settings
        assert response.primary_modality == Modality.VOICE
        # Text fallback should always be available
        assert response.text is not None


class TestEnumCompleteness:
    """Test that all enum values are properly defined."""

    def test_all_modality_values_accessible(self) -> None:
        """Test all modality values can be accessed."""
        modalities = list(Modality)
        assert len(modalities) >= 4
        values = {m.value for m in modalities}
        assert "TEXT" in values
        assert "VOICE" in values
        assert "VISUAL" in values
        assert "HYBRID" in values

    def test_all_visual_types_accessible(self) -> None:
        """Test all visual types can be accessed."""
        types = list(MultiModalVisualType)
        assert len(types) >= 10
        values = {t.value for t in types}
        assert "CARD" in values
        assert "IMAGE" in values
        assert "TABLE" in values

    def test_all_interaction_types_accessible(self) -> None:
        """Test all interaction types can be accessed."""
        types = list(InteractionType)
        assert len(types) >= 5
        values = {t.value for t in types}
        assert "BUTTON" in values
        assert "LINK" in values

    def test_all_wcag_levels_accessible(self) -> None:
        """Test all WCAG levels can be accessed."""
        levels = list(WCAGLevel)
        assert len(levels) >= 3
        values = {l.value for l in levels}
        assert "A" in values
        assert "AA" in values
        assert "AAA" in values
