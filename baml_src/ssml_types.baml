// SSML (Speech Synthesis Markup Language) Types
// W3C SSML 1.1 compliant type definitions for voice output
// Issue #36 - Phase 1: Multi-Modal LUI Support

// ============================================
// SSML Element Types
// ============================================

/// Types of SSML elements supported
enum SSMLElementType {
  SPEAK @description("Root element for SSML document")
  BREAK @description("Insert pause in speech")
  EMPHASIS @description("Add emphasis to text")
  PROSODY @description("Control pitch, rate, and volume")
  SAY_AS @description("Specify how to interpret text (date, time, etc.)")
  PHONEME @description("Specify phonetic pronunciation")
  SUB @description("Substitute text with alias")
  AUDIO @description("Insert audio file")
  P @description("Paragraph break")
  S @description("Sentence break")
  VOICE @description("Switch voice characteristics")
  LANG @description("Specify language for content")
  MARK @description("Named bookmark in speech")
  DESC @description("Description for audio fallback")
}

// ============================================
// SSML Attribute Types
// ============================================

/// Strength levels for breaks
enum SSMLBreakStrength {
  NONE @description("No break")
  X_WEAK @description("Extra weak break (shortest)")
  WEAK @description("Weak break")
  MEDIUM @description("Medium break")
  STRONG @description("Strong break")
  X_STRONG @description("Extra strong break (longest)")
}

/// Emphasis levels
enum SSMLEmphasisLevel {
  REDUCED @description("Less emphasis than normal")
  NONE @description("No emphasis")
  MODERATE @description("Moderate emphasis")
  STRONG @description("Strong emphasis")
}

/// Prosody rate values
enum SSMLProsodyRate {
  X_SLOW @description("Extra slow speech")
  SLOW @description("Slow speech")
  MEDIUM @description("Normal speech rate")
  FAST @description("Fast speech")
  X_FAST @description("Extra fast speech")
}

/// Prosody pitch values
enum SSMLProsodyPitch {
  X_LOW @description("Extra low pitch")
  LOW @description("Low pitch")
  MEDIUM @description("Normal pitch")
  HIGH @description("High pitch")
  X_HIGH @description("Extra high pitch")
}

/// Prosody volume values
enum SSMLProsodyVolume {
  SILENT @description("Silent (no sound)")
  X_SOFT @description("Extra soft volume")
  SOFT @description("Soft volume")
  MEDIUM @description("Normal volume")
  LOUD @description("Loud volume")
  X_LOUD @description("Extra loud volume")
}

/// Types for say-as interpretation
enum SSMLSayAsInterpretAs {
  DATE @description("Interpret as date")
  TIME @description("Interpret as time")
  TELEPHONE @description("Interpret as telephone number")
  CHARACTERS @description("Spell out characters")
  CARDINAL @description("Cardinal number (one, two, three)")
  ORDINAL @description("Ordinal number (first, second, third)")
  FRACTION @description("Fraction (one half)")
  UNIT @description("Unit of measure")
  VERBATIM @description("Spell letter by letter")
  SPELL_OUT @description("Spell out the word")
  ADDRESS @description("Street address")
  CURRENCY @description("Currency amount")
  EXPLETIVE @description("Bleep out content")
}

/// Date format options for say-as
enum SSMLDateFormat {
  MDY @description("Month-Day-Year")
  DMY @description("Day-Month-Year")
  YMD @description("Year-Month-Day")
  MD @description("Month-Day")
  DM @description("Day-Month")
  YM @description("Year-Month")
  MY @description("Month-Year")
  D @description("Day only")
  M @description("Month only")
  Y @description("Year only")
}

// ============================================
// SSML Attribute Classes
// ============================================

/// Attributes for SSML elements
class SSMLAttributes {
  // Break attributes
  time string? @description("Break duration (e.g., '500ms', '1s', '2.5s')")
  strength SSMLBreakStrength? @description("Break strength level")

  // Emphasis attributes
  level SSMLEmphasisLevel? @description("Emphasis level")

  // Prosody attributes
  rate string? @description("Speech rate: enum value, percentage, or relative (+10%, -20%)")
  pitch string? @description("Pitch: enum value, percentage, Hz, or relative")
  volume string? @description("Volume: enum value, percentage, or dB")
  contour string? @description("Pitch contour pattern")
  duration string? @description("Target duration for content")
  range string? @description("Pitch range")

  // Say-as attributes
  interpret_as SSMLSayAsInterpretAs? @description("How to interpret the content")
  format string? @description("Format hint (e.g., 'mdy' for dates)")
  detail string? @description("Level of detail (e.g., '1' or '2' for telephone)")

  // Phoneme attributes
  alphabet string? @description("Phonetic alphabet: 'ipa' or 'x-sampa'")
  ph string? @description("Phonetic transcription")

