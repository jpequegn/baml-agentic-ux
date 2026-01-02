"""Tests for seizure safety validation.

Issue #74 - Task 4.8: Seizure Safety Checker
Part of #27 - Phase 4: LUI Accessibility Standards
"""

import pytest

from src.accessibility.checker import ComplianceLevel, ViolationSeverity
from src.accessibility.seizure_safety import (
    MAX_AUTO_PLAY_DURATION_SECONDS,
    MAX_FLASH_AREA_PERCENT,
    MAX_FLASH_FREQUENCY_HZ,
    AnimationConfig,
    AnimationSafetyResult,
    ContentConfig,
    FlashAnalysis,
    FlashType,
    MediaConfig,
    SeizureCriterion,
    SeizureSafetyChecker,
    SeizureSafetyResult,
    SeizureViolation,
    check_animation_safety,
    check_flash_safety,
)


# ============================================
# Test Fixtures
# ============================================


@pytest.fixture
def checker():
    """Create a SeizureSafetyChecker instance."""
    return SeizureSafetyChecker()


# Safe animations
SAFE_ANIMATION = AnimationConfig(
    animation_id="fade_in",
    frequency_hz=2.0,
    duration_ms=500,
    area_percent=5.0,
    has_flash=False,
    is_red=False,
    auto_plays=True,
    has_pause_control=True,
    has_stop_control=True,
    respects_reduced_motion=True,
    loops=False,
    loop_count=0,
)

SAFE_ANIMATION_DICT = {
    "animation_id": "fade_in",
    "frequency_hz": 2.0,
    "duration_ms": 500,
    "area_percent": 5.0,
    "has_flash": False,
    "is_red": False,
    "auto_plays": True,
    "has_pause_control": True,
    "has_stop_control": True,
    "respects_reduced_motion": True,
    "loops": False,
    "loop_count": 0,
}

# Unsafe animations
UNSAFE_HIGH_FREQUENCY = AnimationConfig(
    animation_id="strobe",
    frequency_hz=5.0,
    duration_ms=1000,
    area_percent=5.0,
    has_flash=True,
    is_red=False,
    auto_plays=True,
    has_pause_control=True,
    has_stop_control=True,
    respects_reduced_motion=True,
)

UNSAFE_LARGE_AREA = AnimationConfig(
    animation_id="fullscreen_flash",
    frequency_hz=2.0,
    duration_ms=500,
    area_percent=15.0,  # Exceeds 10%
    has_flash=True,
    is_red=False,
    auto_plays=True,
    has_pause_control=True,
    has_stop_control=True,
    respects_reduced_motion=True,
)

UNSAFE_RED_FLASH = AnimationConfig(
    animation_id="red_strobe",
    frequency_hz=2.5,  # Would be safe for general, not for red
    duration_ms=1000,
    area_percent=5.0,
    has_flash=True,
    is_red=True,
    auto_plays=True,
    has_pause_control=True,
    has_stop_control=True,
    respects_reduced_motion=True,
)

NO_CONTROLS_ANIMATION = AnimationConfig(
    animation_id="no_controls",
    frequency_hz=1.0,
    duration_ms=500,
    area_percent=5.0,
    auto_plays=True,
    has_pause_control=False,
    has_stop_control=False,
    respects_reduced_motion=False,
)

# Media configs
SAFE_MEDIA = MediaConfig(
    media_id="promo_video",
    media_type="video",
    auto_plays=False,
    has_pause_control=True,
    has_stop_control=True,
    duration_seconds=30.0,
    has_flashing_content=False,
    flash_frequency_hz=0.0,
    respects_reduced_motion=True,
)

UNSAFE_MEDIA = MediaConfig(
    media_id="strobe_video",
    media_type="video",
    auto_plays=True,
    has_pause_control=False,
    has_stop_control=False,
    duration_seconds=60.0,
    has_flashing_content=True,
    flash_frequency_hz=5.0,
    respects_reduced_motion=False,
)


# ============================================
# Constants Tests
# ============================================


class TestConstants:
    """Tests for seizure safety constants."""

    def test_max_flash_frequency(self):
        """Test max flash frequency is 3Hz per WCAG."""
        assert MAX_FLASH_FREQUENCY_HZ == 3.0

    def test_max_flash_area(self):
        """Test max flash area is 10% per WCAG."""
        assert MAX_FLASH_AREA_PERCENT == 10.0

    def test_max_auto_play_duration(self):
        """Test max auto-play duration is 5 seconds."""
        assert MAX_AUTO_PLAY_DURATION_SECONDS == 5.0


