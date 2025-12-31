// Adaptive Response Templates
// Response templates that vary by expertise level while maintaining consistency
// Issue #47 - Phase 2: Adaptive Interface Personalization

// Dependencies:
// - ExpertiseLevel from response_generation.baml
// - VerbosityLevel from response_generation.baml

// ============================================
// Template Purpose
// ============================================

/// Purpose of a response template
enum TemplatePurpose {
  SUCCESS_CONFIRMATION @description("Confirming a successful action")
  ERROR_MESSAGE @description("Communicating an error or failure")
  DISAMBIGUATION @description("Requesting clarification from user")
  HELP_OFFER @description("Offering assistance to the user")
  FEATURE_SUGGESTION @description("Suggesting a feature or shortcut")
  ACTION_CONFIRMATION @description("Requesting confirmation before action")
  PROGRESS_UPDATE @description("Updating user on ongoing task progress")
  WELCOME_MESSAGE @description("Greeting the user at session start")
  TASK_CREATION @description("Confirming task creation")
  SEARCH_RESULTS @description("Presenting search results")
}

// ============================================
// Template Variant
// ============================================

/// A template variant for a specific expertise level
class TemplateVariant {
  expertise_level ExpertiseLevel @description("Target expertise level")
  template_content string @description("Template string with {placeholders}")
  show_examples bool @description("Whether to include examples")
  show_shortcuts bool @description("Whether to show keyboard shortcuts")
  require_confirmation bool @description("Whether to require user confirmation")
  include_undo bool @description("Whether to include undo option")
  max_options int @description("Maximum number of options to show (0=unlimited)")
}

/// Complete set of template variants for a purpose
class AdaptiveTemplate {
  template_id string @description("Unique identifier for this template")
  purpose TemplatePurpose @description("What this template is for")
  description string @description("Human-readable description")
  variants TemplateVariant[] @description("Variants for each expertise level")
  placeholders string[] @description("List of placeholder names used in templates")
}

// ============================================
// Template Selection Context
// ============================================

/// Context for selecting the appropriate template variant
class TemplateSelectionContext {
  expertise_level ExpertiseLevel @description("User's current expertise level")
  verbosity_override VerbosityLevel? @description("User's verbosity preference override")
  is_error bool @description("Whether this is an error context")
  is_first_time bool @description("Whether user is doing this action for first time")
  user_preference_style string? @description("User's preferred interaction style")
}

// ============================================
// Rendered Template
// ============================================

/// Result of rendering a template with context
class RenderedTemplate {
  template_id string @description("ID of the source template")
  purpose TemplatePurpose @description("Purpose of the template")
  expertise_level ExpertiseLevel @description("Level the template was rendered for")
  rendered_content string @description("The final rendered content")
  includes_examples bool @description("Whether examples were included")
  includes_shortcuts bool @description("Whether shortcuts were shown")
  requires_confirmation bool @description("Whether confirmation is required")
  suggested_actions string[]? @description("Actions the user can take")
}

// ============================================
// Template Library
// ============================================

/// Collection of all adaptive templates
class TemplateLibrary {
  library_id string @description("Unique identifier for this library")
  version string @description("Version of the template library")
  templates AdaptiveTemplate[] @description("All templates in the library")
  brand_voice string @description("Description of the brand voice to maintain")
  personality_traits string[] @description("Core personality traits to preserve")
}

// ============================================
// Verbosity Mapping
// ============================================

/// Mapping between expertise levels and default verbosity
class VerbosityMapping {
  expertise_level ExpertiseLevel @description("Expertise level")
  default_verbosity VerbosityLevel @description("Default verbosity for this level")
  confirmation_frequency string @description("How often to confirm: always, sometimes, rarely, never")
  example_frequency string @description("How often to show examples: always, sometimes, rarely, never")
}

// ============================================
// Template Customization
// ============================================

/// User's template customization preferences
class TemplateCustomization {
  user_id string @description("User these customizations apply to")
  verbosity_override VerbosityLevel? @description("Override default verbosity")
  always_show_examples bool @description("Always show examples regardless of level")
  never_show_shortcuts bool @description("Never show shortcuts")
  custom_confirmation_frequency string? @description("Custom confirmation frequency")
  preferred_error_detail string? @description("Preferred error detail: full, brief, minimal")
}

// ============================================
// Error Template Details
// ============================================

/// Error message template with progressive detail
class ErrorTemplateDetails {
  error_code string @description("Error code for reference")
  novice_template string @description("Full explanation + 3 options + help offer")
  beginner_template string @description("Brief explanation + 2 options")
  intermediate_template string @description("Short message + suggestion")
  advanced_template string @description("Minimal + action link")
  expert_template string @description("Symbol + key info only")
  recovery_actions string[] @description("Possible recovery actions")
}

// ============================================
// Functions
// ============================================

/// Select the appropriate template variant based on context
function SelectTemplateVariant(
  template: AdaptiveTemplate,
  context: TemplateSelectionContext
) -> TemplateVariant {
  client CustomSonnet4
  prompt #"
    Select the most appropriate template variant for this context.

    Template: {{ template.template_id }}
    Purpose: {{ template.purpose }}
    Available Variants:
    {% for variant in template.variants %}
    - {{ variant.expertise_level }}: "{{ variant.template_content }}"
      Examples: {{ variant.show_examples }}, Shortcuts: {{ variant.show_shortcuts }}
      Confirmation: {{ variant.require_confirmation }}
    {% endfor %}

    Context:
    - User Level: {{ context.expertise_level }}
    - Verbosity Override: {{ context.verbosity_override }}
    - Is Error: {{ context.is_error }}
    - Is First Time: {{ context.is_first_time }}
    - Style Preference: {{ context.user_preference_style }}

    Selection Rules:
    1. Match expertise level first
    2. If verbosity override, adjust template choice
    3. If first time action, prefer more verbose variant
    4. If error context, include more detail

    Select the variant that best matches the context.

    {{ ctx.output_format }}
  "#
}

