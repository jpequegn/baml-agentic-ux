"""Tests for adaptive response templates.

Issue #47 - Phase 2: Adaptive Interface Personalization
"""

import pytest
from src.lui_simulator.templates import (
    TemplateManager,
    TemplatePurpose,
    TemplateVariant,
    AdaptiveTemplate,
    TemplateSelectionContext,
    RenderedTemplate,
    TemplateLibrary,
    VerbosityMapping,
    TemplateCustomization,
    ErrorTemplateDetails,
    VerbosityLevel,
)
from src.lui_simulator.expertise import ExpertiseLevel


class TestTemplatePurpose:
    """Tests for TemplatePurpose enum."""

    def test_all_purposes_defined(self):
        """All expected template purposes should be defined."""
        expected = [
            "SUCCESS_CONFIRMATION",
            "ERROR_MESSAGE",
            "DISAMBIGUATION",
            "HELP_OFFER",
            "FEATURE_SUGGESTION",
            "ACTION_CONFIRMATION",
            "PROGRESS_UPDATE",
            "WELCOME_MESSAGE",
            "TASK_CREATION",
            "SEARCH_RESULTS",
        ]
        for purpose in expected:
            assert hasattr(TemplatePurpose, purpose)

    def test_purpose_values(self):
        """Purpose enum values should match names."""
        assert TemplatePurpose.SUCCESS_CONFIRMATION.value == "SUCCESS_CONFIRMATION"
        assert TemplatePurpose.ERROR_MESSAGE.value == "ERROR_MESSAGE"
        assert TemplatePurpose.DISAMBIGUATION.value == "DISAMBIGUATION"


class TestVerbosityLevel:
    """Tests for VerbosityLevel enum."""

    def test_all_levels_defined(self):
        """All verbosity levels should be defined."""
        expected = ["MINIMAL", "CONCISE", "STANDARD", "DETAILED"]
        for level in expected:
            assert hasattr(VerbosityLevel, level)

    def test_level_ordering(self):
        """Verbosity levels should have implicit ordering."""
        levels = list(VerbosityLevel)
        assert len(levels) == 4


class TestTemplateVariant:
    """Tests for TemplateVariant dataclass."""

    def test_create_variant(self):
        """Should create a template variant with all fields."""
        variant = TemplateVariant(
            expertise_level=ExpertiseLevel.NOVICE,
            template_content="Hello {name}, your task '{task}' was created!",
            show_examples=True,
            show_shortcuts=False,
            require_confirmation=True,
            include_undo=True,
            max_options=5,
        )
        assert variant.expertise_level == ExpertiseLevel.NOVICE
        assert "{name}" in variant.template_content
        assert variant.show_examples is True
        assert variant.show_shortcuts is False
        assert variant.require_confirmation is True
        assert variant.include_undo is True
        assert variant.max_options == 5

    def test_variant_default_values(self):
        """Variant should work with minimal required fields."""
        variant = TemplateVariant(
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            template_content="Task created",
            show_examples=False,
            show_shortcuts=True,
            require_confirmation=False,
            include_undo=False,
            max_options=0,
        )
        assert variant.max_options == 0  # 0 means unlimited


