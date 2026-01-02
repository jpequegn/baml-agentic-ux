// Accessibility Configuration Types (LUIAG Framework)
// Language User Interface Accessibility Guidelines type definitions
// Issue #67 - Task 4.1: Accessibility Config Types
// Part of #27 - Phase 4: LUI Accessibility Standards

// ============================================
// Core Compliance Enums
// ============================================

/// LUIAG conformance levels (aligned with WCAG structure)
enum ComplianceLevel {
  LEVEL_A @description("Minimum accessibility - essential requirements")
  LEVEL_AA @description("Standard accessibility - recommended for most applications")
  LEVEL_AAA @description("Enhanced accessibility - highest conformance level")
}

/// Reading level based on Flesch-Kincaid readability scores for LUIAG compliance
enum LUIAGReadingLevel {
  GRADE_5 @description("Simple language (Flesch-Kincaid 90-100)")
  GRADE_6 @description("Easy language (Flesch-Kincaid 80-90)")
  GRADE_8 @description("Standard language (Flesch-Kincaid 60-70)")
  GRADE_10 @description("Moderate complexity (Flesch-Kincaid 50-60)")
  GRADE_12 @description("Advanced language (Flesch-Kincaid 30-50)")
  UNRESTRICTED @description("No reading level restriction")
}

/// Cognitive complexity levels for content
enum CognitiveComplexity {
  MINIMAL @description("Simple, single-concept interactions")
  LOW @description("Basic multi-step operations")
  MODERATE @description("Standard application complexity")
  HIGH @description("Complex workflows with multiple dependencies")
}

/// Interaction pace preferences
enum InteractionPace {
  EXTENDED @description("Extended timeouts, no time pressure")
  RELAXED @description("Generous timing, gentle reminders")
  STANDARD @description("Normal timing with reasonable limits")
  FAST @description("Quick interactions for experienced users")
}

// ============================================
// Response Constraint Types
// ============================================

/// Constraints on response content and structure
class ResponseConstraints {
  max_sentence_length int? @description("Maximum words per sentence (null = no limit)")
  max_paragraph_length int? @description("Maximum sentences per paragraph (null = no limit)")
  max_list_items int? @description("Maximum items in a list before grouping")
  reading_level LUIAGReadingLevel @description("Target reading level for content")
  use_simple_vocabulary bool @description("Prefer common, everyday words")
  avoid_idioms bool @description("Avoid idioms, metaphors, and figurative language")
  avoid_abbreviations bool @description("Spell out abbreviations on first use")
  define_technical_terms bool @description("Provide definitions for technical terms")
  use_active_voice bool @description("Prefer active voice over passive")
  consistent_terminology bool @description("Use same term for same concept throughout")
}

/// Default response constraints for each compliance level
class ResponseConstraintDefaults {
  level_a ResponseConstraints @description("Defaults for Level A")
  level_aa ResponseConstraints @description("Defaults for Level AA")
  level_aaa ResponseConstraints @description("Defaults for Level AAA")
}

// ============================================
// Interaction Constraint Types
// ============================================

/// Constraints on interaction timing and input
class InteractionConstraints {
  min_response_time_ms int? @description("Minimum time before expecting user response")
  max_session_timeout_ms int? @description("Maximum session inactivity timeout")
  timeout_extension_allowed bool @description("Allow users to extend timeouts")
  timeout_warning_ms int? @description("Time before timeout to show warning")
  pace InteractionPace @description("Overall interaction pace")
  allow_pause_resume bool @description("Allow pausing and resuming operations")
  provide_progress_indicators bool @description("Show progress for multi-step operations")
  max_steps_before_summary int? @description("Steps before providing progress summary")
  confirm_destructive_actions bool @description("Require confirmation for irreversible actions")
  allow_undo bool @description("Provide undo capability where possible")
  max_concurrent_tasks int? @description("Maximum simultaneous tasks allowed")
}

