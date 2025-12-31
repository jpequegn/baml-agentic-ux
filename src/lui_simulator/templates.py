"""
Adaptive Response Templates for LUI Simulator.
Response templates that vary by expertise level while maintaining consistency.

Issue #47 - Phase 2: Adaptive Interface Personalization

Key Principles:
- Consistency is trust in language form
- Tone whiplash destroys trust
- What stays constant: brand voice, personality traits, core patterns
- What changes: length, confirmation frequency, examples, technical language
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .expertise import ExpertiseLevel


class TemplatePurpose(Enum):
    """Purpose of a response template."""
    SUCCESS_CONFIRMATION = "SUCCESS_CONFIRMATION"
    ERROR_MESSAGE = "ERROR_MESSAGE"
    DISAMBIGUATION = "DISAMBIGUATION"
    HELP_OFFER = "HELP_OFFER"
    FEATURE_SUGGESTION = "FEATURE_SUGGESTION"
    ACTION_CONFIRMATION = "ACTION_CONFIRMATION"
    PROGRESS_UPDATE = "PROGRESS_UPDATE"
    WELCOME_MESSAGE = "WELCOME_MESSAGE"
    TASK_CREATION = "TASK_CREATION"
    SEARCH_RESULTS = "SEARCH_RESULTS"


class VerbosityLevel(Enum):
    """Verbosity level for responses."""
    MINIMAL = "MINIMAL"
    CONCISE = "CONCISE"
    STANDARD = "STANDARD"
    DETAILED = "DETAILED"


@dataclass
class TemplateVariant:
    """A template variant for a specific expertise level."""
    expertise_level: ExpertiseLevel
    template_content: str
    show_examples: bool = False
    show_shortcuts: bool = False
    require_confirmation: bool = False
    include_undo: bool = False
    max_options: int = 0  # 0 = unlimited


@dataclass
class AdaptiveTemplate:
    """Complete set of template variants for a purpose."""
    template_id: str
    purpose: TemplatePurpose
    description: str
    variants: list[TemplateVariant]
    placeholders: list[str] = field(default_factory=list)

    def get_variant(self, level: ExpertiseLevel) -> Optional[TemplateVariant]:
        """Get the variant for a specific expertise level."""
        for variant in self.variants:
            if variant.expertise_level == level:
                return variant
        return None


@dataclass
class RenderedTemplate:
    """Result of rendering a template with context."""
    template_id: str
    purpose: TemplatePurpose
    expertise_level: ExpertiseLevel
    rendered_content: str
    includes_examples: bool = False
    includes_shortcuts: bool = False
    requires_confirmation: bool = False
    suggested_actions: Optional[list[str]] = None


@dataclass
class TemplateSelectionContext:
    """Context for selecting the appropriate template variant."""
    expertise_level: ExpertiseLevel
    verbosity_override: Optional[VerbosityLevel] = None
    is_error: bool = False
    is_first_time: bool = False
    user_preference_style: Optional[str] = None


@dataclass
class TemplateCustomization:
    """User's template customization preferences."""
    user_id: str
    verbosity_override: Optional[VerbosityLevel] = None
    always_show_examples: bool = False
    never_show_shortcuts: bool = False
    custom_confirmation_frequency: Optional[str] = None
    preferred_error_detail: Optional[str] = None


@dataclass
class TemplateLibrary:
    """Collection of all adaptive templates."""
    library_id: str
    version: str
    templates: list[AdaptiveTemplate]
    brand_voice: str
    personality_traits: list[str]


@dataclass
class VerbosityMapping:
    """Mapping between expertise levels and default verbosity."""
    expertise_level: ExpertiseLevel
    default_verbosity: VerbosityLevel
    confirmation_frequency: str  # always, sometimes, rarely, never
    example_frequency: str  # always, sometimes, rarely, never


@dataclass
class ErrorTemplateDetails:
    """Error message template with progressive detail levels."""
    error_code: str
    novice_template: str
    beginner_template: str
    intermediate_template: str
    advanced_template: str
    expert_template: str
    recovery_actions: list[str] = field(default_factory=list)