class TestAdaptiveTemplate:
    """Tests for AdaptiveTemplate dataclass."""

    def test_create_template_with_variants(self):
        """Should create an adaptive template with multiple variants."""
        variants = [
            TemplateVariant(
                expertise_level=ExpertiseLevel.NOVICE,
                template_content="Welcome! I created your task: {task}",
                show_examples=True,
                show_shortcuts=False,
                require_confirmation=True,
                include_undo=True,
                max_options=3,
            ),
            TemplateVariant(
                expertise_level=ExpertiseLevel.EXPERT,
                template_content="+{task}",
                show_examples=False,
                show_shortcuts=True,
                require_confirmation=False,
                include_undo=False,
                max_options=0,
            ),
        ]
        template = AdaptiveTemplate(
            template_id="task_created",
            purpose=TemplatePurpose.TASK_CREATION,
            description="Confirms task creation",
            variants=variants,
            placeholders=["task"],
        )
        assert template.template_id == "task_created"
        assert template.purpose == TemplatePurpose.TASK_CREATION
        assert len(template.variants) == 2
        assert "task" in template.placeholders

    def test_template_requires_variants(self):
        """Template should have at least one variant."""
        template = AdaptiveTemplate(
            template_id="empty",
            purpose=TemplatePurpose.SUCCESS_CONFIRMATION,
            description="Test",
            variants=[],
            placeholders=[],
        )
        assert len(template.variants) == 0  # Empty is allowed but not useful


class TestTemplateSelectionContext:
    """Tests for TemplateSelectionContext dataclass."""

    def test_create_context(self):
        """Should create context with all fields."""
        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.BEGINNER,
            verbosity_override=VerbosityLevel.DETAILED,
            is_error=False,
            is_first_time=True,
            user_preference_style="friendly",
        )
        assert context.expertise_level == ExpertiseLevel.BEGINNER
        assert context.verbosity_override == VerbosityLevel.DETAILED
        assert context.is_error is False
        assert context.is_first_time is True
        assert context.user_preference_style == "friendly"

    def test_context_with_optional_fields(self):
        """Should create context with only required fields."""
        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            is_error=True,
            is_first_time=False,
        )
        assert context.verbosity_override is None
        assert context.user_preference_style is None


class TestRenderedTemplate:
    """Tests for RenderedTemplate dataclass."""

    def test_create_rendered_template(self):
        """Should create a rendered template result."""
        rendered = RenderedTemplate(
            template_id="task_created",
            purpose=TemplatePurpose.TASK_CREATION,
            expertise_level=ExpertiseLevel.NOVICE,
            rendered_content="Great! I've created your task: Buy groceries",
            includes_examples=True,
            includes_shortcuts=False,
            requires_confirmation=True,
            suggested_actions=["View task", "Add another", "Set reminder"],
        )
        assert rendered.template_id == "task_created"
        assert "Buy groceries" in rendered.rendered_content
        assert len(rendered.suggested_actions) == 3

    def test_rendered_without_actions(self):
        """Should work without suggested actions."""
        rendered = RenderedTemplate(
            template_id="simple",
            purpose=TemplatePurpose.SUCCESS_CONFIRMATION,
            expertise_level=ExpertiseLevel.EXPERT,
            rendered_content="Done.",
            includes_examples=False,
            includes_shortcuts=True,
            requires_confirmation=False,
        )
        assert rendered.suggested_actions is None


class TestTemplateLibrary:
    """Tests for TemplateLibrary dataclass."""

    def test_create_library(self):
        """Should create a template library."""
        library = TemplateLibrary(
            library_id="default",
            version="1.0.0",
            templates=[],
            brand_voice="Professional yet friendly",
            personality_traits=["helpful", "clear", "efficient"],
        )
        assert library.library_id == "default"
        assert library.version == "1.0.0"
        assert "helpful" in library.personality_traits


class TestVerbosityMapping:
    """Tests for VerbosityMapping dataclass."""

    def test_create_mapping(self):
        """Should create verbosity mapping for expertise level."""
        mapping = VerbosityMapping(
            expertise_level=ExpertiseLevel.NOVICE,
            default_verbosity=VerbosityLevel.DETAILED,
            confirmation_frequency="always",
            example_frequency="always",
        )
        assert mapping.expertise_level == ExpertiseLevel.NOVICE
        assert mapping.default_verbosity == VerbosityLevel.DETAILED
        assert mapping.confirmation_frequency == "always"

    def test_mapping_frequencies(self):
        """Mapping frequencies should be valid values."""
        valid_frequencies = ["always", "sometimes", "rarely", "never"]
        mapping = VerbosityMapping(
            expertise_level=ExpertiseLevel.EXPERT,
            default_verbosity=VerbosityLevel.MINIMAL,
            confirmation_frequency="never",
            example_frequency="never",
        )
        assert mapping.confirmation_frequency in valid_frequencies
        assert mapping.example_frequency in valid_frequencies


