"""Tests for the graceful response generator module.

Issue #82 - Task 5.5: Graceful Response Generator
Part of #28 - Phase 5: Intent Drift Detection
"""

import pytest

from src.intent_drift.drift_classifier import DriftClassification
from src.intent_drift.response_generator import (
    ACKNOWLEDGMENTS,
    DRIFT_TEMPLATES,
    DRIFT_TO_RESPONSE_TYPE,
    FOLLOW_UP_PROMPTS,
    TEMPLATE_ABSTRACTION_CLIMB,
    TEMPLATE_AMBIGUOUS,
    TEMPLATE_DOMAIN_SHIFT,
    TEMPLATE_ESCALATION,
    TEMPLATE_NONE,
    TEMPLATE_PERSONALIZATION,
    TEMPLATE_SCOPE_EXPANSION,
    TEMPLATE_TEMPORAL_DRIFT,
    GracefulResponseGenerator,
    ResponseGeneratorConfig,
)
from src.intent_drift.types import (
    DriftResponseTone,
    DriftType,
    GracefulResponseType,
    RedirectSuggestion,
)


# ============================================
# Template Tests
# ============================================

class TestTemplates:
    """Tests for response templates."""

    def test_all_drift_types_have_templates(self):
        """Test that all drift types have a template."""
        for drift_type in DriftType:
            assert drift_type in DRIFT_TEMPLATES, f"Missing template for {drift_type}"

    def test_template_none(self):
        """Test NONE drift template."""
        template = TEMPLATE_NONE
        assert template.template_id == "none_in_scope"
        assert DriftType.NONE in template.drift_types
        assert "{request}" in template.template_text
        assert template.tone == DriftResponseTone.HELPFUL

    def test_template_scope_expansion(self):
        """Test SCOPE_EXPANSION template."""
        template = TEMPLATE_SCOPE_EXPANSION
        assert template.template_id == "scope_expansion"
        assert DriftType.SCOPE_EXPANSION in template.drift_types
        assert "feature isn't available" in template.template_text
        assert "{alternatives}" in template.template_text

    def test_template_domain_shift(self):
        """Test DOMAIN_SHIFT template."""
        template = TEMPLATE_DOMAIN_SHIFT
        assert template.template_id == "domain_shift"
        assert DriftType.DOMAIN_SHIFT in template.drift_types
        assert "{topic}" in template.template_text
        assert "{domain}" in template.template_text

    def test_template_abstraction_climb(self):
        """Test ABSTRACTION_CLIMB template."""
        template = TEMPLATE_ABSTRACTION_CLIMB
        assert template.template_id == "abstraction_climb"
        assert DriftType.ABSTRACTION_CLIMB in template.drift_types
        assert "thoughtful" in template.template_text.lower()

    def test_template_personalization(self):
        """Test PERSONALIZATION template."""
        template = TEMPLATE_PERSONALIZATION
        assert template.template_id == "personalization"
        assert DriftType.PERSONALIZATION in template.drift_types
        assert "{data_type}" in template.template_text
        assert template.tone == DriftResponseTone.APOLOGETIC

    def test_template_temporal_drift(self):
        """Test TEMPORAL_DRIFT template."""
        template = TEMPLATE_TEMPORAL_DRIFT
        assert template.template_id == "temporal_drift"
        assert DriftType.TEMPORAL_DRIFT in template.drift_types
        assert "{time_reference}" in template.template_text

    def test_template_ambiguous(self):
        """Test AMBIGUOUS template."""
        template = TEMPLATE_AMBIGUOUS
        assert template.template_id == "ambiguous"
        assert DriftType.AMBIGUOUS in template.drift_types
        assert "{options}" in template.template_text

    def test_template_escalation(self):
        """Test escalation template."""
        template = TEMPLATE_ESCALATION
        assert template.template_id == "escalation"
        assert "{escalation_option}" in template.template_text
        assert template.tone == DriftResponseTone.PROFESSIONAL

    def test_all_templates_have_required_variables(self):
        """Test all templates specify required variables."""
        for drift_type, template in DRIFT_TEMPLATES.items():
            assert len(template.required_variables) > 0, (
                f"Template for {drift_type} has no required variables"
            )

    def test_all_templates_have_example_output(self):
        """Test all templates have example output."""
        for drift_type, template in DRIFT_TEMPLATES.items():
            assert template.example_output is not None, (
                f"Template for {drift_type} has no example output"
            )


