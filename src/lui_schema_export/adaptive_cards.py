"""Adaptive Cards exporter for LUI visual elements.

This module provides utilities for generating, building, and validating
Adaptive Cards from LUI visual elements.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Spacing(str, Enum):
    """Spacing between elements."""

    NONE = "none"
    SMALL = "small"
    DEFAULT = "default"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extraLarge"
    PADDING = "padding"


class HorizontalAlignment(str, Enum):
    """Horizontal alignment."""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class VerticalContentAlignment(str, Enum):
    """Vertical content alignment."""

    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


class ContainerStyle(str, Enum):
    """Container style."""

    DEFAULT = "default"
    EMPHASIS = "emphasis"
    GOOD = "good"
    ATTENTION = "attention"
    WARNING = "warning"
    ACCENT = "accent"


class TextSize(str, Enum):
    """Text sizes."""

    SMALL = "small"
    DEFAULT = "default"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extraLarge"


class TextWeight(str, Enum):
    """Text weights."""

    LIGHTER = "lighter"
    DEFAULT = "default"
    BOLDER = "bolder"


class TextColor(str, Enum):
    """Text colors."""

    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    ACCENT = "accent"
    GOOD = "good"
    WARNING = "warning"
    ATTENTION = "attention"


class FontType(str, Enum):
    """Font types."""

    DEFAULT = "default"
    MONOSPACE = "monospace"


class ImageSize(str, Enum):
    """Image sizes."""

    AUTO = "auto"
    STRETCH = "stretch"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class ImageStyle(str, Enum):
    """Image styles."""

    DEFAULT = "default"
    PERSON = "person"


class CardElementType(str, Enum):
    """Types of card elements."""

    TEXT_BLOCK = "TextBlock"
    IMAGE = "Image"
    RICH_TEXT_BLOCK = "RichTextBlock"
    FACT_SET = "FactSet"
    CONTAINER = "Container"
    COLUMN_SET = "ColumnSet"
    COLUMN = "Column"
    TABLE = "Table"
    TABLE_ROW = "TableRow"
    TABLE_CELL = "TableCell"
    IMAGE_SET = "ImageSet"
    MEDIA = "Media"
    ACTION_SET = "ActionSet"
    INPUT_TEXT = "Input.Text"
    INPUT_NUMBER = "Input.Number"
    INPUT_DATE = "Input.Date"
    INPUT_TIME = "Input.Time"
    INPUT_TOGGLE = "Input.Toggle"
    INPUT_CHOICE_SET = "Input.ChoiceSet"


class CardActionType(str, Enum):
    """Types of card actions."""

    OPEN_URL = "Action.OpenUrl"
    SUBMIT = "Action.Submit"
    SHOW_CARD = "Action.ShowCard"
    TOGGLE_VISIBILITY = "Action.ToggleVisibility"
    EXECUTE = "Action.Execute"


class AdaptiveCardPlatform(str, Enum):
    """Target platforms for Adaptive Cards."""

    GENERIC = "generic"
    TEAMS = "teams"
    OUTLOOK = "outlook"
    WINDOWS = "windows"
    WEB = "web"
    BOT_FRAMEWORK = "bot_framework"


class TextInputStyle(str, Enum):
    """Text input styles."""

    TEXT = "text"
    TEL = "tel"
    URL = "url"
    EMAIL = "email"
    PASSWORD = "password"


class ChoiceInputStyle(str, Enum):
    """Choice input styles."""

    COMPACT = "compact"
    EXPANDED = "expanded"
    FILTERED = "filtered"


@dataclass
class AdaptiveCardOptions:
    """Options for Adaptive Card generation."""

    schema_version: str = "1.5"
    include_fallback_text: bool = True
    target_platform: AdaptiveCardPlatform | None = None
    minify: bool = False
    validate: bool = True
    lang: str | None = None


@dataclass
class ValidationError:
    """Adaptive Card validation error."""

    code: str
    message: str
    path: str | None = None
    element_type: str | None = None


@dataclass
class ValidationWarning:
    """Adaptive Card validation warning."""

    code: str
    message: str
    suggestion: str | None = None
    path: str | None = None


@dataclass
class PlatformCompatibility:
    """Platform compatibility information."""

    teams: bool = True
    outlook: bool = True
    windows: bool = True
    web: bool = True
    unsupported_features: list[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Result of Adaptive Card validation."""

    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationWarning] = field(default_factory=list)
    schema_version: str | None = None
    compatibility: PlatformCompatibility | None = None


