"""Tests for the accessibility report generator.

Issue #76 - Task 4.10: Accessibility Report Generator
"""

import json
import pytest
from datetime import datetime

from src.accessibility.report import (
    AccessibilityReport,
    AccessibilityReportGenerator,
    ComponentReport,
    DisabilityReport,
    Recommendation,
    ReportSummary,
)
from src.accessibility.checker import (
    AccessibilityViolation,
    ComplianceLevel,
    ViolationSeverity,
)
from src.accessibility.disability_evaluators import DisabilityType


# ============================================
# Test Fixtures
# ============================================


@pytest.fixture
def simple_schema():
    """Simple schema for testing."""
    return {
        "name": "Test Schema",
        "components": [
            {
                "id": "greeting",
                "type": "message",
                "feedback": {
                    "success_template": "Hello! How can I help you today?"
                },
            }
        ],
    }


@pytest.fixture
def complex_schema():
    """Complex schema with multiple components."""
    return {
        "name": "Task Manager",
        "components": [
            {
                "id": "welcome",
                "type": "message",
                "feedback": {
                    "success_template": "Welcome to the task management system."
                },
            },
            {
                "id": "create_task",
                "type": "action",
                "feedback": {
                    "success_template": "Your task has been created successfully.",
                    "error_template": "An error occurred while creating the task.",
                },
            },
            {
                "id": "list_tasks",
                "type": "query",
                "feedback": {
                    "success_template": "Here are your tasks.",
                },
            },
        ],
        "timing": {
            "response_timeout": 30000,
            "typing_indicator": True,
        },
    }


@pytest.fixture
def schema_with_violations():
    """Schema designed to have accessibility violations."""
    return {
        "name": "Complex Schema",
        "components": [
            {
                "id": "verbose_message",
                "type": "message",
                "feedback": {
                    "success_template": (
                        "The implementation of the functionality for the authorization "
                        "and authentication mechanisms necessitates the utilization of "
                        "sophisticated verification methodologies that subsequently require "
                        "comprehensive prerequisite configurations notwithstanding the "
                        "aforementioned complexity."
                    ),
                },
            },
        ],
    }


@pytest.fixture
def generator():
    """Report generator instance."""
    return AccessibilityReportGenerator()


@pytest.fixture
def sample_report():
    """Pre-built sample report for export tests."""
    return AccessibilityReport(
        schema_name="Sample Schema",
        target_level=ComplianceLevel.LEVEL_AA,
        achieved_level=ComplianceLevel.LEVEL_A,
        overall_score=0.72,
        passes=False,
        summary=ReportSummary(
            total_components=3,
            passing_components=2,
            critical_violations=0,
            major_violations=2,
            minor_violations=3,
            advisory_count=1,
            top_issues=[
                "Reading level exceeds Grade 8",
                "Sentence too long",
            ],
            remediation_priority=[
                "Simplify vocabulary",
                "Split long sentences",
            ],
        ),
        component_details=[
            ComponentReport(
                component_id="comp1",
                component_type="message",
                score=0.8,
                passes=True,
                achieved_level=ComplianceLevel.LEVEL_AA,
                violations=[],
                recommendations=[],
            ),
            ComponentReport(
                component_id="comp2",
                component_type="action",
                score=0.6,
                passes=False,
                achieved_level=ComplianceLevel.LEVEL_A,
                violations=[
                    AccessibilityViolation(
                        criterion="AA.1.1",
                        severity=ViolationSeverity.MAJOR,
                        description="Reading level 9.2 exceeds maximum 8.0",
                        remediation="Simplify vocabulary",
                    )
                ],
                recommendations=["Simplify vocabulary"],
            ),
        ],
        disability_coverage=[
            DisabilityReport(
                disability_type=DisabilityType.VISUAL,
                accommodation_score=0.85,
                passes=True,
                barriers_count=2,
                critical_barriers=0,
                accommodations_present=["High contrast support"],
                accommodations_missing=["Screen reader labels"],
                recommendations=["Add aria-label attributes"],
            ),
            DisabilityReport(
                disability_type=DisabilityType.COGNITIVE,
                accommodation_score=0.7,
                passes=True,
                barriers_count=3,
                critical_barriers=0,
                accommodations_present=["Clear language"],
                accommodations_missing=["Reading time estimation"],
                recommendations=["Add reading time estimates"],
            ),
        ],
        violations=[
            AccessibilityViolation(
                criterion="AA.1.1",
                severity=ViolationSeverity.MAJOR,
                description="Reading level 9.2 exceeds maximum 8.0",
                remediation="Simplify vocabulary",
            ),
            AccessibilityViolation(
                criterion="AA.2.1",
                severity=ViolationSeverity.MINOR,
                description="Complex word 'utilize' found",
                remediation="Use 'use' instead",
                element="utilize",
            ),
        ],
        recommendations=[
            Recommendation(
                priority="high",
                title="Simplify vocabulary",
                description="Affects 2 instances",
                affected_components=["comp2"],
                impact="Affects user experience",
                effort="low",
            ),
            Recommendation(
                priority="medium",
                title="Split long sentences",
                description="Affects 1 instance",
                affected_components=["comp2"],
                impact="Reduces readability",
                effort="medium",
            ),
        ],
        generated_at=datetime(2024, 1, 15, 10, 30, 0),
    )


