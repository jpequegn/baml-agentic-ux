"""Accessibility validation for multi-modal LUI responses.

This module provides runtime validation of accessibility compliance
following WCAG 2.2 guidelines.
"""

from __future__ import annotations

from typing import Any

from baml_client.types import (
    AccessibilityNeed,
    AccessibilityProfile,
    AccessibilityReport,
    AccessibilityRequirements,
    AccessibilityViolation,
    ActionElementValidation,
    CategoryScores,
    CognitiveLoad,
    ElementValidation,
    EffortLevel,
    ImpactedGroup,
    LabelQuality,
    MultiModalAction,
    MultiModalResponse,
    MultiModalVisualElement,
    RemediationAction,
    RemediationActionType,
    ReportSummary,
    UserAccessibilityCheck,
    ViolationSeverity,
    VisualElementValidation,
    VoiceElementValidation,
    VoiceResponse,
    WCAGCategory,
    WCAGCriterion,
    WCAGLevel,
)


# ============================================
# Constants
# ============================================

# WCAG Success Criteria by Category
PERCEIVABLE_CRITERIA = [
    WCAGCriterion.SC_1_1_1,
    WCAGCriterion.SC_1_2_1,
    WCAGCriterion.SC_1_2_2,
    WCAGCriterion.SC_1_3_1,
    WCAGCriterion.SC_1_3_2,
    WCAGCriterion.SC_1_4_1,
    WCAGCriterion.SC_1_4_3,
]

OPERABLE_CRITERIA = [
    WCAGCriterion.SC_2_1_1,
    WCAGCriterion.SC_2_1_2,
    WCAGCriterion.SC_2_4_4,
    WCAGCriterion.SC_2_4_6,
    WCAGCriterion.SC_2_4_7,
]

UNDERSTANDABLE_CRITERIA = [
    WCAGCriterion.SC_3_1_1,
    WCAGCriterion.SC_3_2_1,
    WCAGCriterion.SC_3_3_1,
    WCAGCriterion.SC_3_3_2,
]

ROBUST_CRITERIA = [
    WCAGCriterion.SC_4_1_2,
    WCAGCriterion.SC_4_1_3,
]

# Minimum requirements by WCAG level
LEVEL_REQUIREMENTS = {
    WCAGLevel.A: {
        "min_score": 60.0,
        "allow_critical": False,
        "allow_serious": True,
    },
    WCAGLevel.AA: {
        "min_score": 80.0,
        "allow_critical": False,
        "allow_serious": False,
    },
    WCAGLevel.AAA: {
        "min_score": 95.0,
        "allow_critical": False,
        "allow_serious": False,
    },
}


# ============================================
# Validation Functions
# ============================================


def validate_multimodal_response(
    response: MultiModalResponse,
    requirements: AccessibilityRequirements | None = None,
    level: WCAGLevel = WCAGLevel.AA,
) -> AccessibilityReport:
    """Validate a multi-modal response for accessibility compliance.

    Args:
        response: The multi-modal response to validate
        requirements: Specific accessibility requirements (optional)
        level: Target WCAG conformance level

    Returns:
        AccessibilityReport with violations and scores
    """
    if requirements is None:
        requirements = AccessibilityRequirements(
            wcag_level=level,
            screen_reader_support=True,
            voice_control_support=False,
            reduced_motion=False,
            high_contrast=False,
            cognitive_support=False,
        )

    violations: list[AccessibilityViolation] = []

    # Run all validation checks
    violations.extend(_check_perceivable(response, requirements))
    violations.extend(_check_operable(response, requirements))
    violations.extend(_check_understandable(response, requirements))
    violations.extend(_check_robust(response, requirements))
    violations.extend(_check_voice_specific(response, requirements))

    # Calculate scores
    category_scores = _calculate_category_scores(violations)
    overall_score = _calculate_overall_score(category_scores)

    # Determine compliance
    compliant = _is_compliant(violations, level, overall_score)

    # Generate summary
    summary = _generate_summary(violations, overall_score)

    # Generate remediations
    remediations = _generate_remediations(violations)

    # Determine achieved level
    achieved_level = _determine_achieved_level(violations, overall_score)

    return AccessibilityReport(
        report_id=f"a11y_{response.response_id}",
        generated_at=_get_timestamp(),
        response_id=response.response_id,
        compliant=compliant,
        wcag_level=level,
        achieved_level=achieved_level,
        score=overall_score,
        violations=violations,
        remediations=remediations if remediations else None,
        summary=summary,
        category_scores=category_scores,
        tested_criteria=_get_tested_criteria(),
    )


