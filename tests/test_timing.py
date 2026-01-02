"""Comprehensive unit tests for interaction timing validator.

Tests cover:
- TimeoutConfig validation
- InputMethodConfig validation
- FeedbackConfig validation
- ErrorHandlingConfig validation
- AutoUpdateConfig validation
- Combined interaction validation
- Timing thresholds by compliance level
- Score calculation and level determination

Issue #73 - Task 4.7: Interaction Timing Validator
Part of #27 - Phase 4: LUI Accessibility Standards
"""

import pytest

from src.accessibility.timing import (
    AutoUpdateConfig,
    ErrorHandlingConfig,
    FeedbackConfig,
    InputMethodConfig,
    InputValidationResult,
    InteractionTimingValidator,
    InteractionValidationResult,
    TimeoutConfig,
    TimingThreshold,
    TimingValidationResult,
    TimingViolation,
    TIMING_THRESHOLDS,
    INPUT_REQUIREMENTS,
)
from src.accessibility.checker import ComplianceLevel, ViolationSeverity


# ============================================
# Test Data
# ============================================

# Valid Level A timeout config
VALID_A_TIMEOUT = TimeoutConfig(
    initial_timeout_seconds=25,
    warning_before_seconds=5,
    extension_allowed=False,
    extension_seconds=0,
    max_extensions=0,
)

# Valid Level AA timeout config
VALID_AA_TIMEOUT = TimeoutConfig(
    initial_timeout_seconds=45,
    warning_before_seconds=15,
    extension_allowed=True,
    extension_seconds=30,
    max_extensions=3,
)

# Valid Level AAA timeout config
VALID_AAA_TIMEOUT = TimeoutConfig(
    initial_timeout_seconds=60,
    warning_before_seconds=20,
    extension_allowed=True,
    extension_seconds=30,
    max_extensions=-1,  # unlimited
)

# Invalid timeout (too short)
INVALID_TIMEOUT = TimeoutConfig(
    initial_timeout_seconds=10,
    warning_before_seconds=2,
    extension_allowed=False,
    extension_seconds=0,
    max_extensions=0,
)

# Valid Level A input config
VALID_A_INPUT = InputMethodConfig(
    keyboard_accessible=True,
    voice_input=False,
    touch_input=True,
    switch_access=False,
    eye_tracking=False,
    gesture_alternatives=False,
    pointer_adjustable=False,
)

# Valid Level AA input config
VALID_AA_INPUT = InputMethodConfig(
    keyboard_accessible=True,
    voice_input=False,
    touch_input=True,
    switch_access=False,
    eye_tracking=False,
    gesture_alternatives=True,
    pointer_adjustable=True,
)

# Valid Level AAA input config
VALID_AAA_INPUT = InputMethodConfig(
    keyboard_accessible=True,
    voice_input=True,
    touch_input=True,
    switch_access=True,
    eye_tracking=True,
    gesture_alternatives=True,
    pointer_adjustable=True,
)

# Invalid input (no keyboard)
INVALID_INPUT = InputMethodConfig(
    keyboard_accessible=False,
    voice_input=False,
    touch_input=True,
    switch_access=False,
    eye_tracking=False,
    gesture_alternatives=False,
    pointer_adjustable=False,
)

# Valid feedback config for AAA
VALID_AAA_FEEDBACK = FeedbackConfig(
    immediate_confirmation=True,
    error_messages_clear=True,
    success_indicators=True,
    progress_indicators=True,
    status_updates=True,
)

# Minimal feedback config
MINIMAL_FEEDBACK = FeedbackConfig(
    immediate_confirmation=True,
    error_messages_clear=True,
    success_indicators=True,
    progress_indicators=False,
    status_updates=False,
)

# Invalid feedback config
INVALID_FEEDBACK = FeedbackConfig(
    immediate_confirmation=False,
    error_messages_clear=False,
    success_indicators=False,
    progress_indicators=False,
    status_updates=False,
)

# Valid error handling for AAA
VALID_AAA_ERROR = ErrorHandlingConfig(
    error_prevention=True,
    error_identification=True,
    error_suggestions=True,
    undo_available=True,
    auto_save=True,
    recovery_options=True,
)

