"""Tests for accessibility validation types and functions."""

from __future__ import annotations

from baml_client.types import (
    # WCAG Types
    WCAGLevel,
    WCAGCategory,
    WCAGCriterion,
    ViolationSeverity,
    ImpactedGroup,
    RemediationActionType,
    AltTextQuality,
    LabelQuality,
    # Requirements and Profile
    AccessibilityRequirements,
    AccessibilityProfile,
    AccessibilityNeed,
    # Violations
    AccessibilityViolation,
    RemediationAction,
    # Reports
    AccessibilityReport,
    ReportSummary,
    CategoryScores,
    # Element Validation
    ElementValidation,
    VisualElementValidation,
    VoiceElementValidation,
    ActionElementValidation,
    # User Check
    UserAccessibilityCheck,
    # Remediation
    RemediationPlan,
    # Multi-modal Types for integration
    MultiModalResponse,
    MultiModalVisualElement,
    MultiModalVisualType,
    MultiModalAction,
    InteractionType,
    VoiceResponse,
    TextResponse,
    TextFormat,
    AccessibilityMeta,
    AriaLiveType,
    CognitiveLoad,
    Modality,
    EffortLevel,
)

from src.lui_simulator.accessibility import (
    validate_multimodal_response,
    check_accessibility_for_user,
    validate_visual_element,
    validate_voice_element,
    validate_action_element,
    PERCEIVABLE_CRITERIA,
    OPERABLE_CRITERIA,
    UNDERSTANDABLE_CRITERIA,
    ROBUST_CRITERIA,
    LEVEL_REQUIREMENTS,
)


# ============================================
# Enum Tests
# ============================================


class TestWCAGLevelEnum:
    """Tests for WCAGLevel enum."""

    def test_all_levels_exist(self) -> None:
        """Test all WCAG conformance levels are defined."""
        assert WCAGLevel.A.value == "A"
        assert WCAGLevel.AA.value == "AA"
        assert WCAGLevel.AAA.value == "AAA"

    def test_enum_count(self) -> None:
        """Test correct number of levels."""
        assert len(WCAGLevel) == 3


class TestWCAGCategoryEnum:
    """Tests for WCAGCategory enum."""

    def test_all_categories_exist(self) -> None:
        """Test all WCAG categories are defined."""
        assert WCAGCategory.PERCEIVABLE.value == "PERCEIVABLE"
        assert WCAGCategory.OPERABLE.value == "OPERABLE"
        assert WCAGCategory.UNDERSTANDABLE.value == "UNDERSTANDABLE"
        assert WCAGCategory.ROBUST.value == "ROBUST"

    def test_enum_count(self) -> None:
        """Test correct number of categories (POUR principles)."""
        assert len(WCAGCategory) == 4


class TestWCAGCriterionEnum:
    """Tests for WCAGCriterion enum."""

    def test_perceivable_criteria_exist(self) -> None:
        """Test perceivable criteria (1.x) are defined."""
        assert WCAGCriterion.SC_1_1_1.value == "SC_1_1_1"
        assert WCAGCriterion.SC_1_2_1.value == "SC_1_2_1"
        assert WCAGCriterion.SC_1_3_1.value == "SC_1_3_1"
        assert WCAGCriterion.SC_1_4_3.value == "SC_1_4_3"

    def test_operable_criteria_exist(self) -> None:
        """Test operable criteria (2.x) are defined."""
        assert WCAGCriterion.SC_2_1_1.value == "SC_2_1_1"
        assert WCAGCriterion.SC_2_4_4.value == "SC_2_4_4"
        assert WCAGCriterion.SC_2_4_7.value == "SC_2_4_7"

    def test_understandable_criteria_exist(self) -> None:
        """Test understandable criteria (3.x) are defined."""
        assert WCAGCriterion.SC_3_1_1.value == "SC_3_1_1"
        assert WCAGCriterion.SC_3_2_1.value == "SC_3_2_1"
        assert WCAGCriterion.SC_3_3_1.value == "SC_3_3_1"

    def test_robust_criteria_exist(self) -> None:
        """Test robust criteria (4.x) are defined."""
        assert WCAGCriterion.SC_4_1_2.value == "SC_4_1_2"
        assert WCAGCriterion.SC_4_1_3.value == "SC_4_1_3"