# Default verbosity mapping by expertise level
DEFAULT_VERBOSITY_MAPPING = {
    ExpertiseLevel.NOVICE: VerbosityLevel.DETAILED,
    ExpertiseLevel.BEGINNER: VerbosityLevel.DETAILED,
    ExpertiseLevel.INTERMEDIATE: VerbosityLevel.STANDARD,
    ExpertiseLevel.ADVANCED: VerbosityLevel.CONCISE,
    ExpertiseLevel.EXPERT: VerbosityLevel.MINIMAL,
}

# Confirmation frequency by level
CONFIRMATION_FREQUENCY = {
    ExpertiseLevel.NOVICE: "always",
    ExpertiseLevel.BEGINNER: "sometimes",
    ExpertiseLevel.INTERMEDIATE: "rarely",
    ExpertiseLevel.ADVANCED: "never",
    ExpertiseLevel.EXPERT: "never",
}

# Example frequency by level
EXAMPLE_FREQUENCY = {
    ExpertiseLevel.NOVICE: "always",
    ExpertiseLevel.BEGINNER: "sometimes",
    ExpertiseLevel.INTERMEDIATE: "rarely",
    ExpertiseLevel.ADVANCED: "never",
    ExpertiseLevel.EXPERT: "never",
}


class TemplateManager:
    """
    Manages adaptive response templates.

    Selects and renders templates based on user expertise level
    while maintaining consistent brand voice and personality.
    """

    # Brand voice constants
    BRAND_VOICE = "Professional yet friendly, helpful without being condescending"
    PERSONALITY_TRAITS = ["Patient", "Clear", "Efficient", "Trustworthy"]

    def __init__(self):
        """Initialize the template manager with default templates."""
        self._templates: dict[str, AdaptiveTemplate] = {}
        self._customizations: dict[str, TemplateCustomization] = {}
        self._library_id = "default"
        self._library_version = "1.0.0"
        self._load_default_templates()

    def _load_default_templates(self) -> None:
        """Load all default templates."""
        # Task Creation Template
        self._templates["task_creation"] = AdaptiveTemplate(
            template_id="task_creation",
            purpose=TemplatePurpose.TASK_CREATION,
            description="Confirming task creation",
            placeholders=["title", "priority", "due_date"],
            variants=[
                TemplateVariant(
                    expertise_level=ExpertiseLevel.NOVICE,
                    template_content=(
                        "I'll create a new task for you. Here's what I understood:\n\n"
                        "- Title: {title}\n"
                        "- Priority: {priority}\n"
                        "- Due: {due_date}\n\n"
                        "Does this look right? Say 'yes' to confirm or tell me what to change."
                    ),
                    show_examples=True,
                    require_confirmation=True,
                    max_options=3,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.BEGINNER,
                    template_content=(
                        "Creating task: '{title}' (Priority: {priority}, Due: {due_date})\n"
                        "Confirm? [Yes/Edit]"
                    ),
                    show_examples=False,
                    require_confirmation=True,
                    max_options=2,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.INTERMEDIATE,
                    template_content=(
                        "Created: '{title}' - {priority} priority, due {due_date}\n"
                        "[Undo]"
                    ),
                    show_shortcuts=True,
                    require_confirmation=False,
                    include_undo=True,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.ADVANCED,
                    template_content="✓ {title} ({priority}, {due_date})",
                    show_shortcuts=True,
                    include_undo=True,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.EXPERT,
                    template_content="✓ {title}",
                    include_undo=True,
                ),
            ],
        )

        # Success Confirmation Template
        self._templates["success"] = AdaptiveTemplate(
            template_id="success",
            purpose=TemplatePurpose.SUCCESS_CONFIRMATION,
            description="Confirming successful action",
            placeholders=["action", "details"],
            variants=[
                TemplateVariant(
                    expertise_level=ExpertiseLevel.NOVICE,
                    template_content=(
                        "Great news! I've successfully {action}.\n\n"
                        "Here's what happened:\n{details}\n\n"
                        "Is there anything else you'd like me to help with?"
                    ),
                    show_examples=True,
                    require_confirmation=False,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.BEGINNER,
                    template_content=(
                        "Done! {action}.\n\n"
                        "{details}"
                    ),
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.INTERMEDIATE,
                    template_content="✓ {action}: {details}",
                    show_shortcuts=True,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.ADVANCED,
                    template_content="✓ {action}",
                    show_shortcuts=True,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.EXPERT,
                    template_content="✓",
                ),
            ],
        )

        # Error Message Template
        self._templates["error"] = AdaptiveTemplate(
            template_id="error",
            purpose=TemplatePurpose.ERROR_MESSAGE,
            description="Communicating an error",
            placeholders=["error_type", "message", "suggestion"],
            variants=[
                TemplateVariant(
                    expertise_level=ExpertiseLevel.NOVICE,
                    template_content=(
                        "I ran into a problem and couldn't complete that action.\n\n"
                        "What happened: {message}\n\n"
                        "Here's what you can try:\n"
                        "1. {suggestion}\n"
                        "2. Try a different approach\n"
                        "3. Ask me for help\n\n"
                        "Would you like me to explain more or try something else?"
                    ),
                    show_examples=True,
                    max_options=3,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.BEGINNER,
                    template_content=(
                        "Oops! {message}\n\n"
                        "Try: {suggestion}\n"
                        "Or ask for help."
                    ),
                    max_options=2,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.INTERMEDIATE,
                    template_content="Error: {message}. Try: {suggestion}",
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.ADVANCED,
                    template_content="✗ {error_type}: {message} → {suggestion}",
                    show_shortcuts=True,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.EXPERT,
                    template_content="✗ {error_type}",
                ),
            ],
        )

        # Disambiguation Template
        self._templates["disambiguation"] = AdaptiveTemplate(
            template_id="disambiguation",
            purpose=TemplatePurpose.DISAMBIGUATION,
            description="Requesting clarification",
            placeholders=["question", "options"],
            variants=[
                TemplateVariant(
                    expertise_level=ExpertiseLevel.NOVICE,
                    template_content=(
                        "I want to make sure I understand you correctly.\n\n"
                        "{question}\n\n"
                        "Here are some options:\n{options}\n\n"
                        "Just pick one or tell me in your own words!"
                    ),
                    show_examples=True,
                    require_confirmation=True,
                    max_options=5,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.BEGINNER,
                    template_content=(
                        "{question}\n\n"
                        "Options:\n{options}"
                    ),
                    max_options=4,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.INTERMEDIATE,
                    template_content="{question}\n{options}",
                    max_options=3,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.ADVANCED,
                    template_content="{question} [{options}]",
                    max_options=3,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.EXPERT,
                    template_content="? {options}",
                    max_options=2,
                ),
            ],
        )

        # Help Offer Template
        self._templates["help_offer"] = AdaptiveTemplate(
            template_id="help_offer",
            purpose=TemplatePurpose.HELP_OFFER,
            description="Offering assistance",
            placeholders=["topic", "tips"],
            variants=[
                TemplateVariant(
                    expertise_level=ExpertiseLevel.NOVICE,
                    template_content=(
                        "I noticed you might need some help with {topic}.\n\n"
                        "Here are some tips:\n{tips}\n\n"
                        "Would you like me to walk you through it step by step?"
                    ),
                    show_examples=True,
                    require_confirmation=True,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.BEGINNER,
                    template_content=(
                        "Need help with {topic}?\n\n"
                        "Tips: {tips}"
                    ),
                    show_examples=True,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.INTERMEDIATE,
                    template_content="Tip: {tips}",
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.ADVANCED,
                    template_content="",  # No unsolicited help
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.EXPERT,
                    template_content="",  # Expert knows
                ),
            ],
        )

        # Feature Suggestion Template
        self._templates["feature_suggestion"] = AdaptiveTemplate(
            template_id="feature_suggestion",
            purpose=TemplatePurpose.FEATURE_SUGGESTION,
            description="Suggesting a feature or shortcut",
            placeholders=["feature", "shortcut", "benefit"],
            variants=[
                TemplateVariant(
                    expertise_level=ExpertiseLevel.NOVICE,
                    template_content=(
                        "Did you know? You can {feature}!\n\n"
                        "Here's how: {shortcut}\n\n"
                        "This helps you {benefit}. Want me to show you?"
                    ),
                    show_examples=True,
                    require_confirmation=True,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.BEGINNER,
                    template_content=(
                        "Tip: Try {shortcut} to {feature}."
                    ),
                    show_examples=True,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.INTERMEDIATE,
                    template_content="",  # Rare tips only
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.ADVANCED,
                    template_content="[{shortcut}]",  # Show shortcuts inline
                    show_shortcuts=True,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.EXPERT,
                    template_content="",  # No suggestions
                ),
            ],
        )

        # Action Confirmation Template
        self._templates["action_confirmation"] = AdaptiveTemplate(
            template_id="action_confirmation",
            purpose=TemplatePurpose.ACTION_CONFIRMATION,
            description="Confirming before action",
            placeholders=["action", "consequences"],
            variants=[
                TemplateVariant(
                    expertise_level=ExpertiseLevel.NOVICE,
                    template_content=(
                        "I'm about to {action}.\n\n"
                        "This will {consequences}.\n\n"
                        "Are you sure you want to proceed? [Yes/No/Tell me more]"
                    ),
                    show_examples=True,
                    require_confirmation=True,
                    max_options=3,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.BEGINNER,
                    template_content=(
                        "{action}? This will {consequences}. [Yes/No]"
                    ),
                    require_confirmation=True,
                    max_options=2,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.INTERMEDIATE,
                    template_content="{action}? [Y/N]",
                    require_confirmation=True,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.ADVANCED,
                    template_content="",  # No confirmation needed
                    require_confirmation=False,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.EXPERT,
                    template_content="",  # Trust expert
                    require_confirmation=False,
                ),
            ],
        )

        # Welcome Message Template
        self._templates["welcome"] = AdaptiveTemplate(
            template_id="welcome",
            purpose=TemplatePurpose.WELCOME_MESSAGE,
            description="Session greeting",
            placeholders=["name", "last_action"],
            variants=[
                TemplateVariant(
                    expertise_level=ExpertiseLevel.NOVICE,
                    template_content=(
                        "Hello {name}! Welcome back.\n\n"
                        "I'm here to help you. Last time, you {last_action}.\n\n"
                        "What would you like to do today? You can ask me anything "
                        "or type 'help' for suggestions."
                    ),
                    show_examples=True,
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.BEGINNER,
                    template_content=(
                        "Hi {name}! Ready to continue?\n\n"
                        "Last: {last_action}"
                    ),
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.INTERMEDIATE,
                    template_content="Welcome back, {name}.",
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.ADVANCED,
                    template_content="Hi {name}",
                ),
                TemplateVariant(
                    expertise_level=ExpertiseLevel.EXPERT,
                    template_content="→",  # Just a prompt
                ),
            ],
        )

    def get_template(self, template_id: str) -> Optional[AdaptiveTemplate]:
        """Get a template by ID."""
        return self._templates.get(template_id)

    def list_templates(self) -> list[str]:
        """List all available template IDs."""
        return list(self._templates.keys())

    def select_variant(
        self,
        template_id: str,
        context: TemplateSelectionContext,
    ) -> Optional[TemplateVariant]:
        """
        Select the appropriate template variant based on context.

        Args:
            template_id: ID of the template to select from.
            context: Context for selection.

        Returns:
            Selected TemplateVariant or None if template not found.
        """
        template = self._templates.get(template_id)
        if not template:
            return None

        # Start with user's expertise level
        target_level = context.expertise_level

        # Adjust for verbosity override
        if context.verbosity_override:
            target_level = self._adjust_level_for_verbosity(
                context.expertise_level,
                context.verbosity_override,
            )

        # Adjust for first-time actions (prefer more verbose)
        if context.is_first_time and target_level != ExpertiseLevel.NOVICE:
            target_level = self._get_previous_level(target_level)

        # Adjust for error context (prefer more detail)
        if context.is_error and target_level in (ExpertiseLevel.ADVANCED, ExpertiseLevel.EXPERT):
            target_level = ExpertiseLevel.INTERMEDIATE

        return template.get_variant(target_level)

    def render(
        self,
        template_id: str,
        context: TemplateSelectionContext,
        values: dict[str, str],
        user_id: Optional[str] = None,
    ) -> Optional[RenderedTemplate]:
        """
        Render a template with the provided values.

        Args:
            template_id: ID of the template to render.
            context: Context for variant selection.
            values: Dictionary of placeholder values.
            user_id: Optional user ID for customization.

        Returns:
            RenderedTemplate or None if template not found.
        """
        template = self._templates.get(template_id)
        if not template:
            return None

        variant = self.select_variant(template_id, context)
        if not variant:
            return None

        # Apply customizations if user has them
        customization = self._customizations.get(user_id) if user_id else None

        # Render the template content
        rendered_content = self._render_content(
            variant.template_content,
            values,
            variant,
            customization,
        )

        # Build suggested actions based on variant settings
        suggested_actions = None
        if variant.max_options > 0:
            suggested_actions = self._build_action_list(template, variant)

        return RenderedTemplate(
            template_id=template_id,
            purpose=template.purpose,
            expertise_level=variant.expertise_level,
            rendered_content=rendered_content,
            includes_examples=variant.show_examples or (
                customization and customization.always_show_examples
            ),
            includes_shortcuts=variant.show_shortcuts and not (
                customization and customization.never_show_shortcuts
            ),
            requires_confirmation=variant.require_confirmation,
            suggested_actions=suggested_actions,
        )

    def _render_content(
        self,
        template_content: str,
        values: dict[str, str],
        variant: TemplateVariant,
        customization: Optional[TemplateCustomization],
    ) -> str:
        """Render template content by replacing placeholders."""
        result = template_content

        # Replace placeholders
        for key, value in values.items():
            placeholder = "{" + key + "}"
            result = result.replace(placeholder, str(value))

        # Add undo hint if applicable
        if variant.include_undo and "[Undo]" not in result:
            result += " [Undo: Ctrl+Z]" if variant.show_shortcuts else ""

        return result

    def _build_action_list(
        self,
        template: AdaptiveTemplate,
        variant: TemplateVariant,
    ) -> list[str]:
        """Build a list of suggested actions based on template purpose."""
        actions = []

        if template.purpose == TemplatePurpose.ERROR_MESSAGE:
            actions = ["Retry", "Get help", "Cancel"]
        elif template.purpose == TemplatePurpose.DISAMBIGUATION:
            actions = ["Select option", "Clarify", "Cancel"]
        elif template.purpose == TemplatePurpose.ACTION_CONFIRMATION:
            actions = ["Confirm", "Cancel"]
        elif template.purpose == TemplatePurpose.TASK_CREATION:
            actions = ["Confirm", "Edit", "Cancel"]

        # Limit to max_options
        if variant.max_options > 0 and len(actions) > variant.max_options:
            actions = actions[:variant.max_options]

        return actions

    def _adjust_level_for_verbosity(
        self,
        level: ExpertiseLevel,
        verbosity: VerbosityLevel,
    ) -> ExpertiseLevel:
        """Adjust expertise level based on verbosity preference."""
        # Map verbosity to equivalent expertise level
        verbosity_to_level = {
            VerbosityLevel.DETAILED: ExpertiseLevel.NOVICE,
            VerbosityLevel.STANDARD: ExpertiseLevel.INTERMEDIATE,
            VerbosityLevel.CONCISE: ExpertiseLevel.ADVANCED,
            VerbosityLevel.MINIMAL: ExpertiseLevel.EXPERT,
        }

        target_level = verbosity_to_level.get(verbosity, level)

        # Return the more verbose of the two
        level_order = [
            ExpertiseLevel.NOVICE,
            ExpertiseLevel.BEGINNER,
            ExpertiseLevel.INTERMEDIATE,
            ExpertiseLevel.ADVANCED,
            ExpertiseLevel.EXPERT,
        ]

        level_idx = level_order.index(level)
        target_idx = level_order.index(target_level)

        # Use the lower index (more verbose)
        return level_order[min(level_idx, target_idx)]

    def _get_previous_level(self, level: ExpertiseLevel) -> ExpertiseLevel:
        """Get the previous (more verbose) expertise level."""
        level_order = [
            ExpertiseLevel.NOVICE,
            ExpertiseLevel.BEGINNER,
            ExpertiseLevel.INTERMEDIATE,
            ExpertiseLevel.ADVANCED,
            ExpertiseLevel.EXPERT,
        ]

        try:
            idx = level_order.index(level)
            if idx > 0:
                return level_order[idx - 1]
        except ValueError:
            pass

        return level

    def set_customization(self, customization: TemplateCustomization) -> None:
        """Set template customization for a user."""
        self._customizations[customization.user_id] = customization

    def get_customization(self, user_id: str) -> Optional[TemplateCustomization]:
        """Get template customization for a user."""
        return self._customizations.get(user_id)

    def remove_customization(self, user_id: str) -> bool:
        """Remove template customization for a user."""
        if user_id in self._customizations:
            del self._customizations[user_id]
            return True
        return False

    def add_template(self, template: AdaptiveTemplate) -> None:
        """Add a custom template."""
        self._templates[template.template_id] = template

    def remove_template(self, template_id: str) -> bool:
        """Remove a template."""
        if template_id in self._templates:
            del self._templates[template_id]
            return True
        return False

    def get_verbosity_for_level(self, level: ExpertiseLevel) -> VerbosityLevel:
        """Get the default verbosity level for an expertise level."""
        return DEFAULT_VERBOSITY_MAPPING.get(level, VerbosityLevel.STANDARD)

    def should_confirm(self, level: ExpertiseLevel) -> bool:
        """Check if confirmation is needed at this expertise level."""
        frequency = CONFIRMATION_FREQUENCY.get(level, "sometimes")
        return frequency in ("always", "sometimes")

    def should_show_examples(self, level: ExpertiseLevel) -> bool:
        """Check if examples should be shown at this expertise level."""
        frequency = EXAMPLE_FREQUENCY.get(level, "sometimes")
        return frequency in ("always", "sometimes")

    def get_all_templates(self) -> list[AdaptiveTemplate]:
        """Get all templates in the library."""
        return list(self._templates.values())

    def get_templates_by_purpose(
        self,
        purpose: TemplatePurpose,
    ) -> list[AdaptiveTemplate]:
        """Get all templates for a specific purpose."""
        return [
            t for t in self._templates.values()
            if t.purpose == purpose
        ]

    def set_user_customization(self, customization: TemplateCustomization) -> None:
        """Set template customization for a user (alias for set_customization)."""
        self.set_customization(customization)

    def get_user_customization(
        self,
        user_id: str,
    ) -> Optional[TemplateCustomization]:
        """Get template customization for a user (alias for get_customization)."""
        return self.get_customization(user_id)

    def get_library(self) -> TemplateLibrary:
        """Get the current template library."""
        return TemplateLibrary(
            library_id=self._library_id,
            version=self._library_version,
            templates=list(self._templates.values()),
            brand_voice=self.BRAND_VOICE,
            personality_traits=self.PERSONALITY_TRAITS,
        )

    def export_library(self) -> dict:
        """Export the library to dictionary format."""
        library = self.get_library()
        return {
            "library_id": library.library_id,
            "version": library.version,
            "templates": [
                {
                    "template_id": t.template_id,
                    "purpose": t.purpose.value,
                    "description": t.description,
                    "placeholders": t.placeholders,
                }
                for t in library.templates
            ],
            "brand_voice": library.brand_voice,
            "personality_traits": library.personality_traits,
        }

    def import_library(self, data: dict) -> None:
        """Import a library from dictionary format."""
        self._library_version = data.get("version", "1.0.0")
        self._library_id = data.get("library_id", "imported")
        self.BRAND_VOICE = data.get("brand_voice", self.BRAND_VOICE)
        if "personality_traits" in data:
            self.PERSONALITY_TRAITS = data["personality_traits"]

    def get_verbosity_mapping(
        self,
        level: ExpertiseLevel,
    ) -> VerbosityMapping:
        """Get the verbosity mapping for an expertise level."""
        return VerbosityMapping(
            expertise_level=level,
            default_verbosity=DEFAULT_VERBOSITY_MAPPING.get(
                level, VerbosityLevel.STANDARD
            ),
            confirmation_frequency=CONFIRMATION_FREQUENCY.get(level, "sometimes"),
            example_frequency=EXAMPLE_FREQUENCY.get(level, "sometimes"),
        )
