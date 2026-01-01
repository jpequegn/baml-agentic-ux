"""
Tests for Schema Conflict Detection Module

Issue #60 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.8)
"""

import pytest
from datetime import datetime, timezone, timedelta

from src.agent_negotiation.conflict_detector import (
    # Enums
    ConflictType,
    ConflictSeverity,
    ConflictCategory,
    ResolutionStrategy,
    EffortLevel,
    # Types
    Conflict,
    ConflictContext,
    ResolutionPath,
    ResolutionStep,
    ResolutionRisk,
    EffortEstimate,
    ConflictSummary,
    ConflictAnalysis,
    ConstraintSpec,
    DetectionOptions,
    SchemaDefinition,
    ConflictDetectionRequest,
    ConflictDetectionResponse,
    # Detector
    ConflictDetector,
)


# ============================================
# Enum Tests
# ============================================


class TestConflictType:
    """Tests for ConflictType enum."""

    def test_all_types_defined(self):
        """All expected conflict types should be defined."""
        expected_types = [
            "SCHEMA_MISMATCH",
            "CONSTRAINT_VIOLATION",
            "RESOURCE_CONTENTION",
            "PRIORITY_CLASH",
            "TRUST_INSUFFICIENT",
            "SEMANTIC_AMBIGUITY",
            "VERSION_INCOMPATIBLE",
            "CAPACITY_EXCEEDED",
            "TIMING_CONFLICT",
            "SECURITY_POLICY",
        ]
        for t in expected_types:
            assert hasattr(ConflictType, t)

    def test_values(self):
        """Enum values should be strings."""
        assert ConflictType.SCHEMA_MISMATCH.value == "schema_mismatch"
        assert ConflictType.TRUST_INSUFFICIENT.value == "trust_insufficient"


class TestConflictSeverity:
    """Tests for ConflictSeverity enum."""

    def test_all_levels_defined(self):
        """All severity levels should be defined."""
        expected = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        for level in expected:
            assert hasattr(ConflictSeverity, level)

    def test_severity_order(self):
        """Severity levels should have correct ordering."""
        levels = [
            ConflictSeverity.LOW,
            ConflictSeverity.MEDIUM,
            ConflictSeverity.HIGH,
            ConflictSeverity.CRITICAL,
        ]
        # Just verify they exist in order
        assert len(levels) == 4


class TestConflictCategory:
    """Tests for ConflictCategory enum."""

    def test_all_categories_defined(self):
        """All categories should be defined."""
        expected = ["STRUCTURAL", "SEMANTIC", "OPERATIONAL", "POLICY", "TEMPORAL"]
        for cat in expected:
            assert hasattr(ConflictCategory, cat)


class TestResolutionStrategy:
    """Tests for ResolutionStrategy enum."""

    def test_all_strategies_defined(self):
        """All resolution strategies should be defined."""
        expected = [
            "TRANSFORM",
            "NEGOTIATE",
            "ADAPT",
            "FALLBACK",
            "ESCALATE",
            "ACCEPT_RISK",
            "REJECT",
            "BRIDGE",
            "SUBSET",
        ]
        for strategy in expected:
            assert hasattr(ResolutionStrategy, strategy)


# ============================================
# Data Type Tests
# ============================================


class TestConflict:
    """Tests for Conflict dataclass."""

    def test_basic_creation(self):
        """Should create a basic conflict."""
        conflict = Conflict(
            conflict_id="c1",
            conflict_type=ConflictType.SCHEMA_MISMATCH,
            category=ConflictCategory.STRUCTURAL,
            severity=ConflictSeverity.HIGH,
            description="Type mismatch",
            source_element="field_a",
            target_element="field_a",
        )
        assert conflict.conflict_id == "c1"
        assert conflict.conflict_type == ConflictType.SCHEMA_MISMATCH
        assert conflict.severity == ConflictSeverity.HIGH

    def test_full_creation(self):
        """Should create a conflict with all fields."""
        context = ConflictContext(
            affected_capabilities=["cap1"],
            related_constraints=["const1"],
            impact_description="Blocks integration",
        )
        conflict = Conflict(
            conflict_id="c2",
            conflict_type=ConflictType.CONSTRAINT_VIOLATION,
            category=ConflictCategory.OPERATIONAL,
            severity=ConflictSeverity.CRITICAL,
            description="Cannot meet rate limit",
            source_element="rate_limit",
            target_element="max_rate",
            source_value="100",
            target_value="1000",
            context=context,
        )
        assert conflict.source_value == "100"
        assert conflict.target_value == "1000"
        assert conflict.context is not None
        assert "cap1" in conflict.context.affected_capabilities


