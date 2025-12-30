// Modality Selection Logic
// Intelligent modality recommendation based on context, device, content, and preferences
// Issue #38 - Phase 1: Multi-Modal LUI Support

// ============================================
// Device and Environment Types
// ============================================

/// Screen size categories for devices
enum ScreenSize {
  NONE @description("No screen available")
  SMALL @description("Small screen (phone, watch)")
  MEDIUM @description("Medium screen (tablet)")
  LARGE @description("Large screen (desktop, TV)")
}

/// Device capabilities for modality selection
class DeviceCapabilities {
  has_screen bool @description("Device has a display")
  has_speaker bool @description("Device can output audio")
  has_microphone bool @description("Device can receive audio input")
  has_keyboard bool @description("Device has text input capability")
  screen_size ScreenSize? @description("Size of available screen")
  supports_touch bool? @description("Touchscreen capability")
  supports_voice_commands bool? @description("Voice input capability")
  bandwidth_quality string? @description("Network quality: low, medium, high")
}

/// Environmental noise levels
enum NoiseLevel {
  QUIET @description("Very quiet environment (library, bedroom)")
  MODERATE @description("Normal ambient noise (office, home)")
  LOUD @description("High noise environment (street, factory)")
}

/// Privacy levels of the environment
enum PrivacyLevel {
  PRIVATE @description("Alone, no one can hear/see")
  SEMI_PRIVATE @description("Others may be nearby")
  PUBLIC @description("In a public space, visible to others")
}

/// Environmental context for modality selection
class EnvironmentContext {
  noise_level NoiseLevel? @description("Ambient noise level")
  privacy_level PrivacyLevel? @description("Privacy of the environment")
  mobility bool? @description("User is moving/walking")
  hands_free_required bool? @description("User needs hands-free interaction")
  eyes_free_required bool? @description("User needs eyes-free interaction")
  time_of_day string? @description("Time context (morning, evening, night)")
}

// ============================================
// Content Classification Types
// ============================================

/// Types of content being delivered
enum ContentType {
  CONFIRMATION @description("Short yes/no acknowledgment")
  ERROR @description("Error message that needs user attention")
  DATA_TABLE @description("Structured data for comparison")
  LONG_TEXT @description("Detailed explanation or information")
  SHORT_RESPONSE @description("Brief answer or acknowledgment")
  ACTION_REQUIRED @description("User must take specific action")
  DISAMBIGUATION @description("Clarification needed between options")
  LIST @description("List of items or options")
  FORM @description("Form to fill out")
  MEDIA @description("Rich media content (images, videos)")
  NOTIFICATION @description("Alert or notification")
  PROGRESS @description("Status or progress update")
  NAVIGATION @description("Navigation instructions")
}

/// Message length categories
enum MessageLength {
  SHORT @description("Less than 20 words")
  MEDIUM @description("20-100 words")
  LONG @description("More than 100 words")
}

/// Message priority levels for modality selection
enum MessagePriority {
  LOW @description("Can be delivered later")
  NORMAL @description("Standard delivery priority")
  HIGH @description("Needs prompt attention")
  CRITICAL @description("Requires immediate action")
}

// ============================================
// Selection Context
// ============================================

/// Complete context for modality selection
class ModalityContext {
  available_modalities Modality[] @description("Modalities available on this device")
  user_preference Modality? @description("User's preferred modality if known")
  device_capabilities DeviceCapabilities @description("Device hardware capabilities")
  environment_context EnvironmentContext? @description("Environmental factors")
  content_type ContentType @description("Type of content to deliver")
  message_length MessageLength @description("Length of the message")
  priority MessagePriority @description("Priority of this message")
  previous_modality Modality? @description("Modality used in previous turn")
  interaction_count int? @description("Number of turns in conversation")
  error_occurred bool? @description("Whether an error occurred recently")
}

// ============================================
// Recommendation Output
// ============================================

/// Modality recommendation with rationale
class ModalityRecommendation {
  primary Modality @description("Recommended primary modality")
  secondary Modality? @description("Optional secondary modality for hybrid")
  rationale string @description("Explanation for the recommendation")
  confidence float @description("Confidence score 0.0-1.0")
  fallback_chain Modality[] @description("Fallback order if primary unavailable")
  accessibility_adaptations string[]? @description("Accessibility modifications applied")
  warnings string[]? @description("Any warnings or considerations")
}

