"""Tests for adaptive response generation.

Issue #48 - Phase 2: Adaptive Interface Personalization
"""

import pytest
from src.lui_simulator.adaptive_response import (
    AdaptiveResponseGenerator,
    AdaptiveResponse,
    AdaptationSettings,
    FrustrationIndicators,
    FrustrationResponse,
    ResponseModifier,
    DEFAULT_SETTINGS,
    LEVEL_GUIDELINES,
)
from src.lui_simulator.expertise import ExpertiseLevel
from src.lui_simulator.templates import VerbosityLevel


class TestFrustrationIndicators:
    """Tests for FrustrationIndicators class."""

    def test_default_no_frustration(self):
        """Default indicators should show no frustration."""
        indicators = FrustrationIndicators()
        assert indicators.frustration_score() == 0.0
        assert not indicators.is_frustrated()

    def test_consecutive_errors_increase_score(self):
        """Consecutive errors should increase frustration score."""
        indicators = FrustrationIndicators(consecutive_errors=3)
        score = indicators.frustration_score()
        assert score >= 0.3  # 3 errors * 0.15 = 0.45
        assert indicators.is_frustrated()

    def test_negative_sentiment_increases_score(self):
        """Negative sentiment should increase frustration score."""
        indicators = FrustrationIndicators(negative_sentiment=True)
        assert indicators.frustration_score() >= 0.2

    def test_multiple_signals_combine(self):
        """Multiple frustration signals should combine."""
        indicators = FrustrationIndicators(
            consecutive_errors=2,
            negative_sentiment=True,
            help_seeking_rate=0.5,
        )
        score = indicators.frustration_score()
        assert score > 0.4  # Combined signals

    def test_max_score_is_capped(self):
        """Frustration score should be capped at 1.0."""
        indicators = FrustrationIndicators(
            consecutive_errors=10,
            repeated_queries=5,
            negative_sentiment=True,
            rapid_interactions=True,
            help_seeking_rate=1.0,
            abandonment_signals=True,
        )
        assert indicators.frustration_score() <= 1.0

    def test_custom_threshold(self):
        """Should use custom frustration threshold."""
        indicators = FrustrationIndicators(consecutive_errors=1)
        assert not indicators.is_frustrated(threshold=0.5)
        assert indicators.is_frustrated(threshold=0.1)


class TestAdaptationSettings:
    """Tests for AdaptationSettings class."""

    def test_create_settings(self):
        """Should create adaptation settings."""
        settings = AdaptationSettings(
            expertise_level=ExpertiseLevel.NOVICE,
            verbosity_level=VerbosityLevel.DETAILED,
            show_examples=True,
            show_shortcuts=False,
            require_confirmation=True,
            use_technical_language=False,
            offer_help_proactively=True,
            define_terms=True,
            max_options=5,
        )
        assert settings.expertise_level == ExpertiseLevel.NOVICE
        assert settings.verbosity_level == VerbosityLevel.DETAILED
        assert settings.show_examples is True
        assert settings.max_options == 5


class TestDefaultSettings:
    """Tests for default settings by level."""

    def test_novice_settings(self):
        """Novice should have verbose, helpful settings."""
        settings = DEFAULT_SETTINGS[ExpertiseLevel.NOVICE]
        assert settings.verbosity_level == VerbosityLevel.DETAILED
        assert settings.show_examples is True
        assert settings.show_shortcuts is False
        assert settings.require_confirmation is True
        assert settings.offer_help_proactively is True
        assert settings.define_terms is True

    def test_beginner_settings(self):
        """Beginner should have detailed but less hand-holding."""
        settings = DEFAULT_SETTINGS[ExpertiseLevel.BEGINNER]
        assert settings.verbosity_level == VerbosityLevel.DETAILED
        assert settings.show_examples is True
        assert settings.offer_help_proactively is True

    def test_intermediate_settings(self):
        """Intermediate should have standard settings."""
        settings = DEFAULT_SETTINGS[ExpertiseLevel.INTERMEDIATE]
        assert settings.verbosity_level == VerbosityLevel.STANDARD
        assert settings.show_examples is False
        assert settings.show_shortcuts is True
        assert settings.offer_help_proactively is False

    def test_advanced_settings(self):
        """Advanced should have concise settings."""
        settings = DEFAULT_SETTINGS[ExpertiseLevel.ADVANCED]
        assert settings.verbosity_level == VerbosityLevel.CONCISE
        assert settings.show_examples is False
        assert settings.show_shortcuts is True
        assert settings.use_technical_language is True

    def test_expert_settings(self):
        """Expert should have minimal settings."""
        settings = DEFAULT_SETTINGS[ExpertiseLevel.EXPERT]
        assert settings.verbosity_level == VerbosityLevel.MINIMAL
        assert settings.show_examples is False
        assert settings.show_shortcuts is True
        assert settings.require_confirmation is False
        assert settings.max_options == 0  # Unlimited


