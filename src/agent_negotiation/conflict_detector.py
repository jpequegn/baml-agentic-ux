"""
Schema Conflict Detection Module

Detects conflicts between agent capabilities including schema mismatches,
constraint violations, and semantic ambiguities.

Issue #60 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.8)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable
import uuid


# ============================================
# Conflict Type Enums
# ============================================


class ConflictType(str, Enum):
    """Types of conflicts that can occur during negotiation."""

    SCHEMA_MISMATCH = "schema_mismatch"
    CONSTRAINT_VIOLATION = "constraint_violation"
    RESOURCE_CONTENTION = "resource_contention"
    PRIORITY_CLASH = "priority_clash"
    TRUST_INSUFFICIENT = "trust_insufficient"
    SEMANTIC_AMBIGUITY = "semantic_ambiguity"
    VERSION_INCOMPATIBLE = "version_incompatible"
    CAPACITY_EXCEEDED = "capacity_exceeded"
    TIMING_CONFLICT = "timing_conflict"
    SECURITY_POLICY = "security_policy"


class ConflictSeverity(str, Enum):
    """Severity levels for conflicts."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConflictCategory(str, Enum):
    """Categories of conflicts for grouping."""

    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    OPERATIONAL = "operational"
    POLICY = "policy"
    TEMPORAL = "temporal"


class ResolutionStrategy(str, Enum):
    """Strategy for resolving a conflict."""

    TRANSFORM = "transform"
    NEGOTIATE = "negotiate"
    ADAPT = "adapt"
    FALLBACK = "fallback"
    ESCALATE = "escalate"
    ACCEPT_RISK = "accept_risk"
    REJECT = "reject"
    BRIDGE = "bridge"
    SUBSET = "subset"


class EffortLevel(str, Enum):
    """Effort levels for resolution."""

    TRIVIAL = "trivial"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


# ============================================
# Conflict Description Types
# ============================================


@dataclass
class ConflictContext:
    """Additional context for understanding a conflict."""

    affected_capabilities: list[str] = field(default_factory=list)
    related_constraints: list[str] = field(default_factory=list)
    impact_description: str = ""
    precedent_conflicts: list[str] = field(default_factory=list)


@dataclass
class Conflict:
    """A single detected conflict."""

    conflict_id: str
    conflict_type: ConflictType
    category: ConflictCategory
    severity: ConflictSeverity
    description: str
    source_element: str
    target_element: str
    source_value: str | None = None
    target_value: str | None = None
    context: ConflictContext | None = None


# ============================================
# Resolution Types
# ============================================


@dataclass
class ResolutionRisk:
    """Risk associated with a resolution."""

    risk_id: str
    description: str
    probability: float
    impact: ConflictSeverity
    mitigation: str | None = None


@dataclass
class EffortEstimate:
    """Effort estimate for resolution."""

    level: EffortLevel
    estimated_hours: float | None = None
    complexity_factors: list[str] = field(default_factory=list)


@dataclass
class ResolutionStep:
    """A single step in a resolution path."""

    step_number: int
    action: str
    actor: str
    details: str
    validation: str | None = None


@dataclass
class ResolutionPath:
    """A possible path to resolve a conflict."""

    path_id: str
    strategy: ResolutionStrategy
    description: str
    steps: list[ResolutionStep] = field(default_factory=list)
    estimated_effort: EffortEstimate | None = None
    success_likelihood: float = 0.5
    trade_offs: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    risks: list[ResolutionRisk] = field(default_factory=list)


# ============================================
# Conflict Analysis Types
# ============================================


@dataclass
class ConflictSeverityCount:
    """Count of conflicts by severity."""

    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0


@dataclass
class ConflictCategoryCount:
    """Count of conflicts by category."""

    structural: int = 0
    semantic: int = 0
    operational: int = 0
    policy: int = 0
    temporal: int = 0


@dataclass
class ConflictTypeCount:
    """Count of conflicts by type."""

    schema_mismatch: int = 0
    constraint_violation: int = 0
    resource_contention: int = 0
    priority_clash: int = 0
    trust_insufficient: int = 0
    semantic_ambiguity: int = 0
    version_incompatible: int = 0
    capacity_exceeded: int = 0
    timing_conflict: int = 0
    security_policy: int = 0


@dataclass
class ConflictSummary:
    """Summary statistics for conflict analysis."""

    total_conflicts: int = 0
    by_severity: ConflictSeverityCount = field(default_factory=ConflictSeverityCount)
    by_category: ConflictCategoryCount = field(default_factory=ConflictCategoryCount)
    by_type: ConflictTypeCount = field(default_factory=ConflictTypeCount)
    blocking_conflicts: int = 0
    auto_resolvable: int = 0


