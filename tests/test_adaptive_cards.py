"""Tests for Adaptive Cards exporter."""

from __future__ import annotations

import json
import pytest

from src.lui_schema_export.adaptive_cards import (
    # Core classes
    AdaptiveCardBuilder,
    AdaptiveCardValidator,
    AdaptiveCardExporter,
    AdaptiveCardOptions,
    # Functions
    export_to_adaptive_card,
    create_adaptive_card,
    validate_adaptive_card,
    # Enums
    Spacing,
    HorizontalAlignment,
    VerticalContentAlignment,
    ContainerStyle,
    TextSize,
    TextWeight,
    TextColor,
    FontType,
    ImageSize,
    ImageStyle,
    CardElementType,
    CardActionType,
    AdaptiveCardPlatform,
    TextInputStyle,
    ChoiceInputStyle,
    # Dataclasses
    ValidationResult,
    ValidationError,
    ValidationWarning,
    PlatformCompatibility,
)


# ============================================
# Enum Tests
# ============================================


class TestSpacingEnum:
    """Tests for Spacing enum."""

    def test_all_values_exist(self) -> None:
        """Test all spacing values are defined."""
        assert Spacing.NONE.value == "none"
        assert Spacing.SMALL.value == "small"
        assert Spacing.DEFAULT.value == "default"
        assert Spacing.MEDIUM.value == "medium"
        assert Spacing.LARGE.value == "large"
        assert Spacing.EXTRA_LARGE.value == "extraLarge"
        assert Spacing.PADDING.value == "padding"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(Spacing) == 7


class TestHorizontalAlignmentEnum:
    """Tests for HorizontalAlignment enum."""

    def test_all_values_exist(self) -> None:
        """Test all alignment values are defined."""
        assert HorizontalAlignment.LEFT.value == "left"
        assert HorizontalAlignment.CENTER.value == "center"
        assert HorizontalAlignment.RIGHT.value == "right"


class TestVerticalContentAlignmentEnum:
    """Tests for VerticalContentAlignment enum."""

    def test_all_values_exist(self) -> None:
        """Test all alignment values are defined."""
        assert VerticalContentAlignment.TOP.value == "top"
        assert VerticalContentAlignment.CENTER.value == "center"
        assert VerticalContentAlignment.BOTTOM.value == "bottom"


class TestContainerStyleEnum:
    """Tests for ContainerStyle enum."""

    def test_all_values_exist(self) -> None:
        """Test all container styles are defined."""
        assert ContainerStyle.DEFAULT.value == "default"
        assert ContainerStyle.EMPHASIS.value == "emphasis"
        assert ContainerStyle.GOOD.value == "good"
        assert ContainerStyle.ATTENTION.value == "attention"
        assert ContainerStyle.WARNING.value == "warning"
        assert ContainerStyle.ACCENT.value == "accent"


class TestTextSizeEnum:
    """Tests for TextSize enum."""

    def test_all_values_exist(self) -> None:
        """Test all text sizes are defined."""
        assert TextSize.SMALL.value == "small"
        assert TextSize.DEFAULT.value == "default"
        assert TextSize.MEDIUM.value == "medium"
        assert TextSize.LARGE.value == "large"
        assert TextSize.EXTRA_LARGE.value == "extraLarge"


class TestTextWeightEnum:
    """Tests for TextWeight enum."""

    def test_all_values_exist(self) -> None:
        """Test all text weights are defined."""
        assert TextWeight.LIGHTER.value == "lighter"
        assert TextWeight.DEFAULT.value == "default"
        assert TextWeight.BOLDER.value == "bolder"


class TestTextColorEnum:
    """Tests for TextColor enum."""

    def test_all_values_exist(self) -> None:
        """Test all text colors are defined."""
        assert TextColor.DEFAULT.value == "default"
        assert TextColor.DARK.value == "dark"
        assert TextColor.LIGHT.value == "light"
        assert TextColor.ACCENT.value == "accent"
        assert TextColor.GOOD.value == "good"
        assert TextColor.WARNING.value == "warning"
        assert TextColor.ATTENTION.value == "attention"


class TestFontTypeEnum:
    """Tests for FontType enum."""

    def test_all_values_exist(self) -> None:
        """Test all font types are defined."""
        assert FontType.DEFAULT.value == "default"
        assert FontType.MONOSPACE.value == "monospace"


class TestImageSizeEnum:
    """Tests for ImageSize enum."""

    def test_all_values_exist(self) -> None:
        """Test all image sizes are defined."""
        assert ImageSize.AUTO.value == "auto"
        assert ImageSize.STRETCH.value == "stretch"
        assert ImageSize.SMALL.value == "small"
        assert ImageSize.MEDIUM.value == "medium"
        assert ImageSize.LARGE.value == "large"


class TestImageStyleEnum:
    """Tests for ImageStyle enum."""

    def test_all_values_exist(self) -> None:
        """Test all image styles are defined."""
        assert ImageStyle.DEFAULT.value == "default"
        assert ImageStyle.PERSON.value == "person"