class TestViolationSeverityEnum:
    """Tests for ViolationSeverity enum."""

    def test_all_severities_exist(self) -> None:
        """Test all severity levels are defined."""
        assert ViolationSeverity.CRITICAL.value == "CRITICAL"
        assert ViolationSeverity.SERIOUS.value == "SERIOUS"
        assert ViolationSeverity.MODERATE.value == "MODERATE"
        assert ViolationSeverity.MINOR.value == "MINOR"

    def test_enum_count(self) -> None:
        """Test correct number of severity levels."""
        assert len(ViolationSeverity) == 4


class TestImpactedGroupEnum:
    """Tests for ImpactedGroup enum."""

    def test_all_groups_exist(self) -> None:
        """Test all impacted user groups are defined."""
        assert ImpactedGroup.BLIND.value == "BLIND"
        assert ImpactedGroup.LOW_VISION.value == "LOW_VISION"
        assert ImpactedGroup.COLOR_BLIND.value == "COLOR_BLIND"
        assert ImpactedGroup.DEAF.value == "DEAF"
        assert ImpactedGroup.HARD_OF_HEARING.value == "HARD_OF_HEARING"
        assert ImpactedGroup.MOTOR_IMPAIRED.value == "MOTOR_IMPAIRED"
        assert ImpactedGroup.COGNITIVE.value == "COGNITIVE"
        assert ImpactedGroup.VESTIBULAR.value == "VESTIBULAR"
        assert ImpactedGroup.PHOTOSENSITIVE.value == "PHOTOSENSITIVE"

    def test_enum_count(self) -> None:
        """Test correct number of groups."""
        assert len(ImpactedGroup) == 9


class TestRemediationActionTypeEnum:
    """Tests for RemediationActionType enum."""

    def test_common_actions_exist(self) -> None:
        """Test common remediation actions are defined."""
        assert RemediationActionType.ADD_ALT_TEXT.value == "ADD_ALT_TEXT"
        assert RemediationActionType.ADD_ARIA_LABEL.value == "ADD_ARIA_LABEL"
        assert RemediationActionType.IMPROVE_CONTRAST.value == "IMPROVE_CONTRAST"
        assert RemediationActionType.ADD_KEYBOARD_NAV.value == "ADD_KEYBOARD_NAV"
        assert RemediationActionType.ADD_TEXT_FALLBACK.value == "ADD_TEXT_FALLBACK"
        assert RemediationActionType.SIMPLIFY_CONTENT.value == "SIMPLIFY_CONTENT"

    def test_enum_count(self) -> None:
        """Test correct number of action types."""
        assert len(RemediationActionType) == 16


class TestAltTextQualityEnum:
    """Tests for AltTextQuality enum."""

    def test_all_qualities_exist(self) -> None:
        """Test all alt text quality levels are defined."""
        assert AltTextQuality.EXCELLENT.value == "EXCELLENT"
        assert AltTextQuality.GOOD.value == "GOOD"
        assert AltTextQuality.NEEDS_IMPROVEMENT.value == "NEEDS_IMPROVEMENT"
        assert AltTextQuality.POOR.value == "POOR"
        assert AltTextQuality.DECORATIVE.value == "DECORATIVE"

    def test_enum_count(self) -> None:
        """Test correct number of quality levels."""
        assert len(AltTextQuality) == 5


class TestLabelQualityEnum:
    """Tests for LabelQuality enum."""

    def test_all_qualities_exist(self) -> None:
        """Test all label quality levels are defined."""
        assert LabelQuality.EXCELLENT.value == "EXCELLENT"
        assert LabelQuality.GOOD.value == "GOOD"
        assert LabelQuality.NEEDS_IMPROVEMENT.value == "NEEDS_IMPROVEMENT"
        assert LabelQuality.POOR.value == "POOR"

    def test_enum_count(self) -> None:
        """Test correct number of quality levels."""
        assert len(LabelQuality) == 4


# ============================================
# Class Tests
# ============================================