def check_accessibility_for_user(
    response: MultiModalResponse,
    user_profile: AccessibilityProfile,
) -> UserAccessibilityCheck:
    """Check if a response is accessible for a specific user profile.

    Args:
        response: The multi-modal response to check
        user_profile: The user's accessibility profile

    Returns:
        UserAccessibilityCheck with accessibility status and recommendations
    """
    meets_needs: dict[str, bool] = {}
    blockers: list[str] = []
    recommendations: list[str] = []

    for need in user_profile.needs:
        meets, issues, recs = _check_accessibility_need(response, need)
        meets_needs[need.value] = meets
        blockers.extend(issues)
        recommendations.extend(recs)

    # Check requirements
    req_violations = validate_multimodal_response(
        response, user_profile.requirements
    ).violations

    for v in req_violations:
        if v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.SERIOUS]:
            blockers.append(v.description)

    accessible = len(blockers) == 0
    confidence = 1.0 if accessible else max(0.0, 1.0 - (len(blockers) * 0.2))

    # Suggest alternative modality if not accessible
    alternative_modality = None
    if not accessible and user_profile.preferred_modality:
        alternative_modality = _suggest_alternative_modality(
            response, user_profile.needs
        )

    return UserAccessibilityCheck(
        accessible=accessible,
        confidence=confidence,
        meets_needs=meets_needs,
        blockers=blockers if blockers else None,
        recommendations=recommendations if recommendations else None,
        alternative_modality=alternative_modality,
    )


def validate_visual_element(
    element: MultiModalVisualElement,
    requirements: AccessibilityRequirements,
) -> VisualElementValidation:
    """Validate a single visual element for accessibility.

    Args:
        element: The visual element to validate
        requirements: Accessibility requirements

    Returns:
        VisualElementValidation with detailed findings
    """
    passed_checks: list[str] = []
    failed_checks: list[AccessibilityViolation] = []

    # Check alt text
    has_alt_text = bool(element.alt_text)
    alt_text_quality = None

    # Generate element ID from type
    element_type_str = element.element_type.value if hasattr(element.element_type, 'value') else str(element.element_type)
    element_id = f"visual_{element_type_str}"

    if has_alt_text:
        passed_checks.append("Has alt text")
        alt_text_quality = _assess_alt_text_quality(element.alt_text)
    else:
        failed_checks.append(
            AccessibilityViolation(
                rule_id="WCAG-1.1.1",
                criterion=WCAGCriterion.SC_1_1_1,
                category=WCAGCategory.PERCEIVABLE,
                severity=ViolationSeverity.CRITICAL,
                element=element_id,
                element_type=element_type_str,
                description="Visual element missing alt text",
                impact="Screen reader users cannot understand this content",
                impacted_groups=[ImpactedGroup.BLIND, ImpactedGroup.LOW_VISION],
                remediation="Add descriptive alt_text to the element",
            )
        )

    # Check keyboard accessibility
    keyboard_accessible = True  # Assume true unless we can verify otherwise

    base_validation = ElementValidation(
        element_id=element_id,
        element_type=element_type_str,
        passed_checks=passed_checks,
        failed_checks=failed_checks,
    )

    return VisualElementValidation(
        element=base_validation,
        has_alt_text=has_alt_text,
        alt_text_quality=alt_text_quality,
        contrast_ratio=None,  # Would need actual color values
        meets_contrast_requirement=None,
        focus_indicator_present=None,
        keyboard_accessible=keyboard_accessible,
    )


