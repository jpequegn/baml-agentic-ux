// Interaction Timing and Accessibility Configuration
// BAML types for interaction timing validation
// Issue #73 - Task 4.7: Interaction Timing Validator
// Part of #27 - Phase 4: LUI Accessibility Standards

// Dependencies:
// - ComplianceLevel from accessibility_types.baml

// ============================================
// Timeout Configuration
// ============================================

/// Configuration for interaction timeouts
class TimeoutConfig {
  initial_timeout_seconds int @description("Base timeout duration before expiration")
  warning_before_seconds int @description("Seconds before timeout to show warning")
  extension_allowed bool @description("Whether users can extend the timeout")
  extension_seconds int @description("Duration of each timeout extension")
  max_extensions int @description("Maximum extensions allowed (-1 for unlimited)")
}

// ============================================
// Input Method Configuration
// ============================================

/// Configuration for supported input methods
class InputMethodConfig {
  keyboard_accessible bool @description("All functions accessible via keyboard")
  voice_input bool @description("Voice input supported")
  touch_input bool @description("Touch input supported")
  switch_access bool @description("Switch device input supported")
  eye_tracking bool @description("Eye tracking input supported")
  gesture_alternatives bool @description("Alternatives to complex gestures provided")
  pointer_adjustable bool @description("Pointer speed/precision adjustable")
}

// ============================================
// Feedback Configuration
// ============================================

/// Configuration for user feedback mechanisms
class TimingFeedbackConfig {
  immediate_confirmation bool @description("Immediate feedback for user actions")
  error_messages_clear bool @description("Error messages are clear and actionable")
  success_indicators bool @description("Visual/audio success indicators")
  progress_indicators bool @description("Progress shown for long operations")
  status_updates bool @description("Regular status updates during operations")
}

// ============================================
// Error Handling Configuration
// ============================================

/// Configuration for error handling accessibility
class ErrorHandlingConfig {
  error_prevention bool @description("Proactive error prevention measures")
  error_identification bool @description("Clear identification of errors")
  error_suggestions bool @description("Suggestions for fixing errors")
  undo_available bool @description("Undo functionality available")
  auto_save bool @description("Automatic saving of user work")
  recovery_options bool @description("Recovery options for failures")
}

// ============================================
// Auto-Update Configuration
// ============================================

/// Configuration for auto-updating content
class AutoUpdateConfig {
  has_auto_update bool @description("Content auto-updates")
  can_pause bool @description("User can pause auto-updates")
  can_stop bool @description("User can stop auto-updates")
  can_adjust_frequency bool @description("User can adjust update frequency")
  update_frequency_seconds int @description("How often content updates")
}

// ============================================
// Complete Interaction Configuration
// ============================================

/// Complete interaction accessibility configuration for a component
class InteractionAccessibilityConfig {
  component_id string @description("ID of the component")
  timing TimeoutConfig @description("Timeout configuration")
  input_methods InputMethodConfig @description("Supported input methods")
  feedback TimingFeedbackConfig @description("Feedback mechanisms")
  error_handling ErrorHandlingConfig @description("Error handling configuration")
  auto_update AutoUpdateConfig? @description("Auto-update configuration if applicable")
}

// ============================================
// Timing Thresholds
// ============================================

/// Timing thresholds for a compliance level
class TimingThreshold {
  level ComplianceLevel @description("Compliance level")
  min_timeout_seconds int @description("Minimum initial timeout duration")
  min_warning_seconds int @description("Minimum warning time before timeout")
  extension_required bool @description("Whether extension mechanism is required")
  unlimited_extensions bool @description("Whether unlimited extensions required")
}

// ============================================
// Validation Result Types
// ============================================

/// Severity of timing violations
enum TimingViolationSeverity {
  CRITICAL @description("Blocks accessibility - must fix")
  MAJOR @description("Significant impact - should fix")
  MINOR @description("Reduces usability - consider fixing")
  ADVISORY @description("Improvement suggestion")
}

/// A timing-related accessibility violation
class TimingViolation {
  code string @description("Violation code (e.g., TIMEOUT_TOO_SHORT)")
  severity TimingViolationSeverity @description("Severity level")
  description string @description("Human-readable description")
  location string @description("Where in config the violation exists")
  remediation string @description("Suggested fix")
  threshold_expected string? @description("Expected threshold value")
  threshold_actual string? @description("Actual value found")
}

/// Result of timing validation
class TimingValidationResult {
  config_type string @description("Type of config validated")
  target_level ComplianceLevel @description("Target compliance level")
  achieved_level ComplianceLevel? @description("Highest level achieved")
  score float @description("Validation score 0.0-1.0")
  passes bool @description("Whether validation passed")
  violations TimingViolation[] @description("List of violations found")
  recommendations string[] @description("Prioritized recommendations")
  summary string @description("Human-readable summary")
}

/// Result of input method validation
class InputValidationResult {
  target_level ComplianceLevel @description("Target compliance level")
  achieved_level ComplianceLevel? @description("Highest level achieved")
  score float @description("Validation score 0.0-1.0")
  passes bool @description("Whether validation passed")
  violations TimingViolation[] @description("List of violations found")
  supported_methods string[] @description("Supported input methods")
  missing_methods string[] @description("Missing required methods")
  summary string @description("Human-readable summary")
}

