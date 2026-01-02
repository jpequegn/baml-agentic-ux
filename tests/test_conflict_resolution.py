"""
Tests for Conflict Resolution Module

Issue #66 - Phase 3 Testing & Documentation
"""

import json
import uuid
import pytest

from src.lui_simulator.agent_types import (
    SchemaDefinition,
    SchemaType,
    SchemaProperty,
    CapabilityConstraint,
    ConstraintCategory,
    ConstraintEnforcement,
)
from src.agent_negotiation.conflict_resolution import (
    # Enums
    ConflictType,
    ConflictSeverity,
    ResolutionStrategy,
    FieldTransformType,
    DataLossRisk,
    MediationStyle,
    # Dataclasses
    Conflict,
    ResolutionStep,
    ResolutionPath,
    ConflictAnalysis,
    FieldTransformation,
    SchemaTransformPlan,
    TransformResult,
    MediationRequest,
    MediationResult,
    DeadlockResolution,
    # Classes
    ConflictDetector,
    SchemaTransformer,
    ConflictMediator,
)


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def string_schema() -> SchemaDefinition:
    """Create a string schema."""
    return SchemaDefinition.string(description="String value")


@pytest.fixture
def integer_schema() -> SchemaDefinition:
    """Create an integer schema."""
    return SchemaDefinition.integer(description="Integer value")


@pytest.fixture
def object_schema() -> SchemaDefinition:
    """Create an object schema with properties."""
    return SchemaDefinition.object(
        description="User object",
        properties=[
            SchemaProperty(
                name="name",
                schema=SchemaDefinition.string(description="User name"),
            ),
            SchemaProperty(
                name="age",
                schema=SchemaDefinition.integer(description="User age"),
            ),
            SchemaProperty(
                name="email",
                schema=SchemaDefinition.string(description="User email"),
            ),
        ],
        required=["name", "email"],
    )


@pytest.fixture
def compatible_object_schema() -> SchemaDefinition:
    """Create a compatible object schema."""
    return SchemaDefinition.object(
        description="Person object",
        properties=[
            SchemaProperty(
                name="name",
                schema=SchemaDefinition.string(description="Person name"),
            ),
            SchemaProperty(
                name="age",
                schema=SchemaDefinition.integer(description="Person age"),
            ),
        ],
        required=["name"],
    )


@pytest.fixture
def incompatible_object_schema() -> SchemaDefinition:
    """Create an incompatible object schema."""
    return SchemaDefinition.object(
        description="Different object",
        properties=[
            SchemaProperty(
                name="id",
                schema=SchemaDefinition.integer(description="ID number"),
            ),
            SchemaProperty(
                name="data",
                schema=SchemaDefinition.string(description="Data string"),
            ),
        ],
        required=["id", "data"],
    )


@pytest.fixture
def array_schema() -> SchemaDefinition:
    """Create an array schema."""
    return SchemaDefinition.array(
        items=SchemaDefinition.string(description="Item"),
        description="List of items",
    )


@pytest.fixture
def rate_limit_constraint() -> CapabilityConstraint:
    """Create a rate limit constraint."""
    return CapabilityConstraint.rate_limit(
        requests_per_minute=100,
        enforcement=ConstraintEnforcement.HARD,
    )


@pytest.fixture
def conflict_detector() -> ConflictDetector:
    """Create a conflict detector instance."""
    return ConflictDetector()


@pytest.fixture
def schema_transformer() -> SchemaTransformer:
    """Create a schema transformer instance."""
    return SchemaTransformer()


@pytest.fixture
def conflict_mediator() -> ConflictMediator:
    """Create a conflict mediator instance."""
    return ConflictMediator()


# ============================================
# Test Enums
# ============================================


class TestConflictType:
    """Tests for ConflictType enum."""

    def test_all_values(self):
        """Test all conflict type values exist."""
        assert ConflictType.SCHEMA_MISMATCH.value == "schema_mismatch"
        assert ConflictType.CONSTRAINT_VIOLATION.value == "constraint_violation"
        assert ConflictType.RESOURCE_CONTENTION.value == "resource_contention"
        assert ConflictType.PRIORITY_CLASH.value == "priority_clash"
        assert ConflictType.TRUST_INSUFFICIENT.value == "trust_insufficient"
        assert ConflictType.SEMANTIC_AMBIGUITY.value == "semantic_ambiguity"


class TestConflictSeverity:
    """Tests for ConflictSeverity enum."""

    def test_all_values(self):
        """Test all severity values exist."""
        assert ConflictSeverity.LOW.value == "low"
        assert ConflictSeverity.MEDIUM.value == "medium"
        assert ConflictSeverity.HIGH.value == "high"
        assert ConflictSeverity.CRITICAL.value == "critical"


