// Metrics Collection Type System
// Tracking behavioral signals for expertise detection
// Issue #44 - Phase 2: Adaptive Interface Personalization

// ============================================
// Interaction Outcomes
// ============================================

/// Outcome of a user interaction
enum InteractionOutcome {
  SUCCESS @description("Intent completed successfully")
  PARTIAL_SUCCESS @description("Intent partially completed with some issues")
  FAILURE @description("Intent failed to complete")
  ABANDONED @description("User abandoned the interaction")
  HELP_ESCALATION @description("User requested help during interaction")
}

// ============================================
// Trend Analysis
// ============================================

/// Direction of a metric trend over time
enum TrendDirection {
  IMPROVING @description("Metric is getting better over time")
  STABLE @description("Metric is relatively unchanged")
  DECLINING @description("Metric is getting worse over time")
}

// ============================================
// Signal Types
// ============================================

/// Type of behavioral signal detected
enum SignalType {
  FRUSTRATION @description("Signals indicating user frustration")
  MASTERY @description("Signals indicating user mastery")
  LEARNING @description("Signals indicating user is learning")
  CONFUSION @description("Signals indicating user is confused")
  ENGAGEMENT @description("Signals indicating user engagement level")
}

/// Severity of a detected signal
enum SignalSeverity {
  LOW @description("Weak signal, may be noise")
  MEDIUM @description("Notable signal worth monitoring")
  HIGH @description("Strong signal requiring attention")
  CRITICAL @description("Critical signal requiring immediate action")
}

// ============================================
// Interaction Record
// ============================================

/// Record of a single user interaction
class InteractionRecord {
  interaction_id string @description("Unique identifier for this interaction")
  timestamp string @description("ISO 8601 timestamp of the interaction")
  session_id string @description("Session this interaction belongs to")

  // Intent information
  intent_detected string @description("The intent that was detected")
  intent_confidence float @description("Confidence score for intent detection (0.0-1.0)")
  parameters_provided int @description("Number of parameters user provided")
  parameters_required int @description("Number of parameters the intent requires")

  // Outcome information
  outcome InteractionOutcome @description("Final outcome of the interaction")
  completion_time_ms int @description("Time to complete the interaction in milliseconds")
  error_count int @description("Number of errors during the interaction")
  help_requested bool @description("Whether user requested help")
  disambiguation_needed bool @description("Whether clarification was required")

  // Efficiency indicators
  used_shortcut bool @description("Whether user used a shortcut command")
  input_length int @description("Character length of user input")
  retries int @description("Number of retry attempts")
  corrections int @description("Number of corrections made by user")
}

// ============================================
// Metrics Window (Aggregated)
// ============================================

/// Aggregated metrics over a sliding window
class MetricsWindow {
  window_id string @description("Unique identifier for this metrics window")
  window_start string @description("ISO 8601 timestamp of window start")
  window_end string @description("ISO 8601 timestamp of window end")
  interaction_count int @description("Number of interactions in this window")

  // Rate metrics (0.0-1.0)
  success_rate float @description("Proportion of successful interactions")
  partial_success_rate float @description("Proportion of partially successful interactions")
  failure_rate float @description("Proportion of failed interactions")
  abandonment_rate float @description("Proportion of abandoned interactions")
  help_rate float @description("Proportion of interactions where help was requested")
  shortcut_rate float @description("Proportion of interactions using shortcuts")
  error_rate float @description("Average errors per interaction")
  disambiguation_rate float @description("Proportion requiring disambiguation")

  // Time metrics
  avg_completion_time_ms float @description("Average completion time in milliseconds")
  median_completion_time_ms float @description("Median completion time in milliseconds")
  p95_completion_time_ms float @description("95th percentile completion time")

  // Efficiency metrics
  avg_input_length float @description("Average input character length")
  avg_parameters_provided float @description("Average parameters provided per intent")
  avg_retries float @description("Average retry attempts per interaction")

  // Trend indicators
  success_trend TrendDirection @description("Trend of success rate")
  efficiency_trend TrendDirection @description("Trend of completion time")
  engagement_trend TrendDirection @description("Trend of interaction frequency")
}

// ============================================
// Frustration Detection
// ============================================

