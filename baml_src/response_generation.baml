// Response Generation
// Generates natural language responses based on LUI feedback templates

// ============================================
// Response Types
// ============================================

/// A generated natural language response
class GeneratedResponse {
  response_text string @description("The main response text to display to user")
  response_type ResponseType @description("Category of response")
  follow_up FollowUpAction? @description("Suggested next action")
  visual_elements VisualElement[]? @description("Optional visual elements to enhance response")
  tone_applied string? @description("The tone that was applied")
  personalization_notes string[]? @description("Notes on how response was personalized")
}

/// Types of responses the system can generate
enum ResponseType {
  CONFIRMATION @description("Confirming an action will be or was taken")
  RESULT @description("Presenting data or query results")
  ERROR @description("Explaining what went wrong")
  CLARIFICATION @description("Asking for more information")
  PROGRESS @description("Updating on ongoing operation")
  COMPLETION @description("Indicating task is finished")
  SUGGESTION @description("Proactively suggesting an action")
  ACKNOWLEDGMENT @description("Simple acknowledgment without action")
}

/// A suggested follow-up action for the user
class FollowUpAction {
  suggested_action string @description("Description of what the user could do next")
  action_phrase string @description("Natural language phrase to trigger this action")
  is_required bool @description("Whether this action is required to continue")
  component_id string? @description("ID of the component this action would invoke")
  urgency UrgencyLevel? @description("How urgent this follow-up is")
}

/// Urgency levels for follow-up actions
enum UrgencyLevel {
  IMMEDIATE @description("Must be done now")
  SOON @description("Should be done shortly")
  OPTIONAL @description("Nice to do but not required")
  INFORMATIONAL @description("Just for awareness")
}

/// A visual element to include in the response
class VisualElement {
  element_type VisualElementType
  content string @description("The content to display")
  alt_text string? @description("Accessible description")
  title string? @description("Optional title or caption")
  metadata map<string, string>? @description("Additional element metadata")
}

/// Types of visual elements supported
enum VisualElementType {
  TABLE @description("Tabular data display")
  LIST @description("Ordered or unordered list")
  CODE_BLOCK @description("Formatted code snippet")
  LINK @description("Clickable hyperlink")
  IMAGE_REF @description("Reference to an image")
  CARD @description("Information card with structured content")
  CHART @description("Data visualization reference")
  BADGE @description("Status indicator or tag")
  QUOTE @description("Quoted text or callout")
}

// ============================================
// Action Result Types
// ============================================

/// The result of executing an action
class ActionResult {
  status ResultStatus @description("Outcome of the action")
  data string? @description("Result data, if any")
  error_message string? @description("Error details if failed")
  metadata ResultMetadata? @description("Additional result metadata")
  affected_entities string[]? @description("IDs of entities affected")
  execution_time_ms int? @description("How long the action took")
}

/// Possible action result statuses
enum ResultStatus {
  SUCCESS @description("Action completed successfully")
  PARTIAL @description("Action partially completed")
  FAILURE @description("Action failed")
  PENDING @description("Action is in progress")
  CANCELLED @description("Action was cancelled")
  TIMEOUT @description("Action timed out")
  REQUIRES_INPUT @description("Waiting for user input to continue")
}

/// Additional metadata about the action result
class ResultMetadata {
  timestamp string @description("When the action completed")
  affected_count int? @description("Number of items affected")
  warnings string[]? @description("Non-fatal warnings")
  debug_info string? @description("Debug information for troubleshooting")
  related_actions string[]? @description("IDs of related actions that may be relevant")
}

// ============================================
// User Context Types
// ============================================

/// Context about the user for personalization
class UserContext {
  user_id string? @description("User identifier")
  preferences UserResponsePreferences? @description("User's response preferences")
  interaction_count int @description("Number of previous interactions")
  expertise_level ExpertiseLevel @description("User's expertise level")
  accessibility_needs AccessibilityNeeds? @description("Accessibility requirements")
  locale string? @description("User's locale (e.g., en-US)")
  previous_responses ResponseHistory? @description("Recent response history")
}