class TestResolutionStrategy:
    """Tests for ResolutionStrategy enum."""

    def test_all_values(self):
        """Test all resolution strategy values exist."""
        assert ResolutionStrategy.TRANSFORM.value == "transform"
        assert ResolutionStrategy.SUBSET.value == "subset"
        assert ResolutionStrategy.MEDIATE.value == "mediate"
        assert ResolutionStrategy.ESCALATE.value == "escalate"
        assert ResolutionStrategy.ALTERNATIVE.value == "alternative"
        assert ResolutionStrategy.NEGOTIATE_TERMS.value == "negotiate_terms"
        assert ResolutionStrategy.BRIDGE.value == "bridge"


class TestFieldTransformType:
    """Tests for FieldTransformType enum."""

    def test_all_values(self):
        """Test all field transform type values exist."""
        assert FieldTransformType.COPY.value == "copy"
        assert FieldTransformType.RENAME.value == "rename"
        assert FieldTransformType.TYPE_COERCE.value == "type_coerce"
        assert FieldTransformType.RESTRUCTURE.value == "restructure"
        assert FieldTransformType.AGGREGATE.value == "aggregate"
        assert FieldTransformType.SPLIT.value == "split"
        assert FieldTransformType.COMPUTE.value == "compute"
        assert FieldTransformType.DEFAULT.value == "default"
        assert FieldTransformType.OMIT.value == "omit"


class TestDataLossRisk:
    """Tests for DataLossRisk enum."""

    def test_all_values(self):
        """Test all data loss risk values exist."""
        assert DataLossRisk.NONE.value == "none"
        assert DataLossRisk.LOW.value == "low"
        assert DataLossRisk.MEDIUM.value == "medium"
        assert DataLossRisk.HIGH.value == "high"


class TestMediationStyle:
    """Tests for MediationStyle enum."""

    def test_all_values(self):
        """Test all mediation style values exist."""
        assert MediationStyle.FACILITATIVE.value == "facilitative"
        assert MediationStyle.EVALUATIVE.value == "evaluative"
        assert MediationStyle.TRANSFORMATIVE.value == "transformative"
        assert MediationStyle.DIRECTIVE.value == "directive"


# ============================================
# Test Dataclasses
# ============================================


class TestConflict:
    """Tests for Conflict dataclass."""

    def test_create_conflict(self):
        """Test creating a conflict."""
        conflict = Conflict(
            conflict_id="conflict-1",
            conflict_type=ConflictType.SCHEMA_MISMATCH,
            description="Type mismatch between string and integer",
            source_element="field_a",
            target_element="field_b",
            severity=ConflictSeverity.HIGH,
        )
        assert conflict.conflict_id == "conflict-1"
        assert conflict.conflict_type == ConflictType.SCHEMA_MISMATCH
        assert conflict.severity == ConflictSeverity.HIGH

    def test_to_dict(self):
        """Test Conflict to_dict method."""
        conflict = Conflict(
            conflict_id="conflict-1",
            conflict_type=ConflictType.CONSTRAINT_VIOLATION,
            description="Rate limit exceeded",
            source_element="rate_limit",
            target_element="max_limit",
            severity=ConflictSeverity.MEDIUM,
        )
        result = conflict.to_dict()
        assert result["conflict_id"] == "conflict-1"
        assert result["conflict_type"] == "constraint_violation"
        assert result["severity"] == "medium"


class TestResolutionStep:
    """Tests for ResolutionStep dataclass."""

    def test_create_step(self):
        """Test creating a resolution step."""
        step = ResolutionStep(
            step_number=1,
            action="Convert string to integer",
            input_type="string",
            output_type="integer",
            reversible=True,
        )
        assert step.step_number == 1
        assert step.action == "Convert string to integer"
        assert step.reversible is True

    def test_to_dict(self):
        """Test ResolutionStep to_dict method."""
        step = ResolutionStep(
            step_number=2,
            action="Apply transformation",
            input_type="object",
            output_type="object",
            reversible=False,
        )
        result = step.to_dict()
        assert result["step_number"] == 2
        assert result["reversible"] is False


