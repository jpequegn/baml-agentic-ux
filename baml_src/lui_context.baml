// Context Types for LUI Components
// Defines the state and environment requirements for component invocation

/// Requirements for component context
class ContextRequirement {
  context_type ContextType
  description string @description("What this context requirement means")
  fallback_action string? @description("What to do if context is not available")
  error_message string? @description("Message to show when requirement not met")
}

/// Types of context that may be required
enum ContextType {
  USER_AUTHENTICATED @description("User must be logged in")
  RESOURCE_SELECTED @description("A specific resource must be selected/active")
  PREVIOUS_ACTION_COMPLETE @description("A prior action must have completed")
  PERMISSION_GRANTED @description("User must have specific permissions")
  DATA_AVAILABLE @description("Required data must be present")
  SESSION_ACTIVE @description("An active session is required")
  FEATURE_ENABLED @description("A specific feature flag must be enabled")
}

/// Runtime context for component execution
class ExecutionContext {
  session_id string
  user_id string?
  authenticated bool
  permissions string[]
  active_resources ResourceReference[]
  conversation_history ConversationTurn[]
  feature_flags string[]
}

/// Reference to a domain resource
class ResourceReference {
  resource_type string @description("Type of resource (e.g., 'document', 'user', 'project')")
  resource_id string
  display_name string
}

/// A single turn in the conversation history
class ConversationTurn {
  role ConversationRole
  content string
  timestamp string @description("ISO 8601 timestamp")
  component_id string? @description("Component that generated this turn, if any")
}

enum ConversationRole {
  USER
  ASSISTANT
  SYSTEM
}

/// Result of context validation
class ContextValidationResult {
  is_valid bool
  missing_requirements ContextRequirement[]
  suggestions string[] @description("Suggested actions to fulfill requirements")
}
