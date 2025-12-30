"""Tests for Multi-Modal Type System (Issue #35).

This module tests the core multi-modal type definitions for LUI responses
including voice, text, and visual modalities.
"""

import pytest
from baml_client.types import (
    # Core modality types
    Modality,
    MultiModalResponse,
    # Visual types
    MultiModalVisualType,
    MultiModalVisualElement,
    Dimensions,
    StyleHints,
    # Voice types
    VoiceResponse,
    VoiceConfig,
    VoiceGender,
    VoiceAgeGroup,
    VoiceSpeakingStyle,
    AudioHints,
    SoundEffect,
    SoundTiming,
    VoiceSegment,
    EmphasisLevel,
    # Text types
    TextResponse,
    TextFormat,
    TruncationStrategy,
    TruncationType,
    TextHighlight,
    HighlightType,
    TextAnnotation,
    AnnotationType,
    # Action types
    MultiModalAction,
    InteractionType,
    # Accessibility types
    AccessibilityMeta,
    AriaLiveType,
    ReadingLevel,
    CognitiveLoad,
    TextAlternatives,
    FocusHints,
    # Timing types
    ResponseTiming,
    ResponseSequence,
    ContextHints,
)


class TestModalityEnum:
    """Test Modality enum values."""

    def test_modality_has_all_values(self):
        """Verify all expected modality types exist."""
        expected = {"TEXT", "VOICE", "VISUAL", "HYBRID"}
        actual = {m.name for m in Modality}
        assert actual == expected

    def test_modality_text_value(self):
        """Test TEXT modality."""
        assert Modality.TEXT.value == "TEXT"

    def test_modality_voice_value(self):
        """Test VOICE modality."""
        assert Modality.VOICE.value == "VOICE"

    def test_modality_visual_value(self):
        """Test VISUAL modality."""
        assert Modality.VISUAL.value == "VISUAL"

    def test_modality_hybrid_value(self):
        """Test HYBRID modality."""
        assert Modality.HYBRID.value == "HYBRID"


class TestMultiModalVisualTypeEnum:
    """Test MultiModalVisualType enum values."""

    def test_visual_type_has_all_values(self):
        """Verify all expected visual element types exist."""
        expected = {
            "TEXT_BLOCK",
            "IMAGE",
            "TABLE",
            "CHART",
            "CARD",
            "BUTTON_GROUP",
            "INPUT_FORM",
            "CODE_BLOCK",
            "LIST",
            "MEDIA_PLAYER",
            "MAP",
            "TIMELINE",
            "PROGRESS",
            "AVATAR",
            "BADGE",
        }
        actual = {t.name for t in MultiModalVisualType}
        assert actual == expected

    def test_visual_type_chart(self):
        """Test CHART visual type."""
        assert MultiModalVisualType.CHART.value == "CHART"

    def test_visual_type_card(self):
        """Test CARD visual type."""
        assert MultiModalVisualType.CARD.value == "CARD"


class TestVoiceEnums:
    """Test voice-related enums."""

    def test_voice_gender_values(self):
        """Verify voice gender options."""
        expected = {"MALE", "FEMALE", "NEUTRAL"}
        actual = {g.name for g in VoiceGender}
        assert actual == expected

    def test_voice_age_group_values(self):
        """Verify voice age group options."""
        expected = {"CHILD", "YOUNG_ADULT", "ADULT", "SENIOR"}
        actual = {a.name for a in VoiceAgeGroup}
        assert actual == expected

    def test_voice_speaking_style_values(self):
        """Verify voice speaking style options."""
        expected = {
            "NEUTRAL",
            "CHEERFUL",
            "EMPATHETIC",
            "PROFESSIONAL",
            "CALM",
            "URGENT",
            "FRIENDLY",
            "EXCITED",
        }
        actual = {s.name for s in VoiceSpeakingStyle}
        assert actual == expected

    def test_sound_timing_values(self):
        """Verify sound timing options."""
        expected = {"START", "END", "ON_SUCCESS", "ON_ERROR", "ON_ATTENTION"}
        actual = {t.name for t in SoundTiming}
        assert actual == expected

    def test_emphasis_level_values(self):
        """Verify emphasis level options."""
        expected = {"NONE", "REDUCED", "MODERATE", "STRONG"}
        actual = {e.name for e in EmphasisLevel}
        assert actual == expected


