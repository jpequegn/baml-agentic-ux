"""Tests for SSML Types and Utilities (Issue #36).

This module tests the SSML type definitions and Python utilities
for generating, validating, and building SSML for voice output.
"""

import pytest
from baml_client.types import (
    # SSML Types
    SSMLElementType,
    SSMLDocument,
    SSMLElement,
    SSMLAttributes,
    SSMLBreakStrength,
    SSMLEmphasisLevel,
    SSMLProsodyRate,
    SSMLProsodyPitch,
    SSMLProsodyVolume,
    SSMLSayAsInterpretAs,
    SSMLDateFormat,
    SSMLProvider,
    SSMLValidationResult,
    SSMLValidationError,
    SSMLValidationWarning,
    SSMLProviderCompatibility,
    SSMLGenerationOptions,
    SSMLPausePatternType,
    SSMLNumberReadAs,
    # Voice types from multimodal
    VoiceResponse,
    VoiceConfig,
    VoiceSpeakingStyle,
    VoiceSegment,
    EmphasisLevel,
)

from src.lui_schema_export.ssml import (
    generate_ssml,
    text_to_ssml,
    validate_ssml,
    SSMLGenerator,
    SSMLValidator,
    SSMLBuilder,
    SSMLOptions,
    SSMLExporter,
    export_to_ssml,
    SSML_VERSION,
    SSML_XMLNS,
)


class TestSSMLElementTypeEnum:
    """Test SSMLElementType enum values."""

    def test_element_type_has_all_values(self):
        """Verify all expected SSML element types exist."""
        expected = {
            "SPEAK",
            "BREAK",
            "EMPHASIS",
            "PROSODY",
            "SAY_AS",
            "PHONEME",
            "SUB",
            "AUDIO",
            "P",
            "S",
            "VOICE",
            "LANG",
            "MARK",
            "DESC",
        }
        actual = {t.name for t in SSMLElementType}
        assert actual == expected


class TestSSMLBreakStrengthEnum:
    """Test SSMLBreakStrength enum values."""

    def test_break_strength_has_all_values(self):
        """Verify all break strength values exist."""
        expected = {"NONE", "X_WEAK", "WEAK", "MEDIUM", "STRONG", "X_STRONG"}
        actual = {s.name for s in SSMLBreakStrength}
        assert actual == expected


class TestSSMLEmphasisLevelEnum:
    """Test SSMLEmphasisLevel enum values."""

    def test_emphasis_level_has_all_values(self):
        """Verify all emphasis level values exist."""
        expected = {"REDUCED", "NONE", "MODERATE", "STRONG"}
        actual = {e.name for e in SSMLEmphasisLevel}
        assert actual == expected


class TestSSMLProsodyEnums:
    """Test prosody-related enums."""

    def test_prosody_rate_values(self):
        """Verify prosody rate options."""
        expected = {"X_SLOW", "SLOW", "MEDIUM", "FAST", "X_FAST"}
        actual = {r.name for r in SSMLProsodyRate}
        assert actual == expected

    def test_prosody_pitch_values(self):
        """Verify prosody pitch options."""
        expected = {"X_LOW", "LOW", "MEDIUM", "HIGH", "X_HIGH"}
        actual = {p.name for p in SSMLProsodyPitch}
        assert actual == expected

    def test_prosody_volume_values(self):
        """Verify prosody volume options."""
        expected = {"SILENT", "X_SOFT", "SOFT", "MEDIUM", "LOUD", "X_LOUD"}
        actual = {v.name for v in SSMLProsodyVolume}
        assert actual == expected


class TestSSMLSayAsEnums:
    """Test say-as related enums."""

    def test_interpret_as_values(self):
        """Verify say-as interpret-as options."""
        expected = {
            "DATE",
            "TIME",
            "TELEPHONE",
            "CHARACTERS",
            "CARDINAL",
            "ORDINAL",
            "FRACTION",
            "UNIT",
            "VERBATIM",
            "SPELL_OUT",
            "ADDRESS",
            "CURRENCY",
            "EXPLETIVE",
        }
        actual = {i.name for i in SSMLSayAsInterpretAs}
        assert actual == expected

    def test_date_format_values(self):
        """Verify date format options."""
        expected = {"MDY", "DMY", "YMD", "MD", "DM", "YM", "MY", "D", "M", "Y"}
        actual = {f.name for f in SSMLDateFormat}
        assert actual == expected