class TestCardElementTypeEnum:
    """Tests for CardElementType enum."""

    def test_all_values_exist(self) -> None:
        """Test all element types are defined."""
        assert CardElementType.TEXT_BLOCK.value == "TextBlock"
        assert CardElementType.IMAGE.value == "Image"
        assert CardElementType.RICH_TEXT_BLOCK.value == "RichTextBlock"
        assert CardElementType.FACT_SET.value == "FactSet"
        assert CardElementType.CONTAINER.value == "Container"
        assert CardElementType.COLUMN_SET.value == "ColumnSet"
        assert CardElementType.COLUMN.value == "Column"
        assert CardElementType.TABLE.value == "Table"
        assert CardElementType.INPUT_TEXT.value == "Input.Text"
        assert CardElementType.INPUT_NUMBER.value == "Input.Number"
        assert CardElementType.INPUT_DATE.value == "Input.Date"
        assert CardElementType.INPUT_TIME.value == "Input.Time"
        assert CardElementType.INPUT_TOGGLE.value == "Input.Toggle"
        assert CardElementType.INPUT_CHOICE_SET.value == "Input.ChoiceSet"


class TestCardActionTypeEnum:
    """Tests for CardActionType enum."""

    def test_all_values_exist(self) -> None:
        """Test all action types are defined."""
        assert CardActionType.OPEN_URL.value == "Action.OpenUrl"
        assert CardActionType.SUBMIT.value == "Action.Submit"
        assert CardActionType.SHOW_CARD.value == "Action.ShowCard"
        assert CardActionType.TOGGLE_VISIBILITY.value == "Action.ToggleVisibility"
        assert CardActionType.EXECUTE.value == "Action.Execute"


class TestAdaptiveCardPlatformEnum:
    """Tests for AdaptiveCardPlatform enum."""

    def test_all_values_exist(self) -> None:
        """Test all platforms are defined."""
        assert AdaptiveCardPlatform.GENERIC.value == "generic"
        assert AdaptiveCardPlatform.TEAMS.value == "teams"
        assert AdaptiveCardPlatform.OUTLOOK.value == "outlook"
        assert AdaptiveCardPlatform.WINDOWS.value == "windows"
        assert AdaptiveCardPlatform.WEB.value == "web"
        assert AdaptiveCardPlatform.BOT_FRAMEWORK.value == "bot_framework"


class TestTextInputStyleEnum:
    """Tests for TextInputStyle enum."""

    def test_all_values_exist(self) -> None:
        """Test all input styles are defined."""
        assert TextInputStyle.TEXT.value == "text"
        assert TextInputStyle.TEL.value == "tel"
        assert TextInputStyle.URL.value == "url"
        assert TextInputStyle.EMAIL.value == "email"
        assert TextInputStyle.PASSWORD.value == "password"


class TestChoiceInputStyleEnum:
    """Tests for ChoiceInputStyle enum."""

    def test_all_values_exist(self) -> None:
        """Test all choice input styles are defined."""
        assert ChoiceInputStyle.COMPACT.value == "compact"
        assert ChoiceInputStyle.EXPANDED.value == "expanded"
        assert ChoiceInputStyle.FILTERED.value == "filtered"


# ============================================
# AdaptiveCardBuilder Tests
# ============================================