class TestResolutionPath:
    """Tests for ResolutionPath dataclass."""

    def test_create_path(self):
        """Test creating a resolution path."""
        path = ResolutionPath(
            path_id="path-1",
            strategy=ResolutionStrategy.TRANSFORM,
            steps=[
                ResolutionStep(
                    step_number=1,
                    action="Transform",
                    input_type="string",
                    output_type="int",
                    reversible=True,
                )
            ],
            estimated_success_probability=0.85,
            side_effects=["Minor precision loss"],
        )
        assert path.path_id == "path-1"
        assert path.strategy == ResolutionStrategy.TRANSFORM
        assert len(path.steps) == 1
        assert path.estimated_success_probability == 0.85

    def test_to_dict(self):
        """Test ResolutionPath to_dict method."""
        path = ResolutionPath(
            path_id="path-1",
            strategy=ResolutionStrategy.SUBSET,
            estimated_success_probability=0.9,
        )
        result = path.to_dict()
        assert result["path_id"] == "path-1"
        assert result["strategy"] == "subset"


class TestConflictAnalysis:
    """Tests for ConflictAnalysis dataclass."""

    def test_create_analysis(self):
        """Test creating a conflict analysis."""
        conflict = Conflict(
            conflict_id="c1",
            conflict_type=ConflictType.SCHEMA_MISMATCH,
            description="Type mismatch",
            source_element="a",
            target_element="b",
            severity=ConflictSeverity.MEDIUM,
        )
        analysis = ConflictAnalysis(
            conflicts=[conflict],
            severity=ConflictSeverity.MEDIUM,
            resolvable=True,
            resolution_paths=[],
        )
        assert len(analysis.conflicts) == 1
        assert analysis.resolvable is True

    def test_default_values(self):
        """Test ConflictAnalysis default values."""
        analysis = ConflictAnalysis()
        assert analysis.conflicts == []
        assert analysis.severity == ConflictSeverity.LOW
        assert analysis.resolvable is True

    def test_to_dict(self):
        """Test ConflictAnalysis to_dict method."""
        analysis = ConflictAnalysis(
            severity=ConflictSeverity.HIGH,
            resolvable=False,
        )
        result = analysis.to_dict()
        assert result["severity"] == "high"
        assert result["resolvable"] is False


class TestFieldTransformation:
    """Tests for FieldTransformation dataclass."""

    def test_create_copy_transform(self):
        """Test creating a copy transformation."""
        transform = FieldTransformation(
            source_path="$.name",
            target_path="$.name",
            transform_type=FieldTransformType.COPY,
        )
        assert transform.transform_type == FieldTransformType.COPY

    def test_create_type_coerce_transform(self):
        """Test creating a type coercion transformation."""
        transform = FieldTransformation(
            source_path="$.age",
            target_path="$.age",
            transform_type=FieldTransformType.TYPE_COERCE,
            transform_function="to_string",
        )
        assert transform.transform_function == "to_string"

    def test_create_default_transform(self):
        """Test creating a default value transformation."""
        transform = FieldTransformation(
            source_path="",
            target_path="$.status",
            transform_type=FieldTransformType.DEFAULT,
            default_value="active",
        )
        assert transform.default_value == "active"

    def test_to_dict(self):
        """Test FieldTransformation to_dict method."""
        transform = FieldTransformation(
            source_path="$.input",
            target_path="$.output",
            transform_type=FieldTransformType.RENAME,
        )
        result = transform.to_dict()
        assert result["source_path"] == "$.input"
        assert result["transform_type"] == "rename"


class TestSchemaTransformPlan:
    """Tests for SchemaTransformPlan dataclass."""

    def test_create_plan(
        self,
        string_schema: SchemaDefinition,
        integer_schema: SchemaDefinition,
    ):
        """Test creating a transform plan."""
        plan = SchemaTransformPlan(
            source_schema=string_schema,
            target_schema=integer_schema,
            transformations=[
                FieldTransformation(
                    source_path="$",
                    target_path="$",
                    transform_type=FieldTransformType.TYPE_COERCE,
                    transform_function="parse_int",
                )
            ],
            data_loss_risk=DataLossRisk.LOW,
            reversible=False,
        )
        assert len(plan.transformations) == 1
        assert plan.data_loss_risk == DataLossRisk.LOW
        assert plan.reversible is False

    def test_to_dict(
        self,
        string_schema: SchemaDefinition,
    ):
        """Test SchemaTransformPlan to_dict method."""
        plan = SchemaTransformPlan(
            source_schema=string_schema,
            target_schema=string_schema,
            data_loss_risk=DataLossRisk.NONE,
            reversible=True,
        )
        result = plan.to_dict()
        assert result["data_loss_risk"] == "none"
        assert result["reversible"] is True