  // Sub attributes
  alias string? @description("Substitution text to speak")

  // Audio attributes
  src string? @description("Audio file URL")
  clip_begin string? @description("Start offset in audio")
  clip_end string? @description("End offset in audio")
  speed string? @description("Playback speed percentage")
  repeat_count int? @description("Number of times to repeat audio")
  repeat_dur string? @description("Maximum duration for repeated audio")
  sound_level string? @description("Audio volume adjustment")

  // Voice attributes
  name string? @description("Voice name")
  gender string? @description("Voice gender")
  age string? @description("Voice age")
  variant int? @description("Voice variant number")

  // Lang attributes
  xml_lang string? @description("Language code (e.g., 'en-US', 'fr-FR')")

  // Mark attributes
  mark_name string? @description("Bookmark name")
}

// ============================================
// SSML Document Structure
// ============================================

/// An individual SSML element
class SSMLElement {
  element_type SSMLElementType @description("Type of SSML element")
  text string? @description("Text content of the element")
  attributes SSMLAttributes? @description("Element attributes")
  children SSMLElement[]? @description("Child elements (for nested structures)")
}

/// A complete SSML document
class SSMLDocument {
  version string @description("SSML version (default: '1.1')")
  xmlns string @description("XML namespace for SSML")
  xml_lang string @description("Primary language (e.g., 'en-US')")
  content SSMLElement[] @description("Root-level content elements")
  onlangfailure string? @description("What to do if language not supported")
}

// ============================================
// SSML Generation Options
// ============================================

/// Options for generating SSML from text
class SSMLGenerationOptions {
  auto_sentence_breaks bool @description("Automatically add sentence breaks")
  auto_paragraph_breaks bool @description("Automatically add paragraph breaks")
  default_rate SSMLProsodyRate? @description("Default speech rate")
  default_pitch SSMLProsodyPitch? @description("Default pitch")
  default_volume SSMLProsodyVolume? @description("Default volume")
  preserve_whitespace bool @description("Preserve original whitespace")
  escape_special_chars bool @description("Escape XML special characters")
  target_provider SSMLProvider? @description("Target TTS provider for compatibility")
}

/// TTS provider targets for SSML compatibility
enum SSMLProvider {
  GENERIC @description("W3C standard SSML")
  GOOGLE @description("Google Cloud Text-to-Speech")
  AMAZON_POLLY @description("Amazon Polly")
  AZURE @description("Azure Cognitive Services Speech")
  ELEVENLABS @description("ElevenLabs (limited SSML support)")
  OPENAI @description("OpenAI TTS (limited SSML support)")
}

// ============================================
// SSML Validation Types
// ============================================

/// Result of SSML validation
class SSMLValidationResult {
  is_valid bool @description("Whether the SSML is valid")
  errors SSMLValidationError[]? @description("Validation errors found")
  warnings SSMLValidationWarning[]? @description("Validation warnings")
  provider_compatibility SSMLProviderCompatibility[]? @description("Provider-specific compatibility")
}

/// An SSML validation error
class SSMLValidationError {
  code string @description("Error code")
  message string @description("Human-readable error message")
  line int? @description("Line number where error occurred")
  column int? @description("Column number where error occurred")
  element string? @description("Element that caused the error")
}

/// An SSML validation warning
class SSMLValidationWarning {
  code string @description("Warning code")
  message string @description("Human-readable warning message")
  suggestion string? @description("Suggested fix")
  element string? @description("Element that caused the warning")
}

/// Provider-specific compatibility information
class SSMLProviderCompatibility {
  provider SSMLProvider @description("TTS provider")
  is_compatible bool @description("Whether SSML is compatible with this provider")
  unsupported_elements string[]? @description("Elements not supported by this provider")
  modifications_needed string[]? @description("Modifications needed for compatibility")
}

// ============================================
// SSML Builder Types (for fluent API)
// ============================================

/// A builder pattern for constructing SSML
class SSMLBuilder {
  document SSMLDocument @description("The document being built")
  current_element SSMLElement? @description("Current element being modified")
  element_stack SSMLElement[]? @description("Stack of parent elements")
}

// ============================================
// Convenience Types for Common Patterns
// ============================================

/// Pre-built SSML pattern for pauses
class SSMLPausePattern {
  pattern_type SSMLPausePatternType @description("Type of pause pattern")
  duration_ms int? @description("Custom duration in milliseconds")
}

/// Types of common pause patterns
enum SSMLPausePatternType {
  COMMA @description("Short pause (like after comma)")
  SENTENCE @description("Sentence-ending pause")
  PARAGRAPH @description("Paragraph break pause")
  DRAMATIC @description("Dramatic pause for effect")
  THINKING @description("Pause suggesting thought")
  CUSTOM @description("Custom duration pause")
}

