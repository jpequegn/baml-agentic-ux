"""Tests for Report Generator.

Issue #95 - Task 6.7: Report Generator
Part of #29 - Phase 6: Conversational Testing Framework
"""

import json
import os
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from src.testing.coverage import (
    CoverageGap,
    CoverageLevel,
    CoverageMetric,
    CoverageReport,
    EdgeCaseCoverage,
    EntityCoverage,
    IntentCoverage,
    PathCoverage,
    TestSuggestion,
)
from src.testing.report_generator import (
    ReportConfig,
    ReportFormat,
    ReportGenerator,
    ReportMetadata,
    TestReport,
    TrendAnalysis,
    TrendDataPoint,
)
from src.testing.types import (
    AssertionResult,
    AssertionSeverity,
    AssertionType,
    FailureSummary,
    QualityScores,
    SuiteSummary,
    TestCategory,
    TestExecutionResult,
    TestStatus,
    TestSuiteResult,
    TurnResult,
)


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def sample_quality_scores() -> QualityScores:
    """Create sample quality scores."""
    return QualityScores(
        coherence=0.92,
        naturalness=0.88,
        accuracy=0.95,
        relevance=0.90,
        avg_confidence=0.85,
        max_drift_score=0.15,
        avg_latency_ms=150.0,
    )


@pytest.fixture
def sample_turn_results() -> list[TurnResult]:
    """Create sample turn results."""
    return [
        TurnResult(
            turn_number=1,
            input="Hello, I need help",
            passed=True,
            latency_ms=120,
            actual_response="Hi! How can I help you today?",
            detected_intent="greeting",
        ),
        TurnResult(
            turn_number=2,
            input="I want to book a flight",
            passed=True,
            latency_ms=180,
            actual_response="I'd be happy to help you book a flight.",
            detected_intent="book_flight",
        ),
    ]


@pytest.fixture
def sample_assertion_results() -> list[AssertionResult]:
    """Create sample assertion results."""
    return [
        AssertionResult(
            assertion_id="assert-1",
            turn_number=1,
            assertion_type=AssertionType.INTENT_MATCH,
            passed=True,
            severity=AssertionSeverity.ERROR,
            expected_value="greeting",
            actual_value="greeting",
        ),
        AssertionResult(
            assertion_id="assert-2",
            turn_number=2,
            assertion_type=AssertionType.INTENT_MATCH,
            passed=True,
            severity=AssertionSeverity.ERROR,
            expected_value="book_flight",
            actual_value="book_flight",
        ),
    ]


@pytest.fixture
def sample_test_result(
    sample_quality_scores: QualityScores,
    sample_turn_results: list[TurnResult],
    sample_assertion_results: list[AssertionResult],
) -> TestExecutionResult:
    """Create a sample test execution result."""
    return TestExecutionResult(
        test_id="test-001",
        test_name="Test Flight Booking Flow",
        status=TestStatus.PASSED,
        started_at="2024-01-15T10:00:00Z",
        completed_at="2024-01-15T10:00:01Z",
        duration_ms=1000,
        quality_scores=sample_quality_scores,
        turn_results=sample_turn_results,
        assertion_results=sample_assertion_results,
    )


@pytest.fixture
def sample_failed_test_result(
    sample_quality_scores: QualityScores,
) -> TestExecutionResult:
    """Create a sample failed test result."""
    return TestExecutionResult(
        test_id="test-002",
        test_name="Test Error Handling",
        status=TestStatus.FAILED,
        started_at="2024-01-15T10:01:00Z",
        completed_at="2024-01-15T10:01:02Z",
        duration_ms=2000,
        quality_scores=sample_quality_scores,
        turn_results=[
            TurnResult(
                turn_number=1,
                input="Invalid request",
                passed=False,
                latency_ms=200,
                actual_response="Error occurred",
                detected_intent="unknown",
            )
        ],
        assertion_results=[
            AssertionResult(
                assertion_id="assert-3",
                turn_number=1,
                assertion_type=AssertionType.INTENT_MATCH,
                passed=False,
                severity=AssertionSeverity.CRITICAL,
                expected_value="error_handling",
                actual_value="unknown",
                message="Intent mismatch",
            )
        ],
        failure_summary=FailureSummary(
            total_assertions=1,
            passed_count=0,
            failed_count=1,
            first_failure_turn=1,
            critical_failures=["Intent mismatch: expected error_handling, got unknown"],
        ),
        logs=["Error: Intent classification failed", "Fallback triggered"],
    )


