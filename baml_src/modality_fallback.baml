// Modality Fallback and Graceful Degradation
// Handle modality failures and provide seamless fallbacks without information loss
// Issue #39 - Phase 1: Multi-Modal LUI Support

// ============================================
// Error Types
// ============================================

/// Types of modality errors
enum ModalityErrorType {
  UNAVAILABLE @description("Modality not supported on device")
  TIMEOUT @description("Service timeout")
  PERMISSION_DENIED @description("User denied access (e.g., microphone)")
  QUOTA_EXCEEDED @description("Rate limited or quota exceeded")
  NETWORK_ERROR @description("Connection failed")
  SERVICE_ERROR @description("Backend service error")
  RESOURCE_EXHAUSTED @description("Device resources exhausted")
  UNSUPPORTED_CONTENT @description("Content cannot be rendered in this modality")
  USER_INTERRUPT @description("User interrupted the modality")
  INITIALIZATION_FAILED @description("Modality failed to initialize")
}

/// Severity of the error
enum ErrorSeverity {
  LOW @description("Minor issue, can continue")
  MEDIUM @description("Significant issue, may need fallback")
  HIGH @description("Severe issue, requires fallback")
  CRITICAL @description("Complete failure, immediate fallback needed")
}

/// Recovery tier based on research
enum RecoveryTier {
  SELF_REPAIR @description("Tier 1: System fixes minor issues (0-1 attempts)")
  GUIDED_REPAIR @description("Tier 2: Offer alternatives (1-2 attempts)")
  ESCALATION @description("Tier 3: Switch modality or escalate (3+ attempts)")
}

// ============================================
// Modality Status
// ============================================

/// Error details for a modality failure
class ModalityError {
  error_type ModalityErrorType @description("Type of error that occurred")
  message string @description("Technical error message")
  user_message string @description("User-friendly error message")
  recoverable bool @description("Whether recovery is possible")
  suggested_fallback Modality? @description("Suggested fallback modality")
  retry_after_ms int? @description("Milliseconds to wait before retry")
  error_code string? @description("Technical error code for logging")
}

/// Status of a modality
class ModalityStatus {
  modality Modality @description("The modality")
  available bool @description("Whether modality is currently available")
  healthy bool @description("Whether modality is functioning properly")
  error ModalityError? @description("Current error if any")
  last_successful_at string? @description("ISO timestamp of last success")
  failure_count int @description("Number of consecutive failures")
  current_tier RecoveryTier @description("Current recovery tier")
}

/// Status of all available modalities
class ModalityHealthReport {
  modalities ModalityStatus[] @description("Status of each modality")
  recommended_modality Modality? @description("Currently recommended modality")
  overall_health OverallHealth @description("Overall system health")
  generated_at string @description("ISO timestamp of report")
}

/// Overall health status
enum OverallHealth {
  HEALTHY @description("All modalities functioning")
  DEGRADED @description("Some modalities unavailable")
  CRITICAL @description("Most modalities unavailable")
  OFFLINE @description("No modalities available")
}

// ============================================
// Degraded Response
// ============================================

/// A response that has been degraded to a fallback modality
class DegradedResponse {
  original_modality Modality @description("Intended modality")
  actual_modality Modality @description("Modality actually used")
  response MultiModalResponse @description("The adapted response")
  degradation_notice string? @description("Brief notice for user about the change")
  recovery_action string? @description("Suggested action to restore original modality")
  information_preserved bool @description("Whether all information was preserved")
  lost_features string[]? @description("Features lost in degradation if any")
}

/// Transformation applied during degradation
class DegradationTransformation {
  transformation_type TransformationType @description("Type of transformation applied")
  original_format string @description("Original content format")
  target_format string @description("Target content format")
  fidelity float @description("Information fidelity 0.0-1.0")
  notes string? @description("Notes about the transformation")
}