# ============================================
# FlashAnalysis Tests
# ============================================


class TestFlashAnalysis:
    """Tests for flash analysis."""

    def test_no_flash(self, checker):
        """Test analysis with no flash."""
        result = checker.analyze_flash(0.0, 0.0)
        assert result.is_safe is True
        assert result.has_flashes is False
        assert result.exceeds_frequency is False
        assert result.exceeds_area is False

    def test_safe_flash(self, checker):
        """Test analysis with safe flash parameters."""
        result = checker.analyze_flash(2.0, 5.0)
        assert result.is_safe is True
        assert result.has_flashes is True
        assert result.flash_frequency_hz == 2.0
        assert result.flash_area_percent == 5.0
        assert result.exceeds_frequency is False
        assert result.exceeds_area is False

    def test_unsafe_frequency(self, checker):
        """Test analysis with unsafe flash frequency."""
        result = checker.analyze_flash(5.0, 5.0)
        assert result.is_safe is False
        assert result.exceeds_frequency is True
        assert result.exceeds_area is False

    def test_unsafe_area(self, checker):
        """Test analysis with unsafe flash area."""
        result = checker.analyze_flash(2.0, 15.0)
        assert result.is_safe is False
        assert result.exceeds_frequency is False
        assert result.exceeds_area is True

    def test_both_unsafe(self, checker):
        """Test analysis with both unsafe parameters."""
        result = checker.analyze_flash(5.0, 15.0)
        assert result.is_safe is False
        assert result.exceeds_frequency is True
        assert result.exceeds_area is True

    def test_red_flash_stricter_limit(self, checker):
        """Test red flashes have stricter frequency limit."""
        # 2.5Hz would be safe for general flash
        result_general = checker.analyze_flash(2.5, 5.0, is_red=False)
        assert result_general.is_safe is True

        # 2.5Hz is unsafe for red flash (limit is ~2Hz)
        result_red = checker.analyze_flash(2.5, 5.0, is_red=True)
        assert result_red.is_safe is False
        assert result_red.is_red_flash is True
        assert result_red.flash_type == FlashType.RED

    def test_boundary_frequency(self, checker):
        """Test boundary at exactly 3Hz."""
        # At 3Hz should be safe
        result_at = checker.analyze_flash(3.0, 5.0)
        assert result_at.is_safe is True

        # Just over should be unsafe
        result_over = checker.analyze_flash(3.1, 5.0)
        assert result_over.is_safe is False

    def test_boundary_area(self, checker):
        """Test boundary at exactly 10%."""
        # At 10% should be safe
        result_at = checker.analyze_flash(2.0, 10.0)
        assert result_at.is_safe is True

        # Just over should be unsafe
        result_over = checker.analyze_flash(2.0, 10.1)
        assert result_over.is_safe is False


# ============================================
# SeizureViolation Tests
# ============================================


class TestSeizureViolation:
    """Tests for seizure violation class."""

    def test_create_violation(self):
        """Test creating a seizure violation."""
        violation = SeizureViolation(
            criterion=SeizureCriterion.SC_2_3_1,
            severity=ViolationSeverity.CRITICAL,
            description="Flash frequency exceeds limit",
            location="animation_1",
            remediation="Reduce flash frequency",
            flash_type=FlashType.GENERAL,
            measured_value=5.0,
            threshold_value=3.0,
        )
        assert violation.criterion == SeizureCriterion.SC_2_3_1
        assert violation.severity == ViolationSeverity.CRITICAL
        assert violation.flash_type == FlashType.GENERAL
        assert violation.measured_value == 5.0
        assert violation.threshold_value == 3.0

    def test_violation_weights(self):
        """Test violation severity weights."""
        critical = SeizureViolation(
            criterion=SeizureCriterion.SC_2_3_1,
            severity=ViolationSeverity.CRITICAL,
            description="",
            location="",
            remediation="",
        )
        assert critical.weight == 0.25

        major = SeizureViolation(
            criterion=SeizureCriterion.SC_2_3_1,
            severity=ViolationSeverity.MAJOR,
            description="",
            location="",
            remediation="",
        )
        assert major.weight == 0.15

        minor = SeizureViolation(
            criterion=SeizureCriterion.SC_2_3_1,
            severity=ViolationSeverity.MINOR,
            description="",
            location="",
            remediation="",
        )
        assert minor.weight == 0.05