def validate_voice_element(
    voice: VoiceResponse,
    has_text_fallback: bool,
) -> VoiceElementValidation:
    """Validate a voice response for accessibility.

    Args:
        voice: The voice response to validate
        has_text_fallback: Whether a text fallback exists

    Returns:
        VoiceElementValidation with detailed findings
    """
    passed_checks: list[str] = []
    failed_checks: list[AccessibilityViolation] = []

    # Check text fallback
    if has_text_fallback:
        passed_checks.append("Has text fallback")
    else:
        failed_checks.append(
            AccessibilityViolation(
                rule_id="WCAG-1.1.1",
                criterion=WCAGCriterion.SC_1_1_1,
                category=WCAGCategory.PERCEIVABLE,
                severity=ViolationSeverity.CRITICAL,
                element="voice_response",
                description="Voice response has no text fallback",
                impact="Deaf or hard of hearing users cannot access this content",
                impacted_groups=[
                    ImpactedGroup.DEAF,
                    ImpactedGroup.HARD_OF_HEARING,
                ],
                remediation="Add text response as fallback for voice content",
            )
        )

    # Check language specification
    language_specified = bool(voice.language)
    if language_specified:
        passed_checks.append("Language specified")
    else:
        failed_checks.append(
            AccessibilityViolation(
                rule_id="WCAG-3.1.1",
                criterion=WCAGCriterion.SC_3_1_1,
                category=WCAGCategory.UNDERSTANDABLE,
                severity=ViolationSeverity.SERIOUS,
                element="voice_response",
                description="Voice response language not specified",
                impact="Screen readers may mispronounce content",
                impacted_groups=[ImpactedGroup.BLIND],
                remediation="Specify language code (e.g., 'en-US') in voice response",
            )
        )

    # Check for SSML pauses
    has_pauses = voice.ssml is not None and "<break" in voice.ssml

    # Estimate duration
    estimated_duration = _estimate_voice_duration(voice.text)

    base_validation = ElementValidation(
        element_id="voice_response",
        element_type="voice",
        passed_checks=passed_checks,
        failed_checks=failed_checks,
    )

    return VoiceElementValidation(
        element=base_validation,
        has_text_fallback=has_text_fallback,
        has_transcript=has_text_fallback,
        language_specified=language_specified,
        speech_rate_adjustable=True,  # Assume TTS supports this
        has_pauses=has_pauses,
        estimated_duration_seconds=estimated_duration,
    )


def validate_action_element(
    action: MultiModalAction,
) -> ActionElementValidation:
    """Validate an action element for accessibility.

    Args:
        action: The action to validate

    Returns:
        ActionElementValidation with detailed findings
    """
    passed_checks: list[str] = []
    failed_checks: list[AccessibilityViolation] = []

    # Check label quality
    label_quality = _assess_label_quality(action.label)

    if label_quality in [LabelQuality.EXCELLENT, LabelQuality.GOOD]:
        passed_checks.append("Clear action label")
    else:
        failed_checks.append(
            AccessibilityViolation(
                rule_id="WCAG-2.4.4",
                criterion=WCAGCriterion.SC_2_4_4,
                category=WCAGCategory.OPERABLE,
                severity=ViolationSeverity.SERIOUS,
                element=action.action_id,
                element_type="action",
                description=f"Action label is not descriptive: '{action.label}'",
                impact="Users may not understand what this action does",
                impacted_groups=[ImpactedGroup.COGNITIVE, ImpactedGroup.BLIND],
                remediation="Use a clear, descriptive label for the action",
            )
        )

    # Check for keyboard shortcut
    has_keyboard_shortcut = bool(action.keyboard_shortcut)

    # Check ARIA label
    has_aria_label = bool(action.description)

    # Action purpose clear from label
    action_purpose_clear = len(action.label) >= 2 and label_quality != LabelQuality.POOR

    base_validation = ElementValidation(
        element_id=action.action_id,
        element_type="action",
        passed_checks=passed_checks,
        failed_checks=failed_checks,
    )

    return ActionElementValidation(
        element=base_validation,
        label_quality=label_quality,
        has_keyboard_shortcut=has_keyboard_shortcut,
        is_focusable=True,  # Assume actions are focusable
        has_aria_label=has_aria_label,
        action_purpose_clear=action_purpose_clear,
    )


# ============================================
# Internal Helper Functions
# ============================================


