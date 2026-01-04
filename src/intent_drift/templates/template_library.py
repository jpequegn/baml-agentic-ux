"""Response template library for intent drift detection.

This module provides a comprehensive library of response templates for all drift
scenarios and edge cases, organized by category with multiple variations.

Issue #86 - Task 5.9: Response Template Library
Part of #28 - Phase 5: Intent Drift Detection
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from ..types import DriftResponseTone, DriftType


# ============================================
# Template Category Enum
# ============================================


class TemplateCategory(Enum):
    """Categories of response templates."""

    CAPABILITY_LIMIT = "capability_limit"
    """Templates for when user request exceeds capabilities."""

    UNCERTAINTY = "uncertainty"
    """Templates for when there's uncertainty about the response."""

    REDIRECT = "redirect"
    """Templates for redirecting to alternative capabilities."""

    CLARIFICATION = "clarification"
    """Templates for asking clarifying questions."""

    ESCALATION = "escalation"
    """Templates for escalating to human support."""

    IN_SCOPE = "in_scope"
    """Templates for requests that are within scope."""


# ============================================
# Template Configuration
# ============================================


@dataclass
class TemplateConfig:
    """Configuration for template selection and rendering.

    Attributes:
        drift_type: The type of drift to address
        tone: Desired response tone
        include_alternatives: Whether to include alternative suggestions
        include_escalation: Whether to include escalation option
        max_alternatives: Maximum number of alternatives to show
    """

    drift_type: DriftType
    tone: DriftResponseTone = DriftResponseTone.HELPFUL
    include_alternatives: bool = True
    include_escalation: bool = False
    max_alternatives: int = 3

    def __post_init__(self) -> None:
        """Validate configuration."""
        if self.max_alternatives < 0:
            raise ValueError("max_alternatives must be non-negative")
        if self.max_alternatives > 10:
            raise ValueError("max_alternatives must be at most 10")


# ============================================
# Response Template
# ============================================


@dataclass
class ResponseTemplate:
    """A response template with metadata.

    Attributes:
        template_id: Unique identifier for the template
        category: The template category
        drift_types: Drift types this template applies to
        template_text: The template string with placeholders
        required_variables: Variables required for rendering
        tone: The tone of the template
        description: Human-readable description of when to use
        example_output: Example of rendered output
    """

    template_id: str
    category: TemplateCategory
    drift_types: list[DriftType]
    template_text: str
    required_variables: list[str]
    tone: DriftResponseTone = DriftResponseTone.HELPFUL
    description: str = ""
    example_output: str = ""

    def render(self, variables: dict[str, str]) -> str:
        """Render the template with provided variables.

        Args:
            variables: Dictionary mapping variable names to values

        Returns:
            Rendered template string

        Raises:
            ValueError: If required variables are missing
        """
        missing = [v for v in self.required_variables if v not in variables]
        if missing:
            raise ValueError(f"Missing required variables: {missing}")

        result = self.template_text
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result

    def can_handle(self, drift_type: DriftType) -> bool:
        """Check if this template can handle a drift type.

        Args:
            drift_type: The drift type to check

        Returns:
            True if this template handles the drift type
        """
        return drift_type in self.drift_types


# ============================================
# Capability Limit Templates
# ============================================

CAPABILITY_SIMPLE_LIMITATION = ResponseTemplate(
    template_id="capability_simple_limitation",
    category=TemplateCategory.CAPABILITY_LIMIT,
    drift_types=[DriftType.SCOPE_EXPANSION, DriftType.DOMAIN_SHIFT],
    template_text="I'm not able to {action}, but I can {alternative}. Would that help?",
    required_variables=["action", "alternative"],
    tone=DriftResponseTone.HELPFUL,
    description="Simple, direct acknowledgment of limitation with alternative",
    example_output="I'm not able to book international flights, but I can help you search for domestic routes. Would that help?",
)