/// Types of transformations during degradation
enum TransformationType {
  VOICE_TO_TEXT @description("Voice content converted to text")
  VISUAL_TO_TEXT @description("Visual elements converted to text")
  TABLE_TO_LIST @description("Tables converted to bullet lists")
  CHART_TO_DESCRIPTION @description("Charts converted to descriptions")
  IMAGE_TO_ALT_TEXT @description("Images replaced with alt text")
  COMPLEX_TO_SIMPLE @description("Complex content simplified")
  MEDIA_TO_TRANSCRIPT @description("Media converted to transcript")
  INTERACTIVE_TO_STATIC @description("Interactive elements made static")
}

// ============================================
// Fallback Configuration
// ============================================

/// Fallback chain configuration for a modality
class FallbackConfiguration {
  primary_modality Modality @description("Primary modality")
  fallback_order Modality[] @description("Ordered fallback options")
  transformations DegradationTransformation[]? @description("How to transform content")
  notifications UserNotification[] @description("Notifications for each fallback level")
}

/// User notification during fallback
class UserNotification {
  level int @description("Fallback level (1 = first fallback)")
  message string @description("User-friendly message")
  show_recovery bool @description("Whether to show recovery option")
  style NotificationStyle @description("How to present notification")
}

/// Notification presentation style
enum NotificationStyle {
  SUBTLE @description("Brief inline notice")
  INFORMATIVE @description("Clear but not intrusive")
  PROMINENT @description("Noticeable notification")
  URGENT @description("Requires acknowledgment")
}

// ============================================
// Recovery Actions
// ============================================

/// A recovery action that can restore a modality
class RecoveryAction {
  action_type RecoveryActionType @description("Type of recovery action")
  description string @description("What this action does")
  user_prompt string? @description("Prompt to show user")
  automatic bool @description("Can be done automatically")
  success_likelihood float @description("Estimated success rate 0.0-1.0")
}

/// Types of recovery actions
enum RecoveryActionType {
  RETRY @description("Simply retry the operation")
  WAIT @description("Wait and retry later")
  REQUEST_PERMISSION @description("Ask user for permission")
  SWITCH_SERVICE @description("Try alternative service")
  REDUCE_QUALITY @description("Use lower quality version")
  REFRESH_CONNECTION @description("Refresh network connection")
  RESTART_SERVICE @description("Restart the modality service")
  ESCALATE_TO_HUMAN @description("Involve human support")
}

/// Result of a recovery attempt
class RecoveryResult {
  action RecoveryAction @description("Action that was attempted")
  success bool @description("Whether recovery succeeded")
  new_status ModalityStatus @description("Status after recovery")
  time_taken_ms int @description("Time taken for recovery")
  next_action RecoveryAction? @description("Next action if this failed")
}

// ============================================
// Fallback Functions
// ============================================

/// Handle a modality failure and generate fallback response
function HandleModalityFailure(
  intended_response: MultiModalResponse,
  failed_modality: Modality,
  error: ModalityError,
  available_modalities: Modality[]
) -> DegradedResponse {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Handle a modality failure and adapt the response.

    ## Failure Context
    - Failed Modality: {{ failed_modality }}
    - Error Type: {{ error.error_type }}
    - Error Message: {{ error.message }}
    - Recoverable: {{ error.recoverable }}
    {% if error.suggested_fallback %}- Suggested Fallback: {{ error.suggested_fallback }}{% endif %}

    ## Original Response
    {{ intended_response }}

    ## Available Fallback Modalities
    {{ available_modalities }}

    ## Adaptation Guidelines

    ### Voice → Fallback
    1. Text with enhanced formatting (bold, bullets)
    2. Visual with text elements
    3. Minimal text-only

    ### Visual → Fallback
    1. Text with structured formatting (tables as lists)
    2. Voice with clear segmentation
    3. Plain text

    ### Text → Fallback
    1. Voice with natural language
    2. Visual cards
    3. Minimal voice-only

    ## Requirements
    1. **Preserve ALL essential information** - no data loss
    2. **Adapt format for new modality** - optimize for target
    3. **Brief user notification** - one sentence, non-technical
    4. **Recovery suggestion** - if applicable

    ## Good Notification Examples
    - "I'm having trouble with voice. Showing you the text instead."
    - "Voice unavailable. Here's what I was going to say..."
    - "Switching to text view for now."

    ## Bad Notifications (AVOID)
    - "Error: Voice synthesis service returned 503"
    - "TTS module failed to initialize"
    - Technical jargon or error codes

    {{ ctx.output_format }}
  "#
}