class TestAdaptiveResponse:
    """Tests for AdaptiveResponse class."""

    def test_create_response(self):
        """Should create an adaptive response."""
        response = AdaptiveResponse(
            content="Task created successfully!",
            verbosity_used=VerbosityLevel.STANDARD,
            adaptations_applied=["examples_included"],
            shortcuts_mentioned=["Ctrl+Z: Undo"],
            follow_up_suggestions=["View task", "Create another"],
            expertise_level_used=ExpertiseLevel.INTERMEDIATE,
            frustration_mode=FrustrationResponse.NORMAL,
            confidence=0.85,
        )
        assert response.content == "Task created successfully!"
        assert response.verbosity_used == VerbosityLevel.STANDARD
        assert "examples_included" in response.adaptations_applied

    def test_response_with_alternative(self):
        """Should support alternative content for toggling."""
        response = AdaptiveResponse(
            content="Done.",
            verbosity_used=VerbosityLevel.MINIMAL,
            alternative_content="Task created. Would you like to add details?",
            show_toggle=True,
        )
        assert response.alternative_content is not None
        assert response.show_toggle is True


class TestAdaptiveResponseGenerator:
    """Tests for AdaptiveResponseGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        return AdaptiveResponseGenerator()

    def test_generator_initialization(self, generator):
        """Generator should initialize with template manager."""
        assert generator._template_manager is not None

    def test_get_settings_novice(self, generator):
        """Should get settings for novice level."""
        settings = generator.get_settings(ExpertiseLevel.NOVICE)
        assert settings.verbosity_level == VerbosityLevel.DETAILED
        assert settings.show_examples is True

    def test_get_settings_expert(self, generator):
        """Should get settings for expert level."""
        settings = generator.get_settings(ExpertiseLevel.EXPERT)
        assert settings.verbosity_level == VerbosityLevel.MINIMAL
        assert settings.show_shortcuts is True

    def test_get_settings_with_frustration(self, generator):
        """Frustration should adjust settings."""
        frustration = FrustrationIndicators(consecutive_errors=3)
        settings = generator.get_settings(ExpertiseLevel.INTERMEDIATE, frustration)
        # Should increase verbosity
        assert settings.verbosity_level == VerbosityLevel.DETAILED
        assert settings.show_examples is True
        assert settings.offer_help_proactively is True

    def test_get_settings_high_frustration(self, generator):
        """High frustration should enable term definitions."""
        frustration = FrustrationIndicators(
            consecutive_errors=5,
            negative_sentiment=True,
        )
        settings = generator.get_settings(ExpertiseLevel.ADVANCED, frustration)
        assert settings.define_terms is True


class TestFrustrationDetection:
    """Tests for frustration detection."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        return AdaptiveResponseGenerator()

    def test_detect_no_frustration(self, generator):
        """Should detect no frustration in normal session."""
        indicators = generator.detect_frustration(
            consecutive_errors=0,
            repeated_queries=0,
            negative_words_detected=False,
        )
        assert not indicators.is_frustrated()

    def test_detect_error_frustration(self, generator):
        """Should detect frustration from consecutive errors."""
        indicators = generator.detect_frustration(consecutive_errors=3)
        assert indicators.is_frustrated()
        assert indicators.consecutive_errors == 3

    def test_detect_rapid_interactions(self, generator):
        """Should detect rapid interactions."""
        indicators = generator.detect_frustration(
            interactions_per_minute=15.0,
        )
        assert indicators.rapid_interactions is True

    def test_detect_abandonment(self, generator):
        """Should detect abandonment signals."""
        indicators = generator.detect_frustration(incomplete_tasks=5)
        assert indicators.abandonment_signals is True

    def test_calculate_help_rate(self, generator):
        """Should calculate help seeking rate."""
        indicators = generator.detect_frustration(
            help_requests=5,
            total_interactions=20,
        )
        assert indicators.help_seeking_rate == 0.25


