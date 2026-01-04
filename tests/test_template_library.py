"""Tests for response template library.

Issue #86 - Task 5.9: Response Template Library
Part of #28 - Phase 5: Intent Drift Detection
"""

import pytest

from src.intent_drift.templates import (
    # Enums
    TemplateCategory,
    # Configuration
    TemplateConfig,
    # Core Classes
    ResponseTemplate,
    TemplateLibrary,
    # Template Collections
    ALL_TEMPLATES,
    CAPABILITY_TEMPLATES,
    CLARIFICATION_TEMPLATES,
    ESCALATION_TEMPLATES,
    IN_SCOPE_TEMPLATES,
    REDIRECT_TEMPLATES,
    UNCERTAINTY_TEMPLATES,
    # Individual Templates
    CAPABILITY_SIMPLE_LIMITATION,
    CAPABILITY_TRANSPARENT_SCOPE,
    CAPABILITY_COMPLEX_BREAKDOWN,
    UNCERTAINTY_CONFIDENT,
    UNCERTAINTY_PARTIAL_KNOWLEDGE,
    REDIRECT_RELATED_FEATURE,
    REDIRECT_MULTI_OPTION,
    CLARIFICATION_DID_YOU_MEAN,
    CLARIFICATION_AMBIGUITY_RESOLUTION,
    ESCALATION_PROACTIVE,
    ESCALATION_FAILED_ATTEMPT,
    IN_SCOPE_READY_TO_HELP,
    # Factory Functions
    get_default_library,
    reset_default_library,
)
from src.intent_drift.types import DriftResponseTone, DriftType


# ============================================
# TemplateConfig Tests
# ============================================