/// Determine the best fallback modality based on context
function SelectFallbackModality(
  failed_modality: Modality,
  error: ModalityError,
  available_modalities: Modality[],
  content_type: ContentType,
  user_accessibility_needs: AccessibilityNeed[]?
) -> FallbackSelection {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Select the best fallback modality after a failure.

    ## Failure
    - Failed: {{ failed_modality }}
    - Error: {{ error.error_type }}
    - Recoverable: {{ error.recoverable }}

    ## Available Options
    {{ available_modalities }}

    ## Content Type
    {{ content_type }}

    {% if user_accessibility_needs %}
    ## Accessibility Needs
    {{ user_accessibility_needs }}
    {% endif %}

    ## Selection Criteria
    1. Accessibility needs are MANDATORY
    2. Content type compatibility
    3. Information preservation
    4. User experience smoothness

    ## Fallback Preferences by Original Modality

    ### VOICE failed
    - For short content: TEXT
    - For structured data: VISUAL
    - For accessibility: Consider VISUAL with audio descriptions

    ### VISUAL failed
    - For tables/charts: TEXT with formatting
    - For images: TEXT descriptions
    - For accessibility: VOICE

    ### TEXT failed
    - For any content: VOICE
    - For complex content: VISUAL

    {{ ctx.output_format }}
  "#
}

/// Result of fallback selection
class FallbackSelection {
  selected_modality Modality @description("Selected fallback")
  rationale string @description("Why this was selected")
  confidence float @description("Confidence in selection 0.0-1.0")
  expected_fidelity float @description("Expected information fidelity")
  transformations_needed TransformationType[] @description("Required transformations")
  alternative Modality? @description("Second choice if first fails")
}

/// Transform content for a different modality
function TransformForModality(
  content: MultiModalResponse,
  source_modality: Modality,
  target_modality: Modality,
  preserve_priority: PreservePriority
) -> TransformedContent {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Transform content from {{ source_modality }} to {{ target_modality }}.

    ## Original Content
    {{ content }}

    ## Preservation Priority
    {{ preserve_priority }}

    ## Transformation Guidelines

    ### VOICE → TEXT
    - Keep natural language, add formatting
    - Convert pauses to line breaks
    - Add emphasis where prosody indicated

    ### VOICE → VISUAL
    - Create text cards with key points
    - Use containers for segmentation
    - Add visual hierarchy

    ### VISUAL → TEXT
    - Tables → Bullet lists with labels
    - Charts → Written descriptions
    - Images → Detailed alt text

    ### VISUAL → VOICE
    - Linearize content logically
    - Describe visual elements
    - Add transition phrases

    ### TEXT → VOICE
    - Optimize for listening
    - Add natural pauses
    - Avoid complex formatting

    ### TEXT → VISUAL
    - Create visual hierarchy
    - Use cards for sections
    - Add spacing and structure

    ## Requirements
    - Preserve all critical information
    - Adapt format to target modality
    - Maintain accessibility
    - Document any information loss

    {{ ctx.output_format }}
  "#
}

/// Priority for preserving content during transformation
class PreservePriority {
  critical_elements string[] @description("Must preserve at all costs")
  important_elements string[] @description("Should preserve if possible")
  optional_elements string[] @description("Can be simplified or dropped")
  acceptable_loss float @description("Acceptable information loss 0.0-1.0")
}

/// Result of content transformation
class TransformedContent {
  content MultiModalResponse @description("Transformed content")
  transformations_applied TransformationType[] @description("What was done")
  fidelity float @description("Information fidelity achieved 0.0-1.0")
  lost_elements string[]? @description("Elements that couldn't be preserved")
  notes string? @description("Notes about the transformation")
}