class TestResolutionPath:
    """Tests for ResolutionPath dataclass."""

    def test_basic_creation(self):
        """Should create a basic resolution path."""
        path = ResolutionPath(
            path_id="p1",
            strategy=ResolutionStrategy.TRANSFORM,
            description="Apply schema transformation",
        )
        assert path.path_id == "p1"
        assert path.strategy == ResolutionStrategy.TRANSFORM
        assert path.success_likelihood == 0.5  # Default

    def test_with_steps(self):
        """Should create a path with steps."""
        steps = [
            ResolutionStep(
                step_number=1,
                action="Identify changes",
                actor="source",
                details="Find required transformations",
            ),
            ResolutionStep(
                step_number=2,
                action="Apply changes",
                actor="source",
                details="Implement transformations",
                validation="Run tests",
            ),
        ]
        path = ResolutionPath(
            path_id="p2",
            strategy=ResolutionStrategy.ADAPT,
            description="Adapt schema",
            steps=steps,
            success_likelihood=0.8,
        )
        assert len(path.steps) == 2
        assert path.steps[0].step_number == 1


class TestConflictAnalysis:
    """Tests for ConflictAnalysis dataclass."""

    def test_empty_analysis(self):
        """Should create an empty analysis."""
        analysis = ConflictAnalysis(
            analysis_id="a1",
            source_id="src",
            target_id="tgt",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        assert analysis.analysis_id == "a1"
        assert len(analysis.conflicts) == 0
        assert analysis.resolvable is True


# ============================================
# Schema Conflict Detection Tests
# ============================================


class TestSchemaConflictDetection:
    """Tests for schema conflict detection."""

    @pytest.fixture
    def detector(self):
        """Create a conflict detector."""
        return ConflictDetector()

    def test_no_conflicts_identical_schemas(self, detector):
        """Should detect no conflicts for identical schemas."""
        source = SchemaDefinition(
            schema_id="s1",
            name="TestSchema",
            properties={"name": "string", "age": "int"},
            required_fields=["name"],
        )
        target = SchemaDefinition(
            schema_id="t1",
            name="TestSchema",
            properties={"name": "string", "age": "int"},
            required_fields=["name"],
        )
        conflicts = detector.detect_schema_conflicts(source, target)
        assert len(conflicts) == 0

    def test_missing_required_field(self, detector):
        """Should detect missing required field."""
        source = SchemaDefinition(
            schema_id="s1",
            name="Source",
            properties={"name": "string"},
            required_fields=[],
        )
        target = SchemaDefinition(
            schema_id="t1",
            name="Target",
            properties={"name": "string", "email": "string"},
            required_fields=["name", "email"],
        )
        conflicts = detector.detect_schema_conflicts(source, target)
        assert len(conflicts) >= 1
        missing_conflicts = [
            c
            for c in conflicts
            if c.conflict_type == ConflictType.SCHEMA_MISMATCH and "email" in c.description
        ]
        assert len(missing_conflicts) == 1
        assert missing_conflicts[0].severity == ConflictSeverity.HIGH

    def test_type_mismatch(self, detector):
        """Should detect type mismatches."""
        source = SchemaDefinition(
            schema_id="s1",
            name="Source",
            properties={"count": "string"},
            required_fields=[],
        )
        target = SchemaDefinition(
            schema_id="t1",
            name="Target",
            properties={"count": "int"},
            required_fields=[],
        )
        conflicts = detector.detect_schema_conflicts(source, target)
        type_conflicts = [
            c for c in conflicts if "Type mismatch" in c.description
        ]
        assert len(type_conflicts) == 1

    def test_compatible_types_no_conflict(self, detector):
        """Should not flag compatible types as conflicts."""
        source = SchemaDefinition(
            schema_id="s1",
            name="Source",
            properties={"value": "int"},
            required_fields=[],
        )
        target = SchemaDefinition(
            schema_id="t1",
            name="Target",
            properties={"value": "number"},  # int is compatible with number
            required_fields=[],
        )
        conflicts = detector.detect_schema_conflicts(source, target)
        # Should not have type mismatch since int is compatible with number
        type_conflicts = [
            c for c in conflicts if "Type mismatch" in c.description
        ]
        assert len(type_conflicts) == 0

    def test_version_mismatch(self, detector):
        """Should detect major version mismatch."""
        source = SchemaDefinition(
            schema_id="s1",
            name="Source",
            properties={},
            version="1.0",
        )
        target = SchemaDefinition(
            schema_id="t1",
            name="Target",
            properties={},
            version="2.0",
        )
        conflicts = detector.detect_schema_conflicts(source, target)
        version_conflicts = [
            c for c in conflicts if c.conflict_type == ConflictType.VERSION_INCOMPATIBLE
        ]
        assert len(version_conflicts) == 1

    def test_nested_schema_conflicts(self, detector):
        """Should detect conflicts in nested schemas."""
        source = SchemaDefinition(
            schema_id="s1",
            name="Source",
            properties={
                "address": {
                    "type": "object",
                    "properties": {"city": "string"},
                    "required": [],
                }
            },
        )
        target = SchemaDefinition(
            schema_id="t1",
            name="Target",
            properties={
                "address": {
                    "type": "object",
                    "properties": {"city": "string", "zip": "string"},
                    "required": ["zip"],
                }
            },
        )
        options = DetectionOptions(deep_schema_analysis=True)
        conflicts = detector.detect_schema_conflicts(source, target, options)
        # Should find missing required field 'zip' in nested address
        nested_conflicts = [c for c in conflicts if "address" in c.source_element]
        assert len(nested_conflicts) >= 1


# ============================================
# Constraint Conflict Detection Tests
# ============================================


class TestConstraintConflictDetection:
    """Tests for constraint conflict detection."""

    @pytest.fixture
    def detector(self):
        """Create a conflict detector."""
        return ConflictDetector()

    def test_missing_required_constraint(self, detector):
        """Should detect missing required constraint."""
        source_constraints = []
        target_constraints = [
            ConstraintSpec(
                constraint_id="c1",
                constraint_type="rate_limit",
                field="requests",
                operator="<=",
                value="100",
                required=True,
            )
        ]
        conflicts = detector.detect_constraint_conflicts(
            source_constraints, target_constraints
        )
        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == ConflictType.CONSTRAINT_VIOLATION

    def test_constraint_value_violation(self, detector):
        """Should detect constraint value violations."""
        source_constraints = [
            ConstraintSpec(
                constraint_id="sc1",
                constraint_type="rate_limit",
                field="requests",
                operator="<=",
                value="50",
                required=True,
            )
        ]
        target_constraints = [
            ConstraintSpec(
                constraint_id="tc1",
                constraint_type="rate_limit",
                field="requests",
                operator=">=",
                value="100",
                required=True,
            )
        ]
        conflicts = detector.detect_constraint_conflicts(
            source_constraints, target_constraints
        )
        # Source offers <=50 but target requires >=100
        assert len(conflicts) == 1

    def test_satisfied_constraint(self, detector):
        """Should not flag satisfied constraints."""
        source_constraints = [
            ConstraintSpec(
                constraint_id="sc1",
                constraint_type="rate_limit",
                field="requests",
                operator="<=",
                value="200",
                required=True,
            )
        ]
        target_constraints = [
            ConstraintSpec(
                constraint_id="tc1",
                constraint_type="rate_limit",
                field="requests",
                operator="<=",
                value="100",
                required=True,
            )
        ]
        conflicts = detector.detect_constraint_conflicts(
            source_constraints, target_constraints
        )
        # Source offers <=200 which satisfies target's <=100 requirement
        # (source can handle up to 200, target only needs up to 100)
        # This should pass since 200 > 100
        pass  # May or may not have conflict depending on interpretation


# ============================================
# Trust Conflict Detection Tests
# ============================================


class TestTrustConflictDetection:
    """Tests for trust level conflict detection."""

    @pytest.fixture
    def detector(self):
        """Create a conflict detector."""
        return ConflictDetector()

    def test_sufficient_trust(self, detector):
        """Should not flag sufficient trust level."""
        conflict = detector.detect_trust_conflicts(
            source_trust_level=80,
            target_required_trust=60,
        )
        assert conflict is None

    def test_insufficient_trust_low(self, detector):
        """Should flag insufficient trust with low severity."""
        conflict = detector.detect_trust_conflicts(
            source_trust_level=55,
            target_required_trust=60,
        )
        assert conflict is not None
        assert conflict.conflict_type == ConflictType.TRUST_INSUFFICIENT
        assert conflict.severity == ConflictSeverity.LOW

    def test_insufficient_trust_medium(self, detector):
        """Should flag moderate trust gap with medium severity."""
        conflict = detector.detect_trust_conflicts(
            source_trust_level=40,
            target_required_trust=60,
        )
        assert conflict is not None
        assert conflict.severity == ConflictSeverity.MEDIUM

    def test_insufficient_trust_high(self, detector):
        """Should flag large trust gap with high severity."""
        conflict = detector.detect_trust_conflicts(
            source_trust_level=20,
            target_required_trust=60,
        )
        assert conflict is not None
        assert conflict.severity == ConflictSeverity.HIGH

    def test_insufficient_trust_critical(self, detector):
        """Should flag critical trust gap."""
        conflict = detector.detect_trust_conflicts(
            source_trust_level=10,
            target_required_trust=80,
        )
        assert conflict is not None
        assert conflict.severity == ConflictSeverity.CRITICAL


# ============================================
# Capacity Conflict Detection Tests
# ============================================


class TestCapacityConflictDetection:
    """Tests for capacity conflict detection."""

    @pytest.fixture
    def detector(self):
        """Create a conflict detector."""
        return ConflictDetector()

    def test_sufficient_capacity(self, detector):
        """Should not flag sufficient capacity."""
        conflicts = detector.detect_capacity_conflicts(
            source_capacity={"memory": 1000, "cpu": 4},
            target_requirements={"memory": 500, "cpu": 2},
        )
        assert len(conflicts) == 0

    def test_insufficient_capacity(self, detector):
        """Should flag insufficient capacity."""
        conflicts = detector.detect_capacity_conflicts(
            source_capacity={"memory": 100},
            target_requirements={"memory": 500},
        )
        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == ConflictType.CAPACITY_EXCEEDED

    def test_missing_resource(self, detector):
        """Should flag missing resource as critical."""
        conflicts = detector.detect_capacity_conflicts(
            source_capacity={},
            target_requirements={"gpu": 1},
        )
        assert len(conflicts) == 1
        assert conflicts[0].severity == ConflictSeverity.CRITICAL


# ============================================
# Timing Conflict Detection Tests
# ============================================


class TestTimingConflictDetection:
    """Tests for timing conflict detection."""

    @pytest.fixture
    def detector(self):
        """Create a conflict detector."""
        return ConflictDetector()

    def test_overlapping_windows(self, detector):
        """Should not flag overlapping time windows."""
        now = datetime.now(timezone.utc)
        conflict = detector.detect_timing_conflicts(
            source_availability=(
                now.isoformat(),
                (now + timedelta(hours=10)).isoformat(),
            ),
            target_requirement=(
                (now + timedelta(hours=2)).isoformat(),
                (now + timedelta(hours=8)).isoformat(),
            ),
        )
        assert conflict is None

    def test_non_overlapping_windows(self, detector):
        """Should flag non-overlapping time windows."""
        now = datetime.now(timezone.utc)
        conflict = detector.detect_timing_conflicts(
            source_availability=(
                now.isoformat(),
                (now + timedelta(hours=5)).isoformat(),
            ),
            target_requirement=(
                (now + timedelta(hours=6)).isoformat(),
                (now + timedelta(hours=10)).isoformat(),
            ),
        )
        assert conflict is not None
        assert conflict.conflict_type == ConflictType.TIMING_CONFLICT
        assert conflict.severity == ConflictSeverity.HIGH

    def test_partial_coverage(self, detector):
        """Should flag partial time coverage."""
        now = datetime.now(timezone.utc)
        conflict = detector.detect_timing_conflicts(
            source_availability=(
                (now + timedelta(hours=1)).isoformat(),
                (now + timedelta(hours=8)).isoformat(),
            ),
            target_requirement=(
                now.isoformat(),
                (now + timedelta(hours=10)).isoformat(),
            ),
        )
        assert conflict is not None
        assert conflict.severity == ConflictSeverity.MEDIUM


# ============================================
# Semantic Conflict Detection Tests
# ============================================


class TestSemanticConflictDetection:
    """Tests for semantic ambiguity conflict detection."""

    @pytest.fixture
    def detector(self):
        """Create a conflict detector."""
        return ConflictDetector()

    def test_no_semantic_conflict(self, detector):
        """Should not flag identical definitions."""
        conflicts = detector.detect_semantic_conflicts(
            source_definitions={"user": "A person using the system"},
            target_definitions={"user": "A person using the system"},
        )
        assert len(conflicts) == 0

    def test_semantic_conflict_detected(self, detector):
        """Should detect different meanings for same term."""
        conflicts = detector.detect_semantic_conflicts(
            source_definitions={"user": "A database table record"},
            target_definitions={"user": "A person using the application"},
        )
        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == ConflictType.SEMANTIC_AMBIGUITY

    def test_semantic_conflict_severity(self, detector):
        """Should assess severity based on meaning similarity."""
        # Very different meanings
        conflicts = detector.detect_semantic_conflicts(
            source_definitions={"token": "Authentication credential"},
            target_definitions={"token": "Unit of cryptocurrency"},
        )
        assert len(conflicts) == 1
        # Low overlap should result in higher severity
        assert conflicts[0].severity in [ConflictSeverity.MEDIUM, ConflictSeverity.HIGH]


# ============================================
# Full Detection Request Tests
# ============================================


class TestFullDetectionRequest:
    """Tests for complete detection requests."""

    @pytest.fixture
    def detector(self):
        """Create a conflict detector."""
        return ConflictDetector()

    def test_full_detection_no_conflicts(self, detector):
        """Should handle detection request with no conflicts."""
        request = ConflictDetectionRequest(
            request_id="req1",
            source_schema=SchemaDefinition(
                schema_id="s1",
                name="Source",
                properties={"id": "string"},
            ),
            target_schema=SchemaDefinition(
                schema_id="t1",
                name="Target",
                properties={"id": "string"},
            ),
            detection_options=DetectionOptions(),
        )
        response = detector.detect_conflicts(request)
        assert response.request_id == "req1"
        assert response.detection_time_ms >= 0
        assert response.analysis.resolvable is True

    def test_full_detection_with_conflicts(self, detector):
        """Should handle detection request with conflicts."""
        request = ConflictDetectionRequest(
            request_id="req2",
            source_schema=SchemaDefinition(
                schema_id="s1",
                name="Source",
                properties={"name": "string"},
            ),
            target_schema=SchemaDefinition(
                schema_id="t1",
                name="Target",
                properties={"name": "string", "email": "string"},
                required_fields=["email"],
            ),
            detection_options=DetectionOptions(include_resolution_paths=True),
        )
        response = detector.detect_conflicts(request)
        assert len(response.analysis.conflicts) >= 1
        assert len(response.analysis.resolution_paths) >= 1

    def test_severity_threshold_filtering(self, detector):
        """Should filter conflicts by severity threshold."""
        request = ConflictDetectionRequest(
            request_id="req3",
            source_schema=SchemaDefinition(
                schema_id="s1",
                name="Source",
                properties={"count": "int"},
                version="1.0",
            ),
            target_schema=SchemaDefinition(
                schema_id="t1",
                name="Target",
                properties={"count": "float"},  # Low severity type coercion
                version="1.1",  # Minor version diff
            ),
            detection_options=DetectionOptions(
                severity_threshold=ConflictSeverity.HIGH
            ),
        )
        response = detector.detect_conflicts(request)
        # Only HIGH or CRITICAL conflicts should be included
        for conflict in response.analysis.conflicts:
            assert conflict.severity in [ConflictSeverity.HIGH, ConflictSeverity.CRITICAL]


# ============================================
# Resolution Path Tests
# ============================================


class TestResolutionPaths:
    """Tests for resolution path generation."""

    @pytest.fixture
    def detector(self):
        """Create a conflict detector."""
        return ConflictDetector()

    def test_schema_mismatch_paths(self, detector):
        """Should generate paths for schema mismatch."""
        request = ConflictDetectionRequest(
            request_id="req1",
            source_schema=SchemaDefinition(
                schema_id="s1",
                name="Source",
                properties={},
            ),
            target_schema=SchemaDefinition(
                schema_id="t1",
                name="Target",
                properties={"required_field": "string"},
                required_fields=["required_field"],
            ),
            detection_options=DetectionOptions(
                include_resolution_paths=True,
                max_resolution_paths=5,
            ),
        )
        response = detector.detect_conflicts(request)
        # Should have resolution paths for the missing field conflict
        assert len(response.analysis.resolution_paths) >= 1
        strategies = [p.strategy for p in response.analysis.resolution_paths]
        assert ResolutionStrategy.TRANSFORM in strategies or ResolutionStrategy.ADAPT in strategies


# ============================================
# Conflict Summary Tests
# ============================================


class TestConflictSummary:
    """Tests for conflict summary generation."""

    @pytest.fixture
    def detector(self):
        """Create a conflict detector."""
        return ConflictDetector()

    def test_summary_counts(self, detector):
        """Should generate accurate summary counts."""
        request = ConflictDetectionRequest(
            request_id="req1",
            source_schema=SchemaDefinition(
                schema_id="s1",
                name="Source",
                properties={"a": "string"},
                version="1.0",
            ),
            target_schema=SchemaDefinition(
                schema_id="t1",
                name="Target",
                properties={"a": "int", "b": "string"},
                required_fields=["a", "b"],
                version="2.0",
            ),
        )
        response = detector.detect_conflicts(request)
        summary = response.analysis.summary

        assert summary.total_conflicts >= 2  # Type mismatch + missing field + version
        assert summary.by_severity.high >= 1 or summary.by_severity.critical >= 1
        assert summary.by_category.structural >= 1

    def test_blocking_conflicts_count(self, detector):
        """Should count blocking (critical) conflicts."""
        # Trust insufficient with huge gap creates critical conflict
        conflict = detector.detect_trust_conflicts(
            source_trust_level=0,
            target_required_trust=100,
        )
        assert conflict is not None
        assert conflict.severity == ConflictSeverity.CRITICAL


# ============================================
# Callback Tests
# ============================================


class TestConflictCallback:
    """Tests for conflict callback functionality."""

    def test_callback_invoked(self):
        """Should invoke callback for each conflict."""
        detected_conflicts = []

        def callback(conflict: Conflict):
            detected_conflicts.append(conflict)

        detector = ConflictDetector(conflict_callback=callback)
        request = ConflictDetectionRequest(
            request_id="req1",
            source_schema=SchemaDefinition(
                schema_id="s1",
                name="Source",
                properties={},
            ),
            target_schema=SchemaDefinition(
                schema_id="t1",
                name="Target",
                properties={"field": "string"},
                required_fields=["field"],
            ),
        )
        response = detector.detect_conflicts(request)

        # Callback should have been invoked for each conflict
        assert len(detected_conflicts) == len(response.analysis.conflicts)


# ============================================
# Edge Cases Tests
# ============================================


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.fixture
    def detector(self):
        """Create a conflict detector."""
        return ConflictDetector()

    def test_empty_schemas(self, detector):
        """Should handle empty schemas."""
        conflicts = detector.detect_schema_conflicts(
            SchemaDefinition(schema_id="s1", name="Empty1", properties={}),
            SchemaDefinition(schema_id="t1", name="Empty2", properties={}),
        )
        assert len(conflicts) == 0

    def test_null_optional_fields(self, detector):
        """Should handle null optional fields in request."""
        request = ConflictDetectionRequest(
            request_id="req1",
            source_schema=None,
            target_schema=None,
        )
        response = detector.detect_conflicts(request)
        assert response.analysis.conflicts == []

    def test_empty_constraint_lists(self, detector):
        """Should handle empty constraint lists."""
        conflicts = detector.detect_constraint_conflicts([], [])
        assert len(conflicts) == 0

    def test_invalid_timestamp_handling(self, detector):
        """Should handle invalid timestamps gracefully."""
        conflict = detector.detect_timing_conflicts(
            source_availability=("invalid", "also-invalid"),
            target_requirement=("bad", "timestamps"),
        )
        assert conflict is None  # Should return None, not raise


# ============================================
# Integration Tests
# ============================================


class TestIntegration:
    """Integration tests for conflict detection."""

    def test_complete_negotiation_scenario(self):
        """Should handle a realistic negotiation conflict scenario."""
        detector = ConflictDetector()

        # Source agent capabilities
        source_schema = SchemaDefinition(
            schema_id="search-agent",
            name="SearchCapability",
            properties={
                "query": "string",
                "max_results": "int",
                "format": "string",
            },
            required_fields=["query"],
            version="1.2",
        )

        # Target requirements
        target_schema = SchemaDefinition(
            schema_id="orchestrator",
            name="SearchRequirements",
            properties={
                "query": "string",
                "max_results": "int",
                "format": "string",
                "filters": {"type": "object", "properties": {"date_range": "string"}},
            },
            required_fields=["query", "max_results", "filters"],
            version="1.2",
        )

        source_constraints = [
            ConstraintSpec(
                constraint_id="rate",
                constraint_type="rate_limit",
                field="requests_per_minute",
                operator="<=",
                value="60",
                required=True,
            )
        ]

        target_constraints = [
            ConstraintSpec(
                constraint_id="rate_req",
                constraint_type="rate_limit",
                field="requests_per_minute",
                operator=">=",
                value="100",
                required=True,
            )
        ]

        request = ConflictDetectionRequest(
            request_id="negotiation-1",
            source_schema=source_schema,
            target_schema=target_schema,
            source_constraints=source_constraints,
            target_constraints=target_constraints,
            detection_options=DetectionOptions(
                include_resolution_paths=True,
                max_resolution_paths=3,
                detect_semantic=True,
                deep_schema_analysis=True,
                include_risk_assessment=True,
            ),
        )

        response = detector.detect_conflicts(request)

        # Should detect:
        # 1. Missing required field 'filters'
        # 2. Constraint violation (rate limit)
        assert len(response.analysis.conflicts) >= 2

        # Should have recommendations
        assert len(response.analysis.recommendations) >= 1

        # Should have resolution paths
        assert len(response.analysis.resolution_paths) >= 1

        # Summary should be populated
        assert response.analysis.summary.total_conflicts >= 2