/// Combined interaction validation result
class InteractionValidationResult {
  component_id string @description("ID of component validated")
  target_level ComplianceLevel @description("Target compliance level")
  timing_result TimingValidationResult? @description("Timeout validation")
  input_result InputValidationResult? @description("Input method validation")
  feedback_result TimingValidationResult? @description("Feedback validation")
  error_handling_result TimingValidationResult? @description("Error handling validation")
  auto_update_result TimingValidationResult? @description("Auto-update validation")
  overall_score float @description("Combined score")
  overall_passes bool @description("Whether all validations pass")
  summary string @description("Human-readable summary")
}

// ============================================
// AI Validation Functions
// ============================================

/// Validate timeout configuration for a compliance level
function ValidateTimeoutConfig(
  config: TimeoutConfig,
  target_level: ComplianceLevel
) -> TimingValidationResult {
  client CustomSonnet4
  prompt #"
    Validate this timeout configuration for LUIAG {{ target_level }} compliance.

    Configuration:
    {{ config }}

    Timing thresholds by level:
    | Level | Min Timeout | Warning Before | Extensions |
    |-------|-------------|----------------|------------|
    | A     | 20s         | 5s             | Optional   |
    | AA    | 30s         | 10s            | Required   |
    | AAA   | 60s         | 20s            | Unlimited  |

    Validation rules:
    1. Check initial_timeout_seconds meets minimum for target level
    2. Check warning_before_seconds meets minimum for target level
    3. Check extension_allowed is true for AA+ if extensions required
    4. Check max_extensions is -1 (unlimited) for AAA
    5. Check extension_seconds is meaningful (≥10s) if extensions enabled

    Calculate score:
    - Start at 1.0
    - CRITICAL violations: -0.25 each
    - MAJOR violations: -0.15 each
    - MINOR violations: -0.05 each
    - ADVISORY notices: -0.02 each

    Pass criteria:
    - Score ≥ 0.70
    - Zero CRITICAL violations

    {{ ctx.output_format }}
  "#
}

/// Validate input methods for a compliance level
function ValidateInputMethods(
  config: InputMethodConfig,
  target_level: ComplianceLevel
) -> InputValidationResult {
  client CustomSonnet4
  prompt #"
    Validate this input method configuration for LUIAG {{ target_level }} compliance.

    Configuration:
    {{ config }}

    Input requirements by level:
    | Level | Keyboard | Gesture Alt | Voice | Switch |
    |-------|----------|-------------|-------|--------|
    | A     | Required | No          | No    | No     |
    | AA    | Required | Required    | No    | No     |
    | AAA   | Required | Required    | Yes   | Yes    |

    Validation rules:
    1. keyboard_accessible is ALWAYS required (CRITICAL if missing)
    2. gesture_alternatives required for AA+
    3. voice_input required for AAA
    4. switch_access required for AAA

    List all supported and missing methods.
    Calculate score and determine achieved level.

    {{ ctx.output_format }}
  "#
}

/// Validate complete interaction configuration
function ValidateInteractionConfig(
  config: InteractionAccessibilityConfig,
  target_level: ComplianceLevel
) -> InteractionValidationResult {
  client CustomSonnet4
  prompt #"
    Validate this complete interaction accessibility configuration.

    Configuration:
    {{ config }}

    Target level: {{ target_level }}

    Validate each aspect:
    1. Timing - timeout configuration
    2. Input Methods - supported input methods
    3. Feedback - user feedback mechanisms
    4. Error Handling - error prevention and recovery
    5. Auto-Update - if applicable, controls for auto-updating content

    For each aspect, check against LUIAG requirements for the target level.
    Calculate individual scores and overall score.
    Determine if overall validation passes.

    {{ ctx.output_format }}
  "#
}

// ============================================
// Test Cases
// ============================================

test validate_aa_timeout {
  functions [ValidateTimeoutConfig]
  args {
    config {
      initial_timeout_seconds 45
      warning_before_seconds 15
      extension_allowed true
      extension_seconds 30
      max_extensions 3
    }
    target_level LEVEL_AA
  }
}

test validate_aaa_timeout_fails {
  functions [ValidateTimeoutConfig]
  args {
    config {
      initial_timeout_seconds 30
      warning_before_seconds 10
      extension_allowed true
      extension_seconds 20
      max_extensions 5
    }
    target_level LEVEL_AAA
  }
}

test validate_input_methods_aa {
  functions [ValidateInputMethods]
  args {
    config {
      keyboard_accessible true
      voice_input false
      touch_input true
      switch_access false
      eye_tracking false
      gesture_alternatives true
      pointer_adjustable true
    }
    target_level LEVEL_AA
  }
}

test validate_interaction_complete {
  functions [ValidateInteractionConfig]
  args {
    config {
      component_id "checkout_form"
      timing {
        initial_timeout_seconds 60
        warning_before_seconds 20
        extension_allowed true
        extension_seconds 30
        max_extensions -1
      }
      input_methods {
        keyboard_accessible true
        voice_input true
        touch_input true
        switch_access true
        eye_tracking false
        gesture_alternatives true
        pointer_adjustable true
      }
      feedback {
        immediate_confirmation true
        error_messages_clear true
        success_indicators true
        progress_indicators true
        status_updates true
      }
      error_handling {
        error_prevention true
        error_identification true
        error_suggestions true
        undo_available true
        auto_save true
        recovery_options true
      }
    }
    target_level LEVEL_AAA
  }
}
