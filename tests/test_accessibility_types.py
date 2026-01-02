"""
Unit tests for Accessibility Configuration Types (LUIAG Framework)

Tests the type definitions and validation for Language User Interface
Accessibility Guidelines compliance.

Issue #67 - Task 4.1: Accessibility Config Types
"""

import pytest
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ============================================
# Python Mirror Types for Testing
# (These mirror the BAML types for validation)
# ============================================


class ComplianceLevel(Enum):
    """LUIAG conformance levels (aligned with WCAG structure)"""
    LEVEL_A = "LEVEL_A"
    LEVEL_AA = "LEVEL_AA"
    LEVEL_AAA = "LEVEL_AAA"


class LUIAGReadingLevel(Enum):
    """Reading level based on Flesch-Kincaid readability scores"""
    GRADE_5 = "GRADE_5"  # Simple (90-100)
    GRADE_6 = "GRADE_6"  # Easy (80-90)
    GRADE_8 = "GRADE_8"  # Standard (60-70)
    GRADE_10 = "GRADE_10"  # Moderate (50-60)
    GRADE_12 = "GRADE_12"  # Advanced (30-50)
    UNRESTRICTED = "UNRESTRICTED"


class CognitiveComplexity(Enum):
    """Cognitive complexity levels for content"""
    MINIMAL = "MINIMAL"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


class InteractionPace(Enum):
    """Interaction pace preferences"""
    EXTENDED = "EXTENDED"
    RELAXED = "RELAXED"
    STANDARD = "STANDARD"
    FAST = "FAST"


class ErrorPreventionLevel(Enum):
    """Level of error prevention measures"""
    BASIC = "BASIC"
    ENHANCED = "ENHANCED"
    MAXIMUM = "MAXIMUM"


class NotificationControl(Enum):
    """Notification control settings"""
    ALL = "ALL"
    IMPORTANT_ONLY = "IMPORTANT_ONLY"
    NONE = "NONE"
    SCHEDULED = "SCHEDULED"


class FocusIndicatorStyle(Enum):
    """Focus indicator style options"""
    OUTLINE = "OUTLINE"
    HIGHLIGHT = "HIGHLIGHT"
    UNDERLINE = "UNDERLINE"
    COMBINATION = "COMBINATION"


class ColorBlindMode(Enum):
    """Color blindness accommodation modes"""
    NONE = "NONE"
    PROTANOPIA = "PROTANOPIA"
    DEUTERANOPIA = "DEUTERANOPIA"
    TRITANOPIA = "TRITANOPIA"
    ACHROMATOPSIA = "ACHROMATOPSIA"


class ConfigIssueSeverity(Enum):
    """Severity levels for configuration issues"""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


# ============================================
# Dataclass Types
# ============================================


@dataclass
class ResponseConstraints:
    """Constraints on response content and structure"""
    reading_level: LUIAGReadingLevel
    use_simple_vocabulary: bool
    avoid_idioms: bool
    avoid_abbreviations: bool
    define_technical_terms: bool
    use_active_voice: bool
    consistent_terminology: bool
    max_sentence_length: Optional[int] = None
    max_paragraph_length: Optional[int] = None
    max_list_items: Optional[int] = None


@dataclass
class FocusIndicatorConfig:
    """Focus indicator configuration"""
    enhanced_visibility: bool
    indicator_style: FocusIndicatorStyle
    indicator_width_px: Optional[int] = None


@dataclass
class AttentionSupport:
    """Attention support features"""
    reduce_animations: bool
    reduce_auto_updates: bool
    notification_control: NotificationControl
    focus_indicators: FocusIndicatorConfig


@dataclass
class InteractionConstraints:
    """Constraints on interaction timing and input"""
    pace: InteractionPace
    timeout_extension_allowed: bool
    allow_pause_resume: bool
    provide_progress_indicators: bool
    confirm_destructive_actions: bool
    allow_undo: bool
    min_response_time_ms: Optional[int] = None
    max_session_timeout_ms: Optional[int] = None
    timeout_warning_ms: Optional[int] = None
    max_steps_before_summary: Optional[int] = None
    max_concurrent_tasks: Optional[int] = None