/// Render a template with provided values
function RenderTemplate(
  template: AdaptiveTemplate,
  variant: TemplateVariant,
  values: map<string, string>
) -> RenderedTemplate {
  client CustomSonnet4
  prompt #"
    Render the template variant with the provided values.

    Template: {{ template.template_id }}
    Purpose: {{ template.purpose }}
    Variant for: {{ variant.expertise_level }}
    Template String: "{{ variant.template_content }}"

    Placeholders: {{ template.placeholders }}

    Values:
    {% for key, value in values %}
    - {{ key }}: {{ value }}
    {% endfor %}

    Settings:
    - Show Examples: {{ variant.show_examples }}
    - Show Shortcuts: {{ variant.show_shortcuts }}
    - Require Confirmation: {{ variant.require_confirmation }}
    - Include Undo: {{ variant.include_undo }}
    - Max Options: {{ variant.max_options }}

    Render the template by:
    1. Replacing all {placeholders} with values
    2. Adding examples if show_examples is true
    3. Adding shortcut hints if show_shortcuts is true
    4. Adding confirmation prompt if require_confirmation is true
    5. Adding undo option if include_undo is true

    {{ ctx.output_format }}
  "#
}

/// Generate an error message appropriate for the expertise level
function GenerateErrorMessage(
  error_details: ErrorTemplateDetails,
  expertise_level: ExpertiseLevel,
  error_context: string
) -> RenderedTemplate {
  client CustomSonnet4
  prompt #"
    Generate an appropriate error message for this expertise level.

    Error Code: {{ error_details.error_code }}
    Context: {{ error_context }}
    User Level: {{ expertise_level }}

    Templates by Level:
    - NOVICE: "{{ error_details.novice_template }}"
    - BEGINNER: "{{ error_details.beginner_template }}"
    - INTERMEDIATE: "{{ error_details.intermediate_template }}"
    - ADVANCED: "{{ error_details.advanced_template }}"
    - EXPERT: "{{ error_details.expert_template }}"

    Recovery Actions: {{ error_details.recovery_actions }}

    Guidelines:
    - NOVICE: Full explanation, empathetic tone, offer help, list 3 options
    - BEGINNER: Brief explanation, 2 options
    - INTERMEDIATE: Short message, 1 suggestion
    - ADVANCED: Minimal text, action link
    - EXPERT: Symbol/emoji + key info only

    Generate the error message matching the user's level.

    {{ ctx.output_format }}
  "#
}

/// Get the default template library with all standard templates
function GetDefaultTemplateLibrary() -> TemplateLibrary {
  client CustomSonnet4
  prompt #"
    Generate the default adaptive template library.

    Include templates for:
    1. SUCCESS_CONFIRMATION - Task/action completed successfully
    2. ERROR_MESSAGE - Something went wrong
    3. DISAMBIGUATION - Need clarification
    4. HELP_OFFER - Offering assistance
    5. FEATURE_SUGGESTION - Suggesting a feature/shortcut
    6. ACTION_CONFIRMATION - Confirming before action
    7. TASK_CREATION - Task created confirmation
    8. WELCOME_MESSAGE - Session greeting

    For each template, include 5 variants (NOVICE through EXPERT):

    NOVICE variants should:
    - Be verbose and explanatory
    - Include examples
    - Show all options
    - Always require confirmation
    - Use encouraging language

    BEGINNER variants should:
    - Be moderately detailed
    - Sometimes include examples
    - Show key options
    - Usually require confirmation

    INTERMEDIATE variants should:
    - Be concise but complete
    - Rarely include examples
    - Show main option
    - Sometimes require confirmation
    - Can mention shortcuts

    ADVANCED variants should:
    - Be minimal
    - Include shortcuts inline
    - Rarely require confirmation
    - Include undo option

    EXPERT variants should:
    - Use symbols/abbreviations
    - Maximum efficiency
    - Never require confirmation
    - Trust user completely

    Brand Voice: Professional yet friendly, helpful without being condescending
    Personality: Patient, clear, efficient, trustworthy

    {{ ctx.output_format }}
  "#
}

/// Get verbosity mappings for all expertise levels
function GetVerbosityMappings() -> VerbosityMapping[] {
  client CustomSonnet4
  prompt #"
    Generate the default verbosity mappings for each expertise level.

    Mappings should define:
    1. Default verbosity level
    2. Confirmation frequency
    3. Example frequency

    Guidelines:
    - NOVICE: DETAILED verbosity, always confirm, always examples
    - BEGINNER: DETAILED verbosity, sometimes confirm, sometimes examples
    - INTERMEDIATE: STANDARD verbosity, rarely confirm, rarely examples
    - ADVANCED: CONCISE verbosity, never confirm, never examples
    - EXPERT: MINIMAL verbosity, never confirm, never examples

    Confirmation frequencies: always, sometimes, rarely, never
    Example frequencies: always, sometimes, rarely, never

    {{ ctx.output_format }}
  "#
}