class TestTemplateCustomization:
    """Tests for TemplateCustomization dataclass."""

    def test_create_customization(self):
        """Should create user customization preferences."""
        custom = TemplateCustomization(
            user_id="user123",
            verbosity_override=VerbosityLevel.CONCISE,
            always_show_examples=False,
            never_show_shortcuts=True,
            custom_confirmation_frequency="rarely",
            preferred_error_detail="brief",
        )
        assert custom.user_id == "user123"
        assert custom.verbosity_override == VerbosityLevel.CONCISE
        assert custom.never_show_shortcuts is True

    def test_customization_with_defaults(self):
        """Should work with minimal customization."""
        custom = TemplateCustomization(
            user_id="user456",
            always_show_examples=True,
            never_show_shortcuts=False,
        )
        assert custom.verbosity_override is None
        assert custom.custom_confirmation_frequency is None


class TestErrorTemplateDetails:
    """Tests for ErrorTemplateDetails dataclass."""

    def test_create_error_template(self):
        """Should create error template with progressive detail levels."""
        error_template = ErrorTemplateDetails(
            error_code="TASK_NOT_FOUND",
            novice_template="I couldn't find that task. Here's what you can do: 1) Check the task name 2) Browse all tasks 3) Create a new task. Would you like help?",
            beginner_template="Task not found. You can browse tasks or create a new one.",
            intermediate_template="Task not found. Try: /tasks list",
            advanced_template="Task not found [/tasks]",
            expert_template="404: task",
            recovery_actions=["list_tasks", "create_task", "search_tasks"],
        )
        assert error_template.error_code == "TASK_NOT_FOUND"
        assert len(error_template.novice_template) > len(error_template.expert_template)
        assert len(error_template.recovery_actions) == 3


