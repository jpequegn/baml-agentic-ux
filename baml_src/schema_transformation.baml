// Schema Transformation Engine Types
// Transform data between incompatible schemas with data loss assessment
// Issue #61 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.9)

// Dependencies:
// - SchemaDefinition from agent_capability.baml
// - SchemaTransformation from capability_matching.baml

// ============================================
// Field Transformation Types
// ============================================

/// Types of field transformations
enum FieldTransformType {
  COPY @description("Direct copy without modification")
  RENAME @description("Change field name, keep value")
  TYPE_COERCE @description("Convert value to different type")
  RESTRUCTURE @description("Change structure (e.g., nested to flat)")
  AGGREGATE @description("Combine multiple fields into one")
  SPLIT @description("Split one field into multiple")
  COMPUTE @description("Calculate derived value")
  DEFAULT @description("Use default value if source missing")
  OMIT @description("Drop field from output")
  MAP @description("Map value through lookup table")
  FORMAT @description("Apply formatting (e.g., date formats)")
}

/// Risk level of data loss during transformation
enum DataLossRisk {
  NONE @description("Completely lossless transformation")
  LOW @description("Minor precision loss possible (e.g., float to int)")
  MEDIUM @description("Some data may be truncated or lost")
  HIGH @description("Significant data loss expected")
  CRITICAL @description("Transformation destroys essential data")
}

/// Validation status for a transformation
enum TransformValidation {
  VALID @description("Transformation is safe to apply")
  WARNING @description("Transformation may have issues")
  ERROR @description("Transformation cannot be applied")
  SKIPPED @description("Transformation was skipped")
}

// ============================================
// Field Transformation Definition
// ============================================

/// A single field transformation operation
class FieldTransformation {
  transformation_id string @description("Unique identifier for this transformation")
  source_path string @description("JSONPath to source field (e.g., '$.user.name')")
  target_path string @description("JSONPath to target field")
  transform_type FieldTransformType @description("Type of transformation")
  transform_function string? @description("Custom function or expression for COMPUTE type")
  default_value string? @description("Default value for DEFAULT type")
  value_mapping ValueMapping? @description("Value mapping for MAP type")
  format_spec FormatSpec? @description("Format specification for FORMAT type")
  conditions TransformCondition[]? @description("Conditions for conditional transformation")
  description string? @description("Human-readable description")
}

/// Mapping of values for MAP transformation type
class ValueMapping {
  mappings MappingEntry[] @description("List of value mappings")
  default_mapping string? @description("Value to use if source not in mappings")
  case_sensitive bool @description("Whether mapping is case-sensitive")
}

/// Single mapping entry
class MappingEntry {
  source_value string @description("Source value to match")
  target_value string @description("Target value to produce")
}

/// Format specification for FORMAT transformation type
class FormatSpec {
  source_format string @description("Format of source value")
  target_format string @description("Desired format for target")
  locale string? @description("Locale for formatting")
}

/// Condition for conditional transformations
class TransformCondition {
  field_path string @description("Field to check")
  operator ConditionOperator @description("Comparison operator")
  value string @description("Value to compare against")
}

/// Operators for transformation conditions
enum ConditionOperator {
  EQUALS @description("Field equals value")
  NOT_EQUALS @description("Field does not equal value")
  CONTAINS @description("Field contains value")
  STARTS_WITH @description("Field starts with value")
  ENDS_WITH @description("Field ends with value")
  GREATER_THAN @description("Field greater than value (numeric)")
  LESS_THAN @description("Field less than value (numeric)")
  EXISTS @description("Field exists")
  NOT_EXISTS @description("Field does not exist")
  MATCHES @description("Field matches regex pattern")
}

// ============================================
// Transform Plan Types
// ============================================

/// Complete transformation plan between two schemas
class SchemaTransformPlan {
  plan_id string @description("Unique identifier for this plan")
  source_schema SchemaSpec @description("Source schema definition")
  target_schema SchemaSpec @description("Target schema definition")
  transformations FieldTransformation[] @description("Ordered list of transformations")
  data_loss_risk DataLossRisk @description("Overall data loss risk")
  reversible bool @description("Whether transformation can be reversed")
  reverse_plan_id string? @description("ID of reverse transformation plan if reversible")
  estimated_complexity TransformComplexity @description("Estimated transformation complexity")
  validation_result SchemaPlanValidation @description("Validation status of the plan")
  metadata PlanMetadata? @description("Additional metadata")
}