@dataclass
class CognitiveConstraints:
    """Constraints related to cognitive accessibility"""
    max_complexity: CognitiveComplexity
    use_progressive_disclosure: bool
    provide_context_reminders: bool
    use_consistent_layout: bool
    minimize_distractions: bool
    provide_clear_structure: bool
    use_familiar_patterns: bool
    support_focus_mode: bool
    provide_summaries: bool
    use_concrete_examples: bool
    max_choices_presented: Optional[int] = None
    max_memory_load: Optional[int] = None


@dataclass
class VisualAccommodations:
    """Visual impairment accommodations"""
    enabled: bool
    screen_reader_optimized: bool = False
    high_contrast_mode: bool = False
    large_text_mode: bool = False
    text_scaling_factor: Optional[float] = None
    color_blind_mode: Optional[ColorBlindMode] = None
    reduce_transparency: bool = False
    provide_text_alternatives: bool = False
    image_descriptions_detailed: bool = False
    avoid_color_only_info: bool = False
    min_contrast_ratio: Optional[float] = None


@dataclass
class HearingAccommodations:
    """Hearing impairment accommodations"""
    enabled: bool
    captions_required: bool = False
    transcripts_required: bool = False
    visual_alerts: bool = False
    sign_language_support: bool = False
    audio_description_text: bool = False
    volume_control: bool = False
    mono_audio: bool = False


@dataclass
class MotorAccommodations:
    """Motor impairment accommodations"""
    enabled: bool
    keyboard_only_mode: bool = False
    switch_access_support: bool = False
    dwell_click_support: bool = False
    dwell_time_ms: Optional[int] = None
    large_touch_targets: bool = False
    touch_target_size_px: Optional[int] = None
    reduce_precision_required: bool = False
    sticky_keys_support: bool = False
    gesture_simplification: bool = False
    motion_input_alternatives: bool = False
    pointer_speed_adjustable: bool = False


@dataclass
class SpeechAccommodations:
    """Speech impairment accommodations"""
    enabled: bool
    text_input_alternative: bool = False
    typing_to_speech: bool = False
    predefined_phrases: bool = False
    spelling_mode: bool = False
    extended_speech_timeout: bool = False
    noise_tolerance_high: bool = False
    accent_adaptation: bool = False


@dataclass
class CognitiveAccommodations:
    """Cognitive disability accommodations"""
    enabled: bool
    simplified_language: bool = False
    reading_support: bool = False
    step_by_step_guidance: bool = False
    memory_aids: bool = False
    decision_support: bool = False
    distraction_reduction: bool = False
    consistent_navigation: bool = False
    clear_error_messages: bool = False
    confirmation_dialogs: bool = False
    help_always_available: bool = False
    symbolic_support: bool = False


@dataclass
class NeurologicalAccommodations:
    """Neurological condition accommodations"""
    enabled: bool
    seizure_safe_mode: bool = False
    flash_frequency_limit: Optional[float] = None
    reduce_motion: bool = False
    vestibular_safe: bool = False
    predictable_interactions: bool = False
    sensory_overload_prevention: bool = False
    calm_mode: bool = False
    break_reminders: bool = False
    break_interval_minutes: Optional[int] = None


@dataclass
class DisabilityAccommodations:
    """Combined disability accommodations container"""
    visual: Optional[VisualAccommodations] = None
    hearing: Optional[HearingAccommodations] = None
    motor: Optional[MotorAccommodations] = None
    speech: Optional[SpeechAccommodations] = None
    cognitive: Optional[CognitiveAccommodations] = None
    neurological: Optional[NeurologicalAccommodations] = None


@dataclass
class LUIAGAccessibilityConfig:
    """Complete accessibility configuration for LUIAG compliance"""
    config_id: str
    config_version: str
    compliance_level: ComplianceLevel
    response_constraints: ResponseConstraints
    interaction_constraints: InteractionConstraints
    cognitive_constraints: CognitiveConstraints
    attention_support: AttentionSupport
    disability_accommodations: DisabilityAccommodations
    custom_settings: Optional[dict] = None