/// Generate recovery suggestions for a modality error
function GenerateRecoverySuggestions(
  error: ModalityError,
  modality: Modality,
  failure_count: int,
  previous_recovery_attempts: RecoveryAction[]?
) -> RecoverySuggestions {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Generate recovery suggestions for a modality failure.

    ## Error Context
    - Modality: {{ modality }}
    - Error Type: {{ error.error_type }}
    - Recoverable: {{ error.recoverable }}
    - Failure Count: {{ failure_count }}

    {% if previous_recovery_attempts %}
    ## Previous Attempts
    {{ previous_recovery_attempts }}
    {% endif %}

    ## Recovery Tier Logic
    - 0-1 failures: SELF_REPAIR (automatic retries)
    - 1-2 failures: GUIDED_REPAIR (offer alternatives)
    - 3+ failures: ESCALATION (switch modality or human)

    ## Recovery Actions by Error Type

    | Error Type | Primary Action | Secondary Action |
    |------------|----------------|------------------|
    | UNAVAILABLE | Switch modality | - |
    | TIMEOUT | Retry with backoff | Switch modality |
    | PERMISSION_DENIED | Request permission | Offer alternative |
    | QUOTA_EXCEEDED | Wait | Reduce quality |
    | NETWORK_ERROR | Retry | Offline mode |
    | SERVICE_ERROR | Switch service | Escalate |

    ## Requirements
    - Provide user-friendly descriptions
    - Estimate success likelihood
    - Identify automatic vs manual actions
    - Order by likelihood of success

    {{ ctx.output_format }}
  "#
}

/// Recovery suggestions for the user
class RecoverySuggestions {
  current_tier RecoveryTier @description("Current recovery tier")
  primary_action RecoveryAction @description("Best action to try")
  alternative_actions RecoveryAction[] @description("Other options")
  user_message string @description("Message to show user")
  automatic_actions RecoveryAction[] @description("Actions to try automatically")
  requires_user_input bool @description("Whether user input is needed")
}

/// Generate user-friendly notification for modality change
function GenerateDegradationNotice(
  original_modality: Modality,
  fallback_modality: Modality,
  error_type: ModalityErrorType,
  recovery_possible: bool
) -> DegradationNotice {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Generate a user-friendly notice about modality change.

    ## Context
    - Original: {{ original_modality }}
    - Fallback: {{ fallback_modality }}
    - Error: {{ error_type }}
    - Recovery Possible: {{ recovery_possible }}

    ## Requirements
    1. One sentence, friendly tone
    2. No technical jargon
    3. Brief recovery suggestion if applicable
    4. Non-alarming

    ## Good Examples
    - "I'm having trouble with voice. Showing you the text instead."
    - "Voice unavailable. Here's what I was going to say..."
    - "Switching to text for now. Tap here when ready for voice."
    - "Can't show the chart right now. Here's a summary instead."

    ## Bad Examples (AVOID)
    - "Error: Voice synthesis service returned 503"
    - "TTS module failed to initialize"
    - "FATAL: AudioContext not available"
    - "Connection to speech server failed"

    {{ ctx.output_format }}
  "#
}

/// User-friendly degradation notice
class DegradationNotice {
  main_message string @description("Primary notification message")
  recovery_hint string? @description("Brief recovery suggestion")
  style NotificationStyle @description("How to present this")
  show_immediately bool @description("Show before or with content")
  dismissible bool @description("Can user dismiss this")
}

// ============================================
// Fallback Configurations
// ============================================