class TestAdaptiveCardBuilder:
    """Tests for AdaptiveCardBuilder."""

    def test_create_empty_card(self) -> None:
        """Test creating an empty card."""
        builder = AdaptiveCardBuilder()
        card = builder.build()

        assert card["type"] == "AdaptiveCard"
        assert card["version"] == "1.5"
        assert card["body"] == []

    def test_create_card_with_custom_version(self) -> None:
        """Test creating a card with custom schema version."""
        builder = AdaptiveCardBuilder(schema_version="1.3")
        card = builder.build()

        assert card["version"] == "1.3"

    def test_add_text_block_basic(self) -> None:
        """Test adding a basic text block."""
        builder = AdaptiveCardBuilder()
        builder.add_text_block("Hello, World!")
        card = builder.build()

        assert len(card["body"]) == 1
        element = card["body"][0]
        assert element["type"] == "TextBlock"
        assert element["text"] == "Hello, World!"
        assert element["wrap"] is True

    def test_add_text_block_with_styling(self) -> None:
        """Test adding a text block with styling."""
        builder = AdaptiveCardBuilder()
        builder.add_text_block(
            "Styled Text",
            size=TextSize.LARGE,
            weight=TextWeight.BOLDER,
            color=TextColor.ACCENT,
            horizontal_alignment=HorizontalAlignment.CENTER,
            is_subtle=True,
            max_lines=3,
            font_type=FontType.MONOSPACE,
        )
        card = builder.build()

        element = card["body"][0]
        assert element["size"] == "large"
        assert element["weight"] == "bolder"
        assert element["color"] == "accent"
        assert element["horizontalAlignment"] == "center"
        assert element["isSubtle"] is True
        assert element["maxLines"] == 3
        assert element["fontType"] == "monospace"

    def test_add_text_block_with_spacing(self) -> None:
        """Test adding a text block with spacing and separator."""
        builder = AdaptiveCardBuilder()
        builder.add_text_block(
            "Text with spacing",
            spacing=Spacing.LARGE,
            separator=True,
            element_id="text-1",
        )
        card = builder.build()

        element = card["body"][0]
        assert element["spacing"] == "large"
        assert element["separator"] is True
        assert element["id"] == "text-1"

    def test_add_image_basic(self) -> None:
        """Test adding a basic image."""
        builder = AdaptiveCardBuilder()
        builder.add_image("https://example.com/image.png")
        card = builder.build()

        assert len(card["body"]) == 1
        element = card["body"][0]
        assert element["type"] == "Image"
        assert element["url"] == "https://example.com/image.png"

    def test_add_image_with_options(self) -> None:
        """Test adding an image with options."""
        builder = AdaptiveCardBuilder()
        builder.add_image(
            "https://example.com/avatar.png",
            alt_text="User avatar",
            size=ImageSize.MEDIUM,
            style=ImageStyle.PERSON,
            width="100px",
            height="100px",
            horizontal_alignment=HorizontalAlignment.CENTER,
        )
        card = builder.build()

        element = card["body"][0]
        assert element["altText"] == "User avatar"
        assert element["size"] == "medium"
        assert element["style"] == "person"
        assert element["width"] == "100px"
        assert element["height"] == "100px"
        assert element["horizontalAlignment"] == "center"

    def test_add_fact_set(self) -> None:
        """Test adding a fact set."""
        builder = AdaptiveCardBuilder()
        builder.add_fact_set([
            ("Name", "John Doe"),
            ("Email", "john@example.com"),
            ("Status", "Active"),
        ])
        card = builder.build()

        element = card["body"][0]
        assert element["type"] == "FactSet"
        assert len(element["facts"]) == 3
        assert element["facts"][0]["title"] == "Name"
        assert element["facts"][0]["value"] == "John Doe"

    def test_container_basic(self) -> None:
        """Test adding a container with items."""
        builder = AdaptiveCardBuilder()
        builder.start_container()
        builder.add_text_block("Inside container")
        builder.end_container()
        card = builder.build()

        assert len(card["body"]) == 1
        container = card["body"][0]
        assert container["type"] == "Container"
        assert len(container["items"]) == 1
        assert container["items"][0]["text"] == "Inside container"

    def test_container_with_styling(self) -> None:
        """Test container with styling options."""
        builder = AdaptiveCardBuilder()
        builder.start_container(
            style=ContainerStyle.EMPHASIS,
            spacing=Spacing.MEDIUM,
            separator=True,
            element_id="container-1",
            vertical_content_alignment=VerticalContentAlignment.CENTER,
            bleed=True,
        )
        builder.add_text_block("Content")
        builder.end_container()
        card = builder.build()

        container = card["body"][0]
        assert container["style"] == "emphasis"
        assert container["spacing"] == "medium"
        assert container["separator"] is True
        assert container["id"] == "container-1"
        assert container["verticalContentAlignment"] == "center"
        assert container["bleed"] is True

    def test_nested_containers(self) -> None:
        """Test nested containers."""
        builder = AdaptiveCardBuilder()
        builder.start_container()
        builder.add_text_block("Outer")
        builder.start_container()
        builder.add_text_block("Inner")
        builder.end_container()
        builder.add_text_block("Outer again")
        builder.end_container()
        card = builder.build()

        outer = card["body"][0]
        assert len(outer["items"]) == 3
        assert outer["items"][0]["text"] == "Outer"
        assert outer["items"][1]["type"] == "Container"
        assert outer["items"][1]["items"][0]["text"] == "Inner"
        assert outer["items"][2]["text"] == "Outer again"

    def test_column_set_basic(self) -> None:
        """Test creating a column set."""
        builder = AdaptiveCardBuilder()
        builder.start_column_set()
        builder.add_column("1")
        builder.add_text_block("Column 1")
        builder.end_column()
        builder.add_column("1")
        builder.add_text_block("Column 2")
        builder.end_column()
        builder.end_column_set()
        card = builder.build()

        column_set = card["body"][0]
        assert column_set["type"] == "ColumnSet"
        assert len(column_set["columns"]) == 2
        assert column_set["columns"][0]["width"] == "1"
        assert column_set["columns"][0]["items"][0]["text"] == "Column 1"

    def test_column_with_options(self) -> None:
        """Test column with styling options."""
        builder = AdaptiveCardBuilder()
        builder.start_column_set()
        builder.add_column(
            "auto",
            style=ContainerStyle.GOOD,
            vertical_content_alignment=VerticalContentAlignment.BOTTOM,
            element_id="col-1",
        )
        builder.add_text_block("Content")
        builder.end_column()
        builder.end_column_set()
        card = builder.build()

        column = card["body"][0]["columns"][0]
        assert column["width"] == "auto"
        assert column["style"] == "good"
        assert column["verticalContentAlignment"] == "bottom"
        assert column["id"] == "col-1"

    def test_input_text_basic(self) -> None:
        """Test adding a basic text input."""
        builder = AdaptiveCardBuilder()
        builder.add_input_text("name-input")
        card = builder.build()

        element = card["body"][0]
        assert element["type"] == "Input.Text"
        assert element["id"] == "name-input"

    def test_input_text_with_options(self) -> None:
        """Test text input with all options."""
        builder = AdaptiveCardBuilder()
        builder.add_input_text(
            "email-input",
            label="Email Address",
            placeholder="Enter your email",
            value="test@example.com",
            is_multiline=False,
            max_length=100,
            style=TextInputStyle.EMAIL,
            is_required=True,
            error_message="Invalid email",
            regex=r"^[\w.-]+@[\w.-]+\.\w+$",
        )
        card = builder.build()

        element = card["body"][0]
        assert element["label"] == "Email Address"
        assert element["placeholder"] == "Enter your email"
        assert element["value"] == "test@example.com"
        assert element["maxLength"] == 100
        assert element["style"] == "email"
        assert element["isRequired"] is True
        assert element["errorMessage"] == "Invalid email"
        assert element["regex"] == r"^[\w.-]+@[\w.-]+\.\w+$"

    def test_input_number(self) -> None:
        """Test adding a number input."""
        builder = AdaptiveCardBuilder()
        builder.add_input_number(
            "quantity-input",
            label="Quantity",
            placeholder="Enter quantity",
            value=1,
            min_value=0,
            max_value=100,
            is_required=True,
        )
        card = builder.build()

        element = card["body"][0]
        assert element["type"] == "Input.Number"
        assert element["id"] == "quantity-input"
        assert element["label"] == "Quantity"
        assert element["value"] == 1
        assert element["min"] == 0
        assert element["max"] == 100
        assert element["isRequired"] is True

    def test_input_date(self) -> None:
        """Test adding a date input."""
        builder = AdaptiveCardBuilder()
        builder.add_input_date(
            "date-input",
            label="Select Date",
            value="2024-01-15",
            min_date="2024-01-01",
            max_date="2024-12-31",
        )
        card = builder.build()

        element = card["body"][0]
        assert element["type"] == "Input.Date"
        assert element["id"] == "date-input"
        assert element["value"] == "2024-01-15"
        assert element["min"] == "2024-01-01"
        assert element["max"] == "2024-12-31"

    def test_input_time(self) -> None:
        """Test adding a time input."""
        builder = AdaptiveCardBuilder()
        builder.add_input_time(
            "time-input",
            label="Select Time",
            value="14:30",
            min_time="09:00",
            max_time="17:00",
        )
        card = builder.build()

        element = card["body"][0]
        assert element["type"] == "Input.Time"
        assert element["id"] == "time-input"
        assert element["value"] == "14:30"
        assert element["min"] == "09:00"
        assert element["max"] == "17:00"

    def test_input_toggle(self) -> None:
        """Test adding a toggle input."""
        builder = AdaptiveCardBuilder()
        builder.add_input_toggle(
            "agree-toggle",
            "I agree to the terms",
            value="false",
            value_on="yes",
            value_off="no",
        )
        card = builder.build()

        element = card["body"][0]
        assert element["type"] == "Input.Toggle"
        assert element["id"] == "agree-toggle"
        assert element["title"] == "I agree to the terms"
        assert element["value"] == "false"
        assert element["valueOn"] == "yes"
        assert element["valueOff"] == "no"

    def test_input_choice_set(self) -> None:
        """Test adding a choice set input."""
        builder = AdaptiveCardBuilder()
        builder.add_input_choice_set(
            "priority-input",
            [
                ("Low", "low"),
                ("Medium", "medium"),
                ("High", "high"),
            ],
            label="Priority",
            value="medium",
            style=ChoiceInputStyle.EXPANDED,
            is_multi_select=False,
        )
        card = builder.build()

        element = card["body"][0]
        assert element["type"] == "Input.ChoiceSet"
        assert element["id"] == "priority-input"
        assert len(element["choices"]) == 3
        assert element["choices"][0]["title"] == "Low"
        assert element["choices"][0]["value"] == "low"
        assert element["style"] == "expanded"

    def test_action_open_url(self) -> None:
        """Test adding an open URL action."""
        builder = AdaptiveCardBuilder()
        builder.add_action_open_url(
            "Visit Website",
            "https://example.com",
            action_id="open-url-1",
            icon_url="https://example.com/icon.png",
            tooltip="Opens example.com",
        )
        card = builder.build()

        assert "actions" in card
        assert len(card["actions"]) == 1
        action = card["actions"][0]
        assert action["type"] == "Action.OpenUrl"
        assert action["title"] == "Visit Website"
        assert action["url"] == "https://example.com"
        assert action["id"] == "open-url-1"
        assert action["iconUrl"] == "https://example.com/icon.png"
        assert action["tooltip"] == "Opens example.com"

    def test_action_submit(self) -> None:
        """Test adding a submit action."""
        builder = AdaptiveCardBuilder()
        builder.add_action_submit(
            "Submit Form",
            data={"action": "submit", "formId": "contact"},
            action_id="submit-1",
            style="positive",
        )
        card = builder.build()

        action = card["actions"][0]
        assert action["type"] == "Action.Submit"
        assert action["title"] == "Submit Form"
        assert action["data"]["action"] == "submit"
        assert action["style"] == "positive"

    def test_action_execute(self) -> None:
        """Test adding an execute action."""
        builder = AdaptiveCardBuilder()
        builder.add_action_execute(
            "Process",
            "processData",
            data={"type": "process"},
            action_id="execute-1",
            associated_inputs="auto",
        )
        card = builder.build()

        action = card["actions"][0]
        assert action["type"] == "Action.Execute"
        assert action["verb"] == "processData"
        assert action["associatedInputs"] == "auto"

    def test_set_fallback_text(self) -> None:
        """Test setting fallback text."""
        builder = AdaptiveCardBuilder()
        builder.set_fallback_text("This is the fallback text")
        card = builder.build()

        assert card["fallbackText"] == "This is the fallback text"

    def test_set_speak(self) -> None:
        """Test setting speak SSML."""
        builder = AdaptiveCardBuilder()
        builder.set_speak("<speak>Hello, this is a test.</speak>")
        card = builder.build()

        assert card["speak"] == "<speak>Hello, this is a test.</speak>"

    def test_set_lang(self) -> None:
        """Test setting language."""
        builder = AdaptiveCardBuilder()
        builder.set_lang("en-US")
        card = builder.build()

        assert card["lang"] == "en-US"

    def test_set_min_height(self) -> None:
        """Test setting minimum height."""
        builder = AdaptiveCardBuilder()
        builder.set_min_height("300px")
        card = builder.build()

        assert card["minHeight"] == "300px"

    def test_set_vertical_content_alignment(self) -> None:
        """Test setting vertical content alignment."""
        builder = AdaptiveCardBuilder()
        builder.set_vertical_content_alignment(VerticalContentAlignment.CENTER)
        card = builder.build()

        assert card["verticalContentAlignment"] == "center"

    def test_set_rtl(self) -> None:
        """Test setting RTL."""
        builder = AdaptiveCardBuilder()
        builder.set_rtl(True)
        card = builder.build()

        assert card["rtl"] is True

    def test_to_json_pretty(self) -> None:
        """Test JSON output (pretty)."""
        builder = AdaptiveCardBuilder()
        builder.add_text_block("Test")
        json_str = builder.to_json()

        assert '"type": "TextBlock"' in json_str
        assert "\n" in json_str

    def test_to_json_minified(self) -> None:
        """Test JSON output (minified)."""
        builder = AdaptiveCardBuilder()
        builder.add_text_block("Test")
        json_str = builder.to_json(minify=True)

        assert '"type":"TextBlock"' in json_str
        assert "\n" not in json_str

    def test_fluent_api_chaining(self) -> None:
        """Test fluent API chaining."""
        card = (
            AdaptiveCardBuilder()
            .add_text_block("Title", size=TextSize.LARGE, weight=TextWeight.BOLDER)
            .add_text_block("Subtitle", is_subtle=True)
            .add_image("https://example.com/img.png", alt_text="Image")
            .add_action_open_url("Learn More", "https://example.com")
            .set_fallback_text("Card content")
            .build()
        )

        assert len(card["body"]) == 3
        assert len(card["actions"]) == 1
        assert card["fallbackText"] == "Card content"