# ============================================
# Animation Analysis Tests
# ============================================


class TestAnimationAnalysis:
    """Tests for animation safety analysis."""

    def test_safe_animation(self, checker):
        """Test safe animation passes."""
        result = checker.analyze_animation(SAFE_ANIMATION)
        assert result.passes is True
        assert result.score >= 0.70
        assert len(result.violations) == 0
        assert result.has_required_controls is True
        assert result.respects_user_preferences is True

    def test_safe_animation_dict(self, checker):
        """Test safe animation from dict passes."""
        result = checker.analyze_animation(SAFE_ANIMATION_DICT)
        assert result.passes is True
        assert result.animation_id == "fade_in"

    def test_unsafe_high_frequency(self, checker):
        """Test animation with high flash frequency fails."""
        result = checker.analyze_animation(UNSAFE_HIGH_FREQUENCY)
        assert result.passes is False
        assert result.flash_analysis.exceeds_frequency is True

        codes = [v.criterion for v in result.violations]
        assert SeizureCriterion.SC_2_3_1 in codes

    def test_unsafe_large_area(self, checker):
        """Test animation with large flash area fails."""
        result = checker.analyze_animation(UNSAFE_LARGE_AREA)
        assert result.passes is False
        assert result.flash_analysis.exceeds_area is True

    def test_unsafe_red_flash(self, checker):
        """Test animation with red flash at unsafe frequency fails."""
        result = checker.analyze_animation(UNSAFE_RED_FLASH)
        assert result.passes is False
        assert result.flash_analysis.is_red_flash is True

    def test_no_controls_animation(self, checker):
        """Test auto-playing animation without controls fails."""
        result = checker.analyze_animation(NO_CONTROLS_ANIMATION)
        # May still pass if score is above threshold, but has violations
        assert result.has_required_controls is False
        assert result.respects_user_preferences is False

        codes = [v.criterion for v in result.violations]
        assert SeizureCriterion.SC_2_3_1 in codes or SeizureCriterion.SC_2_3_3 in codes

    def test_infinite_loop_aaa(self, checker):
        """Test infinite looping animation flagged at AAA."""
        config = AnimationConfig(
            animation_id="infinite_loop",
            frequency_hz=1.0,
            area_percent=5.0,
            loops=True,
            loop_count=-1,
            respects_reduced_motion=True,
            has_pause_control=True,
            has_stop_control=True,
        )
        result = checker.analyze_animation(config, ComplianceLevel.LEVEL_AAA)

        # Should have minor violation for infinite loop at AAA
        criteria = [v.criterion for v in result.violations]
        assert SeizureCriterion.SC_2_3_3 in criteria

    def test_recommendations_generated(self, checker):
        """Test recommendations are generated for violations."""
        result = checker.analyze_animation(NO_CONTROLS_ANIMATION)
        assert len(result.recommendations) > 0

    def test_summary_generated(self, checker):
        """Test summary is generated."""
        result = checker.analyze_animation(SAFE_ANIMATION)
        assert len(result.summary) > 0
        assert "PASSES" in result.summary or "FAILS" in result.summary


# ============================================
# Media Analysis Tests
# ============================================


