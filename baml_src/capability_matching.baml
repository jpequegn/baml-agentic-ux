// Capability Matching Algorithms
// Schema matching for determining capability compatibility between agents
// Issue #56 - Phase 3: Agent-to-Agent Interface Negotiation

// Dependencies:
// - AgentCapability, SchemaDefinition, SchemaType from agent_capability.baml
// - CapabilityType from agent_capability.baml

// ============================================
// Schema Compatibility Types
// ============================================

/// Direction of schema transformation
enum TransformationDirection {
  INPUT_TO_REQUIRED @description("Transform offered input to match required input")
  OUTPUT_TO_REQUIRED @description("Transform offered output to match required output")
  BIDIRECTIONAL @description("Transformation needed in both directions")
}

/// Type of schema transformation needed
enum TransformationType {
  TYPE_COERCION @description("Convert between compatible types (e.g., int to float)")
  PROPERTY_RENAME @description("Rename a property to match expected name")
  PROPERTY_ADD @description("Add a missing property with default value")
  PROPERTY_REMOVE @description("Remove an extra property")
  FORMAT_CONVERSION @description("Convert between formats (e.g., date formats)")
  ARRAY_WRAP @description("Wrap single value in array")
  ARRAY_UNWRAP @description("Extract single value from array")
  OPTIONAL_TO_REQUIRED @description("Handle optional field becoming required")
  ENUM_MAPPING @description("Map enum values between different sets")
  NESTED_TRANSFORM @description("Apply transformation to nested schema")
}

/// Complexity level of a transformation
enum TransformationComplexity {
  TRIVIAL @description("Automatic, no data loss possible")
  SIMPLE @description("Straightforward, minimal risk")
  MODERATE @description("Requires some care, possible edge cases")
  COMPLEX @description("Significant effort, careful testing needed")
  RISKY @description("High risk of data loss or errors")
}

/// A specific schema transformation that can be applied
class SchemaTransformation {
  transformation_type TransformationType @description("Type of transformation")
  direction TransformationDirection @description("Direction of transformation")
  source_path string @description("JSON path to source field")
  target_path string @description("JSON path to target field")
  complexity TransformationComplexity @description("Complexity of transformation")
  reversible bool @description("Whether transformation can be reversed")
  description string @description("Human-readable description")
  example_before string? @description("Example value before transformation")
  example_after string? @description("Example value after transformation")
}

/// Compatibility assessment between two schemas
class SchemaCompatibility {
  input_compatible bool @description("Whether input schemas are compatible")
  output_compatible bool @description("Whether output schemas are compatible")
  input_score float @description("Input compatibility score (0.0-1.0)")
  output_score float @description("Output compatibility score (0.0-1.0)")
  overall_score float @description("Combined compatibility score (0.0-1.0)")
  transformations_needed SchemaTransformation[] @description("Transformations to achieve compatibility")
  property_matches PropertyMatch[] @description("Detailed property-level matches")
  warnings string[] @description("Compatibility warnings")
}

/// Match result for a single property
class PropertyMatch {
  required_property string @description("Property name in required schema")
  offered_property string? @description("Matching property in offered schema")
  match_score float @description("Match score for this property (0.0-1.0)")
  match_reason string @description("Reason for match/no-match")
  type_compatible bool @description("Whether types are compatible")
  transformation_needed SchemaTransformation? @description("Transformation if needed")
}

// ============================================
// Capability Matching Types
// ============================================

/// Result of matching a required capability against an offered capability
class CapabilityMatchResult {
  overall_compatibility float @description("Overall compatibility score (0.0-1.0)")
  type_score float @description("Capability type match score (0.0-1.0)")
  name_score float @description("Name similarity score (0.0-1.0)")
  description_score float @description("Description similarity score (0.0-1.0)")
  schema_score float @description("Schema compatibility score (0.0-1.0)")
  matches CapabilityDetailedMatch[] @description("Detailed match information")
  unmatched_requirements string[] @description("Required capabilities not matched")
  adaptation_suggestions AdaptationSuggestion[] @description("Suggestions for improving compatibility")
  compatible bool @description("Whether capabilities are compatible enough for use")
  confidence float @description("Confidence in the match assessment (0.0-1.0)")
}

/// Detailed match information for a single capability pair
class CapabilityDetailedMatch {
  required_capability string @description("ID of required capability")
  matched_capability string @description("ID of matched capability")
  compatibility_score float @description("Compatibility score for this pair (0.0-1.0)")
  schema_compatibility SchemaCompatibility @description("Schema compatibility details")
  constraint_satisfaction ConstraintSatisfaction @description("Constraint satisfaction status")
  performance_adequate bool @description("Whether performance meets requirements")
  trust_adequate bool @description("Whether trust level is adequate")
}

