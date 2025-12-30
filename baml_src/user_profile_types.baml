// User Profile Type System
// Core type definitions for user profiles, expertise levels, and interaction history
// Issue #43 - Phase 2: Adaptive Interface Personalization

// NOTE: Some types reuse existing enums from other BAML files:
// - ExpertiseLevel from response_generation.baml
// - VerbosityLevel from response_generation.baml
// - InteractionStyle from usability_analysis.baml
// - UserPreferences from intent_extraction.baml (different structure, so we use ProfilePreferences)

// ============================================
// Profile-Specific Verbosity (extends base VerbosityLevel)
// ============================================

/// Profile-specific verbosity with additional tutorial mode
enum ProfileVerbosity {
  MINIMAL @description("Essential information only, no elaboration")
  STANDARD @description("Normal detail level, balanced explanations")
  DETAILED @description("Comprehensive information with context")
  TUTORIAL @description("Full educational mode with step-by-step guidance")
}

/// Profile-specific interaction style
enum ProfileInteractionStyle {
  CONVERSATIONAL @description("Friendly, casual tone with natural language")
  PROFESSIONAL @description("Formal, business-appropriate communication")
  TERSE @description("Brief, direct responses without pleasantries")
  EDUCATIONAL @description("Teaching-oriented with explanations and examples")
}

// ============================================
// Transition Triggers
// ============================================

/// Events that trigger expertise level transitions
enum TransitionTrigger {
  CONSECUTIVE_SUCCESS @description("Multiple successful interactions in a row")
  SHORTCUT_ADOPTION @description("User starts using shortcuts and advanced features")
  REDUCED_HELP_SEEKING @description("Decreased reliance on help and guidance")
  CONSECUTIVE_ERRORS @description("Multiple errors suggest level too high")
  HIGH_HELP_RATE @description("Frequent help requests suggest level too high")
  USER_REQUEST @description("User explicitly requested level change")
  TIME_DECAY @description("Inactivity caused skill regression estimate")
  DOMAIN_CHANGE @description("User switched to unfamiliar domain")
}

// ============================================
// Learning Mode Configuration
// ============================================

/// How the system should adapt to user behavior
enum LearningMode {
  ACTIVE @description("Actively adjust based on real-time behavior")
  PASSIVE @description("Learn patterns but wait for explicit confirmation")
  DISABLED @description("No automatic adaptation, manual control only")
}

/// Feedback frequency preference
enum FeedbackFrequency {
  ALWAYS @description("Confirm every action and change")
  SIGNIFICANT @description("Confirm only significant changes")
  NEVER @description("Silent operation, no confirmations")
}

// ============================================
// Interaction Metrics
// ============================================

/// Aggregate metrics for user interaction history
class InteractionMetrics {
  total_interactions int @description("Total number of interactions")
  session_count int @description("Number of distinct sessions")
  successful_intents int @description("Intents that completed successfully")
  failed_intents int @description("Intents that failed or were abandoned")
  success_rate float @description("Ratio of successful to total intents (0.0-1.0)")
  avg_completion_time_ms float @description("Average time to complete an intent")
  shortcut_usage_rate float @description("Ratio of shortcuts used vs available (0.0-1.0)")
  help_requests int @description("Number of help/assistance requests")
  disambiguation_requests int @description("Number of clarification prompts needed")
  correction_rate float @description("Rate of user corrections to system actions (0.0-1.0)")
  cancellation_rate float @description("Rate of cancelled operations (0.0-1.0)")
}

/// Metrics specific to the current session
class SessionMetrics {
  session_id string @description("Unique identifier for this session")
  session_start string @description("ISO 8601 timestamp when session started")
  interactions_this_session int @description("Number of interactions in current session")
  successes_this_session int @description("Successful intents this session")
  errors_this_session int @description("Failed intents this session")
  consecutive_errors int @description("Current streak of consecutive errors")
  consecutive_successes int @description("Current streak of consecutive successes")
  new_features_used string[] @description("Features used for the first time")
  shortcuts_used string[] @description("Shortcuts invoked this session")
  help_topics_accessed string[] @description("Help topics the user accessed")
}

// ============================================
// Expertise Transitions
// ============================================

/// Record of a user's expertise level change
class ExpertiseTransition {
  transition_id string @description("Unique identifier for this transition")
  previous_level ExpertiseLevel @description("Level before the transition")
  new_level ExpertiseLevel @description("Level after the transition")
  trigger TransitionTrigger @description("What caused the transition")
  timestamp string @description("ISO 8601 timestamp of the transition")
  confidence float @description("Confidence in the transition decision (0.0-1.0)")
  evidence_summary string? @description("Summary of evidence supporting the transition")
  user_confirmed bool @description("Whether user explicitly confirmed this change")
}

/// History of expertise level transitions
class ExpertiseHistory {
  transitions ExpertiseTransition[] @description("Ordered list of transitions (oldest first)")
  current_level ExpertiseLevel @description("Current expertise level")
  level_tenure_days int @description("Days at current level")
  stability_score float @description("How stable the current level appears (0.0-1.0)")
}

// ============================================
// Domain Expertise
// ============================================

/// User's expertise within a specific domain
class DomainExpertise {
  domain_id string @description("Identifier for the domain")
  domain_name string @description("Human-readable domain name")
  expertise_level ExpertiseLevel @description("User's level in this domain")
  expertise_score float @description("Numeric expertise score (0.0-1.0)")
  interaction_count int @description("Number of interactions in this domain")
  last_interaction string? @description("ISO 8601 timestamp of last domain interaction")
  key_concepts_known string[] @description("Concepts the user has demonstrated understanding of")
}