/// Signals indicating user frustration
class FrustrationSignals {
  is_frustrated bool @description("Whether frustration is detected")
  confidence float @description("Confidence in the detection (0.0-1.0)")
  severity SignalSeverity @description("Severity of the frustration")
  signals string[] @description("List of detected frustration indicators")
  trigger_events string[] @description("Specific events that triggered detection")
  recommendation string? @description("Suggested action to help the user")
}

/// Individual frustration signal
class FrustrationIndicator {
  indicator_type string @description("Type of frustration indicator")
  value float @description("Current value of the indicator")
  threshold float @description("Threshold that triggered detection")
  description string @description("Human-readable description")
  weight float @description("Weight in overall frustration score (0.0-1.0)")
}

// ============================================
// Mastery Detection
// ============================================

/// Signals indicating user mastery
class MasterySignals {
  is_demonstrating_mastery bool @description("Whether mastery is detected")
  confidence float @description("Confidence in the detection (0.0-1.0)")
  mastery_level float @description("Overall mastery score (0.0-1.0)")
  signals string[] @description("List of detected mastery indicators")
  skills_demonstrated string[] @description("Specific skills the user has shown")
  ready_for_advancement bool @description("Whether user is ready for next expertise level")
}

/// Individual mastery signal
class MasteryIndicator {
  indicator_type string @description("Type of mastery indicator")
  value float @description("Current value of the indicator")
  target float @description("Target value for mastery")
  description string @description("Human-readable description")
  weight float @description("Weight in overall mastery score (0.0-1.0)")
}

// ============================================
// Behavioral Analysis
// ============================================

/// Complete behavioral analysis combining all signals
class BehavioralAnalysis {
  analysis_id string @description("Unique identifier for this analysis")
  timestamp string @description("ISO 8601 timestamp of the analysis")
  user_id string @description("User being analyzed")
  session_id string? @description("Session if analysis is session-specific")

  // Core analyses
  metrics_window MetricsWindow @description("Aggregated metrics for the analysis period")
  frustration_signals FrustrationSignals @description("Frustration detection results")
  mastery_signals MasterySignals @description("Mastery detection results")

  // Overall assessment
  overall_sentiment float @description("Overall user sentiment (-1.0 to 1.0)")
  engagement_level float @description("User engagement level (0.0-1.0)")
  confidence float @description("Confidence in the analysis (0.0-1.0)")

  // Recommendations
  recommended_actions string[] @description("Suggested actions based on analysis")
  expertise_adjustment ExpertiseAdjustment? @description("Recommended expertise level change")
}

/// Recommended expertise level adjustment
class ExpertiseAdjustment {
  current_level ExpertiseLevel @description("Current expertise level")
  recommended_level ExpertiseLevel @description("Recommended expertise level")
  direction string @description("UPGRADE, DOWNGRADE, or MAINTAIN")
  confidence float @description("Confidence in the recommendation (0.0-1.0)")
  rationale string @description("Explanation for the recommendation")
  evidence string[] @description("Evidence supporting the recommendation")
}

// ============================================
// Privacy-Aware Storage
// ============================================

/// Privacy mode for metrics collection
enum PrivacyMode {
  FULL @description("Store all interaction details")
  AGGREGATE_ONLY @description("Store only aggregated metrics, no individual records")
  SESSION_ONLY @description("Store details for current session only")
  DISABLED @description("No metrics collection")
}

/// Privacy-compliant metrics store configuration
class MetricsStoreConfig {
  privacy_mode PrivacyMode @description("Privacy mode for storage")
  retention_days int @description("Days to retain metrics (0=session only)")
  aggregate_window_size int @description("Number of interactions per aggregate window")
  enable_frustration_detection bool @description("Whether to detect frustration")
  enable_mastery_detection bool @description("Whether to detect mastery")
  anonymize_intents bool @description("Whether to anonymize intent names")
}

// ============================================
// Metrics Collection Events
// ============================================

/// Event types for metrics collection
enum MetricsEventType {
  INTERACTION_START @description("User started an interaction")
  INTERACTION_END @description("Interaction completed")
  HELP_REQUEST @description("User requested help")
  ERROR_OCCURRED @description("Error occurred during interaction")
  SHORTCUT_USED @description("User used a shortcut")
  RETRY_ATTEMPTED @description("User retried an action")
  SESSION_START @description("New session started")
  SESSION_END @description("Session ended")
  WINDOW_COMPLETE @description("Metrics window completed")
}