/// Input method constraints
class InputConstraints {
  min_target_size_px int? @description("Minimum touch/click target size in pixels")
  keyboard_navigation_required bool @description("All functions must be keyboard accessible")
  voice_input_supported bool @description("Support voice input as alternative")
  gesture_alternatives_required bool @description("Provide alternatives to gesture-based input")
  autocomplete_enabled bool @description("Enable autocomplete for text inputs")
  error_prevention_level ErrorPreventionLevel @description("Level of error prevention measures")
}

/// Level of error prevention measures
enum ErrorPreventionLevel {
  BASIC @description("Standard validation and error messages")
  ENHANCED @description("Proactive suggestions and soft warnings")
  MAXIMUM @description("Strict validation, confirmations, and recovery options")
}

// ============================================
// Cognitive Constraint Types
// ============================================

/// Constraints related to cognitive accessibility
class CognitiveConstraints {
  max_complexity CognitiveComplexity @description("Maximum cognitive complexity allowed")
  max_choices_presented int? @description("Maximum options before grouping/filtering")
  use_progressive_disclosure bool @description("Reveal information gradually")
  provide_context_reminders bool @description("Remind users of context during long operations")
  max_memory_load int? @description("Maximum items user must remember (working memory)")
  use_consistent_layout bool @description("Maintain consistent UI patterns")
  minimize_distractions bool @description("Reduce non-essential elements")
  provide_clear_structure bool @description("Use headings, lists, and visual hierarchy")
  use_familiar_patterns bool @description("Prefer common, recognizable UI patterns")
  support_focus_mode bool @description("Option to hide non-essential UI elements")
  provide_summaries bool @description("Summarize long content")
  use_concrete_examples bool @description("Include concrete examples for abstract concepts")
}

/// Attention support features
class AttentionSupport {
  reduce_animations bool @description("Minimize or eliminate animations")
  reduce_auto_updates bool @description("Limit automatic content updates")
  notification_control NotificationControl @description("User control over notifications")
  focus_indicators FocusIndicatorConfig @description("Visual focus indicator settings")
}

/// Notification control settings
enum NotificationControl {
  ALL @description("Receive all notifications")
  IMPORTANT_ONLY @description("Only critical and important notifications")
  NONE @description("Suppress all non-essential notifications")
  SCHEDULED @description("Batch notifications at scheduled intervals")
}

/// Focus indicator configuration
class FocusIndicatorConfig {
  enhanced_visibility bool @description("Use high-contrast focus indicators")
  indicator_style FocusIndicatorStyle @description("Style of focus indicator")
  indicator_width_px int? @description("Width of focus outline in pixels")
}

/// Focus indicator style options
enum FocusIndicatorStyle {
  OUTLINE @description("Standard outline around element")
  HIGHLIGHT @description("Background highlight")
  UNDERLINE @description("Underline for text elements")
  COMBINATION @description("Multiple indicators combined")
}

// ============================================
// Disability Accommodation Types
// ============================================

/// Visual impairment accommodations
class VisualAccommodations {
  enabled bool @description("Enable visual accommodations")
  screen_reader_optimized bool @description("Optimize for screen readers")
  high_contrast_mode bool @description("Use high contrast colors")
  large_text_mode bool @description("Use larger text sizes")
  text_scaling_factor float? @description("Text size multiplier (1.0 = normal)")
  color_blind_mode ColorBlindMode? @description("Color blindness accommodation")
  reduce_transparency bool @description("Reduce transparent/translucent elements")
  provide_text_alternatives bool @description("Text alternatives for all visual content")
  image_descriptions_detailed bool @description("Provide detailed image descriptions")
  avoid_color_only_info bool @description("Never convey information by color alone")
  min_contrast_ratio float? @description("Minimum contrast ratio requirement")
}