class TestSSMLProviderEnum:
    """Test SSMLProvider enum values."""

    def test_provider_has_all_values(self):
        """Verify all TTS provider options exist."""
        expected = {"GENERIC", "GOOGLE", "AMAZON_POLLY", "AZURE", "ELEVENLABS", "OPENAI"}
        actual = {p.name for p in SSMLProvider}
        assert actual == expected


class TestSSMLAttributesClass:
    """Test SSMLAttributes class construction."""

    def test_attributes_creation_break(self):
        """Test creating break attributes."""
        attrs = SSMLAttributes(
            time="500ms",
            strength=SSMLBreakStrength.MEDIUM,
            level=None,
            rate=None,
            pitch=None,
            volume=None,
            contour=None,
            duration=None,
            range=None,
            interpret_as=None,
            format=None,
            detail=None,
            alphabet=None,
            ph=None,
            alias=None,
            src=None,
            clip_begin=None,
            clip_end=None,
            speed=None,
            repeat_count=None,
            repeat_dur=None,
            sound_level=None,
            name=None,
            gender=None,
            age=None,
            variant=None,
            xml_lang=None,
            mark_name=None,
        )
        assert attrs.time == "500ms"
        assert attrs.strength == SSMLBreakStrength.MEDIUM

    def test_attributes_creation_prosody(self):
        """Test creating prosody attributes."""
        attrs = SSMLAttributes(
            time=None,
            strength=None,
            level=None,
            rate="medium",
            pitch="+2st",
            volume="loud",
            contour=None,
            duration=None,
            range=None,
            interpret_as=None,
            format=None,
            detail=None,
            alphabet=None,
            ph=None,
            alias=None,
            src=None,
            clip_begin=None,
            clip_end=None,
            speed=None,
            repeat_count=None,
            repeat_dur=None,
            sound_level=None,
            name=None,
            gender=None,
            age=None,
            variant=None,
            xml_lang=None,
            mark_name=None,
        )
        assert attrs.rate == "medium"
        assert attrs.pitch == "+2st"
        assert attrs.volume == "loud"


class TestSSMLElementClass:
    """Test SSMLElement class construction."""

    def test_element_creation_simple(self):
        """Test creating a simple SSML element."""
        element = SSMLElement(
            element_type=SSMLElementType.BREAK,
            text=None,
            attributes=SSMLAttributes(
                time="250ms",
                strength=None,
                level=None,
                rate=None,
                pitch=None,
                volume=None,
                contour=None,
                duration=None,
                range=None,
                interpret_as=None,
                format=None,
                detail=None,
                alphabet=None,
                ph=None,
                alias=None,
                src=None,
                clip_begin=None,
                clip_end=None,
                speed=None,
                repeat_count=None,
                repeat_dur=None,
                sound_level=None,
                name=None,
                gender=None,
                age=None,
                variant=None,
                xml_lang=None,
                mark_name=None,
            ),
            children=None,
        )
        assert element.element_type == SSMLElementType.BREAK
        assert element.attributes is not None
        assert element.attributes.time == "250ms"

    def test_element_with_text(self):
        """Test creating an element with text content."""
        element = SSMLElement(
            element_type=SSMLElementType.EMPHASIS,
            text="important",
            attributes=SSMLAttributes(
                time=None,
                strength=None,
                level=SSMLEmphasisLevel.STRONG,
                rate=None,
                pitch=None,
                volume=None,
                contour=None,
                duration=None,
                range=None,
                interpret_as=None,
                format=None,
                detail=None,
                alphabet=None,
                ph=None,
                alias=None,
                src=None,
                clip_begin=None,
                clip_end=None,
                speed=None,
                repeat_count=None,
                repeat_dur=None,
                sound_level=None,
                name=None,
                gender=None,
                age=None,
                variant=None,
                xml_lang=None,
                mark_name=None,
            ),
            children=None,
        )
        assert element.text == "important"
        assert element.attributes is not None
        assert element.attributes.level == SSMLEmphasisLevel.STRONG