class TestAccessibilityRequirements:
    """Tests for AccessibilityRequirements class."""

    def test_basic_requirements(self) -> None:
        """Test creating basic accessibility requirements."""
        reqs = AccessibilityRequirements(
            wcag_level=WCAGLevel.AA,
            screen_reader_support=True,
            voice_control_support=False,
            reduced_motion=False,
            high_contrast=False,
            cognitive_support=False,
        )
        assert reqs.wcag_level == WCAGLevel.AA
        assert reqs.screen_reader_support is True
        assert reqs.voice_control_support is False

    def test_full_requirements(self) -> None:
        """Test creating requirements with all options."""
        reqs = AccessibilityRequirements(
            wcag_level=WCAGLevel.AAA,
            screen_reader_support=True,
            voice_control_support=True,
            reduced_motion=True,
            high_contrast=True,
            cognitive_support=True,
            keyboard_only=True,
            large_text=True,
            captions_required=True,
            audio_descriptions=True,
        )
        assert reqs.wcag_level == WCAGLevel.AAA
        assert reqs.keyboard_only is True
        assert reqs.large_text is True


class TestAccessibilityProfile:
    """Tests for AccessibilityProfile class."""

    def test_basic_profile(self) -> None:
        """Test creating basic user profile."""
        reqs = AccessibilityRequirements(
            wcag_level=WCAGLevel.AA,
            screen_reader_support=True,
            voice_control_support=False,
            reduced_motion=False,
            high_contrast=False,
            cognitive_support=False,
        )
        profile = AccessibilityProfile(
            needs=[AccessibilityNeed.VISUAL],
            requirements=reqs,
        )
        assert AccessibilityNeed.VISUAL in profile.needs
        assert profile.requirements.screen_reader_support is True

    def test_profile_with_all_options(self) -> None:
        """Test creating profile with all options."""
        reqs = AccessibilityRequirements(
            wcag_level=WCAGLevel.AA,
            screen_reader_support=True,
            voice_control_support=True,
            reduced_motion=False,
            high_contrast=True,
            cognitive_support=False,
        )
        profile = AccessibilityProfile(
            needs=[AccessibilityNeed.VISUAL, AccessibilityNeed.MOTOR],
            requirements=reqs,
            preferred_modality=Modality.VOICE,
            assistive_technologies=["VoiceOver", "Switch Control"],
            custom_preferences={"speech_rate": "slow"},
        )
        assert len(profile.needs) == 2
        assert profile.preferred_modality == Modality.VOICE
        assert profile.assistive_technologies is not None
        assert "VoiceOver" in profile.assistive_technologies


class TestAccessibilityViolation:
    """Tests for AccessibilityViolation class."""

    def test_basic_violation(self) -> None:
        """Test creating basic violation."""
        violation = AccessibilityViolation(
            rule_id="WCAG-1.1.1",
            criterion=WCAGCriterion.SC_1_1_1,
            category=WCAGCategory.PERCEIVABLE,
            severity=ViolationSeverity.CRITICAL,
            element="image-001",
            description="Image missing alt text",
            impact="Screen reader users cannot understand this content",
            impacted_groups=[ImpactedGroup.BLIND, ImpactedGroup.LOW_VISION],
            remediation="Add descriptive alt_text",
        )
        assert violation.rule_id == "WCAG-1.1.1"
        assert violation.severity == ViolationSeverity.CRITICAL
        assert ImpactedGroup.BLIND in violation.impacted_groups

    def test_violation_with_all_fields(self) -> None:
        """Test creating violation with all fields."""
        violation = AccessibilityViolation(
            rule_id="WCAG-1.4.3",
            criterion=WCAGCriterion.SC_1_4_3,
            category=WCAGCategory.PERCEIVABLE,
            severity=ViolationSeverity.SERIOUS,
            element="button-submit",
            element_type="button",
            description="Insufficient contrast ratio",
            impact="Users with low vision may struggle to read text",
            impacted_groups=[ImpactedGroup.LOW_VISION],
            remediation="Increase contrast to at least 4.5:1",
            code_example='<button style="color: #000; background: #fff">Submit</button>',
            wcag_reference="https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum",
        )
        assert violation.element_type == "button"
        assert violation.code_example is not None


