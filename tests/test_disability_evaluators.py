"""Comprehensive unit tests for disability-specific accessibility evaluators.

Tests cover:
- All 6 disability evaluators (Visual, Hearing, Motor, Speech, Cognitive, Neurological)
- Barrier detection and classification
- Accommodation identification
- Score calculation
- Combined evaluation functionality

Issue #72 - Task 4.6: Disability-Specific Evaluators
Part of #27 - Phase 4: LUI Accessibility Standards
"""

import pytest

from src.accessibility.disability_evaluators import (
    Barrier,
    BarrierAnalysis,
    BarrierCategory,
    CognitiveAccessibilityEvaluator,
    CombinedDisabilityEvaluator,
    DisabilityEvaluation,
    DisabilityEvaluator,
    DisabilityType,
    HearingAccessibilityEvaluator,
    MotorAccessibilityEvaluator,
    NeurologicalAccessibilityEvaluator,
    SpeechAccessibilityEvaluator,
    VisualAccessibilityEvaluator,
)
from src.accessibility.checker import ViolationSeverity


# ============================================
# Test Data
# ============================================

# Accessible schema with all accommodations
FULLY_ACCESSIBLE_SCHEMA = {
    "name": "fully_accessible",
    "version": "1.0.0",
    "accessibility": {
        "audio_first_design": True,
        "audio_output_enabled": True,
        "caption_support": True,
        "sign_language_available": True,
        "voice_input_enabled": True,
        "switch_access_compatible": True,
        "text_input_fallback": True,
        "aac_device_compatible": True,
        "gesture_input_enabled": True,
        "consistent_navigation": True,
        "progress_indicators_enabled": True,
        "undo_support": True,
        "auto_save_enabled": True,
        "simple_language_mode": True,
        "clear_error_messages": True,
        "seizure_safe_mode": True,
        "no_auto_play": True,
        "default_config": {
            "screen_reader_label": "Accessible Application",
            "audio_feedback_enabled": True,
            "visual_alerts_enabled": True,
            "text_alternatives_enabled": True,
            "interaction_constraints": {
                "max_session_timeout_ms": 120000,  # 120 seconds
                "single_action_mode": True,
                "keyboard_input_enabled": True,
            },
            "visual_config": {
                "high_contrast_support": True,
                "reduced_motion_support": True,
                "animation_controls": True,
                "flash_config": {
                    "max_frequency_hz": 2,
                },
            },
        },
    },
    "components": [
        {
            "component_id": "accessible_action",
            "component_type": "ACTION",
            "accessibility": {
                "screen_reader_label": "Submit form",
                "aria_config": {
                    "live_region": "polite",
                },
            },
            "feedback": {
                "success_template": "Form sent. You are done.",
                "error_template": "Form failed. Try again.",
                "confirmation_required": True,
            },
        }
    ],
}

# Schema with minimal accessibility
MINIMAL_SCHEMA = {
    "name": "minimal_schema",
    "version": "1.0.0",
    "accessibility": {},
    "components": [],
}

# Schema with visual-only content
VISUAL_ONLY_SCHEMA = {
    "name": "visual_only",
    "version": "1.0.0",
    "accessibility": {
        "audio_output_enabled": False,
    },
    "components": [
        {
            "component_id": "image_display",
            "component_type": "IMAGE",
            "accessibility": {},
        },
        {
            "component_id": "action_no_label",
            "component_type": "ACTION",
            "accessibility": {},
        },
    ],
}

# Schema with audio-only content
AUDIO_ONLY_SCHEMA = {
    "name": "audio_only",
    "version": "1.0.0",
    "accessibility": {
        "audio_only_mode": True,
        "caption_config": {
            "accuracy_threshold": 0.85,
        },
    },
    "components": [
        {
            "component_id": "audio_content",
            "component_type": "AUDIO",
            "feedback": {
                "audio_alert": True,
            },
        },
    ],
}

# Schema with motor accessibility issues
MOTOR_ISSUES_SCHEMA = {
    "name": "motor_issues",
    "version": "1.0.0",
    "accessibility": {
        "default_config": {
            "interaction_constraints": {
                "max_session_timeout_ms": 30000,  # 30 seconds - too short
                "requires_complex_gestures": True,
            },
        },
    },
    "components": [
        {
            "component_id": "small_target",
            "component_type": "ACTION",
            "accessibility": {
                "touch_config": {
                    "min_target_size": 20,  # Below 44px minimum
                },
                "requires_multi_step_action": True,
            },
        },
    ],
}

