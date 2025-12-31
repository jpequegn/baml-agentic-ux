// Level Transition Logic
// Smooth, non-jarring expertise level transitions
// Issue #46 - Phase 2: Adaptive Interface Personalization

// Dependencies:
// - ExpertiseLevel from response_generation.baml
// - MetricsWindow, InteractionRecord from metrics_collection.baml
// - UserProfile, SessionMetrics from user_profile_types.baml
// - FrustrationSignals from metrics_collection.baml

// ============================================
// Transition Direction
// ============================================

/// Direction of an expertise level transition
enum TransitionDirection {
  LEVEL_UP @description("User is advancing to a higher expertise level")
  LEVEL_DOWN @description("User is moving to a lower expertise level for more support")
  LATERAL @description("User is moving between domains at the same level")
}

// ============================================
// Transition Policy Configuration
// ============================================

/// Policy configuration for level transitions
class TransitionPolicy {
  // Level Up Criteria
  min_consecutive_successes int @description("Minimum consecutive successes for level up (default: 5)")
  min_success_rate float @description("Minimum success rate for level up (default: 0.8)")
  min_interactions_at_level int @description("Minimum interactions before level change (default: 10)")
  min_shortcut_rate float @description("Minimum shortcut usage rate for advanced levels (default: 0.3)")

  // Level Down Criteria
  max_consecutive_errors int @description("Maximum consecutive errors before level down (default: 3)")
  max_help_rate float @description("Maximum help rate before level down (default: 0.4)")
  frustration_confidence_threshold float @description("Frustration confidence threshold for level down (default: 0.7)")

  // Stability Controls
  transition_cooldown_hours int @description("Hours to wait after a transition (default: 24)")
  gradual_transition bool @description("Whether to transition gradually one level at a time (default: true)")
  require_user_confirmation bool @description("Whether to require user confirmation for transitions (default: false)")

  // Rollback Settings
  enable_rollback bool @description("Whether to allow rollback of recent transitions (default: true)")
  rollback_window_hours int @description("Hours during which rollback is available (default: 48)")
}

// ============================================
// Transition Decision
// ============================================

/// Decision about whether to transition and how
class TransitionDecision {
  should_transition bool @description("Whether a transition should occur")
  direction TransitionDirection? @description("Direction of the transition if applicable")
  from_level ExpertiseLevel @description("Current expertise level")
  to_level ExpertiseLevel? @description("Target expertise level if transitioning")

  // Decision Context
  confidence float @description("Confidence in the transition decision (0.0-1.0)")
  rationale string @description("Explanation for the decision")
  evidence string[] @description("Evidence supporting the decision")

  // User Communication
  user_notification string? @description("Message to show the user")
  notification_tone string? @description("Tone of notification: encouraging, supportive, neutral")

  // Control Flags
  rollback_available bool @description("Whether this transition can be rolled back")
  requires_confirmation bool @description("Whether user confirmation is needed")
  cooldown_active bool @description("Whether cooldown is preventing this transition")
}

// ============================================
// Transition Result
// ============================================

/// Result of executing a transition
class TransitionResult {
  success bool @description("Whether the transition was executed successfully")
  transition_id string @description("Unique identifier for this transition")
  executed_at string @description("ISO 8601 timestamp of execution")

  // Levels
  previous_level ExpertiseLevel @description("Level before transition")
  new_level ExpertiseLevel @description("Level after transition")
  direction TransitionDirection @description("Direction of the transition")

  // Tracking
  rollback_token string? @description("Token for rolling back this transition")
  rollback_expires_at string? @description("ISO 8601 timestamp when rollback expires")

  // User Experience
  notification_sent bool @description("Whether user was notified")
  notification_message string? @description("The notification that was sent")
}

// ============================================
// Rollback Request and Result
// ============================================

/// Request to rollback a recent transition
class RollbackRequest {
  user_id string @description("User requesting the rollback")
  transition_id string? @description("Specific transition to rollback, or latest if null")
  rollback_token string? @description("Token from the original transition")
  reason string? @description("User's reason for requesting rollback")
}

