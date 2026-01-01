// Agent Capability Types
// BAML types for capability advertisement and schema definitions
// Compatible with A2A and MCP standards
// Issue #53 - Phase 3: Agent-to-Agent Interface Negotiation

// Dependencies:
// - TrustLevel, TrustRequirements from agent_identity.baml

// ============================================
// Capability Types
// ============================================

/// Types of capabilities an agent can provide
enum CapabilityType {
  ACTION @description("Performs an action with side effects")
  QUERY @description("Retrieves information without side effects")
  TRANSFORM @description("Transforms data from one format to another")
  COMPOSITE @description("Combines multiple capabilities into one")
  DELEGATION @description("Delegates execution to other agents")
  STREAMING @description("Provides streaming/continuous output")
  INTERACTIVE @description("Requires multi-turn interaction")
}

/// Full capability definition
class AgentCapability {
  capability_id string @description("Unique identifier for this capability")
  capability_type CapabilityType @description("Type of capability")
  name string @description("Human-readable name")
  description string @description("Detailed description of what this capability does")
  input_schema SchemaDefinition @description("Schema for capability input")
  output_schema SchemaDefinition @description("Schema for capability output")
  constraints CapabilityConstraint[] @description("Constraints on capability usage")
  performance_hints PerformanceHints? @description("Expected performance characteristics")
  trust_requirements TrustRequirements? @description("Trust requirements for this capability")
  examples CapabilityExample[]? @description("Usage examples")
  deprecated bool @description("Whether this capability is deprecated")
  deprecation_message string? @description("Message explaining deprecation and alternatives")
}

// ============================================
// Schema Definitions
// ============================================

/// Schema type for defining data structures
enum SchemaType {
  STRING @description("String value")
  NUMBER @description("Numeric value (integer or float)")
  INTEGER @description("Integer value")
  BOOLEAN @description("Boolean value")
  ARRAY @description("Array/list of items")
  OBJECT @description("Complex object with properties")
  NULL @description("Null value")
  ANY @description("Any type allowed")
  UNION @description("One of multiple types")
  ENUM @description("Enumerated string values")
  REFERENCE @description("Reference to another schema definition")
}

/// Definition of a data schema (JSON Schema compatible but BAML-native)
class SchemaDefinition {
  schema_id string? @description("Optional ID for referencing this schema")
  type SchemaType @description("Primary type of this schema")
  description string? @description("Description of what this schema represents")
  properties SchemaProperty[]? @description("Properties for OBJECT type")
  required string[]? @description("List of required property names")
  items SchemaDefinition? @description("Item schema for ARRAY type")
  enum_values string[]? @description("Allowed values for ENUM type")
  union_types SchemaDefinition[]? @description("Possible types for UNION type")
  reference string? @description("Schema ID for REFERENCE type")
  format string? @description("Format hint (e.g., 'date-time', 'email', 'uri')")
  default_value string? @description("Default value as JSON string")
  examples string[]? @description("Example values as JSON strings")
  constraints SchemaConstraint[]? @description("Validation constraints")
}

/// A property within an object schema
class SchemaProperty {
  name string @description("Property name")
  schema SchemaDefinition @description("Schema for this property")
  description string? @description("Description of this property")
  deprecated bool @description("Whether this property is deprecated")
}

/// Constraints on schema values
class SchemaConstraint {
  constraint_type SchemaConstraintType @description("Type of constraint")
  value string @description("Constraint value as JSON")
  error_message string? @description("Custom error message")
}

/// Types of schema constraints
enum SchemaConstraintType {
  MIN_LENGTH @description("Minimum string length")
  MAX_LENGTH @description("Maximum string length")
  MIN_VALUE @description("Minimum numeric value")
  MAX_VALUE @description("Maximum numeric value")
  PATTERN @description("Regex pattern for strings")
  MIN_ITEMS @description("Minimum array length")
  MAX_ITEMS @description("Maximum array length")
  UNIQUE_ITEMS @description("Array items must be unique")
  ADDITIONAL_PROPERTIES @description("Whether extra properties allowed")
}

// ============================================
// Capability Constraints
// ============================================

/// Constraints on capability usage
class CapabilityConstraint {
  constraint_id string @description("Unique identifier for this constraint")
  constraint_type ConstraintCategory @description("Category of constraint")
  description string @description("Human-readable description")
  enforcement ConstraintEnforcement @description("How constraint is enforced")
  parameters map<string, string> @description("Constraint parameters")
}

/// Categories of capability constraints
enum ConstraintCategory {
  RATE_LIMIT @description("Limits on invocation frequency")
  SIZE_LIMIT @description("Limits on input/output size")
  TIME_LIMIT @description("Limits on execution time")
  RESOURCE_LIMIT @description("Limits on resource usage")
  CONCURRENCY_LIMIT @description("Limits on concurrent executions")
  DEPENDENCY @description("Requires another capability")
  EXCLUSION @description("Mutually exclusive with another capability")
  PREREQUISITE @description("Requires prior successful invocation")
}

/// How constraints are enforced
enum ConstraintEnforcement {
  HARD @description("Request rejected if constraint violated")
  SOFT @description("Warning issued but request proceeds")
  INFORMATIONAL @description("Information only, not enforced")
}

// ============================================
// Performance Hints
// ============================================

