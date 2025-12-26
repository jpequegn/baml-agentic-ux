// GUI to LUI Converter
// Converts traditional GUI specifications to Language User Interface schemas

// ============================================
// GUI Specification Types
// ============================================

/// Complete GUI specification for conversion
class GUISpecification {
  name string @description("Name of the GUI/application")
  description string? @description("What this GUI does")
  component_tree GUIComponent[] @description("Hierarchical component structure")
  navigation NavigationStructure? @description("Navigation patterns")
  forms FormDefinition[]? @description("Form definitions")
  actions ActionDefinition[]? @description("Available actions")
  states StateDefinition[]? @description("UI states and transitions")
}

/// A single GUI component
class GUIComponent {
  component_id string? @description("Unique identifier")
  component_type GUIComponentType
  label string? @description("User-visible label")
  placeholder string? @description("Placeholder text")
  children GUIComponent[]? @description("Nested components")
  properties GUIProperty[]? @description("Component properties")
  events GUIEvent[]? @description("Events this component handles")
  validation GUIValidation[]? @description("Validation rules")
}

/// Types of GUI components
enum GUIComponentType {
  // Input components
  BUTTON @description("Clickable button")
  INPUT_TEXT @description("Text input field")
  INPUT_NUMBER @description("Numeric input")
  INPUT_EMAIL @description("Email input")
  INPUT_PASSWORD @description("Password input")
  INPUT_DATE @description("Date picker")
  INPUT_FILE @description("File upload")
  TEXTAREA @description("Multi-line text input")
  SELECT @description("Dropdown select")
  MULTISELECT @description("Multiple selection dropdown")
  CHECKBOX @description("Single checkbox")
  CHECKBOX_GROUP @description("Multiple checkboxes")
  RADIO_GROUP @description("Radio button group")
  TOGGLE @description("Toggle switch")
  SLIDER @description("Range slider")
  COLOR_PICKER @description("Color selection")

  // Navigation components
  LINK @description("Hyperlink")
  MENU @description("Navigation menu")
  TAB @description("Tab navigation")
  BREADCRUMB @description("Breadcrumb navigation")
  PAGINATION @description("Page navigation")

  // Container components
  MODAL @description("Modal dialog")
  DRAWER @description("Side drawer")
  ACCORDION @description("Collapsible sections")
  CARD @description("Card container")
  FORM @description("Form container")
  TABLE @description("Data table")
  LIST @description("List view")
  GRID @description("Grid layout")

  // Display components
  TEXT @description("Static text")
  HEADING @description("Section heading")
  IMAGE @description("Image display")
  ICON @description("Icon")
  BADGE @description("Status badge")
  ALERT @description("Alert message")
  TOOLTIP @description("Tooltip")
  PROGRESS @description("Progress indicator")
  AVATAR @description("User avatar")
  CHIP @description("Tag/chip")
}

/// Component property
class GUIProperty {
  property_name string
  property_value string
  property_type GUIPropertyType
}

enum GUIPropertyType {
  STRING
  NUMBER
  BOOLEAN
  ENUM
  STYLE
  DATA_BINDING
}

/// Event handler
class GUIEvent {
  event_type GUIEventType
  handler_description string @description("What happens when triggered")
  navigates_to string? @description("Target page/route if navigation")
  api_call string? @description("API endpoint if applicable")
}

enum GUIEventType {
  CLICK
  SUBMIT
  CHANGE
  FOCUS
  BLUR
  HOVER
  DRAG
  DROP
  SCROLL
  KEYBOARD
}

/// Validation rule for inputs
class GUIValidation {
  rule_type string @description("Type of validation")
  constraint string @description("Validation constraint")
  error_message string
}

// ============================================
// Navigation and Structure Types
// ============================================

/// Navigation structure of the application
class NavigationStructure {
  nav_type NavigationType
  items NavigationItem[]
  default_route string?
  auth_required_routes string[]?
}

enum NavigationType {
  SIDEBAR @description("Side navigation")
  TOP_BAR @description("Top navigation bar")
  BOTTOM_BAR @description("Bottom navigation")
  HAMBURGER @description("Hamburger menu")
  TAB_BAR @description("Tab-based navigation")
  BREADCRUMB @description("Breadcrumb-based")
}

class NavigationItem {
  item_id string
  label string
  route string
  icon string?
  children NavigationItem[]?
  badge_count int?
  requires_auth bool?
}

// ============================================
// Form and Action Types
// ============================================

/// Form definition
class FormDefinition {
  form_id string
  form_name string
  purpose string @description("What this form accomplishes")
  fields FormField[]
  submit_action string
  validation_mode ValidationMode
}

class FormField {
  field_id string
  field_label string
  field_type GUIComponentType
  required bool
  default_value string?
  options SelectOption[]? @description("For select/radio/checkbox")
  depends_on string[]? @description("Fields this depends on")
}

