// Accessibility Validation (WCAG 2.2 Compliance)
// Automated accessibility validation for multi-modal LUI responses
// Issue #41 - Phase 1: Multi-Modal LUI Support

// ============================================
// WCAG Compliance Types
// ============================================

/// WCAG conformance levels
enum WCAGLevel {
  A @description("Level A - Minimum accessibility")
  AA @description("Level AA - Standard accessibility (recommended)")
  AAA @description("Level AAA - Enhanced accessibility")
}

/// WCAG success criteria categories
enum WCAGCategory {
  PERCEIVABLE @description("Information must be presentable")
  OPERABLE @description("UI components must be operable")
  UNDERSTANDABLE @description("Information and operation must be understandable")
  ROBUST @description("Content must be robust enough for assistive technologies")
}

/// Specific WCAG success criteria
enum WCAGCriterion {
  // Perceivable
  SC_1_1_1 @description("Non-text Content - Text alternatives")
  SC_1_2_1 @description("Audio-only and Video-only - Alternatives")
  SC_1_2_2 @description("Captions - Prerecorded audio")
  SC_1_2_3 @description("Audio Description or Media Alternative")
  SC_1_3_1 @description("Info and Relationships - Semantic structure")
  SC_1_3_2 @description("Meaningful Sequence - Logical order")
  SC_1_3_3 @description("Sensory Characteristics - Not solely sensory")
  SC_1_4_1 @description("Use of Color - Not sole visual means")
  SC_1_4_3 @description("Contrast Minimum - 4.5:1 ratio")
  SC_1_4_4 @description("Resize Text - Up to 200%")
  SC_1_4_5 @description("Images of Text - Avoid unless essential")

  // Operable
  SC_2_1_1 @description("Keyboard - All functionality keyboard accessible")
  SC_2_1_2 @description("No Keyboard Trap - Can navigate away")
  SC_2_2_1 @description("Timing Adjustable - User can extend timeouts")
  SC_2_3_1 @description("Three Flashes or Below - No seizure triggers")
  SC_2_4_1 @description("Bypass Blocks - Skip navigation mechanism")
  SC_2_4_2 @description("Page Titled - Descriptive titles")
  SC_2_4_3 @description("Focus Order - Logical focus sequence")
  SC_2_4_4 @description("Link Purpose - Clear from link text")
  SC_2_4_6 @description("Headings and Labels - Descriptive")
  SC_2_4_7 @description("Focus Visible - Visible focus indicator")

  // Understandable
  SC_3_1_1 @description("Language of Page - Specified")
  SC_3_1_2 @description("Language of Parts - Specified for parts")
  SC_3_2_1 @description("On Focus - No unexpected changes")
  SC_3_2_2 @description("On Input - No unexpected changes")
  SC_3_2_3 @description("Consistent Navigation - Predictable")
  SC_3_2_4 @description("Consistent Identification - Same functions same labels")
  SC_3_3_1 @description("Error Identification - Errors described")
  SC_3_3_2 @description("Labels or Instructions - Provided")
  SC_3_3_3 @description("Error Suggestion - Correction suggested")
  SC_3_3_4 @description("Error Prevention - Review before submit")

  // Robust
  SC_4_1_1 @description("Parsing - Valid markup")
  SC_4_1_2 @description("Name, Role, Value - ARIA attributes")
  SC_4_1_3 @description("Status Messages - Programmatically announced")
}

// ============================================
// Accessibility Requirements
// ============================================

/// Complete accessibility requirements configuration
class AccessibilityRequirements {
  wcag_level WCAGLevel @description("Target WCAG conformance level")
  screen_reader_support bool @description("Must support screen readers")
  voice_control_support bool @description("Must support voice control")
  reduced_motion bool @description("User prefers reduced motion")
  high_contrast bool @description("User requires high contrast")
  cognitive_support bool @description("Enhanced cognitive accessibility")
  keyboard_only bool? @description("User navigates with keyboard only")
  large_text bool? @description("User requires large text")
  captions_required bool? @description("User requires captions for audio")
  audio_descriptions bool? @description("User requires audio descriptions")
}

/// User-specific accessibility profile
class AccessibilityProfile {
  needs AccessibilityNeed[] @description("Types of accessibility needs")
  requirements AccessibilityRequirements @description("Specific requirements")
  preferred_modality Modality? @description("Preferred communication modality")
  assistive_technologies string[]? @description("Technologies used (screen reader, voice control, etc.)")
  custom_preferences map<string, string>? @description("Custom preference key-value pairs")
}