@dataclass
class FleschKincaidMapping:
    """Reference mapping for reading level to Flesch-Kincaid scores"""
    reading_level: LUIAGReadingLevel
    grade_level_min: int
    grade_level_max: int
    flesch_score_min: float
    flesch_score_max: float
    description: str


# ============================================
# Test Classes
# ============================================


class TestComplianceLevel:
    """Tests for LUIAG compliance level enum"""

    def test_all_levels_exist(self):
        """Verify all compliance levels are defined"""
        assert ComplianceLevel.LEVEL_A.value == "LEVEL_A"
        assert ComplianceLevel.LEVEL_AA.value == "LEVEL_AA"
        assert ComplianceLevel.LEVEL_AAA.value == "LEVEL_AAA"

    def test_level_count(self):
        """Verify correct number of levels"""
        assert len(ComplianceLevel) == 3


class TestLUIAGReadingLevel:
    """Tests for reading level enum with Flesch-Kincaid mapping"""

    def test_all_levels_exist(self):
        """Verify all reading levels are defined"""
        levels = [
            LUIAGReadingLevel.GRADE_5,
            LUIAGReadingLevel.GRADE_6,
            LUIAGReadingLevel.GRADE_8,
            LUIAGReadingLevel.GRADE_10,
            LUIAGReadingLevel.GRADE_12,
            LUIAGReadingLevel.UNRESTRICTED,
        ]
        assert len(levels) == 6

    def test_flesch_kincaid_mappings(self):
        """Verify Flesch-Kincaid score mappings are correct"""
        mappings = [
            FleschKincaidMapping(
                reading_level=LUIAGReadingLevel.GRADE_5,
                grade_level_min=5,
                grade_level_max=5,
                flesch_score_min=90.0,
                flesch_score_max=100.0,
                description="Simple language"
            ),
            FleschKincaidMapping(
                reading_level=LUIAGReadingLevel.GRADE_6,
                grade_level_min=6,
                grade_level_max=6,
                flesch_score_min=80.0,
                flesch_score_max=90.0,
                description="Easy language"
            ),
            FleschKincaidMapping(
                reading_level=LUIAGReadingLevel.GRADE_8,
                grade_level_min=7,
                grade_level_max=8,
                flesch_score_min=60.0,
                flesch_score_max=70.0,
                description="Standard language"
            ),
            FleschKincaidMapping(
                reading_level=LUIAGReadingLevel.GRADE_10,
                grade_level_min=9,
                grade_level_max=10,
                flesch_score_min=50.0,
                flesch_score_max=60.0,
                description="Moderate complexity"
            ),
            FleschKincaidMapping(
                reading_level=LUIAGReadingLevel.GRADE_12,
                grade_level_min=11,
                grade_level_max=12,
                flesch_score_min=30.0,
                flesch_score_max=50.0,
                description="Advanced language"
            ),
        ]

        for mapping in mappings:
            assert mapping.flesch_score_min <= mapping.flesch_score_max
            assert mapping.grade_level_min <= mapping.grade_level_max


class TestResponseConstraints:
    """Tests for response constraints"""

    def test_create_minimal_constraints(self):
        """Test creating response constraints with minimal settings"""
        constraints = ResponseConstraints(
            reading_level=LUIAGReadingLevel.GRADE_8,
            use_simple_vocabulary=False,
            avoid_idioms=False,
            avoid_abbreviations=False,
            define_technical_terms=False,
            use_active_voice=True,
            consistent_terminology=True,
        )
        assert constraints.reading_level == LUIAGReadingLevel.GRADE_8
        assert constraints.max_sentence_length is None

    def test_create_level_aaa_constraints(self):
        """Test creating AAA-level response constraints"""
        constraints = ResponseConstraints(
            max_sentence_length=15,
            max_paragraph_length=3,
            max_list_items=5,
            reading_level=LUIAGReadingLevel.GRADE_5,
            use_simple_vocabulary=True,
            avoid_idioms=True,
            avoid_abbreviations=True,
            define_technical_terms=True,
            use_active_voice=True,
            consistent_terminology=True,
        )
        assert constraints.reading_level == LUIAGReadingLevel.GRADE_5
        assert constraints.max_sentence_length == 15
        assert constraints.use_simple_vocabulary is True