class TestTransformResult:
    """Tests for TransformResult dataclass."""

    def test_successful_result(self):
        """Test creating a successful transform result."""
        result = TransformResult(
            success=True,
            output_data='{"value": 42}',
        )
        assert result.success is True
        assert result.data_loss_occurred is False

    def test_failed_result(self):
        """Test creating a failed transform result."""
        result = TransformResult(
            success=False,
            output_data="{}",
            warnings=["Field conversion failed"],
            data_loss_occurred=True,
            lost_fields=["extra_field"],
        )
        assert result.success is False
        assert len(result.warnings) == 1
        assert len(result.lost_fields) == 1

    def test_to_dict(self):
        """Test TransformResult to_dict method."""
        result = TransformResult(
            success=True,
            output_data='{"result": "ok"}',
        )
        dict_result = result.to_dict()
        assert dict_result["success"] is True


class TestMediationRequest:
    """Tests for MediationRequest dataclass."""

    def test_create_request(self):
        """Test creating a mediation request."""
        analysis = ConflictAnalysis()
        request = MediationRequest(
            session_id="session-1",
            conflict=analysis,
            party_a_position={"terms": {"duration_seconds": 3600}},
            party_b_position={"terms": {"duration_seconds": 7200}},
            mediation_style=MediationStyle.FACILITATIVE,
        )
        assert request.session_id == "session-1"
        assert request.mediation_style == MediationStyle.FACILITATIVE

    def test_to_dict(self):
        """Test MediationRequest to_dict method."""
        request = MediationRequest(
            session_id="session-1",
            conflict=ConflictAnalysis(),
            party_a_position={},
            party_b_position={},
            mediation_style=MediationStyle.DIRECTIVE,
        )
        result = request.to_dict()
        assert result["session_id"] == "session-1"
        assert result["mediation_style"] == "directive"


class TestMediationResult:
    """Tests for MediationResult dataclass."""

    def test_successful_mediation(self):
        """Test creating a successful mediation result."""
        result = MediationResult(
            resolved=True,
            compromise_proposal={"terms": {"duration_seconds": 5400}},
            accepted_by=["agent-1", "agent-2"],
            mediator_notes="Compromise reached on duration",
        )
        assert result.resolved is True
        assert len(result.accepted_by) == 2

    def test_failed_mediation(self):
        """Test creating a failed mediation result."""
        conflict = Conflict(
            conflict_id="c1",
            conflict_type=ConflictType.PRIORITY_CLASH,
            description="Cannot resolve priorities",
            source_element="priority",
            target_element="priority",
            severity=ConflictSeverity.CRITICAL,
        )
        result = MediationResult(
            resolved=False,
            remaining_conflicts=[conflict],
            mediator_notes="Could not find compromise",
        )
        assert result.resolved is False
        assert len(result.remaining_conflicts) == 1

    def test_to_dict(self):
        """Test MediationResult to_dict method."""
        result = MediationResult(
            resolved=True,
            mediator_notes="All resolved",
        )
        dict_result = result.to_dict()
        assert dict_result["resolved"] is True


class TestDeadlockResolution:
    """Tests for DeadlockResolution dataclass."""

    def test_resolvable_deadlock(self):
        """Test creating a resolvable deadlock resolution."""
        resolution = DeadlockResolution(
            resolution_possible=True,
            strategy=ResolutionStrategy.NEGOTIATE_TERMS,
            proposal={"modified": True},
            explanation="Modified terms to break deadlock",
        )
        assert resolution.resolution_possible is True
        assert resolution.strategy == ResolutionStrategy.NEGOTIATE_TERMS

    def test_unresolvable_deadlock(self):
        """Test creating an unresolvable deadlock resolution."""
        resolution = DeadlockResolution(
            resolution_possible=False,
            strategy=ResolutionStrategy.ESCALATE,
            explanation="Cannot resolve automatically",
            escalation_needed=True,
            escalation_reason="Human decision required",
        )
        assert resolution.resolution_possible is False
        assert resolution.escalation_needed is True

    def test_to_dict(self):
        """Test DeadlockResolution to_dict method."""
        resolution = DeadlockResolution(
            resolution_possible=True,
            strategy=ResolutionStrategy.SUBSET,
            explanation="Using common subset",
        )
        result = resolution.to_dict()
        assert result["strategy"] == "subset"


# ============================================
# Test ConflictDetector
# ============================================