class TestSSMLDocumentClass:
    """Test SSMLDocument class construction."""

    def test_document_creation(self):
        """Test creating an SSML document."""
        content = [
            SSMLElement(
                element_type=SSMLElementType.PROSODY,
                text="Hello world",
                attributes=SSMLAttributes(
                    time=None,
                    strength=None,
                    level=None,
                    rate="medium",
                    pitch=None,
                    volume=None,
                    contour=None,
                    duration=None,
                    range=None,
                    interpret_as=None,
                    format=None,
                    detail=None,
                    alphabet=None,
                    ph=None,
                    alias=None,
                    src=None,
                    clip_begin=None,
                    clip_end=None,
                    speed=None,
                    repeat_count=None,
                    repeat_dur=None,
                    sound_level=None,
                    name=None,
                    gender=None,
                    age=None,
                    variant=None,
                    xml_lang=None,
                    mark_name=None,
                ),
                children=None,
            )
        ]
        doc = SSMLDocument(
            version="1.1",
            xmlns="http://www.w3.org/2001/10/synthesis",
            xml_lang="en-US",
            content=content,
            onlangfailure=None,
        )
        assert doc.version == "1.1"
        assert doc.xml_lang == "en-US"
        assert len(doc.content) == 1


class TestSSMLValidationResultClass:
    """Test SSMLValidationResult class construction."""

    def test_valid_result(self):
        """Test creating a valid result."""
        result = SSMLValidationResult(
            is_valid=True,
            errors=None,
            warnings=None,
            provider_compatibility=None,
        )
        assert result.is_valid is True
        assert result.errors is None

    def test_invalid_result_with_errors(self):
        """Test creating an invalid result with errors."""
        errors = [
            SSMLValidationError(
                code="XML_PARSE_ERROR",
                message="Invalid XML structure",
                line=5,
                column=10,
                element="prosody",
            )
        ]
        result = SSMLValidationResult(
            is_valid=False,
            errors=errors,
            warnings=None,
            provider_compatibility=None,
        )
        assert result.is_valid is False
        assert result.errors is not None
        assert len(result.errors) == 1
        assert result.errors[0].code == "XML_PARSE_ERROR"


class TestSSMLGenerationOptionsClass:
    """Test SSMLGenerationOptions class construction."""

    def test_options_creation(self):
        """Test creating generation options."""
        options = SSMLGenerationOptions(
            auto_sentence_breaks=True,
            auto_paragraph_breaks=True,
            default_rate=SSMLProsodyRate.MEDIUM,
            default_pitch=SSMLProsodyPitch.MEDIUM,
            default_volume=SSMLProsodyVolume.MEDIUM,
            preserve_whitespace=False,
            escape_special_chars=True,
            target_provider=SSMLProvider.GOOGLE,
        )
        assert options.auto_sentence_breaks is True
        assert options.default_rate == SSMLProsodyRate.MEDIUM
        assert options.target_provider == SSMLProvider.GOOGLE


# ============================================
# Python Utility Tests
# ============================================


class TestSSMLOptions:
    """Test SSMLOptions dataclass."""

    def test_default_options(self):
        """Test default option values."""
        opts = SSMLOptions()
        assert opts.auto_sentence_breaks is True
        assert opts.auto_paragraph_breaks is True
        assert opts.default_rate is None
        assert opts.escape_special_chars is True
        assert opts.target_provider == SSMLProvider.GENERIC

    def test_custom_options(self):
        """Test custom option values."""
        opts = SSMLOptions(
            auto_sentence_breaks=False,
            default_rate=SSMLProsodyRate.FAST,
            target_provider=SSMLProvider.AMAZON_POLLY,
        )
        assert opts.auto_sentence_breaks is False
        assert opts.default_rate == SSMLProsodyRate.FAST
        assert opts.target_provider == SSMLProvider.AMAZON_POLLY