/// Color blindness accommodation modes
enum ColorBlindMode {
  NONE @description("No color blind accommodation")
  PROTANOPIA @description("Red-blind (protanopia) accommodation")
  DEUTERANOPIA @description("Green-blind (deuteranopia) accommodation")
  TRITANOPIA @description("Blue-blind (tritanopia) accommodation")
  ACHROMATOPSIA @description("Complete color blindness accommodation")
}

/// Hearing impairment accommodations
class HearingAccommodations {
  enabled bool @description("Enable hearing accommodations")
  captions_required bool @description("Require captions for audio content")
  transcripts_required bool @description("Require full transcripts")
  visual_alerts bool @description("Use visual alerts instead of/with audio")
  sign_language_support bool @description("Provide sign language interpretation option")
  audio_description_text bool @description("Provide text descriptions of audio cues")
  volume_control bool @description("Allow fine-grained volume control")
  mono_audio bool @description("Mix stereo to mono for single-sided hearing loss")
}

/// Motor impairment accommodations
class MotorAccommodations {
  enabled bool @description("Enable motor accommodations")
  keyboard_only_mode bool @description("Support keyboard-only navigation")
  switch_access_support bool @description("Support switch device input")
  dwell_click_support bool @description("Support eye-gaze dwell clicking")
  dwell_time_ms int? @description("Dwell time for dwell click in milliseconds")
  large_touch_targets bool @description("Use larger touch/click targets")
  touch_target_size_px int? @description("Minimum touch target size in pixels")
  reduce_precision_required bool @description("Minimize need for precise movements")
  sticky_keys_support bool @description("Support sticky key functionality")
  gesture_simplification bool @description("Simplify or provide alternatives to complex gestures")
  motion_input_alternatives bool @description("Alternatives to motion-based input")
  pointer_speed_adjustable bool @description("Allow pointer speed adjustment")
}

/// Speech impairment accommodations
class SpeechAccommodations {
  enabled bool @description("Enable speech accommodations")
  text_input_alternative bool @description("Allow text as alternative to speech")
  typing_to_speech bool @description("Convert typed text to speech output")
  predefined_phrases bool @description("Offer predefined phrase selections")
  spelling_mode bool @description("Allow spelling out words letter by letter")
  extended_speech_timeout bool @description("Allow more time for speech input")
  noise_tolerance_high bool @description("Higher tolerance for background noise")
  accent_adaptation bool @description("Adapt to different accents and speech patterns")
}

/// Cognitive disability accommodations
class CognitiveAccommodations {
  enabled bool @description("Enable cognitive accommodations")
  simplified_language bool @description("Use simplified language throughout")
  reading_support bool @description("Provide reading assistance features")
  step_by_step_guidance bool @description("Break complex tasks into simple steps")
  memory_aids bool @description("Provide memory aids and reminders")
  decision_support bool @description("Help with decision making")
  distraction_reduction bool @description("Minimize distracting elements")
  consistent_navigation bool @description("Maintain highly consistent navigation")
  clear_error_messages bool @description("Use clear, actionable error messages")
  confirmation_dialogs bool @description("Confirm important actions")
  help_always_available bool @description("Keep help accessible at all times")
  symbolic_support bool @description("Use symbols/icons alongside text")
}

/// Neurological condition accommodations
class NeurologicalAccommodations {
  enabled bool @description("Enable neurological accommodations")
  seizure_safe_mode bool @description("Eliminate seizure-triggering content")
  flash_frequency_limit float? @description("Maximum flash frequency (Hz)")
  reduce_motion bool @description("Minimize motion and animations")
  vestibular_safe bool @description("Avoid vestibular-triggering effects")
  predictable_interactions bool @description("Ensure all interactions are predictable")
  sensory_overload_prevention bool @description("Prevent sensory overload")
  calm_mode bool @description("Use calming colors and minimal stimulation")
  break_reminders bool @description("Remind users to take breaks")
  break_interval_minutes int? @description("Minutes between break reminders")
}

