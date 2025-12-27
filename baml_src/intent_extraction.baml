// Intent Extraction and Routing
// Extracts user intent and routes to appropriate LUI components

// ============================================
// Intent Types
// ============================================

/// Represents a detected user intent
class Intent {
  intent_name string @description("Human-readable intent name")
  intent_category IntentCategory
  target_component string @description("LUIComponent ID to route to")
  action_verb string @description("The main action verb (create, find, update, etc.)")
}

/// Categories of user intents
enum IntentCategory {
  CREATE @description("Creating new resources")
  READ @description("Reading or viewing existing resources")
  UPDATE @description("Modifying existing resources")
  DELETE @description("Removing resources")
  NAVIGATE @description("Moving between views or sections")
  QUERY @description("Searching or filtering data")
  CONFIGURE @description("Changing settings or preferences")
  HELP @description("Requesting assistance or information")
}

// Note: ExtractedParameter is defined in lui_examples.baml

/// Information about ambiguous intents
class AmbiguityInfo {
  is_ambiguous bool @description("Whether the input is ambiguous")
  possible_intents Intent[] @description("List of possible matching intents")
  disambiguation_question string @description("Question to resolve ambiguity")
}

/// Complete result of intent extraction
class IntentExtraction {
  detected_intent Intent @description("The primary detected intent")
  confidence float @description("Overall confidence in the extraction (0-1)")
  extracted_parameters ExtractedParameter[] @description("Parameters found in input")
  ambiguity AmbiguityInfo? @description("Ambiguity info if present")
  suggested_clarification string? @description("Clarifying question if needed")
}

// ============================================
// Context Types for Intent Extraction
// ============================================

/// Conversation context to improve intent extraction
class ConversationContext {
  recent_messages ConversationMessage[] @description("Recent conversation history")
  current_state string? @description("Current application state")
  active_entity string? @description("Currently focused entity ID")
  user_preferences UserPreferences? @description("Known user preferences")
}

/// A message in conversation history
class ConversationMessage {
  role MessageRole
  content string
  timestamp string? @description("ISO 8601 timestamp")
  extracted_intent Intent? @description("Intent from this message if any")
}

enum MessageRole {
  USER
  ASSISTANT
  SYSTEM
}

/// User preferences that affect intent interpretation
class UserPreferences {
  preferred_language string? @description("User's preferred language code")
  verbosity_preference VerbosityPreference? @description("How detailed responses should be")
  shortcuts map<string, string>? @description("User-defined command shortcuts")
}

enum VerbosityPreference {
  BRIEF
  STANDARD
  DETAILED
}

// ============================================
// Multi-Intent Support
// ============================================

/// Result when multiple intents are detected in a single input
class MultiIntentExtraction {
  intents IntentExtraction[] @description("All detected intents in order")
  execution_strategy ExecutionStrategy @description("How to handle multiple intents")
  dependencies IntentDependency[]? @description("Dependencies between intents")
}

/// How to execute multiple intents
enum ExecutionStrategy {
  SEQUENTIAL @description("Execute intents one after another")
  PARALLEL @description("Execute intents simultaneously if possible")
  CONDITIONAL @description("Later intents depend on earlier results")
  USER_CHOICE @description("Let user choose which intent to execute")
}

/// Dependency relationship between intents
class IntentDependency {
  dependent_intent_index int @description("Index of the dependent intent")
  depends_on_index int @description("Index of the intent it depends on")
  dependency_type DependencyType
}

enum DependencyType {
  REQUIRES_COMPLETION @description("Must complete before dependent can start")
  REQUIRES_SUCCESS @description("Must succeed for dependent to execute")
  SHARES_PARAMETER @description("Output of one is input to another")
}

// ============================================
// Routing Types
// ============================================

/// Result of routing an intent to a component
class RoutingResult {
  matched_component ComponentMatch @description("The matched component")
  parameter_bindings ParameterBinding[] @description("Mapped parameters")
  missing_required MissingParameter[]? @description("Required params not provided")
  execution_ready bool @description("Whether all required info is available")
}

/// A matched LUI component
class ComponentMatch {
  component_id string
  component_type LUIComponentType
  match_confidence float @description("How well the intent matches (0-1)")
  match_reason string @description("Why this component was matched")
}