class TestRemediationAction:
    """Tests for RemediationAction class."""

    def test_basic_action(self) -> None:
        """Test creating basic remediation action."""
        action = RemediationAction(
            violation_id="WCAG-1.1.1",
            action_type=RemediationActionType.ADD_ALT_TEXT,
            description="Add descriptive alt text to image",
            effort_estimate=EffortLevel.TRIVIAL,
            priority=1,
            automated_fix=False,
        )
        assert action.action_type == RemediationActionType.ADD_ALT_TEXT
        assert action.priority == 1
        assert action.automated_fix is False

    def test_action_with_suggestion(self) -> None:
        """Test creating action with suggested value."""
        action = RemediationAction(
            violation_id="WCAG-3.1.1",
            action_type=RemediationActionType.ADD_LANGUAGE,
            description="Specify content language",
            effort_estimate=EffortLevel.TRIVIAL,
            priority=2,
            automated_fix=True,
            suggested_value="en-US",
        )
        assert action.automated_fix is True
        assert action.suggested_value == "en-US"


class TestAccessibilityReport:
    """Tests for AccessibilityReport class."""

    def test_compliant_report(self) -> None:
        """Test creating a compliant report."""
        summary = ReportSummary(
            total_violations=0,
            critical_count=0,
            serious_count=0,
            moderate_count=0,
            minor_count=0,
            pass_rate=100.0,
            primary_issues=[],
            strengths=["No accessibility issues found"],
            recommendations=[],
        )
        scores = CategoryScores(
            perceivable=100.0,
            operable=100.0,
            understandable=100.0,
            robust=100.0,
        )
        report = AccessibilityReport(
            report_id="test-001",
            generated_at="2025-12-31T00:00:00Z",
            response_id="response-001",
            compliant=True,
            wcag_level=WCAGLevel.AA,
            achieved_level=WCAGLevel.AA,
            score=100.0,
            violations=[],
            summary=summary,
            category_scores=scores,
            tested_criteria=[WCAGCriterion.SC_1_1_1],
        )
        assert report.compliant is True
        assert report.score == 100.0

    def test_report_with_violations(self) -> None:
        """Test creating report with violations."""
        violation = AccessibilityViolation(
            rule_id="WCAG-1.1.1",
            criterion=WCAGCriterion.SC_1_1_1,
            category=WCAGCategory.PERCEIVABLE,
            severity=ViolationSeverity.CRITICAL,
            element="image-001",
            description="Missing alt text",
            impact="Screen readers cannot describe image",
            impacted_groups=[ImpactedGroup.BLIND],
            remediation="Add alt text",
        )
        summary = ReportSummary(
            total_violations=1,
            critical_count=1,
            serious_count=0,
            moderate_count=0,
            minor_count=0,
            pass_rate=80.0,
            primary_issues=["Missing alt text"],
            strengths=[],
            recommendations=["Add alt text to all images"],
        )
        scores = CategoryScores(
            perceivable=75.0,
            operable=100.0,
            understandable=100.0,
            robust=100.0,
        )
        report = AccessibilityReport(
            report_id="test-002",
            generated_at="2025-12-31T00:00:00Z",
            response_id="response-002",
            compliant=False,
            wcag_level=WCAGLevel.AA,
            score=75.0,
            violations=[violation],
            summary=summary,
            category_scores=scores,
            tested_criteria=[WCAGCriterion.SC_1_1_1],
        )
        assert report.compliant is False
        assert len(report.violations) == 1


class TestCategoryScores:
    """Tests for CategoryScores class."""

    def test_perfect_scores(self) -> None:
        """Test perfect category scores."""
        scores = CategoryScores(
            perceivable=100.0,
            operable=100.0,
            understandable=100.0,
            robust=100.0,
        )
        assert scores.perceivable == 100.0
        assert scores.robust == 100.0

    def test_varied_scores(self) -> None:
        """Test varied category scores."""
        scores = CategoryScores(
            perceivable=75.0,
            operable=90.0,
            understandable=85.0,
            robust=80.0,
        )
        avg = (75.0 + 90.0 + 85.0 + 80.0) / 4
        assert scores.perceivable == 75.0
        assert avg == 82.5