/// Combined disability accommodations container
class DisabilityAccommodations {
  visual VisualAccommodations? @description("Visual impairment accommodations")
  hearing HearingAccommodations? @description("Hearing impairment accommodations")
  motor MotorAccommodations? @description("Motor impairment accommodations")
  speech SpeechAccommodations? @description("Speech impairment accommodations")
  cognitive CognitiveAccommodations? @description("Cognitive disability accommodations")
  neurological NeurologicalAccommodations? @description("Neurological condition accommodations")
}

// ============================================
// Main Accessibility Configuration
// ============================================

/// Complete accessibility configuration for LUIAG compliance
class LUIAGAccessibilityConfig {
  config_id string @description("Unique identifier for this configuration")
  config_version string @description("Version of this configuration")
  compliance_level ComplianceLevel @description("Target LUIAG compliance level")
  response_constraints ResponseConstraints @description("Response content constraints")
  interaction_constraints InteractionConstraints @description("Interaction timing/input constraints")
  cognitive_constraints CognitiveConstraints @description("Cognitive load constraints")
  attention_support AttentionSupport @description("Attention and focus support settings")
  disability_accommodations DisabilityAccommodations @description("Disability-specific accommodations")
  custom_settings map<string, string>? @description("Additional custom accessibility settings")
}

/// Accessibility configuration preset
class AccessibilityPreset {
  preset_id string @description("Unique preset identifier")
  name string @description("Human-readable preset name")
  description string @description("Description of what this preset provides")
  target_audience string @description("Who this preset is designed for")
  config LUIAGAccessibilityConfig @description("The accessibility configuration")
  tags string[]? @description("Tags for categorization")
}

/// Accessibility configuration update
class AccessibilityConfigUpdate {
  update_id string @description("Unique update identifier")
  config_id string @description("ID of configuration being updated")
  timestamp string @description("ISO 8601 timestamp of update")
  field_path string @description("Dot-notation path to updated field")
  previous_value string? @description("Previous value (JSON-encoded)")
  new_value string @description("New value (JSON-encoded)")
  reason string? @description("Reason for the update")
}

// ============================================
// Integration with InterfaceSchema
// ============================================

/// Accessibility metadata for interface schemas
class InterfaceAccessibility {
  supported_compliance_levels ComplianceLevel[] @description("Compliance levels this interface supports")
  default_config LUIAGAccessibilityConfig @description("Default accessibility configuration")
  available_presets AccessibilityPreset[]? @description("Pre-configured accessibility presets")
  accessibility_statement string? @description("Accessibility statement/policy")
  contact_for_accessibility string? @description("Contact for accessibility issues")
  last_audit_date string? @description("Date of last accessibility audit")
  known_limitations string[]? @description("Known accessibility limitations")
}

// ============================================
// Flesch-Kincaid Mapping Reference
// ============================================

/// Reference mapping for reading level to Flesch-Kincaid scores
class FleschKincaidMapping {
  reading_level LUIAGReadingLevel @description("Reading level enum value")
  grade_level_min int @description("Minimum school grade level")
  grade_level_max int @description("Maximum school grade level")
  flesch_score_min float @description("Minimum Flesch Reading Ease score")
  flesch_score_max float @description("Maximum Flesch Reading Ease score")
  description string @description("Description of reading difficulty")
}

// ============================================
// Functions
// ============================================

/// Create a default accessibility configuration for a compliance level
function CreateDefaultAccessibilityConfig(
  compliance_level: ComplianceLevel
) -> LUIAGAccessibilityConfig {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Create a complete accessibility configuration for LUIAG compliance level: {{ compliance_level }}

    Apply these guidelines based on compliance level:

    LEVEL_A (Minimum):
    - reading_level: GRADE_8
    - max_complexity: MODERATE
    - pace: STANDARD
    - Basic keyboard navigation required
    - Essential accommodations only

    LEVEL_AA (Standard - Recommended):
    - reading_level: GRADE_6
    - max_complexity: LOW
    - pace: RELAXED
    - Full keyboard navigation
    - Enhanced accommodations
    - Progress indicators required
    - Undo capability required

    LEVEL_AAA (Enhanced):
    - reading_level: GRADE_5
    - max_complexity: MINIMAL
    - pace: EXTENDED
    - Maximum accommodations
    - All optional features enabled
    - Detailed image descriptions
    - Full cognitive support

    Generate appropriate config_id and config_version.

    {{ ctx.output_format }}
  "#
}

