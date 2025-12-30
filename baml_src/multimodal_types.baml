// Multi-Modal Type System
// Core type definitions for multi-modal LUI responses (voice, text, visual)
// Issue #35 - Phase 1: Core Infrastructure

// ============================================
// Modality Types
// ============================================

/// Primary modality for response delivery
enum Modality {
  TEXT @description("Text-based response for display")
  VOICE @description("Voice/audio response for TTS")
  VISUAL @description("Visual elements like charts, cards, images")
  HYBRID @description("Combination of multiple modalities")
}

// ============================================
// Visual Element Types (Multi-Modal)
// ============================================

/// Types of visual elements for multi-modal responses
/// Note: This extends the existing VisualElementType in response_generation.baml
/// with additional types specific to multi-modal interactions
enum MultiModalVisualType {
  TEXT_BLOCK @description("Formatted text block with styling")
  IMAGE @description("Image or graphic content")
  TABLE @description("Tabular data display")
  CHART @description("Data visualization (bar, line, pie, etc.)")
  CARD @description("Information card with structured content")
  BUTTON_GROUP @description("Group of interactive buttons")
  INPUT_FORM @description("Form elements for user input")
  CODE_BLOCK @description("Syntax-highlighted code snippet")
  LIST @description("Ordered or unordered list")
  MEDIA_PLAYER @description("Audio or video player component")
  MAP @description("Geographic map display")
  TIMELINE @description("Chronological event display")
  PROGRESS @description("Progress indicator or loading state")
  AVATAR @description("User or system avatar image")
  BADGE @description("Status indicator or notification badge")
}

/// A visual element in a multi-modal response
class MultiModalVisualElement {
  element_type MultiModalVisualType @description("Type of visual element")
  content string @description("The content to display or render")
  alt_text string? @description("Accessible text description for screen readers")
  title string? @description("Optional title or caption")
  priority int @description("Display priority (1=highest)")
  interactive bool @description("Whether element accepts user interaction")
  metadata map<string, string>? @description("Additional element-specific metadata")
  dimensions Dimensions? @description("Suggested width/height for rendering")
  style_hints StyleHints? @description("Visual styling hints")
}

/// Dimensions for visual element sizing
class Dimensions {
  width string? @description("Width (e.g., '100%', '300px', 'auto')")
  height string? @description("Height (e.g., 'auto', '200px')")
  aspect_ratio string? @description("Aspect ratio (e.g., '16:9', '1:1')")
  min_width string? @description("Minimum width constraint")
  max_width string? @description("Maximum width constraint")
}

/// Style hints for rendering visual elements
class StyleHints {
  theme string? @description("Theme variant (e.g., 'light', 'dark', 'high-contrast')")
  color_scheme string? @description("Color scheme identifier")
  emphasis string? @description("Emphasis level: 'normal', 'subtle', 'strong')")
  animation string? @description("Animation type: 'none', 'fade', 'slide'")
  border_style string? @description("Border styling hint")
}

// ============================================
// Voice Response Types
// ============================================

/// A voice/audio response for TTS rendering
class VoiceResponse {
  text string @description("Plain text content for TTS")
  ssml string? @description("SSML-formatted speech markup")
  voice_config VoiceConfig? @description("Voice configuration settings")
  audio_hints AudioHints? @description("Hints for audio rendering")
  fallback_text string? @description("Fallback text if TTS unavailable")
  language string @description("Language code (e.g., 'en-US', 'es-ES')")
  segments VoiceSegment[]? @description("Segmented voice content for complex responses")
}

/// Configuration for text-to-speech voice
class VoiceConfig {
  voice_id string? @description("Specific voice identifier")
  gender VoiceGender? @description("Preferred voice gender")
  age_group VoiceAgeGroup? @description("Preferred age group for voice")
  speaking_rate float? @description("Speech rate multiplier (0.5-2.0, default 1.0)")
  pitch float? @description("Voice pitch adjustment (-20 to +20 semitones)")
  volume float? @description("Volume level (0.0-1.0, default 1.0)")
  style VoiceSpeakingStyle? @description("Speaking style/emotion")
}

/// Voice gender options
enum VoiceGender {
  MALE @description("Male voice")
  FEMALE @description("Female voice")
  NEUTRAL @description("Gender-neutral voice")
}

/// Voice age group options
enum VoiceAgeGroup {
  CHILD @description("Child voice")
  YOUNG_ADULT @description("Young adult voice")
  ADULT @description("Adult voice")
  SENIOR @description("Senior voice")
}

