"""Accessibility report generator for LUI applications.

This module implements comprehensive accessibility compliance report generation
that aggregates all accessibility checks into actionable documentation.

Issue #76 - Task 4.10: Accessibility Report Generator
Part of #27 - Phase 4: LUI Accessibility Standards
"""

from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .checker import (
    AccessibilityViolation,
    ComplianceLevel,
    ViolationSeverity,
)
from .disability_evaluators import (
    CombinedDisabilityEvaluator,
    DisabilityEvaluation,
    DisabilityType,
)
from .schema_checker import (
    ComponentAccessibilityEval,
    SchemaAccessibilityChecker,
    SchemaAccessibilityResult,
)


# ============================================
# Data Classes
# ============================================


@dataclass
class Recommendation:
    """A prioritized remediation recommendation."""

    priority: str  # "high", "medium", "low"
    title: str
    description: str
    affected_components: list[str] = field(default_factory=list)
    impact: str = ""  # Description of impact if not addressed
    effort: str = ""  # "low", "medium", "high"


@dataclass
class ReportSummary:
    """Executive summary of the accessibility report."""

    total_components: int
    passing_components: int
    critical_violations: int
    major_violations: int
    minor_violations: int
    advisory_count: int
    top_issues: list[str]
    remediation_priority: list[str]


@dataclass
class ComponentReport:
    """Detailed accessibility report for a single component."""

    component_id: str
    component_type: str
    score: float
    passes: bool
    achieved_level: Optional[ComplianceLevel]
    violations: list[AccessibilityViolation]
    recommendations: list[str]


@dataclass
class DisabilityReport:
    """Accessibility report for a specific disability type."""

    disability_type: DisabilityType
    accommodation_score: float
    passes: bool
    barriers_count: int
    critical_barriers: int
    accommodations_present: list[str]
    accommodations_missing: list[str]
    recommendations: list[str]


@dataclass
class AccessibilityReport:
    """Complete accessibility compliance report."""

    schema_name: str
    target_level: ComplianceLevel
    achieved_level: Optional[ComplianceLevel]
    overall_score: float
    passes: bool
    summary: ReportSummary
    component_details: list[ComponentReport]
    disability_coverage: list[DisabilityReport]
    violations: list[AccessibilityViolation]
    recommendations: list[Recommendation]
    generated_at: datetime = field(default_factory=datetime.now)

    @property
    def score_percentage(self) -> int:
        """Overall score as percentage."""
        return int(self.overall_score * 100)

    @property
    def level_badge(self) -> str:
        """Get compliance level badge text."""
        if self.achieved_level:
            return f"Level {self.achieved_level.value}"
        return "Non-Compliant"


# ============================================
# Report Generator Class
# ============================================