/// Detailed breakdown of selection factors
class SelectionFactors {
  content_match float @description("How well modality matches content type")
  environment_score float @description("Environmental suitability")
  device_score float @description("Device capability score")
  user_preference_score float @description("Alignment with user preference")
  accessibility_score float @description("Accessibility compliance")
  overall_score float @description("Combined weighted score")
}

/// Complete selection result with detailed analysis
class ModalitySelectionResult {
  recommendation ModalityRecommendation @description("The recommendation")
  factors SelectionFactors @description("Breakdown of selection factors")
  alternatives ModalityRecommendation[]? @description("Alternative options considered")
  decision_path string @description("Explanation of decision logic")
}

// ============================================
// Selection Rules and Weights
// ============================================

/// Weights for different selection factors
class SelectionWeights {
  accessibility float @description("Weight for accessibility needs (highest)")
  content_match float @description("Weight for content-modality match")
  environment float @description("Weight for environmental factors")
  device float @description("Weight for device capabilities")
  user_preference float @description("Weight for user preference")
  continuity float @description("Weight for staying in same modality")
}

/// Default selection weights
class DefaultSelectionWeights {
  accessibility float @description("Default: 1.0 (overrides all)")
  content_match float @description("Default: 0.35")
  environment float @description("Default: 0.25")
  device float @description("Default: 0.20")
  user_preference float @description("Default: 0.15")
  continuity float @description("Default: 0.05")
}

// ============================================
// Selection Function
// ============================================

/// Select the optimal modality based on context
function SelectModality(
  context: ModalityContext,
  user_accessibility_needs: AccessibilityNeed[]?
) -> ModalityRecommendation {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Given the context, recommend the optimal modality for delivering content.

    ## Context
    - Available Modalities: {{ context.available_modalities }}
    - Device Capabilities:
      - Screen: {{ context.device_capabilities.has_screen }} (Size: {{ context.device_capabilities.screen_size }})
      - Speaker: {{ context.device_capabilities.has_speaker }}
      - Microphone: {{ context.device_capabilities.has_microphone }}
      - Keyboard: {{ context.device_capabilities.has_keyboard }}
    - Content Type: {{ context.content_type }}
    - Message Length: {{ context.message_length }}
    - Priority: {{ context.priority }}
    {% if context.environment_context %}
    - Environment:
      - Noise Level: {{ context.environment_context.noise_level }}
      - Privacy: {{ context.environment_context.privacy_level }}
      - Mobility: {{ context.environment_context.mobility }}
      - Hands-Free Required: {{ context.environment_context.hands_free_required }}
      - Eyes-Free Required: {{ context.environment_context.eyes_free_required }}
    {% endif %}
    {% if context.user_preference %}
    - User Preference: {{ context.user_preference }}
    {% endif %}
    {% if context.previous_modality %}
    - Previous Modality: {{ context.previous_modality }}
    {% endif %}
    {% if context.error_occurred %}
    - Error Context: An error occurred recently (prefer to stay in same modality)
    {% endif %}

    {% if user_accessibility_needs %}
    ## Accessibility Needs
    {{ user_accessibility_needs }}
    {% endif %}

    ## Selection Guidelines

    ### Priority Order (Highest to Lowest)
    1. **Accessibility needs ALWAYS override other preferences**
       - VISUAL impairment: Prefer VOICE, avoid visual-only
       - AUDITORY impairment: Prefer TEXT/VISUAL, avoid audio-only
       - MOTOR impairment: Prefer VOICE input
       - COGNITIVE: Use simpler, shorter responses

    2. **Match content type to modality affordances**
       | Content Type    | Best Modality | Rationale |
       |-----------------|---------------|-----------|
       | CONFIRMATION    | VOICE         | Quick, non-intrusive |
       | ERROR           | TEXT + VISUAL | Persistent, actionable |
       | DATA_TABLE      | VISUAL        | Spatial comparison |
       | LONG_TEXT       | TEXT          | Searchable, skimmable |
       | SHORT_RESPONSE  | VOICE or TEXT | User preference |
       | ACTION_REQUIRED | VISUAL + TEXT | Clear next steps |
       | DISAMBIGUATION  | VISUAL        | Show all options |
       | LIST            | VISUAL        | Easy scanning |
       | FORM            | VISUAL        | Structured input |
       | MEDIA           | VISUAL        | Rich content display |
       | NOTIFICATION    | VOICE or VISUAL | Based on urgency |
       | PROGRESS        | VISUAL        | Track status |
       | NAVIGATION      | VOICE + VISUAL | Hands-free + reference |

    3. **Consider environmental factors**
       - Loud environment → Avoid VOICE
       - Public space → Avoid audio output (privacy)
       - Mobility → Prefer VOICE (hands-free)
       - Eyes-free required → Must use VOICE
       - Hands-free required → Must use VOICE

    4. **Consider device capabilities**
       - No screen → Must use VOICE
       - No speaker → Must use TEXT/VISUAL
       - Small screen → Shorter visual content

    5. **Modality continuity (reduces cognitive load)**
       - Prefer staying in same modality (~23 min cognitive switch cost)
       - Exception: Content type strongly favors different modality

    6. **User preference (when factors are equal)**
       - Use historical preference as tiebreaker

    ## Output Requirements
    - Primary modality MUST be in available_modalities
    - Always provide fallback_chain with at least one alternative
    - Confidence should reflect certainty (0.5 = uncertain, 1.0 = certain)
    - Rationale should explain the key deciding factor

    {{ ctx.output_format }}
  "#
}