class TestSSMLGenerator:
    """Test SSMLGenerator class."""

    def test_generate_ssml_basic(self):
        """Test basic SSML generation from VoiceResponse."""
        voice = VoiceResponse(
            text="Hello, how can I help you?",
            ssml=None,
            voice_config=None,
            audio_hints=None,
            fallback_text=None,
            language="en-US",
            segments=None,
        )
        generator = SSMLGenerator()
        ssml = generator.generate_ssml(voice)

        assert '<speak version="1.1"' in ssml
        assert 'xml:lang="en-US"' in ssml
        assert "Hello" in ssml
        assert "</speak>" in ssml

    def test_generate_ssml_with_prosody(self):
        """Test SSML generation with voice config."""
        voice = VoiceResponse(
            text="Important announcement",
            ssml=None,
            voice_config=VoiceConfig(
                voice_id=None,
                gender=None,
                age_group=None,
                speaking_rate=1.2,
                pitch=2.0,
                volume=0.8,
                style=None,
            ),
            audio_hints=None,
            fallback_text=None,
            language="en-US",
            segments=None,
        )
        generator = SSMLGenerator()
        ssml = generator.generate_ssml(voice)

        assert "<prosody" in ssml
        assert 'rate="120%"' in ssml
        assert 'pitch="+2.0st"' in ssml
        assert 'volume="loud"' in ssml

    def test_generate_ssml_with_segments(self):
        """Test SSML generation with voice segments."""
        voice = VoiceResponse(
            text="Base text",
            ssml=None,
            voice_config=None,
            audio_hints=None,
            fallback_text=None,
            language="en-US",
            segments=[
                VoiceSegment(
                    text="First segment",
                    ssml=None,
                    pause_before_ms=500,
                    pause_after_ms=None,
                    emphasis=EmphasisLevel.STRONG,
                ),
                VoiceSegment(
                    text="Second segment",
                    ssml=None,
                    pause_before_ms=None,
                    pause_after_ms=250,
                    emphasis=None,
                ),
            ],
        )
        generator = SSMLGenerator()
        ssml = generator.generate_ssml(voice)

        assert '<break time="500ms"/>' in ssml
        assert '<emphasis level="strong">' in ssml
        assert "First segment" in ssml
        assert '<break time="250ms"/>' in ssml
        assert "Second segment" in ssml

    def test_text_to_ssml_basic(self):
        """Test basic text to SSML conversion."""
        generator = SSMLGenerator()
        ssml = generator.text_to_ssml("Hello world. How are you?")

        assert '<speak version="1.1"' in ssml
        assert "</speak>" in ssml
        assert "Hello world" in ssml

    def test_text_to_ssml_with_paragraphs(self):
        """Test text to SSML with paragraph breaks."""
        text = "First paragraph.\n\nSecond paragraph."
        generator = SSMLGenerator()
        ssml = generator.text_to_ssml(text)

        assert "<p>" in ssml
        assert "</p>" in ssml
        assert '<break strength="strong"/>' in ssml

    def test_text_to_ssml_with_options(self):
        """Test text to SSML with custom options."""
        opts = SSMLOptions(
            default_rate=SSMLProsodyRate.FAST,
            default_pitch=SSMLProsodyPitch.HIGH,
            auto_paragraph_breaks=False,
        )
        generator = SSMLGenerator(options=opts)
        ssml = generator.text_to_ssml("Test text", opts)

        assert "<prosody" in ssml
        assert 'rate="fast"' in ssml
        assert 'pitch="high"' in ssml

    def test_escape_special_characters(self):
        """Test that special characters are escaped."""
        voice = VoiceResponse(
            text="Use <command> & press Enter",
            ssml=None,
            voice_config=None,
            audio_hints=None,
            fallback_text=None,
            language="en-US",
            segments=None,
        )
        generator = SSMLGenerator()
        ssml = generator.generate_ssml(voice)

        assert "&lt;command&gt;" in ssml
        assert "&amp;" in ssml