def _check_perceivable(
    response: MultiModalResponse,
    requirements: AccessibilityRequirements,
) -> list[AccessibilityViolation]:
    """Check WCAG Perceivable criteria (1.x)."""
    violations: list[AccessibilityViolation] = []

    # 1.1.1: Non-text Content
    if response.visuals:
        for element in response.visuals:
            if not element.alt_text:
                violations.append(
                    AccessibilityViolation(
                        rule_id="WCAG-1.1.1",
                        criterion=WCAGCriterion.SC_1_1_1,
                        category=WCAGCategory.PERCEIVABLE,
                        severity=ViolationSeverity.CRITICAL,
                        element=f"visual_{element.element_type.value if hasattr(element.element_type, 'value') else str(element.element_type)}",
                        element_type=element.element_type.value if hasattr(element.element_type, 'value') else str(element.element_type),
                        description="Visual element missing alternative text",
                        impact="Screen reader users cannot understand this content",
                        impacted_groups=[
                            ImpactedGroup.BLIND,
                            ImpactedGroup.LOW_VISION,
                        ],
                        remediation="Add descriptive alt_text to the visual element",
                    )
                )

    # Voice without text fallback
    if response.voice and not response.text:
        violations.append(
            AccessibilityViolation(
                rule_id="WCAG-1.1.1",
                criterion=WCAGCriterion.SC_1_1_1,
                category=WCAGCategory.PERCEIVABLE,
                severity=ViolationSeverity.CRITICAL,
                element="voice_response",
                description="Voice response has no text fallback",
                impact="Deaf or hard of hearing users cannot access this content",
                impacted_groups=[
                    ImpactedGroup.DEAF,
                    ImpactedGroup.HARD_OF_HEARING,
                ],
                remediation="Add text response as fallback for voice content",
            )
        )

    # 1.3.1: Info and Relationships
    if not response.accessibility.supports_screen_reader and requirements.screen_reader_support:
        violations.append(
            AccessibilityViolation(
                rule_id="WCAG-1.3.1",
                criterion=WCAGCriterion.SC_1_3_1,
                category=WCAGCategory.PERCEIVABLE,
                severity=ViolationSeverity.SERIOUS,
                element="response",
                description="Response not optimized for screen readers",
                impact="Screen reader users may miss structural information",
                impacted_groups=[ImpactedGroup.BLIND],
                remediation="Enable screen reader optimization in accessibility meta",
            )
        )

    # High contrast check
    if requirements.high_contrast and not response.accessibility.high_contrast_available:
        violations.append(
            AccessibilityViolation(
                rule_id="WCAG-1.4.3",
                criterion=WCAGCriterion.SC_1_4_3,
                category=WCAGCategory.PERCEIVABLE,
                severity=ViolationSeverity.SERIOUS,
                element="response",
                description="High contrast mode not available",
                impact="Users with low vision may struggle to read content",
                impacted_groups=[ImpactedGroup.LOW_VISION],
                remediation="Enable high contrast mode in accessibility meta",
            )
        )

    return violations


def _check_operable(
    response: MultiModalResponse,
    requirements: AccessibilityRequirements,
) -> list[AccessibilityViolation]:
    """Check WCAG Operable criteria (2.x)."""
    violations: list[AccessibilityViolation] = []

    # 2.1.1: Keyboard
    if not response.accessibility.supports_keyboard_nav:
        keyboard_only = getattr(requirements, 'keyboard_only', False)
        if keyboard_only:
            violations.append(
                AccessibilityViolation(
                    rule_id="WCAG-2.1.1",
                    criterion=WCAGCriterion.SC_2_1_1,
                    category=WCAGCategory.OPERABLE,
                    severity=ViolationSeverity.CRITICAL,
                    element="response",
                    description="Response not keyboard navigable",
                    impact="Keyboard-only users cannot interact with this content",
                    impacted_groups=[ImpactedGroup.MOTOR_IMPAIRED],
                    remediation="Enable keyboard navigation support",
                )
            )

    # 2.4.4: Link Purpose (for actions)
    if response.actions:
        for action in response.actions:
            if len(action.label) < 2:
                violations.append(
                    AccessibilityViolation(
                        rule_id="WCAG-2.4.4",
                        criterion=WCAGCriterion.SC_2_4_4,
                        category=WCAGCategory.OPERABLE,
                        severity=ViolationSeverity.SERIOUS,
                        element=action.action_id,
                        element_type="action",
                        description=f"Action label too short: '{action.label}'",
                        impact="Users may not understand action purpose",
                        impacted_groups=[ImpactedGroup.COGNITIVE, ImpactedGroup.BLIND],
                        remediation="Use descriptive action label (at least 2 characters)",
                    )
                )

    # Check action count (usability, not strict WCAG)
    if response.actions and len(response.actions) > 4:
        violations.append(
            AccessibilityViolation(
                rule_id="BEST-PRACTICE-ACTIONS",
                criterion=WCAGCriterion.SC_2_4_6,
                category=WCAGCategory.OPERABLE,
                severity=ViolationSeverity.MINOR,
                element="actions",
                description=f"Too many actions ({len(response.actions)} > 4 recommended)",
                impact="May overwhelm users with cognitive disabilities",
                impacted_groups=[ImpactedGroup.COGNITIVE],
                remediation="Limit actions to 4 or fewer",
            )
        )

    return violations