class AdaptiveCardBuilder:
    """Builder for constructing Adaptive Cards with a fluent API."""

    def __init__(self, schema_version: str = "1.5"):
        """Initialize the builder.

        Args:
            schema_version: The Adaptive Card schema version.
        """
        self._card: dict[str, Any] = {
            "type": "AdaptiveCard",
            "$schema": f"http://adaptivecards.io/schemas/adaptive-card.json",
            "version": schema_version,
            "body": [],
        }
        self._current_container: list[dict[str, Any]] | None = None
        self._container_stack: list[list[dict[str, Any]]] = []

    def add_text_block(
        self,
        text: str,
        *,
        size: TextSize | None = None,
        weight: TextWeight | None = None,
        color: TextColor | None = None,
        wrap: bool = True,
        horizontal_alignment: HorizontalAlignment | None = None,
        is_subtle: bool = False,
        max_lines: int | None = None,
        font_type: FontType | None = None,
        spacing: Spacing | None = None,
        separator: bool = False,
        element_id: str | None = None,
    ) -> "AdaptiveCardBuilder":
        """Add a text block to the card.

        Args:
            text: The text content.
            size: Text size.
            weight: Text weight.
            color: Text color.
            wrap: Whether to wrap text.
            horizontal_alignment: Text alignment.
            is_subtle: Whether to use subtle styling.
            max_lines: Maximum number of lines.
            font_type: Font type.
            spacing: Spacing above element.
            separator: Show separator above.
            element_id: Unique element ID.

        Returns:
            The builder for chaining.
        """
        element: dict[str, Any] = {"type": "TextBlock", "text": text, "wrap": wrap}

        if size:
            element["size"] = size.value
        if weight:
            element["weight"] = weight.value
        if color:
            element["color"] = color.value
        if horizontal_alignment:
            element["horizontalAlignment"] = horizontal_alignment.value
        if is_subtle:
            element["isSubtle"] = True
        if max_lines:
            element["maxLines"] = max_lines
        if font_type:
            element["fontType"] = font_type.value
        if spacing:
            element["spacing"] = spacing.value
        if separator:
            element["separator"] = True
        if element_id:
            element["id"] = element_id

        self._add_element(element)
        return self

    def add_image(
        self,
        url: str,
        *,
        alt_text: str | None = None,
        size: ImageSize | None = None,
        style: ImageStyle | None = None,
        width: str | None = None,
        height: str | None = None,
        horizontal_alignment: HorizontalAlignment | None = None,
        spacing: Spacing | None = None,
        separator: bool = False,
        element_id: str | None = None,
    ) -> "AdaptiveCardBuilder":
        """Add an image to the card.

        Args:
            url: Image URL.
            alt_text: Alt text for accessibility.
            size: Image size.
            style: Image style (default or person).
            width: Explicit width.
            height: Explicit height.
            horizontal_alignment: Image alignment.
            spacing: Spacing above element.
            separator: Show separator above.
            element_id: Unique element ID.

        Returns:
            The builder for chaining.
        """
        element: dict[str, Any] = {"type": "Image", "url": url}

        if alt_text:
            element["altText"] = alt_text
        if size:
            element["size"] = size.value
        if style:
            element["style"] = style.value
        if width:
            element["width"] = width
        if height:
            element["height"] = height
        if horizontal_alignment:
            element["horizontalAlignment"] = horizontal_alignment.value
        if spacing:
            element["spacing"] = spacing.value
        if separator:
            element["separator"] = True
        if element_id:
            element["id"] = element_id

        self._add_element(element)
        return self

    def add_fact_set(
        self,
        facts: list[tuple[str, str]],
        *,
        spacing: Spacing | None = None,
        separator: bool = False,
        element_id: str | None = None,
    ) -> "AdaptiveCardBuilder":
        """Add a fact set (key-value pairs) to the card.

        Args:
            facts: List of (title, value) tuples.
            spacing: Spacing above element.
            separator: Show separator above.
            element_id: Unique element ID.

        Returns:
            The builder for chaining.
        """
        element: dict[str, Any] = {
            "type": "FactSet",
            "facts": [{"title": title, "value": value} for title, value in facts],
        }

        if spacing:
            element["spacing"] = spacing.value
        if separator:
            element["separator"] = True
        if element_id:
            element["id"] = element_id

        self._add_element(element)
        return self

    def start_container(
        self,
        *,
        style: ContainerStyle | None = None,
        spacing: Spacing | None = None,
        separator: bool = False,
        element_id: str | None = None,
        vertical_content_alignment: VerticalContentAlignment | None = None,
        bleed: bool = False,
    ) -> "AdaptiveCardBuilder":
        """Start a container. Elements added after this will be in the container.

        Args:
            style: Container style.
            spacing: Spacing above container.
            separator: Show separator above.
            element_id: Unique element ID.
            vertical_content_alignment: Vertical alignment.
            bleed: Bleed to parent edges.

        Returns:
            The builder for chaining.
        """
        element: dict[str, Any] = {"type": "Container", "items": []}

        if style:
            element["style"] = style.value
        if spacing:
            element["spacing"] = spacing.value
        if separator:
            element["separator"] = True
        if element_id:
            element["id"] = element_id
        if vertical_content_alignment:
            element["verticalContentAlignment"] = vertical_content_alignment.value
        if bleed:
            element["bleed"] = True

        self._add_element(element)

        # Push current container to stack and set new container
        if self._current_container is not None:
            self._container_stack.append(self._current_container)
        else:
            self._container_stack.append(self._card["body"])

        self._current_container = element["items"]
        return self

    def end_container(self) -> "AdaptiveCardBuilder":
        """End the current container.

        Returns:
            The builder for chaining.
        """
        if self._container_stack:
            self._current_container = self._container_stack.pop()
            if self._current_container is self._card["body"]:
                self._current_container = None
        return self

    def start_column_set(
        self,
        *,
        spacing: Spacing | None = None,
        separator: bool = False,
        element_id: str | None = None,
    ) -> "AdaptiveCardBuilder":
        """Start a column set.

        Args:
            spacing: Spacing above column set.
            separator: Show separator above.
            element_id: Unique element ID.

        Returns:
            The builder for chaining.
        """
        element: dict[str, Any] = {"type": "ColumnSet", "columns": []}

        if spacing:
            element["spacing"] = spacing.value
        if separator:
            element["separator"] = True
        if element_id:
            element["id"] = element_id

        self._add_element(element)

        # Push current container to stack and set columns as new target
        if self._current_container is not None:
            self._container_stack.append(self._current_container)
        else:
            self._container_stack.append(self._card["body"])

        self._current_container = element["columns"]
        return self

    def add_column(
        self,
        width: str = "auto",
        *,
        style: ContainerStyle | None = None,
        vertical_content_alignment: VerticalContentAlignment | None = None,
        element_id: str | None = None,
    ) -> "AdaptiveCardBuilder":
        """Add a column to the current column set.

        Args:
            width: Column width (auto, stretch, or weight like "1").
            style: Column style.
            vertical_content_alignment: Vertical alignment.
            element_id: Unique element ID.

        Returns:
            The builder for chaining.
        """
        column: dict[str, Any] = {"type": "Column", "width": width, "items": []}

        if style:
            column["style"] = style.value
        if vertical_content_alignment:
            column["verticalContentAlignment"] = vertical_content_alignment.value
        if element_id:
            column["id"] = element_id

        if self._current_container is not None:
            self._current_container.append(column)

        # Push current target and set column items as new target
        if self._current_container is not None:
            self._container_stack.append(self._current_container)
        self._current_container = column["items"]
        return self

    def end_column(self) -> "AdaptiveCardBuilder":
        """End the current column.

        Returns:
            The builder for chaining.
        """
        if self._container_stack:
            self._current_container = self._container_stack.pop()
        return self

    def end_column_set(self) -> "AdaptiveCardBuilder":
        """End the current column set.

        Returns:
            The builder for chaining.
        """
        if self._container_stack:
            self._current_container = self._container_stack.pop()
            if self._current_container is self._card["body"]:
                self._current_container = None
        return self

    def add_input_text(
        self,
        input_id: str,
        *,
        label: str | None = None,
        placeholder: str | None = None,
        value: str | None = None,
        is_multiline: bool = False,
        max_length: int | None = None,
        style: TextInputStyle | None = None,
        is_required: bool = False,
        error_message: str | None = None,
        regex: str | None = None,
        spacing: Spacing | None = None,
    ) -> "AdaptiveCardBuilder":
        """Add a text input field.

        Args:
            input_id: Input field ID.
            label: Input label.
            placeholder: Placeholder text.
            value: Default value.
            is_multiline: Multi-line input.
            max_length: Maximum character length.
            style: Input style (text, tel, url, email, password).
            is_required: Required field.
            error_message: Error message for validation.
            regex: Validation regex.
            spacing: Spacing above element.

        Returns:
            The builder for chaining.
        """
        element: dict[str, Any] = {"type": "Input.Text", "id": input_id}

        if label:
            element["label"] = label
        if placeholder:
            element["placeholder"] = placeholder
        if value:
            element["value"] = value
        if is_multiline:
            element["isMultiline"] = True
        if max_length:
            element["maxLength"] = max_length
        if style:
            element["style"] = style.value
        if is_required:
            element["isRequired"] = True
        if error_message:
            element["errorMessage"] = error_message
        if regex:
            element["regex"] = regex
        if spacing:
            element["spacing"] = spacing.value

        self._add_element(element)
        return self

    def add_input_number(
        self,
        input_id: str,
        *,
        label: str | None = None,
        placeholder: str | None = None,
        value: float | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
        is_required: bool = False,
        error_message: str | None = None,
        spacing: Spacing | None = None,
    ) -> "AdaptiveCardBuilder":
        """Add a number input field.

        Args:
            input_id: Input field ID.
            label: Input label.
            placeholder: Placeholder text.
            value: Default value.
            min_value: Minimum value.
            max_value: Maximum value.
            is_required: Required field.
            error_message: Error message for validation.
            spacing: Spacing above element.

        Returns:
            The builder for chaining.
        """
        element: dict[str, Any] = {"type": "Input.Number", "id": input_id}

        if label:
            element["label"] = label
        if placeholder:
            element["placeholder"] = placeholder
        if value is not None:
            element["value"] = value
        if min_value is not None:
            element["min"] = min_value
        if max_value is not None:
            element["max"] = max_value
        if is_required:
            element["isRequired"] = True
        if error_message:
            element["errorMessage"] = error_message
        if spacing:
            element["spacing"] = spacing.value

        self._add_element(element)
        return self

    def add_input_date(
        self,
        input_id: str,
        *,
        label: str | None = None,
        placeholder: str | None = None,
        value: str | None = None,
        min_date: str | None = None,
        max_date: str | None = None,
        is_required: bool = False,
        error_message: str | None = None,
        spacing: Spacing | None = None,
    ) -> "AdaptiveCardBuilder":
        """Add a date input field.

        Args:
            input_id: Input field ID.
            label: Input label.
            placeholder: Placeholder text.
            value: Default value (YYYY-MM-DD).
            min_date: Minimum date (YYYY-MM-DD).
            max_date: Maximum date (YYYY-MM-DD).
            is_required: Required field.
            error_message: Error message for validation.
            spacing: Spacing above element.

        Returns:
            The builder for chaining.
        """
        element: dict[str, Any] = {"type": "Input.Date", "id": input_id}

        if label:
            element["label"] = label
        if placeholder:
            element["placeholder"] = placeholder
        if value:
            element["value"] = value
        if min_date:
            element["min"] = min_date
        if max_date:
            element["max"] = max_date
        if is_required:
            element["isRequired"] = True
        if error_message:
            element["errorMessage"] = error_message
        if spacing:
            element["spacing"] = spacing.value

        self._add_element(element)
        return self

    def add_input_time(
        self,
        input_id: str,
        *,
        label: str | None = None,
        placeholder: str | None = None,
        value: str | None = None,
        min_time: str | None = None,
        max_time: str | None = None,
        is_required: bool = False,
        error_message: str | None = None,
        spacing: Spacing | None = None,
    ) -> "AdaptiveCardBuilder":
        """Add a time input field.

        Args:
            input_id: Input field ID.
            label: Input label.
            placeholder: Placeholder text.
            value: Default value (HH:MM).
            min_time: Minimum time (HH:MM).
            max_time: Maximum time (HH:MM).
            is_required: Required field.
            error_message: Error message for validation.
            spacing: Spacing above element.

        Returns:
            The builder for chaining.
        """
        element: dict[str, Any] = {"type": "Input.Time", "id": input_id}

        if label:
            element["label"] = label
        if placeholder:
            element["placeholder"] = placeholder
        if value:
            element["value"] = value
        if min_time:
            element["min"] = min_time
        if max_time:
            element["max"] = max_time
        if is_required:
            element["isRequired"] = True
        if error_message:
            element["errorMessage"] = error_message
        if spacing:
            element["spacing"] = spacing.value

        self._add_element(element)
        return self

    def add_input_toggle(
        self,
        input_id: str,
        title: str,
        *,
        value: str = "false",
        value_on: str = "true",
        value_off: str = "false",
        is_required: bool = False,
        spacing: Spacing | None = None,
    ) -> "AdaptiveCardBuilder":
        """Add a toggle input.

        Args:
            input_id: Input field ID.
            title: Toggle title/label.
            value: Default value.
            value_on: Value when on.
            value_off: Value when off.
            is_required: Required field.
            spacing: Spacing above element.

        Returns:
            The builder for chaining.
        """
        element: dict[str, Any] = {
            "type": "Input.Toggle",
            "id": input_id,
            "title": title,
            "value": value,
            "valueOn": value_on,
            "valueOff": value_off,
        }

        if is_required:
            element["isRequired"] = True
        if spacing:
            element["spacing"] = spacing.value

        self._add_element(element)
        return self

    def add_input_choice_set(
        self,
        input_id: str,
        choices: list[tuple[str, str]],
        *,
        label: str | None = None,
        value: str | None = None,
        is_multi_select: bool = False,
        style: ChoiceInputStyle | None = None,
        is_required: bool = False,
        error_message: str | None = None,
        placeholder: str | None = None,
        wrap: bool = False,
        spacing: Spacing | None = None,
    ) -> "AdaptiveCardBuilder":
        """Add a choice set input.

        Args:
            input_id: Input field ID.
            choices: List of (title, value) tuples.
            label: Input label.
            value: Default value(s).
            is_multi_select: Allow multiple selections.
            style: Choice input style (compact, expanded, filtered).
            is_required: Required field.
            error_message: Error message for validation.
            placeholder: Placeholder text.
            wrap: Wrap choice labels.
            spacing: Spacing above element.

        Returns:
            The builder for chaining.
        """
        element: dict[str, Any] = {
            "type": "Input.ChoiceSet",
            "id": input_id,
            "choices": [{"title": title, "value": val} for title, val in choices],
        }

        if label:
            element["label"] = label
        if value:
            element["value"] = value
        if is_multi_select:
            element["isMultiSelect"] = True
        if style:
            element["style"] = style.value
        if is_required:
            element["isRequired"] = True
        if error_message:
            element["errorMessage"] = error_message
        if placeholder:
            element["placeholder"] = placeholder
        if wrap:
            element["wrap"] = True
        if spacing:
            element["spacing"] = spacing.value

        self._add_element(element)
        return self

    def add_action_open_url(
        self,
        title: str,
        url: str,
        *,
        action_id: str | None = None,
        icon_url: str | None = None,
        tooltip: str | None = None,
        style: str | None = None,
    ) -> "AdaptiveCardBuilder":
        """Add an open URL action.

        Args:
            title: Action button title.
            url: URL to open.
            action_id: Action ID.
            icon_url: Icon URL.
            tooltip: Tooltip text.
            style: Action style (default, positive, destructive).

        Returns:
            The builder for chaining.
        """
        action: dict[str, Any] = {"type": "Action.OpenUrl", "title": title, "url": url}

        if action_id:
            action["id"] = action_id
        if icon_url:
            action["iconUrl"] = icon_url
        if tooltip:
            action["tooltip"] = tooltip
        if style:
            action["style"] = style

        self._add_action(action)
        return self

    def add_action_submit(
        self,
        title: str,
        *,
        data: dict[str, Any] | str | None = None,
        action_id: str | None = None,
        icon_url: str | None = None,
        tooltip: str | None = None,
        style: str | None = None,
        associated_inputs: str | None = None,
    ) -> "AdaptiveCardBuilder":
        """Add a submit action.

        Args:
            title: Action button title.
            data: Data to submit.
            action_id: Action ID.
            icon_url: Icon URL.
            tooltip: Tooltip text.
            style: Action style (default, positive, destructive).
            associated_inputs: Which inputs to include (auto, none).

        Returns:
            The builder for chaining.
        """
        action: dict[str, Any] = {"type": "Action.Submit", "title": title}

        if data:
            action["data"] = data
        if action_id:
            action["id"] = action_id
        if icon_url:
            action["iconUrl"] = icon_url
        if tooltip:
            action["tooltip"] = tooltip
        if style:
            action["style"] = style
        if associated_inputs:
            action["associatedInputs"] = associated_inputs

        self._add_action(action)
        return self

    def add_action_execute(
        self,
        title: str,
        verb: str,
        *,
        data: dict[str, Any] | str | None = None,
        action_id: str | None = None,
        icon_url: str | None = None,
        tooltip: str | None = None,
        style: str | None = None,
        associated_inputs: str | None = None,
    ) -> "AdaptiveCardBuilder":
        """Add an execute action (for Bot Framework).

        Args:
            title: Action button title.
            verb: Action verb.
            data: Data to submit.
            action_id: Action ID.
            icon_url: Icon URL.
            tooltip: Tooltip text.
            style: Action style.
            associated_inputs: Which inputs to include.

        Returns:
            The builder for chaining.
        """
        action: dict[str, Any] = {
            "type": "Action.Execute",
            "title": title,
            "verb": verb,
        }

        if data:
            action["data"] = data
        if action_id:
            action["id"] = action_id
        if icon_url:
            action["iconUrl"] = icon_url
        if tooltip:
            action["tooltip"] = tooltip
        if style:
            action["style"] = style
        if associated_inputs:
            action["associatedInputs"] = associated_inputs

        self._add_action(action)
        return self

    def set_fallback_text(self, text: str) -> "AdaptiveCardBuilder":
        """Set the fallback text for screen readers.

        Args:
            text: Fallback text.

        Returns:
            The builder for chaining.
        """
        self._card["fallbackText"] = text
        return self

    def set_speak(self, ssml: str) -> "AdaptiveCardBuilder":
        """Set the speech text (SSML) for the card.

        Args:
            ssml: SSML content.

        Returns:
            The builder for chaining.
        """
        self._card["speak"] = ssml
        return self

    def set_lang(self, lang: str) -> "AdaptiveCardBuilder":
        """Set the language code for the card.

        Args:
            lang: Language code (e.g., "en-US").

        Returns:
            The builder for chaining.
        """
        self._card["lang"] = lang
        return self

    def set_min_height(self, height: str) -> "AdaptiveCardBuilder":
        """Set the minimum height of the card.

        Args:
            height: Minimum height (e.g., "200px").

        Returns:
            The builder for chaining.
        """
        self._card["minHeight"] = height
        return self

    def set_vertical_content_alignment(
        self, alignment: VerticalContentAlignment
    ) -> "AdaptiveCardBuilder":
        """Set the vertical content alignment of the card.

        Args:
            alignment: Vertical alignment.

        Returns:
            The builder for chaining.
        """
        self._card["verticalContentAlignment"] = alignment.value
        return self

    def set_rtl(self, rtl: bool) -> "AdaptiveCardBuilder":
        """Set right-to-left layout.

        Args:
            rtl: Enable RTL layout.

        Returns:
            The builder for chaining.
        """
        self._card["rtl"] = rtl
        return self

    def build(self) -> dict[str, Any]:
        """Build and return the Adaptive Card dictionary.

        Returns:
            The complete Adaptive Card as a dictionary.
        """
        return self._card.copy()

    def to_json(self, minify: bool = False) -> str:
        """Convert the card to JSON string.

        Args:
            minify: Whether to minify the output.

        Returns:
            JSON string representation.
        """
        if minify:
            return json.dumps(self._card, separators=(",", ":"))
        return json.dumps(self._card, indent=2)

    def _add_element(self, element: dict[str, Any]) -> None:
        """Add an element to the current container."""
        if self._current_container is not None:
            self._current_container.append(element)
        else:
            self._card["body"].append(element)

    def _add_action(self, action: dict[str, Any]) -> None:
        """Add an action to the card."""
        if "actions" not in self._card:
            self._card["actions"] = []
        self._card["actions"].append(action)


