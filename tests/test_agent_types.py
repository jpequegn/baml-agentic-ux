"""
Tests for Agent Identity and Capability Types

Issue #53 - Phase 3: Agent-to-Agent Interface Negotiation
"""

import json
import pytest
from datetime import datetime, timezone

from src.lui_simulator.agent_types import (
    # Identity types
    AgentIdentity,
    AgentMetadata,
    TrustLevel,
    TrustRequirements,
    HealthStatus,
    EndpointProtocol,
    AgentEndpoint,
    RateLimit,
    AgentRegistration,
    # Discovery types
    AgentDiscoveryQuery,
    DiscoveredAgent,
    # Verification types
    VerificationType,
    VerificationRequest,
    VerificationResult,
    CapabilityType,
    SchemaType,
    SchemaProperty,
    SchemaDefinition,
    ConstraintCategory,
    ConstraintEnforcement,
    CapabilityConstraint,
    ResourceIntensity,
    CostEstimate,
    PerformanceHints,
    CapabilityExample,
    AgentCapability,
    CapabilityAdvertisement,
    # Invocation types
    InvocationPriority,
    InvocationStatus,
    ErrorType,
    CapabilityInvocation,
    InvocationError,
    InvocationResult,
)


class TestTrustLevel:
    """Test TrustLevel enum and ordering."""

    def test_trust_level_ordering(self) -> None:
        """Verify trust levels are correctly ordered."""
        assert TrustLevel.NONE < TrustLevel.BASIC
        assert TrustLevel.BASIC < TrustLevel.VERIFIED
        assert TrustLevel.VERIFIED < TrustLevel.TRUSTED
        assert TrustLevel.TRUSTED < TrustLevel.PRIVILEGED

    def test_trust_level_comparison_operators(self) -> None:
        """Test all comparison operators."""
        assert TrustLevel.NONE <= TrustLevel.BASIC
        assert TrustLevel.BASIC <= TrustLevel.BASIC
        assert TrustLevel.PRIVILEGED > TrustLevel.TRUSTED
        assert TrustLevel.TRUSTED >= TrustLevel.TRUSTED

    def test_trust_level_equality(self) -> None:
        """Test trust level equality."""
        assert TrustLevel.VERIFIED == TrustLevel.VERIFIED
        assert TrustLevel.BASIC != TrustLevel.VERIFIED


class TestTrustRequirements:
    """Test TrustRequirements class."""

    def test_default_trust_requirements(self) -> None:
        """Test default trust requirements."""
        req = TrustRequirements()
        assert req.minimum_trust_level == TrustLevel.NONE
        assert req.require_mutual_tls is False
        assert req.require_attestation is False

    def test_is_satisfied_by(self) -> None:
        """Test trust level satisfaction check."""
        req = TrustRequirements(minimum_trust_level=TrustLevel.VERIFIED)
        assert req.is_satisfied_by(TrustLevel.VERIFIED) is True
        assert req.is_satisfied_by(TrustLevel.TRUSTED) is True
        assert req.is_satisfied_by(TrustLevel.PRIVILEGED) is True
        assert req.is_satisfied_by(TrustLevel.BASIC) is False
        assert req.is_satisfied_by(TrustLevel.NONE) is False


class TestAgentMetadata:
    """Test AgentMetadata class."""

    def test_create_metadata(self) -> None:
        """Test creating metadata with current timestamps."""
        metadata = AgentMetadata.create(
            homepage="https://example.com",
            authors=["Alice", "Bob"],
            tags=["nlp", "assistant"],
        )
        assert metadata.homepage == "https://example.com"
        assert metadata.authors == ["Alice", "Bob"]
        assert metadata.tags == ["nlp", "assistant"]
        # Check timestamps are set
        assert metadata.created_at is not None
        assert metadata.updated_at is not None

    def test_metadata_default_values(self) -> None:
        """Test metadata with default values."""
        metadata = AgentMetadata.create()
        assert metadata.authors == []
        assert metadata.tags == []
        assert metadata.license is None


