"""Disability-specific accessibility evaluators for LUI applications.

This module implements specialized evaluators for each major disability category
to ensure comprehensive accessibility coverage.

Issue #72 - Task 4.6: Disability-Specific Evaluators
Part of #27 - Phase 4: LUI Accessibility Standards
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .checker import ComplianceLevel, ViolationSeverity
from .readability import ReadabilityAnalyzer


# ============================================
# Enums
# ============================================


class DisabilityType(Enum):
    """Types of disabilities for targeted evaluation."""

    VISUAL = "visual"
    HEARING = "hearing"
    MOTOR = "motor"
    SPEECH = "speech"
    COGNITIVE = "cognitive"
    NEUROLOGICAL = "neurological"


class BarrierCategory(Enum):
    """Categories of accessibility barriers."""

    PERCEPTION = "perception"  # Ability to perceive content
    OPERATION = "operation"  # Ability to operate interface
    UNDERSTANDING = "understanding"  # Ability to understand content
    ROBUSTNESS = "robustness"  # Compatibility with assistive tech


# ============================================
# Data Classes
# ============================================


@dataclass
class Barrier:
    """A specific accessibility barrier for a disability type."""

    category: BarrierCategory
    severity: ViolationSeverity
    description: str
    location: str  # Where in the schema this barrier exists
    impact: str  # How this affects users
    remediation: str  # Suggested fix


@dataclass
class BarrierAnalysis:
    """Analysis of barriers for a specific component or area."""

    area: str  # Component or area being analyzed
    barriers: list[Barrier]
    barrier_count: int = 0
    critical_count: int = 0

    def __post_init__(self):
        """Calculate counts after initialization."""
        self.barrier_count = len(self.barriers)
        self.critical_count = sum(
            1 for b in self.barriers if b.severity == ViolationSeverity.CRITICAL
        )


@dataclass
class DisabilityEvaluation:
    """Complete evaluation result for a disability type."""

    disability_type: DisabilityType
    accommodation_score: float  # 0.0-1.0
    barriers: list[BarrierAnalysis]
    accommodations_present: list[str]
    accommodations_missing: list[str]
    recommendations: list[str]
    passes: bool = False
    summary: str = ""

    @property
    def total_barriers(self) -> int:
        """Total number of barriers found."""
        return sum(ba.barrier_count for ba in self.barriers)

    @property
    def critical_barriers(self) -> int:
        """Total critical barriers."""
        return sum(ba.critical_count for ba in self.barriers)

    def __post_init__(self):
        """Generate summary and pass status."""
        # Calculate passes FIRST so summary can use it
        self.passes = self.accommodation_score >= 0.7 and self.critical_barriers == 0
        if not self.summary:
            self.summary = self._generate_summary()

    def _generate_summary(self) -> str:
        """Generate a human-readable summary."""
        status = "PASSES" if self.passes else "NEEDS IMPROVEMENT"
        return (
            f"{self.disability_type.value.title()} accessibility: {status}. "
            f"Score: {self.accommodation_score:.0%}. "
            f"Barriers: {self.total_barriers} ({self.critical_barriers} critical). "
            f"Accommodations: {len(self.accommodations_present)} present, "
            f"{len(self.accommodations_missing)} missing."
        )


# ============================================
# Base Evaluator Class
# ============================================


class DisabilityEvaluator(ABC):
    """Base class for disability-specific evaluators."""

    disability_type: DisabilityType

    def __init__(self):
        """Initialize the evaluator."""
        self._readability = ReadabilityAnalyzer()

    @abstractmethod
    def evaluate(self, schema: dict[str, Any]) -> DisabilityEvaluation:
        """Evaluate a schema for disability-specific accessibility.

        Args:
            schema: The LUI schema dictionary to evaluate

        Returns:
            DisabilityEvaluation with barriers and accommodations
        """
        pass

    def _calculate_score(self, barriers: list[BarrierAnalysis]) -> float:
        """Calculate accommodation score from barriers found."""
        if not barriers:
            return 1.0

        total_weight = 0.0
        weights = {
            ViolationSeverity.CRITICAL: 0.30,
            ViolationSeverity.MAJOR: 0.15,
            ViolationSeverity.MINOR: 0.05,
            ViolationSeverity.ADVISORY: 0.02,
        }

        for ba in barriers:
            for barrier in ba.barriers:
                total_weight += weights.get(barrier.severity, 0.05)

        return max(0.0, min(1.0, 1.0 - total_weight))

    def _get_components(self, schema: dict[str, Any]) -> list[dict[str, Any]]:
        """Get components from schema safely."""
        return schema.get("components") or []

    def _get_accessibility_config(
        self, schema: dict[str, Any]
    ) -> dict[str, Any]:
        """Get accessibility configuration from schema."""
        return schema.get("accessibility") or {}

    def _get_component_accessibility(
        self, component: dict[str, Any]
    ) -> dict[str, Any]:
        """Get accessibility config from a component."""
        return component.get("accessibility") or {}


# ============================================
# Visual Accessibility Evaluator
# ============================================


class VisualAccessibilityEvaluator(DisabilityEvaluator):
    """Evaluator for visual impairment accessibility.

    Checks:
    - Audio-first design verification
    - Screen reader optimization (ARIA live regions)
    - No visual-only information check
    - High contrast support verification
    """

    disability_type = DisabilityType.VISUAL

    def evaluate(self, schema: dict[str, Any]) -> DisabilityEvaluation:
        """Evaluate schema for visual accessibility."""
        barriers: list[BarrierAnalysis] = []
        accommodations_present: list[str] = []
        accommodations_missing: list[str] = []
        recommendations: list[str] = []

        # Check schema-level accessibility
        schema_barriers = self._check_schema_level(schema)
        if schema_barriers.barriers:
            barriers.append(schema_barriers)

        # Check components
        for i, component in enumerate(self._get_components(schema)):
            comp_barriers = self._check_component(component, i)
            if comp_barriers.barriers:
                barriers.append(comp_barriers)

        # Identify accommodations
        accessibility = self._get_accessibility_config(schema)

        # Audio-first design
        if accessibility.get("audio_first_design"):
            accommodations_present.append("Audio-first design enabled")
        else:
            accommodations_missing.append("Audio-first design configuration")
            recommendations.append("Enable audio_first_design for blind users")

        # Screen reader support
        default_config = accessibility.get("default_config") or {}
        if default_config.get("screen_reader_label"):
            accommodations_present.append("Global screen reader label")
        else:
            accommodations_missing.append("Global screen reader configuration")

        # Check for audio feedback
        if self._has_audio_feedback(schema):
            accommodations_present.append("Audio feedback available")
        else:
            accommodations_missing.append("Audio feedback for actions")
            recommendations.append("Add audio confirmation for all user actions")

        # High contrast support
        visual_config = default_config.get("visual_config") or {}
        if visual_config.get("high_contrast_support"):
            accommodations_present.append("High contrast mode supported")
        else:
            accommodations_missing.append("High contrast mode support")

        score = self._calculate_score(barriers)

        return DisabilityEvaluation(
            disability_type=self.disability_type,
            accommodation_score=score,
            barriers=barriers,
            accommodations_present=accommodations_present,
            accommodations_missing=accommodations_missing,
            recommendations=recommendations,
        )

    def _check_schema_level(self, schema: dict[str, Any]) -> BarrierAnalysis:
        """Check schema-level visual accessibility."""
        barriers = []
        accessibility = self._get_accessibility_config(schema)

        # Check for audio output configuration
        if not accessibility.get("audio_output_enabled", True):
            barriers.append(
                Barrier(
                    category=BarrierCategory.PERCEPTION,
                    severity=ViolationSeverity.CRITICAL,
                    description="Audio output disabled - blind users cannot perceive responses",
                    location="accessibility.audio_output_enabled",
                    impact="Blind users have no way to receive information",
                    remediation="Enable audio_output_enabled for screen reader compatibility",
                )
            )

        # Check for visual-only information
        if self._has_visual_only_info(schema):
            barriers.append(
                Barrier(
                    category=BarrierCategory.PERCEPTION,
                    severity=ViolationSeverity.MAJOR,
                    description="Schema contains visual-only information without text alternatives",
                    location="schema",
                    impact="Visual content inaccessible to blind users",
                    remediation="Add text descriptions for all visual content",
                )
            )

        return BarrierAnalysis(area="schema", barriers=barriers)

    def _check_component(
        self, component: dict[str, Any], index: int
    ) -> BarrierAnalysis:
        """Check component for visual accessibility."""
        barriers = []
        comp_id = component.get("component_id", f"component_{index}")
        comp_accessibility = self._get_component_accessibility(component)

        # Check for screen reader label
        if not comp_accessibility.get("screen_reader_label"):
            barriers.append(
                Barrier(
                    category=BarrierCategory.PERCEPTION,
                    severity=ViolationSeverity.MAJOR,
                    description=f"Component '{comp_id}' missing screen reader label",
                    location=f"components[{index}].accessibility.screen_reader_label",
                    impact="Screen readers cannot describe this component",
                    remediation="Add descriptive screen_reader_label",
                )
            )

        # Check for ARIA live region configuration
        aria_config = comp_accessibility.get("aria_config") or {}
        if not aria_config.get("live_region"):
            # Only flag for dynamic components
            if component.get("component_type") in ["ACTION", "QUERY", "STREAM"]:
                barriers.append(
                    Barrier(
                        category=BarrierCategory.OPERATION,
                        severity=ViolationSeverity.MINOR,
                        description=f"Component '{comp_id}' missing ARIA live region for updates",
                        location=f"components[{index}].accessibility.aria_config.live_region",
                        impact="Screen readers may not announce dynamic updates",
                        remediation="Configure aria_config.live_region for dynamic content",
                    )
                )

        return BarrierAnalysis(area=comp_id, barriers=barriers)

    def _has_visual_only_info(self, schema: dict[str, Any]) -> bool:
        """Check if schema has visual-only information without alternatives."""
        # Check for images, charts, or visual elements without alt text
        for component in self._get_components(schema):
            comp_type = component.get("component_type", "")
            if comp_type in ["IMAGE", "CHART", "VISUAL"]:
                accessibility = self._get_component_accessibility(component)
                if not accessibility.get("alt_text"):
                    return True
        return False

    def _has_audio_feedback(self, schema: dict[str, Any]) -> bool:
        """Check if schema has audio feedback configured."""
        accessibility = self._get_accessibility_config(schema)
        default_config = accessibility.get("default_config") or {}
        return default_config.get("audio_feedback_enabled", False)


# ============================================
# Hearing Accessibility Evaluator
# ============================================


class HearingAccessibilityEvaluator(DisabilityEvaluator):
    """Evaluator for hearing impairment accessibility.

    Checks:
    - Text alternatives for all audio
    - Visual alerts for audio cues
    - Real-time caption support
    - Sign language availability check
    """

    disability_type = DisabilityType.HEARING

    def evaluate(self, schema: dict[str, Any]) -> DisabilityEvaluation:
        """Evaluate schema for hearing accessibility."""
        barriers: list[BarrierAnalysis] = []
        accommodations_present: list[str] = []
        accommodations_missing: list[str] = []
        recommendations: list[str] = []

        # Check schema-level
        schema_barriers = self._check_schema_level(schema)
        if schema_barriers.barriers:
            barriers.append(schema_barriers)

        # Check components
        for i, component in enumerate(self._get_components(schema)):
            comp_barriers = self._check_component(component, i)
            if comp_barriers.barriers:
                barriers.append(comp_barriers)

        # Identify accommodations
        accessibility = self._get_accessibility_config(schema)
        default_config = accessibility.get("default_config") or {}

        # Text alternatives
        if default_config.get("text_alternatives_enabled", True):
            accommodations_present.append("Text alternatives enabled")
        else:
            accommodations_missing.append("Text alternatives for audio")
            recommendations.append("Enable text_alternatives_enabled for deaf users")

        # Visual alerts
        if default_config.get("visual_alerts_enabled"):
            accommodations_present.append("Visual alerts for audio cues")
        else:
            accommodations_missing.append("Visual alerts for audio cues")
            recommendations.append("Add visual_alerts_enabled for notification visibility")

        # Captions
        if accessibility.get("caption_support"):
            accommodations_present.append("Real-time caption support")
        else:
            accommodations_missing.append("Real-time caption support")
            recommendations.append("Implement caption_support for audio content")

        # Sign language
        if accessibility.get("sign_language_available"):
            accommodations_present.append("Sign language interpretation available")
        else:
            accommodations_missing.append("Sign language option")

        score = self._calculate_score(barriers)

        return DisabilityEvaluation(
            disability_type=self.disability_type,
            accommodation_score=score,
            barriers=barriers,
            accommodations_present=accommodations_present,
            accommodations_missing=accommodations_missing,
            recommendations=recommendations,
        )

    def _check_schema_level(self, schema: dict[str, Any]) -> BarrierAnalysis:
        """Check schema-level hearing accessibility."""
        barriers = []
        accessibility = self._get_accessibility_config(schema)

        # Check if audio-only without text
        if accessibility.get("audio_only_mode") and not accessibility.get("text_fallback"):
            barriers.append(
                Barrier(
                    category=BarrierCategory.PERCEPTION,
                    severity=ViolationSeverity.CRITICAL,
                    description="Audio-only mode without text fallback",
                    location="accessibility",
                    impact="Deaf users cannot access audio-only content",
                    remediation="Add text_fallback for all audio content",
                )
            )

        # Check caption accuracy configuration
        caption_config = accessibility.get("caption_config") or {}
        accuracy = caption_config.get("accuracy_threshold", 0)
        if 0 < accuracy < 0.99:
            barriers.append(
                Barrier(
                    category=BarrierCategory.PERCEPTION,
                    severity=ViolationSeverity.MAJOR,
                    description=f"Caption accuracy threshold {accuracy:.0%} below 99% target",
                    location="accessibility.caption_config.accuracy_threshold",
                    impact="Captions may miss important information",
                    remediation="Increase caption accuracy threshold to 99%",
                )
            )

        return BarrierAnalysis(area="schema", barriers=barriers)

    def _check_component(
        self, component: dict[str, Any], index: int
    ) -> BarrierAnalysis:
        """Check component for hearing accessibility."""
        barriers = []
        comp_id = component.get("component_id", f"component_{index}")
        feedback = component.get("feedback") or {}

        # Check for audio alerts without visual alternatives
        if feedback.get("audio_alert") and not feedback.get("visual_alert"):
            barriers.append(
                Barrier(
                    category=BarrierCategory.PERCEPTION,
                    severity=ViolationSeverity.MAJOR,
                    description=f"Component '{comp_id}' has audio alert without visual alternative",
                    location=f"components[{index}].feedback",
                    impact="Deaf users will miss audio notifications",
                    remediation="Add visual_alert alongside audio_alert",
                )
            )

        # Check for transcripts on audio components
        comp_type = component.get("component_type", "")
        if comp_type in ["AUDIO", "VIDEO", "STREAM"]:
            if not feedback.get("transcript_available"):
                barriers.append(
                    Barrier(
                        category=BarrierCategory.PERCEPTION,
                        severity=ViolationSeverity.CRITICAL,
                        description=f"Audio/video component '{comp_id}' has no transcript",
                        location=f"components[{index}].feedback.transcript_available",
                        impact="Audio content inaccessible to deaf users",
                        remediation="Provide transcript_available for all audio/video content",
                    )
                )

        return BarrierAnalysis(area=comp_id, barriers=barriers)


# ============================================
# Motor Accessibility Evaluator
# ============================================


class MotorAccessibilityEvaluator(DisabilityEvaluator):
    """Evaluator for motor impairment accessibility.

    Checks:
    - Timeout verification (≥5x standard)
    - Single-action interaction check
    - Touch target size (≥44×44px)
    - Voice input support verification
    - Switch access compatibility
    """

    disability_type = DisabilityType.MOTOR

    # Standard timeout is typically 20 seconds, motor needs 5x = 100s minimum
    MIN_TIMEOUT_MULTIPLIER = 5
    STANDARD_TIMEOUT = 20  # seconds
    MIN_MOTOR_TIMEOUT = STANDARD_TIMEOUT * MIN_TIMEOUT_MULTIPLIER  # 100 seconds
    MIN_TOUCH_TARGET = 44  # pixels

    def evaluate(self, schema: dict[str, Any]) -> DisabilityEvaluation:
        """Evaluate schema for motor accessibility."""
        barriers: list[BarrierAnalysis] = []
        accommodations_present: list[str] = []
        accommodations_missing: list[str] = []
        recommendations: list[str] = []

        # Check schema-level
        schema_barriers = self._check_schema_level(schema)
        if schema_barriers.barriers:
            barriers.append(schema_barriers)

        # Check components
        for i, component in enumerate(self._get_components(schema)):
            comp_barriers = self._check_component(component, i)
            if comp_barriers.barriers:
                barriers.append(comp_barriers)

        # Identify accommodations
        accessibility = self._get_accessibility_config(schema)
        default_config = accessibility.get("default_config") or {}
        interaction = default_config.get("interaction_constraints") or {}

        # Timeout extension
        timeout_ms = interaction.get("max_session_timeout_ms", 0)
        timeout_sec = timeout_ms / 1000 if timeout_ms else 0
        if timeout_sec >= self.MIN_MOTOR_TIMEOUT:
            accommodations_present.append(f"Extended timeout ({timeout_sec:.0f}s ≥ {self.MIN_MOTOR_TIMEOUT}s)")
        else:
            accommodations_missing.append(f"Extended timeout (need {self.MIN_MOTOR_TIMEOUT}s, have {timeout_sec:.0f}s)")
            recommendations.append(f"Increase timeout to at least {self.MIN_MOTOR_TIMEOUT} seconds (5× standard)")

        # Voice input
        if accessibility.get("voice_input_enabled"):
            accommodations_present.append("Voice input support")
        else:
            accommodations_missing.append("Voice input alternative")
            recommendations.append("Enable voice_input_enabled for hands-free operation")

        # Switch access
        if accessibility.get("switch_access_compatible"):
            accommodations_present.append("Switch access compatibility")
        else:
            accommodations_missing.append("Switch access compatibility")
            recommendations.append("Add switch_access_compatible for alternative input devices")

        # Single-action mode
        if interaction.get("single_action_mode"):
            accommodations_present.append("Single-action interaction mode")
        else:
            accommodations_missing.append("Single-action interaction mode")

        score = self._calculate_score(barriers)

        return DisabilityEvaluation(
            disability_type=self.disability_type,
            accommodation_score=score,
            barriers=barriers,
            accommodations_present=accommodations_present,
            accommodations_missing=accommodations_missing,
            recommendations=recommendations,
        )

    def _check_schema_level(self, schema: dict[str, Any]) -> BarrierAnalysis:
        """Check schema-level motor accessibility."""
        barriers = []
        accessibility = self._get_accessibility_config(schema)
        default_config = accessibility.get("default_config") or {}
        interaction = default_config.get("interaction_constraints") or {}

        # Check timeout duration
        timeout_ms = interaction.get("max_session_timeout_ms", 0)
        timeout_sec = timeout_ms / 1000 if timeout_ms else 0
        if 0 < timeout_sec < self.MIN_MOTOR_TIMEOUT:
            barriers.append(
                Barrier(
                    category=BarrierCategory.OPERATION,
                    severity=ViolationSeverity.CRITICAL,
                    description=(
                        f"Session timeout {timeout_sec:.0f}s is below {self.MIN_MOTOR_TIMEOUT}s "
                        f"minimum for motor impairment (5× standard)"
                    ),
                    location="accessibility.default_config.interaction_constraints.max_session_timeout_ms",
                    impact="Users with motor impairments may time out before completing actions",
                    remediation=f"Increase timeout to at least {self.MIN_MOTOR_TIMEOUT} seconds",
                )
            )

        # Check for complex gestures required
        if interaction.get("requires_complex_gestures"):
            barriers.append(
                Barrier(
                    category=BarrierCategory.OPERATION,
                    severity=ViolationSeverity.MAJOR,
                    description="Interface requires complex gestures",
                    location="accessibility.default_config.interaction_constraints.requires_complex_gestures",
                    impact="Users with motor impairments cannot perform complex gestures",
                    remediation="Provide single-action alternatives for all complex gestures",
                )
            )

        return BarrierAnalysis(area="schema", barriers=barriers)

    def _check_component(
        self, component: dict[str, Any], index: int
    ) -> BarrierAnalysis:
        """Check component for motor accessibility."""
        barriers = []
        comp_id = component.get("component_id", f"component_{index}")
        comp_accessibility = self._get_component_accessibility(component)

        # Check touch target size
        touch_config = comp_accessibility.get("touch_config") or {}
        target_size = touch_config.get("min_target_size", 0)
        if 0 < target_size < self.MIN_TOUCH_TARGET:
            barriers.append(
                Barrier(
                    category=BarrierCategory.OPERATION,
                    severity=ViolationSeverity.MAJOR,
                    description=(
                        f"Component '{comp_id}' touch target {target_size}px "
                        f"below {self.MIN_TOUCH_TARGET}px minimum"
                    ),
                    location=f"components[{index}].accessibility.touch_config.min_target_size",
                    impact="Small touch targets are difficult for users with motor impairments",
                    remediation=f"Increase touch target to at least {self.MIN_TOUCH_TARGET}×{self.MIN_TOUCH_TARGET} pixels",
                )
            )

        # Check for multi-step requirements
        if comp_accessibility.get("requires_multi_step_action"):
            barriers.append(
                Barrier(
                    category=BarrierCategory.OPERATION,
                    severity=ViolationSeverity.MINOR,
                    description=f"Component '{comp_id}' requires multi-step action",
                    location=f"components[{index}].accessibility.requires_multi_step_action",
                    impact="Multi-step actions are difficult for users with motor impairments",
                    remediation="Provide single-action alternative or allow action to be split",
                )
            )

        return BarrierAnalysis(area=comp_id, barriers=barriers)


# ============================================
# Speech Accessibility Evaluator
# ============================================


class SpeechAccessibilityEvaluator(DisabilityEvaluator):
    """Evaluator for speech impairment accessibility.

    Checks:
    - Text input alternatives (100% fallback)
    - AAC device compatibility
    - Gesture input support
    """

    disability_type = DisabilityType.SPEECH

    def evaluate(self, schema: dict[str, Any]) -> DisabilityEvaluation:
        """Evaluate schema for speech accessibility."""
        barriers: list[BarrierAnalysis] = []
        accommodations_present: list[str] = []
        accommodations_missing: list[str] = []
        recommendations: list[str] = []

        # Check schema-level
        schema_barriers = self._check_schema_level(schema)
        if schema_barriers.barriers:
            barriers.append(schema_barriers)

        # Check components
        for i, component in enumerate(self._get_components(schema)):
            comp_barriers = self._check_component(component, i)
            if comp_barriers.barriers:
                barriers.append(comp_barriers)

        # Identify accommodations
        accessibility = self._get_accessibility_config(schema)
        default_config = accessibility.get("default_config") or {}

        # Text input fallback
        if accessibility.get("text_input_fallback", True):
            accommodations_present.append("100% text input fallback available")
        else:
            accommodations_missing.append("Text input fallback")
            recommendations.append("Enable text_input_fallback for users who cannot speak")

        # AAC device support
        if accessibility.get("aac_device_compatible"):
            accommodations_present.append("AAC device compatibility")
        else:
            accommodations_missing.append("AAC device compatibility")
            recommendations.append("Add aac_device_compatible for alternative communication devices")

        # Gesture input
        if accessibility.get("gesture_input_enabled"):
            accommodations_present.append("Gesture input support")
        else:
            accommodations_missing.append("Gesture input support")

        # Typing alternatives
        interaction = default_config.get("interaction_constraints") or {}
        if interaction.get("keyboard_input_enabled", True):
            accommodations_present.append("Keyboard input enabled")

        score = self._calculate_score(barriers)

        return DisabilityEvaluation(
            disability_type=self.disability_type,
            accommodation_score=score,
            barriers=barriers,
            accommodations_present=accommodations_present,
            accommodations_missing=accommodations_missing,
            recommendations=recommendations,
        )

    def _check_schema_level(self, schema: dict[str, Any]) -> BarrierAnalysis:
        """Check schema-level speech accessibility."""
        barriers = []
        accessibility = self._get_accessibility_config(schema)

        # Check for voice-only requirement
        if accessibility.get("voice_only_mode") and not accessibility.get("text_input_fallback"):
            barriers.append(
                Barrier(
                    category=BarrierCategory.OPERATION,
                    severity=ViolationSeverity.CRITICAL,
                    description="Voice-only mode without text input fallback",
                    location="accessibility",
                    impact="Users with speech impairments cannot interact with voice-only interface",
                    remediation="Add text_input_fallback for 100% non-voice alternative",
                )
            )

        # Check text fallback coverage
        fallback_coverage = accessibility.get("text_fallback_coverage", 1.0)
        if fallback_coverage < 1.0:
            barriers.append(
                Barrier(
                    category=BarrierCategory.OPERATION,
                    severity=ViolationSeverity.MAJOR,
                    description=f"Text fallback coverage {fallback_coverage:.0%} is below 100% requirement",
                    location="accessibility.text_fallback_coverage",
                    impact="Some voice actions have no text alternative",
                    remediation="Ensure 100% text fallback coverage for all voice interactions",
                )
            )

        return BarrierAnalysis(area="schema", barriers=barriers)

    def _check_component(
        self, component: dict[str, Any], index: int
    ) -> BarrierAnalysis:
        """Check component for speech accessibility."""
        barriers = []
        comp_id = component.get("component_id", f"component_{index}")
        comp_accessibility = self._get_component_accessibility(component)

        # Check if voice-required without alternative
        if comp_accessibility.get("voice_input_required") and not comp_accessibility.get("text_alternative"):
            barriers.append(
                Barrier(
                    category=BarrierCategory.OPERATION,
                    severity=ViolationSeverity.CRITICAL,
                    description=f"Component '{comp_id}' requires voice input without text alternative",
                    location=f"components[{index}].accessibility",
                    impact="Users with speech impairments cannot use this component",
                    remediation="Add text_alternative for voice input requirement",
                )
            )

        return BarrierAnalysis(area=comp_id, barriers=barriers)


# ============================================
# Cognitive Accessibility Evaluator
# ============================================


class CognitiveAccessibilityEvaluator(DisabilityEvaluator):
    """Evaluator for cognitive impairment accessibility.

    Checks:
    - Reading level verification (Grade 6-8)
    - Consistent navigation patterns
    - Progress indicator presence
    - Undo support verification
    - Auto-save functionality
    """

    disability_type = DisabilityType.COGNITIVE

    MAX_READING_GRADE = 8.0  # Grade 6-8 target range
    MIN_READING_GRADE = 6.0

    def evaluate(self, schema: dict[str, Any]) -> DisabilityEvaluation:
        """Evaluate schema for cognitive accessibility."""
        barriers: list[BarrierAnalysis] = []
        accommodations_present: list[str] = []
        accommodations_missing: list[str] = []
        recommendations: list[str] = []

        # Check schema-level
        schema_barriers = self._check_schema_level(schema)
        if schema_barriers.barriers:
            barriers.append(schema_barriers)

        # Check components
        for i, component in enumerate(self._get_components(schema)):
            comp_barriers = self._check_component(component, i)
            if comp_barriers.barriers:
                barriers.append(comp_barriers)

        # Check feedback template readability
        readability_barriers = self._check_readability(schema)
        if readability_barriers.barriers:
            barriers.append(readability_barriers)

        # Identify accommodations
        accessibility = self._get_accessibility_config(schema)
        default_config = accessibility.get("default_config") or {}

        # Consistent navigation
        if accessibility.get("consistent_navigation"):
            accommodations_present.append("Consistent navigation patterns")
        else:
            accommodations_missing.append("Consistent navigation patterns")
            recommendations.append("Implement consistent_navigation for predictable interface")

        # Progress indicators
        if accessibility.get("progress_indicators_enabled"):
            accommodations_present.append("Progress indicators available")
        else:
            accommodations_missing.append("Progress indicators")
            recommendations.append("Add progress_indicators_enabled for multi-step processes")

        # Undo support
        if accessibility.get("undo_support"):
            accommodations_present.append("Undo support available")
        else:
            accommodations_missing.append("Undo support")
            recommendations.append("Implement undo_support for error recovery")

        # Auto-save
        if accessibility.get("auto_save_enabled"):
            accommodations_present.append("Auto-save functionality")
        else:
            accommodations_missing.append("Auto-save functionality")
            recommendations.append("Enable auto_save_enabled to prevent data loss")

        # Simple language mode
        if accessibility.get("simple_language_mode"):
            accommodations_present.append("Simple language mode available")
        else:
            accommodations_missing.append("Simple language mode")

        score = self._calculate_score(barriers)

        return DisabilityEvaluation(
            disability_type=self.disability_type,
            accommodation_score=score,
            barriers=barriers,
            accommodations_present=accommodations_present,
            accommodations_missing=accommodations_missing,
            recommendations=recommendations,
        )

    def _check_schema_level(self, schema: dict[str, Any]) -> BarrierAnalysis:
        """Check schema-level cognitive accessibility."""
        barriers = []
        accessibility = self._get_accessibility_config(schema)

        # Check for clear error messages
        if not accessibility.get("clear_error_messages"):
            barriers.append(
                Barrier(
                    category=BarrierCategory.UNDERSTANDING,
                    severity=ViolationSeverity.MINOR,
                    description="Clear error message mode not configured",
                    location="accessibility.clear_error_messages",
                    impact="Error messages may be confusing for users with cognitive impairments",
                    remediation="Enable clear_error_messages for simple, actionable error feedback",
                )
            )

        # Check for step-by-step mode
        flows = schema.get("flows") or []
        for flow in flows:
            steps = flow.get("steps") or []
            if len(steps) > 3 and not accessibility.get("progress_indicators_enabled"):
                barriers.append(
                    Barrier(
                        category=BarrierCategory.UNDERSTANDING,
                        severity=ViolationSeverity.MAJOR,
                        description=f"Multi-step flow without progress indicators",
                        location="accessibility.progress_indicators_enabled",
                        impact="Users may lose track of progress in multi-step processes",
                        remediation="Enable progress indicators for flows with more than 3 steps",
                    )
                )
                break  # Only flag once

        return BarrierAnalysis(area="schema", barriers=barriers)

    def _check_component(
        self, component: dict[str, Any], index: int
    ) -> BarrierAnalysis:
        """Check component for cognitive accessibility."""
        barriers = []
        comp_id = component.get("component_id", f"component_{index}")
        feedback = component.get("feedback") or {}

        # Check for clear feedback
        if component.get("component_type") == "ACTION":
            if not feedback.get("success_template") and not feedback.get("error_template"):
                barriers.append(
                    Barrier(
                        category=BarrierCategory.UNDERSTANDING,
                        severity=ViolationSeverity.MINOR,
                        description=f"Action component '{comp_id}' missing feedback templates",
                        location=f"components[{index}].feedback",
                        impact="Users may not understand action outcomes",
                        remediation="Add success_template and error_template for clear feedback",
                    )
                )

        # Check for confirmation on destructive actions
        if component.get("destructive_action") and not feedback.get("confirmation_required"):
            barriers.append(
                Barrier(
                    category=BarrierCategory.OPERATION,
                    severity=ViolationSeverity.MAJOR,
                    description=f"Destructive action '{comp_id}' has no confirmation requirement",
                    location=f"components[{index}].feedback.confirmation_required",
                    impact="Users may accidentally trigger destructive actions",
                    remediation="Require confirmation for all destructive actions",
                )
            )

        return BarrierAnalysis(area=comp_id, barriers=barriers)

    def _check_readability(self, schema: dict[str, Any]) -> BarrierAnalysis:
        """Check readability of feedback templates."""
        barriers = []

        for i, component in enumerate(self._get_components(schema)):
            comp_id = component.get("component_id", f"component_{i}")
            feedback = component.get("feedback") or {}

            templates = [
                ("success_template", feedback.get("success_template")),
                ("error_template", feedback.get("error_template")),
            ]

            for template_name, template_text in templates:
                if template_text and len(template_text) > 20:  # Skip very short text
                    metrics = self._readability.analyze(template_text)
                    if metrics.flesch_kincaid_grade > self.MAX_READING_GRADE:
                        barriers.append(
                            Barrier(
                                category=BarrierCategory.UNDERSTANDING,
                                severity=ViolationSeverity.MAJOR,
                                description=(
                                    f"Template '{template_name}' grade level {metrics.flesch_kincaid_grade:.1f} "
                                    f"exceeds Grade {self.MAX_READING_GRADE} maximum"
                                ),
                                location=f"components[{i}].feedback.{template_name}",
                                impact="Complex language difficult for users with cognitive impairments",
                                remediation=f"Simplify text to Grade {self.MIN_READING_GRADE}-{self.MAX_READING_GRADE} level",
                            )
                        )

        return BarrierAnalysis(area="readability", barriers=barriers)


# ============================================
# Neurological Accessibility Evaluator
# ============================================


class NeurologicalAccessibilityEvaluator(DisabilityEvaluator):
    """Evaluator for neurological condition accessibility.

    Checks:
    - Seizure safety (no flashes >3Hz)
    - Animation controls
    - Reduced motion support
    - Auto-play media prevention
    """

    disability_type = DisabilityType.NEUROLOGICAL

    MAX_FLASH_FREQUENCY = 3  # Hz - above this can trigger seizures

    def evaluate(self, schema: dict[str, Any]) -> DisabilityEvaluation:
        """Evaluate schema for neurological accessibility."""
        barriers: list[BarrierAnalysis] = []
        accommodations_present: list[str] = []
        accommodations_missing: list[str] = []
        recommendations: list[str] = []

        # Check schema-level
        schema_barriers = self._check_schema_level(schema)
        if schema_barriers.barriers:
            barriers.append(schema_barriers)

        # Check components
        for i, component in enumerate(self._get_components(schema)):
            comp_barriers = self._check_component(component, i)
            if comp_barriers.barriers:
                barriers.append(comp_barriers)

        # Identify accommodations
        accessibility = self._get_accessibility_config(schema)
        default_config = accessibility.get("default_config") or {}
        visual_config = default_config.get("visual_config") or {}

        # Seizure safety
        if accessibility.get("seizure_safe_mode"):
            accommodations_present.append("Seizure-safe mode available")
        else:
            accommodations_missing.append("Seizure-safe mode")
            recommendations.append("Implement seizure_safe_mode to prevent flashing content")

        # Reduced motion
        if visual_config.get("reduced_motion_support"):
            accommodations_present.append("Reduced motion support")
        else:
            accommodations_missing.append("Reduced motion support")
            recommendations.append("Add reduced_motion_support respecting prefers-reduced-motion")

        # Animation controls
        if visual_config.get("animation_controls"):
            accommodations_present.append("Animation pause/stop controls")
        else:
            accommodations_missing.append("Animation controls")
            recommendations.append("Provide animation_controls to pause/stop all animations")

        # Auto-play prevention
        if accessibility.get("no_auto_play", False):
            accommodations_present.append("Auto-play media prevention")
        else:
            accommodations_missing.append("Auto-play prevention")
            recommendations.append("Set no_auto_play to prevent unexpected media playback")

        # Flash threshold config
        flash_config = visual_config.get("flash_config") or {}
        if flash_config.get("max_frequency_hz", 0) <= self.MAX_FLASH_FREQUENCY:
            accommodations_present.append(f"Flash frequency limited to ≤{self.MAX_FLASH_FREQUENCY}Hz")

        score = self._calculate_score(barriers)

        return DisabilityEvaluation(
            disability_type=self.disability_type,
            accommodation_score=score,
            barriers=barriers,
            accommodations_present=accommodations_present,
            accommodations_missing=accommodations_missing,
            recommendations=recommendations,
        )

    def _check_schema_level(self, schema: dict[str, Any]) -> BarrierAnalysis:
        """Check schema-level neurological accessibility."""
        barriers = []
        accessibility = self._get_accessibility_config(schema)
        default_config = accessibility.get("default_config") or {}
        visual_config = default_config.get("visual_config") or {}

        # Check flash frequency
        flash_config = visual_config.get("flash_config") or {}
        max_flash = flash_config.get("max_frequency_hz", 0)
        if max_flash > self.MAX_FLASH_FREQUENCY:
            barriers.append(
                Barrier(
                    category=BarrierCategory.PERCEPTION,
                    severity=ViolationSeverity.CRITICAL,
                    description=(
                        f"Maximum flash frequency {max_flash}Hz exceeds "
                        f"{self.MAX_FLASH_FREQUENCY}Hz seizure safety limit"
                    ),
                    location="accessibility.default_config.visual_config.flash_config.max_frequency_hz",
                    impact="Flashing content can trigger seizures in users with photosensitive epilepsy",
                    remediation=f"Limit flash frequency to {self.MAX_FLASH_FREQUENCY}Hz or lower",
                )
            )

        # Check for auto-play media
        if accessibility.get("auto_play_enabled", False):
            barriers.append(
                Barrier(
                    category=BarrierCategory.OPERATION,
                    severity=ViolationSeverity.MAJOR,
                    description="Auto-play media is enabled",
                    location="accessibility.auto_play_enabled",
                    impact="Unexpected media playback can be disorienting or trigger episodes",
                    remediation="Disable auto_play_enabled and require user activation",
                )
            )

        return BarrierAnalysis(area="schema", barriers=barriers)

    def _check_component(
        self, component: dict[str, Any], index: int
    ) -> BarrierAnalysis:
        """Check component for neurological accessibility."""
        barriers = []
        comp_id = component.get("component_id", f"component_{index}")
        comp_accessibility = self._get_component_accessibility(component)

        # Check for uncontrollable animations
        animation_config = comp_accessibility.get("animation_config") or {}
        if animation_config.get("enabled") and not animation_config.get("user_controllable"):
            barriers.append(
                Barrier(
                    category=BarrierCategory.OPERATION,
                    severity=ViolationSeverity.MINOR,
                    description=f"Component '{comp_id}' has animations without user controls",
                    location=f"components[{index}].accessibility.animation_config",
                    impact="Users cannot pause or stop animations that may cause discomfort",
                    remediation="Add user_controllable: true to animation_config",
                )
            )

        # Check for flashing content in component
        visual = comp_accessibility.get("visual_config") or {}
        if visual.get("has_flashing_content") and not visual.get("flashing_disabled_option"):
            barriers.append(
                Barrier(
                    category=BarrierCategory.PERCEPTION,
                    severity=ViolationSeverity.CRITICAL,
                    description=f"Component '{comp_id}' has flashing content without disable option",
                    location=f"components[{index}].accessibility.visual_config",
                    impact="Flashing content can trigger seizures",
                    remediation="Add flashing_disabled_option or remove flashing content",
                )
            )

        return BarrierAnalysis(area=comp_id, barriers=barriers)


# ============================================
# Combined Evaluator
# ============================================


class CombinedDisabilityEvaluator:
    """Runs all disability evaluators and combines results."""

    def __init__(self):
        """Initialize all evaluators."""
        self._evaluators: dict[DisabilityType, DisabilityEvaluator] = {
            DisabilityType.VISUAL: VisualAccessibilityEvaluator(),
            DisabilityType.HEARING: HearingAccessibilityEvaluator(),
            DisabilityType.MOTOR: MotorAccessibilityEvaluator(),
            DisabilityType.SPEECH: SpeechAccessibilityEvaluator(),
            DisabilityType.COGNITIVE: CognitiveAccessibilityEvaluator(),
            DisabilityType.NEUROLOGICAL: NeurologicalAccessibilityEvaluator(),
        }

    def evaluate(
        self,
        schema: dict[str, Any],
        disability_types: Optional[list[DisabilityType]] = None,
    ) -> dict[DisabilityType, DisabilityEvaluation]:
        """Evaluate schema for specified disability types.

        Args:
            schema: The LUI schema to evaluate
            disability_types: Types to evaluate (None = all)

        Returns:
            Dictionary mapping disability type to evaluation result
        """
        types_to_check = disability_types or list(DisabilityType)
        results = {}

        for dtype in types_to_check:
            if dtype in self._evaluators:
                results[dtype] = self._evaluators[dtype].evaluate(schema)

        return results

    def evaluate_single(
        self,
        schema: dict[str, Any],
        disability_type: DisabilityType,
    ) -> DisabilityEvaluation:
        """Evaluate schema for a single disability type.

        Args:
            schema: The LUI schema to evaluate
            disability_type: The disability type to evaluate

        Returns:
            DisabilityEvaluation result
        """
        if disability_type not in self._evaluators:
            raise ValueError(f"Unknown disability type: {disability_type}")
        return self._evaluators[disability_type].evaluate(schema)

    def get_overall_score(
        self,
        results: dict[DisabilityType, DisabilityEvaluation],
    ) -> float:
        """Calculate overall accessibility score across all evaluations.

        Args:
            results: Dictionary of evaluation results

        Returns:
            Average accommodation score (0.0-1.0)
        """
        if not results:
            return 1.0
        return sum(r.accommodation_score for r in results.values()) / len(results)

    def get_summary(
        self,
        results: dict[DisabilityType, DisabilityEvaluation],
    ) -> str:
        """Generate a summary of all evaluation results.

        Args:
            results: Dictionary of evaluation results

        Returns:
            Human-readable summary string
        """
        if not results:
            return "No evaluations performed."

        overall_score = self.get_overall_score(results)
        passing = sum(1 for r in results.values() if r.passes)
        total = len(results)

        lines = [
            f"Overall Disability Accessibility Score: {overall_score:.0%}",
            f"Passing: {passing}/{total} disability categories",
            "",
            "By Category:",
        ]

        for dtype, result in sorted(results.items(), key=lambda x: x[0].value):
            status = "✓" if result.passes else "✗"
            lines.append(
                f"  {status} {dtype.value.title()}: {result.accommodation_score:.0%} "
                f"({result.total_barriers} barriers)"
            )

        return "\n".join(lines)