CAPABILITY_TRANSPARENT_SCOPE = ResponseTemplate(
    template_id="capability_transparent_scope",
    category=TemplateCategory.CAPABILITY_LIMIT,
    drift_types=[DriftType.SCOPE_EXPANSION, DriftType.DOMAIN_SHIFT],
    template_text=(
        "That's outside my capabilities right now. I'm designed to handle:\n"
        "{capabilities}\n"
        "For {original_request}, I can connect you with {resource}."
    ),
    required_variables=["capabilities", "original_request", "resource"],
    tone=DriftResponseTone.PROFESSIONAL,
    description="Transparent about scope with clear list of capabilities",
    example_output=(
        "That's outside my capabilities right now. I'm designed to handle:\n"
        "- Flight searches\n"
        "- Hotel bookings\n"
        "- Itinerary planning\n"
        "For currency exchange, I can connect you with our finance team."
    ),
)

CAPABILITY_COMPLEX_BREAKDOWN = ResponseTemplate(
    template_id="capability_complex_breakdown",
    category=TemplateCategory.CAPABILITY_LIMIT,
    drift_types=[DriftType.SCOPE_EXPANSION],
    template_text=(
        "That's a multi-part request. I can handle {parts_possible}. "
        "For {parts_not_possible}, you'll need to {alternative_process}."
    ),
    required_variables=["parts_possible", "parts_not_possible", "alternative_process"],
    tone=DriftResponseTone.HELPFUL,
    description="Breaks down complex requests into handleable parts",
    example_output=(
        "That's a multi-part request. I can handle the flight search and hotel booking. "
        "For visa requirements, you'll need to check with the embassy directly."
    ),
)

CAPABILITY_HONEST_BOUNDARY = ResponseTemplate(
    template_id="capability_honest_boundary",
    category=TemplateCategory.CAPABILITY_LIMIT,
    drift_types=[DriftType.DOMAIN_SHIFT, DriftType.ABSTRACTION_CLIMB],
    template_text=(
        "I appreciate you asking, but {request} falls outside what I can help with. "
        "My expertise is in {domain}. Would you like to explore options there?"
    ),
    required_variables=["request", "domain"],
    tone=DriftResponseTone.APOLOGETIC,
    description="Honest boundary statement with domain focus",
    example_output=(
        "I appreciate you asking, but legal advice falls outside what I can help with. "
        "My expertise is in travel planning. Would you like to explore options there?"
    ),
)

CAPABILITY_FUTURE_POTENTIAL = ResponseTemplate(
    template_id="capability_future_potential",
    category=TemplateCategory.CAPABILITY_LIMIT,
    drift_types=[DriftType.SCOPE_EXPANSION],
    template_text=(
        "That feature isn't available yet, but it's a great suggestion. "
        "In the meantime, I can help you with {workaround}. "
        "Would you like to try that approach?"
    ),
    required_variables=["workaround"],
    tone=DriftResponseTone.ENCOURAGING,
    description="Acknowledges feature gap while offering workaround",
    example_output=(
        "That feature isn't available yet, but it's a great suggestion. "
        "In the meantime, I can help you with booking each leg separately. "
        "Would you like to try that approach?"
    ),
)


# ============================================
# Uncertainty Templates
# ============================================

UNCERTAINTY_CONFIDENT = ResponseTemplate(
    template_id="uncertainty_confident",
    category=TemplateCategory.UNCERTAINTY,
    drift_types=[DriftType.AMBIGUOUS, DriftType.TEMPORAL_DRIFT],
    template_text=(
        "I don't have that specific information. Rather than guess, "
        "let me {escalation_action}."
    ),
    required_variables=["escalation_action"],
    tone=DriftResponseTone.PROFESSIONAL,
    description="Confidently admits uncertainty and offers escalation",
    example_output=(
        "I don't have that specific information. Rather than guess, "
        "let me connect you with someone who has access to those records."
    ),
)