class TestSSMLValidator:
    """Test SSMLValidator class."""

    def test_validate_valid_ssml(self):
        """Test validation of valid SSML."""
        ssml = '<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis">Hello world</speak>'
        validator = SSMLValidator()
        result = validator.validate_ssml(ssml)

        assert result.is_valid is True
        assert result.errors is None or len(result.errors) == 0

    def test_validate_invalid_xml(self):
        """Test validation of invalid XML."""
        ssml = "<speak>Unclosed tag"
        validator = SSMLValidator()
        result = validator.validate_ssml(ssml)

        assert result.is_valid is False
        assert result.errors is not None
        assert len(result.errors) > 0
        assert result.errors[0].code == "XML_PARSE_ERROR"

    def test_validate_missing_version(self):
        """Test validation warning for missing version."""
        ssml = '<speak xmlns="http://www.w3.org/2001/10/synthesis">Hello</speak>'
        validator = SSMLValidator()
        result = validator.validate_ssml(ssml)

        assert result.is_valid is True
        assert result.warnings is not None
        assert any(w.code == "MISSING_VERSION" for w in result.warnings)

    def test_validate_provider_compatibility(self):
        """Test provider compatibility checking."""
        ssml = '<speak version="1.1"><phoneme alphabet="ipa" ph="həˈloʊ">hello</phoneme></speak>'
        validator = SSMLValidator()
        result = validator.validate_ssml(ssml, [SSMLProvider.ELEVENLABS])

        assert result.provider_compatibility is not None
        assert len(result.provider_compatibility) == 1
        compat = result.provider_compatibility[0]
        assert compat.provider == SSMLProvider.ELEVENLABS
        assert compat.is_compatible is False
        assert compat.unsupported_elements is not None
        assert "phoneme" in compat.unsupported_elements

    def test_validate_prosody_attributes(self):
        """Test prosody attribute validation."""
        ssml = '<speak version="1.1"><prosody rate="invalid-rate">Hello</prosody></speak>'
        validator = SSMLValidator()
        result = validator.validate_ssml(ssml)

        assert result.warnings is not None
        assert any(w.code == "INVALID_RATE" for w in result.warnings)