# ============================================
# ReportSummary Tests
# ============================================


class TestReportSummary:
    """Tests for ReportSummary dataclass."""

    def test_create_summary(self):
        """Test creating a report summary."""
        summary = ReportSummary(
            total_components=5,
            passing_components=3,
            critical_violations=1,
            major_violations=2,
            minor_violations=4,
            advisory_count=1,
            top_issues=["Issue 1", "Issue 2"],
            remediation_priority=["Fix 1", "Fix 2"],
        )

        assert summary.total_components == 5
        assert summary.passing_components == 3
        assert summary.critical_violations == 1
        assert summary.major_violations == 2

    def test_empty_summary(self):
        """Test summary with no violations."""
        summary = ReportSummary(
            total_components=2,
            passing_components=2,
            critical_violations=0,
            major_violations=0,
            minor_violations=0,
            advisory_count=0,
            top_issues=[],
            remediation_priority=[],
        )

        assert summary.critical_violations == 0
        assert len(summary.top_issues) == 0


# ============================================
# ComponentReport Tests
# ============================================


class TestComponentReport:
    """Tests for ComponentReport dataclass."""

    def test_create_component_report(self):
        """Test creating a component report."""
        report = ComponentReport(
            component_id="test_comp",
            component_type="message",
            score=0.85,
            passes=True,
            achieved_level=ComplianceLevel.LEVEL_AA,
            violations=[],
            recommendations=["Consider simplifying"],
        )

        assert report.component_id == "test_comp"
        assert report.score == 0.85
        assert report.passes is True
        assert report.achieved_level == ComplianceLevel.LEVEL_AA

    def test_component_with_violations(self):
        """Test component report with violations."""
        violation = AccessibilityViolation(
            criterion="AA.1.1",
            severity=ViolationSeverity.MAJOR,
            description="Reading level too high",
            remediation="Simplify",
        )

        report = ComponentReport(
            component_id="test",
            component_type="action",
            score=0.6,
            passes=False,
            achieved_level=ComplianceLevel.LEVEL_A,
            violations=[violation],
            recommendations=["Simplify"],
        )

        assert len(report.violations) == 1
        assert report.passes is False


# ============================================
# DisabilityReport Tests
# ============================================


class TestDisabilityReport:
    """Tests for DisabilityReport dataclass."""

    def test_create_disability_report(self):
        """Test creating a disability report."""
        report = DisabilityReport(
            disability_type=DisabilityType.VISUAL,
            accommodation_score=0.9,
            passes=True,
            barriers_count=1,
            critical_barriers=0,
            accommodations_present=["High contrast"],
            accommodations_missing=["Audio descriptions"],
            recommendations=["Add audio descriptions"],
        )

        assert report.disability_type == DisabilityType.VISUAL
        assert report.accommodation_score == 0.9
        assert report.passes is True

    def test_all_disability_types(self):
        """Test reports for all disability types."""
        for dtype in DisabilityType:
            report = DisabilityReport(
                disability_type=dtype,
                accommodation_score=0.75,
                passes=True,
                barriers_count=2,
                critical_barriers=0,
                accommodations_present=[],
                accommodations_missing=[],
                recommendations=[],
            )
            assert report.disability_type == dtype