@pytest.fixture
def sample_suite_result(
    sample_test_result: TestExecutionResult,
    sample_failed_test_result: TestExecutionResult,
) -> TestSuiteResult:
    """Create a sample test suite result."""
    return TestSuiteResult(
        suite_id="suite-001",
        suite_name="Flight Booking Test Suite",
        status=TestStatus.FAILED,
        started_at="2024-01-15T10:00:00Z",
        completed_at="2024-01-15T10:01:02Z",
        duration_ms=62000,
        summary=SuiteSummary(
            total_tests=2,
            passed=1,
            failed=1,
            errors=0,
            skipped=0,
            pass_rate=0.5,
            avg_duration_ms=1500.0,
        ),
        test_results=[sample_test_result, sample_failed_test_result],
    )


@pytest.fixture
def sample_passing_suite_result(
    sample_test_result: TestExecutionResult,
) -> TestSuiteResult:
    """Create a sample passing test suite result."""
    return TestSuiteResult(
        suite_id="suite-002",
        suite_name="Simple Test Suite",
        status=TestStatus.PASSED,
        started_at="2024-01-15T10:00:00Z",
        completed_at="2024-01-15T10:00:01Z",
        duration_ms=1000,
        summary=SuiteSummary(
            total_tests=1,
            passed=1,
            failed=0,
            errors=0,
            skipped=0,
            pass_rate=1.0,
            avg_duration_ms=1000.0,
        ),
        test_results=[sample_test_result],
    )


@pytest.fixture
def sample_coverage_report() -> CoverageReport:
    """Create a sample coverage report."""
    return CoverageReport(
        schema_id="schema-001",
        schema_name="Flight Booking Schema",
        total_tests=10,
        total_assertions=50,
        intent_coverage=IntentCoverage(
            metric=CoverageMetric(
                name="intent",
                covered=8,
                total=10,
                percentage=0.80,
                target=0.80,
                meets_target=True,
                level=CoverageLevel.GOOD,
                covered_items=["greeting", "book_flight", "cancel_flight"],
                uncovered_items=["modify_booking", "get_status"],
            ),
            intent_test_counts={"greeting": 3, "book_flight": 5},
        ),
        entity_coverage=EntityCoverage(
            metric=CoverageMetric(
                name="entity",
                covered=5,
                total=8,
                percentage=0.625,
                target=0.70,
                meets_target=False,
                level=CoverageLevel.ADEQUATE,
            ),
            entity_test_counts={"destination": 3, "date": 2},
        ),
        path_coverage=PathCoverage(
            metric=CoverageMetric(
                name="path",
                covered=4,
                total=6,
                percentage=0.667,
                target=0.60,
                meets_target=True,
                level=CoverageLevel.ADEQUATE,
            ),
        ),
        edge_case_coverage=EdgeCaseCoverage(
            metric=CoverageMetric(
                name="edge_case",
                covered=7,
                total=8,
                percentage=0.875,
                target=0.85,
                meets_target=True,
                level=CoverageLevel.GOOD,
            ),
        ),
        overall_score=0.74,
        meets_all_targets=False,
        gaps=[
            CoverageGap(
                gap_id="gap-1",
                gap_type="entity",
                item_id="departure_time",
                item_name="Departure Time Entity",
                severity="high",
                description="No tests cover departure time extraction",
            )
        ],
        suggestions=[
            TestSuggestion(
                suggestion_id="sug-1",
                gap_id="gap-1",
                test_name="Test Departure Time Extraction",
                test_description="Add test for extracting departure time from user input",
                category=TestCategory.ENTITY_EXTRACTION,
                priority="high",
                estimated_coverage_gain=0.05,
            )
        ],
    )