# ============================================
# AdaptiveCardValidator Tests
# ============================================


class TestAdaptiveCardValidator:
    """Tests for AdaptiveCardValidator."""

    def test_validate_valid_card(self) -> None:
        """Test validating a valid card."""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [{"type": "TextBlock", "text": "Hello"}],
            "fallbackText": "Hello",
        }
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_missing_type(self) -> None:
        """Test validation fails without type."""
        card = {"version": "1.5", "body": []}
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert result.is_valid is False
        assert any(e.code == "INVALID_TYPE" for e in result.errors)

    def test_validate_missing_version(self) -> None:
        """Test validation fails without version."""
        card = {"type": "AdaptiveCard", "body": []}
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert result.is_valid is False
        assert any(e.code == "MISSING_VERSION" for e in result.errors)

    def test_validate_missing_body(self) -> None:
        """Test validation fails without body."""
        card = {"type": "AdaptiveCard", "version": "1.5"}
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert result.is_valid is False
        assert any(e.code == "MISSING_BODY" for e in result.errors)

    def test_validate_invalid_body_type(self) -> None:
        """Test validation fails with non-array body."""
        card = {"type": "AdaptiveCard", "version": "1.5", "body": "invalid"}
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert result.is_valid is False
        assert any(e.code == "INVALID_BODY" for e in result.errors)

    def test_validate_unsupported_version_warning(self) -> None:
        """Test warning for unsupported version."""
        card = {
            "type": "AdaptiveCard",
            "version": "2.0",
            "body": [],
            "fallbackText": "Test",
        }
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert any(w.code == "UNSUPPORTED_VERSION" for w in result.warnings)

    def test_validate_missing_accessibility_warning(self) -> None:
        """Test warning for missing accessibility."""
        card = {"type": "AdaptiveCard", "version": "1.5", "body": []}
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert any(w.code == "MISSING_ACCESSIBILITY" for w in result.warnings)

    def test_validate_text_block_missing_text(self) -> None:
        """Test validation fails for TextBlock without text."""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [{"type": "TextBlock"}],
            "fallbackText": "Test",
        }
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert result.is_valid is False
        assert any(e.code == "MISSING_TEXT" for e in result.errors)

    def test_validate_image_missing_url(self) -> None:
        """Test validation fails for Image without url."""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [{"type": "Image"}],
            "fallbackText": "Test",
        }
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert result.is_valid is False
        assert any(e.code == "MISSING_URL" for e in result.errors)

    def test_validate_image_missing_alt_text_warning(self) -> None:
        """Test warning for Image without altText."""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [{"type": "Image", "url": "https://example.com/img.png"}],
            "fallbackText": "Test",
        }
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert any(w.code == "MISSING_ALT_TEXT" for w in result.warnings)

    def test_validate_input_missing_id(self) -> None:
        """Test validation fails for input without id."""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [{"type": "Input.Text"}],
            "fallbackText": "Test",
        }
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert result.is_valid is False
        assert any(e.code == "MISSING_INPUT_ID" for e in result.errors)

    def test_validate_action_missing_url(self) -> None:
        """Test validation fails for Action.OpenUrl without url."""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [],
            "actions": [{"type": "Action.OpenUrl", "title": "Click"}],
            "fallbackText": "Test",
        }
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert result.is_valid is False
        assert any(e.code == "MISSING_ACTION_URL" for e in result.errors)

    def test_validate_action_execute_missing_verb(self) -> None:
        """Test validation fails for Action.Execute without verb."""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [],
            "actions": [{"type": "Action.Execute", "title": "Execute"}],
            "fallbackText": "Test",
        }
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert result.is_valid is False
        assert any(e.code == "MISSING_EXECUTE_VERB" for e in result.errors)

    def test_validate_nested_container(self) -> None:
        """Test validation of nested container elements."""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "Container",
                    "items": [
                        {"type": "TextBlock", "text": "Nested"},
                    ],
                }
            ],
            "fallbackText": "Test",
        }
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert result.is_valid is True

    def test_validate_column_set(self) -> None:
        """Test validation of column set."""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "items": [{"type": "TextBlock", "text": "Col 1"}],
                        },
                        {
                            "type": "Column",
                            "items": [{"type": "TextBlock", "text": "Col 2"}],
                        },
                    ],
                }
            ],
            "fallbackText": "Test",
        }
        validator = AdaptiveCardValidator()
        result = validator.validate(card)

        assert result.is_valid is True

    def test_platform_compatibility_outlook(self) -> None:
        """Test platform compatibility for Outlook."""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [],
            "actions": [{"type": "Action.Execute", "title": "Exec", "verb": "test"}],
            "fallbackText": "Test",
        }
        validator = AdaptiveCardValidator()
        result = validator.validate(card, AdaptiveCardPlatform.OUTLOOK)

        assert result.compatibility is not None
        assert result.compatibility.outlook is False