/// User preferences for responses
class UserResponsePreferences {
  preferred_verbosity VerbosityLevel @description("How detailed responses should be")
  include_explanations bool @description("Whether to include explanations")
  include_examples bool @description("Whether to include examples")
  preferred_format FormatPreference @description("Preferred response format")
  use_emojis bool @description("Whether to use emojis")
}

/// How verbose responses should be
enum VerbosityLevel {
  MINIMAL @description("Just the essentials")
  CONCISE @description("Brief but complete")
  STANDARD @description("Normal level of detail")
  DETAILED @description("Comprehensive explanations")
  EXHAUSTIVE @description("Maximum detail for learning")
}

/// User's expertise level
enum ExpertiseLevel {
  NOVICE @description("New to the system")
  BEGINNER @description("Some familiarity")
  INTERMEDIATE @description("Regular user")
  ADVANCED @description("Power user")
  EXPERT @description("Deep system knowledge")
}

/// Preferred response format
enum FormatPreference {
  PROSE @description("Natural sentences")
  BULLETS @description("Bullet points")
  STRUCTURED @description("Headers and sections")
  MINIMAL @description("Just the data")
}

/// Accessibility needs that affect response generation
class AccessibilityNeeds {
  screen_reader_optimized bool @description("Optimize for screen readers")
  high_contrast bool @description("Use high contrast elements")
  reduce_motion bool @description("Avoid animated elements")
  simple_language bool @description("Use simpler vocabulary")
  large_text bool @description("Prefer larger text elements")
}

/// History of recent responses for context
class ResponseHistory {
  recent_responses RecentResponse[] @description("Last few responses")
  common_follow_ups string[] @description("Frequently used follow-up actions")
  avoided_phrases string[]? @description("Phrases to avoid repeating")
}

class RecentResponse {
  response_type ResponseType
  timestamp string
  was_helpful bool? @description("User feedback on response")
}

// ============================================
// Response Style Types
// ============================================

/// Style configuration for response generation
class ResponseStyle {
  tone ResponseTone @description("Overall tone of the response")
  formality FormalityLevel @description("How formal the language should be")
  personality PersonalityTraits? @description("Personality characteristics")
  brand_voice BrandVoice? @description("Brand-specific voice guidelines")
}

/// Tone options for responses
enum ResponseTone {
  PROFESSIONAL @description("Business-appropriate, neutral")
  FRIENDLY @description("Warm, approachable")
  EMPATHETIC @description("Understanding, supportive")
  ENTHUSIASTIC @description("Excited, energetic")
  CALM @description("Soothing, measured")
  DIRECT @description("Straightforward, no-nonsense")
  PLAYFUL @description("Light-hearted, fun")
}

/// Formality levels
enum FormalityLevel {
  VERY_FORMAL @description("Corporate, official language")
  FORMAL @description("Professional but not stiff")
  NEUTRAL @description("Neither formal nor casual")
  CASUAL @description("Relaxed, conversational")
  VERY_CASUAL @description("Very informal, like texting")
}

/// Personality traits for the response
class PersonalityTraits {
  is_humorous bool @description("Include appropriate humor")
  is_encouraging bool @description("Add encouraging remarks")
  is_concise bool @description("Keep responses short")
  uses_analogies bool @description("Use analogies to explain")
  is_proactive bool @description("Anticipate user needs")
}

/// Brand-specific voice guidelines
class BrandVoice {
  brand_name string @description("Name of the brand")
  voice_description string @description("Description of brand voice")
  key_phrases string[]? @description("Phrases the brand uses")
  avoided_phrases string[]? @description("Phrases to avoid")
  emoji_style EmojiStyle? @description("How to use emojis")
  signature_elements string[]? @description("Unique brand elements")
}

/// How to use emojis in responses
enum EmojiStyle {
  NONE @description("Never use emojis")
  MINIMAL @description("Occasional, subtle use")
  MODERATE @description("Regular, balanced use")
  EXPRESSIVE @description("Frequent, expressive use")
}

// ============================================
// Main Generation Function
// ============================================