/// Binding of extracted value to component parameter
class ParameterBinding {
  parameter_name string
  bound_value string
  source ExtractedParameter
  requires_validation bool @description("Whether value needs validation")
}

/// A required parameter that was not provided
class MissingParameter {
  parameter_name string
  parameter_type string
  prompt_for_value string @description("Question to ask user for this value")
  has_default bool @description("Whether a default value exists")
}

// ============================================
// Main Extraction Function
// ============================================

/// Extract user intent and match to LUI components
function ExtractIntent(
  user_input: string,
  interface_schema: InterfaceSchema,
  conversation_context: ConversationContext?
) -> IntentExtraction {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    You are an intent extraction system for a Language User Interface (LUI).
    Your task is to understand what the user wants to do and match it to available components.

    ## User Input
    "{{ user_input }}"

    ## Available Components
    {% for component in interface_schema.components %}
    - **{{ component.component_id }}** ({{ component.component_type }}): {{ component.intent }}
      Primary invocation: "{{ component.invocation.primary_phrase }}"
      {% if component.invocation.alternate_phrases %}
      Alternates: {{ component.invocation.alternate_phrases }}
      {% endif %}
      {% if component.parameters %}
      Parameters:
      {% for param in component.parameters %}
        - {{ param.name }} ({{ param.param_type }}{% if param.required %}, required{% endif %}): {{ param.description }}
          {% if param.extraction_hints %}Hints: {{ param.extraction_hints }}{% endif %}
      {% endfor %}
      {% endif %}
    {% endfor %}

    {% if conversation_context %}
    ## Conversation Context
    {% if conversation_context.recent_messages %}
    Recent conversation:
    {% for msg in conversation_context.recent_messages %}
    - {{ msg.role }}: {{ msg.content }}
    {% endfor %}
    {% endif %}
    {% if conversation_context.current_state %}
    Current state: {{ conversation_context.current_state }}
    {% endif %}
    {% if conversation_context.active_entity %}
    Active entity: {{ conversation_context.active_entity }}
    {% endif %}
    {% endif %}

    ## Instructions
    1. Identify the user's primary intent
    2. Match it to the most appropriate component
    3. Extract any parameter values from the input
    4. Assess confidence in the extraction
    5. If ambiguous, identify alternatives and suggest a clarifying question

    Consider:
    - Synonyms and variations of invocation phrases
    - Implicit parameters from context
    - Partial matches that might need clarification
    - The conversation history for context

    {{ ctx.output_format }}
  "#
}

// ============================================
// Multi-Intent Extraction Function
// ============================================

/// Extract multiple intents from a compound user input
function ExtractMultipleIntents(
  user_input: string,
  interface_schema: InterfaceSchema,
  conversation_context: ConversationContext?
) -> MultiIntentExtraction {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    You are a multi-intent extraction system for a Language User Interface (LUI).
    Users may express multiple intentions in a single message.

    ## User Input
    "{{ user_input }}"

    ## Available Components
    {% for component in interface_schema.components %}
    - **{{ component.component_id }}** ({{ component.component_type }}): {{ component.intent }}
      Invocation: "{{ component.invocation.primary_phrase }}"
      {% if component.parameters %}
      Parameters: {% for param in component.parameters %}{{ param.name }}{% if not loop.last %}, {% endif %}{% endfor %}
      {% endif %}
    {% endfor %}

    {% if conversation_context %}
    ## Context
    {% if conversation_context.current_state %}Current state: {{ conversation_context.current_state }}{% endif %}
    {% if conversation_context.active_entity %}Active entity: {{ conversation_context.active_entity }}{% endif %}
    {% endif %}

    ## Instructions
    1. Identify ALL distinct intents in the input
    2. Order them by their logical sequence
    3. Determine the best execution strategy
    4. Identify any dependencies between intents

    Look for:
    - Conjunctions: "and", "then", "also", "after that"
    - Implied sequences: "create X and add to Y"
    - Conditional requests: "if X then Y"

    {{ ctx.output_format }}
  "#
}

// ============================================
// Routing Function
// ============================================