class TestSSMLBuilder:
    """Test SSMLBuilder fluent API."""

    def test_builder_basic(self):
        """Test basic builder usage."""
        builder = SSMLBuilder(language="en-US")
        ssml = builder.text("Hello world").build()

        assert '<speak version="1.1"' in ssml
        assert 'xml:lang="en-US"' in ssml
        assert "Hello world" in ssml

    def test_builder_with_break(self):
        """Test builder with break."""
        builder = SSMLBuilder()
        ssml = builder.text("Hello").break_pause(time_ms=500).text("world").build()

        assert '<break time="500ms"/>' in ssml
        assert "Hello" in ssml
        assert "world" in ssml

    def test_builder_with_emphasis(self):
        """Test builder with emphasis."""
        builder = SSMLBuilder()
        ssml = builder.text("This is ").emphasis("important", SSMLEmphasisLevel.STRONG).build()

        assert '<emphasis level="strong">important</emphasis>' in ssml

    def test_builder_with_prosody(self):
        """Test builder with prosody."""
        builder = SSMLBuilder()
        ssml = builder.prosody("Fast speech", rate="fast", pitch="high").build()

        assert '<prosody rate="fast" pitch="high">' in ssml
        assert "Fast speech" in ssml

    def test_builder_with_say_as(self):
        """Test builder with say-as."""
        builder = SSMLBuilder()
        ssml = builder.say_as("12/25/2025", interpret_as="date", format="mdy").build()

        assert '<say-as interpret-as="date" format="mdy">' in ssml
        assert "12/25/2025" in ssml

    def test_builder_with_phoneme(self):
        """Test builder with phoneme."""
        builder = SSMLBuilder()
        ssml = builder.phoneme("tomato", "təˈmeɪtoʊ", alphabet="ipa").build()

        assert '<phoneme alphabet="ipa" ph="təˈmeɪtoʊ">' in ssml
        assert "tomato" in ssml

    def test_builder_with_sub(self):
        """Test builder with substitution."""
        builder = SSMLBuilder()
        ssml = builder.sub("W3C", "World Wide Web Consortium").build()

        assert '<sub alias="World Wide Web Consortium">W3C</sub>' in ssml

    def test_builder_with_audio(self):
        """Test builder with audio."""
        builder = SSMLBuilder()
        ssml = builder.audio("https://example.com/sound.mp3", alt_text="A sound").build()

        assert '<audio src="https://example.com/sound.mp3">' in ssml
        assert "<desc>A sound</desc>" in ssml

    def test_builder_with_sentence_and_paragraph(self):
        """Test builder with sentence and paragraph."""
        builder = SSMLBuilder()
        ssml = builder.paragraph("This is a paragraph.").sentence("This is a sentence.").build()

        assert "<p>This is a paragraph.</p>" in ssml
        assert "<s>This is a sentence.</s>" in ssml

    def test_builder_chain_multiple(self):
        """Test chaining multiple builder methods."""
        builder = SSMLBuilder(language="en-US")
        ssml = (
            builder.text("Welcome! ")
            .break_pause(time_ms=300)
            .emphasis("Important:", SSMLEmphasisLevel.MODERATE)
            .text(" ")
            .prosody("Please listen carefully.", rate="slow")
            .build()
        )

        assert "Welcome!" in ssml
        assert '<break time="300ms"/>' in ssml
        assert '<emphasis level="moderate">' in ssml
        assert '<prosody rate="slow">' in ssml


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_generate_ssml_function(self):
        """Test generate_ssml convenience function."""
        voice = VoiceResponse(
            text="Test message",
            ssml=None,
            voice_config=None,
            audio_hints=None,
            fallback_text=None,
            language="en-US",
            segments=None,
        )
        ssml = generate_ssml(voice)

        assert "<speak" in ssml
        assert "Test message" in ssml

    def test_text_to_ssml_function(self):
        """Test text_to_ssml convenience function."""
        ssml = text_to_ssml("Hello world")

        assert "<speak" in ssml
        assert "Hello world" in ssml

    def test_validate_ssml_function(self):
        """Test validate_ssml convenience function."""
        ssml = '<speak version="1.1">Hello</speak>'
        result = validate_ssml(ssml)

        assert result.is_valid is True


class TestSSMLExporter:
    """Test SSMLExporter class."""

    def test_exporter_export(self):
        """Test SSMLExporter export method."""
        voice = VoiceResponse(
            text="Export test",
            ssml=None,
            voice_config=None,
            audio_hints=None,
            fallback_text=None,
            language="en-US",
            segments=None,
        )
        exporter = SSMLExporter()
        ssml = exporter.export(voice)

        assert "<speak" in ssml
        assert "Export test" in ssml

    def test_exporter_export_text(self):
        """Test SSMLExporter export_text method."""
        exporter = SSMLExporter()
        ssml = exporter.export_text("Text export test")

        assert "<speak" in ssml
        assert "Text export test" in ssml

    def test_exporter_validate(self):
        """Test SSMLExporter validate method."""
        exporter = SSMLExporter()
        result = exporter.validate('<speak version="1.1">Test</speak>')

        assert result.is_valid is True

    def test_export_to_ssml_function(self):
        """Test export_to_ssml convenience function."""
        voice = VoiceResponse(
            text="Export function test",
            ssml=None,
            voice_config=None,
            audio_hints=None,
            fallback_text=None,
            language="en-US",
            segments=None,
        )
        ssml = export_to_ssml(voice)

        assert "<speak" in ssml
        assert "Export function test" in ssml


