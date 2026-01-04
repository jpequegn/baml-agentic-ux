"""Report Generator for Conversational Testing.

Generate comprehensive test reports in multiple formats (HTML, JUnit XML, JSON, Markdown).

Issue #95 - Task 6.7: Report Generator
Part of #29 - Phase 6: Conversational Testing Framework
"""

import html
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from xml.etree import ElementTree as ET

from .coverage import CoverageReport
from .types import (
    AssertionResult,
    TestExecutionResult,
    TestStatus,
    TestSuiteResult,
)


# ============================================
# Report Format Types
# ============================================


class ReportFormat(Enum):
    """Available report formats."""

    HTML = "html"
    JUNIT_XML = "junit_xml"
    JSON = "json"
    MARKDOWN = "markdown"


# ============================================
# Report Configuration
# ============================================


@dataclass
class ReportConfig:
    """Configuration for report generation."""

    include_logs: bool = True
    include_turn_details: bool = True
    include_quality_breakdown: bool = True
    include_coverage: bool = True
    include_trends: bool = True
    collapsible_sections: bool = True
    max_log_lines: int = 100
    output_dir: Optional[str] = None
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"


# ============================================
# Trend Data Types
# ============================================


@dataclass
class TrendDataPoint:
    """A single data point for trend analysis."""

    timestamp: str
    pass_rate: float
    avg_quality_score: float
    total_tests: int
    avg_duration_ms: float


@dataclass
class TrendAnalysis:
    """Trend analysis over time."""

    data_points: list[TrendDataPoint] = field(default_factory=list)
    pass_rate_trend: str = "stable"  # improving, declining, stable
    quality_trend: str = "stable"
    performance_trend: str = "stable"


# ============================================
# Report Data Types
# ============================================


@dataclass
class ReportMetadata:
    """Metadata for the report."""

    generated_at: str
    generator_version: str = "1.0.0"
    report_format: str = "unknown"
    title: Optional[str] = None


@dataclass
class TestReport:
    """Complete test report data."""

    metadata: ReportMetadata
    suite_result: TestSuiteResult
    coverage: Optional[CoverageReport] = None
    trends: Optional[TrendAnalysis] = None


# ============================================
# Report Generator
# ============================================