# ============================================
# Recommendation Tests
# ============================================


class TestRecommendation:
    """Tests for Recommendation dataclass."""

    def test_create_recommendation(self):
        """Test creating a recommendation."""
        rec = Recommendation(
            priority="high",
            title="Simplify language",
            description="Complex vocabulary detected",
            affected_components=["comp1", "comp2"],
            impact="Blocks accessibility",
            effort="medium",
        )

        assert rec.priority == "high"
        assert rec.title == "Simplify language"
        assert len(rec.affected_components) == 2

    def test_priority_values(self):
        """Test all priority values."""
        for priority in ["high", "medium", "low"]:
            rec = Recommendation(
                priority=priority,
                title="Test",
                description="Test",
            )
            assert rec.priority == priority


# ============================================
# AccessibilityReport Tests
# ============================================


class TestAccessibilityReport:
    """Tests for AccessibilityReport dataclass."""

    def test_score_percentage(self, sample_report):
        """Test score percentage calculation."""
        assert sample_report.score_percentage == 72

    def test_level_badge_with_level(self, sample_report):
        """Test level badge when level achieved."""
        assert sample_report.level_badge == "Level A"

    def test_level_badge_no_level(self):
        """Test level badge when no level achieved."""
        report = AccessibilityReport(
            schema_name="Test",
            target_level=ComplianceLevel.LEVEL_AA,
            achieved_level=None,
            overall_score=0.4,
            passes=False,
            summary=ReportSummary(
                total_components=1,
                passing_components=0,
                critical_violations=2,
                major_violations=3,
                minor_violations=0,
                advisory_count=0,
                top_issues=[],
                remediation_priority=[],
            ),
            component_details=[],
            disability_coverage=[],
            violations=[],
            recommendations=[],
        )
        assert report.level_badge == "Non-Compliant"


# ============================================
# AccessibilityReportGenerator Tests
# ============================================


class TestAccessibilityReportGenerator:
    """Tests for AccessibilityReportGenerator class."""

    def test_init(self, generator):
        """Test generator initialization."""
        assert generator._schema_checker is not None
        assert generator._disability_evaluator is not None

    def test_generate_report_simple(self, generator, simple_schema):
        """Test generating report for simple schema."""
        report = generator.generate_report(simple_schema, ComplianceLevel.LEVEL_AA)

        assert report.schema_name == "Test Schema"
        assert report.target_level == ComplianceLevel.LEVEL_AA
        assert isinstance(report.overall_score, float)
        assert 0.0 <= report.overall_score <= 1.0
        assert isinstance(report.summary, ReportSummary)

    def test_generate_report_complex(self, generator, complex_schema):
        """Test generating report for complex schema."""
        report = generator.generate_report(complex_schema, ComplianceLevel.LEVEL_AA)

        assert report.schema_name == "Task Manager"
        assert len(report.component_details) == 3
        assert len(report.disability_coverage) > 0

    def test_generate_report_with_violations(self, generator, schema_with_violations):
        """Test report for schema with accessibility violations."""
        report = generator.generate_report(
            schema_with_violations, ComplianceLevel.LEVEL_AA
        )

        # Should have violations due to complex language
        assert len(report.violations) > 0
        assert report.summary.major_violations > 0 or report.summary.minor_violations > 0

    def test_generate_report_level_a(self, generator, simple_schema):
        """Test report generation for Level A."""
        report = generator.generate_report(simple_schema, ComplianceLevel.LEVEL_A)
        assert report.target_level == ComplianceLevel.LEVEL_A

    def test_generate_report_level_aaa(self, generator, simple_schema):
        """Test report generation for Level AAA."""
        report = generator.generate_report(simple_schema, ComplianceLevel.LEVEL_AAA)
        assert report.target_level == ComplianceLevel.LEVEL_AAA

    def test_generate_report_empty_schema(self, generator):
        """Test report for empty schema."""
        report = generator.generate_report({"name": "Empty"}, ComplianceLevel.LEVEL_AA)
        assert report.schema_name == "Empty"
        assert report.summary.total_components == 0

    def test_report_has_generated_timestamp(self, generator, simple_schema):
        """Test that report has generated timestamp."""
        report = generator.generate_report(simple_schema, ComplianceLevel.LEVEL_AA)
        assert isinstance(report.generated_at, datetime)

    def test_recommendations_sorted_by_priority(self, generator, schema_with_violations):
        """Test that recommendations are sorted by priority."""
        report = generator.generate_report(
            schema_with_violations, ComplianceLevel.LEVEL_AA
        )

        if len(report.recommendations) >= 2:
            priority_order = {"high": 0, "medium": 1, "low": 2}
            for i in range(len(report.recommendations) - 1):
                current = priority_order.get(report.recommendations[i].priority, 3)
                next_val = priority_order.get(report.recommendations[i + 1].priority, 3)
                assert current <= next_val