class TestElementValidation:
    """Tests for ElementValidation class."""

    def test_passing_validation(self) -> None:
        """Test element that passes all checks."""
        validation = ElementValidation(
            element_id="btn-submit",
            element_type="button",
            passed_checks=["Has accessible name", "Is focusable", "Has visible focus"],
            failed_checks=[],
        )
        assert len(validation.passed_checks) == 3
        assert len(validation.failed_checks) == 0

    def test_failing_validation(self) -> None:
        """Test element with failed checks."""
        violation = AccessibilityViolation(
            rule_id="WCAG-1.1.1",
            criterion=WCAGCriterion.SC_1_1_1,
            category=WCAGCategory.PERCEIVABLE,
            severity=ViolationSeverity.CRITICAL,
            element="img-001",
            description="Missing alt text",
            impact="Not accessible",
            impacted_groups=[ImpactedGroup.BLIND],
            remediation="Add alt text",
        )
        validation = ElementValidation(
            element_id="img-001",
            element_type="image",
            passed_checks=[],
            failed_checks=[violation],
            suggestions=["Add descriptive alt text"],
        )
        assert len(validation.failed_checks) == 1


class TestVisualElementValidation:
    """Tests for VisualElementValidation class."""

    def test_accessible_visual(self) -> None:
        """Test accessible visual element."""
        base = ElementValidation(
            element_id="img-001",
            element_type="image",
            passed_checks=["Has alt text"],
            failed_checks=[],
        )
        validation = VisualElementValidation(
            element=base,
            has_alt_text=True,
            alt_text_quality=AltTextQuality.GOOD,
            keyboard_accessible=True,
        )
        assert validation.has_alt_text is True
        assert validation.alt_text_quality == AltTextQuality.GOOD


class TestVoiceElementValidation:
    """Tests for VoiceElementValidation class."""

    def test_accessible_voice(self) -> None:
        """Test accessible voice element."""
        base = ElementValidation(
            element_id="voice-001",
            element_type="voice",
            passed_checks=["Has text fallback", "Language specified"],
            failed_checks=[],
        )
        validation = VoiceElementValidation(
            element=base,
            has_text_fallback=True,
            language_specified=True,
            speech_rate_adjustable=True,
            has_pauses=True,
            estimated_duration_seconds=10.5,
        )
        assert validation.has_text_fallback is True
        assert validation.language_specified is True


class TestActionElementValidation:
    """Tests for ActionElementValidation class."""

    def test_accessible_action(self) -> None:
        """Test accessible action element."""
        base = ElementValidation(
            element_id="btn-submit",
            element_type="button",
            passed_checks=["Clear label", "Is focusable"],
            failed_checks=[],
        )
        validation = ActionElementValidation(
            element=base,
            label_quality=LabelQuality.EXCELLENT,
            has_keyboard_shortcut=True,
            is_focusable=True,
            has_aria_label=True,
            action_purpose_clear=True,
        )
        assert validation.label_quality == LabelQuality.EXCELLENT
        assert validation.has_keyboard_shortcut is True


class TestUserAccessibilityCheck:
    """Tests for UserAccessibilityCheck class."""

    def test_accessible_response(self) -> None:
        """Test response that is accessible for user."""
        check = UserAccessibilityCheck(
            accessible=True,
            confidence=0.95,
            meets_needs={"VISUAL": True, "MOTOR": True},
        )
        assert check.accessible is True
        assert check.confidence == 0.95

    def test_inaccessible_response(self) -> None:
        """Test response with accessibility blockers."""
        check = UserAccessibilityCheck(
            accessible=False,
            confidence=0.8,
            meets_needs={"VISUAL": False, "MOTOR": True},
            blockers=["No voice alternative for visual content"],
            recommendations=["Add voice description"],
            alternative_modality=Modality.VOICE,
        )
        assert check.accessible is False
        assert check.blockers is not None
        assert len(check.blockers) == 1


class TestRemediationPlan:
    """Tests for RemediationPlan class."""

    def test_remediation_plan(self) -> None:
        """Test creating remediation plan."""
        action = RemediationAction(
            violation_id="WCAG-1.1.1",
            action_type=RemediationActionType.ADD_ALT_TEXT,
            description="Add alt text",
            effort_estimate=EffortLevel.TRIVIAL,
            priority=1,
            automated_fix=False,
        )
        plan = RemediationPlan(
            plan_id="plan-001",
            total_issues=1,
            estimated_effort="1 hour",
            quick_wins=[action],
            critical_fixes=[action],
            recommended_order=[action],
            effort_breakdown={"TRIVIAL": 1},
        )
        assert plan.total_issues == 1
        assert len(plan.quick_wins) == 1