class SelectOption {
  value string
  label string
  disabled bool?
}

enum ValidationMode {
  ON_SUBMIT @description("Validate when form submitted")
  ON_BLUR @description("Validate when field loses focus")
  ON_CHANGE @description("Validate on every change")
  REAL_TIME @description("Continuous validation")
}

/// Action definition
class ActionDefinition {
  action_id string
  action_name string
  action_type ActionType
  description string
  requires_confirmation bool
  permission_required string?
  parameters ActionParameter[]?
}

enum ActionType {
  CREATE
  READ
  UPDATE
  DELETE
  NAVIGATE
  DOWNLOAD
  UPLOAD
  SHARE
  EXPORT
  IMPORT
  PRINT
  REFRESH
  SEARCH
  FILTER
  SORT
}

class ActionParameter {
  param_name string
  param_type string
  required bool
  source ParameterSource
}

enum ParameterSource {
  USER_INPUT @description("User enters value")
  SELECTION @description("From selected item")
  CONTEXT @description("From current context")
  COMPUTED @description("Calculated value")
}

// ============================================
// State Types
// ============================================

/// UI state definition
class StateDefinition {
  state_id string
  state_name string
  description string
  visible_components string[] @description("Component IDs visible in this state")
  enabled_actions string[] @description("Action IDs enabled in this state")
  transitions StateTransition[]
}

class StateTransition {
  trigger string @description("What triggers this transition")
  target_state string
  condition string?
}

// ============================================
// Conversion Options
// ============================================

/// Options for GUI to LUI conversion
class ConversionOptions {
  approach ConversionApproach @description("Overall conversion strategy")
  preserve_structure bool @description("Try to maintain GUI hierarchy")
  add_confirmations bool @description("Add confirmation steps for destructive actions")
  generate_help bool @description("Generate help/guidance flows")
  optimize_for_voice bool @description("Optimize for voice interaction")
  include_shortcuts bool @description("Include keyboard/voice shortcuts")
  group_related_actions bool @description("Group related actions into flows")
  max_flow_depth int? @description("Maximum steps in a flow")
}

enum ConversionApproach {
  LITERAL @description("Direct 1:1 mapping - preserves GUI structure")
  OPTIMIZED @description("Redesign for conversation - may restructure")
  HYBRID @description("Balance structure preservation with optimization")
  MINIMAL @description("Only essential components - simplified")
  COMPREHENSIVE @description("Full conversion with all features")
}

// ============================================
// Main Converter Function
// ============================================

/// Convert GUI specification to LUI schema
function ConvertGUIToLUI(
  gui_spec: GUISpecification,
  conversion_options: ConversionOptions,
  style_preferences: StylePreferences?
) -> ConversionResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    You are an expert at converting traditional GUI specifications to
    Language User Interfaces (LUI) optimized for AI agent interaction.

    ## GUI Specification
    {{ gui_spec }}

    ## Conversion Options
    - Approach: {{ conversion_options.approach }}
    - Preserve structure: {{ conversion_options.preserve_structure }}
    - Add confirmations: {{ conversion_options.add_confirmations }}
    - Generate help: {{ conversion_options.generate_help }}
    - Optimize for voice: {{ conversion_options.optimize_for_voice }}
    - Include shortcuts: {{ conversion_options.include_shortcuts }}
    - Group related actions: {{ conversion_options.group_related_actions }}
    {% if conversion_options.max_flow_depth %}
    - Max flow depth: {{ conversion_options.max_flow_depth }}
    {% endif %}

    {% if style_preferences %}
    ## Style Preferences
    - Tone: {{ style_preferences.tone }}
    - Verbosity: {{ style_preferences.verbosity }}
    - Formality: {{ style_preferences.formality }}
    {% endif %}

    ## Conversion Guidelines

    ### Button → ACTION Component
    - Extract the underlying intent from button label
    - Create natural invocation phrases users might say
    - Identify parameters from context or related inputs

    ### Form → Conversational Flow
    - Transform form fields into conversational prompts
    - Group related fields logically
    - Determine validation feedback messages
    - Create confirmation step if needed

    ### Navigation → NAVIGATION Components
    - Convert menu items to navigation intents
    - Create natural navigation phrases
    - Preserve hierarchy in context requirements

    ### Table/List → QUERY Components
    - Identify what data is displayed
    - Create search/filter patterns
    - Define sorting and pagination language

    ### Modal → Confirmation Flow
    - Convert modal triggers to flow starts
    - Handle modal content as flow steps
    - Map modal actions to flow completions

    Generate a complete LUI schema with:
    1. Components for each functional element
    2. Conversational flows for multi-step interactions
    3. Entity definitions from form/data structures
    4. Conversion notes explaining decisions

    {{ ctx.output_format }}
  "#
}