class TestTextEnums:
    """Test text-related enums."""

    def test_text_format_values(self):
        """Verify text format options."""
        expected = {"PLAIN", "MARKDOWN", "HTML", "RICH_TEXT"}
        actual = {f.name for f in TextFormat}
        assert actual == expected

    def test_truncation_type_values(self):
        """Verify truncation type options."""
        expected = {"ELLIPSIS", "FADE", "COLLAPSE", "SCROLL"}
        actual = {t.name for t in TruncationType}
        assert actual == expected

    def test_highlight_type_values(self):
        """Verify highlight type options."""
        expected = {"IMPORTANT", "WARNING", "SUCCESS", "ERROR", "INFO", "CODE", "LINK"}
        actual = {h.name for h in HighlightType}
        assert actual == expected

    def test_annotation_type_values(self):
        """Verify annotation type options."""
        expected = {"FOOTNOTE", "TOOLTIP", "DEFINITION", "CITATION", "COMMENT"}
        actual = {a.name for a in AnnotationType}
        assert actual == expected


class TestInteractionTypeEnum:
    """Test InteractionType enum values."""

    def test_interaction_type_has_all_values(self):
        """Verify all expected interaction types exist."""
        expected = {
            "BUTTON",
            "LINK",
            "VOICE_COMMAND",
            "GESTURE",
            "KEYBOARD",
            "CONTEXTUAL",
            "FORM_SUBMIT",
            "DISMISS",
            "UNDO",
            "REDO",
            "EXPAND",
            "COLLAPSE",
            "SHARE",
            "COPY",
            "DOWNLOAD",
            "PRINT",
        }
        actual = {t.name for t in InteractionType}
        assert actual == expected


class TestAccessibilityEnums:
    """Test accessibility-related enums."""

    def test_aria_live_type_values(self):
        """Verify ARIA live type options."""
        expected = {"OFF", "POLITE", "ASSERTIVE"}
        actual = {t.name for t in AriaLiveType}
        assert actual == expected

    def test_reading_level_values(self):
        """Verify reading level options."""
        expected = {
            "ELEMENTARY",
            "MIDDLE_SCHOOL",
            "HIGH_SCHOOL",
            "COLLEGE",
            "PROFESSIONAL",
        }
        actual = {r.name for r in ReadingLevel}
        assert actual == expected

    def test_cognitive_load_values(self):
        """Verify cognitive load options."""
        expected = {"MINIMAL", "LOW", "MODERATE", "HIGH", "VERY_HIGH"}
        actual = {c.name for c in CognitiveLoad}
        assert actual == expected


class TestDimensionsClass:
    """Test Dimensions class construction."""

    def test_dimensions_creation(self):
        """Test creating Dimensions instance."""
        dims = Dimensions(
            width="100%",
            height="200px",
            aspect_ratio="16:9",
            min_width="100px",
            max_width="800px",
        )
        assert dims.width == "100%"
        assert dims.height == "200px"
        assert dims.aspect_ratio == "16:9"
        assert dims.min_width == "100px"
        assert dims.max_width == "800px"

    def test_dimensions_with_nulls(self):
        """Test Dimensions with optional fields null."""
        dims = Dimensions(
            width="auto",
            height=None,
            aspect_ratio=None,
            min_width=None,
            max_width=None,
        )
        assert dims.width == "auto"
        assert dims.height is None


class TestStyleHintsClass:
    """Test StyleHints class construction."""

    def test_style_hints_creation(self):
        """Test creating StyleHints instance."""
        hints = StyleHints(
            theme="dark",
            color_scheme="primary",
            emphasis="strong",
            animation="fade",
            border_style="rounded",
        )
        assert hints.theme == "dark"
        assert hints.color_scheme == "primary"
        assert hints.emphasis == "strong"
        assert hints.animation == "fade"
        assert hints.border_style == "rounded"


