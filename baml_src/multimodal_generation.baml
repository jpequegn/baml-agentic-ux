// Multi-Modal Response Generation
// Main BAML function for generating multi-modal responses
// Issue #40 - Phase 1: Multi-Modal LUI Support

// Note: Uses existing types from response_generation.baml:
// - ResponseTone (PROFESSIONAL, FRIENDLY, EMPATHETIC, ENTHUSIASTIC, CALM, DIRECT, PLAYFUL)
// - FormalityLevel (VERY_FORMAL, FORMAL, NEUTRAL, CASUAL, VERY_CASUAL)

// ============================================
// Response Persona Types
// ============================================

/// Response persona configuration for multi-modal generation
class ResponsePersona {
  name string @description("Persona name for identification")
  description string? @description("Description of this persona")
  tone ResponseTone @description("Communication tone")
  formality FormalityLevel @description("Level of formality")
  personality PersonalityConfig? @description("Personality traits")
  brand_guidelines BrandGuidelines? @description("Brand-specific guidelines")
  language_preferences LanguagePreferences? @description("Language and localization preferences")
}

/// Personality configuration for response generation
class PersonalityConfig {
  is_humorous bool @description("Include appropriate humor")
  is_encouraging bool @description("Add encouraging remarks")
  is_concise bool @description("Prefer brevity")
  uses_analogies bool @description("Use analogies for explanation")
  is_proactive bool @description("Anticipate user needs")
  empathy_level EmpathyLevel? @description("Level of emotional responsiveness")
}

/// Empathy levels for response generation
enum EmpathyLevel {
  LOW @description("Minimal emotional acknowledgment")
  MODERATE @description("Balanced emotional response")
  HIGH @description("Strong emotional attunement")
}

/// Brand-specific guidelines for response generation
class BrandGuidelines {
  brand_name string @description("Brand name")
  voice_description string @description("Description of brand voice")
  key_phrases string[]? @description("Signature phrases to use")
  avoided_phrases string[]? @description("Phrases to avoid")
  emoji_usage EmojiUsage @description("How to use emojis")
  signature_elements string[]? @description("Unique brand elements")
}

/// Emoji usage preferences
enum EmojiUsage {
  NONE @description("Never use emojis")
  MINIMAL @description("Occasional, subtle use")
  MODERATE @description("Regular, balanced use")
  EXPRESSIVE @description("Frequent, expressive use")
}

/// Language and localization preferences
class LanguagePreferences {
  primary_language string @description("Primary language code (e.g., 'en-US')")
  reading_level ReadingLevel? @description("Target reading level")
  use_contractions bool? @description("Use contractions in text")
  date_format string? @description("Preferred date format")
  number_format string? @description("Preferred number format")
  currency_symbol string? @description("Preferred currency symbol")
}

// ============================================
// Generation Context Types
// ============================================

/// Context for multi-modal response generation
class GenerationContext {
  session_id string? @description("Session identifier for continuity")
  turn_count int? @description("Number of turns in conversation")
  last_response_modality Modality? @description("Modality of last response")
  user_feedback_history UserFeedbackSummary? @description("Summary of user feedback")
  performance_hints PerformanceHints? @description("Performance optimization hints")
}

/// Summary of user feedback for adaptation
class UserFeedbackSummary {
  preferred_length ResponseLength? @description("Preferred response length")
  preferred_detail DetailLevel? @description("Preferred level of detail")
  positive_reactions string[]? @description("Types of responses user liked")
  negative_reactions string[]? @description("Types of responses user disliked")
}

/// Preferred response length
enum ResponseLength {
  VERY_SHORT @description("Minimal, essential information only")
  SHORT @description("Brief, concise responses")
  MEDIUM @description("Balanced detail")
  LONG @description("Comprehensive responses")
  DETAILED @description("Full explanations with examples")
}

/// Level of detail in responses
enum DetailLevel {
  OVERVIEW @description("High-level summary only")
  STANDARD @description("Normal level of detail")
  COMPREHENSIVE @description("Thorough coverage")
  EXHAUSTIVE @description("Complete detail with edge cases")
}