class AdaptiveCardValidator:
    """Validator for Adaptive Cards."""

    # Supported schema versions
    SUPPORTED_VERSIONS = ["1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6"]

    # Elements introduced in each version
    VERSION_ELEMENTS: dict[str, list[str]] = {
        "1.0": [
            "TextBlock",
            "Image",
            "Container",
            "ColumnSet",
            "Column",
            "FactSet",
            "ImageSet",
        ],
        "1.1": ["Media"],
        "1.2": ["ActionSet", "RichTextBlock"],
        "1.3": ["Table"],
        "1.4": [],
        "1.5": ["Input.ChoiceSet.filtered"],
        "1.6": [],
    }

    # Platform-specific limitations
    PLATFORM_LIMITATIONS: dict[str, list[str]] = {
        "teams": ["Action.ShowCard nested more than 3 levels"],
        "outlook": ["Media", "Action.Execute"],
        "windows": [],
        "web": [],
    }

    def validate(
        self,
        card: dict[str, Any],
        target_platform: AdaptiveCardPlatform | None = None,
    ) -> ValidationResult:
        """Validate an Adaptive Card.

        Args:
            card: The card to validate.
            target_platform: Target platform for compatibility checks.

        Returns:
            ValidationResult with errors, warnings, and compatibility info.
        """
        errors: list[ValidationError] = []
        warnings: list[ValidationWarning] = []

        # Check required fields
        if card.get("type") != "AdaptiveCard":
            errors.append(
                ValidationError(
                    code="INVALID_TYPE",
                    message="Card type must be 'AdaptiveCard'",
                    path="type",
                )
            )

        version = card.get("version")
        if not version:
            errors.append(
                ValidationError(
                    code="MISSING_VERSION",
                    message="Card must have a version",
                    path="version",
                )
            )
        elif version not in self.SUPPORTED_VERSIONS:
            warnings.append(
                ValidationWarning(
                    code="UNSUPPORTED_VERSION",
                    message=f"Version {version} may not be supported by all renderers",
                    suggestion=f"Consider using version 1.5 or lower",
                    path="version",
                )
            )

        # Check body
        body = card.get("body")
        if body is None:
            errors.append(
                ValidationError(
                    code="MISSING_BODY",
                    message="Card must have a body",
                    path="body",
                )
            )
        elif not isinstance(body, list):
            errors.append(
                ValidationError(
                    code="INVALID_BODY",
                    message="Card body must be an array",
                    path="body",
                )
            )
        else:
            # Validate body elements
            for i, element in enumerate(body):
                self._validate_element(element, f"body[{i}]", errors, warnings)

        # Check actions
        actions = card.get("actions")
        if actions:
            if not isinstance(actions, list):
                errors.append(
                    ValidationError(
                        code="INVALID_ACTIONS",
                        message="Card actions must be an array",
                        path="actions",
                    )
                )
            else:
                for i, action in enumerate(actions):
                    self._validate_action(action, f"actions[{i}]", errors, warnings)

        # Check accessibility
        if not card.get("fallbackText") and not card.get("speak"):
            warnings.append(
                ValidationWarning(
                    code="MISSING_ACCESSIBILITY",
                    message="Card lacks fallbackText or speak for accessibility",
                    suggestion="Add fallbackText for screen reader support",
                )
            )

        # Check platform compatibility
        compatibility = self._check_platform_compatibility(card, target_platform)

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            schema_version=version,
            compatibility=compatibility,
        )

    def _validate_element(
        self,
        element: dict[str, Any],
        path: str,
        errors: list[ValidationError],
        warnings: list[ValidationWarning],
    ) -> None:
        """Validate a card element."""
        if not isinstance(element, dict):
            errors.append(
                ValidationError(
                    code="INVALID_ELEMENT",
                    message="Element must be an object",
                    path=path,
                )
            )
            return

        element_type = element.get("type")
        if not element_type:
            errors.append(
                ValidationError(
                    code="MISSING_TYPE",
                    message="Element must have a type",
                    path=f"{path}.type",
                )
            )
            return

        # Validate specific element types
        if element_type == "TextBlock":
            if not element.get("text"):
                errors.append(
                    ValidationError(
                        code="MISSING_TEXT",
                        message="TextBlock must have text",
                        path=f"{path}.text",
                        element_type=element_type,
                    )
                )

        elif element_type == "Image":
            if not element.get("url"):
                errors.append(
                    ValidationError(
                        code="MISSING_URL",
                        message="Image must have a url",
                        path=f"{path}.url",
                        element_type=element_type,
                    )
                )
            if not element.get("altText"):
                warnings.append(
                    ValidationWarning(
                        code="MISSING_ALT_TEXT",
                        message="Image lacks altText for accessibility",
                        suggestion="Add altText to describe the image",
                        path=f"{path}.altText",
                    )
                )

        elif element_type == "Container":
            items = element.get("items")
            if items:
                for i, item in enumerate(items):
                    self._validate_element(item, f"{path}.items[{i}]", errors, warnings)

        elif element_type == "ColumnSet":
            columns = element.get("columns")
            if columns:
                for i, column in enumerate(columns):
                    self._validate_column(column, f"{path}.columns[{i}]", errors, warnings)

        elif element_type == "FactSet":
            facts = element.get("facts")
            if not facts:
                warnings.append(
                    ValidationWarning(
                        code="EMPTY_FACT_SET",
                        message="FactSet has no facts",
                        path=f"{path}.facts",
                    )
                )

        # Validate input elements
        elif element_type.startswith("Input."):
            if not element.get("id"):
                errors.append(
                    ValidationError(
                        code="MISSING_INPUT_ID",
                        message=f"{element_type} must have an id",
                        path=f"{path}.id",
                        element_type=element_type,
                    )
                )

    def _validate_column(
        self,
        column: dict[str, Any],
        path: str,
        errors: list[ValidationError],
        warnings: list[ValidationWarning],
    ) -> None:
        """Validate a column."""
        if column.get("type") != "Column":
            errors.append(
                ValidationError(
                    code="INVALID_COLUMN_TYPE",
                    message="Column type must be 'Column'",
                    path=f"{path}.type",
                )
            )

        items = column.get("items")
        if items:
            for i, item in enumerate(items):
                self._validate_element(item, f"{path}.items[{i}]", errors, warnings)

    def _validate_action(
        self,
        action: dict[str, Any],
        path: str,
        errors: list[ValidationError],
        warnings: list[ValidationWarning],
    ) -> None:
        """Validate a card action."""
        if not isinstance(action, dict):
            errors.append(
                ValidationError(
                    code="INVALID_ACTION",
                    message="Action must be an object",
                    path=path,
                )
            )
            return

        action_type = action.get("type")
        if not action_type:
            errors.append(
                ValidationError(
                    code="MISSING_ACTION_TYPE",
                    message="Action must have a type",
                    path=f"{path}.type",
                )
            )
            return

        if not action.get("title"):
            warnings.append(
                ValidationWarning(
                    code="MISSING_ACTION_TITLE",
                    message="Action lacks title",
                    suggestion="Add a title for user clarity",
                    path=f"{path}.title",
                )
            )

        # Validate specific action types
        if action_type == "Action.OpenUrl":
            if not action.get("url"):
                errors.append(
                    ValidationError(
                        code="MISSING_ACTION_URL",
                        message="Action.OpenUrl must have a url",
                        path=f"{path}.url",
                    )
                )

        elif action_type == "Action.ShowCard":
            card = action.get("card")
            if not card:
                errors.append(
                    ValidationError(
                        code="MISSING_SHOW_CARD",
                        message="Action.ShowCard must have a card",
                        path=f"{path}.card",
                    )
                )

        elif action_type == "Action.Execute":
            if not action.get("verb"):
                errors.append(
                    ValidationError(
                        code="MISSING_EXECUTE_VERB",
                        message="Action.Execute must have a verb",
                        path=f"{path}.verb",
                    )
                )

    def _check_platform_compatibility(
        self,
        card: dict[str, Any],
        target_platform: AdaptiveCardPlatform | None,
    ) -> PlatformCompatibility:
        """Check platform compatibility."""
        compatibility = PlatformCompatibility()
        unsupported: list[str] = []

        # Check for platform-specific issues
        body = card.get("body", [])
        if isinstance(body, list):
            self._check_elements_compatibility(body, unsupported)

        actions = card.get("actions", [])
        for action in actions:
            if action.get("type") == "Action.Execute":
                if target_platform == AdaptiveCardPlatform.OUTLOOK:
                    unsupported.append("Action.Execute (not supported in Outlook)")
                    compatibility.outlook = False

        # Check for Media elements
        if isinstance(body, list) and self._has_element_type(body, "Media"):
            if target_platform == AdaptiveCardPlatform.OUTLOOK:
                unsupported.append("Media (not supported in Outlook)")
                compatibility.outlook = False

        compatibility.unsupported_features = unsupported
        return compatibility

    def _check_elements_compatibility(
        self,
        elements: list[dict[str, Any]],
        unsupported: list[str],
    ) -> None:
        """Recursively check elements for compatibility issues."""
        for element in elements:
            element_type = element.get("type")

            # Check nested containers
            if element_type == "Container":
                items = element.get("items", [])
                self._check_elements_compatibility(items, unsupported)

            elif element_type == "ColumnSet":
                columns = element.get("columns", [])
                for column in columns:
                    items = column.get("items", [])
                    self._check_elements_compatibility(items, unsupported)

    def _has_element_type(self, elements: list[dict[str, Any]], element_type: str) -> bool:
        """Check if any element has the given type."""
        for element in elements:
            if element.get("type") == element_type:
                return True

            # Check nested containers
            if element.get("type") == "Container":
                items = element.get("items", [])
                if self._has_element_type(items, element_type):
                    return True

            elif element.get("type") == "ColumnSet":
                columns = element.get("columns", [])
                for column in columns:
                    items = column.get("items", [])
                    if self._has_element_type(items, element_type):
                        return True

        return False