class TestMultiModalVisualElementClass:
    """Test MultiModalVisualElement class construction."""

    def test_visual_element_minimal(self):
        """Test creating minimal visual element."""
        element = MultiModalVisualElement(
            element_type=MultiModalVisualType.CHART,
            content="Sales data chart",
            alt_text=None,
            title=None,
            priority=1,
            interactive=False,
            metadata=None,
            dimensions=None,
            style_hints=None,
        )
        assert element.element_type == MultiModalVisualType.CHART
        assert element.content == "Sales data chart"
        assert element.priority == 1
        assert element.interactive is False

    def test_visual_element_full(self):
        """Test creating visual element with all fields."""
        dims = Dimensions(
            width="100%", height="300px", aspect_ratio=None, min_width=None, max_width=None
        )
        hints = StyleHints(
            theme="light", color_scheme=None, emphasis=None, animation=None, border_style=None
        )
        element = MultiModalVisualElement(
            element_type=MultiModalVisualType.TABLE,
            content="User data table",
            alt_text="Table showing user statistics",
            title="User Statistics",
            priority=1,
            interactive=True,
            metadata={"rows": "10", "columns": "5"},
            dimensions=dims,
            style_hints=hints,
        )
        assert element.element_type == MultiModalVisualType.TABLE
        assert element.alt_text == "Table showing user statistics"
        assert element.title == "User Statistics"
        assert element.interactive is True
        assert element.metadata is not None
        assert element.metadata["rows"] == "10"


class TestVoiceResponseClass:
    """Test VoiceResponse class construction."""

    def test_voice_response_minimal(self):
        """Test creating minimal voice response."""
        voice = VoiceResponse(
            text="Hello, how can I help you today?",
            ssml=None,
            voice_config=None,
            audio_hints=None,
            fallback_text=None,
            language="en-US",
            segments=None,
        )
        assert voice.text == "Hello, how can I help you today?"
        assert voice.language == "en-US"

    def test_voice_response_with_ssml(self):
        """Test voice response with SSML markup."""
        voice = VoiceResponse(
            text="Hello",
            ssml='<speak>Hello, <emphasis level="strong">how can I help</emphasis> you today?</speak>',
            voice_config=None,
            audio_hints=None,
            fallback_text="Hello, how can I help you today?",
            language="en-US",
            segments=None,
        )
        assert voice.ssml is not None
        assert "<speak>" in voice.ssml


class TestVoiceConfigClass:
    """Test VoiceConfig class construction."""

    def test_voice_config_creation(self):
        """Test creating voice configuration."""
        config = VoiceConfig(
            voice_id="voice-123",
            gender=VoiceGender.FEMALE,
            age_group=VoiceAgeGroup.ADULT,
            speaking_rate=1.0,
            pitch=0.0,
            volume=0.8,
            style=VoiceSpeakingStyle.FRIENDLY,
        )
        assert config.voice_id == "voice-123"
        assert config.gender == VoiceGender.FEMALE
        assert config.age_group == VoiceAgeGroup.ADULT
        assert config.speaking_rate == 1.0
        assert config.style == VoiceSpeakingStyle.FRIENDLY


class TestVoiceSegmentClass:
    """Test VoiceSegment class construction."""

    def test_voice_segment_creation(self):
        """Test creating voice segment."""
        segment = VoiceSegment(
            text="Important point",
            ssml='<emphasis level="strong">Important point</emphasis>',
            pause_before_ms=500,
            pause_after_ms=200,
            emphasis=EmphasisLevel.STRONG,
        )
        assert segment.text == "Important point"
        assert segment.pause_before_ms == 500
        assert segment.emphasis == EmphasisLevel.STRONG


class TestSoundEffectClass:
    """Test SoundEffect class construction."""

    def test_sound_effect_creation(self):
        """Test creating sound effect."""
        effect = SoundEffect(
            effect_id="notification-chime",
            timing=SoundTiming.ON_SUCCESS,
            volume=0.5,
        )
        assert effect.effect_id == "notification-chime"
        assert effect.timing == SoundTiming.ON_SUCCESS
        assert effect.volume == 0.5


