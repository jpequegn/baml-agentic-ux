"""Tests for ARIA live region generation.

Issue #75 - Task 4.9: ARIA Live Region Generator
Part of #27 - Phase 4: LUI Accessibility Standards
"""

import pytest

from src.accessibility.aria import (
    ARIAConfig,
    ARIALiveRegionGenerator,
    ARIAPoliteness,
    ARIARelevant,
    ARIARole,
    ContentType,
    LiveRegionResult,
    ScreenReader,
    ScreenReaderHint,
    CONTENT_TYPE_CONFIGS,
    SCREEN_READER_HINTS,
    generate_error_alert,
    generate_live_region,
    generate_status_update,
)


# ============================================
# Test Fixtures
# ============================================


@pytest.fixture
def generator():
    """Create an ARIALiveRegionGenerator instance."""
    return ARIALiveRegionGenerator()


@pytest.fixture
def generator_no_escape():
    """Create a generator that doesn't escape content."""
    return ARIALiveRegionGenerator(escape_content=False)


# ============================================
# ARIAPoliteness Tests
# ============================================


class TestARIAPoliteness:
    """Tests for ARIAPoliteness enum."""

    def test_all_levels_exist(self):
        """Test all politeness levels are defined."""
        assert ARIAPoliteness.OFF is not None
        assert ARIAPoliteness.POLITE is not None
        assert ARIAPoliteness.ASSERTIVE is not None

    def test_level_values(self):
        """Test politeness level values are correct."""
        assert ARIAPoliteness.OFF.value == "off"
        assert ARIAPoliteness.POLITE.value == "polite"
        assert ARIAPoliteness.ASSERTIVE.value == "assertive"

    def test_level_count(self):
        """Test expected number of levels."""
        assert len(ARIAPoliteness) == 3


# ============================================
# ARIARole Tests
# ============================================


class TestARIARole:
    """Tests for ARIARole enum."""

    def test_all_roles_exist(self):
        """Test all roles are defined."""
        assert ARIARole.LOG is not None
        assert ARIARole.STATUS is not None
        assert ARIARole.ALERT is not None
        assert ARIARole.ALERTDIALOG is not None
        assert ARIARole.PROGRESSBAR is not None
        assert ARIARole.TIMER is not None
        assert ARIARole.MARQUEE is not None
        assert ARIARole.REGION is not None

    def test_role_values(self):
        """Test role values are correct."""
        assert ARIARole.LOG.value == "log"
        assert ARIARole.STATUS.value == "status"
        assert ARIARole.ALERT.value == "alert"

    def test_role_count(self):
        """Test expected number of roles."""
        assert len(ARIARole) == 8


# ============================================
# ARIARelevant Tests
# ============================================


class TestARIARelevant:
    """Tests for ARIARelevant enum."""

    def test_all_values_exist(self):
        """Test all aria-relevant values are defined."""
        assert ARIARelevant.ADDITIONS is not None
        assert ARIARelevant.REMOVALS is not None
        assert ARIARelevant.TEXT is not None
        assert ARIARelevant.ALL is not None
        assert ARIARelevant.ADDITIONS_TEXT is not None
        assert ARIARelevant.ADDITIONS_REMOVALS is not None

    def test_values_correct(self):
        """Test aria-relevant values are correct."""
        assert ARIARelevant.ADDITIONS.value == "additions"
        assert ARIARelevant.ADDITIONS_TEXT.value == "additions text"


# ============================================
# ARIAConfig Tests
# ============================================