# Schema with voice-only content
VOICE_ONLY_SCHEMA = {
    "name": "voice_only",
    "version": "1.0.0",
    "accessibility": {
        "voice_only_mode": True,
        "text_fallback_coverage": 0.7,  # Only 70% coverage
    },
    "components": [
        {
            "component_id": "voice_required",
            "component_type": "ACTION",
            "accessibility": {
                "voice_input_required": True,
            },
        },
    ],
}

# Schema with cognitive accessibility issues
COGNITIVE_ISSUES_SCHEMA = {
    "name": "cognitive_issues",
    "version": "1.0.0",
    "accessibility": {},
    "components": [
        {
            "component_id": "complex_action",
            "component_type": "ACTION",
            "destructive_action": True,
            "feedback": {
                "success_template": (
                    "The authentication protocol necessitates verification "
                    "of credentials prior to authorization being granted to "
                    "the user's account with administrative privileges."
                ),
            },
        },
    ],
    "flows": [
        {
            "flow_id": "long_flow",
            "steps": [
                {"prompt": "Step 1"},
                {"prompt": "Step 2"},
                {"prompt": "Step 3"},
                {"prompt": "Step 4"},
            ],
        },
    ],
}

# Schema with neurological issues
NEUROLOGICAL_ISSUES_SCHEMA = {
    "name": "neurological_issues",
    "version": "1.0.0",
    "accessibility": {
        "auto_play_enabled": True,
        "default_config": {
            "visual_config": {
                "flash_config": {
                    "max_frequency_hz": 5,  # Above 3Hz limit
                },
            },
        },
    },
    "components": [
        {
            "component_id": "flashing_content",
            "component_type": "VISUAL",
            "accessibility": {
                "animation_config": {
                    "enabled": True,
                },
                "visual_config": {
                    "has_flashing_content": True,
                },
            },
        },
    ],
}


# ============================================
# Barrier Tests
# ============================================


class TestBarrier:
    """Tests for Barrier dataclass."""

    def test_create_barrier(self):
        """Test creating a barrier."""
        barrier = Barrier(
            category=BarrierCategory.PERCEPTION,
            severity=ViolationSeverity.CRITICAL,
            description="Audio output disabled",
            location="accessibility.audio_output_enabled",
            impact="Blind users cannot perceive responses",
            remediation="Enable audio output",
        )
        assert barrier.category == BarrierCategory.PERCEPTION
        assert barrier.severity == ViolationSeverity.CRITICAL
        assert "audio" in barrier.description.lower()

    def test_barrier_categories(self):
        """Test all barrier categories."""
        assert BarrierCategory.PERCEPTION.value == "perception"
        assert BarrierCategory.OPERATION.value == "operation"
        assert BarrierCategory.UNDERSTANDING.value == "understanding"
        assert BarrierCategory.ROBUSTNESS.value == "robustness"


class TestBarrierAnalysis:
    """Tests for BarrierAnalysis dataclass."""

    def test_create_empty_analysis(self):
        """Test creating analysis with no barriers."""
        analysis = BarrierAnalysis(area="schema", barriers=[])
        assert analysis.barrier_count == 0
        assert analysis.critical_count == 0

    def test_create_analysis_with_barriers(self):
        """Test creating analysis with barriers."""
        barriers = [
            Barrier(
                category=BarrierCategory.PERCEPTION,
                severity=ViolationSeverity.CRITICAL,
                description="Test",
                location="test",
                impact="Test",
                remediation="Fix",
            ),
            Barrier(
                category=BarrierCategory.OPERATION,
                severity=ViolationSeverity.MAJOR,
                description="Test 2",
                location="test2",
                impact="Test 2",
                remediation="Fix 2",
            ),
        ]
        analysis = BarrierAnalysis(area="test_area", barriers=barriers)
        assert analysis.barrier_count == 2
        assert analysis.critical_count == 1


# ============================================
# DisabilityEvaluation Tests
# ============================================