class TestTextResponseClass:
    """Test TextResponse class construction."""

    def test_text_response_minimal(self):
        """Test creating minimal text response."""
        text = TextResponse(
            content="Order confirmed",
            formatted_content=None,
            format=TextFormat.PLAIN,
            truncation=None,
            highlights=None,
            annotations=None,
        )
        assert text.content == "Order confirmed"
        assert text.format == TextFormat.PLAIN

    def test_text_response_with_markdown(self):
        """Test text response with markdown formatting."""
        text = TextResponse(
            content="Order confirmed",
            formatted_content="**Order #12345** has been *confirmed*.",
            format=TextFormat.MARKDOWN,
            truncation=None,
            highlights=None,
            annotations=None,
        )
        assert text.format == TextFormat.MARKDOWN
        assert text.formatted_content is not None
        assert "**Order" in text.formatted_content


class TestTruncationStrategyClass:
    """Test TruncationStrategy class construction."""

    def test_truncation_strategy_creation(self):
        """Test creating truncation strategy."""
        truncation = TruncationStrategy(
            max_length=500,
            truncation_type=TruncationType.ELLIPSIS,
            show_more_label="Show more...",
        )
        assert truncation.max_length == 500
        assert truncation.truncation_type == TruncationType.ELLIPSIS
        assert truncation.show_more_label == "Show more..."


class TestTextHighlightClass:
    """Test TextHighlight class construction."""

    def test_text_highlight_creation(self):
        """Test creating text highlight."""
        highlight = TextHighlight(
            start_offset=10,
            end_offset=25,
            highlight_type=HighlightType.IMPORTANT,
            label="Key information",
        )
        assert highlight.start_offset == 10
        assert highlight.end_offset == 25
        assert highlight.highlight_type == HighlightType.IMPORTANT


class TestTextAnnotationClass:
    """Test TextAnnotation class construction."""

    def test_text_annotation_creation(self):
        """Test creating text annotation."""
        annotation = TextAnnotation(
            position=50,
            annotation_type=AnnotationType.DEFINITION,
            content="Technical term explanation",
            tooltip="Click to learn more",
        )
        assert annotation.position == 50
        assert annotation.annotation_type == AnnotationType.DEFINITION
        assert annotation.content == "Technical term explanation"


class TestMultiModalActionClass:
    """Test MultiModalAction class construction."""

    def test_action_minimal(self):
        """Test creating minimal action."""
        action = MultiModalAction(
            action_id="action-1",
            interaction_type=InteractionType.BUTTON,
            label="Confirm",
            description=None,
            icon=None,
            keyboard_shortcut=None,
            is_primary=True,
            is_destructive=False,
            requires_confirmation=False,
            disabled=False,
            disabled_reason=None,
            payload=None,
        )
        assert action.action_id == "action-1"
        assert action.interaction_type == InteractionType.BUTTON
        assert action.label == "Confirm"
        assert action.is_primary is True

    def test_action_destructive(self):
        """Test creating destructive action."""
        action = MultiModalAction(
            action_id="delete-1",
            interaction_type=InteractionType.BUTTON,
            label="Delete",
            description="Permanently delete this item",
            icon="trash",
            keyboard_shortcut="Ctrl+D",
            is_primary=False,
            is_destructive=True,
            requires_confirmation=True,
            disabled=False,
            disabled_reason=None,
            payload={"item_id": "123"},
        )
        assert action.is_destructive is True
        assert action.requires_confirmation is True
        assert action.keyboard_shortcut == "Ctrl+D"

    def test_action_disabled(self):
        """Test creating disabled action."""
        action = MultiModalAction(
            action_id="submit-1",
            interaction_type=InteractionType.FORM_SUBMIT,
            label="Submit",
            description=None,
            icon=None,
            keyboard_shortcut=None,
            is_primary=True,
            is_destructive=False,
            requires_confirmation=False,
            disabled=True,
            disabled_reason="Form validation errors",
            payload=None,
        )
        assert action.disabled is True
        assert action.disabled_reason == "Form validation errors"


