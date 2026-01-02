"""Schema-level accessibility checker for LUI applications.

This module implements schema-level accessibility evaluation that checks entire
LUI schemas against LUIAG (Language User Interface Accessibility Guidelines) criteria.

Issue #70 - Task 4.4: Schema Accessibility Evaluator
Part of #27 - Phase 4: LUI Accessibility Standards
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from .checker import (
    AccessibilityViolation,
    ComplianceLevel,
    LUIAccessibilityChecker,
    LEVEL_THRESHOLDS,
    SEVERITY_WEIGHTS,
    ViolationSeverity,
)


# ============================================
# Schema-Specific Data Classes
# ============================================


@dataclass
class SchemaViolation(AccessibilityViolation):
    """An accessibility violation with schema location information."""

    location: str = ""  # e.g., "components[0].feedback.success_template"

    def __post_init__(self):
        """Ensure location is set."""
        if not self.location and self.element:
            self.location = self.element


@dataclass
class ComponentAccessibilityEval:
    """Accessibility evaluation for a single component."""

    component_id: str
    component_type: str
    score: float  # 0.0-1.0
    violations: list[SchemaViolation]
    passes: bool
    achieved_level: Optional[ComplianceLevel]

    @property
    def critical_count(self) -> int:
        """Count of critical violations."""
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.CRITICAL)

    @property
    def major_count(self) -> int:
        """Count of major violations."""
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.MAJOR)


@dataclass
class SchemaAccessibilityResult:
    """Complete result of a schema accessibility check."""

    schema_name: str
    target_level: ComplianceLevel
    achieved_level: Optional[ComplianceLevel]
    overall_score: float  # 0.0-1.0
    passes: bool
    violations: list[SchemaViolation]
    component_evaluations: list[ComponentAccessibilityEval]
    summary: str
    recommendations: list[str] = field(default_factory=list)

    @property
    def total_components(self) -> int:
        """Total number of components evaluated."""
        return len(self.component_evaluations)

    @property
    def passing_components(self) -> int:
        """Number of components that pass target level."""
        return sum(1 for c in self.component_evaluations if c.passes)

    @property
    def critical_count(self) -> int:
        """Total critical violations across schema."""
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.CRITICAL)

    @property
    def major_count(self) -> int:
        """Total major violations across schema."""
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.MAJOR)


# ============================================
# Main Schema Checker Class
# ============================================


class SchemaAccessibilityChecker:
    """Checks LUI schemas for accessibility compliance.

    This checker validates entire interface schemas against LUIAG requirements,
    including:
    - Schema-level accessibility configuration
    - Per-component accessibility attributes
    - Feedback template readability
    - Timing configurations
    - Input method compatibility
    """

    def __init__(self):
        """Initialize the schema checker."""
        self._response_checker = LUIAccessibilityChecker()

    def check_schema(
        self,
        schema: dict[str, Any],
        target_level: ComplianceLevel = ComplianceLevel.LEVEL_AA,
    ) -> SchemaAccessibilityResult:
        """Check a schema against LUIAG criteria.

        Args:
            schema: The LUI schema dictionary to check
            target_level: Target compliance level (default: AA)

        Returns:
            SchemaAccessibilityResult with violations and scores
        """
        schema_name = schema.get("name", schema.get("schema_id", "unnamed_schema"))
        violations: list[SchemaViolation] = []
        component_evaluations: list[ComponentAccessibilityEval] = []

        # 1. Check schema-level accessibility configuration
        violations.extend(self._check_schema_config(schema, target_level))

        # 2. Check timing configurations
        violations.extend(self._check_timing_config(schema, target_level))

        # 3. Evaluate each component
        components = schema.get("components") or []
        for i, component in enumerate(components):
            comp_eval = self._evaluate_component(component, i, target_level)
            component_evaluations.append(comp_eval)
            # Add component violations to overall list with location
            for v in comp_eval.violations:
                if not v.location.startswith("components"):
                    v.location = f"components[{i}].{v.location}"
                violations.append(v)

        # 4. Check conversational flows for accessibility
        flows = schema.get("flows") or []
        for i, flow in enumerate(flows):
            flow_violations = self._check_flow(flow, i, target_level)
            violations.extend(flow_violations)

        # Calculate overall score
        overall_score = self._calculate_schema_score(violations, component_evaluations)

        # Determine achieved level
        achieved_level = self._determine_achieved_level(violations)

        # Check if passes target level
        passes = achieved_level is not None and self._level_value(achieved_level) >= self._level_value(target_level)

        # Generate summary and recommendations
        summary = self._generate_summary(
            schema_name, violations, overall_score, target_level, achieved_level, component_evaluations
        )
        recommendations = self._generate_recommendations(violations, component_evaluations)

        return SchemaAccessibilityResult(
            schema_name=schema_name,
            target_level=target_level,
            achieved_level=achieved_level,
            overall_score=overall_score,
            passes=passes,
            violations=violations,
            component_evaluations=component_evaluations,
            summary=summary,
            recommendations=recommendations,
        )

    def _check_schema_config(
        self,
        schema: dict[str, Any],
        target_level: ComplianceLevel,
    ) -> list[SchemaViolation]:
        """Check for schema-level accessibility configuration."""
        violations = []

        # Check for accessibility configuration
        accessibility = schema.get("accessibility")
        if accessibility is None:
            violations.append(
                SchemaViolation(
                    criterion="A.1.1",
                    severity=ViolationSeverity.MAJOR,
                    description="Schema missing accessibility configuration",
                    remediation="Add InterfaceAccessibility configuration to schema",
                    location=schema.get("name", schema.get("schema_id", "schema")),
                )
            )
        else:
            # Check for required sub-configurations
            if not accessibility.get("default_config"):
                violations.append(
                    SchemaViolation(
                        criterion="A.1.2",
                        severity=ViolationSeverity.MAJOR,
                        description="Missing default accessibility configuration",
                        remediation="Add default_config to accessibility settings",
                        location="accessibility.default_config",
                    )
                )

            # Check supported compliance levels
            supported_levels = accessibility.get("supported_compliance_levels", [])
            target_value = target_level.value
            if target_value not in supported_levels and target_level.name not in supported_levels:
                violations.append(
                    SchemaViolation(
                        criterion="AA.1.1",
                        severity=ViolationSeverity.MINOR,
                        description=f"Target level {target_value} not in supported_compliance_levels",
                        remediation=f"Add {target_value} to supported_compliance_levels",
                        location="accessibility.supported_compliance_levels",
                    )
                )

        return violations

    def _check_timing_config(
        self,
        schema: dict[str, Any],
        target_level: ComplianceLevel,
    ) -> list[SchemaViolation]:
        """Check timing configurations against level thresholds."""
        violations = []
        thresholds = LEVEL_THRESHOLDS[target_level]
        min_timeout = thresholds["min_timeout_seconds"]

        # Check global context for rate limits / timing
        global_context = schema.get("global_context") or {}
        rate_limits = global_context.get("rate_limits") or {}

        # Check accessibility config for interaction constraints
        accessibility = schema.get("accessibility") or {}
        default_config = accessibility.get("default_config") or {}
        interaction = default_config.get("interaction_constraints", {})

        # Check session timeout
        session_timeout_ms = interaction.get("max_session_timeout_ms")
        if session_timeout_ms is not None:
            session_timeout_sec = session_timeout_ms / 1000
            if session_timeout_sec < min_timeout:
                violations.append(
                    SchemaViolation(
                        criterion=f"{target_level.value}.2.1",
                        severity=ViolationSeverity.MAJOR,
                        description=(
                            f"Session timeout {session_timeout_sec:.1f}s below minimum "
                            f"{min_timeout}s for {target_level.value}"
                        ),
                        remediation=f"Increase session timeout to at least {min_timeout} seconds",
                        location="accessibility.default_config.interaction_constraints.max_session_timeout_ms",
                    )
                )

        # Check if timeout extension is allowed at AA/AAA
        if target_level in [ComplianceLevel.LEVEL_AA, ComplianceLevel.LEVEL_AAA]:
            if not interaction.get("timeout_extension_allowed", True):
                violations.append(
                    SchemaViolation(
                        criterion=f"{target_level.value}.2.2",
                        severity=ViolationSeverity.MINOR,
                        description="Timeout extension not allowed",
                        remediation="Enable timeout_extension_allowed for better accessibility",
                        location="accessibility.default_config.interaction_constraints.timeout_extension_allowed",
                    )
                )

        return violations

    def _evaluate_component(
        self,
        component: dict[str, Any],
        index: int,
        target_level: ComplianceLevel,
    ) -> ComponentAccessibilityEval:
        """Evaluate a single component for accessibility compliance."""
        component_id = component.get("component_id", f"component_{index}")
        component_type = component.get("component_type", "UNKNOWN")
        violations: list[SchemaViolation] = []

        # Check component accessibility config
        comp_accessibility = component.get("accessibility")
        if comp_accessibility is None:
            violations.append(
                SchemaViolation(
                    criterion="A.2.1",
                    severity=ViolationSeverity.MINOR,
                    description=f"Component '{component_id}' missing accessibility configuration",
                    remediation="Add AccessibilityConfig to component",
                    location=f"{component_id}.accessibility",
                )
            )
        else:
            # Check for screen reader label
            if not comp_accessibility.get("screen_reader_label"):
                violations.append(
                    SchemaViolation(
                        criterion="A.2.2",
                        severity=ViolationSeverity.MAJOR,
                        description=f"Component '{component_id}' missing screen reader label",
                        remediation="Add screen_reader_label for assistive technology support",
                        location=f"{component_id}.accessibility.screen_reader_label",
                    )
                )

            # Check for voice hints at AA level
            if target_level in [ComplianceLevel.LEVEL_AA, ComplianceLevel.LEVEL_AAA]:
                voice_hints = comp_accessibility.get("voice_hints", [])
                if not voice_hints:
                    violations.append(
                        SchemaViolation(
                            criterion="AA.2.2",
                            severity=ViolationSeverity.ADVISORY,
                            description=f"Component '{component_id}' has no voice hints",
                            remediation="Add voice_hints for voice interface support",
                            location=f"{component_id}.accessibility.voice_hints",
                        )
                    )

        # Check feedback templates
        feedback = component.get("feedback", {})
        feedback_violations = self._check_feedback_templates(
            feedback, component_id, target_level
        )
        violations.extend(feedback_violations)

        # Check confirmation requirements for destructive actions
        if component_type in ["ACTION", "CONFIRMATION"]:
            if not feedback.get("confirmation_required", False):
                # Only flag at AA/AAA for actions that might be destructive
                if target_level in [ComplianceLevel.LEVEL_AA, ComplianceLevel.LEVEL_AAA]:
                    violations.append(
                        SchemaViolation(
                            criterion="AA.3.1",
                            severity=ViolationSeverity.ADVISORY,
                            description=f"Action component '{component_id}' has no confirmation requirement",
                            remediation="Consider adding confirmation_required for important actions",
                            location=f"{component_id}.feedback.confirmation_required",
                        )
                    )

        # Calculate component score
        score = self._calculate_score(violations)
        achieved_level = self._determine_achieved_level(violations)
        passes = achieved_level is not None and self._level_value(achieved_level) >= self._level_value(target_level)

        return ComponentAccessibilityEval(
            component_id=component_id,
            component_type=component_type,
            score=score,
            violations=violations,
            passes=passes,
            achieved_level=achieved_level,
        )

    def _check_feedback_templates(
        self,
        feedback: dict[str, Any],
        component_id: str,
        target_level: ComplianceLevel,
    ) -> list[SchemaViolation]:
        """Check feedback templates for readability compliance."""
        violations = []

        templates = [
            ("success_template", feedback.get("success_template")),
            ("error_template", feedback.get("error_template")),
            ("progress_template", feedback.get("progress_template")),
            ("confirmation_prompt", feedback.get("confirmation_prompt")),
        ]

        for template_name, template_text in templates:
            if template_text:
                # Use the response checker to analyze the template
                result = self._response_checker.check_response(template_text, target_level)

                # Convert response violations to schema violations with location
                for v in result.violations:
                    violations.append(
                        SchemaViolation(
                            criterion=v.criterion,
                            severity=v.severity,
                            description=v.description,
                            remediation=v.remediation,
                            element=v.element,
                            line_number=v.line_number,
                            location=f"{component_id}.feedback.{template_name}",
                        )
                    )

        return violations

    def _check_flow(
        self,
        flow: dict[str, Any],
        index: int,
        target_level: ComplianceLevel,
    ) -> list[SchemaViolation]:
        """Check a conversational flow for accessibility compliance."""
        violations = []
        flow_id = flow.get("flow_id", f"flow_{index}")

        # Check flow description readability
        description = flow.get("description", "")
        if description:
            result = self._response_checker.check_response(description, target_level)
            for v in result.violations:
                violations.append(
                    SchemaViolation(
                        criterion=v.criterion,
                        severity=v.severity,
                        description=v.description,
                        remediation=v.remediation,
                        element=v.element,
                        location=f"flows[{index}].description",
                    )
                )

        # Check steps if present
        steps = flow.get("steps", [])
        for step_index, step in enumerate(steps):
            step_prompt = step.get("prompt", "")
            if step_prompt:
                result = self._response_checker.check_response(step_prompt, target_level)
                for v in result.violations:
                    violations.append(
                        SchemaViolation(
                            criterion=v.criterion,
                            severity=v.severity,
                            description=v.description,
                            remediation=v.remediation,
                            element=v.element,
                            location=f"flows[{index}].steps[{step_index}].prompt",
                        )
                    )

        return violations

    def _calculate_score(self, violations: list[SchemaViolation]) -> float:
        """Calculate accessibility score from violations."""
        if not violations:
            return 1.0

        total_weight = sum(SEVERITY_WEIGHTS.get(v.severity, 0.05) for v in violations)
        score = max(0.0, 1.0 - total_weight)
        return round(score, 2)

    def _calculate_schema_score(
        self,
        violations: list[SchemaViolation],
        component_evals: list[ComponentAccessibilityEval],
    ) -> float:
        """Calculate overall schema accessibility score.

        Combines schema-level violations with component scores.
        """
        if not violations and not component_evals:
            return 1.0

        # Weight schema-level violations
        schema_weight = sum(SEVERITY_WEIGHTS.get(v.severity, 0.05) for v in violations)

        # Average component scores if we have components
        if component_evals:
            avg_component_score = sum(c.score for c in component_evals) / len(component_evals)
            # Combine: 40% schema-level, 60% component-level
            combined_score = 0.4 * max(0.0, 1.0 - schema_weight) + 0.6 * avg_component_score
        else:
            combined_score = max(0.0, 1.0 - schema_weight)

        return round(combined_score, 2)

    def _determine_achieved_level(
        self,
        violations: list[SchemaViolation],
    ) -> Optional[ComplianceLevel]:
        """Determine the highest compliance level achieved."""
        # Filter to get violations by level prefix
        def has_critical_or_major_at_level(level_prefix: str) -> bool:
            return any(
                v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.MAJOR]
                and v.criterion.startswith(level_prefix)
                for v in violations
            )

        # Also check for violations that prevent any level
        has_a_blocking = any(
            v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.MAJOR]
            and v.criterion.startswith("A.")
            for v in violations
        )

        if has_a_blocking:
            return None

        has_aa_blocking = any(
            v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.MAJOR]
            and v.criterion.startswith("AA.")
            for v in violations
        )

        has_aaa_blocking = any(
            v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.MAJOR]
            and v.criterion.startswith("AAA.")
            for v in violations
        )

        if not has_aaa_blocking and not has_aa_blocking:
            return ComplianceLevel.LEVEL_AAA
        elif not has_aa_blocking:
            return ComplianceLevel.LEVEL_AA
        else:
            return ComplianceLevel.LEVEL_A

    def _level_value(self, level: ComplianceLevel) -> int:
        """Get numeric value for level comparison."""
        return {
            ComplianceLevel.LEVEL_A: 1,
            ComplianceLevel.LEVEL_AA: 2,
            ComplianceLevel.LEVEL_AAA: 3,
        }[level]

    def _generate_summary(
        self,
        schema_name: str,
        violations: list[SchemaViolation],
        score: float,
        target_level: ComplianceLevel,
        achieved_level: Optional[ComplianceLevel],
        component_evals: list[ComponentAccessibilityEval],
    ) -> str:
        """Generate a human-readable summary."""
        achieved_str = achieved_level.value if achieved_level else "None"
        passing_count = sum(1 for c in component_evals if c.passes)
        total_count = len(component_evals)

        parts = [
            f"Schema '{schema_name}' accessibility score: {score:.0%}",
            f"Target: {target_level.value}, Achieved: {achieved_str}",
        ]

        if total_count > 0:
            parts.append(f"Components: {passing_count}/{total_count} passing")

        critical = sum(1 for v in violations if v.severity == ViolationSeverity.CRITICAL)
        major = sum(1 for v in violations if v.severity == ViolationSeverity.MAJOR)

        if critical > 0:
            parts.append(f"{critical} critical violation(s)")
        if major > 0:
            parts.append(f"{major} major violation(s)")

        return ". ".join(parts)

    def _generate_recommendations(
        self,
        violations: list[SchemaViolation],
        component_evals: list[ComponentAccessibilityEval],
    ) -> list[str]:
        """Generate prioritized recommendations."""
        recommendations = []
        seen = set()

        # Sort violations by severity
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
            rec_key = (v.remediation, v.location.split(".")[0] if v.location else "")
            if rec_key not in seen:
                location_hint = f" (at {v.location})" if v.location else ""
                recommendations.append(f"{v.remediation}{location_hint}")
                seen.add(rec_key)

        # Add component-specific recommendations
        failing_components = [c for c in component_evals if not c.passes]
        if failing_components:
            component_ids = [c.component_id for c in failing_components[:3]]
            if len(failing_components) > 3:
                recommendations.append(
                    f"Review failing components: {', '.join(component_ids)} and {len(failing_components) - 3} more"
                )
            elif failing_components:
                recommendations.append(f"Review failing components: {', '.join(component_ids)}")

        return recommendations[:10]  # Limit to top 10
