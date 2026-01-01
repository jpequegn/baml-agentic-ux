"""
Agent Negotiation Module

Agent-to-Agent interface negotiation components for Phase 3.
"""

from .agent_card import (
    # Protocol types
    ProtocolType,
    SupportedProtocol,
    # Endpoint types
    EndpointType,
    AuthMethod,
    AuthConfig,
    CardEndpoint,
    RetryPolicy,
    # Compliance types
    ComplianceStandard,
    ComplianceTag,
    DataHandlingPolicy,
    # Agent Card
    AgentCard,
    AgentCardSummary,
    # Discovery types
    WellKnownAgentDescriptions,
    AgentCardRequest,
    AgentCardResponse,
    AgentCardError,
    # Protocol negotiation
    ProtocolNegotiationRequest,
    ProtocolNegotiationResult,
    # Validation
    CardValidationResult,
    CardValidationError,
    CardValidationWarning,
    # Utilities
    AgentCardBuilder,
    AgentCardValidator,
    AgentCardSerializer,
)

from .capability_registry import (
    # Constraint types
    ConstraintType,
    ConstraintOperator,
    DiscoveryConstraint,
    # Discovery types
    DiscoverySource,
    DiscoveryRequest,
    AgentMatch,
    DiscoveryResponse,
    # Registry operations
    RegistrationRequest,
    RegistrationError,
    RegistrationResponse,
    DeregistrationRequest,
    DeregistrationResponse,
    # Registry status
    RegistryStatus,
    CapabilityStats,
    CapabilityIndex,
    # Registry class
    CapabilityRegistry,
)

from .capability_matcher import (
    # Transformation types
    TransformationDirection,
    TransformationType,
    TransformationComplexity,
    SchemaTransformation,
    PropertyMatch,
    SchemaCompatibility,
    # Constraint satisfaction
    ConstraintSatisfaction,
    # Adaptation suggestions
    SuggestionType,
    SuggestionPriority,
    EffortLevel,
    AdaptationSuggestion,
    # Capability matching
    CapabilityDetailedMatch,
    CapabilityMatchResult,
    MatchOptions,
    BestMatch,
    CapabilityMatchResponse,
    # Matcher class
    CapabilityMatcher,
)

from .negotiation_state import (
    # Enums
    NegotiationStatus,
    NegotiationAction,
    NegotiationOutcome,
    UrgencyLevel,
    RiskLevel,
    StrategyApproach,
    ConstraintType,
    ConstraintOperator,
    TERMINAL_STATES,
    # Proposal types
    NegotiationParameter,
    SLARequirement,
    NegotiationTerms,
    ProposalConstraint,
    CapabilityNegotiationItem,
    NegotiationProposal,
    # Turn types
    TurnMetadata,
    NegotiationTurn,
    # Result types
    NegotiationResult,
    NegotiationContext,
    # Identity (local copy)
    AgentIdentity,
    # Transition types
    StateTransitionError,
    StateTransitionResult,
    # Risk types
    RiskFactor,
    RiskAssessment,
    # Strategy types
    NegotiationStrategy,
    # State change callback type
    StateChangeCallback,
    # Session class
    NegotiationSession,
    # State machine class
    NegotiationStateMachine,
)

__all__ = [
    # Protocol types
    "ProtocolType",
    "SupportedProtocol",
    # Endpoint types
    "EndpointType",
    "AuthMethod",
    "AuthConfig",
    "CardEndpoint",
    "RetryPolicy",
    # Compliance types
    "ComplianceStandard",
    "ComplianceTag",
    "DataHandlingPolicy",
    # Agent Card
    "AgentCard",
    "AgentCardSummary",
    # Discovery types (agent_card)
    "WellKnownAgentDescriptions",
    "AgentCardRequest",
    "AgentCardResponse",
    "AgentCardError",
    # Protocol negotiation
    "ProtocolNegotiationRequest",
    "ProtocolNegotiationResult",
    # Validation
    "CardValidationResult",
    "CardValidationError",
    "CardValidationWarning",
    # Utilities
    "AgentCardBuilder",
    "AgentCardValidator",
    "AgentCardSerializer",
    # Constraint types
    "ConstraintType",
    "ConstraintOperator",
    "DiscoveryConstraint",
    # Discovery types (capability_registry)
    "DiscoverySource",
    "DiscoveryRequest",
    "AgentMatch",
    "DiscoveryResponse",
    # Registry operations
    "RegistrationRequest",
    "RegistrationError",
    "RegistrationResponse",
    "DeregistrationRequest",
    "DeregistrationResponse",
    # Registry status
    "RegistryStatus",
    "CapabilityStats",
    "CapabilityIndex",
    # Registry class
    "CapabilityRegistry",
    # Transformation types
    "TransformationDirection",
    "TransformationType",
    "TransformationComplexity",
    "SchemaTransformation",
    "PropertyMatch",
    "SchemaCompatibility",
    # Constraint satisfaction
    "ConstraintSatisfaction",
    # Adaptation suggestions
    "SuggestionType",
    "SuggestionPriority",
    "EffortLevel",
    "AdaptationSuggestion",
    # Capability matching
    "CapabilityDetailedMatch",
    "CapabilityMatchResult",
    "MatchOptions",
    "BestMatch",
    "CapabilityMatchResponse",
    # Matcher class
    "CapabilityMatcher",
    # Negotiation status and action enums
    "NegotiationStatus",
    "NegotiationAction",
    "NegotiationOutcome",
    "UrgencyLevel",
    "RiskLevel",
    "StrategyApproach",
    "ConstraintType",
    "ConstraintOperator",
    "TERMINAL_STATES",
    # Proposal types
    "NegotiationParameter",
    "SLARequirement",
    "NegotiationTerms",
    "ProposalConstraint",
    "CapabilityNegotiationItem",
    "NegotiationProposal",
    # Turn types
    "TurnMetadata",
    "NegotiationTurn",
    # Result types
    "NegotiationResult",
    "NegotiationContext",
    "AgentIdentity",
    # Transition types
    "StateTransitionError",
    "StateTransitionResult",
    # Risk types
    "RiskFactor",
    "RiskAssessment",
    # Strategy types
    "NegotiationStrategy",
    # State change callback type
    "StateChangeCallback",
    # Session class
    "NegotiationSession",
    # State machine class
    "NegotiationStateMachine",
]
