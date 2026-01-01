"""
Agent Card Schema (A2A-compatible)

Complete agent advertisement format compatible with Google A2A protocol.

Issue #54 - Phase 3: Agent-to-Agent Interface Negotiation
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import hashlib
import json
import uuid

from src.lui_simulator.agent_types import (
    AgentIdentity,
    AgentMetadata,
    AgentCapability,
    TrustRequirements,
)


# ============================================
# Protocol Types
# ============================================


class ProtocolType(Enum):
    """Supported communication protocols for agent interaction."""

    A2A = "a2a"  # Google Agent-to-Agent protocol
    MCP = "mcp"  # Model Context Protocol (Anthropic)
    OPENAPI = "openapi"  # OpenAPI/REST specification
    JSON_RPC = "json_rpc"  # JSON-RPC 2.0 protocol
    GRPC = "grpc"  # gRPC protocol
    GRAPHQL = "graphql"  # GraphQL API
    WEBSOCKET = "websocket"  # WebSocket real-time protocol
    CUSTOM = "custom"  # Custom protocol implementation


@dataclass
class SupportedProtocol:
    """Protocol version declaration."""

    protocol: ProtocolType
    version: str
    uri: str | None = None
    extensions: list[str] = field(default_factory=list)
    deprecated: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "protocol": self.protocol.value,
            "version": self.version,
            "deprecated": self.deprecated,
        }
        if self.uri:
            result["uri"] = self.uri
        if self.extensions:
            result["extensions"] = self.extensions
        return result


# ============================================
# Endpoint Types
# ============================================


class EndpointType(Enum):
    """Types of endpoints an agent can expose."""

    PRIMARY = "primary"
    FALLBACK = "fallback"
    HEALTH_CHECK = "health_check"
    DISCOVERY = "discovery"
    METRICS = "metrics"
    ADMIN = "admin"


class AuthMethod(Enum):
    """Authentication methods for endpoints."""

    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC = "basic"
    MTLS = "mtls"
    SPIFFE = "spiffe"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    CUSTOM = "custom"


@dataclass
class AuthConfig:
    """Authentication configuration for an endpoint."""

    method: AuthMethod
    header_name: str | None = None
    token_endpoint: str | None = None
    scopes: list[str] = field(default_factory=list)
    audience: str | None = None
    issuer: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {"method": self.method.value}
        if self.header_name:
            result["header_name"] = self.header_name
        if self.token_endpoint:
            result["token_endpoint"] = self.token_endpoint
        if self.scopes:
            result["scopes"] = self.scopes
        if self.audience:
            result["audience"] = self.audience
        if self.issuer:
            result["issuer"] = self.issuer
        return result


@dataclass
class RetryPolicy:
    """Retry policy for endpoint calls."""

    max_retries: int = 3
    initial_backoff_ms: int = 100
    max_backoff_ms: int = 10000
    backoff_multiplier: float = 2.0
    retryable_status_codes: list[int] = field(
        default_factory=lambda: [429, 500, 502, 503, 504]
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "max_retries": self.max_retries,
            "initial_backoff_ms": self.initial_backoff_ms,
            "max_backoff_ms": self.max_backoff_ms,
            "backoff_multiplier": self.backoff_multiplier,
            "retryable_status_codes": self.retryable_status_codes,
        }


@dataclass
class CardEndpoint:
    """Complete endpoint definition for AgentCard."""

    endpoint_type: EndpointType
    url: str
    protocol: ProtocolType
    auth_config: AuthConfig | None = None
    timeout_ms: int | None = None
    retry_policy: RetryPolicy | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "endpoint_type": self.endpoint_type.value,
            "url": self.url,
            "protocol": self.protocol.value,
        }
        if self.auth_config:
            result["auth_config"] = self.auth_config.to_dict()
        if self.timeout_ms:
            result["timeout_ms"] = self.timeout_ms
        if self.retry_policy:
            result["retry_policy"] = self.retry_policy.to_dict()
        return result


# ============================================
# Compliance Types
# ============================================


class ComplianceStandard(Enum):
    """Standard compliance certifications."""

    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    SOC2_TYPE1 = "soc2_type1"
    SOC2_TYPE2 = "soc2_type2"
    ISO27001 = "iso27001"
    ISO27017 = "iso27017"
    ISO27018 = "iso27018"
    PCI_DSS = "pci_dss"
    FEDRAMP = "fedramp"
    FEDRAMP_HIGH = "fedramp_high"
    FEDRAMP_MODERATE = "fedramp_moderate"
    NIST_800_53 = "nist_800_53"
    CSA_STAR = "csa_star"


@dataclass
class ComplianceTag:
    """Compliance tag with verification details."""

    standard: ComplianceStandard
    certified: bool = True
    certificate_url: str | None = None
    expiry_date: str | None = None
    auditor: str | None = None
    scope: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "standard": self.standard.value,
            "certified": self.certified,
        }
        if self.certificate_url:
            result["certificate_url"] = self.certificate_url
        if self.expiry_date:
            result["expiry_date"] = self.expiry_date
        if self.auditor:
            result["auditor"] = self.auditor
        if self.scope:
            result["scope"] = self.scope
        return result

    def is_expired(self) -> bool:
        """Check if the certification has expired."""
        if not self.expiry_date:
            return False
        try:
            expiry = datetime.fromisoformat(self.expiry_date.replace("Z", "+00:00"))
            return expiry < datetime.now(timezone.utc)
        except ValueError:
            return False


@dataclass
class DataHandlingPolicy:
    """Data handling policies for compliance."""

    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    audit_logging: bool = True
    data_residency: list[str] = field(default_factory=list)
    data_retention_days: int | None = None
    pii_handling: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "encryption_at_rest": self.encryption_at_rest,
            "encryption_in_transit": self.encryption_in_transit,
            "audit_logging": self.audit_logging,
        }
        if self.data_residency:
            result["data_residency"] = self.data_residency
        if self.data_retention_days is not None:
            result["data_retention_days"] = self.data_retention_days
        if self.pii_handling:
            result["pii_handling"] = self.pii_handling
        return result


# ============================================
# Agent Card
# ============================================


@dataclass
class AgentCard:
    """
    Complete agent advertisement card (A2A-compatible).

    This is the primary format for agent discovery and capability advertisement.
    """

    identity: AgentIdentity
    capabilities: list[AgentCapability]
    supported_protocols: list[SupportedProtocol]
    endpoints: list[CardEndpoint]
    card_version: str = "1.0.0"
    compliance_tags: list[ComplianceTag] = field(default_factory=list)
    data_handling: DataHandlingPolicy | None = None
    trust_requirements: TrustRequirements | None = None
    metadata: AgentMetadata | None = None
    signature: str | None = None

    def get_primary_endpoint(self) -> CardEndpoint | None:
        """Get the primary endpoint if available."""
        for endpoint in self.endpoints:
            if endpoint.endpoint_type == EndpointType.PRIMARY:
                return endpoint
        return self.endpoints[0] if self.endpoints else None

    def get_discovery_endpoint(self) -> CardEndpoint | None:
        """Get the discovery endpoint if available."""
        for endpoint in self.endpoints:
            if endpoint.endpoint_type == EndpointType.DISCOVERY:
                return endpoint
        return None

    def get_health_check_endpoint(self) -> CardEndpoint | None:
        """Get the health check endpoint if available."""
        for endpoint in self.endpoints:
            if endpoint.endpoint_type == EndpointType.HEALTH_CHECK:
                return endpoint
        return None

    def supports_protocol(self, protocol: ProtocolType) -> bool:
        """Check if the agent supports a specific protocol."""
        return any(p.protocol == protocol for p in self.supported_protocols)

    def get_protocol(self, protocol_type: ProtocolType) -> SupportedProtocol | None:
        """Get protocol details for a specific protocol type."""
        for p in self.supported_protocols:
            if p.protocol == protocol_type:
                return p
        return None

    def is_compliant_with(self, standard: ComplianceStandard) -> bool:
        """Check if the agent is compliant with a specific standard."""
        return any(
            t.standard == standard and t.certified and not t.is_expired()
            for t in self.compliance_tags
        )

    def get_capability(self, capability_id: str) -> AgentCapability | None:
        """Get a specific capability by ID."""
        for cap in self.capabilities:
            if cap.capability_id == capability_id:
                return cap
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to A2A-compatible JSON dictionary."""
        result: dict[str, Any] = {
            "card_version": self.card_version,
            "identity": {
                "agent_id": self.identity.agent_id,
                "name": self.identity.name,
                "version": self.identity.version,
                "description": self.identity.description,
            },
            "capabilities": [
                {
                    "capability_id": cap.capability_id,
                    "capability_type": cap.capability_type.value,
                    "name": cap.name,
                    "description": cap.description,
                }
                for cap in self.capabilities
            ],
            "supported_protocols": [p.to_dict() for p in self.supported_protocols],
            "endpoints": [e.to_dict() for e in self.endpoints],
        }

        if self.identity.provider:
            result["identity"]["provider"] = self.identity.provider
        if self.identity.trust_domain:
            result["identity"]["trust_domain"] = self.identity.trust_domain

        if self.compliance_tags:
            result["compliance_tags"] = [t.to_dict() for t in self.compliance_tags]
        if self.data_handling:
            result["data_handling"] = self.data_handling.to_dict()
        if self.trust_requirements:
            result["trust_requirements"] = {
                "minimum_trust_level": self.trust_requirements.minimum_trust_level.value,
                "require_mutual_tls": self.trust_requirements.require_mutual_tls,
                "require_attestation": self.trust_requirements.require_attestation,
            }
        if self.signature:
            result["signature"] = self.signature

        return result

    def to_json(self, indent: int | None = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of card contents (excluding signature)."""
        card_dict = self.to_dict()
        card_dict.pop("signature", None)
        content = json.dumps(card_dict, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class AgentCardSummary:
    """Lightweight agent card for discovery responses."""

    agent_id: str
    name: str
    description: str
    capability_count: int
    protocols: list[ProtocolType]
    compliance_standards: list[ComplianceStandard]
    discovery_url: str

    @classmethod
    def from_card(cls, card: AgentCard, discovery_url: str) -> "AgentCardSummary":
        """Create summary from full agent card."""
        return cls(
            agent_id=card.identity.agent_id,
            name=card.identity.name,
            description=card.identity.description,
            capability_count=len(card.capabilities),
            protocols=[p.protocol for p in card.supported_protocols],
            compliance_standards=[t.standard for t in card.compliance_tags if t.certified],
            discovery_url=discovery_url,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capability_count": self.capability_count,
            "protocols": [p.value for p in self.protocols],
            "compliance_standards": [s.value for s in self.compliance_standards],
            "discovery_url": self.discovery_url,
        }


# ============================================
# Well-Known Discovery
# ============================================


@dataclass
class WellKnownAgentDescriptions:
    """Response format for .well-known/agent-descriptions endpoint."""

    agents: list[AgentCardSummary]
    total_count: int
    schema_version: str = "1.0.0"
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    next_cursor: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "agents": [a.to_dict() for a in self.agents],
            "total_count": self.total_count,
        }
        if self.next_cursor:
            result["next_cursor"] = self.next_cursor
        return result

    def to_json(self, indent: int | None = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class AgentCardRequest:
    """Request to retrieve agent card."""

    agent_id: str
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    include_capabilities: bool = True
    include_signature: bool = False
    requested_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class AgentCardError:
    """Error response for agent card retrieval."""

    error_code: str
    error_message: str
    suggested_action: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "error_code": self.error_code,
            "error_message": self.error_message,
        }
        if self.suggested_action:
            result["suggested_action"] = self.suggested_action
        return result


@dataclass
class AgentCardResponse:
    """Response containing agent card."""

    request_id: str
    found: bool
    agent_card: AgentCard | None = None
    cached: bool = False
    cache_expires_at: str | None = None
    error: AgentCardError | None = None

    @classmethod
    def success(
        cls,
        request_id: str,
        card: AgentCard,
        cached: bool = False,
        cache_expires_at: str | None = None,
    ) -> "AgentCardResponse":
        """Create a successful response."""
        return cls(
            request_id=request_id,
            found=True,
            agent_card=card,
            cached=cached,
            cache_expires_at=cache_expires_at,
        )

    @classmethod
    def not_found(cls, request_id: str, agent_id: str) -> "AgentCardResponse":
        """Create a not-found response."""
        return cls(
            request_id=request_id,
            found=False,
            error=AgentCardError(
                error_code="AGENT_NOT_FOUND",
                error_message=f"Agent with ID '{agent_id}' not found",
                suggested_action="Verify the agent ID and try again",
            ),
        )


# ============================================
# Protocol Negotiation
# ============================================


@dataclass
class ProtocolNegotiationRequest:
    """Request to negotiate communication protocol."""

    client_protocols: list[SupportedProtocol]
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    preferred_protocol: ProtocolType | None = None
    capabilities_required: list[str] = field(default_factory=list)


@dataclass
class ProtocolNegotiationResult:
    """Result of protocol negotiation."""

    request_id: str
    success: bool
    selected_protocol: SupportedProtocol | None = None
    selected_endpoint: CardEndpoint | None = None
    fallback_protocols: list[SupportedProtocol] = field(default_factory=list)
    failure_reason: str | None = None

    @classmethod
    def successful(
        cls,
        request_id: str,
        protocol: SupportedProtocol,
        endpoint: CardEndpoint,
        fallbacks: list[SupportedProtocol] | None = None,
    ) -> "ProtocolNegotiationResult":
        """Create a successful negotiation result."""
        return cls(
            request_id=request_id,
            success=True,
            selected_protocol=protocol,
            selected_endpoint=endpoint,
            fallback_protocols=fallbacks or [],
        )

    @classmethod
    def failed(cls, request_id: str, reason: str) -> "ProtocolNegotiationResult":
        """Create a failed negotiation result."""
        return cls(
            request_id=request_id,
            success=False,
            failure_reason=reason,
        )


# ============================================
# Card Validation
# ============================================


@dataclass
class CardValidationError:
    """Validation error for agent card."""

    field: str
    error_code: str
    message: str


@dataclass
class CardValidationWarning:
    """Validation warning for agent card."""

    field: str
    warning_code: str
    message: str
    suggestion: str | None = None


@dataclass
class CardValidationResult:
    """Result of validating an agent card."""

    valid: bool
    errors: list[CardValidationError] = field(default_factory=list)
    warnings: list[CardValidationWarning] = field(default_factory=list)
    signature_verified: bool | None = None
    a2a_compliant: bool = False
    mcp_compliant: bool = False


# ============================================
# Utility Classes
# ============================================


class AgentCardBuilder:
    """Builder for creating AgentCard instances."""

    def __init__(self, identity: AgentIdentity) -> None:
        """Initialize builder with agent identity."""
        self._identity = identity
        self._capabilities: list[AgentCapability] = []
        self._protocols: list[SupportedProtocol] = []
        self._endpoints: list[CardEndpoint] = []
        self._compliance_tags: list[ComplianceTag] = []
        self._data_handling: DataHandlingPolicy | None = None
        self._trust_requirements: TrustRequirements | None = None
        self._metadata: AgentMetadata | None = None

    def add_capability(self, capability: AgentCapability) -> "AgentCardBuilder":
        """Add a capability to the card."""
        self._capabilities.append(capability)
        return self

    def add_protocol(
        self,
        protocol: ProtocolType,
        version: str,
        uri: str | None = None,
        extensions: list[str] | None = None,
    ) -> "AgentCardBuilder":
        """Add a supported protocol."""
        self._protocols.append(
            SupportedProtocol(
                protocol=protocol,
                version=version,
                uri=uri,
                extensions=extensions or [],
            )
        )
        return self

    def add_endpoint(
        self,
        endpoint_type: EndpointType,
        url: str,
        protocol: ProtocolType,
        auth_config: AuthConfig | None = None,
        timeout_ms: int | None = None,
    ) -> "AgentCardBuilder":
        """Add an endpoint."""
        self._endpoints.append(
            CardEndpoint(
                endpoint_type=endpoint_type,
                url=url,
                protocol=protocol,
                auth_config=auth_config,
                timeout_ms=timeout_ms,
            )
        )
        return self

    def add_compliance(
        self,
        standard: ComplianceStandard,
        certified: bool = True,
        certificate_url: str | None = None,
        expiry_date: str | None = None,
    ) -> "AgentCardBuilder":
        """Add a compliance tag."""
        self._compliance_tags.append(
            ComplianceTag(
                standard=standard,
                certified=certified,
                certificate_url=certificate_url,
                expiry_date=expiry_date,
            )
        )
        return self

    def with_data_handling(
        self,
        encryption_at_rest: bool = True,
        encryption_in_transit: bool = True,
        audit_logging: bool = True,
        data_residency: list[str] | None = None,
    ) -> "AgentCardBuilder":
        """Set data handling policy."""
        self._data_handling = DataHandlingPolicy(
            encryption_at_rest=encryption_at_rest,
            encryption_in_transit=encryption_in_transit,
            audit_logging=audit_logging,
            data_residency=data_residency or [],
        )
        return self

    def with_trust_requirements(
        self, requirements: TrustRequirements
    ) -> "AgentCardBuilder":
        """Set trust requirements."""
        self._trust_requirements = requirements
        return self

    def with_metadata(self, metadata: AgentMetadata) -> "AgentCardBuilder":
        """Set metadata."""
        self._metadata = metadata
        return self

    def build(self) -> AgentCard:
        """Build the AgentCard."""
        if not self._protocols:
            raise ValueError("At least one protocol must be specified")
        if not self._endpoints:
            raise ValueError("At least one endpoint must be specified")

        return AgentCard(
            identity=self._identity,
            capabilities=self._capabilities,
            supported_protocols=self._protocols,
            endpoints=self._endpoints,
            compliance_tags=self._compliance_tags,
            data_handling=self._data_handling,
            trust_requirements=self._trust_requirements,
            metadata=self._metadata,
        )


class AgentCardValidator:
    """Validator for AgentCard instances."""

    def validate(self, card: AgentCard) -> CardValidationResult:
        """Validate an agent card."""
        errors: list[CardValidationError] = []
        warnings: list[CardValidationWarning] = []

        # Validate identity
        if not card.identity.agent_id:
            errors.append(
                CardValidationError(
                    field="identity.agent_id",
                    error_code="REQUIRED_FIELD",
                    message="Agent ID is required",
                )
            )
        if not card.identity.name:
            errors.append(
                CardValidationError(
                    field="identity.name",
                    error_code="REQUIRED_FIELD",
                    message="Agent name is required",
                )
            )
        if not card.identity.version:
            errors.append(
                CardValidationError(
                    field="identity.version",
                    error_code="REQUIRED_FIELD",
                    message="Agent version is required",
                )
            )

        # Validate protocols
        if not card.supported_protocols:
            errors.append(
                CardValidationError(
                    field="supported_protocols",
                    error_code="EMPTY_LIST",
                    message="At least one protocol must be supported",
                )
            )

        # Validate endpoints
        if not card.endpoints:
            errors.append(
                CardValidationError(
                    field="endpoints",
                    error_code="EMPTY_LIST",
                    message="At least one endpoint must be defined",
                )
            )

        primary_endpoints = [
            e for e in card.endpoints if e.endpoint_type == EndpointType.PRIMARY
        ]
        if not primary_endpoints:
            warnings.append(
                CardValidationWarning(
                    field="endpoints",
                    warning_code="NO_PRIMARY_ENDPOINT",
                    message="No primary endpoint defined",
                    suggestion="Consider marking one endpoint as PRIMARY",
                )
            )

        # Check for expired compliance tags
        for i, tag in enumerate(card.compliance_tags):
            if tag.is_expired():
                warnings.append(
                    CardValidationWarning(
                        field=f"compliance_tags[{i}]",
                        warning_code="EXPIRED_CERTIFICATION",
                        message=f"{tag.standard.value} certification has expired",
                        suggestion="Renew certification or remove expired tag",
                    )
                )

        # Check A2A compliance
        a2a_compliant = (
            len(errors) == 0
            and card.supports_protocol(ProtocolType.A2A)
            and any(e.endpoint_type == EndpointType.PRIMARY for e in card.endpoints)
        )

        # Check MCP compliance
        mcp_compliant = len(errors) == 0 and card.supports_protocol(ProtocolType.MCP)

        return CardValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            a2a_compliant=a2a_compliant,
            mcp_compliant=mcp_compliant,
        )


class AgentCardSerializer:
    """Serializer for AgentCard to/from JSON."""

    @staticmethod
    def to_json(card: AgentCard, indent: int | None = 2) -> str:
        """Serialize AgentCard to JSON string."""
        return card.to_json(indent=indent)

    @staticmethod
    def to_dict(card: AgentCard) -> dict[str, Any]:
        """Serialize AgentCard to dictionary."""
        return card.to_dict()

    @staticmethod
    def to_a2a_format(card: AgentCard) -> dict[str, Any]:
        """
        Serialize to A2A-compatible format.

        This matches the Google A2A protocol specification.
        """
        base = card.to_dict()
        # A2A specific formatting
        a2a_format = {
            "agentCard": {
                "version": card.card_version,
                "agent": base["identity"],
                "capabilities": base["capabilities"],
                "protocols": base["supported_protocols"],
                "endpoints": base["endpoints"],
            }
        }
        if "compliance_tags" in base:
            a2a_format["agentCard"]["compliance"] = base["compliance_tags"]
        if "data_handling" in base:
            a2a_format["agentCard"]["dataHandling"] = base["data_handling"]
        if "trust_requirements" in base:
            a2a_format["agentCard"]["trustRequirements"] = base["trust_requirements"]

        return a2a_format

    @staticmethod
    def to_well_known_format(
        cards: list[AgentCard], base_url: str
    ) -> WellKnownAgentDescriptions:
        """Create well-known agent descriptions response."""
        summaries = [
            AgentCardSummary.from_card(
                card, f"{base_url}/agents/{card.identity.agent_id}"
            )
            for card in cards
        ]
        return WellKnownAgentDescriptions(
            agents=summaries,
            total_count=len(summaries),
        )


def negotiate_protocol(
    card: AgentCard, request: ProtocolNegotiationRequest
) -> ProtocolNegotiationResult:
    """
    Negotiate communication protocol between client and agent.

    Returns the best matching protocol and endpoint.
    """
    # Get protocols supported by both client and agent
    agent_protocols = {p.protocol: p for p in card.supported_protocols}
    client_protocols = {p.protocol: p for p in request.client_protocols}

    common_protocols = set(agent_protocols.keys()) & set(client_protocols.keys())

    if not common_protocols:
        return ProtocolNegotiationResult.failed(
            request_id=request.request_id,
            reason="No common protocols found between client and agent",
        )

    # Check if preferred protocol is available
    selected: SupportedProtocol | None = None
    if request.preferred_protocol and request.preferred_protocol in common_protocols:
        selected = agent_protocols[request.preferred_protocol]
    else:
        # Priority order: A2A > MCP > GRPC > OPENAPI > others
        priority = [
            ProtocolType.A2A,
            ProtocolType.MCP,
            ProtocolType.GRPC,
            ProtocolType.OPENAPI,
        ]
        for proto in priority:
            if proto in common_protocols:
                selected = agent_protocols[proto]
                break
        if not selected:
            # Just pick one from common
            selected = agent_protocols[next(iter(common_protocols))]

    # Find matching endpoint
    selected_endpoint: CardEndpoint | None = None
    for endpoint in card.endpoints:
        if endpoint.protocol == selected.protocol:
            if endpoint.endpoint_type == EndpointType.PRIMARY:
                selected_endpoint = endpoint
                break
            elif selected_endpoint is None:
                selected_endpoint = endpoint

    if not selected_endpoint:
        return ProtocolNegotiationResult.failed(
            request_id=request.request_id,
            reason=f"No endpoint found for protocol {selected.protocol.value}",
        )

    # Collect fallbacks
    fallbacks = [
        agent_protocols[p]
        for p in common_protocols
        if p != selected.protocol and not agent_protocols[p].deprecated
    ]

    return ProtocolNegotiationResult.successful(
        request_id=request.request_id,
        protocol=selected,
        endpoint=selected_endpoint,
        fallbacks=fallbacks,
    )