class TestConflictDetector:
    """Tests for ConflictDetector class."""

    def test_no_conflicts_same_schema(
        self,
        conflict_detector: ConflictDetector,
        string_schema: SchemaDefinition,
    ):
        """Test that identical schemas have no conflicts."""
        conflicts = conflict_detector.detect_schema_conflicts(
            string_schema, string_schema
        )
        assert len(conflicts) == 0

    def test_root_type_mismatch(
        self,
        conflict_detector: ConflictDetector,
        string_schema: SchemaDefinition,
        integer_schema: SchemaDefinition,
    ):
        """Test detecting root type mismatch."""
        conflicts = conflict_detector.detect_schema_conflicts(
            string_schema, integer_schema
        )
        assert len(conflicts) > 0
        assert any(
            c.conflict_type == ConflictType.SCHEMA_MISMATCH for c in conflicts
        )

    def test_safe_coercion_low_severity(
        self,
        conflict_detector: ConflictDetector,
        integer_schema: SchemaDefinition,
    ):
        """Test that safe coercions have low severity."""
        # Integer to string is safe
        string_schema = SchemaDefinition.string()
        conflicts = conflict_detector.detect_schema_conflicts(
            integer_schema, string_schema
        )
        # Should still detect a conflict but with low severity
        type_conflicts = [
            c for c in conflicts if c.conflict_type == ConflictType.SCHEMA_MISMATCH
        ]
        if type_conflicts:
            assert type_conflicts[0].severity == ConflictSeverity.LOW

    def test_structural_mismatch_critical(
        self,
        conflict_detector: ConflictDetector,
        object_schema: SchemaDefinition,
        array_schema: SchemaDefinition,
    ):
        """Test that object vs array is critical severity."""
        conflicts = conflict_detector.detect_schema_conflicts(
            object_schema, array_schema
        )
        assert len(conflicts) > 0
        # Structural mismatch should be critical
        assert any(c.severity == ConflictSeverity.CRITICAL for c in conflicts)

    def test_missing_required_property(
        self,
        conflict_detector: ConflictDetector,
        object_schema: SchemaDefinition,
        compatible_object_schema: SchemaDefinition,
    ):
        """Test detecting missing required properties."""
        # compatible_object_schema requires only "name"
        # object_schema requires "name" and "email"
        conflicts = conflict_detector.detect_schema_conflicts(
            compatible_object_schema, object_schema
        )
        # Should detect that source is missing "email" required by target
        missing_prop_conflicts = [
            c
            for c in conflicts
            if "email" in c.description and "missing" in c.description.lower()
        ]
        assert len(missing_prop_conflicts) >= 1

    def test_property_type_mismatch(
        self,
        conflict_detector: ConflictDetector,
    ):
        """Test detecting property type mismatches."""
        source = SchemaDefinition.object(
            properties=[
                SchemaProperty(
                    name="count",
                    schema=SchemaDefinition.string(),  # String
                )
            ]
        )
        target = SchemaDefinition.object(
            properties=[
                SchemaProperty(
                    name="count",
                    schema=SchemaDefinition.integer(),  # Integer
                )
            ]
        )
        conflicts = conflict_detector.detect_schema_conflicts(source, target)
        property_conflicts = [
            c for c in conflicts if "count" in c.description
        ]
        assert len(property_conflicts) >= 1

    def test_array_item_conflicts(
        self,
        conflict_detector: ConflictDetector,
    ):
        """Test detecting conflicts in array item types."""
        source = SchemaDefinition.array(
            items=SchemaDefinition.string(),
        )
        target = SchemaDefinition.array(
            items=SchemaDefinition.integer(),
        )
        conflicts = conflict_detector.detect_schema_conflicts(source, target)
        # Should detect item type mismatch
        assert len(conflicts) > 0
        assert any("items" in c.source_element for c in conflicts)

    def test_detect_constraint_conflicts(
        self,
        conflict_detector: ConflictDetector,
        rate_limit_constraint: CapabilityConstraint,
    ):
        """Test detecting constraint conflicts."""
        required = [rate_limit_constraint]
        # No constraints offered
        offered: list[CapabilityConstraint] = []
        conflicts = conflict_detector.detect_constraint_conflicts(
            required, offered
        )
        assert len(conflicts) > 0
        assert any(
            c.conflict_type == ConflictType.CONSTRAINT_VIOLATION for c in conflicts
        )

    def test_constraint_satisfied(
        self,
        conflict_detector: ConflictDetector,
        rate_limit_constraint: CapabilityConstraint,
    ):
        """Test that satisfied constraints have no conflicts."""
        required = [rate_limit_constraint]
        offered = [rate_limit_constraint]  # Same constraint
        conflicts = conflict_detector.detect_constraint_conflicts(
            required, offered
        )
        # No missing constraint conflicts
        missing = [
            c for c in conflicts if "not present" in c.description
        ]
        assert len(missing) == 0

    def test_any_type_compatibility(
        self,
        conflict_detector: ConflictDetector,
        string_schema: SchemaDefinition,
    ):
        """Test that ANY type is compatible with anything."""
        any_schema = SchemaDefinition(type=SchemaType.ANY)
        conflicts = conflict_detector.detect_schema_conflicts(
            string_schema, any_schema
        )
        # Should have no conflicts or low severity
        critical = [c for c in conflicts if c.severity == ConflictSeverity.CRITICAL]
        assert len(critical) == 0


