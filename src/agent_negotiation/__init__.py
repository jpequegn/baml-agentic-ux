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
]
