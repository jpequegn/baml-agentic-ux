"""Tests for the Coverage Analyzer.

Issue #93 - Task 6.5: Coverage Analyzer
Part of #29 - Phase 6: Conversational Testing Framework
"""

import pytest

from src.testing import (
    ConversationPath,
    ConversationTest,
    CoverageAnalyzer,
    CoverageConfig,
    CoverageGap,
    CoverageLevel,
    CoverageMetric,
    CoverageReport,
    EdgeCase,
    EdgeCaseCoverage,
    EntityCoverage,
    EntityDefinition,
    ExpectedEntity,
    ExpectedOutcome,
    IntentCoverage,
    IntentDefinition,
    PathCoverage,
    SchemaDefinition,
    TestCategory,
    TestPriority,
    TestSuggestion,
    TestTurn,
    TurnRole,
)


# ============================================
# Test Fixtures
# ============================================


def create_sample_schema() -> SchemaDefinition:
    """Create a sample schema for testing."""
    return SchemaDefinition(
        schema_id="test-schema",
        name="Test Schema",
        intents=[
            IntentDefinition(
                intent_id="greeting",
                name="Greeting",
                examples=["hello", "hi", "hey"],
                category="core",
            ),
            IntentDefinition(
                intent_id="booking",
                name="Booking",
                examples=["book a flight", "reserve a seat"],
                required_entities=["destination"],
            ),
            IntentDefinition(
                intent_id="cancel",
                name="Cancel",
                examples=["cancel my booking"],
            ),
        ],
        entities=[
            EntityDefinition(
                entity_id="destination",
                name="Destination",
                entity_type="location",
                examples=["NYC", "LA", "Chicago"],
            ),
            EntityDefinition(
                entity_id="date",
                name="Date",
                entity_type="datetime",
                examples=["tomorrow", "next week"],
            ),
        ],
        paths=[
            ConversationPath(
                path_id="booking-flow",
                name="Booking Flow",
                trigger_intents=["booking"],
                steps=["collect destination", "collect date", "confirm"],
            ),
            ConversationPath(
                path_id="cancel-flow",
                name="Cancel Flow",
                trigger_intents=["cancel"],
                steps=["verify booking", "confirm cancel"],
            ),
        ],
        edge_cases=[
            EdgeCase(
                case_id="invalid-date",
                name="Invalid Date",
                description="User provides invalid date format",
                category="error_handling",
            ),
            EdgeCase(
                case_id="timeout",
                name="Session Timeout",
                description="Session times out during booking",
                category="timeout",
            ),
        ],
    )


def create_sample_tests() -> list[ConversationTest]:
    """Create sample tests for coverage analysis."""
    return [
        ConversationTest(
            test_id="test-greeting",
            name="Greeting Test",
            category=TestCategory.INTENT_RECOGNITION,
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.USER,
                    input="Hello!",
                    expected_intent="greeting",
                ),
            ],
            expected_outcome=ExpectedOutcome(),
        ),
        ConversationTest(
            test_id="test-booking",
            name="Booking Test",
            category=TestCategory.DIALOGUE_FLOW,
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.USER,
                    input="Book a flight to NYC",
                    expected_intent="booking",
                    expected_entities=[
                        ExpectedEntity(entity_type="destination", value="NYC"),
                    ],
                ),
                TestTurn(
                    turn_number=2,
                    role=TurnRole.ASSISTANT,
                    input="I'll help you book a flight to NYC.",
                ),
                TestTurn(
                    turn_number=3,
                    role=TurnRole.USER,
                    input="For tomorrow",
                    expected_entities=[
                        ExpectedEntity(entity_type="date", value="tomorrow"),
                    ],
                ),
            ],
            expected_outcome=ExpectedOutcome(),
        ),
        ConversationTest(
            test_id="test-error",
            name="Error Handling Test",
            category=TestCategory.ERROR_HANDLING,
            tags=["error_handling", "invalid-date"],
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.USER,
                    input="Book for xyz123",
                ),
            ],
            expected_outcome=ExpectedOutcome(),
        ),
    ]


# ============================================
# Schema Type Tests
# ============================================