/// Route an extracted intent to its target component
function RouteIntent(
  intent_extraction: IntentExtraction,
  interface_schema: InterfaceSchema
) -> RoutingResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    You are a routing system for a Language User Interface (LUI).
    Given an extracted intent, prepare it for execution by the target component.

    ## Extracted Intent
    - Name: {{ intent_extraction.detected_intent.intent_name }}
    - Category: {{ intent_extraction.detected_intent.intent_category }}
    - Target: {{ intent_extraction.detected_intent.target_component }}
    - Confidence: {{ intent_extraction.confidence }}

    ## Extracted Parameters
    {% for param in intent_extraction.extracted_parameters %}
    - {{ param.parameter_name }}: "{{ param.extracted_value }}" (confidence: {{ param.confidence }})
      From: "{{ param.source_text }}"
    {% endfor %}

    ## Target Component Details
    {% for component in interface_schema.components %}
    {% if component.component_id == intent_extraction.detected_intent.target_component %}
    Component: {{ component.component_id }}
    Type: {{ component.component_type }}
    Intent: {{ component.intent }}
    {% if component.parameters %}
    Required Parameters:
    {% for param in component.parameters %}
    - {{ param.name }} ({{ param.param_type }}{% if param.required %}, REQUIRED{% endif %}): {{ param.description }}
    {% endfor %}
    {% endif %}
    {% endif %}
    {% endfor %}

    ## Instructions
    1. Match extracted parameters to component parameters
    2. Identify any required parameters that are missing
    3. Generate prompts for missing required parameters
    4. Determine if execution can proceed

    {{ ctx.output_format }}
  "#
}

// ============================================
// Disambiguation Function
// ============================================

/// Resolve ambiguity when multiple intents match
function DisambiguateIntent(
  user_input: string,
  ambiguity_info: AmbiguityInfo,
  user_response: string,
  interface_schema: InterfaceSchema
) -> IntentExtraction {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    You are resolving an ambiguous user intent based on their clarification.

    ## Original Input
    "{{ user_input }}"

    ## Ambiguity Detected
    Question asked: "{{ ambiguity_info.disambiguation_question }}"

    Possible intents:
    {% for intent in ambiguity_info.possible_intents %}
    {{ loop.index }}. {{ intent.intent_name }} ({{ intent.intent_category }}) → {{ intent.target_component }}
    {% endfor %}

    ## User's Clarification
    "{{ user_response }}"

    ## Available Components
    {% for component in interface_schema.components %}
    - {{ component.component_id }}: {{ component.intent }}
    {% endfor %}

    ## Instructions
    Based on the user's clarification, determine:
    1. Which intent they meant
    2. Any additional parameters revealed
    3. Final confidence level

    {{ ctx.output_format }}
  "#
}

// ============================================
// Test Cases
// ============================================

test extract_simple_intent {
  functions [ExtractIntent]
  args {
    user_input "create a new task called Review PR"
    interface_schema {
      schema_id "test-schema"
      name "Task Manager"
      description "Task management interface"
      version "1.0.0"
      domain {
        domain_name "task-management"
        subdomain null
        description "Task tracking"
        key_concepts ["tasks", "projects"]
        terminology null
      }
      components [
        {
          component_id "create-task"
          component_type ACTION
          intent "Create a new task"
          invocation {
            primary_phrase "create task"
            alternate_phrases ["add task", "new task"]
            examples ["Create a task to review code"]
            context_requirements null
          }
          parameters [
            {
              name "title"
              param_type "string"
              description "Task title"
              required true
              default_value null
              extraction_hints ["the name", "called", "titled"]
              validation null
            }
          ]
          feedback {
            success_template "Task created"
            error_template "Failed to create task"
            progress_template null
            confirmation_required false
            confirmation_prompt null
          }
          accessibility null
        }
      ]
      flows []
      entities []
      global_context null
    }
    conversation_context null
  }
}