/// Result of GUI to LUI conversion
class ConversionResult {
  lui_schema InterfaceSchema @description("Generated LUI schema")
  conversion_notes ConversionNote[] @description("Notes about conversion decisions")
  warnings string[] @description("Potential issues or limitations")
  unmapped_elements string[] @description("GUI elements that couldn't be converted")
  suggestions string[] @description("Suggestions for improving the LUI")
}

class ConversionNote {
  source_element string @description("Original GUI element")
  target_element string @description("Resulting LUI element")
  conversion_type ConversionNoteType
  rationale string
}

enum ConversionNoteType {
  DIRECT_MAP @description("1:1 mapping")
  MERGED @description("Multiple elements combined")
  SPLIT @description("Single element split")
  TRANSFORMED @description("Significantly changed")
  ENHANCED @description("Added functionality")
  SIMPLIFIED @description("Reduced complexity")
  SKIPPED @description("Not converted")
}

// ============================================
// Visual Input Support
// ============================================

/// Analyze a screenshot/image to extract GUI specification
function AnalyzeGUIFromImage(
  image_description: string,
  context: string?
) -> GUIAnalysisResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Analyze this GUI description/screenshot and extract a structured
    GUI specification.

    ## Image/Screenshot Description
    {{ image_description }}

    {% if context %}
    ## Additional Context
    {{ context }}
    {% endif %}

    ## Analysis Task
    Identify and extract:
    1. All visible UI components with their types
    2. Component hierarchy and relationships
    3. Navigation patterns
    4. Forms and their fields
    5. Available actions (buttons, links, etc.)
    6. Data displays (tables, lists, cards)

    For each component, determine:
    - Component type
    - Label/text
    - Purpose/function
    - Relationships to other components
    - Events/interactions

    {{ ctx.output_format }}
  "#
}

class GUIAnalysisResult {
  extracted_spec GUISpecification
  confidence float @description("Confidence in extraction accuracy 0-1")
  ambiguities string[] @description("Uncertain interpretations")
  assumptions string[] @description("Assumptions made during analysis")
  recommended_verification string[] @description("Things to verify manually")
}

// ============================================
// Helper Functions
// ============================================

/// Convert a single form to conversational flow
function ConvertFormToFlow(
  form: FormDefinition,
  style: StylePreferences?
) -> ConversationalFlow {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Convert this form definition to a conversational flow.

    ## Form Definition
    {{ form }}

    {% if style %}
    ## Style Preferences
    - Tone: {{ style.tone }}
    - Verbosity: {{ style.verbosity }}
    {% endif %}

    ## Conversion Guidelines
    1. Each required field becomes a PROMPT step
    2. Group related fields where natural
    3. Add VALIDATE step after collection
    4. Add CONFIRM step before submission
    5. Include error handling for validation failures

    Create natural, conversational prompts that would feel
    natural to speak or type.

    {{ ctx.output_format }}
  "#
}

/// Convert navigation structure to LUI navigation patterns
function ConvertNavigationToLUI(
  navigation: NavigationStructure
) -> NavigationConversionResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Convert this navigation structure to LUI navigation patterns.

    ## Navigation Structure
    {{ navigation }}

    ## Conversion Guidelines
    1. Create natural navigation phrases for each route
    2. Handle nested navigation hierarchically
    3. Include breadcrumb-style context
    4. Add shortcuts for common destinations
    5. Consider voice-friendly alternatives

    {{ ctx.output_format }}
  "#
}

class NavigationConversionResult {
  components LUIComponent[]
  navigation_flow ConversationalFlow?
  shortcuts KeyboardShortcut[]?
  voice_commands string[]
}

class KeyboardShortcut {
  key_combination string
  action string
  description string
}

/// Analyze differences between GUI and generated LUI
function AnalyzeConversionDifferences(
  original_gui: GUISpecification,
  converted_lui: InterfaceSchema
) -> DifferenceAnalysis {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Analyze the differences between the original GUI and converted LUI.

    ## Original GUI
    {{ original_gui }}

    ## Converted LUI
    {{ converted_lui }}

    ## Analysis
    Compare and identify:
    1. Features present in GUI but not in LUI
    2. Features in LUI not in original GUI
    3. Functionality changes
    4. UX improvements
    5. Potential issues
    6. Recommendations

    {{ ctx.output_format }}
  "#
}

class DifferenceAnalysis {
  gui_only_features string[] @description("Features only in GUI")
  lui_only_features string[] @description("Features only in LUI")
  functionality_changes FunctionalityChange[]
  ux_improvements string[]
  potential_issues string[]
  recommendations string[]
  parity_score float @description("0-1 score of feature parity")
}