class TestSchemaTypes:
    """Tests for schema type dataclasses."""

    def test_intent_definition(self) -> None:
        """Test IntentDefinition creation."""
        intent = IntentDefinition(
            intent_id="test",
            name="Test Intent",
            description="A test intent",
            examples=["example 1", "example 2"],
        )
        assert intent.intent_id == "test"
        assert intent.name == "Test Intent"
        assert len(intent.examples) == 2

    def test_entity_definition(self) -> None:
        """Test EntityDefinition creation."""
        entity = EntityDefinition(
            entity_id="location",
            name="Location",
            entity_type="string",
        )
        assert entity.entity_id == "location"
        assert entity.entity_type == "string"

    def test_conversation_path(self) -> None:
        """Test ConversationPath creation."""
        path = ConversationPath(
            path_id="flow-1",
            name="Test Flow",
            trigger_intents=["intent1"],
            steps=["step1", "step2"],
        )
        assert path.path_id == "flow-1"
        assert len(path.steps) == 2

    def test_edge_case(self) -> None:
        """Test EdgeCase creation."""
        case = EdgeCase(
            case_id="edge-1",
            name="Edge Case 1",
            description="Test edge case",
            category="error_handling",
        )
        assert case.case_id == "edge-1"
        assert case.category == "error_handling"

    def test_schema_definition(self) -> None:
        """Test SchemaDefinition creation."""
        schema = create_sample_schema()
        assert schema.schema_id == "test-schema"
        assert len(schema.intents) == 3
        assert len(schema.entities) == 2
        assert len(schema.paths) == 2
        assert len(schema.edge_cases) == 2


# ============================================
# Coverage Config Tests
# ============================================


class TestCoverageConfig:
    """Tests for CoverageConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = CoverageConfig()
        assert config.intent_target == 0.80
        assert config.entity_target == 0.70
        assert config.path_target == 0.60
        assert config.edge_case_target == 0.85
        assert config.generate_suggestions is True

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = CoverageConfig(
            intent_target=0.90,
            entity_target=0.80,
            generate_suggestions=False,
        )
        assert config.intent_target == 0.90
        assert config.entity_target == 0.80
        assert config.generate_suggestions is False


# ============================================
# Coverage Metric Tests
# ============================================


class TestCoverageMetric:
    """Tests for CoverageMetric."""

    def test_metric_creation(self) -> None:
        """Test creating a coverage metric."""
        metric = CoverageMetric(
            name="Test Metric",
            covered=8,
            total=10,
            percentage=80.0,
            target=80.0,
            meets_target=True,
            level=CoverageLevel.GOOD,
            covered_items=["a", "b", "c"],
            uncovered_items=["d", "e"],
        )
        assert metric.covered == 8
        assert metric.total == 10
        assert metric.percentage == 80.0
        assert metric.meets_target is True
        assert metric.level == CoverageLevel.GOOD


class TestCoverageLevel:
    """Tests for CoverageLevel enum."""

    def test_coverage_levels(self) -> None:
        """Test coverage level values."""
        assert CoverageLevel.EXCELLENT.value == "excellent"
        assert CoverageLevel.GOOD.value == "good"
        assert CoverageLevel.ADEQUATE.value == "adequate"
        assert CoverageLevel.LOW.value == "low"
        assert CoverageLevel.CRITICAL.value == "critical"


# ============================================
# Coverage Analyzer Basic Tests
# ============================================


class TestCoverageAnalyzerBasic:
    """Basic tests for CoverageAnalyzer."""

    def test_create_analyzer(self) -> None:
        """Test creating a coverage analyzer."""
        analyzer = CoverageAnalyzer()
        assert analyzer.config is not None
        assert analyzer.config.intent_target == 0.80

    def test_create_analyzer_with_config(self) -> None:
        """Test creating analyzer with custom config."""
        config = CoverageConfig(intent_target=0.95)
        analyzer = CoverageAnalyzer(config)
        assert analyzer.config.intent_target == 0.95


# ============================================
# Coverage Analysis Tests
# ============================================


class TestCoverageAnalysis:
    """Tests for coverage analysis functionality."""

    def test_analyze_full_coverage(self) -> None:
        """Test analyzing coverage with full test suite."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)

        assert report.schema_id == "test-schema"
        assert report.total_tests == 3
        assert report.intent_coverage is not None
        assert report.entity_coverage is not None
        assert report.path_coverage is not None
        assert report.edge_case_coverage is not None

    def test_intent_coverage_calculation(self) -> None:
        """Test intent coverage is calculated correctly."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)

        # We have 3 intents, tests cover greeting and booking (2/3)
        assert report.intent_coverage.metric.total == 3
        assert report.intent_coverage.metric.covered == 2
        assert report.intent_coverage.metric.percentage == pytest.approx(66.67, rel=0.1)

    def test_entity_coverage_calculation(self) -> None:
        """Test entity coverage is calculated correctly."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)

        # We have 2 entities, tests cover destination and date (2/2)
        assert report.entity_coverage.metric.total == 2
        assert report.entity_coverage.metric.covered == 2

    def test_path_coverage_calculation(self) -> None:
        """Test path coverage is calculated correctly."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)

        # Booking test should cover booking-flow path
        assert report.path_coverage.metric.total == 2

    def test_edge_case_coverage_calculation(self) -> None:
        """Test edge case coverage is calculated correctly."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)

        # Error handling test should cover invalid-date edge case
        assert report.edge_case_coverage.metric.total == 2

    def test_overall_score_calculation(self) -> None:
        """Test overall score is calculated."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)

        assert report.overall_score >= 0
        assert report.overall_score <= 100

    def test_empty_tests(self) -> None:
        """Test analysis with no tests."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()

        report = analyzer.analyze_coverage(schema, [])

        assert report.total_tests == 0
        assert report.intent_coverage.metric.covered == 0
        assert report.entity_coverage.metric.covered == 0

    def test_empty_schema(self) -> None:
        """Test analysis with empty schema."""
        analyzer = CoverageAnalyzer()
        schema = SchemaDefinition(schema_id="empty", name="Empty Schema")
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)

        assert report.intent_coverage.metric.total == 0
        assert report.entity_coverage.metric.total == 0