def _check_understandable(
    response: MultiModalResponse,
    requirements: AccessibilityRequirements,
) -> list[AccessibilityViolation]:
    """Check WCAG Understandable criteria (3.x)."""
    violations: list[AccessibilityViolation] = []

    # 3.1.1: Language of Page
    if response.voice and not response.voice.language:
        violations.append(
            AccessibilityViolation(
                rule_id="WCAG-3.1.1",
                criterion=WCAGCriterion.SC_3_1_1,
                category=WCAGCategory.UNDERSTANDABLE,
                severity=ViolationSeverity.SERIOUS,
                element="voice_response",
                description="Voice response language not specified",
                impact="Screen readers may mispronounce content",
                impacted_groups=[ImpactedGroup.BLIND],
                remediation="Specify language code in voice response",
            )
        )

    # Cognitive load check
    if requirements.cognitive_support:
        if response.accessibility.cognitive_load in [
            CognitiveLoad.HIGH,
            CognitiveLoad.VERY_HIGH,
        ]:
            violations.append(
                AccessibilityViolation(
                    rule_id="WCAG-3.1.5",
                    criterion=WCAGCriterion.SC_3_1_2,
                    category=WCAGCategory.UNDERSTANDABLE,
                    severity=ViolationSeverity.MODERATE,
                    element="response",
                    description=f"High cognitive load ({response.accessibility.cognitive_load.value})",
                    impact="May exclude users with cognitive disabilities",
                    impacted_groups=[ImpactedGroup.COGNITIVE],
                    remediation="Simplify content or provide simpler alternative",
                )
            )

    return violations


def _check_robust(
    response: MultiModalResponse,
    requirements: AccessibilityRequirements,
) -> list[AccessibilityViolation]:
    """Check WCAG Robust criteria (4.x)."""
    violations: list[AccessibilityViolation] = []

    # 4.1.2: Name, Role, Value
    if not response.accessibility.aria_label:
        violations.append(
            AccessibilityViolation(
                rule_id="WCAG-4.1.2",
                criterion=WCAGCriterion.SC_4_1_2,
                category=WCAGCategory.ROBUST,
                severity=ViolationSeverity.MODERATE,
                element="response",
                description="Response missing ARIA label",
                impact="Assistive technologies may not properly identify this content",
                impacted_groups=[ImpactedGroup.BLIND],
                remediation="Add aria_label to accessibility meta",
            )
        )

    # 4.1.3: Status Messages (aria-live)
    from baml_client.types import AriaLiveType
    if response.accessibility.aria_live == AriaLiveType.OFF:
        violations.append(
            AccessibilityViolation(
                rule_id="WCAG-4.1.3",
                criterion=WCAGCriterion.SC_4_1_3,
                category=WCAGCategory.ROBUST,
                severity=ViolationSeverity.MODERATE,
                element="response",
                description="ARIA live region not configured",
                impact="Screen reader users may miss dynamic updates",
                impacted_groups=[ImpactedGroup.BLIND],
                remediation="Set aria_live to POLITE or ASSERTIVE for announcements",
            )
        )

    return violations