/// Get default fallback configuration for a modality
function GetDefaultFallbackConfig(
  modality: Modality
) -> FallbackConfiguration {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Generate the default fallback configuration for {{ modality }}.

    ## Standard Fallback Chains

    ### VOICE
    Fallback order: TEXT → VISUAL → HYBRID
    - TEXT: Add formatting, preserve emphasis
    - VISUAL: Use text cards, add structure
    - HYBRID: Combine available modalities

    ### VISUAL
    Fallback order: TEXT → VOICE → HYBRID
    - TEXT: Convert tables to lists, describe images
    - VOICE: Read content with good pacing
    - HYBRID: Combine available modalities

    ### TEXT
    Fallback order: VISUAL → VOICE → HYBRID
    - VISUAL: Create card layout
    - VOICE: Read naturally
    - HYBRID: Combine available modalities

    ### HYBRID
    Fallback order: TEXT → VOICE → VISUAL
    - Single modality fallbacks in order of fidelity

    ## Notification Templates
    Level 1 (first fallback): Subtle, inline
    Level 2 (second fallback): Informative, clear
    Level 3+ (deep fallback): Prominent, suggest recovery

    {{ ctx.output_format }}
  "#
}

// ============================================
// Test Cases
// ============================================

test handle_voice_failure {
  functions [HandleModalityFailure]
  args {
    intended_response {
      response_id "test-response-001"
      primary_modality VOICE
      text null
      voice {
        text "Your meeting with John starts in 30 minutes."
        language "en-US"
        voice_config null
        segments null
        total_duration null
      }
      visuals null
      actions null
      accessibility {
        alt_text "Meeting reminder"
        aria_label null
        screen_reader_hints null
        keyboard_shortcuts null
        high_contrast_supported false
        reduced_motion_supported false
      }
      timing null
      sequence null
      context_hints null
      metadata null
    }
    failed_modality VOICE
    error {
      error_type TIMEOUT
      message "TTS service timeout after 5000ms"
      user_message "Voice is taking too long"
      recoverable true
      suggested_fallback TEXT
      retry_after_ms 10000
      error_code "TTS_TIMEOUT"
    }
    available_modalities [TEXT, VISUAL]
  }
}

test handle_visual_failure {
  functions [HandleModalityFailure]
  args {
    intended_response {
      response_id "test-response-002"
      primary_modality VISUAL
      text null
      voice null
      visuals [
        {
          element_id "chart-1"
          element_type CHART
          title "Monthly Sales"
          content null
          dimensions null
          style_hints null
          accessibility_label "Bar chart showing monthly sales data"
        }
      ]
      actions null
      accessibility {
        alt_text "Sales chart"
        aria_label null
        screen_reader_hints null
        keyboard_shortcuts null
        high_contrast_supported false
        reduced_motion_supported false
      }
      timing null
      sequence null
      context_hints null
      metadata null
    }
    failed_modality VISUAL
    error {
      error_type SERVICE_ERROR
      message "Chart rendering service unavailable"
      user_message "Can't display chart right now"
      recoverable false
      suggested_fallback TEXT
      retry_after_ms null
      error_code "CHART_RENDER_ERR"
    }
    available_modalities [TEXT, VOICE]
  }
}

test select_fallback_accessibility {
  functions [SelectFallbackModality]
  args {
    failed_modality VISUAL
    error {
      error_type UNAVAILABLE
      message "No display available"
      user_message "Display not available"
      recoverable false
      suggested_fallback VOICE
      retry_after_ms null
      error_code null
    }
    available_modalities [TEXT, VOICE]
    content_type DATA_TABLE
    user_accessibility_needs [VISUAL]
  }
}

test generate_recovery_escalation {
  functions [GenerateRecoverySuggestions]
  args {
    error {
      error_type NETWORK_ERROR
      message "Connection failed"
      user_message "Network unavailable"
      recoverable true
      suggested_fallback null
      retry_after_ms 5000
      error_code "NET_ERR"
    }
    modality VOICE
    failure_count 3
    previous_recovery_attempts [
      {
        action_type RETRY
        description "Retry connection"
        user_prompt null
        automatic true
        success_likelihood 0.7
      },
      {
        action_type RETRY
        description "Retry with exponential backoff"
        user_prompt null
        automatic true
        success_likelihood 0.5
      }
    ]
  }
}
