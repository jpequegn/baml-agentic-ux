// Schema Conflict Detection Types
// Detection and analysis of conflicts during agent capability negotiation
// Issue #60 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.8)

// Dependencies:
// - SchemaDefinition from agent_capability.baml
// - SchemaTransformation from capability_matching.baml

// ============================================
// Conflict Type Enums
// ============================================

/// Types of conflicts that can occur during negotiation
enum ConflictType {
  SCHEMA_MISMATCH @description("Type or structure incompatibility between schemas")
  CONSTRAINT_VIOLATION @description("Cannot meet required constraint")
  RESOURCE_CONTENTION @description("Exclusive resource needs that cannot be shared")
  PRIORITY_CLASH @description("Conflicting priority requirements")
  TRUST_INSUFFICIENT @description("Trust level too low for requested operation")
  SEMANTIC_AMBIGUITY @description("Same term used with different meanings")
  VERSION_INCOMPATIBLE @description("Incompatible API or protocol versions")
  CAPACITY_EXCEEDED @description("Requested capacity exceeds available resources")
  TIMING_CONFLICT @description("Incompatible timing or scheduling requirements")
  SECURITY_POLICY @description("Security policy prevents operation")
}

/// Severity levels for conflicts
enum ConflictSeverity {
  LOW @description("Minor issue, auto-resolvable with simple adaptation")
  MEDIUM @description("Requires adaptation or negotiation to resolve")
  HIGH @description("May require intervention or significant changes")
  CRITICAL @description("Blocks negotiation, must be resolved to proceed")
}

/// Categories of conflicts for grouping
enum ConflictCategory {
  STRUCTURAL @description("Schema structure conflicts")
  SEMANTIC @description("Meaning and interpretation conflicts")
  OPERATIONAL @description("Runtime and resource conflicts")
  POLICY @description("Policy and compliance conflicts")
  TEMPORAL @description("Timing and scheduling conflicts")
}

// ============================================
// Conflict Description Types
// ============================================

/// A single detected conflict
class Conflict {
  conflict_id string @description("Unique identifier for this conflict")
  conflict_type ConflictType @description("Type of conflict")
  category ConflictCategory @description("Category for grouping")
  severity ConflictSeverity @description("Severity of the conflict")
  description string @description("Human-readable description of the conflict")
  source_element string @description("Element in source schema/spec causing conflict")
  target_element string @description("Element in target schema/spec affected")
  source_value string? @description("Actual value in source if applicable")
  target_value string? @description("Expected or required value in target if applicable")
  context ConflictContext? @description("Additional context about the conflict")
}

/// Additional context for understanding a conflict
class ConflictContext {
  affected_capabilities string[] @description("Capability IDs affected by this conflict")
  related_constraints string[] @description("Related constraint IDs")
  impact_description string @description("Description of the impact if unresolved")
  precedent_conflicts string[] @description("IDs of conflicts this one depends on")
}

// ============================================
// Resolution Types
// ============================================

/// Strategy for resolving a conflict
enum ResolutionStrategy {
  TRANSFORM @description("Apply data transformation")
  NEGOTIATE @description("Negotiate alternative terms")
  ADAPT @description("Adapt capability or schema")
  FALLBACK @description("Use fallback option")
  ESCALATE @description("Escalate for human intervention")
  ACCEPT_RISK @description("Accept with documented risk")
  REJECT @description("Cannot resolve, reject negotiation")
  BRIDGE @description("Add bridging layer")
  SUBSET @description("Use subset of capability")
}

/// A possible path to resolve a conflict
class ResolutionPath {
  path_id string @description("Unique identifier for this resolution path")
  strategy ResolutionStrategy @description("Resolution strategy to use")
  description string @description("Description of the resolution approach")
  steps ResolutionStep[] @description("Steps to implement resolution")
  estimated_effort EffortEstimate @description("Effort required")
  success_likelihood float @description("Probability of success (0.0-1.0)")
  trade_offs string[] @description("Trade-offs or compromises involved")
  prerequisites string[] @description("Prerequisites for this resolution")
  risks ResolutionRisk[] @description("Risks associated with this resolution")
}