class TestAgentIdentity:
    """Test AgentIdentity class."""

    def test_create_agent_identity(self) -> None:
        """Test creating an agent identity."""
        identity = AgentIdentity.create(
            name="TestAgent",
            version="1.0.0",
            description="A test agent",
            provider="acme",
        )
        assert identity.name == "TestAgent"
        assert identity.version == "1.0.0"
        assert identity.description == "A test agent"
        assert identity.provider == "acme"
        assert identity.agent_id == "urn:agent:acme:testagent:1.0.0"

    def test_agent_identity_urn_format(self) -> None:
        """Test URN format validation."""
        identity = AgentIdentity.create(
            name="My Agent",
            version="2.1.0",
            description="Test",
            provider="example",
        )
        assert identity.is_valid_urn() is True
        assert identity.agent_id.startswith("urn:agent:")

    def test_from_urn(self) -> None:
        """Test creating identity from URN."""
        urn = "urn:agent:acme:myagent:1.2.3"
        identity = AgentIdentity.from_urn(urn, description="Parsed agent")
        assert identity.agent_id == urn
        assert identity.name == "myagent"
        assert identity.version == "1.2.3"
        assert identity.provider == "acme"

    def test_invalid_urn_raises_error(self) -> None:
        """Test that invalid URN raises ValueError."""
        with pytest.raises(ValueError, match="Invalid agent URN format"):
            AgentIdentity.from_urn("invalid-urn")

    def test_invalid_version_raises_error(self) -> None:
        """Test that invalid semver raises ValueError."""
        with pytest.raises(ValueError, match="Invalid semantic version"):
            AgentIdentity(
                agent_id="test",
                name="Test",
                version="not-a-version",
                description="Test",
            )

    def test_empty_name_raises_error(self) -> None:
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Agent name cannot be empty"):
            AgentIdentity(
                agent_id="test", name="", version="1.0.0", description="Test"
            )

    def test_get_spiffe_id(self) -> None:
        """Test SPIFFE ID generation."""
        identity = AgentIdentity.create(
            name="MyAgent",
            version="1.0.0",
            description="Test",
            trust_domain="example.com",
        )
        spiffe_id = identity.get_spiffe_id()
        assert spiffe_id == "spiffe://example.com/agent/myagent"

    def test_get_spiffe_id_without_trust_domain(self) -> None:
        """Test SPIFFE ID is None without trust domain."""
        identity = AgentIdentity.create(
            name="MyAgent", version="1.0.0", description="Test"
        )
        assert identity.get_spiffe_id() is None


class TestAgentEndpoint:
    """Test AgentEndpoint class."""

    def test_create_endpoint(self) -> None:
        """Test creating an endpoint."""
        endpoint = AgentEndpoint.create(
            protocol=EndpointProtocol.HTTP,
            url="https://api.example.com/v1",
            priority=1,
            health_check_path="/health",
        )
        assert endpoint.protocol == EndpointProtocol.HTTP
        assert endpoint.url == "https://api.example.com/v1"
        assert endpoint.priority == 1
        assert endpoint.endpoint_id is not None

    def test_endpoint_with_rate_limit(self) -> None:
        """Test endpoint with rate limiting."""
        rate_limit = RateLimit(
            requests_per_second=10.0, burst_size=20, retry_after_seconds=30
        )
        endpoint = AgentEndpoint.create(
            protocol=EndpointProtocol.GRPC,
            url="grpc://api.example.com:50051",
            rate_limit=rate_limit,
        )
        assert endpoint.rate_limit is not None
        assert endpoint.rate_limit.requests_per_second == 10.0


class TestAgentRegistration:
    """Test AgentRegistration class."""

    def test_create_registration(self) -> None:
        """Test creating a registration."""
        identity = AgentIdentity.create(
            name="RegAgent", version="1.0.0", description="Test"
        )
        endpoint = AgentEndpoint.create(
            protocol=EndpointProtocol.HTTP, url="https://api.example.com"
        )
        registration = AgentRegistration(
            identity=identity,
            endpoints=[endpoint],
            capabilities=["cap1", "cap2"],
        )
        assert registration.identity.name == "RegAgent"
        assert len(registration.endpoints) == 1
        assert len(registration.capabilities) == 2


