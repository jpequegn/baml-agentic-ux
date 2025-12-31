// Adaptive Response Generation
// Profile-aware response generation that adapts to user expertise
// Issue #48 - Phase 2: Adaptive Interface Personalization

// Dependencies:
// - IntentExtraction, ConversationContext from intent_extraction.baml
// - ActionResult from response_generation.baml
// - UserProfile, SessionMetrics from user_profile_types.baml
// - ExpertiseLevel, VerbosityLevel from response_generation.baml

// ============================================
// Adaptation Settings
// ============================================

/// Settings that control how responses are adapted
class AdaptationSettings {
  expertise_level ExpertiseLevel @description("User's current expertise level")
  verbosity_level VerbosityLevel @description("Response verbosity to use")
  show_examples bool @description("Whether to include examples")
  show_shortcuts bool @description("Whether to mention shortcuts")
  require_confirmation bool @description("Whether to require confirmation")
  use_technical_language bool @description("Whether to use technical terms")
  offer_help_proactively bool @description("Whether to offer unsolicited help")
  define_terms bool @description("Whether to define domain terms")
  max_options int @description("Maximum options to show (0=unlimited)")
}

/// Frustration handling mode
enum FrustrationResponse {
  NORMAL @description("No frustration detected, normal responses")
  INCREASED_HELP @description("Increase helpfulness temporarily")
  OFFER_ALTERNATIVES @description("Suggest simpler approaches")
  SIMPLIFY @description("Reduce complexity, more guidance")
  ESCALATE @description("Offer human support option")
}

/// Signals indicating user frustration
class FrustrationIndicators {
  consecutive_errors int @description("Number of consecutive errors")
  repeated_queries int @description("Same query repeated")
  negative_sentiment bool @description("Negative language detected")
  rapid_interactions bool @description("Unusually fast interaction pace")
  help_seeking_rate float @description("Rate of help requests (0.0-1.0)")
  abandonment_signals bool @description("Signs of giving up")
}

// ============================================
// Adaptive Response Types
// ============================================

/// A response adapted to user profile
class AdaptiveResponse {
  content string @description("The main response content")
  verbosity_used VerbosityLevel @description("Verbosity level applied")
  adaptations_applied string[] @description("List of adaptations made")
  shortcuts_mentioned string[] @description("Shortcuts included in response")
  follow_up_suggestions string[] @description("Suggested next actions")

  // For gradual transition support
  alternative_content string? @description("Alternative phrasing for A/B or toggle")
  show_toggle bool @description("Whether to show verbosity toggle")

  // Metadata
  expertise_level_used ExpertiseLevel @description("Expertise level response was generated for")
  frustration_mode FrustrationResponse @description("Frustration response mode applied")
  confidence float @description("Confidence in response appropriateness (0.0-1.0)")
}

/// Context for generating adaptive responses
class AdaptiveResponseContext {
  intent IntentExtraction @description("The extracted user intent")
  action_result ActionResult? @description("Result of action if executed")
  conversation ConversationContext @description("Conversation history")
  user_profile UserProfile @description("Complete user profile")
  session_metrics SessionMetrics @description("Current session metrics")
  frustration_indicators FrustrationIndicators? @description("Frustration signals if any")
}

// ============================================
// Expertise Level Guidelines
// ============================================

/// Guidelines for each expertise level
class ExpertiseLevelGuidelines {
  level ExpertiseLevel @description("The expertise level")
  description string @description("Description of this level")
  confirmation_policy string @description("When to ask for confirmation")
  explanation_depth string @description("How deep explanations should go")
  shortcut_policy string @description("How to handle shortcuts")
  error_handling string @description("How to handle errors")
  help_policy string @description("How to offer help")
  language_style string @description("Language style to use")
}

// ============================================
// Response Modifiers
// ============================================

/// Modifiers that can be applied to responses
class ResponseModifier {
  modifier_type ModifierType @description("Type of modification")
  reason string @description("Why this modifier was applied")
  impact string @description("How it changes the response")
}

enum ModifierType {
  INCREASE_VERBOSITY @description("Make response more detailed")
  DECREASE_VERBOSITY @description("Make response more concise")
  ADD_EXAMPLES @description("Include examples")
  ADD_SHORTCUTS @description("Add shortcut hints")
  ADD_CONFIRMATION @description("Add confirmation request")
  ADD_HELP_OFFER @description("Offer additional help")
  SIMPLIFY_LANGUAGE @description("Use simpler vocabulary")
  ADD_CONTEXT @description("Provide more background")
  INCREASE_EMPATHY @description("More supportive tone")
}