/// Pre-built SSML pattern for emphasis
class SSMLEmphasisPattern {
  text string @description("Text to emphasize")
  level SSMLEmphasisLevel @description("Emphasis level")
  with_pause bool @description("Add brief pause before emphasized text")
}

/// Pre-built SSML pattern for number reading
class SSMLNumberPattern {
  value string @description("Number to speak")
  read_as SSMLNumberReadAs @description("How to read the number")
}

/// Ways to read numbers
enum SSMLNumberReadAs {
  CARDINAL @description("As a number (123 = 'one hundred twenty-three')")
  ORDINAL @description("As an ordinal (1 = 'first')")
  DIGITS @description("Digit by digit (123 = 'one two three')")
  YEAR @description("As a year (2024 = 'twenty twenty-four')")
  PHONE @description("As a phone number")
  CURRENCY @description("As currency")
  FRACTION @description("As a fraction")
}

// ============================================
// SSML Helper Functions
// ============================================

/// Generate SSML from a VoiceResponse
function GenerateSSMLFromVoice(
  voice_response: VoiceResponse,
  options: SSMLGenerationOptions?
) -> SSMLDocument {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Generate an SSML document from the given voice response.

    ## Voice Response
    - Text: {{ voice_response.text }}
    - Language: {{ voice_response.language }}
    {% if voice_response.voice_config %}
    - Speaking Rate: {{ voice_response.voice_config.speaking_rate }}
    - Pitch: {{ voice_response.voice_config.pitch }}
    - Volume: {{ voice_response.voice_config.volume }}
    - Style: {{ voice_response.voice_config.style }}
    {% endif %}
    {% if voice_response.segments %}
    - Segments: {{ voice_response.segments }}
    {% endif %}

    {% if options %}
    ## Generation Options
    - Auto sentence breaks: {{ options.auto_sentence_breaks }}
    - Auto paragraph breaks: {{ options.auto_paragraph_breaks }}
    - Target provider: {{ options.target_provider }}
    {% endif %}

    ## Requirements
    1. Generate valid W3C SSML 1.1
    2. Apply voice configuration settings appropriately
    3. Use prosody elements for rate, pitch, and volume
    4. Handle segments as separate elements if present
    5. Ensure proper XML escaping

    {{ ctx.output_format }}
  "#
}

/// Convert plain text to SSML with intelligent markup
function TextToSSML(
  text: string,
  options: SSMLGenerationOptions?
) -> SSMLDocument {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Convert plain text to an SSML document with intelligent markup.

    ## Text
    {{ text }}

    {% if options %}
    ## Options
    - Auto sentence breaks: {{ options.auto_sentence_breaks }}
    - Auto paragraph breaks: {{ options.auto_paragraph_breaks }}
    - Default rate: {{ options.default_rate }}
    - Default pitch: {{ options.default_pitch }}
    - Default volume: {{ options.default_volume }}
    - Target provider: {{ options.target_provider }}
    {% endif %}

    ## Requirements
    1. Analyze text for natural speech patterns
    2. Add appropriate breaks for punctuation
    3. Apply emphasis to important words/phrases
    4. Use say-as for numbers, dates, and special content
    5. Ensure proper XML structure and escaping

    {{ ctx.output_format }}
  "#
}

/// Validate SSML against W3C spec and provider compatibility
function ValidateSSML(
  ssml_content: string,
  target_providers: SSMLProvider[]?
) -> SSMLValidationResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Validate the given SSML content.

    ## SSML Content
    {{ ssml_content }}

    {% if target_providers %}
    ## Target Providers
    Check compatibility with: {{ target_providers }}
    {% endif %}

    ## Validation Steps
    1. Check XML well-formedness
    2. Verify SSML 1.1 compliance
    3. Check for deprecated elements
    4. Validate attribute values
    5. Check provider-specific compatibility if specified

    {{ ctx.output_format }}
  "#
}

// ============================================
// Test Cases
// ============================================

test generate_ssml_basic {
  functions [TextToSSML]
  args {
    text "Hello! Welcome to the task manager. Your meeting starts in 30 minutes."
    options {
      auto_sentence_breaks true
      auto_paragraph_breaks false
      default_rate MEDIUM
      default_pitch MEDIUM
      default_volume MEDIUM
      preserve_whitespace false
      escape_special_chars true
      target_provider GOOGLE
    }
  }
}

test validate_ssml {
  functions [ValidateSSML]
  args {
    ssml_content "<speak version=\"1.1\"><prosody rate=\"medium\">Hello world</prosody></speak>"
    target_providers [GOOGLE, AMAZON_POLLY, AZURE]
  }
}