UNCERTAINTY_PARTIAL_KNOWLEDGE = ResponseTemplate(
    template_id="uncertainty_partial_knowledge",
    category=TemplateCategory.UNCERTAINTY,
    drift_types=[DriftType.AMBIGUOUS, DriftType.TEMPORAL_DRIFT],
    template_text=(
        "I know {known_part}, but I'm uncertain about {uncertain_part}. "
        "Would you like me to proceed with what I'm certain about?"
    ),
    required_variables=["known_part", "uncertain_part"],
    tone=DriftResponseTone.HELPFUL,
    description="Distinguishes known from uncertain information",
    example_output=(
        "I know the flight departs at 3pm, but I'm uncertain about the gate number. "
        "Would you like me to proceed with what I'm certain about?"
    ),
)

UNCERTAINTY_VERIFICATION_NEEDED = ResponseTemplate(
    template_id="uncertainty_verification_needed",
    category=TemplateCategory.UNCERTAINTY,
    drift_types=[DriftType.TEMPORAL_DRIFT, DriftType.PERSONALIZATION],
    template_text=(
        "I have some information about {topic}, but it may be outdated. "
        "I'd recommend verifying {verification_point} before proceeding. "
        "Would you like me to share what I have?"
    ),
    required_variables=["topic", "verification_point"],
    tone=DriftResponseTone.HELPFUL,
    description="Suggests verification for potentially outdated info",
    example_output=(
        "I have some information about the pricing, but it may be outdated. "
        "I'd recommend verifying current rates on the airline's website before proceeding. "
        "Would you like me to share what I have?"
    ),
)

UNCERTAINTY_BEST_EFFORT = ResponseTemplate(
    template_id="uncertainty_best_effort",
    category=TemplateCategory.UNCERTAINTY,
    drift_types=[DriftType.AMBIGUOUS],
    template_text=(
        "Based on what you've shared, my best understanding is {interpretation}. "
        "Is that what you meant, or should I approach this differently?"
    ),
    required_variables=["interpretation"],
    tone=DriftResponseTone.HELPFUL,
    description="Offers interpretation for confirmation",
    example_output=(
        "Based on what you've shared, my best understanding is you want a round-trip flight to London next month. "
        "Is that what you meant, or should I approach this differently?"
    ),
)


# ============================================
# Redirect Templates
# ============================================

REDIRECT_RELATED_FEATURE = ResponseTemplate(
    template_id="redirect_related_feature",
    category=TemplateCategory.REDIRECT,
    drift_types=[DriftType.SCOPE_EXPANSION, DriftType.DOMAIN_SHIFT],
    template_text=(
        "I can't do {requested}, but I CAN help you achieve a similar "
        "result by {alternative}. Would you like to try that?"
    ),
    required_variables=["requested", "alternative"],
    tone=DriftResponseTone.ENCOURAGING,
    description="Pivots to related feature that can achieve similar outcome",
    example_output=(
        "I can't do real-time price tracking, but I CAN help you achieve a similar "
        "result by setting up daily price alerts. Would you like to try that?"
    ),
)

REDIRECT_MULTI_OPTION = ResponseTemplate(
    template_id="redirect_multi_option",
    category=TemplateCategory.REDIRECT,
    drift_types=[DriftType.SCOPE_EXPANSION, DriftType.DOMAIN_SHIFT, DriftType.ABSTRACTION_CLIMB],
    template_text=(
        "For {request}, here are your best options:\n"
        "{options}\n"
        "Which works best for you?"
    ),
    required_variables=["request", "options"],
    tone=DriftResponseTone.HELPFUL,
    description="Offers multiple alternative options",
    example_output=(
        "For tracking your expenses, here are your best options:\n"
        "- Export your bookings to a spreadsheet\n"
        "- View your booking history summary\n"
        "- Download receipts for all trips\n"
        "Which works best for you?"
    ),
)

