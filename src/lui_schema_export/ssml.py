"""SSML (Speech Synthesis Markup Language) utilities for voice output.

This module provides utilities for generating, parsing, and validating SSML
following W3C SSML 1.1 standards with compatibility for major TTS providers.
"""

import html
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from xml.etree import ElementTree as ET

from baml_client.types import (
    VoiceResponse,
    VoiceConfig,
    VoiceSpeakingStyle,
    VoiceSegment,
    EmphasisLevel,
    SSMLDocument,
    SSMLElement,
    SSMLElementType,
    SSMLAttributes,
    SSMLBreakStrength,
    SSMLEmphasisLevel,
    SSMLProsodyRate,
    SSMLProsodyPitch,
    SSMLProsodyVolume,
    SSMLProvider,
    SSMLValidationResult,
    SSMLValidationError,
    SSMLValidationWarning,
    SSMLProviderCompatibility,
)


# ============================================
# Constants
# ============================================

SSML_VERSION = "1.1"
SSML_XMLNS = "http://www.w3.org/2001/10/synthesis"

# Provider-specific unsupported elements
PROVIDER_UNSUPPORTED: dict[SSMLProvider, set[str]] = {
    SSMLProvider.GENERIC: set(),
    SSMLProvider.GOOGLE: {"voice", "mark"},
    SSMLProvider.AMAZON_POLLY: {"voice", "lang"},
    SSMLProvider.AZURE: set(),
    SSMLProvider.ELEVENLABS: {
        "phoneme",
        "sub",
        "audio",
        "voice",
        "lang",
        "mark",
        "desc",
    },
    SSMLProvider.OPENAI: {
        "phoneme",
        "sub",
        "audio",
        "voice",
        "lang",
        "mark",
        "desc",
        "prosody",
        "emphasis",
    },
}

# Break strength to duration mappings
BREAK_DURATIONS: dict[SSMLBreakStrength, str] = {
    SSMLBreakStrength.NONE: "0ms",
    SSMLBreakStrength.X_WEAK: "100ms",
    SSMLBreakStrength.WEAK: "250ms",
    SSMLBreakStrength.MEDIUM: "500ms",
    SSMLBreakStrength.STRONG: "750ms",
    SSMLBreakStrength.X_STRONG: "1s",
}


# ============================================
# Options Dataclass
# ============================================


@dataclass
class SSMLOptions:
    """Options for SSML generation."""

    auto_sentence_breaks: bool = True
    auto_paragraph_breaks: bool = True
    default_rate: SSMLProsodyRate | None = None
    default_pitch: SSMLProsodyPitch | None = None
    default_volume: SSMLProsodyVolume | None = None
    preserve_whitespace: bool = False
    escape_special_chars: bool = True
    target_provider: SSMLProvider = SSMLProvider.GENERIC
    include_xml_declaration: bool = False


# ============================================
# SSML Generator
# ============================================