/// Generate a natural language response based on action result and context
function GenerateResponse(
  action_result: ActionResult,
  component: LUIComponent,
  user_context: UserContext?,
  style: ResponseStyle
) -> GeneratedResponse {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    You are a response generation system for a Language User Interface (LUI).
    Generate a natural, contextually appropriate response for the user.

    ## Action Information
    - Intent: {{ component.intent }}
    - Result Status: {{ action_result.status }}
    {% if action_result.data %}
    - Result Data: {{ action_result.data }}
    {% endif %}
    {% if action_result.error_message %}
    - Error: {{ action_result.error_message }}
    {% endif %}
    {% if action_result.metadata %}
    - Affected Count: {{ action_result.metadata.affected_count }}
    {% if action_result.metadata.warnings %}
    - Warnings: {{ action_result.metadata.warnings }}
    {% endif %}
    {% endif %}

    ## Feedback Templates
    - Success: "{{ component.feedback.success_template }}"
    - Error: "{{ component.feedback.error_template }}"
    {% if component.feedback.progress_template %}
    - Progress: "{{ component.feedback.progress_template }}"
    {% endif %}

    ## Style Requirements
    - Tone: {{ style.tone }}
    - Formality: {{ style.formality }}
    {% if style.personality %}
    - Humorous: {{ style.personality.is_humorous }}
    - Encouraging: {{ style.personality.is_encouraging }}
    - Concise: {{ style.personality.is_concise }}
    {% endif %}
    {% if style.brand_voice %}
    - Brand: {{ style.brand_voice.brand_name }}
    - Voice: {{ style.brand_voice.voice_description }}
    {% if style.brand_voice.key_phrases %}
    - Use phrases: {{ style.brand_voice.key_phrases }}
    {% endif %}
    {% endif %}

    {% if user_context %}
    ## User Context
    - Expertise: {{ user_context.expertise_level }}
    - Interactions: {{ user_context.interaction_count }}
    {% if user_context.preferences %}
    - Verbosity: {{ user_context.preferences.preferred_verbosity }}
    - Format: {{ user_context.preferences.preferred_format }}
    - Include examples: {{ user_context.preferences.include_examples }}
    {% endif %}
    {% if user_context.accessibility_needs %}
    - Screen reader optimized: {{ user_context.accessibility_needs.screen_reader_optimized }}
    - Simple language: {{ user_context.accessibility_needs.simple_language }}
    {% endif %}
    {% endif %}

    ## Generation Guidelines
    1. Use the appropriate feedback template as a starting point
    2. Incorporate actual result data naturally
    3. Match the requested tone and formality
    4. Adjust complexity based on user expertise level
    5. Suggest logical follow-up actions when appropriate
    6. Include visual elements if they would help clarity
    7. Apply brand voice guidelines if provided
    8. Consider accessibility needs

    {{ ctx.output_format }}
  "#
}

// ============================================
// Specialized Response Functions
// ============================================

/// Generate an error response with helpful recovery suggestions
function GenerateErrorResponse(
  error_result: ActionResult,
  component: LUIComponent,
  style: ResponseStyle
) -> GeneratedResponse {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Generate a helpful error response that explains what went wrong and how to fix it.

    ## Error Details
    - Component: {{ component.intent }}
    - Status: {{ error_result.status }}
    - Error Message: {{ error_result.error_message }}
    {% if error_result.metadata and error_result.metadata.debug_info %}
    - Debug Info: {{ error_result.metadata.debug_info }}
    {% endif %}

    ## Error Template
    "{{ component.feedback.error_template }}"

    ## Style
    - Tone: {{ style.tone }} (but always empathetic for errors)
    - Formality: {{ style.formality }}

    ## Guidelines
    1. Acknowledge the error without blame
    2. Explain what went wrong in simple terms
    3. Provide specific steps to resolve
    4. Suggest alternative approaches if available
    5. Keep the user calm and supported
    6. Include a clear follow-up action

    {{ ctx.output_format }}
  "#
}

