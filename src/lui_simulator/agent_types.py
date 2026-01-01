"""
Agent Identity and Capability Types

Python implementations for agent identity and capability types
compatible with A2A and MCP standards.

Issue #53 - Phase 3: Agent-to-Agent Interface Negotiation
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import re
import uuid


# ============================================
# Trust Levels
# ============================================


class TrustLevel(Enum):
    """Trust levels for agent-to-agent communication."""

    NONE = "none"  # Public access, no authentication required
    BASIC = "basic"  # API key or basic authentication
    VERIFIED = "verified"  # Verified identity through certificate or token
    TRUSTED = "trusted"  # Established relationship with mutual trust
    PRIVILEGED = "privileged"  # High-privilege operations, requires strong auth

    def __lt__(self, other: "TrustLevel") -> bool:
        """Compare trust levels for ordering."""
        order = [
            TrustLevel.NONE,
            TrustLevel.BASIC,
            TrustLevel.VERIFIED,
            TrustLevel.TRUSTED,
            TrustLevel.PRIVILEGED,
        ]
        return order.index(self) < order.index(other)

    def __le__(self, other: "TrustLevel") -> bool:
        return self == other or self < other

    def __gt__(self, other: "TrustLevel") -> bool:
        return not self <= other

    def __ge__(self, other: "TrustLevel") -> bool:
        return not self < other


# ============================================
# Health Status
# ============================================


class HealthStatus(Enum):
    """Health status of an agent."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


# ============================================
# Endpoint Protocol
# ============================================


class EndpointProtocol(Enum):
    """Supported communication protocols."""

    HTTP = "http"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    MCP = "mcp"
    A2A = "a2a"


# ============================================
# Verification Types
# ============================================


class VerificationType(Enum):
    """Types of identity verification."""

    CERTIFICATE = "certificate"
    SPIFFE = "spiffe"
    CHALLENGE_RESPONSE = "challenge_response"
    TOKEN = "token"
    ATTESTATION = "attestation"


# ============================================
# Agent Metadata
# ============================================


@dataclass
class AgentMetadata:
    """Additional metadata about an agent."""

    created_at: str
    updated_at: str
    homepage: str | None = None
    repository: str | None = None
    license: str | None = None
    authors: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        homepage: str | None = None,
        repository: str | None = None,
        license_id: str | None = None,
        authors: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> "AgentMetadata":
        """Create new metadata with current timestamps."""
        now = datetime.now(timezone.utc).isoformat()
        return cls(
            created_at=now,
            updated_at=now,
            homepage=homepage,
            repository=repository,
            license=license_id,
            authors=authors or [],
            tags=tags or [],
        )


# ============================================
# Trust Requirements
# ============================================


@dataclass
class TrustRequirements:
    """Requirements for establishing trust."""

    minimum_trust_level: TrustLevel = TrustLevel.NONE
    require_mutual_tls: bool = False
    allowed_trust_domains: list[str] = field(default_factory=list)
    require_attestation: bool = False
    allowed_issuers: list[str] = field(default_factory=list)

    def is_satisfied_by(self, trust_level: TrustLevel) -> bool:
        """Check if a trust level satisfies these requirements."""
        return trust_level >= self.minimum_trust_level


# ============================================
# Agent Identity
# ============================================


# URN pattern for agent IDs
AGENT_URN_PATTERN = re.compile(
    r"^urn:agent:(?P<provider>[a-z0-9-]+):(?P<name>[a-z0-9-]+):(?P<version>\d+\.\d+\.\d+)$"
)

# Semantic version pattern
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?(?:\+[a-zA-Z0-9.]+)?$")