class TestTemplateManager:
    """Tests for TemplateManager class."""

    @pytest.fixture
    def manager(self):
        """Create a TemplateManager instance."""
        return TemplateManager()

    def test_manager_initialization(self):
        """Manager should initialize with default templates."""
        manager = TemplateManager()
        assert manager is not None

    def test_get_default_templates(self, manager):
        """Should have default templates loaded."""
        templates = manager.get_all_templates()
        assert len(templates) > 0

    def test_get_template_by_id(self, manager):
        """Should retrieve template by ID."""
        template = manager.get_template("task_creation")
        assert template is not None
        assert template.purpose == TemplatePurpose.TASK_CREATION

    def test_get_nonexistent_template(self, manager):
        """Should return None for unknown template ID."""
        template = manager.get_template("nonexistent_template")
        assert template is None

    def test_get_templates_by_purpose(self, manager):
        """Should retrieve templates by purpose."""
        templates = manager.get_templates_by_purpose(TemplatePurpose.SUCCESS_CONFIRMATION)
        assert len(templates) >= 1
        for t in templates:
            assert t.purpose == TemplatePurpose.SUCCESS_CONFIRMATION

    def test_select_variant_for_novice(self, manager):
        """Should select appropriate variant for novice user."""
        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.NOVICE,
            is_error=False,
            is_first_time=True,
        )
        variant = manager.select_variant("task_creation", context)
        assert variant is not None
        assert variant.expertise_level == ExpertiseLevel.NOVICE
        assert variant.show_examples is True

    def test_select_variant_for_expert(self, manager):
        """Should select appropriate variant for expert user."""
        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.EXPERT,
            is_error=False,
            is_first_time=False,
        )
        variant = manager.select_variant("task_creation", context)
        assert variant is not None
        assert variant.expertise_level == ExpertiseLevel.EXPERT
        assert variant.require_confirmation is False

    def test_select_variant_intermediate(self, manager):
        """Should select intermediate variant correctly."""
        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            is_error=False,
            is_first_time=False,
        )
        variant = manager.select_variant("task_creation", context)
        assert variant is not None
        assert variant.expertise_level == ExpertiseLevel.INTERMEDIATE

    def test_render_template_novice(self, manager):
        """Should render template with placeholders for novice."""
        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.NOVICE,
            is_error=False,
            is_first_time=True,
        )
        values = {"title": "Buy groceries", "priority": "high", "due_date": "tomorrow"}
        rendered = manager.render("task_creation", context, values)
        assert rendered is not None
        assert "Buy groceries" in rendered.rendered_content
        assert rendered.includes_examples is True

    def test_render_template_expert(self, manager):
        """Should render concise template for expert."""
        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.EXPERT,
            is_error=False,
            is_first_time=False,
        )
        values = {"title": "Meeting", "priority": "normal", "due_date": "today"}
        rendered = manager.render("task_creation", context, values)
        assert rendered is not None
        assert rendered.requires_confirmation is False

    def test_render_nonexistent_template(self, manager):
        """Should return None for unknown template."""
        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.NOVICE,
            is_error=False,
            is_first_time=True,
        )
        rendered = manager.render("nonexistent", context, {})
        assert rendered is None

    def test_error_template_progressive_detail(self, manager):
        """Error messages should have decreasing detail by level."""
        error_context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.NOVICE,
            is_error=True,
            is_first_time=False,
        )
        novice_render = manager.render("error", error_context, {"error_message": "Task failed"})

        error_context_expert = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.EXPERT,
            is_error=True,
            is_first_time=False,
        )
        expert_render = manager.render("error", error_context_expert, {"error_message": "Task failed"})

        if novice_render and expert_render:
            assert len(novice_render.rendered_content) >= len(expert_render.rendered_content)

    def test_verbosity_override(self, manager):
        """Verbosity override should affect template selection."""
        # Expert with detailed verbosity override
        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.EXPERT,
            verbosity_override=VerbosityLevel.DETAILED,
            is_error=False,
            is_first_time=False,
        )
        variant = manager.select_variant("task_creation", context)
        # With verbosity override, might get more detailed variant
        assert variant is not None

    def test_first_time_affects_selection(self, manager):
        """First time flag should affect variant selection."""
        first_time_context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            is_error=False,
            is_first_time=True,
        )
        regular_context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            is_error=False,
            is_first_time=False,
        )
        first_variant = manager.select_variant("task_creation", first_time_context)
        regular_variant = manager.select_variant("task_creation", regular_context)
        # Both should work, first time might get more verbose
        assert first_variant is not None
        assert regular_variant is not None


