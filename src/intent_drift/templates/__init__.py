"""Response template library module.

This module provides a comprehensive library of response templates for all drift
scenarios and edge cases.

Issue #86 - Task 5.9: Response Template Library
Part of #28 - Phase 5: Intent Drift Detection
"""

from .template_library import (
    # Enums
    TemplateCategory,
    # Configuration
    TemplateConfig,
    # Core Classes
    ResponseTemplate,
    TemplateLibrary,
    # Capability Limit Templates
    CAPABILITY_SIMPLE_LIMITATION,
    CAPABILITY_TRANSPARENT_SCOPE,
    CAPABILITY_COMPLEX_BREAKDOWN,
    CAPABILITY_HONEST_BOUNDARY,
    CAPABILITY_FUTURE_POTENTIAL,
    CAPABILITY_TEMPLATES,
    # Uncertainty Templates
    UNCERTAINTY_CONFIDENT,
    UNCERTAINTY_PARTIAL_KNOWLEDGE,
    UNCERTAINTY_VERIFICATION_NEEDED,
    UNCERTAINTY_BEST_EFFORT,
    UNCERTAINTY_TEMPLATES,
    # Redirect Templates
    REDIRECT_RELATED_FEATURE,
    REDIRECT_MULTI_OPTION,
    REDIRECT_STEPPING_STONE,
    REDIRECT_DOMAIN_EXPERT,
    REDIRECT_PARTIAL_HELP,
    REDIRECT_TEMPLATES,
    # Clarification Templates
    CLARIFICATION_DID_YOU_MEAN,
    CLARIFICATION_AMBIGUITY_RESOLUTION,
    CLARIFICATION_MISSING_DETAIL,
    CLARIFICATION_CONFIRM_UNDERSTANDING,
    CLARIFICATION_CONTEXT_NEEDED,
    CLARIFICATION_TEMPLATES,
    # Escalation Templates
    ESCALATION_PROACTIVE,
    ESCALATION_FAILED_ATTEMPT,
    ESCALATION_COMPLEXITY,
    ESCALATION_SENSITIVITY,
    ESCALATION_USER_CHOICE,
    ESCALATION_TEMPLATES,
    # In-Scope Templates
    IN_SCOPE_READY_TO_HELP,
    IN_SCOPE_ENTHUSIASTIC,
    IN_SCOPE_PROFESSIONAL,
    IN_SCOPE_TEMPLATES,
    # All Templates
    ALL_TEMPLATES,
    # Factory Functions
    get_default_library,
    reset_default_library,
)

__all__ = [
    # Enums
    "TemplateCategory",
    # Configuration
    "TemplateConfig",
    # Core Classes
    "ResponseTemplate",
    "TemplateLibrary",
    # Capability Limit Templates
    "CAPABILITY_SIMPLE_LIMITATION",
    "CAPABILITY_TRANSPARENT_SCOPE",
    "CAPABILITY_COMPLEX_BREAKDOWN",
    "CAPABILITY_HONEST_BOUNDARY",
    "CAPABILITY_FUTURE_POTENTIAL",
    "CAPABILITY_TEMPLATES",
    # Uncertainty Templates
    "UNCERTAINTY_CONFIDENT",
    "UNCERTAINTY_PARTIAL_KNOWLEDGE",
    "UNCERTAINTY_VERIFICATION_NEEDED",
    "UNCERTAINTY_BEST_EFFORT",
    "UNCERTAINTY_TEMPLATES",
    # Redirect Templates
    "REDIRECT_RELATED_FEATURE",
    "REDIRECT_MULTI_OPTION",
    "REDIRECT_STEPPING_STONE",
    "REDIRECT_DOMAIN_EXPERT",
    "REDIRECT_PARTIAL_HELP",
    "REDIRECT_TEMPLATES",
    # Clarification Templates
    "CLARIFICATION_DID_YOU_MEAN",
    "CLARIFICATION_AMBIGUITY_RESOLUTION",
    "CLARIFICATION_MISSING_DETAIL",
    "CLARIFICATION_CONFIRM_UNDERSTANDING",
    "CLARIFICATION_CONTEXT_NEEDED",
    "CLARIFICATION_TEMPLATES",
    # Escalation Templates
    "ESCALATION_PROACTIVE",
    "ESCALATION_FAILED_ATTEMPT",
    "ESCALATION_COMPLEXITY",
    "ESCALATION_SENSITIVITY",
    "ESCALATION_USER_CHOICE",
    "ESCALATION_TEMPLATES",
    # In-Scope Templates
    "IN_SCOPE_READY_TO_HELP",
    "IN_SCOPE_ENTHUSIASTIC",
    "IN_SCOPE_PROFESSIONAL",
    "IN_SCOPE_TEMPLATES",
    # All Templates
    "ALL_TEMPLATES",
    # Factory Functions
    "get_default_library",
    "reset_default_library",
]