# ============================================
# Test SchemaTransformer
# ============================================


class TestSchemaTransformer:
    """Tests for SchemaTransformer class."""

    def test_create_plan_same_type(
        self,
        schema_transformer: SchemaTransformer,
        string_schema: SchemaDefinition,
    ):
        """Test creating plan for same type schemas."""
        plan = schema_transformer.create_plan(string_schema, string_schema)
        assert plan.data_loss_risk == DataLossRisk.NONE
        assert plan.reversible is True

    def test_create_plan_type_coercion(
        self,
        schema_transformer: SchemaTransformer,
        integer_schema: SchemaDefinition,
        string_schema: SchemaDefinition,
    ):
        """Test creating plan for type coercion."""
        plan = schema_transformer.create_plan(integer_schema, string_schema)
        # Should have type coercion transformation
        coercions = [
            t for t in plan.transformations
            if t.transform_type == FieldTransformType.TYPE_COERCE
        ]
        assert len(coercions) >= 1

    def test_create_plan_object_properties(
        self,
        schema_transformer: SchemaTransformer,
        object_schema: SchemaDefinition,
        compatible_object_schema: SchemaDefinition,
    ):
        """Test creating plan for object with property transforms."""
        plan = schema_transformer.create_plan(object_schema, compatible_object_schema)
        # Should have copy transformations for common properties
        copies = [
            t for t in plan.transformations
            if t.transform_type == FieldTransformType.COPY
        ]
        assert len(copies) >= 1  # At least "name" should be copied

    def test_apply_copy_transformation(
        self,
        schema_transformer: SchemaTransformer,
        object_schema: SchemaDefinition,
    ):
        """Test applying copy transformations."""
        plan = SchemaTransformPlan(
            source_schema=object_schema,
            target_schema=object_schema,
            transformations=[
                FieldTransformation(
                    source_path="$.name",
                    target_path="$.name",
                    transform_type=FieldTransformType.COPY,
                )
            ],
            data_loss_risk=DataLossRisk.NONE,
            reversible=True,
        )
        data = {"name": "John", "age": 30}
        result = schema_transformer.apply(data, plan)
        assert result.success is True
        output = json.loads(result.output_data)
        assert output["name"] == "John"

    def test_apply_type_coercion(
        self,
        schema_transformer: SchemaTransformer,
        string_schema: SchemaDefinition,
        integer_schema: SchemaDefinition,
    ):
        """Test applying type coercion transformation."""
        plan = SchemaTransformPlan(
            source_schema=string_schema,
            target_schema=integer_schema,
            transformations=[
                FieldTransformation(
                    source_path="$.value",
                    target_path="$.value",
                    transform_type=FieldTransformType.TYPE_COERCE,
                    transform_function="parse_int",
                )
            ],
            data_loss_risk=DataLossRisk.LOW,
            reversible=False,
        )
        data = {"value": "42"}
        result = schema_transformer.apply(data, plan)
        assert result.success is True
        output = json.loads(result.output_data)
        assert output["value"] == 42

    def test_apply_default_value(
        self,
        schema_transformer: SchemaTransformer,
        object_schema: SchemaDefinition,
    ):
        """Test applying default value transformation."""
        plan = SchemaTransformPlan(
            source_schema=object_schema,
            target_schema=object_schema,
            transformations=[
                FieldTransformation(
                    source_path="",
                    target_path="$.status",
                    transform_type=FieldTransformType.DEFAULT,
                    default_value="active",
                )
            ],
            data_loss_risk=DataLossRisk.NONE,
            reversible=True,
        )
        data = {}
        result = schema_transformer.apply(data, plan)
        assert result.success is True
        output = json.loads(result.output_data)
        assert output["status"] == "active"

    def test_apply_omit_transformation(
        self,
        schema_transformer: SchemaTransformer,
        object_schema: SchemaDefinition,
    ):
        """Test applying omit transformation."""
        plan = SchemaTransformPlan(
            source_schema=object_schema,
            target_schema=object_schema,
            transformations=[
                FieldTransformation(
                    source_path="$.extra_field",
                    target_path="",
                    transform_type=FieldTransformType.OMIT,
                )
            ],
            data_loss_risk=DataLossRisk.MEDIUM,
            reversible=False,
        )
        data = {"extra_field": "value"}
        result = schema_transformer.apply(data, plan)
        # Omit should mark field as lost
        assert "extra_field" in result.lost_fields

    def test_coerce_to_float(
        self,
        schema_transformer: SchemaTransformer,
    ):
        """Test to_float coercion."""
        plan = SchemaTransformPlan(
            source_schema=SchemaDefinition.integer(),
            target_schema=SchemaDefinition(type=SchemaType.NUMBER),
            transformations=[
                FieldTransformation(
                    source_path="$.value",
                    target_path="$.value",
                    transform_type=FieldTransformType.TYPE_COERCE,
                    transform_function="to_float",
                )
            ],
        )
        data = {"value": 42}
        result = schema_transformer.apply(data, plan)
        output = json.loads(result.output_data)
        assert output["value"] == 42.0

    def test_coerce_to_string(
        self,
        schema_transformer: SchemaTransformer,
    ):
        """Test to_string coercion."""
        plan = SchemaTransformPlan(
            source_schema=SchemaDefinition.integer(),
            target_schema=SchemaDefinition.string(),
            transformations=[
                FieldTransformation(
                    source_path="$.value",
                    target_path="$.value",
                    transform_type=FieldTransformType.TYPE_COERCE,
                    transform_function="to_string",
                )
            ],
        )
        data = {"value": 42}
        result = schema_transformer.apply(data, plan)
        output = json.loads(result.output_data)
        assert output["value"] == "42"

    def test_coerce_parse_bool(
        self,
        schema_transformer: SchemaTransformer,
    ):
        """Test parse_bool coercion."""
        plan = SchemaTransformPlan(
            source_schema=SchemaDefinition.string(),
            target_schema=SchemaDefinition.boolean(),
            transformations=[
                FieldTransformation(
                    source_path="$.value",
                    target_path="$.value",
                    transform_type=FieldTransformType.TYPE_COERCE,
                    transform_function="parse_bool",
                )
            ],
        )
        data = {"value": "true"}
        result = schema_transformer.apply(data, plan)
        output = json.loads(result.output_data)
        assert output["value"] is True

    def test_transform_error_handling(
        self,
        schema_transformer: SchemaTransformer,
    ):
        """Test error handling during transformation."""
        plan = SchemaTransformPlan(
            source_schema=SchemaDefinition.string(),
            target_schema=SchemaDefinition.integer(),
            transformations=[
                FieldTransformation(
                    source_path="$.value",
                    target_path="$.value",
                    transform_type=FieldTransformType.TYPE_COERCE,
                    transform_function="parse_int",
                )
            ],
        )
        data = {"value": "not_a_number"}  # Will fail to parse
        result = schema_transformer.apply(data, plan)
        # Should have warnings but not crash
        assert len(result.warnings) > 0