# ============================================
# Export Markdown Tests
# ============================================


class TestExportMarkdown:
    """Tests for Markdown export functionality."""

    def test_export_markdown_basic(self, generator, sample_report):
        """Test basic markdown export."""
        md = generator.export_markdown(sample_report)

        assert "# LUI Accessibility Report" in md
        assert "Sample Schema" in md
        assert "Target Level" in md

    def test_export_markdown_contains_summary(self, generator, sample_report):
        """Test markdown contains summary table."""
        md = generator.export_markdown(sample_report)

        assert "## Summary" in md
        assert "| Metric | Value |" in md
        assert "Total Components" in md

    def test_export_markdown_contains_issues(self, generator, sample_report):
        """Test markdown contains top issues."""
        md = generator.export_markdown(sample_report)

        assert "## Top Issues" in md
        assert "Reading level exceeds Grade 8" in md

    def test_export_markdown_contains_recommendations(self, generator, sample_report):
        """Test markdown contains recommendations."""
        md = generator.export_markdown(sample_report)

        assert "## Recommendations" in md
        assert "Simplify vocabulary" in md

    def test_export_markdown_contains_components(self, generator, sample_report):
        """Test markdown contains component details."""
        md = generator.export_markdown(sample_report)

        assert "## Component Details" in md
        assert "comp1" in md
        assert "comp2" in md

    def test_export_markdown_contains_disability(self, generator, sample_report):
        """Test markdown contains disability coverage."""
        md = generator.export_markdown(sample_report)

        assert "## Disability Coverage" in md
        assert "Visual" in md
        assert "Cognitive" in md

    def test_export_markdown_contains_violations(self, generator, sample_report):
        """Test markdown contains violations."""
        md = generator.export_markdown(sample_report)

        assert "## Violations Detail" in md
        assert "AA.1.1" in md

    def test_export_markdown_status_icons(self, generator, sample_report):
        """Test markdown includes status icons."""
        md = generator.export_markdown(sample_report)

        # Should have pass/fail icons for components
        assert "✅" in md or "❌" in md

    def test_export_markdown_priority_icons(self, generator, sample_report):
        """Test markdown includes priority icons."""
        md = generator.export_markdown(sample_report)

        # Should have priority icons
        assert any(icon in md for icon in ["🔴", "🟡", "🟢"])


# ============================================
# Export JSON Tests
# ============================================