/// Performance optimization hints
class PerformanceHints {
  max_response_time_ms int? @description("Target max response time")
  bandwidth_constraint BandwidthConstraint? @description("Network bandwidth limitations")
  prefer_cached bool? @description("Prefer cached responses")
}

/// Bandwidth constraints for response optimization
enum BandwidthConstraint {
  NONE @description("No bandwidth constraints")
  LOW @description("Limited bandwidth, minimize data")
  VERY_LOW @description("Very limited, essential only")
}

// ============================================
// Generation Result Types
// ============================================

/// Result of multi-modal response generation
class GenerationResult {
  response MultiModalResponse @description("The generated multi-modal response")
  generation_metadata GenerationMetadata @description("Metadata about generation")
  quality_metrics QualityMetrics? @description("Quality assessment metrics")
  alternatives AlternativeResponse[]? @description("Alternative response options")
}

/// Metadata about the generation process
class GenerationMetadata {
  generation_time_ms int @description("Time taken to generate response")
  modality_selection_rationale string @description("Why this modality was chosen")
  persona_applied string @description("Persona name that was applied")
  accessibility_adaptations string[]? @description("Accessibility adaptations made")
  content_warnings string[]? @description("Any content warnings")
}

/// Quality metrics for generated response
class QualityMetrics {
  clarity_score float @description("Clarity of the response (0-1)")
  relevance_score float @description("Relevance to the intent (0-1)")
  completeness_score float @description("Completeness of information (0-1)")
  accessibility_score float @description("Accessibility compliance (0-1)")
  brand_alignment_score float? @description("Alignment with brand guidelines (0-1)")
}

/// Alternative response option
class AlternativeResponse {
  response MultiModalResponse @description("Alternative response")
  rationale string @description("Why this is a good alternative")
  use_case string @description("When to prefer this alternative")
}

// ============================================
// Quick Reply Types
// ============================================

/// Quick reply suggestion for user
class QuickReply {
  id string @description("Unique identifier")
  label string @description("Display text")
  value string @description("Value sent when selected")
  icon string? @description("Optional icon identifier")
  is_primary bool @description("Whether this is the primary suggestion")
}

/// Collection of quick replies with metadata
class QuickReplySet {
  replies QuickReply[] @description("List of quick replies")
  max_visible int? @description("Maximum to show initially")
  layout QuickReplyLayout @description("How to display replies")
}

/// Layout for quick replies
enum QuickReplyLayout {
  HORIZONTAL @description("Horizontal row of buttons")
  VERTICAL @description("Vertical list")
  GRID @description("Grid layout")
  CHIPS @description("Chip/pill style")
}

// ============================================
// Main Generation Functions
// ============================================