/// A metrics collection event
class MetricsEvent {
  event_id string @description("Unique event identifier")
  event_type MetricsEventType @description("Type of event")
  timestamp string @description("ISO 8601 timestamp")
  session_id string @description("Session identifier")
  interaction_id string? @description("Interaction identifier if applicable")
  data map<string, string>? @description("Event-specific data")
}

// ============================================
// Functions
// ============================================

/// Analyze metrics window and detect behavioral signals
function AnalyzeBehavior(
  metrics_window: MetricsWindow,
  recent_interactions: InteractionRecord[]
) -> BehavioralAnalysis {
  client CustomSonnet4
  prompt #"
    Analyze the user's behavioral patterns based on these metrics and interactions.

    Metrics Window:
    {{ metrics_window }}

    Recent Interactions (last {{ recent_interactions | length }}):
    {% for interaction in recent_interactions %}
    - {{ interaction.timestamp }}: {{ interaction.intent_detected }}
      Outcome: {{ interaction.outcome }}, Time: {{ interaction.completion_time_ms }}ms
      Errors: {{ interaction.error_count }}, Help: {{ interaction.help_requested }}
    {% endfor %}

    Analyze for:
    1. Frustration signals (3+ consecutive errors, rapid retries, high help rate)
    2. Mastery signals (high success rate, shortcut usage, efficient completions)
    3. Overall engagement and sentiment
    4. Recommended expertise adjustments

    {{ ctx.output_format }}
  "#
}

/// Detect frustration patterns in recent interactions
function DetectFrustration(
  recent_interactions: InteractionRecord[],
  metrics_window: MetricsWindow
) -> FrustrationSignals {
  client CustomSonnet4
  prompt #"
    Analyze these interactions for signs of user frustration.

    Recent Interactions:
    {% for interaction in recent_interactions %}
    - {{ interaction.timestamp }}: {{ interaction.outcome }}
      Errors: {{ interaction.error_count }}, Retries: {{ interaction.retries }}
      Help: {{ interaction.help_requested }}, Time: {{ interaction.completion_time_ms }}ms
    {% endfor %}

    Aggregated Metrics:
    - Success Rate: {{ metrics_window.success_rate }}
    - Help Rate: {{ metrics_window.help_rate }}
    - Error Rate: {{ metrics_window.error_rate }}
    - Avg Retries: {{ metrics_window.avg_retries }}

    Frustration Triggers to Check:
    1. 3+ consecutive errors
    2. Rapid retry pattern (multiple retries in short time)
    3. Declining success rate trend
    4. Help rate > 40%
    5. High abandonment rate
    6. Increasing error counts

    Return the frustration analysis with specific signals detected.

    {{ ctx.output_format }}
  "#
}

/// Detect mastery patterns in recent interactions
function DetectMastery(
  recent_interactions: InteractionRecord[],
  metrics_window: MetricsWindow
) -> MasterySignals {
  client CustomSonnet4
  prompt #"
    Analyze these interactions for signs of user mastery.

    Recent Interactions:
    {% for interaction in recent_interactions %}
    - {{ interaction.timestamp }}: {{ interaction.outcome }}
      Shortcut: {{ interaction.used_shortcut }}, Time: {{ interaction.completion_time_ms }}ms
      Input Length: {{ interaction.input_length }}, Parameters: {{ interaction.parameters_provided }}/{{ interaction.parameters_required }}
    {% endfor %}

    Aggregated Metrics:
    - Success Rate: {{ metrics_window.success_rate }}
    - Shortcut Rate: {{ metrics_window.shortcut_rate }}
    - Avg Completion Time: {{ metrics_window.avg_completion_time_ms }}ms
    - Efficiency Trend: {{ metrics_window.efficiency_trend }}

    Mastery Indicators to Check:
    1. High success rate (>90%)
    2. Shortcut usage (>50% of eligible interactions)
    3. Fast completion times (below average)
    4. Complete parameter provision
    5. No help requests
    6. Improving efficiency trend

    Return the mastery analysis with specific signals detected.

    {{ ctx.output_format }}
  "#
}