class TestExportJSON:
    """Tests for JSON export functionality."""

    def test_export_json_basic(self, generator, sample_report):
        """Test basic JSON export."""
        data = generator.export_json(sample_report)

        assert isinstance(data, dict)
        assert data["schema_name"] == "Sample Schema"
        assert data["target_level"] == "AA"

    def test_export_json_serializable(self, generator, sample_report):
        """Test JSON is serializable."""
        data = generator.export_json(sample_report)
        # Should not raise
        json_str = json.dumps(data)
        assert isinstance(json_str, str)

    def test_export_json_roundtrip(self, generator, sample_report):
        """Test JSON can be serialized and deserialized."""
        data = generator.export_json(sample_report)
        json_str = json.dumps(data)
        parsed = json.loads(json_str)

        assert parsed["schema_name"] == "Sample Schema"
        assert parsed["overall_score"] == 0.72

    def test_export_json_contains_summary(self, generator, sample_report):
        """Test JSON contains summary."""
        data = generator.export_json(sample_report)

        assert "summary" in data
        assert data["summary"]["total_components"] == 3
        assert data["summary"]["passing_components"] == 2

    def test_export_json_contains_components(self, generator, sample_report):
        """Test JSON contains component details."""
        data = generator.export_json(sample_report)

        assert "component_details" in data
        assert len(data["component_details"]) == 2
        assert data["component_details"][0]["component_id"] == "comp1"

    def test_export_json_contains_disability(self, generator, sample_report):
        """Test JSON contains disability coverage."""
        data = generator.export_json(sample_report)

        assert "disability_coverage" in data
        assert len(data["disability_coverage"]) == 2
        assert data["disability_coverage"][0]["disability_type"] == "visual"

    def test_export_json_contains_violations(self, generator, sample_report):
        """Test JSON contains violations."""
        data = generator.export_json(sample_report)

        assert "violations" in data
        assert len(data["violations"]) == 2
        assert data["violations"][0]["severity"] == "major"

    def test_export_json_contains_recommendations(self, generator, sample_report):
        """Test JSON contains recommendations."""
        data = generator.export_json(sample_report)

        assert "recommendations" in data
        assert len(data["recommendations"]) == 2
        assert data["recommendations"][0]["priority"] == "high"

    def test_export_json_timestamp_format(self, generator, sample_report):
        """Test JSON timestamp is ISO format."""
        data = generator.export_json(sample_report)

        assert "generated_at" in data
        # Should be parseable as ISO format
        datetime.fromisoformat(data["generated_at"])


# ============================================
# Export HTML Tests
# ============================================


class TestExportHTML:
    """Tests for HTML export functionality."""

    def test_export_html_basic(self, generator, sample_report):
        """Test basic HTML export."""
        html = generator.export_html(sample_report)

        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "Sample Schema" in html

    def test_export_html_contains_title(self, generator, sample_report):
        """Test HTML contains title."""
        html = generator.export_html(sample_report)

        assert "<title>" in html
        assert "Accessibility Report" in html

    def test_export_html_contains_styles(self, generator, sample_report):
        """Test HTML contains styles."""
        html = generator.export_html(sample_report)

        assert "<style>" in html
        assert "font-family" in html

    def test_export_html_contains_summary(self, generator, sample_report):
        """Test HTML contains summary section."""
        html = generator.export_html(sample_report)

        assert "Summary" in html
        assert "Total Components" in html

    def test_export_html_contains_score_meter(self, generator, sample_report):
        """Test HTML contains score meter."""
        html = generator.export_html(sample_report)

        assert "score-meter" in html
        assert "72%" in html

    def test_export_html_contains_badges(self, generator, sample_report):
        """Test HTML contains status badges."""
        html = generator.export_html(sample_report)

        assert "badge" in html
        assert "FAIL" in html  # Report doesn't pass

    def test_export_html_escapes_content(self, generator):
        """Test HTML escapes special characters."""
        report = AccessibilityReport(
            schema_name="<script>alert('xss')</script>",
            target_level=ComplianceLevel.LEVEL_AA,
            achieved_level=None,
            overall_score=0.5,
            passes=False,
            summary=ReportSummary(
                total_components=0,
                passing_components=0,
                critical_violations=0,
                major_violations=0,
                minor_violations=0,
                advisory_count=0,
                top_issues=[],
                remediation_priority=[],
            ),
            component_details=[],
            disability_coverage=[],
            violations=[],
            recommendations=[],
        )

        html = generator.export_html(report)

        # Script tag should be escaped
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    def test_export_html_contains_recommendations(self, generator, sample_report):
        """Test HTML contains recommendations."""
        html = generator.export_html(sample_report)

        assert "Recommendations" in html
        assert "Simplify vocabulary" in html

    def test_export_html_contains_disability_table(self, generator, sample_report):
        """Test HTML contains disability coverage table."""
        html = generator.export_html(sample_report)

        assert "Disability Coverage" in html
        assert "Visual" in html
        assert "Cognitive" in html

    def test_export_html_contains_violations(self, generator, sample_report):
        """Test HTML contains violations section."""
        html = generator.export_html(sample_report)

        assert "Violations" in html
        assert "AA.1.1" in html


