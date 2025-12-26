// Language User Interface (LUI) Component Types
// Defines the schema for agent-friendly interface components

/// Core LUI component representing a single interface element
class LUIComponent {
  component_id string @description("Unique identifier for the component")
  component_type LUIComponentType
  intent string @description("What action or goal does this component enable")
  invocation InvocationPattern
  parameters ComponentParameter[]
  feedback FeedbackConfig
  accessibility AccessibilityConfig?
}

/// Types of LUI components based on their function
enum LUIComponentType {
  ACTION @description("Triggers an action (e.g., send message, create item)")
  QUERY @description("Retrieves information (e.g., search, lookup)")
  NAVIGATION @description("Changes context or view (e.g., go to, open)")
  INPUT @description("Collects user input (e.g., form fields, selections)")
  CONFIRMATION @description("Confirms an action before execution")
  FEEDBACK @description("Provides status, results, or notifications")
}

/// How users can invoke/trigger this component
class InvocationPattern {
  primary_phrase string @description("The main way to invoke this component")
  alternate_phrases string[] @description("Alternative ways to invoke (synonyms, variations)")
  examples string[] @description("Example natural language invocations")
  context_requirements ContextRequirement[]? @description("Required context for invocation")
}

/// Parameters that can be extracted from natural language
class ComponentParameter {
  name string @description("Parameter identifier")
  param_type ParameterType
  description string @description("What this parameter represents")
  required bool
  default_value string? @description("Default value if not provided")
  extraction_hints string[] @description("Patterns/phrases to identify this parameter in natural language")
  validation ValidationRule[]?
}

/// Types of parameters for type-safe extraction
enum ParameterType {
  STRING @description("Free-form text")
  NUMBER @description("Numeric value")
  BOOLEAN @description("True/false value")
  DATE @description("Date or datetime")
  ENUM @description("One of predefined options")
  ENTITY @description("Reference to a domain entity")
  LIST @description("Multiple values")
}

/// Validation rules for parameters
class ValidationRule {
  rule_type ValidationRuleType
  value string @description("The validation constraint value")
  error_message string
}

enum ValidationRuleType {
  MIN_LENGTH
  MAX_LENGTH
  MIN_VALUE
  MAX_VALUE
  PATTERN @description("Regex pattern")
  ENUM_VALUES @description("Allowed values, comma-separated")
  REQUIRED_FORMAT @description("Expected format description")
}

/// Configuration for conversational feedback
class FeedbackConfig {
  success_template string @description("Message template for successful execution")
  error_template string @description("Message template for errors")
  progress_template string? @description("Message template for in-progress status")
  confirmation_required bool @description("Whether to confirm before executing")
  confirmation_prompt string? @description("Custom confirmation message")
}

/// Accessibility configuration for inclusive design
class AccessibilityConfig {
  screen_reader_label string @description("Label for screen readers")
  keyboard_shortcut string? @description("Keyboard shortcut if available")
  voice_hints string[] @description("Pronunciation hints for voice interfaces")
  haptic_feedback bool @description("Whether haptic feedback is supported")
}
