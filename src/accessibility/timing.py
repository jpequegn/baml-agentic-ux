"""Interaction timing and timeout validation for LUI accessibility.

This module validates timeout and timing configurations to ensure
motor and cognitive accessibility compliance.

Issue #73 - Task 4.7: Interaction Timing Validator
Part of #27 - Phase 4: LUI Accessibility Standards
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .checker import ComplianceLevel, ViolationSeverity


# ============================================
# Configuration Data Classes
# ============================================


@dataclass
class TimeoutConfig:
    """Configuration for interaction timeouts.

    Attributes:
        initial_timeout_seconds: Base timeout duration before expiration
        warning_before_seconds: Seconds before timeout to show warning
        extension_allowed: Whether users can extend the timeout
        extension_seconds: Duration of each timeout extension
        max_extensions: Maximum number of extensions allowed (-1 for unlimited)
    """

    initial_timeout_seconds: int
    warning_before_seconds: int = 0
    extension_allowed: bool = False
    extension_seconds: int = 0
    max_extensions: int = 0


@dataclass
class InputMethodConfig:
    """Configuration for supported input methods.

    Attributes:
        keyboard_accessible: All functions accessible via keyboard
        voice_input: Voice input supported
        touch_input: Touch input supported
        switch_access: Switch device input supported
        eye_tracking: Eye tracking input supported
        gesture_alternatives: Alternatives to complex gestures provided
        pointer_adjustable: Pointer speed/precision adjustable
    """

    keyboard_accessible: bool = True
    voice_input: bool = False
    touch_input: bool = True
    switch_access: bool = False
    eye_tracking: bool = False
    gesture_alternatives: bool = False
    pointer_adjustable: bool = False


@dataclass
class FeedbackConfig:
    """Configuration for user feedback mechanisms.

    Attributes:
        immediate_confirmation: Immediate feedback for user actions
        error_messages_clear: Error messages are clear and actionable
        success_indicators: Visual/audio success indicators
        progress_indicators: Progress shown for long operations
        status_updates: Regular status updates during operations
    """

    immediate_confirmation: bool = True
    error_messages_clear: bool = True
    success_indicators: bool = True
    progress_indicators: bool = False
    status_updates: bool = False


@dataclass
class ErrorHandlingConfig:
    """Configuration for error handling accessibility.

    Attributes:
        error_prevention: Proactive error prevention measures
        error_identification: Clear identification of errors
        error_suggestions: Suggestions for fixing errors
        undo_available: Undo functionality available
        auto_save: Automatic saving of user work
        recovery_options: Recovery options for failures
    """

    error_prevention: bool = True
    error_identification: bool = True
    error_suggestions: bool = False
    undo_available: bool = False
    auto_save: bool = False
    recovery_options: bool = False


@dataclass
class AutoUpdateConfig:
    """Configuration for auto-updating content.

    Attributes:
        has_auto_update: Content auto-updates
        can_pause: User can pause auto-updates
        can_stop: User can stop auto-updates
        can_adjust_frequency: User can adjust update frequency
        update_frequency_seconds: How often content updates
    """

    has_auto_update: bool = False
    can_pause: bool = False
    can_stop: bool = False
    can_adjust_frequency: bool = False
    update_frequency_seconds: int = 0


# ============================================
# Timing Thresholds
# ============================================


@dataclass
class TimingThreshold:
    """Timing thresholds for a compliance level.

    Attributes:
        min_timeout_seconds: Minimum initial timeout duration
        min_warning_seconds: Minimum warning time before timeout
        extension_required: Whether extension mechanism is required
        unlimited_extensions: Whether unlimited extensions required
    """

    min_timeout_seconds: int
    min_warning_seconds: int
    extension_required: bool
    unlimited_extensions: bool = False


# Timing thresholds by compliance level
TIMING_THRESHOLDS: dict[ComplianceLevel, TimingThreshold] = {
    ComplianceLevel.LEVEL_A: TimingThreshold(
        min_timeout_seconds=20,
        min_warning_seconds=5,
        extension_required=False,
        unlimited_extensions=False,
    ),
    ComplianceLevel.LEVEL_AA: TimingThreshold(
        min_timeout_seconds=30,
        min_warning_seconds=10,
        extension_required=True,
        unlimited_extensions=False,
    ),
    ComplianceLevel.LEVEL_AAA: TimingThreshold(
        min_timeout_seconds=60,
        min_warning_seconds=20,
        extension_required=True,
        unlimited_extensions=True,
    ),
}


# Input method requirements by level
INPUT_REQUIREMENTS: dict[ComplianceLevel, dict[str, bool]] = {
    ComplianceLevel.LEVEL_A: {
        "keyboard_accessible": True,
        "gesture_alternatives": False,
        "voice_input": False,
        "switch_access": False,
    },
    ComplianceLevel.LEVEL_AA: {
        "keyboard_accessible": True,
        "gesture_alternatives": True,
        "voice_input": False,
        "switch_access": False,
    },
    ComplianceLevel.LEVEL_AAA: {
        "keyboard_accessible": True,
        "gesture_alternatives": True,
        "voice_input": True,
        "switch_access": True,
    },
}


# ============================================
# Validation Result Types
# ============================================


@dataclass
class TimingViolation:
    """A timing-related accessibility violation.

    Attributes:
        code: Violation code (e.g., "TIMEOUT_TOO_SHORT")
        severity: Severity level
        description: Human-readable description
        location: Where in the config the violation exists
        remediation: Suggested fix
        threshold_expected: Expected threshold value
        threshold_actual: Actual value found
    """

    code: str
    severity: ViolationSeverity
    description: str
    location: str
    remediation: str
    threshold_expected: Optional[Any] = None
    threshold_actual: Optional[Any] = None

    @property
    def weight(self) -> float:
        """Get severity weight for scoring."""
        weights = {
            ViolationSeverity.CRITICAL: 0.25,
            ViolationSeverity.MAJOR: 0.15,
            ViolationSeverity.MINOR: 0.05,
            ViolationSeverity.ADVISORY: 0.02,
        }
        return weights.get(self.severity, 0.05)


@dataclass
class TimingValidationResult:
    """Result of timing validation.

    Attributes:
        config_type: Type of config validated
        target_level: Target compliance level
        achieved_level: Highest level achieved
        score: Validation score 0.0-1.0
        passes: Whether validation passed for target level
        violations: List of violations found
        recommendations: Prioritized recommendations
        summary: Human-readable summary
    """

    config_type: str
    target_level: ComplianceLevel
    achieved_level: Optional[ComplianceLevel]
    score: float
    passes: bool
    violations: list[TimingViolation] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    summary: str = ""

    @property
    def critical_count(self) -> int:
        """Count of critical violations."""
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.CRITICAL)

    @property
    def major_count(self) -> int:
        """Count of major violations."""
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.MAJOR)

    def __post_init__(self):
        """Generate summary if not provided."""
        if not self.summary:
            self.summary = self._generate_summary()

    def _generate_summary(self) -> str:
        """Generate human-readable summary."""
        status = "PASSES" if self.passes else "FAILS"
        achieved = self.achieved_level.value if self.achieved_level else "None"
        return (
            f"Timing validation {status} for {self.target_level.value}. "
            f"Score: {self.score:.0%}. Achieved: {achieved}. "
            f"Violations: {len(self.violations)} "
            f"({self.critical_count} critical, {self.major_count} major)."
        )


@dataclass
class InputValidationResult:
    """Result of input method validation.

    Attributes:
        target_level: Target compliance level
        achieved_level: Highest level achieved
        score: Validation score 0.0-1.0
        passes: Whether validation passed
        violations: List of violations found
        supported_methods: List of supported input methods
        missing_methods: List of missing required methods
        summary: Human-readable summary
    """

    target_level: ComplianceLevel
    achieved_level: Optional[ComplianceLevel]
    score: float
    passes: bool
    violations: list[TimingViolation] = field(default_factory=list)
    supported_methods: list[str] = field(default_factory=list)
    missing_methods: list[str] = field(default_factory=list)
    summary: str = ""

    def __post_init__(self):
        """Generate summary if not provided."""
        if not self.summary:
            status = "PASSES" if self.passes else "FAILS"
            achieved = self.achieved_level.value if self.achieved_level else "None"
            self.summary = (
                f"Input validation {status} for {self.target_level.value}. "
                f"Score: {self.score:.0%}. Achieved: {achieved}. "
                f"Supported: {len(self.supported_methods)}, Missing: {len(self.missing_methods)}."
            )


@dataclass
class InteractionValidationResult:
    """Combined interaction timing and input validation result.

    Attributes:
        component_id: ID of component being validated
        target_level: Target compliance level
        timing_result: Timeout validation result
        input_result: Input method validation result
        feedback_result: Feedback config validation result
        error_handling_result: Error handling validation result
        auto_update_result: Auto-update validation result
        overall_score: Combined score
        overall_passes: Whether all validations pass
        summary: Human-readable summary
    """

    component_id: str
    target_level: ComplianceLevel
    timing_result: Optional[TimingValidationResult] = None
    input_result: Optional[InputValidationResult] = None
    feedback_result: Optional[TimingValidationResult] = None
    error_handling_result: Optional[TimingValidationResult] = None
    auto_update_result: Optional[TimingValidationResult] = None
    overall_score: float = 0.0
    overall_passes: bool = False
    summary: str = ""

    def __post_init__(self):
        """Calculate overall score and status."""
        results = [
            r for r in [
                self.timing_result,
                self.input_result,
                self.feedback_result,
                self.error_handling_result,
                self.auto_update_result,
            ]
            if r is not None
        ]

        if results:
            self.overall_score = sum(r.score for r in results) / len(results)
            self.overall_passes = all(r.passes for r in results)
        else:
            self.overall_score = 1.0
            self.overall_passes = True

        if not self.summary:
            status = "PASSES" if self.overall_passes else "FAILS"
            self.summary = (
                f"Interaction validation for '{self.component_id}' {status} "
                f"at {self.target_level.value}. Overall score: {self.overall_score:.0%}."
            )


# ============================================
# Validators
# ============================================


class InteractionTimingValidator:
    """Validates timeout and timing configurations for accessibility."""

    def validate_timeout(
        self,
        config: TimeoutConfig,
        target_level: ComplianceLevel,
    ) -> TimingValidationResult:
        """Validate timeout configuration against compliance level.

        Args:
            config: Timeout configuration to validate
            target_level: Target compliance level

        Returns:
            TimingValidationResult with validation details
        """
        violations: list[TimingViolation] = []
        recommendations: list[str] = []
        threshold = TIMING_THRESHOLDS[target_level]

        # Check initial timeout duration
        if config.initial_timeout_seconds < threshold.min_timeout_seconds:
            violations.append(
                TimingViolation(
                    code="TIMEOUT_TOO_SHORT",
                    severity=ViolationSeverity.CRITICAL,
                    description=(
                        f"Initial timeout {config.initial_timeout_seconds}s is below "
                        f"minimum {threshold.min_timeout_seconds}s for {target_level.value}"
                    ),
                    location="initial_timeout_seconds",
                    remediation=f"Increase timeout to at least {threshold.min_timeout_seconds} seconds",
                    threshold_expected=threshold.min_timeout_seconds,
                    threshold_actual=config.initial_timeout_seconds,
                )
            )
            recommendations.append(
                f"Increase initial timeout from {config.initial_timeout_seconds}s "
                f"to at least {threshold.min_timeout_seconds}s"
            )

        # Check warning time
        if config.warning_before_seconds < threshold.min_warning_seconds:
            severity = ViolationSeverity.MAJOR if target_level == ComplianceLevel.LEVEL_AAA else ViolationSeverity.MINOR
            violations.append(
                TimingViolation(
                    code="WARNING_TIME_INSUFFICIENT",
                    severity=severity,
                    description=(
                        f"Warning time {config.warning_before_seconds}s is below "
                        f"minimum {threshold.min_warning_seconds}s for {target_level.value}"
                    ),
                    location="warning_before_seconds",
                    remediation=f"Increase warning time to at least {threshold.min_warning_seconds} seconds",
                    threshold_expected=threshold.min_warning_seconds,
                    threshold_actual=config.warning_before_seconds,
                )
            )
            recommendations.append(
                f"Increase warning time from {config.warning_before_seconds}s "
                f"to at least {threshold.min_warning_seconds}s"
            )

        # Check extension mechanism
        if threshold.extension_required and not config.extension_allowed:
            violations.append(
                TimingViolation(
                    code="EXTENSION_NOT_ALLOWED",
                    severity=ViolationSeverity.CRITICAL,
                    description=f"Timeout extension is required for {target_level.value} but not enabled",
                    location="extension_allowed",
                    remediation="Enable timeout extension mechanism",
                    threshold_expected=True,
                    threshold_actual=config.extension_allowed,
                )
            )
            recommendations.append("Enable timeout extension for users who need more time")

        # Check unlimited extensions for AAA
        if threshold.unlimited_extensions and config.max_extensions >= 0:
            violations.append(
                TimingViolation(
                    code="EXTENSIONS_LIMITED",
                    severity=ViolationSeverity.MAJOR,
                    description=f"Level {target_level.value} requires unlimited extensions, but max is {config.max_extensions}",
                    location="max_extensions",
                    remediation="Set max_extensions to -1 for unlimited extensions",
                    threshold_expected=-1,
                    threshold_actual=config.max_extensions,
                )
            )
            recommendations.append("Allow unlimited timeout extensions for AAA compliance")

        # Check extension duration is meaningful
        if config.extension_allowed and config.extension_seconds < 10:
            violations.append(
                TimingViolation(
                    code="EXTENSION_TOO_SHORT",
                    severity=ViolationSeverity.MINOR,
                    description=f"Extension duration {config.extension_seconds}s may be too short to be useful",
                    location="extension_seconds",
                    remediation="Increase extension duration to at least 10 seconds",
                    threshold_expected=10,
                    threshold_actual=config.extension_seconds,
                )
            )
            recommendations.append("Increase extension duration to at least 10 seconds")

        # Calculate score and determine achieved level
        score = self._calculate_score(violations)
        achieved_level = self._determine_achieved_level_timeout(config)
        passes = len([v for v in violations if v.severity == ViolationSeverity.CRITICAL]) == 0 and score >= 0.7

        return TimingValidationResult(
            config_type="TimeoutConfig",
            target_level=target_level,
            achieved_level=achieved_level,
            score=score,
            passes=passes,
            violations=violations,
            recommendations=recommendations,
        )

    def validate_input_methods(
        self,
        config: InputMethodConfig,
        target_level: ComplianceLevel,
    ) -> InputValidationResult:
        """Validate input method configuration against compliance level.

        Args:
            config: Input method configuration to validate
            target_level: Target compliance level

        Returns:
            InputValidationResult with validation details
        """
        violations: list[TimingViolation] = []
        supported_methods: list[str] = []
        missing_methods: list[str] = []
        requirements = INPUT_REQUIREMENTS[target_level]

        # Check keyboard accessibility (required for all levels)
        if config.keyboard_accessible:
            supported_methods.append("keyboard")
        else:
            missing_methods.append("keyboard")
            violations.append(
                TimingViolation(
                    code="KEYBOARD_NOT_ACCESSIBLE",
                    severity=ViolationSeverity.CRITICAL,
                    description="Keyboard accessibility is required for all compliance levels",
                    location="keyboard_accessible",
                    remediation="Ensure all functionality is keyboard accessible",
                )
            )

        # Check gesture alternatives (AA+)
        if requirements["gesture_alternatives"]:
            if config.gesture_alternatives:
                supported_methods.append("gesture_alternatives")
            else:
                missing_methods.append("gesture_alternatives")
                violations.append(
                    TimingViolation(
                        code="GESTURE_ALTERNATIVES_MISSING",
                        severity=ViolationSeverity.MAJOR,
                        description=f"Gesture alternatives required for {target_level.value}",
                        location="gesture_alternatives",
                        remediation="Provide alternatives for all gesture-based interactions",
                    )
                )

        # Check voice input (AAA)
        if requirements["voice_input"]:
            if config.voice_input:
                supported_methods.append("voice_input")
            else:
                missing_methods.append("voice_input")
                violations.append(
                    TimingViolation(
                        code="VOICE_INPUT_MISSING",
                        severity=ViolationSeverity.MAJOR,
                        description=f"Voice input support required for {target_level.value}",
                        location="voice_input",
                        remediation="Add voice input as an alternative input method",
                    )
                )

        # Check switch access (AAA)
        if requirements["switch_access"]:
            if config.switch_access:
                supported_methods.append("switch_access")
            else:
                missing_methods.append("switch_access")
                violations.append(
                    TimingViolation(
                        code="SWITCH_ACCESS_MISSING",
                        severity=ViolationSeverity.MAJOR,
                        description=f"Switch access support required for {target_level.value}",
                        location="switch_access",
                        remediation="Add switch device support for motor accessibility",
                    )
                )

        # Add optional supported methods
        if config.touch_input:
            supported_methods.append("touch_input")
        if config.eye_tracking:
            supported_methods.append("eye_tracking")
        if config.pointer_adjustable:
            supported_methods.append("pointer_adjustable")

        # Calculate score and determine level
        score = self._calculate_score(violations)
        achieved_level = self._determine_achieved_level_input(config)
        passes = len([v for v in violations if v.severity == ViolationSeverity.CRITICAL]) == 0 and score >= 0.7

        return InputValidationResult(
            target_level=target_level,
            achieved_level=achieved_level,
            score=score,
            passes=passes,
            violations=violations,
            supported_methods=supported_methods,
            missing_methods=missing_methods,
        )

    def validate_feedback(
        self,
        config: FeedbackConfig,
        target_level: ComplianceLevel,
    ) -> TimingValidationResult:
        """Validate feedback configuration for accessibility.

        Args:
            config: Feedback configuration to validate
            target_level: Target compliance level

        Returns:
            TimingValidationResult with validation details
        """
        violations: list[TimingViolation] = []
        recommendations: list[str] = []

        # Immediate confirmation is important at all levels
        if not config.immediate_confirmation:
            violations.append(
                TimingViolation(
                    code="NO_IMMEDIATE_CONFIRMATION",
                    severity=ViolationSeverity.MAJOR,
                    description="Users should receive immediate confirmation of their actions",
                    location="immediate_confirmation",
                    remediation="Provide immediate feedback for all user actions",
                )
            )
            recommendations.append("Add immediate confirmation for user actions")

        # Clear error messages are important at all levels
        if not config.error_messages_clear:
            violations.append(
                TimingViolation(
                    code="ERROR_MESSAGES_UNCLEAR",
                    severity=ViolationSeverity.MAJOR,
                    description="Error messages should be clear and actionable",
                    location="error_messages_clear",
                    remediation="Ensure error messages explain what went wrong and how to fix it",
                )
            )
            recommendations.append("Improve error messages to be clear and actionable")

        # Progress indicators required for AA+
        if target_level in [ComplianceLevel.LEVEL_AA, ComplianceLevel.LEVEL_AAA]:
            if not config.progress_indicators:
                violations.append(
                    TimingViolation(
                        code="NO_PROGRESS_INDICATORS",
                        severity=ViolationSeverity.MINOR,
                        description=f"Progress indicators required for {target_level.value}",
                        location="progress_indicators",
                        remediation="Add progress indicators for long-running operations",
                    )
                )
                recommendations.append("Add progress indicators for operations taking more than a few seconds")

        # Status updates required for AAA
        if target_level == ComplianceLevel.LEVEL_AAA:
            if not config.status_updates:
                violations.append(
                    TimingViolation(
                        code="NO_STATUS_UPDATES",
                        severity=ViolationSeverity.MINOR,
                        description="Regular status updates required for AAA",
                        location="status_updates",
                        remediation="Provide regular status updates during long operations",
                    )
                )
                recommendations.append("Provide status updates during long operations")

        score = self._calculate_score(violations)
        passes = len([v for v in violations if v.severity == ViolationSeverity.CRITICAL]) == 0 and score >= 0.7

        return TimingValidationResult(
            config_type="FeedbackConfig",
            target_level=target_level,
            achieved_level=self._determine_achieved_level_feedback(config),
            score=score,
            passes=passes,
            violations=violations,
            recommendations=recommendations,
        )

    def validate_error_handling(
        self,
        config: ErrorHandlingConfig,
        target_level: ComplianceLevel,
    ) -> TimingValidationResult:
        """Validate error handling configuration for accessibility.

        Args:
            config: Error handling configuration to validate
            target_level: Target compliance level

        Returns:
            TimingValidationResult with validation details
        """
        violations: list[TimingViolation] = []
        recommendations: list[str] = []

        # Error prevention is important at all levels
        if not config.error_prevention:
            violations.append(
                TimingViolation(
                    code="NO_ERROR_PREVENTION",
                    severity=ViolationSeverity.MINOR,
                    description="Error prevention measures should be implemented",
                    location="error_prevention",
                    remediation="Add proactive error prevention (validation, constraints)",
                )
            )
            recommendations.append("Implement error prevention measures")

        # Error identification required at all levels
        if not config.error_identification:
            violations.append(
                TimingViolation(
                    code="ERROR_IDENTIFICATION_MISSING",
                    severity=ViolationSeverity.MAJOR,
                    description="Clear error identification is required",
                    location="error_identification",
                    remediation="Ensure errors are clearly identified to users",
                )
            )
            recommendations.append("Add clear error identification")

        # Undo required for AA+
        if target_level in [ComplianceLevel.LEVEL_AA, ComplianceLevel.LEVEL_AAA]:
            if not config.undo_available:
                violations.append(
                    TimingViolation(
                        code="NO_UNDO",
                        severity=ViolationSeverity.MAJOR if target_level == ComplianceLevel.LEVEL_AAA else ViolationSeverity.MINOR,
                        description=f"Undo functionality required for {target_level.value}",
                        location="undo_available",
                        remediation="Implement undo functionality for user actions",
                    )
                )
                recommendations.append("Implement undo functionality")

        # Error suggestions required for AA+
        if target_level in [ComplianceLevel.LEVEL_AA, ComplianceLevel.LEVEL_AAA]:
            if not config.error_suggestions:
                violations.append(
                    TimingViolation(
                        code="NO_ERROR_SUGGESTIONS",
                        severity=ViolationSeverity.MINOR,
                        description=f"Error suggestions required for {target_level.value}",
                        location="error_suggestions",
                        remediation="Provide suggestions for fixing errors",
                    )
                )
                recommendations.append("Add suggestions for fixing errors")

        # Auto-save required for AAA
        if target_level == ComplianceLevel.LEVEL_AAA:
            if not config.auto_save:
                violations.append(
                    TimingViolation(
                        code="NO_AUTO_SAVE",
                        severity=ViolationSeverity.MINOR,
                        description="Auto-save functionality required for AAA",
                        location="auto_save",
                        remediation="Implement auto-save to prevent data loss",
                    )
                )
                recommendations.append("Implement auto-save functionality")

        score = self._calculate_score(violations)
        passes = len([v for v in violations if v.severity == ViolationSeverity.CRITICAL]) == 0 and score >= 0.7

        return TimingValidationResult(
            config_type="ErrorHandlingConfig",
            target_level=target_level,
            achieved_level=self._determine_achieved_level_error(config),
            score=score,
            passes=passes,
            violations=violations,
            recommendations=recommendations,
        )

    def validate_auto_update(
        self,
        config: AutoUpdateConfig,
        target_level: ComplianceLevel,
    ) -> TimingValidationResult:
        """Validate auto-updating content configuration.

        Args:
            config: Auto-update configuration to validate
            target_level: Target compliance level

        Returns:
            TimingValidationResult with validation details
        """
        violations: list[TimingViolation] = []
        recommendations: list[str] = []

        # If no auto-update, no issues
        if not config.has_auto_update:
            return TimingValidationResult(
                config_type="AutoUpdateConfig",
                target_level=target_level,
                achieved_level=ComplianceLevel.LEVEL_AAA,
                score=1.0,
                passes=True,
                violations=[],
                recommendations=[],
            )

        # Pause control required at all levels
        if not config.can_pause:
            violations.append(
                TimingViolation(
                    code="CANNOT_PAUSE_AUTO_UPDATE",
                    severity=ViolationSeverity.CRITICAL,
                    description="Users must be able to pause auto-updating content",
                    location="can_pause",
                    remediation="Add pause control for auto-updating content",
                )
            )
            recommendations.append("Add pause control for auto-updating content")

        # Stop control required at all levels
        if not config.can_stop:
            violations.append(
                TimingViolation(
                    code="CANNOT_STOP_AUTO_UPDATE",
                    severity=ViolationSeverity.CRITICAL,
                    description="Users must be able to stop auto-updating content",
                    location="can_stop",
                    remediation="Add stop control for auto-updating content",
                )
            )
            recommendations.append("Add stop control for auto-updating content")

        # Frequency adjustment for AAA
        if target_level == ComplianceLevel.LEVEL_AAA:
            if not config.can_adjust_frequency:
                violations.append(
                    TimingViolation(
                        code="CANNOT_ADJUST_FREQUENCY",
                        severity=ViolationSeverity.MINOR,
                        description="Users should be able to adjust update frequency for AAA",
                        location="can_adjust_frequency",
                        remediation="Add frequency adjustment control for auto-updating content",
                    )
                )
                recommendations.append("Allow users to adjust auto-update frequency")

        # Check update frequency is not too aggressive
        if config.update_frequency_seconds > 0 and config.update_frequency_seconds < 5:
            violations.append(
                TimingViolation(
                    code="UPDATE_FREQUENCY_TOO_HIGH",
                    severity=ViolationSeverity.MAJOR,
                    description=f"Update frequency of {config.update_frequency_seconds}s is too aggressive",
                    location="update_frequency_seconds",
                    remediation="Reduce update frequency to at least 5 seconds",
                    threshold_expected=5,
                    threshold_actual=config.update_frequency_seconds,
                )
            )
            recommendations.append("Reduce auto-update frequency to at least 5 seconds")

        score = self._calculate_score(violations)
        passes = len([v for v in violations if v.severity == ViolationSeverity.CRITICAL]) == 0 and score >= 0.7

        return TimingValidationResult(
            config_type="AutoUpdateConfig",
            target_level=target_level,
            achieved_level=self._determine_achieved_level_auto_update(config),
            score=score,
            passes=passes,
            violations=violations,
            recommendations=recommendations,
        )

    def validate_interaction(
        self,
        component_id: str,
        target_level: ComplianceLevel,
        timeout_config: Optional[TimeoutConfig] = None,
        input_config: Optional[InputMethodConfig] = None,
        feedback_config: Optional[FeedbackConfig] = None,
        error_config: Optional[ErrorHandlingConfig] = None,
        auto_update_config: Optional[AutoUpdateConfig] = None,
    ) -> InteractionValidationResult:
        """Validate complete interaction configuration.

        Args:
            component_id: ID of the component being validated
            target_level: Target compliance level
            timeout_config: Timeout configuration (optional)
            input_config: Input method configuration (optional)
            feedback_config: Feedback configuration (optional)
            error_config: Error handling configuration (optional)
            auto_update_config: Auto-update configuration (optional)

        Returns:
            InteractionValidationResult with all validation results
        """
        timing_result = None
        input_result = None
        feedback_result = None
        error_result = None
        auto_update_result = None

        if timeout_config:
            timing_result = self.validate_timeout(timeout_config, target_level)
        if input_config:
            input_result = self.validate_input_methods(input_config, target_level)
        if feedback_config:
            feedback_result = self.validate_feedback(feedback_config, target_level)
        if error_config:
            error_result = self.validate_error_handling(error_config, target_level)
        if auto_update_config:
            auto_update_result = self.validate_auto_update(auto_update_config, target_level)

        return InteractionValidationResult(
            component_id=component_id,
            target_level=target_level,
            timing_result=timing_result,
            input_result=input_result,
            feedback_result=feedback_result,
            error_handling_result=error_result,
            auto_update_result=auto_update_result,
        )

    def check_timing_essential(
        self,
        requires_real_time: bool,
        has_time_limit: bool,
        allows_pause: bool,
        target_level: ComplianceLevel,
    ) -> list[TimingViolation]:
        """Check for timing-essential interaction issues.

        Timing-essential interactions (where timing is fundamental to the
        activity) are restricted at AA and AAA levels.

        Args:
            requires_real_time: Whether interaction requires real-time response
            has_time_limit: Whether there's a time limit on the interaction
            allows_pause: Whether the interaction can be paused
            target_level: Target compliance level

        Returns:
            List of violations if timing-essential issues found
        """
        violations = []

        if target_level in [ComplianceLevel.LEVEL_AA, ComplianceLevel.LEVEL_AAA]:
            if requires_real_time and has_time_limit:
                if not allows_pause:
                    violations.append(
                        TimingViolation(
                            code="TIMING_ESSENTIAL_NO_PAUSE",
                            severity=ViolationSeverity.CRITICAL,
                            description=(
                                "Timing-essential interactions must allow pause at "
                                f"{target_level.value} level"
                            ),
                            location="timing_essential",
                            remediation="Allow users to pause timing-essential interactions",
                        )
                    )

        return violations

    def _calculate_score(self, violations: list[TimingViolation]) -> float:
        """Calculate score from violations."""
        if not violations:
            return 1.0

        total_weight = sum(v.weight for v in violations)
        return max(0.0, min(1.0, 1.0 - total_weight))

    def _determine_achieved_level_timeout(
        self, config: TimeoutConfig
    ) -> Optional[ComplianceLevel]:
        """Determine highest timeout compliance level achieved."""
        # Check AAA first
        threshold_aaa = TIMING_THRESHOLDS[ComplianceLevel.LEVEL_AAA]
        if (
            config.initial_timeout_seconds >= threshold_aaa.min_timeout_seconds
            and config.warning_before_seconds >= threshold_aaa.min_warning_seconds
            and config.extension_allowed
            and config.max_extensions < 0  # unlimited
        ):
            return ComplianceLevel.LEVEL_AAA

        # Check AA
        threshold_aa = TIMING_THRESHOLDS[ComplianceLevel.LEVEL_AA]
        if (
            config.initial_timeout_seconds >= threshold_aa.min_timeout_seconds
            and config.warning_before_seconds >= threshold_aa.min_warning_seconds
            and config.extension_allowed
        ):
            return ComplianceLevel.LEVEL_AA

        # Check A
        threshold_a = TIMING_THRESHOLDS[ComplianceLevel.LEVEL_A]
        if config.initial_timeout_seconds >= threshold_a.min_timeout_seconds:
            return ComplianceLevel.LEVEL_A

        return None

    def _determine_achieved_level_input(
        self, config: InputMethodConfig
    ) -> Optional[ComplianceLevel]:
        """Determine highest input method compliance level achieved."""
        if not config.keyboard_accessible:
            return None

        # Check AAA
        if (
            config.gesture_alternatives
            and config.voice_input
            and config.switch_access
        ):
            return ComplianceLevel.LEVEL_AAA

        # Check AA
        if config.gesture_alternatives:
            return ComplianceLevel.LEVEL_AA

        return ComplianceLevel.LEVEL_A

    def _determine_achieved_level_feedback(
        self, config: FeedbackConfig
    ) -> Optional[ComplianceLevel]:
        """Determine highest feedback compliance level achieved."""
        if not config.immediate_confirmation or not config.error_messages_clear:
            return None

        if config.progress_indicators and config.status_updates:
            return ComplianceLevel.LEVEL_AAA

        if config.progress_indicators:
            return ComplianceLevel.LEVEL_AA

        return ComplianceLevel.LEVEL_A

    def _determine_achieved_level_error(
        self, config: ErrorHandlingConfig
    ) -> Optional[ComplianceLevel]:
        """Determine highest error handling compliance level achieved."""
        if not config.error_identification:
            return None

        if (
            config.undo_available
            and config.error_suggestions
            and config.auto_save
            and config.recovery_options
        ):
            return ComplianceLevel.LEVEL_AAA

        if config.undo_available and config.error_suggestions:
            return ComplianceLevel.LEVEL_AA

        return ComplianceLevel.LEVEL_A

    def _determine_achieved_level_auto_update(
        self, config: AutoUpdateConfig
    ) -> Optional[ComplianceLevel]:
        """Determine highest auto-update compliance level achieved."""
        if not config.has_auto_update:
            return ComplianceLevel.LEVEL_AAA

        if not config.can_pause or not config.can_stop:
            return None

        if config.can_adjust_frequency:
            return ComplianceLevel.LEVEL_AAA

        return ComplianceLevel.LEVEL_AA