class TestAccessibilityMetaClass:
    """Test AccessibilityMeta class construction."""

    def test_accessibility_meta_minimal(self):
        """Test creating minimal accessibility metadata."""
        meta = AccessibilityMeta(
            aria_label=None,
            aria_live=AriaLiveType.POLITE,
            reading_level=None,
            cognitive_load=CognitiveLoad.LOW,
            supports_screen_reader=True,
            supports_keyboard_nav=True,
            high_contrast_available=False,
            reduced_motion_safe=True,
            text_alternatives=None,
            focus_hints=None,
        )
        assert meta.aria_live == AriaLiveType.POLITE
        assert meta.cognitive_load == CognitiveLoad.LOW
        assert meta.supports_screen_reader is True

    def test_accessibility_meta_full(self):
        """Test creating full accessibility metadata."""
        alternatives = TextAlternatives(
            simple_text="Order confirmed",
            verbose_text="Your order number 12345 has been confirmed and is being processed.",
            audio_description="Order confirmation notification",
            braille_text=None,
        )
        focus = FocusHints(
            initial_focus="confirm-button",
            focus_trap=False,
            return_focus="order-form",
            skip_link="main-content",
        )
        meta = AccessibilityMeta(
            aria_label="Order confirmation dialog",
            aria_live=AriaLiveType.ASSERTIVE,
            reading_level=ReadingLevel.MIDDLE_SCHOOL,
            cognitive_load=CognitiveLoad.MINIMAL,
            supports_screen_reader=True,
            supports_keyboard_nav=True,
            high_contrast_available=True,
            reduced_motion_safe=True,
            text_alternatives=alternatives,
            focus_hints=focus,
        )
        assert meta.aria_label == "Order confirmation dialog"
        assert meta.reading_level == ReadingLevel.MIDDLE_SCHOOL
        assert meta.text_alternatives is not None
        assert meta.text_alternatives.simple_text == "Order confirmed"
        assert meta.focus_hints is not None
        assert meta.focus_hints.initial_focus == "confirm-button"


class TestResponseTimingClass:
    """Test ResponseTiming class construction."""

    def test_response_timing_creation(self):
        """Test creating response timing."""
        sequence = ResponseSequence(
            total_parts=3,
            current_part=1,
            has_more=True,
            continuation_hint="More details follow...",
        )
        timing = ResponseTiming(
            duration_hint_ms=2000,
            sequence=sequence,
            auto_dismiss_ms=5000,
            delay_ms=100,
        )
        assert timing.duration_hint_ms == 2000
        assert timing.auto_dismiss_ms == 5000
        assert timing.sequence is not None
        assert timing.sequence.total_parts == 3
        assert timing.sequence.has_more is True


class TestContextHintsClass:
    """Test ContextHints class construction."""

    def test_context_hints_creation(self):
        """Test creating context hints."""
        hints = ContextHints(
            preserve_context=True,
            context_key="order-confirmation-12345",
            expires_at="2025-01-16T00:00:00Z",
            related_responses=["resp-001", "resp-002"],
        )
        assert hints.preserve_context is True
        assert hints.context_key == "order-confirmation-12345"
        assert hints.related_responses is not None
        assert len(hints.related_responses) == 2