/// Generate a complete multi-modal response
function GenerateMultiModalResponse(
  intent: IntentExtraction,
  action_result: ActionResult?,
  conversation_context: ConversationContext,
  modality_context: ModalityContext,
  persona: ResponsePersona?,
  generation_context: GenerationContext?,
  user_accessibility_needs: AccessibilityNeed[]?
) -> MultiModalResponse {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Generate a multi-modal response for this interaction.

    ## Intent
    - Detected Intent: {{ intent.detected_intent }}
    - Confidence: {{ intent.confidence }}
    {% if intent.extracted_parameters %}
    - Parameters: {{ intent.extracted_parameters }}
    {% endif %}
    {% if intent.suggested_clarification %}
    - Needs Clarification: {{ intent.suggested_clarification }}
    {% endif %}

    {% if action_result %}
    ## Action Result
    - Status: {{ action_result.status }}
    {% if action_result.data %}
    - Data: {{ action_result.data }}
    {% endif %}
    {% if action_result.error_message %}
    - Error: {{ action_result.error_message }}
    {% endif %}
    {% if action_result.affected_entities %}
    - Affected: {{ action_result.affected_entities }}
    {% endif %}
    {% endif %}

    ## Conversation Context
    {% if conversation_context.recent_messages %}
    - Recent Messages: {{ conversation_context.recent_messages }}
    {% endif %}
    {% if conversation_context.current_state %}
    - Current State: {{ conversation_context.current_state }}
    {% endif %}
    {% if conversation_context.active_entity %}
    - Active Entity: {{ conversation_context.active_entity }}
    {% endif %}

    ## Modality Context
    - Available Modalities: {{ modality_context.available_modalities }}
    - Device:
      - Screen: {{ modality_context.device_capabilities.has_screen }} (Size: {{ modality_context.device_capabilities.screen_size }})
      - Speaker: {{ modality_context.device_capabilities.has_speaker }}
      - Microphone: {{ modality_context.device_capabilities.has_microphone }}
      - Keyboard: {{ modality_context.device_capabilities.has_keyboard }}
    - Content Type: {{ modality_context.content_type }}
    - Message Length: {{ modality_context.message_length }}
    - Priority: {{ modality_context.priority }}
    {% if modality_context.environment_context %}
    - Environment:
      - Noise: {{ modality_context.environment_context.noise_level }}
      - Privacy: {{ modality_context.environment_context.privacy_level }}
      - Mobile: {{ modality_context.environment_context.mobility }}
      - Hands-Free: {{ modality_context.environment_context.hands_free_required }}
      - Eyes-Free: {{ modality_context.environment_context.eyes_free_required }}
    {% endif %}
    {% if modality_context.user_preference %}
    - User Preference: {{ modality_context.user_preference }}
    {% endif %}

    {% if persona %}
    ## Response Persona
    - Name: {{ persona.name }}
    - Tone: {{ persona.tone }}
    - Formality: {{ persona.formality }}
    {% if persona.personality %}
    - Personality:
      - Humorous: {{ persona.personality.is_humorous }}
      - Encouraging: {{ persona.personality.is_encouraging }}
      - Concise: {{ persona.personality.is_concise }}
      - Uses Analogies: {{ persona.personality.uses_analogies }}
      - Proactive: {{ persona.personality.is_proactive }}
    {% endif %}
    {% if persona.brand_guidelines %}
    - Brand: {{ persona.brand_guidelines.brand_name }}
    - Voice: {{ persona.brand_guidelines.voice_description }}
    {% if persona.brand_guidelines.key_phrases %}
    - Use phrases: {{ persona.brand_guidelines.key_phrases }}
    {% endif %}
    {% if persona.brand_guidelines.avoided_phrases %}
    - Avoid phrases: {{ persona.brand_guidelines.avoided_phrases }}
    {% endif %}
    - Emoji usage: {{ persona.brand_guidelines.emoji_usage }}
    {% endif %}
    {% if persona.language_preferences %}
    - Language: {{ persona.language_preferences.primary_language }}
    {% if persona.language_preferences.reading_level %}
    - Reading Level: {{ persona.language_preferences.reading_level }}
    {% endif %}
    {% endif %}
    {% endif %}

    {% if generation_context %}
    ## Generation Context
    {% if generation_context.turn_count %}
    - Turn Count: {{ generation_context.turn_count }}
    {% endif %}
    {% if generation_context.last_response_modality %}
    - Last Modality: {{ generation_context.last_response_modality }}
    {% endif %}
    {% if generation_context.user_feedback_history %}
    - Preferred Length: {{ generation_context.user_feedback_history.preferred_length }}
    - Preferred Detail: {{ generation_context.user_feedback_history.preferred_detail }}
    {% endif %}
    {% endif %}

    {% if user_accessibility_needs %}
    ## Accessibility Needs
    {{ user_accessibility_needs }}
    {% endif %}

    ## Generation Guidelines

    ### Primary Modality Selection
    Choose primary modality based on:
    1. **Accessibility needs OVERRIDE all other factors**
       - VISUAL impairment: Use VOICE, avoid visual-only
       - AUDITORY impairment: Use TEXT/VISUAL, avoid audio-only
       - MOTOR impairment: Prefer VOICE input
       - COGNITIVE: Simpler, shorter responses

    2. **Content-Modality Match**
       | Content Type    | Best Modality | Rationale |
       |-----------------|---------------|-----------|
       | CONFIRMATION    | VOICE         | Quick, non-intrusive |
       | ERROR           | TEXT + VISUAL | Persistent, actionable |
       | DATA_TABLE      | VISUAL        | Spatial comparison |
       | LONG_TEXT       | TEXT          | Skimmable, searchable |
       | SHORT_RESPONSE  | VOICE or TEXT | User preference |
       | LIST            | VISUAL        | Easy scanning |

    3. **Environmental factors**
       - Loud → Avoid VOICE
       - Public → Avoid audio output
       - Mobile → Prefer VOICE
       - Eyes-free → Must use VOICE
       - Hands-free → Must use VOICE

    ### Text Response Guidelines
    - Clear, concise language
    - Match reading level to user (if specified)
    - Include 2-4 quick reply suggestions when appropriate
    - Use markdown formatting for structured content
    - Keep paragraphs short for mobile readability

    ### Voice Response Guidelines
    - Conversational, natural tone
    - Use SSML for emphasis, pauses, pronunciation
    - Keep under 30 seconds of speech (~75 words)
    - Always provide plain_text fallback
    - Use appropriate prosody for emotion/emphasis
    - Structure: greeting → main content → call to action

    ### Visual Element Guidelines
    - Use when comparing data or showing structure
    - Always include alt_text for accessibility
    - Provide fallback_text for screen readers
    - Limit interactive elements to 3-4 maximum
    - Use appropriate visual types:
      - CARD for structured info
      - TABLE for comparisons
      - LIST for sequences
      - BUTTON_GROUP for actions

    ### Accessibility Requirements
    - Set aria_live appropriately (POLITE for updates, ASSERTIVE for errors)
    - Include role attributes for screen readers
    - Match cognitive_load to user needs
    - Ensure high contrast support
    - Support keyboard navigation
    - Provide text alternatives for all visuals

    ### Action Limits
    - Maximum 4 primary actions
    - Always have one clear primary action
    - Mark destructive actions appropriately
    - Include keyboard shortcuts where applicable

    ## Response Structure
    Generate a response with:
    1. Unique response_id (format: "resp_" + context)
    2. Appropriate primary_modality
    3. Text response (always include for fallback)
    4. Voice response (if voice is available)
    5. Visual elements (if visual is available and appropriate)
    6. Actions (limited to 3-4 max)
    7. Complete accessibility metadata

    {{ ctx.output_format }}
  "#
}