# ============================================
# AdaptiveCardExporter Tests
# ============================================


class TestAdaptiveCardExporter:
    """Tests for AdaptiveCardExporter."""

    def test_export_basic_schema(self) -> None:
        """Test exporting a basic LUI schema."""
        schema = {
            "visuals": [{"type": "text", "content": "Hello, World!"}],
            "fallback_text": "Hello",
        }
        exporter = AdaptiveCardExporter()
        json_str = exporter.export(schema)
        card = json.loads(json_str)

        assert card["type"] == "AdaptiveCard"
        assert len(card["body"]) == 1
        assert card["body"][0]["type"] == "TextBlock"
        assert card["body"][0]["text"] == "Hello, World!"

    def test_export_with_image(self) -> None:
        """Test exporting schema with image."""
        schema = {
            "visuals": [
                {
                    "type": "image",
                    "url": "https://example.com/img.png",
                    "alt_text": "Test image",
                }
            ],
            "fallback_text": "Image",
        }
        exporter = AdaptiveCardExporter()
        json_str = exporter.export(schema)
        card = json.loads(json_str)

        assert card["body"][0]["type"] == "Image"
        assert card["body"][0]["url"] == "https://example.com/img.png"
        assert card["body"][0]["altText"] == "Test image"

    def test_export_with_list(self) -> None:
        """Test exporting schema with list."""
        schema = {
            "visuals": [{"type": "list", "items": ["Item 1", "Item 2", "Item 3"]}],
            "fallback_text": "List",
        }
        exporter = AdaptiveCardExporter()
        json_str = exporter.export(schema)
        card = json.loads(json_str)

        container = card["body"][0]
        assert container["type"] == "Container"
        assert len(container["items"]) == 3
        assert container["items"][0]["text"] == "• Item 1"

    def test_export_with_table(self) -> None:
        """Test exporting schema with table."""
        schema = {
            "visuals": [
                {
                    "type": "table",
                    "headers": ["Name", "Value"],
                    "rows": [["Item 1", "100"], ["Item 2", "200"]],
                }
            ],
            "fallback_text": "Table",
        }
        exporter = AdaptiveCardExporter()
        json_str = exporter.export(schema)
        card = json.loads(json_str)

        table = card["body"][0]
        assert table["type"] == "Table"
        assert len(table["rows"]) == 3  # 1 header + 2 data rows

    def test_export_with_actions(self) -> None:
        """Test exporting schema with actions."""
        schema = {
            "visuals": [],
            "actions": [
                {"type": "url", "label": "Open", "url": "https://example.com"},
                {"type": "submit", "label": "Submit", "data": {"id": "1"}},
            ],
            "fallback_text": "Actions",
        }
        exporter = AdaptiveCardExporter()
        json_str = exporter.export(schema)
        card = json.loads(json_str)

        assert len(card["actions"]) == 2
        assert card["actions"][0]["type"] == "Action.OpenUrl"
        assert card["actions"][1]["type"] == "Action.Submit"

    def test_export_with_options(self) -> None:
        """Test exporting with custom options."""
        schema = {"visuals": [], "fallback_text": "Test"}
        options = AdaptiveCardOptions(
            schema_version="1.3",
            lang="fr-FR",
            minify=True,
            validate=True,
        )
        exporter = AdaptiveCardExporter(options)
        json_str = exporter.export(schema)

        assert '"version":"1.3"' in json_str
        assert '"lang":"fr-FR"' in json_str
        assert "\n" not in json_str

    def test_export_validation_failure(self) -> None:
        """Test export fails on invalid card."""
        schema = {"visuals": [{"type": "text"}]}  # Missing content
        options = AdaptiveCardOptions(validate=True, include_fallback_text=False)
        exporter = AdaptiveCardExporter(options)

        with pytest.raises(ValueError, match="Invalid Adaptive Card"):
            exporter.export(schema)


