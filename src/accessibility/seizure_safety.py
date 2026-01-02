"""Seizure safety validation for LUI accessibility.

This module validates content for seizure safety per WCAG 2.3 guidelines
to prevent photosensitive seizure triggers.

Issue #74 - Task 4.8: Seizure Safety Checker
Part of #27 - Phase 4: LUI Accessibility Standards
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .checker import ComplianceLevel, ViolationSeverity


# ============================================
# Constants
# ============================================

# Maximum safe flash frequency (Hz) per WCAG 2.3.1
MAX_FLASH_FREQUENCY_HZ = 3.0

# Maximum flash area as percentage of field of view
MAX_FLASH_AREA_PERCENT = 10.0

# Red flash luminance threshold (relative units)
# Red flashes are more dangerous and have stricter limits
RED_FLASH_LUMINANCE_THRESHOLD = 0.8

# Maximum consecutive flashes before triggering warning
MAX_CONSECUTIVE_FLASHES = 3

# Minimum animation duration warning threshold (ms)
MIN_ANIMATION_DURATION_MS = 100

# Maximum auto-play duration before requiring controls (seconds)
MAX_AUTO_PLAY_DURATION_SECONDS = 5.0

# Severity weights for scoring
SEVERITY_WEIGHTS = {
    ViolationSeverity.CRITICAL: 0.25,
    ViolationSeverity.MAJOR: 0.15,
    ViolationSeverity.MINOR: 0.05,
    ViolationSeverity.ADVISORY: 0.02,
}


# ============================================
# WCAG 2.3 Criteria
# ============================================


class SeizureCriterion(Enum):
    """WCAG 2.3 Seizure and Physical Reactions criteria."""

    SC_2_3_1 = "2.3.1"  # Three Flashes or Below Threshold (Level A)
    SC_2_3_2 = "2.3.2"  # Three Flashes (Level AAA)
    SC_2_3_3 = "2.3.3"  # Animation from Interactions (Level AAA)


# Criteria requirements by compliance level
CRITERIA_BY_LEVEL = {
    ComplianceLevel.LEVEL_A: [SeizureCriterion.SC_2_3_1],
    ComplianceLevel.LEVEL_AA: [SeizureCriterion.SC_2_3_1],
    ComplianceLevel.LEVEL_AAA: [
        SeizureCriterion.SC_2_3_1,
        SeizureCriterion.SC_2_3_2,
        SeizureCriterion.SC_2_3_3,
    ],
}


# ============================================
# Flash Types
# ============================================


class FlashType(Enum):
    """Types of potentially dangerous flashes."""

    GENERAL = "general"  # Standard luminance flash
    RED = "red"  # Red/saturated red flash (more dangerous)
    PATTERN = "pattern"  # Repeating pattern that could flash


# ============================================
# Result Data Classes
# ============================================


@dataclass
class SeizureViolation:
    """A seizure safety violation.

    Attributes:
        criterion: WCAG criterion violated
        severity: Severity level of the violation
        description: Human-readable description
        location: Where the violation was found
        remediation: Suggested fix
        flash_type: Type of flash if applicable
        measured_value: The measured value that caused violation
        threshold_value: The threshold that was exceeded
    """

    criterion: SeizureCriterion
    severity: ViolationSeverity
    description: str
    location: str
    remediation: str
    flash_type: Optional[FlashType] = None
    measured_value: Optional[float] = None
    threshold_value: Optional[float] = None

    @property
    def weight(self) -> float:
        """Get the weight for this violation's severity."""
        return SEVERITY_WEIGHTS.get(self.severity, 0.0)


@dataclass
class FlashAnalysis:
    """Analysis of flash content.

    Attributes:
        has_flashes: Whether content has flashing elements
        flash_frequency_hz: Measured flash frequency
        flash_area_percent: Flash area as percentage of FOV
        flash_type: Type of flash detected
        is_safe: Whether the flash is within safe limits
        consecutive_flashes: Number of consecutive flashes
        exceeds_frequency: Whether frequency exceeds safe limit
        exceeds_area: Whether area exceeds safe limit
        is_red_flash: Whether flash contains dangerous red
    """

    has_flashes: bool = False
    flash_frequency_hz: float = 0.0
    flash_area_percent: float = 0.0
    flash_type: FlashType = FlashType.GENERAL
    is_safe: bool = True
    consecutive_flashes: int = 0
    exceeds_frequency: bool = False
    exceeds_area: bool = False
    is_red_flash: bool = False