// ============================================
// Violation Types
// ============================================

/// Severity of accessibility violations
enum ViolationSeverity {
  CRITICAL @description("Prevents access for some users - must fix")
  SERIOUS @description("Significant barrier - should fix for compliance")
  MODERATE @description("Some users affected - recommended to fix")
  MINOR @description("Best practice - nice to fix")
}

/// Impact on specific user groups
enum ImpactedGroup {
  BLIND @description("Users who are blind")
  LOW_VISION @description("Users with low vision")
  COLOR_BLIND @description("Users with color blindness")
  DEAF @description("Users who are deaf")
  HARD_OF_HEARING @description("Users with hearing difficulties")
  MOTOR_IMPAIRED @description("Users with motor impairments")
  COGNITIVE @description("Users with cognitive disabilities")
  VESTIBULAR @description("Users with vestibular disorders")
  PHOTOSENSITIVE @description("Users with photosensitive conditions")
}

/// An individual accessibility violation
class AccessibilityViolation {
  rule_id string @description("WCAG rule identifier (e.g., WCAG-1.1.1)")
  criterion WCAGCriterion @description("Specific WCAG success criterion")
  category WCAGCategory @description("WCAG category")
  severity ViolationSeverity @description("Severity of the violation")
  element string @description("Element or component with violation")
  element_type string? @description("Type of element (image, button, etc.)")
  description string @description("Description of the violation")
  impact string @description("Impact on users")
  impacted_groups ImpactedGroup[] @description("User groups affected")
  remediation string @description("How to fix the violation")
  code_example string? @description("Example of correct implementation")
  wcag_reference string? @description("Link to WCAG documentation")
}

/// Remediation action for a violation
class RemediationAction {
  violation_id string @description("ID of violation to fix")
  action_type RemediationActionType @description("Type of remediation")
  description string @description("What needs to be done")
  effort_estimate EffortLevel @description("Estimated effort to fix")
  priority int @description("Priority order (1 = highest)")
  automated_fix bool @description("Whether fix can be automated")
  suggested_value string? @description("Suggested value for fix")
}

/// Types of remediation actions
enum RemediationActionType {
  ADD_ALT_TEXT @description("Add alternative text to element")
  ADD_ARIA_LABEL @description("Add ARIA label")
  ADD_ARIA_LIVE @description("Add ARIA live region")
  ADD_ROLE @description("Add element role")
  IMPROVE_CONTRAST @description("Improve color contrast")
  ADD_KEYBOARD_NAV @description("Add keyboard navigation")
  ADD_FOCUS_INDICATOR @description("Add visible focus indicator")
  SIMPLIFY_CONTENT @description("Simplify content for cognitive accessibility")
  ADD_CAPTIONS @description("Add captions to audio/video")
  ADD_AUDIO_DESCRIPTION @description("Add audio descriptions")
  ADD_TEXT_FALLBACK @description("Add text fallback for voice")
  ADD_VOICE_FALLBACK @description("Add voice fallback for text")
  REDUCE_MOTION @description("Remove or reduce animations")
  ADD_LANGUAGE @description("Specify content language")
  ADD_HEADING_STRUCTURE @description("Add proper heading structure")
  FIX_LINK_TEXT @description("Improve link text clarity")
}

// Note: EffortLevel is defined in usability_analysis.baml (TRIVIAL, LOW, MEDIUM, HIGH, MAJOR)

// ============================================
// Accessibility Report Types
// ============================================

/// Complete accessibility validation report
class AccessibilityReport {
  report_id string @description("Unique report identifier")
  generated_at string @description("ISO timestamp of report generation")
  response_id string @description("ID of validated response")
  compliant bool @description("Meets target WCAG level")
  wcag_level WCAGLevel @description("Target conformance level")
  achieved_level WCAGLevel? @description("Actual achieved level")
  score float @description("Accessibility score 0-100")
  violations AccessibilityViolation[] @description("List of violations found")
  remediations RemediationAction[]? @description("Suggested fixes")
  summary ReportSummary @description("Summary of findings")
  category_scores CategoryScores @description("Scores by WCAG category")
  tested_criteria WCAGCriterion[] @description("Criteria that were tested")
}