/// Validate an accessibility configuration against LUIAG requirements
function ValidateAccessibilityConfig(
  config: LUIAGAccessibilityConfig
) -> AccessibilityConfigValidation {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Validate this accessibility configuration against LUIAG requirements.

    Configuration to validate:
    {{ config }}

    Check for:
    1. Completeness - all required fields present
    2. Consistency - no conflicting settings
    3. Compliance - meets stated compliance level requirements
    4. Feasibility - settings are technically achievable

    Provide specific issues found and recommendations.

    {{ ctx.output_format }}
  "#
}

/// Result of accessibility configuration validation
class AccessibilityConfigValidation {
  valid bool @description("Whether configuration is valid")
  compliance_achieved ComplianceLevel? @description("Actual compliance level achieved")
  issues ConfigValidationIssue[]? @description("Issues found during validation")
  recommendations string[]? @description("Recommendations for improvement")
  score float @description("Configuration quality score 0-100")
}

/// A specific issue found during configuration validation
class ConfigValidationIssue {
  severity ConfigIssueSeverity @description("Severity of the issue")
  field_path string @description("Path to the problematic field")
  issue string @description("Description of the issue")
  suggestion string? @description("Suggested fix")
}

/// Severity levels for configuration issues
enum ConfigIssueSeverity {
  ERROR @description("Must fix - prevents compliance")
  WARNING @description("Should fix - reduces effectiveness")
  INFO @description("Consider fixing - minor improvement")
}

/// Apply an accessibility preset to an existing configuration
function ApplyAccessibilityPreset(
  current_config: LUIAGAccessibilityConfig,
  preset: AccessibilityPreset
) -> LUIAGAccessibilityConfig {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Apply the accessibility preset to the current configuration.

    Current configuration:
    {{ current_config }}

    Preset to apply:
    {{ preset }}

    Merge the preset settings with the current configuration.
    Preset values should override current values where they conflict.
    Preserve any custom_settings from both.

    {{ ctx.output_format }}
  "#
}

// ============================================
// Test Cases
// ============================================

test create_level_aa_config {
  functions [CreateDefaultAccessibilityConfig]
  args {
    compliance_level LEVEL_AA
  }
}

test validate_minimal_config {
  functions [ValidateAccessibilityConfig]
  args {
    config {
      config_id "test-config-001"
      config_version "1.0.0"
      compliance_level LEVEL_A
      response_constraints {
        reading_level LUIAGReadingLevel.GRADE_8
        use_simple_vocabulary false
        avoid_idioms false
        avoid_abbreviations false
        define_technical_terms false
        use_active_voice true
        consistent_terminology true
      }
      interaction_constraints {
        timeout_extension_allowed true
        pace STANDARD
        allow_pause_resume true
        provide_progress_indicators true
        confirm_destructive_actions true
        allow_undo true
      }
      cognitive_constraints {
        max_complexity MODERATE
        use_progressive_disclosure true
        provide_context_reminders false
        use_consistent_layout true
        minimize_distractions false
        provide_clear_structure true
        use_familiar_patterns true
        support_focus_mode false
        provide_summaries false
        use_concrete_examples false
      }
      attention_support {
        reduce_animations false
        reduce_auto_updates false
        notification_control ALL
        focus_indicators {
          enhanced_visibility false
          indicator_style OUTLINE
        }
      }
      disability_accommodations {}
    }
  }
}