class TestSSMLProviderCompatibility:
    """Test SSML provider compatibility."""

    def test_google_compatibility(self):
        """Test Google TTS compatibility."""
        ssml = '<speak version="1.1"><prosody rate="medium">Hello</prosody></speak>'
        result = validate_ssml(ssml, [SSMLProvider.GOOGLE])

        assert result.provider_compatibility is not None
        compat = result.provider_compatibility[0]
        assert compat.provider == SSMLProvider.GOOGLE
        assert compat.is_compatible is True

    def test_elevenlabs_limited_support(self):
        """Test ElevenLabs limited SSML support."""
        # ElevenLabs doesn't support phoneme
        ssml = '<speak version="1.1"><phoneme>test</phoneme></speak>'
        result = validate_ssml(ssml, [SSMLProvider.ELEVENLABS])

        assert result.provider_compatibility is not None
        compat = result.provider_compatibility[0]
        assert compat.provider == SSMLProvider.ELEVENLABS
        assert compat.is_compatible is False

    def test_openai_very_limited_support(self):
        """Test OpenAI very limited SSML support."""
        # OpenAI doesn't support prosody
        ssml = '<speak version="1.1"><prosody rate="fast">test</prosody></speak>'
        result = validate_ssml(ssml, [SSMLProvider.OPENAI])

        assert result.provider_compatibility is not None
        compat = result.provider_compatibility[0]
        assert compat.provider == SSMLProvider.OPENAI
        assert compat.is_compatible is False

    def test_multiple_providers(self):
        """Test checking multiple providers."""
        ssml = '<speak version="1.1">Simple text</speak>'
        result = validate_ssml(
            ssml, [SSMLProvider.GOOGLE, SSMLProvider.AMAZON_POLLY, SSMLProvider.AZURE]
        )

        assert result.provider_compatibility is not None
        assert len(result.provider_compatibility) == 3
        # Simple text should be compatible with all
        for compat in result.provider_compatibility:
            assert compat.is_compatible is True


class TestSSMLIntegration:
    """Integration tests for SSML generation and validation."""

    def test_generate_and_validate(self):
        """Test generating SSML and validating it."""
        voice = VoiceResponse(
            text="This is a complete test of SSML generation.",
            ssml=None,
            voice_config=VoiceConfig(
                voice_id=None,
                gender=None,
                age_group=None,
                speaking_rate=1.0,
                pitch=0.0,
                volume=0.7,
                style=VoiceSpeakingStyle.FRIENDLY,
            ),
            audio_hints=None,
            fallback_text=None,
            language="en-US",
            segments=None,
        )

        ssml = generate_ssml(voice)
        result = validate_ssml(ssml)

        assert result.is_valid is True

    def test_builder_output_validates(self):
        """Test that builder output is valid SSML."""
        builder = SSMLBuilder(language="en-US")
        ssml = (
            builder.text("Welcome to our service. ")
            .break_pause(time_ms=500)
            .emphasis("Important notice:", SSMLEmphasisLevel.STRONG)
            .text(" Please review the terms. ")
            .prosody("Thank you for your attention.", rate="medium", pitch="medium")
            .build()
        )

        result = validate_ssml(ssml)
        assert result.is_valid is True

    def test_complex_ssml_all_providers(self):
        """Test complex SSML against all providers."""
        # Build SSML with basic elements that most providers support
        builder = SSMLBuilder(language="en-US")
        ssml = builder.text("Hello. ").break_pause(time_ms=300).text("How are you?").build()

        result = validate_ssml(
            ssml,
            [
                SSMLProvider.GENERIC,
                SSMLProvider.GOOGLE,
                SSMLProvider.AMAZON_POLLY,
                SSMLProvider.AZURE,
            ],
        )

        assert result.is_valid is True
        assert result.provider_compatibility is not None
        # Basic break should be compatible with major providers
        compatible_count = sum(
            1 for c in result.provider_compatibility if c.is_compatible
        )
        assert compatible_count >= 3  # At least 3 providers should support this