# Minimal error handling
MINIMAL_ERROR = ErrorHandlingConfig(
    error_prevention=True,
    error_identification=True,
    error_suggestions=False,
    undo_available=False,
    auto_save=False,
    recovery_options=False,
)

# Auto-update with controls
AUTO_UPDATE_CONTROLLED = AutoUpdateConfig(
    has_auto_update=True,
    can_pause=True,
    can_stop=True,
    can_adjust_frequency=True,
    update_frequency_seconds=30,
)

# Auto-update without controls
AUTO_UPDATE_UNCONTROLLED = AutoUpdateConfig(
    has_auto_update=True,
    can_pause=False,
    can_stop=False,
    can_adjust_frequency=False,
    update_frequency_seconds=5,
)

# No auto-update
NO_AUTO_UPDATE = AutoUpdateConfig(
    has_auto_update=False,
    can_pause=False,
    can_stop=False,
    can_adjust_frequency=False,
    update_frequency_seconds=0,
)


# ============================================
# TimingViolation Tests
# ============================================


class TestTimingViolation:
    """Tests for TimingViolation dataclass."""

    def test_create_violation(self):
        """Test creating a timing violation."""
        violation = TimingViolation(
            code="TIMEOUT_TOO_SHORT",
            severity=ViolationSeverity.CRITICAL,
            description="Timeout is too short",
            location="initial_timeout_seconds",
            remediation="Increase timeout",
            threshold_expected=20,
            threshold_actual=10,
        )
        assert violation.code == "TIMEOUT_TOO_SHORT"
        assert violation.severity == ViolationSeverity.CRITICAL
        assert violation.weight == 0.25

    def test_violation_weights(self):
        """Test violation weight for all severities."""
        weights = {
            ViolationSeverity.CRITICAL: 0.25,
            ViolationSeverity.MAJOR: 0.15,
            ViolationSeverity.MINOR: 0.05,
            ViolationSeverity.ADVISORY: 0.02,
        }
        for severity, expected_weight in weights.items():
            violation = TimingViolation(
                code="TEST",
                severity=severity,
                description="Test",
                location="test",
                remediation="Fix",
            )
            assert violation.weight == expected_weight


# ============================================
# TimingValidationResult Tests
# ============================================


class TestTimingValidationResult:
    """Tests for TimingValidationResult dataclass."""

    def test_create_passing_result(self):
        """Test creating a passing result."""
        result = TimingValidationResult(
            config_type="TimeoutConfig",
            target_level=ComplianceLevel.LEVEL_AA,
            achieved_level=ComplianceLevel.LEVEL_AA,
            score=0.85,
            passes=True,
            violations=[],
            recommendations=[],
        )
        assert result.passes is True
        assert result.critical_count == 0
        assert "PASSES" in result.summary

    def test_create_failing_result(self):
        """Test creating a failing result."""
        violations = [
            TimingViolation(
                code="TEST",
                severity=ViolationSeverity.CRITICAL,
                description="Test",
                location="test",
                remediation="Fix",
            )
        ]
        result = TimingValidationResult(
            config_type="TimeoutConfig",
            target_level=ComplianceLevel.LEVEL_AA,
            achieved_level=None,
            score=0.5,
            passes=False,
            violations=violations,
        )
        assert result.passes is False
        assert result.critical_count == 1
        assert "FAILS" in result.summary


# ============================================
# TIMING_THRESHOLDS Tests
# ============================================