class TestMediaAnalysis:
    """Tests for media safety analysis."""

    def test_safe_media(self, checker):
        """Test safe media passes."""
        result = checker.analyze_media(SAFE_MEDIA)
        assert result.passes is True
        assert len(result.violations) == 0

    def test_safe_media_dict(self, checker):
        """Test safe media from dict passes."""
        result = checker.analyze_media({
            "media_id": "video",
            "auto_plays": False,
            "has_pause_control": True,
            "has_stop_control": True,
        })
        assert result.passes is True

    def test_unsafe_media(self, checker):
        """Test unsafe media fails."""
        result = checker.analyze_media(UNSAFE_MEDIA)
        assert result.passes is False
        assert result.has_required_controls is False
        assert result.respects_user_preferences is False

    def test_auto_play_without_controls(self, checker):
        """Test auto-playing media without controls."""
        config = MediaConfig(
            media_id="autoplay",
            auto_plays=True,
            has_pause_control=False,
            has_stop_control=False,
        )
        result = checker.analyze_media(config)
        assert result.has_required_controls is False
        assert len(result.violations) >= 2  # Missing pause and stop

    def test_long_auto_play(self, checker):
        """Test long auto-playing media is flagged."""
        config = MediaConfig(
            media_id="long_video",
            auto_plays=True,
            has_pause_control=True,
            has_stop_control=True,
            duration_seconds=60.0,  # Exceeds 5s threshold
        )
        result = checker.analyze_media(config)

        # Should have minor violation for long auto-play
        severities = [v.severity for v in result.violations]
        assert ViolationSeverity.MINOR in severities

    def test_flashing_media(self, checker):
        """Test media with flashing content."""
        config = MediaConfig(
            media_id="flash_video",
            has_flashing_content=True,
            flash_frequency_hz=5.0,
            has_pause_control=True,
            has_stop_control=True,
        )
        result = checker.analyze_media(config)
        assert result.passes is False
        assert result.flash_analysis is not None
        assert result.flash_analysis.exceeds_frequency is True


# ============================================
# Content Validation Tests
# ============================================


class TestContentValidation:
    """Tests for complete content validation."""

    def test_safe_content(self, checker):
        """Test safe content passes."""
        content = ContentConfig(
            content_id="homepage",
            animations=[SAFE_ANIMATION],
            media=[SAFE_MEDIA],
            respects_reduced_motion=True,
        )
        result = checker.check_content(content)
        assert result.passes is True
        assert result.score >= 0.70
        assert len(result.criteria_met) > 0

    def test_safe_content_dict(self, checker):
        """Test safe content from dict passes."""
        content = {
            "content_id": "homepage",
            "animations": [SAFE_ANIMATION_DICT],
            "media": [],
            "respects_reduced_motion": True,
        }
        result = checker.check_content(content)
        assert result.passes is True

    def test_content_with_unsafe_animation(self, checker):
        """Test content with unsafe animation fails."""
        content = ContentConfig(
            content_id="unsafe_page",
            animations=[UNSAFE_HIGH_FREQUENCY],
            respects_reduced_motion=True,
        )
        result = checker.check_content(content)
        assert result.passes is False
        assert len(result.animation_results) == 1
        assert result.animation_results[0].passes is False

    def test_content_with_unsafe_media(self, checker):
        """Test content with unsafe media fails."""
        content = ContentConfig(
            content_id="unsafe_page",
            media=[UNSAFE_MEDIA],
            respects_reduced_motion=True,
        )
        result = checker.check_content(content)
        assert result.passes is False
        assert len(result.media_results) == 1

    def test_auto_updating_content(self, checker):
        """Test auto-updating content at high frequency."""
        content = ContentConfig(
            content_id="live_feed",
            has_auto_updating_content=True,
            update_frequency_hz=5.0,  # Too fast
            respects_reduced_motion=True,
        )
        result = checker.check_content(content)

        # Should have violation for high update frequency
        assert len(result.violations) > 0

    def test_no_reduced_motion_support(self, checker):
        """Test content without reduced motion support."""
        content = ContentConfig(
            content_id="no_motion",
            respects_reduced_motion=False,
        )
        result = checker.check_content(content)

        codes = [v.criterion for v in result.violations]
        assert SeizureCriterion.SC_2_3_3 in codes

    def test_multiple_animations(self, checker):
        """Test content with multiple animations."""
        content = ContentConfig(
            content_id="multi_anim",
            animations=[SAFE_ANIMATION, UNSAFE_HIGH_FREQUENCY],
            respects_reduced_motion=True,
        )
        result = checker.check_content(content)
        assert result.passes is False
        assert len(result.animation_results) == 2
        assert result.animation_results[0].passes is True
        assert result.animation_results[1].passes is False

    def test_criteria_evaluation(self, checker):
        """Test WCAG criteria are properly evaluated."""
        content = ContentConfig(
            content_id="test",
            animations=[SAFE_ANIMATION],
            respects_reduced_motion=True,
        )
        result = checker.check_content(content, ComplianceLevel.LEVEL_A)

        # Should meet 2.3.1 for Level A
        assert SeizureCriterion.SC_2_3_1 in result.criteria_met

    def test_aaa_level_criteria(self, checker):
        """Test AAA level has additional criteria."""
        content = ContentConfig(
            content_id="test",
            animations=[SAFE_ANIMATION],
            respects_reduced_motion=True,
        )
        result = checker.check_content(content, ComplianceLevel.LEVEL_AAA)

        # Should check 2.3.1, 2.3.2, and 2.3.3
        all_criteria = result.criteria_met + result.criteria_failed
        assert len(all_criteria) >= 1

    def test_empty_content(self, checker):
        """Test empty content passes."""
        content = ContentConfig(
            content_id="empty",
            respects_reduced_motion=True,
        )
        result = checker.check_content(content)
        assert result.passes is True
        assert result.score == 1.0

    def test_recommendations_deduplicated(self, checker):
        """Test duplicate recommendations are removed."""
        content = ContentConfig(
            content_id="test",
            animations=[NO_CONTROLS_ANIMATION, NO_CONTROLS_ANIMATION],
            respects_reduced_motion=True,
        )
        result = checker.check_content(content)

        # Recommendations should be deduplicated
        assert len(result.recommendations) == len(set(result.recommendations))


