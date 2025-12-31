// Expertise Detection Algorithm
// Weighted scoring model for adaptive expertise level determination
// Issue #45 - Phase 2: Adaptive Interface Personalization

// Dependencies:
// - ExpertiseLevel from response_generation.baml
// - MetricsWindow, InteractionRecord from metrics_collection.baml
// - UserProfile from user_profile_types.baml

// ============================================
// Expertise Factor Weights
// ============================================

/// Individual factor contributing to expertise score
class ExpertiseFactor {
  factor_name string @description("Name of the expertise factor")
  weight float @description("Weight in overall score (0.0-1.0, sum to 1.0)")
  raw_value float @description("Raw measured value (0.0-1.0)")
  weighted_value float @description("Value after applying weight")
  confidence float @description("Confidence in this measurement (0.0-1.0)")
  evidence string[] @description("Evidence supporting this value")
}

/// Complete breakdown of expertise factors
class ExpertiseFactorBreakdown {
  command_fluency ExpertiseFactor @description("Command formulation efficiency (weight: 0.30)")
  success_rate ExpertiseFactor @description("Task completion success rate (weight: 0.25)")
  self_sufficiency ExpertiseFactor @description("Independence from help/disambiguation (weight: 0.25)")
  engagement ExpertiseFactor @description("Interaction frequency and consistency (weight: 0.20)")
}

// ============================================
// Expertise Estimate Result
// ============================================

/// Result of expertise level estimation
class ExpertiseEstimate {
  estimated_level ExpertiseLevel @description("Determined expertise level")
  expertise_score float @description("Numeric score (0.0-1.0)")
  previous_score float? @description("Previous score for comparison")
  score_delta float? @description("Change from previous score")

  // Factor breakdown
  factor_breakdown ExpertiseFactorBreakdown @description("Individual factor contributions")

  // Confidence and cold start
  confidence float @description("Overall confidence in estimate (0.0-1.0)")
  is_cold_start bool @description("Whether this is a cold start estimate")
  cold_start_reason string? @description("Reason for cold start if applicable")
  interactions_analyzed int @description("Number of interactions used for estimation")

  // EMA tracking
  ema_alpha float @description("Exponential moving average alpha value used")
  ema_applied bool @description("Whether EMA smoothing was applied")

  // Recommendations
  level_stable bool @description("Whether the current level appears stable")
  recommended_action string? @description("Suggested action (UPGRADE, DOWNGRADE, MONITOR, MAINTAIN)")
  action_rationale string? @description("Explanation for the recommendation")
}

// ============================================
// Level Thresholds
// ============================================

/// Threshold configuration for expertise levels
class LevelThreshold {
  level ExpertiseLevel @description("The expertise level")
  min_score float @description("Minimum score for this level (inclusive)")
  max_score float @description("Maximum score for this level (exclusive)")
  description string @description("Description of typical user at this level")
}

/// Complete threshold configuration
class ExpertiseThresholds {
  thresholds LevelThreshold[] @description("Ordered list of level thresholds")
  upgrade_buffer float @description("Buffer score required above threshold for upgrade")
  downgrade_buffer float @description("Buffer score required below threshold for downgrade")
}

// ============================================
// Cold Start Configuration
// ============================================

/// Configuration for handling cold start scenarios
class ColdStartConfig {
  min_interactions int @description("Minimum interactions before confident estimation")
  default_level ExpertiseLevel @description("Default level for new users")
  default_score float @description("Default score for new users")
  default_confidence float @description("Confidence for cold start estimates")
  ramp_up_interactions int @description("Interactions needed to reach full confidence")
}

// ============================================
// Detection Configuration
// ============================================

/// Complete configuration for expertise detection
class ExpertiseDetectionConfig {
  // Factor weights (must sum to 1.0)
  command_fluency_weight float @description("Weight for command fluency (default: 0.30)")
  success_rate_weight float @description("Weight for success rate (default: 0.25)")
  self_sufficiency_weight float @description("Weight for self-sufficiency (default: 0.25)")
  engagement_weight float @description("Weight for engagement (default: 0.20)")

  // EMA configuration
  ema_alpha float @description("EMA smoothing factor (default: 0.3)")

  // Level thresholds
  thresholds ExpertiseThresholds @description("Level threshold configuration")

  // Cold start
  cold_start ColdStartConfig @description("Cold start handling configuration")

  // Stability
  stability_window int @description("Number of estimates to consider for stability")
  stability_threshold float @description("Max score variance for stable level")
}

// ============================================
// Functions
// ============================================