class TestFrustrationResponseMode:
    """Tests for frustration response mode determination."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        return AdaptiveResponseGenerator()

    def test_normal_mode(self, generator):
        """Low frustration should return NORMAL mode."""
        indicators = FrustrationIndicators()
        mode = generator.get_frustration_response_mode(indicators)
        assert mode == FrustrationResponse.NORMAL

    def test_increased_help_mode(self, generator):
        """Moderate frustration should increase help."""
        indicators = FrustrationIndicators(consecutive_errors=2)
        mode = generator.get_frustration_response_mode(indicators)
        assert mode == FrustrationResponse.INCREASED_HELP

    def test_offer_alternatives_mode(self, generator):
        """Higher frustration should offer alternatives."""
        indicators = FrustrationIndicators(
            consecutive_errors=3,
            negative_sentiment=True,
        )
        mode = generator.get_frustration_response_mode(indicators)
        assert mode in (FrustrationResponse.OFFER_ALTERNATIVES, FrustrationResponse.SIMPLIFY)

    def test_escalate_mode(self, generator):
        """Very high frustration should escalate."""
        indicators = FrustrationIndicators(
            consecutive_errors=5,
            negative_sentiment=True,
            abandonment_signals=True,
            help_seeking_rate=0.8,
        )
        mode = generator.get_frustration_response_mode(indicators)
        assert mode == FrustrationResponse.ESCALATE


class TestGenerateResponse:
    """Tests for response generation."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        return AdaptiveResponseGenerator()

    def test_generate_response_novice(self, generator):
        """Should generate verbose response for novice."""
        response = generator.generate_response(
            template_id="task_creation",
            expertise_level=ExpertiseLevel.NOVICE,
            values={"title": "Test task", "priority": "high", "due_date": "tomorrow"},
        )
        assert response is not None
        assert response.expertise_level_used == ExpertiseLevel.NOVICE
        assert response.verbosity_used == VerbosityLevel.DETAILED

    def test_generate_response_expert(self, generator):
        """Should generate concise response for expert."""
        response = generator.generate_response(
            template_id="task_creation",
            expertise_level=ExpertiseLevel.EXPERT,
            values={"title": "Test task", "priority": "high", "due_date": "tomorrow"},
        )
        assert response is not None
        assert response.expertise_level_used == ExpertiseLevel.EXPERT
        assert response.verbosity_used == VerbosityLevel.MINIMAL

    def test_generate_response_with_frustration(self, generator):
        """Frustrated user should get adjusted response."""
        frustration = FrustrationIndicators(consecutive_errors=3)
        response = generator.generate_response(
            template_id="task_creation",
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            values={"title": "Test task", "priority": "high", "due_date": "tomorrow"},
            frustration=frustration,
        )
        assert response.frustration_mode != FrustrationResponse.NORMAL
        # Verbosity should be increased
        assert response.verbosity_used == VerbosityLevel.DETAILED

    def test_generate_response_first_time(self, generator):
        """First time should show toggle for transitioning users."""
        response = generator.generate_response(
            template_id="task_creation",
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            values={"title": "Test task", "priority": "high", "due_date": "tomorrow"},
            is_first_time=True,
        )
        assert response.show_toggle is True

    def test_generate_response_fallback(self, generator):
        """Should generate fallback for unknown template."""
        response = generator.generate_response(
            template_id="nonexistent_template",
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            values={},
        )
        assert response is not None
        assert "fallback_used" in response.adaptations_applied