/// Generate a multi-modal response with full generation metadata
function GenerateMultiModalResponseWithMetadata(
  intent: IntentExtraction,
  action_result: ActionResult?,
  conversation_context: ConversationContext,
  modality_context: ModalityContext,
  persona: ResponsePersona?,
  generation_context: GenerationContext?,
  user_accessibility_needs: AccessibilityNeed[]?
) -> GenerationResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Generate a complete multi-modal response with quality metrics.

    ## Input Context
    - Intent: {{ intent.detected_intent }} (confidence: {{ intent.confidence }})
    {% if action_result %}
    - Action Result: {{ action_result.status }}
    {% endif %}
    - Available Modalities: {{ modality_context.available_modalities }}
    - Content Type: {{ modality_context.content_type }}
    {% if persona %}
    - Persona: {{ persona.name }} ({{ persona.tone }}, {{ persona.formality }})
    {% endif %}
    {% if user_accessibility_needs %}
    - Accessibility Needs: {{ user_accessibility_needs }}
    {% endif %}

    ## Task
    1. Generate an appropriate multi-modal response
    2. Provide metadata about the generation
    3. Calculate quality metrics
    4. Optionally provide alternatives

    ## Guidelines
    - Follow the same guidelines as GenerateMultiModalResponse
    - Assess quality across clarity, relevance, completeness, accessibility
    - Explain modality selection rationale
    - Note any accessibility adaptations made
    - Provide alternatives if the primary response has limitations

    {{ ctx.output_format }}
  "#
}