class AccessibilityReportGenerator:
    """Generates comprehensive accessibility compliance reports.

    This generator aggregates results from all accessibility checkers into
    a unified report with multiple export formats.
    """

    def __init__(self):
        """Initialize the report generator with required checkers."""
        self._schema_checker = SchemaAccessibilityChecker()
        self._disability_evaluator = CombinedDisabilityEvaluator()

    def generate_report(
        self,
        schema: dict[str, Any],
        target_level: ComplianceLevel = ComplianceLevel.LEVEL_AA,
    ) -> AccessibilityReport:
        """Generate a comprehensive accessibility report.

        Args:
            schema: The LUI schema dictionary to evaluate
            target_level: Target compliance level (default: AA)

        Returns:
            AccessibilityReport with complete analysis
        """
        # Run schema accessibility check
        schema_result = self._schema_checker.check_schema(schema, target_level)

        # Run disability evaluations
        disability_results = self._disability_evaluator.evaluate(schema)
        disability_evals = list(disability_results.values())

        # Build component reports
        component_reports = self._build_component_reports(schema_result)

        # Build disability reports
        disability_reports = self._build_disability_reports(disability_evals)

        # Aggregate violations
        all_violations = list(schema_result.violations)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            schema_result, disability_evals, all_violations
        )

        # Build summary
        summary = self._build_summary(
            schema_result, all_violations, recommendations
        )

        return AccessibilityReport(
            schema_name=schema_result.schema_name,
            target_level=target_level,
            achieved_level=schema_result.achieved_level,
            overall_score=schema_result.overall_score,
            passes=schema_result.passes,
            summary=summary,
            component_details=component_reports,
            disability_coverage=disability_reports,
            violations=all_violations,
            recommendations=recommendations,
        )

    def _build_component_reports(
        self,
        schema_result: SchemaAccessibilityResult,
    ) -> list[ComponentReport]:
        """Build component reports from schema result."""
        reports = []
        for comp_eval in schema_result.component_evaluations:
            reports.append(
                ComponentReport(
                    component_id=comp_eval.component_id,
                    component_type=comp_eval.component_type,
                    score=comp_eval.score,
                    passes=comp_eval.passes,
                    achieved_level=comp_eval.achieved_level,
                    violations=list(comp_eval.violations),
                    recommendations=self._component_recommendations(comp_eval),
                )
            )
        return reports

    def _component_recommendations(
        self,
        comp_eval: ComponentAccessibilityEval,
    ) -> list[str]:
        """Generate recommendations for a component."""
        recommendations = []
        seen = set()

        for v in comp_eval.violations:
            if v.remediation not in seen:
                recommendations.append(v.remediation)
                seen.add(v.remediation)

        return recommendations[:5]  # Limit to top 5

    def _build_disability_reports(
        self,
        disability_evals: list[DisabilityEvaluation],
    ) -> list[DisabilityReport]:
        """Build disability reports from evaluations."""
        reports = []
        for eval_ in disability_evals:
            reports.append(
                DisabilityReport(
                    disability_type=eval_.disability_type,
                    accommodation_score=eval_.accommodation_score,
                    passes=eval_.passes,
                    barriers_count=eval_.total_barriers,
                    critical_barriers=eval_.critical_barriers,
                    accommodations_present=list(eval_.accommodations_present),
                    accommodations_missing=list(eval_.accommodations_missing),
                    recommendations=list(eval_.recommendations),
                )
            )
        return reports

    def _generate_recommendations(
        self,
        schema_result: SchemaAccessibilityResult,
        disability_evals: list[DisabilityEvaluation],
        violations: list[AccessibilityViolation],
    ) -> list[Recommendation]:
        """Generate prioritized recommendations."""
        recommendations = []

        # Group violations by remediation
        remediation_groups: dict[str, list[AccessibilityViolation]] = {}
        for v in violations:
            if v.remediation not in remediation_groups:
                remediation_groups[v.remediation] = []
            remediation_groups[v.remediation].append(v)

        # Create recommendations from grouped violations
        for remediation, group_violations in remediation_groups.items():
            # Determine priority based on severity
            has_critical = any(
                v.severity == ViolationSeverity.CRITICAL for v in group_violations
            )
            has_major = any(
                v.severity == ViolationSeverity.MAJOR for v in group_violations
            )

            if has_critical:
                priority = "high"
            elif has_major:
                priority = "medium"
            else:
                priority = "low"

            # Get affected components
            affected = []
            for v in group_violations:
                if v.element and v.element not in affected:
                    affected.append(v.element[:50])  # Truncate long elements

            recommendations.append(
                Recommendation(
                    priority=priority,
                    title=remediation,
                    description=f"Affects {len(group_violations)} instance(s)",
                    affected_components=affected[:5],
                    impact=self._determine_impact(group_violations),
                    effort=self._estimate_effort(len(group_violations)),
                )
            )

        # Add disability-specific recommendations
        for eval_ in disability_evals:
            if not eval_.passes:
                for rec in eval_.recommendations[:2]:
                    recommendations.append(
                        Recommendation(
                            priority="medium" if eval_.critical_barriers > 0 else "low",
                            title=f"{eval_.disability_type.value.title()} accessibility",
                            description=rec,
                            impact=f"Affects users with {eval_.disability_type.value} disabilities",
                            effort="medium",
                        )
                    )

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 3))

        return recommendations[:15]  # Limit to top 15

    def _determine_impact(self, violations: list[AccessibilityViolation]) -> str:
        """Determine the impact of violations."""
        has_critical = any(v.severity == ViolationSeverity.CRITICAL for v in violations)
        has_major = any(v.severity == ViolationSeverity.MAJOR for v in violations)

        if has_critical:
            return "Blocks accessibility - users cannot access content"
        elif has_major:
            return "Significant barrier - affects user experience"
        return "Minor impact - reduces usability"

    def _estimate_effort(self, count: int) -> str:
        """Estimate remediation effort."""
        if count <= 2:
            return "low"
        elif count <= 5:
            return "medium"
        return "high"

    def _build_summary(
        self,
        schema_result: SchemaAccessibilityResult,
        violations: list[AccessibilityViolation],
        recommendations: list[Recommendation],
    ) -> ReportSummary:
        """Build executive summary."""
        # Count by severity
        critical = sum(1 for v in violations if v.severity == ViolationSeverity.CRITICAL)
        major = sum(1 for v in violations if v.severity == ViolationSeverity.MAJOR)
        minor = sum(1 for v in violations if v.severity == ViolationSeverity.MINOR)
        advisory = sum(1 for v in violations if v.severity == ViolationSeverity.ADVISORY)

        # Get top issues (unique descriptions by severity)
        top_issues = []
        seen_issues = set()
        sorted_violations = sorted(
            violations,
            key=lambda v: [
                ViolationSeverity.CRITICAL,
                ViolationSeverity.MAJOR,
                ViolationSeverity.MINOR,
                ViolationSeverity.ADVISORY,
            ].index(v.severity),
        )
        for v in sorted_violations:
            if v.description not in seen_issues:
                top_issues.append(v.description)
                seen_issues.add(v.description)
                if len(top_issues) >= 5:
                    break

        # Get remediation priorities
        remediation_priority = [r.title for r in recommendations if r.priority == "high"]
        remediation_priority.extend(
            [r.title for r in recommendations if r.priority == "medium"][:3]
        )

        return ReportSummary(
            total_components=schema_result.total_components,
            passing_components=schema_result.passing_components,
            critical_violations=critical,
            major_violations=major,
            minor_violations=minor,
            advisory_count=advisory,
            top_issues=top_issues[:5],
            remediation_priority=remediation_priority[:5],
        )

    # ============================================
    # Export Methods
    # ============================================

    def export_markdown(self, report: AccessibilityReport) -> str:
        """Export report to Markdown format.

        Args:
            report: The accessibility report to export

        Returns:
            Markdown-formatted string
        """
        lines = []

        # Header
        lines.append("# LUI Accessibility Report")
        lines.append("")
        lines.append(f"**Schema**: {report.schema_name}")
        lines.append(f"**Target Level**: {report.target_level.value}")
        lines.append(f"**Achieved Level**: {report.level_badge}")
        lines.append(f"**Overall Score**: {report.score_percentage}%")
        lines.append(f"**Status**: {'PASS' if report.passes else 'FAIL'}")
        lines.append(f"**Generated**: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Summary table
        lines.append("## Summary")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Components | {report.summary.total_components} |")
        lines.append(f"| Passing Components | {report.summary.passing_components} |")
        lines.append(f"| Critical Violations | {report.summary.critical_violations} |")
        lines.append(f"| Major Violations | {report.summary.major_violations} |")
        lines.append(f"| Minor Violations | {report.summary.minor_violations} |")
        lines.append(f"| Advisory Notices | {report.summary.advisory_count} |")
        lines.append("")

        # Top Issues
        if report.summary.top_issues:
            lines.append("## Top Issues")
            lines.append("")
            for i, issue in enumerate(report.summary.top_issues, 1):
                lines.append(f"{i}. {issue}")
            lines.append("")

        # Recommendations
        if report.recommendations:
            lines.append("## Recommendations")
            lines.append("")
            for rec in report.recommendations:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                    rec.priority, "⚪"
                )
                lines.append(f"### {priority_icon} {rec.title}")
                lines.append("")
                lines.append(f"**Priority**: {rec.priority.title()}")
                lines.append(f"**Impact**: {rec.impact}")
                lines.append(f"**Effort**: {rec.effort.title()}")
                lines.append("")
                if rec.affected_components:
                    lines.append("Affected areas:")
                    for comp in rec.affected_components[:3]:
                        lines.append(f"- {comp}")
                    lines.append("")

        # Component Details
        if report.component_details:
            lines.append("## Component Details")
            lines.append("")
            for comp in report.component_details:
                status = "✅" if comp.passes else "❌"
                lines.append(f"### {status} {comp.component_id}")
                lines.append("")
                lines.append(f"- **Type**: {comp.component_type}")
                lines.append(f"- **Score**: {int(comp.score * 100)}%")
                level = comp.achieved_level.value if comp.achieved_level else "None"
                lines.append(f"- **Achieved Level**: {level}")
                lines.append(f"- **Violations**: {len(comp.violations)}")
                lines.append("")
                if comp.recommendations:
                    lines.append("Recommendations:")
                    for rec in comp.recommendations[:3]:
                        lines.append(f"- {rec}")
                    lines.append("")

        # Disability Coverage
        if report.disability_coverage:
            lines.append("## Disability Coverage")
            lines.append("")
            lines.append("| Disability Type | Score | Status | Barriers |")
            lines.append("|-----------------|-------|--------|----------|")
            for dis in report.disability_coverage:
                status = "✅ Pass" if dis.passes else "❌ Fail"
                lines.append(
                    f"| {dis.disability_type.value.title()} | "
                    f"{int(dis.accommodation_score * 100)}% | "
                    f"{status} | "
                    f"{dis.barriers_count} ({dis.critical_barriers} critical) |"
                )
            lines.append("")

        # Violations Detail
        if report.violations:
            lines.append("## Violations Detail")
            lines.append("")
            for v in report.violations[:20]:  # Limit to 20
                severity_icon = {
                    ViolationSeverity.CRITICAL: "🔴",
                    ViolationSeverity.MAJOR: "🟠",
                    ViolationSeverity.MINOR: "🟡",
                    ViolationSeverity.ADVISORY: "🔵",
                }.get(v.severity, "⚪")
                lines.append(f"- {severity_icon} **{v.criterion}**: {v.description}")
                lines.append(f"  - Remediation: {v.remediation}")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append("*Report generated by LUI Accessibility Report Generator*")

        return "\n".join(lines)

    def export_json(self, report: AccessibilityReport) -> dict[str, Any]:
        """Export report to JSON-serializable dictionary.

        Args:
            report: The accessibility report to export

        Returns:
            Dictionary suitable for JSON serialization
        """
        return {
            "schema_name": report.schema_name,
            "target_level": report.target_level.value,
            "achieved_level": report.achieved_level.value if report.achieved_level else None,
            "overall_score": report.overall_score,
            "score_percentage": report.score_percentage,
            "passes": report.passes,
            "generated_at": report.generated_at.isoformat(),
            "summary": {
                "total_components": report.summary.total_components,
                "passing_components": report.summary.passing_components,
                "critical_violations": report.summary.critical_violations,
                "major_violations": report.summary.major_violations,
                "minor_violations": report.summary.minor_violations,
                "advisory_count": report.summary.advisory_count,
                "top_issues": report.summary.top_issues,
                "remediation_priority": report.summary.remediation_priority,
            },
            "component_details": [
                {
                    "component_id": c.component_id,
                    "component_type": c.component_type,
                    "score": c.score,
                    "passes": c.passes,
                    "achieved_level": c.achieved_level.value if c.achieved_level else None,
                    "violation_count": len(c.violations),
                    "recommendations": c.recommendations,
                }
                for c in report.component_details
            ],
            "disability_coverage": [
                {
                    "disability_type": d.disability_type.value,
                    "accommodation_score": d.accommodation_score,
                    "passes": d.passes,
                    "barriers_count": d.barriers_count,
                    "critical_barriers": d.critical_barriers,
                    "accommodations_present": d.accommodations_present,
                    "accommodations_missing": d.accommodations_missing,
                    "recommendations": d.recommendations,
                }
                for d in report.disability_coverage
            ],
            "violations": [
                {
                    "criterion": v.criterion,
                    "severity": v.severity.value,
                    "description": v.description,
                    "remediation": v.remediation,
                    "element": v.element,
                    "line_number": v.line_number,
                }
                for v in report.violations
            ],
            "recommendations": [
                {
                    "priority": r.priority,
                    "title": r.title,
                    "description": r.description,
                    "affected_components": r.affected_components,
                    "impact": r.impact,
                    "effort": r.effort,
                }
                for r in report.recommendations
            ],
        }

    def export_html(self, report: AccessibilityReport) -> str:
        """Export report to HTML format with styling.

        Args:
            report: The accessibility report to export

        Returns:
            HTML-formatted string
        """
        # Escape helper
        def esc(text: str) -> str:
            return html.escape(str(text))

        # Badge colors
        def get_level_color(level: Optional[ComplianceLevel]) -> str:
            if level == ComplianceLevel.LEVEL_AAA:
                return "#22c55e"  # green
            elif level == ComplianceLevel.LEVEL_AA:
                return "#3b82f6"  # blue
            elif level == ComplianceLevel.LEVEL_A:
                return "#f59e0b"  # amber
            return "#ef4444"  # red

        def get_severity_color(severity: ViolationSeverity) -> str:
            return {
                ViolationSeverity.CRITICAL: "#ef4444",  # red
                ViolationSeverity.MAJOR: "#f97316",  # orange
                ViolationSeverity.MINOR: "#eab308",  # yellow
                ViolationSeverity.ADVISORY: "#3b82f6",  # blue
            }.get(severity, "#6b7280")

        def get_priority_color(priority: str) -> str:
            return {
                "high": "#ef4444",
                "medium": "#f59e0b",
                "low": "#22c55e",
            }.get(priority, "#6b7280")

        level_color = get_level_color(report.achieved_level)
        status_color = "#22c55e" if report.passes else "#ef4444"

        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accessibility Report - {esc(report.schema_name)}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #1f2937;
            background: #f9fafb;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ font-size: 2rem; margin-bottom: 1rem; }}
        h2 {{ font-size: 1.5rem; margin: 2rem 0 1rem; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem; }}
        h3 {{ font-size: 1.25rem; margin: 1.5rem 0 0.75rem; }}

        .header {{
            background: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}
        .header-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}
        .header-item {{ text-align: center; padding: 1rem; background: #f9fafb; border-radius: 0.375rem; }}
        .header-label {{ font-size: 0.875rem; color: #6b7280; }}
        .header-value {{ font-size: 1.5rem; font-weight: 600; }}

        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
            color: white;
        }}

        .score-meter {{
            width: 100%;
            height: 1.5rem;
            background: #e5e7eb;
            border-radius: 0.375rem;
            overflow: hidden;
            margin: 1rem 0;
        }}
        .score-fill {{
            height: 100%;
            border-radius: 0.375rem;
            transition: width 0.5s ease;
        }}

        .card {{
            background: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }}
        th {{ background: #f9fafb; font-weight: 600; }}

        .violation {{
            padding: 0.75rem;
            border-left: 4px solid;
            margin-bottom: 0.5rem;
            background: #f9fafb;
            border-radius: 0 0.25rem 0.25rem 0;
        }}

        .recommendation {{
            border-left: 4px solid;
            padding: 1rem;
            margin-bottom: 1rem;
            background: white;
        }}

        .grid-2 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }}

        .tag {{
            display: inline-block;
            padding: 0.125rem 0.5rem;
            background: #e5e7eb;
            border-radius: 0.25rem;
            font-size: 0.75rem;
            margin-right: 0.25rem;
        }}

        footer {{
            margin-top: 3rem;
            text-align: center;
            color: #6b7280;
            font-size: 0.875rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>LUI Accessibility Report</h1>
            <div class="header-grid">
                <div class="header-item">
                    <div class="header-label">Schema</div>
                    <div class="header-value">{esc(report.schema_name)}</div>
                </div>
                <div class="header-item">
                    <div class="header-label">Target Level</div>
                    <div class="header-value">{esc(report.target_level.value)}</div>
                </div>
                <div class="header-item">
                    <div class="header-label">Achieved Level</div>
                    <div class="header-value">
                        <span class="badge" style="background: {level_color}">{esc(report.level_badge)}</span>
                    </div>
                </div>
                <div class="header-item">
                    <div class="header-label">Status</div>
                    <div class="header-value">
                        <span class="badge" style="background: {status_color}">{'PASS' if report.passes else 'FAIL'}</span>
                    </div>
                </div>
            </div>

            <h3>Overall Score</h3>
            <div class="score-meter">
                <div class="score-fill" style="width: {report.score_percentage}%; background: {level_color};"></div>
            </div>
            <div style="text-align: center; font-size: 1.25rem; font-weight: 600;">{report.score_percentage}%</div>
        </div>

        <h2>Summary</h2>
        <div class="card">
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Total Components</td><td>{report.summary.total_components}</td></tr>
                <tr><td>Passing Components</td><td>{report.summary.passing_components}</td></tr>
                <tr><td>Critical Violations</td><td style="color: #ef4444; font-weight: 600;">{report.summary.critical_violations}</td></tr>
                <tr><td>Major Violations</td><td style="color: #f97316; font-weight: 600;">{report.summary.major_violations}</td></tr>
                <tr><td>Minor Violations</td><td style="color: #eab308;">{report.summary.minor_violations}</td></tr>
                <tr><td>Advisory Notices</td><td style="color: #3b82f6;">{report.summary.advisory_count}</td></tr>
            </table>
        </div>
'''

        # Top Issues
        if report.summary.top_issues:
            html_content += '''
        <h2>Top Issues</h2>
        <div class="card">
            <ol>
'''
            for issue in report.summary.top_issues:
                html_content += f'                <li>{esc(issue)}</li>\n'
            html_content += '''            </ol>
        </div>
'''

        # Recommendations
        if report.recommendations:
            html_content += '''
        <h2>Recommendations</h2>
'''
            for rec in report.recommendations[:10]:
                color = get_priority_color(rec.priority)
                html_content += f'''
        <div class="recommendation" style="border-color: {color};">
            <h3>{esc(rec.title)}</h3>
            <p><strong>Priority:</strong> <span class="badge" style="background: {color}">{esc(rec.priority.upper())}</span></p>
            <p><strong>Impact:</strong> {esc(rec.impact)}</p>
            <p><strong>Effort:</strong> {esc(rec.effort.title())}</p>
'''
                if rec.affected_components:
                    html_content += '            <p><strong>Affected:</strong> '
                    for comp in rec.affected_components[:3]:
                        html_content += f'<span class="tag">{esc(comp)}</span>'
                    html_content += '</p>\n'
                html_content += '        </div>\n'

        # Disability Coverage
        if report.disability_coverage:
            html_content += '''
        <h2>Disability Coverage</h2>
        <div class="card">
            <table>
                <tr>
                    <th>Disability Type</th>
                    <th>Score</th>
                    <th>Status</th>
                    <th>Barriers</th>
                </tr>
'''
            for dis in report.disability_coverage:
                status_badge = (
                    '<span class="badge" style="background: #22c55e">PASS</span>'
                    if dis.passes
                    else '<span class="badge" style="background: #ef4444">FAIL</span>'
                )
                html_content += f'''                <tr>
                    <td>{esc(dis.disability_type.value.title())}</td>
                    <td>{int(dis.accommodation_score * 100)}%</td>
                    <td>{status_badge}</td>
                    <td>{dis.barriers_count} ({dis.critical_barriers} critical)</td>
                </tr>
'''
            html_content += '''            </table>
        </div>
'''

        # Violations
        if report.violations:
            html_content += '''
        <h2>Violations</h2>
        <div class="card">
'''
            for v in report.violations[:15]:
                color = get_severity_color(v.severity)
                html_content += f'''            <div class="violation" style="border-color: {color};">
                <strong>[{esc(v.criterion)}]</strong> {esc(v.description)}
                <br><small><strong>Remediation:</strong> {esc(v.remediation)}</small>
            </div>
'''
            html_content += '''        </div>
'''

        # Footer
        html_content += f'''
        <footer>
            <p>Generated on {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')} by LUI Accessibility Report Generator</p>
        </footer>
    </div>
</body>
</html>'''

        return html_content