@pytest.fixture
def sample_trends() -> TrendAnalysis:
    """Create sample trend analysis."""
    return TrendAnalysis(
        data_points=[
            TrendDataPoint(
                timestamp="2024-01-14T10:00:00Z",
                pass_rate=0.45,
                avg_quality_score=0.80,
                total_tests=10,
                avg_duration_ms=1200.0,
            ),
            TrendDataPoint(
                timestamp="2024-01-15T10:00:00Z",
                pass_rate=0.50,
                avg_quality_score=0.85,
                total_tests=12,
                avg_duration_ms=1100.0,
            ),
        ],
        pass_rate_trend="improving",
        quality_trend="improving",
        performance_trend="improving",
    )


@pytest.fixture
def report_generator() -> ReportGenerator:
    """Create a report generator with default config."""
    return ReportGenerator()


@pytest.fixture
def report_generator_with_config() -> ReportGenerator:
    """Create a report generator with custom config."""
    config = ReportConfig(
        include_logs=True,
        include_turn_details=True,
        include_quality_breakdown=True,
        include_coverage=True,
        include_trends=True,
        max_log_lines=50,
    )
    return ReportGenerator(config)


# ============================================
# Test ReportGenerator Initialization
# ============================================


class TestReportGeneratorInit:
    """Tests for ReportGenerator initialization."""

    def test_default_config(self):
        """Test generator with default configuration."""
        generator = ReportGenerator()
        assert generator.config is not None
        assert generator.config.include_logs is True
        assert generator.config.include_turn_details is True

    def test_custom_config(self):
        """Test generator with custom configuration."""
        config = ReportConfig(
            include_logs=False,
            include_turn_details=False,
            max_log_lines=25,
        )
        generator = ReportGenerator(config)
        assert generator.config.include_logs is False
        assert generator.config.include_turn_details is False
        assert generator.config.max_log_lines == 25


# ============================================
# Test HTML Report Generation
# ============================================