@dataclass
class ConflictAnalysis:
    """Complete analysis of conflicts between two parties."""

    analysis_id: str
    source_id: str
    target_id: str
    timestamp: str
    conflicts: list[Conflict] = field(default_factory=list)
    overall_severity: ConflictSeverity = ConflictSeverity.LOW
    resolvable: bool = True
    resolution_paths: list[ResolutionPath] = field(default_factory=list)
    summary: ConflictSummary = field(default_factory=ConflictSummary)
    recommendations: list[str] = field(default_factory=list)


# ============================================
# Detection Request/Response Types
# ============================================


@dataclass
class ConstraintSpec:
    """Constraint specification for detection."""

    constraint_id: str
    constraint_type: str
    operator: str
    value: str
    required: bool = True
    field: str | None = None


@dataclass
class DetectionOptions:
    """Options for conflict detection."""

    include_resolution_paths: bool = True
    max_resolution_paths: int = 3
    severity_threshold: ConflictSeverity = ConflictSeverity.LOW
    detect_semantic: bool = True
    deep_schema_analysis: bool = True
    include_risk_assessment: bool = True


@dataclass
class SchemaDefinition:
    """Schema definition for conflict detection."""

    schema_id: str
    name: str
    properties: dict[str, Any] = field(default_factory=dict)
    required_fields: list[str] = field(default_factory=list)
    version: str = "1.0"


@dataclass
class ConflictDetectionRequest:
    """Request to detect conflicts."""

    request_id: str
    source_schema: SchemaDefinition | None = None
    target_schema: SchemaDefinition | None = None
    source_constraints: list[ConstraintSpec] | None = None
    target_constraints: list[ConstraintSpec] | None = None
    detection_options: DetectionOptions = field(default_factory=DetectionOptions)


@dataclass
class ConflictDetectionResponse:
    """Response from conflict detection."""

    request_id: str
    analysis: ConflictAnalysis
    detection_time_ms: int = 0
    warnings: list[str] = field(default_factory=list)


# ============================================
# Conflict Detector Implementation
# ============================================


# Type alias for conflict detection callback
ConflictCallback = Callable[[Conflict], None]