/// Result of a rollback attempt
class RollbackResult {
  success bool @description("Whether the rollback was successful")
  message string @description("Result message")
  restored_level ExpertiseLevel? @description("The restored expertise level")
  reason_failed string? @description("Reason for failure if unsuccessful")
}

// ============================================
// Transition History
// ============================================

/// Record of a past transition
class TransitionRecord {
  transition_id string @description("Unique identifier")
  user_id string @description("User who transitioned")
  timestamp string @description("ISO 8601 timestamp")
  direction TransitionDirection @description("Direction of transition")
  from_level ExpertiseLevel @description("Starting level")
  to_level ExpertiseLevel @description("Ending level")
  rationale string @description("Why the transition occurred")
  was_rolled_back bool @description("Whether this transition was later rolled back")
  triggered_by string @description("What triggered the transition: auto, user_request, admin")
}

/// Complete transition history for a user
class TransitionHistory {
  user_id string @description("User this history belongs to")
  transitions TransitionRecord[] @description("Ordered list of transitions (oldest first)")
  last_transition TransitionRecord? @description("Most recent transition")
  last_transition_at string? @description("Timestamp of last transition")
  total_level_ups int @description("Total number of level ups")
  total_level_downs int @description("Total number of level downs")
  rollback_count int @description("Number of rollbacks performed")
}

// ============================================
// User Notification Templates
// ============================================

/// Predefined notification messages for transitions
class TransitionNotifications {
  to_beginner string @description("Message when transitioning to BEGINNER")
  to_intermediate string @description("Message when transitioning to INTERMEDIATE")
  to_advanced string @description("Message when transitioning to ADVANCED")
  to_expert string @description("Message when transitioning to EXPERT")
  level_down_supportive string @description("Supportive message when going down a level")
  rollback_success string @description("Message when rollback succeeds")
  cooldown_active string @description("Message when cooldown prevents transition")
}

// ============================================
// Functions
// ============================================

/// Evaluate whether a level-up transition should occur
function EvaluateLevelUp(
  profile: UserProfile,
  metrics_window: MetricsWindow,
  session_metrics: SessionMetrics,
  policy: TransitionPolicy
) -> TransitionDecision {
  client CustomSonnet4
  prompt #"
    Evaluate whether the user should level up based on their performance.

    === CURRENT PROFILE ===
    User: {{ profile.user_id }}
    Current Level: {{ profile.expertise_level }}
    Expertise Score: {{ profile.expertise_score }}
    Time at Level: {{ profile.expertise_history.level_tenure_days }} days

    === SESSION METRICS ===
    Consecutive Successes: {{ session_metrics.consecutive_successes }}
    Successes This Session: {{ session_metrics.successes_this_session }}
    Errors This Session: {{ session_metrics.errors_this_session }}
    Shortcuts Used: {{ session_metrics.shortcuts_used | length }}

    === WINDOW METRICS ===
    Success Rate: {{ metrics_window.success_rate }}
    Shortcut Rate: {{ metrics_window.shortcut_rate }}
    Help Rate: {{ metrics_window.help_rate }}
    Interaction Count: {{ metrics_window.interaction_count }}
    Success Trend: {{ metrics_window.success_trend }}

    === POLICY ===
    Min Consecutive Successes: {{ policy.min_consecutive_successes }}
    Min Success Rate: {{ policy.min_success_rate }}
    Min Interactions at Level: {{ policy.min_interactions_at_level }}
    Min Shortcut Rate: {{ policy.min_shortcut_rate }}
    Gradual Transition: {{ policy.gradual_transition }}

    === LEVEL UP CRITERIA ===
    1. {{ policy.min_consecutive_successes }}+ consecutive successes
    2. Success rate > {{ policy.min_success_rate }}
    3. Help rate < 10%
    4. Shortcut usage emerging (rate > {{ policy.min_shortcut_rate }})
    5. Minimum {{ policy.min_interactions_at_level }} interactions at current level

    === NOTIFICATION TEMPLATES ===
    - BEGINNER → INTERMEDIATE: "You're getting the hang of this! I'll show you some shortcuts."
    - INTERMEDIATE → ADVANCED: "Nice progress! I'll be more concise now."
    - ADVANCED → EXPERT: "You're a pro! Enabling power-user features."
    - Any Level Up: Encouraging, celebratory tone

    Evaluate all criteria and decide whether to level up.
    If yes, provide an encouraging, non-condescending notification.
    If no, explain what criteria are not yet met.

    {{ ctx.output_format }}
  "#
}