// ============================================
// Adaptation Result
// ============================================

/// Complete result of response adaptation
class AdaptationResult {
  original_intent string @description("The original intent being addressed")
  adapted_response AdaptiveResponse @description("The adapted response")
  settings_used AdaptationSettings @description("Settings applied")
  modifiers_applied ResponseModifier[] @description("Modifiers that were applied")
  guidelines_followed ExpertiseLevelGuidelines @description("Guidelines for the level")
}

// ============================================
// Main Generation Function
// ============================================

/// Generate a response adapted to user expertise level
function GenerateAdaptiveResponse(
  intent: IntentExtraction,
  action_result: ActionResult?,
  conversation_context: ConversationContext,
  user_profile: UserProfile,
  session_metrics: SessionMetrics
) -> AdaptiveResponse {
  client CustomSonnet4
  prompt #"
    Generate a response adapted to the user's expertise level and preferences.

    ## User Intent
    - Intent: {{ intent.detected_intent.intent_name }}
    - Category: {{ intent.detected_intent.intent_category }}
    - Confidence: {{ intent.confidence }}
    {% if intent.extracted_parameters %}
    - Parameters: {{ intent.extracted_parameters }}
    {% endif %}

    {% if action_result %}
    ## Action Result
    - Status: {{ action_result.status }}
    {% if action_result.data %}
    - Data: {{ action_result.data }}
    {% endif %}
    {% if action_result.error_message %}
    - Error: {{ action_result.error_message }}
    {% endif %}
    {% endif %}

    ## User Profile
    - Expertise Level: {{ user_profile.expertise_level }}
    - Expertise Score: {{ user_profile.expertise_score }}
    - Expertise Confidence: {{ user_profile.expertise_confidence }}
    - Preferred Verbosity: {{ user_profile.preferences.preferred_verbosity }}
    - Preferred Style: {{ user_profile.preferences.preferred_style }}
    - Enable Shortcuts: {{ user_profile.preferences.enable_shortcuts }}
    - Enable Proactive Help: {{ user_profile.preferences.enable_proactive_help }}

    ## Session Metrics
    - Interactions: {{ session_metrics.interactions_this_session }}
    - Successes: {{ session_metrics.successes_this_session }}
    - Errors: {{ session_metrics.errors_this_session }}
    - Consecutive Errors: {{ session_metrics.consecutive_errors }}
    - Consecutive Successes: {{ session_metrics.consecutive_successes }}
    {% if session_metrics.shortcuts_used %}
    - Shortcuts Used: {{ session_metrics.shortcuts_used }}
    {% endif %}

    ## Adaptation Guidelines by Level

    ### NOVICE
    - Full explanations with examples
    - Confirm before ALL actions
    - Offer help proactively
    - Define domain terms
    - Show step-by-step guidance
    - Max 3-5 options
    - Encouraging, supportive tone

    ### BEGINNER
    - Brief explanations
    - Confirm destructive actions only
    - Mention shortcuts exist (but explain)
    - Assume basic familiarity
    - Max 3-4 options

    ### INTERMEDIATE
    - Standard responses
    - No unsolicited explanations
    - Suggest efficiency tips occasionally
    - Assume competence
    - Show relevant shortcuts
    - Rarely confirm

    ### ADVANCED
    - Concise responses
    - No confirmations except critical
    - Surface power features
    - Technical language OK
    - Show keyboard shortcuts
    - Trust user knows what they're doing

    ### EXPERT
    - Minimal responses
    - No hand-holding
    - Assume full knowledge
    - Support command-line style
    - Symbol-based feedback OK
    - Maximum efficiency

    ## Frustration Handling
    {% if session_metrics.consecutive_errors > 2 %}
    FRUSTRATION DETECTED: {{ session_metrics.consecutive_errors }} consecutive errors
    - Increase helpfulness temporarily
    - Offer alternatives and simpler approaches
    - Don't apologize excessively
    - Be encouraging but not condescending
    {% endif %}

    ## Response Requirements
    1. Match verbosity to expertise level
    2. Include shortcuts only if appropriate for level
    3. Maintain consistent brand voice (professional yet friendly)
    4. If profile is incomplete, default to INTERMEDIATE
    5. Suggest follow-up actions appropriate to level
    6. Set show_toggle=true if user is transitioning levels

    Generate a response that feels natural for this user's expertise level.

    {{ ctx.output_format }}
  "#
}