class ConflictDetector:
    """
    Detects and analyzes conflicts between agent capabilities.

    The detector identifies various types of conflicts including:
    - Schema mismatches (type incompatibilities, missing fields)
    - Constraint violations (cannot meet requirements)
    - Resource contention (exclusive resource needs)
    - Trust insufficiency (security level gaps)
    - Semantic ambiguities (same term, different meanings)
    """

    # Mapping of Python types for schema comparison
    TYPE_COMPATIBILITY: dict[str, set[str]] = {
        "string": {"string", "str"},
        "str": {"string", "str"},
        "integer": {"integer", "int", "number", "float"},
        "int": {"integer", "int", "number", "float"},
        "number": {"number", "float", "integer", "int"},
        "float": {"number", "float", "integer", "int"},
        "boolean": {"boolean", "bool"},
        "bool": {"boolean", "bool"},
        "array": {"array", "list"},
        "list": {"array", "list"},
        "object": {"object", "dict", "map"},
        "dict": {"object", "dict", "map"},
        "map": {"object", "dict", "map"},
    }

    # Type coercion severity (lower is easier)
    TYPE_COERCION_SEVERITY: dict[tuple[str, str], ConflictSeverity] = {
        ("int", "float"): ConflictSeverity.LOW,
        ("integer", "number"): ConflictSeverity.LOW,
        ("float", "int"): ConflictSeverity.MEDIUM,  # Potential data loss
        ("number", "integer"): ConflictSeverity.MEDIUM,
        ("string", "int"): ConflictSeverity.HIGH,
        ("string", "number"): ConflictSeverity.HIGH,
        ("int", "string"): ConflictSeverity.LOW,
        ("number", "string"): ConflictSeverity.LOW,
        ("boolean", "string"): ConflictSeverity.LOW,
        ("string", "boolean"): ConflictSeverity.MEDIUM,
    }

    def __init__(
        self,
        default_options: DetectionOptions | None = None,
        conflict_callback: ConflictCallback | None = None,
    ):
        """
        Initialize the conflict detector.

        Args:
            default_options: Default detection options
            conflict_callback: Optional callback invoked for each detected conflict
        """
        self.default_options = default_options or DetectionOptions()
        self.conflict_callback = conflict_callback

    def detect_conflicts(
        self,
        request: ConflictDetectionRequest,
    ) -> ConflictDetectionResponse:
        """
        Detect conflicts based on the provided request.

        Args:
            request: Detection request with schemas and constraints

        Returns:
            Response containing conflict analysis
        """
        start_time = datetime.now(timezone.utc)
        options = request.detection_options or self.default_options

        conflicts: list[Conflict] = []
        warnings: list[str] = []

        # Detect schema conflicts
        if request.source_schema and request.target_schema:
            schema_conflicts = self.detect_schema_conflicts(
                request.source_schema,
                request.target_schema,
                options,
            )
            conflicts.extend(schema_conflicts)

        # Detect constraint conflicts
        if request.source_constraints and request.target_constraints:
            constraint_conflicts = self.detect_constraint_conflicts(
                request.source_constraints,
                request.target_constraints,
                options,
            )
            conflicts.extend(constraint_conflicts)

        # Filter by severity threshold
        conflicts = self._filter_by_severity(conflicts, options.severity_threshold)

        # Invoke callbacks
        for conflict in conflicts:
            if self.conflict_callback:
                self.conflict_callback(conflict)

        # Generate resolution paths if requested
        resolution_paths: list[ResolutionPath] = []
        if options.include_resolution_paths:
            resolution_paths = self._generate_resolution_paths(
                conflicts, options.max_resolution_paths
            )

        # Build analysis
        analysis = self._build_analysis(
            source_id=request.source_schema.schema_id if request.source_schema else "",
            target_id=request.target_schema.schema_id if request.target_schema else "",
            conflicts=conflicts,
            resolution_paths=resolution_paths,
        )

        # Calculate detection time
        end_time = datetime.now(timezone.utc)
        detection_time_ms = int((end_time - start_time).total_seconds() * 1000)

        return ConflictDetectionResponse(
            request_id=request.request_id,
            analysis=analysis,
            detection_time_ms=detection_time_ms,
            warnings=warnings,
        )

    def detect_schema_conflicts(
        self,
        source: SchemaDefinition,
        target: SchemaDefinition,
        options: DetectionOptions | None = None,
    ) -> list[Conflict]:
        """
        Detect conflicts between two schemas.

        Args:
            source: Source schema definition
            target: Target schema requirements
            options: Detection options

        Returns:
            List of detected conflicts
        """
        conflicts: list[Conflict] = []
        options = options or self.default_options

        # Check for missing required fields
        missing_conflicts = self._detect_missing_fields(source, target)
        conflicts.extend(missing_conflicts)

        # Check for type mismatches
        type_conflicts = self._detect_type_mismatches(source, target)
        conflicts.extend(type_conflicts)

        # Check for version incompatibilities
        if source.version != target.version:
            version_conflict = self._create_version_conflict(source, target)
            if version_conflict:
                conflicts.append(version_conflict)

        # Deep schema analysis for nested types
        if options.deep_schema_analysis:
            nested_conflicts = self._detect_nested_conflicts(source, target)
            conflicts.extend(nested_conflicts)

        return conflicts

    def detect_constraint_conflicts(
        self,
        source_constraints: list[ConstraintSpec],
        target_constraints: list[ConstraintSpec],
        options: DetectionOptions | None = None,
    ) -> list[Conflict]:
        """
        Detect conflicts between constraints.

        Args:
            source_constraints: Constraints from source
            target_constraints: Constraints from target
            options: Detection options

        Returns:
            List of detected constraint conflicts
        """
        conflicts: list[Conflict] = []

        # Build lookup for source constraints by field
        source_by_field: dict[str | None, list[ConstraintSpec]] = {}
        for c in source_constraints:
            if c.field not in source_by_field:
                source_by_field[c.field] = []
            source_by_field[c.field].append(c)

        # Check each target constraint
        for target_c in target_constraints:
            if not target_c.required:
                continue

            source_matches = source_by_field.get(target_c.field, [])

            if not source_matches:
                # Missing constraint
                conflict = Conflict(
                    conflict_id=str(uuid.uuid4()),
                    conflict_type=ConflictType.CONSTRAINT_VIOLATION,
                    category=ConflictCategory.OPERATIONAL,
                    severity=ConflictSeverity.HIGH,
                    description=f"Required constraint '{target_c.constraint_type}' on field '{target_c.field}' not provided by source",
                    source_element="(missing)",
                    target_element=target_c.constraint_id,
                    target_value=target_c.value,
                )
                conflicts.append(conflict)
            else:
                # Check for constraint value conflicts
                for source_c in source_matches:
                    value_conflict = self._check_constraint_values(source_c, target_c)
                    if value_conflict:
                        conflicts.append(value_conflict)

        return conflicts

    def detect_trust_conflicts(
        self,
        source_trust_level: int,
        target_required_trust: int,
        context: str = "",
    ) -> Conflict | None:
        """
        Detect trust level conflicts.

        Args:
            source_trust_level: Trust level offered by source (0-100)
            target_required_trust: Trust level required by target (0-100)
            context: Additional context

        Returns:
            Conflict if trust is insufficient, None otherwise
        """
        if source_trust_level >= target_required_trust:
            return None

        gap = target_required_trust - source_trust_level
        severity = ConflictSeverity.LOW
        if gap > 50:
            severity = ConflictSeverity.CRITICAL
        elif gap > 30:
            severity = ConflictSeverity.HIGH
        elif gap > 10:
            severity = ConflictSeverity.MEDIUM

        return Conflict(
            conflict_id=str(uuid.uuid4()),
            conflict_type=ConflictType.TRUST_INSUFFICIENT,
            category=ConflictCategory.POLICY,
            severity=severity,
            description=f"Trust level {source_trust_level} is below required {target_required_trust}",
            source_element="trust_level",
            target_element="required_trust",
            source_value=str(source_trust_level),
            target_value=str(target_required_trust),
            context=ConflictContext(
                impact_description=f"Trust gap of {gap} points. {context}",
            ),
        )

    def detect_capacity_conflicts(
        self,
        source_capacity: dict[str, float],
        target_requirements: dict[str, float],
    ) -> list[Conflict]:
        """
        Detect capacity/resource conflicts.

        Args:
            source_capacity: Available capacity (resource -> amount)
            target_requirements: Required capacity (resource -> amount)

        Returns:
            List of capacity conflicts
        """
        conflicts: list[Conflict] = []

        for resource, required in target_requirements.items():
            available = source_capacity.get(resource, 0.0)
            if available < required:
                shortage = required - available
                severity = ConflictSeverity.MEDIUM
                if shortage > required * 0.5:
                    severity = ConflictSeverity.HIGH
                if shortage >= required:
                    severity = ConflictSeverity.CRITICAL

                conflict = Conflict(
                    conflict_id=str(uuid.uuid4()),
                    conflict_type=ConflictType.CAPACITY_EXCEEDED,
                    category=ConflictCategory.OPERATIONAL,
                    severity=severity,
                    description=f"Resource '{resource}' capacity ({available}) below required ({required})",
                    source_element=f"capacity.{resource}",
                    target_element=f"requirements.{resource}",
                    source_value=str(available),
                    target_value=str(required),
                    context=ConflictContext(
                        impact_description=f"Shortage of {shortage} units for {resource}",
                    ),
                )
                conflicts.append(conflict)

        return conflicts

    def detect_timing_conflicts(
        self,
        source_availability: tuple[str, str],  # (start, end) ISO timestamps
        target_requirement: tuple[str, str],
    ) -> Conflict | None:
        """
        Detect timing/scheduling conflicts.

        Args:
            source_availability: When source is available (start, end)
            target_requirement: When target needs it (start, end)

        Returns:
            Conflict if timing is incompatible, None otherwise
        """
        try:
            src_start = datetime.fromisoformat(source_availability[0].replace("Z", "+00:00"))
            src_end = datetime.fromisoformat(source_availability[1].replace("Z", "+00:00"))
            tgt_start = datetime.fromisoformat(target_requirement[0].replace("Z", "+00:00"))
            tgt_end = datetime.fromisoformat(target_requirement[1].replace("Z", "+00:00"))
        except ValueError:
            return None

        # Check for overlap
        if src_end < tgt_start or src_start > tgt_end:
            return Conflict(
                conflict_id=str(uuid.uuid4()),
                conflict_type=ConflictType.TIMING_CONFLICT,
                category=ConflictCategory.TEMPORAL,
                severity=ConflictSeverity.HIGH,
                description="No overlap between source availability and target requirements",
                source_element="availability_window",
                target_element="required_window",
                source_value=f"{source_availability[0]} to {source_availability[1]}",
                target_value=f"{target_requirement[0]} to {target_requirement[1]}",
            )

        # Check if source covers the full requirement
        if src_start > tgt_start or src_end < tgt_end:
            return Conflict(
                conflict_id=str(uuid.uuid4()),
                conflict_type=ConflictType.TIMING_CONFLICT,
                category=ConflictCategory.TEMPORAL,
                severity=ConflictSeverity.MEDIUM,
                description="Source availability does not fully cover target requirements",
                source_element="availability_window",
                target_element="required_window",
                source_value=f"{source_availability[0]} to {source_availability[1]}",
                target_value=f"{target_requirement[0]} to {target_requirement[1]}",
            )

        return None

    def detect_semantic_conflicts(
        self,
        source_definitions: dict[str, str],
        target_definitions: dict[str, str],
    ) -> list[Conflict]:
        """
        Detect semantic ambiguity conflicts.

        Args:
            source_definitions: Term -> meaning mappings from source
            target_definitions: Term -> meaning mappings from target

        Returns:
            List of semantic conflicts
        """
        conflicts: list[Conflict] = []

        # Find shared terms with different meanings
        shared_terms = set(source_definitions.keys()) & set(target_definitions.keys())

        for term in shared_terms:
            source_meaning = source_definitions[term].lower().strip()
            target_meaning = target_definitions[term].lower().strip()

            if source_meaning != target_meaning:
                # Calculate similarity (simple word overlap)
                source_words = set(source_meaning.split())
                target_words = set(target_meaning.split())
                overlap = len(source_words & target_words)
                total = len(source_words | target_words)
                similarity = overlap / total if total > 0 else 0

                severity = ConflictSeverity.LOW
                if similarity < 0.3:
                    severity = ConflictSeverity.HIGH
                elif similarity < 0.6:
                    severity = ConflictSeverity.MEDIUM

                conflict = Conflict(
                    conflict_id=str(uuid.uuid4()),
                    conflict_type=ConflictType.SEMANTIC_AMBIGUITY,
                    category=ConflictCategory.SEMANTIC,
                    severity=severity,
                    description=f"Term '{term}' has different meanings in source and target",
                    source_element=term,
                    target_element=term,
                    source_value=source_definitions[term],
                    target_value=target_definitions[term],
                    context=ConflictContext(
                        impact_description=f"Semantic similarity: {similarity:.2%}",
                    ),
                )
                conflicts.append(conflict)

        return conflicts

    # ============================================
    # Private Helper Methods
    # ============================================

    def _detect_missing_fields(
        self,
        source: SchemaDefinition,
        target: SchemaDefinition,
    ) -> list[Conflict]:
        """Detect missing required fields."""
        conflicts: list[Conflict] = []

        for required_field in target.required_fields:
            if required_field not in source.properties:
                conflict = Conflict(
                    conflict_id=str(uuid.uuid4()),
                    conflict_type=ConflictType.SCHEMA_MISMATCH,
                    category=ConflictCategory.STRUCTURAL,
                    severity=ConflictSeverity.HIGH,
                    description=f"Required field '{required_field}' missing in source schema",
                    source_element=f"properties.{required_field}",
                    target_element=f"required_fields.{required_field}",
                    source_value="(missing)",
                    target_value="required",
                )
                conflicts.append(conflict)

        return conflicts

    def _detect_type_mismatches(
        self,
        source: SchemaDefinition,
        target: SchemaDefinition,
    ) -> list[Conflict]:
        """Detect type mismatches in shared properties."""
        conflicts: list[Conflict] = []

        for prop_name, target_info in target.properties.items():
            if prop_name not in source.properties:
                continue  # Handled by missing fields check

            source_info = source.properties[prop_name]
            source_type = self._get_type(source_info)
            target_type = self._get_type(target_info)

            if not self._types_compatible(source_type, target_type):
                severity = self._get_type_mismatch_severity(source_type, target_type)
                conflict = Conflict(
                    conflict_id=str(uuid.uuid4()),
                    conflict_type=ConflictType.SCHEMA_MISMATCH,
                    category=ConflictCategory.STRUCTURAL,
                    severity=severity,
                    description=f"Type mismatch for property '{prop_name}': source has '{source_type}', target expects '{target_type}'",
                    source_element=f"properties.{prop_name}",
                    target_element=f"properties.{prop_name}",
                    source_value=source_type,
                    target_value=target_type,
                )
                conflicts.append(conflict)

        return conflicts

    def _create_version_conflict(
        self,
        source: SchemaDefinition,
        target: SchemaDefinition,
    ) -> Conflict | None:
        """Create a version conflict if versions are incompatible."""
        try:
            source_parts = [int(x) for x in source.version.split(".")]
            target_parts = [int(x) for x in target.version.split(".")]
        except ValueError:
            # Non-numeric versions, treat as potentially incompatible
            return Conflict(
                conflict_id=str(uuid.uuid4()),
                conflict_type=ConflictType.VERSION_INCOMPATIBLE,
                category=ConflictCategory.STRUCTURAL,
                severity=ConflictSeverity.MEDIUM,
                description=f"Version mismatch: source '{source.version}' vs target '{target.version}'",
                source_element="version",
                target_element="version",
                source_value=source.version,
                target_value=target.version,
            )

        # Compare major versions
        if len(source_parts) > 0 and len(target_parts) > 0:
            if source_parts[0] != target_parts[0]:
                return Conflict(
                    conflict_id=str(uuid.uuid4()),
                    conflict_type=ConflictType.VERSION_INCOMPATIBLE,
                    category=ConflictCategory.STRUCTURAL,
                    severity=ConflictSeverity.HIGH,
                    description=f"Major version mismatch: source v{source.version} vs target v{target.version}",
                    source_element="version",
                    target_element="version",
                    source_value=source.version,
                    target_value=target.version,
                )

        return None

    def _detect_nested_conflicts(
        self,
        source: SchemaDefinition,
        target: SchemaDefinition,
    ) -> list[Conflict]:
        """Detect conflicts in nested object properties."""
        conflicts: list[Conflict] = []

        for prop_name, target_info in target.properties.items():
            if prop_name not in source.properties:
                continue

            source_info = source.properties[prop_name]

            # Check for nested objects
            if isinstance(target_info, dict) and isinstance(source_info, dict):
                if "properties" in target_info and "properties" in source_info:
                    # Create nested schemas and recurse
                    nested_source = SchemaDefinition(
                        schema_id=f"{source.schema_id}.{prop_name}",
                        name=f"{source.name}.{prop_name}",
                        properties=source_info.get("properties", {}),
                        required_fields=source_info.get("required", []),
                    )
                    nested_target = SchemaDefinition(
                        schema_id=f"{target.schema_id}.{prop_name}",
                        name=f"{target.name}.{prop_name}",
                        properties=target_info.get("properties", {}),
                        required_fields=target_info.get("required", []),
                    )
                    nested_conflicts = self.detect_schema_conflicts(
                        nested_source, nested_target
                    )
                    # Update conflict paths to include parent
                    for c in nested_conflicts:
                        c.source_element = f"{prop_name}.{c.source_element}"
                        c.target_element = f"{prop_name}.{c.target_element}"
                    conflicts.extend(nested_conflicts)

        return conflicts

    def _check_constraint_values(
        self,
        source: ConstraintSpec,
        target: ConstraintSpec,
    ) -> Conflict | None:
        """Check if source constraint satisfies target constraint."""
        # Try numeric comparison
        try:
            source_val = float(source.value)
            target_val = float(target.value)

            # Check based on operator
            satisfied = True
            if target.operator in (">=", "gte"):
                satisfied = source_val >= target_val
            elif target.operator in ("<=", "lte"):
                satisfied = source_val <= target_val
            elif target.operator in (">", "gt"):
                satisfied = source_val > target_val
            elif target.operator in ("<", "lt"):
                satisfied = source_val < target_val
            elif target.operator in ("==", "eq", "equals"):
                satisfied = source_val == target_val
            elif target.operator in ("!=", "ne", "not_equals"):
                satisfied = source_val != target_val

            if not satisfied:
                return Conflict(
                    conflict_id=str(uuid.uuid4()),
                    conflict_type=ConflictType.CONSTRAINT_VIOLATION,
                    category=ConflictCategory.OPERATIONAL,
                    severity=ConflictSeverity.MEDIUM,
                    description=f"Constraint violation: source value {source_val} does not satisfy {target.operator} {target_val}",
                    source_element=source.constraint_id,
                    target_element=target.constraint_id,
                    source_value=source.value,
                    target_value=f"{target.operator} {target.value}",
                )
        except ValueError:
            # String comparison
            if target.operator in ("==", "eq", "equals"):
                if source.value != target.value:
                    return Conflict(
                        conflict_id=str(uuid.uuid4()),
                        conflict_type=ConflictType.CONSTRAINT_VIOLATION,
                        category=ConflictCategory.OPERATIONAL,
                        severity=ConflictSeverity.MEDIUM,
                        description=f"Constraint mismatch: '{source.value}' != '{target.value}'",
                        source_element=source.constraint_id,
                        target_element=target.constraint_id,
                        source_value=source.value,
                        target_value=target.value,
                    )

        return None

    def _get_type(self, info: Any) -> str:
        """Extract type from property info."""
        if isinstance(info, str):
            return info.lower()
        if isinstance(info, dict):
            return info.get("type", "unknown").lower()
        return "unknown"

    def _types_compatible(self, source_type: str, target_type: str) -> bool:
        """Check if two types are compatible."""
        if source_type == target_type:
            return True
        compatible_types = self.TYPE_COMPATIBILITY.get(source_type, set())
        return target_type in compatible_types

    def _get_type_mismatch_severity(
        self, source_type: str, target_type: str
    ) -> ConflictSeverity:
        """Determine severity of a type mismatch."""
        key = (source_type, target_type)
        if key in self.TYPE_COERCION_SEVERITY:
            return self.TYPE_COERCION_SEVERITY[key]

        # Check reverse direction
        reverse_key = (target_type, source_type)
        if reverse_key in self.TYPE_COERCION_SEVERITY:
            return self.TYPE_COERCION_SEVERITY[reverse_key]

        # Default to high for unknown conversions
        return ConflictSeverity.HIGH

    def _filter_by_severity(
        self,
        conflicts: list[Conflict],
        threshold: ConflictSeverity,
    ) -> list[Conflict]:
        """Filter conflicts by minimum severity."""
        severity_order = [
            ConflictSeverity.LOW,
            ConflictSeverity.MEDIUM,
            ConflictSeverity.HIGH,
            ConflictSeverity.CRITICAL,
        ]
        threshold_idx = severity_order.index(threshold)

        return [
            c
            for c in conflicts
            if severity_order.index(c.severity) >= threshold_idx
        ]

    def _generate_resolution_paths(
        self,
        conflicts: list[Conflict],
        max_paths: int,
    ) -> list[ResolutionPath]:
        """Generate resolution paths for conflicts."""
        paths: list[ResolutionPath] = []

        for conflict in conflicts:
            conflict_paths = self._get_resolution_paths_for_conflict(conflict)
            paths.extend(conflict_paths[:max_paths])

        return paths

    def _get_resolution_paths_for_conflict(
        self, conflict: Conflict
    ) -> list[ResolutionPath]:
        """Get resolution paths for a specific conflict."""
        paths: list[ResolutionPath] = []

        if conflict.conflict_type == ConflictType.SCHEMA_MISMATCH:
            paths.append(
                ResolutionPath(
                    path_id=str(uuid.uuid4()),
                    strategy=ResolutionStrategy.TRANSFORM,
                    description=f"Transform schema to resolve: {conflict.description}",
                    steps=[
                        ResolutionStep(
                            step_number=1,
                            action="Identify transformation",
                            actor="source",
                            details="Determine required transformation to match target schema",
                        ),
                        ResolutionStep(
                            step_number=2,
                            action="Apply transformation",
                            actor="source",
                            details="Implement and apply the schema transformation",
                            validation="Verify transformed data matches target schema",
                        ),
                    ],
                    estimated_effort=EffortEstimate(
                        level=EffortLevel.MEDIUM,
                        estimated_hours=2.0,
                        complexity_factors=["schema complexity", "data volume"],
                    ),
                    success_likelihood=0.8,
                )
            )
            paths.append(
                ResolutionPath(
                    path_id=str(uuid.uuid4()),
                    strategy=ResolutionStrategy.ADAPT,
                    description="Adapt target to accept source schema",
                    steps=[
                        ResolutionStep(
                            step_number=1,
                            action="Negotiate schema flexibility",
                            actor="target",
                            details="Request target to accept alternative schema",
                        ),
                    ],
                    estimated_effort=EffortEstimate(level=EffortLevel.LOW),
                    success_likelihood=0.5,
                )
            )

        elif conflict.conflict_type == ConflictType.CONSTRAINT_VIOLATION:
            paths.append(
                ResolutionPath(
                    path_id=str(uuid.uuid4()),
                    strategy=ResolutionStrategy.NEGOTIATE,
                    description="Negotiate constraint relaxation",
                    steps=[
                        ResolutionStep(
                            step_number=1,
                            action="Propose alternative constraint",
                            actor="source",
                            details="Suggest modified constraint that source can meet",
                        ),
                    ],
                    estimated_effort=EffortEstimate(level=EffortLevel.LOW),
                    success_likelihood=0.6,
                )
            )

        elif conflict.conflict_type == ConflictType.TRUST_INSUFFICIENT:
            paths.append(
                ResolutionPath(
                    path_id=str(uuid.uuid4()),
                    strategy=ResolutionStrategy.ESCALATE,
                    description="Escalate for trust verification",
                    steps=[
                        ResolutionStep(
                            step_number=1,
                            action="Request trust verification",
                            actor="source",
                            details="Provide additional credentials or verification",
                        ),
                    ],
                    estimated_effort=EffortEstimate(level=EffortLevel.MEDIUM),
                    success_likelihood=0.7,
                )
            )

        elif conflict.conflict_type == ConflictType.CAPACITY_EXCEEDED:
            paths.append(
                ResolutionPath(
                    path_id=str(uuid.uuid4()),
                    strategy=ResolutionStrategy.SUBSET,
                    description="Use reduced capacity subset",
                    steps=[
                        ResolutionStep(
                            step_number=1,
                            action="Identify reducible requirements",
                            actor="both",
                            details="Find requirements that can be reduced",
                        ),
                    ],
                    estimated_effort=EffortEstimate(level=EffortLevel.LOW),
                    success_likelihood=0.7,
                )
            )

        elif conflict.conflict_type == ConflictType.TIMING_CONFLICT:
            paths.append(
                ResolutionPath(
                    path_id=str(uuid.uuid4()),
                    strategy=ResolutionStrategy.NEGOTIATE,
                    description="Negotiate alternative timing",
                    steps=[
                        ResolutionStep(
                            step_number=1,
                            action="Propose alternative schedule",
                            actor="both",
                            details="Find mutually acceptable time window",
                        ),
                    ],
                    estimated_effort=EffortEstimate(level=EffortLevel.LOW),
                    success_likelihood=0.8,
                )
            )

        elif conflict.conflict_type == ConflictType.SEMANTIC_AMBIGUITY:
            paths.append(
                ResolutionPath(
                    path_id=str(uuid.uuid4()),
                    strategy=ResolutionStrategy.BRIDGE,
                    description="Create semantic mapping",
                    steps=[
                        ResolutionStep(
                            step_number=1,
                            action="Define term mapping",
                            actor="both",
                            details="Create explicit mapping between term definitions",
                        ),
                    ],
                    estimated_effort=EffortEstimate(level=EffortLevel.MEDIUM),
                    success_likelihood=0.9,
                )
            )

        # Add fallback path for critical conflicts
        if conflict.severity == ConflictSeverity.CRITICAL:
            paths.append(
                ResolutionPath(
                    path_id=str(uuid.uuid4()),
                    strategy=ResolutionStrategy.REJECT,
                    description="Reject negotiation due to unresolvable conflict",
                    steps=[
                        ResolutionStep(
                            step_number=1,
                            action="Document conflict",
                            actor="both",
                            details="Document the blocking conflict for future reference",
                        ),
                    ],
                    estimated_effort=EffortEstimate(level=EffortLevel.TRIVIAL),
                    success_likelihood=1.0,
                    trade_offs=["Negotiation fails", "No capability exchange"],
                )
            )

        return paths

    def _build_analysis(
        self,
        source_id: str,
        target_id: str,
        conflicts: list[Conflict],
        resolution_paths: list[ResolutionPath],
    ) -> ConflictAnalysis:
        """Build complete conflict analysis."""
        # Calculate summary
        summary = ConflictSummary(total_conflicts=len(conflicts))

        for conflict in conflicts:
            # By severity
            if conflict.severity == ConflictSeverity.LOW:
                summary.by_severity.low += 1
                summary.auto_resolvable += 1
            elif conflict.severity == ConflictSeverity.MEDIUM:
                summary.by_severity.medium += 1
            elif conflict.severity == ConflictSeverity.HIGH:
                summary.by_severity.high += 1
            elif conflict.severity == ConflictSeverity.CRITICAL:
                summary.by_severity.critical += 1
                summary.blocking_conflicts += 1

            # By category
            if conflict.category == ConflictCategory.STRUCTURAL:
                summary.by_category.structural += 1
            elif conflict.category == ConflictCategory.SEMANTIC:
                summary.by_category.semantic += 1
            elif conflict.category == ConflictCategory.OPERATIONAL:
                summary.by_category.operational += 1
            elif conflict.category == ConflictCategory.POLICY:
                summary.by_category.policy += 1
            elif conflict.category == ConflictCategory.TEMPORAL:
                summary.by_category.temporal += 1

            # By type
            if conflict.conflict_type == ConflictType.SCHEMA_MISMATCH:
                summary.by_type.schema_mismatch += 1
            elif conflict.conflict_type == ConflictType.CONSTRAINT_VIOLATION:
                summary.by_type.constraint_violation += 1
            elif conflict.conflict_type == ConflictType.RESOURCE_CONTENTION:
                summary.by_type.resource_contention += 1
            elif conflict.conflict_type == ConflictType.PRIORITY_CLASH:
                summary.by_type.priority_clash += 1
            elif conflict.conflict_type == ConflictType.TRUST_INSUFFICIENT:
                summary.by_type.trust_insufficient += 1
            elif conflict.conflict_type == ConflictType.SEMANTIC_AMBIGUITY:
                summary.by_type.semantic_ambiguity += 1
            elif conflict.conflict_type == ConflictType.VERSION_INCOMPATIBLE:
                summary.by_type.version_incompatible += 1
            elif conflict.conflict_type == ConflictType.CAPACITY_EXCEEDED:
                summary.by_type.capacity_exceeded += 1
            elif conflict.conflict_type == ConflictType.TIMING_CONFLICT:
                summary.by_type.timing_conflict += 1
            elif conflict.conflict_type == ConflictType.SECURITY_POLICY:
                summary.by_type.security_policy += 1

        # Determine overall severity
        overall_severity = ConflictSeverity.LOW
        if summary.by_severity.critical > 0:
            overall_severity = ConflictSeverity.CRITICAL
        elif summary.by_severity.high > 0:
            overall_severity = ConflictSeverity.HIGH
        elif summary.by_severity.medium > 0:
            overall_severity = ConflictSeverity.MEDIUM

        # Determine if resolvable
        resolvable = summary.blocking_conflicts == 0

        # Generate recommendations
        recommendations: list[str] = []
        if summary.by_type.schema_mismatch > 0:
            recommendations.append(
                "Consider implementing schema transformations to resolve type mismatches"
            )
        if summary.by_type.trust_insufficient > 0:
            recommendations.append(
                "Verify trust credentials or negotiate reduced trust requirements"
            )
        if summary.blocking_conflicts > 0:
            recommendations.append(
                f"Address {summary.blocking_conflicts} critical conflicts before proceeding"
            )
        if not resolvable:
            recommendations.append(
                "Negotiation cannot proceed without resolving critical conflicts"
            )

        return ConflictAnalysis(
            analysis_id=str(uuid.uuid4()),
            source_id=source_id,
            target_id=target_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            conflicts=conflicts,
            overall_severity=overall_severity,
            resolvable=resolvable,
            resolution_paths=resolution_paths,
            summary=summary,
            recommendations=recommendations,
        )