/// Simplified schema specification for transform plans
class SchemaSpec {
  schema_id string @description("Schema identifier")
  name string @description("Schema name")
  version string @description("Schema version")
  fields FieldSpec[] @description("Field specifications")
}

/// Field specification within a schema
class FieldSpec {
  path string @description("JSONPath to field")
  name string @description("Field name")
  type string @description("Field type (string, int, float, bool, array, object)")
  required bool @description("Whether field is required")
  default_value string? @description("Default value if any")
  description string? @description("Field description")
  nested_schema SchemaSpec? @description("Nested schema for object types")
}

/// Complexity level of transformation
enum TransformComplexity {
  TRIVIAL @description("Direct field mapping only")
  SIMPLE @description("Basic type coercions and renames")
  MODERATE @description("Some restructuring required")
  COMPLEX @description("Significant transformations needed")
  VERY_COMPLEX @description("Requires custom logic or AI assistance")
}

/// Validation result for a transform plan
class SchemaPlanValidation {
  is_valid bool @description("Whether plan is valid")
  errors SchemaValidationIssue[] @description("Validation errors")
  warnings SchemaValidationIssue[] @description("Validation warnings")
  coverage_analysis CoverageAnalysis @description("Field coverage analysis")
}

/// A validation issue (error or warning)
class SchemaValidationIssue {
  issue_id string @description("Issue identifier")
  severity string @description("error or warning")
  message string @description("Issue description")
  field_path string? @description("Related field path if applicable")
  suggestion string? @description("Suggested fix")
}

/// Analysis of field coverage in transformation
class CoverageAnalysis {
  source_fields_mapped int @description("Source fields with transformations")
  source_fields_total int @description("Total source fields")
  target_fields_covered int @description("Target fields that will be populated")
  target_fields_required int @description("Required target fields")
  unmapped_source_fields string[] @description("Source fields without transformations")
  uncovered_target_fields string[] @description("Target fields not covered")
  coverage_percentage float @description("Overall coverage percentage (0.0-1.0)")
}

/// Additional metadata for a transform plan
class PlanMetadata {
  created_at string @description("ISO 8601 timestamp")
  created_by string? @description("Agent or user that created the plan")
  purpose string? @description("Purpose of the transformation")
  tags string[]? @description("Tags for categorization")
}

// ============================================
// Transform Execution Types
// ============================================

/// Result of executing a transformation
class TransformResult {
  result_id string @description("Unique result identifier")
  plan_id string @description("ID of the plan that was executed")
  success bool @description("Whether transformation succeeded")
  output_data string @description("Transformed data as JSON string")
  input_hash string? @description("Hash of input data for verification")
  output_hash string? @description("Hash of output data for verification")
  execution_time_ms int @description("Time taken in milliseconds")
  warnings string[] @description("Warnings during transformation")
  errors string[] @description("Errors if transformation failed")
  data_loss_report DataLossReport @description("Report on data loss")
  field_results FieldTransformResult[] @description("Results for each field transformation")
}

/// Report on data loss during transformation
class DataLossReport {
  data_loss_occurred bool @description("Whether any data was lost")
  lost_fields LostField[] @description("Fields that were lost")
  truncated_fields TruncatedField[] @description("Fields that were truncated")
  precision_loss_fields PrecisionLossField[] @description("Fields with precision loss")
  overall_loss_severity DataLossRisk @description("Overall severity of data loss")
}

/// Information about a lost field
class LostField {
  source_path string @description("Path of lost field")
  reason string @description("Why field was lost")
  original_value string? @description("Original value if available")
}

/// Information about a truncated field
class TruncatedField {
  field_path string @description("Path of truncated field")
  original_length int @description("Original length")
  truncated_length int @description("Truncated length")
  original_value string? @description("Original value")
  truncated_value string @description("Truncated value")
}

/// Information about precision loss
class PrecisionLossField {
  field_path string @description("Path of field with precision loss")
  original_value string @description("Original value")
  converted_value string @description("Converted value")
  precision_lost string @description("Description of precision lost")
}

/// Result of a single field transformation
class FieldTransformResult {
  transformation_id string @description("ID of the transformation")
  status TransformValidation @description("Status of this transformation")
  source_value string? @description("Original value")
  target_value string? @description("Transformed value")
  message string? @description("Status message")
}

// ============================================
// Transform Request/Response Types
// ============================================