/// Determine adaptation settings based on profile and context
function DetermineAdaptationSettings(
  user_profile: UserProfile,
  session_metrics: SessionMetrics,
  frustration_indicators: FrustrationIndicators?
) -> AdaptationSettings {
  client CustomSonnet4
  prompt #"
    Determine the optimal adaptation settings for this user.

    ## User Profile
    - Expertise Level: {{ user_profile.expertise_level }}
    - Expertise Score: {{ user_profile.expertise_score }}
    - Preferred Verbosity: {{ user_profile.preferences.preferred_verbosity }}
    - Preferred Style: {{ user_profile.preferences.preferred_style }}
    - Enable Shortcuts: {{ user_profile.preferences.enable_shortcuts }}
    - Enable Proactive Help: {{ user_profile.preferences.enable_proactive_help }}

    ## Session Metrics
    - Consecutive Errors: {{ session_metrics.consecutive_errors }}
    - Consecutive Successes: {{ session_metrics.consecutive_successes }}
    - Errors This Session: {{ session_metrics.errors_this_session }}

    {% if frustration_indicators %}
    ## Frustration Signals
    - Consecutive Errors: {{ frustration_indicators.consecutive_errors }}
    - Repeated Queries: {{ frustration_indicators.repeated_queries }}
    - Negative Sentiment: {{ frustration_indicators.negative_sentiment }}
    - Help Seeking Rate: {{ frustration_indicators.help_seeking_rate }}
    - Abandonment Signals: {{ frustration_indicators.abandonment_signals }}
    {% endif %}

    ## Settings Mapping by Level

    NOVICE:
    - verbosity_level: DETAILED
    - show_examples: true
    - show_shortcuts: false
    - require_confirmation: true
    - use_technical_language: false
    - offer_help_proactively: true
    - define_terms: true
    - max_options: 5

    BEGINNER:
    - verbosity_level: DETAILED
    - show_examples: sometimes
    - show_shortcuts: mention only
    - require_confirmation: for destructive
    - use_technical_language: false
    - offer_help_proactively: true
    - define_terms: sometimes
    - max_options: 4

    INTERMEDIATE:
    - verbosity_level: STANDARD
    - show_examples: rarely
    - show_shortcuts: true
    - require_confirmation: rarely
    - use_technical_language: ok
    - offer_help_proactively: false
    - define_terms: false
    - max_options: 3

    ADVANCED:
    - verbosity_level: CONCISE
    - show_examples: false
    - show_shortcuts: true
    - require_confirmation: critical only
    - use_technical_language: true
    - offer_help_proactively: false
    - define_terms: false
    - max_options: unlimited

    EXPERT:
    - verbosity_level: MINIMAL
    - show_examples: false
    - show_shortcuts: true
    - require_confirmation: never
    - use_technical_language: true
    - offer_help_proactively: false
    - define_terms: false
    - max_options: unlimited

    ## Frustration Adjustments
    If frustration detected, temporarily:
    - Increase verbosity one level
    - Enable examples
    - Offer help proactively
    - Be more encouraging

    Generate appropriate settings.

    {{ ctx.output_format }}
  "#
}

/// Get guidelines for a specific expertise level
function GetExpertiseLevelGuidelines(
  level: ExpertiseLevel
) -> ExpertiseLevelGuidelines {
  client CustomSonnet4
  prompt #"
    Provide the response generation guidelines for expertise level: {{ level }}

    Return comprehensive guidelines covering:
    - Description of this user type
    - When to ask for confirmation
    - How detailed explanations should be
    - How to handle shortcuts
    - How to handle errors
    - When and how to offer help
    - Language style to use

    Be specific and actionable.

    {{ ctx.output_format }}
  "#
}

/// Detect frustration signals from session metrics
function DetectFrustrationSignals(
  session_metrics: SessionMetrics,
  conversation_context: ConversationContext
) -> FrustrationIndicators {
  client CustomSonnet4
  prompt #"
    Analyze the session for frustration signals.

    ## Session Metrics
    - Interactions: {{ session_metrics.interactions_this_session }}
    - Successes: {{ session_metrics.successes_this_session }}
    - Errors: {{ session_metrics.errors_this_session }}
    - Consecutive Errors: {{ session_metrics.consecutive_errors }}
    - Consecutive Successes: {{ session_metrics.consecutive_successes }}
    - Help Topics Accessed: {{ session_metrics.help_topics_accessed }}

    ## Conversation Context
    {% for msg in conversation_context.recent_messages %}
    - [{{ msg.role }}]: {{ msg.content }}
    {% endfor %}

    Analyze for:
    1. Consecutive errors (count them)
    2. Repeated queries (same question asked multiple times)
    3. Negative sentiment (frustration words, caps, punctuation)
    4. Rapid interactions (unusually fast pace)
    5. Help seeking rate (proportion of help requests)
    6. Abandonment signals (incomplete tasks, giving up language)

    {{ ctx.output_format }}
  "#
}