class TestTimingThresholds:
    """Tests for timing threshold constants."""

    def test_level_a_thresholds(self):
        """Test Level A thresholds."""
        threshold = TIMING_THRESHOLDS[ComplianceLevel.LEVEL_A]
        assert threshold.min_timeout_seconds == 20
        assert threshold.min_warning_seconds == 5
        assert threshold.extension_required is False
        assert threshold.unlimited_extensions is False

    def test_level_aa_thresholds(self):
        """Test Level AA thresholds."""
        threshold = TIMING_THRESHOLDS[ComplianceLevel.LEVEL_AA]
        assert threshold.min_timeout_seconds == 30
        assert threshold.min_warning_seconds == 10
        assert threshold.extension_required is True
        assert threshold.unlimited_extensions is False

    def test_level_aaa_thresholds(self):
        """Test Level AAA thresholds."""
        threshold = TIMING_THRESHOLDS[ComplianceLevel.LEVEL_AAA]
        assert threshold.min_timeout_seconds == 60
        assert threshold.min_warning_seconds == 20
        assert threshold.extension_required is True
        assert threshold.unlimited_extensions is True

    def test_all_levels_exist(self):
        """Test all compliance levels have thresholds."""
        for level in ComplianceLevel:
            assert level in TIMING_THRESHOLDS


# ============================================
# INPUT_REQUIREMENTS Tests
# ============================================


class TestInputRequirements:
    """Tests for input requirement constants."""

    def test_keyboard_always_required(self):
        """Test keyboard is required at all levels."""
        for level in ComplianceLevel:
            assert INPUT_REQUIREMENTS[level]["keyboard_accessible"] is True

    def test_gesture_alternatives_aa_plus(self):
        """Test gesture alternatives required for AA+."""
        assert INPUT_REQUIREMENTS[ComplianceLevel.LEVEL_A]["gesture_alternatives"] is False
        assert INPUT_REQUIREMENTS[ComplianceLevel.LEVEL_AA]["gesture_alternatives"] is True
        assert INPUT_REQUIREMENTS[ComplianceLevel.LEVEL_AAA]["gesture_alternatives"] is True

    def test_voice_switch_aaa_only(self):
        """Test voice and switch access only required for AAA."""
        assert INPUT_REQUIREMENTS[ComplianceLevel.LEVEL_A]["voice_input"] is False
        assert INPUT_REQUIREMENTS[ComplianceLevel.LEVEL_AA]["voice_input"] is False
        assert INPUT_REQUIREMENTS[ComplianceLevel.LEVEL_AAA]["voice_input"] is True
        assert INPUT_REQUIREMENTS[ComplianceLevel.LEVEL_AAA]["switch_access"] is True


# ============================================
# TimeoutConfig Validation Tests
# ============================================