/// Speaking style for emotional delivery
enum VoiceSpeakingStyle {
  NEUTRAL @description("Neutral, default speaking style")
  CHEERFUL @description("Happy, upbeat tone")
  EMPATHETIC @description("Warm, understanding tone")
  PROFESSIONAL @description("Formal, business-like tone")
  CALM @description("Soothing, relaxed tone")
  URGENT @description("Conveying urgency or importance")
  FRIENDLY @description("Casual, approachable tone")
  EXCITED @description("Enthusiastic, energetic tone")
}

/// Hints for audio rendering
class AudioHints {
  prefer_streaming bool @description("Stream audio for long responses")
  cache_audio bool @description("Cache generated audio for replay")
  background_audio string? @description("Background audio/music identifier")
  sound_effects SoundEffect[]? @description("Sound effects to include")
}

/// A sound effect cue
class SoundEffect {
  effect_id string @description("Sound effect identifier")
  timing SoundTiming @description("When to play the effect")
  volume float @description("Effect volume (0.0-1.0)")
}

/// Timing for sound effects
enum SoundTiming {
  START @description("Play at response start")
  END @description("Play at response end")
  ON_SUCCESS @description("Play on successful action")
  ON_ERROR @description("Play on error")
  ON_ATTENTION @description("Play to get attention")
}

/// A segment of voice content for complex responses
class VoiceSegment {
  text string @description("Segment text content")
  ssml string? @description("SSML markup for this segment")
  pause_before_ms int? @description("Pause before segment in milliseconds")
  pause_after_ms int? @description("Pause after segment in milliseconds")
  emphasis EmphasisLevel? @description("Emphasis level for this segment")
}

/// Emphasis levels for voice segments
enum EmphasisLevel {
  NONE @description("No special emphasis")
  REDUCED @description("De-emphasized, softer")
  MODERATE @description("Moderate emphasis")
  STRONG @description("Strong emphasis")
}

// ============================================
// Text Response Types
// ============================================

/// A text response with formatting support
class TextResponse {
  content string @description("Plain text content")
  formatted_content string? @description("Markdown or rich text content")
  format TextFormat @description("Text format type")
  truncation TruncationStrategy? @description("How to handle long content")
  highlights TextHighlight[]? @description("Sections to highlight")
  annotations TextAnnotation[]? @description("Inline annotations")
}

/// Text format types
enum TextFormat {
  PLAIN @description("Plain text, no formatting")
  MARKDOWN @description("Markdown formatted text")
  HTML @description("HTML formatted text")
  RICH_TEXT @description("Rich text with inline styles")
}

/// Strategy for truncating long text
class TruncationStrategy {
  max_length int @description("Maximum character length")
  truncation_type TruncationType @description("How to truncate")
  show_more_label string? @description("Label for 'show more' action")
}

/// Types of text truncation
enum TruncationType {
  ELLIPSIS @description("End with '...'")
  FADE @description("Visual fade at end")
  COLLAPSE @description("Collapsible with expand option")
  SCROLL @description("Scrollable container")
}

/// A highlighted section of text
class TextHighlight {
  start_offset int @description("Character offset for highlight start")
  end_offset int @description("Character offset for highlight end")
  highlight_type HighlightType @description("Type of highlight")
  label string? @description("Optional label for the highlight")
}

/// Types of text highlighting
enum HighlightType {
  IMPORTANT @description("Important information")
  WARNING @description("Warning or caution")
  SUCCESS @description("Positive/success information")
  ERROR @description("Error or problem")
  INFO @description("Informational highlight")
  CODE @description("Code or technical term")
  LINK @description("Clickable link")
}

/// An annotation on text content
class TextAnnotation {
  position int @description("Character position for annotation")
  annotation_type AnnotationType @description("Type of annotation")
  content string @description("Annotation content")
  tooltip string? @description("Tooltip text on hover")
}

/// Types of text annotations
enum AnnotationType {
  FOOTNOTE @description("Footnote reference")
  TOOLTIP @description("Hover tooltip")
  DEFINITION @description("Term definition")
  CITATION @description("Source citation")
  COMMENT @description("Inline comment")
}

// ============================================
// Multi-Modal Response (Main Type)
// ============================================