@dataclass
class SSMLGenerator:
    """Generator for creating SSML from various inputs."""

    options: SSMLOptions = field(default_factory=SSMLOptions)

    def generate_ssml(self, voice_response: VoiceResponse) -> str:
        """Generate SSML from a VoiceResponse type.

        Args:
            voice_response: The voice response to convert to SSML.

        Returns:
            A valid SSML string.
        """
        # Build the SSML structure
        root_attrs = {
            "version": SSML_VERSION,
            "xmlns": SSML_XMLNS,
            "xml:lang": voice_response.language,
        }

        lines = [f'<speak version="{SSML_VERSION}" xmlns="{SSML_XMLNS}" xml:lang="{voice_response.language}">']

        # Apply prosody if voice config is present
        prosody_attrs = self._build_prosody_attrs(voice_response.voice_config)

        if prosody_attrs:
            lines.append(f"  <prosody {prosody_attrs}>")
            indent = "    "
        else:
            indent = "  "

        # Handle segments or plain text
        if voice_response.segments:
            for segment in voice_response.segments:
                lines.extend(self._render_segment(segment, indent))
        else:
            # Escape and add text
            text = self._escape_text(voice_response.text)
            if self.options.auto_sentence_breaks:
                text = self._add_sentence_breaks(text)
            lines.append(f"{indent}{text}")

        if prosody_attrs:
            lines.append("  </prosody>")

        lines.append("</speak>")

        return "\n".join(lines)

    def text_to_ssml(self, text: str, options: SSMLOptions | None = None) -> str:
        """Convert plain text to SSML with smart defaults.

        Args:
            text: Plain text to convert.
            options: Optional generation options.

        Returns:
            A valid SSML string.
        """
        opts = options or self.options
        language = "en-US"  # Default language

        lines = [f'<speak version="{SSML_VERSION}" xmlns="{SSML_XMLNS}" xml:lang="{language}">']

        # Apply default prosody if set
        prosody_attrs = self._build_default_prosody_attrs(opts)
        if prosody_attrs:
            lines.append(f"  <prosody {prosody_attrs}>")
            indent = "    "
        else:
            indent = "  "

        # Process text
        escaped_text = self._escape_text(text) if opts.escape_special_chars else text

        if opts.auto_paragraph_breaks:
            paragraphs = escaped_text.split("\n\n")
            for i, para in enumerate(paragraphs):
                if para.strip():
                    lines.append(f"{indent}<p>")
                    if opts.auto_sentence_breaks:
                        sentences = self._split_sentences(para)
                        for sent in sentences:
                            if sent.strip():
                                lines.append(f"{indent}  <s>{sent.strip()}</s>")
                    else:
                        lines.append(f"{indent}  {para.strip()}")
                    lines.append(f"{indent}</p>")
                    if i < len(paragraphs) - 1:
                        lines.append(f'{indent}<break strength="strong"/>')
        elif opts.auto_sentence_breaks:
            sentences = self._split_sentences(escaped_text)
            for sent in sentences:
                if sent.strip():
                    lines.append(f"{indent}<s>{sent.strip()}</s>")
        else:
            lines.append(f"{indent}{escaped_text}")

        if prosody_attrs:
            lines.append("  </prosody>")

        lines.append("</speak>")

        return "\n".join(lines)

    def _build_prosody_attrs(self, config: VoiceConfig | None) -> str:
        """Build prosody attribute string from voice config."""
        if not config:
            return ""

        attrs = []

        if config.speaking_rate is not None:
            # Convert float rate to percentage
            rate_pct = int(config.speaking_rate * 100)
            attrs.append(f'rate="{rate_pct}%"')

        if config.pitch is not None:
            # Convert pitch adjustment to semitones
            if config.pitch > 0:
                attrs.append(f'pitch="+{config.pitch}st"')
            elif config.pitch < 0:
                attrs.append(f'pitch="{config.pitch}st"')

        if config.volume is not None:
            # Convert 0-1 volume to dB or named value
            if config.volume >= 0.9:
                attrs.append('volume="x-loud"')
            elif config.volume >= 0.7:
                attrs.append('volume="loud"')
            elif config.volume >= 0.4:
                attrs.append('volume="medium"')
            elif config.volume >= 0.2:
                attrs.append('volume="soft"')
            elif config.volume > 0:
                attrs.append('volume="x-soft"')
            else:
                attrs.append('volume="silent"')

        return " ".join(attrs)

    def _build_default_prosody_attrs(self, opts: SSMLOptions) -> str:
        """Build prosody attributes from default options."""
        attrs = []

        if opts.default_rate:
            rate_value = opts.default_rate.value.lower().replace("_", "-")
            attrs.append(f'rate="{rate_value}"')

        if opts.default_pitch:
            pitch_value = opts.default_pitch.value.lower().replace("_", "-")
            attrs.append(f'pitch="{pitch_value}"')

        if opts.default_volume:
            volume_value = opts.default_volume.value.lower().replace("_", "-")
            attrs.append(f'volume="{volume_value}"')

        return " ".join(attrs)

    def _render_segment(self, segment: VoiceSegment, indent: str) -> list[str]:
        """Render a voice segment to SSML lines."""
        lines = []

        # Add pause before if specified
        if segment.pause_before_ms:
            lines.append(f'{indent}<break time="{segment.pause_before_ms}ms"/>')

        # Build emphasis wrapper if needed
        if segment.emphasis and segment.emphasis != EmphasisLevel.NONE:
            level = segment.emphasis.value.lower()
            text = self._escape_text(segment.text)
            ssml_content = segment.ssml if segment.ssml else text
            lines.append(f'{indent}<emphasis level="{level}">{ssml_content}</emphasis>')
        elif segment.ssml:
            lines.append(f"{indent}{segment.ssml}")
        else:
            lines.append(f"{indent}{self._escape_text(segment.text)}")

        # Add pause after if specified
        if segment.pause_after_ms:
            lines.append(f'{indent}<break time="{segment.pause_after_ms}ms"/>')

        return lines

    def _escape_text(self, text: str) -> str:
        """Escape XML special characters in text."""
        return html.escape(text, quote=False)

    def _add_sentence_breaks(self, text: str) -> str:
        """Add SSML sentence breaks after periods, question marks, etc."""
        # Add breaks after sentence endings
        text = re.sub(r"([.!?])\s+", r'\1<break time="250ms"/> ', text)
        return text

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s for s in sentences if s.strip()]