# ============================================
# Constants Tests
# ============================================


class TestConstants:
    """Tests for module constants."""

    def test_perceivable_criteria(self) -> None:
        """Test perceivable criteria list."""
        assert WCAGCriterion.SC_1_1_1 in PERCEIVABLE_CRITERIA
        assert len(PERCEIVABLE_CRITERIA) >= 5

    def test_operable_criteria(self) -> None:
        """Test operable criteria list."""
        assert WCAGCriterion.SC_2_1_1 in OPERABLE_CRITERIA
        assert len(OPERABLE_CRITERIA) >= 4

    def test_understandable_criteria(self) -> None:
        """Test understandable criteria list."""
        assert WCAGCriterion.SC_3_1_1 in UNDERSTANDABLE_CRITERIA
        assert len(UNDERSTANDABLE_CRITERIA) >= 3

    def test_robust_criteria(self) -> None:
        """Test robust criteria list."""
        assert WCAGCriterion.SC_4_1_2 in ROBUST_CRITERIA
        assert len(ROBUST_CRITERIA) >= 2

    def test_level_requirements(self) -> None:
        """Test level requirements dictionary."""
        assert WCAGLevel.A in LEVEL_REQUIREMENTS
        assert WCAGLevel.AA in LEVEL_REQUIREMENTS
        assert WCAGLevel.AAA in LEVEL_REQUIREMENTS

        # Level A is least strict
        assert LEVEL_REQUIREMENTS[WCAGLevel.A]["min_score"] < LEVEL_REQUIREMENTS[WCAGLevel.AA]["min_score"]
        # Level AAA is most strict
        assert LEVEL_REQUIREMENTS[WCAGLevel.AAA]["min_score"] > LEVEL_REQUIREMENTS[WCAGLevel.AA]["min_score"]


# ============================================
# Validation Function Tests
# ============================================