/// Generate quick reply suggestions for a response
function GenerateQuickReplies(
  response_context: string,
  intent: IntentExtraction,
  max_replies: int?,
  include_navigation: bool?
) -> QuickReplySet {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Generate quick reply suggestions for a multi-modal response.

    ## Context
    {{ response_context }}

    ## Intent
    - Detected: {{ intent.detected_intent }}
    - Confidence: {{ intent.confidence }}
    {% if intent.extracted_parameters %}
    - Parameters: {{ intent.extracted_parameters }}
    {% endif %}

    ## Requirements
    - Maximum replies: {{ max_replies | default(4) }}
    - Include navigation: {{ include_navigation | default(false) }}

    ## Guidelines
    - Suggestions should be logical next steps
    - Keep labels short (2-4 words)
    - Make one suggestion primary
    - Include undo/cancel if action was taken
    - Match user's apparent expertise level
    {% if include_navigation %}
    - Include navigation options (back, home, help)
    {% endif %}

    {{ ctx.output_format }}
  "#
}

/// Adapt a response to a different modality
function AdaptResponseToModality(
  original_response: MultiModalResponse,
  target_modality: Modality,
  preserve_priority: PreservePriority?
) -> MultiModalResponse {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Adapt this multi-modal response to a different target modality.

    ## Original Response
    - ID: {{ original_response.response_id }}
    - Primary Modality: {{ original_response.primary_modality }}
    {% if original_response.text %}
    - Text: {{ original_response.text.content }}
    {% endif %}
    {% if original_response.voice %}
    - Voice: {{ original_response.voice.text }}
    {% endif %}
    {% if original_response.visuals %}
    - Visuals: {{ original_response.visuals | length }} elements
    {% endif %}

    ## Target Modality
    {{ target_modality }}

    {% if preserve_priority %}
    ## Preservation Priority
    - Critical: {{ preserve_priority.critical_elements }}
    - Important: {{ preserve_priority.important_elements }}
    - Optional: {{ preserve_priority.optional_elements }}
    - Acceptable Loss: {{ preserve_priority.acceptable_loss }}
    {% endif %}

    ## Guidelines
    1. Preserve all critical information
    2. Adapt format to target modality strengths
    3. Maintain accessibility
    4. Update response_id with suffix "_adapted"

    ### Modality-Specific Adaptations
    - To TEXT: Convert voice to readable text, describe visuals
    - To VOICE: Make text conversational, describe visuals verbally
    - To VISUAL: Structure text as cards/lists, add visual hierarchy
    - To HYBRID: Combine complementary modalities

    {{ ctx.output_format }}
  "#
}

/// Validate a generated multi-modal response
function ValidateMultiModalResponse(
  response: MultiModalResponse,
  modality_context: ModalityContext,
  user_accessibility_needs: AccessibilityNeed[]?
) -> ResponseValidation {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Validate this multi-modal response for quality and compliance.

    ## Response
    - ID: {{ response.response_id }}
    - Primary Modality: {{ response.primary_modality }}
    {% if response.text %}
    - Has Text: Yes ({{ response.text.content | length }} chars)
    {% endif %}
    {% if response.voice %}
    - Has Voice: Yes
    {% endif %}
    {% if response.visuals %}
    - Has Visuals: Yes ({{ response.visuals | length }} elements)
    {% endif %}
    {% if response.actions %}
    - Has Actions: Yes ({{ response.actions | length }} actions)
    {% endif %}
    - Accessibility: aria_live={{ response.accessibility.aria_live }}, cognitive_load={{ response.accessibility.cognitive_load }}

    ## Context
    - Available: {{ modality_context.available_modalities }}
    - Device: Screen={{ modality_context.device_capabilities.has_screen }}, Speaker={{ modality_context.device_capabilities.has_speaker }}

    {% if user_accessibility_needs %}
    ## Accessibility Needs
    {{ user_accessibility_needs }}
    {% endif %}

    ## Validation Checks
    1. Is primary modality available on device?
    2. Does response have required components for primary modality?
    3. Are accessibility requirements met?
    4. Is action count within limits (≤4)?
    5. Is voice response under 30 seconds (~75 words)?
    6. Do all visuals have alt_text?
    7. Is SSML valid (if present)?
    8. Is cognitive load appropriate for user?

    {{ ctx.output_format }}
  "#
}