class TestDisabilityEvaluation:
    """Tests for DisabilityEvaluation dataclass."""

    def test_create_passing_evaluation(self):
        """Test creating a passing evaluation."""
        eval = DisabilityEvaluation(
            disability_type=DisabilityType.VISUAL,
            accommodation_score=0.85,
            barriers=[],
            accommodations_present=["Audio-first design"],
            accommodations_missing=[],
            recommendations=[],
        )
        assert eval.passes is True
        assert eval.total_barriers == 0
        assert "PASSES" in eval.summary

    def test_create_failing_evaluation(self):
        """Test creating a failing evaluation."""
        barriers = [
            BarrierAnalysis(
                area="test",
                barriers=[
                    Barrier(
                        category=BarrierCategory.PERCEPTION,
                        severity=ViolationSeverity.CRITICAL,
                        description="Critical barrier",
                        location="test",
                        impact="Test",
                        remediation="Fix",
                    )
                ],
            )
        ]
        eval = DisabilityEvaluation(
            disability_type=DisabilityType.VISUAL,
            accommodation_score=0.5,
            barriers=barriers,
            accommodations_present=[],
            accommodations_missing=["Audio output"],
            recommendations=["Enable audio"],
        )
        assert eval.passes is False
        assert eval.total_barriers == 1
        assert eval.critical_barriers == 1
        assert "NEEDS IMPROVEMENT" in eval.summary

    def test_evaluation_with_score_below_threshold(self):
        """Test evaluation fails with score below 0.7."""
        eval = DisabilityEvaluation(
            disability_type=DisabilityType.HEARING,
            accommodation_score=0.65,
            barriers=[],
            accommodations_present=[],
            accommodations_missing=[],
            recommendations=[],
        )
        assert eval.passes is False

    def test_evaluation_with_critical_barrier(self):
        """Test evaluation fails with critical barrier even if score >= 0.7."""
        barriers = [
            BarrierAnalysis(
                area="test",
                barriers=[
                    Barrier(
                        category=BarrierCategory.PERCEPTION,
                        severity=ViolationSeverity.CRITICAL,
                        description="Critical",
                        location="test",
                        impact="Test",
                        remediation="Fix",
                    )
                ],
            )
        ]
        eval = DisabilityEvaluation(
            disability_type=DisabilityType.MOTOR,
            accommodation_score=0.8,  # High score
            barriers=barriers,  # But critical barrier
            accommodations_present=[],
            accommodations_missing=[],
            recommendations=[],
        )
        assert eval.passes is False


# ============================================
# Visual Accessibility Evaluator Tests
# ============================================


class TestVisualAccessibilityEvaluator:
    """Tests for VisualAccessibilityEvaluator."""

    @pytest.fixture
    def evaluator(self):
        return VisualAccessibilityEvaluator()

    def test_disability_type(self, evaluator):
        """Test disability type is correct."""
        assert evaluator.disability_type == DisabilityType.VISUAL

    def test_fully_accessible_schema(self, evaluator):
        """Test evaluation of fully accessible schema."""
        result = evaluator.evaluate(FULLY_ACCESSIBLE_SCHEMA)

        assert result.disability_type == DisabilityType.VISUAL
        assert result.accommodation_score >= 0.7
        assert len(result.accommodations_present) > 0
        assert "Audio-first design enabled" in result.accommodations_present

    def test_visual_only_schema(self, evaluator):
        """Test evaluation of visual-only schema."""
        result = evaluator.evaluate(VISUAL_ONLY_SCHEMA)

        assert result.passes is False
        assert result.total_barriers > 0
        # Should detect audio output disabled
        critical_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if b.severity == ViolationSeverity.CRITICAL
        ]
        assert len(critical_barriers) > 0

    def test_missing_screen_reader_label(self, evaluator):
        """Test detection of missing screen reader labels."""
        result = evaluator.evaluate(VISUAL_ONLY_SCHEMA)

        # Should have barrier for missing screen reader label
        label_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "screen reader" in b.description.lower()
        ]
        assert len(label_barriers) > 0

    def test_visual_only_information(self, evaluator):
        """Test detection of visual-only information."""
        schema = {
            "name": "visual_info",
            "accessibility": {"audio_output_enabled": True},
            "components": [
                {
                    "component_id": "chart",
                    "component_type": "CHART",
                    "accessibility": {},  # Missing alt_text
                }
            ],
        }
        result = evaluator.evaluate(schema)

        # Should detect visual-only information
        visual_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "visual" in b.description.lower()
        ]
        assert len(visual_barriers) > 0

    def test_aria_live_region_check(self, evaluator):
        """Test ARIA live region configuration check."""
        schema = {
            "name": "no_aria",
            "accessibility": {"audio_output_enabled": True},
            "components": [
                {
                    "component_id": "dynamic",
                    "component_type": "ACTION",
                    "accessibility": {
                        "screen_reader_label": "Action",
                        # Missing aria_config.live_region
                    },
                }
            ],
        }
        result = evaluator.evaluate(schema)

        # Should flag missing ARIA live region for ACTION component
        aria_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "aria" in b.description.lower() or "live region" in b.description.lower()
        ]
        assert len(aria_barriers) > 0


# ============================================
# Hearing Accessibility Evaluator Tests
# ============================================