# ============================================
# Integration Tests
# ============================================


class TestIntegration:
    """Integration tests for full report workflow."""

    def test_full_workflow(self, generator, complex_schema):
        """Test full report generation and export workflow."""
        # Generate report
        report = generator.generate_report(complex_schema, ComplianceLevel.LEVEL_AA)

        # Export to all formats
        md = generator.export_markdown(report)
        json_data = generator.export_json(report)
        html = generator.export_html(report)

        # Verify all exports are non-empty
        assert len(md) > 100
        assert len(json_data) > 0
        assert len(html) > 100

    def test_report_consistency_across_formats(self, generator, simple_schema):
        """Test that report data is consistent across formats."""
        report = generator.generate_report(simple_schema, ComplianceLevel.LEVEL_AA)

        md = generator.export_markdown(report)
        json_data = generator.export_json(report)
        html = generator.export_html(report)

        # Schema name should appear in all formats
        assert "Test Schema" in md
        assert json_data["schema_name"] == "Test Schema"
        assert "Test Schema" in html

    def test_empty_schema_all_formats(self, generator):
        """Test all export formats work with empty schema."""
        report = generator.generate_report({"name": "Empty"}, ComplianceLevel.LEVEL_A)

        md = generator.export_markdown(report)
        json_data = generator.export_json(report)
        html = generator.export_html(report)

        assert "Empty" in md
        assert json_data["schema_name"] == "Empty"
        assert "Empty" in html


# ============================================
# Edge Cases
# ============================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_schema_without_name(self, generator):
        """Test schema without name field."""
        report = generator.generate_report(
            {"components": []}, ComplianceLevel.LEVEL_AA
        )
        assert report.schema_name  # Should have some default name

    def test_very_long_schema_name(self, generator):
        """Test very long schema name."""
        long_name = "A" * 1000
        report = generator.generate_report(
            {"name": long_name}, ComplianceLevel.LEVEL_AA
        )
        assert long_name in report.schema_name

    def test_unicode_content(self, generator):
        """Test schema with unicode content."""
        schema = {
            "name": "Unicode Test 日本語 émoji 🎉",
            "components": [
                {
                    "id": "unicode",
                    "type": "message",
                    "feedback": {"success_template": "Café ñ 中文"},
                }
            ],
        }
        report = generator.generate_report(schema, ComplianceLevel.LEVEL_AA)

        md = generator.export_markdown(report)
        json_data = generator.export_json(report)
        html = generator.export_html(report)

        # All formats should handle unicode
        assert "日本語" in md
        assert "日本語" in json_data["schema_name"]
        assert "日本語" in html

    def test_special_characters_in_violations(self, generator):
        """Test special characters in violation descriptions."""
        schema = {
            "name": "Test",
            "components": [
                {
                    "id": "special",
                    "type": "message",
                    "feedback": {
                        "success_template": "Use <tag> & 'quotes' or \"double\""
                    },
                }
            ],
        }
        report = generator.generate_report(schema, ComplianceLevel.LEVEL_AA)

        # HTML export should escape properly
        html = generator.export_html(report)
        assert "<tag>" not in html or "&lt;tag&gt;" in html

    def test_many_components(self, generator):
        """Test schema with many components."""
        components = [
            {
                "id": f"comp_{i}",
                "type": "message",
                "feedback": {"success_template": f"Message {i}"},
            }
            for i in range(50)
        ]
        schema = {"name": "Large Schema", "components": components}

        report = generator.generate_report(schema, ComplianceLevel.LEVEL_AA)
        assert report.summary.total_components == 50

    def test_deeply_nested_schema(self, generator):
        """Test deeply nested schema structure."""
        schema = {
            "name": "Nested",
            "components": [
                {
                    "id": "nested",
                    "type": "complex",
                    "feedback": {
                        "success_template": "Success",
                        "nested": {
                            "deep": {"deeper": {"deepest": "value"}},
                        },
                    },
                }
            ],
        }
        report = generator.generate_report(schema, ComplianceLevel.LEVEL_AA)
        assert report is not None