@dataclass
class AnimationConfig:
    """Configuration for an animation.

    Attributes:
        animation_id: Identifier for the animation
        frequency_hz: Animation frequency in Hz
        duration_ms: Animation duration in milliseconds
        area_percent: Area covered as percentage of viewport
        has_flash: Whether animation includes flashing
        is_red: Whether animation contains red flash
        auto_plays: Whether animation auto-plays
        has_pause_control: Whether pause control is available
        has_stop_control: Whether stop control is available
        respects_reduced_motion: Whether it respects prefers-reduced-motion
        loops: Whether animation loops
        loop_count: Number of loops (-1 for infinite)
    """

    animation_id: str = ""
    frequency_hz: float = 0.0
    duration_ms: float = 0.0
    area_percent: float = 0.0
    has_flash: bool = False
    is_red: bool = False
    auto_plays: bool = False
    has_pause_control: bool = True
    has_stop_control: bool = True
    respects_reduced_motion: bool = True
    loops: bool = False
    loop_count: int = 0


@dataclass
class AnimationSafetyResult:
    """Result of animation safety analysis.

    Attributes:
        animation_id: ID of the animation analyzed
        passes: Whether animation passes safety checks
        score: Safety score from 0.0 to 1.0
        violations: List of safety violations
        flash_analysis: Flash content analysis
        has_required_controls: Whether required controls exist
        respects_user_preferences: Whether user motion preferences respected
        recommendations: Suggested improvements
        summary: Human-readable summary
    """

    animation_id: str
    passes: bool
    score: float
    violations: list[SeizureViolation] = field(default_factory=list)
    flash_analysis: Optional[FlashAnalysis] = None
    has_required_controls: bool = True
    respects_user_preferences: bool = True
    recommendations: list[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class MediaConfig:
    """Configuration for media content.

    Attributes:
        media_id: Identifier for the media
        media_type: Type of media (video, gif, etc.)
        auto_plays: Whether media auto-plays
        has_pause_control: Whether pause control is available
        has_stop_control: Whether stop control is available
        duration_seconds: Duration of media in seconds
        has_flashing_content: Whether media contains flashing
        flash_frequency_hz: Flash frequency if applicable
        respects_reduced_motion: Whether it respects prefers-reduced-motion
    """

    media_id: str = ""
    media_type: str = ""
    auto_plays: bool = False
    has_pause_control: bool = True
    has_stop_control: bool = True
    duration_seconds: float = 0.0
    has_flashing_content: bool = False
    flash_frequency_hz: float = 0.0
    respects_reduced_motion: bool = True


@dataclass
class ContentConfig:
    """Configuration for content to be checked.

    Attributes:
        content_id: Identifier for the content
        animations: List of animation configurations
        media: List of media configurations
        has_auto_updating_content: Whether content auto-updates
        update_frequency_hz: Frequency of updates if applicable
        has_motion_trigger: Whether motion is triggered by user
        respects_reduced_motion: Global reduced motion support
    """

    content_id: str = ""
    animations: list[AnimationConfig] = field(default_factory=list)
    media: list[MediaConfig] = field(default_factory=list)
    has_auto_updating_content: bool = False
    update_frequency_hz: float = 0.0
    has_motion_trigger: bool = False
    respects_reduced_motion: bool = True


@dataclass
class SeizureSafetyResult:
    """Result of seizure safety validation.

    Attributes:
        content_id: ID of content validated
        target_level: Target compliance level
        passes: Whether content passes safety checks
        score: Safety score from 0.0 to 1.0
        violations: List of safety violations
        animation_results: Results for individual animations
        media_results: Results for individual media
        flash_analysis: Overall flash analysis
        has_controls: Whether required controls exist
        respects_reduced_motion: Whether reduced motion is respected
        criteria_met: WCAG criteria that are met
        criteria_failed: WCAG criteria that failed
        recommendations: Suggested improvements
        summary: Human-readable summary
    """

    content_id: str
    target_level: ComplianceLevel
    passes: bool
    score: float
    violations: list[SeizureViolation] = field(default_factory=list)
    animation_results: list[AnimationSafetyResult] = field(default_factory=list)
    media_results: list[AnimationSafetyResult] = field(default_factory=list)
    flash_analysis: Optional[FlashAnalysis] = None
    has_controls: bool = True
    respects_reduced_motion: bool = True
    criteria_met: list[SeizureCriterion] = field(default_factory=list)
    criteria_failed: list[SeizureCriterion] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    summary: str = ""


# ============================================
# Seizure Safety Checker
# ============================================


class SeizureSafetyChecker:
    """Validates content for seizure safety per WCAG 2.3.

    This checker analyzes content for photosensitive seizure triggers
    including flash frequency, flash area, red flashes, and animation
    controls.

    Example:
        >>> checker = SeizureSafetyChecker()
        >>> config = AnimationConfig(frequency_hz=2, area_percent=5)
        >>> result = checker.analyze_animation(config)
        >>> print(result.passes)  # True

        >>> config = AnimationConfig(frequency_hz=5, area_percent=5)
        >>> result = checker.analyze_animation(config)
        >>> print(result.passes)  # False
    """

    def __init__(
        self,
        max_flash_frequency: float = MAX_FLASH_FREQUENCY_HZ,
        max_flash_area: float = MAX_FLASH_AREA_PERCENT,
    ):
        """Initialize the checker with thresholds.

        Args:
            max_flash_frequency: Maximum safe flash frequency in Hz
            max_flash_area: Maximum safe flash area as percent of FOV
        """
        self.max_flash_frequency = max_flash_frequency
        self.max_flash_area = max_flash_area

    # ============================================
    # Flash Detection
    # ============================================

    def analyze_flash(
        self,
        frequency_hz: float,
        area_percent: float,
        is_red: bool = False,
        consecutive_count: int = 1,
    ) -> FlashAnalysis:
        """Analyze flash content for safety.

        Args:
            frequency_hz: Flash frequency in Hz
            area_percent: Flash area as percentage of FOV
            is_red: Whether flash contains saturated red
            consecutive_count: Number of consecutive flashes

        Returns:
            FlashAnalysis with safety assessment
        """
        has_flashes = frequency_hz > 0 or consecutive_count > 1

        # Determine flash type
        flash_type = FlashType.RED if is_red else FlashType.GENERAL

        # Check thresholds
        exceeds_frequency = frequency_hz > self.max_flash_frequency
        exceeds_area = area_percent > self.max_flash_area

        # Red flashes have stricter requirements
        # Per WCAG, red flashes are especially dangerous
        if is_red:
            # For red flashes, even lower frequencies can be dangerous
            exceeds_frequency = frequency_hz > (self.max_flash_frequency * 0.67)

        # Determine overall safety
        is_safe = not (exceeds_frequency or exceeds_area)

        return FlashAnalysis(
            has_flashes=has_flashes,
            flash_frequency_hz=frequency_hz,
            flash_area_percent=area_percent,
            flash_type=flash_type,
            is_safe=is_safe,
            consecutive_flashes=consecutive_count,
            exceeds_frequency=exceeds_frequency,
            exceeds_area=exceeds_area,
            is_red_flash=is_red,
        )

    def _create_flash_violations(
        self, flash_analysis: FlashAnalysis, location: str
    ) -> list[SeizureViolation]:
        """Create violations from flash analysis.

        Args:
            flash_analysis: The flash analysis result
            location: Location identifier for the violation

        Returns:
            List of violations found
        """
        violations = []

        if flash_analysis.exceeds_frequency:
            threshold = self.max_flash_frequency
            if flash_analysis.is_red_flash:
                threshold = self.max_flash_frequency * 0.67
                description = (
                    f"Red flash frequency {flash_analysis.flash_frequency_hz:.1f}Hz "
                    f"exceeds safe limit of {threshold:.1f}Hz"
                )
            else:
                description = (
                    f"Flash frequency {flash_analysis.flash_frequency_hz:.1f}Hz "
                    f"exceeds safe limit of {self.max_flash_frequency:.1f}Hz"
                )

            violations.append(
                SeizureViolation(
                    criterion=SeizureCriterion.SC_2_3_1,
                    severity=ViolationSeverity.CRITICAL,
                    description=description,
                    location=location,
                    remediation="Reduce flash frequency to 3Hz or below",
                    flash_type=flash_analysis.flash_type,
                    measured_value=flash_analysis.flash_frequency_hz,
                    threshold_value=threshold,
                )
            )

        if flash_analysis.exceeds_area:
            violations.append(
                SeizureViolation(
                    criterion=SeizureCriterion.SC_2_3_1,
                    severity=ViolationSeverity.CRITICAL,
                    description=(
                        f"Flash area {flash_analysis.flash_area_percent:.1f}% "
                        f"exceeds safe limit of {self.max_flash_area:.1f}%"
                    ),
                    location=location,
                    remediation="Reduce flash area to less than 10% of viewport",
                    flash_type=flash_analysis.flash_type,
                    measured_value=flash_analysis.flash_area_percent,
                    threshold_value=self.max_flash_area,
                )
            )

        return violations

    # ============================================
    # Animation Validation
    # ============================================

    def analyze_animation(
        self,
        animation_config: AnimationConfig | dict[str, Any],
        target_level: ComplianceLevel = ComplianceLevel.LEVEL_AA,
    ) -> AnimationSafetyResult:
        """Analyze an animation for seizure safety.

        Args:
            animation_config: Animation configuration (dict or AnimationConfig)
            target_level: Target compliance level

        Returns:
            AnimationSafetyResult with safety assessment
        """
        # Convert dict to AnimationConfig if needed
        if isinstance(animation_config, dict):
            config = AnimationConfig(
                animation_id=animation_config.get("animation_id", ""),
                frequency_hz=animation_config.get("frequency_hz", 0.0),
                duration_ms=animation_config.get("duration_ms", 0.0),
                area_percent=animation_config.get("area_percent", 0.0),
                has_flash=animation_config.get("has_flash", False),
                is_red=animation_config.get("is_red", False),
                auto_plays=animation_config.get("auto_plays", False),
                has_pause_control=animation_config.get("has_pause_control", True),
                has_stop_control=animation_config.get("has_stop_control", True),
                respects_reduced_motion=animation_config.get(
                    "respects_reduced_motion", True
                ),
                loops=animation_config.get("loops", False),
                loop_count=animation_config.get("loop_count", 0),
            )
        else:
            config = animation_config

        violations: list[SeizureViolation] = []
        recommendations: list[str] = []

        # Analyze flash content
        flash_analysis = self.analyze_flash(
            frequency_hz=config.frequency_hz,
            area_percent=config.area_percent,
            is_red=config.is_red,
        )

        # Add flash violations
        location = config.animation_id or "animation"
        violations.extend(self._create_flash_violations(flash_analysis, location))

        # Check animation controls
        has_required_controls = True

        if config.auto_plays:
            # Auto-playing animations must have controls
            if not config.has_pause_control:
                has_required_controls = False
                violations.append(
                    SeizureViolation(
                        criterion=SeizureCriterion.SC_2_3_1,
                        severity=ViolationSeverity.MAJOR,
                        description="Auto-playing animation lacks pause control",
                        location=location,
                        remediation="Add pause control for auto-playing animations",
                    )
                )
                recommendations.append("Add pause control")

            if not config.has_stop_control:
                has_required_controls = False
                violations.append(
                    SeizureViolation(
                        criterion=SeizureCriterion.SC_2_3_1,
                        severity=ViolationSeverity.MAJOR,
                        description="Auto-playing animation lacks stop control",
                        location=location,
                        remediation="Add stop control for auto-playing animations",
                    )
                )
                recommendations.append("Add stop control")

        # Check reduced motion support
        respects_user_preferences = config.respects_reduced_motion

        if not respects_user_preferences:
            violations.append(
                SeizureViolation(
                    criterion=SeizureCriterion.SC_2_3_3,
                    severity=ViolationSeverity.MAJOR,
                    description="Animation does not respect prefers-reduced-motion",
                    location=location,
                    remediation="Implement prefers-reduced-motion media query support",
                )
            )
            recommendations.append("Add prefers-reduced-motion support")

        # AAA level: Animation from Interactions (2.3.3)
        if target_level == ComplianceLevel.LEVEL_AAA:
            # Check for motion-triggered animations
            if config.loops and config.loop_count < 0:
                violations.append(
                    SeizureViolation(
                        criterion=SeizureCriterion.SC_2_3_3,
                        severity=ViolationSeverity.MINOR,
                        description="Infinite looping animation detected",
                        location=location,
                        remediation="Limit animation loops or provide disable option",
                    )
                )
                recommendations.append("Limit animation loops")

        # Calculate score
        score = self._calculate_score(violations)

        # Determine if passes
        critical_count = sum(
            1 for v in violations if v.severity == ViolationSeverity.CRITICAL
        )
        passes = score >= 0.70 and critical_count == 0

        # Generate summary
        summary = self._generate_animation_summary(
            config.animation_id, passes, score, len(violations), critical_count
        )

        return AnimationSafetyResult(
            animation_id=config.animation_id,
            passes=passes,
            score=score,
            violations=violations,
            flash_analysis=flash_analysis,
            has_required_controls=has_required_controls,
            respects_user_preferences=respects_user_preferences,
            recommendations=recommendations,
            summary=summary,
        )

    # ============================================
    # Media Validation
    # ============================================

    def analyze_media(
        self,
        media_config: MediaConfig | dict[str, Any],
        target_level: ComplianceLevel = ComplianceLevel.LEVEL_AA,
    ) -> AnimationSafetyResult:
        """Analyze media content for seizure safety.

        Args:
            media_config: Media configuration (dict or MediaConfig)
            target_level: Target compliance level

        Returns:
            AnimationSafetyResult with safety assessment
        """
        # Convert dict to MediaConfig if needed
        if isinstance(media_config, dict):
            config = MediaConfig(
                media_id=media_config.get("media_id", ""),
                media_type=media_config.get("media_type", ""),
                auto_plays=media_config.get("auto_plays", False),
                has_pause_control=media_config.get("has_pause_control", True),
                has_stop_control=media_config.get("has_stop_control", True),
                duration_seconds=media_config.get("duration_seconds", 0.0),
                has_flashing_content=media_config.get("has_flashing_content", False),
                flash_frequency_hz=media_config.get("flash_frequency_hz", 0.0),
                respects_reduced_motion=media_config.get(
                    "respects_reduced_motion", True
                ),
            )
        else:
            config = media_config

        violations: list[SeizureViolation] = []
        recommendations: list[str] = []
        location = config.media_id or "media"

        # Analyze flash content if present
        flash_analysis = None
        if config.has_flashing_content:
            flash_analysis = self.analyze_flash(
                frequency_hz=config.flash_frequency_hz,
                area_percent=100.0,  # Assume full media area
            )
            violations.extend(self._create_flash_violations(flash_analysis, location))

        # Check auto-play
        has_required_controls = True

        if config.auto_plays:
            # Auto-playing media requires controls
            if not config.has_pause_control:
                has_required_controls = False
                violations.append(
                    SeizureViolation(
                        criterion=SeizureCriterion.SC_2_3_1,
                        severity=ViolationSeverity.MAJOR,
                        description="Auto-playing media lacks pause control",
                        location=location,
                        remediation="Add pause control for auto-playing media",
                    )
                )
                recommendations.append("Add pause control")

            if not config.has_stop_control:
                has_required_controls = False
                violations.append(
                    SeizureViolation(
                        criterion=SeizureCriterion.SC_2_3_1,
                        severity=ViolationSeverity.MAJOR,
                        description="Auto-playing media lacks stop control",
                        location=location,
                        remediation="Add stop control for auto-playing media",
                    )
                )
                recommendations.append("Add stop control")

            # Long auto-playing media warning
            if config.duration_seconds > MAX_AUTO_PLAY_DURATION_SECONDS:
                violations.append(
                    SeizureViolation(
                        criterion=SeizureCriterion.SC_2_3_1,
                        severity=ViolationSeverity.MINOR,
                        description=(
                            f"Auto-playing media duration {config.duration_seconds:.1f}s "
                            f"exceeds recommended {MAX_AUTO_PLAY_DURATION_SECONDS:.1f}s"
                        ),
                        location=location,
                        remediation="Limit auto-play duration or require user interaction",
                        measured_value=config.duration_seconds,
                        threshold_value=MAX_AUTO_PLAY_DURATION_SECONDS,
                    )
                )
                recommendations.append("Reduce auto-play duration")

        # Check reduced motion support
        respects_user_preferences = config.respects_reduced_motion

        if not respects_user_preferences:
            violations.append(
                SeizureViolation(
                    criterion=SeizureCriterion.SC_2_3_3,
                    severity=ViolationSeverity.MAJOR,
                    description="Media does not respect prefers-reduced-motion",
                    location=location,
                    remediation="Implement prefers-reduced-motion media query support",
                )
            )
            recommendations.append("Add prefers-reduced-motion support")

        # Calculate score
        score = self._calculate_score(violations)

        # Determine if passes
        critical_count = sum(
            1 for v in violations if v.severity == ViolationSeverity.CRITICAL
        )
        passes = score >= 0.70 and critical_count == 0

        # Generate summary
        summary = self._generate_animation_summary(
            config.media_id, passes, score, len(violations), critical_count
        )

        return AnimationSafetyResult(
            animation_id=config.media_id,
            passes=passes,
            score=score,
            violations=violations,
            flash_analysis=flash_analysis,
            has_required_controls=has_required_controls,
            respects_user_preferences=respects_user_preferences,
            recommendations=recommendations,
            summary=summary,
        )

    # ============================================
    # Content Validation
    # ============================================

    def check_content(
        self,
        content: ContentConfig | dict[str, Any],
        target_level: ComplianceLevel = ComplianceLevel.LEVEL_AA,
    ) -> SeizureSafetyResult:
        """Validate content for seizure safety.

        Args:
            content: Content configuration (dict or ContentConfig)
            target_level: Target compliance level

        Returns:
            SeizureSafetyResult with complete safety assessment
        """
        # Convert dict to ContentConfig if needed
        if isinstance(content, dict):
            animations = [
                AnimationConfig(**a) if isinstance(a, dict) else a
                for a in content.get("animations", [])
            ]
            media = [
                MediaConfig(**m) if isinstance(m, dict) else m
                for m in content.get("media", [])
            ]
            config = ContentConfig(
                content_id=content.get("content_id", ""),
                animations=animations,
                media=media,
                has_auto_updating_content=content.get(
                    "has_auto_updating_content", False
                ),
                update_frequency_hz=content.get("update_frequency_hz", 0.0),
                has_motion_trigger=content.get("has_motion_trigger", False),
                respects_reduced_motion=content.get("respects_reduced_motion", True),
            )
        else:
            config = content

        all_violations: list[SeizureViolation] = []
        recommendations: list[str] = []
        animation_results: list[AnimationSafetyResult] = []
        media_results: list[AnimationSafetyResult] = []

        # Analyze all animations
        for anim in config.animations:
            result = self.analyze_animation(anim, target_level)
            animation_results.append(result)
            all_violations.extend(result.violations)
            recommendations.extend(result.recommendations)

        # Analyze all media
        for med in config.media:
            result = self.analyze_media(med, target_level)
            media_results.append(result)
            all_violations.extend(result.violations)
            recommendations.extend(result.recommendations)

        # Check auto-updating content
        if config.has_auto_updating_content:
            if config.update_frequency_hz > self.max_flash_frequency:
                all_violations.append(
                    SeizureViolation(
                        criterion=SeizureCriterion.SC_2_3_1,
                        severity=ViolationSeverity.MAJOR,
                        description=(
                            f"Auto-update frequency {config.update_frequency_hz:.1f}Hz "
                            f"may cause flash-like effects"
                        ),
                        location="content",
                        remediation="Reduce auto-update frequency",
                        measured_value=config.update_frequency_hz,
                        threshold_value=self.max_flash_frequency,
                    )
                )
                recommendations.append("Reduce auto-update frequency")

        # Check global reduced motion support
        respects_reduced_motion = config.respects_reduced_motion
        if not respects_reduced_motion:
            all_violations.append(
                SeizureViolation(
                    criterion=SeizureCriterion.SC_2_3_3,
                    severity=ViolationSeverity.MAJOR,
                    description="Content does not globally respect prefers-reduced-motion",
                    location="content",
                    remediation="Implement global prefers-reduced-motion support",
                )
            )
            recommendations.append("Add global prefers-reduced-motion support")

        # Determine controls status
        has_controls = all(r.has_required_controls for r in animation_results)
        has_controls = has_controls and all(
            r.has_required_controls for r in media_results
        )

        # Determine which criteria are met
        criteria_met, criteria_failed = self._evaluate_criteria(
            all_violations, target_level
        )

        # Calculate overall score
        score = self._calculate_score(all_violations)

        # Determine if passes
        critical_count = sum(
            1 for v in all_violations if v.severity == ViolationSeverity.CRITICAL
        )
        passes = score >= 0.70 and critical_count == 0

        # Generate summary
        summary = self._generate_content_summary(
            config.content_id,
            target_level,
            passes,
            score,
            len(all_violations),
            critical_count,
            criteria_met,
            criteria_failed,
        )

        # Deduplicate recommendations
        unique_recommendations = list(dict.fromkeys(recommendations))

        return SeizureSafetyResult(
            content_id=config.content_id,
            target_level=target_level,
            passes=passes,
            score=score,
            violations=all_violations,
            animation_results=animation_results,
            media_results=media_results,
            has_controls=has_controls,
            respects_reduced_motion=respects_reduced_motion,
            criteria_met=criteria_met,
            criteria_failed=criteria_failed,
            recommendations=unique_recommendations,
            summary=summary,
        )

    # ============================================
    # Helper Methods
    # ============================================

    def _calculate_score(self, violations: list[SeizureViolation]) -> float:
        """Calculate score from violations."""
        if not violations:
            return 1.0

        total_weight = sum(v.weight for v in violations)
        return max(0.0, min(1.0, 1.0 - total_weight))

    def _evaluate_criteria(
        self, violations: list[SeizureViolation], target_level: ComplianceLevel
    ) -> tuple[list[SeizureCriterion], list[SeizureCriterion]]:
        """Evaluate which WCAG 2.3 criteria are met.

        Args:
            violations: List of violations found
            target_level: Target compliance level

        Returns:
            Tuple of (criteria_met, criteria_failed)
        """
        required_criteria = CRITERIA_BY_LEVEL.get(target_level, [])
        failed_criteria_codes = {v.criterion for v in violations}

        criteria_met = [c for c in required_criteria if c not in failed_criteria_codes]
        criteria_failed = [c for c in required_criteria if c in failed_criteria_codes]

        return criteria_met, criteria_failed

    def _generate_animation_summary(
        self,
        animation_id: str,
        passes: bool,
        score: float,
        violation_count: int,
        critical_count: int,
    ) -> str:
        """Generate animation result summary."""
        status = "PASSES" if passes else "FAILS"
        name = animation_id or "Animation"
        return (
            f"{name} {status}. Score: {score:.0%}. "
            f"Violations: {violation_count} ({critical_count} critical)."
        )

    def _generate_content_summary(
        self,
        content_id: str,
        target_level: ComplianceLevel,
        passes: bool,
        score: float,
        violation_count: int,
        critical_count: int,
        criteria_met: list[SeizureCriterion],
        criteria_failed: list[SeizureCriterion],
    ) -> str:
        """Generate content result summary."""
        status = "PASSES" if passes else "FAILS"
        name = content_id or "Content"
        met_count = len(criteria_met)
        failed_count = len(criteria_failed)

        return (
            f"Seizure safety check {status} for {name} at {target_level.value}. "
            f"Score: {score:.0%}. Violations: {violation_count} ({critical_count} critical). "
            f"WCAG 2.3 criteria: {met_count} met, {failed_count} failed."
        )


# ============================================
# Convenience Functions
# ============================================


def check_flash_safety(
    frequency_hz: float,
    area_percent: float = 100.0,
    is_red: bool = False,
) -> bool:
    """Quick check if a flash is safe.

    Args:
        frequency_hz: Flash frequency in Hz
        area_percent: Flash area as percentage of FOV
        is_red: Whether flash contains saturated red

    Returns:
        True if flash is safe, False otherwise
    """
    checker = SeizureSafetyChecker()
    analysis = checker.analyze_flash(frequency_hz, area_percent, is_red)
    return analysis.is_safe


def check_animation_safety(animation: dict[str, Any]) -> bool:
    """Quick check if an animation is safe.

    Args:
        animation: Animation configuration dict

    Returns:
        True if animation is safe, False otherwise
    """
    checker = SeizureSafetyChecker()
    result = checker.analyze_animation(animation)
    return result.passes