/// Summary of accessibility report
class ReportSummary {
  total_violations int @description("Total number of violations")
  critical_count int @description("Number of critical violations")
  serious_count int @description("Number of serious violations")
  moderate_count int @description("Number of moderate violations")
  minor_count int @description("Number of minor violations")
  pass_rate float @description("Percentage of tests passed")
  primary_issues string[] @description("Main accessibility issues")
  strengths string[] @description("Accessibility strengths")
  recommendations string[] @description("Priority recommendations")
}

/// Scores by WCAG category
class CategoryScores {
  perceivable float @description("Perceivable category score 0-100")
  operable float @description("Operable category score 0-100")
  understandable float @description("Understandable category score 0-100")
  robust float @description("Robust category score 0-100")
}

// ============================================
// Element-Specific Validation
// ============================================

/// Validation result for a single element
class ElementValidation {
  element_id string @description("Element identifier")
  element_type string @description("Type of element")
  passed_checks string[] @description("Checks that passed")
  failed_checks AccessibilityViolation[] @description("Checks that failed")
  suggestions string[]? @description("Improvement suggestions")
}

/// Validation for visual elements
class VisualElementValidation {
  element ElementValidation @description("Base validation")
  has_alt_text bool @description("Has alternative text")
  alt_text_quality AltTextQuality? @description("Quality of alt text")
  contrast_ratio float? @description("Color contrast ratio")
  meets_contrast_requirement bool? @description("Meets AA contrast ratio")
  focus_indicator_present bool? @description("Has focus indicator")
  keyboard_accessible bool @description("Accessible via keyboard")
}

/// Quality assessment of alternative text
enum AltTextQuality {
  EXCELLENT @description("Descriptive, concise, informative")
  GOOD @description("Adequate description")
  NEEDS_IMPROVEMENT @description("Too brief or generic")
  POOR @description("Missing key information")
  DECORATIVE @description("Correctly marked as decorative")
}

/// Validation for voice elements
class VoiceElementValidation {
  element ElementValidation @description("Base validation")
  has_text_fallback bool @description("Has text fallback")
  has_transcript bool? @description("Has full transcript")
  language_specified bool @description("Language is specified")
  speech_rate_adjustable bool @description("Speech rate can be adjusted")
  has_pauses bool @description("Has appropriate pauses")
  estimated_duration_seconds float? @description("Estimated duration")
}

/// Validation for action elements
class ActionElementValidation {
  element ElementValidation @description("Base validation")
  label_quality LabelQuality @description("Quality of action label")
  has_keyboard_shortcut bool @description("Has keyboard shortcut")
  is_focusable bool @description("Can receive focus")
  has_aria_label bool @description("Has ARIA label")
  action_purpose_clear bool @description("Purpose is clear from label")
}

/// Quality of action/button labels
enum LabelQuality {
  EXCELLENT @description("Clear, descriptive, actionable")
  GOOD @description("Understandable label")
  NEEDS_IMPROVEMENT @description("Vague or unclear")
  POOR @description("Single character or icon only")
}

// ============================================
// Validation Functions
// ============================================