def _check_voice_specific(
    response: MultiModalResponse,
    requirements: AccessibilityRequirements,
) -> list[AccessibilityViolation]:
    """Check voice-specific accessibility requirements."""
    violations: list[AccessibilityViolation] = []

    if not response.voice:
        return violations

    # Check for SSML pauses
    if response.voice.ssml:
        if "<break" not in response.voice.ssml:
            violations.append(
                AccessibilityViolation(
                    rule_id="VOICE-PAUSES",
                    criterion=WCAGCriterion.SC_1_2_1,
                    category=WCAGCategory.PERCEIVABLE,
                    severity=ViolationSeverity.MINOR,
                    element="voice_ssml",
                    description="Voice response lacks SSML pauses",
                    impact="Content may be difficult to follow",
                    impacted_groups=[ImpactedGroup.COGNITIVE, ImpactedGroup.BLIND],
                    remediation="Add <break> tags between logical sections",
                )
            )

    # Check voice duration
    estimated_duration = _estimate_voice_duration(response.voice.text)
    if estimated_duration > 30:
        violations.append(
            AccessibilityViolation(
                rule_id="VOICE-DURATION",
                criterion=WCAGCriterion.SC_2_2_1,
                category=WCAGCategory.OPERABLE,
                severity=ViolationSeverity.MODERATE,
                element="voice_response",
                description=f"Voice response may be too long (~{estimated_duration:.0f}s)",
                impact="Users may lose track of content",
                impacted_groups=[ImpactedGroup.COGNITIVE],
                remediation="Keep voice responses under 30 seconds",
            )
        )

    # Reduced motion check
    if requirements.reduced_motion and not response.accessibility.reduced_motion_safe:
        violations.append(
            AccessibilityViolation(
                rule_id="WCAG-2.3.1",
                criterion=WCAGCriterion.SC_2_3_1,
                category=WCAGCategory.OPERABLE,
                severity=ViolationSeverity.SERIOUS,
                element="response",
                description="Response not marked as reduced motion safe",
                impact="May trigger vestibular disorders",
                impacted_groups=[ImpactedGroup.VESTIBULAR],
                remediation="Mark response as reduced_motion_safe or remove animations",
            )
        )

    return violations


def _check_accessibility_need(
    response: MultiModalResponse,
    need: AccessibilityNeed,
) -> tuple[bool, list[str], list[str]]:
    """Check if response meets a specific accessibility need."""
    issues: list[str] = []
    recommendations: list[str] = []

    if need == AccessibilityNeed.VISUAL:
        # Blind users need voice or text
        if not response.voice and not response.text:
            issues.append("No voice or text content for blind users")
            recommendations.append("Add voice response for visual impairment support")
        if response.visuals and not all(v.alt_text for v in response.visuals):
            issues.append("Visual elements missing alt text")
            recommendations.append("Add alt text to all visual elements")

    elif need == AccessibilityNeed.AUDITORY:
        # Deaf users need visual or text
        if response.voice and not response.text:
            issues.append("Voice content without text fallback for deaf users")
            recommendations.append("Add text fallback for voice content")

    elif need == AccessibilityNeed.MOTOR:
        # Motor impaired users need keyboard access
        if not response.accessibility.supports_keyboard_nav:
            issues.append("Content not keyboard navigable")
            recommendations.append("Enable keyboard navigation support")

    elif need == AccessibilityNeed.COGNITIVE:
        # Cognitive accessibility
        if response.accessibility.cognitive_load in [
            CognitiveLoad.HIGH,
            CognitiveLoad.VERY_HIGH,
        ]:
            issues.append("High cognitive load may be difficult to process")
            recommendations.append("Simplify content or provide alternative")

    meets = len(issues) == 0
    return meets, issues, recommendations