class AdaptiveCardExporter:
    """Exporter for LUI schemas to Adaptive Cards format."""

    def __init__(self, options: AdaptiveCardOptions | None = None):
        """Initialize the exporter.

        Args:
            options: Export options.
        """
        self.options = options or AdaptiveCardOptions()
        self.validator = AdaptiveCardValidator()

    def export(self, lui_schema: dict[str, Any]) -> str:
        """Export a LUI schema to Adaptive Card JSON.

        Args:
            lui_schema: The LUI schema to export.

        Returns:
            JSON string of the Adaptive Card.
        """
        card = self._convert_to_card(lui_schema)

        if self.options.validate:
            result = self.validator.validate(card, self.options.target_platform)
            if not result.is_valid:
                error_messages = [e.message for e in result.errors]
                raise ValueError(f"Invalid Adaptive Card: {'; '.join(error_messages)}")

        if self.options.minify:
            return json.dumps(card, separators=(",", ":"))
        return json.dumps(card, indent=2)

    def _convert_to_card(self, lui_schema: dict[str, Any]) -> dict[str, Any]:
        """Convert a LUI schema to an Adaptive Card structure."""
        card: dict[str, Any] = {
            "type": "AdaptiveCard",
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "version": self.options.schema_version,
            "body": [],
        }

        if self.options.lang:
            card["lang"] = self.options.lang

        # Convert visual elements
        visuals = lui_schema.get("visuals", [])
        for visual in visuals:
            element = self._convert_visual_element(visual)
            if element:
                card["body"].append(element)

        # Convert actions
        actions = lui_schema.get("actions", [])
        if actions:
            card["actions"] = [self._convert_action(a) for a in actions]

        # Add fallback text
        if self.options.include_fallback_text:
            fallback = lui_schema.get("fallback_text") or lui_schema.get("text", "")
            if fallback:
                card["fallbackText"] = fallback

        return card

    def _convert_visual_element(self, visual: dict[str, Any]) -> dict[str, Any] | None:
        """Convert a LUI visual element to an Adaptive Card element."""
        visual_type = visual.get("type", "").lower()

        if visual_type == "text":
            return {
                "type": "TextBlock",
                "text": visual.get("content", ""),
                "wrap": True,
            }

        elif visual_type == "image":
            return {
                "type": "Image",
                "url": visual.get("url", ""),
                "altText": visual.get("alt_text", ""),
            }

        elif visual_type == "list":
            items = visual.get("items", [])
            return {
                "type": "Container",
                "items": [
                    {"type": "TextBlock", "text": f"• {item}", "wrap": True}
                    for item in items
                ],
            }

        elif visual_type == "table":
            return self._convert_table(visual)

        elif visual_type == "card":
            return self._convert_nested_card(visual)

        return None

    def _convert_table(self, visual: dict[str, Any]) -> dict[str, Any]:
        """Convert a table visual to Adaptive Card table."""
        headers = visual.get("headers", [])
        rows = visual.get("rows", [])

        table: dict[str, Any] = {
            "type": "Table",
            "columns": [{"width": 1} for _ in headers],
            "rows": [],
        }

        # Add header row
        if headers:
            header_row = {
                "type": "TableRow",
                "cells": [
                    {
                        "type": "TableCell",
                        "items": [{"type": "TextBlock", "text": h, "weight": "bolder"}],
                    }
                    for h in headers
                ],
            }
            table["rows"].append(header_row)

        # Add data rows
        for row in rows:
            data_row = {
                "type": "TableRow",
                "cells": [
                    {"type": "TableCell", "items": [{"type": "TextBlock", "text": str(cell)}]}
                    for cell in row
                ],
            }
            table["rows"].append(data_row)

        return table

    def _convert_nested_card(self, visual: dict[str, Any]) -> dict[str, Any]:
        """Convert a nested card visual."""
        return {
            "type": "Container",
            "style": "emphasis",
            "items": [
                {
                    "type": "TextBlock",
                    "text": visual.get("title", ""),
                    "weight": "bolder",
                    "size": "medium",
                },
                {"type": "TextBlock", "text": visual.get("content", ""), "wrap": True},
            ],
        }

    def _convert_action(self, action: dict[str, Any]) -> dict[str, Any]:
        """Convert a LUI action to an Adaptive Card action."""
        action_type = action.get("type", "").lower()

        if action_type == "url" or action_type == "link":
            return {
                "type": "Action.OpenUrl",
                "title": action.get("label", "Open"),
                "url": action.get("url", ""),
            }

        elif action_type == "submit":
            return {
                "type": "Action.Submit",
                "title": action.get("label", "Submit"),
                "data": action.get("data", {}),
            }

        elif action_type == "execute":
            return {
                "type": "Action.Execute",
                "title": action.get("label", "Execute"),
                "verb": action.get("verb", ""),
                "data": action.get("data", {}),
            }

        # Default to submit
        return {
            "type": "Action.Submit",
            "title": action.get("label", action.get("title", "Action")),
            "data": action.get("data", {}),
        }