# ============================================
# Gap Identification Tests
# ============================================


class TestGapIdentification:
    """Tests for coverage gap identification."""

    def test_identify_intent_gaps(self) -> None:
        """Test identifying uncovered intents."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)

        # Cancel intent is not covered
        intent_gaps = [g for g in report.gaps if g.gap_type == "intent"]
        assert len(intent_gaps) >= 1
        assert any(g.item_id == "cancel" for g in intent_gaps)

    def test_gap_severity(self) -> None:
        """Test gap severity is set correctly."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)

        for gap in report.gaps:
            assert gap.severity in ("critical", "high", "medium", "low")

    def test_gap_suggestions(self) -> None:
        """Test gaps include suggested tests."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)

        for gap in report.gaps:
            assert gap.suggested_test is not None


# ============================================
# Test Suggestion Tests
# ============================================


class TestTestSuggestions:
    """Tests for test suggestion generation."""

    def test_generate_suggestions(self) -> None:
        """Test suggestions are generated."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)

        if report.gaps:  # Only if there are gaps
            assert len(report.suggestions) > 0

    def test_suggestion_structure(self) -> None:
        """Test suggestion has correct structure."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)

        for suggestion in report.suggestions:
            assert suggestion.suggestion_id is not None
            assert suggestion.gap_id is not None
            assert suggestion.test_name is not None
            assert suggestion.priority in ("high", "medium", "low")

    def test_max_suggestions_limit(self) -> None:
        """Test suggestion count respects max limit."""
        config = CoverageConfig(max_suggestions=2)
        analyzer = CoverageAnalyzer(config)
        schema = create_sample_schema()

        report = analyzer.analyze_coverage(schema, [])

        assert len(report.suggestions) <= 2

    def test_suggestions_disabled(self) -> None:
        """Test suggestions can be disabled."""
        config = CoverageConfig(generate_suggestions=False)
        analyzer = CoverageAnalyzer(config)
        schema = create_sample_schema()

        report = analyzer.analyze_coverage(schema, [])

        assert len(report.suggestions) == 0

    def test_sample_turns_included(self) -> None:
        """Test sample turns are included when configured."""
        config = CoverageConfig(include_sample_turns=True)
        analyzer = CoverageAnalyzer(config)
        schema = create_sample_schema()

        report = analyzer.analyze_coverage(schema, [])

        # Check that at least some suggestions have sample turns
        suggestions_with_turns = [s for s in report.suggestions if s.sample_turns]
        assert len(suggestions_with_turns) > 0


# ============================================
# Report Generation Tests
# ============================================


class TestReportGeneration:
    """Tests for report generation."""

    def test_generate_text_report(self) -> None:
        """Test generating text-based report."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)
        text = analyzer.generate_report_text(report)

        assert "COVERAGE REPORT" in text
        assert "Test Schema" in text
        assert "Intent" in text
        assert "Entity" in text

    def test_generate_dict_report(self) -> None:
        """Test generating dictionary report."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)
        data = analyzer.generate_report_dict(report)

        assert "schema_id" in data
        assert "summary" in data
        assert "metrics" in data
        assert "gaps" in data
        assert "suggestions" in data

    def test_dict_report_metrics(self) -> None:
        """Test dictionary report has correct metrics."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)
        data = analyzer.generate_report_dict(report)

        assert "intent" in data["metrics"]
        assert "entity" in data["metrics"]
        assert "path" in data["metrics"]
        assert "edge_case" in data["metrics"]

        for metric_name in ["intent", "entity", "path", "edge_case"]:
            metric = data["metrics"][metric_name]
            assert "covered" in metric
            assert "total" in metric
            assert "percentage" in metric