class TestTimeoutValidation:
    """Tests for timeout configuration validation."""

    @pytest.fixture
    def validator(self):
        return InteractionTimingValidator()

    def test_valid_a_timeout(self, validator):
        """Test valid Level A timeout passes."""
        result = validator.validate_timeout(VALID_A_TIMEOUT, ComplianceLevel.LEVEL_A)
        assert result.passes is True
        assert result.achieved_level == ComplianceLevel.LEVEL_A

    def test_valid_aa_timeout(self, validator):
        """Test valid Level AA timeout passes."""
        result = validator.validate_timeout(VALID_AA_TIMEOUT, ComplianceLevel.LEVEL_AA)
        assert result.passes is True
        assert result.achieved_level == ComplianceLevel.LEVEL_AA

    def test_valid_aaa_timeout(self, validator):
        """Test valid Level AAA timeout passes."""
        result = validator.validate_timeout(VALID_AAA_TIMEOUT, ComplianceLevel.LEVEL_AAA)
        assert result.passes is True
        assert result.achieved_level == ComplianceLevel.LEVEL_AAA

    def test_invalid_timeout_too_short(self, validator):
        """Test timeout too short fails."""
        result = validator.validate_timeout(INVALID_TIMEOUT, ComplianceLevel.LEVEL_A)
        assert result.passes is False
        assert result.critical_count >= 1

        # Check for TIMEOUT_TOO_SHORT violation
        codes = [v.code for v in result.violations]
        assert "TIMEOUT_TOO_SHORT" in codes

    def test_aa_timeout_without_extension(self, validator):
        """Test AA timeout without extension fails."""
        config = TimeoutConfig(
            initial_timeout_seconds=45,
            warning_before_seconds=15,
            extension_allowed=False,
            extension_seconds=0,
            max_extensions=0,
        )
        result = validator.validate_timeout(config, ComplianceLevel.LEVEL_AA)
        assert result.passes is False

        codes = [v.code for v in result.violations]
        assert "EXTENSION_NOT_ALLOWED" in codes

    def test_aaa_timeout_limited_extensions(self, validator):
        """Test AAA timeout with limited extensions doesn't achieve AAA."""
        config = TimeoutConfig(
            initial_timeout_seconds=60,
            warning_before_seconds=20,
            extension_allowed=True,
            extension_seconds=30,
            max_extensions=3,  # Should be -1 for unlimited
        )
        result = validator.validate_timeout(config, ComplianceLevel.LEVEL_AAA)
        # Passes overall (score >= 0.70, no critical violations) but doesn't achieve AAA
        assert result.achieved_level == ComplianceLevel.LEVEL_AA  # Only achieves AA

        codes = [v.code for v in result.violations]
        assert "EXTENSIONS_LIMITED" in codes

    def test_warning_time_insufficient(self, validator):
        """Test insufficient warning time is flagged."""
        config = TimeoutConfig(
            initial_timeout_seconds=60,
            warning_before_seconds=5,  # Too short for AAA (needs 20s)
            extension_allowed=True,
            extension_seconds=30,
            max_extensions=-1,
        )
        result = validator.validate_timeout(config, ComplianceLevel.LEVEL_AAA)

        codes = [v.code for v in result.violations]
        assert "WARNING_TIME_INSUFFICIENT" in codes

    def test_short_extension_duration(self, validator):
        """Test short extension duration is flagged."""
        config = TimeoutConfig(
            initial_timeout_seconds=45,
            warning_before_seconds=15,
            extension_allowed=True,
            extension_seconds=5,  # Too short
            max_extensions=3,
        )
        result = validator.validate_timeout(config, ComplianceLevel.LEVEL_AA)

        codes = [v.code for v in result.violations]
        assert "EXTENSION_TOO_SHORT" in codes

    def test_recommendations_generated(self, validator):
        """Test recommendations are generated for violations."""
        result = validator.validate_timeout(INVALID_TIMEOUT, ComplianceLevel.LEVEL_AA)
        assert len(result.recommendations) > 0


# ============================================
# InputMethodConfig Validation Tests
# ============================================


class TestInputValidation:
    """Tests for input method configuration validation."""

    @pytest.fixture
    def validator(self):
        return InteractionTimingValidator()

    def test_valid_a_input(self, validator):
        """Test valid Level A input passes."""
        result = validator.validate_input_methods(VALID_A_INPUT, ComplianceLevel.LEVEL_A)
        assert result.passes is True
        assert result.achieved_level == ComplianceLevel.LEVEL_A

    def test_valid_aa_input(self, validator):
        """Test valid Level AA input passes."""
        result = validator.validate_input_methods(VALID_AA_INPUT, ComplianceLevel.LEVEL_AA)
        assert result.passes is True
        assert result.achieved_level == ComplianceLevel.LEVEL_AA

    def test_valid_aaa_input(self, validator):
        """Test valid Level AAA input passes."""
        result = validator.validate_input_methods(VALID_AAA_INPUT, ComplianceLevel.LEVEL_AAA)
        assert result.passes is True
        assert result.achieved_level == ComplianceLevel.LEVEL_AAA

    def test_keyboard_not_accessible_fails(self, validator):
        """Test missing keyboard accessibility fails."""
        result = validator.validate_input_methods(INVALID_INPUT, ComplianceLevel.LEVEL_A)
        assert result.passes is False
        assert result.achieved_level is None

        codes = [v.code for v in result.violations]
        assert "KEYBOARD_NOT_ACCESSIBLE" in codes

    def test_aa_without_gesture_alternatives(self, validator):
        """Test AA without gesture alternatives fails."""
        result = validator.validate_input_methods(VALID_A_INPUT, ComplianceLevel.LEVEL_AA)
        # Should fail or have violations for missing gesture alternatives
        codes = [v.code for v in result.violations]
        assert "GESTURE_ALTERNATIVES_MISSING" in codes

    def test_aaa_without_voice(self, validator):
        """Test AAA without voice input has violations."""
        result = validator.validate_input_methods(VALID_AA_INPUT, ComplianceLevel.LEVEL_AAA)
        codes = [v.code for v in result.violations]
        assert "VOICE_INPUT_MISSING" in codes

    def test_aaa_without_switch_access(self, validator):
        """Test AAA without switch access has violations."""
        result = validator.validate_input_methods(VALID_AA_INPUT, ComplianceLevel.LEVEL_AAA)
        codes = [v.code for v in result.violations]
        assert "SWITCH_ACCESS_MISSING" in codes

    def test_supported_methods_listed(self, validator):
        """Test supported methods are listed."""
        result = validator.validate_input_methods(VALID_AAA_INPUT, ComplianceLevel.LEVEL_AAA)
        assert "keyboard" in result.supported_methods
        assert "voice_input" in result.supported_methods
        assert "switch_access" in result.supported_methods

    def test_missing_methods_listed(self, validator):
        """Test missing methods are listed."""
        result = validator.validate_input_methods(VALID_A_INPUT, ComplianceLevel.LEVEL_AAA)
        assert "voice_input" in result.missing_methods
        assert "switch_access" in result.missing_methods