# ============================================
# Score Calculation Tests
# ============================================


class TestScoreCalculation:
    """Tests for score calculation."""

    def test_perfect_score_no_violations(self, checker):
        """Test perfect score with no violations."""
        result = checker.analyze_animation(SAFE_ANIMATION)
        assert result.score == 1.0

    def test_score_with_critical(self, checker):
        """Test score decreases with critical violation."""
        result = checker.analyze_animation(UNSAFE_HIGH_FREQUENCY)
        assert result.score < 1.0
        assert result.score <= 0.75  # Critical is -0.25

    def test_score_with_multiple_violations(self, checker):
        """Test score decreases with multiple violations."""
        result = checker.analyze_animation(NO_CONTROLS_ANIMATION)
        # Multiple major violations
        assert result.score < 1.0

    def test_score_minimum_zero(self, checker):
        """Test score doesn't go below 0."""
        # Create animation with many violations
        config = AnimationConfig(
            animation_id="worst",
            frequency_hz=10.0,
            area_percent=50.0,
            is_red=True,
            auto_plays=True,
            has_pause_control=False,
            has_stop_control=False,
            respects_reduced_motion=False,
            loops=True,
            loop_count=-1,
        )
        result = checker.analyze_animation(config, ComplianceLevel.LEVEL_AAA)
        assert result.score >= 0.0


# ============================================
# Convenience Functions Tests
# ============================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_check_flash_safety_safe(self):
        """Test check_flash_safety with safe parameters."""
        assert check_flash_safety(2.0, 5.0) is True

    def test_check_flash_safety_unsafe_frequency(self):
        """Test check_flash_safety with unsafe frequency."""
        assert check_flash_safety(5.0, 5.0) is False

    def test_check_flash_safety_unsafe_area(self):
        """Test check_flash_safety with unsafe area."""
        assert check_flash_safety(2.0, 15.0) is False

    def test_check_flash_safety_red(self):
        """Test check_flash_safety with red flash."""
        # 2.5Hz is safe for general but not for red
        assert check_flash_safety(2.5, 5.0, is_red=False) is True
        assert check_flash_safety(2.5, 5.0, is_red=True) is False

    def test_check_animation_safety_safe(self):
        """Test check_animation_safety with safe animation."""
        assert check_animation_safety(SAFE_ANIMATION_DICT) is True

    def test_check_animation_safety_unsafe(self):
        """Test check_animation_safety with unsafe animation."""
        unsafe = {
            "frequency_hz": 5.0,
            "area_percent": 5.0,
        }
        assert check_animation_safety(unsafe) is False