# ============================================
# Coverage Level Tests
# ============================================


class TestCoverageLevelClassification:
    """Tests for coverage level classification."""

    def test_excellent_level(self) -> None:
        """Test excellent coverage level (>= 90%)."""
        analyzer = CoverageAnalyzer()
        level = analyzer._get_coverage_level(95.0)
        assert level == CoverageLevel.EXCELLENT

    def test_good_level(self) -> None:
        """Test good coverage level (>= 80%)."""
        analyzer = CoverageAnalyzer()
        level = analyzer._get_coverage_level(85.0)
        assert level == CoverageLevel.GOOD

    def test_adequate_level(self) -> None:
        """Test adequate coverage level (>= 70%)."""
        analyzer = CoverageAnalyzer()
        level = analyzer._get_coverage_level(75.0)
        assert level == CoverageLevel.ADEQUATE

    def test_low_level(self) -> None:
        """Test low coverage level (>= 50%)."""
        analyzer = CoverageAnalyzer()
        level = analyzer._get_coverage_level(55.0)
        assert level == CoverageLevel.LOW

    def test_critical_level(self) -> None:
        """Test critical coverage level (< 50%)."""
        analyzer = CoverageAnalyzer()
        level = analyzer._get_coverage_level(30.0)
        assert level == CoverageLevel.CRITICAL


# ============================================
# Target Checking Tests
# ============================================


class TestTargetChecking:
    """Tests for coverage target checking."""

    def test_meets_all_targets_true(self) -> None:
        """Test when all targets are met."""
        config = CoverageConfig(
            intent_target=0.0,  # Very low targets
            entity_target=0.0,
            path_target=0.0,
            edge_case_target=0.0,
        )
        analyzer = CoverageAnalyzer(config)
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)
        assert report.meets_all_targets is True

    def test_meets_all_targets_false(self) -> None:
        """Test when not all targets are met."""
        config = CoverageConfig(
            intent_target=1.0,  # Impossible target
        )
        analyzer = CoverageAnalyzer(config)
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)
        assert report.meets_all_targets is False


# ============================================
# Edge Cases
# ============================================


class TestEdgeCases:
    """Tests for edge cases in coverage analysis."""

    def test_duplicate_intents_in_tests(self) -> None:
        """Test handling duplicate intent coverage in multiple tests."""
        analyzer = CoverageAnalyzer()
        schema = SchemaDefinition(
            schema_id="test",
            name="Test",
            intents=[IntentDefinition(intent_id="greeting", name="Greeting")],
        )
        tests = [
            ConversationTest(
                test_id="test-1",
                name="Test 1",
                turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hi", expected_intent="greeting")],
                expected_outcome=ExpectedOutcome(),
            ),
            ConversationTest(
                test_id="test-2",
                name="Test 2",
                turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hello", expected_intent="greeting")],
                expected_outcome=ExpectedOutcome(),
            ),
        ]

        report = analyzer.analyze_coverage(schema, tests)

        # Should still only count as 1 covered intent
        assert report.intent_coverage.metric.covered == 1
        # But should track test count
        assert report.intent_coverage.intent_test_counts.get("greeting", 0) == 2

    def test_unknown_intent_in_tests(self) -> None:
        """Test handling intents in tests not in schema."""
        analyzer = CoverageAnalyzer()
        schema = SchemaDefinition(
            schema_id="test",
            name="Test",
            intents=[IntentDefinition(intent_id="greeting", name="Greeting")],
        )
        tests = [
            ConversationTest(
                test_id="test-1",
                name="Test 1",
                turns=[TestTurn(turn_number=1, role=TurnRole.USER, input="Hi", expected_intent="unknown")],
                expected_outcome=ExpectedOutcome(),
            ),
        ]

        report = analyzer.analyze_coverage(schema, tests)

        # Unknown intent should not count toward coverage
        assert report.intent_coverage.metric.covered == 0

    def test_assertion_count(self) -> None:
        """Test total assertion count is correct."""
        analyzer = CoverageAnalyzer()
        schema = create_sample_schema()
        tests = create_sample_tests()

        report = analyzer.analyze_coverage(schema, tests)

        # Count assertions manually
        total = sum(len(turn.assertions) for test in tests for turn in test.turns)
        assert report.total_assertions == total