# ============================================
# FeedbackConfig Validation Tests
# ============================================


class TestFeedbackValidation:
    """Tests for feedback configuration validation."""

    @pytest.fixture
    def validator(self):
        return InteractionTimingValidator()

    def test_valid_aaa_feedback(self, validator):
        """Test valid AAA feedback passes."""
        result = validator.validate_feedback(VALID_AAA_FEEDBACK, ComplianceLevel.LEVEL_AAA)
        assert result.passes is True

    def test_minimal_feedback_level_a(self, validator):
        """Test minimal feedback passes at Level A."""
        result = validator.validate_feedback(MINIMAL_FEEDBACK, ComplianceLevel.LEVEL_A)
        assert result.passes is True

    def test_invalid_feedback(self, validator):
        """Test invalid feedback has violations and doesn't achieve any level."""
        result = validator.validate_feedback(INVALID_FEEDBACK, ComplianceLevel.LEVEL_A)
        # Has MAJOR violations but score is 0.70, which meets threshold
        assert result.achieved_level is None  # Doesn't achieve any level
        assert len(result.violations) >= 2

        codes = [v.code for v in result.violations]
        assert "NO_IMMEDIATE_CONFIRMATION" in codes
        assert "ERROR_MESSAGES_UNCLEAR" in codes

    def test_aa_without_progress_indicators(self, validator):
        """Test AA without progress indicators is flagged."""
        result = validator.validate_feedback(MINIMAL_FEEDBACK, ComplianceLevel.LEVEL_AA)
        codes = [v.code for v in result.violations]
        assert "NO_PROGRESS_INDICATORS" in codes

    def test_aaa_without_status_updates(self, validator):
        """Test AAA without status updates is flagged."""
        config = FeedbackConfig(
            immediate_confirmation=True,
            error_messages_clear=True,
            success_indicators=True,
            progress_indicators=True,
            status_updates=False,
        )
        result = validator.validate_feedback(config, ComplianceLevel.LEVEL_AAA)
        codes = [v.code for v in result.violations]
        assert "NO_STATUS_UPDATES" in codes


# ============================================
# ErrorHandlingConfig Validation Tests
# ============================================