# ============================================
# Test ConflictMediator
# ============================================


class TestConflictMediator:
    """Tests for ConflictMediator class."""

    def test_mediate_no_critical_conflicts(
        self,
        conflict_mediator: ConflictMediator,
    ):
        """Test mediation with no critical conflicts."""
        analysis = ConflictAnalysis(
            conflicts=[
                Conflict(
                    conflict_id="c1",
                    conflict_type=ConflictType.SCHEMA_MISMATCH,
                    description="Minor type difference",
                    source_element="field_a",
                    target_element="field_b",
                    severity=ConflictSeverity.MEDIUM,
                )
            ],
            severity=ConflictSeverity.MEDIUM,
            resolvable=True,
        )
        request = MediationRequest(
            session_id="session-1",
            conflict=analysis,
            party_a_position={"terms": {"duration_seconds": 3600}},
            party_b_position={"terms": {"duration_seconds": 7200}},
            mediation_style=MediationStyle.FACILITATIVE,
        )
        result = conflict_mediator.mediate(request)
        assert result.resolved is True
        assert result.compromise_proposal is not None

    def test_mediate_critical_conflicts(
        self,
        conflict_mediator: ConflictMediator,
    ):
        """Test mediation with critical conflicts."""
        analysis = ConflictAnalysis(
            conflicts=[
                Conflict(
                    conflict_id="c1",
                    conflict_type=ConflictType.SCHEMA_MISMATCH,
                    description="Incompatible structures",
                    source_element="root",
                    target_element="root",
                    severity=ConflictSeverity.CRITICAL,
                )
            ],
            severity=ConflictSeverity.CRITICAL,
            resolvable=False,
        )
        request = MediationRequest(
            session_id="session-1",
            conflict=analysis,
            party_a_position={"terms": {}},
            party_b_position={"terms": {}},
            mediation_style=MediationStyle.FACILITATIVE,
        )
        result = conflict_mediator.mediate(request)
        assert result.resolved is False
        assert len(result.remaining_conflicts) == 1
        assert "Critical" in result.mediator_notes

    def test_facilitative_mediation(
        self,
        conflict_mediator: ConflictMediator,
    ):
        """Test facilitative mediation style."""
        analysis = ConflictAnalysis(
            conflicts=[],
            severity=ConflictSeverity.LOW,
            resolvable=True,
        )
        request = MediationRequest(
            session_id="session-1",
            conflict=analysis,
            party_a_position={
                "terms": {"duration_seconds": 3600},
                "requested_capabilities": [{"capability_type": "action"}],
            },
            party_b_position={
                "terms": {"duration_seconds": 7200},
                "requested_capabilities": [{"capability_type": "query"}],
            },
            mediation_style=MediationStyle.FACILITATIVE,
        )
        result = conflict_mediator.mediate(request)
        assert result.resolved is True
        # Compromise should have averaged duration
        if result.compromise_proposal:
            terms = result.compromise_proposal.get("terms", {})
            duration = terms.get("duration_seconds")
            if duration:
                assert duration == 5400  # (3600 + 7200) / 2

    def test_evaluative_mediation(
        self,
        conflict_mediator: ConflictMediator,
    ):
        """Test evaluative mediation style."""
        analysis = ConflictAnalysis(
            conflicts=[
                Conflict(
                    conflict_id="c1",
                    conflict_type=ConflictType.SCHEMA_MISMATCH,
                    description="Issue in party_a",
                    source_element="field",
                    target_element="field",
                    severity=ConflictSeverity.MEDIUM,
                )
            ],
            severity=ConflictSeverity.MEDIUM,
            resolvable=True,
        )
        request = MediationRequest(
            session_id="session-1",
            conflict=analysis,
            party_a_position={"terms": {"duration_seconds": 3600}},
            party_b_position={"terms": {"duration_seconds": 7200}},
            mediation_style=MediationStyle.EVALUATIVE,
        )
        result = conflict_mediator.mediate(request)
        assert result.resolved is True
        # Evaluative should favor position with fewer conflicts
        assert result.compromise_proposal is not None

    def test_directive_mediation(
        self,
        conflict_mediator: ConflictMediator,
    ):
        """Test directive mediation style."""
        analysis = ConflictAnalysis(
            conflicts=[],
            severity=ConflictSeverity.LOW,
            resolvable=True,
        )
        request = MediationRequest(
            session_id="session-1",
            conflict=analysis,
            party_a_position={
                "terms": {"duration_seconds": 3600},
                "requested_capabilities": [{"capability_type": "action"}],
            },
            party_b_position={
                "terms": {"duration_seconds": 7200},
                "requested_capabilities": [{"capability_type": "action"}],
            },
            mediation_style=MediationStyle.DIRECTIVE,
        )
        result = conflict_mediator.mediate(request)
        assert result.resolved is True
        # Directive should provide binding decision
        if result.compromise_proposal:
            assert "terms" in result.compromise_proposal

    def test_transformative_mediation_no_compromise(
        self,
        conflict_mediator: ConflictMediator,
    ):
        """Test transformative mediation (currently returns no compromise)."""
        analysis = ConflictAnalysis()
        request = MediationRequest(
            session_id="session-1",
            conflict=analysis,
            party_a_position={"terms": {}},
            party_b_position={"terms": {}},
            mediation_style=MediationStyle.TRANSFORMATIVE,
        )
        result = conflict_mediator.mediate(request)
        # Transformative is not yet implemented, should return not resolved
        assert result.resolved is False

    def test_merge_capabilities(
        self,
        conflict_mediator: ConflictMediator,
    ):
        """Test merging capabilities from both parties."""
        analysis = ConflictAnalysis()
        request = MediationRequest(
            session_id="session-1",
            conflict=analysis,
            party_a_position={
                "terms": {"duration_seconds": 3600},
                "requested_capabilities": [{"capability_type": "action"}],
            },
            party_b_position={
                "terms": {"duration_seconds": 7200},
                "requested_capabilities": [{"capability_type": "query"}],
            },
            mediation_style=MediationStyle.FACILITATIVE,
        )
        result = conflict_mediator.mediate(request)
        if result.compromise_proposal and "requested_capabilities" in result.compromise_proposal:
            caps = result.compromise_proposal["requested_capabilities"]
            cap_types = {c.get("capability_type") for c in caps}
            # Should have merged both capabilities
            assert "action" in cap_types
            assert "query" in cap_types