class TestMultiModalResponseClass:
    """Test MultiModalResponse class construction."""

    def test_multimodal_response_text_only(self):
        """Test creating text-only multi-modal response."""
        text = TextResponse(
            content="Your order has been confirmed.",
            formatted_content=None,
            format=TextFormat.PLAIN,
            truncation=None,
            highlights=None,
            annotations=None,
        )
        meta = AccessibilityMeta(
            aria_label=None,
            aria_live=AriaLiveType.POLITE,
            reading_level=ReadingLevel.MIDDLE_SCHOOL,
            cognitive_load=CognitiveLoad.LOW,
            supports_screen_reader=True,
            supports_keyboard_nav=True,
            high_contrast_available=False,
            reduced_motion_safe=True,
            text_alternatives=None,
            focus_hints=None,
        )
        response = MultiModalResponse(
            response_id="resp-001",
            primary_modality=Modality.TEXT,
            text=text,
            voice=None,
            visuals=None,
            actions=None,
            accessibility=meta,
            timing=None,
            context_hints=None,
        )
        assert response.response_id == "resp-001"
        assert response.primary_modality == Modality.TEXT
        assert response.text is not None
        assert response.text.content == "Your order has been confirmed."
        assert response.voice is None

    def test_multimodal_response_voice_only(self):
        """Test creating voice-only multi-modal response."""
        voice = VoiceResponse(
            text="Good morning! You have 3 meetings today.",
            ssml=None,
            voice_config=None,
            audio_hints=None,
            fallback_text=None,
            language="en-US",
            segments=None,
        )
        meta = AccessibilityMeta(
            aria_label=None,
            aria_live=AriaLiveType.POLITE,
            reading_level=None,
            cognitive_load=CognitiveLoad.LOW,
            supports_screen_reader=True,
            supports_keyboard_nav=False,
            high_contrast_available=False,
            reduced_motion_safe=True,
            text_alternatives=None,
            focus_hints=None,
        )
        response = MultiModalResponse(
            response_id="resp-002",
            primary_modality=Modality.VOICE,
            text=None,
            voice=voice,
            visuals=None,
            actions=None,
            accessibility=meta,
            timing=None,
            context_hints=None,
        )
        assert response.primary_modality == Modality.VOICE
        assert response.voice is not None
        assert response.voice.text == "Good morning! You have 3 meetings today."
        assert response.voice.language == "en-US"

    def test_multimodal_response_visual(self):
        """Test creating visual multi-modal response."""
        visual = MultiModalVisualElement(
            element_type=MultiModalVisualType.CHART,
            content="Monthly revenue data",
            alt_text="Bar chart showing monthly revenue",
            title="Revenue Overview",
            priority=1,
            interactive=True,
            metadata=None,
            dimensions=None,
            style_hints=None,
        )
        meta = AccessibilityMeta(
            aria_label="Revenue chart",
            aria_live=AriaLiveType.OFF,
            reading_level=None,
            cognitive_load=CognitiveLoad.MODERATE,
            supports_screen_reader=True,
            supports_keyboard_nav=True,
            high_contrast_available=True,
            reduced_motion_safe=True,
            text_alternatives=None,
            focus_hints=None,
        )
        response = MultiModalResponse(
            response_id="resp-003",
            primary_modality=Modality.VISUAL,
            text=None,
            voice=None,
            visuals=[visual],
            actions=None,
            accessibility=meta,
            timing=None,
            context_hints=None,
        )
        assert response.primary_modality == Modality.VISUAL
        assert response.visuals is not None
        assert len(response.visuals) == 1
        assert response.visuals[0].element_type == MultiModalVisualType.CHART

    def test_multimodal_response_hybrid(self):
        """Test creating hybrid multi-modal response."""
        text = TextResponse(
            content="Here's your weekly activity summary.",
            formatted_content=None,
            format=TextFormat.PLAIN,
            truncation=None,
            highlights=None,
            annotations=None,
        )
        voice = VoiceResponse(
            text="Here's your weekly activity summary.",
            ssml=None,
            voice_config=None,
            audio_hints=None,
            fallback_text=None,
            language="en-US",
            segments=None,
        )
        visual = MultiModalVisualElement(
            element_type=MultiModalVisualType.CHART,
            content="Steps data",
            alt_text="Chart of daily steps",
            title="Weekly Steps",
            priority=1,
            interactive=False,
            metadata=None,
            dimensions=None,
            style_hints=None,
        )
        action = MultiModalAction(
            action_id="view-details",
            interaction_type=InteractionType.BUTTON,
            label="View Details",
            description=None,
            icon="arrow-right",
            keyboard_shortcut=None,
            is_primary=True,
            is_destructive=False,
            requires_confirmation=False,
            disabled=False,
            disabled_reason=None,
            payload=None,
        )
        meta = AccessibilityMeta(
            aria_label=None,
            aria_live=AriaLiveType.POLITE,
            reading_level=ReadingLevel.MIDDLE_SCHOOL,
            cognitive_load=CognitiveLoad.MODERATE,
            supports_screen_reader=True,
            supports_keyboard_nav=True,
            high_contrast_available=True,
            reduced_motion_safe=True,
            text_alternatives=None,
            focus_hints=None,
        )
        response = MultiModalResponse(
            response_id="resp-004",
            primary_modality=Modality.HYBRID,
            text=text,
            voice=voice,
            visuals=[visual],
            actions=[action],
            accessibility=meta,
            timing=None,
            context_hints=None,
        )
        assert response.primary_modality == Modality.HYBRID
        assert response.text is not None
        assert response.voice is not None
        assert response.visuals is not None
        assert len(response.visuals) == 1
        assert response.actions is not None
        assert len(response.actions) == 1
        assert response.actions[0].label == "View Details"