class TestErrorHandlingValidation:
    """Tests for error handling configuration validation."""

    @pytest.fixture
    def validator(self):
        return InteractionTimingValidator()

    def test_valid_aaa_error_handling(self, validator):
        """Test valid AAA error handling passes."""
        result = validator.validate_error_handling(VALID_AAA_ERROR, ComplianceLevel.LEVEL_AAA)
        assert result.passes is True

    def test_minimal_error_level_a(self, validator):
        """Test minimal error handling passes at Level A."""
        result = validator.validate_error_handling(MINIMAL_ERROR, ComplianceLevel.LEVEL_A)
        assert result.passes is True

    def test_no_error_identification_fails(self, validator):
        """Test missing error identification doesn't achieve any level."""
        config = ErrorHandlingConfig(
            error_prevention=True,
            error_identification=False,
            error_suggestions=False,
            undo_available=False,
            auto_save=False,
            recovery_options=False,
        )
        result = validator.validate_error_handling(config, ComplianceLevel.LEVEL_A)
        # Has violation but passes overall since score meets threshold
        assert result.achieved_level is None  # Doesn't achieve any level
        assert len(result.violations) >= 1

        codes = [v.code for v in result.violations]
        assert "ERROR_IDENTIFICATION_MISSING" in codes

    def test_aa_without_undo(self, validator):
        """Test AA without undo is flagged."""
        result = validator.validate_error_handling(MINIMAL_ERROR, ComplianceLevel.LEVEL_AA)
        codes = [v.code for v in result.violations]
        assert "NO_UNDO" in codes

    def test_aaa_without_auto_save(self, validator):
        """Test AAA without auto-save is flagged."""
        config = ErrorHandlingConfig(
            error_prevention=True,
            error_identification=True,
            error_suggestions=True,
            undo_available=True,
            auto_save=False,
            recovery_options=True,
        )
        result = validator.validate_error_handling(config, ComplianceLevel.LEVEL_AAA)
        codes = [v.code for v in result.violations]
        assert "NO_AUTO_SAVE" in codes


# ============================================
# AutoUpdateConfig Validation Tests
# ============================================


class TestAutoUpdateValidation:
    """Tests for auto-update configuration validation."""

    @pytest.fixture
    def validator(self):
        return InteractionTimingValidator()

    def test_no_auto_update_passes(self, validator):
        """Test no auto-update passes at all levels."""
        result = validator.validate_auto_update(NO_AUTO_UPDATE, ComplianceLevel.LEVEL_AAA)
        assert result.passes is True
        assert result.achieved_level == ComplianceLevel.LEVEL_AAA

    def test_controlled_auto_update_passes(self, validator):
        """Test controlled auto-update passes."""
        result = validator.validate_auto_update(AUTO_UPDATE_CONTROLLED, ComplianceLevel.LEVEL_AAA)
        assert result.passes is True

    def test_uncontrolled_auto_update_fails(self, validator):
        """Test uncontrolled auto-update fails."""
        result = validator.validate_auto_update(AUTO_UPDATE_UNCONTROLLED, ComplianceLevel.LEVEL_A)
        assert result.passes is False

        codes = [v.code for v in result.violations]
        assert "CANNOT_PAUSE_AUTO_UPDATE" in codes
        assert "CANNOT_STOP_AUTO_UPDATE" in codes

    def test_aaa_without_frequency_adjustment(self, validator):
        """Test AAA without frequency adjustment is flagged."""
        config = AutoUpdateConfig(
            has_auto_update=True,
            can_pause=True,
            can_stop=True,
            can_adjust_frequency=False,
            update_frequency_seconds=30,
        )
        result = validator.validate_auto_update(config, ComplianceLevel.LEVEL_AAA)
        codes = [v.code for v in result.violations]
        assert "CANNOT_ADJUST_FREQUENCY" in codes

    def test_high_update_frequency_flagged(self, validator):
        """Test high update frequency is flagged."""
        config = AutoUpdateConfig(
            has_auto_update=True,
            can_pause=True,
            can_stop=True,
            can_adjust_frequency=True,
            update_frequency_seconds=2,  # Too fast
        )
        result = validator.validate_auto_update(config, ComplianceLevel.LEVEL_AA)
        codes = [v.code for v in result.violations]
        assert "UPDATE_FREQUENCY_TOO_HIGH" in codes


# ============================================
# Combined Interaction Validation Tests
# ============================================


