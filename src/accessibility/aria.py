"""ARIA live region generation for screen reader compatibility.

This module generates ARIA live region markup for LUI conversational output,
ensuring compatibility with major screen readers (JAWS, NVDA, VoiceOver, TalkBack).

Issue #75 - Task 4.9: ARIA Live Region Generator
Part of #27 - Phase 4: LUI Accessibility Standards
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ============================================
# Enums
# ============================================


class ARIAPoliteness(Enum):
    """ARIA live region politeness levels.

    Determines how and when screen readers announce content changes.
    """

    OFF = "off"  # No announcements - content changes silently
    POLITE = "polite"  # Wait for user idle before announcing (default)
    ASSERTIVE = "assertive"  # Interrupt immediately - use sparingly


class ARIARole(Enum):
    """ARIA landmark and widget roles for live regions.

    Different roles provide different semantic meaning to screen readers.
    """

    LOG = "log"  # Sequential information log (chat history)
    STATUS = "status"  # Status information (non-critical)
    ALERT = "alert"  # Important messages requiring attention
    ALERTDIALOG = "alertdialog"  # Alert that requires response
    PROGRESSBAR = "progressbar"  # Progress indication
    TIMER = "timer"  # Time-related updates
    MARQUEE = "marquee"  # Scrolling text (non-essential)
    REGION = "region"  # Generic live region


class ARIARelevant(Enum):
    """Values for aria-relevant attribute.

    Specifies what types of changes should be announced.
    """

    ADDITIONS = "additions"  # Only new nodes
    REMOVALS = "removals"  # Only removed nodes
    TEXT = "text"  # Only text changes
    ALL = "all"  # All changes
    ADDITIONS_TEXT = "additions text"  # New nodes and text changes (default)
    ADDITIONS_REMOVALS = "additions removals"  # Node additions and removals


class ScreenReader(Enum):
    """Major screen reader platforms for optimization."""

    JAWS = "jaws"  # Windows + Chrome/Firefox
    NVDA = "nvda"  # Windows + Firefox
    VOICEOVER = "voiceover"  # macOS/iOS + Safari
    TALKBACK = "talkback"  # Android
    NARRATOR = "narrator"  # Windows built-in
    ORCA = "orca"  # Linux


class ContentType(Enum):
    """Types of content for automatic configuration."""

    MESSAGE = "message"  # Standard message/response
    ERROR = "error"  # Error message
    WARNING = "warning"  # Warning message
    SUCCESS = "success"  # Success confirmation
    INFO = "info"  # Informational message
    PROGRESS = "progress"  # Progress update
    CHAT = "chat"  # Chat/conversation message
    NOTIFICATION = "notification"  # Notification


# ============================================
# Configuration Data Classes
# ============================================


@dataclass
class ARIAConfig:
    """Configuration for ARIA live region.

    Attributes:
        role: ARIA role for the region
        aria_live: Politeness level (off/polite/assertive)
        aria_atomic: Whether to announce entire region on changes
        aria_relevant: What types of changes to announce
        aria_busy: Whether content is currently being updated
        aria_label: Accessible label for the region
        aria_labelledby: ID of element providing label
        aria_describedby: ID of element providing description
    """

    role: ARIARole = ARIARole.LOG
    aria_live: ARIAPoliteness = ARIAPoliteness.POLITE
    aria_atomic: bool = False
    aria_relevant: ARIARelevant = ARIARelevant.ADDITIONS_TEXT
    aria_busy: bool = False
    aria_label: Optional[str] = None
    aria_labelledby: Optional[str] = None
    aria_describedby: Optional[str] = None


@dataclass
class ScreenReaderHint:
    """Hints for specific screen reader optimization.

    Attributes:
        reader: Target screen reader
        recommendation: Specific configuration recommendation
        notes: Additional notes for developers
    """

    reader: ScreenReader
    recommendation: str
    notes: str = ""


# Screen reader compatibility notes
SCREEN_READER_HINTS: dict[ScreenReader, ScreenReaderHint] = {
    ScreenReader.JAWS: ScreenReaderHint(
        reader=ScreenReader.JAWS,
        recommendation="Use aria-live='polite' for best experience",
        notes="JAWS works best with role='log' for chat interfaces",
    ),
    ScreenReader.NVDA: ScreenReaderHint(
        reader=ScreenReader.NVDA,
        recommendation="role='log' works best with NVDA",
        notes="NVDA respects aria-relevant for fine-grained control",
    ),
    ScreenReader.VOICEOVER: ScreenReaderHint(
        reader=ScreenReader.VOICEOVER,
        recommendation="Use aria-atomic='false' for message-by-message reading",
        notes="VoiceOver on iOS may need aria-live='assertive' for immediate feedback",
    ),
    ScreenReader.TALKBACK: ScreenReaderHint(
        reader=ScreenReader.TALKBACK,
        recommendation="Test with role='status' for notifications",
        notes="TalkBack works well with aria-live on Android 8+",
    ),
    ScreenReader.NARRATOR: ScreenReaderHint(
        reader=ScreenReader.NARRATOR,
        recommendation="Use role='alert' for critical messages",
        notes="Narrator supports all ARIA live region attributes",
    ),
    ScreenReader.ORCA: ScreenReaderHint(
        reader=ScreenReader.ORCA,
        recommendation="Standard ARIA live regions work well",
        notes="Orca follows ARIA spec closely",
    ),
}

# Default configurations by content type
CONTENT_TYPE_CONFIGS: dict[ContentType, ARIAConfig] = {
    ContentType.MESSAGE: ARIAConfig(
        role=ARIARole.LOG,
        aria_live=ARIAPoliteness.POLITE,
        aria_atomic=False,
        aria_relevant=ARIARelevant.ADDITIONS_TEXT,
    ),
    ContentType.ERROR: ARIAConfig(
        role=ARIARole.ALERT,
        aria_live=ARIAPoliteness.ASSERTIVE,
        aria_atomic=True,
        aria_relevant=ARIARelevant.ALL,
    ),
    ContentType.WARNING: ARIAConfig(
        role=ARIARole.ALERT,
        aria_live=ARIAPoliteness.ASSERTIVE,
        aria_atomic=True,
        aria_relevant=ARIARelevant.ADDITIONS_TEXT,
    ),
    ContentType.SUCCESS: ARIAConfig(
        role=ARIARole.STATUS,
        aria_live=ARIAPoliteness.POLITE,
        aria_atomic=True,
        aria_relevant=ARIARelevant.ADDITIONS_TEXT,
    ),
    ContentType.INFO: ARIAConfig(
        role=ARIARole.STATUS,
        aria_live=ARIAPoliteness.POLITE,
        aria_atomic=False,
        aria_relevant=ARIARelevant.ADDITIONS_TEXT,
    ),
    ContentType.PROGRESS: ARIAConfig(
        role=ARIARole.PROGRESSBAR,
        aria_live=ARIAPoliteness.POLITE,
        aria_atomic=False,
        aria_relevant=ARIARelevant.TEXT,
    ),
    ContentType.CHAT: ARIAConfig(
        role=ARIARole.LOG,
        aria_live=ARIAPoliteness.POLITE,
        aria_atomic=False,
        aria_relevant=ARIARelevant.ADDITIONS,
    ),
    ContentType.NOTIFICATION: ARIAConfig(
        role=ARIARole.STATUS,
        aria_live=ARIAPoliteness.POLITE,
        aria_atomic=True,
        aria_relevant=ARIARelevant.ADDITIONS_TEXT,
    ),
}


@dataclass
class LiveRegionResult:
    """Result of live region generation.

    Attributes:
        html: Generated HTML markup
        config: Configuration used
        screen_reader_hints: Hints for major screen readers
        is_valid: Whether generated HTML is valid
        warnings: Any warnings about the generation
    """

    html: str
    config: ARIAConfig
    screen_reader_hints: list[ScreenReaderHint] = field(default_factory=list)
    is_valid: bool = True
    warnings: list[str] = field(default_factory=list)


# ============================================
# ARIA Live Region Generator
# ============================================


class ARIALiveRegionGenerator:
    """Generates ARIA live region markup for LUI responses.

    This generator creates accessible HTML markup with proper ARIA attributes
    for screen reader compatibility across major platforms.

    Example:
        >>> generator = ARIALiveRegionGenerator()
        >>> html = generator.generate_live_region("Task completed", ARIAPoliteness.POLITE)
        >>> print(html)
        <div role="log" aria-live="polite">Task completed</div>

        >>> html = generator.generate_live_region("Error!", ARIAPoliteness.ASSERTIVE)
        >>> print(html)
        <div role="alert" aria-live="assertive">Error!</div>
    """

    def __init__(
        self,
        default_politeness: ARIAPoliteness = ARIAPoliteness.POLITE,
        escape_content: bool = True,
        include_timestamps: bool = False,
        message_class: str = "lui-message",
    ):
        """Initialize the generator.

        Args:
            default_politeness: Default politeness level for regions
            escape_content: Whether to HTML-escape content
            include_timestamps: Whether to include timestamps in messages
            message_class: CSS class for message containers
        """
        self.default_politeness = default_politeness
        self.escape_content = escape_content
        self.include_timestamps = include_timestamps
        self.message_class = message_class

    # ============================================
    # Main Generation Methods
    # ============================================

    def generate_live_region(
        self,
        response: str,
        politeness: Optional[ARIAPoliteness] = None,
        role: Optional[ARIARole] = None,
        config: Optional[ARIAConfig] = None,
        **kwargs: Any,
    ) -> str:
        """Generate ARIA live region markup for a response.

        Args:
            response: The response content to wrap
            politeness: Politeness level (defaults to instance default)
            role: ARIA role for the region
            config: Full configuration (overrides politeness/role)
            **kwargs: Additional attributes to add

        Returns:
            HTML string with ARIA live region markup
        """
        # Determine configuration
        if config is None:
            config = ARIAConfig(
                role=role or ARIARole.LOG,
                aria_live=politeness or self.default_politeness,
            )

        # Escape content if needed
        content = html.escape(response) if self.escape_content else response

        # Build attributes
        attrs = self._build_attributes(config, **kwargs)

        return f"<div {attrs}>{content}</div>"

    def generate_live_region_full(
        self,
        response: str,
        politeness: Optional[ARIAPoliteness] = None,
        content_type: Optional[ContentType] = None,
        config: Optional[ARIAConfig] = None,
        include_hints: bool = True,
        **kwargs: Any,
    ) -> LiveRegionResult:
        """Generate ARIA live region with full result details.

        Args:
            response: The response content to wrap
            politeness: Politeness level
            content_type: Type of content for automatic configuration
            config: Full configuration (overrides content_type)
            include_hints: Whether to include screen reader hints
            **kwargs: Additional attributes

        Returns:
            LiveRegionResult with HTML and metadata
        """
        warnings: list[str] = []

        # Determine configuration
        if config is not None:
            used_config = config
        elif content_type is not None:
            used_config = CONTENT_TYPE_CONFIGS.get(
                content_type,
                ARIAConfig(),
            )
            # Override politeness if specified
            if politeness is not None:
                used_config = ARIAConfig(
                    role=used_config.role,
                    aria_live=politeness,
                    aria_atomic=used_config.aria_atomic,
                    aria_relevant=used_config.aria_relevant,
                    aria_busy=used_config.aria_busy,
                    aria_label=used_config.aria_label,
                )
        else:
            used_config = ARIAConfig(
                aria_live=politeness or self.default_politeness,
            )

        # Generate HTML
        html_output = self.generate_live_region(
            response,
            config=used_config,
            **kwargs,
        )

        # Validate
        is_valid = self._validate_html(html_output)
        if not is_valid:
            warnings.append("Generated HTML may have validation issues")

        # Check for potential issues
        if used_config.aria_live == ARIAPoliteness.ASSERTIVE:
            warnings.append(
                "Assertive politeness should be used sparingly for critical messages"
            )

        # Get screen reader hints
        hints = list(SCREEN_READER_HINTS.values()) if include_hints else []

        return LiveRegionResult(
            html=html_output,
            config=used_config,
            screen_reader_hints=hints,
            is_valid=is_valid,
            warnings=warnings,
        )

    def generate_message(
        self,
        content: str,
        sender: str = "assistant",
        aria_label: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate a single message within a live region.

        Args:
            content: Message content
            sender: Who sent the message (assistant/user)
            aria_label: Custom label for screen readers
            **kwargs: Additional attributes

        Returns:
            HTML for a single message element
        """
        escaped_content = html.escape(content) if self.escape_content else content
        label = aria_label or f"{sender.title()} message"

        # Build message-specific attributes
        extra_attrs = []
        for key, value in kwargs.items():
            attr_name = key.replace("_", "-")
            extra_attrs.append(f'{attr_name}="{html.escape(str(value))}"')

        attrs_str = " ".join(extra_attrs)
        if attrs_str:
            attrs_str = " " + attrs_str

        return (
            f'<div class="{self.message_class}" '
            f'aria-label="{html.escape(label)}" '
            f'data-sender="{html.escape(sender)}"{attrs_str}>'
            f"{escaped_content}"
            f"</div>"
        )

    def generate_conversation_container(
        self,
        messages: list[dict[str, str]],
        config: Optional[ARIAConfig] = None,
        container_id: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate a complete conversation container with live region.

        Args:
            messages: List of message dicts with 'content' and optional 'sender'
            config: Configuration for the container
            container_id: ID for the container element
            **kwargs: Additional container attributes

        Returns:
            HTML for complete conversation with ARIA live region
        """
        if config is None:
            config = CONTENT_TYPE_CONFIGS[ContentType.CHAT]

        # Generate message elements
        message_html = []
        for msg in messages:
            content = msg.get("content", "")
            sender = msg.get("sender", "assistant")
            message_html.append(self.generate_message(content, sender))

        messages_content = "\n  ".join(message_html)

        # Build container attributes
        attrs = self._build_attributes(config, **kwargs)
        if container_id:
            attrs = f'id="{html.escape(container_id)}" {attrs}'

        return f"<div {attrs}>\n  {messages_content}\n</div>"

    # ============================================
    # Specialized Region Generators
    # ============================================

    def generate_error_region(
        self,
        error_message: str,
        error_code: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate an error announcement region.

        Args:
            error_message: The error message
            error_code: Optional error code
            **kwargs: Additional attributes

        Returns:
            HTML for error live region
        """
        config = CONTENT_TYPE_CONFIGS[ContentType.ERROR]

        content = error_message
        if error_code:
            content = f"Error {error_code}: {error_message}"

        return self.generate_live_region(content, config=config, **kwargs)

    def generate_status_region(
        self,
        status_message: str,
        **kwargs: Any,
    ) -> str:
        """Generate a status announcement region.

        Args:
            status_message: The status message
            **kwargs: Additional attributes

        Returns:
            HTML for status live region
        """
        config = CONTENT_TYPE_CONFIGS[ContentType.INFO]
        return self.generate_live_region(status_message, config=config, **kwargs)

    def generate_progress_region(
        self,
        progress_message: str,
        value_now: Optional[int] = None,
        value_min: int = 0,
        value_max: int = 100,
        **kwargs: Any,
    ) -> str:
        """Generate a progress announcement region.

        Args:
            progress_message: Progress description
            value_now: Current progress value
            value_min: Minimum value
            value_max: Maximum value
            **kwargs: Additional attributes

        Returns:
            HTML for progress live region
        """
        escaped_message = (
            html.escape(progress_message) if self.escape_content else progress_message
        )

        # Build progress attributes
        attrs_list = [
            'role="progressbar"',
            f'aria-live="{ARIAPoliteness.POLITE.value}"',
            f'aria-valuemin="{value_min}"',
            f'aria-valuemax="{value_max}"',
        ]

        if value_now is not None:
            attrs_list.append(f'aria-valuenow="{value_now}"')
            percent = int((value_now - value_min) / (value_max - value_min) * 100)
            attrs_list.append(f'aria-valuetext="{percent}% complete"')

        for key, value in kwargs.items():
            attr_name = key.replace("_", "-")
            attrs_list.append(f'{attr_name}="{html.escape(str(value))}"')

        attrs_str = " ".join(attrs_list)

        return f"<div {attrs_str}>{escaped_message}</div>"

    def generate_notification_region(
        self,
        notification: str,
        notification_type: str = "info",
        **kwargs: Any,
    ) -> str:
        """Generate a notification region.

        Args:
            notification: Notification message
            notification_type: Type of notification (info/success/warning/error)
            **kwargs: Additional attributes

        Returns:
            HTML for notification region
        """
        # Map notification type to content type
        type_mapping = {
            "info": ContentType.INFO,
            "success": ContentType.SUCCESS,
            "warning": ContentType.WARNING,
            "error": ContentType.ERROR,
        }

        content_type = type_mapping.get(notification_type, ContentType.NOTIFICATION)
        config = CONTENT_TYPE_CONFIGS[content_type]

        kwargs["data_notification_type"] = notification_type
        return self.generate_live_region(notification, config=config, **kwargs)

    # ============================================
    # Helper Methods
    # ============================================

    def _build_attributes(self, config: ARIAConfig, **kwargs: Any) -> str:
        """Build HTML attribute string from config.

        Args:
            config: ARIA configuration
            **kwargs: Additional attributes

        Returns:
            Space-separated attribute string
        """
        attrs = [
            f'role="{config.role.value}"',
            f'aria-live="{config.aria_live.value}"',
        ]

        # Only include aria-atomic if true (false is default)
        if config.aria_atomic:
            attrs.append('aria-atomic="true"')
        else:
            attrs.append('aria-atomic="false"')

        # Always include aria-relevant
        attrs.append(f'aria-relevant="{config.aria_relevant.value}"')

        # Include aria-busy if true
        if config.aria_busy:
            attrs.append('aria-busy="true"')

        # Include optional labels
        if config.aria_label:
            attrs.append(f'aria-label="{html.escape(config.aria_label)}"')
        if config.aria_labelledby:
            attrs.append(f'aria-labelledby="{html.escape(config.aria_labelledby)}"')
        if config.aria_describedby:
            attrs.append(f'aria-describedby="{html.escape(config.aria_describedby)}"')

        # Add additional kwargs as attributes
        for key, value in kwargs.items():
            # Convert snake_case to kebab-case for HTML attributes
            attr_name = key.replace("_", "-")
            attrs.append(f'{attr_name}="{html.escape(str(value))}"')

        return " ".join(attrs)

    def _validate_html(self, html_str: str) -> bool:
        """Basic HTML validation.

        Args:
            html_str: HTML string to validate

        Returns:
            True if HTML appears valid
        """
        # Check for basic tag matching
        if not html_str.startswith("<") or not html_str.endswith(">"):
            return False

        # Check for required ARIA attributes
        required_attrs = ["role=", "aria-live="]
        for attr in required_attrs:
            if attr not in html_str:
                return False

        return True

    def get_screen_reader_recommendations(
        self,
        content_type: ContentType = ContentType.MESSAGE,
    ) -> dict[ScreenReader, str]:
        """Get screen reader recommendations for a content type.

        Args:
            content_type: Type of content

        Returns:
            Dict mapping screen reader to recommendation
        """
        return {
            reader: hint.recommendation for reader, hint in SCREEN_READER_HINTS.items()
        }

    def get_config_for_content_type(self, content_type: ContentType) -> ARIAConfig:
        """Get recommended configuration for a content type.

        Args:
            content_type: Type of content

        Returns:
            Recommended ARIAConfig for the content type
        """
        return CONTENT_TYPE_CONFIGS.get(content_type, ARIAConfig())


# ============================================
# Convenience Functions
# ============================================


def generate_live_region(
    content: str,
    politeness: ARIAPoliteness = ARIAPoliteness.POLITE,
) -> str:
    """Quick function to generate a live region.

    Args:
        content: Content to wrap
        politeness: Politeness level

    Returns:
        HTML string with ARIA live region
    """
    generator = ARIALiveRegionGenerator()
    return generator.generate_live_region(content, politeness=politeness)


def generate_error_alert(error_message: str) -> str:
    """Quick function to generate an error alert.

    Args:
        error_message: Error message

    Returns:
        HTML string with assertive alert
    """
    generator = ARIALiveRegionGenerator()
    return generator.generate_error_region(error_message)


def generate_status_update(status_message: str) -> str:
    """Quick function to generate a status update.

    Args:
        status_message: Status message

    Returns:
        HTML string with polite status region
    """
    generator = ARIALiveRegionGenerator()
    return generator.generate_status_region(status_message)
