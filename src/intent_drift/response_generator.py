"""Graceful response generator for intent drift detection.

This module generates natural, graceful responses for drift scenarios
that acknowledge limitations while offering alternatives.

Issue #82 - Task 5.5: Graceful Response Generator
Part of #28 - Phase 5: Intent Drift Detection
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .drift_classifier import DriftClassification
from .types import (
    DriftResponseTone,
    DriftResponseTemplate,
    DriftType,
    GracefulResponse,
    GracefulResponseType,
    Redirect,
    RedirectSuggestion,
)


# ============================================
# Response Templates
# ============================================

# Template for NONE drift (within capability)
TEMPLATE_NONE = DriftResponseTemplate(
    template_id="none_in_scope",
    drift_types=[DriftType.NONE],
    template_text="I can help you with {request}. {action_prompt}",
    required_variables=["request", "action_prompt"],
    tone=DriftResponseTone.HELPFUL,
    example_output="I can help you with booking a flight. What destination are you interested in?",
)

# Template for SCOPE_EXPANSION drift
TEMPLATE_SCOPE_EXPANSION = DriftResponseTemplate(
    template_id="scope_expansion",
    drift_types=[DriftType.SCOPE_EXPANSION],
    template_text=(
        "I understand you're looking for {request}. "
        "That specific feature isn't available yet. "
        "However, I can help you with:\n{alternatives}\n"
        "Would any of these be helpful?"
    ),
    required_variables=["request", "alternatives"],
    tone=DriftResponseTone.HELPFUL,
    example_output=(
        "I understand you're looking for multi-city booking. "
        "That specific feature isn't available yet. "
        "However, I can help you with:\n"
        "• Booking individual flights\n"
        "• Planning your itinerary\n"
        "Would any of these be helpful?"
    ),
)

# Template for DOMAIN_SHIFT drift
TEMPLATE_DOMAIN_SHIFT = DriftResponseTemplate(
    template_id="domain_shift",
    drift_types=[DriftType.DOMAIN_SHIFT],
    template_text=(
        "That's an interesting question about {topic}. "
        "I'm designed to help with {domain}, so that's outside my area. "
        "Here's what I can help with: {alternatives}"
    ),
    required_variables=["topic", "domain", "alternatives"],
    tone=DriftResponseTone.HELPFUL,
    example_output=(
        "That's an interesting question about quantum physics. "
        "I'm designed to help with travel booking, so that's outside my area. "
        "Here's what I can help with: flight searches, hotel reservations, and itinerary planning."
    ),
)

# Template for ABSTRACTION_CLIMB drift
TEMPLATE_ABSTRACTION_CLIMB = DriftResponseTemplate(
    template_id="abstraction_climb",
    drift_types=[DriftType.ABSTRACTION_CLIMB],
    template_text=(
        "That's a thoughtful question! "
        "I'm better at practical, actionable tasks than philosophical discussions. "
        "I could help you with concrete things like: {alternatives}"
    ),
    required_variables=["alternatives"],
    tone=DriftResponseTone.ENCOURAGING,
    example_output=(
        "That's a thoughtful question! "
        "I'm better at practical, actionable tasks than philosophical discussions. "
        "I could help you with concrete things like: planning a trip, finding flights, or creating a budget."
    ),
)

# Template for PERSONALIZATION drift
TEMPLATE_PERSONALIZATION = DriftResponseTemplate(
    template_id="personalization",
    drift_types=[DriftType.PERSONALIZATION],
    template_text=(
        "I'd like to help with that, but I don't have access to your personal "
        "{data_type} information. What I can do is: {alternatives}"
    ),
    required_variables=["data_type", "alternatives"],
    tone=DriftResponseTone.APOLOGETIC,
    example_output=(
        "I'd like to help with that, but I don't have access to your personal "
        "account information. What I can do is: provide general guidance or help you reset your settings."
    ),
)

# Template for TEMPORAL_DRIFT drift
TEMPLATE_TEMPORAL_DRIFT = DriftResponseTemplate(
    template_id="temporal_drift",
    drift_types=[DriftType.TEMPORAL_DRIFT],
    template_text=(
        "Good question about {time_reference}. "
        "My knowledge has limitations on {temporal_scope}. "
        "I can help with current information like: {alternatives}"
    ),
    required_variables=["time_reference", "temporal_scope"],
    tone=DriftResponseTone.HELPFUL,
    example_output=(
        "Good question about next year's schedule. "
        "My knowledge has limitations on future events. "
        "I can help with current information like: today's availability and recent updates."
    ),
)

# Template for AMBIGUOUS drift
TEMPLATE_AMBIGUOUS = DriftResponseTemplate(
    template_id="ambiguous",
    drift_types=[DriftType.AMBIGUOUS],
    template_text=(
        "I want to make sure I understand you correctly. "
        "Did you mean:\n{options}\n"
        "Please let me know which one, or clarify what you're looking for."
    ),
    required_variables=["options"],
    tone=DriftResponseTone.HELPFUL,
    example_output=(
        "I want to make sure I understand you correctly. "
        "Did you mean:\n"
        "• Book a flight\n"
        "• Search for flights\n"
        "Please let me know which one, or clarify what you're looking for."
    ),
)

# Escalation template for severe drift
TEMPLATE_ESCALATION = DriftResponseTemplate(
    template_id="escalation",
    drift_types=[DriftType.DOMAIN_SHIFT, DriftType.ABSTRACTION_CLIMB],
    template_text=(
        "This request is quite complex. "
        "Would you like me to {escalation_option}? "
        "I want to make sure you get the help you need."
    ),
    required_variables=["escalation_option"],
    tone=DriftResponseTone.PROFESSIONAL,
    example_output=(
        "This request is quite complex. "
        "Would you like me to connect you with a human specialist? "
        "I want to make sure you get the help you need."
    ),
)

# Map drift types to their primary templates
DRIFT_TEMPLATES: dict[DriftType, DriftResponseTemplate] = {
    DriftType.NONE: TEMPLATE_NONE,
    DriftType.SCOPE_EXPANSION: TEMPLATE_SCOPE_EXPANSION,
    DriftType.DOMAIN_SHIFT: TEMPLATE_DOMAIN_SHIFT,
    DriftType.ABSTRACTION_CLIMB: TEMPLATE_ABSTRACTION_CLIMB,
    DriftType.PERSONALIZATION: TEMPLATE_PERSONALIZATION,
    DriftType.TEMPORAL_DRIFT: TEMPLATE_TEMPORAL_DRIFT,
    DriftType.AMBIGUOUS: TEMPLATE_AMBIGUOUS,
}


# ============================================
# Response Type Mapping
# ============================================

DRIFT_TO_RESPONSE_TYPE: dict[DriftType, GracefulResponseType] = {
    DriftType.NONE: GracefulResponseType.PARTIAL_HELP,  # Can fully help
    DriftType.SCOPE_EXPANSION: GracefulResponseType.PARTIAL_HELP,
    DriftType.DOMAIN_SHIFT: GracefulResponseType.BOUNDARY_STATEMENT,
    DriftType.ABSTRACTION_CLIMB: GracefulResponseType.REDIRECT,
    DriftType.PERSONALIZATION: GracefulResponseType.BOUNDARY_STATEMENT,
    DriftType.TEMPORAL_DRIFT: GracefulResponseType.BOUNDARY_STATEMENT,
    DriftType.AMBIGUOUS: GracefulResponseType.CLARIFICATION,
}


# ============================================
# Configuration
# ============================================

@dataclass
class ResponseGeneratorConfig:
    """Configuration for response generator.

    Attributes:
        max_alternatives: Maximum alternatives to show
        include_acknowledgment: Whether to include acknowledgment
        include_follow_up: Whether to include follow-up prompt
        escalation_threshold: Drift score threshold for escalation
        default_domain: Default domain description
        personalization_data_types: Common personalization data types
    """

    max_alternatives: int = 3
    include_acknowledgment: bool = True
    include_follow_up: bool = True
    escalation_threshold: float = 0.8
    default_domain: str = "task management"
    personalization_data_types: dict[str, str] = field(default_factory=lambda: {
        "password": "account credentials",
        "email": "email address",
        "phone": "phone number",
        "address": "address",
        "payment": "payment details",
        "history": "browsing history",
        "preference": "personal preferences",
    })

    @classmethod
    def default(cls) -> ResponseGeneratorConfig:
        """Create default configuration."""
        return cls()

    @classmethod
    def minimal(cls) -> ResponseGeneratorConfig:
        """Create minimal configuration (no acknowledgments/follow-ups)."""
        return cls(
            include_acknowledgment=False,
            include_follow_up=False,
        )


# ============================================
# Acknowledgment Templates
# ============================================

ACKNOWLEDGMENTS: dict[DriftType, list[str]] = {
    DriftType.NONE: [
        "Great question!",
        "I'd be happy to help with that.",
        "Sure thing!",
    ],
    DriftType.SCOPE_EXPANSION: [
        "I see what you're looking for.",
        "That's a reasonable request.",
        "I understand what you need.",
    ],
    DriftType.DOMAIN_SHIFT: [
        "Interesting question!",
        "I appreciate your curiosity.",
        "That's a good question.",
    ],
    DriftType.ABSTRACTION_CLIMB: [
        "That's quite thought-provoking!",
        "Interesting perspective!",
        "I can see you're thinking deeply about this.",
    ],
    DriftType.PERSONALIZATION: [
        "I understand you'd like personalized help.",
        "That's a reasonable request for your specific situation.",
        "I can see why you'd want that.",
    ],
    DriftType.TEMPORAL_DRIFT: [
        "That's a forward-looking question.",
        "I appreciate your interest in future planning.",
        "Good thinking about timing.",
    ],
    DriftType.AMBIGUOUS: [
        "Let me make sure I understand.",
        "I want to help with exactly what you need.",
        "Thanks for reaching out.",
    ],
}


# ============================================
# Follow-up Prompts
# ============================================

FOLLOW_UP_PROMPTS: dict[DriftType, list[str]] = {
    DriftType.NONE: [
        "What would you like to know?",
        "How can I help you further?",
        "What else can I do for you?",
    ],
    DriftType.SCOPE_EXPANSION: [
        "Would any of these alternatives work for you?",
        "Is there something else I can help with?",
        "Let me know if you'd like to try one of these options.",
    ],
    DriftType.DOMAIN_SHIFT: [
        "Would you like to explore any of these instead?",
        "Is there anything within my capabilities I can help with?",
        "Feel free to ask about anything in my area.",
    ],
    DriftType.ABSTRACTION_CLIMB: [
        "Would you like to start with one of these practical steps?",
        "Which of these would be most helpful right now?",
        "Let me know if any of these interest you.",
    ],
    DriftType.PERSONALIZATION: [
        "Would you like general guidance instead?",
        "Can I help in a more general way?",
        "Is there a general version of this I could help with?",
    ],
    DriftType.TEMPORAL_DRIFT: [
        "Would current information be helpful?",
        "Can I help with what's available now?",
        "Is there something current I can look up?",
    ],
    DriftType.AMBIGUOUS: [
        "Which one did you have in mind?",
        "Can you tell me more about what you need?",
        "What specifically are you looking for?",
    ],
}


# ============================================
# Graceful Response Generator
# ============================================

class GracefulResponseGenerator:
    """Generates graceful responses for drift scenarios.

    This generator creates natural, helpful responses that:
    - Acknowledge the user's request
    - Explain limitations honestly but briefly
    - Offer actionable alternatives
    - Include appropriate follow-up prompts

    Example:
        >>> generator = GracefulResponseGenerator()
        >>> response = generator.generate(
        ...     drift_classification=classification,
        ...     redirect_suggestions=suggestions,
        ...     user_input="What's the meaning of life?",
        ... )
        >>> print(response.to_message())
    """

    def __init__(self, config: Optional[ResponseGeneratorConfig] = None):
        """Initialize the response generator.

        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self.config = config or ResponseGeneratorConfig.default()

    def generate(
        self,
        drift_classification: DriftClassification,
        redirect_suggestions: list[RedirectSuggestion],
        user_input: str,
        context: Optional[dict[str, str]] = None,
    ) -> GracefulResponse:
        """Generate a graceful response for a drift scenario.

        Args:
            drift_classification: Classification of the drift
            redirect_suggestions: Suggested alternative capabilities
            user_input: The original user input
            context: Optional additional context for template variables

        Returns:
            GracefulResponse with appropriate messaging
        """
        drift_type = drift_classification.drift_type
        context = context or {}

        # Get response type
        response_type = DRIFT_TO_RESPONSE_TYPE.get(
            drift_type, GracefulResponseType.CLARIFICATION
        )

        # Check for escalation
        should_escalate = self._should_escalate(drift_classification)

        # Build template variables
        variables = self._build_variables(
            drift_type=drift_type,
            user_input=user_input,
            redirect_suggestions=redirect_suggestions,
            context=context,
        )

        # Get primary message from template
        primary_message = self._render_template(drift_type, variables)

        # Build alternatives
        alternatives = self._build_alternatives(redirect_suggestions)

        # Get acknowledgment
        acknowledgment = None
        if self.config.include_acknowledgment:
            acknowledgment = self._get_acknowledgment(drift_type)

        # Get follow-up prompt
        follow_up = None
        if self.config.include_follow_up:
            follow_up = self._get_follow_up(drift_type)

        # Get tone
        template = DRIFT_TEMPLATES.get(drift_type, TEMPLATE_AMBIGUOUS)
        tone = template.tone

        # Build explanation
        explanation = self._build_explanation(drift_classification)

        # Handle escalation
        if should_escalate:
            primary_message = self._add_escalation(primary_message)
            response_type = GracefulResponseType.ESCALATION

        return GracefulResponse(
            response_type=response_type,
            primary_message=primary_message,
            tone=tone,
            acknowledgment=acknowledgment,
            explanation=explanation,
            alternatives=alternatives,
            follow_up_prompt=follow_up,
        )

    def generate_simple(
        self,
        drift_type: DriftType,
        user_input: str,
        alternatives: Optional[list[str]] = None,
    ) -> GracefulResponse:
        """Generate a simple response without full classification.

        Convenience method for quick response generation.

        Args:
            drift_type: The type of drift
            user_input: The original user input
            alternatives: Optional list of alternative descriptions

        Returns:
            GracefulResponse with appropriate messaging
        """
        # Create simple redirect suggestions from alternatives
        redirect_suggestions = []
        if alternatives:
            for i, alt in enumerate(alternatives):
                redirect_suggestions.append(
                    RedirectSuggestion(
                        target_intent=f"alternative_{i}",
                        similarity_score=0.5,
                        redirect_reason="Alternative capability",
                        transition_phrase=alt,
                        confidence=0.5,
                    )
                )

        # Create minimal classification
        from .drift_classifier import DriftClassification
        classification = DriftClassification(
            drift_type=drift_type,
            drift_score=0.5,
            confidence=0.5,
        )

        return self.generate(
            drift_classification=classification,
            redirect_suggestions=redirect_suggestions,
            user_input=user_input,
        )

    def _should_escalate(self, classification: DriftClassification) -> bool:
        """Determine if escalation should be offered.

        Args:
            classification: The drift classification

        Returns:
            True if escalation should be offered
        """
        # Escalate for severe drift
        if classification.drift_score >= self.config.escalation_threshold:
            return True

        # Escalate for certain drift types with low confidence
        if (
            classification.drift_type in [DriftType.DOMAIN_SHIFT, DriftType.ABSTRACTION_CLIMB]
            and classification.confidence < 0.5
        ):
            return True

        return False

    def _build_variables(
        self,
        drift_type: DriftType,
        user_input: str,
        redirect_suggestions: list[RedirectSuggestion],
        context: dict[str, str],
    ) -> dict[str, str]:
        """Build template variables from inputs.

        Args:
            drift_type: The drift type
            user_input: Original user input
            redirect_suggestions: Suggested alternatives
            context: Additional context

        Returns:
            Dictionary of template variables
        """
        variables: dict[str, str] = dict(context)

        # Common variables
        variables["request"] = self._summarize_request(user_input)

        # Build alternatives string
        alternatives_list = [s.transition_phrase for s in redirect_suggestions[:self.config.max_alternatives]]
        if alternatives_list:
            variables["alternatives"] = "\n".join(f"• {alt}" for alt in alternatives_list)
        else:
            variables["alternatives"] = "general assistance"

        # Type-specific variables
        if drift_type == DriftType.DOMAIN_SHIFT:
            variables.setdefault("topic", self._extract_topic(user_input))
            variables.setdefault("domain", self.config.default_domain)

        elif drift_type == DriftType.PERSONALIZATION:
            variables.setdefault("data_type", self._detect_data_type(user_input))

        elif drift_type == DriftType.TEMPORAL_DRIFT:
            variables.setdefault("time_reference", self._extract_time_reference(user_input))
            variables.setdefault("temporal_scope", "future events" if "will" in user_input.lower() else "past events")

        elif drift_type == DriftType.AMBIGUOUS:
            # Build options from alternatives
            if alternatives_list:
                variables["options"] = "\n".join(f"• {alt}" for alt in alternatives_list)
            else:
                variables["options"] = "• Option A\n• Option B"

        elif drift_type == DriftType.NONE:
            variables.setdefault("action_prompt", "What would you like to do?")

        return variables

    def _render_template(
        self,
        drift_type: DriftType,
        variables: dict[str, str],
    ) -> str:
        """Render the appropriate template.

        Args:
            drift_type: The drift type
            variables: Template variables

        Returns:
            Rendered template string
        """
        template = DRIFT_TEMPLATES.get(drift_type, TEMPLATE_AMBIGUOUS)

        # Fill in any missing required variables with defaults
        for var in template.required_variables:
            if var not in variables:
                variables[var] = self._get_default_variable(var)

        try:
            return template.render(variables)
        except (KeyError, ValueError):
            # Fallback to simple substitution
            result = template.template_text
            for key, value in variables.items():
                result = result.replace(f"{{{key}}}", value)
            return result

    def _build_alternatives(
        self,
        redirect_suggestions: list[RedirectSuggestion],
    ) -> list[Redirect]:
        """Build Redirect list from suggestions.

        Args:
            redirect_suggestions: Suggested alternatives

        Returns:
            List of Redirect objects
        """
        alternatives = []
        for suggestion in redirect_suggestions[:self.config.max_alternatives]:
            alternatives.append(
                Redirect(
                    capability_name=suggestion.target_intent,
                    description=suggestion.transition_phrase,
                    relevance_score=suggestion.similarity_score,
                    action_phrase=suggestion.transition_phrase,
                )
            )
        return alternatives

    def _get_acknowledgment(self, drift_type: DriftType) -> str:
        """Get an acknowledgment phrase for the drift type.

        Args:
            drift_type: The drift type

        Returns:
            Acknowledgment phrase
        """
        acknowledgments = ACKNOWLEDGMENTS.get(drift_type, ACKNOWLEDGMENTS[DriftType.NONE])
        # Return first one for consistency (could be randomized)
        return acknowledgments[0]

    def _get_follow_up(self, drift_type: DriftType) -> str:
        """Get a follow-up prompt for the drift type.

        Args:
            drift_type: The drift type

        Returns:
            Follow-up prompt
        """
        prompts = FOLLOW_UP_PROMPTS.get(drift_type, FOLLOW_UP_PROMPTS[DriftType.NONE])
        return prompts[0]

    def _build_explanation(self, classification: DriftClassification) -> str:
        """Build explanation from classification reasoning.

        Args:
            classification: The drift classification

        Returns:
            Explanation string
        """
        if classification.reasoning:
            return classification.reasoning
        return ""

    def _add_escalation(self, message: str) -> str:
        """Add escalation offer to message.

        Args:
            message: The current message

        Returns:
            Message with escalation offer
        """
        escalation = (
            "\n\nIf you'd prefer, I can connect you with someone "
            "who might be able to help further."
        )
        return message + escalation

    def _summarize_request(self, user_input: str) -> str:
        """Summarize user request for template.

        Args:
            user_input: Original user input

        Returns:
            Summarized request (truncated if needed)
        """
        # Clean and truncate
        clean = user_input.strip()
        if len(clean) > 50:
            return clean[:47] + "..."
        return clean

    def _extract_topic(self, user_input: str) -> str:
        """Extract main topic from user input.

        Args:
            user_input: Original user input

        Returns:
            Extracted topic
        """
        # Simple extraction - first noun phrase or subject
        words = user_input.split()
        # Filter common words
        stop_words = {"what", "is", "the", "a", "an", "how", "why", "when", "where", "can", "you", "i", "do"}
        meaningful = [w for w in words if w.lower() not in stop_words]
        if meaningful:
            return " ".join(meaningful[:3])
        return "that topic"

    def _detect_data_type(self, user_input: str) -> str:
        """Detect type of personal data referenced.

        Args:
            user_input: Original user input

        Returns:
            Data type description
        """
        lower_input = user_input.lower()
        for keyword, data_type in self.config.personalization_data_types.items():
            if keyword in lower_input:
                return data_type
        return "personal"

    def _extract_time_reference(self, user_input: str) -> str:
        """Extract temporal reference from input.

        Args:
            user_input: Original user input

        Returns:
            Time reference description
        """
        lower_input = user_input.lower()

        # Future patterns
        future_patterns = ["tomorrow", "next week", "next month", "next year", "will", "going to", "future"]
        for pattern in future_patterns:
            if pattern in lower_input:
                return f"future ({pattern})"

        # Past patterns
        past_patterns = ["yesterday", "last week", "last month", "last year", "was", "were", "did", "past"]
        for pattern in past_patterns:
            if pattern in lower_input:
                return f"past ({pattern})"

        return "that time period"

    def _get_default_variable(self, var_name: str) -> str:
        """Get default value for a variable.

        Args:
            var_name: Variable name

        Returns:
            Default value
        """
        defaults = {
            "request": "your request",
            "alternatives": "general assistance",
            "topic": "that topic",
            "domain": self.config.default_domain,
            "data_type": "personal",
            "time_reference": "that time",
            "temporal_scope": "specific dates",
            "options": "• Option A\n• Option B",
            "action_prompt": "How can I help?",
            "escalation_option": "connect you with a specialist",
        }
        return defaults.get(var_name, "")

    def get_template_for_type(self, drift_type: DriftType) -> DriftResponseTemplate:
        """Get the template for a drift type.

        Args:
            drift_type: The drift type

        Returns:
            The corresponding template
        """
        return DRIFT_TEMPLATES.get(drift_type, TEMPLATE_AMBIGUOUS)

    def get_all_templates(self) -> dict[DriftType, DriftResponseTemplate]:
        """Get all drift templates.

        Returns:
            Dictionary of drift types to templates
        """
        return dict(DRIFT_TEMPLATES)