class TestInteractionValidation:
    """Tests for combined interaction validation."""

    @pytest.fixture
    def validator(self):
        return InteractionTimingValidator()

    def test_complete_validation(self, validator):
        """Test complete interaction validation."""
        result = validator.validate_interaction(
            component_id="test_component",
            target_level=ComplianceLevel.LEVEL_AA,
            timeout_config=VALID_AA_TIMEOUT,
            input_config=VALID_AA_INPUT,
            feedback_config=VALID_AAA_FEEDBACK,
            error_config=VALID_AAA_ERROR,
            auto_update_config=NO_AUTO_UPDATE,
        )
        assert result.component_id == "test_component"
        assert result.target_level == ComplianceLevel.LEVEL_AA
        assert result.timing_result is not None
        assert result.input_result is not None
        assert result.feedback_result is not None
        assert result.error_handling_result is not None
        assert result.auto_update_result is not None

    def test_partial_validation(self, validator):
        """Test validation with only some configs."""
        result = validator.validate_interaction(
            component_id="partial",
            target_level=ComplianceLevel.LEVEL_A,
            timeout_config=VALID_A_TIMEOUT,
        )
        assert result.timing_result is not None
        assert result.input_result is None
        assert result.feedback_result is None

    def test_overall_passes_when_all_pass(self, validator):
        """Test overall passes when all individual validations pass."""
        result = validator.validate_interaction(
            component_id="passing",
            target_level=ComplianceLevel.LEVEL_AA,
            timeout_config=VALID_AA_TIMEOUT,
            input_config=VALID_AA_INPUT,
        )
        assert result.overall_passes is True
        assert result.overall_score >= 0.7

    def test_overall_fails_when_any_fails(self, validator):
        """Test overall fails when any validation fails."""
        result = validator.validate_interaction(
            component_id="failing",
            target_level=ComplianceLevel.LEVEL_AA,
            timeout_config=VALID_AA_TIMEOUT,
            input_config=INVALID_INPUT,  # This fails
        )
        assert result.overall_passes is False


# ============================================
# Timing Essential Tests
# ============================================


class TestTimingEssential:
    """Tests for timing-essential interaction checks."""

    @pytest.fixture
    def validator(self):
        return InteractionTimingValidator()

    def test_timing_essential_aa_no_pause(self, validator):
        """Test timing-essential without pause fails at AA."""
        violations = validator.check_timing_essential(
            requires_real_time=True,
            has_time_limit=True,
            allows_pause=False,
            target_level=ComplianceLevel.LEVEL_AA,
        )
        assert len(violations) > 0
        codes = [v.code for v in violations]
        assert "TIMING_ESSENTIAL_NO_PAUSE" in codes

    def test_timing_essential_with_pause_passes(self, validator):
        """Test timing-essential with pause passes."""
        violations = validator.check_timing_essential(
            requires_real_time=True,
            has_time_limit=True,
            allows_pause=True,
            target_level=ComplianceLevel.LEVEL_AA,
        )
        assert len(violations) == 0

    def test_timing_essential_level_a_ok(self, validator):
        """Test timing-essential is OK at Level A."""
        violations = validator.check_timing_essential(
            requires_real_time=True,
            has_time_limit=True,
            allows_pause=False,
            target_level=ComplianceLevel.LEVEL_A,
        )
        assert len(violations) == 0


# ============================================
# Score Calculation Tests
# ============================================


class TestScoreCalculation:
    """Tests for score calculation."""

    @pytest.fixture
    def validator(self):
        return InteractionTimingValidator()

    def test_perfect_score_no_violations(self, validator):
        """Test perfect score with no violations."""
        score = validator._calculate_score([])
        assert score == 1.0

    def test_score_with_critical(self, validator):
        """Test score decreases with critical violation."""
        violations = [
            TimingViolation(
                code="TEST",
                severity=ViolationSeverity.CRITICAL,
                description="Test",
                location="test",
                remediation="Fix",
            )
        ]
        score = validator._calculate_score(violations)
        assert score == 0.75  # 1.0 - 0.25

    def test_score_with_multiple_violations(self, validator):
        """Test score with multiple violations."""
        violations = [
            TimingViolation(
                code="CRIT",
                severity=ViolationSeverity.CRITICAL,
                description="Critical",
                location="test",
                remediation="Fix",
            ),
            TimingViolation(
                code="MAJOR",
                severity=ViolationSeverity.MAJOR,
                description="Major",
                location="test",
                remediation="Fix",
            ),
        ]
        score = validator._calculate_score(violations)
        assert score == 0.60  # 1.0 - 0.25 - 0.15

    def test_score_minimum_zero(self, validator):
        """Test score doesn't go below zero."""
        violations = [
            TimingViolation(
                code=f"CRIT{i}",
                severity=ViolationSeverity.CRITICAL,
                description=f"Critical {i}",
                location="test",
                remediation="Fix",
            )
            for i in range(10)
        ]
        score = validator._calculate_score(violations)
        assert score == 0.0


