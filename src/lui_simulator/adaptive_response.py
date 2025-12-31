"""
Adaptive Response Generation for LUI Simulator.
Profile-aware response generation that adapts to user expertise level.

Issue #48 - Phase 2: Adaptive Interface Personalization

Integrates:
- User profiles from expertise detection
- Session metrics for frustration detection
- Adaptive templates for response formatting
- Level-appropriate language and features
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .expertise import ExpertiseLevel
from .templates import VerbosityLevel, TemplateManager, TemplateSelectionContext


class FrustrationResponse(Enum):
    """How to respond to frustration signals."""
    NORMAL = "NORMAL"
    INCREASED_HELP = "INCREASED_HELP"
    OFFER_ALTERNATIVES = "OFFER_ALTERNATIVES"
    SIMPLIFY = "SIMPLIFY"
    ESCALATE = "ESCALATE"


@dataclass
class FrustrationIndicators:
    """Signals indicating user frustration."""
    consecutive_errors: int = 0
    repeated_queries: int = 0
    negative_sentiment: bool = False
    rapid_interactions: bool = False
    help_seeking_rate: float = 0.0
    abandonment_signals: bool = False

    def frustration_score(self) -> float:
        """Calculate overall frustration score (0.0-1.0)."""
        score = 0.0
        # Weight different signals
        score += min(self.consecutive_errors * 0.15, 0.45)  # Max 0.45 for 3+ errors
        score += min(self.repeated_queries * 0.1, 0.2)  # Max 0.2 for 2+ repeats
        if self.negative_sentiment:
            score += 0.2
        if self.rapid_interactions:
            score += 0.1
        score += self.help_seeking_rate * 0.15
        if self.abandonment_signals:
            score += 0.2
        return min(score, 1.0)

    def is_frustrated(self, threshold: float = 0.3) -> bool:
        """Check if frustration level exceeds threshold."""
        return self.frustration_score() >= threshold


@dataclass
class AdaptationSettings:
    """Settings that control how responses are adapted."""
    expertise_level: ExpertiseLevel
    verbosity_level: VerbosityLevel
    show_examples: bool = False
    show_shortcuts: bool = False
    require_confirmation: bool = False
    use_technical_language: bool = False
    offer_help_proactively: bool = False
    define_terms: bool = False
    max_options: int = 0  # 0 = unlimited


@dataclass
class AdaptiveResponse:
    """A response adapted to user profile."""
    content: str
    verbosity_used: VerbosityLevel
    adaptations_applied: list[str] = field(default_factory=list)
    shortcuts_mentioned: list[str] = field(default_factory=list)
    follow_up_suggestions: list[str] = field(default_factory=list)

    # For gradual transition support
    alternative_content: Optional[str] = None
    show_toggle: bool = False

    # Metadata
    expertise_level_used: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE
    frustration_mode: FrustrationResponse = FrustrationResponse.NORMAL
    confidence: float = 0.8


@dataclass
class ResponseModifier:
    """A modifier applied to a response."""
    modifier_type: str
    reason: str
    impact: str


# Default settings by expertise level
DEFAULT_SETTINGS = {
    ExpertiseLevel.NOVICE: AdaptationSettings(
        expertise_level=ExpertiseLevel.NOVICE,
        verbosity_level=VerbosityLevel.DETAILED,
        show_examples=True,
        show_shortcuts=False,
        require_confirmation=True,
        use_technical_language=False,
        offer_help_proactively=True,
        define_terms=True,
        max_options=5,
    ),
    ExpertiseLevel.BEGINNER: AdaptationSettings(
        expertise_level=ExpertiseLevel.BEGINNER,
        verbosity_level=VerbosityLevel.DETAILED,
        show_examples=True,
        show_shortcuts=False,
        require_confirmation=True,  # For destructive only, handled in logic
        use_technical_language=False,
        offer_help_proactively=True,
        define_terms=True,
        max_options=4,
    ),
    ExpertiseLevel.INTERMEDIATE: AdaptationSettings(
        expertise_level=ExpertiseLevel.INTERMEDIATE,
        verbosity_level=VerbosityLevel.STANDARD,
        show_examples=False,
        show_shortcuts=True,
        require_confirmation=False,
        use_technical_language=True,
        offer_help_proactively=False,
        define_terms=False,
        max_options=3,
    ),
    ExpertiseLevel.ADVANCED: AdaptationSettings(
        expertise_level=ExpertiseLevel.ADVANCED,
        verbosity_level=VerbosityLevel.CONCISE,
        show_examples=False,
        show_shortcuts=True,
        require_confirmation=False,
        use_technical_language=True,
        offer_help_proactively=False,
        define_terms=False,
        max_options=0,
    ),
    ExpertiseLevel.EXPERT: AdaptationSettings(
        expertise_level=ExpertiseLevel.EXPERT,
        verbosity_level=VerbosityLevel.MINIMAL,
        show_examples=False,
        show_shortcuts=True,
        require_confirmation=False,
        use_technical_language=True,
        offer_help_proactively=False,
        define_terms=False,
        max_options=0,
    ),
}

# Guidelines text for each level
LEVEL_GUIDELINES = {
    ExpertiseLevel.NOVICE: {
        "description": "New user, needs guidance and reassurance",
        "confirmation_policy": "Always confirm before actions",
        "explanation_depth": "Full explanations with examples",
        "shortcut_policy": "Don't mention shortcuts",
        "error_handling": "Explain errors fully, offer 3 recovery options",
        "help_policy": "Offer help proactively",
        "language_style": "Simple, encouraging, step-by-step",
    },
    ExpertiseLevel.BEGINNER: {
        "description": "Some familiarity, still learning",
        "confirmation_policy": "Confirm destructive actions only",
        "explanation_depth": "Brief explanations",
        "shortcut_policy": "Mention shortcuts exist",
        "error_handling": "Brief explanation, 2 options",
        "help_policy": "Offer help when struggling",
        "language_style": "Friendly, approachable",
    },
    ExpertiseLevel.INTERMEDIATE: {
        "description": "Regular user, comfortable with basics",
        "confirmation_policy": "Rarely confirm",
        "explanation_depth": "Standard responses",
        "shortcut_policy": "Show relevant shortcuts",
        "error_handling": "Concise message, 1 suggestion",
        "help_policy": "Only when requested",
        "language_style": "Professional, efficient",
    },
    ExpertiseLevel.ADVANCED: {
        "description": "Power user, wants efficiency",
        "confirmation_policy": "Critical actions only",
        "explanation_depth": "Concise responses",
        "shortcut_policy": "Prominently show shortcuts",
        "error_handling": "Short error with action",
        "help_policy": "Never unsolicited",
        "language_style": "Technical, direct",
    },
    ExpertiseLevel.EXPERT: {
        "description": "Expert user, maximum efficiency",
        "confirmation_policy": "Never confirm",
        "explanation_depth": "Minimal responses",
        "shortcut_policy": "Assume shortcuts known",
        "error_handling": "Error code + minimal message",
        "help_policy": "Never",
        "language_style": "Terse, symbol-based OK",
    },
}


class AdaptiveResponseGenerator:
    """
    Generates responses adapted to user expertise level.

    Integrates with TemplateManager for consistent formatting
    and applies level-appropriate adaptations.
    """

    def __init__(self, template_manager: Optional[TemplateManager] = None):
        """Initialize the generator with optional template manager."""
        self._template_manager = template_manager or TemplateManager()
        self._modifiers_applied: list[ResponseModifier] = []

    def get_settings(
        self,
        expertise_level: ExpertiseLevel,
        frustration: Optional[FrustrationIndicators] = None,
    ) -> AdaptationSettings:
        """
        Get adaptation settings for an expertise level.

        Adjusts settings if frustration is detected.
        """
        base_settings = DEFAULT_SETTINGS.get(
            expertise_level,
            DEFAULT_SETTINGS[ExpertiseLevel.INTERMEDIATE],
        )

        # Copy settings to avoid modifying defaults
        settings = AdaptationSettings(
            expertise_level=base_settings.expertise_level,
            verbosity_level=base_settings.verbosity_level,
            show_examples=base_settings.show_examples,
            show_shortcuts=base_settings.show_shortcuts,
            require_confirmation=base_settings.require_confirmation,
            use_technical_language=base_settings.use_technical_language,
            offer_help_proactively=base_settings.offer_help_proactively,
            define_terms=base_settings.define_terms,
            max_options=base_settings.max_options,
        )

        # Adjust for frustration
        if frustration and frustration.is_frustrated():
            settings = self._adjust_for_frustration(settings, frustration)

        return settings

    def _adjust_for_frustration(
        self,
        settings: AdaptationSettings,
        frustration: FrustrationIndicators,
    ) -> AdaptationSettings:
        """Adjust settings to help frustrated user."""
        score = frustration.frustration_score()

        # Increase verbosity one level if possible
        verbosity_order = [
            VerbosityLevel.MINIMAL,
            VerbosityLevel.CONCISE,
            VerbosityLevel.STANDARD,
            VerbosityLevel.DETAILED,
        ]
        current_idx = verbosity_order.index(settings.verbosity_level)
        if current_idx < len(verbosity_order) - 1:
            settings.verbosity_level = verbosity_order[current_idx + 1]

        # Enable more help features
        settings.show_examples = True
        settings.offer_help_proactively = True

        # For high frustration, define terms too
        if score > 0.5:
            settings.define_terms = True

        return settings

    def detect_frustration(
        self,
        consecutive_errors: int = 0,
        repeated_queries: int = 0,
        negative_words_detected: bool = False,
        interactions_per_minute: float = 0.0,
        help_requests: int = 0,
        total_interactions: int = 1,
        incomplete_tasks: int = 0,
    ) -> FrustrationIndicators:
        """
        Detect frustration signals from session data.

        Args:
            consecutive_errors: Number of errors in a row
            repeated_queries: Same query asked multiple times
            negative_words_detected: If negative sentiment was found
            interactions_per_minute: Rate of interactions
            help_requests: Number of help requests
            total_interactions: Total interactions for rate calc
            incomplete_tasks: Number of abandoned tasks

        Returns:
            FrustrationIndicators with calculated signals
        """
        help_rate = help_requests / max(total_interactions, 1)
        rapid = interactions_per_minute > 10  # More than 10/min is rapid
        abandonment = incomplete_tasks > 2

        return FrustrationIndicators(
            consecutive_errors=consecutive_errors,
            repeated_queries=repeated_queries,
            negative_sentiment=negative_words_detected,
            rapid_interactions=rapid,
            help_seeking_rate=help_rate,
            abandonment_signals=abandonment,
        )

    def get_frustration_response_mode(
        self,
        frustration: FrustrationIndicators,
    ) -> FrustrationResponse:
        """Determine how to respond to frustration level."""
        score = frustration.frustration_score()

        if score < 0.2:
            return FrustrationResponse.NORMAL
        elif score < 0.4:
            return FrustrationResponse.INCREASED_HELP
        elif score < 0.6:
            return FrustrationResponse.OFFER_ALTERNATIVES
        elif score < 0.8:
            return FrustrationResponse.SIMPLIFY
        else:
            return FrustrationResponse.ESCALATE

    def generate_response(
        self,
        template_id: str,
        expertise_level: ExpertiseLevel,
        values: dict[str, str],
        frustration: Optional[FrustrationIndicators] = None,
        is_error: bool = False,
        is_first_time: bool = False,
        user_id: Optional[str] = None,
    ) -> AdaptiveResponse:
        """
        Generate an adaptive response using templates.

        Args:
            template_id: ID of template to use
            expertise_level: User's expertise level
            values: Placeholder values for template
            frustration: Optional frustration indicators
            is_error: Whether this is an error context
            is_first_time: Whether user is doing this for first time
            user_id: Optional user ID for customization

        Returns:
            AdaptiveResponse with adapted content
        """
        settings = self.get_settings(expertise_level, frustration)
        frustration_mode = FrustrationResponse.NORMAL

        if frustration:
            frustration_mode = self.get_frustration_response_mode(frustration)

        # Build template context
        context = TemplateSelectionContext(
            expertise_level=expertise_level,
            verbosity_override=settings.verbosity_level,
            is_error=is_error,
            is_first_time=is_first_time,
        )

        # Render template
        rendered = self._template_manager.render(
            template_id, context, values, user_id
        )

        if not rendered:
            # Fallback response
            return AdaptiveResponse(
                content=self._generate_fallback(values, settings),
                verbosity_used=settings.verbosity_level,
                adaptations_applied=["fallback_used"],
                expertise_level_used=expertise_level,
                frustration_mode=frustration_mode,
                confidence=0.5,
            )

        # Build adaptations list
        adaptations = []
        if settings.show_examples:
            adaptations.append("examples_included")
        if settings.show_shortcuts:
            adaptations.append("shortcuts_shown")
        if settings.define_terms:
            adaptations.append("terms_defined")
        if frustration_mode != FrustrationResponse.NORMAL:
            adaptations.append(f"frustration_mode_{frustration_mode.value.lower()}")

        # Build shortcuts list
        shortcuts = []
        if settings.show_shortcuts and rendered.includes_shortcuts:
            shortcuts = self._get_relevant_shortcuts(template_id)

        # Build follow-up suggestions
        suggestions = []
        if rendered.suggested_actions:
            # Filter based on expertise level
            max_suggestions = settings.max_options if settings.max_options > 0 else 5
            suggestions = rendered.suggested_actions[:max_suggestions]

        # Determine if toggle should be shown (transitioning users)
        show_toggle = is_first_time and expertise_level not in (
            ExpertiseLevel.NOVICE, ExpertiseLevel.EXPERT
        )

        return AdaptiveResponse(
            content=rendered.rendered_content,
            verbosity_used=settings.verbosity_level,
            adaptations_applied=adaptations,
            shortcuts_mentioned=shortcuts,
            follow_up_suggestions=suggestions,
            show_toggle=show_toggle,
            expertise_level_used=expertise_level,
            frustration_mode=frustration_mode,
            confidence=0.85 if not frustration else 0.75,
        )

    def _generate_fallback(
        self,
        values: dict[str, str],
        settings: AdaptationSettings,
    ) -> str:
        """Generate a fallback response when template not found."""
        if settings.verbosity_level == VerbosityLevel.MINIMAL:
            return "Done."
        elif settings.verbosity_level == VerbosityLevel.CONCISE:
            return "Action completed."
        elif settings.verbosity_level == VerbosityLevel.STANDARD:
            return "Your action has been completed successfully."
        else:
            return (
                "Great news! Your action has been completed successfully. "
                "Is there anything else you'd like me to help with?"
            )

    def _get_relevant_shortcuts(self, template_id: str) -> list[str]:
        """Get shortcuts relevant to a template."""
        # Map template IDs to common shortcuts
        shortcut_map = {
            "task_creation": ["Ctrl+T: New task", "Ctrl+Enter: Submit"],
            "success": ["Ctrl+Z: Undo"],
            "error": ["Ctrl+R: Retry", "?: Help"],
            "disambiguation": ["1-9: Select option", "Esc: Cancel"],
            "welcome": ["?: Help", "Ctrl+K: Command palette"],
        }
        return shortcut_map.get(template_id, [])

    def generate_error_response(
        self,
        error_message: str,
        expertise_level: ExpertiseLevel,
        frustration: Optional[FrustrationIndicators] = None,
        recovery_options: Optional[list[str]] = None,
    ) -> AdaptiveResponse:
        """
        Generate an error response adapted to expertise level.

        Args:
            error_message: The error message
            expertise_level: User's expertise level
            frustration: Optional frustration indicators
            recovery_options: Possible recovery actions

        Returns:
            AdaptiveResponse with adapted error message
        """
        settings = self.get_settings(expertise_level, frustration)
        frustration_mode = FrustrationResponse.NORMAL

        if frustration:
            frustration_mode = self.get_frustration_response_mode(frustration)

        # Format error based on level
        content = self._format_error(
            error_message, settings, frustration_mode, recovery_options
        )

        adaptations = ["error_formatted"]
        if frustration_mode != FrustrationResponse.NORMAL:
            adaptations.append("frustration_adjusted")

        return AdaptiveResponse(
            content=content,
            verbosity_used=settings.verbosity_level,
            adaptations_applied=adaptations,
            shortcuts_mentioned=["Ctrl+R: Retry", "?: Help"] if settings.show_shortcuts else [],
            follow_up_suggestions=recovery_options[:settings.max_options] if recovery_options and settings.max_options > 0 else recovery_options or [],
            expertise_level_used=expertise_level,
            frustration_mode=frustration_mode,
            confidence=0.8,
        )

    def _format_error(
        self,
        error_message: str,
        settings: AdaptationSettings,
        frustration_mode: FrustrationResponse,
        recovery_options: Optional[list[str]],
    ) -> str:
        """Format error message based on settings."""
        options = recovery_options or ["Try again", "Get help"]

        if settings.expertise_level == ExpertiseLevel.NOVICE:
            content = (
                f"I ran into a problem and couldn't complete that action.\n\n"
                f"What happened: {error_message}\n\n"
                f"Here's what you can try:\n"
            )
            for i, opt in enumerate(options[:3], 1):
                content += f"{i}. {opt}\n"
            content += "\nWould you like me to explain more or try something else?"

        elif settings.expertise_level == ExpertiseLevel.BEGINNER:
            content = f"Oops! {error_message}\n\n"
            content += f"Try: {options[0] if options else 'Try again'}\n"
            content += "Or ask for help."

        elif settings.expertise_level == ExpertiseLevel.INTERMEDIATE:
            content = f"Error: {error_message}"
            if options:
                content += f". Try: {options[0]}"

        elif settings.expertise_level == ExpertiseLevel.ADVANCED:
            content = f"Error: {error_message}"
            if settings.show_shortcuts:
                content += " [Ctrl+R: retry]"

        else:  # EXPERT
            # Extract error code if present
            error_code = error_message.split(":")[0] if ":" in error_message else "ERR"
            content = f"Error: {error_code}"

        # Adjust for frustration
        if frustration_mode in (FrustrationResponse.SIMPLIFY, FrustrationResponse.OFFER_ALTERNATIVES):
            content += "\n\nWould you like me to suggest a simpler approach?"
        elif frustration_mode == FrustrationResponse.ESCALATE:
            content += "\n\nWould you like to speak with a human support agent?"

        return content

    def adapt_response_to_level(
        self,
        original_response: str,
        target_level: ExpertiseLevel,
        include_shortcuts: bool = True,
    ) -> AdaptiveResponse:
        """
        Transform a standard response to match target expertise level.

        Args:
            original_response: The original response text
            target_level: Target expertise level
            include_shortcuts: Whether to include shortcuts

        Returns:
            AdaptiveResponse adapted to target level
        """
        settings = self.get_settings(target_level)

        # Apply transformations based on level
        content = self._transform_response(original_response, settings)

        shortcuts = []
        if include_shortcuts and settings.show_shortcuts:
            shortcuts = ["Ctrl+Z: Undo", "?: Help"]

        return AdaptiveResponse(
            content=content,
            verbosity_used=settings.verbosity_level,
            adaptations_applied=["level_adapted"],
            shortcuts_mentioned=shortcuts,
            follow_up_suggestions=[],
            expertise_level_used=target_level,
            frustration_mode=FrustrationResponse.NORMAL,
            confidence=0.75,
        )

    def _transform_response(
        self,
        original: str,
        settings: AdaptationSettings,
    ) -> str:
        """Transform response based on settings."""
        if settings.verbosity_level == VerbosityLevel.MINIMAL:
            # Extract just the key action/result
            words = original.split()
            if len(words) <= 5:
                return original
            # Try to find a period and take first sentence
            first_period = original.find(".")
            if first_period > 0 and first_period < 50:
                return original[:first_period + 1]
            return " ".join(words[:5]) + "..."

        elif settings.verbosity_level == VerbosityLevel.CONCISE:
            # Keep first sentence or first 100 chars
            first_period = original.find(".")
            if first_period > 0:
                return original[:first_period + 1]
            return original[:100] + ("..." if len(original) > 100 else "")

        elif settings.verbosity_level == VerbosityLevel.DETAILED:
            # Add context if not present
            if len(original) < 100:
                return original + " Let me know if you need any help with this."
            return original

        return original  # STANDARD - return as-is

    def get_level_guidelines(
        self,
        level: ExpertiseLevel,
    ) -> dict[str, str]:
        """Get response generation guidelines for a level."""
        return LEVEL_GUIDELINES.get(level, LEVEL_GUIDELINES[ExpertiseLevel.INTERMEDIATE])

    def should_show_feature(
        self,
        feature: str,
        expertise_level: ExpertiseLevel,
    ) -> bool:
        """
        Determine if a feature should be shown at expertise level.

        Args:
            feature: Feature name (e.g., 'shortcuts', 'examples', 'confirmation')
            expertise_level: User's expertise level

        Returns:
            Whether the feature should be shown
        """
        settings = self.get_settings(expertise_level)

        feature_map = {
            "shortcuts": settings.show_shortcuts,
            "examples": settings.show_examples,
            "confirmation": settings.require_confirmation,
            "help": settings.offer_help_proactively,
            "technical": settings.use_technical_language,
            "definitions": settings.define_terms,
        }

        return feature_map.get(feature, False)

    def get_max_options(self, expertise_level: ExpertiseLevel) -> int:
        """Get maximum options to show for expertise level."""
        settings = self.get_settings(expertise_level)
        return settings.max_options