class TestMultiModalResponseWithTimingAndContext:
    """Test MultiModalResponse with timing and context features."""

    def test_response_with_timing(self):
        """Test response with timing information."""
        sequence = ResponseSequence(
            total_parts=2,
            current_part=1,
            has_more=True,
            continuation_hint="Part 2 includes detailed breakdown",
        )
        timing = ResponseTiming(
            duration_hint_ms=3000,
            sequence=sequence,
            auto_dismiss_ms=None,
            delay_ms=0,
        )
        meta = AccessibilityMeta(
            aria_label=None,
            aria_live=AriaLiveType.POLITE,
            reading_level=None,
            cognitive_load=CognitiveLoad.LOW,
            supports_screen_reader=True,
            supports_keyboard_nav=True,
            high_contrast_available=False,
            reduced_motion_safe=True,
            text_alternatives=None,
            focus_hints=None,
        )
        response = MultiModalResponse(
            response_id="resp-005",
            primary_modality=Modality.TEXT,
            text=TextResponse(
                content="Loading results...",
                formatted_content=None,
                format=TextFormat.PLAIN,
                truncation=None,
                highlights=None,
                annotations=None,
            ),
            voice=None,
            visuals=None,
            actions=None,
            accessibility=meta,
            timing=timing,
            context_hints=None,
        )
        assert response.timing is not None
        assert response.timing.sequence is not None
        assert response.timing.sequence.has_more is True
        assert response.timing.sequence.total_parts == 2

    def test_response_with_context_hints(self):
        """Test response with context preservation hints."""
        hints = ContextHints(
            preserve_context=True,
            context_key="search-session-abc",
            expires_at="2025-01-16T12:00:00Z",
            related_responses=["resp-001", "resp-002"],
        )
        meta = AccessibilityMeta(
            aria_label=None,
            aria_live=AriaLiveType.POLITE,
            reading_level=None,
            cognitive_load=CognitiveLoad.LOW,
            supports_screen_reader=True,
            supports_keyboard_nav=True,
            high_contrast_available=False,
            reduced_motion_safe=True,
            text_alternatives=None,
            focus_hints=None,
        )
        response = MultiModalResponse(
            response_id="resp-006",
            primary_modality=Modality.TEXT,
            text=TextResponse(
                content="Search results for 'products'",
                formatted_content=None,
                format=TextFormat.PLAIN,
                truncation=None,
                highlights=None,
                annotations=None,
            ),
            voice=None,
            visuals=None,
            actions=None,
            accessibility=meta,
            timing=None,
            context_hints=hints,
        )
        assert response.context_hints is not None
        assert response.context_hints.preserve_context is True
        assert response.context_hints.context_key == "search-session-abc"
        assert response.context_hints.related_responses is not None
        assert len(response.context_hints.related_responses) == 2