/// Validate a multi-modal response for accessibility
function ValidateAccessibility(
  response: MultiModalResponse,
  requirements: AccessibilityRequirements
) -> AccessibilityReport {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Validate this multi-modal response for accessibility compliance.

    ## Response to Validate
    - Response ID: {{ response.response_id }}
    - Primary Modality: {{ response.primary_modality }}
    {% if response.text %}
    - Has Text: Yes ({{ response.text.content | length }} characters)
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
    - Accessibility Meta:
      - ARIA Live: {{ response.accessibility.aria_live }}
      - Cognitive Load: {{ response.accessibility.cognitive_load }}
      - Screen Reader Support: {{ response.accessibility.supports_screen_reader }}
      - Keyboard Nav: {{ response.accessibility.supports_keyboard_nav }}
      - High Contrast: {{ response.accessibility.high_contrast_available }}
      - Reduced Motion Safe: {{ response.accessibility.reduced_motion_safe }}

    ## Requirements
    - WCAG Level: {{ requirements.wcag_level }}
    - Screen Reader Support: {{ requirements.screen_reader_support }}
    - Voice Control Support: {{ requirements.voice_control_support }}
    - Reduced Motion: {{ requirements.reduced_motion }}
    - High Contrast: {{ requirements.high_contrast }}
    - Cognitive Support: {{ requirements.cognitive_support }}
    {% if requirements.keyboard_only %}
    - Keyboard Only: {{ requirements.keyboard_only }}
    {% endif %}

    ## WCAG Checks by Category

    ### PERCEIVABLE (1.x)
    1.1.1 Non-text Content:
    - All images MUST have alt_text
    - All icons MUST have labels
    - Decorative images should be marked as such

    1.3.1 Info and Relationships:
    - Structure MUST be determinable programmatically
    - Use semantic elements (headings, lists, etc.)
    - ARIA roles where appropriate

    1.4.3 Contrast (AA):
    - Text contrast MUST be at least 4.5:1
    - Large text contrast MUST be at least 3:1
    - {% if requirements.wcag_level == "AAA" %}AAA requires 7:1{% endif %}

    ### OPERABLE (2.x)
    2.1.1 Keyboard:
    - ALL functionality MUST be keyboard accessible
    - No keyboard traps

    2.4.4 Link Purpose:
    - Action labels MUST be descriptive
    - Purpose clear from link text alone

    2.4.7 Focus Visible:
    - Focus indicator MUST be visible

    ### UNDERSTANDABLE (3.x)
    3.1.1 Language of Page:
    - Language MUST be specified
    - Voice SSML should include lang attribute

    3.2.1-2 Predictable:
    - No unexpected changes on focus/input

    3.3.1-2 Error Handling:
    - Errors MUST be identified and described

    ### ROBUST (4.x)
    4.1.2 Name, Role, Value:
    - All elements MUST have accessible names
    - ARIA attributes MUST be valid
    - aria-live for dynamic content

    4.1.3 Status Messages:
    - Status updates via aria-live

    ### VOICE-SPECIFIC
    - Voice responses MUST have text fallback
    - Speech rate should be adjustable
    - Sufficient pauses between segments
    - No time limits on audio

    ### COGNITIVE ACCESSIBILITY
    {% if requirements.cognitive_support %}
    - Cognitive load should be LOW or MINIMAL
    - Content should be simple and clear
    - Actions should be predictable
    {% endif %}

    ## Instructions
    1. Check each applicable WCAG criterion
    2. Report all violations with severity
    3. Calculate category scores
    4. Provide remediation steps
    5. Generate overall compliance score

    {{ ctx.output_format }}
  "#
}

/// Validate accessibility with detailed element analysis
function ValidateAccessibilityDetailed(
  response: MultiModalResponse,
  requirements: AccessibilityRequirements,
  focus_areas: WCAGCategory[]?
) -> DetailedAccessibilityReport {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Perform detailed accessibility validation with element-level analysis.

    ## Response
    {{ response }}

    ## Requirements
    {{ requirements }}

    {% if focus_areas %}
    ## Focus Areas
    Only validate these categories: {{ focus_areas }}
    {% endif %}

    ## Instructions
    1. Validate each element individually
    2. Provide element-specific recommendations
    3. Assess alt text quality for images
    4. Check label quality for actions
    5. Validate voice accessibility

    {{ ctx.output_format }}
  "#
}

/// Detailed accessibility report with element validation
class DetailedAccessibilityReport {
  base_report AccessibilityReport @description("Base accessibility report")
  visual_validations VisualElementValidation[]? @description("Visual element validations")
  voice_validations VoiceElementValidation[]? @description("Voice element validations")
  action_validations ActionElementValidation[]? @description("Action element validations")
  element_summary string @description("Summary of element-level findings")
}

/// Check if response meets minimum accessibility for a user profile
function CheckAccessibilityForUser(
  response: MultiModalResponse,
  user_profile: AccessibilityProfile
) -> UserAccessibilityCheck {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Check if this response is accessible for a specific user profile.

    ## Response
    - Modality: {{ response.primary_modality }}
    {% if response.text %}- Has Text{% endif %}
    {% if response.voice %}- Has Voice{% endif %}
    {% if response.visuals %}- Has {{ response.visuals | length }} visuals{% endif %}
    - ARIA Live: {{ response.accessibility.aria_live }}
    - Cognitive Load: {{ response.accessibility.cognitive_load }}

    ## User Profile
    - Accessibility Needs: {{ user_profile.needs }}
    - Requirements: {{ user_profile.requirements }}
    {% if user_profile.preferred_modality %}
    - Preferred Modality: {{ user_profile.preferred_modality }}
    {% endif %}
    {% if user_profile.assistive_technologies %}
    - Assistive Technologies: {{ user_profile.assistive_technologies }}
    {% endif %}

    ## Check Instructions
    For each accessibility need, verify:
    - VISUAL: Voice/text available, no visual-only info
    - AUDITORY: Text available, captions if needed
    - MOTOR: Keyboard accessible, simple interactions
    - COGNITIVE: Low complexity, clear structure

    {{ ctx.output_format }}
  "#
}