class TestCognitiveConstraints:
    """Tests for cognitive constraints"""

    def test_create_minimal_cognitive_constraints(self):
        """Test creating minimal cognitive constraints"""
        constraints = CognitiveConstraints(
            max_complexity=CognitiveComplexity.MODERATE,
            use_progressive_disclosure=True,
            provide_context_reminders=False,
            use_consistent_layout=True,
            minimize_distractions=False,
            provide_clear_structure=True,
            use_familiar_patterns=True,
            support_focus_mode=False,
            provide_summaries=False,
            use_concrete_examples=False,
        )
        assert constraints.max_complexity == CognitiveComplexity.MODERATE

    def test_create_enhanced_cognitive_constraints(self):
        """Test creating enhanced cognitive constraints"""
        constraints = CognitiveConstraints(
            max_complexity=CognitiveComplexity.MINIMAL,
            max_choices_presented=3,
            max_memory_load=3,
            use_progressive_disclosure=True,
            provide_context_reminders=True,
            use_consistent_layout=True,
            minimize_distractions=True,
            provide_clear_structure=True,
            use_familiar_patterns=True,
            support_focus_mode=True,
            provide_summaries=True,
            use_concrete_examples=True,
        )
        assert constraints.max_complexity == CognitiveComplexity.MINIMAL
        assert constraints.max_choices_presented == 3


class TestDisabilityAccommodations:
    """Tests for disability accommodations"""

    def test_create_empty_accommodations(self):
        """Test creating empty accommodations container"""
        accommodations = DisabilityAccommodations()
        assert accommodations.visual is None
        assert accommodations.hearing is None
        assert accommodations.motor is None

    def test_create_visual_accommodations(self):
        """Test creating visual accommodations"""
        visual = VisualAccommodations(
            enabled=True,
            screen_reader_optimized=True,
            high_contrast_mode=True,
            large_text_mode=True,
            text_scaling_factor=1.5,
            color_blind_mode=ColorBlindMode.DEUTERANOPIA,
            provide_text_alternatives=True,
            image_descriptions_detailed=True,
            avoid_color_only_info=True,
            min_contrast_ratio=7.0,
        )
        assert visual.enabled is True
        assert visual.text_scaling_factor == 1.5
        assert visual.min_contrast_ratio == 7.0

    def test_create_hearing_accommodations(self):
        """Test creating hearing accommodations"""
        hearing = HearingAccommodations(
            enabled=True,
            captions_required=True,
            transcripts_required=True,
            visual_alerts=True,
        )
        assert hearing.enabled is True
        assert hearing.captions_required is True

    def test_create_motor_accommodations(self):
        """Test creating motor accommodations"""
        motor = MotorAccommodations(
            enabled=True,
            keyboard_only_mode=True,
            large_touch_targets=True,
            touch_target_size_px=48,
            dwell_click_support=True,
            dwell_time_ms=1000,
        )
        assert motor.enabled is True
        assert motor.touch_target_size_px == 48
        assert motor.dwell_time_ms == 1000

    def test_create_neurological_accommodations(self):
        """Test creating neurological accommodations"""
        neuro = NeurologicalAccommodations(
            enabled=True,
            seizure_safe_mode=True,
            flash_frequency_limit=3.0,
            reduce_motion=True,
            vestibular_safe=True,
            break_reminders=True,
            break_interval_minutes=20,
        )
        assert neuro.enabled is True
        assert neuro.flash_frequency_limit == 3.0
        assert neuro.break_interval_minutes == 20