/// A single step in a resolution path
class ResolutionStep {
  step_number int @description("Order of this step")
  action string @description("Action to take")
  actor string @description("Who performs this step (source, target, both)")
  details string @description("Detailed instructions")
  validation string? @description("How to validate step completion")
}

/// Effort estimate for resolution
class EffortEstimate {
  level ConflictEffortLevel @description("Overall effort level")
  estimated_hours float? @description("Estimated hours if quantifiable")
  complexity_factors string[] @description("Factors contributing to complexity")
}

/// Effort levels for resolution
enum ConflictEffortLevel {
  TRIVIAL @description("Automatic or near-instant")
  LOW @description("Minutes of work")
  MEDIUM @description("Hours of work")
  HIGH @description("Days of work")
  VERY_HIGH @description("Weeks of work or major project")
}

/// Risk associated with a resolution
class ResolutionRisk {
  risk_id string @description("Unique identifier for this risk")
  description string @description("Description of the risk")
  probability float @description("Probability of occurrence (0.0-1.0)")
  impact ConflictSeverity @description("Impact if risk materializes")
  mitigation string? @description("How to mitigate this risk")
}

// ============================================
// Conflict Analysis Types
// ============================================

/// Complete analysis of conflicts between two parties
class ConflictAnalysis {
  analysis_id string @description("Unique identifier for this analysis")
  source_id string @description("ID of the source agent/capability")
  target_id string @description("ID of the target agent/capability")
  timestamp string @description("ISO 8601 timestamp of analysis")
  conflicts Conflict[] @description("All detected conflicts")
  overall_severity ConflictSeverity @description("Highest severity among conflicts")
  resolvable bool @description("Whether all conflicts can be resolved")
  resolution_paths ResolutionPath[] @description("Suggested resolution paths")
  summary ConflictSummary @description("Summary of conflict analysis")
  recommendations string[] @description("Overall recommendations")
}

/// Summary statistics for conflict analysis
class ConflictSummary {
  total_conflicts int @description("Total number of conflicts detected")
  by_severity ConflictSeverityCount @description("Counts by severity level")
  by_category ConflictCategoryCount @description("Counts by category")
  by_type ConflictTypeCount @description("Counts by conflict type")
  blocking_conflicts int @description("Number of conflicts blocking progress")
  auto_resolvable int @description("Number that can be auto-resolved")
}

/// Count of conflicts by severity
class ConflictSeverityCount {
  low int @description("Number of LOW severity conflicts")
  medium int @description("Number of MEDIUM severity conflicts")
  high int @description("Number of HIGH severity conflicts")
  critical int @description("Number of CRITICAL severity conflicts")
}

/// Count of conflicts by category
class ConflictCategoryCount {
  structural int @description("Number of STRUCTURAL conflicts")
  semantic int @description("Number of SEMANTIC conflicts")
  operational int @description("Number of OPERATIONAL conflicts")
  policy int @description("Number of POLICY conflicts")
  temporal int @description("Number of TEMPORAL conflicts")
}

/// Count of conflicts by type
class ConflictTypeCount {
  schema_mismatch int @description("SCHEMA_MISMATCH count")
  constraint_violation int @description("CONSTRAINT_VIOLATION count")
  resource_contention int @description("RESOURCE_CONTENTION count")
  priority_clash int @description("PRIORITY_CLASH count")
  trust_insufficient int @description("TRUST_INSUFFICIENT count")
  semantic_ambiguity int @description("SEMANTIC_AMBIGUITY count")
  version_incompatible int @description("VERSION_INCOMPATIBLE count")
  capacity_exceeded int @description("CAPACITY_EXCEEDED count")
  timing_conflict int @description("TIMING_CONFLICT count")
  security_policy int @description("SECURITY_POLICY count")
}

// ============================================
// Detection Request/Response Types
// ============================================