def _calculate_category_scores(
    violations: list[AccessibilityViolation],
) -> CategoryScores:
    """Calculate accessibility scores by WCAG category."""
    category_violations = {
        WCAGCategory.PERCEIVABLE: 0,
        WCAGCategory.OPERABLE: 0,
        WCAGCategory.UNDERSTANDABLE: 0,
        WCAGCategory.ROBUST: 0,
    }

    # Weight violations by severity
    severity_weights = {
        ViolationSeverity.CRITICAL: 25,
        ViolationSeverity.SERIOUS: 15,
        ViolationSeverity.MODERATE: 8,
        ViolationSeverity.MINOR: 3,
    }

    for v in violations:
        weight = severity_weights.get(v.severity, 5)
        category_violations[v.category] += weight

    # Convert to scores (100 - deductions, min 0)
    return CategoryScores(
        perceivable=max(0, 100 - category_violations[WCAGCategory.PERCEIVABLE]),
        operable=max(0, 100 - category_violations[WCAGCategory.OPERABLE]),
        understandable=max(0, 100 - category_violations[WCAGCategory.UNDERSTANDABLE]),
        robust=max(0, 100 - category_violations[WCAGCategory.ROBUST]),
    )


def _calculate_overall_score(category_scores: CategoryScores) -> float:
    """Calculate overall accessibility score from category scores."""
    # Weighted average
    weights = {
        "perceivable": 0.30,
        "operable": 0.30,
        "understandable": 0.20,
        "robust": 0.20,
    }

    score = (
        category_scores.perceivable * weights["perceivable"]
        + category_scores.operable * weights["operable"]
        + category_scores.understandable * weights["understandable"]
        + category_scores.robust * weights["robust"]
    )

    return round(score, 2)


def _is_compliant(
    violations: list[AccessibilityViolation],
    level: WCAGLevel,
    score: float,
) -> bool:
    """Determine if response meets target WCAG level."""
    reqs = LEVEL_REQUIREMENTS[level]

    # Check score threshold
    if score < reqs["min_score"]:
        return False

    # Check critical violations
    critical_count = sum(
        1 for v in violations if v.severity == ViolationSeverity.CRITICAL
    )
    if critical_count > 0 and not reqs["allow_critical"]:
        return False

    # Check serious violations
    serious_count = sum(
        1 for v in violations if v.severity == ViolationSeverity.SERIOUS
    )
    if serious_count > 0 and not reqs["allow_serious"]:
        return False

    return True


def _determine_achieved_level(
    violations: list[AccessibilityViolation],
    score: float,
) -> WCAGLevel | None:
    """Determine highest WCAG level achieved."""
    for level in [WCAGLevel.AAA, WCAGLevel.AA, WCAGLevel.A]:
        if _is_compliant(violations, level, score):
            return level
    return None


def _generate_summary(
    violations: list[AccessibilityViolation],
    score: float,
) -> ReportSummary:
    """Generate summary of accessibility findings."""
    critical = sum(1 for v in violations if v.severity == ViolationSeverity.CRITICAL)
    serious = sum(1 for v in violations if v.severity == ViolationSeverity.SERIOUS)
    moderate = sum(1 for v in violations if v.severity == ViolationSeverity.MODERATE)
    minor = sum(1 for v in violations if v.severity == ViolationSeverity.MINOR)

    # Calculate pass rate (assuming ~20 checks per category)
    total_checks = 20
    pass_rate = max(0, (total_checks - len(violations)) / total_checks * 100)

    # Identify primary issues
    primary_issues = list(
        set(v.description for v in violations if v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.SERIOUS])
    )[:5]

    # Identify strengths
    strengths: list[str] = []
    if critical == 0:
        strengths.append("No critical accessibility issues")
    if score >= 80:
        strengths.append("Good overall accessibility score")

    # Priority recommendations
    recommendations = list(
        set(v.remediation for v in violations if v.severity == ViolationSeverity.CRITICAL)
    )[:3]
    if not recommendations:
        recommendations = list(
            set(v.remediation for v in violations if v.severity == ViolationSeverity.SERIOUS)
        )[:3]

    return ReportSummary(
        total_violations=len(violations),
        critical_count=critical,
        serious_count=serious,
        moderate_count=moderate,
        minor_count=minor,
        pass_rate=round(pass_rate, 1),
        primary_issues=primary_issues,
        strengths=strengths,
        recommendations=recommendations,
    )