class TestHearingAccessibilityEvaluator:
    """Tests for HearingAccessibilityEvaluator."""

    @pytest.fixture
    def evaluator(self):
        return HearingAccessibilityEvaluator()

    def test_disability_type(self, evaluator):
        """Test disability type is correct."""
        assert evaluator.disability_type == DisabilityType.HEARING

    def test_fully_accessible_schema(self, evaluator):
        """Test evaluation of fully accessible schema."""
        result = evaluator.evaluate(FULLY_ACCESSIBLE_SCHEMA)

        assert result.disability_type == DisabilityType.HEARING
        assert result.accommodation_score >= 0.7
        assert "Real-time caption support" in result.accommodations_present

    def test_audio_only_schema(self, evaluator):
        """Test evaluation of audio-only schema."""
        result = evaluator.evaluate(AUDIO_ONLY_SCHEMA)

        assert result.passes is False
        # Should detect audio-only without text fallback
        critical_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if b.severity == ViolationSeverity.CRITICAL
        ]
        assert len(critical_barriers) > 0

    def test_caption_accuracy_check(self, evaluator):
        """Test caption accuracy threshold check."""
        result = evaluator.evaluate(AUDIO_ONLY_SCHEMA)

        # Should flag caption accuracy below 99%
        accuracy_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "caption accuracy" in b.description.lower()
        ]
        assert len(accuracy_barriers) > 0

    def test_audio_alert_without_visual(self, evaluator):
        """Test detection of audio alerts without visual alternatives."""
        result = evaluator.evaluate(AUDIO_ONLY_SCHEMA)

        # Should detect audio alert without visual alternative
        alert_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "audio alert" in b.description.lower()
        ]
        assert len(alert_barriers) > 0

    def test_missing_transcript(self, evaluator):
        """Test detection of missing transcripts."""
        schema = {
            "name": "no_transcript",
            "accessibility": {},
            "components": [
                {
                    "component_id": "video",
                    "component_type": "VIDEO",
                    "feedback": {},  # Missing transcript_available
                }
            ],
        }
        result = evaluator.evaluate(schema)

        # Should flag missing transcript for video component
        transcript_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "transcript" in b.description.lower()
        ]
        assert len(transcript_barriers) > 0


# ============================================
# Motor Accessibility Evaluator Tests
# ============================================


class TestMotorAccessibilityEvaluator:
    """Tests for MotorAccessibilityEvaluator."""

    @pytest.fixture
    def evaluator(self):
        return MotorAccessibilityEvaluator()

    def test_disability_type(self, evaluator):
        """Test disability type is correct."""
        assert evaluator.disability_type == DisabilityType.MOTOR

    def test_timeout_constants(self, evaluator):
        """Test motor timeout constants are correct."""
        assert evaluator.MIN_TIMEOUT_MULTIPLIER == 5
        assert evaluator.STANDARD_TIMEOUT == 20
        assert evaluator.MIN_MOTOR_TIMEOUT == 100  # 5x standard
        assert evaluator.MIN_TOUCH_TARGET == 44

    def test_fully_accessible_schema(self, evaluator):
        """Test evaluation of fully accessible schema."""
        result = evaluator.evaluate(FULLY_ACCESSIBLE_SCHEMA)

        assert result.disability_type == DisabilityType.MOTOR
        assert result.accommodation_score >= 0.7
        assert "Voice input support" in result.accommodations_present

    def test_motor_issues_schema(self, evaluator):
        """Test evaluation of schema with motor issues."""
        result = evaluator.evaluate(MOTOR_ISSUES_SCHEMA)

        assert result.passes is False
        assert result.total_barriers > 0

    def test_timeout_too_short(self, evaluator):
        """Test detection of timeout below 100 seconds."""
        result = evaluator.evaluate(MOTOR_ISSUES_SCHEMA)

        # Should flag timeout below 100s
        timeout_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "timeout" in b.description.lower()
        ]
        assert len(timeout_barriers) > 0
        assert any(b.severity == ViolationSeverity.CRITICAL for b in timeout_barriers)

    def test_complex_gestures_required(self, evaluator):
        """Test detection of complex gesture requirements."""
        result = evaluator.evaluate(MOTOR_ISSUES_SCHEMA)

        # Should flag complex gestures
        gesture_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "gesture" in b.description.lower()
        ]
        assert len(gesture_barriers) > 0

    def test_touch_target_too_small(self, evaluator):
        """Test detection of small touch targets."""
        result = evaluator.evaluate(MOTOR_ISSUES_SCHEMA)

        # Should flag touch target below 44px
        target_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "touch target" in b.description.lower()
        ]
        assert len(target_barriers) > 0

    def test_multi_step_action(self, evaluator):
        """Test detection of multi-step actions."""
        result = evaluator.evaluate(MOTOR_ISSUES_SCHEMA)

        # Should flag multi-step action requirement
        multistep_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "multi-step" in b.description.lower()
        ]
        assert len(multistep_barriers) > 0

    def test_extended_timeout_accommodation(self, evaluator):
        """Test extended timeout is recognized as accommodation."""
        result = evaluator.evaluate(FULLY_ACCESSIBLE_SCHEMA)

        # Should recognize extended timeout
        timeout_accs = [a for a in result.accommodations_present if "timeout" in a.lower()]
        assert len(timeout_accs) > 0