class FunctionalityChange {
  feature string
  gui_behavior string
  lui_behavior string
  change_type string @description("improved, simplified, different, lost")
  impact string
}

// ============================================
// Test Cases
// ============================================

test convert_login_form {
  functions [ConvertGUIToLUI]
  args {
    gui_spec {
      name "Login Page"
      description "User authentication page"
      component_tree [
        {
          component_id "login-form"
          component_type FORM
          label "Sign In"
          children [
            {
              component_id "email-input"
              component_type INPUT_EMAIL
              label "Email Address"
              placeholder "Enter your email"
              properties []
              events []
              validation [
                {
                  rule_type "required"
                  constraint "true"
                  error_message "Email is required"
                },
                {
                  rule_type "email"
                  constraint "true"
                  error_message "Please enter a valid email"
                }
              ]
            },
            {
              component_id "password-input"
              component_type INPUT_PASSWORD
              label "Password"
              placeholder "Enter your password"
              properties []
              events []
              validation [
                {
                  rule_type "required"
                  constraint "true"
                  error_message "Password is required"
                }
              ]
            },
            {
              component_id "remember-me"
              component_type CHECKBOX
              label "Remember me"
              properties []
              events []
              validation []
            },
            {
              component_id "login-button"
              component_type BUTTON
              label "Sign In"
              properties []
              events [
                {
                  event_type SUBMIT
                  handler_description "Authenticate user and redirect to dashboard"
                  navigates_to "/dashboard"
                  api_call "POST /api/auth/login"
                }
              ]
              validation []
            }
          ]
          properties []
          events []
          validation []
        },
        {
          component_id "forgot-password"
          component_type LINK
          label "Forgot Password?"
          properties []
          events [
            {
              event_type CLICK
              handler_description "Navigate to password reset"
              navigates_to "/forgot-password"
              api_call null
            }
          ]
          validation []
        }
      ]
      navigation null
      forms [
        {
          form_id "login-form"
          form_name "Login Form"
          purpose "Authenticate user"
          fields [
            {
              field_id "email"
              field_label "Email Address"
              field_type INPUT_EMAIL
              required true
              default_value null
              options null
              depends_on null
            },
            {
              field_id "password"
              field_label "Password"
              field_type INPUT_PASSWORD
              required true
              default_value null
              options null
              depends_on null
            }
          ]
          submit_action "login"
          validation_mode ON_SUBMIT
        }
      ]
      actions [
        {
          action_id "login"
          action_name "Sign In"
          action_type CREATE
          description "Authenticate user"
          requires_confirmation false
          permission_required null
          parameters [
            {
              param_name "email"
              param_type "string"
              required true
              source USER_INPUT
            },
            {
              param_name "password"
              param_type "string"
              required true
              source USER_INPUT
            }
          ]
        }
      ]
      states null
    }
    conversion_options {
      approach OPTIMIZED
      preserve_structure false
      add_confirmations false
      generate_help true
      optimize_for_voice true
      include_shortcuts true
      group_related_actions true
      max_flow_depth null
    }
    style_preferences {
      tone FRIENDLY
      verbosity STANDARD
      formality NEUTRAL
      language_code "en-US"
      brand_voice null
    }
  }
}

test convert_data_table {
  functions [ConvertGUIToLUI]
  args {
    gui_spec {
      name "User Management Table"
      description "Admin table for managing users"
      component_tree [
        {
          component_id "search-bar"
          component_type INPUT_TEXT
          label null
          placeholder "Search users..."
          children null
          properties []
          events [
            {
              event_type CHANGE
              handler_description "Filter table results"
              navigates_to null
              api_call "GET /api/users?search={query}"
            }
          ]
          validation []
        },
        {
          component_id "users-table"
          component_type TABLE
          label "Users"
          placeholder null
          children null
          properties [
            {
              property_name "columns"
              property_value "name,email,role,status,actions"
              property_type STRING
            }
          ]
          events []
          validation []
        }
      ]
      navigation null
      forms null
      actions [
        {
          action_id "edit-user"
          action_name "Edit User"
          action_type UPDATE
          description "Edit user details"
          requires_confirmation false
          permission_required "admin"
          parameters [
            {
              param_name "user_id"
              param_type "string"
              required true
              source SELECTION
            }
          ]
        },
        {
          action_id "delete-user"
          action_name "Delete User"
          action_type DELETE
          description "Remove user from system"
          requires_confirmation true
          permission_required "admin"
          parameters [
            {
              param_name "user_id"
              param_type "string"
              required true
              source SELECTION
            }
          ]
        }
      ]
      states null
    }
    conversion_options {
      approach HYBRID
      preserve_structure true
      add_confirmations true
      generate_help false
      optimize_for_voice false
      include_shortcuts true
      group_related_actions false
      max_flow_depth 5
    }
    style_preferences null
  }
}