/// Generate an error response appropriate for expertise level
function GenerateAdaptiveErrorResponse(
  error_result: ActionResult,
  user_profile: UserProfile,
  frustration_indicators: FrustrationIndicators?
) -> AdaptiveResponse {
  client CustomSonnet4
  prompt #"
    Generate an error response adapted to user expertise level.

    ## Error Details
    - Status: {{ error_result.status }}
    - Error Message: {{ error_result.error_message }}
    {% if error_result.metadata %}
    {% if error_result.metadata.debug_info %}
    - Debug Info: {{ error_result.metadata.debug_info }}
    {% endif %}
    {% endif %}

    ## User Profile
    - Expertise Level: {{ user_profile.expertise_level }}
    - Preferred Verbosity: {{ user_profile.preferences.preferred_verbosity }}

    {% if frustration_indicators %}
    ## Frustration Status
    - Consecutive Errors: {{ frustration_indicators.consecutive_errors }}
    - Negative Sentiment: {{ frustration_indicators.negative_sentiment }}
    {% endif %}

    ## Error Response by Level

    NOVICE:
    - Explain what went wrong in simple terms
    - Don't blame the user
    - Provide 3 specific recovery options
    - Offer to help
    - Be encouraging

    BEGINNER:
    - Brief explanation of the error
    - 2 recovery options
    - Mention help is available

    INTERMEDIATE:
    - Concise error message
    - 1 suggested fix
    - Link to relevant help

    ADVANCED:
    - Short error with action
    - Technical details OK

    EXPERT:
    - Error code + minimal message
    - Trust user knows how to fix

    ## If Frustrated
    - Be extra supportive
    - Offer simpler alternatives
    - Don't apologize excessively (once is enough)
    - Focus on solutions

    {{ ctx.output_format }}
  "#
}

/// Transform a standard response to match expertise level
function AdaptResponseToLevel(
  original_response: string,
  target_level: ExpertiseLevel,
  include_shortcuts: bool
) -> AdaptiveResponse {
  client CustomSonnet4
  prompt #"
    Transform this response to match the target expertise level.

    ## Original Response
    {{ original_response }}

    ## Target Level: {{ target_level }}
    ## Include Shortcuts: {{ include_shortcuts }}

    ## Transformation Rules

    If NOVICE:
    - Expand abbreviations
    - Add explanatory context
    - Define any technical terms
    - Add examples where helpful
    - Keep encouraging tone

    If BEGINNER:
    - Keep it approachable
    - Brief explanations
    - Simple vocabulary

    If INTERMEDIATE:
    - Standard professional response
    - Assume reasonable knowledge
    - Mention shortcuts if enabled

    If ADVANCED:
    - Make it concise
    - Technical terms OK
    - Include shortcuts prominently

    If EXPERT:
    - Minimal words
    - Symbol/abbreviation OK
    - Maximum efficiency

    Transform the response appropriately.

    {{ ctx.output_format }}
  "#
}

// ============================================
// Test Cases
// ============================================

test adaptive_response_novice {
  functions [GenerateAdaptiveResponse]
  args {
    intent {
      detected_intent {
        intent_name "Create Task"
        intent_category CREATE
        target_component "task-creator"
        action_verb "create"
      }
      confidence 0.95
      extracted_parameters []
      ambiguity null
      suggested_clarification null
    }
    action_result {
      status SUCCESS
      data "Task 'Review code' created"
      error_message null
      metadata null
      affected_entities ["task-123"]
      execution_time_ms 150
    }
    conversation_context {
      recent_messages []
      current_state null
      active_entity null
      user_preferences null
    }
    user_profile {
      user_id "user-1"
      profile_version "1.0"
      created_at "2025-01-01T00:00:00Z"
      updated_at "2025-01-15T00:00:00Z"
      expertise_level NOVICE
      expertise_score 0.15
      expertise_confidence 0.6
      expertise_history null
      domain_expertise null
      preferences {
        preferred_verbosity DETAILED
        preferred_style CONVERSATIONAL
        learning_mode ACTIVE
        feedback_frequency ALWAYS
        enable_shortcuts false
        enable_proactive_help true
        preferred_language "en"
        timezone "UTC"
      }
      interaction_metrics null
      current_session null
      consent {
        profiling_enabled true
        store_interaction_history true
        allow_expertise_inference true
        allow_preference_learning true
        data_retention_days 90
        consent_timestamp "2025-01-01T00:00:00Z"
        consent_version "1.0"
      }
    }
    session_metrics {
      session_id "session-1"
      session_start "2025-01-15T10:00:00Z"
      interactions_this_session 5
      successes_this_session 4
      errors_this_session 1
      consecutive_errors 0
      consecutive_successes 2
      new_features_used []
      shortcuts_used []
      help_topics_accessed ["getting-started"]
    }
  }
}