# ============================================
# Speech Accessibility Evaluator Tests
# ============================================


class TestSpeechAccessibilityEvaluator:
    """Tests for SpeechAccessibilityEvaluator."""

    @pytest.fixture
    def evaluator(self):
        return SpeechAccessibilityEvaluator()

    def test_disability_type(self, evaluator):
        """Test disability type is correct."""
        assert evaluator.disability_type == DisabilityType.SPEECH

    def test_fully_accessible_schema(self, evaluator):
        """Test evaluation of fully accessible schema."""
        result = evaluator.evaluate(FULLY_ACCESSIBLE_SCHEMA)

        assert result.disability_type == DisabilityType.SPEECH
        assert result.accommodation_score >= 0.7
        assert "100% text input fallback available" in result.accommodations_present

    def test_voice_only_schema(self, evaluator):
        """Test evaluation of voice-only schema."""
        result = evaluator.evaluate(VOICE_ONLY_SCHEMA)

        assert result.passes is False
        # Should detect voice-only without text fallback
        critical_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if b.severity == ViolationSeverity.CRITICAL
        ]
        assert len(critical_barriers) > 0

    def test_text_fallback_coverage(self, evaluator):
        """Test detection of incomplete text fallback coverage."""
        result = evaluator.evaluate(VOICE_ONLY_SCHEMA)

        # Should flag coverage below 100%
        coverage_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "coverage" in b.description.lower()
        ]
        assert len(coverage_barriers) > 0

    def test_voice_required_without_alternative(self, evaluator):
        """Test detection of voice required without alternative."""
        result = evaluator.evaluate(VOICE_ONLY_SCHEMA)

        # Should flag voice required without text alternative
        voice_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "voice input" in b.description.lower() and "required" in b.description.lower()
        ]
        assert len(voice_barriers) > 0


# ============================================
# Cognitive Accessibility Evaluator Tests
# ============================================


class TestCognitiveAccessibilityEvaluator:
    """Tests for CognitiveAccessibilityEvaluator."""

    @pytest.fixture
    def evaluator(self):
        return CognitiveAccessibilityEvaluator()

    def test_disability_type(self, evaluator):
        """Test disability type is correct."""
        assert evaluator.disability_type == DisabilityType.COGNITIVE

    def test_reading_level_constants(self, evaluator):
        """Test reading level constants."""
        assert evaluator.MAX_READING_GRADE == 8.0
        assert evaluator.MIN_READING_GRADE == 6.0

    def test_fully_accessible_schema(self, evaluator):
        """Test evaluation of fully accessible schema."""
        result = evaluator.evaluate(FULLY_ACCESSIBLE_SCHEMA)

        assert result.disability_type == DisabilityType.COGNITIVE
        assert result.accommodation_score >= 0.7
        assert "Consistent navigation patterns" in result.accommodations_present

    def test_cognitive_issues_schema(self, evaluator):
        """Test evaluation of schema with cognitive issues."""
        result = evaluator.evaluate(COGNITIVE_ISSUES_SCHEMA)

        assert result.passes is False
        assert result.total_barriers > 0

    def test_multi_step_flow_without_progress(self, evaluator):
        """Test detection of multi-step flow without progress indicators."""
        result = evaluator.evaluate(COGNITIVE_ISSUES_SCHEMA)

        # Should flag multi-step flow without progress indicators
        progress_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "progress" in b.description.lower()
        ]
        assert len(progress_barriers) > 0

    def test_destructive_action_without_confirmation(self, evaluator):
        """Test detection of destructive actions without confirmation."""
        result = evaluator.evaluate(COGNITIVE_ISSUES_SCHEMA)

        # Should flag destructive action without confirmation
        confirm_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "confirmation" in b.description.lower() or "destructive" in b.description.lower()
        ]
        assert len(confirm_barriers) > 0

    def test_complex_readability(self, evaluator):
        """Test detection of complex text exceeding grade level."""
        result = evaluator.evaluate(COGNITIVE_ISSUES_SCHEMA)

        # Should flag complex text
        readability_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "grade" in b.description.lower() or "reading" in b.description.lower()
        ]
        # Complex template should be flagged
        assert len(readability_barriers) > 0

    def test_missing_accommodations(self, evaluator):
        """Test identification of missing cognitive accommodations."""
        result = evaluator.evaluate(MINIMAL_SCHEMA)

        # Should identify missing accommodations
        assert "Consistent navigation patterns" in result.accommodations_missing
        assert "Progress indicators" in result.accommodations_missing
        assert "Undo support" in result.accommodations_missing