class TestGenerateErrorResponse:
    """Tests for error response generation."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        return AdaptiveResponseGenerator()

    def test_error_response_novice(self, generator):
        """Novice should get detailed error with options."""
        response = generator.generate_error_response(
            error_message="Task creation failed: duplicate name",
            expertise_level=ExpertiseLevel.NOVICE,
            recovery_options=["Rename task", "View existing", "Cancel"],
        )
        assert "couldn't complete" in response.content.lower() or "problem" in response.content.lower()
        assert "1." in response.content  # Numbered options

    def test_error_response_expert(self, generator):
        """Expert should get minimal error."""
        response = generator.generate_error_response(
            error_message="DUPLICATE_NAME: Task creation failed",
            expertise_level=ExpertiseLevel.EXPERT,
        )
        assert len(response.content) < 100  # Concise
        assert "DUPLICATE" in response.content or "Error" in response.content

    def test_error_response_frustrated(self, generator):
        """Frustrated user should get supportive error."""
        frustration = FrustrationIndicators(consecutive_errors=3, negative_sentiment=True)
        response = generator.generate_error_response(
            error_message="Task creation failed",
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            frustration=frustration,
        )
        # Should offer simpler approach or support
        assert "simpler" in response.content.lower() or "support" in response.content.lower()

    def test_error_response_includes_shortcuts(self, generator):
        """Advanced error should include shortcuts."""
        response = generator.generate_error_response(
            error_message="Error occurred",
            expertise_level=ExpertiseLevel.ADVANCED,
        )
        assert len(response.shortcuts_mentioned) > 0


class TestAdaptResponseToLevel:
    """Tests for response adaptation."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        return AdaptiveResponseGenerator()

    def test_adapt_to_minimal(self, generator):
        """Should minimize response for expert."""
        original = "Great job! Your task has been created successfully. Would you like to add more details?"
        response = generator.adapt_response_to_level(
            original, ExpertiseLevel.EXPERT, include_shortcuts=True
        )
        assert len(response.content) < len(original)
        assert response.verbosity_used == VerbosityLevel.MINIMAL

    def test_adapt_to_detailed(self, generator):
        """Should expand response for novice."""
        original = "Task created."
        response = generator.adapt_response_to_level(
            original, ExpertiseLevel.NOVICE, include_shortcuts=False
        )
        assert len(response.content) >= len(original)
        assert response.verbosity_used == VerbosityLevel.DETAILED

    def test_adapt_includes_shortcuts(self, generator):
        """Should include shortcuts when requested."""
        response = generator.adapt_response_to_level(
            "Task created", ExpertiseLevel.ADVANCED, include_shortcuts=True
        )
        assert len(response.shortcuts_mentioned) > 0

    def test_adapt_excludes_shortcuts_for_novice(self, generator):
        """Should not include shortcuts for novice."""
        response = generator.adapt_response_to_level(
            "Task created", ExpertiseLevel.NOVICE, include_shortcuts=True
        )
        # Novice settings have show_shortcuts=False
        assert len(response.shortcuts_mentioned) == 0


class TestLevelGuidelines:
    """Tests for expertise level guidelines."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        return AdaptiveResponseGenerator()

    def test_guidelines_exist_for_all_levels(self, generator):
        """Guidelines should exist for all expertise levels."""
        for level in ExpertiseLevel:
            guidelines = generator.get_level_guidelines(level)
            assert guidelines is not None
            assert "description" in guidelines
            assert "confirmation_policy" in guidelines

    def test_novice_guidelines(self, generator):
        """Novice guidelines should emphasize guidance."""
        guidelines = generator.get_level_guidelines(ExpertiseLevel.NOVICE)
        assert "guidance" in guidelines["description"].lower() or "new" in guidelines["description"].lower()
        assert "always" in guidelines["confirmation_policy"].lower()

    def test_expert_guidelines(self, generator):
        """Expert guidelines should emphasize efficiency."""
        guidelines = generator.get_level_guidelines(ExpertiseLevel.EXPERT)
        assert "expert" in guidelines["description"].lower() or "maximum" in guidelines["description"].lower()
        assert "never" in guidelines["confirmation_policy"].lower()


class TestShouldShowFeature:
    """Tests for feature visibility decisions."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        return AdaptiveResponseGenerator()

    def test_shortcuts_by_level(self, generator):
        """Shortcuts should only show for intermediate+."""
        assert not generator.should_show_feature("shortcuts", ExpertiseLevel.NOVICE)
        assert not generator.should_show_feature("shortcuts", ExpertiseLevel.BEGINNER)
        assert generator.should_show_feature("shortcuts", ExpertiseLevel.INTERMEDIATE)
        assert generator.should_show_feature("shortcuts", ExpertiseLevel.ADVANCED)
        assert generator.should_show_feature("shortcuts", ExpertiseLevel.EXPERT)

    def test_examples_by_level(self, generator):
        """Examples should show for novice/beginner."""
        assert generator.should_show_feature("examples", ExpertiseLevel.NOVICE)
        assert generator.should_show_feature("examples", ExpertiseLevel.BEGINNER)
        assert not generator.should_show_feature("examples", ExpertiseLevel.INTERMEDIATE)
        assert not generator.should_show_feature("examples", ExpertiseLevel.EXPERT)

    def test_confirmation_by_level(self, generator):
        """Confirmation should be required for novice/beginner."""
        assert generator.should_show_feature("confirmation", ExpertiseLevel.NOVICE)
        assert generator.should_show_feature("confirmation", ExpertiseLevel.BEGINNER)
        assert not generator.should_show_feature("confirmation", ExpertiseLevel.ADVANCED)
        assert not generator.should_show_feature("confirmation", ExpertiseLevel.EXPERT)

    def test_help_by_level(self, generator):
        """Proactive help should be offered for novice/beginner."""
        assert generator.should_show_feature("help", ExpertiseLevel.NOVICE)
        assert generator.should_show_feature("help", ExpertiseLevel.BEGINNER)
        assert not generator.should_show_feature("help", ExpertiseLevel.INTERMEDIATE)
        assert not generator.should_show_feature("help", ExpertiseLevel.EXPERT)