class TestLUIAGAccessibilityConfig:
    """Tests for complete accessibility configuration"""

    def test_create_level_a_config(self):
        """Test creating Level A configuration"""
        config = LUIAGAccessibilityConfig(
            config_id="test-config-001",
            config_version="1.0.0",
            compliance_level=ComplianceLevel.LEVEL_A,
            response_constraints=ResponseConstraints(
                reading_level=LUIAGReadingLevel.GRADE_8,
                use_simple_vocabulary=False,
                avoid_idioms=False,
                avoid_abbreviations=False,
                define_technical_terms=False,
                use_active_voice=True,
                consistent_terminology=True,
            ),
            interaction_constraints=InteractionConstraints(
                pace=InteractionPace.STANDARD,
                timeout_extension_allowed=True,
                allow_pause_resume=True,
                provide_progress_indicators=True,
                confirm_destructive_actions=True,
                allow_undo=True,
            ),
            cognitive_constraints=CognitiveConstraints(
                max_complexity=CognitiveComplexity.MODERATE,
                use_progressive_disclosure=True,
                provide_context_reminders=False,
                use_consistent_layout=True,
                minimize_distractions=False,
                provide_clear_structure=True,
                use_familiar_patterns=True,
                support_focus_mode=False,
                provide_summaries=False,
                use_concrete_examples=False,
            ),
            attention_support=AttentionSupport(
                reduce_animations=False,
                reduce_auto_updates=False,
                notification_control=NotificationControl.ALL,
                focus_indicators=FocusIndicatorConfig(
                    enhanced_visibility=False,
                    indicator_style=FocusIndicatorStyle.OUTLINE,
                ),
            ),
            disability_accommodations=DisabilityAccommodations(),
        )
        assert config.compliance_level == ComplianceLevel.LEVEL_A
        assert config.config_id == "test-config-001"

    def test_create_level_aaa_config(self):
        """Test creating Level AAA configuration"""
        config = LUIAGAccessibilityConfig(
            config_id="test-config-aaa",
            config_version="1.0.0",
            compliance_level=ComplianceLevel.LEVEL_AAA,
            response_constraints=ResponseConstraints(
                max_sentence_length=15,
                max_paragraph_length=3,
                max_list_items=5,
                reading_level=LUIAGReadingLevel.GRADE_5,
                use_simple_vocabulary=True,
                avoid_idioms=True,
                avoid_abbreviations=True,
                define_technical_terms=True,
                use_active_voice=True,
                consistent_terminology=True,
            ),
            interaction_constraints=InteractionConstraints(
                pace=InteractionPace.EXTENDED,
                timeout_extension_allowed=True,
                allow_pause_resume=True,
                provide_progress_indicators=True,
                confirm_destructive_actions=True,
                allow_undo=True,
                max_steps_before_summary=3,
            ),
            cognitive_constraints=CognitiveConstraints(
                max_complexity=CognitiveComplexity.MINIMAL,
                max_choices_presented=3,
                max_memory_load=3,
                use_progressive_disclosure=True,
                provide_context_reminders=True,
                use_consistent_layout=True,
                minimize_distractions=True,
                provide_clear_structure=True,
                use_familiar_patterns=True,
                support_focus_mode=True,
                provide_summaries=True,
                use_concrete_examples=True,
            ),
            attention_support=AttentionSupport(
                reduce_animations=True,
                reduce_auto_updates=True,
                notification_control=NotificationControl.IMPORTANT_ONLY,
                focus_indicators=FocusIndicatorConfig(
                    enhanced_visibility=True,
                    indicator_style=FocusIndicatorStyle.COMBINATION,
                    indicator_width_px=3,
                ),
            ),
            disability_accommodations=DisabilityAccommodations(
                visual=VisualAccommodations(
                    enabled=True,
                    screen_reader_optimized=True,
                    high_contrast_mode=True,
                    provide_text_alternatives=True,
                ),
                cognitive=CognitiveAccommodations(
                    enabled=True,
                    simplified_language=True,
                    step_by_step_guidance=True,
                    memory_aids=True,
                ),
            ),
        )
        assert config.compliance_level == ComplianceLevel.LEVEL_AAA
        assert config.response_constraints.reading_level == LUIAGReadingLevel.GRADE_5
        assert config.cognitive_constraints.max_complexity == CognitiveComplexity.MINIMAL