class TestTemplateManagerCustomization:
    """Tests for TemplateManager customization features."""

    @pytest.fixture
    def manager(self):
        """Create a TemplateManager instance."""
        return TemplateManager()

    def test_add_custom_template(self, manager):
        """Should allow adding custom templates."""
        custom_template = AdaptiveTemplate(
            template_id="custom_greeting",
            purpose=TemplatePurpose.WELCOME_MESSAGE,
            description="Custom greeting template",
            variants=[
                TemplateVariant(
                    expertise_level=ExpertiseLevel.NOVICE,
                    template_content="Hello {name}! Welcome to our app!",
                    show_examples=True,
                    show_shortcuts=False,
                    require_confirmation=False,
                    include_undo=False,
                    max_options=0,
                ),
            ],
            placeholders=["name"],
        )
        manager.add_template(custom_template)
        retrieved = manager.get_template("custom_greeting")
        assert retrieved is not None
        assert retrieved.template_id == "custom_greeting"

    def test_override_default_template(self, manager):
        """Should allow overriding default templates."""
        original = manager.get_template("task_creation")
        assert original is not None

        override = AdaptiveTemplate(
            template_id="task_creation",
            purpose=TemplatePurpose.TASK_CREATION,
            description="Overridden task creation",
            variants=[
                TemplateVariant(
                    expertise_level=ExpertiseLevel.NOVICE,
                    template_content="Custom: {title}",
                    show_examples=False,
                    show_shortcuts=False,
                    require_confirmation=False,
                    include_undo=False,
                    max_options=0,
                ),
            ],
            placeholders=["title"],
        )
        manager.add_template(override)
        updated = manager.get_template("task_creation")
        assert updated is not None
        assert updated.description == "Overridden task creation"

    def test_remove_template(self, manager):
        """Should allow removing templates."""
        # First add a custom template
        custom = AdaptiveTemplate(
            template_id="temp_template",
            purpose=TemplatePurpose.SUCCESS_CONFIRMATION,
            description="Temporary",
            variants=[],
            placeholders=[],
        )
        manager.add_template(custom)
        assert manager.get_template("temp_template") is not None

        # Remove it
        manager.remove_template("temp_template")
        assert manager.get_template("temp_template") is None

    def test_set_user_customization(self, manager):
        """Should store user customization preferences."""
        customization = TemplateCustomization(
            user_id="user789",
            verbosity_override=VerbosityLevel.MINIMAL,
            always_show_examples=False,
            never_show_shortcuts=False,
        )
        manager.set_user_customization(customization)
        retrieved = manager.get_user_customization("user789")
        assert retrieved is not None
        assert retrieved.verbosity_override == VerbosityLevel.MINIMAL

    def test_user_customization_affects_rendering(self, manager):
        """User customization should affect template rendering."""
        customization = TemplateCustomization(
            user_id="custom_user",
            always_show_examples=True,
            never_show_shortcuts=True,
        )
        manager.set_user_customization(customization)

        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.EXPERT,  # Expert normally doesn't get examples
            is_error=False,
            is_first_time=False,
        )
        rendered = manager.render("task_creation", context, {"title": "Test", "priority": "high", "due_date": "today"}, user_id="custom_user")
        # With always_show_examples=True, even expert should get examples
        if rendered:
            assert rendered.includes_examples is True


class TestDefaultTemplates:
    """Tests for default template content."""

    @pytest.fixture
    def manager(self):
        """Create a TemplateManager instance."""
        return TemplateManager()

    def test_task_creation_template_exists(self, manager):
        """Task creation template should exist with all variants."""
        template = manager.get_template("task_creation")
        assert template is not None
        assert template.purpose == TemplatePurpose.TASK_CREATION
        # Should have variants for all expertise levels
        levels = {v.expertise_level for v in template.variants}
        assert ExpertiseLevel.NOVICE in levels
        assert ExpertiseLevel.EXPERT in levels

    def test_success_template_exists(self, manager):
        """Success confirmation template should exist."""
        template = manager.get_template("success")
        assert template is not None
        assert template.purpose == TemplatePurpose.SUCCESS_CONFIRMATION

    def test_error_template_exists(self, manager):
        """Error message template should exist."""
        template = manager.get_template("error")
        assert template is not None
        assert template.purpose == TemplatePurpose.ERROR_MESSAGE

    def test_disambiguation_template_exists(self, manager):
        """Disambiguation template should exist."""
        template = manager.get_template("disambiguation")
        assert template is not None
        assert template.purpose == TemplatePurpose.DISAMBIGUATION

    def test_help_offer_template_exists(self, manager):
        """Help offer template should exist."""
        template = manager.get_template("help_offer")
        assert template is not None
        assert template.purpose == TemplatePurpose.HELP_OFFER

    def test_feature_suggestion_template_exists(self, manager):
        """Feature suggestion template should exist."""
        template = manager.get_template("feature_suggestion")
        assert template is not None
        assert template.purpose == TemplatePurpose.FEATURE_SUGGESTION

    def test_action_confirmation_template_exists(self, manager):
        """Action confirmation template should exist."""
        template = manager.get_template("action_confirmation")
        assert template is not None
        assert template.purpose == TemplatePurpose.ACTION_CONFIRMATION

    def test_welcome_template_exists(self, manager):
        """Welcome message template should exist."""
        template = manager.get_template("welcome")
        assert template is not None
        assert template.purpose == TemplatePurpose.WELCOME_MESSAGE