class TestAgentDiscovery:
    """Test agent discovery types."""

    def test_create_discovery_query(self) -> None:
        """Test creating a discovery query."""
        query = AgentDiscoveryQuery.create(
            capability_filter=["nlp", "translation"],
            provider_filter=["acme"],
            trust_level_filter=TrustLevel.VERIFIED,
            limit=20,
        )
        assert len(query.capability_filter) == 2
        assert query.trust_level_filter == TrustLevel.VERIFIED
        assert query.limit == 20
        assert query.query_id is not None

    def test_discovered_agent(self) -> None:
        """Test DiscoveredAgent structure."""
        identity = AgentIdentity.create(
            name="FoundAgent", version="1.0.0", description="Test"
        )
        discovered = DiscoveredAgent(
            identity=identity,
            capability_count=5,
            endpoint_count=2,
            trust_level=TrustLevel.TRUSTED,
            last_seen=datetime.now(timezone.utc).isoformat(),
            health_status=HealthStatus.HEALTHY,
        )
        assert discovered.capability_count == 5
        assert discovered.health_status == HealthStatus.HEALTHY


class TestVerification:
    """Test verification types."""

    def test_create_verification_request(self) -> None:
        """Test creating a verification request."""
        request = VerificationRequest.create(
            agent_id="urn:agent:acme:test:1.0.0",
            verification_type=VerificationType.CERTIFICATE,
        )
        assert request.agent_id == "urn:agent:acme:test:1.0.0"
        assert request.verification_type == VerificationType.CERTIFICATE
        assert request.request_id is not None

    def test_verification_result_success(self) -> None:
        """Test successful verification result."""
        result = VerificationResult.success(
            request_id="req-123",
            agent_id="urn:agent:acme:test:1.0.0",
            trust_level=TrustLevel.VERIFIED,
            verification_time_ms=50,
        )
        assert result.verified is True
        assert result.trust_level == TrustLevel.VERIFIED
        assert result.failure_reason is None

    def test_verification_result_failure(self) -> None:
        """Test failed verification result."""
        result = VerificationResult.failure(
            request_id="req-456",
            agent_id="urn:agent:acme:test:1.0.0",
            failure_reason="Certificate expired",
            verification_time_ms=10,
        )
        assert result.verified is False
        assert result.trust_level == TrustLevel.NONE
        assert result.failure_reason == "Certificate expired"


class TestSchemaDefinition:
    """Test SchemaDefinition class."""

    def test_string_schema(self) -> None:
        """Test creating a string schema."""
        schema = SchemaDefinition.string(
            description="A name field",
            min_length=1,
            max_length=100,
        )
        assert schema.type == SchemaType.STRING
        assert schema.description == "A name field"
        assert len(schema.constraints) == 2

    def test_integer_schema(self) -> None:
        """Test creating an integer schema."""
        schema = SchemaDefinition.integer(
            description="Age", min_value=0, max_value=150
        )
        assert schema.type == SchemaType.INTEGER
        assert len(schema.constraints) == 2

    def test_boolean_schema(self) -> None:
        """Test creating a boolean schema."""
        schema = SchemaDefinition.boolean(description="Is active")
        assert schema.type == SchemaType.BOOLEAN
        assert schema.description == "Is active"

    def test_array_schema(self) -> None:
        """Test creating an array schema."""
        item_schema = SchemaDefinition.string()
        schema = SchemaDefinition.array(
            items=item_schema, description="List of names", min_items=1, max_items=10
        )
        assert schema.type == SchemaType.ARRAY
        assert schema.items is not None
        assert schema.items.type == SchemaType.STRING

    def test_object_schema(self) -> None:
        """Test creating an object schema."""
        properties = [
            SchemaProperty(
                name="name", schema=SchemaDefinition.string(), description="User name"
            ),
            SchemaProperty(
                name="age", schema=SchemaDefinition.integer(), description="User age"
            ),
        ]
        schema = SchemaDefinition.object(
            properties=properties, required=["name"], description="User object"
        )
        assert schema.type == SchemaType.OBJECT
        assert len(schema.properties) == 2
        assert schema.required == ["name"]

    def test_enum_schema(self) -> None:
        """Test creating an enum schema."""
        schema = SchemaDefinition.enum(
            values=["low", "medium", "high"], description="Priority level"
        )
        assert schema.type == SchemaType.ENUM
        assert schema.enum_values == ["low", "medium", "high"]


class TestCapabilityConstraint:
    """Test CapabilityConstraint class."""

    def test_rate_limit_constraint(self) -> None:
        """Test creating a rate limit constraint."""
        constraint = CapabilityConstraint.rate_limit(requests_per_minute=60)
        assert constraint.constraint_type == ConstraintCategory.RATE_LIMIT
        assert constraint.enforcement == ConstraintEnforcement.HARD
        assert constraint.parameters["requests_per_minute"] == "60"

    def test_time_limit_constraint(self) -> None:
        """Test creating a time limit constraint."""
        constraint = CapabilityConstraint.time_limit(
            max_seconds=30, enforcement=ConstraintEnforcement.SOFT
        )
        assert constraint.constraint_type == ConstraintCategory.TIME_LIMIT
        assert constraint.enforcement == ConstraintEnforcement.SOFT
        assert constraint.parameters["max_seconds"] == "30"