@dataclass
class AgentIdentity:
    """Unique identifier for an agent in URN format."""

    agent_id: str
    name: str
    version: str
    description: str
    provider: str | None = None
    trust_domain: str | None = None
    metadata: AgentMetadata | None = None

    def __post_init__(self) -> None:
        """Validate agent identity fields."""
        if not self.name:
            raise ValueError("Agent name cannot be empty")
        if not self.version:
            raise ValueError("Agent version cannot be empty")
        if not SEMVER_PATTERN.match(self.version):
            raise ValueError(f"Invalid semantic version: {self.version}")

    @classmethod
    def create(
        cls,
        name: str,
        version: str,
        description: str,
        provider: str | None = None,
        trust_domain: str | None = None,
        metadata: AgentMetadata | None = None,
    ) -> "AgentIdentity":
        """Create a new agent identity with auto-generated URN ID."""
        # Generate URN format ID
        provider_part = provider or "unknown"
        name_normalized = name.lower().replace(" ", "-")
        agent_id = f"urn:agent:{provider_part}:{name_normalized}:{version}"

        return cls(
            agent_id=agent_id,
            name=name,
            version=version,
            description=description,
            provider=provider,
            trust_domain=trust_domain,
            metadata=metadata,
        )

    @classmethod
    def from_urn(cls, urn: str, description: str = "") -> "AgentIdentity":
        """Create identity from an existing URN."""
        match = AGENT_URN_PATTERN.match(urn)
        if not match:
            raise ValueError(f"Invalid agent URN format: {urn}")

        return cls(
            agent_id=urn,
            name=match.group("name"),
            version=match.group("version"),
            description=description,
            provider=match.group("provider"),
        )

    def is_valid_urn(self) -> bool:
        """Check if the agent_id follows URN format."""
        return bool(AGENT_URN_PATTERN.match(self.agent_id))

    def get_spiffe_id(self) -> str | None:
        """Get SPIFFE ID if trust domain is configured."""
        if not self.trust_domain:
            return None
        name_normalized = self.name.lower().replace(" ", "-")
        return f"spiffe://{self.trust_domain}/agent/{name_normalized}"


# ============================================
# Rate Limit
# ============================================


@dataclass
class RateLimit:
    """Rate limiting configuration for an endpoint."""

    requests_per_second: float
    burst_size: int
    retry_after_seconds: int = 60


# ============================================
# Agent Endpoint
# ============================================


@dataclass
class AgentEndpoint:
    """An endpoint where an agent can be reached."""

    endpoint_id: str
    protocol: EndpointProtocol
    url: str
    priority: int = 0
    health_check_path: str | None = None
    rate_limit: RateLimit | None = None

    @classmethod
    def create(
        cls,
        protocol: EndpointProtocol,
        url: str,
        priority: int = 0,
        health_check_path: str | None = None,
        rate_limit: RateLimit | None = None,
    ) -> "AgentEndpoint":
        """Create a new endpoint with auto-generated ID."""
        return cls(
            endpoint_id=str(uuid.uuid4()),
            protocol=protocol,
            url=url,
            priority=priority,
            health_check_path=health_check_path,
            rate_limit=rate_limit,
        )


# ============================================
# Agent Registration
# ============================================


@dataclass
class AgentRegistration:
    """Request to register an agent in a registry."""

    identity: AgentIdentity
    endpoints: list[AgentEndpoint]
    capabilities: list[str]
    trust_requirements: TrustRequirements | None = None
    registration_token: str | None = None


# ============================================
# Agent Discovery
# ============================================