REDIRECT_STEPPING_STONE = ResponseTemplate(
    template_id="redirect_stepping_stone",
    category=TemplateCategory.REDIRECT,
    drift_types=[DriftType.ABSTRACTION_CLIMB],
    template_text=(
        "That's a big goal! Let's break it down. A good first step would be {first_step}. "
        "From there, I can help you with {next_steps}. Sound good?"
    ),
    required_variables=["first_step", "next_steps"],
    tone=DriftResponseTone.ENCOURAGING,
    description="Breaks abstract goal into concrete first step",
    example_output=(
        "That's a big goal! Let's break it down. A good first step would be defining your budget. "
        "From there, I can help you with destination research and booking. Sound good?"
    ),
)

REDIRECT_DOMAIN_EXPERT = ResponseTemplate(
    template_id="redirect_domain_expert",
    category=TemplateCategory.REDIRECT,
    drift_types=[DriftType.DOMAIN_SHIFT],
    template_text=(
        "For {topic}, you'd be better served by {expert_resource}. "
        "They specialize in exactly this kind of request. "
        "In the meantime, is there anything in {my_domain} I can help with?"
    ),
    required_variables=["topic", "expert_resource", "my_domain"],
    tone=DriftResponseTone.HELPFUL,
    description="Redirects to domain expert while offering own capabilities",
    example_output=(
        "For tax advice, you'd be better served by a certified accountant. "
        "They specialize in exactly this kind of request. "
        "In the meantime, is there anything in travel planning I can help with?"
    ),
)

REDIRECT_PARTIAL_HELP = ResponseTemplate(
    template_id="redirect_partial_help",
    category=TemplateCategory.REDIRECT,
    drift_types=[DriftType.SCOPE_EXPANSION, DriftType.PERSONALIZATION],
    template_text=(
        "While I can't fully {full_request}, I can definitely help with {partial_help}. "
        "That would get you {benefit}. Want me to start there?"
    ),
    required_variables=["full_request", "partial_help", "benefit"],
    tone=DriftResponseTone.HELPFUL,
    description="Offers partial solution with clear benefit",
    example_output=(
        "While I can't fully manage your entire trip, I can definitely help with finding and booking flights. "
        "That would get you the best prices locked in. Want me to start there?"
    ),
)


# ============================================
# Clarification Templates
# ============================================

CLARIFICATION_DID_YOU_MEAN = ResponseTemplate(
    template_id="clarification_did_you_mean",
    category=TemplateCategory.CLARIFICATION,
    drift_types=[DriftType.AMBIGUOUS],
    template_text=(
        "I found some similar requests:\n"
        "{interpretations}\n"
        "Which is closest to what you need?"
    ),
    required_variables=["interpretations"],
    tone=DriftResponseTone.HELPFUL,
    description="Offers multiple interpretations for selection",
    example_output=(
        "I found some similar requests:\n"
        "- Book a one-way flight\n"
        "- Search for flight options\n"
        "- Check flight status\n"
        "Which is closest to what you need?"
    ),
)

CLARIFICATION_AMBIGUITY_RESOLUTION = ResponseTemplate(
    template_id="clarification_ambiguity_resolution",
    category=TemplateCategory.CLARIFICATION,
    drift_types=[DriftType.AMBIGUOUS],
    template_text=(
        "'{ambiguous_term}' could mean different things:\n"
        "1. {meaning_1}\n"
        "2. {meaning_2}\n"
        "Which did you have in mind?"
    ),
    required_variables=["ambiguous_term", "meaning_1", "meaning_2"],
    tone=DriftResponseTone.HELPFUL,
    description="Resolves specific ambiguous term",
    example_output=(
        "'Change my flight' could mean different things:\n"
        "1. Reschedule to a different date\n"
        "2. Switch to a different airline\n"
        "Which did you have in mind?"
    ),
)

CLARIFICATION_MISSING_DETAIL = ResponseTemplate(
    template_id="clarification_missing_detail",
    category=TemplateCategory.CLARIFICATION,
    drift_types=[DriftType.AMBIGUOUS, DriftType.NONE],
    template_text=(
        "I'd be happy to help with that! To give you the best results, "
        "could you tell me {missing_info}?"
    ),
    required_variables=["missing_info"],
    tone=DriftResponseTone.HELPFUL,
    description="Requests specific missing information",
    example_output=(
        "I'd be happy to help with that! To give you the best results, "
        "could you tell me your preferred departure date and destination?"
    ),
)