/// Select modality with detailed analysis
function SelectModalityDetailed(
  context: ModalityContext,
  user_accessibility_needs: AccessibilityNeed[]?,
  weights: SelectionWeights?
) -> ModalitySelectionResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Analyze the context and recommend the optimal modality with detailed scoring.

    ## Context
    - Available Modalities: {{ context.available_modalities }}
    - Device: Screen={{ context.device_capabilities.has_screen }}, Speaker={{ context.device_capabilities.has_speaker }}, Keyboard={{ context.device_capabilities.has_keyboard }}
    - Content Type: {{ context.content_type }}
    - Message Length: {{ context.message_length }}
    - Priority: {{ context.priority }}
    {% if context.environment_context %}
    - Environment: Noise={{ context.environment_context.noise_level }}, Privacy={{ context.environment_context.privacy_level }}, Mobile={{ context.environment_context.mobility }}
    {% endif %}
    {% if context.user_preference %}- User Preference: {{ context.user_preference }}{% endif %}
    {% if context.previous_modality %}- Previous: {{ context.previous_modality }}{% endif %}

    {% if user_accessibility_needs %}
    ## Accessibility Needs: {{ user_accessibility_needs }}
    {% endif %}

    {% if weights %}
    ## Selection Weights
    - Accessibility: {{ weights.accessibility }}
    - Content Match: {{ weights.content_match }}
    - Environment: {{ weights.environment }}
    - Device: {{ weights.device }}
    - User Preference: {{ weights.user_preference }}
    - Continuity: {{ weights.continuity }}
    {% else %}
    ## Default Weights
    - Accessibility: 1.0 (override)
    - Content Match: 0.35
    - Environment: 0.25
    - Device: 0.20
    - User Preference: 0.15
    - Continuity: 0.05
    {% endif %}

    ## Instructions
    1. Score each available modality on all factors (0.0-1.0)
    2. Apply weights to calculate overall score
    3. Consider accessibility as override (if needs present, must satisfy)
    4. Provide top recommendation with detailed rationale
    5. List alternatives considered with their scores
    6. Explain the decision path taken

    {{ ctx.output_format }}
  "#
}