# ============================================
# SSML Validator
# ============================================


@dataclass
class SSMLValidator:
    """Validator for SSML content."""

    def validate_ssml(
        self,
        ssml: str,
        target_providers: list[SSMLProvider] | None = None,
    ) -> SSMLValidationResult:
        """Validate SSML against W3C spec.

        Args:
            ssml: The SSML string to validate.
            target_providers: Optional list of providers to check compatibility.

        Returns:
            Validation result with errors, warnings, and provider compatibility.
        """
        errors: list[SSMLValidationError] = []
        warnings: list[SSMLValidationWarning] = []
        provider_compat: list[SSMLProviderCompatibility] = []

        # Check XML well-formedness
        try:
            root = ET.fromstring(ssml)
        except ET.ParseError as e:
            errors.append(
                SSMLValidationError(
                    code="XML_PARSE_ERROR",
                    message=f"XML parsing error: {str(e)}",
                    line=getattr(e, "position", (None, None))[0],
                    column=getattr(e, "position", (None, None))[1],
                    element=None,
                )
            )
            return SSMLValidationResult(
                is_valid=False,
                errors=errors,
                warnings=warnings,
                provider_compatibility=provider_compat,
            )

        # Check root element
        if not root.tag.endswith("speak"):
            errors.append(
                SSMLValidationError(
                    code="INVALID_ROOT",
                    message=f"Root element must be 'speak', found '{root.tag}'",
                    line=None,
                    column=None,
                    element=root.tag,
                )
            )

        # Check for required attributes
        version = root.get("version")
        if not version:
            warnings.append(
                SSMLValidationWarning(
                    code="MISSING_VERSION",
                    message="Missing 'version' attribute on speak element",
                    suggestion="Add version=\"1.1\" to speak element",
                    element="speak",
                )
            )

        # Check for deprecated or invalid elements
        valid_elements = {
            "speak",
            "break",
            "emphasis",
            "prosody",
            "say-as",
            "phoneme",
            "sub",
            "audio",
            "p",
            "s",
            "voice",
            "lang",
            "mark",
            "desc",
        }

        for elem in root.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag not in valid_elements:
                warnings.append(
                    SSMLValidationWarning(
                        code="UNKNOWN_ELEMENT",
                        message=f"Unknown SSML element: {tag}",
                        suggestion="Check W3C SSML 1.1 specification for valid elements",
                        element=tag,
                    )
                )

        # Validate prosody attributes
        for prosody in root.iter():
            tag = prosody.tag.split("}")[-1] if "}" in prosody.tag else prosody.tag
            if tag == "prosody":
                self._validate_prosody(prosody, errors, warnings)

        # Check provider compatibility
        if target_providers:
            for provider in target_providers:
                compat = self._check_provider_compatibility(root, provider)
                provider_compat.append(compat)

        is_valid = len(errors) == 0

        return SSMLValidationResult(
            is_valid=is_valid,
            errors=errors if errors else None,
            warnings=warnings if warnings else None,
            provider_compatibility=provider_compat if provider_compat else None,
        )

    def _validate_prosody(
        self,
        elem: ET.Element,
        errors: list[SSMLValidationError],
        warnings: list[SSMLValidationWarning],
    ) -> None:
        """Validate prosody element attributes."""
        rate = elem.get("rate")
        if rate:
            valid_rates = {"x-slow", "slow", "medium", "fast", "x-fast"}
            # Check if it's a valid named rate or percentage
            if rate not in valid_rates and not re.match(r"^[+-]?\d+%$", rate):
                warnings.append(
                    SSMLValidationWarning(
                        code="INVALID_RATE",
                        message=f"Invalid prosody rate value: {rate}",
                        suggestion="Use x-slow, slow, medium, fast, x-fast, or a percentage",
                        element="prosody",
                    )
                )

        pitch = elem.get("pitch")
        if pitch:
            valid_pitches = {"x-low", "low", "medium", "high", "x-high"}
            if pitch not in valid_pitches and not re.match(r"^[+-]?\d+(%|Hz|st)$", pitch):
                warnings.append(
                    SSMLValidationWarning(
                        code="INVALID_PITCH",
                        message=f"Invalid prosody pitch value: {pitch}",
                        suggestion="Use x-low, low, medium, high, x-high, or a value in Hz/st/%",
                        element="prosody",
                    )
                )

        volume = elem.get("volume")
        if volume:
            valid_volumes = {"silent", "x-soft", "soft", "medium", "loud", "x-loud"}
            if volume not in valid_volumes and not re.match(r"^[+-]?\d+(\.\d+)?(dB|%)$", volume):
                warnings.append(
                    SSMLValidationWarning(
                        code="INVALID_VOLUME",
                        message=f"Invalid prosody volume value: {volume}",
                        suggestion="Use silent, x-soft, soft, medium, loud, x-loud, or a value in dB/%",
                        element="prosody",
                    )
                )

    def _check_provider_compatibility(
        self,
        root: ET.Element,
        provider: SSMLProvider,
    ) -> SSMLProviderCompatibility:
        """Check SSML compatibility with a specific provider."""
        unsupported = PROVIDER_UNSUPPORTED.get(provider, set())
        found_unsupported: list[str] = []
        modifications: list[str] = []

        for elem in root.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
            if tag in unsupported:
                found_unsupported.append(tag)

        if found_unsupported:
            modifications.append(f"Remove or replace: {', '.join(set(found_unsupported))}")

        return SSMLProviderCompatibility(
            provider=provider,
            is_compatible=len(found_unsupported) == 0,
            unsupported_elements=found_unsupported if found_unsupported else None,
            modifications_needed=modifications if modifications else None,
        )