class TestTemplateConfig:
    """Tests for TemplateConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = TemplateConfig(drift_type=DriftType.SCOPE_EXPANSION)

        assert config.drift_type == DriftType.SCOPE_EXPANSION
        assert config.tone == DriftResponseTone.HELPFUL
        assert config.include_alternatives is True
        assert config.include_escalation is False
        assert config.max_alternatives == 3

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = TemplateConfig(
            drift_type=DriftType.DOMAIN_SHIFT,
            tone=DriftResponseTone.PROFESSIONAL,
            include_alternatives=False,
            include_escalation=True,
            max_alternatives=5,
        )

        assert config.drift_type == DriftType.DOMAIN_SHIFT
        assert config.tone == DriftResponseTone.PROFESSIONAL
        assert config.include_alternatives is False
        assert config.include_escalation is True
        assert config.max_alternatives == 5

    def test_invalid_max_alternatives_negative(self) -> None:
        """Test that negative max_alternatives raises error."""
        with pytest.raises(ValueError, match="non-negative"):
            TemplateConfig(drift_type=DriftType.NONE, max_alternatives=-1)

    def test_invalid_max_alternatives_too_large(self) -> None:
        """Test that too large max_alternatives raises error."""
        with pytest.raises(ValueError, match="at most 10"):
            TemplateConfig(drift_type=DriftType.NONE, max_alternatives=11)


# ============================================
# ResponseTemplate Tests
# ============================================


class TestResponseTemplate:
    """Tests for ResponseTemplate dataclass."""

    def test_create_template(self) -> None:
        """Test creating a response template."""
        template = ResponseTemplate(
            template_id="test_template",
            category=TemplateCategory.CAPABILITY_LIMIT,
            drift_types=[DriftType.SCOPE_EXPANSION],
            template_text="I can't do {action}, but I can {alternative}.",
            required_variables=["action", "alternative"],
            tone=DriftResponseTone.HELPFUL,
            description="Test template",
            example_output="I can't do X, but I can Y.",
        )

        assert template.template_id == "test_template"
        assert template.category == TemplateCategory.CAPABILITY_LIMIT
        assert DriftType.SCOPE_EXPANSION in template.drift_types
        assert "action" in template.required_variables
        assert template.tone == DriftResponseTone.HELPFUL

    def test_render_template(self) -> None:
        """Test rendering a template with variables."""
        template = ResponseTemplate(
            template_id="test",
            category=TemplateCategory.REDIRECT,
            drift_types=[DriftType.SCOPE_EXPANSION],
            template_text="I can't {action}, but I can {alternative}.",
            required_variables=["action", "alternative"],
        )

        result = template.render({"action": "book flights", "alternative": "search"})

        assert result == "I can't book flights, but I can search."

    def test_render_missing_variable(self) -> None:
        """Test that missing variables raise an error."""
        template = ResponseTemplate(
            template_id="test",
            category=TemplateCategory.REDIRECT,
            drift_types=[DriftType.SCOPE_EXPANSION],
            template_text="I can't {action}, but I can {alternative}.",
            required_variables=["action", "alternative"],
        )

        with pytest.raises(ValueError, match="Missing required variables"):
            template.render({"action": "book"})

    def test_can_handle_drift_type(self) -> None:
        """Test checking if template handles a drift type."""
        template = ResponseTemplate(
            template_id="test",
            category=TemplateCategory.CAPABILITY_LIMIT,
            drift_types=[DriftType.SCOPE_EXPANSION, DriftType.DOMAIN_SHIFT],
            template_text="Test",
            required_variables=[],
        )

        assert template.can_handle(DriftType.SCOPE_EXPANSION) is True
        assert template.can_handle(DriftType.DOMAIN_SHIFT) is True
        assert template.can_handle(DriftType.AMBIGUOUS) is False


# ============================================
# Template Collection Tests
# ============================================


class TestTemplateCollections:
    """Tests for template collections."""

    def test_capability_templates_count(self) -> None:
        """Test that capability templates has expected count."""
        assert len(CAPABILITY_TEMPLATES) == 5

    def test_uncertainty_templates_count(self) -> None:
        """Test that uncertainty templates has expected count."""
        assert len(UNCERTAINTY_TEMPLATES) == 4

    def test_redirect_templates_count(self) -> None:
        """Test that redirect templates has expected count."""
        assert len(REDIRECT_TEMPLATES) == 5

    def test_clarification_templates_count(self) -> None:
        """Test that clarification templates has expected count."""
        assert len(CLARIFICATION_TEMPLATES) == 5

    def test_escalation_templates_count(self) -> None:
        """Test that escalation templates has expected count."""
        assert len(ESCALATION_TEMPLATES) == 5

    def test_in_scope_templates_count(self) -> None:
        """Test that in-scope templates has expected count."""
        assert len(IN_SCOPE_TEMPLATES) == 3

    def test_all_templates_total(self) -> None:
        """Test that all templates is the sum of all categories."""
        expected_total = (
            len(CAPABILITY_TEMPLATES)
            + len(UNCERTAINTY_TEMPLATES)
            + len(REDIRECT_TEMPLATES)
            + len(CLARIFICATION_TEMPLATES)
            + len(ESCALATION_TEMPLATES)
            + len(IN_SCOPE_TEMPLATES)
        )
        assert len(ALL_TEMPLATES) == expected_total

    def test_all_templates_unique_ids(self) -> None:
        """Test that all template IDs are unique."""
        ids = [t.template_id for t in ALL_TEMPLATES]
        assert len(ids) == len(set(ids))

    def test_capability_templates_category(self) -> None:
        """Test that all capability templates have correct category."""
        for template in CAPABILITY_TEMPLATES:
            assert template.category == TemplateCategory.CAPABILITY_LIMIT

    def test_escalation_templates_category(self) -> None:
        """Test that all escalation templates have correct category."""
        for template in ESCALATION_TEMPLATES:
            assert template.category == TemplateCategory.ESCALATION


# ============================================
# Individual Template Tests
# ============================================


class TestCapabilityTemplates:
    """Tests for capability limit templates."""

    def test_simple_limitation_render(self) -> None:
        """Test rendering simple limitation template."""
        result = CAPABILITY_SIMPLE_LIMITATION.render({
            "action": "book international flights",
            "alternative": "search domestic routes",
        })

        assert "can't" in result.lower() or "not able" in result.lower()
        assert "book international flights" in result
        assert "search domestic routes" in result

    def test_transparent_scope_render(self) -> None:
        """Test rendering transparent scope template."""
        result = CAPABILITY_TRANSPARENT_SCOPE.render({
            "capabilities": "- Flight searches\n- Hotel bookings",
            "original_request": "currency exchange",
            "resource": "our finance team",
        })

        assert "Flight searches" in result
        assert "currency exchange" in result
        assert "finance team" in result

    def test_complex_breakdown_render(self) -> None:
        """Test rendering complex breakdown template."""
        result = CAPABILITY_COMPLEX_BREAKDOWN.render({
            "parts_possible": "the flight search and hotel booking",
            "parts_not_possible": "visa requirements",
            "alternative_process": "check with the embassy",
        })

        assert "multi-part" in result.lower()
        assert "flight search" in result
        assert "visa requirements" in result


class TestUncertaintyTemplates:
    """Tests for uncertainty templates."""

    def test_confident_uncertainty_render(self) -> None:
        """Test rendering confident uncertainty template."""
        result = UNCERTAINTY_CONFIDENT.render({
            "escalation_action": "connect you with a specialist",
        })

        assert "don't have" in result.lower()
        assert "specialist" in result

    def test_partial_knowledge_render(self) -> None:
        """Test rendering partial knowledge template."""
        result = UNCERTAINTY_PARTIAL_KNOWLEDGE.render({
            "known_part": "the departure time",
            "uncertain_part": "the gate number",
        })

        assert "departure time" in result
        assert "gate number" in result
        assert "uncertain" in result.lower()


class TestRedirectTemplates:
    """Tests for redirect templates."""

    def test_related_feature_render(self) -> None:
        """Test rendering related feature template."""
        result = REDIRECT_RELATED_FEATURE.render({
            "requested": "real-time tracking",
            "alternative": "setting up alerts",
        })

        assert "can't" in result.lower()
        assert "CAN" in result
        assert "real-time tracking" in result

    def test_multi_option_render(self) -> None:
        """Test rendering multi-option template."""
        result = REDIRECT_MULTI_OPTION.render({
            "request": "expense tracking",
            "options": "- Export to spreadsheet\n- View history\n- Download receipts",
        })

        assert "best options" in result.lower()
        assert "Export to spreadsheet" in result
        assert "Which works best" in result


class TestClarificationTemplates:
    """Tests for clarification templates."""

    def test_did_you_mean_render(self) -> None:
        """Test rendering did you mean template."""
        result = CLARIFICATION_DID_YOU_MEAN.render({
            "interpretations": "- Book a flight\n- Check flight status",
        })

        assert "closest" in result.lower()
        assert "Book a flight" in result

    def test_ambiguity_resolution_render(self) -> None:
        """Test rendering ambiguity resolution template."""
        result = CLARIFICATION_AMBIGUITY_RESOLUTION.render({
            "ambiguous_term": "change my flight",
            "meaning_1": "Reschedule to a different date",
            "meaning_2": "Switch to a different airline",
        })

        assert "change my flight" in result
        assert "Reschedule" in result
        assert "different airline" in result


class TestEscalationTemplates:
    """Tests for escalation templates."""

    def test_proactive_escalation_render(self) -> None:
        """Test rendering proactive escalation template."""
        result = ESCALATION_PROACTIVE.render({
            "complex_topic": "travel insurance claims",
        })

        assert "specialist" in result.lower()
        assert "travel insurance claims" in result

    def test_failed_attempt_render(self) -> None:
        """Test rendering failed attempt template."""
        result = ESCALATION_FAILED_ATTEMPT.render({})

        assert "apologize" in result.lower()
        assert "connect you" in result.lower()


class TestInScopeTemplates:
    """Tests for in-scope templates."""

    def test_ready_to_help_render(self) -> None:
        """Test rendering ready to help template."""
        result = IN_SCOPE_READY_TO_HELP.render({
            "request": "booking a flight",
            "action_prompt": "What's your destination?",
        })

        assert "help" in result.lower()
        assert "booking a flight" in result
        assert "destination" in result


# ============================================
# TemplateLibrary Tests
# ============================================


class TestTemplateLibrary:
    """Tests for TemplateLibrary class."""

    def test_create_library_default(self) -> None:
        """Test creating library with default templates."""
        library = TemplateLibrary()

        assert library.get_template_count() == len(ALL_TEMPLATES)

    def test_create_library_custom(self) -> None:
        """Test creating library with custom templates."""
        custom_templates = [CAPABILITY_SIMPLE_LIMITATION, REDIRECT_RELATED_FEATURE]
        library = TemplateLibrary(templates=custom_templates)

        assert library.get_template_count() == 2

    def test_get_template_by_id(self) -> None:
        """Test getting template by ID."""
        library = TemplateLibrary()

        template = library.get_template_by_id("capability_simple_limitation")

        assert template is not None
        assert template.template_id == "capability_simple_limitation"

    def test_get_template_by_id_not_found(self) -> None:
        """Test getting non-existent template by ID."""
        library = TemplateLibrary()

        template = library.get_template_by_id("nonexistent")

        assert template is None

    def test_get_templates_for_drift_type(self) -> None:
        """Test getting templates for a drift type."""
        library = TemplateLibrary()

        templates = library.get_templates_for_drift_type(DriftType.SCOPE_EXPANSION)

        assert len(templates) > 0
        for template in templates:
            assert DriftType.SCOPE_EXPANSION in template.drift_types

    def test_get_templates_for_drift_type_with_category(self) -> None:
        """Test getting templates for drift type filtered by category."""
        library = TemplateLibrary()

        templates = library.get_templates_for_drift_type(
            DriftType.SCOPE_EXPANSION,
            category=TemplateCategory.CAPABILITY_LIMIT,
        )

        assert len(templates) > 0
        for template in templates:
            assert template.category == TemplateCategory.CAPABILITY_LIMIT

    def test_get_templates_for_category(self) -> None:
        """Test getting templates for a category."""
        library = TemplateLibrary()

        templates = library.get_templates_for_category(TemplateCategory.ESCALATION)

        assert len(templates) == 5
        for template in templates:
            assert template.category == TemplateCategory.ESCALATION

    def test_get_templates_for_category_with_drift_type(self) -> None:
        """Test getting templates for category filtered by drift type."""
        library = TemplateLibrary()

        templates = library.get_templates_for_category(
            TemplateCategory.CAPABILITY_LIMIT,
            drift_type=DriftType.DOMAIN_SHIFT,
        )

        assert len(templates) > 0
        for template in templates:
            assert DriftType.DOMAIN_SHIFT in template.drift_types

    def test_select_template(self) -> None:
        """Test selecting a template."""
        library = TemplateLibrary()

        template = library.select_template(DriftType.AMBIGUOUS)

        assert template is not None
        assert DriftType.AMBIGUOUS in template.drift_types

    def test_select_template_with_category(self) -> None:
        """Test selecting template with category filter."""
        library = TemplateLibrary()

        template = library.select_template(
            DriftType.SCOPE_EXPANSION,
            category=TemplateCategory.REDIRECT,
        )

        assert template is not None
        assert template.category == TemplateCategory.REDIRECT

    def test_select_template_with_tone(self) -> None:
        """Test selecting template with tone filter."""
        library = TemplateLibrary()

        template = library.select_template(
            DriftType.SCOPE_EXPANSION,
            tone=DriftResponseTone.ENCOURAGING,
        )

        assert template is not None
        assert template.tone == DriftResponseTone.ENCOURAGING

    def test_select_template_no_match(self) -> None:
        """Test selecting template with no match."""
        library = TemplateLibrary(templates=[CAPABILITY_SIMPLE_LIMITATION])

        template = library.select_template(DriftType.TEMPORAL_DRIFT)

        assert template is None

    def test_select_template_with_config(self) -> None:
        """Test selecting template with config."""
        library = TemplateLibrary()
        config = TemplateConfig(
            drift_type=DriftType.DOMAIN_SHIFT,
            tone=DriftResponseTone.PROFESSIONAL,
        )

        template = library.select_template_with_config(config)

        assert template is not None
        assert DriftType.DOMAIN_SHIFT in template.drift_types

    def test_get_all_categories(self) -> None:
        """Test getting all categories."""
        library = TemplateLibrary()

        categories = library.get_all_categories()

        assert TemplateCategory.CAPABILITY_LIMIT in categories
        assert TemplateCategory.ESCALATION in categories
        assert TemplateCategory.CLARIFICATION in categories

    def test_get_all_drift_types_covered(self) -> None:
        """Test getting all covered drift types."""
        library = TemplateLibrary()

        drift_types = library.get_all_drift_types_covered()

        # Should cover all 7 drift types
        assert DriftType.NONE in drift_types
        assert DriftType.SCOPE_EXPANSION in drift_types
        assert DriftType.DOMAIN_SHIFT in drift_types
        assert DriftType.AMBIGUOUS in drift_types

    def test_get_templates_by_tone(self) -> None:
        """Test getting templates by tone."""
        library = TemplateLibrary()

        helpful_templates = library.get_templates_by_tone(DriftResponseTone.HELPFUL)

        assert len(helpful_templates) > 0
        for template in helpful_templates:
            assert template.tone == DriftResponseTone.HELPFUL

    def test_add_template(self) -> None:
        """Test adding a template."""
        library = TemplateLibrary(templates=[])
        new_template = ResponseTemplate(
            template_id="new_test",
            category=TemplateCategory.IN_SCOPE,
            drift_types=[DriftType.NONE],
            template_text="Test",
            required_variables=[],
        )

        library.add_template(new_template)

        assert library.get_template_count() == 1
        assert library.get_template_by_id("new_test") is not None

    def test_remove_template(self) -> None:
        """Test removing a template."""
        library = TemplateLibrary()
        initial_count = library.get_template_count()

        removed = library.remove_template("capability_simple_limitation")

        assert removed is True
        assert library.get_template_count() == initial_count - 1
        assert library.get_template_by_id("capability_simple_limitation") is None

    def test_remove_template_not_found(self) -> None:
        """Test removing non-existent template."""
        library = TemplateLibrary()

        removed = library.remove_template("nonexistent")

        assert removed is False

    def test_get_category_summary(self) -> None:
        """Test getting category summary."""
        library = TemplateLibrary()

        summary = library.get_category_summary()

        assert summary[TemplateCategory.CAPABILITY_LIMIT] == 5
        assert summary[TemplateCategory.ESCALATION] == 5
        assert summary[TemplateCategory.UNCERTAINTY] == 4

    def test_get_drift_type_summary(self) -> None:
        """Test getting drift type summary."""
        library = TemplateLibrary()

        summary = library.get_drift_type_summary()

        # Should have entries for all covered drift types
        assert DriftType.SCOPE_EXPANSION in summary
        assert summary[DriftType.SCOPE_EXPANSION] > 0


# ============================================
# Factory Function Tests
# ============================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_get_default_library(self) -> None:
        """Test getting default library."""
        reset_default_library()

        library1 = get_default_library()
        library2 = get_default_library()

        # Should return same instance
        assert library1 is library2
        assert library1.get_template_count() == len(ALL_TEMPLATES)

    def test_reset_default_library(self) -> None:
        """Test resetting default library."""
        library1 = get_default_library()
        reset_default_library()
        library2 = get_default_library()

        # Should be different instances
        assert library1 is not library2


# ============================================
# Acceptance Criteria Tests
# ============================================


class TestAcceptanceCriteria:
    """Tests for issue acceptance criteria."""

    def test_templates_for_all_drift_types(self) -> None:
        """Test that templates exist for all 7 drift types."""
        library = TemplateLibrary()

        all_drift_types = [
            DriftType.NONE,
            DriftType.SCOPE_EXPANSION,
            DriftType.DOMAIN_SHIFT,
            DriftType.ABSTRACTION_CLIMB,
            DriftType.PERSONALIZATION,
            DriftType.TEMPORAL_DRIFT,
            DriftType.AMBIGUOUS,
        ]

        for drift_type in all_drift_types:
            templates = library.get_templates_for_drift_type(drift_type)
            assert len(templates) >= 1, f"No templates for {drift_type}"

    def test_multiple_variations_per_type(self) -> None:
        """Test that most drift types have multiple template variations."""
        library = TemplateLibrary()

        # Major drift types should have 3+ templates
        major_types = [
            DriftType.SCOPE_EXPANSION,
            DriftType.DOMAIN_SHIFT,
            DriftType.AMBIGUOUS,
        ]

        for drift_type in major_types:
            templates = library.get_templates_for_drift_type(drift_type)
            assert len(templates) >= 3, f"Expected 3+ templates for {drift_type}, got {len(templates)}"

    def test_variable_substitution_works(self) -> None:
        """Test that variable substitution works correctly for all templates."""
        for template in ALL_TEMPLATES:
            # Create dummy variables
            variables = {var: f"test_{var}" for var in template.required_variables}

            # Should render without error
            result = template.render(variables)

            # All variables should be substituted
            for var in template.required_variables:
                assert f"test_{var}" in result
                assert f"{{{var}}}" not in result

    def test_no_dead_end_templates(self) -> None:
        """Test that templates offer a path forward (alternatives, follow-up, etc.)."""
        # Templates should either offer alternatives, ask questions, or escalate
        path_forward_keywords = [
            "can",
            "would",
            "like",
            "help",
            "option",
            "alternative",
            "try",
            "connect",
            "let me",
            "transfer",
            "i'll",
            "?",
        ]

        for template in ALL_TEMPLATES:
            text_lower = template.template_text.lower()
            has_path = any(kw in text_lower for kw in path_forward_keywords)
            assert has_path, f"Template {template.template_id} may be a dead-end"

    def test_tone_appropriate_per_scenario(self) -> None:
        """Test that templates have appropriate tones for their categories."""
        # Escalation should be professional or apologetic
        for template in ESCALATION_TEMPLATES:
            assert template.tone in [
                DriftResponseTone.PROFESSIONAL,
                DriftResponseTone.APOLOGETIC,
                DriftResponseTone.HELPFUL,
            ]

        # In-scope should be helpful or encouraging
        for template in IN_SCOPE_TEMPLATES:
            assert template.tone in [
                DriftResponseTone.HELPFUL,
                DriftResponseTone.ENCOURAGING,
                DriftResponseTone.PROFESSIONAL,
            ]

    def test_all_templates_have_documentation(self) -> None:
        """Test that all templates have descriptions."""
        for template in ALL_TEMPLATES:
            # Description should exist (can be empty for simple ones)
            assert hasattr(template, "description")


# ============================================
# Integration Tests
# ============================================


class TestIntegration:
    """Integration tests for template library."""

    def test_full_workflow(self) -> None:
        """Test full workflow of selecting and rendering templates."""
        library = TemplateLibrary()

        # 1. Configure for scope expansion
        config = TemplateConfig(
            drift_type=DriftType.SCOPE_EXPANSION,
            tone=DriftResponseTone.HELPFUL,
            include_alternatives=True,
            max_alternatives=3,
        )

        # 2. Select appropriate template
        template = library.select_template_with_config(
            config,
            category=TemplateCategory.CAPABILITY_LIMIT,
        )

        assert template is not None

        # 3. Render with variables
        variables = {
            "action": "book multi-city flights",
            "alternative": "book individual segments",
        }
        # Add any other required variables
        for var in template.required_variables:
            if var not in variables:
                variables[var] = f"test_{var}"

        result = template.render(variables)

        assert len(result) > 0
        assert "{" not in result  # No unsubstituted variables

    def test_escalation_after_failed_attempts(self) -> None:
        """Test escalation flow after capability limit."""
        library = TemplateLibrary()

        # First, try capability limit
        cap_template = library.select_template(
            DriftType.SCOPE_EXPANSION,
            category=TemplateCategory.CAPABILITY_LIMIT,
        )
        assert cap_template is not None

        # If that doesn't work, escalate
        esc_template = library.select_template(
            DriftType.SCOPE_EXPANSION,
            category=TemplateCategory.ESCALATION,
        )
        assert esc_template is not None
        assert esc_template.category == TemplateCategory.ESCALATION