class TestHTMLReport:
    """Tests for HTML report generation."""

    def test_generate_html_basic(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test basic HTML report generation."""
        html = report_generator.generate_html(sample_suite_result)

        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "Flight Booking Test Suite" in html
        assert "</html>" in html

    def test_generate_html_contains_summary(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test HTML report contains summary section."""
        html = report_generator.generate_html(sample_suite_result)

        assert "Summary" in html
        assert "Total Tests" in html
        assert "Pass Rate" in html
        assert "50" in html  # 50% pass rate

    def test_generate_html_contains_test_results(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test HTML report contains test results."""
        html = report_generator.generate_html(sample_suite_result)

        assert "Test Flight Booking Flow" in html
        assert "Test Error Handling" in html
        assert "test-001" in html

    def test_generate_html_contains_quality_metrics(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test HTML report contains quality metrics."""
        html = report_generator.generate_html(sample_suite_result)

        assert "Quality Metrics" in html
        assert "Coherence" in html
        assert "Naturalness" in html

    def test_generate_html_with_coverage(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
        sample_coverage_report: CoverageReport,
    ):
        """Test HTML report with coverage data."""
        html = report_generator.generate_html(
            sample_suite_result, coverage=sample_coverage_report
        )

        assert "Coverage Analysis" in html
        assert "Intent" in html
        assert "Entity" in html
        assert "80" in html  # 80% intent coverage

    def test_generate_html_with_trends(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
        sample_trends: TrendAnalysis,
    ):
        """Test HTML report with trend data."""
        html = report_generator.generate_html(sample_suite_result, trends=sample_trends)

        assert "Trend Analysis" in html
        assert "improving" in html

    def test_generate_html_failures_section(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test HTML report contains failures section."""
        html = report_generator.generate_html(sample_suite_result)

        assert "Failed Assertions" in html
        assert "Intent mismatch" in html

    def test_generate_html_collapsible_sections(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test HTML report has collapsible sections."""
        html = report_generator.generate_html(sample_suite_result)

        assert "toggleSection" in html
        assert "collapsed" in html

    def test_generate_html_styling(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test HTML report contains proper styling."""
        html = report_generator.generate_html(sample_suite_result)

        assert "<style>" in html
        assert "--pass-color" in html
        assert "--fail-color" in html
        assert "card" in html


# ============================================
# Test JUnit XML Report Generation
# ============================================


class TestJUnitXMLReport:
    """Tests for JUnit XML report generation."""

    def test_generate_junit_xml_basic(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test basic JUnit XML generation."""
        xml = report_generator.generate_junit_xml(sample_suite_result)

        assert '<?xml version="1.0"' in xml
        assert "<testsuite" in xml
        assert "</testsuite>" in xml

    def test_generate_junit_xml_valid(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test JUnit XML is valid XML."""
        xml = report_generator.generate_junit_xml(sample_suite_result)

        # Remove XML declaration for parsing
        xml_content = xml.split("?>", 1)[1] if "?>" in xml else xml
        root = ET.fromstring(xml_content)

        assert root.tag == "testsuite"
        assert root.get("name") == "Flight Booking Test Suite"

    def test_generate_junit_xml_attributes(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test JUnit XML has correct attributes."""
        xml = report_generator.generate_junit_xml(sample_suite_result)
        xml_content = xml.split("?>", 1)[1]
        root = ET.fromstring(xml_content)

        assert root.get("tests") == "2"
        assert root.get("failures") == "1"
        assert root.get("errors") == "0"
        assert root.get("skipped") == "0"

    def test_generate_junit_xml_testcases(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test JUnit XML contains test cases."""
        xml = report_generator.generate_junit_xml(sample_suite_result)
        xml_content = xml.split("?>", 1)[1]
        root = ET.fromstring(xml_content)

        testcases = root.findall("testcase")
        assert len(testcases) == 2

        names = [tc.get("name") for tc in testcases]
        assert "Test Flight Booking Flow" in names
        assert "Test Error Handling" in names

    def test_generate_junit_xml_failure_element(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test JUnit XML contains failure elements for failed tests."""
        xml = report_generator.generate_junit_xml(sample_suite_result)
        xml_content = xml.split("?>", 1)[1]
        root = ET.fromstring(xml_content)

        failures = root.findall(".//failure")
        assert len(failures) == 1
        assert failures[0].get("type") == "AssertionError"

    def test_generate_junit_xml_properties(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test JUnit XML contains properties."""
        xml = report_generator.generate_junit_xml(sample_suite_result)
        xml_content = xml.split("?>", 1)[1]
        root = ET.fromstring(xml_content)

        properties = root.find("properties")
        assert properties is not None

        props = {p.get("name"): p.get("value") for p in properties.findall("property")}
        assert "suite_id" in props
        assert "pass_rate" in props

    def test_generate_junit_xml_system_out(
        self,
        report_generator_with_config: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test JUnit XML contains system-out for logs."""
        xml = report_generator_with_config.generate_junit_xml(sample_suite_result)
        xml_content = xml.split("?>", 1)[1]
        root = ET.fromstring(xml_content)

        system_outs = root.findall(".//system-out")
        # Should have system-out for test with logs
        assert len(system_outs) >= 1


# ============================================
# Test JSON Report Generation
# ============================================


class TestJSONReport:
    """Tests for JSON report generation."""

    def test_generate_json_basic(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test basic JSON generation."""
        json_str = report_generator.generate_json(sample_suite_result)

        data = json.loads(json_str)
        assert "metadata" in data
        assert "suite" in data

    def test_generate_json_metadata(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test JSON metadata section."""
        json_str = report_generator.generate_json(sample_suite_result)

        data = json.loads(json_str)
        assert "generated_at" in data["metadata"]
        assert "generator_version" in data["metadata"]
        assert data["metadata"]["report_format"] == "json"

    def test_generate_json_suite_data(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test JSON suite data."""
        json_str = report_generator.generate_json(sample_suite_result)

        data = json.loads(json_str)
        suite = data["suite"]
        assert suite["suite_id"] == "suite-001"
        assert suite["suite_name"] == "Flight Booking Test Suite"
        assert suite["status"] == "failed"

    def test_generate_json_summary(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test JSON summary section."""
        json_str = report_generator.generate_json(sample_suite_result)

        data = json.loads(json_str)
        summary = data["suite"]["summary"]
        assert summary["total_tests"] == 2
        assert summary["passed"] == 1
        assert summary["failed"] == 1
        assert summary["pass_rate"] == 0.5

    def test_generate_json_test_results(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test JSON test results."""
        json_str = report_generator.generate_json(sample_suite_result)

        data = json.loads(json_str)
        results = data["suite"]["test_results"]
        assert len(results) == 2

        test_ids = [r["test_id"] for r in results]
        assert "test-001" in test_ids
        assert "test-002" in test_ids

    def test_generate_json_quality_scores(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test JSON quality scores."""
        json_str = report_generator.generate_json(sample_suite_result)

        data = json.loads(json_str)
        result = data["suite"]["test_results"][0]
        scores = result["quality_scores"]

        assert "coherence" in scores
        assert "naturalness" in scores
        assert "accuracy" in scores
        assert scores["coherence"] == 0.92

    def test_generate_json_with_coverage(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
        sample_coverage_report: CoverageReport,
    ):
        """Test JSON with coverage data."""
        json_str = report_generator.generate_json(
            sample_suite_result, coverage=sample_coverage_report
        )

        data = json.loads(json_str)
        assert "coverage" in data
        assert data["coverage"]["schema_name"] == "Flight Booking Schema"
        assert data["coverage"]["overall_score"] == 0.74

    def test_generate_json_with_trends(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
        sample_trends: TrendAnalysis,
    ):
        """Test JSON with trend data."""
        json_str = report_generator.generate_json(
            sample_suite_result, trends=sample_trends
        )

        data = json.loads(json_str)
        assert "trends" in data
        assert data["trends"]["pass_rate_trend"] == "improving"
        assert len(data["trends"]["data_points"]) == 2


# ============================================
# Test Markdown Report Generation
# ============================================


class TestMarkdownReport:
    """Tests for Markdown report generation."""

    def test_generate_markdown_basic(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test basic Markdown generation."""
        md = report_generator.generate_markdown(sample_suite_result)

        assert "# " in md  # Has heading
        assert "Test Report" in md
        assert "Flight Booking Test Suite" in md

    def test_generate_markdown_status_emoji(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
        sample_passing_suite_result: TestSuiteResult,
    ):
        """Test Markdown has correct status emoji."""
        failed_md = report_generator.generate_markdown(sample_suite_result)
        passed_md = report_generator.generate_markdown(sample_passing_suite_result)

        assert "❌" in failed_md
        assert "✅" in passed_md

    def test_generate_markdown_summary_table(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test Markdown has summary table."""
        md = report_generator.generate_markdown(sample_suite_result)

        assert "## Summary" in md
        assert "| Metric | Value |" in md
        assert "| Total Tests | 2 |" in md

    def test_generate_markdown_quality_section(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test Markdown has quality section."""
        md = report_generator.generate_markdown(sample_suite_result)

        assert "## Quality Metrics" in md
        assert "Coherence" in md
        assert "Naturalness" in md

    def test_generate_markdown_with_coverage(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
        sample_coverage_report: CoverageReport,
    ):
        """Test Markdown with coverage data."""
        md = report_generator.generate_markdown(
            sample_suite_result, coverage=sample_coverage_report
        )

        assert "## Coverage Analysis" in md
        assert "Overall Score" in md
        assert "74" in md  # 74% overall

    def test_generate_markdown_with_trends(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
        sample_trends: TrendAnalysis,
    ):
        """Test Markdown with trend data."""
        md = report_generator.generate_markdown(
            sample_suite_result, trends=sample_trends
        )

        assert "## Trend Analysis" in md
        assert "improving" in md
        assert "📈" in md

    def test_generate_markdown_failures_section(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test Markdown has failures section."""
        md = report_generator.generate_markdown(sample_suite_result)

        assert "## Failed Tests" in md
        assert "Test Error Handling" in md

    def test_generate_markdown_collapsible_details(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test Markdown has collapsible test details."""
        md = report_generator.generate_markdown(sample_suite_result)

        assert "<details>" in md
        assert "<summary>" in md
        assert "</details>" in md


# ============================================
# Test Coverage Report Generation
# ============================================


class TestCoverageReport:
    """Tests for standalone coverage report generation."""

    def test_generate_coverage_report(
        self,
        report_generator: ReportGenerator,
        sample_coverage_report: CoverageReport,
    ):
        """Test coverage report generation."""
        md = report_generator.generate_coverage_report(sample_coverage_report)

        assert "# Coverage Report" in md
        assert "Flight Booking Schema" in md
        assert "74" in md  # 74% overall

    def test_generate_coverage_report_metrics(
        self,
        report_generator: ReportGenerator,
        sample_coverage_report: CoverageReport,
    ):
        """Test coverage report metrics table."""
        md = report_generator.generate_coverage_report(sample_coverage_report)

        assert "## Coverage Metrics" in md
        assert "| Dimension | Covered | Total | Percentage | Target | Status |" in md
        assert "Intent" in md
        assert "Entity" in md

    def test_generate_coverage_report_gaps(
        self,
        report_generator: ReportGenerator,
        sample_coverage_report: CoverageReport,
    ):
        """Test coverage report gaps section."""
        md = report_generator.generate_coverage_report(sample_coverage_report)

        assert "## Coverage Gaps" in md
        assert "Departure Time Entity" in md

    def test_generate_coverage_report_suggestions(
        self,
        report_generator: ReportGenerator,
        sample_coverage_report: CoverageReport,
    ):
        """Test coverage report suggestions section."""
        md = report_generator.generate_coverage_report(sample_coverage_report)

        assert "## Suggested Tests" in md
        assert "Test Departure Time Extraction" in md


# ============================================
# Test Report Format Selection
# ============================================


class TestReportFormat:
    """Tests for report format selection."""

    def test_generate_report_html(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test generate_report with HTML format."""
        report = report_generator.generate_report(
            sample_suite_result, ReportFormat.HTML
        )

        assert "<!DOCTYPE html>" in report

    def test_generate_report_junit(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test generate_report with JUnit XML format."""
        report = report_generator.generate_report(
            sample_suite_result, ReportFormat.JUNIT_XML
        )

        assert '<?xml version="1.0"' in report
        assert "<testsuite" in report

    def test_generate_report_json(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test generate_report with JSON format."""
        report = report_generator.generate_report(
            sample_suite_result, ReportFormat.JSON
        )

        data = json.loads(report)
        assert "suite" in data

    def test_generate_report_markdown(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test generate_report with Markdown format."""
        report = report_generator.generate_report(
            sample_suite_result, ReportFormat.MARKDOWN
        )

        assert "# " in report
        assert "Test Report" in report


# ============================================
# Test File Export
# ============================================


class TestFileExport:
    """Tests for file export functionality."""

    def test_export_to_file_html(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test exporting HTML to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_generator.config.output_dir = tmpdir
            html = report_generator.generate_html(sample_suite_result)

            filepath = report_generator.export_to_file(
                html, "test_report", ReportFormat.HTML
            )

            assert filepath.endswith(".html")
            assert Path(filepath).exists()
            assert Path(filepath).read_text() == html

    def test_export_to_file_xml(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test exporting JUnit XML to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_generator.config.output_dir = tmpdir
            xml = report_generator.generate_junit_xml(sample_suite_result)

            filepath = report_generator.export_to_file(
                xml, "test_report", ReportFormat.JUNIT_XML
            )

            assert filepath.endswith(".xml")
            assert Path(filepath).exists()

    def test_export_to_file_json(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test exporting JSON to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_generator.config.output_dir = tmpdir
            json_str = report_generator.generate_json(sample_suite_result)

            filepath = report_generator.export_to_file(
                json_str, "test_report", ReportFormat.JSON
            )

            assert filepath.endswith(".json")
            assert Path(filepath).exists()

    def test_export_to_file_markdown(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test exporting Markdown to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_generator.config.output_dir = tmpdir
            md = report_generator.generate_markdown(sample_suite_result)

            filepath = report_generator.export_to_file(
                md, "test_report", ReportFormat.MARKDOWN
            )

            assert filepath.endswith(".md")
            assert Path(filepath).exists()

    def test_export_creates_directory(
        self,
        report_generator: ReportGenerator,
        sample_suite_result: TestSuiteResult,
    ):
        """Test export creates output directory if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_dir = os.path.join(tmpdir, "nested", "reports")
            report_generator.config.output_dir = nested_dir
            html = report_generator.generate_html(sample_suite_result)

            filepath = report_generator.export_to_file(
                html, "test_report", ReportFormat.HTML
            )

            assert Path(nested_dir).exists()
            assert Path(filepath).exists()


# ============================================
# Test Data Types
# ============================================


class TestDataTypes:
    """Tests for report data types."""

    def test_report_config_defaults(self):
        """Test ReportConfig default values."""
        config = ReportConfig()
        assert config.include_logs is True
        assert config.include_turn_details is True
        assert config.include_quality_breakdown is True
        assert config.max_log_lines == 100

    def test_trend_data_point(self):
        """Test TrendDataPoint creation."""
        point = TrendDataPoint(
            timestamp="2024-01-15T10:00:00Z",
            pass_rate=0.85,
            avg_quality_score=0.90,
            total_tests=50,
            avg_duration_ms=1200.0,
        )
        assert point.pass_rate == 0.85
        assert point.total_tests == 50

    def test_trend_analysis(self):
        """Test TrendAnalysis creation."""
        trends = TrendAnalysis(
            pass_rate_trend="improving",
            quality_trend="stable",
            performance_trend="declining",
        )
        assert trends.pass_rate_trend == "improving"
        assert trends.quality_trend == "stable"

    def test_report_metadata(self):
        """Test ReportMetadata creation."""
        metadata = ReportMetadata(
            generated_at="2024-01-15T10:00:00Z",
            generator_version="1.0.0",
            report_format="html",
            title="Test Report",
        )
        assert metadata.generator_version == "1.0.0"
        assert metadata.title == "Test Report"

    def test_test_report(
        self,
        sample_suite_result: TestSuiteResult,
        sample_coverage_report: CoverageReport,
        sample_trends: TrendAnalysis,
    ):
        """Test TestReport creation."""
        report = TestReport(
            metadata=ReportMetadata(
                generated_at="2024-01-15T10:00:00Z",
                report_format="json",
            ),
            suite_result=sample_suite_result,
            coverage=sample_coverage_report,
            trends=sample_trends,
        )
        assert report.suite_result.suite_id == "suite-001"
        assert report.coverage is not None
        assert report.trends is not None


# ============================================
# Test Edge Cases
# ============================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_test_results(self, report_generator: ReportGenerator):
        """Test report generation with empty results."""
        empty_suite = TestSuiteResult(
            suite_id="empty-suite",
            suite_name="Empty Suite",
            status=TestStatus.PASSED,
            started_at="2024-01-15T10:00:00Z",
            completed_at="2024-01-15T10:00:00Z",
            duration_ms=0,
            summary=SuiteSummary(
                total_tests=0,
                passed=0,
                failed=0,
                errors=0,
                skipped=0,
                pass_rate=1.0,
                avg_duration_ms=0.0,
            ),
            test_results=[],
        )

        # Should not raise
        html = report_generator.generate_html(empty_suite)
        assert "Empty Suite" in html

        xml = report_generator.generate_junit_xml(empty_suite)
        assert 'tests="0"' in xml

        json_str = report_generator.generate_json(empty_suite)
        data = json.loads(json_str)
        assert data["suite"]["summary"]["total_tests"] == 0

    def test_special_characters_in_names(
        self, report_generator: ReportGenerator, sample_quality_scores: QualityScores
    ):
        """Test handling of special characters in names."""
        test_result = TestExecutionResult(
            test_id="test-special",
            test_name='Test with "quotes" & <brackets>',
            status=TestStatus.PASSED,
            started_at="2024-01-15T10:00:00Z",
            completed_at="2024-01-15T10:00:01Z",
            duration_ms=1000,
            quality_scores=sample_quality_scores,
        )

        suite = TestSuiteResult(
            suite_id="special-suite",
            suite_name='Suite with <special> & "chars"',
            status=TestStatus.PASSED,
            started_at="2024-01-15T10:00:00Z",
            completed_at="2024-01-15T10:00:01Z",
            duration_ms=1000,
            summary=SuiteSummary(
                total_tests=1,
                passed=1,
                failed=0,
                errors=0,
                skipped=0,
                pass_rate=1.0,
                avg_duration_ms=1000.0,
            ),
            test_results=[test_result],
        )

        # HTML should escape special chars
        html = report_generator.generate_html(suite)
        assert "&lt;" in html or "<special>" not in html.split("<style>")[0]

        # JSON should handle properly
        json_str = report_generator.generate_json(suite)
        data = json.loads(json_str)
        assert data["suite"]["suite_name"] == 'Suite with <special> & "chars"'

    def test_very_long_logs(
        self, report_generator: ReportGenerator, sample_quality_scores: QualityScores
    ):
        """Test handling of very long logs."""
        long_logs = [f"Log line {i}" for i in range(500)]

        test_result = TestExecutionResult(
            test_id="test-logs",
            test_name="Test with many logs",
            status=TestStatus.PASSED,
            started_at="2024-01-15T10:00:00Z",
            completed_at="2024-01-15T10:00:01Z",
            duration_ms=1000,
            quality_scores=sample_quality_scores,
            logs=long_logs,
        )

        suite = TestSuiteResult(
            suite_id="logs-suite",
            suite_name="Logs Suite",
            status=TestStatus.PASSED,
            started_at="2024-01-15T10:00:00Z",
            completed_at="2024-01-15T10:00:01Z",
            duration_ms=1000,
            summary=SuiteSummary(
                total_tests=1,
                passed=1,
                failed=0,
                errors=0,
                skipped=0,
                pass_rate=1.0,
                avg_duration_ms=1000.0,
            ),
            test_results=[test_result],
        )

        # Should respect max_log_lines
        config = ReportConfig(max_log_lines=10)
        generator = ReportGenerator(config)
        xml = generator.generate_junit_xml(suite)

        # Should not contain all 500 lines
        assert "Log line 499" not in xml

    def test_all_test_statuses(
        self, report_generator: ReportGenerator, sample_quality_scores: QualityScores
    ):
        """Test report with all possible test statuses."""
        statuses = [
            TestStatus.PASSED,
            TestStatus.FAILED,
            TestStatus.ERROR,
            TestStatus.SKIPPED,
        ]

        test_results = [
            TestExecutionResult(
                test_id=f"test-{status.value}",
                test_name=f"Test {status.value}",
                status=status,
                started_at="2024-01-15T10:00:00Z",
                completed_at="2024-01-15T10:00:01Z",
                duration_ms=1000,
                quality_scores=sample_quality_scores,
            )
            for status in statuses
        ]

        suite = TestSuiteResult(
            suite_id="status-suite",
            suite_name="All Statuses Suite",
            status=TestStatus.FAILED,
            started_at="2024-01-15T10:00:00Z",
            completed_at="2024-01-15T10:00:04Z",
            duration_ms=4000,
            summary=SuiteSummary(
                total_tests=4,
                passed=1,
                failed=1,
                errors=1,
                skipped=1,
                pass_rate=0.25,
                avg_duration_ms=1000.0,
            ),
            test_results=test_results,
        )

        # All formats should handle all statuses
        html = report_generator.generate_html(suite)
        assert "passed" in html.lower()
        assert "failed" in html.lower()

        xml = report_generator.generate_junit_xml(suite)
        xml_content = xml.split("?>", 1)[1]
        root = ET.fromstring(xml_content)

        assert root.find(".//failure") is not None
        assert root.find(".//error") is not None
        assert root.find(".//skipped") is not None


# ============================================
# Test Configuration Impact
# ============================================


class TestConfigurationImpact:
    """Tests for configuration affecting output."""

    def test_disable_quality_breakdown(self, sample_suite_result: TestSuiteResult):
        """Test disabling quality breakdown."""
        config = ReportConfig(include_quality_breakdown=False)
        generator = ReportGenerator(config)

        # Should not raise - quality section may still be present
        # but with different content
        result = generator.generate_html(sample_suite_result)
        assert "<!DOCTYPE html>" in result

    def test_disable_turn_details(self, sample_suite_result: TestSuiteResult):
        """Test disabling turn details."""
        config = ReportConfig(include_turn_details=False)
        generator = ReportGenerator(config)

        md = generator.generate_markdown(sample_suite_result)
        # Details section should not be present
        assert "<details>" not in md

    def test_disable_logs(self, sample_suite_result: TestSuiteResult):
        """Test disabling logs in output."""
        config = ReportConfig(include_logs=False)
        generator = ReportGenerator(config)

        xml = generator.generate_junit_xml(sample_suite_result)
        # System-out should not be present
        assert "<system-out>" not in xml