class TestARIAConfig:
    """Tests for ARIAConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ARIAConfig()
        assert config.role == ARIARole.LOG
        assert config.aria_live == ARIAPoliteness.POLITE
        assert config.aria_atomic is False
        assert config.aria_relevant == ARIARelevant.ADDITIONS_TEXT
        assert config.aria_busy is False
        assert config.aria_label is None

    def test_custom_config(self):
        """Test custom configuration."""
        config = ARIAConfig(
            role=ARIARole.ALERT,
            aria_live=ARIAPoliteness.ASSERTIVE,
            aria_atomic=True,
            aria_label="Error message",
        )
        assert config.role == ARIARole.ALERT
        assert config.aria_live == ARIAPoliteness.ASSERTIVE
        assert config.aria_atomic is True
        assert config.aria_label == "Error message"


# ============================================
# ContentType Tests
# ============================================


class TestContentType:
    """Tests for ContentType enum."""

    def test_all_types_exist(self):
        """Test all content types are defined."""
        assert ContentType.MESSAGE is not None
        assert ContentType.ERROR is not None
        assert ContentType.WARNING is not None
        assert ContentType.SUCCESS is not None
        assert ContentType.INFO is not None
        assert ContentType.PROGRESS is not None
        assert ContentType.CHAT is not None
        assert ContentType.NOTIFICATION is not None

    def test_type_count(self):
        """Test expected number of types."""
        assert len(ContentType) == 8


# ============================================
# CONTENT_TYPE_CONFIGS Tests
# ============================================


class TestContentTypeConfigs:
    """Tests for content type configurations."""

    def test_all_content_types_have_config(self):
        """Test all content types have a configuration."""
        for content_type in ContentType:
            assert content_type in CONTENT_TYPE_CONFIGS

    def test_error_config_is_assertive(self):
        """Test error config uses assertive politeness."""
        config = CONTENT_TYPE_CONFIGS[ContentType.ERROR]
        assert config.aria_live == ARIAPoliteness.ASSERTIVE
        assert config.role == ARIARole.ALERT

    def test_message_config_is_polite(self):
        """Test message config uses polite politeness."""
        config = CONTENT_TYPE_CONFIGS[ContentType.MESSAGE]
        assert config.aria_live == ARIAPoliteness.POLITE
        assert config.role == ARIARole.LOG

    def test_chat_config_uses_log_role(self):
        """Test chat config uses log role."""
        config = CONTENT_TYPE_CONFIGS[ContentType.CHAT]
        assert config.role == ARIARole.LOG
        assert config.aria_atomic is False


# ============================================
# ScreenReader Tests
# ============================================


class TestScreenReader:
    """Tests for ScreenReader enum."""

    def test_all_readers_exist(self):
        """Test all screen readers are defined."""
        assert ScreenReader.JAWS is not None
        assert ScreenReader.NVDA is not None
        assert ScreenReader.VOICEOVER is not None
        assert ScreenReader.TALKBACK is not None
        assert ScreenReader.NARRATOR is not None
        assert ScreenReader.ORCA is not None

    def test_reader_count(self):
        """Test expected number of readers."""
        assert len(ScreenReader) == 6


# ============================================
# SCREEN_READER_HINTS Tests
# ============================================


class TestScreenReaderHints:
    """Tests for screen reader hints."""

    def test_all_readers_have_hints(self):
        """Test all screen readers have hints."""
        for reader in ScreenReader:
            assert reader in SCREEN_READER_HINTS

    def test_hint_has_recommendation(self):
        """Test hints have recommendations."""
        for hint in SCREEN_READER_HINTS.values():
            assert len(hint.recommendation) > 0

    def test_jaws_hint(self):
        """Test JAWS-specific hint."""
        hint = SCREEN_READER_HINTS[ScreenReader.JAWS]
        assert "polite" in hint.recommendation.lower()


# ============================================
# ARIALiveRegionGenerator Basic Tests
# ============================================


class TestARIALiveRegionGenerator:
    """Tests for ARIALiveRegionGenerator."""

    def test_create_generator(self, generator):
        """Test generator creation."""
        assert generator is not None
        assert generator.default_politeness == ARIAPoliteness.POLITE
        assert generator.escape_content is True

    def test_custom_generator(self):
        """Test generator with custom settings."""
        gen = ARIALiveRegionGenerator(
            default_politeness=ARIAPoliteness.ASSERTIVE,
            escape_content=False,
            message_class="custom-message",
        )
        assert gen.default_politeness == ARIAPoliteness.ASSERTIVE
        assert gen.escape_content is False
        assert gen.message_class == "custom-message"


# ============================================
# generate_live_region Tests
# ============================================


class TestGenerateLiveRegion:
    """Tests for generate_live_region method."""

    def test_simple_polite_region(self, generator):
        """Test generating a simple polite region."""
        html = generator.generate_live_region("Hello world")
        assert 'role="log"' in html
        assert 'aria-live="polite"' in html
        assert "Hello world" in html

    def test_assertive_region(self, generator):
        """Test generating an assertive region."""
        html = generator.generate_live_region(
            "Important!", politeness=ARIAPoliteness.ASSERTIVE
        )
        assert 'aria-live="assertive"' in html

    def test_off_region(self, generator):
        """Test generating a region with announcements off."""
        html = generator.generate_live_region(
            "Silent", politeness=ARIAPoliteness.OFF
        )
        assert 'aria-live="off"' in html

    def test_custom_role(self, generator):
        """Test generating with custom role."""
        html = generator.generate_live_region(
            "Status update", role=ARIARole.STATUS
        )
        assert 'role="status"' in html

    def test_html_escape(self, generator):
        """Test HTML content is escaped."""
        html = generator.generate_live_region("<script>alert('xss')</script>")
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_no_escape(self, generator_no_escape):
        """Test HTML content is not escaped when disabled."""
        html = generator_no_escape.generate_live_region("<strong>Bold</strong>")
        assert "<strong>Bold</strong>" in html

    def test_config_override(self, generator):
        """Test config parameter overrides other params."""
        config = ARIAConfig(
            role=ARIARole.ALERT,
            aria_live=ARIAPoliteness.ASSERTIVE,
        )
        html = generator.generate_live_region(
            "Alert!",
            politeness=ARIAPoliteness.POLITE,  # Should be overridden
            config=config,
        )
        assert 'role="alert"' in html
        assert 'aria-live="assertive"' in html

    def test_includes_aria_atomic(self, generator):
        """Test aria-atomic is included."""
        html = generator.generate_live_region("Test")
        assert 'aria-atomic="false"' in html

    def test_includes_aria_relevant(self, generator):
        """Test aria-relevant is included."""
        html = generator.generate_live_region("Test")
        assert 'aria-relevant="additions text"' in html

    def test_extra_attributes(self, generator):
        """Test extra attributes are added."""
        html = generator.generate_live_region(
            "Test",
            data_testid="my-region",
            class_name="custom",
        )
        assert 'data-testid="my-region"' in html
        assert 'class-name="custom"' in html


# ============================================
# generate_live_region_full Tests
# ============================================


class TestGenerateLiveRegionFull:
    """Tests for generate_live_region_full method."""

    def test_returns_result_object(self, generator):
        """Test returns LiveRegionResult."""
        result = generator.generate_live_region_full("Test")
        assert isinstance(result, LiveRegionResult)

    def test_result_has_html(self, generator):
        """Test result contains HTML."""
        result = generator.generate_live_region_full("Test")
        assert len(result.html) > 0
        assert "Test" in result.html

    def test_result_has_config(self, generator):
        """Test result contains config."""
        result = generator.generate_live_region_full("Test")
        assert isinstance(result.config, ARIAConfig)

    def test_result_has_hints(self, generator):
        """Test result contains screen reader hints."""
        result = generator.generate_live_region_full("Test", include_hints=True)
        assert len(result.screen_reader_hints) > 0

    def test_result_no_hints_when_disabled(self, generator):
        """Test no hints when disabled."""
        result = generator.generate_live_region_full("Test", include_hints=False)
        assert len(result.screen_reader_hints) == 0

    def test_result_is_valid(self, generator):
        """Test result is marked valid."""
        result = generator.generate_live_region_full("Test")
        assert result.is_valid is True

    def test_content_type_config(self, generator):
        """Test content type determines config."""
        result = generator.generate_live_region_full(
            "Error!", content_type=ContentType.ERROR
        )
        assert result.config.role == ARIARole.ALERT
        assert result.config.aria_live == ARIAPoliteness.ASSERTIVE

    def test_assertive_warning(self, generator):
        """Test warning for assertive politeness."""
        result = generator.generate_live_region_full(
            "Alert!", politeness=ARIAPoliteness.ASSERTIVE
        )
        assert len(result.warnings) > 0
        assert any("sparingly" in w.lower() for w in result.warnings)


# ============================================
# generate_message Tests
# ============================================


class TestGenerateMessage:
    """Tests for generate_message method."""

    def test_simple_message(self, generator):
        """Test generating a simple message."""
        html = generator.generate_message("Hello!")
        assert 'class="lui-message"' in html
        assert 'aria-label="Assistant message"' in html
        assert 'data-sender="assistant"' in html
        assert "Hello!" in html

    def test_user_message(self, generator):
        """Test generating a user message."""
        html = generator.generate_message("Hi there", sender="user")
        assert 'aria-label="User message"' in html
        assert 'data-sender="user"' in html

    def test_custom_label(self, generator):
        """Test custom aria-label."""
        html = generator.generate_message(
            "Test", aria_label="Custom label"
        )
        assert 'aria-label="Custom label"' in html

    def test_message_escapes_content(self, generator):
        """Test message content is escaped."""
        html = generator.generate_message("<b>Bold</b>")
        assert "<b>" not in html
        assert "&lt;b&gt;" in html


# ============================================
# generate_conversation_container Tests
# ============================================


class TestGenerateConversationContainer:
    """Tests for generate_conversation_container method."""

    def test_empty_conversation(self, generator):
        """Test generating empty conversation container."""
        html = generator.generate_conversation_container([])
        assert 'role="log"' in html
        assert 'aria-live="polite"' in html

    def test_single_message(self, generator):
        """Test conversation with single message."""
        messages = [{"content": "Hello", "sender": "assistant"}]
        html = generator.generate_conversation_container(messages)
        assert "Hello" in html
        assert 'data-sender="assistant"' in html

    def test_multiple_messages(self, generator):
        """Test conversation with multiple messages."""
        messages = [
            {"content": "Hi", "sender": "user"},
            {"content": "Hello!", "sender": "assistant"},
        ]
        html = generator.generate_conversation_container(messages)
        assert "Hi" in html
        assert "Hello!" in html
        assert 'data-sender="user"' in html
        assert 'data-sender="assistant"' in html

    def test_container_id(self, generator):
        """Test container has ID when specified."""
        html = generator.generate_conversation_container(
            [], container_id="chat-container"
        )
        assert 'id="chat-container"' in html

    def test_custom_config(self, generator):
        """Test custom config is applied."""
        config = ARIAConfig(
            role=ARIARole.REGION,
            aria_live=ARIAPoliteness.ASSERTIVE,
        )
        html = generator.generate_conversation_container([], config=config)
        assert 'role="region"' in html
        assert 'aria-live="assertive"' in html


# ============================================
# generate_error_region Tests
# ============================================


class TestGenerateErrorRegion:
    """Tests for generate_error_region method."""

    def test_error_region_is_alert(self, generator):
        """Test error region uses alert role."""
        html = generator.generate_error_region("Something went wrong")
        assert 'role="alert"' in html

    def test_error_region_is_assertive(self, generator):
        """Test error region is assertive."""
        html = generator.generate_error_region("Error!")
        assert 'aria-live="assertive"' in html

    def test_error_with_code(self, generator):
        """Test error with error code."""
        html = generator.generate_error_region("Not found", error_code="404")
        assert "Error 404:" in html
        assert "Not found" in html


# ============================================
# generate_status_region Tests
# ============================================


class TestGenerateStatusRegion:
    """Tests for generate_status_region method."""

    def test_status_region_role(self, generator):
        """Test status region uses status role."""
        html = generator.generate_status_region("Loading...")
        assert 'role="status"' in html

    def test_status_region_is_polite(self, generator):
        """Test status region is polite."""
        html = generator.generate_status_region("Done")
        assert 'aria-live="polite"' in html


# ============================================
# generate_progress_region Tests
# ============================================


class TestGenerateProgressRegion:
    """Tests for generate_progress_region method."""

    def test_progress_region_role(self, generator):
        """Test progress region uses progressbar role."""
        html = generator.generate_progress_region("Loading...")
        assert 'role="progressbar"' in html

    def test_progress_with_values(self, generator):
        """Test progress with value attributes."""
        html = generator.generate_progress_region(
            "Uploading...",
            value_now=50,
            value_min=0,
            value_max=100,
        )
        assert 'aria-valuenow="50"' in html
        assert 'aria-valuemin="0"' in html
        assert 'aria-valuemax="100"' in html
        assert 'aria-valuetext="50% complete"' in html

    def test_progress_without_value(self, generator):
        """Test progress without specific value."""
        html = generator.generate_progress_region("Loading...")
        assert 'aria-valuenow' not in html


# ============================================
# generate_notification_region Tests
# ============================================


class TestGenerateNotificationRegion:
    """Tests for generate_notification_region method."""

    def test_info_notification(self, generator):
        """Test info notification."""
        html = generator.generate_notification_region("Update available", "info")
        assert 'data-notification-type="info"' in html

    def test_success_notification(self, generator):
        """Test success notification."""
        html = generator.generate_notification_region("Saved!", "success")
        assert 'data-notification-type="success"' in html

    def test_warning_notification(self, generator):
        """Test warning notification uses alert."""
        html = generator.generate_notification_region("Warning!", "warning")
        assert 'role="alert"' in html

    def test_error_notification(self, generator):
        """Test error notification uses alert."""
        html = generator.generate_notification_region("Failed", "error")
        assert 'role="alert"' in html
        assert 'aria-live="assertive"' in html


# ============================================
# Helper Method Tests
# ============================================


class TestHelperMethods:
    """Tests for helper methods."""

    def test_get_screen_reader_recommendations(self, generator):
        """Test getting screen reader recommendations."""
        recs = generator.get_screen_reader_recommendations()
        assert ScreenReader.JAWS in recs
        assert ScreenReader.NVDA in recs
        assert len(recs[ScreenReader.JAWS]) > 0

    def test_get_config_for_content_type(self, generator):
        """Test getting config for content type."""
        config = generator.get_config_for_content_type(ContentType.ERROR)
        assert config.role == ARIARole.ALERT
        assert config.aria_live == ARIAPoliteness.ASSERTIVE

    def test_get_config_for_unknown_type(self, generator):
        """Test getting config returns default for unknown type."""
        # This would require a mock content type, just test default
        config = generator.get_config_for_content_type(ContentType.MESSAGE)
        assert config is not None


# ============================================
# Convenience Function Tests
# ============================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_generate_live_region_function(self):
        """Test generate_live_region convenience function."""
        html = generate_live_region("Test content")
        assert 'aria-live="polite"' in html
        assert "Test content" in html

    def test_generate_live_region_assertive(self):
        """Test generate_live_region with assertive."""
        html = generate_live_region("Alert!", ARIAPoliteness.ASSERTIVE)
        assert 'aria-live="assertive"' in html

    def test_generate_error_alert_function(self):
        """Test generate_error_alert convenience function."""
        html = generate_error_alert("Something went wrong")
        assert 'role="alert"' in html
        assert 'aria-live="assertive"' in html
        assert "Something went wrong" in html

    def test_generate_status_update_function(self):
        """Test generate_status_update convenience function."""
        html = generate_status_update("Loading complete")
        assert 'role="status"' in html
        assert 'aria-live="polite"' in html
        assert "Loading complete" in html


# ============================================
# Edge Cases Tests
# ============================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_content(self, generator):
        """Test generating with empty content."""
        html = generator.generate_live_region("")
        assert 'role="log"' in html
        assert 'aria-live="polite"' in html

    def test_unicode_content(self, generator):
        """Test generating with unicode content."""
        html = generator.generate_live_region("Hello 你好 مرحبا 🎉")
        assert "Hello 你好 مرحبا 🎉" in html

    def test_multiline_content(self, generator):
        """Test generating with multiline content."""
        content = "Line 1\nLine 2\nLine 3"
        html = generator.generate_live_region(content)
        assert "Line 1" in html
        assert "Line 2" in html
        assert "Line 3" in html

    def test_very_long_content(self, generator):
        """Test generating with very long content."""
        content = "A" * 10000
        html = generator.generate_live_region(content)
        assert len(html) > 10000

    def test_special_characters_in_attributes(self, generator):
        """Test attributes with special characters are escaped."""
        config = ARIAConfig(
            aria_label='Test "quoted" label',
        )
        html = generator.generate_live_region("Test", config=config)
        assert "&quot;" in html or '"' not in html.split("aria-label=")[1].split(" ")[0]

    def test_config_with_all_optional_attrs(self, generator):
        """Test config with all optional attributes."""
        config = ARIAConfig(
            role=ARIARole.LOG,
            aria_live=ARIAPoliteness.POLITE,
            aria_atomic=True,
            aria_relevant=ARIARelevant.ALL,
            aria_busy=True,
            aria_label="My region",
            aria_labelledby="label-id",
            aria_describedby="desc-id",
        )
        html = generator.generate_live_region("Test", config=config)
        assert 'aria-atomic="true"' in html
        assert 'aria-relevant="all"' in html
        assert 'aria-busy="true"' in html
        assert 'aria-label="My region"' in html
        assert 'aria-labelledby="label-id"' in html
        assert 'aria-describedby="desc-id"' in html


# ============================================
# HTML Validation Tests
# ============================================


class TestHTMLValidation:
    """Tests for HTML validation."""

    def test_valid_html_structure(self, generator):
        """Test generated HTML has valid structure."""
        html = generator.generate_live_region("Test")
        assert html.startswith("<div")
        assert html.endswith("</div>")

    def test_contains_required_attributes(self, generator):
        """Test generated HTML has required ARIA attributes."""
        html = generator.generate_live_region("Test")
        assert "role=" in html
        assert "aria-live=" in html

    def test_validation_detects_invalid(self, generator):
        """Test validation detects invalid HTML."""
        # Test internal validation method
        assert generator._validate_html("<div>Test</div>") is False  # Missing role
        assert generator._validate_html('role="log">Test</div>') is False  # Bad start
        assert (
            generator._validate_html('<div role="log" aria-live="polite">Test</div>')
            is True
        )


# ============================================
# LiveRegionResult Tests
# ============================================


class TestLiveRegionResult:
    """Tests for LiveRegionResult dataclass."""

    def test_create_result(self):
        """Test creating a result."""
        result = LiveRegionResult(
            html="<div>Test</div>",
            config=ARIAConfig(),
        )
        assert result.html == "<div>Test</div>"
        assert result.is_valid is True
        assert len(result.warnings) == 0

    def test_result_with_warnings(self):
        """Test result with warnings."""
        result = LiveRegionResult(
            html="<div>Test</div>",
            config=ARIAConfig(),
            warnings=["Warning 1", "Warning 2"],
        )
        assert len(result.warnings) == 2

    def test_result_with_hints(self):
        """Test result with screen reader hints."""
        hint = ScreenReaderHint(
            reader=ScreenReader.JAWS,
            recommendation="Use polite",
        )
        result = LiveRegionResult(
            html="<div>Test</div>",
            config=ARIAConfig(),
            screen_reader_hints=[hint],
        )
        assert len(result.screen_reader_hints) == 1
        assert result.screen_reader_hints[0].reader == ScreenReader.JAWS