test adaptive_response_expert {
  functions [GenerateAdaptiveResponse]
  args {
    intent {
      detected_intent {
        intent_name "Create Task"
        intent_category CREATE
        target_component "task-creator"
        action_verb "create"
      }
      confidence 0.98
      extracted_parameters []
      ambiguity null
      suggested_clarification null
    }
    action_result {
      status SUCCESS
      data "Task 'Review code' created"
      error_message null
      metadata null
      affected_entities ["task-123"]
      execution_time_ms 150
    }
    conversation_context {
      recent_messages []
      current_state null
      active_entity null
      user_preferences null
    }
    user_profile {
      user_id "user-2"
      profile_version "1.0"
      created_at "2024-01-01T00:00:00Z"
      updated_at "2025-01-15T00:00:00Z"
      expertise_level EXPERT
      expertise_score 0.92
      expertise_confidence 0.95
      expertise_history null
      domain_expertise null
      preferences {
        preferred_verbosity MINIMAL
        preferred_style TERSE
        learning_mode PASSIVE
        feedback_frequency NEVER
        enable_shortcuts true
        enable_proactive_help false
        preferred_language "en"
        timezone "UTC"
      }
      interaction_metrics null
      current_session null
      consent {
        profiling_enabled true
        store_interaction_history true
        allow_expertise_inference true
        allow_preference_learning true
        data_retention_days 365
        consent_timestamp "2024-01-01T00:00:00Z"
        consent_version "1.0"
      }
    }
    session_metrics {
      session_id "session-2"
      session_start "2025-01-15T10:00:00Z"
      interactions_this_session 50
      successes_this_session 48
      errors_this_session 2
      consecutive_errors 0
      consecutive_successes 15
      new_features_used []
      shortcuts_used ["ctrl+t", "ctrl+s", "ctrl+d"]
      help_topics_accessed []
    }
  }
}

test adaptive_response_frustrated_user {
  functions [GenerateAdaptiveResponse]
  args {
    intent {
      detected_intent {
        intent_name "Create Task"
        intent_category CREATE
        target_component "task-creator"
        action_verb "create"
      }
      confidence 0.85
      extracted_parameters []
      ambiguity null
      suggested_clarification null
    }
    action_result {
      status FAILURE
      data null
      error_message "Task creation failed: duplicate name"
      metadata null
      affected_entities null
      execution_time_ms 50
    }
    conversation_context {
      recent_messages [
        { role USER, content "create task review code", timestamp "2025-01-15T10:00:00Z", extracted_intent null },
        { role ASSISTANT, content "Error: duplicate name", timestamp "2025-01-15T10:00:05Z", extracted_intent null },
        { role USER, content "create task review code!", timestamp "2025-01-15T10:00:30Z", extracted_intent null }
      ]
      current_state null
      active_entity null
      user_preferences null
    }
    user_profile {
      user_id "user-3"
      profile_version "1.0"
      created_at "2025-01-10T00:00:00Z"
      updated_at "2025-01-15T00:00:00Z"
      expertise_level INTERMEDIATE
      expertise_score 0.55
      expertise_confidence 0.7
      expertise_history null
      domain_expertise null
      preferences {
        preferred_verbosity STANDARD
        preferred_style CONVERSATIONAL
        learning_mode ACTIVE
        feedback_frequency SIGNIFICANT
        enable_shortcuts true
        enable_proactive_help false
        preferred_language "en"
        timezone "UTC"
      }
      interaction_metrics null
      current_session null
      consent {
        profiling_enabled true
        store_interaction_history true
        allow_expertise_inference true
        allow_preference_learning true
        data_retention_days 90
        consent_timestamp "2025-01-10T00:00:00Z"
        consent_version "1.0"
      }
    }
    session_metrics {
      session_id "session-3"
      session_start "2025-01-15T09:55:00Z"
      interactions_this_session 10
      successes_this_session 5
      errors_this_session 5
      consecutive_errors 3
      consecutive_successes 0
      new_features_used []
      shortcuts_used []
      help_topics_accessed ["task-naming"]
    }
  }
}