// ============================================
// Profile Preferences (distinct from intent_extraction.UserPreferences)
// ============================================

/// User-configurable preferences for profile-based adaptation
class ProfilePreferences {
  preferred_verbosity ProfileVerbosity @description("Desired response detail level")
  preferred_style ProfileInteractionStyle @description("Desired communication style")
  learning_mode LearningMode @description("How the system should adapt")
  feedback_frequency FeedbackFrequency @description("How often to confirm actions")
  enable_shortcuts bool @description("Whether to suggest/enable shortcuts")
  enable_proactive_help bool @description("Whether to offer unsolicited assistance")
  preferred_language string? @description("ISO 639-1 language code preference")
  timezone string? @description("User's timezone (IANA format)")
}

// ============================================
// Privacy and Consent
// ============================================

/// User's consent for profiling and data collection
class ProfilingConsent {
  profiling_enabled bool @description("Master switch for behavior profiling")
  store_interaction_history bool @description("Permission to store interaction history")
  allow_expertise_inference bool @description("Permission to infer expertise from behavior")
  allow_preference_learning bool @description("Permission to learn preferences automatically")
  data_retention_days int @description("How long to retain profile data (0=session only)")
  consent_timestamp string @description("ISO 8601 timestamp when consent was given")
  consent_version string @description("Version of consent agreement accepted")
}

// ============================================
// Main User Profile
// ============================================

/// Complete user profile for adaptive personalization
class UserProfile {
  // Identity
  user_id string @description("Unique user identifier")
  profile_version string @description("Schema version for migration support")
  created_at string @description("ISO 8601 timestamp when profile was created")
  updated_at string @description("ISO 8601 timestamp of last update")

  // Expertise
  expertise_level ExpertiseLevel @description("Current overall expertise level")
  expertise_score float @description("Numeric expertise score (0.0-1.0)")
  expertise_confidence float @description("Confidence in expertise assessment (0.0-1.0)")
  expertise_history ExpertiseHistory? @description("History of level transitions")
  domain_expertise DomainExpertise[]? @description("Domain-specific expertise levels")

  // Preferences
  preferences ProfilePreferences @description("User-configurable preferences")

  // Metrics
  interaction_metrics InteractionMetrics? @description("Aggregate interaction statistics")
  current_session SessionMetrics? @description("Current session metrics")

  // Consent
  consent ProfilingConsent @description("Privacy and consent settings")
}

// ============================================
// Profile Update Types
// ============================================

/// Type of profile update
enum ProfileUpdateType {
  EXPERTISE_CHANGE @description("Expertise level changed")
  PREFERENCE_CHANGE @description("User preference updated")
  METRICS_UPDATE @description("Interaction metrics updated")
  CONSENT_CHANGE @description("Privacy/consent settings changed")
  SESSION_START @description("New session started")
  SESSION_END @description("Session ended")
}

/// Record of a profile update
class ProfileUpdate {
  update_id string @description("Unique identifier for this update")
  update_type ProfileUpdateType @description("Type of update")
  timestamp string @description("ISO 8601 timestamp of the update")
  field_path string @description("Dot-notation path to updated field")
  previous_value string? @description("Previous value (JSON-encoded if complex)")
  new_value string @description("New value (JSON-encoded if complex)")
  reason string? @description("Reason for the update")
}

// ============================================
// Profile Summary (for quick access)
// ============================================

/// Lightweight profile summary for efficient access
class ProfileSummary {
  user_id string @description("User identifier")
  expertise_level ExpertiseLevel @description("Current expertise level")
  preferred_verbosity ProfileVerbosity @description("Verbosity preference")
  preferred_style ProfileInteractionStyle @description("Communication style")
  profiling_enabled bool @description("Whether profiling is active")
  session_count int @description("Total sessions")
  success_rate float @description("Overall success rate")
}

// ============================================
// Functions (to be implemented)
// ============================================

/// Create a new user profile with default settings
function CreateUserProfile(user_id: string) -> UserProfile {
  client CustomSonnet4
  prompt #"
    Create a new user profile for user: {{user_id}}

    Use these default settings:
    - expertise_level: INTERMEDIATE (standard starting point)
    - expertise_score: 0.5
    - expertise_confidence: 0.3 (low confidence for new user)
    - preferred_verbosity: STANDARD
    - preferred_style: CONVERSATIONAL
    - learning_mode: ACTIVE
    - feedback_frequency: SIGNIFICANT
    - profiling_enabled: true
    - data_retention_days: 90

    Generate appropriate timestamps (current time in ISO 8601).
    Generate a unique profile_version string.

    {{ ctx.output_format }}
  "#
}

/// Get a lightweight profile summary
function GetProfileSummary(profile: UserProfile) -> ProfileSummary {
  client CustomSonnet4
  prompt #"
    Extract a lightweight summary from this user profile:

    {{ profile }}

    Return only the essential fields for quick access.

    {{ ctx.output_format }}
  "#
}

/// Determine if expertise transition is needed based on metrics
function EvaluateExpertiseTransition(
  profile: UserProfile,
  session_metrics: SessionMetrics
) -> ExpertiseTransition? {
  client CustomSonnet4
  prompt #"
    Evaluate whether the user should transition to a different expertise level.

    Current Profile:
    {{ profile }}

    Session Metrics:
    {{ session_metrics }}

    Transition Criteria:
    - UPGRADE triggers: consecutive_successes >= 10, shortcut_usage_rate > 0.5, help_requests == 0
    - DOWNGRADE triggers: consecutive_errors >= 3, high help rate (> 30%), high correction rate

    Return null if no transition is warranted.
    If transition is warranted, return the transition details with confidence score.

    {{ ctx.output_format }}
  "#
}