/// A complete multi-modal response combining text, voice, and visual elements
class MultiModalResponse {
  response_id string @description("Unique response identifier")
  primary_modality Modality @description("Primary delivery modality")
  text TextResponse? @description("Text component of response")
  voice VoiceResponse? @description("Voice/audio component of response")
  visuals MultiModalVisualElement[]? @description("Visual elements in response")
  actions MultiModalAction[]? @description("Available user actions")
  accessibility AccessibilityMeta @description("Accessibility metadata")
  timing ResponseTiming? @description("Timing and sequencing information")
  context_hints ContextHints? @description("Hints for context preservation")
}

/// Timing information for response delivery
class ResponseTiming {
  duration_hint_ms int? @description("Expected duration in milliseconds")
  sequence ResponseSequence? @description("Sequencing for multi-part responses")
  auto_dismiss_ms int? @description("Auto-dismiss after milliseconds (notifications)")
  delay_ms int? @description("Delay before showing response")
}

/// Sequencing for multi-part responses
class ResponseSequence {
  total_parts int @description("Total parts in sequence")
  current_part int @description("Current part number (1-indexed)")
  has_more bool @description("Whether more parts follow")
  continuation_hint string? @description("Hint for next part")
}

/// Context hints for maintaining conversation state
class ContextHints {
  preserve_context bool @description("Whether to preserve in context window")
  context_key string? @description("Key for context storage")
  expires_at string? @description("ISO timestamp for context expiry")
  related_responses string[]? @description("IDs of related responses")
}

// ============================================
// Action Types
// ============================================

/// An action available to the user in multi-modal responses
class MultiModalAction {
  action_id string @description("Unique action identifier")
  interaction_type InteractionType @description("Type of user interaction")
  label string @description("Display label for action")
  description string? @description("Longer description of action")
  icon string? @description("Icon identifier")
  keyboard_shortcut string? @description("Keyboard shortcut (e.g., 'Ctrl+S')")
  is_primary bool @description("Whether this is the primary/recommended action")
  is_destructive bool @description("Whether action is destructive/irreversible")
  requires_confirmation bool @description("Whether confirmation is needed")
  disabled bool @description("Whether action is currently disabled")
  disabled_reason string? @description("Reason action is disabled")
  payload map<string, string>? @description("Action payload/parameters")
}

/// Types of user interactions for multi-modal responses
/// Note: Distinct from ActionType in gui_converter.baml which covers CRUD operations
enum InteractionType {
  BUTTON @description("Clickable button action")
  LINK @description("Navigation link")
  VOICE_COMMAND @description("Voice-activated command")
  GESTURE @description("Touch/gesture action")
  KEYBOARD @description("Keyboard shortcut action")
  CONTEXTUAL @description("Context menu action")
  FORM_SUBMIT @description("Form submission action")
  DISMISS @description("Dismiss/close action")
  UNDO @description("Undo previous action")
  REDO @description("Redo undone action")
  EXPAND @description("Expand/show more")
  COLLAPSE @description("Collapse/show less")
  SHARE @description("Share content")
  COPY @description("Copy to clipboard")
  DOWNLOAD @description("Download content")
  PRINT @description("Print content")
}

// ============================================
// Accessibility Types
// ============================================

/// Accessibility metadata for multi-modal responses
class AccessibilityMeta {
  aria_label string? @description("ARIA label for screen readers")
  aria_live AriaLiveType @description("ARIA live region type")
  reading_level ReadingLevel? @description("Content reading level")
  cognitive_load CognitiveLoad @description("Cognitive complexity rating")
  supports_screen_reader bool @description("Optimized for screen readers")
  supports_keyboard_nav bool @description("Supports full keyboard navigation")
  high_contrast_available bool @description("Has high contrast mode")
  reduced_motion_safe bool @description("Safe for reduced motion preference")
  text_alternatives TextAlternatives? @description("Alternative text representations")
  focus_hints FocusHints? @description("Focus management hints")
}

/// ARIA live region announcement types
enum AriaLiveType {
  OFF @description("No live announcements")
  POLITE @description("Announced when user is idle")
  ASSERTIVE @description("Announced immediately, interrupts")
}

/// Content reading level assessment
enum ReadingLevel {
  ELEMENTARY @description("Elementary school level (grades 1-5)")
  MIDDLE_SCHOOL @description("Middle school level (grades 6-8)")
  HIGH_SCHOOL @description("High school level (grades 9-12)")
  COLLEGE @description("College/university level")
  PROFESSIONAL @description("Professional/technical level")
}