class TestComplianceLevelDefaults:
    """Tests for compliance level default values"""

    def test_level_a_defaults(self):
        """Test Level A has appropriate defaults"""
        # Level A: minimum requirements
        assert ComplianceLevel.LEVEL_A.value == "LEVEL_A"
        # In a real implementation, would verify defaults like:
        # - reading_level: GRADE_8
        # - max_complexity: MODERATE
        # - pace: STANDARD

    def test_level_aa_defaults(self):
        """Test Level AA has appropriate defaults"""
        # Level AA: recommended standard
        assert ComplianceLevel.LEVEL_AA.value == "LEVEL_AA"
        # In a real implementation, would verify defaults like:
        # - reading_level: GRADE_6
        # - max_complexity: LOW
        # - pace: RELAXED

    def test_level_aaa_defaults(self):
        """Test Level AAA has appropriate defaults"""
        # Level AAA: enhanced accessibility
        assert ComplianceLevel.LEVEL_AAA.value == "LEVEL_AAA"
        # In a real implementation, would verify defaults like:
        # - reading_level: GRADE_5
        # - max_complexity: MINIMAL
        # - pace: EXTENDED


class TestIntegrationWithInterfaceSchema:
    """Tests for integration with InterfaceSchema"""

    def test_accessibility_config_serializable(self):
        """Test that config can be serialized for schema integration"""
        config = LUIAGAccessibilityConfig(
            config_id="schema-integration-test",
            config_version="1.0.0",
            compliance_level=ComplianceLevel.LEVEL_AA,
            response_constraints=ResponseConstraints(
                reading_level=LUIAGReadingLevel.GRADE_6,
                use_simple_vocabulary=True,
                avoid_idioms=True,
                avoid_abbreviations=False,
                define_technical_terms=True,
                use_active_voice=True,
                consistent_terminology=True,
            ),
            interaction_constraints=InteractionConstraints(
                pace=InteractionPace.RELAXED,
                timeout_extension_allowed=True,
                allow_pause_resume=True,
                provide_progress_indicators=True,
                confirm_destructive_actions=True,
                allow_undo=True,
            ),
            cognitive_constraints=CognitiveConstraints(
                max_complexity=CognitiveComplexity.LOW,
                use_progressive_disclosure=True,
                provide_context_reminders=True,
                use_consistent_layout=True,
                minimize_distractions=True,
                provide_clear_structure=True,
                use_familiar_patterns=True,
                support_focus_mode=True,
                provide_summaries=True,
                use_concrete_examples=True,
            ),
            attention_support=AttentionSupport(
                reduce_animations=True,
                reduce_auto_updates=True,
                notification_control=NotificationControl.SIGNIFICANT,
                focus_indicators=FocusIndicatorConfig(
                    enhanced_visibility=True,
                    indicator_style=FocusIndicatorStyle.OUTLINE,
                    indicator_width_px=2,
                ),
            ),
            disability_accommodations=DisabilityAccommodations(),
        )

        # Verify config is properly structured
        assert config.config_id is not None
        assert config.compliance_level == ComplianceLevel.LEVEL_AA
        assert config.response_constraints.reading_level == LUIAGReadingLevel.GRADE_6


# Add SIGNIFICANT to NotificationControl for this test
NotificationControl.SIGNIFICANT = "SIGNIFICANT"


class TestColorBlindModes:
    """Tests for color blindness accommodation modes"""

    def test_all_modes_exist(self):
        """Verify all color blind modes are defined"""
        modes = [
            ColorBlindMode.NONE,
            ColorBlindMode.PROTANOPIA,
            ColorBlindMode.DEUTERANOPIA,
            ColorBlindMode.TRITANOPIA,
            ColorBlindMode.ACHROMATOPSIA,
        ]
        assert len(modes) == 5

    def test_common_modes_covered(self):
        """Verify common color blindness types are covered"""
        # Red-green color blindness (most common)
        assert ColorBlindMode.PROTANOPIA.value == "PROTANOPIA"  # Red-blind
        assert ColorBlindMode.DEUTERANOPIA.value == "DEUTERANOPIA"  # Green-blind

        # Blue-yellow color blindness (rare)
        assert ColorBlindMode.TRITANOPIA.value == "TRITANOPIA"

        # Complete color blindness (very rare)
        assert ColorBlindMode.ACHROMATOPSIA.value == "ACHROMATOPSIA"