/// Generate a progress update response
function GenerateProgressResponse(
  progress_info: ProgressInfo,
  component: LUIComponent,
  style: ResponseStyle
) -> GeneratedResponse {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Generate a progress update that keeps the user informed and engaged.

    ## Progress Details
    - Operation: {{ component.intent }}
    - Current Step: {{ progress_info.current_step }} of {{ progress_info.total_steps }}
    - Percentage: {{ progress_info.percentage_complete }}%
    - Status: {{ progress_info.status_message }}
    {% if progress_info.estimated_time_remaining %}
    - Time Remaining: {{ progress_info.estimated_time_remaining }}
    {% endif %}

    {% if component.feedback.progress_template %}
    ## Progress Template
    "{{ component.feedback.progress_template }}"
    {% endif %}

    ## Style
    - Tone: {{ style.tone }}
    - Formality: {{ style.formality }}

    ## Guidelines
    1. Be clear about current progress
    2. Set appropriate expectations
    3. Keep it brief but informative
    4. Include visual progress indicator if appropriate
    5. Don't over-communicate on minor updates

    {{ ctx.output_format }}
  "#
}

/// Progress information for long-running operations
class ProgressInfo {
  current_step int @description("Current step number")
  total_steps int @description("Total number of steps")
  percentage_complete float @description("Completion percentage (0-100)")
  status_message string @description("Current status description")
  estimated_time_remaining string? @description("Estimated time to completion")
  can_cancel bool @description("Whether operation can be cancelled")
}

/// Generate a multi-result response for batch operations
function GenerateBatchResultResponse(
  batch_result: BatchResult,
  component: LUIComponent,
  style: ResponseStyle
) -> GeneratedResponse {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Generate a summary response for a batch operation result.

    ## Batch Details
    - Operation: {{ component.intent }}
    - Total Items: {{ batch_result.total_count }}
    - Successful: {{ batch_result.success_count }}
    - Failed: {{ batch_result.failure_count }}
    - Skipped: {{ batch_result.skipped_count }}

    {% if batch_result.sample_successes %}
    ## Sample Successes
    {{ batch_result.sample_successes }}
    {% endif %}

    {% if batch_result.failure_reasons %}
    ## Failure Reasons
    {% for reason in batch_result.failure_reasons %}
    - {{ reason.reason }}: {{ reason.count }} items
    {% endfor %}
    {% endif %}

    ## Style
    - Tone: {{ style.tone }}
    - Formality: {{ style.formality }}

    ## Guidelines
    1. Lead with the overall outcome (success/partial/failure)
    2. Provide clear counts
    3. Summarize failures helpfully
    4. Suggest follow-up actions for failed items
    5. Use visual elements like lists or tables for clarity

    {{ ctx.output_format }}
  "#
}

/// Result of a batch operation
class BatchResult {
  total_count int @description("Total items processed")
  success_count int @description("Items that succeeded")
  failure_count int @description("Items that failed")
  skipped_count int @description("Items that were skipped")
  sample_successes string[]? @description("Sample of successful items")
  failure_reasons FailureReason[]? @description("Categorized failure reasons")
  overall_status ResultStatus @description("Overall batch status")
}

/// A categorized failure reason
class FailureReason {
  reason string @description("Description of why items failed")
  count int @description("Number of items with this failure")
  affected_ids string[]? @description("IDs of affected items")
}

// ============================================
// Test Cases
// ============================================

test generate_success_response {
  functions [GenerateResponse]
  args {
    action_result {
      status SUCCESS
      data "Task 'Review PR #42' created successfully"
      error_message null
      metadata {
        timestamp "2025-01-15T10:30:00Z"
        affected_count 1
        warnings null
        debug_info null
        related_actions null
      }
      affected_entities ["task-123"]
      execution_time_ms 150
    }
    component {
      component_id "create-task"
      component_type ACTION
      intent "Create a new task"
      invocation {
        primary_phrase "create task"
        alternate_phrases ["add task", "new task"]
        examples ["Create a task to review code"]
        context_requirements null
      }
      parameters []
      feedback {
        success_template "Task '{title}' has been created"
        error_template "Could not create task: {error}"
        progress_template null
        confirmation_required false
        confirmation_prompt null
      }
      accessibility null
    }
    user_context {
      user_id "user-1"
      preferences {
        preferred_verbosity STANDARD
        include_explanations true
        include_examples false
        preferred_format PROSE
        use_emojis false
      }
      interaction_count 15
      expertise_level INTERMEDIATE
      accessibility_needs null
      locale "en-US"
      previous_responses null
    }
    style {
      tone FRIENDLY
      formality NEUTRAL
      personality {
        is_humorous false
        is_encouraging true
        is_concise false
        uses_analogies false
        is_proactive true
      }
      brand_voice null
    }
  }
}