/// Request to detect conflicts
class ConflictDetectionRequest {
  request_id string @description("Unique request identifier")
  source_schema SchemaDefinition? @description("Source schema to analyze")
  target_schema SchemaDefinition? @description("Target schema requirements")
  source_constraints ConstraintSpec[]? @description("Constraints from source")
  target_constraints ConstraintSpec[]? @description("Constraints from target")
  detection_options DetectionOptions @description("Options for detection")
}

/// Constraint specification for detection
class ConstraintSpec {
  constraint_id string @description("Unique identifier for constraint")
  constraint_type string @description("Type of constraint")
  field string? @description("Field the constraint applies to")
  operator string @description("Comparison operator")
  value string @description("Constraint value")
  required bool @description("Whether constraint is required")
}

/// Options for conflict detection
class DetectionOptions {
  include_resolution_paths bool @description("Whether to generate resolution suggestions")
  max_resolution_paths int @description("Maximum resolution paths per conflict")
  severity_threshold ConflictSeverity @description("Minimum severity to report")
  detect_semantic bool @description("Whether to detect semantic conflicts")
  deep_schema_analysis bool @description("Whether to analyze nested schemas deeply")
  include_risk_assessment bool @description("Whether to assess resolution risks")
}

/// Response from conflict detection
class ConflictDetectionResponse {
  request_id string @description("ID of the original request")
  analysis ConflictAnalysis @description("Complete conflict analysis")
  detection_time_ms int @description("Time taken for detection in milliseconds")
  warnings string[] @description("Warnings about detection process")
}

// ============================================
// AI Functions
// ============================================

/// Analyze conflicts between two schemas and generate resolution suggestions
function AnalyzeSchemaConflicts(
  source_schema: string,
  target_schema: string,
  context: string?
) -> ConflictAnalysis {
  client CustomSonnet4
  prompt #"
    Analyze the potential conflicts between these two schemas and suggest resolutions.

    Source Schema:
    {{ source_schema }}

    Target Schema:
    {{ target_schema }}

    {% if context %}
    Additional Context:
    {{ context }}
    {% endif %}

    Identify all conflicts including:
    1. Type mismatches (string vs int, nested vs flat, etc.)
    2. Missing required fields
    3. Constraint violations
    4. Semantic ambiguities

    For each conflict, assess severity and suggest resolution paths.

    {{ ctx.output_format }}
  "#
}

/// Suggest the optimal resolution strategy for a set of conflicts
function SuggestResolutionStrategy(
  conflicts: Conflict[],
  available_strategies: ResolutionStrategy[],
  constraints: string[]?
) -> ResolutionPath[] {
  client CustomSonnet4
  prompt #"
    Given these conflicts and available resolution strategies, suggest the optimal resolution paths.

    Conflicts:
    {{ conflicts }}

    Available Strategies:
    {{ available_strategies }}

    {% if constraints %}
    Constraints to Consider:
    {{ constraints }}
    {% endif %}

    Prioritize resolutions that:
    1. Address critical conflicts first
    2. Minimize required effort
    3. Maximize success likelihood
    4. Consider dependencies between conflicts

    {{ ctx.output_format }}
  "#
}

/// Validate whether a proposed resolution will work
function ValidateResolution(
  conflict: Conflict,
  proposed_resolution: ResolutionPath,
  current_state: string
) -> ResolutionValidation {
  client CustomSonnet4
  prompt #"
    Validate whether this proposed resolution will effectively address the conflict.

    Conflict:
    {{ conflict }}

    Proposed Resolution:
    {{ proposed_resolution }}

    Current State:
    {{ current_state }}

    Analyze:
    1. Will this resolution fully address the conflict?
    2. Are there any side effects?
    3. What risks remain?
    4. What validation steps are needed?

    {{ ctx.output_format }}
  "#
}

/// Result of resolution validation
class ResolutionValidation {
  is_valid bool @description("Whether the resolution is valid")
  effectiveness float @description("How effectively it addresses the conflict (0.0-1.0)")
  remaining_issues string[] @description("Issues that remain after resolution")
  side_effects string[] @description("Potential side effects")
  validation_steps string[] @description("Steps to validate resolution")
  confidence float @description("Confidence in this assessment (0.0-1.0)")
}