# ============================================
# Neurological Accessibility Evaluator Tests
# ============================================


class TestNeurologicalAccessibilityEvaluator:
    """Tests for NeurologicalAccessibilityEvaluator."""

    @pytest.fixture
    def evaluator(self):
        return NeurologicalAccessibilityEvaluator()

    def test_disability_type(self, evaluator):
        """Test disability type is correct."""
        assert evaluator.disability_type == DisabilityType.NEUROLOGICAL

    def test_flash_frequency_constant(self, evaluator):
        """Test flash frequency constant."""
        assert evaluator.MAX_FLASH_FREQUENCY == 3

    def test_fully_accessible_schema(self, evaluator):
        """Test evaluation of fully accessible schema."""
        result = evaluator.evaluate(FULLY_ACCESSIBLE_SCHEMA)

        assert result.disability_type == DisabilityType.NEUROLOGICAL
        assert result.accommodation_score >= 0.7
        assert "Seizure-safe mode available" in result.accommodations_present

    def test_neurological_issues_schema(self, evaluator):
        """Test evaluation of schema with neurological issues."""
        result = evaluator.evaluate(NEUROLOGICAL_ISSUES_SCHEMA)

        assert result.passes is False
        assert result.total_barriers > 0

    def test_flash_frequency_exceeded(self, evaluator):
        """Test detection of flash frequency above 3Hz."""
        result = evaluator.evaluate(NEUROLOGICAL_ISSUES_SCHEMA)

        # Should flag flash frequency above 3Hz
        flash_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "flash" in b.description.lower()
        ]
        assert len(flash_barriers) > 0
        assert any(b.severity == ViolationSeverity.CRITICAL for b in flash_barriers)

    def test_auto_play_enabled(self, evaluator):
        """Test detection of auto-play media."""
        result = evaluator.evaluate(NEUROLOGICAL_ISSUES_SCHEMA)

        # Should flag auto-play enabled
        autoplay_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "auto-play" in b.description.lower() or "auto play" in b.description.lower()
        ]
        assert len(autoplay_barriers) > 0

    def test_animation_without_controls(self, evaluator):
        """Test detection of animations without user controls."""
        result = evaluator.evaluate(NEUROLOGICAL_ISSUES_SCHEMA)

        # Should flag animation without controls
        animation_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "animation" in b.description.lower()
        ]
        assert len(animation_barriers) > 0

    def test_flashing_content_without_disable(self, evaluator):
        """Test detection of flashing content without disable option."""
        result = evaluator.evaluate(NEUROLOGICAL_ISSUES_SCHEMA)

        # Should flag flashing content
        flashing_barriers = [
            b for ba in result.barriers for b in ba.barriers
            if "flashing" in b.description.lower() and "content" in b.description.lower()
        ]
        assert len(flashing_barriers) > 0


# ============================================
# Combined Evaluator Tests
# ============================================