def export_to_adaptive_card(
    lui_schema: dict[str, Any],
    options: AdaptiveCardOptions | None = None,
) -> str:
    """Export a LUI schema to Adaptive Card JSON.

    Args:
        lui_schema: The LUI schema to export.
        options: Export options.

    Returns:
        JSON string of the Adaptive Card.
    """
    exporter = AdaptiveCardExporter(options)
    return exporter.export(lui_schema)


def create_adaptive_card() -> AdaptiveCardBuilder:
    """Create a new Adaptive Card builder.

    Returns:
        A new AdaptiveCardBuilder instance.
    """
    return AdaptiveCardBuilder()


def validate_adaptive_card(
    card: dict[str, Any] | str,
    target_platform: AdaptiveCardPlatform | None = None,
) -> ValidationResult:
    """Validate an Adaptive Card.

    Args:
        card: The card to validate (dict or JSON string).
        target_platform: Target platform for compatibility checks.

    Returns:
        ValidationResult with errors, warnings, and compatibility info.
    """
    card_dict: dict[str, Any]
    if isinstance(card, str):
        try:
            card_dict = json.loads(card)
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(
                        code="INVALID_JSON",
                        message=f"Invalid JSON: {e}",
                    )
                ],
            )
    else:
        card_dict = card

    validator = AdaptiveCardValidator()
    return validator.validate(card_dict, target_platform)
