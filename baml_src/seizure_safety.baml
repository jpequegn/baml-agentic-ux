// Seizure Safety Validation
// BAML types for photosensitive seizure safety validation
// Issue #74 - Task 4.8: Seizure Safety Checker
// Part of #27 - Phase 4: LUI Accessibility Standards

// Dependencies:
// - ComplianceLevel from accessibility_types.baml

// ============================================
// WCAG 2.3 Criteria
// ============================================

/// WCAG 2.3 Seizure and Physical Reactions criteria
enum SeizureCriterion {
  SC_2_3_1 @description("Three Flashes or Below Threshold (Level A)")
  SC_2_3_2 @description("Three Flashes (Level AAA)")
  SC_2_3_3 @description("Animation from Interactions (Level AAA)")
}

/// Types of potentially dangerous flashes
enum FlashType {
  GENERAL @description("Standard luminance flash")
  RED @description("Red/saturated red flash (more dangerous)")
  PATTERN @description("Repeating pattern that could flash")
}

// ============================================
// Flash Analysis
// ============================================

/// Analysis of flash content
class FlashAnalysis {
  has_flashes bool @description("Whether content has flashing elements")
  flash_frequency_hz float @description("Measured flash frequency in Hz")
  flash_area_percent float @description("Flash area as percentage of FOV")
  flash_type FlashType @description("Type of flash detected")
  is_safe bool @description("Whether the flash is within safe limits")
  consecutive_flashes int @description("Number of consecutive flashes")
  exceeds_frequency bool @description("Whether frequency exceeds safe limit")
  exceeds_area bool @description("Whether area exceeds safe limit")
  is_red_flash bool @description("Whether flash contains dangerous red")
}

// ============================================
// Animation Configuration
// ============================================

/// Configuration for an animation
class AnimationConfig {
  animation_id string @description("Identifier for the animation")
  frequency_hz float @description("Animation frequency in Hz")
  duration_ms float @description("Animation duration in milliseconds")
  area_percent float @description("Area covered as percentage of viewport")
  has_flash bool @description("Whether animation includes flashing")
  is_red bool @description("Whether animation contains red flash")
  auto_plays bool @description("Whether animation auto-plays")
  has_pause_control bool @description("Whether pause control is available")
  has_stop_control bool @description("Whether stop control is available")
  respects_reduced_motion bool @description("Whether it respects prefers-reduced-motion")
  loops bool @description("Whether animation loops")
  loop_count int @description("Number of loops (-1 for infinite)")
}

/// Configuration for media content
class MediaConfig {
  media_id string @description("Identifier for the media")
  media_type string @description("Type of media (video, gif, etc.)")
  auto_plays bool @description("Whether media auto-plays")
  has_pause_control bool @description("Whether pause control is available")
  has_stop_control bool @description("Whether stop control is available")
  duration_seconds float @description("Duration of media in seconds")
  has_flashing_content bool @description("Whether media contains flashing")
  flash_frequency_hz float @description("Flash frequency if applicable")
  respects_reduced_motion bool @description("Whether it respects prefers-reduced-motion")
}

/// Complete content configuration for seizure safety check
class ContentConfig {
  content_id string @description("Identifier for the content")
  animations AnimationConfig[] @description("List of animation configurations")
  media MediaConfig[] @description("List of media configurations")
  has_auto_updating_content bool @description("Whether content auto-updates")
  update_frequency_hz float @description("Frequency of updates if applicable")
  has_motion_trigger bool @description("Whether motion is triggered by user")
  respects_reduced_motion bool @description("Global reduced motion support")
}

// ============================================
// Violation Types
// ============================================

/// Severity of seizure safety violations
enum SeizureViolationSeverity {
  CRITICAL @description("Immediate seizure risk - must fix")
  MAJOR @description("Significant risk - should fix")
  MINOR @description("Reduced safety - consider fixing")
  ADVISORY @description("Safety improvement suggestion")
}