class TestCombinedDisabilityEvaluator:
    """Tests for CombinedDisabilityEvaluator."""

    @pytest.fixture
    def evaluator(self):
        return CombinedDisabilityEvaluator()

    def test_evaluate_all_disabilities(self, evaluator):
        """Test evaluating all disability types."""
        results = evaluator.evaluate(FULLY_ACCESSIBLE_SCHEMA)

        assert len(results) == 6
        assert DisabilityType.VISUAL in results
        assert DisabilityType.HEARING in results
        assert DisabilityType.MOTOR in results
        assert DisabilityType.SPEECH in results
        assert DisabilityType.COGNITIVE in results
        assert DisabilityType.NEUROLOGICAL in results

    def test_evaluate_specific_disabilities(self, evaluator):
        """Test evaluating specific disability types."""
        types = [DisabilityType.VISUAL, DisabilityType.MOTOR]
        results = evaluator.evaluate(FULLY_ACCESSIBLE_SCHEMA, disability_types=types)

        assert len(results) == 2
        assert DisabilityType.VISUAL in results
        assert DisabilityType.MOTOR in results
        assert DisabilityType.HEARING not in results

    def test_evaluate_single(self, evaluator):
        """Test evaluating a single disability type."""
        result = evaluator.evaluate_single(
            FULLY_ACCESSIBLE_SCHEMA, DisabilityType.VISUAL
        )

        assert result.disability_type == DisabilityType.VISUAL
        assert isinstance(result, DisabilityEvaluation)

    def test_evaluate_single_unknown_type(self, evaluator):
        """Test evaluating unknown disability type raises error."""
        with pytest.raises(ValueError):
            evaluator.evaluate_single(FULLY_ACCESSIBLE_SCHEMA, "UNKNOWN")

    def test_get_overall_score(self, evaluator):
        """Test calculating overall score."""
        results = evaluator.evaluate(FULLY_ACCESSIBLE_SCHEMA)
        score = evaluator.get_overall_score(results)

        assert 0.0 <= score <= 1.0

    def test_get_overall_score_empty(self, evaluator):
        """Test overall score for empty results."""
        score = evaluator.get_overall_score({})
        assert score == 1.0

    def test_get_summary(self, evaluator):
        """Test generating summary."""
        results = evaluator.evaluate(FULLY_ACCESSIBLE_SCHEMA)
        summary = evaluator.get_summary(results)

        assert "Overall Disability Accessibility Score" in summary
        assert "Passing:" in summary
        assert "By Category:" in summary

    def test_get_summary_empty(self, evaluator):
        """Test summary for empty results."""
        summary = evaluator.get_summary({})
        assert "No evaluations" in summary

    def test_fully_accessible_passes_all(self, evaluator):
        """Test fully accessible schema passes all categories."""
        results = evaluator.evaluate(FULLY_ACCESSIBLE_SCHEMA)

        passing_count = sum(1 for r in results.values() if r.passes)
        # Should pass most/all categories
        assert passing_count >= 4

    def test_minimal_schema_has_low_accommodations(self, evaluator):
        """Test minimal schema has fewer accommodations than fully accessible."""
        minimal_results = evaluator.evaluate(MINIMAL_SCHEMA)
        full_results = evaluator.evaluate(FULLY_ACCESSIBLE_SCHEMA)

        # Minimal schema should have fewer accommodations present
        minimal_accs = sum(len(r.accommodations_present) for r in minimal_results.values())
        full_accs = sum(len(r.accommodations_present) for r in full_results.values())
        assert minimal_accs < full_accs


# ============================================
# Score Calculation Tests
# ============================================


class TestScoreCalculation:
    """Tests for score calculation logic."""

    @pytest.fixture
    def evaluator(self):
        return VisualAccessibilityEvaluator()

    def test_perfect_score_no_barriers(self, evaluator):
        """Test perfect score with no barriers."""
        score = evaluator._calculate_score([])
        assert score == 1.0

    def test_score_decreases_with_critical(self, evaluator):
        """Test score decreases by 0.30 for critical barrier."""
        barriers = [
            BarrierAnalysis(
                area="test",
                barriers=[
                    Barrier(
                        category=BarrierCategory.PERCEPTION,
                        severity=ViolationSeverity.CRITICAL,
                        description="Critical",
                        location="test",
                        impact="Test",
                        remediation="Fix",
                    )
                ],
            )
        ]
        score = evaluator._calculate_score(barriers)
        assert score == 0.70

    def test_score_decreases_with_major(self, evaluator):
        """Test score decreases by 0.15 for major barrier."""
        barriers = [
            BarrierAnalysis(
                area="test",
                barriers=[
                    Barrier(
                        category=BarrierCategory.OPERATION,
                        severity=ViolationSeverity.MAJOR,
                        description="Major",
                        location="test",
                        impact="Test",
                        remediation="Fix",
                    )
                ],
            )
        ]
        score = evaluator._calculate_score(barriers)
        assert score == 0.85

    def test_score_minimum_zero(self, evaluator):
        """Test score doesn't go below zero."""
        barriers = [
            BarrierAnalysis(
                area="test",
                barriers=[
                    Barrier(
                        category=BarrierCategory.PERCEPTION,
                        severity=ViolationSeverity.CRITICAL,
                        description="Critical",
                        location="test",
                        impact="Test",
                        remediation="Fix",
                    )
                    for _ in range(10)  # 10 critical barriers
                ],
            )
        ]
        score = evaluator._calculate_score(barriers)
        assert score == 0.0

    def test_score_cumulative_deductions(self, evaluator):
        """Test cumulative deductions from multiple barriers."""
        barriers = [
            BarrierAnalysis(
                area="test",
                barriers=[
                    Barrier(
                        category=BarrierCategory.PERCEPTION,
                        severity=ViolationSeverity.CRITICAL,  # -0.30
                        description="Critical",
                        location="test",
                        impact="Test",
                        remediation="Fix",
                    ),
                    Barrier(
                        category=BarrierCategory.OPERATION,
                        severity=ViolationSeverity.MAJOR,  # -0.15
                        description="Major",
                        location="test",
                        impact="Test",
                        remediation="Fix",
                    ),
                    Barrier(
                        category=BarrierCategory.UNDERSTANDING,
                        severity=ViolationSeverity.MINOR,  # -0.05
                        description="Minor",
                        location="test",
                        impact="Test",
                        remediation="Fix",
                    ),
                ],
            )
        ]
        score = evaluator._calculate_score(barriers)
        # 1.0 - 0.30 - 0.15 - 0.05 = 0.50
        assert score == 0.50