class ReportGenerator:
    """Generate test reports in multiple formats."""

    def __init__(self, config: Optional[ReportConfig] = None):
        """Initialize the report generator.

        Args:
            config: Configuration for report generation
        """
        self.config = config or ReportConfig()

    def generate_report(
        self,
        results: TestSuiteResult,
        format: ReportFormat,
        coverage: Optional[CoverageReport] = None,
        trends: Optional[TrendAnalysis] = None,
    ) -> str:
        """Generate a report in the specified format.

        Args:
            results: Test suite execution results
            format: Output format
            coverage: Optional coverage analysis
            trends: Optional trend data

        Returns:
            Report content as string
        """
        if format == ReportFormat.HTML:
            return self.generate_html(results, coverage, trends)
        elif format == ReportFormat.JUNIT_XML:
            return self.generate_junit_xml(results)
        elif format == ReportFormat.JSON:
            return self.generate_json(results, coverage, trends)
        elif format == ReportFormat.MARKDOWN:
            return self.generate_markdown(results, coverage, trends)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def generate_html(
        self,
        results: TestSuiteResult,
        coverage: Optional[CoverageReport] = None,
        trends: Optional[TrendAnalysis] = None,
    ) -> str:
        """Generate HTML report with interactive visualization.

        Args:
            results: Test suite execution results
            coverage: Optional coverage analysis
            trends: Optional trend data

        Returns:
            HTML report content
        """
        summary = results.summary

        # Build HTML sections
        html_parts = [
            self._html_header(results.suite_name),
            self._html_summary_section(results, summary),
        ]

        # Quality metrics section
        if self.config.include_quality_breakdown:
            html_parts.append(self._html_quality_section(results))

        # Coverage section
        if self.config.include_coverage and coverage:
            html_parts.append(self._html_coverage_section(coverage))

        # Trends section
        if self.config.include_trends and trends:
            html_parts.append(self._html_trends_section(trends))

        # Test results section
        html_parts.append(self._html_test_results_section(results))

        # Failed assertions section
        failed_assertions = self._get_failed_assertions(results)
        if failed_assertions:
            html_parts.append(self._html_failures_section(failed_assertions))

        html_parts.append(self._html_footer())

        return "\n".join(html_parts)

    def generate_junit_xml(self, results: TestSuiteResult) -> str:
        """Generate JUnit XML report for CI/CD integration.

        Args:
            results: Test suite execution results

        Returns:
            JUnit XML report content
        """
        # Create root testsuite element
        testsuite = ET.Element("testsuite")
        testsuite.set("name", results.suite_name)
        testsuite.set("tests", str(results.summary.total_tests))
        testsuite.set("failures", str(results.summary.failed))
        testsuite.set("errors", str(results.summary.errors))
        testsuite.set("skipped", str(results.summary.skipped))
        testsuite.set("time", str(results.duration_ms / 1000))
        testsuite.set("timestamp", results.started_at)

        # Add properties
        properties = ET.SubElement(testsuite, "properties")
        self._add_property(properties, "suite_id", results.suite_id)
        self._add_property(properties, "pass_rate", str(results.summary.pass_rate))
        self._add_property(
            properties, "avg_duration_ms", str(results.summary.avg_duration_ms)
        )

        # Add test cases
        for test_result in results.test_results:
            testcase = ET.SubElement(testsuite, "testcase")
            testcase.set("name", test_result.test_name)
            testcase.set("classname", f"conversational.{test_result.test_id}")
            testcase.set("time", str(test_result.duration_ms / 1000))

            if test_result.status == TestStatus.FAILED:
                failure = ET.SubElement(testcase, "failure")
                failure.set("type", "AssertionError")
                if test_result.failure_summary:
                    failure.set(
                        "message",
                        f"Failed {test_result.failure_summary.failed_count} assertions",
                    )
                    failure.text = "\n".join(
                        test_result.failure_summary.critical_failures
                    )
            elif test_result.status == TestStatus.ERROR:
                error = ET.SubElement(testcase, "error")
                error.set("type", "TestError")
                error.set("message", "Test execution error")
                if test_result.logs:
                    error.text = "\n".join(test_result.logs[-10:])
            elif test_result.status == TestStatus.SKIPPED:
                skipped = ET.SubElement(testcase, "skipped")
                skipped.set("message", "Test skipped")

            # Add system-out for logs
            if self.config.include_logs and test_result.logs:
                system_out = ET.SubElement(testcase, "system-out")
                system_out.text = "\n".join(
                    test_result.logs[: self.config.max_log_lines]
                )

        # Convert to string with proper formatting
        ET.indent(testsuite, space="  ")
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        return xml_declaration + ET.tostring(testsuite, encoding="unicode")

    def generate_json(
        self,
        results: TestSuiteResult,
        coverage: Optional[CoverageReport] = None,
        trends: Optional[TrendAnalysis] = None,
    ) -> str:
        """Generate JSON report for programmatic access.

        Args:
            results: Test suite execution results
            coverage: Optional coverage analysis
            trends: Optional trend data

        Returns:
            JSON report content
        """
        report_data = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "metadata": {
                "generated_at": datetime.now().strftime(self.config.timestamp_format),
                "generator_version": "1.0.0",
                "report_format": "json",
            },
            "suite": self._serialize_suite_result(results),
        }

        if coverage:
            report_data["coverage"] = self._serialize_coverage(coverage)

        if trends:
            report_data["trends"] = self._serialize_trends(trends)

        return json.dumps(report_data, indent=2, default=str)

    def generate_markdown(
        self,
        results: TestSuiteResult,
        coverage: Optional[CoverageReport] = None,
        trends: Optional[TrendAnalysis] = None,
    ) -> str:
        """Generate Markdown report for documentation/PR comments.

        Args:
            results: Test suite execution results
            coverage: Optional coverage analysis
            trends: Optional trend data

        Returns:
            Markdown report content
        """
        summary = results.summary
        status_emoji = "✅" if results.status == TestStatus.PASSED else "❌"

        md_parts = [
            f"# {status_emoji} Test Report: {results.suite_name}",
            "",
            f"**Generated:** {datetime.now().strftime(self.config.timestamp_format)}",
            "",
            "## Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Status | {results.status.value} |",
            f"| Total Tests | {summary.total_tests} |",
            f"| Passed | {summary.passed} |",
            f"| Failed | {summary.failed} |",
            f"| Errors | {summary.errors} |",
            f"| Skipped | {summary.skipped} |",
            f"| Pass Rate | {summary.pass_rate:.1%} |",
            f"| Duration | {results.duration_ms}ms |",
            "",
        ]

        # Quality metrics
        if self.config.include_quality_breakdown:
            md_parts.extend(self._markdown_quality_section(results))

        # Coverage section
        if self.config.include_coverage and coverage:
            md_parts.extend(self._markdown_coverage_section(coverage))

        # Trends section
        if self.config.include_trends and trends:
            md_parts.extend(self._markdown_trends_section(trends))

        # Failed tests details
        failed_tests = [
            r for r in results.test_results if r.status == TestStatus.FAILED
        ]
        if failed_tests:
            md_parts.extend(self._markdown_failures_section(failed_tests))

        # Test details (collapsible)
        if self.config.include_turn_details:
            md_parts.extend(self._markdown_test_details_section(results))

        return "\n".join(md_parts)

    def generate_coverage_report(self, coverage: CoverageReport) -> str:
        """Generate a standalone coverage report.

        Args:
            coverage: Coverage analysis results

        Returns:
            Markdown formatted coverage report
        """
        md_parts = [
            "# Coverage Report",
            "",
            f"**Schema:** {coverage.schema_name}",
            f"**Overall Score:** {coverage.overall_score:.1%}",
            f"**Meets All Targets:** {'Yes' if coverage.meets_all_targets else 'No'}",
            "",
            "## Coverage Metrics",
            "",
            "| Dimension | Covered | Total | Percentage | Target | Status |",
            "|-----------|---------|-------|------------|--------|--------|",
        ]

        for metric_name, metric in [
            ("Intent", coverage.intent_coverage.metric),
            ("Entity", coverage.entity_coverage.metric),
            ("Path", coverage.path_coverage.metric),
            ("Edge Case", coverage.edge_case_coverage.metric),
        ]:
            status = "✅" if metric.meets_target else "❌"
            md_parts.append(
                f"| {metric_name} | {metric.covered} | {metric.total} | "
                f"{metric.percentage:.1%} | {metric.target:.0%} | {status} |"
            )

        # Gaps section
        if coverage.gaps:
            md_parts.extend(
                [
                    "",
                    "## Coverage Gaps",
                    "",
                ]
            )
            for gap in coverage.gaps[:10]:  # Limit to top 10
                md_parts.append(
                    f"- **{gap.severity}**: {gap.item_name} ({gap.gap_type})"
                )
                md_parts.append(f"  - {gap.description}")

        # Suggestions section
        if coverage.suggestions:
            md_parts.extend(
                [
                    "",
                    "## Suggested Tests",
                    "",
                ]
            )
            for suggestion in coverage.suggestions[:5]:  # Limit to top 5
                md_parts.append(f"### {suggestion.test_name}")
                md_parts.append(f"- Priority: {suggestion.priority}")
                md_parts.append(
                    f"- Expected Coverage Gain: {suggestion.estimated_coverage_gain:.1%}"
                )
                md_parts.append(f"- {suggestion.test_description}")
                md_parts.append("")

        return "\n".join(md_parts)

    def export_to_file(
        self,
        report_content: str,
        filename: str,
        format: ReportFormat,
    ) -> str:
        """Export report content to a file.

        Args:
            report_content: The report content to write
            filename: Base filename (without extension)
            format: Report format for extension

        Returns:
            Full path to the written file
        """
        extensions = {
            ReportFormat.HTML: ".html",
            ReportFormat.JUNIT_XML: ".xml",
            ReportFormat.JSON: ".json",
            ReportFormat.MARKDOWN: ".md",
        }

        extension = extensions.get(format, ".txt")
        output_dir = Path(self.config.output_dir or ".")
        output_dir.mkdir(parents=True, exist_ok=True)

        filepath = output_dir / f"{filename}{extension}"
        filepath.write_text(report_content, encoding="utf-8")

        return str(filepath)

    # ============================================
    # Private HTML Helper Methods
    # ============================================

    def _html_header(self, title: str) -> str:
        """Generate HTML header with styles."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report: {html.escape(title)}</title>
    <style>
        :root {{
            --pass-color: #22c55e;
            --fail-color: #ef4444;
            --warn-color: #f59e0b;
            --info-color: #3b82f6;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-color: #1e293b;
            --border-color: #e2e8f0;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{
            background: var(--card-bg);
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
            overflow: hidden;
        }}
        .card-header {{
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border-color);
            font-weight: 600;
            font-size: 1.1rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .card-header:hover {{ background: #f1f5f9; }}
        .card-header .toggle {{ color: #94a3b8; }}
        .card-body {{ padding: 1.5rem; }}
        .card-body.collapsed {{ display: none; }}
        h1 {{ font-size: 1.75rem; margin-bottom: 1.5rem; }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }}
        .metric {{
            text-align: center;
            padding: 1rem;
            background: var(--bg-color);
            border-radius: 6px;
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.2;
        }}
        .metric-label {{ font-size: 0.875rem; color: #64748b; }}
        .status-passed {{ color: var(--pass-color); }}
        .status-failed {{ color: var(--fail-color); }}
        .status-error {{ color: var(--fail-color); }}
        .status-skipped {{ color: var(--warn-color); }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{ background: var(--bg-color); font-weight: 600; }}
        tr:hover {{ background: #f8fafc; }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .badge-pass {{ background: #dcfce7; color: #166534; }}
        .badge-fail {{ background: #fee2e2; color: #991b1b; }}
        .badge-error {{ background: #fee2e2; color: #991b1b; }}
        .badge-skip {{ background: #fef3c7; color: #92400e; }}
        .progress-bar {{
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: var(--pass-color);
            transition: width 0.3s ease;
        }}
        .quality-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }}
        .quality-item {{
            padding: 1rem;
            background: var(--bg-color);
            border-radius: 6px;
        }}
        .quality-label {{ font-size: 0.875rem; color: #64748b; margin-bottom: 0.5rem; }}
        .quality-value {{ font-size: 1.25rem; font-weight: 600; }}
        .failure-item {{
            padding: 1rem;
            background: #fef2f2;
            border-left: 4px solid var(--fail-color);
            margin-bottom: 1rem;
            border-radius: 0 6px 6px 0;
        }}
        .failure-title {{ font-weight: 600; color: #991b1b; }}
        .failure-detail {{ font-size: 0.875rem; color: #64748b; margin-top: 0.5rem; }}
        code {{
            background: #f1f5f9;
            padding: 0.125rem 0.375rem;
            border-radius: 3px;
            font-size: 0.875rem;
        }}
        .trend-indicator {{ font-size: 0.875rem; }}
        .trend-up {{ color: var(--pass-color); }}
        .trend-down {{ color: var(--fail-color); }}
        .trend-stable {{ color: #64748b; }}
    </style>
    <script>
        function toggleSection(id) {{
            const body = document.getElementById(id);
            const toggle = document.querySelector(`[data-target="${{id}}"] .toggle`);
            if (body.classList.contains('collapsed')) {{
                body.classList.remove('collapsed');
                toggle.textContent = '▼';
            }} else {{
                body.classList.add('collapsed');
                toggle.textContent = '▶';
            }}
        }}
    </script>
</head>
<body>
<div class="container">
    <h1>Test Report: {html.escape(title)}</h1>
"""

    def _html_footer(self) -> str:
        """Generate HTML footer."""
        timestamp = datetime.now().strftime(self.config.timestamp_format)
        return f"""
    <div style="text-align: center; color: #64748b; font-size: 0.875rem; margin-top: 2rem;">
        Generated at {timestamp} by Conversational Testing Framework
    </div>
</div>
</body>
</html>"""

    def _html_summary_section(self, results: TestSuiteResult, summary: Any) -> str:
        """Generate HTML summary section."""
        status_class = f"status-{results.status.value}"
        pass_rate_pct = summary.pass_rate * 100

        return f"""
    <div class="card">
        <div class="card-header" onclick="toggleSection('summary-body')" data-target="summary-body">
            Summary <span class="toggle">▼</span>
        </div>
        <div class="card-body" id="summary-body">
            <div class="summary-grid">
                <div class="metric">
                    <div class="metric-value {status_class}">{results.status.value.upper()}</div>
                    <div class="metric-label">Status</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary.total_tests}</div>
                    <div class="metric-label">Total Tests</div>
                </div>
                <div class="metric">
                    <div class="metric-value status-passed">{summary.passed}</div>
                    <div class="metric-label">Passed</div>
                </div>
                <div class="metric">
                    <div class="metric-value status-failed">{summary.failed}</div>
                    <div class="metric-label">Failed</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{summary.pass_rate:.1%}</div>
                    <div class="metric-label">Pass Rate</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{results.duration_ms}ms</div>
                    <div class="metric-label">Duration</div>
                </div>
            </div>
            <div style="margin-top: 1.5rem;">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {pass_rate_pct}%"></div>
                </div>
            </div>
        </div>
    </div>"""

    def _html_quality_section(self, results: TestSuiteResult) -> str:
        """Generate HTML quality metrics section."""
        # Aggregate quality scores from all tests
        quality_scores = self._aggregate_quality_scores(results)
        if not quality_scores:
            return ""

        return f"""
    <div class="card">
        <div class="card-header" onclick="toggleSection('quality-body')" data-target="quality-body">
            Quality Metrics <span class="toggle">▼</span>
        </div>
        <div class="card-body" id="quality-body">
            <div class="quality-grid">
                <div class="quality-item">
                    <div class="quality-label">Coherence</div>
                    <div class="quality-value">{quality_scores.get("coherence", 0):.2f}</div>
                </div>
                <div class="quality-item">
                    <div class="quality-label">Naturalness</div>
                    <div class="quality-value">{quality_scores.get("naturalness", 0):.2f}</div>
                </div>
                <div class="quality-item">
                    <div class="quality-label">Accuracy</div>
                    <div class="quality-value">{quality_scores.get("accuracy", 0):.2f}</div>
                </div>
                <div class="quality-item">
                    <div class="quality-label">Relevance</div>
                    <div class="quality-value">{quality_scores.get("relevance", 0):.2f}</div>
                </div>
                <div class="quality-item">
                    <div class="quality-label">Avg Confidence</div>
                    <div class="quality-value">{quality_scores.get("avg_confidence", 0):.2f}</div>
                </div>
                <div class="quality-item">
                    <div class="quality-label">Avg Latency</div>
                    <div class="quality-value">{quality_scores.get("avg_latency_ms", 0):.0f}ms</div>
                </div>
            </div>
        </div>
    </div>"""

    def _html_coverage_section(self, coverage: CoverageReport) -> str:
        """Generate HTML coverage section."""
        metrics = [
            ("Intent", coverage.intent_coverage.metric),
            ("Entity", coverage.entity_coverage.metric),
            ("Path", coverage.path_coverage.metric),
            ("Edge Case", coverage.edge_case_coverage.metric),
        ]

        rows = []
        for name, metric in metrics:
            status_class = "status-passed" if metric.meets_target else "status-failed"
            rows.append(f"""
                <tr>
                    <td>{name}</td>
                    <td>{metric.covered}/{metric.total}</td>
                    <td class="{status_class}">{metric.percentage:.1%}</td>
                    <td>{metric.target:.0%}</td>
                    <td>{metric.level.value}</td>
                </tr>""")

        return f"""
    <div class="card">
        <div class="card-header" onclick="toggleSection('coverage-body')" data-target="coverage-body">
            Coverage Analysis <span class="toggle">▼</span>
        </div>
        <div class="card-body" id="coverage-body">
            <div style="margin-bottom: 1rem;">
                <strong>Overall Score:</strong> {coverage.overall_score:.1%}
                | <strong>Meets All Targets:</strong> {"Yes" if coverage.meets_all_targets else "No"}
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Dimension</th>
                        <th>Coverage</th>
                        <th>Percentage</th>
                        <th>Target</th>
                        <th>Level</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
        </div>
    </div>"""

    def _html_trends_section(self, trends: TrendAnalysis) -> str:
        """Generate HTML trends section."""
        trend_icons = {
            "improving": ("↑", "trend-up"),
            "declining": ("↓", "trend-down"),
            "stable": ("→", "trend-stable"),
        }

        pass_icon, pass_class = trend_icons.get(
            trends.pass_rate_trend, ("→", "trend-stable")
        )
        quality_icon, quality_class = trend_icons.get(
            trends.quality_trend, ("→", "trend-stable")
        )
        perf_icon, perf_class = trend_icons.get(
            trends.performance_trend, ("→", "trend-stable")
        )

        return f"""
    <div class="card">
        <div class="card-header" onclick="toggleSection('trends-body')" data-target="trends-body">
            Trend Analysis <span class="toggle">▼</span>
        </div>
        <div class="card-body" id="trends-body">
            <div class="quality-grid">
                <div class="quality-item">
                    <div class="quality-label">Pass Rate Trend</div>
                    <div class="quality-value">
                        <span class="trend-indicator {pass_class}">{pass_icon}</span>
                        {trends.pass_rate_trend}
                    </div>
                </div>
                <div class="quality-item">
                    <div class="quality-label">Quality Trend</div>
                    <div class="quality-value">
                        <span class="trend-indicator {quality_class}">{quality_icon}</span>
                        {trends.quality_trend}
                    </div>
                </div>
                <div class="quality-item">
                    <div class="quality-label">Performance Trend</div>
                    <div class="quality-value">
                        <span class="trend-indicator {perf_class}">{perf_icon}</span>
                        {trends.performance_trend}
                    </div>
                </div>
            </div>
        </div>
    </div>"""

    def _html_test_results_section(self, results: TestSuiteResult) -> str:
        """Generate HTML test results table."""
        rows = []
        for test in results.test_results:
            status_badge = f"badge-{test.status.value}"
            rows.append(f"""
                <tr>
                    <td><code>{html.escape(test.test_id)}</code></td>
                    <td>{html.escape(test.test_name)}</td>
                    <td><span class="badge {status_badge}">{test.status.value}</span></td>
                    <td>{test.duration_ms}ms</td>
                    <td>{test.quality_scores.coherence:.2f}</td>
                </tr>""")

        return f"""
    <div class="card">
        <div class="card-header" onclick="toggleSection('tests-body')" data-target="tests-body">
            Test Results ({len(results.test_results)} tests) <span class="toggle">▼</span>
        </div>
        <div class="card-body" id="tests-body">
            <table>
                <thead>
                    <tr>
                        <th>Test ID</th>
                        <th>Name</th>
                        <th>Status</th>
                        <th>Duration</th>
                        <th>Coherence</th>
                    </tr>
                </thead>
                <tbody>
                    {"".join(rows)}
                </tbody>
            </table>
        </div>
    </div>"""

    def _html_failures_section(
        self, failures: list[tuple[TestExecutionResult, AssertionResult]]
    ) -> str:
        """Generate HTML failures section."""
        items = []
        for test, assertion in failures[:20]:  # Limit to 20
            items.append(f"""
            <div class="failure-item">
                <div class="failure-title">
                    {html.escape(test.test_name)} - Turn {assertion.turn_number}
                </div>
                <div class="failure-detail">
                    <strong>Assertion:</strong> {assertion.assertion_type.value}<br>
                    <strong>Expected:</strong> <code>{html.escape(str(assertion.expected_value or "N/A"))}</code><br>
                    <strong>Actual:</strong> <code>{html.escape(str(assertion.actual_value or "N/A"))}</code><br>
                    {f"<strong>Message:</strong> {html.escape(assertion.message)}" if assertion.message else ""}
                </div>
            </div>""")

        return f"""
    <div class="card">
        <div class="card-header" onclick="toggleSection('failures-body')" data-target="failures-body">
            Failed Assertions ({len(failures)}) <span class="toggle">▼</span>
        </div>
        <div class="card-body" id="failures-body">
            {"".join(items)}
        </div>
    </div>"""

    # ============================================
    # Private Markdown Helper Methods
    # ============================================

    def _markdown_quality_section(self, results: TestSuiteResult) -> list[str]:
        """Generate markdown quality metrics section."""
        quality_scores = self._aggregate_quality_scores(results)
        if not quality_scores:
            return []

        return [
            "## Quality Metrics",
            "",
            "| Metric | Score |",
            "|--------|-------|",
            f"| Coherence | {quality_scores.get('coherence', 0):.2f} |",
            f"| Naturalness | {quality_scores.get('naturalness', 0):.2f} |",
            f"| Accuracy | {quality_scores.get('accuracy', 0):.2f} |",
            f"| Relevance | {quality_scores.get('relevance', 0):.2f} |",
            f"| Avg Confidence | {quality_scores.get('avg_confidence', 0):.2f} |",
            f"| Avg Latency | {quality_scores.get('avg_latency_ms', 0):.0f}ms |",
            "",
        ]

    def _markdown_coverage_section(self, coverage: CoverageReport) -> list[str]:
        """Generate markdown coverage section."""
        md = [
            "## Coverage Analysis",
            "",
            f"**Overall Score:** {coverage.overall_score:.1%}",
            "",
            "| Dimension | Covered | Total | Percentage | Target | Status |",
            "|-----------|---------|-------|------------|--------|--------|",
        ]

        for name, metric in [
            ("Intent", coverage.intent_coverage.metric),
            ("Entity", coverage.entity_coverage.metric),
            ("Path", coverage.path_coverage.metric),
            ("Edge Case", coverage.edge_case_coverage.metric),
        ]:
            status = "✅" if metric.meets_target else "❌"
            md.append(
                f"| {name} | {metric.covered} | {metric.total} | "
                f"{metric.percentage:.1%} | {metric.target:.0%} | {status} |"
            )

        md.append("")
        return md

    def _markdown_trends_section(self, trends: TrendAnalysis) -> list[str]:
        """Generate markdown trends section."""
        trend_icons = {
            "improving": "📈",
            "declining": "📉",
            "stable": "➡️",
        }

        return [
            "## Trend Analysis",
            "",
            f"- **Pass Rate:** {trend_icons.get(trends.pass_rate_trend, '➡️')} {trends.pass_rate_trend}",
            f"- **Quality:** {trend_icons.get(trends.quality_trend, '➡️')} {trends.quality_trend}",
            f"- **Performance:** {trend_icons.get(trends.performance_trend, '➡️')} {trends.performance_trend}",
            "",
        ]

    def _markdown_failures_section(
        self, failed_tests: list[TestExecutionResult]
    ) -> list[str]:
        """Generate markdown failures section."""
        md = [
            "## Failed Tests",
            "",
        ]

        for test in failed_tests[:10]:  # Limit to 10
            md.append(f"### ❌ {test.test_name}")
            md.append("")
            if test.failure_summary:
                md.append(
                    f"- **Failed Assertions:** {test.failure_summary.failed_count}"
                )
                if test.failure_summary.critical_failures:
                    md.append("- **Critical Failures:**")
                    for failure in test.failure_summary.critical_failures[:3]:
                        md.append(f"  - {failure}")
            md.append("")

        return md

    def _markdown_test_details_section(self, results: TestSuiteResult) -> list[str]:
        """Generate markdown test details section (collapsible)."""
        md = [
            "## Test Details",
            "",
            "<details>",
            "<summary>Click to expand test details</summary>",
            "",
            "| Test | Status | Duration | Coherence |",
            "|------|--------|----------|-----------|",
        ]

        for test in results.test_results:
            status_emoji = {
                TestStatus.PASSED: "✅",
                TestStatus.FAILED: "❌",
                TestStatus.ERROR: "💥",
                TestStatus.SKIPPED: "⏭️",
            }.get(test.status, "❓")

            md.append(
                f"| {test.test_name} | {status_emoji} {test.status.value} | "
                f"{test.duration_ms}ms | {test.quality_scores.coherence:.2f} |"
            )

        md.extend(["", "</details>", ""])
        return md

    # ============================================
    # Private Serialization Methods
    # ============================================

    def _serialize_suite_result(self, results: TestSuiteResult) -> dict[str, Any]:
        """Serialize TestSuiteResult to dict."""
        return {
            "suite_id": results.suite_id,
            "suite_name": results.suite_name,
            "status": results.status.value,
            "started_at": results.started_at,
            "completed_at": results.completed_at,
            "duration_ms": results.duration_ms,
            "summary": {
                "total_tests": results.summary.total_tests,
                "passed": results.summary.passed,
                "failed": results.summary.failed,
                "errors": results.summary.errors,
                "skipped": results.summary.skipped,
                "pass_rate": results.summary.pass_rate,
                "avg_duration_ms": results.summary.avg_duration_ms,
            },
            "test_results": [
                self._serialize_test_result(tr) for tr in results.test_results
            ],
        }

    def _serialize_test_result(self, result: TestExecutionResult) -> dict[str, Any]:
        """Serialize TestExecutionResult to dict."""
        return {
            "test_id": result.test_id,
            "test_name": result.test_name,
            "status": result.status.value,
            "started_at": result.started_at,
            "completed_at": result.completed_at,
            "duration_ms": result.duration_ms,
            "quality_scores": {
                "coherence": result.quality_scores.coherence,
                "naturalness": result.quality_scores.naturalness,
                "accuracy": result.quality_scores.accuracy,
                "relevance": result.quality_scores.relevance,
                "avg_confidence": result.quality_scores.avg_confidence,
                "max_drift_score": result.quality_scores.max_drift_score,
                "avg_latency_ms": result.quality_scores.avg_latency_ms,
            },
            "turn_count": len(result.turn_results),
            "assertion_count": len(result.assertion_results),
            "failure_summary": (
                {
                    "total_assertions": result.failure_summary.total_assertions,
                    "passed_count": result.failure_summary.passed_count,
                    "failed_count": result.failure_summary.failed_count,
                    "first_failure_turn": result.failure_summary.first_failure_turn,
                }
                if result.failure_summary
                else None
            ),
        }

    def _serialize_coverage(self, coverage: CoverageReport) -> dict[str, Any]:
        """Serialize CoverageReport to dict."""
        return {
            "schema_id": coverage.schema_id,
            "schema_name": coverage.schema_name,
            "total_tests": coverage.total_tests,
            "total_assertions": coverage.total_assertions,
            "overall_score": coverage.overall_score,
            "meets_all_targets": coverage.meets_all_targets,
            "metrics": {
                "intent": self._serialize_metric(coverage.intent_coverage.metric),
                "entity": self._serialize_metric(coverage.entity_coverage.metric),
                "path": self._serialize_metric(coverage.path_coverage.metric),
                "edge_case": self._serialize_metric(coverage.edge_case_coverage.metric),
            },
            "gaps_count": len(coverage.gaps),
            "suggestions_count": len(coverage.suggestions),
        }

    def _serialize_metric(self, metric: Any) -> dict[str, Any]:
        """Serialize a coverage metric."""
        return {
            "name": metric.name,
            "covered": metric.covered,
            "total": metric.total,
            "percentage": metric.percentage,
            "target": metric.target,
            "meets_target": metric.meets_target,
            "level": metric.level.value,
        }

    def _serialize_trends(self, trends: TrendAnalysis) -> dict[str, Any]:
        """Serialize TrendAnalysis to dict."""
        return {
            "pass_rate_trend": trends.pass_rate_trend,
            "quality_trend": trends.quality_trend,
            "performance_trend": trends.performance_trend,
            "data_points": [
                {
                    "timestamp": dp.timestamp,
                    "pass_rate": dp.pass_rate,
                    "avg_quality_score": dp.avg_quality_score,
                    "total_tests": dp.total_tests,
                    "avg_duration_ms": dp.avg_duration_ms,
                }
                for dp in trends.data_points
            ],
        }

    # ============================================
    # Private Utility Methods
    # ============================================

    def _add_property(self, parent: ET.Element, name: str, value: str) -> None:
        """Add a property element to JUnit XML."""
        prop = ET.SubElement(parent, "property")
        prop.set("name", name)
        prop.set("value", value)

    def _get_failed_assertions(
        self, results: TestSuiteResult
    ) -> list[tuple[TestExecutionResult, AssertionResult]]:
        """Get all failed assertions from suite results."""
        failures = []
        for test in results.test_results:
            for assertion in test.assertion_results:
                if not assertion.passed:
                    failures.append((test, assertion))
        return failures

    def _aggregate_quality_scores(self, results: TestSuiteResult) -> dict[str, float]:
        """Aggregate quality scores across all tests."""
        if not results.test_results:
            return {}

        scores = {
            "coherence": 0.0,
            "naturalness": 0.0,
            "accuracy": 0.0,
            "relevance": 0.0,
            "avg_confidence": 0.0,
            "max_drift_score": 0.0,
            "avg_latency_ms": 0.0,
        }

        count = len(results.test_results)
        for test in results.test_results:
            qs = test.quality_scores
            scores["coherence"] += qs.coherence
            scores["naturalness"] += qs.naturalness
            scores["accuracy"] += qs.accuracy
            scores["relevance"] += qs.relevance
            scores["avg_confidence"] += qs.avg_confidence
            scores["max_drift_score"] += qs.max_drift_score
            scores["avg_latency_ms"] += qs.avg_latency_ms

        return {k: v / count for k, v in scores.items()}