/// A seizure safety violation
class SeizureViolation {
  criterion SeizureCriterion @description("WCAG criterion violated")
  severity SeizureViolationSeverity @description("Severity level")
  description string @description("Human-readable description")
  location string @description("Where the violation was found")
  remediation string @description("Suggested fix")
  flash_type FlashType? @description("Type of flash if applicable")
  measured_value float? @description("The measured value that caused violation")
  threshold_value float? @description("The threshold that was exceeded")
}

// ============================================
// Result Types
// ============================================

/// Result of animation safety analysis
class AnimationSafetyResult {
  animation_id string @description("ID of the animation analyzed")
  passes bool @description("Whether animation passes safety checks")
  score float @description("Safety score from 0.0 to 1.0")
  violations SeizureViolation[] @description("List of safety violations")
  flash_analysis FlashAnalysis? @description("Flash content analysis")
  has_required_controls bool @description("Whether required controls exist")
  respects_user_preferences bool @description("Whether user motion preferences respected")
  recommendations string[] @description("Suggested improvements")
  summary string @description("Human-readable summary")
}

/// Result of seizure safety validation
class SeizureSafetyResult {
  content_id string @description("ID of content validated")
  target_level ComplianceLevel @description("Target compliance level")
  passes bool @description("Whether content passes safety checks")
  score float @description("Safety score from 0.0 to 1.0")
  violations SeizureViolation[] @description("List of safety violations")
  animation_results AnimationSafetyResult[] @description("Results for individual animations")
  media_results AnimationSafetyResult[] @description("Results for individual media")
  flash_analysis FlashAnalysis? @description("Overall flash analysis")
  has_controls bool @description("Whether required controls exist")
  respects_reduced_motion bool @description("Whether reduced motion is respected")
  criteria_met SeizureCriterion[] @description("WCAG criteria that are met")
  criteria_failed SeizureCriterion[] @description("WCAG criteria that failed")
  recommendations string[] @description("Suggested improvements")
  summary string @description("Human-readable summary")
}

// ============================================
// Safety Thresholds
// ============================================

/// Safety thresholds for seizure prevention
class SeizureSafetyThresholds {
  max_flash_frequency_hz float @description("Maximum safe flash frequency (3Hz per WCAG)")
  max_flash_area_percent float @description("Maximum flash area as % of FOV (10%)")
  red_flash_frequency_multiplier float @description("Stricter limit for red flashes (0.67)")
  max_consecutive_flashes int @description("Maximum consecutive flashes allowed")
  max_auto_play_duration_seconds float @description("Max auto-play before requiring controls")
}

// ============================================
// AI Validation Functions
// ============================================

/// Analyze flash content for seizure safety
function AnalyzeFlashSafety(
  frequency_hz: float,
  area_percent: float,
  is_red: bool
) -> FlashAnalysis {
  client CustomSonnet4
  prompt #"
    Analyze this flash content for seizure safety per WCAG 2.3.

    Flash Parameters:
    - Frequency: {{ frequency_hz }} Hz
    - Area: {{ area_percent }}% of viewport
    - Is Red Flash: {{ is_red }}

    Safety thresholds:
    | Check | Threshold | Notes |
    |-------|-----------|-------|
    | Flash frequency | ≤3 Hz | Critical threshold |
    | Flash area | <10% FOV | Critical threshold |
    | Red flash | 67% of normal limit | More dangerous |

    Analysis rules:
    1. Any flash >3Hz is dangerous (CRITICAL)
    2. Red flashes >2Hz are dangerous (stricter limit)
    3. Flash area >10% increases danger
    4. Consecutive flashes multiply risk

    Determine if this flash configuration is safe.

    {{ ctx.output_format }}
  "#
}