test generate_error_response {
  functions [GenerateErrorResponse]
  args {
    error_result {
      status FAILURE
      data null
      error_message "Permission denied: User does not have write access to this project"
      metadata {
        timestamp "2025-01-15T10:35:00Z"
        affected_count 0
        warnings null
        debug_info "ACL check failed for project-456"
        related_actions ["request-access"]
      }
      affected_entities null
      execution_time_ms 50
    }
    component {
      component_id "create-task"
      component_type ACTION
      intent "Create a new task"
      invocation {
        primary_phrase "create task"
        alternate_phrases []
        examples []
        context_requirements null
      }
      parameters []
      feedback {
        success_template "Task created"
        error_template "Could not create task: {error}"
        progress_template null
        confirmation_required false
        confirmation_prompt null
      }
      accessibility null
    }
    style {
      tone EMPATHETIC
      formality NEUTRAL
      personality null
      brand_voice null
    }
  }
}

test generate_progress_response {
  functions [GenerateProgressResponse]
  args {
    progress_info {
      current_step 3
      total_steps 5
      percentage_complete 60.0
      status_message "Processing file 3 of 5..."
      estimated_time_remaining "About 2 minutes"
      can_cancel true
    }
    component {
      component_id "import-data"
      component_type ACTION
      intent "Import data from file"
      invocation {
        primary_phrase "import data"
        alternate_phrases []
        examples []
        context_requirements null
      }
      parameters []
      feedback {
        success_template "Data imported successfully"
        error_template "Import failed: {error}"
        progress_template "Importing... {percentage}% complete"
        confirmation_required false
        confirmation_prompt null
      }
      accessibility null
    }
    style {
      tone CALM
      formality NEUTRAL
      personality {
        is_humorous false
        is_encouraging false
        is_concise true
        uses_analogies false
        is_proactive false
      }
      brand_voice null
    }
  }
}

test generate_batch_response {
  functions [GenerateBatchResultResponse]
  args {
    batch_result {
      total_count 100
      success_count 95
      failure_count 3
      skipped_count 2
      sample_successes ["item-1", "item-2", "item-3"]
      failure_reasons [
        {
          reason "Invalid format"
          count 2
          affected_ids ["item-50", "item-75"]
        },
        {
          reason "Duplicate entry"
          count 1
          affected_ids ["item-88"]
        }
      ]
      overall_status PARTIAL
    }
    component {
      component_id "bulk-import"
      component_type ACTION
      intent "Import multiple items"
      invocation {
        primary_phrase "bulk import"
        alternate_phrases []
        examples []
        context_requirements null
      }
      parameters []
      feedback {
        success_template "All items imported successfully"
        error_template "Import failed for some items"
        progress_template null
        confirmation_required false
        confirmation_prompt null
      }
      accessibility null
    }
    style {
      tone PROFESSIONAL
      formality FORMAL
      personality null
      brand_voice null
    }
  }
}

test generate_branded_response {
  functions [GenerateResponse]
  args {
    action_result {
      status SUCCESS
      data "Order #12345 confirmed"
      error_message null
      metadata null
      affected_entities null
      execution_time_ms null
    }
    component {
      component_id "confirm-order"
      component_type ACTION
      intent "Confirm an order"
      invocation {
        primary_phrase "confirm order"
        alternate_phrases []
        examples []
        context_requirements null
      }
      parameters []
      feedback {
        success_template "Your order is confirmed!"
        error_template "Order failed"
        progress_template null
        confirmation_required false
        confirmation_prompt null
      }
      accessibility null
    }
    user_context null
    style {
      tone ENTHUSIASTIC
      formality CASUAL
      personality {
        is_humorous false
        is_encouraging true
        is_concise false
        uses_analogies false
        is_proactive true
      }
      brand_voice {
        brand_name "HappyShop"
        voice_description "Upbeat, friendly, and celebration-focused"
        key_phrases ["Woohoo!", "You're all set!", "Happy shopping!"]
        avoided_phrases ["unfortunately", "sorry"]
        emoji_style EXPRESSIVE
        signature_elements ["celebration emojis", "confetti references"]
      }
    }
  }
}
