"""
Conflict Resolution for Agent Negotiation

Handles schema mismatches, constraint conflicts, and negotiation deadlocks
with intelligent resolution strategies.

Issue #56 - Phase 3c: Conflict Resolution
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import json
import uuid

from src.lui_simulator.agent_types import (
    AgentCapability,
    SchemaDefinition,
    SchemaType,
    SchemaProperty,
)


# ============================================
# Enums
# ============================================


class ConflictType(Enum):
    """Types of conflicts that can occur during negotiation."""

    SCHEMA_MISMATCH = "schema_mismatch"  # Type/structure incompatibility
    CONSTRAINT_VIOLATION = "constraint_violation"  # Cannot meet constraint
    RESOURCE_CONTENTION = "resource_contention"  # Both need exclusive resource
    PRIORITY_CLASH = "priority_clash"  # Conflicting priorities
    TRUST_INSUFFICIENT = "trust_insufficient"  # Trust level too low
    SEMANTIC_AMBIGUITY = "semantic_ambiguity"  # Same term, different meanings


class ConflictSeverity(Enum):
    """Severity levels for conflicts."""

    LOW = "low"  # Minor, auto-resolvable
    MEDIUM = "medium"  # Requires adaptation
    HIGH = "high"  # May require human intervention
    CRITICAL = "critical"  # Blocks negotiation


class ResolutionStrategy(Enum):
    """Strategies for resolving conflicts."""

    TRANSFORM = "transform"  # Convert one format to another
    SUBSET = "subset"  # Use common subset
    MEDIATE = "mediate"  # Third-party mediation
    ESCALATE = "escalate"  # Human decision
    ALTERNATIVE = "alternative"  # Find different capability
    NEGOTIATE_TERMS = "negotiate_terms"  # Adjust terms
    BRIDGE = "bridge"  # Create adapter


class FieldTransformType(Enum):
    """Types of field transformations."""

    COPY = "copy"  # Direct copy
    RENAME = "rename"  # Change field name
    TYPE_COERCE = "type_coerce"  # Convert type (string->int)
    RESTRUCTURE = "restructure"  # Nested -> flat or vice versa
    AGGREGATE = "aggregate"  # Combine multiple fields
    SPLIT = "split"  # Split into multiple fields
    COMPUTE = "compute"  # Derived value
    DEFAULT = "default"  # Use default if missing
    OMIT = "omit"  # Drop field


class DataLossRisk(Enum):
    """Risk levels for data loss during transformation."""

    NONE = "none"  # Lossless transformation
    LOW = "low"  # Minor precision loss
    MEDIUM = "medium"  # Some data may be lost
    HIGH = "high"  # Significant data loss

    def __lt__(self, other: "DataLossRisk") -> bool:
        """Compare risk levels: NONE < LOW < MEDIUM < HIGH."""
        if not isinstance(other, DataLossRisk):
            return NotImplemented
        order = [DataLossRisk.NONE, DataLossRisk.LOW, DataLossRisk.MEDIUM, DataLossRisk.HIGH]
        return order.index(self) < order.index(other)

    def __le__(self, other: "DataLossRisk") -> bool:
        return self == other or self < other

    def __gt__(self, other: "DataLossRisk") -> bool:
        if not isinstance(other, DataLossRisk):
            return NotImplemented
        return other < self

    def __ge__(self, other: "DataLossRisk") -> bool:
        return self == other or self > other


class MediationStyle(Enum):
    """Styles of conflict mediation."""

    FACILITATIVE = "facilitative"  # Help parties find solution
    EVALUATIVE = "evaluative"  # Suggest/evaluate solutions
    TRANSFORMATIVE = "transformative"  # Change relationship dynamics
    DIRECTIVE = "directive"  # Provide binding decision


# ============================================
# Dataclasses
# ============================================


@dataclass
class Conflict:
    """A specific conflict between two negotiating parties."""

    conflict_id: str
    conflict_type: ConflictType
    description: str
    source_element: str
    target_element: str
    severity: ConflictSeverity

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "conflict_id": self.conflict_id,
            "conflict_type": self.conflict_type.value,
            "description": self.description,
            "source_element": self.source_element,
            "target_element": self.target_element,
            "severity": self.severity.value,
        }


@dataclass
class ResolutionStep:
    """A single step in a resolution path."""

    step_number: int
    action: str
    input_type: str
    output_type: str
    reversible: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "step_number": self.step_number,
            "action": self.action,
            "input_type": self.input_type,
            "output_type": self.output_type,
            "reversible": self.reversible,
        }


@dataclass
class ResolutionPath:
    """A possible path to resolve conflicts."""

    path_id: str
    strategy: ResolutionStrategy
    steps: list[ResolutionStep] = field(default_factory=list)
    estimated_success_probability: float = 0.0
    side_effects: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "path_id": self.path_id,
            "strategy": self.strategy.value,
            "steps": [s.to_dict() for s in self.steps],
            "estimated_success_probability": self.estimated_success_probability,
            "side_effects": self.side_effects,
        }


@dataclass
class ConflictAnalysis:
    """Analysis of conflicts between proposals."""

    conflicts: list[Conflict] = field(default_factory=list)
    severity: ConflictSeverity = ConflictSeverity.LOW
    resolvable: bool = True
    resolution_paths: list[ResolutionPath] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "conflicts": [c.to_dict() for c in self.conflicts],
            "severity": self.severity.value,
            "resolvable": self.resolvable,
            "resolution_paths": [p.to_dict() for p in self.resolution_paths],
        }


@dataclass
class FieldTransformation:
    """Transformation for a specific field."""

    source_path: str
    target_path: str
    transform_type: FieldTransformType
    transform_function: str | None = None
    default_value: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "source_path": self.source_path,
            "target_path": self.target_path,
            "transform_type": self.transform_type.value,
        }
        if self.transform_function:
            result["transform_function"] = self.transform_function
        if self.default_value:
            result["default_value"] = self.default_value
        return result


@dataclass
class SchemaTransformPlan:
    """Plan for transforming one schema to another."""

    source_schema: SchemaDefinition
    target_schema: SchemaDefinition
    transformations: list[FieldTransformation] = field(default_factory=list)
    data_loss_risk: DataLossRisk = DataLossRisk.NONE
    reversible: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "source_schema_type": self.source_schema.type.value,
            "target_schema_type": self.target_schema.type.value,
            "transformations": [t.to_dict() for t in self.transformations],
            "data_loss_risk": self.data_loss_risk.value,
            "reversible": self.reversible,
        }


@dataclass
class TransformResult:
    """Result of applying a schema transformation."""

    success: bool
    output_data: str
    warnings: list[str] = field(default_factory=list)
    data_loss_occurred: bool = False
    lost_fields: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "output_data": self.output_data,
            "warnings": self.warnings,
            "data_loss_occurred": self.data_loss_occurred,
            "lost_fields": self.lost_fields,
        }


@dataclass
class MediationRequest:
    """Request for conflict mediation."""

    session_id: str
    conflict: ConflictAnalysis
    party_a_position: dict[str, Any]  # NegotiationProposal as dict
    party_b_position: dict[str, Any]  # NegotiationProposal as dict
    mediation_style: MediationStyle

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "conflict": self.conflict.to_dict(),
            "party_a_position": self.party_a_position,
            "party_b_position": self.party_b_position,
            "mediation_style": self.mediation_style.value,
        }


@dataclass
class MediationResult:
    """Result of conflict mediation."""

    resolved: bool
    compromise_proposal: dict[str, Any] | None = None  # NegotiationProposal as dict
    accepted_by: list[str] = field(default_factory=list)
    remaining_conflicts: list[Conflict] = field(default_factory=list)
    mediator_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "resolved": self.resolved,
            "accepted_by": self.accepted_by,
            "remaining_conflicts": [c.to_dict() for c in self.remaining_conflicts],
            "mediator_notes": self.mediator_notes,
        }
        if self.compromise_proposal:
            result["compromise_proposal"] = self.compromise_proposal
        return result


@dataclass
class DeadlockResolution:
    """Resolution proposal for a negotiation deadlock."""

    resolution_possible: bool
    strategy: ResolutionStrategy
    proposal: dict[str, Any] | None = None  # NegotiationProposal as dict
    explanation: str = ""
    escalation_needed: bool = False
    escalation_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "resolution_possible": self.resolution_possible,
            "strategy": self.strategy.value,
            "explanation": self.explanation,
            "escalation_needed": self.escalation_needed,
        }
        if self.proposal:
            result["proposal"] = self.proposal
        if self.escalation_reason:
            result["escalation_reason"] = self.escalation_reason
        return result


# ============================================
# ConflictDetector Class
# ============================================


class ConflictDetector:
    """
    Detects conflicts between schemas, constraints, and proposals.
    Uses schema analysis to identify incompatibilities.
    """

    # Type coercion safety matrix
    SAFE_COERCIONS = {
        (SchemaType.INTEGER, SchemaType.NUMBER),
        (SchemaType.INTEGER, SchemaType.STRING),
        (SchemaType.NUMBER, SchemaType.STRING),
        (SchemaType.BOOLEAN, SchemaType.STRING),
    }

    def detect_schema_conflicts(
        self,
        source: SchemaDefinition,
        target: SchemaDefinition,
    ) -> list[Conflict]:
        """
        Detect schema incompatibilities between source and target schemas.

        Args:
            source: Source schema definition
            target: Target schema definition

        Returns:
            List of detected conflicts
        """
        conflicts: list[Conflict] = []

        # Root type mismatch
        if source.type != target.type:
            severity = self._assess_type_mismatch_severity(source.type, target.type)
            conflicts.append(
                Conflict(
                    conflict_id=str(uuid.uuid4())[:8],
                    conflict_type=ConflictType.SCHEMA_MISMATCH,
                    description=f"Root type mismatch: {source.type.value} vs {target.type.value}",
                    source_element="root",
                    target_element="root",
                    severity=severity,
                )
            )
            # If root types are incompatible, can't proceed with property comparison
            if severity == ConflictSeverity.CRITICAL:
                return conflicts

        # Property-level conflicts for object types
        if source.type == SchemaType.OBJECT and target.type == SchemaType.OBJECT:
            property_conflicts = self._detect_property_conflicts(source, target)
            conflicts.extend(property_conflicts)

        # Array item conflicts
        if source.type == SchemaType.ARRAY and target.type == SchemaType.ARRAY:
            if source.items and target.items:
                item_conflicts = self.detect_schema_conflicts(
                    source.items, target.items
                )
                # Wrap with array context
                for conflict in item_conflicts:
                    conflict.source_element = f"items.{conflict.source_element}"
                    conflict.target_element = f"items.{conflict.target_element}"
                conflicts.extend(item_conflicts)

        return conflicts

    def detect_constraint_conflicts(
        self,
        required_constraints: list[Any],
        offered_constraints: list[Any],
    ) -> list[Conflict]:
        """
        Detect conflicts between capability constraints.

        Args:
            required_constraints: Constraints from required capability
            offered_constraints: Constraints from offered capability

        Returns:
            List of constraint conflicts
        """
        conflicts: list[Conflict] = []

        # Build constraint lookup by type
        offered_by_type: dict[str, Any] = {}
        for constraint in offered_constraints:
            if hasattr(constraint, "constraint_type"):
                constraint_type = (
                    constraint.constraint_type.value
                    if hasattr(constraint.constraint_type, "value")
                    else str(constraint.constraint_type)
                )
                offered_by_type[constraint_type] = constraint

        # Check each required constraint
        for req_constraint in required_constraints:
            if not hasattr(req_constraint, "constraint_type"):
                continue

            constraint_type = (
                req_constraint.constraint_type.value
                if hasattr(req_constraint.constraint_type, "value")
                else str(req_constraint.constraint_type)
            )

            # Check if constraint is satisfied
            if constraint_type not in offered_by_type:
                conflicts.append(
                    Conflict(
                        conflict_id=str(uuid.uuid4())[:8],
                        conflict_type=ConflictType.CONSTRAINT_VIOLATION,
                        description=f"Required constraint '{constraint_type}' not present in offered capability",
                        source_element=f"constraint.{constraint_type}",
                        target_element="constraints",
                        severity=ConflictSeverity.HIGH,
                    )
                )
            else:
                # Check constraint compatibility (implementation specific)
                offered = offered_by_type[constraint_type]
                if not self._constraints_compatible(req_constraint, offered):
                    conflicts.append(
                        Conflict(
                            conflict_id=str(uuid.uuid4())[:8],
                            conflict_type=ConflictType.CONSTRAINT_VIOLATION,
                            description=f"Constraint '{constraint_type}' values incompatible",
                            source_element=f"constraint.{constraint_type}",
                            target_element=f"constraint.{constraint_type}",
                            severity=ConflictSeverity.MEDIUM,
                        )
                    )

        return conflicts

    def _detect_property_conflicts(
        self, source: SchemaDefinition, target: SchemaDefinition
    ) -> list[Conflict]:
        """Detect property-level conflicts in object schemas."""
        conflicts: list[Conflict] = []

        source_props = {p.name: p for p in (source.properties or [])}
        target_props = {p.name: p for p in (target.properties or [])}
        target_required = set(target.required or [])

        # Check for missing required properties
        for req_name in target_required:
            if req_name not in source_props:
                conflicts.append(
                    Conflict(
                        conflict_id=str(uuid.uuid4())[:8],
                        conflict_type=ConflictType.SCHEMA_MISMATCH,
                        description=f"Required property '{req_name}' missing in source schema",
                        source_element="properties",
                        target_element=req_name,
                        severity=ConflictSeverity.HIGH,
                    )
                )

        # Check for type mismatches in common properties
        for name, target_prop in target_props.items():
            if name in source_props:
                source_prop = source_props[name]
                if source_prop.schema.type != target_prop.schema.type:
                    severity = self._assess_type_mismatch_severity(
                        source_prop.schema.type, target_prop.schema.type
                    )
                    conflicts.append(
                        Conflict(
                            conflict_id=str(uuid.uuid4())[:8],
                            conflict_type=ConflictType.SCHEMA_MISMATCH,
                            description=f"Property '{name}' type mismatch: {source_prop.schema.type.value} vs {target_prop.schema.type.value}",
                            source_element=name,
                            target_element=name,
                            severity=severity,
                        )
                    )

        return conflicts

    def _assess_type_mismatch_severity(
        self, source_type: SchemaType, target_type: SchemaType
    ) -> ConflictSeverity:
        """Assess severity of a type mismatch."""
        # Same type - no conflict
        if source_type == target_type:
            return ConflictSeverity.LOW

        # ANY accepts anything
        if source_type == SchemaType.ANY or target_type == SchemaType.ANY:
            return ConflictSeverity.LOW

        # Safe coercions
        if (source_type, target_type) in self.SAFE_COERCIONS:
            return ConflictSeverity.LOW

        # String can be parsed to most things
        if source_type == SchemaType.STRING:
            return ConflictSeverity.MEDIUM

        # Structural mismatches are critical
        if source_type in {SchemaType.OBJECT, SchemaType.ARRAY} or target_type in {
            SchemaType.OBJECT,
            SchemaType.ARRAY,
        }:
            return ConflictSeverity.CRITICAL

        # Everything else is high severity
        return ConflictSeverity.HIGH

    def _constraints_compatible(self, required: Any, offered: Any) -> bool:
        """Check if two constraints are compatible."""
        # Simplified compatibility check
        # In production, this would need detailed constraint-specific logic
        if hasattr(required, "parameters") and hasattr(offered, "parameters"):
            # For now, just check they have the same parameters
            return True
        return True


# ============================================
# SchemaTransformer Class
# ============================================


class SchemaTransformer:
    """
    Transforms data between incompatible schemas.
    Creates transformation plans and applies them to data.
    """

    def create_plan(
        self,
        source: SchemaDefinition,
        target: SchemaDefinition,
    ) -> SchemaTransformPlan:
        """
        Create a transformation plan from source to target schema.

        Args:
            source: Source schema definition
            target: Target schema definition

        Returns:
            Schema transformation plan
        """
        transformations: list[FieldTransformation] = []
        data_loss_risk = DataLossRisk.NONE
        reversible = True

        # Handle different type transformations
        if source.type != target.type:
            # Type coercion at root level
            transform_func = self._get_coercion_function(source.type, target.type)
            if transform_func:
                transformations.append(
                    FieldTransformation(
                        source_path="$",
                        target_path="$",
                        transform_type=FieldTransformType.TYPE_COERCE,
                        transform_function=transform_func,
                    )
                )
                data_loss_risk = DataLossRisk.MEDIUM
                reversible = False
            else:
                data_loss_risk = DataLossRisk.HIGH
                reversible = False

        # Handle object property transformations
        if source.type == SchemaType.OBJECT and target.type == SchemaType.OBJECT:
            prop_transforms, prop_risk = self._create_property_transforms(
                source, target
            )
            transformations.extend(prop_transforms)
            if prop_risk > data_loss_risk:
                data_loss_risk = prop_risk

        return SchemaTransformPlan(
            source_schema=source,
            target_schema=target,
            transformations=transformations,
            data_loss_risk=data_loss_risk,
            reversible=reversible,
        )

    def apply(
        self, data: dict[str, Any], plan: SchemaTransformPlan
    ) -> TransformResult:
        """
        Apply a transformation plan to data.

        Args:
            data: Input data dictionary
            plan: Transformation plan to apply

        Returns:
            Transformation result with output data
        """
        output: dict[str, Any] = {}
        warnings: list[str] = []
        lost_fields: list[str] = []

        try:
            for transform in plan.transformations:
                try:
                    if transform.transform_type == FieldTransformType.COPY:
                        # Direct copy
                        value = self._get_by_path(data, transform.source_path)
                        self._set_by_path(output, transform.target_path, value)

                    elif transform.transform_type == FieldTransformType.RENAME:
                        # Rename field
                        value = self._get_by_path(data, transform.source_path)
                        self._set_by_path(output, transform.target_path, value)

                    elif transform.transform_type == FieldTransformType.TYPE_COERCE:
                        # Type coercion
                        value = self._get_by_path(data, transform.source_path)
                        coerced = self._coerce_value(
                            value, transform.transform_function
                        )
                        self._set_by_path(output, transform.target_path, coerced)

                    elif transform.transform_type == FieldTransformType.DEFAULT:
                        # Use default value
                        self._set_by_path(
                            output, transform.target_path, transform.default_value
                        )

                    elif transform.transform_type == FieldTransformType.OMIT:
                        # Drop field
                        field_name = self._extract_field_name(transform.source_path)
                        lost_fields.append(field_name)

                except Exception as e:
                    warnings.append(
                        f"Transform failed for {transform.target_path}: {str(e)}"
                    )

            return TransformResult(
                success=len(warnings) == 0,
                output_data=json.dumps(output),
                warnings=warnings,
                data_loss_occurred=plan.data_loss_risk != DataLossRisk.NONE,
                lost_fields=lost_fields,
            )

        except Exception as e:
            return TransformResult(
                success=False,
                output_data=json.dumps({}),
                warnings=[f"Critical transformation error: {str(e)}"],
                data_loss_occurred=True,
                lost_fields=lost_fields,
            )

    def _create_property_transforms(
        self, source: SchemaDefinition, target: SchemaDefinition
    ) -> tuple[list[FieldTransformation], DataLossRisk]:
        """Create transformations for object properties."""
        transformations: list[FieldTransformation] = []
        max_risk = DataLossRisk.NONE

        source_props = {p.name: p for p in (source.properties or [])}
        target_props = {p.name: p for p in (target.properties or [])}

        for target_name, target_prop in target_props.items():
            if target_name in source_props:
                # Direct copy or type coercion
                source_prop = source_props[target_name]
                if source_prop.schema.type == target_prop.schema.type:
                    transformations.append(
                        FieldTransformation(
                            source_path=f"$.{target_name}",
                            target_path=f"$.{target_name}",
                            transform_type=FieldTransformType.COPY,
                        )
                    )
                else:
                    # Type coercion needed
                    transform_func = self._get_coercion_function(
                        source_prop.schema.type, target_prop.schema.type
                    )
                    transformations.append(
                        FieldTransformation(
                            source_path=f"$.{target_name}",
                            target_path=f"$.{target_name}",
                            transform_type=FieldTransformType.TYPE_COERCE,
                            transform_function=transform_func,
                        )
                    )
                    max_risk = DataLossRisk.MEDIUM
            else:
                # Missing property - use default if available
                if target_prop.schema.default_value:
                    transformations.append(
                        FieldTransformation(
                            source_path="",
                            target_path=f"$.{target_name}",
                            transform_type=FieldTransformType.DEFAULT,
                            default_value=target_prop.schema.default_value,
                        )
                    )
                else:
                    max_risk = DataLossRisk.HIGH

        return transformations, max_risk

    def _get_coercion_function(
        self, source_type: SchemaType, target_type: SchemaType
    ) -> str | None:
        """Get the coercion function for type conversion."""
        coercion_map = {
            (SchemaType.INTEGER, SchemaType.NUMBER): "to_float",
            (SchemaType.INTEGER, SchemaType.STRING): "to_string",
            (SchemaType.NUMBER, SchemaType.STRING): "to_string",
            (SchemaType.BOOLEAN, SchemaType.STRING): "to_string",
            (SchemaType.STRING, SchemaType.INTEGER): "parse_int",
            (SchemaType.STRING, SchemaType.NUMBER): "parse_float",
            (SchemaType.STRING, SchemaType.BOOLEAN): "parse_bool",
        }
        return coercion_map.get((source_type, target_type))

    def _get_by_path(self, data: dict[str, Any], path: str) -> Any:
        """Get value from data by JSONPath."""
        if path == "$":
            return data

        # Simple path extraction ($.field)
        field = path.replace("$.", "")
        return data.get(field)

    def _set_by_path(self, data: dict[str, Any], path: str, value: Any) -> None:
        """Set value in data by JSONPath."""
        if path == "$":
            # Can't set root directly
            return

        # Simple path setting ($.field)
        field = path.replace("$.", "")
        data[field] = value

    def _extract_field_name(self, path: str) -> str:
        """Extract field name from JSONPath."""
        return path.replace("$.", "")

    def _coerce_value(self, value: Any, function: str | None) -> Any:
        """Coerce a value using the specified function."""
        if function == "to_float":
            return float(value)
        elif function == "to_string":
            return str(value)
        elif function == "parse_int":
            return int(value)
        elif function == "parse_float":
            return float(value)
        elif function == "parse_bool":
            if isinstance(value, str):
                return value.lower() in {"true", "1", "yes"}
            return bool(value)
        return value


# ============================================
# ConflictMediator Class
# ============================================


class ConflictMediator:
    """
    Mediates conflicts between negotiating parties.
    Generates compromise proposals and facilitates resolution.
    """

    def mediate(self, request: MediationRequest) -> MediationResult:
        """
        Attempt to mediate a conflict between parties.

        Args:
            request: Mediation request with conflict details

        Returns:
            Mediation result with compromise or remaining conflicts
        """
        conflicts = request.conflict.conflicts

        # Sort by severity
        critical = [c for c in conflicts if c.severity == ConflictSeverity.CRITICAL]
        high = [c for c in conflicts if c.severity == ConflictSeverity.HIGH]
        medium = [c for c in conflicts if c.severity == ConflictSeverity.MEDIUM]
        low = [c for c in conflicts if c.severity == ConflictSeverity.LOW]

        # Critical conflicts require manual intervention
        if critical:
            return MediationResult(
                resolved=False,
                remaining_conflicts=critical,
                mediator_notes="Critical conflicts detected. Manual intervention required. "
                + f"Critical issues: {', '.join([c.description for c in critical])}",
            )

        # Try to generate compromise
        compromise = self._generate_compromise(
            request.party_a_position,
            request.party_b_position,
            request.mediation_style,
            high + medium + low,
        )

        if compromise:
            return MediationResult(
                resolved=True,
                compromise_proposal=compromise,
                accepted_by=[],  # Parties need to accept
                remaining_conflicts=high,  # High severity issues remain
                mediator_notes=f"Compromise proposal generated using {request.mediation_style.value} approach. "
                + f"Addressed {len(medium) + len(low)} conflicts. {len(high)} high-severity conflicts remain.",
            )

        return MediationResult(
            resolved=False,
            remaining_conflicts=conflicts,
            mediator_notes=f"Could not find acceptable compromise. {len(conflicts)} unresolved conflicts.",
        )

    def _generate_compromise(
        self,
        position_a: dict[str, Any],
        position_b: dict[str, Any],
        style: MediationStyle,
        conflicts: list[Conflict],
    ) -> dict[str, Any] | None:
        """
        Generate a compromise proposal between two positions.

        Args:
            position_a: First party's position
            position_b: Second party's position
            style: Mediation style to use
            conflicts: List of conflicts to resolve

        Returns:
            Compromise proposal or None if no compromise possible
        """
        # Extract terms from positions
        terms_a = position_a.get("terms", {})
        terms_b = position_b.get("terms", {})

        # Split the difference on duration
        duration_a = terms_a.get("duration_seconds", 3600)
        duration_b = terms_b.get("duration_seconds", 3600)
        compromise_duration = (duration_a + duration_b) // 2

        # Build compromise based on style
        if style == MediationStyle.FACILITATIVE:
            # Help parties find middle ground
            compromise = {
                "proposal_id": str(uuid.uuid4()),
                "requested_capabilities": self._merge_capabilities(
                    position_a.get("requested_capabilities", []),
                    position_b.get("requested_capabilities", []),
                ),
                "offered_capabilities": [],
                "terms": {
                    "duration_seconds": compromise_duration,
                    "auto_renew": False,
                    "termination_conditions": ["mutual agreement", "expiration"],
                },
                "validity_period_seconds": 3600,
            }
            return compromise

        elif style == MediationStyle.EVALUATIVE:
            # Evaluate and suggest optimal solution
            # For now, favor the position with fewer conflicts
            conflicts_a = sum(
                1 for c in conflicts if c.source_element in str(position_a)
            )
            conflicts_b = sum(
                1 for c in conflicts if c.source_element in str(position_b)
            )

            if conflicts_a < conflicts_b:
                return position_a
            else:
                return position_b

        elif style == MediationStyle.DIRECTIVE:
            # Provide binding decision - use middle ground
            compromise = {
                "proposal_id": str(uuid.uuid4()),
                "requested_capabilities": self._intersect_capabilities(
                    position_a.get("requested_capabilities", []),
                    position_b.get("requested_capabilities", []),
                ),
                "offered_capabilities": [],
                "terms": {
                    "duration_seconds": compromise_duration,
                    "auto_renew": False,
                    "termination_conditions": ["expiration"],
                },
                "validity_period_seconds": 3600,
            }
            return compromise

        # Default: no compromise
        return None

    def _merge_capabilities(
        self, caps_a: list[dict[str, Any]], caps_b: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Merge capabilities from both parties."""
        # Union of capabilities
        merged = list(caps_a)
        cap_types_a = {c.get("capability_type") for c in caps_a}
        for cap in caps_b:
            if cap.get("capability_type") not in cap_types_a:
                merged.append(cap)
        return merged

    def _intersect_capabilities(
        self, caps_a: list[dict[str, Any]], caps_b: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Find intersection of capabilities from both parties."""
        cap_types_b = {c.get("capability_type") for c in caps_b}
        return [c for c in caps_a if c.get("capability_type") in cap_types_b]