/// Response validation result
class ResponseValidation {
  is_valid bool @description("Whether response passes all checks")
  is_optimal bool @description("Whether response is optimal for context")
  issues ValidationIssue[] @description("List of validation issues")
  suggestions string[]? @description("Improvement suggestions")
  accessibility_compliant bool @description("Meets accessibility requirements")
  estimated_voice_duration_seconds float? @description("Estimated voice duration")
}

/// A validation issue found in the response
class ValidationIssue {
  severity ValidationSeverity @description("Severity of the issue")
  category string @description("Category of the issue")
  message string @description("Description of the issue")
  field string? @description("Field with the issue")
  recommendation string? @description("How to fix")
}

// Note: ValidationSeverity is defined in entity_definitions.baml (ERROR, WARNING, INFO)

// ============================================
// Test Cases
// ============================================

test generate_confirmation_response {
  functions [GenerateMultiModalResponse]
  args {
    intent {
      detected_intent CREATE
      confidence 0.95
      extracted_parameters [
        {
          name "task_name"
          value "Review PR #123"
          confidence 0.98
          source EXPLICIT
        }
      ]
      ambiguity null
      suggested_clarification null
      raw_input "Create a task to review PR 123"
      entities_referenced []
      is_compound false
    }
    action_result {
      status SUCCESS
      data "task_id: 456"
      error_message null
      metadata null
      affected_entities ["task_456"]
    }
    conversation_context {
      recent_messages []
      current_state "task_list"
      active_entity null
      user_preferences null
    }
    modality_context {
      available_modalities [TEXT, VOICE, VISUAL]
      user_preference null
      device_capabilities {
        has_screen true
        has_speaker true
        has_microphone true
        has_keyboard true
        screen_size MEDIUM
        supports_touch true
        supports_voice_commands true
        bandwidth_quality "high"
      }
      environment_context {
        noise_level QUIET
        privacy_level PRIVATE
        mobility false
        hands_free_required false
        eyes_free_required false
        time_of_day "morning"
      }
      content_type CONFIRMATION
      message_length SHORT
      priority NORMAL
      previous_modality null
      interaction_count 1
      error_occurred false
    }
    persona {
      name "Helpful Assistant"
      description "A friendly and efficient assistant"
      tone FRIENDLY
      formality CASUAL
      personality {
        is_humorous false
        is_encouraging true
        is_concise true
        uses_analogies false
        is_proactive false
        empathy_level MODERATE
      }
      brand_guidelines null
      language_preferences {
        primary_language "en-US"
        reading_level null
        use_contractions true
        date_format null
        number_format null
        currency_symbol null
      }
    }
    generation_context null
    user_accessibility_needs null
  }
}