/// Validate that a modality choice is appropriate for the context
function ValidateModalityChoice(
  chosen_modality: Modality,
  context: ModalityContext,
  user_accessibility_needs: AccessibilityNeed[]?
) -> ModalityValidationResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Validate whether the chosen modality is appropriate for this context.

    ## Chosen Modality: {{ chosen_modality }}

    ## Context
    - Available: {{ context.available_modalities }}
    - Content Type: {{ context.content_type }}
    - Device: Screen={{ context.device_capabilities.has_screen }}, Speaker={{ context.device_capabilities.has_speaker }}
    {% if context.environment_context %}
    - Environment: {{ context.environment_context }}
    {% endif %}

    {% if user_accessibility_needs %}
    ## Accessibility Needs: {{ user_accessibility_needs }}
    {% endif %}

    ## Validation Checks
    1. Is modality available on device?
    2. Does it satisfy accessibility requirements?
    3. Is it appropriate for content type?
    4. Is it suitable for the environment?
    5. Any warnings or concerns?

    {{ ctx.output_format }}
  "#
}

/// Result of modality validation
class ModalityValidationResult {
  is_valid bool @description("Whether the choice is acceptable")
  is_optimal bool @description("Whether this is the best choice")
  issues string[]? @description("Any problems with this choice")
  suggestions string[]? @description("Suggestions for improvement")
  accessibility_compliant bool @description("Meets accessibility requirements")
  recommended_alternative Modality? @description("Better alternative if not optimal")
}

// ============================================
// Fallback Chain Generation
// ============================================

/// Generate an appropriate fallback chain for a modality
function GenerateFallbackChain(
  primary_modality: Modality,
  available_modalities: Modality[],
  content_type: ContentType
) -> FallbackChain {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Generate a fallback chain for the primary modality.

    Primary: {{ primary_modality }}
    Available: {{ available_modalities }}
    Content Type: {{ content_type }}

    ## Guidelines
    - Order fallbacks by suitability for content type
    - Consider graceful degradation
    - TEXT is usually the safest fallback
    - HYBRID can degrade to single modality

    {{ ctx.output_format }}
  "#
}

/// Fallback chain with degradation strategies
class FallbackChain {
  chain Modality[] @description("Ordered list of fallback modalities")
  degradation_notes string[] @description("How content adapts at each fallback")
  minimum_viable Modality @description("Minimum modality that works")
}

// ============================================
// Test Cases
// ============================================

test select_modality_confirmation {
  functions [SelectModality]
  args {
    context {
      available_modalities [TEXT, VOICE, VISUAL, HYBRID]
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
    user_accessibility_needs null
  }
}

test select_modality_error_with_accessibility {
  functions [SelectModality]
  args {
    context {
      available_modalities [TEXT, VOICE, VISUAL, HYBRID]
      user_preference TEXT
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
      environment_context null
      content_type ERROR
      message_length MEDIUM
      priority HIGH
      previous_modality TEXT
      interaction_count 5
      error_occurred true
    }
    user_accessibility_needs [VISUAL]
  }
}

test select_modality_loud_environment {
  functions [SelectModality]
  args {
    context {
      available_modalities [TEXT, VOICE, VISUAL]
      user_preference VOICE
      device_capabilities {
        has_screen true
        has_speaker true
        has_microphone true
        has_keyboard true
        screen_size SMALL
        supports_touch true
        supports_voice_commands false
        bandwidth_quality "medium"
      }
      environment_context {
        noise_level LOUD
        privacy_level PUBLIC
        mobility true
        hands_free_required false
        eyes_free_required false
        time_of_day "afternoon"
      }
      content_type SHORT_RESPONSE
      message_length SHORT
      priority NORMAL
      previous_modality VOICE
      interaction_count 3
      error_occurred false
    }
    user_accessibility_needs null
  }
}

test select_modality_data_table {
  functions [SelectModality]
  args {
    context {
      available_modalities [TEXT, VOICE, VISUAL, HYBRID]
      user_preference null
      device_capabilities {
        has_screen true
        has_speaker true
        has_microphone false
        has_keyboard true
        screen_size LARGE
        supports_touch false
        supports_voice_commands false
        bandwidth_quality "high"
      }
      environment_context {
        noise_level MODERATE
        privacy_level SEMI_PRIVATE
        mobility false
        hands_free_required false
        eyes_free_required false
        time_of_day "evening"
      }
      content_type DATA_TABLE
      message_length LONG
      priority LOW
      previous_modality TEXT
      interaction_count 10
      error_occurred false
    }
    user_accessibility_needs null
  }
}