# ============================================
# SSML Builder (Fluent API)
# ============================================


class SSMLBuilder:
    """Fluent builder for constructing SSML programmatically."""

    def __init__(self, language: str = "en-US"):
        """Initialize the builder with a language."""
        self._language = language
        self._elements: list[str] = []
        self._prosody_stack: list[dict[str, str]] = []

    def text(self, content: str) -> "SSMLBuilder":
        """Add plain text content."""
        self._elements.append(html.escape(content, quote=False))
        return self

    def break_pause(
        self,
        time_ms: int | None = None,
        strength: SSMLBreakStrength | None = None,
    ) -> "SSMLBuilder":
        """Add a break/pause."""
        if time_ms:
            self._elements.append(f'<break time="{time_ms}ms"/>')
        elif strength:
            self._elements.append(f'<break strength="{strength.value.lower().replace("_", "-")}"/>')
        else:
            self._elements.append('<break time="250ms"/>')
        return self

    def emphasis(self, text: str, level: SSMLEmphasisLevel = SSMLEmphasisLevel.MODERATE) -> "SSMLBuilder":
        """Add emphasized text."""
        level_value = level.value.lower()
        escaped = html.escape(text, quote=False)
        self._elements.append(f'<emphasis level="{level_value}">{escaped}</emphasis>')
        return self

    def prosody(
        self,
        text: str,
        rate: str | None = None,
        pitch: str | None = None,
        volume: str | None = None,
    ) -> "SSMLBuilder":
        """Add text with prosody modifications."""
        attrs = []
        if rate:
            attrs.append(f'rate="{rate}"')
        if pitch:
            attrs.append(f'pitch="{pitch}"')
        if volume:
            attrs.append(f'volume="{volume}"')

        attr_str = " ".join(attrs)
        escaped = html.escape(text, quote=False)
        self._elements.append(f"<prosody {attr_str}>{escaped}</prosody>")
        return self

    def say_as(
        self,
        text: str,
        interpret_as: str,
        format: str | None = None,
    ) -> "SSMLBuilder":
        """Add say-as element for special interpretation."""
        escaped = html.escape(text, quote=False)
        if format:
            self._elements.append(f'<say-as interpret-as="{interpret_as}" format="{format}">{escaped}</say-as>')
        else:
            self._elements.append(f'<say-as interpret-as="{interpret_as}">{escaped}</say-as>')
        return self

    def phoneme(self, text: str, phonetic: str, alphabet: str = "ipa") -> "SSMLBuilder":
        """Add phoneme for custom pronunciation."""
        escaped = html.escape(text, quote=False)
        self._elements.append(f'<phoneme alphabet="{alphabet}" ph="{phonetic}">{escaped}</phoneme>')
        return self

    def sub(self, text: str, alias: str) -> "SSMLBuilder":
        """Substitute text with an alias."""
        escaped = html.escape(text, quote=False)
        alias_escaped = html.escape(alias, quote=False)
        self._elements.append(f'<sub alias="{alias_escaped}">{escaped}</sub>')
        return self

    def audio(self, src: str, alt_text: str | None = None) -> "SSMLBuilder":
        """Add an audio clip."""
        if alt_text:
            escaped = html.escape(alt_text, quote=False)
            self._elements.append(f'<audio src="{src}"><desc>{escaped}</desc></audio>')
        else:
            self._elements.append(f'<audio src="{src}"/>')
        return self

    def sentence(self, text: str) -> "SSMLBuilder":
        """Wrap text in a sentence element."""
        escaped = html.escape(text, quote=False)
        self._elements.append(f"<s>{escaped}</s>")
        return self

    def paragraph(self, text: str) -> "SSMLBuilder":
        """Wrap text in a paragraph element."""
        escaped = html.escape(text, quote=False)
        self._elements.append(f"<p>{escaped}</p>")
        return self

    def build(self) -> str:
        """Build the final SSML string."""
        content = "\n  ".join(self._elements)
        return f'<speak version="{SSML_VERSION}" xmlns="{SSML_XMLNS}" xml:lang="{self._language}">\n  {content}\n</speak>'