/// Estimate user expertise level from behavioral metrics
function EstimateExpertise(
  metrics_window: MetricsWindow,
  recent_interactions: InteractionRecord[],
  previous_estimate: ExpertiseEstimate?
) -> ExpertiseEstimate {
  client CustomSonnet4
  prompt #"
    Estimate the user's expertise level based on behavioral metrics.

    === METRICS WINDOW ===
    {{ metrics_window }}

    === RECENT INTERACTIONS ({{ recent_interactions | length }}) ===
    {% for interaction in recent_interactions %}
    - {{ interaction.timestamp }}: {{ interaction.intent_detected }}
      Outcome: {{ interaction.outcome }}
      Shortcut: {{ interaction.used_shortcut }}, Help: {{ interaction.help_requested }}
      Time: {{ interaction.completion_time_ms }}ms, Input Length: {{ interaction.input_length }}
      Params: {{ interaction.parameters_provided }}/{{ interaction.parameters_required }}
    {% endfor %}

    {% if previous_estimate %}
    === PREVIOUS ESTIMATE ===
    Level: {{ previous_estimate.estimated_level }}
    Score: {{ previous_estimate.expertise_score }}
    Confidence: {{ previous_estimate.confidence }}
    {% endif %}

    === FACTOR WEIGHTS ===
    1. Command Fluency (30%): Efficient command formulation
       - Concise input (shorter = better for same intent)
       - Complete parameter provision
       - Use of shortcuts

    2. Success Rate (25%): Task completion effectiveness
       - SUCCESS and PARTIAL_SUCCESS outcomes
       - Low error counts
       - Few retries

    3. Self-Sufficiency (25%): Independence from assistance
       - No help requests
       - No disambiguation needed
       - Confident interactions

    4. Engagement (20%): Consistent interaction patterns
       - Regular interaction frequency
       - Exploration of features
       - Sustained usage over time

    === LEVEL THRESHOLDS ===
    - NOVICE: 0.0 - 0.2
    - BEGINNER: 0.2 - 0.4
    - INTERMEDIATE: 0.4 - 0.6
    - ADVANCED: 0.6 - 0.8
    - EXPERT: 0.8 - 1.0

    === ALGORITHM ===
    1. Calculate each factor's raw value (0.0-1.0)
    2. Apply weights to get weighted values
    3. Sum weighted values for total score
    4. Apply EMA smoothing if previous estimate exists (alpha=0.3):
       new_score = alpha * current + (1-alpha) * previous
    5. Map score to expertise level using thresholds
    6. Apply hysteresis (require buffer for level changes)

    === COLD START HANDLING ===
    If fewer than 10 interactions:
    - is_cold_start: true
    - Reduce confidence proportionally
    - Use conservative level estimates
    - Default to INTERMEDIATE for brand new users

    Calculate the expertise estimate with full factor breakdown.

    {{ ctx.output_format }}
  "#
}

/// Get default expertise detection configuration
function GetDefaultExpertiseConfig() -> ExpertiseDetectionConfig {
  client CustomSonnet4
  prompt #"
    Generate the default expertise detection configuration.

    Use these standard values:
    - command_fluency_weight: 0.30
    - success_rate_weight: 0.25
    - self_sufficiency_weight: 0.25
    - engagement_weight: 0.20
    - ema_alpha: 0.3

    Level thresholds:
    - NOVICE: 0.0 - 0.2 (New to the system, needs extensive guidance)
    - BEGINNER: 0.2 - 0.4 (Some familiarity, still learning)
    - INTERMEDIATE: 0.4 - 0.6 (Regular user, comfortable with basics)
    - ADVANCED: 0.6 - 0.8 (Power user, uses advanced features)
    - EXPERT: 0.8 - 1.0 (Deep system knowledge, optimal efficiency)

    Upgrade/downgrade buffer: 0.05

    Cold start:
    - min_interactions: 10
    - default_level: INTERMEDIATE
    - default_score: 0.5
    - default_confidence: 0.3
    - ramp_up_interactions: 50

    Stability:
    - stability_window: 5
    - stability_threshold: 0.1

    {{ ctx.output_format }}
  "#
}

/// Analyze expertise trend over multiple estimates
function AnalyzeExpertiseTrend(
  estimates: ExpertiseEstimate[]
) -> TrendDirection {
  client CustomSonnet4
  prompt #"
    Analyze the trend in expertise scores over time.

    Expertise Estimates (oldest to newest):
    {% for estimate in estimates %}
    - Score: {{ estimate.expertise_score }}, Level: {{ estimate.estimated_level }}
      Confidence: {{ estimate.confidence }}, Interactions: {{ estimate.interactions_analyzed }}
    {% endfor %}

    Determine if the user's expertise is:
    - IMPROVING: Consistent score increases (>0.05 improvement)
    - STABLE: Minimal variance (<0.05 change)
    - DECLINING: Consistent score decreases (>0.05 decline)

    Consider:
    1. Overall direction of score changes
    2. Magnitude of changes
    3. Consistency of the trend
    4. Confidence levels of estimates

    {{ ctx.output_format }}
  "#
}