test generate_error_response {
  functions [GenerateMultiModalResponse]
  args {
    intent {
      detected_intent READ
      confidence 0.75
      extracted_parameters [
        {
          name "task_name"
          value "meeting notes"
          confidence 0.6
          source INFERRED
        }
      ]
      ambiguity {
        type ENTITY_AMBIGUITY
        options ["Meeting notes - weekly", "Meeting notes - daily", "Meeting notes - project"]
        needs_clarification true
      }
      suggested_clarification "Did you mean one of these tasks?"
      raw_input "Show me the meeting notes task"
      entities_referenced []
      is_compound false
    }
    action_result {
      status NOT_FOUND
      data null
      error_message "No task found with exact name 'meeting notes'"
      metadata null
      affected_entities []
    }
    conversation_context {
      recent_messages []
      current_state "search"
      active_entity null
      user_preferences null
    }
    modality_context {
      available_modalities [TEXT, VISUAL]
      user_preference TEXT
      device_capabilities {
        has_screen true
        has_speaker false
        has_microphone false
        has_keyboard true
        screen_size LARGE
        supports_touch false
        supports_voice_commands false
        bandwidth_quality "high"
      }
      environment_context null
      content_type ERROR
      message_length MEDIUM
      priority HIGH
      previous_modality TEXT
      interaction_count 3
      error_occurred true
    }
    persona null
    generation_context null
    user_accessibility_needs null
  }
}

test generate_data_display_response {
  functions [GenerateMultiModalResponse]
  args {
    intent {
      detected_intent LIST
      confidence 0.92
      extracted_parameters [
        {
          name "filter"
          value "high priority"
          confidence 0.88
          source EXPLICIT
        }
      ]
      ambiguity null
      suggested_clarification null
      raw_input "Show me my high priority tasks"
      entities_referenced []
      is_compound false
    }
    action_result {
      status SUCCESS
      data "[{\"id\":\"1\",\"title\":\"Review PR\",\"priority\":\"high\",\"due\":\"tomorrow\"},{\"id\":\"2\",\"title\":\"Update docs\",\"priority\":\"high\",\"due\":\"next week\"},{\"id\":\"3\",\"title\":\"Fix bug\",\"priority\":\"high\",\"due\":\"today\"}]"
      error_message null
      metadata {
        affected_count 3
        execution_time_ms 150
        warnings null
        additional_info null
      }
      affected_entities ["task_1", "task_2", "task_3"]
    }
    conversation_context {
      recent_messages []
      current_state "task_list"
      active_entity null
      user_preferences null
    }
    modality_context {
      available_modalities [TEXT, VOICE, VISUAL, HYBRID]
      user_preference null
      device_capabilities {
        has_screen true
        has_speaker true
        has_microphone true
        has_keyboard true
        screen_size LARGE
        supports_touch false
        supports_voice_commands true
        bandwidth_quality "high"
      }
      environment_context {
        noise_level MODERATE
        privacy_level SEMI_PRIVATE
        mobility false
        hands_free_required false
        eyes_free_required false
        time_of_day "afternoon"
      }
      content_type DATA_TABLE
      message_length MEDIUM
      priority NORMAL
      previous_modality null
      interaction_count 1
      error_occurred false
    }
    persona null
    generation_context null
    user_accessibility_needs null
  }
}

test generate_accessibility_focused_response {
  functions [GenerateMultiModalResponse]
  args {
    intent {
      detected_intent READ
      confidence 0.9
      extracted_parameters []
      ambiguity null
      suggested_clarification null
      raw_input "What's on my calendar today?"
      entities_referenced []
      is_compound false
    }
    action_result {
      status SUCCESS
      data "2 meetings: Team standup at 10am, Project review at 2pm"
      error_message null
      metadata null
      affected_entities []
    }
    conversation_context {
      recent_messages []
      current_state "calendar"
      active_entity null
      user_preferences null
    }
    modality_context {
      available_modalities [TEXT, VOICE]
      user_preference VOICE
      device_capabilities {
        has_screen true
        has_speaker true
        has_microphone true
        has_keyboard false
        screen_size SMALL
        supports_touch true
        supports_voice_commands true
        bandwidth_quality "medium"
      }
      environment_context {
        noise_level QUIET
        privacy_level PRIVATE
        mobility true
        hands_free_required true
        eyes_free_required false
        time_of_day "morning"
      }
      content_type SHORT_RESPONSE
      message_length SHORT
      priority NORMAL
      previous_modality VOICE
      interaction_count 5
      error_occurred false
    }
    persona null
    generation_context null
    user_accessibility_needs [VISUAL]
  }
}