CLARIFICATION_CONFIRM_UNDERSTANDING = ResponseTemplate(
    template_id="clarification_confirm_understanding",
    category=TemplateCategory.CLARIFICATION,
    drift_types=[DriftType.AMBIGUOUS],
    template_text=(
        "Just to confirm, you're looking to {understood_action}, correct? "
        "I want to make sure I help you with exactly what you need."
    ),
    required_variables=["understood_action"],
    tone=DriftResponseTone.HELPFUL,
    description="Confirms understanding before proceeding",
    example_output=(
        "Just to confirm, you're looking to book a flight from New York to Los Angeles for next Friday, correct? "
        "I want to make sure I help you with exactly what you need."
    ),
)

CLARIFICATION_CONTEXT_NEEDED = ResponseTemplate(
    template_id="clarification_context_needed",
    category=TemplateCategory.CLARIFICATION,
    drift_types=[DriftType.AMBIGUOUS, DriftType.PERSONALIZATION],
    template_text=(
        "To help you effectively, I need a bit more context. "
        "Specifically, {context_question} "
        "This will help me {benefit}."
    ),
    required_variables=["context_question", "benefit"],
    tone=DriftResponseTone.HELPFUL,
    description="Explains why context is needed",
    example_output=(
        "To help you effectively, I need a bit more context. "
        "Specifically, are you traveling for business or leisure? "
        "This will help me recommend the right class and amenities."
    ),
)


# ============================================
# Escalation Templates
# ============================================

ESCALATION_PROACTIVE = ResponseTemplate(
    template_id="escalation_proactive",
    category=TemplateCategory.ESCALATION,
    drift_types=[DriftType.DOMAIN_SHIFT, DriftType.ABSTRACTION_CLIMB, DriftType.PERSONALIZATION],
    template_text=(
        "I notice you're asking about {complex_topic}. A specialist can "
        "give you better guidance on this. Would you like me to connect you?"
    ),
    required_variables=["complex_topic"],
    tone=DriftResponseTone.PROFESSIONAL,
    description="Proactively offers escalation for complex topics",
    example_output=(
        "I notice you're asking about travel insurance claims. A specialist can "
        "give you better guidance on this. Would you like me to connect you?"
    ),
)

ESCALATION_FAILED_ATTEMPT = ResponseTemplate(
    template_id="escalation_failed_attempt",
    category=TemplateCategory.ESCALATION,
    drift_types=[DriftType.SCOPE_EXPANSION, DriftType.DOMAIN_SHIFT],
    template_text=(
        "I apologize - I'm having trouble with this request. Let me connect you "
        "with someone who can definitely help. One moment please."
    ),
    required_variables=[],
    tone=DriftResponseTone.APOLOGETIC,
    description="Escalates after failed attempt",
    example_output=(
        "I apologize - I'm having trouble with this request. Let me connect you "
        "with someone who can definitely help. One moment please."
    ),
)

ESCALATION_COMPLEXITY = ResponseTemplate(
    template_id="escalation_complexity",
    category=TemplateCategory.ESCALATION,
    drift_types=[DriftType.SCOPE_EXPANSION, DriftType.ABSTRACTION_CLIMB],
    template_text=(
        "This is quite a complex situation involving {complexity_factors}. "
        "I want to make sure you get the right help. Would you prefer to "
        "{escalation_options}?"
    ),
    required_variables=["complexity_factors", "escalation_options"],
    tone=DriftResponseTone.PROFESSIONAL,
    description="Acknowledges complexity and offers escalation options",
    example_output=(
        "This is quite a complex situation involving multiple bookings and a visa requirement. "
        "I want to make sure you get the right help. Would you prefer to "
        "speak with a travel agent or continue step-by-step with me?"
    ),
)