class TestPerformanceHints:
    """Test PerformanceHints class."""

    def test_performance_hints_with_cost(self) -> None:
        """Test performance hints with cost estimate."""
        cost = CostEstimate(
            currency="USD",
            per_invocation=0.01,
            per_input_unit=0.001,
            unit_type="token",
        )
        hints = PerformanceHints(
            typical_latency_ms=100,
            max_latency_ms=500,
            throughput_rps=50.0,
            resource_intensity=ResourceIntensity.MEDIUM,
            idempotent=True,
            cacheable=True,
            cache_ttl_seconds=300,
            cost_estimate=cost,
        )
        assert hints.typical_latency_ms == 100
        assert hints.idempotent is True
        assert hints.cost_estimate.per_invocation == 0.01


class TestAgentCapability:
    """Test AgentCapability class."""

    def test_create_capability(self) -> None:
        """Test creating a capability."""
        input_schema = SchemaDefinition.object(
            properties=[
                SchemaProperty(name="query", schema=SchemaDefinition.string())
            ],
            required=["query"],
        )
        output_schema = SchemaDefinition.object(
            properties=[
                SchemaProperty(name="result", schema=SchemaDefinition.string())
            ],
            required=["result"],
        )
        capability = AgentCapability.create(
            name="Search",
            description="Search for information",
            capability_type=CapabilityType.QUERY,
            input_schema=input_schema,
            output_schema=output_schema,
        )
        assert capability.name == "Search"
        assert capability.capability_type == CapabilityType.QUERY
        assert capability.deprecated is False
        assert capability.capability_id is not None

    def test_capability_with_constraints(self) -> None:
        """Test capability with constraints."""
        input_schema = SchemaDefinition.string()
        output_schema = SchemaDefinition.string()
        constraints = [
            CapabilityConstraint.rate_limit(100),
            CapabilityConstraint.time_limit(60),
        ]
        capability = AgentCapability.create(
            name="Transform",
            description="Transform data",
            capability_type=CapabilityType.TRANSFORM,
            input_schema=input_schema,
            output_schema=output_schema,
            constraints=constraints,
        )
        assert len(capability.constraints) == 2


class TestCapabilityExample:
    """Test CapabilityExample class."""

    def test_create_example(self) -> None:
        """Test creating a capability example."""
        example = CapabilityExample.create(
            name="Basic search",
            description="Search for weather",
            input_data={"query": "weather today"},
            output_data={"result": "Sunny, 72°F"},
        )
        assert example.name == "Basic search"
        assert json.loads(example.input) == {"query": "weather today"}
        assert json.loads(example.output) == {"result": "Sunny, 72°F"}


class TestCapabilityAdvertisement:
    """Test CapabilityAdvertisement class."""

    def test_create_advertisement(self) -> None:
        """Test creating a capability advertisement."""
        capability = AgentCapability.create(
            name="Echo",
            description="Echo input",
            capability_type=CapabilityType.ACTION,
            input_schema=SchemaDefinition.string(),
            output_schema=SchemaDefinition.string(),
        )
        advertisement = CapabilityAdvertisement.create(
            agent_id="urn:agent:acme:echo:1.0.0",
            capabilities=[capability],
            version="1.0.0",
        )
        assert advertisement.agent_id == "urn:agent:acme:echo:1.0.0"
        assert len(advertisement.capabilities) == 1
        assert advertisement.version == "1.0.0"
        assert advertisement.advertised_at is not None