# ============================================
# Convenience Functions
# ============================================


def generate_ssml(
    voice_response: VoiceResponse,
    options: SSMLOptions | None = None,
) -> str:
    """Generate SSML from a VoiceResponse type.

    Args:
        voice_response: The voice response to convert.
        options: Optional generation options.

    Returns:
        A valid SSML string.
    """
    generator = SSMLGenerator(options or SSMLOptions())
    return generator.generate_ssml(voice_response)


def text_to_ssml(
    text: str,
    options: SSMLOptions | None = None,
) -> str:
    """Convert plain text to SSML with smart defaults.

    Args:
        text: Plain text to convert.
        options: Optional generation options.

    Returns:
        A valid SSML string.
    """
    generator = SSMLGenerator(options or SSMLOptions())
    return generator.text_to_ssml(text, options)


def validate_ssml(
    ssml: str,
    target_providers: list[SSMLProvider] | None = None,
) -> SSMLValidationResult:
    """Validate SSML against W3C spec.

    Args:
        ssml: The SSML string to validate.
        target_providers: Optional list of providers to check compatibility.

    Returns:
        Validation result with errors, warnings, and provider compatibility.
    """
    validator = SSMLValidator()
    return validator.validate_ssml(ssml, target_providers)


# ============================================
# Exporter Class (for consistency with other exporters)
# ============================================


@dataclass
class SSMLExporter:
    """Exporter for converting VoiceResponse to SSML.

    Provides a consistent interface with other LUI schema exporters.
    """

    options: SSMLOptions = field(default_factory=SSMLOptions)

    def export(self, voice_response: VoiceResponse) -> str:
        """Export a VoiceResponse to SSML format.

        Args:
            voice_response: The voice response to export.

        Returns:
            A valid SSML string.
        """
        return generate_ssml(voice_response, self.options)

    def export_text(self, text: str) -> str:
        """Export plain text to SSML format.

        Args:
            text: Plain text to convert.

        Returns:
            A valid SSML string.
        """
        return text_to_ssml(text, self.options)

    def validate(
        self,
        ssml: str,
        target_providers: list[SSMLProvider] | None = None,
    ) -> SSMLValidationResult:
        """Validate SSML content.

        Args:
            ssml: The SSML string to validate.
            target_providers: Optional providers to check compatibility.

        Returns:
            Validation result.
        """
        return validate_ssml(ssml, target_providers)


def export_to_ssml(
    voice_response: VoiceResponse,
    options: SSMLOptions | None = None,
) -> str:
    """Export a VoiceResponse to SSML format.

    Args:
        voice_response: The voice response to export.
        options: Optional generation options.

    Returns:
        A valid SSML string.
    """
    exporter = SSMLExporter(options or SSMLOptions())
    return exporter.export(voice_response)