/// Evaluate whether a level-down transition should occur
function EvaluateLevelDown(
  profile: UserProfile,
  session_metrics: SessionMetrics,
  frustration_signals: FrustrationSignals,
  policy: TransitionPolicy
) -> TransitionDecision {
  client CustomSonnet4
  prompt #"
    Evaluate whether the user should level down for more support.

    === CURRENT PROFILE ===
    User: {{ profile.user_id }}
    Current Level: {{ profile.expertise_level }}
    Expertise Score: {{ profile.expertise_score }}

    === SESSION METRICS ===
    Consecutive Errors: {{ session_metrics.consecutive_errors }}
    Errors This Session: {{ session_metrics.errors_this_session }}
    Help Topics Accessed: {{ session_metrics.help_topics_accessed | length }}

    === FRUSTRATION SIGNALS ===
    Is Frustrated: {{ frustration_signals.is_frustrated }}
    Frustration Confidence: {{ frustration_signals.confidence }}
    Severity: {{ frustration_signals.severity }}
    Signals: {{ frustration_signals.signals }}
    Recommendation: {{ frustration_signals.recommendation }}

    === POLICY ===
    Max Consecutive Errors: {{ policy.max_consecutive_errors }}
    Max Help Rate: {{ policy.max_help_rate }}
    Frustration Confidence Threshold: {{ policy.frustration_confidence_threshold }}
    Gradual Transition: {{ policy.gradual_transition }}

    === LEVEL DOWN CRITERIA ===
    1. {{ policy.max_consecutive_errors }}+ consecutive errors
    2. Help rate > {{ policy.max_help_rate }}
    3. Frustration detected with confidence > {{ policy.frustration_confidence_threshold }}
    4. User explicitly requests more help

    === NOTIFICATION GUIDELINES ===
    - Be supportive, not condescending
    - Frame as "providing more guidance" not "dumbing down"
    - Example: "I'll provide more guidance to help you out."
    - Tone should be warm and helpful

    Evaluate criteria and decide whether to level down.
    If yes, provide a supportive, non-condescending notification.
    Ensure the decision prioritizes user experience and learning.

    {{ ctx.output_format }}
  "#
}

/// Generate a user-friendly notification for a transition
function GenerateTransitionNotification(
  direction: TransitionDirection,
  from_level: ExpertiseLevel,
  to_level: ExpertiseLevel
) -> string {
  client CustomSonnet4
  prompt #"
    Generate a brief, friendly notification for an expertise level transition.

    Direction: {{ direction }}
    From: {{ from_level }}
    To: {{ to_level }}

    Guidelines:
    - Keep it to 1-2 sentences
    - Be encouraging for level ups
    - Be supportive (not condescending) for level downs
    - Explain what will change for the user
    - Use a warm, conversational tone

    Standard Messages (can customize):
    - NOVICE → BEGINNER: "Great start! You're ready for some handy tips."
    - BEGINNER → INTERMEDIATE: "You're getting the hang of this! I'll show you some shortcuts."
    - INTERMEDIATE → ADVANCED: "Nice progress! I'll be more concise now."
    - ADVANCED → EXPERT: "You're a pro! Enabling power-user features."
    - Any → Lower: "I'll provide more guidance to help you out."

    Return just the notification message as a plain string.
  "#
}

/// Get the default transition policy
function GetDefaultTransitionPolicy() -> TransitionPolicy {
  client CustomSonnet4
  prompt #"
    Generate the default transition policy configuration.

    Use these standard values:
    - min_consecutive_successes: 5
    - min_success_rate: 0.8
    - min_interactions_at_level: 10
    - min_shortcut_rate: 0.3
    - max_consecutive_errors: 3
    - max_help_rate: 0.4
    - frustration_confidence_threshold: 0.7
    - transition_cooldown_hours: 24
    - gradual_transition: true
    - require_user_confirmation: false
    - enable_rollback: true
    - rollback_window_hours: 48

    {{ ctx.output_format }}
  "#
}