class TestValidateMultimodalResponse:
    """Tests for validate_multimodal_response function."""

    def _create_accessible_response(self) -> MultiModalResponse:
        """Create a response that should pass accessibility checks."""
        return MultiModalResponse(
            response_id="accessible-001",
            primary_modality=Modality.TEXT,
            text=TextResponse(
                content="Your meeting has been scheduled.",
                format=TextFormat.PLAIN,
            ),
            voice=VoiceResponse(
                text="Your meeting has been scheduled.",
                language="en-US",
            ),
            accessibility=AccessibilityMeta(
                aria_label="Meeting confirmation",
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.MINIMAL,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

    def _create_inaccessible_response(self) -> MultiModalResponse:
        """Create a response with accessibility issues."""
        return MultiModalResponse(
            response_id="inaccessible-001",
            primary_modality=Modality.VISUAL,
            visuals=[
                MultiModalVisualElement(
                    element_type=MultiModalVisualType.IMAGE,
                    content="Chart data",
                    priority=1,
                    interactive=False,
                    # Missing alt_text!
                ),
            ],
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.OFF,
                cognitive_load=CognitiveLoad.HIGH,
                supports_screen_reader=False,
                supports_keyboard_nav=False,
                high_contrast_available=False,
                reduced_motion_safe=False,
            ),
        )

    def test_accessible_response_passes(self) -> None:
        """Test that accessible response passes validation."""
        response = self._create_accessible_response()
        report = validate_multimodal_response(response)

        assert report.response_id == "accessible-001"
        assert report.wcag_level == WCAGLevel.AA
        assert report.score > 50.0

    def test_inaccessible_response_has_violations(self) -> None:
        """Test that inaccessible response has violations."""
        response = self._create_inaccessible_response()
        report = validate_multimodal_response(response)

        assert len(report.violations) > 0
        assert report.score < 100.0

    def test_validates_missing_alt_text(self) -> None:
        """Test that missing alt text is detected."""
        response = self._create_inaccessible_response()
        report = validate_multimodal_response(response)

        alt_text_violations = [
            v for v in report.violations
            if v.criterion == WCAGCriterion.SC_1_1_1
        ]
        assert len(alt_text_violations) > 0

    def test_custom_requirements(self) -> None:
        """Test validation with custom requirements."""
        response = self._create_inaccessible_response()
        reqs = AccessibilityRequirements(
            wcag_level=WCAGLevel.AAA,
            screen_reader_support=True,
            voice_control_support=True,
            reduced_motion=True,
            high_contrast=True,
            cognitive_support=True,
        )
        report = validate_multimodal_response(
            response, requirements=reqs, level=WCAGLevel.AAA
        )

        assert report.wcag_level == WCAGLevel.AAA
        # Strict requirements = more violations
        assert len(report.violations) > 0


class TestCheckAccessibilityForUser:
    """Tests for check_accessibility_for_user function."""

    def _create_voice_response(self) -> MultiModalResponse:
        """Create a voice-primary response."""
        return MultiModalResponse(
            response_id="voice-001",
            primary_modality=Modality.VOICE,
            voice=VoiceResponse(
                text="You have 3 new messages.",
                language="en-US",
            ),
            text=TextResponse(
                content="You have 3 new messages.",
                format=TextFormat.PLAIN,
            ),
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.LOW,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

    def _create_blind_user_profile(self) -> AccessibilityProfile:
        """Create profile for blind user."""
        return AccessibilityProfile(
            needs=[AccessibilityNeed.VISUAL],
            requirements=AccessibilityRequirements(
                wcag_level=WCAGLevel.AA,
                screen_reader_support=True,
                voice_control_support=True,
                reduced_motion=False,
                high_contrast=False,
                cognitive_support=False,
            ),
            preferred_modality=Modality.VOICE,
        )

    def test_voice_response_accessible_for_blind(self) -> None:
        """Test that voice response is accessible for blind users."""
        response = self._create_voice_response()
        profile = self._create_blind_user_profile()

        check = check_accessibility_for_user(response, profile)

        assert check.accessible is True
        assert check.confidence > 0.5


class TestValidateVisualElement:
    """Tests for validate_visual_element function."""

    def test_element_with_alt_text(self) -> None:
        """Test visual element with proper alt text."""
        element = MultiModalVisualElement(
            element_type=MultiModalVisualType.IMAGE,
            content="chart_data.png",
            alt_text="Sales chart showing growth of 25% in Q4 2025",
            priority=1,
            interactive=False,
        )
        reqs = AccessibilityRequirements(
            wcag_level=WCAGLevel.AA,
            screen_reader_support=True,
            voice_control_support=False,
            reduced_motion=False,
            high_contrast=False,
            cognitive_support=False,
        )

        validation = validate_visual_element(element, reqs)

        assert validation.has_alt_text is True
        assert validation.alt_text_quality is not None
        assert len(validation.element.failed_checks) == 0

    def test_element_without_alt_text(self) -> None:
        """Test visual element missing alt text."""
        element = MultiModalVisualElement(
            element_type=MultiModalVisualType.IMAGE,
            content="chart_data.png",
            priority=1,
            interactive=False,
            # No alt_text
        )
        reqs = AccessibilityRequirements(
            wcag_level=WCAGLevel.AA,
            screen_reader_support=True,
            voice_control_support=False,
            reduced_motion=False,
            high_contrast=False,
            cognitive_support=False,
        )

        validation = validate_visual_element(element, reqs)

        assert validation.has_alt_text is False
        assert len(validation.element.failed_checks) > 0


class TestValidateVoiceElement:
    """Tests for validate_voice_element function."""

    def test_voice_with_text_fallback(self) -> None:
        """Test voice element with text fallback."""
        voice = VoiceResponse(
            text="Welcome to the application.",
            language="en-US",
            ssml='<speak><break time="500ms"/>Welcome to the application.</speak>',
        )

        validation = validate_voice_element(voice, has_text_fallback=True)

        assert validation.has_text_fallback is True
        assert validation.language_specified is True
        assert validation.has_pauses is True
        assert len(validation.element.failed_checks) == 0

    def test_voice_without_fallback(self) -> None:
        """Test voice element without text fallback."""
        voice = VoiceResponse(
            text="Important message",
            language="en-US",
        )

        validation = validate_voice_element(voice, has_text_fallback=False)

        assert validation.has_text_fallback is False
        assert len(validation.element.failed_checks) > 0


class TestValidateActionElement:
    """Tests for validate_action_element function."""

    def test_action_with_clear_label(self) -> None:
        """Test action with clear, descriptive label."""
        action = MultiModalAction(
            action_id="btn-submit",
            interaction_type=InteractionType.BUTTON,
            label="Submit Application",
            description="Submit your completed application for review",
            keyboard_shortcut="Ctrl+Enter",
            is_primary=True,
            is_destructive=False,
            requires_confirmation=False,
            disabled=False,
        )

        validation = validate_action_element(action)

        assert validation.label_quality in [LabelQuality.EXCELLENT, LabelQuality.GOOD]
        assert validation.has_keyboard_shortcut is True
        assert validation.action_purpose_clear is True

    def test_action_with_poor_label(self) -> None:
        """Test action with poor, non-descriptive label."""
        action = MultiModalAction(
            action_id="btn-x",
            interaction_type=InteractionType.BUTTON,
            label="X",  # Too short!
            is_primary=False,
            is_destructive=True,
            requires_confirmation=False,
            disabled=False,
        )

        validation = validate_action_element(action)

        assert validation.label_quality == LabelQuality.POOR
        assert len(validation.element.failed_checks) > 0


# ============================================
# Integration Tests
# ============================================


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_validation_workflow(self) -> None:
        """Test complete validation workflow."""
        # Create response
        response = MultiModalResponse(
            response_id="test-001",
            primary_modality=Modality.HYBRID,
            text=TextResponse(
                content="Here is your report summary.",
                format=TextFormat.PLAIN,
            ),
            voice=VoiceResponse(
                text="Here is your report summary.",
                language="en-US",
            ),
            visuals=[
                MultiModalVisualElement(
                    element_type=MultiModalVisualType.CHART,
                    content="chart_data",
                    alt_text="Bar chart showing monthly sales increasing from $10K to $50K",
                    priority=1,
                    interactive=True,
                ),
            ],
            actions=[
                MultiModalAction(
                    action_id="download",
                    interaction_type=InteractionType.BUTTON,
                    label="Download Full Report",
                    keyboard_shortcut="Ctrl+D",
                    is_primary=True,
                    is_destructive=False,
                    requires_confirmation=False,
                    disabled=False,
                ),
            ],
            accessibility=AccessibilityMeta(
                aria_label="Report summary",
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.LOW,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        # Validate
        report = validate_multimodal_response(response)

        # Check results
        assert report.response_id == "test-001"
        assert report.score > 70.0
        assert report.summary.total_violations >= 0

    def test_accessibility_for_multiple_user_profiles(self) -> None:
        """Test accessibility for different user profiles."""
        response = MultiModalResponse(
            response_id="multi-user-001",
            primary_modality=Modality.HYBRID,
            text=TextResponse(
                content="Welcome message",
                format=TextFormat.PLAIN,
            ),
            voice=VoiceResponse(
                text="Welcome message",
                language="en-US",
            ),
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.LOW,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        # Test for blind user
        blind_profile = AccessibilityProfile(
            needs=[AccessibilityNeed.VISUAL],
            requirements=AccessibilityRequirements(
                wcag_level=WCAGLevel.AA,
                screen_reader_support=True,
                voice_control_support=True,
                reduced_motion=False,
                high_contrast=False,
                cognitive_support=False,
            ),
        )
        blind_check = check_accessibility_for_user(response, blind_profile)
        assert blind_check.accessible is True

        # Test for deaf user
        deaf_profile = AccessibilityProfile(
            needs=[AccessibilityNeed.AUDITORY],
            requirements=AccessibilityRequirements(
                wcag_level=WCAGLevel.AA,
                screen_reader_support=False,
                voice_control_support=False,
                reduced_motion=False,
                high_contrast=False,
                cognitive_support=False,
            ),
        )
        deaf_check = check_accessibility_for_user(response, deaf_profile)
        assert deaf_check.accessible is True  # Has text fallback