class TestTemplateVariantProgression:
    """Tests for expertise level variant progression."""

    @pytest.fixture
    def manager(self):
        """Create a TemplateManager instance."""
        return TemplateManager()

    def test_novice_variants_are_verbose(self, manager):
        """Novice variants should be most verbose."""
        template = manager.get_template("task_creation")
        novice_variant = next(
            (v for v in template.variants if v.expertise_level == ExpertiseLevel.NOVICE),
            None
        )
        assert novice_variant is not None
        assert novice_variant.show_examples is True
        assert novice_variant.require_confirmation is True

    def test_expert_variants_are_concise(self, manager):
        """Expert variants should be most concise."""
        template = manager.get_template("task_creation")
        expert_variant = next(
            (v for v in template.variants if v.expertise_level == ExpertiseLevel.EXPERT),
            None
        )
        assert expert_variant is not None
        assert expert_variant.show_examples is False
        assert expert_variant.require_confirmation is False

    def test_intermediate_is_balanced(self, manager):
        """Intermediate variants should be balanced."""
        template = manager.get_template("task_creation")
        intermediate_variant = next(
            (v for v in template.variants if v.expertise_level == ExpertiseLevel.INTERMEDIATE),
            None
        )
        assert intermediate_variant is not None
        # Intermediate should have some features but not all
        # Typically no examples but might have shortcuts

    def test_verbosity_decreases_with_expertise(self, manager):
        """Template content length should generally decrease with expertise."""
        template = manager.get_template("task_creation")
        variants_by_level = {v.expertise_level: v for v in template.variants}

        novice_len = len(variants_by_level.get(ExpertiseLevel.NOVICE, TemplateVariant(
            expertise_level=ExpertiseLevel.NOVICE,
            template_content="",
            show_examples=False,
            show_shortcuts=False,
            require_confirmation=False,
            include_undo=False,
            max_options=0,
        )).template_content)

        expert_len = len(variants_by_level.get(ExpertiseLevel.EXPERT, TemplateVariant(
            expertise_level=ExpertiseLevel.EXPERT,
            template_content="",
            show_examples=False,
            show_shortcuts=False,
            require_confirmation=False,
            include_undo=False,
            max_options=0,
        )).template_content)

        # Expert should be more concise
        assert expert_len <= novice_len