test extract_intent_with_context {
  functions [ExtractIntent]
  args {
    user_input "mark it as complete"
    interface_schema {
      schema_id "test-schema"
      name "Task Manager"
      description "Task management interface"
      version "1.0.0"
      domain {
        domain_name "task-management"
        subdomain null
        description "Task tracking"
        key_concepts ["tasks"]
        terminology null
      }
      components [
        {
          component_id "complete-task"
          component_type ACTION
          intent "Mark a task as complete"
          invocation {
            primary_phrase "complete task"
            alternate_phrases ["mark complete", "finish task", "done with task"]
            examples ["Mark the review task as complete"]
            context_requirements null
          }
          parameters [
            {
              name "task_id"
              param_type "string"
              description "ID of task to complete"
              required true
              default_value null
              extraction_hints null
              validation null
            }
          ]
          feedback {
            success_template "Task marked complete"
            error_template "Could not complete task"
            progress_template null
            confirmation_required false
            confirmation_prompt null
          }
          accessibility null
        }
      ]
      flows []
      entities []
      global_context null
    }
    conversation_context {
      recent_messages [
        {
          role USER
          content "Show me task #123"
          timestamp "2025-01-15T10:00:00Z"
          extracted_intent null
        },
        {
          role ASSISTANT
          content "Here is task #123: Review PR"
          timestamp "2025-01-15T10:00:01Z"
          extracted_intent null
        }
      ]
      current_state "viewing-task"
      active_entity "task-123"
      user_preferences null
    }
  }
}

test extract_multiple_intents {
  functions [ExtractMultipleIntents]
  args {
    user_input "create a task for code review and then assign it to John"
    interface_schema {
      schema_id "test-schema"
      name "Task Manager"
      description "Task management"
      version "1.0.0"
      domain {
        domain_name "task-management"
        subdomain null
        description "Tasks"
        key_concepts ["tasks", "assignments"]
        terminology null
      }
      components [
        {
          component_id "create-task"
          component_type ACTION
          intent "Create a new task"
          invocation {
            primary_phrase "create task"
            alternate_phrases ["add task"]
            examples []
            context_requirements null
          }
          parameters [
            {
              name "title"
              param_type "string"
              description "Task title"
              required true
              default_value null
              extraction_hints null
              validation null
            }
          ]
          feedback {
            success_template "Created"
            error_template "Failed"
            progress_template null
            confirmation_required false
            confirmation_prompt null
          }
          accessibility null
        },
        {
          component_id "assign-task"
          component_type ACTION
          intent "Assign a task to someone"
          invocation {
            primary_phrase "assign task"
            alternate_phrases ["give task to"]
            examples []
            context_requirements null
          }
          parameters [
            {
              name "task_id"
              param_type "string"
              description "Task to assign"
              required true
              default_value null
              extraction_hints null
              validation null
            },
            {
              name "assignee"
              param_type "string"
              description "Person to assign to"
              required true
              default_value null
              extraction_hints ["to", "for"]
              validation null
            }
          ]
          feedback {
            success_template "Assigned"
            error_template "Failed"
            progress_template null
            confirmation_required false
            confirmation_prompt null
          }
          accessibility null
        }
      ]
      flows []
      entities []
      global_context null
    }
    conversation_context null
  }
}

test route_extracted_intent {
  functions [RouteIntent]
  args {
    intent_extraction {
      detected_intent {
        intent_name "Create Task"
        intent_category CREATE
        target_component "create-task"
        action_verb "create"
      }
      confidence 0.95
      extracted_parameters [
        {
          parameter_name "title"
          extracted_value "Review PR #42"
          source_text "called Review PR #42"
          confidence 0.9
        }
      ]
      ambiguity null
      suggested_clarification null
    }
    interface_schema {
      schema_id "test-schema"
      name "Task Manager"
      description "Task management"
      version "1.0.0"
      domain {
        domain_name "task-management"
        subdomain null
        description "Tasks"
        key_concepts ["tasks"]
        terminology null
      }
      components [
        {
          component_id "create-task"
          component_type ACTION
          intent "Create a new task"
          invocation {
            primary_phrase "create task"
            alternate_phrases []
            examples []
            context_requirements null
          }
          parameters [
            {
              name "title"
              param_type "string"
              description "Task title"
              required true
              default_value null
              extraction_hints null
              validation null
            },
            {
              name "priority"
              param_type "string"
              description "Task priority"
              required false
              default_value "medium"
              extraction_hints null
              validation null
            }
          ]
          feedback {
            success_template "Created"
            error_template "Failed"
            progress_template null
            confirmation_required false
            confirmation_prompt null
          }
          accessibility null
        }
      ]
      flows []
      entities []
      global_context null
    }
  }
}