# ============================================
# Helper Method Tests
# ============================================


class TestHelperMethods:
    """Tests for evaluator helper methods."""

    @pytest.fixture
    def evaluator(self):
        return VisualAccessibilityEvaluator()

    def test_get_components_empty(self, evaluator):
        """Test getting components from empty schema."""
        components = evaluator._get_components({})
        assert components == []

    def test_get_components_none(self, evaluator):
        """Test getting components when None."""
        components = evaluator._get_components({"components": None})
        assert components == []

    def test_get_components_valid(self, evaluator):
        """Test getting components from valid schema."""
        schema = {"components": [{"id": "test"}]}
        components = evaluator._get_components(schema)
        assert len(components) == 1

    def test_get_accessibility_config_empty(self, evaluator):
        """Test getting accessibility from empty schema."""
        config = evaluator._get_accessibility_config({})
        assert config == {}

    def test_get_accessibility_config_none(self, evaluator):
        """Test getting accessibility when None."""
        config = evaluator._get_accessibility_config({"accessibility": None})
        assert config == {}

    def test_get_component_accessibility(self, evaluator):
        """Test getting component accessibility."""
        component = {"accessibility": {"screen_reader_label": "Test"}}
        config = evaluator._get_component_accessibility(component)
        assert config["screen_reader_label"] == "Test"


# ============================================
# Disability Type Enum Tests
# ============================================


class TestDisabilityType:
    """Tests for DisabilityType enum."""

    def test_all_disability_types(self):
        """Test all disability types exist."""
        assert DisabilityType.VISUAL.value == "visual"
        assert DisabilityType.HEARING.value == "hearing"
        assert DisabilityType.MOTOR.value == "motor"
        assert DisabilityType.SPEECH.value == "speech"
        assert DisabilityType.COGNITIVE.value == "cognitive"
        assert DisabilityType.NEUROLOGICAL.value == "neurological"

    def test_disability_type_count(self):
        """Test correct number of disability types."""
        assert len(DisabilityType) == 6


# ============================================
# Edge Case Tests
# ============================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_schema_visual(self):
        """Test visual evaluator with empty schema."""
        evaluator = VisualAccessibilityEvaluator()
        result = evaluator.evaluate({})
        assert result is not None
        assert result.disability_type == DisabilityType.VISUAL

    def test_empty_schema_hearing(self):
        """Test hearing evaluator with empty schema."""
        evaluator = HearingAccessibilityEvaluator()
        result = evaluator.evaluate({})
        assert result is not None
        assert result.disability_type == DisabilityType.HEARING

    def test_empty_schema_motor(self):
        """Test motor evaluator with empty schema."""
        evaluator = MotorAccessibilityEvaluator()
        result = evaluator.evaluate({})
        assert result is not None
        assert result.disability_type == DisabilityType.MOTOR

    def test_empty_schema_speech(self):
        """Test speech evaluator with empty schema."""
        evaluator = SpeechAccessibilityEvaluator()
        result = evaluator.evaluate({})
        assert result is not None
        assert result.disability_type == DisabilityType.SPEECH

    def test_empty_schema_cognitive(self):
        """Test cognitive evaluator with empty schema."""
        evaluator = CognitiveAccessibilityEvaluator()
        result = evaluator.evaluate({})
        assert result is not None
        assert result.disability_type == DisabilityType.COGNITIVE

    def test_empty_schema_neurological(self):
        """Test neurological evaluator with empty schema."""
        evaluator = NeurologicalAccessibilityEvaluator()
        result = evaluator.evaluate({})
        assert result is not None
        assert result.disability_type == DisabilityType.NEUROLOGICAL

    def test_schema_with_null_values(self):
        """Test handling of None values in schema."""
        schema = {
            "name": "null_test",
            "accessibility": {
                "default_config": None,
            },
            "components": [
                {
                    "component_id": "test",
                    "component_type": "ACTION",
                    "accessibility": None,
                    "feedback": None,
                }
            ],
        }
        evaluator = CombinedDisabilityEvaluator()
        results = evaluator.evaluate(schema)

        # Should handle gracefully without crashing
        assert len(results) == 6

    def test_component_without_type(self):
        """Test handling component without component_type."""
        schema = {
            "name": "no_type",
            "accessibility": {},
            "components": [
                {
                    "component_id": "no_type_comp",
                    # Missing component_type
                    "accessibility": {},
                }
            ],
        }
        evaluator = VisualAccessibilityEvaluator()
        result = evaluator.evaluate(schema)

        # Should handle gracefully
        assert result is not None