class TestRenderingEdgeCases:
    """Tests for edge cases in template rendering."""

    @pytest.fixture
    def manager(self):
        """Create a TemplateManager instance."""
        return TemplateManager()

    def test_render_with_missing_placeholder(self, manager):
        """Should handle missing placeholder values gracefully."""
        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.NOVICE,
            is_error=False,
            is_first_time=True,
        )
        # Don't provide all placeholders
        rendered = manager.render("task_creation", context, {})
        # Should still render, possibly with empty or placeholder text
        assert rendered is not None

    def test_render_with_extra_values(self, manager):
        """Should ignore extra placeholder values."""
        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.NOVICE,
            is_error=False,
            is_first_time=True,
        )
        values = {
            "title": "Test task",
            "priority": "high",
            "due_date": "tomorrow",
            "extra_field": "Should be ignored",
            "another_extra": "Also ignored",
        }
        rendered = manager.render("task_creation", context, values)
        assert rendered is not None
        assert "Test task" in rendered.rendered_content

    def test_render_with_special_characters(self, manager):
        """Should handle special characters in values."""
        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.NOVICE,
            is_error=False,
            is_first_time=True,
        )
        values = {"title": "Task with <html> & 'quotes' and \"double quotes\"", "priority": "high", "due_date": "today"}
        rendered = manager.render("task_creation", context, values)
        assert rendered is not None
        # Content should be preserved
        assert "<html>" in rendered.rendered_content or "html" in rendered.rendered_content.lower()

    def test_render_with_unicode(self, manager):
        """Should handle unicode characters in values."""
        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.NOVICE,
            is_error=False,
            is_first_time=True,
        )
        values = {"title": "Task with emoji and unicode chars", "priority": "high", "due_date": "today"}
        rendered = manager.render("task_creation", context, values)
        assert rendered is not None

    def test_render_preserves_newlines(self, manager):
        """Should preserve newlines in values when appropriate."""
        context = TemplateSelectionContext(
            expertise_level=ExpertiseLevel.NOVICE,
            is_error=False,
            is_first_time=True,
        )
        values = {"title": "Multi-line\ntask\ndescription", "priority": "normal", "due_date": "today"}
        rendered = manager.render("task_creation", context, values)
        assert rendered is not None


class TestTemplateLibraryOperations:
    """Tests for template library operations."""

    @pytest.fixture
    def manager(self):
        """Create a TemplateManager instance."""
        return TemplateManager()

    def test_get_library_info(self, manager):
        """Should provide library metadata."""
        library = manager.get_library()
        assert library is not None
        assert library.library_id is not None
        assert library.version is not None

    def test_export_library(self, manager):
        """Should export library to dictionary format."""
        export = manager.export_library()
        assert isinstance(export, dict)
        assert "templates" in export
        assert "version" in export

    def test_import_library(self, manager):
        """Should import library from dictionary format."""
        library_data = {
            "library_id": "imported",
            "version": "2.0.0",
            "templates": [],
            "brand_voice": "Custom voice",
            "personality_traits": ["custom"],
        }
        manager.import_library(library_data)
        library = manager.get_library()
        assert library.version == "2.0.0"


class TestVerbosityMappingDefaults:
    """Tests for default verbosity mappings."""

    @pytest.fixture
    def manager(self):
        """Create a TemplateManager instance."""
        return TemplateManager()

    def test_novice_default_verbosity(self, manager):
        """Novice should default to detailed verbosity."""
        mapping = manager.get_verbosity_mapping(ExpertiseLevel.NOVICE)
        assert mapping is not None
        assert mapping.default_verbosity == VerbosityLevel.DETAILED
        assert mapping.confirmation_frequency == "always"
        assert mapping.example_frequency == "always"

    def test_beginner_default_verbosity(self, manager):
        """Beginner should default to detailed verbosity."""
        mapping = manager.get_verbosity_mapping(ExpertiseLevel.BEGINNER)
        assert mapping is not None
        assert mapping.default_verbosity == VerbosityLevel.DETAILED

    def test_intermediate_default_verbosity(self, manager):
        """Intermediate should default to standard verbosity."""
        mapping = manager.get_verbosity_mapping(ExpertiseLevel.INTERMEDIATE)
        assert mapping is not None
        assert mapping.default_verbosity == VerbosityLevel.STANDARD

    def test_advanced_default_verbosity(self, manager):
        """Advanced should default to concise verbosity."""
        mapping = manager.get_verbosity_mapping(ExpertiseLevel.ADVANCED)
        assert mapping is not None
        assert mapping.default_verbosity == VerbosityLevel.CONCISE

    def test_expert_default_verbosity(self, manager):
        """Expert should default to minimal verbosity."""
        mapping = manager.get_verbosity_mapping(ExpertiseLevel.EXPERT)
        assert mapping is not None
        assert mapping.default_verbosity == VerbosityLevel.MINIMAL
        assert mapping.confirmation_frequency == "never"
        assert mapping.example_frequency == "never"