class TestMultiModalTypeIntegration:
    """Integration tests for multi-modal type system."""

    def test_complex_notification_response(self):
        """Test creating a complex notification response."""
        text = TextResponse(
            content="You have a new message from John",
            formatted_content="You have a **new message** from *John*",
            format=TextFormat.MARKDOWN,
            truncation=TruncationStrategy(
                max_length=100,
                truncation_type=TruncationType.ELLIPSIS,
                show_more_label=None,
            ),
            highlights=[
                TextHighlight(
                    start_offset=15,
                    end_offset=26,
                    highlight_type=HighlightType.IMPORTANT,
                    label=None,
                )
            ],
            annotations=None,
        )
        voice_config = VoiceConfig(
            voice_id=None,
            gender=VoiceGender.NEUTRAL,
            age_group=VoiceAgeGroup.ADULT,
            speaking_rate=1.0,
            pitch=None,
            volume=0.8,
            style=VoiceSpeakingStyle.FRIENDLY,
        )
        voice = VoiceResponse(
            text="You have a new message from John",
            ssml=None,
            voice_config=voice_config,
            audio_hints=AudioHints(
                prefer_streaming=False,
                cache_audio=True,
                background_audio=None,
                sound_effects=[
                    SoundEffect(
                        effect_id="notification",
                        timing=SoundTiming.START,
                        volume=0.3,
                    )
                ],
            ),
            fallback_text="New message from John",
            language="en-US",
            segments=None,
        )
        visual = MultiModalVisualElement(
            element_type=MultiModalVisualType.CARD,
            content="Message preview: Hey, are you available for lunch?",
            alt_text="Message notification card",
            title="New Message",
            priority=1,
            interactive=True,
            metadata={"sender": "John", "timestamp": "2025-01-15T10:30:00Z"},
            dimensions=Dimensions(
                width="300px",
                height="auto",
                aspect_ratio=None,
                min_width=None,
                max_width="400px",
            ),
            style_hints=StyleHints(
                theme="light",
                color_scheme="notification",
                emphasis="normal",
                animation="slide",
                border_style=None,
            ),
        )
        actions = [
            MultiModalAction(
                action_id="reply",
                interaction_type=InteractionType.BUTTON,
                label="Reply",
                description=None,
                icon="reply",
                keyboard_shortcut="R",
                is_primary=True,
                is_destructive=False,
                requires_confirmation=False,
                disabled=False,
                disabled_reason=None,
                payload={"message_id": "msg-123"},
            ),
            MultiModalAction(
                action_id="dismiss",
                interaction_type=InteractionType.DISMISS,
                label="Dismiss",
                description=None,
                icon="x",
                keyboard_shortcut="Esc",
                is_primary=False,
                is_destructive=False,
                requires_confirmation=False,
                disabled=False,
                disabled_reason=None,
                payload=None,
            ),
        ]
        meta = AccessibilityMeta(
            aria_label="New message notification",
            aria_live=AriaLiveType.POLITE,
            reading_level=ReadingLevel.MIDDLE_SCHOOL,
            cognitive_load=CognitiveLoad.LOW,
            supports_screen_reader=True,
            supports_keyboard_nav=True,
            high_contrast_available=True,
            reduced_motion_safe=False,
            text_alternatives=TextAlternatives(
                simple_text="New message from John",
                verbose_text="You received a new message from John at 10:30 AM. The message says: Hey, are you available for lunch?",
                audio_description=None,
                braille_text=None,
            ),
            focus_hints=FocusHints(
                initial_focus="reply",
                focus_trap=True,
                return_focus="inbox-list",
                skip_link=None,
            ),
        )
        timing = ResponseTiming(
            duration_hint_ms=5000,
            sequence=None,
            auto_dismiss_ms=10000,
            delay_ms=0,
        )
        response = MultiModalResponse(
            response_id="notification-001",
            primary_modality=Modality.HYBRID,
            text=text,
            voice=voice,
            visuals=[visual],
            actions=actions,
            accessibility=meta,
            timing=timing,
            context_hints=ContextHints(
                preserve_context=False,
                context_key=None,
                expires_at=None,
                related_responses=None,
            ),
        )

        # Verify all components
        assert response.response_id == "notification-001"
        assert response.primary_modality == Modality.HYBRID
        assert response.text is not None
        assert response.text.format == TextFormat.MARKDOWN
        assert response.text.highlights is not None
        assert len(response.text.highlights) == 1
        assert response.voice is not None
        assert response.voice.voice_config is not None
        assert response.voice.voice_config.style == VoiceSpeakingStyle.FRIENDLY
        assert response.voice.audio_hints is not None
        assert response.voice.audio_hints.sound_effects is not None
        assert len(response.voice.audio_hints.sound_effects) == 1
        assert response.visuals is not None
        assert response.visuals[0].element_type == MultiModalVisualType.CARD
        assert response.actions is not None
        assert len(response.actions) == 2
        assert response.accessibility.aria_live == AriaLiveType.POLITE
        assert response.timing is not None
        assert response.timing.auto_dismiss_ms == 10000