@dataclass
class AgentDiscoveryQuery:
    """Query for discovering agents."""

    query_id: str
    capability_filter: list[str] = field(default_factory=list)
    provider_filter: list[str] = field(default_factory=list)
    tag_filter: list[str] = field(default_factory=list)
    trust_level_filter: TrustLevel | None = None
    limit: int = 10
    offset: int = 0

    @classmethod
    def create(
        cls,
        capability_filter: list[str] | None = None,
        provider_filter: list[str] | None = None,
        tag_filter: list[str] | None = None,
        trust_level_filter: TrustLevel | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> "AgentDiscoveryQuery":
        """Create a new discovery query with auto-generated ID."""
        return cls(
            query_id=str(uuid.uuid4()),
            capability_filter=capability_filter or [],
            provider_filter=provider_filter or [],
            tag_filter=tag_filter or [],
            trust_level_filter=trust_level_filter,
            limit=limit,
            offset=offset,
        )


@dataclass
class DiscoveredAgent:
    """A discovered agent with summary information."""

    identity: AgentIdentity
    capability_count: int
    endpoint_count: int
    trust_level: TrustLevel
    last_seen: str
    health_status: HealthStatus


@dataclass
class AgentDiscoveryResult:
    """Result of an agent discovery query."""

    query_id: str
    agents: list[DiscoveredAgent]
    total_count: int
    has_more: bool


# ============================================
# Verification
# ============================================


@dataclass
class VerificationRequest:
    """Request to verify an agent's identity."""

    request_id: str
    agent_id: str
    verification_type: VerificationType
    challenge: str | None = None
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @classmethod
    def create(
        cls,
        agent_id: str,
        verification_type: VerificationType,
        challenge: str | None = None,
    ) -> "VerificationRequest":
        """Create a new verification request."""
        return cls(
            request_id=str(uuid.uuid4()),
            agent_id=agent_id,
            verification_type=verification_type,
            challenge=challenge,
        )


@dataclass
class CertificateInfo:
    """Certificate information for verified agents."""

    issuer: str
    subject: str
    valid_from: str
    valid_until: str
    fingerprint: str
    spiffe_id: str | None = None


@dataclass
class VerificationResult:
    """Result of identity verification."""

    request_id: str
    agent_id: str
    verified: bool
    trust_level: TrustLevel
    verification_time_ms: int
    certificate_info: CertificateInfo | None = None
    failure_reason: str | None = None

    @classmethod
    def success(
        cls,
        request_id: str,
        agent_id: str,
        trust_level: TrustLevel,
        verification_time_ms: int,
        certificate_info: CertificateInfo | None = None,
    ) -> "VerificationResult":
        """Create a successful verification result."""
        return cls(
            request_id=request_id,
            agent_id=agent_id,
            verified=True,
            trust_level=trust_level,
            verification_time_ms=verification_time_ms,
            certificate_info=certificate_info,
        )

    @classmethod
    def failure(
        cls,
        request_id: str,
        agent_id: str,
        failure_reason: str,
        verification_time_ms: int,
    ) -> "VerificationResult":
        """Create a failed verification result."""
        return cls(
            request_id=request_id,
            agent_id=agent_id,
            verified=False,
            trust_level=TrustLevel.NONE,
            verification_time_ms=verification_time_ms,
            failure_reason=failure_reason,
        )


# ============================================
# Capability Types
# ============================================


class CapabilityType(Enum):
    """Types of capabilities an agent can provide."""

    ACTION = "action"
    QUERY = "query"
    TRANSFORM = "transform"
    COMPOSITE = "composite"
    DELEGATION = "delegation"
    STREAMING = "streaming"
    INTERACTIVE = "interactive"


class SchemaType(Enum):
    """Schema type for defining data structures."""

    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"
    ANY = "any"
    UNION = "union"
    ENUM = "enum"
    REFERENCE = "reference"


class SchemaConstraintType(Enum):
    """Types of schema constraints."""

    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    PATTERN = "pattern"
    MIN_ITEMS = "min_items"
    MAX_ITEMS = "max_items"
    UNIQUE_ITEMS = "unique_items"
    ADDITIONAL_PROPERTIES = "additional_properties"


class ConstraintCategory(Enum):
    """Categories of capability constraints."""

    RATE_LIMIT = "rate_limit"
    SIZE_LIMIT = "size_limit"
    TIME_LIMIT = "time_limit"
    RESOURCE_LIMIT = "resource_limit"
    CONCURRENCY_LIMIT = "concurrency_limit"
    DEPENDENCY = "dependency"
    EXCLUSION = "exclusion"
    PREREQUISITE = "prerequisite"


class ConstraintEnforcement(Enum):
    """How constraints are enforced."""

    HARD = "hard"
    SOFT = "soft"
    INFORMATIONAL = "informational"


class ResourceIntensity(Enum):
    """Resource usage intensity levels."""

    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class InvocationPriority(Enum):
    """Priority levels for capability invocation."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class InvocationStatus(Enum):
    """Status of a capability invocation."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ErrorType(Enum):
    """Types of invocation errors."""

    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    RATE_LIMITED = "rate_limited"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    TIMEOUT = "timeout"
    INTERNAL = "internal"
    UNAVAILABLE = "unavailable"
    DEPENDENCY_FAILED = "dependency_failed"


# ============================================
# Schema Definitions
# ============================================


@dataclass
class SchemaConstraint:
    """Constraints on schema values."""

    constraint_type: SchemaConstraintType
    value: str
    error_message: str | None = None


@dataclass
class SchemaProperty:
    """A property within an object schema."""

    name: str
    schema: "SchemaDefinition"
    description: str | None = None
    deprecated: bool = False


@dataclass
class SchemaDefinition:
    """Definition of a data schema."""

    type: SchemaType
    schema_id: str | None = None
    description: str | None = None
    properties: list[SchemaProperty] | None = None
    required: list[str] | None = None
    items: "SchemaDefinition | None" = None
    enum_values: list[str] | None = None
    union_types: list["SchemaDefinition"] | None = None
    reference: str | None = None
    format: str | None = None
    default_value: str | None = None
    examples: list[str] | None = None
    constraints: list[SchemaConstraint] | None = None

    @classmethod
    def string(
        cls,
        description: str | None = None,
        format_hint: str | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        pattern: str | None = None,
    ) -> "SchemaDefinition":
        """Create a string schema."""
        constraints = []
        if min_length is not None:
            constraints.append(
                SchemaConstraint(SchemaConstraintType.MIN_LENGTH, str(min_length))
            )
        if max_length is not None:
            constraints.append(
                SchemaConstraint(SchemaConstraintType.MAX_LENGTH, str(max_length))
            )
        if pattern is not None:
            constraints.append(
                SchemaConstraint(SchemaConstraintType.PATTERN, pattern)
            )
        return cls(
            type=SchemaType.STRING,
            description=description,
            format=format_hint,
            constraints=constraints if constraints else None,
        )

    @classmethod
    def integer(
        cls,
        description: str | None = None,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> "SchemaDefinition":
        """Create an integer schema."""
        constraints = []
        if min_value is not None:
            constraints.append(
                SchemaConstraint(SchemaConstraintType.MIN_VALUE, str(min_value))
            )
        if max_value is not None:
            constraints.append(
                SchemaConstraint(SchemaConstraintType.MAX_VALUE, str(max_value))
            )
        return cls(
            type=SchemaType.INTEGER,
            description=description,
            constraints=constraints if constraints else None,
        )

    @classmethod
    def boolean(cls, description: str | None = None) -> "SchemaDefinition":
        """Create a boolean schema."""
        return cls(type=SchemaType.BOOLEAN, description=description)

    @classmethod
    def array(
        cls,
        items: "SchemaDefinition",
        description: str | None = None,
        min_items: int | None = None,
        max_items: int | None = None,
    ) -> "SchemaDefinition":
        """Create an array schema."""
        constraints = []
        if min_items is not None:
            constraints.append(
                SchemaConstraint(SchemaConstraintType.MIN_ITEMS, str(min_items))
            )
        if max_items is not None:
            constraints.append(
                SchemaConstraint(SchemaConstraintType.MAX_ITEMS, str(max_items))
            )
        return cls(
            type=SchemaType.ARRAY,
            items=items,
            description=description,
            constraints=constraints if constraints else None,
        )

    @classmethod
    def object(
        cls,
        properties: list[SchemaProperty],
        required: list[str] | None = None,
        description: str | None = None,
    ) -> "SchemaDefinition":
        """Create an object schema."""
        return cls(
            type=SchemaType.OBJECT,
            properties=properties,
            required=required,
            description=description,
        )

    @classmethod
    def enum(
        cls, values: list[str], description: str | None = None
    ) -> "SchemaDefinition":
        """Create an enum schema."""
        return cls(type=SchemaType.ENUM, enum_values=values, description=description)


# ============================================
# Capability Definitions
# ============================================


@dataclass
class CapabilityConstraint:
    """Constraints on capability usage."""

    constraint_id: str
    constraint_type: ConstraintCategory
    description: str
    enforcement: ConstraintEnforcement
    parameters: dict[str, str] = field(default_factory=dict)

    @classmethod
    def rate_limit(
        cls,
        requests_per_minute: int,
        enforcement: ConstraintEnforcement = ConstraintEnforcement.HARD,
    ) -> "CapabilityConstraint":
        """Create a rate limit constraint."""
        return cls(
            constraint_id=str(uuid.uuid4()),
            constraint_type=ConstraintCategory.RATE_LIMIT,
            description=f"Maximum {requests_per_minute} requests per minute",
            enforcement=enforcement,
            parameters={"requests_per_minute": str(requests_per_minute)},
        )

    @classmethod
    def time_limit(
        cls,
        max_seconds: int,
        enforcement: ConstraintEnforcement = ConstraintEnforcement.HARD,
    ) -> "CapabilityConstraint":
        """Create a time limit constraint."""
        return cls(
            constraint_id=str(uuid.uuid4()),
            constraint_type=ConstraintCategory.TIME_LIMIT,
            description=f"Maximum execution time: {max_seconds} seconds",
            enforcement=enforcement,
            parameters={"max_seconds": str(max_seconds)},
        )


@dataclass
class CostEstimate:
    """Estimated cost of capability invocation."""

    currency: str
    per_invocation: float
    per_input_unit: float | None = None
    per_output_unit: float | None = None
    unit_type: str | None = None


@dataclass
class PerformanceHints:
    """Performance characteristics of a capability."""

    typical_latency_ms: int
    max_latency_ms: int
    throughput_rps: float
    resource_intensity: ResourceIntensity
    supports_batching: bool = False
    supports_streaming: bool = False
    idempotent: bool = False
    cacheable: bool = False
    cache_ttl_seconds: int | None = None
    cost_estimate: CostEstimate | None = None


@dataclass
class CapabilityExample:
    """Example usage of a capability."""

    example_id: str
    name: str
    description: str
    input: str
    output: str
    notes: str | None = None

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        input_data: Any,
        output_data: Any,
        notes: str | None = None,
    ) -> "CapabilityExample":
        """Create a new capability example."""
        import json

        return cls(
            example_id=str(uuid.uuid4()),
            name=name,
            description=description,
            input=json.dumps(input_data),
            output=json.dumps(output_data),
            notes=notes,
        )


@dataclass
class AgentCapability:
    """Full capability definition."""

    capability_id: str
    capability_type: CapabilityType
    name: str
    description: str
    input_schema: SchemaDefinition
    output_schema: SchemaDefinition
    constraints: list[CapabilityConstraint] = field(default_factory=list)
    performance_hints: PerformanceHints | None = None
    trust_requirements: TrustRequirements | None = None
    examples: list[CapabilityExample] | None = None
    deprecated: bool = False
    deprecation_message: str | None = None

    @classmethod
    def create(
        cls,
        name: str,
        description: str,
        capability_type: CapabilityType,
        input_schema: SchemaDefinition,
        output_schema: SchemaDefinition,
        constraints: list[CapabilityConstraint] | None = None,
        performance_hints: PerformanceHints | None = None,
        trust_requirements: TrustRequirements | None = None,
    ) -> "AgentCapability":
        """Create a new capability with auto-generated ID."""
        return cls(
            capability_id=str(uuid.uuid4()),
            capability_type=capability_type,
            name=name,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema,
            constraints=constraints or [],
            performance_hints=performance_hints,
            trust_requirements=trust_requirements,
        )


# ============================================
# Capability Advertisement
# ============================================


@dataclass
class CapabilityAdvertisement:
    """Advertisement of capabilities from an agent."""

    advertisement_id: str
    agent_id: str
    capabilities: list[AgentCapability]
    advertised_at: str
    version: str
    expires_at: str | None = None

    @classmethod
    def create(
        cls,
        agent_id: str,
        capabilities: list[AgentCapability],
        version: str,
        expires_at: str | None = None,
    ) -> "CapabilityAdvertisement":
        """Create a new capability advertisement."""
        return cls(
            advertisement_id=str(uuid.uuid4()),
            agent_id=agent_id,
            capabilities=capabilities,
            advertised_at=datetime.now(timezone.utc).isoformat(),
            version=version,
            expires_at=expires_at,
        )


# ============================================
# Capability Invocation
# ============================================


@dataclass
class CapabilityInvocation:
    """Request to invoke a capability."""

    invocation_id: str
    capability_id: str
    agent_id: str
    input: str
    priority: InvocationPriority = InvocationPriority.NORMAL
    correlation_id: str | None = None
    timeout_ms: int | None = None
    metadata: dict[str, str] | None = None

    @classmethod
    def create(
        cls,
        capability_id: str,
        agent_id: str,
        input_data: Any,
        priority: InvocationPriority = InvocationPriority.NORMAL,
        timeout_ms: int | None = None,
    ) -> "CapabilityInvocation":
        """Create a new capability invocation."""
        import json

        return cls(
            invocation_id=str(uuid.uuid4()),
            capability_id=capability_id,
            agent_id=agent_id,
            input=json.dumps(input_data),
            priority=priority,
            timeout_ms=timeout_ms,
        )


@dataclass
class InvocationError:
    """Error details for failed invocation."""

    error_code: str
    error_message: str
    error_type: ErrorType
    retryable: bool
    retry_after_ms: int | None = None
    details: dict[str, str] | None = None


@dataclass
class InvocationResult:
    """Result of a capability invocation."""

    invocation_id: str
    status: InvocationStatus
    execution_time_ms: int
    completed_at: str
    output: str | None = None
    error: InvocationError | None = None
    metadata: dict[str, str] | None = None

    @classmethod
    def success(
        cls,
        invocation_id: str,
        output_data: Any,
        execution_time_ms: int,
    ) -> "InvocationResult":
        """Create a successful invocation result."""
        import json

        return cls(
            invocation_id=invocation_id,
            status=InvocationStatus.SUCCEEDED,
            execution_time_ms=execution_time_ms,
            completed_at=datetime.now(timezone.utc).isoformat(),
            output=json.dumps(output_data),
        )

    @classmethod
    def failure(
        cls,
        invocation_id: str,
        error: InvocationError,
        execution_time_ms: int,
    ) -> "InvocationResult":
        """Create a failed invocation result."""
        return cls(
            invocation_id=invocation_id,
            status=InvocationStatus.FAILED,
            execution_time_ms=execution_time_ms,
            completed_at=datetime.now(timezone.utc).isoformat(),
            error=error,
        )