ESCALATION_SENSITIVITY = ResponseTemplate(
    template_id="escalation_sensitivity",
    category=TemplateCategory.ESCALATION,
    drift_types=[DriftType.PERSONALIZATION],
    template_text=(
        "This involves {sensitive_topic}, which requires special handling. "
        "For your security, I'll need to transfer you to our {specialist_team}. "
        "They'll take great care of you."
    ),
    required_variables=["sensitive_topic", "specialist_team"],
    tone=DriftResponseTone.PROFESSIONAL,
    description="Escalates due to sensitivity requirements",
    example_output=(
        "This involves your payment information, which requires special handling. "
        "For your security, I'll need to transfer you to our billing team. "
        "They'll take great care of you."
    ),
)

ESCALATION_USER_CHOICE = ResponseTemplate(
    template_id="escalation_user_choice",
    category=TemplateCategory.ESCALATION,
    drift_types=[DriftType.SCOPE_EXPANSION, DriftType.DOMAIN_SHIFT],
    template_text=(
        "I can {what_i_can_do}, or if you'd prefer more comprehensive help, "
        "I can connect you with {human_resource}. "
        "What would you prefer?"
    ),
    required_variables=["what_i_can_do", "human_resource"],
    tone=DriftResponseTone.HELPFUL,
    description="Gives user choice between self-service and escalation",
    example_output=(
        "I can help you search for flights and provide general booking info, or if you'd prefer more comprehensive help, "
        "I can connect you with a travel agent. "
        "What would you prefer?"
    ),
)


# ============================================
# In-Scope Templates
# ============================================

IN_SCOPE_READY_TO_HELP = ResponseTemplate(
    template_id="in_scope_ready_to_help",
    category=TemplateCategory.IN_SCOPE,
    drift_types=[DriftType.NONE],
    template_text="I can help you with {request}. {action_prompt}",
    required_variables=["request", "action_prompt"],
    tone=DriftResponseTone.HELPFUL,
    description="Ready to help with in-scope request",
    example_output="I can help you with booking a flight. What's your destination?",
)

IN_SCOPE_ENTHUSIASTIC = ResponseTemplate(
    template_id="in_scope_enthusiastic",
    category=TemplateCategory.IN_SCOPE,
    drift_types=[DriftType.NONE],
    template_text=(
        "Great question! I'd be happy to help you {action}. "
        "Let me {first_step}."
    ),
    required_variables=["action", "first_step"],
    tone=DriftResponseTone.ENCOURAGING,
    description="Enthusiastic response to in-scope request",
    example_output=(
        "Great question! I'd be happy to help you find the best flight deals. "
        "Let me search for options matching your criteria."
    ),
)

IN_SCOPE_PROFESSIONAL = ResponseTemplate(
    template_id="in_scope_professional",
    category=TemplateCategory.IN_SCOPE,
    drift_types=[DriftType.NONE],
    template_text="Certainly. I'll {action} for you now. {follow_up}",
    required_variables=["action", "follow_up"],
    tone=DriftResponseTone.PROFESSIONAL,
    description="Professional acknowledgment of in-scope request",
    example_output="Certainly. I'll search for available flights for you now. One moment please.",
)


# ============================================
# Template Collections
# ============================================

CAPABILITY_TEMPLATES: list[ResponseTemplate] = [
    CAPABILITY_SIMPLE_LIMITATION,
    CAPABILITY_TRANSPARENT_SCOPE,
    CAPABILITY_COMPLEX_BREAKDOWN,
    CAPABILITY_HONEST_BOUNDARY,
    CAPABILITY_FUTURE_POTENTIAL,
]

UNCERTAINTY_TEMPLATES: list[ResponseTemplate] = [
    UNCERTAINTY_CONFIDENT,
    UNCERTAINTY_PARTIAL_KNOWLEDGE,
    UNCERTAINTY_VERIFICATION_NEEDED,
    UNCERTAINTY_BEST_EFFORT,
]