# ============================================
# Convenience Function Tests
# ============================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_export_to_adaptive_card(self) -> None:
        """Test export_to_adaptive_card function."""
        schema = {
            "visuals": [{"type": "text", "content": "Test"}],
            "fallback_text": "Test",
        }
        json_str = export_to_adaptive_card(schema)
        card = json.loads(json_str)

        assert card["type"] == "AdaptiveCard"

    def test_create_adaptive_card(self) -> None:
        """Test create_adaptive_card function."""
        builder = create_adaptive_card()
        assert isinstance(builder, AdaptiveCardBuilder)

        card = builder.add_text_block("Test").build()
        assert card["type"] == "AdaptiveCard"

    def test_validate_adaptive_card_dict(self) -> None:
        """Test validate_adaptive_card with dict."""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [{"type": "TextBlock", "text": "Test"}],
            "fallbackText": "Test",
        }
        result = validate_adaptive_card(card)

        assert result.is_valid is True

    def test_validate_adaptive_card_json(self) -> None:
        """Test validate_adaptive_card with JSON string."""
        card_json = json.dumps(
            {
                "type": "AdaptiveCard",
                "version": "1.5",
                "body": [{"type": "TextBlock", "text": "Test"}],
                "fallbackText": "Test",
            }
        )
        result = validate_adaptive_card(card_json)

        assert result.is_valid is True

    def test_validate_adaptive_card_invalid_json(self) -> None:
        """Test validate_adaptive_card with invalid JSON."""
        result = validate_adaptive_card("not valid json")

        assert result.is_valid is False
        assert any(e.code == "INVALID_JSON" for e in result.errors)

    def test_validate_adaptive_card_with_platform(self) -> None:
        """Test validate_adaptive_card with platform target."""
        card = {
            "type": "AdaptiveCard",
            "version": "1.5",
            "body": [],
            "fallbackText": "Test",
        }
        result = validate_adaptive_card(card, AdaptiveCardPlatform.TEAMS)

        assert result.is_valid is True
        assert result.compatibility is not None
        assert result.compatibility.teams is True