/// Performance characteristics of a capability
class PerformanceHints {
  typical_latency_ms int @description("Typical response time in milliseconds")
  max_latency_ms int @description("Maximum expected response time")
  throughput_rps float @description("Expected requests per second capacity")
  cost_estimate CostEstimate? @description("Estimated cost per invocation")
  resource_intensity ResourceIntensity @description("Resource usage level")
  supports_batching bool @description("Whether batched requests are supported")
  supports_streaming bool @description("Whether streaming responses are supported")
  idempotent bool @description("Whether capability is idempotent")
  cacheable bool @description("Whether results can be cached")
  cache_ttl_seconds int? @description("Recommended cache TTL if cacheable")
}

/// Estimated cost of capability invocation
class CostEstimate {
  currency string @description("Currency code (e.g., USD)")
  per_invocation float @description("Base cost per invocation")
  per_input_unit float? @description("Additional cost per input unit")
  per_output_unit float? @description("Additional cost per output unit")
  unit_type string? @description("Type of unit (e.g., token, KB)")
}

/// Resource usage intensity levels
enum ResourceIntensity {
  MINIMAL @description("Very low resource usage")
  LOW @description("Below average resource usage")
  MEDIUM @description("Average resource usage")
  HIGH @description("Above average resource usage")
  VERY_HIGH @description("Very high resource usage, use sparingly")
}

// ============================================
// Capability Examples
// ============================================

/// Example usage of a capability
class CapabilityExample {
  example_id string @description("Unique identifier for this example")
  name string @description("Name of this example")
  description string @description("What this example demonstrates")
  input string @description("Example input as JSON string")
  output string @description("Expected output as JSON string")
  notes string? @description("Additional notes about this example")
}

// ============================================
// Capability Advertisement
// ============================================

/// Advertisement of capabilities from an agent
class CapabilityAdvertisement {
  advertisement_id string @description("Unique identifier for this advertisement")
  agent_id string @description("ID of the advertising agent")
  capabilities AgentCapability[] @description("Advertised capabilities")
  advertised_at string @description("ISO 8601 timestamp of advertisement")
  expires_at string? @description("ISO 8601 timestamp when advertisement expires")
  version string @description("Version of the capability set")
}

/// Query for finding capabilities
class CapabilityQuery {
  query_id string @description("Unique identifier for this query")
  capability_type CapabilityType? @description("Filter by capability type")
  keyword string? @description("Search keyword for name/description")
  input_schema_type SchemaType? @description("Filter by input schema type")
  output_schema_type SchemaType? @description("Filter by output schema type")
  max_latency_ms int? @description("Maximum acceptable latency")
  require_idempotent bool? @description("Require idempotent capabilities")
  limit int @description("Maximum number of results")
  offset int @description("Offset for pagination")
}

/// Result of a capability query
class CapabilityQueryResult {
  query_id string @description("ID of the original query")
  capabilities CapabilityMatch[] @description("Matching capabilities")
  total_count int @description("Total number of matches")
  has_more bool @description("Whether more results are available")
}

/// A capability match with relevance score
class CapabilityMatch {
  capability AgentCapability @description("The matched capability")
  agent_id string @description("ID of the agent providing this capability")
  relevance_score float @description("Relevance score (0.0 to 1.0)")
  match_reasons string[] @description("Reasons why this capability matched")
}

// ============================================
// Capability Invocation
// ============================================

/// Request to invoke a capability
class CapabilityInvocation {
  invocation_id string @description("Unique identifier for this invocation")
  capability_id string @description("ID of capability to invoke")
  agent_id string @description("ID of agent providing the capability")
  input string @description("Input data as JSON string")
  correlation_id string? @description("Correlation ID for tracking")
  timeout_ms int? @description("Timeout for this invocation")
  priority InvocationPriority @description("Priority of this invocation")
  metadata map<string, string>? @description("Additional invocation metadata")
}

/// Priority levels for capability invocation
enum InvocationPriority {
  LOW @description("Low priority, can be delayed")
  NORMAL @description("Normal priority")
  HIGH @description("High priority, process quickly")
  CRITICAL @description("Critical, process immediately")
}

/// Result of a capability invocation
class InvocationResult {
  invocation_id string @description("ID of the invocation")
  status InvocationStatus @description("Status of the invocation")
  output string? @description("Output data as JSON string if successful")
  error InvocationError? @description("Error details if failed")
  execution_time_ms int @description("Time taken to execute")
  completed_at string @description("ISO 8601 timestamp of completion")
  metadata map<string, string>? @description("Additional result metadata")
}

/// Status of a capability invocation
enum InvocationStatus {
  PENDING @description("Invocation is queued")
  RUNNING @description("Invocation is executing")
  SUCCEEDED @description("Invocation completed successfully")
  FAILED @description("Invocation failed with error")
  TIMEOUT @description("Invocation timed out")
  CANCELLED @description("Invocation was cancelled")
}

/// Error details for failed invocation
class InvocationError {
  error_code string @description("Machine-readable error code")
  error_message string @description("Human-readable error message")
  error_type ErrorType @description("Category of error")
  retryable bool @description("Whether invocation can be retried")
  retry_after_ms int? @description("Suggested wait time before retry")
  details map<string, string>? @description("Additional error details")
}

/// Types of invocation errors
enum ErrorType {
  VALIDATION @description("Input validation failed")
  AUTHENTICATION @description("Authentication failed")
  AUTHORIZATION @description("Authorization failed")
  NOT_FOUND @description("Capability or agent not found")
  RATE_LIMITED @description("Rate limit exceeded")
  RESOURCE_EXHAUSTED @description("Resource limits exceeded")
  TIMEOUT @description("Execution timed out")
  INTERNAL @description("Internal error")
  UNAVAILABLE @description("Service unavailable")
  DEPENDENCY_FAILED @description("Dependent capability failed")
}