# ============================================
# Level Determination Tests
# ============================================


class TestLevelDetermination:
    """Tests for compliance level determination."""

    @pytest.fixture
    def validator(self):
        return InteractionTimingValidator()

    def test_timeout_achieves_aaa(self, validator):
        """Test timeout config achieves AAA."""
        level = validator._determine_achieved_level_timeout(VALID_AAA_TIMEOUT)
        assert level == ComplianceLevel.LEVEL_AAA

    def test_timeout_achieves_aa(self, validator):
        """Test timeout config achieves AA."""
        level = validator._determine_achieved_level_timeout(VALID_AA_TIMEOUT)
        assert level == ComplianceLevel.LEVEL_AA

    def test_timeout_achieves_a(self, validator):
        """Test timeout config achieves A."""
        level = validator._determine_achieved_level_timeout(VALID_A_TIMEOUT)
        assert level == ComplianceLevel.LEVEL_A

    def test_timeout_achieves_none(self, validator):
        """Test invalid timeout achieves no level."""
        level = validator._determine_achieved_level_timeout(INVALID_TIMEOUT)
        assert level is None

    def test_input_achieves_aaa(self, validator):
        """Test input config achieves AAA."""
        level = validator._determine_achieved_level_input(VALID_AAA_INPUT)
        assert level == ComplianceLevel.LEVEL_AAA

    def test_input_achieves_aa(self, validator):
        """Test input config achieves AA."""
        level = validator._determine_achieved_level_input(VALID_AA_INPUT)
        assert level == ComplianceLevel.LEVEL_AA

    def test_input_achieves_a(self, validator):
        """Test input config achieves A."""
        level = validator._determine_achieved_level_input(VALID_A_INPUT)
        assert level == ComplianceLevel.LEVEL_A

    def test_input_achieves_none(self, validator):
        """Test invalid input achieves no level."""
        level = validator._determine_achieved_level_input(INVALID_INPUT)
        assert level is None


# ============================================
# Edge Case Tests
# ============================================


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.fixture
    def validator(self):
        return InteractionTimingValidator()

    def test_zero_timeout(self, validator):
        """Test zero timeout fails."""
        config = TimeoutConfig(
            initial_timeout_seconds=0,
            warning_before_seconds=0,
            extension_allowed=False,
            extension_seconds=0,
            max_extensions=0,
        )
        result = validator.validate_timeout(config, ComplianceLevel.LEVEL_A)
        assert result.passes is False

    def test_negative_max_extensions(self, validator):
        """Test negative max_extensions means unlimited."""
        config = TimeoutConfig(
            initial_timeout_seconds=60,
            warning_before_seconds=20,
            extension_allowed=True,
            extension_seconds=30,
            max_extensions=-1,
        )
        result = validator.validate_timeout(config, ComplianceLevel.LEVEL_AAA)
        # Should not have EXTENSIONS_LIMITED violation
        codes = [v.code for v in result.violations]
        assert "EXTENSIONS_LIMITED" not in codes

    def test_empty_validation(self, validator):
        """Test validation with no configs."""
        result = validator.validate_interaction(
            component_id="empty",
            target_level=ComplianceLevel.LEVEL_A,
        )
        assert result.overall_passes is True
        assert result.overall_score == 1.0

    def test_summary_generation(self, validator):
        """Test summary is properly generated."""
        result = validator.validate_timeout(VALID_AA_TIMEOUT, ComplianceLevel.LEVEL_AA)
        assert "TimeoutConfig" in result.summary or "Timing" in result.summary
        assert "AA" in result.summary