/// Cognitive load rating
enum CognitiveLoad {
  MINIMAL @description("Very simple, minimal cognitive effort")
  LOW @description("Low cognitive load, easy to process")
  MODERATE @description("Moderate complexity")
  HIGH @description("High cognitive load, requires focus")
  VERY_HIGH @description("Very complex, may need multiple readings")
}

/// Alternative text representations for accessibility
class TextAlternatives {
  simple_text string? @description("Simplified text version")
  verbose_text string? @description("More detailed text version")
  audio_description string? @description("Description for audio-only users")
  braille_text string? @description("Braille-optimized text")
}

/// Focus management hints
class FocusHints {
  initial_focus string? @description("Element ID for initial focus")
  focus_trap bool @description("Whether to trap focus in component")
  return_focus string? @description("Element to return focus to on close")
  skip_link string? @description("Skip link target for keyboard nav")
}

// ============================================
// Utility Functions
// ============================================

/// Create a simple text-only multi-modal response
function CreateTextResponse(
  text: string,
  reading_level: ReadingLevel?
) -> MultiModalResponse {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Create a simple text-only multi-modal response.

    ## Input
    - Text: {{ text }}
    - Reading Level: {{ reading_level }}

    ## Requirements
    1. Set primary_modality to TEXT
    2. Create appropriate text response with formatting
    3. Set accessibility metadata appropriately
    4. Reading level should influence content complexity

    {{ ctx.output_format }}
  "#
}

/// Create a voice-first multi-modal response
function CreateVoiceResponse(
  text: string,
  voice_style: VoiceSpeakingStyle?,
  language: string
) -> MultiModalResponse {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Create a voice-first multi-modal response optimized for TTS.

    ## Input
    - Text: {{ text }}
    - Voice Style: {{ voice_style }}
    - Language: {{ language }}

    ## Requirements
    1. Set primary_modality to VOICE
    2. Create voice response with appropriate SSML markup
    3. Include text fallback
    4. Configure voice settings based on style
    5. Set accessibility for audio-first experience

    {{ ctx.output_format }}
  "#
}

/// Create a visual-rich multi-modal response
function CreateVisualResponse(
  content: string,
  visual_type: MultiModalVisualType,
  include_voice_description: bool
) -> MultiModalResponse {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Create a visual-rich multi-modal response.

    ## Input
    - Content: {{ content }}
    - Visual Type: {{ visual_type }}
    - Include Voice Description: {{ include_voice_description }}

    ## Requirements
    1. Set primary_modality to VISUAL
    2. Create appropriate visual element
    3. Include alt text for accessibility
    4. If include_voice_description, add voice component describing the visual
    5. Set accessibility metadata for visual content

    {{ ctx.output_format }}
  "#
}

/// Create a hybrid multi-modal response
function CreateHybridResponse(
  text: string,
  visuals: MultiModalVisualElement[],
  include_voice: bool,
  voice_style: VoiceSpeakingStyle?
) -> MultiModalResponse {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Create a hybrid multi-modal response combining multiple modalities.

    ## Input
    - Text: {{ text }}
    - Visuals: {{ visuals }}
    - Include Voice: {{ include_voice }}
    - Voice Style: {{ voice_style }}

    ## Requirements
    1. Set primary_modality to HYBRID
    2. Create coordinated text, voice (if included), and visual components
    3. Ensure all modalities convey consistent information
    4. Set comprehensive accessibility metadata
    5. Include appropriate actions

    {{ ctx.output_format }}
  "#
}

// ============================================
// Test Cases
// ============================================

test create_text_response {
  functions [CreateTextResponse]
  args {
    text "Your order #12345 has been confirmed and will arrive by Friday."
    reading_level MIDDLE_SCHOOL
  }
}

test create_voice_response {
  functions [CreateVoiceResponse]
  args {
    text "Good morning! You have 3 meetings scheduled for today. Would you like me to read them out?"
    voice_style FRIENDLY
    language "en-US"
  }
}

test create_visual_response {
  functions [CreateVisualResponse]
  args {
    content "Monthly sales data: January $50K, February $65K, March $72K, April $68K"
    visual_type CHART
    include_voice_description true
  }
}

test create_hybrid_response {
  functions [CreateHybridResponse]
  args {
    text "Here's a summary of your fitness activity this week."
    visuals []
    include_voice true
    voice_style CHEERFUL
  }
}