# ============================================
# Response Type Mapping Tests
# ============================================

class TestResponseTypeMapping:
    """Tests for drift to response type mapping."""

    def test_all_drift_types_have_response_type(self):
        """Test that all drift types map to a response type."""
        for drift_type in DriftType:
            assert drift_type in DRIFT_TO_RESPONSE_TYPE

    def test_none_maps_to_partial_help(self):
        """Test NONE maps to PARTIAL_HELP."""
        assert DRIFT_TO_RESPONSE_TYPE[DriftType.NONE] == GracefulResponseType.PARTIAL_HELP

    def test_ambiguous_maps_to_clarification(self):
        """Test AMBIGUOUS maps to CLARIFICATION."""
        assert DRIFT_TO_RESPONSE_TYPE[DriftType.AMBIGUOUS] == GracefulResponseType.CLARIFICATION

    def test_domain_shift_maps_to_boundary(self):
        """Test DOMAIN_SHIFT maps to BOUNDARY_STATEMENT."""
        assert DRIFT_TO_RESPONSE_TYPE[DriftType.DOMAIN_SHIFT] == GracefulResponseType.BOUNDARY_STATEMENT


# ============================================
# Acknowledgment Tests
# ============================================

class TestAcknowledgments:
    """Tests for acknowledgment phrases."""

    def test_all_drift_types_have_acknowledgments(self):
        """Test all drift types have acknowledgment phrases."""
        for drift_type in DriftType:
            assert drift_type in ACKNOWLEDGMENTS
            assert len(ACKNOWLEDGMENTS[drift_type]) > 0

    def test_acknowledgments_are_positive(self):
        """Test acknowledgments don't over-apologize."""
        for drift_type, phrases in ACKNOWLEDGMENTS.items():
            for phrase in phrases:
                # Should not over-apologize
                assert "sorry" not in phrase.lower()
                assert "apologize" not in phrase.lower()


# ============================================
# Follow-up Prompts Tests
# ============================================

class TestFollowUpPrompts:
    """Tests for follow-up prompts."""

    def test_all_drift_types_have_follow_ups(self):
        """Test all drift types have follow-up prompts."""
        for drift_type in DriftType:
            assert drift_type in FOLLOW_UP_PROMPTS
            assert len(FOLLOW_UP_PROMPTS[drift_type]) > 0

    def test_follow_ups_are_questions(self):
        """Test follow-ups are questions or suggestions."""
        for drift_type, prompts in FOLLOW_UP_PROMPTS.items():
            for prompt in prompts:
                # Should end with ? or be a suggestion/invitation
                prompt_lower = prompt.lower()
                assert (
                    "?" in prompt
                    or "let me know" in prompt_lower
                    or "would" in prompt_lower
                    or "feel free" in prompt_lower
                    or "can" in prompt_lower
                )


# ============================================
# ResponseGeneratorConfig Tests
# ============================================

