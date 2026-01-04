"""Coverage Analyzer for Conversational Testing.

This module provides coverage analysis for conversation tests.

Issue #93 - Task 6.5: Coverage Analyzer
Part of #29 - Phase 6: Conversational Testing Framework
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .types import (
    ConversationTest,
    TestCategory,
    TestSuite,
    TestTurn,
    TurnRole,
)


# ============================================
# Schema Types for Coverage Analysis
# ============================================


@dataclass
class IntentDefinition:
    """Definition of an intent in the schema."""

    intent_id: str
    name: str
    description: Optional[str] = None
    examples: list[str] = field(default_factory=list)
    required_entities: list[str] = field(default_factory=list)
    category: Optional[str] = None


@dataclass
class EntityDefinition:
    """Definition of an entity type in the schema."""

    entity_id: str
    name: str
    entity_type: str
    description: Optional[str] = None
    examples: list[str] = field(default_factory=list)
    validations: list[str] = field(default_factory=list)


@dataclass
class ConversationPath:
    """Definition of a conversation path/flow."""

    path_id: str
    name: str
    description: Optional[str] = None
    trigger_intents: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)
    outcomes: list[str] = field(default_factory=list)


@dataclass
class EdgeCase:
    """Definition of an edge case to test."""

    case_id: str
    name: str
    description: str
    category: str  # error_handling, boundary, invalid_input, timeout, etc.
    test_scenario: Optional[str] = None


@dataclass
class SchemaDefinition:
    """Complete schema definition for coverage analysis."""

    schema_id: str
    name: str
    intents: list[IntentDefinition] = field(default_factory=list)
    entities: list[EntityDefinition] = field(default_factory=list)
    paths: list[ConversationPath] = field(default_factory=list)
    edge_cases: list[EdgeCase] = field(default_factory=list)


# ============================================
# Coverage Types
# ============================================


class CoverageLevel(Enum):
    """Coverage level classification."""

    EXCELLENT = "excellent"  # >= 90%
    GOOD = "good"  # >= 80%
    ADEQUATE = "adequate"  # >= 70%
    LOW = "low"  # >= 50%
    CRITICAL = "critical"  # < 50%


@dataclass
class CoverageMetric:
    """A single coverage metric."""

    name: str
    covered: int
    total: int
    percentage: float
    target: float
    meets_target: bool
    level: CoverageLevel
    covered_items: list[str] = field(default_factory=list)
    uncovered_items: list[str] = field(default_factory=list)


@dataclass
class IntentCoverage:
    """Intent coverage details."""

    metric: CoverageMetric
    intent_test_counts: dict[str, int] = field(default_factory=dict)
    intents_with_assertions: list[str] = field(default_factory=list)


@dataclass
class EntityCoverage:
    """Entity coverage details."""

    metric: CoverageMetric
    entity_test_counts: dict[str, int] = field(default_factory=dict)
    entities_with_validations: list[str] = field(default_factory=list)


@dataclass
class PathCoverage:
    """Conversation path coverage details."""

    metric: CoverageMetric
    path_test_counts: dict[str, int] = field(default_factory=dict)
    fully_covered_paths: list[str] = field(default_factory=list)
    partially_covered_paths: list[str] = field(default_factory=list)


@dataclass
class EdgeCaseCoverage:
    """Edge case coverage details."""

    metric: CoverageMetric
    case_test_counts: dict[str, int] = field(default_factory=dict)
    categories_covered: dict[str, int] = field(default_factory=dict)


@dataclass
class CoverageGap:
    """A gap in test coverage."""

    gap_id: str
    gap_type: str  # intent, entity, path, edge_case
    item_id: str
    item_name: str
    severity: str  # critical, high, medium, low
    description: str
    suggested_test: Optional[str] = None


@dataclass
class TestSuggestion:
    """A suggested test to improve coverage."""

    suggestion_id: str
    gap_id: str
    test_name: str
    test_description: str
    category: TestCategory
    priority: str
    estimated_coverage_gain: float
    sample_turns: list[str] = field(default_factory=list)


@dataclass
class CoverageReport:
    """Complete coverage analysis report."""

    schema_id: str
    schema_name: str
    total_tests: int
    total_assertions: int
    intent_coverage: IntentCoverage
    entity_coverage: EntityCoverage
    path_coverage: PathCoverage
    edge_case_coverage: EdgeCaseCoverage
    overall_score: float
    meets_all_targets: bool
    gaps: list[CoverageGap] = field(default_factory=list)
    suggestions: list[TestSuggestion] = field(default_factory=list)


# ============================================
# Coverage Analyzer Configuration
# ============================================


@dataclass
class CoverageConfig:
    """Configuration for coverage analysis."""

    intent_target: float = 0.80  # 80%
    entity_target: float = 0.70  # 70%
    path_target: float = 0.60  # 60%
    edge_case_target: float = 0.85  # 85%
    generate_suggestions: bool = True
    max_suggestions: int = 10
    include_sample_turns: bool = True


# ============================================
# Coverage Analyzer
# ============================================


class CoverageAnalyzer:
    """Analyzes test coverage for conversation tests."""

    def __init__(self, config: Optional[CoverageConfig] = None):
        """Initialize the coverage analyzer.

        Args:
            config: Configuration for coverage analysis
        """
        self.config = config or CoverageConfig()

    def analyze_coverage(
        self,
        schema: SchemaDefinition,
        tests: list[ConversationTest],
    ) -> CoverageReport:
        """Analyze test coverage against a schema.

        Args:
            schema: The schema definition to analyze against
            tests: List of conversation tests

        Returns:
            CoverageReport with detailed coverage metrics
        """
        # Extract test data
        test_intents = self._extract_tested_intents(tests)
        test_entities = self._extract_tested_entities(tests)
        test_paths = self._extract_tested_paths(tests, schema)
        test_edge_cases = self._extract_tested_edge_cases(tests, schema)

        # Calculate coverage metrics
        intent_coverage = self._calculate_intent_coverage(
            schema.intents, test_intents
        )
        entity_coverage = self._calculate_entity_coverage(
            schema.entities, test_entities
        )
        path_coverage = self._calculate_path_coverage(
            schema.paths, test_paths
        )
        edge_case_coverage = self._calculate_edge_case_coverage(
            schema.edge_cases, test_edge_cases
        )

        # Calculate overall score (weighted average)
        overall_score = self._calculate_overall_score(
            intent_coverage.metric,
            entity_coverage.metric,
            path_coverage.metric,
            edge_case_coverage.metric,
        )

        # Check if all targets are met
        meets_all_targets = all([
            intent_coverage.metric.meets_target,
            entity_coverage.metric.meets_target,
            path_coverage.metric.meets_target,
            edge_case_coverage.metric.meets_target,
        ])

        # Identify gaps
        gaps = self.identify_gaps(
            schema, intent_coverage, entity_coverage,
            path_coverage, edge_case_coverage
        )

        # Generate suggestions if configured
        suggestions: list[TestSuggestion] = []
        if self.config.generate_suggestions and gaps:
            suggestions = self.suggest_tests(gaps, schema)

        # Count total assertions
        total_assertions = sum(
            len(turn.assertions)
            for test in tests
            for turn in test.turns
        )

        return CoverageReport(
            schema_id=schema.schema_id,
            schema_name=schema.name,
            total_tests=len(tests),
            total_assertions=total_assertions,
            intent_coverage=intent_coverage,
            entity_coverage=entity_coverage,
            path_coverage=path_coverage,
            edge_case_coverage=edge_case_coverage,
            overall_score=overall_score,
            meets_all_targets=meets_all_targets,
            gaps=gaps,
            suggestions=suggestions,
        )

    def identify_gaps(
        self,
        schema: SchemaDefinition,
        intent_cov: IntentCoverage,
        entity_cov: EntityCoverage,
        path_cov: PathCoverage,
        edge_case_cov: EdgeCaseCoverage,
    ) -> list[CoverageGap]:
        """Identify coverage gaps.

        Args:
            schema: Schema definition
            intent_cov: Intent coverage data
            entity_cov: Entity coverage data
            path_cov: Path coverage data
            edge_case_cov: Edge case coverage data

        Returns:
            List of coverage gaps
        """
        gaps: list[CoverageGap] = []
        gap_counter = 0

        # Intent gaps
        for intent_id in intent_cov.metric.uncovered_items:
            intent = next(
                (i for i in schema.intents if i.intent_id == intent_id), None
            )
            if intent:
                gap_counter += 1
                gaps.append(CoverageGap(
                    gap_id=f"gap-{gap_counter:03d}",
                    gap_type="intent",
                    item_id=intent_id,
                    item_name=intent.name,
                    severity="high" if intent.category == "core" else "medium",
                    description=f"Intent '{intent.name}' has no test coverage",
                    suggested_test=f"Add test for {intent.name} intent recognition",
                ))

        # Entity gaps
        for entity_id in entity_cov.metric.uncovered_items:
            entity = next(
                (e for e in schema.entities if e.entity_id == entity_id), None
            )
            if entity:
                gap_counter += 1
                gaps.append(CoverageGap(
                    gap_id=f"gap-{gap_counter:03d}",
                    gap_type="entity",
                    item_id=entity_id,
                    item_name=entity.name,
                    severity="medium",
                    description=f"Entity '{entity.name}' has no test coverage",
                    suggested_test=f"Add test for {entity.name} entity extraction",
                ))

        # Path gaps
        for path_id in path_cov.metric.uncovered_items:
            path = next(
                (p for p in schema.paths if p.path_id == path_id), None
            )
            if path:
                gap_counter += 1
                gaps.append(CoverageGap(
                    gap_id=f"gap-{gap_counter:03d}",
                    gap_type="path",
                    item_id=path_id,
                    item_name=path.name,
                    severity="medium",
                    description=f"Conversation path '{path.name}' has no test coverage",
                    suggested_test=f"Add multi-turn test for {path.name} flow",
                ))

        # Edge case gaps
        for case_id in edge_case_cov.metric.uncovered_items:
            case = next(
                (c for c in schema.edge_cases if c.case_id == case_id), None
            )
            if case:
                gap_counter += 1
                gaps.append(CoverageGap(
                    gap_id=f"gap-{gap_counter:03d}",
                    gap_type="edge_case",
                    item_id=case_id,
                    item_name=case.name,
                    severity="high" if case.category == "error_handling" else "medium",
                    description=f"Edge case '{case.name}' has no test coverage",
                    suggested_test=f"Add test for {case.name} ({case.category})",
                ))

        return gaps

    def suggest_tests(
        self,
        gaps: list[CoverageGap],
        schema: SchemaDefinition,
    ) -> list[TestSuggestion]:
        """Generate test suggestions to fill coverage gaps.

        Args:
            gaps: List of coverage gaps
            schema: Schema definition

        Returns:
            List of test suggestions
        """
        suggestions: list[TestSuggestion] = []

        # Sort gaps by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_gaps = sorted(gaps, key=lambda g: severity_order.get(g.severity, 4))

        for i, gap in enumerate(sorted_gaps[: self.config.max_suggestions]):
            suggestion = self._create_suggestion(gap, schema, i + 1)
            suggestions.append(suggestion)

        return suggestions

    def _create_suggestion(
        self,
        gap: CoverageGap,
        schema: SchemaDefinition,
        index: int,
    ) -> TestSuggestion:
        """Create a test suggestion for a gap."""
        category = self._get_category_for_gap(gap)
        priority = "high" if gap.severity in ("critical", "high") else "medium"

        sample_turns: list[str] = []
        if self.config.include_sample_turns:
            sample_turns = self._generate_sample_turns(gap, schema)

        # Estimate coverage gain based on gap type
        coverage_gain = {
            "intent": 5.0,
            "entity": 3.0,
            "path": 4.0,
            "edge_case": 6.0,
        }.get(gap.gap_type, 2.0)

        return TestSuggestion(
            suggestion_id=f"suggestion-{index:03d}",
            gap_id=gap.gap_id,
            test_name=f"test_{gap.gap_type}_{gap.item_id}",
            test_description=gap.suggested_test or f"Test for {gap.item_name}",
            category=category,
            priority=priority,
            estimated_coverage_gain=coverage_gain,
            sample_turns=sample_turns,
        )

    def _get_category_for_gap(self, gap: CoverageGap) -> TestCategory:
        """Get the appropriate test category for a gap."""
        if gap.gap_type == "intent":
            return TestCategory.INTENT_RECOGNITION
        elif gap.gap_type == "entity":
            return TestCategory.ENTITY_EXTRACTION
        elif gap.gap_type == "path":
            return TestCategory.DIALOGUE_FLOW
        elif gap.gap_type == "edge_case":
            return TestCategory.ERROR_HANDLING
        return TestCategory.QUALITY_ASSURANCE

    def _generate_sample_turns(
        self,
        gap: CoverageGap,
        schema: SchemaDefinition,
    ) -> list[str]:
        """Generate sample turn inputs for a test suggestion."""
        turns: list[str] = []

        if gap.gap_type == "intent":
            intent = next(
                (i for i in schema.intents if i.intent_id == gap.item_id), None
            )
            if intent and intent.examples:
                turns = intent.examples[:3]
            else:
                turns = [f"User input for {gap.item_name}"]

        elif gap.gap_type == "entity":
            entity = next(
                (e for e in schema.entities if e.entity_id == gap.item_id), None
            )
            if entity and entity.examples:
                turns = [f"Input with {ex}" for ex in entity.examples[:3]]
            else:
                turns = [f"Input containing {gap.item_name}"]

        elif gap.gap_type == "path":
            path = next(
                (p for p in schema.paths if p.path_id == gap.item_id), None
            )
            if path and path.steps:
                turns = [f"Step: {step}" for step in path.steps[:3]]
            else:
                turns = [f"Start {gap.item_name} flow"]

        elif gap.gap_type == "edge_case":
            case = next(
                (c for c in schema.edge_cases if c.case_id == gap.item_id), None
            )
            if case and case.test_scenario:
                turns = [case.test_scenario]
            else:
                turns = [f"Trigger {gap.item_name} scenario"]

        return turns

    def _extract_tested_intents(
        self, tests: list[ConversationTest]
    ) -> dict[str, int]:
        """Extract intents tested across all tests."""
        intent_counts: dict[str, int] = {}

        for test in tests:
            for turn in test.turns:
                if turn.expected_intent:
                    intent_id = turn.expected_intent
                    intent_counts[intent_id] = intent_counts.get(intent_id, 0) + 1

                # Also count intents from assertions
                for assertion in turn.assertions:
                    if assertion.assertion_type.value == "intent_match":
                        if assertion.expected_value:
                            intent_id = assertion.expected_value
                            intent_counts[intent_id] = intent_counts.get(intent_id, 0) + 1

        return intent_counts

    def _extract_tested_entities(
        self, tests: list[ConversationTest]
    ) -> dict[str, int]:
        """Extract entities tested across all tests."""
        entity_counts: dict[str, int] = {}

        for test in tests:
            for turn in test.turns:
                # Count expected entities
                for entity in turn.expected_entities:
                    entity_type = entity.entity_type
                    entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

                # Count entity assertions
                for assertion in turn.assertions:
                    if assertion.assertion_type.value in (
                        "entity_present",
                        "entity_value",
                    ):
                        if assertion.expected_value:
                            # Use target as entity type identifier
                            entity_type = assertion.target.value
                            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

        return entity_counts

    def _extract_tested_paths(
        self,
        tests: list[ConversationTest],
        schema: SchemaDefinition,
    ) -> dict[str, int]:
        """Extract conversation paths tested."""
        path_counts: dict[str, int] = {}

        for test in tests:
            # Check if test targets a specific path
            if test.category == TestCategory.DIALOGUE_FLOW:
                # Try to match test to schema paths
                for path in schema.paths:
                    # Check if test uses any trigger intents from this path
                    test_intents = {
                        turn.expected_intent
                        for turn in test.turns
                        if turn.expected_intent
                    }
                    if test_intents & set(path.trigger_intents):
                        path_counts[path.path_id] = path_counts.get(path.path_id, 0) + 1

            # Multi-turn tests cover conversation paths
            if len(test.turns) >= 3:
                for path in schema.paths:
                    if any(
                        turn.expected_intent in path.trigger_intents
                        for turn in test.turns
                        if turn.expected_intent
                    ):
                        path_counts[path.path_id] = path_counts.get(path.path_id, 0) + 1

        return path_counts

    def _extract_tested_edge_cases(
        self,
        tests: list[ConversationTest],
        schema: SchemaDefinition,
    ) -> dict[str, int]:
        """Extract edge cases tested."""
        case_counts: dict[str, int] = {}

        edge_case_categories = {
            TestCategory.ERROR_HANDLING: "error_handling",
        }

        for test in tests:
            # Match by test category
            if test.category in edge_case_categories:
                category = edge_case_categories[test.category]
                for case in schema.edge_cases:
                    if case.category == category:
                        case_counts[case.case_id] = case_counts.get(case.case_id, 0) + 1

            # Match by tags
            for tag in test.tags:
                tag_lower = tag.lower()
                for case in schema.edge_cases:
                    if (
                        tag_lower in case.name.lower()
                        or tag_lower == case.category
                    ):
                        case_counts[case.case_id] = case_counts.get(case.case_id, 0) + 1

        return case_counts

    def _calculate_intent_coverage(
        self,
        intents: list[IntentDefinition],
        tested: dict[str, int],
    ) -> IntentCoverage:
        """Calculate intent coverage metrics."""
        total = len(intents)
        intent_ids = {i.intent_id for i in intents}
        covered_ids = {id for id in tested.keys() if id in intent_ids}
        covered = len(covered_ids)

        percentage = (covered / total * 100) if total > 0 else 0.0
        meets_target = percentage >= self.config.intent_target * 100

        uncovered = [i.intent_id for i in intents if i.intent_id not in tested]
        intents_with_assertions = [
            id for id, count in tested.items() if count > 1 and id in intent_ids
        ]

        metric = CoverageMetric(
            name="Intent Coverage",
            covered=covered,
            total=total,
            percentage=percentage,
            target=self.config.intent_target * 100,
            meets_target=meets_target,
            level=self._get_coverage_level(percentage),
            covered_items=list(covered_ids),
            uncovered_items=uncovered,
        )

        return IntentCoverage(
            metric=metric,
            intent_test_counts={k: v for k, v in tested.items() if k in intent_ids},
            intents_with_assertions=intents_with_assertions,
        )

    def _calculate_entity_coverage(
        self,
        entities: list[EntityDefinition],
        tested: dict[str, int],
    ) -> EntityCoverage:
        """Calculate entity coverage metrics."""
        total = len(entities)
        entity_ids = {e.entity_id for e in entities}
        covered_ids = {id for id in tested.keys() if id in entity_ids}
        covered = len(covered_ids)

        percentage = (covered / total * 100) if total > 0 else 0.0
        meets_target = percentage >= self.config.entity_target * 100

        uncovered = [e.entity_id for e in entities if e.entity_id not in tested]

        metric = CoverageMetric(
            name="Entity Coverage",
            covered=covered,
            total=total,
            percentage=percentage,
            target=self.config.entity_target * 100,
            meets_target=meets_target,
            level=self._get_coverage_level(percentage),
            covered_items=list(covered_ids),
            uncovered_items=uncovered,
        )

        return EntityCoverage(
            metric=metric,
            entity_test_counts={k: v for k, v in tested.items() if k in entity_ids},
            entities_with_validations=[],
        )

    def _calculate_path_coverage(
        self,
        paths: list[ConversationPath],
        tested: dict[str, int],
    ) -> PathCoverage:
        """Calculate conversation path coverage metrics."""
        total = len(paths)
        path_ids = {p.path_id for p in paths}
        covered_ids = {id for id in tested.keys() if id in path_ids}
        covered = len(covered_ids)

        percentage = (covered / total * 100) if total > 0 else 0.0
        meets_target = percentage >= self.config.path_target * 100

        uncovered = [p.path_id for p in paths if p.path_id not in tested]
        fully_covered = [id for id, count in tested.items() if count >= 3 and id in path_ids]
        partially_covered = [
            id for id, count in tested.items()
            if 0 < count < 3 and id in path_ids
        ]

        metric = CoverageMetric(
            name="Path Coverage",
            covered=covered,
            total=total,
            percentage=percentage,
            target=self.config.path_target * 100,
            meets_target=meets_target,
            level=self._get_coverage_level(percentage),
            covered_items=list(covered_ids),
            uncovered_items=uncovered,
        )

        return PathCoverage(
            metric=metric,
            path_test_counts={k: v for k, v in tested.items() if k in path_ids},
            fully_covered_paths=fully_covered,
            partially_covered_paths=partially_covered,
        )

    def _calculate_edge_case_coverage(
        self,
        edge_cases: list[EdgeCase],
        tested: dict[str, int],
    ) -> EdgeCaseCoverage:
        """Calculate edge case coverage metrics."""
        total = len(edge_cases)
        case_ids = {c.case_id for c in edge_cases}
        covered_ids = {id for id in tested.keys() if id in case_ids}
        covered = len(covered_ids)

        percentage = (covered / total * 100) if total > 0 else 0.0
        meets_target = percentage >= self.config.edge_case_target * 100

        uncovered = [c.case_id for c in edge_cases if c.case_id not in tested]

        # Count coverage by category
        categories_covered: dict[str, int] = {}
        for case in edge_cases:
            if case.case_id in tested:
                cat = case.category
                categories_covered[cat] = categories_covered.get(cat, 0) + 1

        metric = CoverageMetric(
            name="Edge Case Coverage",
            covered=covered,
            total=total,
            percentage=percentage,
            target=self.config.edge_case_target * 100,
            meets_target=meets_target,
            level=self._get_coverage_level(percentage),
            covered_items=list(covered_ids),
            uncovered_items=uncovered,
        )

        return EdgeCaseCoverage(
            metric=metric,
            case_test_counts={k: v for k, v in tested.items() if k in case_ids},
            categories_covered=categories_covered,
        )

    def _calculate_overall_score(
        self,
        intent: CoverageMetric,
        entity: CoverageMetric,
        path: CoverageMetric,
        edge_case: CoverageMetric,
    ) -> float:
        """Calculate weighted overall coverage score."""
        # Weights based on importance
        weights = {
            "intent": 0.30,
            "entity": 0.25,
            "path": 0.20,
            "edge_case": 0.25,
        }

        weighted_sum = (
            intent.percentage * weights["intent"]
            + entity.percentage * weights["entity"]
            + path.percentage * weights["path"]
            + edge_case.percentage * weights["edge_case"]
        )

        return round(weighted_sum, 2)

    def _get_coverage_level(self, percentage: float) -> CoverageLevel:
        """Get coverage level classification."""
        if percentage >= 90:
            return CoverageLevel.EXCELLENT
        elif percentage >= 80:
            return CoverageLevel.GOOD
        elif percentage >= 70:
            return CoverageLevel.ADEQUATE
        elif percentage >= 50:
            return CoverageLevel.LOW
        else:
            return CoverageLevel.CRITICAL

    def generate_report_text(self, report: CoverageReport) -> str:
        """Generate a text-based coverage report.

        Args:
            report: Coverage report to format

        Returns:
            Formatted text report
        """
        lines = [
            "=" * 60,
            f"COVERAGE REPORT: {report.schema_name}",
            "=" * 60,
            "",
            f"Total Tests: {report.total_tests}",
            f"Total Assertions: {report.total_assertions}",
            f"Overall Score: {report.overall_score:.1f}%",
            f"All Targets Met: {'Yes' if report.meets_all_targets else 'No'}",
            "",
            "-" * 40,
            "COVERAGE METRICS",
            "-" * 40,
        ]

        # Add metric summaries
        for name, metric in [
            ("Intent", report.intent_coverage.metric),
            ("Entity", report.entity_coverage.metric),
            ("Path", report.path_coverage.metric),
            ("Edge Case", report.edge_case_coverage.metric),
        ]:
            status = "✓" if metric.meets_target else "✗"
            lines.append(
                f"  {name}: {metric.covered}/{metric.total} "
                f"({metric.percentage:.1f}%) [{metric.level.value}] {status}"
            )

        # Add gaps if any
        if report.gaps:
            lines.extend([
                "",
                "-" * 40,
                f"COVERAGE GAPS ({len(report.gaps)})",
                "-" * 40,
            ])
            for gap in report.gaps[:10]:  # Show top 10
                lines.append(f"  [{gap.severity}] {gap.gap_type}: {gap.item_name}")
                lines.append(f"           {gap.description}")

        # Add suggestions if any
        if report.suggestions:
            lines.extend([
                "",
                "-" * 40,
                f"SUGGESTED TESTS ({len(report.suggestions)})",
                "-" * 40,
            ])
            for suggestion in report.suggestions[:5]:  # Show top 5
                lines.append(f"  [{suggestion.priority}] {suggestion.test_name}")
                lines.append(f"           {suggestion.test_description}")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def generate_report_dict(self, report: CoverageReport) -> dict[str, Any]:
        """Generate a dictionary representation of the coverage report.

        Args:
            report: Coverage report to format

        Returns:
            Dictionary representation
        """
        return {
            "schema_id": report.schema_id,
            "schema_name": report.schema_name,
            "summary": {
                "total_tests": report.total_tests,
                "total_assertions": report.total_assertions,
                "overall_score": report.overall_score,
                "meets_all_targets": report.meets_all_targets,
            },
            "metrics": {
                "intent": {
                    "covered": report.intent_coverage.metric.covered,
                    "total": report.intent_coverage.metric.total,
                    "percentage": report.intent_coverage.metric.percentage,
                    "target": report.intent_coverage.metric.target,
                    "meets_target": report.intent_coverage.metric.meets_target,
                    "level": report.intent_coverage.metric.level.value,
                },
                "entity": {
                    "covered": report.entity_coverage.metric.covered,
                    "total": report.entity_coverage.metric.total,
                    "percentage": report.entity_coverage.metric.percentage,
                    "target": report.entity_coverage.metric.target,
                    "meets_target": report.entity_coverage.metric.meets_target,
                    "level": report.entity_coverage.metric.level.value,
                },
                "path": {
                    "covered": report.path_coverage.metric.covered,
                    "total": report.path_coverage.metric.total,
                    "percentage": report.path_coverage.metric.percentage,
                    "target": report.path_coverage.metric.target,
                    "meets_target": report.path_coverage.metric.meets_target,
                    "level": report.path_coverage.metric.level.value,
                },
                "edge_case": {
                    "covered": report.edge_case_coverage.metric.covered,
                    "total": report.edge_case_coverage.metric.total,
                    "percentage": report.edge_case_coverage.metric.percentage,
                    "target": report.edge_case_coverage.metric.target,
                    "meets_target": report.edge_case_coverage.metric.meets_target,
                    "level": report.edge_case_coverage.metric.level.value,
                },
            },
            "gaps": [
                {
                    "gap_id": gap.gap_id,
                    "type": gap.gap_type,
                    "item_id": gap.item_id,
                    "item_name": gap.item_name,
                    "severity": gap.severity,
                    "description": gap.description,
                }
                for gap in report.gaps
            ],
            "suggestions": [
                {
                    "suggestion_id": s.suggestion_id,
                    "test_name": s.test_name,
                    "description": s.test_description,
                    "priority": s.priority,
                    "coverage_gain": s.estimated_coverage_gain,
                }
                for s in report.suggestions
            ],
        }