# ============================================
# Dataclass Tests
# ============================================


class TestDataclasses:
    """Tests for dataclasses."""

    def test_adaptive_card_options_defaults(self) -> None:
        """Test AdaptiveCardOptions default values."""
        options = AdaptiveCardOptions()

        assert options.schema_version == "1.5"
        assert options.include_fallback_text is True
        assert options.target_platform is None
        assert options.minify is False
        assert options.validate is True
        assert options.lang is None

    def test_validation_error_creation(self) -> None:
        """Test ValidationError creation."""
        error = ValidationError(
            code="TEST_ERROR",
            message="Test error message",
            path="body[0].text",
            element_type="TextBlock",
        )

        assert error.code == "TEST_ERROR"
        assert error.message == "Test error message"
        assert error.path == "body[0].text"
        assert error.element_type == "TextBlock"

    def test_validation_warning_creation(self) -> None:
        """Test ValidationWarning creation."""
        warning = ValidationWarning(
            code="TEST_WARNING",
            message="Test warning message",
            suggestion="Fix it",
            path="body[0]",
        )

        assert warning.code == "TEST_WARNING"
        assert warning.message == "Test warning message"
        assert warning.suggestion == "Fix it"
        assert warning.path == "body[0]"

    def test_platform_compatibility_defaults(self) -> None:
        """Test PlatformCompatibility default values."""
        compatibility = PlatformCompatibility()

        assert compatibility.teams is True
        assert compatibility.outlook is True
        assert compatibility.windows is True
        assert compatibility.web is True
        assert compatibility.unsupported_features == []

    def test_validation_result_creation(self) -> None:
        """Test ValidationResult creation."""
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            schema_version="1.5",
            compatibility=PlatformCompatibility(),
        )

        assert result.is_valid is True
        assert result.schema_version == "1.5"
        assert result.compatibility is not None