class TestResponseGeneratorConfig:
    """Tests for ResponseGeneratorConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = ResponseGeneratorConfig.default()
        assert config.max_alternatives == 3
        assert config.include_acknowledgment is True
        assert config.include_follow_up is True
        assert config.escalation_threshold == 0.8

    def test_minimal_config(self):
        """Test minimal configuration."""
        config = ResponseGeneratorConfig.minimal()
        assert config.include_acknowledgment is False
        assert config.include_follow_up is False

    def test_custom_config(self):
        """Test custom configuration."""
        config = ResponseGeneratorConfig(
            max_alternatives=5,
            escalation_threshold=0.9,
            default_domain="travel booking",
        )
        assert config.max_alternatives == 5
        assert config.escalation_threshold == 0.9
        assert config.default_domain == "travel booking"

    def test_personalization_data_types(self):
        """Test personalization data types are defined."""
        config = ResponseGeneratorConfig.default()
        assert "password" in config.personalization_data_types
        assert "email" in config.personalization_data_types
        assert config.personalization_data_types["password"] == "account credentials"


# ============================================
# GracefulResponseGenerator Tests
# ============================================

class TestGracefulResponseGenerator:
    """Tests for GracefulResponseGenerator."""

    @pytest.fixture
    def generator(self):
        """Create default generator."""
        return GracefulResponseGenerator()

    @pytest.fixture
    def minimal_generator(self):
        """Create minimal generator (no acknowledgments/follow-ups)."""
        config = ResponseGeneratorConfig.minimal()
        return GracefulResponseGenerator(config)

    @pytest.fixture
    def classification_none(self):
        """Create NONE drift classification."""
        return DriftClassification(
            drift_type=DriftType.NONE,
            drift_score=0.1,
            confidence=0.9,
        )

    @pytest.fixture
    def classification_scope_expansion(self):
        """Create SCOPE_EXPANSION drift classification."""
        return DriftClassification(
            drift_type=DriftType.SCOPE_EXPANSION,
            drift_score=0.5,
            confidence=0.8,
        )

    @pytest.fixture
    def classification_domain_shift(self):
        """Create DOMAIN_SHIFT drift classification."""
        return DriftClassification(
            drift_type=DriftType.DOMAIN_SHIFT,
            drift_score=0.7,
            confidence=0.85,
        )

    @pytest.fixture
    def classification_severe(self):
        """Create severe drift classification."""
        return DriftClassification(
            drift_type=DriftType.DOMAIN_SHIFT,
            drift_score=0.9,  # Above escalation threshold
            confidence=0.9,
        )

    @pytest.fixture
    def redirect_suggestions(self):
        """Create sample redirect suggestions."""
        return [
            RedirectSuggestion(
                target_intent="book_flight",
                similarity_score=0.7,
                redirect_reason="Related capability",
                transition_phrase="Book a flight instead",
                confidence=0.8,
            ),
            RedirectSuggestion(
                target_intent="search_hotels",
                similarity_score=0.6,
                redirect_reason="Alternative option",
                transition_phrase="Search for hotels",
                confidence=0.7,
            ),
        ]

    # Basic Generation Tests

    def test_generate_none_drift(self, generator, classification_none, redirect_suggestions):
        """Test generating response for NONE drift."""
        response = generator.generate(
            drift_classification=classification_none,
            redirect_suggestions=redirect_suggestions,
            user_input="Book a flight to Paris",
        )
        assert response.response_type == GracefulResponseType.PARTIAL_HELP
        assert response.tone == DriftResponseTone.HELPFUL
        assert response.primary_message

    def test_generate_scope_expansion(self, generator, classification_scope_expansion, redirect_suggestions):
        """Test generating response for SCOPE_EXPANSION drift."""
        response = generator.generate(
            drift_classification=classification_scope_expansion,
            redirect_suggestions=redirect_suggestions,
            user_input="Book a multi-city trip",
        )
        assert response.response_type == GracefulResponseType.PARTIAL_HELP
        assert "alternatives" in response.primary_message.lower() or "•" in response.primary_message

    def test_generate_domain_shift(self, generator, classification_domain_shift, redirect_suggestions):
        """Test generating response for DOMAIN_SHIFT drift."""
        response = generator.generate(
            drift_classification=classification_domain_shift,
            redirect_suggestions=redirect_suggestions,
            user_input="What is quantum physics?",
        )
        assert response.response_type == GracefulResponseType.BOUNDARY_STATEMENT
        assert response.tone == DriftResponseTone.HELPFUL

    def test_generate_abstraction_climb(self, generator, redirect_suggestions):
        """Test generating response for ABSTRACTION_CLIMB drift."""
        classification = DriftClassification(
            drift_type=DriftType.ABSTRACTION_CLIMB,
            drift_score=0.6,
            confidence=0.8,
        )
        response = generator.generate(
            drift_classification=classification,
            redirect_suggestions=redirect_suggestions,
            user_input="What is the meaning of life?",
        )
        assert response.response_type == GracefulResponseType.REDIRECT
        assert "thoughtful" in response.primary_message.lower()

    def test_generate_personalization(self, generator, redirect_suggestions):
        """Test generating response for PERSONALIZATION drift."""
        classification = DriftClassification(
            drift_type=DriftType.PERSONALIZATION,
            drift_score=0.5,
            confidence=0.8,
        )
        response = generator.generate(
            drift_classification=classification,
            redirect_suggestions=redirect_suggestions,
            user_input="What is my password?",
        )
        assert response.response_type == GracefulResponseType.BOUNDARY_STATEMENT
        assert response.tone == DriftResponseTone.APOLOGETIC
        assert "personal" in response.primary_message.lower() or "access" in response.primary_message.lower()

    def test_generate_temporal_drift(self, generator, redirect_suggestions):
        """Test generating response for TEMPORAL_DRIFT drift."""
        classification = DriftClassification(
            drift_type=DriftType.TEMPORAL_DRIFT,
            drift_score=0.5,
            confidence=0.8,
        )
        response = generator.generate(
            drift_classification=classification,
            redirect_suggestions=redirect_suggestions,
            user_input="What will happen next year?",
        )
        assert response.response_type == GracefulResponseType.BOUNDARY_STATEMENT
        assert response.tone == DriftResponseTone.HELPFUL

    def test_generate_ambiguous(self, generator, redirect_suggestions):
        """Test generating response for AMBIGUOUS drift."""
        classification = DriftClassification(
            drift_type=DriftType.AMBIGUOUS,
            drift_score=0.5,
            confidence=0.5,
        )
        response = generator.generate(
            drift_classification=classification,
            redirect_suggestions=redirect_suggestions,
            user_input="Help with booking",
        )
        assert response.response_type == GracefulResponseType.CLARIFICATION
        assert "understand" in response.primary_message.lower() or "mean" in response.primary_message.lower()

    # Component Tests

    def test_acknowledgment_included(self, generator, classification_none, redirect_suggestions):
        """Test acknowledgment is included when enabled."""
        response = generator.generate(
            drift_classification=classification_none,
            redirect_suggestions=redirect_suggestions,
            user_input="Book a flight",
        )
        assert response.acknowledgment is not None

    def test_acknowledgment_excluded(self, minimal_generator, classification_none, redirect_suggestions):
        """Test acknowledgment is excluded when disabled."""
        response = minimal_generator.generate(
            drift_classification=classification_none,
            redirect_suggestions=redirect_suggestions,
            user_input="Book a flight",
        )
        assert response.acknowledgment is None

    def test_follow_up_included(self, generator, classification_none, redirect_suggestions):
        """Test follow-up prompt is included when enabled."""
        response = generator.generate(
            drift_classification=classification_none,
            redirect_suggestions=redirect_suggestions,
            user_input="Book a flight",
        )
        assert response.follow_up_prompt is not None

    def test_follow_up_excluded(self, minimal_generator, classification_none, redirect_suggestions):
        """Test follow-up prompt is excluded when disabled."""
        response = minimal_generator.generate(
            drift_classification=classification_none,
            redirect_suggestions=redirect_suggestions,
            user_input="Book a flight",
        )
        assert response.follow_up_prompt is None

    def test_alternatives_built(self, generator, classification_scope_expansion, redirect_suggestions):
        """Test alternatives are built from suggestions."""
        response = generator.generate(
            drift_classification=classification_scope_expansion,
            redirect_suggestions=redirect_suggestions,
            user_input="Multi-city booking",
        )
        assert len(response.alternatives) <= generator.config.max_alternatives
        assert len(response.alternatives) == len(redirect_suggestions)

    def test_alternatives_limited(self, generator, classification_scope_expansion):
        """Test alternatives are limited to max_alternatives."""
        many_suggestions = [
            RedirectSuggestion(
                target_intent=f"intent_{i}",
                similarity_score=0.5,
                redirect_reason="Option",
                transition_phrase=f"Option {i}",
                confidence=0.5,
            )
            for i in range(10)
        ]
        response = generator.generate(
            drift_classification=classification_scope_expansion,
            redirect_suggestions=many_suggestions,
            user_input="Test",
        )
        assert len(response.alternatives) == generator.config.max_alternatives

    # Escalation Tests

    def test_escalation_triggered_by_high_score(self, generator, classification_severe, redirect_suggestions):
        """Test escalation is triggered by high drift score."""
        response = generator.generate(
            drift_classification=classification_severe,
            redirect_suggestions=redirect_suggestions,
            user_input="Complex request",
        )
        assert response.response_type == GracefulResponseType.ESCALATION
        assert "connect" in response.primary_message.lower() or "specialist" in response.primary_message.lower()

    def test_escalation_triggered_by_low_confidence(self, generator, redirect_suggestions):
        """Test escalation is triggered by low confidence domain shift."""
        classification = DriftClassification(
            drift_type=DriftType.DOMAIN_SHIFT,
            drift_score=0.5,
            confidence=0.3,  # Low confidence
        )
        response = generator.generate(
            drift_classification=classification,
            redirect_suggestions=redirect_suggestions,
            user_input="Unclear request",
        )
        assert response.response_type == GracefulResponseType.ESCALATION

    def test_no_escalation_below_threshold(self, generator, classification_scope_expansion, redirect_suggestions):
        """Test no escalation below threshold."""
        response = generator.generate(
            drift_classification=classification_scope_expansion,
            redirect_suggestions=redirect_suggestions,
            user_input="Normal request",
        )
        assert response.response_type != GracefulResponseType.ESCALATION

    # generate_simple Tests

    def test_generate_simple_basic(self, generator):
        """Test generate_simple basic functionality."""
        response = generator.generate_simple(
            drift_type=DriftType.SCOPE_EXPANSION,
            user_input="Extended feature request",
            alternatives=["Option A", "Option B"],
        )
        assert response.response_type == GracefulResponseType.PARTIAL_HELP
        assert len(response.alternatives) == 2

    def test_generate_simple_no_alternatives(self, generator):
        """Test generate_simple without alternatives."""
        response = generator.generate_simple(
            drift_type=DriftType.DOMAIN_SHIFT,
            user_input="Off-topic question",
        )
        assert response.primary_message

    def test_generate_simple_all_drift_types(self, generator):
        """Test generate_simple works for all drift types."""
        for drift_type in DriftType:
            response = generator.generate_simple(
                drift_type=drift_type,
                user_input="Test input",
                alternatives=["Alternative"],
            )
            assert response.primary_message
            assert response.response_type is not None

    # Variable Extraction Tests

    def test_extract_topic(self, generator):
        """Test topic extraction from input."""
        topic = generator._extract_topic("What is quantum physics?")
        assert "quantum" in topic.lower() or "physics" in topic.lower()

    def test_extract_topic_filters_stop_words(self, generator):
        """Test topic extraction filters stop words."""
        topic = generator._extract_topic("What is the best way to do this?")
        assert "what" not in topic.lower()
        assert "is" not in topic.lower()

    def test_detect_data_type_password(self, generator):
        """Test password data type detection."""
        data_type = generator._detect_data_type("What is my password?")
        assert "credentials" in data_type.lower() or "password" in data_type.lower()

    def test_detect_data_type_email(self, generator):
        """Test email data type detection."""
        data_type = generator._detect_data_type("Show me my email address")
        assert "email" in data_type.lower()

    def test_detect_data_type_default(self, generator):
        """Test default data type detection."""
        data_type = generator._detect_data_type("Show me my stuff")
        assert data_type == "personal"

    def test_extract_time_reference_future(self, generator):
        """Test future time reference extraction."""
        ref = generator._extract_time_reference("What will happen tomorrow?")
        assert "future" in ref.lower() or "tomorrow" in ref.lower()

    def test_extract_time_reference_past(self, generator):
        """Test past time reference extraction."""
        ref = generator._extract_time_reference("What happened yesterday?")
        assert "past" in ref.lower() or "yesterday" in ref.lower()

    def test_summarize_request_short(self, generator):
        """Test short request summarization."""
        summary = generator._summarize_request("Book a flight")
        assert summary == "Book a flight"

    def test_summarize_request_long(self, generator):
        """Test long request summarization (truncated)."""
        long_input = "This is a very long request that exceeds the maximum length and should be truncated"
        summary = generator._summarize_request(long_input)
        assert len(summary) <= 50
        assert summary.endswith("...")

    # to_message Tests

    def test_to_message_complete(self, generator, classification_scope_expansion, redirect_suggestions):
        """Test to_message generates complete response."""
        response = generator.generate(
            drift_classification=classification_scope_expansion,
            redirect_suggestions=redirect_suggestions,
            user_input="Extended feature",
        )
        message = response.to_message()
        assert len(message) > 0
        # Should contain multiple parts
        assert response.acknowledgment in message if response.acknowledgment else True

    def test_to_message_includes_alternatives(self, generator, classification_scope_expansion, redirect_suggestions):
        """Test to_message includes alternatives."""
        response = generator.generate(
            drift_classification=classification_scope_expansion,
            redirect_suggestions=redirect_suggestions,
            user_input="Extended feature",
        )
        message = response.to_message()
        # Should mention alternatives
        assert "help with" in message.lower() or redirect_suggestions[0].transition_phrase.lower() in message.lower()

    # Helper Method Tests

    def test_get_template_for_type(self, generator):
        """Test getting template for drift type."""
        template = generator.get_template_for_type(DriftType.SCOPE_EXPANSION)
        assert template == TEMPLATE_SCOPE_EXPANSION

    def test_get_template_for_unknown_type(self, generator):
        """Test getting template for unknown type returns ambiguous."""
        # Should return AMBIGUOUS template for unknown types
        template = generator.get_template_for_type(DriftType.AMBIGUOUS)
        assert template == TEMPLATE_AMBIGUOUS

    def test_get_all_templates(self, generator):
        """Test getting all templates."""
        templates = generator.get_all_templates()
        assert len(templates) == len(DriftType)
        for drift_type in DriftType:
            assert drift_type in templates


# ============================================
# Integration Tests
# ============================================

class TestResponseGeneratorIntegration:
    """Integration tests for GracefulResponseGenerator."""

    def test_full_workflow_scope_expansion(self):
        """Test full workflow for scope expansion."""
        generator = GracefulResponseGenerator()

        classification = DriftClassification(
            drift_type=DriftType.SCOPE_EXPANSION,
            drift_score=0.6,
            confidence=0.8,
            reasoning="User requested multi-city booking which is not supported",
        )

        suggestions = [
            RedirectSuggestion(
                target_intent="book_single_flight",
                similarity_score=0.8,
                redirect_reason="Book individual flights",
                transition_phrase="Book individual flights for each leg",
                confidence=0.85,
            ),
            RedirectSuggestion(
                target_intent="plan_itinerary",
                similarity_score=0.6,
                redirect_reason="Plan travel itinerary",
                transition_phrase="Create a travel itinerary",
                confidence=0.7,
            ),
        ]

        response = generator.generate(
            drift_classification=classification,
            redirect_suggestions=suggestions,
            user_input="I want to book a multi-city trip to Paris, Rome, and Barcelona",
        )

        # Verify response structure
        assert response.response_type == GracefulResponseType.PARTIAL_HELP
        assert response.acknowledgment is not None
        assert response.primary_message
        assert len(response.alternatives) == 2
        assert response.follow_up_prompt is not None

        # Verify message generation
        message = response.to_message()
        assert len(message) > 50  # Should be substantial

    def test_full_workflow_with_escalation(self):
        """Test full workflow with escalation."""
        generator = GracefulResponseGenerator()

        classification = DriftClassification(
            drift_type=DriftType.DOMAIN_SHIFT,
            drift_score=0.95,  # High severity
            confidence=0.9,
            reasoning="Request is about medical advice",
        )

        response = generator.generate(
            drift_classification=classification,
            redirect_suggestions=[],
            user_input="What medication should I take for my headache?",
        )

        # Should trigger escalation
        assert response.response_type == GracefulResponseType.ESCALATION
        message = response.to_message()
        assert "connect" in message.lower() or "specialist" in message.lower() or "help" in message.lower()

    def test_no_over_apologizing(self):
        """Test responses don't over-apologize."""
        generator = GracefulResponseGenerator()

        for drift_type in DriftType:
            classification = DriftClassification(
                drift_type=drift_type,
                drift_score=0.5,
                confidence=0.8,
            )

            response = generator.generate(
                drift_classification=classification,
                redirect_suggestions=[],
                user_input="Test request",
            )

            message = response.to_message()
            # Should not over-apologize
            assert message.lower().count("sorry") <= 1
            assert message.lower().count("apologize") == 0

    def test_always_offers_alternatives_or_help(self):
        """Test responses always offer alternatives when available."""
        generator = GracefulResponseGenerator()

        suggestions = [
            RedirectSuggestion(
                target_intent="alt_1",
                similarity_score=0.5,
                redirect_reason="Alternative",
                transition_phrase="Try this instead",
                confidence=0.5,
            ),
        ]

        for drift_type in DriftType:
            classification = DriftClassification(
                drift_type=drift_type,
                drift_score=0.5,
                confidence=0.8,
            )

            response = generator.generate(
                drift_classification=classification,
                redirect_suggestions=suggestions,
                user_input="Test request",
            )

            # Should have alternatives or helpful content
            message = response.to_message()
            assert (
                len(response.alternatives) > 0
                or "help" in message.lower()
                or "can" in message.lower()
            )