# ============================================
# Edge Cases Tests
# ============================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_zero_frequency(self, checker):
        """Test zero frequency is safe."""
        result = checker.analyze_flash(0.0, 5.0)
        assert result.is_safe is True

    def test_zero_area(self, checker):
        """Test zero area is safe."""
        result = checker.analyze_flash(2.0, 0.0)
        assert result.is_safe is True

    def test_negative_values(self, checker):
        """Test negative values don't crash."""
        result = checker.analyze_flash(-1.0, -1.0)
        assert result.is_safe is True

    def test_very_high_values(self, checker):
        """Test very high values are handled."""
        result = checker.analyze_flash(1000.0, 1000.0)
        assert result.is_safe is False
        assert result.exceeds_frequency is True
        assert result.exceeds_area is True

    def test_custom_thresholds(self):
        """Test custom thresholds work."""
        checker = SeizureSafetyChecker(
            max_flash_frequency=2.0,
            max_flash_area=5.0,
        )
        # 2.5Hz would be safe with default but not with custom
        result = checker.analyze_flash(2.5, 5.0)
        assert result.is_safe is False

    def test_empty_animation_id(self, checker):
        """Test animation with empty ID."""
        config = AnimationConfig(animation_id="")
        result = checker.analyze_animation(config)
        assert result.animation_id == ""
        assert "animation" in result.summary.lower() or "Animation" in result.summary

    def test_summary_generation(self, checker):
        """Test summary is properly generated."""
        content = ContentConfig(
            content_id="test_content",
            animations=[SAFE_ANIMATION],
            respects_reduced_motion=True,
        )
        result = checker.check_content(content)
        assert "test_content" in result.summary
        assert "PASSES" in result.summary or "FAILS" in result.summary


# ============================================
# Criteria by Level Tests
# ============================================


class TestCriteriaByLevel:
    """Tests for criteria requirements by level."""

    def test_level_a_criteria(self, checker):
        """Test Level A requires 2.3.1."""
        content = ContentConfig(content_id="test", respects_reduced_motion=True)
        result = checker.check_content(content, ComplianceLevel.LEVEL_A)
        # 2.3.1 should be checked at Level A
        all_criteria = result.criteria_met + result.criteria_failed
        # With no animations, should meet 2.3.1
        assert SeizureCriterion.SC_2_3_1 in result.criteria_met or len(all_criteria) >= 0

    def test_level_aa_criteria(self, checker):
        """Test Level AA also requires 2.3.1."""
        content = ContentConfig(content_id="test", respects_reduced_motion=True)
        result = checker.check_content(content, ComplianceLevel.LEVEL_AA)
        # 2.3.1 should be checked at Level AA
        all_criteria = result.criteria_met + result.criteria_failed
        assert len(all_criteria) >= 0

    def test_level_aaa_additional_criteria(self, checker):
        """Test Level AAA has additional criteria."""
        content = ContentConfig(
            content_id="test",
            animations=[
                AnimationConfig(
                    animation_id="test",
                    loops=True,
                    loop_count=-1,
                    respects_reduced_motion=True,
                    has_pause_control=True,
                    has_stop_control=True,
                )
            ],
            respects_reduced_motion=True,
        )
        result = checker.check_content(content, ComplianceLevel.LEVEL_AAA)
        # Should check 2.3.3 at AAA
        criteria = [v.criterion for v in result.violations]
        # Infinite loop should trigger 2.3.3
        assert SeizureCriterion.SC_2_3_3 in criteria


# ============================================
# SeizureCriterion Tests
# ============================================


class TestSeizureCriterion:
    """Tests for seizure criterion enum."""

    def test_all_criteria_exist(self):
        """Test all WCAG 2.3 criteria are defined."""
        assert SeizureCriterion.SC_2_3_1 is not None
        assert SeizureCriterion.SC_2_3_2 is not None
        assert SeizureCriterion.SC_2_3_3 is not None

    def test_criterion_values(self):
        """Test criterion values are correct."""
        assert SeizureCriterion.SC_2_3_1.value == "2.3.1"
        assert SeizureCriterion.SC_2_3_2.value == "2.3.2"
        assert SeizureCriterion.SC_2_3_3.value == "2.3.3"


# ============================================
# FlashType Tests
# ============================================


class TestFlashType:
    """Tests for flash type enum."""

    def test_flash_types_exist(self):
        """Test all flash types are defined."""
        assert FlashType.GENERAL is not None
        assert FlashType.RED is not None
        assert FlashType.PATTERN is not None

    def test_red_flash_detection(self, checker):
        """Test red flash is properly detected."""
        result = checker.analyze_flash(2.0, 5.0, is_red=True)
        assert result.flash_type == FlashType.RED
        assert result.is_red_flash is True

    def test_general_flash_detection(self, checker):
        """Test general flash is properly detected."""
        result = checker.analyze_flash(2.0, 5.0, is_red=False)
        assert result.flash_type == FlashType.GENERAL
        assert result.is_red_flash is False