class TestCapabilityInvocation:
    """Test capability invocation types."""

    def test_create_invocation(self) -> None:
        """Test creating an invocation."""
        invocation = CapabilityInvocation.create(
            capability_id="cap-123",
            agent_id="urn:agent:acme:test:1.0.0",
            input_data={"query": "test"},
            priority=InvocationPriority.HIGH,
            timeout_ms=5000,
        )
        assert invocation.capability_id == "cap-123"
        assert invocation.priority == InvocationPriority.HIGH
        assert invocation.timeout_ms == 5000
        assert json.loads(invocation.input) == {"query": "test"}

    def test_invocation_result_success(self) -> None:
        """Test successful invocation result."""
        result = InvocationResult.success(
            invocation_id="inv-123",
            output_data={"result": "success"},
            execution_time_ms=50,
        )
        assert result.status == InvocationStatus.SUCCEEDED
        assert json.loads(result.output) == {"result": "success"}
        assert result.error is None

    def test_invocation_result_failure(self) -> None:
        """Test failed invocation result."""
        error = InvocationError(
            error_code="VALIDATION_ERROR",
            error_message="Invalid input",
            error_type=ErrorType.VALIDATION,
            retryable=False,
        )
        result = InvocationResult.failure(
            invocation_id="inv-456", error=error, execution_time_ms=10
        )
        assert result.status == InvocationStatus.FAILED
        assert result.output is None
        assert result.error.error_code == "VALIDATION_ERROR"
        assert result.error.retryable is False


class TestEnumValues:
    """Test all enum types have expected values."""

    def test_capability_types(self) -> None:
        """Test CapabilityType enum values."""
        assert CapabilityType.ACTION.value == "action"
        assert CapabilityType.QUERY.value == "query"
        assert CapabilityType.TRANSFORM.value == "transform"
        assert CapabilityType.COMPOSITE.value == "composite"
        assert CapabilityType.DELEGATION.value == "delegation"

    def test_health_status_values(self) -> None:
        """Test HealthStatus enum values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"

    def test_endpoint_protocol_values(self) -> None:
        """Test EndpointProtocol enum values."""
        assert EndpointProtocol.HTTP.value == "http"
        assert EndpointProtocol.GRPC.value == "grpc"
        assert EndpointProtocol.WEBSOCKET.value == "websocket"
        assert EndpointProtocol.MCP.value == "mcp"
        assert EndpointProtocol.A2A.value == "a2a"

    def test_invocation_status_values(self) -> None:
        """Test InvocationStatus enum values."""
        assert InvocationStatus.PENDING.value == "pending"
        assert InvocationStatus.RUNNING.value == "running"
        assert InvocationStatus.SUCCEEDED.value == "succeeded"
        assert InvocationStatus.FAILED.value == "failed"
        assert InvocationStatus.TIMEOUT.value == "timeout"
        assert InvocationStatus.CANCELLED.value == "cancelled"

    def test_error_type_values(self) -> None:
        """Test ErrorType enum values."""
        assert ErrorType.VALIDATION.value == "validation"
        assert ErrorType.AUTHENTICATION.value == "authentication"
        assert ErrorType.AUTHORIZATION.value == "authorization"
        assert ErrorType.NOT_FOUND.value == "not_found"
        assert ErrorType.RATE_LIMITED.value == "rate_limited"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_agent_identity_with_special_characters(self) -> None:
        """Test agent identity handles special characters in name."""
        identity = AgentIdentity.create(
            name="My Cool Agent",
            version="1.0.0",
            description="Test",
            provider="example",
        )
        # Should normalize to lowercase with hyphens
        assert "my-cool-agent" in identity.agent_id

    def test_semver_with_prerelease(self) -> None:
        """Test semantic version with prerelease tag."""
        identity = AgentIdentity.create(
            name="BetaAgent",
            version="1.0.0-beta.1",
            description="Test",
        )
        assert identity.version == "1.0.0-beta.1"

    def test_semver_with_build_metadata(self) -> None:
        """Test semantic version with build metadata."""
        identity = AgentIdentity.create(
            name="BuildAgent",
            version="1.0.0+build.123",
            description="Test",
        )
        assert identity.version == "1.0.0+build.123"

    def test_empty_capability_constraints(self) -> None:
        """Test capability with empty constraints."""
        capability = AgentCapability.create(
            name="Simple",
            description="Simple capability",
            capability_type=CapabilityType.ACTION,
            input_schema=SchemaDefinition.string(),
            output_schema=SchemaDefinition.string(),
            constraints=[],
        )
        assert capability.constraints == []

    def test_discovery_query_defaults(self) -> None:
        """Test discovery query with all defaults."""
        query = AgentDiscoveryQuery.create()
        assert query.capability_filter == []
        assert query.provider_filter == []
        assert query.tag_filter == []
        assert query.trust_level_filter is None
        assert query.limit == 10
        assert query.offset == 0