/// Request to generate a transformation plan
class GeneratePlanRequest {
  request_id string @description("Unique request identifier")
  source_schema SchemaSpec @description("Source schema")
  target_schema SchemaSpec @description("Target schema")
  options PlanGenerationOptions @description("Options for plan generation")
}

/// Options for plan generation
class PlanGenerationOptions {
  prefer_lossless bool @description("Prefer lossless transformations")
  allow_defaults bool @description("Allow default values for missing fields")
  fuzzy_field_matching bool @description("Use fuzzy matching for field names")
  fuzzy_threshold float @description("Threshold for fuzzy matching (0.0-1.0)")
  include_reverse_plan bool @description("Generate reverse plan if possible")
  max_complexity TransformComplexity @description("Maximum allowed complexity")
}

/// Response from plan generation
class GeneratePlanResponse {
  request_id string @description("Original request ID")
  plan SchemaTransformPlan @description("Generated transformation plan")
  alternatives SchemaTransformPlan[]? @description("Alternative plans if available")
  generation_time_ms int @description("Time taken to generate")
  notes string[] @description("Notes about the generated plan")
}

/// Request to execute a transformation
class ExecuteTransformRequest {
  request_id string @description("Unique request identifier")
  plan_id string @description("ID of the plan to execute")
  plan SchemaTransformPlan @description("The transformation plan")
  input_data string @description("Input data as JSON string")
  options ExecutionOptions @description("Execution options")
}

/// Options for transformation execution
class ExecutionOptions {
  validate_input bool @description("Validate input against source schema")
  validate_output bool @description("Validate output against target schema")
  stop_on_error bool @description("Stop on first error vs continue")
  collect_metrics bool @description("Collect detailed metrics")
  dry_run bool @description("Simulate without producing output")
}

/// Response from transformation execution
class ExecuteTransformResponse {
  request_id string @description("Original request ID")
  result TransformResult @description("Transformation result")
}

// ============================================
// AI Functions
// ============================================

/// Generate a transformation plan between two schemas
function GenerateTransformPlan(
  source_schema: string,
  target_schema: string,
  preferences: string?
) -> SchemaTransformPlan {
  client CustomSonnet4
  prompt #"
    Generate a transformation plan to convert data from the source schema to the target schema.

    Source Schema:
    {{ source_schema }}

    Target Schema:
    {{ target_schema }}

    {% if preferences %}
    Preferences:
    {{ preferences }}
    {% endif %}

    Create a comprehensive transformation plan that:
    1. Maps all source fields to appropriate target fields
    2. Handles type conversions safely
    3. Provides default values where needed
    4. Assesses data loss risk accurately
    5. Determines if the transformation is reversible

    {{ ctx.output_format }}
  "#
}

/// Apply a transformation plan to actual data
function ApplyTransformation(
  input_data: string,
  plan: string,
  options: string?
) -> TransformResult {
  client CustomSonnet4
  prompt #"
    Apply this transformation plan to the input data.

    Input Data:
    {{ input_data }}

    Transformation Plan:
    {{ plan }}

    {% if options %}
    Options:
    {{ options }}
    {% endif %}

    Execute the transformation and:
    1. Apply each field transformation in order
    2. Track any data loss or warnings
    3. Validate the output structure
    4. Report detailed results for each field

    {{ ctx.output_format }}
  "#
}

/// Suggest improvements to a transformation plan
function SuggestPlanImprovements(
  plan: string,
  sample_data: string?,
  issues: string[]
) -> SchemaPlanImprovement[] {
  client CustomSonnet4
  prompt #"
    Analyze this transformation plan and suggest improvements.

    Current Plan:
    {{ plan }}

    {% if sample_data %}
    Sample Data:
    {{ sample_data }}
    {% endif %}

    Known Issues:
    {{ issues }}

    Suggest improvements to:
    1. Reduce data loss risk
    2. Improve transformation accuracy
    3. Handle edge cases better
    4. Increase reversibility

    {{ ctx.output_format }}
  "#
}

/// Suggestion for improving a transform plan
class SchemaPlanImprovement {
  improvement_id string @description("Unique improvement identifier")
  target_transformation_id string? @description("ID of transformation to improve")
  improvement_type string @description("Type of improvement")
  description string @description("Description of the improvement")
  before_risk DataLossRisk @description("Risk level before improvement")
  after_risk DataLossRisk @description("Expected risk level after")
  implementation_hint string @description("How to implement the improvement")
}