class TestMaxOptions:
    """Tests for max options by level."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        return AdaptiveResponseGenerator()

    def test_max_options_novice(self, generator):
        """Novice should have limited options."""
        max_opts = generator.get_max_options(ExpertiseLevel.NOVICE)
        assert max_opts == 5

    def test_max_options_beginner(self, generator):
        """Beginner should have 4 options."""
        max_opts = generator.get_max_options(ExpertiseLevel.BEGINNER)
        assert max_opts == 4

    def test_max_options_intermediate(self, generator):
        """Intermediate should have 3 options."""
        max_opts = generator.get_max_options(ExpertiseLevel.INTERMEDIATE)
        assert max_opts == 3

    def test_max_options_expert(self, generator):
        """Expert should have unlimited options."""
        max_opts = generator.get_max_options(ExpertiseLevel.EXPERT)
        assert max_opts == 0  # 0 = unlimited


class TestResponseModifier:
    """Tests for ResponseModifier class."""

    def test_create_modifier(self):
        """Should create a response modifier."""
        modifier = ResponseModifier(
            modifier_type="INCREASE_VERBOSITY",
            reason="User is frustrated",
            impact="Response will be more detailed",
        )
        assert modifier.modifier_type == "INCREASE_VERBOSITY"
        assert modifier.reason == "User is frustrated"


class TestIntegration:
    """Integration tests for adaptive response generation."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        return AdaptiveResponseGenerator()

    def test_full_workflow_novice(self, generator):
        """Test complete workflow for novice user."""
        # Detect no frustration
        frustration = generator.detect_frustration(
            consecutive_errors=0,
            help_requests=2,
            total_interactions=10,
        )
        assert not frustration.is_frustrated()

        # Get settings
        settings = generator.get_settings(ExpertiseLevel.NOVICE, frustration)
        assert settings.show_examples is True

        # Generate response
        response = generator.generate_response(
            template_id="task_creation",
            expertise_level=ExpertiseLevel.NOVICE,
            values={"title": "My task", "priority": "low", "due_date": "next week"},
            frustration=frustration,
        )
        assert response.verbosity_used == VerbosityLevel.DETAILED

    def test_full_workflow_frustrated_intermediate(self, generator):
        """Test complete workflow for frustrated intermediate user."""
        # Detect frustration
        frustration = generator.detect_frustration(
            consecutive_errors=3,
            negative_words_detected=True,
            help_requests=5,
            total_interactions=10,
        )
        assert frustration.is_frustrated()

        # Get response mode
        mode = generator.get_frustration_response_mode(frustration)
        assert mode != FrustrationResponse.NORMAL

        # Generate error response
        response = generator.generate_error_response(
            error_message="Connection timeout",
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            frustration=frustration,
            recovery_options=["Retry", "Check connection", "Contact support"],
        )
        assert response.frustration_mode != FrustrationResponse.NORMAL
        # Should suggest simpler approach due to frustration
        assert "simpler" in response.content.lower() or len(response.follow_up_suggestions) > 0

    def test_consistency_across_levels(self, generator):
        """Response structure should be consistent across levels."""
        levels = [
            ExpertiseLevel.NOVICE,
            ExpertiseLevel.BEGINNER,
            ExpertiseLevel.INTERMEDIATE,
            ExpertiseLevel.ADVANCED,
            ExpertiseLevel.EXPERT,
        ]

        for level in levels:
            response = generator.generate_response(
                template_id="success",
                expertise_level=level,
                values={"action": "completed task", "details": "Task done"},
            )
            # All should have these fields
            assert response.content is not None
            assert response.verbosity_used is not None
            assert response.expertise_level_used == level
            assert response.frustration_mode == FrustrationResponse.NORMAL

    def test_graceful_with_incomplete_profile(self, generator):
        """Should handle incomplete profile gracefully."""
        # Generate with minimal info - defaults to INTERMEDIATE
        response = generator.generate_response(
            template_id="task_creation",
            expertise_level=ExpertiseLevel.INTERMEDIATE,  # Default
            values={},  # No values
        )
        assert response is not None
        assert response.content is not None