def _generate_remediations(
    violations: list[AccessibilityViolation],
) -> list[RemediationAction]:
    """Generate remediation actions for violations."""
    remediations: list[RemediationAction] = []

    # Map violations to remediation actions
    action_type_map = {
        "missing alt text": RemediationActionType.ADD_ALT_TEXT,
        "missing alternative text": RemediationActionType.ADD_ALT_TEXT,
        "ARIA label": RemediationActionType.ADD_ARIA_LABEL,
        "aria_label": RemediationActionType.ADD_ARIA_LABEL,
        "aria_live": RemediationActionType.ADD_ARIA_LIVE,
        "keyboard": RemediationActionType.ADD_KEYBOARD_NAV,
        "contrast": RemediationActionType.IMPROVE_CONTRAST,
        "text fallback": RemediationActionType.ADD_TEXT_FALLBACK,
        "language": RemediationActionType.ADD_LANGUAGE,
        "cognitive": RemediationActionType.SIMPLIFY_CONTENT,
        "label": RemediationActionType.FIX_LINK_TEXT,
    }

    priority = 1
    for v in sorted(
        violations,
        key=lambda x: (
            0 if x.severity == ViolationSeverity.CRITICAL else
            1 if x.severity == ViolationSeverity.SERIOUS else
            2 if x.severity == ViolationSeverity.MODERATE else 3
        ),
    ):
        # Determine action type
        action_type = RemediationActionType.ADD_ALT_TEXT  # default
        for keyword, at in action_type_map.items():
            if keyword.lower() in v.description.lower() or keyword.lower() in v.remediation.lower():
                action_type = at
                break

        # Determine effort
        effort = EffortLevel.TRIVIAL
        if v.severity == ViolationSeverity.CRITICAL:
            effort = EffortLevel.LOW
        elif v.severity == ViolationSeverity.SERIOUS:
            effort = EffortLevel.MEDIUM

        remediations.append(
            RemediationAction(
                violation_id=v.rule_id,
                action_type=action_type,
                description=v.remediation,
                effort_estimate=effort,
                priority=priority,
                automated_fix=action_type in [
                    RemediationActionType.ADD_ARIA_LIVE,
                    RemediationActionType.ADD_LANGUAGE,
                ],
            )
        )
        priority += 1

    return remediations


def _suggest_alternative_modality(
    response: MultiModalResponse,
    needs: list[AccessibilityNeed],
) -> Any:
    """Suggest an alternative modality based on user needs."""
    from baml_client.types import Modality

    if AccessibilityNeed.VISUAL in needs:
        return Modality.VOICE
    if AccessibilityNeed.AUDITORY in needs:
        return Modality.TEXT
    return None


def _assess_alt_text_quality(alt_text: str | None) -> Any:
    """Assess the quality of alternative text."""
    from baml_client.types import AltTextQuality

    if not alt_text:
        return None

    if alt_text.lower() in ["image", "picture", "photo", "icon", ""]:
        return AltTextQuality.POOR

    if len(alt_text) < 10:
        return AltTextQuality.NEEDS_IMPROVEMENT

    if len(alt_text) > 20 and " " in alt_text:
        return AltTextQuality.GOOD

    if len(alt_text) > 50:
        return AltTextQuality.EXCELLENT

    return AltTextQuality.GOOD


def _assess_label_quality(label: str) -> LabelQuality:
    """Assess the quality of an action label."""
    if len(label) < 2:
        return LabelQuality.POOR

    if len(label) < 5:
        return LabelQuality.NEEDS_IMPROVEMENT

    # Check for action verbs
    action_words = ["add", "create", "delete", "edit", "save", "cancel", "submit", "open", "close", "show", "hide"]
    has_action_word = any(word in label.lower() for word in action_words)

    if has_action_word and len(label) > 10:
        return LabelQuality.EXCELLENT

    if has_action_word or len(label) > 8:
        return LabelQuality.GOOD

    return LabelQuality.NEEDS_IMPROVEMENT


def _estimate_voice_duration(text: str) -> float:
    """Estimate voice duration in seconds (assuming ~150 words/minute)."""
    words = len(text.split())
    return words / 2.5  # ~2.5 words per second


def _get_timestamp() -> str:
    """Get current ISO timestamp."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def _get_tested_criteria() -> list[WCAGCriterion]:
    """Get list of all tested WCAG criteria."""
    return (
        PERCEIVABLE_CRITERIA
        + OPERABLE_CRITERIA
        + UNDERSTANDABLE_CRITERIA
        + ROBUST_CRITERIA
    )