# ============================================
# Integration Tests
# ============================================


class TestIntegration:
    """Integration tests for Adaptive Cards."""

    def test_complete_card_workflow(self) -> None:
        """Test complete card creation and validation workflow."""
        # Build a card
        builder = AdaptiveCardBuilder()
        card = (
            builder.add_text_block(
                "Welcome to Adaptive Cards",
                size=TextSize.LARGE,
                weight=TextWeight.BOLDER,
            )
            .add_text_block(
                "This is a sample card with various elements",
                is_subtle=True,
            )
            .start_container(style=ContainerStyle.EMPHASIS)
            .add_fact_set(
                [
                    ("Status", "Active"),
                    ("Priority", "High"),
                    ("Due Date", "2024-12-31"),
                ]
            )
            .end_container()
            .start_column_set()
            .add_column("1")
            .add_image(
                "https://example.com/avatar.png",
                alt_text="User avatar",
                style=ImageStyle.PERSON,
            )
            .end_column()
            .add_column("2")
            .add_text_block("John Doe", weight=TextWeight.BOLDER)
            .add_text_block("Software Engineer", is_subtle=True)
            .end_column()
            .end_column_set()
            .add_input_text("feedback", label="Your Feedback", is_multiline=True)
            .add_action_submit("Submit Feedback", data={"action": "feedback"})
            .add_action_open_url("Learn More", "https://example.com")
            .set_fallback_text("Welcome card with user profile and feedback form")
            .set_lang("en-US")
            .build()
        )

        # Validate the card
        result = validate_adaptive_card(card)
        assert result.is_valid is True

        # Convert to JSON
        json_str = json.dumps(card, indent=2)
        assert "AdaptiveCard" in json_str
        assert "Welcome to Adaptive Cards" in json_str
        assert "John Doe" in json_str
        assert "Action.Submit" in json_str

    def test_form_card(self) -> None:
        """Test creating a form card."""
        builder = AdaptiveCardBuilder()
        card = (
            builder.add_text_block("Contact Form", size=TextSize.LARGE)
            .add_input_text(
                "name",
                label="Name",
                is_required=True,
                error_message="Name is required",
            )
            .add_input_text(
                "email",
                label="Email",
                style=TextInputStyle.EMAIL,
                is_required=True,
            )
            .add_input_choice_set(
                "subject",
                [
                    ("General Inquiry", "general"),
                    ("Support", "support"),
                    ("Feedback", "feedback"),
                ],
                label="Subject",
                style=ChoiceInputStyle.COMPACT,
            )
            .add_input_text("message", label="Message", is_multiline=True)
            .add_action_submit("Send", style="positive")
            .set_fallback_text("Contact form")
            .build()
        )

        result = validate_adaptive_card(card)
        assert result.is_valid is True
        assert len(card["body"]) == 5  # 1 title + 4 inputs
        assert card["actions"][0]["style"] == "positive"

    def test_export_and_validate_lui_schema(self) -> None:
        """Test exporting LUI schema and validating the result."""
        schema = {
            "visuals": [
                {"type": "text", "content": "Task Dashboard"},
                {
                    "type": "table",
                    "headers": ["Task", "Status", "Due"],
                    "rows": [
                        ["Review PRs", "In Progress", "Today"],
                        ["Write tests", "Pending", "Tomorrow"],
                    ],
                },
                {
                    "type": "card",
                    "title": "Reminder",
                    "content": "Don't forget to update the docs!",
                },
            ],
            "actions": [
                {"type": "url", "label": "View All Tasks", "url": "https://tasks.com"},
                {"type": "submit", "label": "Mark Complete", "data": {"action": "complete"}},
            ],
            "fallback_text": "Task dashboard with pending tasks",
        }

        json_str = export_to_adaptive_card(schema)
        card = json.loads(json_str)

        result = validate_adaptive_card(card)
        assert result.is_valid is True
        assert len(card["body"]) == 3
        assert len(card["actions"]) == 2