REDIRECT_TEMPLATES: list[ResponseTemplate] = [
    REDIRECT_RELATED_FEATURE,
    REDIRECT_MULTI_OPTION,
    REDIRECT_STEPPING_STONE,
    REDIRECT_DOMAIN_EXPERT,
    REDIRECT_PARTIAL_HELP,
]

CLARIFICATION_TEMPLATES: list[ResponseTemplate] = [
    CLARIFICATION_DID_YOU_MEAN,
    CLARIFICATION_AMBIGUITY_RESOLUTION,
    CLARIFICATION_MISSING_DETAIL,
    CLARIFICATION_CONFIRM_UNDERSTANDING,
    CLARIFICATION_CONTEXT_NEEDED,
]

ESCALATION_TEMPLATES: list[ResponseTemplate] = [
    ESCALATION_PROACTIVE,
    ESCALATION_FAILED_ATTEMPT,
    ESCALATION_COMPLEXITY,
    ESCALATION_SENSITIVITY,
    ESCALATION_USER_CHOICE,
]

IN_SCOPE_TEMPLATES: list[ResponseTemplate] = [
    IN_SCOPE_READY_TO_HELP,
    IN_SCOPE_ENTHUSIASTIC,
    IN_SCOPE_PROFESSIONAL,
]

ALL_TEMPLATES: list[ResponseTemplate] = (
    CAPABILITY_TEMPLATES
    + UNCERTAINTY_TEMPLATES
    + REDIRECT_TEMPLATES
    + CLARIFICATION_TEMPLATES
    + ESCALATION_TEMPLATES
    + IN_SCOPE_TEMPLATES
)


# ============================================
# Template Library Class
# ============================================


