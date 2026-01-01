"""
Schema Transformation Engine Module

Transform data between incompatible schemas with data loss assessment.

Issue #61 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.9)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from difflib import SequenceMatcher
from enum import Enum
from typing import Any
import hashlib
import json
import re
import uuid


# ============================================
# Enums
# ============================================


class FieldTransformType(str, Enum):
    """Types of field transformations."""

    COPY = "copy"
    RENAME = "rename"
    TYPE_COERCE = "type_coerce"
    RESTRUCTURE = "restructure"
    AGGREGATE = "aggregate"
    SPLIT = "split"
    COMPUTE = "compute"
    DEFAULT = "default"
    OMIT = "omit"
    MAP = "map"
    FORMAT = "format"


class DataLossRisk(str, Enum):
    """Risk level of data loss during transformation."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TransformValidation(str, Enum):
    """Validation status for a transformation."""

    VALID = "valid"
    WARNING = "warning"
    ERROR = "error"
    SKIPPED = "skipped"


class ConditionOperator(str, Enum):
    """Operators for transformation conditions."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"
    MATCHES = "matches"


class TransformComplexity(str, Enum):
    """Complexity level of transformation."""

    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


# ============================================
# Supporting Types
# ============================================


@dataclass
class MappingEntry:
    """Single mapping entry."""

    source_value: str
    target_value: str


@dataclass
class ValueMapping:
    """Mapping of values for MAP transformation type."""

    mappings: list[MappingEntry] = field(default_factory=list)
    default_mapping: str | None = None
    case_sensitive: bool = True


@dataclass
class FormatSpec:
    """Format specification for FORMAT transformation type."""

    source_format: str
    target_format: str
    locale: str | None = None


@dataclass
class TransformCondition:
    """Condition for conditional transformations."""

    field_path: str
    operator: ConditionOperator
    value: str


@dataclass
class FieldTransformation:
    """A single field transformation operation."""

    transformation_id: str
    source_path: str
    target_path: str
    transform_type: FieldTransformType
    transform_function: str | None = None
    default_value: str | None = None
    value_mapping: ValueMapping | None = None
    format_spec: FormatSpec | None = None
    conditions: list[TransformCondition] | None = None
    description: str | None = None


# ============================================
# Schema Types
# ============================================


@dataclass
class FieldSpec:
    """Field specification within a schema."""

    path: str
    name: str
    type: str
    required: bool = False
    default_value: str | None = None
    description: str | None = None
    nested_schema: "SchemaSpec | None" = None


@dataclass
class SchemaSpec:
    """Simplified schema specification for transform plans."""

    schema_id: str
    name: str
    version: str = "1.0"
    fields: list[FieldSpec] = field(default_factory=list)


# ============================================
# Validation Types
# ============================================


@dataclass
class ValidationIssue:
    """A validation issue (error or warning)."""

    issue_id: str
    severity: str
    message: str
    field_path: str | None = None
    suggestion: str | None = None


@dataclass
class CoverageAnalysis:
    """Analysis of field coverage in transformation."""

    source_fields_mapped: int = 0
    source_fields_total: int = 0
    target_fields_covered: int = 0
    target_fields_required: int = 0
    unmapped_source_fields: list[str] = field(default_factory=list)
    uncovered_target_fields: list[str] = field(default_factory=list)
    coverage_percentage: float = 0.0


@dataclass
class PlanValidation:
    """Validation result for a transform plan."""

    is_valid: bool = True
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)
    coverage_analysis: CoverageAnalysis = field(default_factory=CoverageAnalysis)


@dataclass
class PlanMetadata:
    """Additional metadata for a transform plan."""

    created_at: str = ""
    created_by: str | None = None
    purpose: str | None = None
    tags: list[str] | None = None


# ============================================
# Transform Plan
# ============================================


@dataclass
class SchemaTransformPlan:
    """Complete transformation plan between two schemas."""

    plan_id: str
    source_schema: SchemaSpec
    target_schema: SchemaSpec
    transformations: list[FieldTransformation] = field(default_factory=list)
    data_loss_risk: DataLossRisk = DataLossRisk.NONE
    reversible: bool = True
    reverse_plan_id: str | None = None
    estimated_complexity: TransformComplexity = TransformComplexity.TRIVIAL
    validation_result: PlanValidation = field(default_factory=PlanValidation)
    metadata: PlanMetadata | None = None


# ============================================
# Transform Result Types
# ============================================


@dataclass
class LostField:
    """Information about a lost field."""

    source_path: str
    reason: str
    original_value: str | None = None


@dataclass
class TruncatedField:
    """Information about a truncated field."""

    field_path: str
    original_length: int
    truncated_length: int
    original_value: str | None = None
    truncated_value: str = ""


@dataclass
class PrecisionLossField:
    """Information about precision loss."""

    field_path: str
    original_value: str
    converted_value: str
    precision_lost: str


@dataclass
class DataLossReport:
    """Report on data loss during transformation."""

    data_loss_occurred: bool = False
    lost_fields: list[LostField] = field(default_factory=list)
    truncated_fields: list[TruncatedField] = field(default_factory=list)
    precision_loss_fields: list[PrecisionLossField] = field(default_factory=list)
    overall_loss_severity: DataLossRisk = DataLossRisk.NONE


@dataclass
class FieldTransformResult:
    """Result of a single field transformation."""

    transformation_id: str
    status: TransformValidation
    source_value: str | None = None
    target_value: str | None = None
    message: str | None = None


@dataclass
class TransformResult:
    """Result of executing a transformation."""

    result_id: str
    plan_id: str
    success: bool
    output_data: str
    input_hash: str | None = None
    output_hash: str | None = None
    execution_time_ms: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    data_loss_report: DataLossReport = field(default_factory=DataLossReport)
    field_results: list[FieldTransformResult] = field(default_factory=list)


# ============================================
# Request/Response Types
# ============================================


@dataclass
class PlanGenerationOptions:
    """Options for plan generation."""

    prefer_lossless: bool = True
    allow_defaults: bool = True
    fuzzy_field_matching: bool = True
    fuzzy_threshold: float = 0.6
    include_reverse_plan: bool = False
    max_complexity: TransformComplexity = TransformComplexity.VERY_COMPLEX


@dataclass
class ExecutionOptions:
    """Options for transformation execution."""

    validate_input: bool = True
    validate_output: bool = True
    stop_on_error: bool = False
    collect_metrics: bool = True
    dry_run: bool = False


# ============================================
# Schema Transformer Implementation
# ============================================


class SchemaTransformer:
    """
    Transform data between incompatible schemas.

    The transformer handles:
    - Field mapping and renaming
    - Type coercion with validation
    - Default value injection
    - Fuzzy field matching
    - Data loss tracking
    """

    # Type compatibility for coercion
    TYPE_COERCION_RISK: dict[tuple[str, str], DataLossRisk] = {
        # Safe coercions
        ("int", "float"): DataLossRisk.NONE,
        ("int", "string"): DataLossRisk.NONE,
        ("float", "string"): DataLossRisk.NONE,
        ("bool", "string"): DataLossRisk.NONE,
        ("bool", "int"): DataLossRisk.NONE,
        # Low risk coercions
        ("float", "int"): DataLossRisk.LOW,  # Precision loss
        ("string", "int"): DataLossRisk.LOW,  # May fail
        ("string", "float"): DataLossRisk.LOW,
        ("string", "bool"): DataLossRisk.LOW,
        # Medium risk
        ("object", "string"): DataLossRisk.MEDIUM,
        ("array", "string"): DataLossRisk.MEDIUM,
        # High risk
        ("string", "object"): DataLossRisk.HIGH,
        ("string", "array"): DataLossRisk.HIGH,
    }

    def __init__(
        self,
        default_options: PlanGenerationOptions | None = None,
    ):
        """
        Initialize the schema transformer.

        Args:
            default_options: Default options for plan generation
        """
        self.default_options = default_options or PlanGenerationOptions()

    def generate_plan(
        self,
        source_schema: SchemaSpec,
        target_schema: SchemaSpec,
        options: PlanGenerationOptions | None = None,
    ) -> SchemaTransformPlan:
        """
        Generate a transformation plan between two schemas.

        Args:
            source_schema: Source schema specification
            target_schema: Target schema specification
            options: Plan generation options

        Returns:
            Generated transformation plan
        """
        options = options or self.default_options
        transformations: list[FieldTransformation] = []
        overall_risk = DataLossRisk.NONE

        # Build lookup maps
        source_fields = {f.path: f for f in source_schema.fields}
        target_fields = {f.path: f for f in target_schema.fields}

        # Track coverage
        mapped_source_paths: set[str] = set()
        covered_target_paths: set[str] = set()

        # Match target fields to source fields
        for target_field in target_schema.fields:
            transformation, risk = self._match_field(
                target_field, source_fields, options
            )
            if transformation:
                transformations.append(transformation)
                mapped_source_paths.add(transformation.source_path)
                covered_target_paths.add(target_field.path)
                overall_risk = self._max_risk(overall_risk, risk)
            elif target_field.required:
                # Required field not covered - use default if allowed
                if options.allow_defaults and target_field.default_value:
                    transformation = FieldTransformation(
                        transformation_id=str(uuid.uuid4()),
                        source_path="",
                        target_path=target_field.path,
                        transform_type=FieldTransformType.DEFAULT,
                        default_value=target_field.default_value,
                        description=f"Use default for missing required field '{target_field.name}'",
                    )
                    transformations.append(transformation)
                    covered_target_paths.add(target_field.path)
                else:
                    overall_risk = DataLossRisk.HIGH

        # Calculate coverage
        unmapped = [p for p in source_fields.keys() if p not in mapped_source_paths]
        uncovered = [
            p
            for p, f in target_fields.items()
            if p not in covered_target_paths and f.required
        ]

        # Calculate coverage percentage
        total_target_required = sum(1 for f in target_schema.fields if f.required)
        covered_required = sum(
            1
            for f in target_schema.fields
            if f.required and f.path in covered_target_paths
        )
        coverage_pct = covered_required / total_target_required if total_target_required > 0 else 1.0

        # Validate the plan
        validation = self._validate_plan(
            source_schema, target_schema, transformations, unmapped, uncovered, coverage_pct
        )

        # Assess complexity
        complexity = self._assess_complexity(transformations)

        # Check reversibility
        reversible = self._is_reversible(transformations)

        return SchemaTransformPlan(
            plan_id=str(uuid.uuid4()),
            source_schema=source_schema,
            target_schema=target_schema,
            transformations=transformations,
            data_loss_risk=overall_risk,
            reversible=reversible,
            estimated_complexity=complexity,
            validation_result=validation,
            metadata=PlanMetadata(
                created_at=datetime.now(timezone.utc).isoformat(),
                purpose="Auto-generated transformation plan",
            ),
        )

    def execute(
        self,
        data: dict[str, Any],
        plan: SchemaTransformPlan,
        options: ExecutionOptions | None = None,
    ) -> TransformResult:
        """
        Execute a transformation plan on data.

        Args:
            data: Input data dictionary
            plan: Transformation plan to execute
            options: Execution options

        Returns:
            Transformation result
        """
        options = options or ExecutionOptions()
        start_time = datetime.now(timezone.utc)

        # Calculate input hash
        input_json = json.dumps(data, sort_keys=True)
        input_hash = hashlib.sha256(input_json.encode()).hexdigest()[:16]

        # Initialize result tracking
        output: dict[str, Any] = {}
        field_results: list[FieldTransformResult] = []
        warnings: list[str] = []
        errors: list[str] = []
        data_loss_report = DataLossReport()

        # Execute each transformation
        for transform in plan.transformations:
            result = self._execute_transformation(data, output, transform, options)
            field_results.append(result)

            if result.status == TransformValidation.ERROR:
                errors.append(result.message or "Unknown error")
                if options.stop_on_error:
                    break
            elif result.status == TransformValidation.WARNING:
                warnings.append(result.message or "Warning")

            # Track data loss
            self._track_data_loss(transform, result, data_loss_report)

        # Calculate output hash
        output_json = json.dumps(output, sort_keys=True)
        output_hash = hashlib.sha256(output_json.encode()).hexdigest()[:16]

        # Calculate execution time
        end_time = datetime.now(timezone.utc)
        execution_time_ms = int((end_time - start_time).total_seconds() * 1000)

        # Determine overall success
        success = len(errors) == 0

        # Finalize data loss report
        data_loss_report.data_loss_occurred = bool(
            data_loss_report.lost_fields
            or data_loss_report.truncated_fields
            or data_loss_report.precision_loss_fields
        )
        if data_loss_report.data_loss_occurred:
            data_loss_report.overall_loss_severity = self._calculate_loss_severity(
                data_loss_report
            )

        return TransformResult(
            result_id=str(uuid.uuid4()),
            plan_id=plan.plan_id,
            success=success,
            output_data=output_json if not options.dry_run else "{}",
            input_hash=input_hash,
            output_hash=output_hash if not options.dry_run else None,
            execution_time_ms=execution_time_ms,
            warnings=warnings,
            errors=errors,
            data_loss_report=data_loss_report,
            field_results=field_results,
        )

    def execute_json(
        self,
        json_data: str,
        plan: SchemaTransformPlan,
        options: ExecutionOptions | None = None,
    ) -> TransformResult:
        """
        Execute a transformation plan on JSON string data.

        Args:
            json_data: Input data as JSON string
            plan: Transformation plan to execute
            options: Execution options

        Returns:
            Transformation result
        """
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            return TransformResult(
                result_id=str(uuid.uuid4()),
                plan_id=plan.plan_id,
                success=False,
                output_data="{}",
                errors=[f"Invalid JSON input: {e}"],
                data_loss_report=DataLossReport(),
            )
        return self.execute(data, plan, options)

    def generate_reverse_plan(
        self,
        plan: SchemaTransformPlan,
    ) -> SchemaTransformPlan | None:
        """
        Generate a reverse transformation plan if possible.

        Args:
            plan: Original transformation plan

        Returns:
            Reverse plan or None if not reversible
        """
        if not plan.reversible:
            return None

        reverse_transformations: list[FieldTransformation] = []

        for transform in plan.transformations:
            if transform.transform_type == FieldTransformType.OMIT:
                continue  # Cannot reverse omitted fields

            if transform.transform_type == FieldTransformType.DEFAULT:
                continue  # Default values cannot be reversed

            reverse_transform = FieldTransformation(
                transformation_id=str(uuid.uuid4()),
                source_path=transform.target_path,
                target_path=transform.source_path,
                transform_type=self._get_reverse_transform_type(transform),
                description=f"Reverse of: {transform.description or transform.transformation_id}",
            )
            reverse_transformations.append(reverse_transform)

        return SchemaTransformPlan(
            plan_id=str(uuid.uuid4()),
            source_schema=plan.target_schema,
            target_schema=plan.source_schema,
            transformations=reverse_transformations,
            data_loss_risk=plan.data_loss_risk,
            reversible=True,
            reverse_plan_id=plan.plan_id,
            estimated_complexity=plan.estimated_complexity,
            validation_result=PlanValidation(is_valid=True),
            metadata=PlanMetadata(
                created_at=datetime.now(timezone.utc).isoformat(),
                purpose=f"Reverse of plan {plan.plan_id}",
            ),
        )

    # ============================================
    # Type Coercion Methods
    # ============================================

    def coerce_value(
        self,
        value: Any,
        source_type: str,
        target_type: str,
    ) -> tuple[Any, DataLossRisk, str | None]:
        """
        Coerce a value from one type to another.

        Args:
            value: Value to coerce
            source_type: Source type name
            target_type: Target type name

        Returns:
            Tuple of (coerced_value, risk_level, error_message)
        """
        if source_type == target_type:
            return value, DataLossRisk.NONE, None

        risk = self.TYPE_COERCION_RISK.get(
            (source_type, target_type), DataLossRisk.MEDIUM
        )

        try:
            if target_type == "string":
                return str(value), DataLossRisk.NONE, None

            elif target_type == "int":
                if isinstance(value, bool):
                    return 1 if value else 0, DataLossRisk.NONE, None
                if isinstance(value, float):
                    int_val = int(value)
                    if int_val != value:
                        return int_val, DataLossRisk.LOW, "Decimal truncated"
                    return int_val, DataLossRisk.NONE, None
                if isinstance(value, str):
                    try:
                        return int(float(value)), DataLossRisk.LOW, None
                    except ValueError:
                        return 0, DataLossRisk.HIGH, f"Cannot convert '{value}' to int"
                return int(value), risk, None

            elif target_type == "float":
                if isinstance(value, str):
                    try:
                        return float(value), DataLossRisk.LOW, None
                    except ValueError:
                        return 0.0, DataLossRisk.HIGH, f"Cannot convert '{value}' to float"
                return float(value), risk, None

            elif target_type == "bool":
                if isinstance(value, str):
                    lower = value.lower()
                    if lower in ("true", "1", "yes", "on"):
                        return True, DataLossRisk.NONE, None
                    if lower in ("false", "0", "no", "off"):
                        return False, DataLossRisk.NONE, None
                    return bool(value), DataLossRisk.LOW, None
                return bool(value), DataLossRisk.NONE, None

            elif target_type == "array":
                if isinstance(value, list):
                    return value, DataLossRisk.NONE, None
                return [value], DataLossRisk.NONE, None

            elif target_type == "object":
                if isinstance(value, dict):
                    return value, DataLossRisk.NONE, None
                if isinstance(value, str):
                    try:
                        return json.loads(value), DataLossRisk.LOW, None
                    except json.JSONDecodeError:
                        return {"value": value}, DataLossRisk.MEDIUM, None
                return {"value": value}, DataLossRisk.MEDIUM, None

            else:
                return value, DataLossRisk.MEDIUM, f"Unknown target type: {target_type}"

        except (TypeError, ValueError) as e:
            return None, DataLossRisk.HIGH, str(e)

    # ============================================
    # Private Helper Methods
    # ============================================

    def _match_field(
        self,
        target_field: FieldSpec,
        source_fields: dict[str, FieldSpec],
        options: PlanGenerationOptions,
    ) -> tuple[FieldTransformation | None, DataLossRisk]:
        """Match a target field to a source field."""
        # Try exact path match
        if target_field.path in source_fields:
            source_field = source_fields[target_field.path]
            return self._create_transformation(source_field, target_field)

        # Try exact name match
        for source_path, source_field in source_fields.items():
            if source_field.name == target_field.name:
                return self._create_transformation(source_field, target_field)

        # Try fuzzy matching if enabled
        if options.fuzzy_field_matching:
            best_match = None
            best_score = 0.0
            for source_path, source_field in source_fields.items():
                score = self._fuzzy_match_score(source_field.name, target_field.name)
                if score > best_score and score >= options.fuzzy_threshold:
                    best_score = score
                    best_match = source_field

            if best_match:
                return self._create_transformation(best_match, target_field)

        return None, DataLossRisk.NONE

    def _create_transformation(
        self,
        source_field: FieldSpec,
        target_field: FieldSpec,
    ) -> tuple[FieldTransformation, DataLossRisk]:
        """Create a transformation between two fields."""
        # Determine transform type
        if source_field.path == target_field.path and source_field.type == target_field.type:
            transform_type = FieldTransformType.COPY
            risk = DataLossRisk.NONE
        elif source_field.path != target_field.path and source_field.type == target_field.type:
            transform_type = FieldTransformType.RENAME
            risk = DataLossRisk.NONE
        elif source_field.type != target_field.type:
            transform_type = FieldTransformType.TYPE_COERCE
            risk = self.TYPE_COERCION_RISK.get(
                (source_field.type, target_field.type), DataLossRisk.MEDIUM
            )
        else:
            transform_type = FieldTransformType.COPY
            risk = DataLossRisk.NONE

        transformation = FieldTransformation(
            transformation_id=str(uuid.uuid4()),
            source_path=source_field.path,
            target_path=target_field.path,
            transform_type=transform_type,
            description=f"Transform '{source_field.name}' to '{target_field.name}' ({transform_type.value})",
        )

        return transformation, risk

    def _fuzzy_match_score(self, name1: str, name2: str) -> float:
        """Calculate fuzzy match score between two names."""
        # Normalize names
        n1 = self._normalize_name(name1)
        n2 = self._normalize_name(name2)

        # Use SequenceMatcher for similarity
        return SequenceMatcher(None, n1, n2).ratio()

    def _normalize_name(self, name: str) -> str:
        """Normalize a field name for comparison."""
        # Convert camelCase and PascalCase to lowercase with underscores
        name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
        name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
        return name.lower().replace("-", "_").replace(" ", "_")

    def _max_risk(self, risk1: DataLossRisk, risk2: DataLossRisk) -> DataLossRisk:
        """Return the higher of two risk levels."""
        risk_order = [
            DataLossRisk.NONE,
            DataLossRisk.LOW,
            DataLossRisk.MEDIUM,
            DataLossRisk.HIGH,
            DataLossRisk.CRITICAL,
        ]
        idx1 = risk_order.index(risk1)
        idx2 = risk_order.index(risk2)
        return risk_order[max(idx1, idx2)]

    def _validate_plan(
        self,
        source_schema: SchemaSpec,
        target_schema: SchemaSpec,
        transformations: list[FieldTransformation],
        unmapped: list[str],
        uncovered: list[str],
        coverage_pct: float,
    ) -> PlanValidation:
        """Validate a transformation plan."""
        errors: list[ValidationIssue] = []
        warnings: list[ValidationIssue] = []

        # Check for uncovered required fields
        for path in uncovered:
            errors.append(
                ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    severity="error",
                    message=f"Required target field '{path}' is not covered",
                    field_path=path,
                    suggestion="Add a transformation or default value",
                )
            )

        # Check for unmapped source fields
        for path in unmapped:
            warnings.append(
                ValidationIssue(
                    issue_id=str(uuid.uuid4()),
                    severity="warning",
                    message=f"Source field '{path}' is not mapped",
                    field_path=path,
                    suggestion="Consider if this data should be preserved",
                )
            )

        # Build coverage analysis
        coverage = CoverageAnalysis(
            source_fields_mapped=len(source_schema.fields) - len(unmapped),
            source_fields_total=len(source_schema.fields),
            target_fields_covered=len(target_schema.fields) - len(uncovered),
            target_fields_required=sum(1 for f in target_schema.fields if f.required),
            unmapped_source_fields=unmapped,
            uncovered_target_fields=uncovered,
            coverage_percentage=coverage_pct,
        )

        return PlanValidation(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            coverage_analysis=coverage,
        )

    def _assess_complexity(
        self, transformations: list[FieldTransformation]
    ) -> TransformComplexity:
        """Assess the complexity of a set of transformations."""
        if not transformations:
            return TransformComplexity.TRIVIAL

        complex_types = {
            FieldTransformType.RESTRUCTURE,
            FieldTransformType.AGGREGATE,
            FieldTransformType.SPLIT,
            FieldTransformType.COMPUTE,
        }

        simple_types = {
            FieldTransformType.COPY,
            FieldTransformType.RENAME,
        }

        complex_count = sum(
            1 for t in transformations if t.transform_type in complex_types
        )
        simple_count = sum(
            1 for t in transformations if t.transform_type in simple_types
        )
        total = len(transformations)

        if total == simple_count:
            return TransformComplexity.TRIVIAL if total < 5 else TransformComplexity.SIMPLE
        if complex_count == 0:
            return TransformComplexity.SIMPLE
        if complex_count < total * 0.3:
            return TransformComplexity.MODERATE
        if complex_count < total * 0.6:
            return TransformComplexity.COMPLEX
        return TransformComplexity.VERY_COMPLEX

    def _is_reversible(self, transformations: list[FieldTransformation]) -> bool:
        """Determine if transformations are reversible."""
        irreversible_types = {
            FieldTransformType.OMIT,
            FieldTransformType.AGGREGATE,
            FieldTransformType.COMPUTE,
        }

        for t in transformations:
            if t.transform_type in irreversible_types:
                return False
            if t.transform_type == FieldTransformType.DEFAULT and not t.source_path:
                return False

        return True

    def _get_reverse_transform_type(
        self, transform: FieldTransformation
    ) -> FieldTransformType:
        """Get the reverse transformation type."""
        if transform.transform_type == FieldTransformType.RENAME:
            return FieldTransformType.RENAME
        if transform.transform_type == FieldTransformType.TYPE_COERCE:
            return FieldTransformType.TYPE_COERCE
        if transform.transform_type == FieldTransformType.SPLIT:
            return FieldTransformType.AGGREGATE
        return FieldTransformType.COPY

    def _execute_transformation(
        self,
        input_data: dict[str, Any],
        output_data: dict[str, Any],
        transform: FieldTransformation,
        options: ExecutionOptions,
    ) -> FieldTransformResult:
        """Execute a single transformation."""
        try:
            # Get source value
            source_value = self._get_value_at_path(input_data, transform.source_path)

            if transform.transform_type == FieldTransformType.DEFAULT:
                # Use default value
                target_value = transform.default_value
                self._set_value_at_path(output_data, transform.target_path, target_value)
                return FieldTransformResult(
                    transformation_id=transform.transformation_id,
                    status=TransformValidation.VALID,
                    source_value=None,
                    target_value=str(target_value),
                    message="Used default value",
                )

            if source_value is None and transform.transform_type != FieldTransformType.DEFAULT:
                if transform.default_value:
                    self._set_value_at_path(
                        output_data, transform.target_path, transform.default_value
                    )
                    return FieldTransformResult(
                        transformation_id=transform.transformation_id,
                        status=TransformValidation.WARNING,
                        source_value=None,
                        target_value=str(transform.default_value),
                        message="Source value missing, used default",
                    )
                return FieldTransformResult(
                    transformation_id=transform.transformation_id,
                    status=TransformValidation.SKIPPED,
                    message="Source value not found",
                )

            # Apply transformation
            if transform.transform_type == FieldTransformType.COPY:
                target_value = source_value
            elif transform.transform_type == FieldTransformType.RENAME:
                target_value = source_value
            elif transform.transform_type == FieldTransformType.TYPE_COERCE:
                # Infer types from paths
                source_type = self._infer_type(source_value)
                target_type = self._infer_target_type(transform.target_path, source_type)
                target_value, _, err = self.coerce_value(source_value, source_type, target_type)
                if err:
                    return FieldTransformResult(
                        transformation_id=transform.transformation_id,
                        status=TransformValidation.WARNING,
                        source_value=str(source_value),
                        target_value=str(target_value),
                        message=err,
                    )
            elif transform.transform_type == FieldTransformType.MAP:
                target_value = self._apply_mapping(source_value, transform.value_mapping)
            elif transform.transform_type == FieldTransformType.OMIT:
                return FieldTransformResult(
                    transformation_id=transform.transformation_id,
                    status=TransformValidation.VALID,
                    source_value=str(source_value),
                    target_value=None,
                    message="Field omitted",
                )
            else:
                target_value = source_value

            self._set_value_at_path(output_data, transform.target_path, target_value)

            return FieldTransformResult(
                transformation_id=transform.transformation_id,
                status=TransformValidation.VALID,
                source_value=str(source_value),
                target_value=str(target_value),
            )

        except Exception as e:
            return FieldTransformResult(
                transformation_id=transform.transformation_id,
                status=TransformValidation.ERROR,
                message=str(e),
            )

    def _get_value_at_path(self, data: dict[str, Any], path: str) -> Any:
        """Get value at a JSON-like path."""
        if not path:
            return None

        # Handle JSONPath-like syntax
        path = path.lstrip("$.")

        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                try:
                    idx = int(part)
                    current = current[idx] if idx < len(current) else None
                except ValueError:
                    return None
            else:
                return None
            if current is None:
                return None
        return current

    def _set_value_at_path(self, data: dict[str, Any], path: str, value: Any) -> None:
        """Set value at a JSON-like path."""
        if not path:
            return

        # Handle JSONPath-like syntax
        path = path.lstrip("$.")

        parts = path.split(".")
        current = data
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

    def _infer_type(self, value: Any) -> str:
        """Infer the type of a value."""
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
        if isinstance(value, str):
            return "string"
        if isinstance(value, list):
            return "array"
        if isinstance(value, dict):
            return "object"
        return "string"

    def _infer_target_type(self, path: str, default_type: str) -> str:
        """Infer target type from path hints."""
        # Simple heuristics based on common naming patterns
        lower_path = path.lower()
        if any(x in lower_path for x in ["count", "num", "id", "age", "quantity"]):
            return "int"
        if any(x in lower_path for x in ["price", "rate", "amount", "percentage"]):
            return "float"
        if any(x in lower_path for x in ["is_", "has_", "can_", "should_", "enabled"]):
            return "bool"
        if any(x in lower_path for x in ["list", "items", "array"]):
            return "array"
        return default_type

    def _apply_mapping(
        self, value: Any, mapping: ValueMapping | None
    ) -> Any:
        """Apply value mapping."""
        if not mapping:
            return value

        str_value = str(value)
        compare_value = str_value if mapping.case_sensitive else str_value.lower()

        for entry in mapping.mappings:
            entry_source = (
                entry.source_value
                if mapping.case_sensitive
                else entry.source_value.lower()
            )
            if compare_value == entry_source:
                return entry.target_value

        return mapping.default_mapping if mapping.default_mapping else value

    def _track_data_loss(
        self,
        transform: FieldTransformation,
        result: FieldTransformResult,
        report: DataLossReport,
    ) -> None:
        """Track data loss from a transformation."""
        if transform.transform_type == FieldTransformType.OMIT:
            report.lost_fields.append(
                LostField(
                    source_path=transform.source_path,
                    reason="Field omitted by transformation",
                    original_value=result.source_value,
                )
            )

        if result.status == TransformValidation.WARNING and result.message:
            if "truncated" in result.message.lower():
                report.truncated_fields.append(
                    TruncatedField(
                        field_path=transform.target_path,
                        original_length=len(result.source_value or ""),
                        truncated_length=len(result.target_value or ""),
                        original_value=result.source_value,
                        truncated_value=result.target_value or "",
                    )
                )
            elif "precision" in result.message.lower() or "decimal" in result.message.lower():
                report.precision_loss_fields.append(
                    PrecisionLossField(
                        field_path=transform.target_path,
                        original_value=result.source_value or "",
                        converted_value=result.target_value or "",
                        precision_lost=result.message,
                    )
                )

    def _calculate_loss_severity(self, report: DataLossReport) -> DataLossRisk:
        """Calculate overall data loss severity."""
        if report.lost_fields:
            if len(report.lost_fields) > 3:
                return DataLossRisk.HIGH
            return DataLossRisk.MEDIUM
        if report.truncated_fields:
            return DataLossRisk.MEDIUM
        if report.precision_loss_fields:
            return DataLossRisk.LOW
        return DataLossRisk.NONE