/// Result of user-specific accessibility check
class UserAccessibilityCheck {
  accessible bool @description("Response is accessible for this user")
  confidence float @description("Confidence in assessment 0-1")
  meets_needs map<string, bool> @description("Whether each need is met")
  blockers string[]? @description("Issues preventing access")
  recommendations string[]? @description("Recommendations for improvement")
  alternative_modality Modality? @description("Suggested alternative modality if not accessible")
}

/// Generate remediation plan for violations
function GenerateRemediationPlan(
  violations: AccessibilityViolation[],
  priority_focus: WCAGCategory?
) -> RemediationPlan {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Generate a prioritized remediation plan for these accessibility violations.

    ## Violations
    {{ violations }}

    {% if priority_focus %}
    ## Priority Focus: {{ priority_focus }}
    {% endif %}

    ## Instructions
    1. Group violations by severity
    2. Order by impact and effort
    3. Provide specific fix instructions
    4. Estimate effort for each fix
    5. Identify quick wins

    {{ ctx.output_format }}
  "#
}

/// Remediation plan for accessibility violations
class RemediationPlan {
  plan_id string @description("Unique plan identifier")
  total_issues int @description("Total issues to address")
  estimated_effort string @description("Total estimated effort")
  quick_wins RemediationAction[] @description("Easy fixes with high impact")
  critical_fixes RemediationAction[] @description("Critical issues to fix first")
  recommended_order RemediationAction[] @description("All fixes in recommended order")
  effort_breakdown map<string, int> @description("Count by effort level")
}

// ============================================
// Test Cases
// ============================================

test validate_accessible_response {
  functions [ValidateAccessibility]
  args {
    response {
      response_id "accessible-001"
      primary_modality TEXT
      text {
        content "Your meeting has been scheduled for tomorrow at 2 PM."
        format PLAIN
      }
      voice {
        text "Your meeting has been scheduled for tomorrow at 2 PM."
        ssml "<speak><lang xml:lang=\"en-US\">Your meeting has been scheduled for tomorrow at 2 PM.</lang></speak>"
        language "en-US"
      }
      accessibility {
        aria_label "Meeting confirmation"
        aria_live POLITE
        cognitive_load MINIMAL
        supports_screen_reader true
        supports_keyboard_nav true
        high_contrast_available true
        reduced_motion_safe true
      }
    }
    requirements {
      wcag_level AA
      screen_reader_support true
      voice_control_support true
      reduced_motion false
      high_contrast false
      cognitive_support false
    }
  }
}

test validate_inaccessible_response {
  functions [ValidateAccessibility]
  args {
    response {
      response_id "inaccessible-001"
      primary_modality VISUAL
      visuals [
        {
          element_type IMAGE
          element_id "chart-001"
          title "Sales Chart"
          description null
          content "{...chart data...}"
          alt_text null
          fallback_text null
        }
      ]
      accessibility {
        aria_live OFF
        cognitive_load HIGH
        supports_screen_reader false
        supports_keyboard_nav false
        high_contrast_available false
        reduced_motion_safe false
      }
    }
    requirements {
      wcag_level AA
      screen_reader_support true
      voice_control_support false
      reduced_motion true
      high_contrast true
      cognitive_support true
    }
  }
}

test check_for_blind_user {
  functions [CheckAccessibilityForUser]
  args {
    response {
      response_id "voice-response-001"
      primary_modality VOICE
      voice {
        text "You have 3 new messages."
        language "en-US"
      }
      text {
        content "You have 3 new messages."
        format PLAIN
      }
      accessibility {
        aria_live POLITE
        cognitive_load LOW
        supports_screen_reader true
        supports_keyboard_nav true
        high_contrast_available true
        reduced_motion_safe true
      }
    }
    user_profile {
      needs [VISUAL]
      requirements {
        wcag_level AA
        screen_reader_support true
        voice_control_support true
        reduced_motion false
        high_contrast false
        cognitive_support false
      }
      preferred_modality VOICE
      assistive_technologies ["JAWS", "VoiceOver"]
    }
  }
}