class TemplateLibrary:
    """Library for managing and selecting response templates.

    Provides methods to:
    - Get templates by drift type
    - Get templates by category
    - Select appropriate template based on configuration
    - Render templates with variables

    Example:
        >>> library = TemplateLibrary()
        >>> templates = library.get_templates_for_drift_type(DriftType.SCOPE_EXPANSION)
        >>> template = library.select_template(
        ...     drift_type=DriftType.SCOPE_EXPANSION,
        ...     category=TemplateCategory.CAPABILITY_LIMIT,
        ... )
        >>> response = template.render({"action": "book", "alternative": "search"})
    """

    def __init__(self, templates: Optional[list[ResponseTemplate]] = None):
        """Initialize the template library.

        Args:
            templates: Optional custom templates. Uses defaults if not provided.
        """
        self._templates = templates if templates is not None else list(ALL_TEMPLATES)
        self._build_indices()

    def _build_indices(self) -> None:
        """Build lookup indices for fast template retrieval."""
        self._by_drift_type: dict[DriftType, list[ResponseTemplate]] = {}
        self._by_category: dict[TemplateCategory, list[ResponseTemplate]] = {}
        self._by_id: dict[str, ResponseTemplate] = {}

        for template in self._templates:
            # Index by drift type
            for drift_type in template.drift_types:
                if drift_type not in self._by_drift_type:
                    self._by_drift_type[drift_type] = []
                self._by_drift_type[drift_type].append(template)

            # Index by category
            if template.category not in self._by_category:
                self._by_category[template.category] = []
            self._by_category[template.category].append(template)

            # Index by ID
            self._by_id[template.template_id] = template

    def get_template_by_id(self, template_id: str) -> Optional[ResponseTemplate]:
        """Get a template by its ID.

        Args:
            template_id: The template ID

        Returns:
            The template, or None if not found
        """
        return self._by_id.get(template_id)

    def get_templates_for_drift_type(
        self,
        drift_type: DriftType,
        category: Optional[TemplateCategory] = None,
    ) -> list[ResponseTemplate]:
        """Get all templates that handle a drift type.

        Args:
            drift_type: The drift type
            category: Optional category filter

        Returns:
            List of matching templates
        """
        templates = self._by_drift_type.get(drift_type, [])
        if category is not None:
            templates = [t for t in templates if t.category == category]
        return templates

    def get_templates_for_category(
        self,
        category: TemplateCategory,
        drift_type: Optional[DriftType] = None,
    ) -> list[ResponseTemplate]:
        """Get all templates in a category.

        Args:
            category: The template category
            drift_type: Optional drift type filter

        Returns:
            List of matching templates
        """
        templates = self._by_category.get(category, [])
        if drift_type is not None:
            templates = [t for t in templates if drift_type in t.drift_types]
        return templates

    def select_template(
        self,
        drift_type: DriftType,
        category: Optional[TemplateCategory] = None,
        tone: Optional[DriftResponseTone] = None,
        random_selection: bool = False,
    ) -> Optional[ResponseTemplate]:
        """Select the best template for given criteria.

        Args:
            drift_type: The drift type to handle
            category: Optional preferred category
            tone: Optional preferred tone
            random_selection: If True, randomly select from candidates

        Returns:
            Selected template, or None if no match
        """
        candidates = self.get_templates_for_drift_type(drift_type, category)

        if not candidates:
            return None

        # Filter by tone if specified
        if tone is not None:
            tone_matches = [t for t in candidates if t.tone == tone]
            if tone_matches:
                candidates = tone_matches

        if random_selection and candidates:
            return random.choice(candidates)

        # Return first (most specific) match
        return candidates[0] if candidates else None

    def select_template_with_config(
        self,
        config: TemplateConfig,
        category: Optional[TemplateCategory] = None,
    ) -> Optional[ResponseTemplate]:
        """Select template using configuration.

        Args:
            config: Template configuration
            category: Optional category override

        Returns:
            Selected template, or None if no match
        """
        return self.select_template(
            drift_type=config.drift_type,
            category=category,
            tone=config.tone,
        )

    def get_all_categories(self) -> list[TemplateCategory]:
        """Get all available categories.

        Returns:
            List of template categories
        """
        return list(self._by_category.keys())

    def get_all_drift_types_covered(self) -> list[DriftType]:
        """Get all drift types covered by templates.

        Returns:
            List of covered drift types
        """
        return list(self._by_drift_type.keys())

    def get_template_count(self) -> int:
        """Get total number of templates.

        Returns:
            Number of templates in the library
        """
        return len(self._templates)

    def get_templates_by_tone(self, tone: DriftResponseTone) -> list[ResponseTemplate]:
        """Get all templates with a specific tone.

        Args:
            tone: The desired tone

        Returns:
            List of templates with that tone
        """
        return [t for t in self._templates if t.tone == tone]

    def add_template(self, template: ResponseTemplate) -> None:
        """Add a template to the library.

        Args:
            template: The template to add
        """
        self._templates.append(template)
        self._build_indices()

    def remove_template(self, template_id: str) -> bool:
        """Remove a template from the library.

        Args:
            template_id: ID of template to remove

        Returns:
            True if template was removed, False if not found
        """
        original_count = len(self._templates)
        self._templates = [t for t in self._templates if t.template_id != template_id]

        if len(self._templates) < original_count:
            self._build_indices()
            return True
        return False

    def get_category_summary(self) -> dict[TemplateCategory, int]:
        """Get count of templates per category.

        Returns:
            Dictionary mapping categories to template counts
        """
        return {cat: len(templates) for cat, templates in self._by_category.items()}

    def get_drift_type_summary(self) -> dict[DriftType, int]:
        """Get count of templates per drift type.

        Returns:
            Dictionary mapping drift types to template counts
        """
        return {dt: len(templates) for dt, templates in self._by_drift_type.items()}


# ============================================
# Default Library Instance
# ============================================

_default_library: Optional[TemplateLibrary] = None


def get_default_library() -> TemplateLibrary:
    """Get the default template library instance.

    Returns:
        The default TemplateLibrary instance
    """
    global _default_library
    if _default_library is None:
        _default_library = TemplateLibrary()
    return _default_library


def reset_default_library() -> None:
    """Reset the default template library instance."""
    global _default_library
    _default_library = None
