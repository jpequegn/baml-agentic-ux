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
    # Discovery types
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
]