/// Status of constraint satisfaction
class ConstraintSatisfaction {
  all_satisfied bool @description("Whether all required constraints are satisfied")
  satisfied_constraints string[] @description("List of satisfied constraint IDs")
  unsatisfied_constraints string[] @description("List of unsatisfied constraint IDs")
  partially_satisfied string[] @description("Constraints that are partially met")
  notes string[] @description("Notes about constraint satisfaction")
}

// ============================================
// Adaptation Suggestions
// ============================================

/// Suggestion for adapting capabilities to improve compatibility
class AdaptationSuggestion {
  suggestion_id string @description("Unique identifier for this suggestion")
  suggestion_type SuggestionType @description("Type of adaptation suggested")
  priority SuggestionPriority @description("Priority/importance of suggestion")
  description string @description("Human-readable description of suggestion")
  effort_estimate EffortLevel @description("Estimated effort to implement")
  compatibility_improvement float @description("Expected score improvement (0.0-1.0)")
  implementation_hints string[] @description("Hints for implementation")
  risks string[] @description("Potential risks of this adaptation")
}

/// Types of adaptation suggestions
enum SuggestionType {
  SCHEMA_TRANSFORM @description("Apply schema transformation")
  ADD_WRAPPER @description("Add wrapper/adapter layer")
  PROTOCOL_BRIDGE @description("Add protocol bridging")
  TYPE_CONVERTER @description("Add type conversion")
  DEFAULT_VALUES @description("Add default values for missing fields")
  VALIDATION_LAYER @description("Add validation layer")
  CACHING_LAYER @description("Add caching for performance")
  FALLBACK @description("Use fallback capability")
  COMPOSITION @description("Compose multiple capabilities")
  CUSTOM_ADAPTER @description("Implement custom adapter")
}

/// Priority levels for suggestions
enum SuggestionPriority {
  CRITICAL @description("Must be addressed for any compatibility")
  HIGH @description("Strongly recommended for good compatibility")
  MEDIUM @description("Would improve compatibility")
  LOW @description("Nice to have, minor improvement")
  OPTIONAL @description("Optional enhancement")
}

/// Effort levels for implementation
enum EffortLevel {
  TRIVIAL @description("Minimal effort, quick fix")
  LOW @description("Small effort, straightforward")
  MEDIUM @description("Moderate effort required")
  HIGH @description("Significant effort needed")
  VERY_HIGH @description("Major undertaking")
}

// ============================================
// Matching Request/Response
// ============================================

/// Request to match capabilities
class CapabilityMatchRequest {
  request_id string @description("Unique request identifier")
  required_capabilities AgentCapability[] @description("Capabilities being requested")
  offered_capabilities AgentCapability[] @description("Capabilities being offered")
  match_options MatchOptions @description("Options for matching algorithm")
  context MatchContext? @description("Additional context for matching")
}

/// Options for the matching algorithm
class MatchOptions {
  minimum_compatibility float @description("Minimum score to consider a match (0.0-1.0)")
  type_weight float @description("Weight for type matching (0.0-1.0)")
  name_weight float @description("Weight for name similarity (0.0-1.0)")
  description_weight float @description("Weight for description similarity (0.0-1.0)")
  schema_weight float @description("Weight for schema compatibility (0.0-1.0)")
  include_transformations bool @description("Whether to suggest transformations")
  include_suggestions bool @description("Whether to generate adaptation suggestions")
  fuzzy_matching bool @description("Whether to use fuzzy string matching")
  semantic_matching bool @description("Whether to use semantic similarity")
}

/// Context for matching
class MatchContext {
  requester_agent_id string? @description("ID of the requesting agent")
  use_case string? @description("Description of intended use case")
  performance_requirements PerformanceRequirements? @description("Required performance levels")
  trust_requirements TrustRequirements? @description("Required trust levels")
}

/// Performance requirements for matching context
class PerformanceRequirements {
  max_latency_ms int? @description("Maximum acceptable latency")
  min_throughput_rps float? @description("Minimum required throughput")
  require_idempotent bool @description("Whether idempotency is required")
  require_cacheable bool @description("Whether cacheability is required")
}

/// Response from capability matching
class CapabilityMatchResponse {
  request_id string @description("ID of the original request")
  overall_result CapabilityMatchResult @description("Overall matching result")
  best_matches BestMatch[] @description("Best matches for each required capability")
  match_time_ms int @description("Time taken for matching in milliseconds")
  algorithm_version string @description("Version of matching algorithm used")
}

/// Best match for a single required capability
class BestMatch {
  required_capability_id string @description("ID of the required capability")
  best_match_id string? @description("ID of best matching capability if found")
  match_score float @description("Score of best match (0.0-1.0)")
  alternatives AlternativeMatch[] @description("Alternative matches")
}

/// An alternative match option
class AlternativeMatch {
  capability_id string @description("ID of the alternative capability")
  match_score float @description("Match score (0.0-1.0)")
  trade_offs string[] @description("Trade-offs compared to best match")
}