/// Analyze animation for seizure safety
function AnalyzeAnimationSafety(
  config: AnimationConfig,
  target_level: ComplianceLevel
) -> AnimationSafetyResult {
  client CustomSonnet4
  prompt #"
    Analyze this animation for seizure safety per WCAG 2.3.

    Animation Configuration:
    {{ config }}

    Target Level: {{ target_level }}

    Safety requirements:
    | Criterion | Level | Requirement |
    |-----------|-------|-------------|
    | 2.3.1 | A | No more than 3 flashes/sec OR below threshold |
    | 2.3.2 | AAA | No more than 3 flashes/sec (stricter) |
    | 2.3.3 | AAA | Motion can be disabled |

    Control requirements:
    - Auto-playing animations MUST have pause/stop controls
    - MUST respect prefers-reduced-motion
    - AAA: Infinite loops should be avoidable

    Check for:
    1. Flash frequency violations
    2. Flash area violations
    3. Red flash special handling
    4. Missing animation controls
    5. Reduced motion support

    {{ ctx.output_format }}
  "#
}

/// Validate complete content for seizure safety
function ValidateSeizureSafety(
  content: ContentConfig,
  target_level: ComplianceLevel
) -> SeizureSafetyResult {
  client CustomSonnet4
  prompt #"
    Validate this content for seizure safety per WCAG 2.3.

    Content Configuration:
    {{ content }}

    Target Level: {{ target_level }}

    WCAG 2.3 Guidelines:

    2.3.1 Three Flashes or Below Threshold (Level A):
    - No content flashes more than 3 times per second
    - OR the flash is below the general flash and red flash thresholds

    2.3.2 Three Flashes (Level AAA):
    - No content flashes more than 3 times per second (no exceptions)

    2.3.3 Animation from Interactions (Level AAA):
    - Motion triggered by interaction can be disabled
    - Unless motion is essential

    Check all animations and media for:
    1. Flash frequency (≤3Hz)
    2. Flash area (<10% of viewport)
    3. Red flash special limits
    4. Animation controls (pause/stop)
    5. Prefers-reduced-motion support
    6. Auto-update frequency

    Calculate overall score and determine which criteria are met.

    {{ ctx.output_format }}
  "#
}

// ============================================
// Test Cases
// ============================================

test safe_animation {
  functions [AnalyzeAnimationSafety]
  args {
    config {
      animation_id "fade_in"
      frequency_hz 2.0
      duration_ms 500
      area_percent 5.0
      has_flash false
      is_red false
      auto_plays true
      has_pause_control true
      has_stop_control true
      respects_reduced_motion true
      loops false
      loop_count 0
    }
    target_level LEVEL_AA
  }
}

test unsafe_flash_frequency {
  functions [AnalyzeAnimationSafety]
  args {
    config {
      animation_id "strobe"
      frequency_hz 5.0
      duration_ms 1000
      area_percent 5.0
      has_flash true
      is_red false
      auto_plays true
      has_pause_control true
      has_stop_control true
      respects_reduced_motion true
      loops true
      loop_count -1
    }
    target_level LEVEL_A
  }
}

test unsafe_red_flash {
  functions [AnalyzeAnimationSafety]
  args {
    config {
      animation_id "red_strobe"
      frequency_hz 2.5
      duration_ms 1000
      area_percent 15.0
      has_flash true
      is_red true
      auto_plays true
      has_pause_control false
      has_stop_control false
      respects_reduced_motion false
      loops true
      loop_count -1
    }
    target_level LEVEL_AA
  }
}

test content_validation {
  functions [ValidateSeizureSafety]
  args {
    content {
      content_id "homepage"
      animations [
        {
          animation_id "hero_fade"
          frequency_hz 1.0
          duration_ms 300
          area_percent 30.0
          has_flash false
          is_red false
          auto_plays true
          has_pause_control true
          has_stop_control true
          respects_reduced_motion true
          loops false
          loop_count 0
        }
      ]
      media [
        {
          media_id "promo_video"
          media_type "video"
          auto_plays false
          has_pause_control true
          has_stop_control true
          duration_seconds 30.0
          has_flashing_content false
          flash_frequency_hz 0.0
          respects_reduced_motion true
        }
      ]
      has_auto_updating_content false
      update_frequency_hz 0.0
      has_motion_trigger false
      respects_reduced_motion true
    }
    target_level LEVEL_AA
  }
}
