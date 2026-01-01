"""
Tests for Agent Card Schema (A2A-compatible)

Issue #54 - Phase 3: Agent-to-Agent Interface Negotiation
"""

import json
import pytest
from datetime import datetime, timezone, timedelta

from src.lui_simulator.agent_types import (
    AgentIdentity,
    AgentCapability,
    CapabilityType,
    SchemaDefinition,
)
from src.agent_negotiation.agent_card import (
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
    ProtocolNegotiationRequest,
    ProtocolNegotiationResult,
    # Validation
    CardValidationError,
    CardValidationWarning,
    # Utilities
    AgentCardBuilder,
    AgentCardValidator,
    AgentCardSerializer,
    negotiate_protocol,
)


# ============================================
# Test Fixtures
# ============================================


@pytest.fixture
def sample_identity() -> AgentIdentity:
    """Create a sample agent identity."""
    return AgentIdentity.create(
        name="TestAgent",
        version="1.0.0",
        description="A test agent for unit tests",
        provider="acme",
        trust_domain="example.com",
    )


@pytest.fixture
def sample_capability() -> AgentCapability:
    """Create a sample capability."""
    return AgentCapability.create(
        name="search",
        description="Search for information",
        capability_type=CapabilityType.QUERY,
        input_schema=SchemaDefinition.string(description="Search query"),
        output_schema=SchemaDefinition.string(description="Search results"),
    )


@pytest.fixture
def sample_protocol() -> SupportedProtocol:
    """Create a sample protocol."""
    return SupportedProtocol(
        protocol=ProtocolType.A2A,
        version="1.0.0",
        uri="https://a2a.dev/spec/1.0",
    )


@pytest.fixture
def sample_endpoint() -> CardEndpoint:
    """Create a sample endpoint."""
    return CardEndpoint(
        endpoint_type=EndpointType.PRIMARY,
        url="https://api.example.com/v1",
        protocol=ProtocolType.A2A,
        auth_config=AuthConfig(method=AuthMethod.BEARER_TOKEN),
        timeout_ms=30000,
    )


@pytest.fixture
def sample_card(
    sample_identity: AgentIdentity,
    sample_capability: AgentCapability,
    sample_protocol: SupportedProtocol,
    sample_endpoint: CardEndpoint,
) -> AgentCard:
    """Create a sample agent card."""
    return AgentCard(
        identity=sample_identity,
        capabilities=[sample_capability],
        supported_protocols=[sample_protocol],
        endpoints=[sample_endpoint],
        compliance_tags=[
            ComplianceTag(standard=ComplianceStandard.GDPR, certified=True)
        ],
    )


# ============================================
# Test Protocol Types
# ============================================


class TestProtocolType:
    """Test ProtocolType enum."""

    def test_protocol_values(self) -> None:
        """Test protocol type values."""
        assert ProtocolType.A2A.value == "a2a"
        assert ProtocolType.MCP.value == "mcp"
        assert ProtocolType.OPENAPI.value == "openapi"
        assert ProtocolType.JSON_RPC.value == "json_rpc"
        assert ProtocolType.GRPC.value == "grpc"

    def test_supported_protocol_creation(self) -> None:
        """Test creating a supported protocol."""
        protocol = SupportedProtocol(
            protocol=ProtocolType.A2A,
            version="1.0.0",
            uri="https://a2a.dev/spec",
            extensions=["streaming"],
        )
        assert protocol.protocol == ProtocolType.A2A
        assert protocol.version == "1.0.0"
        assert protocol.uri == "https://a2a.dev/spec"
        assert protocol.extensions == ["streaming"]
        assert protocol.deprecated is False

    def test_supported_protocol_to_dict(self) -> None:
        """Test protocol serialization."""
        protocol = SupportedProtocol(
            protocol=ProtocolType.MCP,
            version="2.0.0",
            deprecated=True,
        )
        d = protocol.to_dict()
        assert d["protocol"] == "mcp"
        assert d["version"] == "2.0.0"
        assert d["deprecated"] is True


# ============================================
# Test Endpoint Types
# ============================================


class TestEndpointTypes:
    """Test endpoint-related types."""

    def test_endpoint_type_values(self) -> None:
        """Test endpoint type values."""
        assert EndpointType.PRIMARY.value == "primary"
        assert EndpointType.FALLBACK.value == "fallback"
        assert EndpointType.HEALTH_CHECK.value == "health_check"
        assert EndpointType.DISCOVERY.value == "discovery"

    def test_auth_method_values(self) -> None:
        """Test auth method values."""
        assert AuthMethod.NONE.value == "none"
        assert AuthMethod.API_KEY.value == "api_key"
        assert AuthMethod.BEARER_TOKEN.value == "bearer_token"
        assert AuthMethod.MTLS.value == "mtls"
        assert AuthMethod.OAUTH2.value == "oauth2"

    def test_auth_config_creation(self) -> None:
        """Test creating auth config."""
        config = AuthConfig(
            method=AuthMethod.OAUTH2,
            token_endpoint="https://auth.example.com/token",
            scopes=["read", "write"],
            audience="api.example.com",
        )
        assert config.method == AuthMethod.OAUTH2
        assert config.scopes == ["read", "write"]

    def test_auth_config_to_dict(self) -> None:
        """Test auth config serialization."""
        config = AuthConfig(
            method=AuthMethod.API_KEY, header_name="X-API-Key"
        )
        d = config.to_dict()
        assert d["method"] == "api_key"
        assert d["header_name"] == "X-API-Key"

    def test_retry_policy_defaults(self) -> None:
        """Test retry policy defaults."""
        policy = RetryPolicy()
        assert policy.max_retries == 3
        assert policy.initial_backoff_ms == 100
        assert policy.max_backoff_ms == 10000
        assert policy.backoff_multiplier == 2.0
        assert 429 in policy.retryable_status_codes
        assert 503 in policy.retryable_status_codes

    def test_card_endpoint_creation(self) -> None:
        """Test creating a card endpoint."""
        endpoint = CardEndpoint(
            endpoint_type=EndpointType.PRIMARY,
            url="https://api.example.com",
            protocol=ProtocolType.A2A,
            timeout_ms=5000,
        )
        assert endpoint.endpoint_type == EndpointType.PRIMARY
        assert endpoint.url == "https://api.example.com"
        assert endpoint.timeout_ms == 5000

    def test_card_endpoint_to_dict(self) -> None:
        """Test endpoint serialization."""
        endpoint = CardEndpoint(
            endpoint_type=EndpointType.HEALTH_CHECK,
            url="https://api.example.com/health",
            protocol=ProtocolType.OPENAPI,
            auth_config=AuthConfig(method=AuthMethod.NONE),
        )
        d = endpoint.to_dict()
        assert d["endpoint_type"] == "health_check"
        assert d["url"] == "https://api.example.com/health"
        assert d["protocol"] == "openapi"
        assert d["auth_config"]["method"] == "none"


# ============================================
# Test Compliance Types
# ============================================


class TestComplianceTypes:
    """Test compliance-related types."""

    def test_compliance_standard_values(self) -> None:
        """Test compliance standard values."""
        assert ComplianceStandard.GDPR.value == "gdpr"
        assert ComplianceStandard.HIPAA.value == "hipaa"
        assert ComplianceStandard.SOC2.value == "soc2"
        assert ComplianceStandard.ISO27001.value == "iso27001"
        assert ComplianceStandard.PCI_DSS.value == "pci_dss"

    def test_compliance_tag_creation(self) -> None:
        """Test creating a compliance tag."""
        tag = ComplianceTag(
            standard=ComplianceStandard.SOC2_TYPE2,
            certified=True,
            certificate_url="https://example.com/cert.pdf",
            auditor="Big4 Firm",
        )
        assert tag.standard == ComplianceStandard.SOC2_TYPE2
        assert tag.certified is True
        assert tag.auditor == "Big4 Firm"

    def test_compliance_tag_expiry_check_not_expired(self) -> None:
        """Test compliance tag is not expired."""
        future_date = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
        tag = ComplianceTag(
            standard=ComplianceStandard.GDPR,
            expiry_date=future_date,
        )
        assert tag.is_expired() is False

    def test_compliance_tag_expiry_check_expired(self) -> None:
        """Test compliance tag is expired."""
        past_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        tag = ComplianceTag(
            standard=ComplianceStandard.GDPR,
            expiry_date=past_date,
        )
        assert tag.is_expired() is True

    def test_compliance_tag_no_expiry(self) -> None:
        """Test compliance tag without expiry date."""
        tag = ComplianceTag(standard=ComplianceStandard.GDPR)
        assert tag.is_expired() is False

    def test_data_handling_policy_creation(self) -> None:
        """Test creating data handling policy."""
        policy = DataHandlingPolicy(
            encryption_at_rest=True,
            encryption_in_transit=True,
            audit_logging=True,
            data_residency=["US", "EU"],
            data_retention_days=90,
        )
        assert policy.encryption_at_rest is True
        assert policy.data_residency == ["US", "EU"]
        assert policy.data_retention_days == 90


# ============================================
# Test Agent Card
# ============================================


class TestAgentCard:
    """Test AgentCard class."""

    def test_agent_card_creation(self, sample_card: AgentCard) -> None:
        """Test creating an agent card."""
        assert sample_card.identity.name == "TestAgent"
        assert len(sample_card.capabilities) == 1
        assert len(sample_card.supported_protocols) == 1
        assert len(sample_card.endpoints) == 1
        assert sample_card.card_version == "1.0.0"

    def test_get_primary_endpoint(self, sample_card: AgentCard) -> None:
        """Test getting primary endpoint."""
        endpoint = sample_card.get_primary_endpoint()
        assert endpoint is not None
        assert endpoint.endpoint_type == EndpointType.PRIMARY

    def test_get_discovery_endpoint_none(self, sample_card: AgentCard) -> None:
        """Test getting discovery endpoint when not present."""
        endpoint = sample_card.get_discovery_endpoint()
        assert endpoint is None

    def test_supports_protocol(self, sample_card: AgentCard) -> None:
        """Test protocol support check."""
        assert sample_card.supports_protocol(ProtocolType.A2A) is True
        assert sample_card.supports_protocol(ProtocolType.MCP) is False

    def test_get_protocol(self, sample_card: AgentCard) -> None:
        """Test getting protocol details."""
        protocol = sample_card.get_protocol(ProtocolType.A2A)
        assert protocol is not None
        assert protocol.version == "1.0.0"

    def test_is_compliant_with(self, sample_card: AgentCard) -> None:
        """Test compliance check."""
        assert sample_card.is_compliant_with(ComplianceStandard.GDPR) is True
        assert sample_card.is_compliant_with(ComplianceStandard.HIPAA) is False

    def test_get_capability(self, sample_card: AgentCard) -> None:
        """Test getting capability by ID."""
        cap = sample_card.capabilities[0]
        found = sample_card.get_capability(cap.capability_id)
        assert found is not None
        assert found.name == "search"

    def test_to_dict(self, sample_card: AgentCard) -> None:
        """Test card to dictionary conversion."""
        d = sample_card.to_dict()
        assert d["card_version"] == "1.0.0"
        assert d["identity"]["name"] == "TestAgent"
        assert len(d["capabilities"]) == 1
        assert len(d["supported_protocols"]) == 1
        assert len(d["endpoints"]) == 1

    def test_to_json(self, sample_card: AgentCard) -> None:
        """Test card to JSON conversion."""
        json_str = sample_card.to_json()
        parsed = json.loads(json_str)
        assert parsed["card_version"] == "1.0.0"
        assert parsed["identity"]["name"] == "TestAgent"

    def test_compute_hash(self, sample_card: AgentCard) -> None:
        """Test card hash computation."""
        hash1 = sample_card.compute_hash()
        hash2 = sample_card.compute_hash()
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex


# ============================================
# Test Agent Card Summary
# ============================================


class TestAgentCardSummary:
    """Test AgentCardSummary class."""

    def test_from_card(self, sample_card: AgentCard) -> None:
        """Test creating summary from card."""
        summary = AgentCardSummary.from_card(
            sample_card, "https://example.com/agents/testagent"
        )
        assert summary.agent_id == sample_card.identity.agent_id
        assert summary.name == "TestAgent"
        assert summary.capability_count == 1
        assert ProtocolType.A2A in summary.protocols
        assert ComplianceStandard.GDPR in summary.compliance_standards

    def test_summary_to_dict(self, sample_card: AgentCard) -> None:
        """Test summary serialization."""
        summary = AgentCardSummary.from_card(
            sample_card, "https://example.com/agents/testagent"
        )
        d = summary.to_dict()
        assert d["name"] == "TestAgent"
        assert d["capability_count"] == 1
        assert "a2a" in d["protocols"]


# ============================================
# Test Well-Known Discovery
# ============================================


class TestWellKnownDiscovery:
    """Test well-known discovery types."""

    def test_well_known_agent_descriptions(self, sample_card: AgentCard) -> None:
        """Test well-known agent descriptions."""
        summary = AgentCardSummary.from_card(sample_card, "https://example.com")
        descriptions = WellKnownAgentDescriptions(
            agents=[summary],
            total_count=1,
        )
        assert descriptions.total_count == 1
        assert len(descriptions.agents) == 1
        assert descriptions.schema_version == "1.0.0"

    def test_well_known_to_json(self, sample_card: AgentCard) -> None:
        """Test well-known to JSON."""
        summary = AgentCardSummary.from_card(sample_card, "https://example.com")
        descriptions = WellKnownAgentDescriptions(agents=[summary], total_count=1)
        json_str = descriptions.to_json()
        parsed = json.loads(json_str)
        assert parsed["total_count"] == 1
        assert len(parsed["agents"]) == 1

    def test_agent_card_request(self) -> None:
        """Test agent card request creation."""
        request = AgentCardRequest(
            agent_id="urn:agent:acme:test:1.0.0",
            include_capabilities=True,
        )
        assert request.agent_id == "urn:agent:acme:test:1.0.0"
        assert request.include_capabilities is True
        assert request.request_id is not None

    def test_agent_card_response_success(self, sample_card: AgentCard) -> None:
        """Test successful agent card response."""
        response = AgentCardResponse.success(
            request_id="req-123",
            card=sample_card,
            cached=True,
        )
        assert response.found is True
        assert response.agent_card is not None
        assert response.cached is True
        assert response.error is None

    def test_agent_card_response_not_found(self) -> None:
        """Test not-found agent card response."""
        response = AgentCardResponse.not_found(
            request_id="req-456",
            agent_id="unknown-agent",
        )
        assert response.found is False
        assert response.agent_card is None
        assert response.error is not None
        assert response.error.error_code == "AGENT_NOT_FOUND"


# ============================================
# Test Protocol Negotiation
# ============================================


class TestProtocolNegotiation:
    """Test protocol negotiation."""

    def test_successful_negotiation(self, sample_card: AgentCard) -> None:
        """Test successful protocol negotiation."""
        request = ProtocolNegotiationRequest(
            client_protocols=[
                SupportedProtocol(protocol=ProtocolType.A2A, version="1.0.0"),
                SupportedProtocol(protocol=ProtocolType.MCP, version="1.0.0"),
            ],
        )
        result = negotiate_protocol(sample_card, request)
        assert result.success is True
        assert result.selected_protocol is not None
        assert result.selected_protocol.protocol == ProtocolType.A2A
        assert result.selected_endpoint is not None

    def test_negotiation_with_preferred_protocol(self, sample_card: AgentCard) -> None:
        """Test negotiation with preferred protocol."""
        # Add MCP to the card
        sample_card.supported_protocols.append(
            SupportedProtocol(protocol=ProtocolType.MCP, version="1.0.0")
        )
        sample_card.endpoints.append(
            CardEndpoint(
                endpoint_type=EndpointType.FALLBACK,
                url="https://api.example.com/mcp",
                protocol=ProtocolType.MCP,
            )
        )
        request = ProtocolNegotiationRequest(
            client_protocols=[
                SupportedProtocol(protocol=ProtocolType.A2A, version="1.0.0"),
                SupportedProtocol(protocol=ProtocolType.MCP, version="1.0.0"),
            ],
            preferred_protocol=ProtocolType.MCP,
        )
        result = negotiate_protocol(sample_card, request)
        assert result.success is True
        assert result.selected_protocol.protocol == ProtocolType.MCP

    def test_negotiation_no_common_protocols(self, sample_card: AgentCard) -> None:
        """Test negotiation failure with no common protocols."""
        request = ProtocolNegotiationRequest(
            client_protocols=[
                SupportedProtocol(protocol=ProtocolType.GRAPHQL, version="1.0.0"),
            ],
        )
        result = negotiate_protocol(sample_card, request)
        assert result.success is False
        assert result.failure_reason is not None
        assert "No common protocols" in result.failure_reason


# ============================================
# Test Card Validation
# ============================================


class TestCardValidation:
    """Test card validation."""

    def test_validate_valid_card(self, sample_card: AgentCard) -> None:
        """Test validating a valid card."""
        validator = AgentCardValidator()
        result = validator.validate(sample_card)
        assert result.valid is True
        assert len(result.errors) == 0
        assert result.a2a_compliant is True

    def test_validate_missing_protocols(
        self, sample_identity: AgentIdentity, sample_capability: AgentCapability
    ) -> None:
        """Test validating card with missing protocols."""
        card = AgentCard(
            identity=sample_identity,
            capabilities=[sample_capability],
            supported_protocols=[],
            endpoints=[
                CardEndpoint(
                    endpoint_type=EndpointType.PRIMARY,
                    url="https://example.com",
                    protocol=ProtocolType.A2A,
                )
            ],
        )
        validator = AgentCardValidator()
        result = validator.validate(card)
        assert result.valid is False
        assert any(e.error_code == "EMPTY_LIST" for e in result.errors)

    def test_validate_missing_endpoints(
        self, sample_identity: AgentIdentity, sample_capability: AgentCapability
    ) -> None:
        """Test validating card with missing endpoints."""
        card = AgentCard(
            identity=sample_identity,
            capabilities=[sample_capability],
            supported_protocols=[
                SupportedProtocol(protocol=ProtocolType.A2A, version="1.0.0")
            ],
            endpoints=[],
        )
        validator = AgentCardValidator()
        result = validator.validate(card)
        assert result.valid is False
        assert any(e.error_code == "EMPTY_LIST" for e in result.errors)

    def test_validate_expired_compliance(self, sample_card: AgentCard) -> None:
        """Test validation warns about expired compliance."""
        past_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        sample_card.compliance_tags.append(
            ComplianceTag(
                standard=ComplianceStandard.HIPAA,
                certified=True,
                expiry_date=past_date,
            )
        )
        validator = AgentCardValidator()
        result = validator.validate(sample_card)
        assert any(w.warning_code == "EXPIRED_CERTIFICATION" for w in result.warnings)

    def test_validate_no_primary_endpoint(
        self, sample_identity: AgentIdentity, sample_capability: AgentCapability
    ) -> None:
        """Test validation warns about missing primary endpoint."""
        card = AgentCard(
            identity=sample_identity,
            capabilities=[sample_capability],
            supported_protocols=[
                SupportedProtocol(protocol=ProtocolType.A2A, version="1.0.0")
            ],
            endpoints=[
                CardEndpoint(
                    endpoint_type=EndpointType.FALLBACK,
                    url="https://example.com",
                    protocol=ProtocolType.A2A,
                )
            ],
        )
        validator = AgentCardValidator()
        result = validator.validate(card)
        assert result.valid is True  # Still valid, just a warning
        assert any(w.warning_code == "NO_PRIMARY_ENDPOINT" for w in result.warnings)


# ============================================
# Test Agent Card Builder
# ============================================


class TestAgentCardBuilder:
    """Test AgentCardBuilder class."""

    def test_builder_basic_card(
        self, sample_identity: AgentIdentity, sample_capability: AgentCapability
    ) -> None:
        """Test building a basic card."""
        card = (
            AgentCardBuilder(sample_identity)
            .add_capability(sample_capability)
            .add_protocol(ProtocolType.A2A, "1.0.0")
            .add_endpoint(
                EndpointType.PRIMARY,
                "https://api.example.com",
                ProtocolType.A2A,
            )
            .build()
        )
        assert card.identity == sample_identity
        assert len(card.capabilities) == 1
        assert len(card.supported_protocols) == 1
        assert len(card.endpoints) == 1

    def test_builder_with_compliance(
        self, sample_identity: AgentIdentity, sample_capability: AgentCapability
    ) -> None:
        """Test building card with compliance."""
        card = (
            AgentCardBuilder(sample_identity)
            .add_capability(sample_capability)
            .add_protocol(ProtocolType.A2A, "1.0.0")
            .add_endpoint(EndpointType.PRIMARY, "https://api.example.com", ProtocolType.A2A)
            .add_compliance(ComplianceStandard.GDPR)
            .add_compliance(ComplianceStandard.SOC2_TYPE2)
            .build()
        )
        assert len(card.compliance_tags) == 2
        assert card.is_compliant_with(ComplianceStandard.GDPR)

    def test_builder_with_data_handling(
        self, sample_identity: AgentIdentity, sample_capability: AgentCapability
    ) -> None:
        """Test building card with data handling."""
        card = (
            AgentCardBuilder(sample_identity)
            .add_capability(sample_capability)
            .add_protocol(ProtocolType.A2A, "1.0.0")
            .add_endpoint(EndpointType.PRIMARY, "https://api.example.com", ProtocolType.A2A)
            .with_data_handling(
                encryption_at_rest=True,
                encryption_in_transit=True,
                data_residency=["US", "EU"],
            )
            .build()
        )
        assert card.data_handling is not None
        assert card.data_handling.encryption_at_rest is True
        assert card.data_handling.data_residency == ["US", "EU"]

    def test_builder_fails_without_protocols(
        self, sample_identity: AgentIdentity
    ) -> None:
        """Test builder fails without protocols."""
        builder = AgentCardBuilder(sample_identity).add_endpoint(
            EndpointType.PRIMARY, "https://api.example.com", ProtocolType.A2A
        )
        with pytest.raises(ValueError, match="At least one protocol"):
            builder.build()

    def test_builder_fails_without_endpoints(
        self, sample_identity: AgentIdentity
    ) -> None:
        """Test builder fails without endpoints."""
        builder = AgentCardBuilder(sample_identity).add_protocol(
            ProtocolType.A2A, "1.0.0"
        )
        with pytest.raises(ValueError, match="At least one endpoint"):
            builder.build()


# ============================================
# Test Serializer
# ============================================


class TestAgentCardSerializer:
    """Test AgentCardSerializer class."""

    def test_to_json(self, sample_card: AgentCard) -> None:
        """Test serializing to JSON."""
        json_str = AgentCardSerializer.to_json(sample_card)
        parsed = json.loads(json_str)
        assert parsed["card_version"] == "1.0.0"

    def test_to_dict(self, sample_card: AgentCard) -> None:
        """Test serializing to dict."""
        d = AgentCardSerializer.to_dict(sample_card)
        assert d["card_version"] == "1.0.0"

    def test_to_a2a_format(self, sample_card: AgentCard) -> None:
        """Test serializing to A2A format."""
        a2a = AgentCardSerializer.to_a2a_format(sample_card)
        assert "agentCard" in a2a
        assert a2a["agentCard"]["version"] == "1.0.0"
        assert "agent" in a2a["agentCard"]
        assert "capabilities" in a2a["agentCard"]
        assert "protocols" in a2a["agentCard"]

    def test_to_well_known_format(self, sample_card: AgentCard) -> None:
        """Test creating well-known format."""
        descriptions = AgentCardSerializer.to_well_known_format(
            [sample_card], "https://example.com"
        )
        assert descriptions.total_count == 1
        assert len(descriptions.agents) == 1
        assert "testagent" in descriptions.agents[0].discovery_url.lower()


# ============================================
# Test Edge Cases
# ============================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_capabilities_list(
        self, sample_identity: AgentIdentity
    ) -> None:
        """Test card with no capabilities."""
        card = AgentCard(
            identity=sample_identity,
            capabilities=[],
            supported_protocols=[
                SupportedProtocol(protocol=ProtocolType.A2A, version="1.0.0")
            ],
            endpoints=[
                CardEndpoint(
                    endpoint_type=EndpointType.PRIMARY,
                    url="https://api.example.com",
                    protocol=ProtocolType.A2A,
                )
            ],
        )
        assert len(card.capabilities) == 0
        assert card.get_capability("nonexistent") is None

    def test_multiple_endpoints_same_type(
        self, sample_identity: AgentIdentity
    ) -> None:
        """Test card with multiple endpoints of same type."""
        card = AgentCard(
            identity=sample_identity,
            capabilities=[],
            supported_protocols=[
                SupportedProtocol(protocol=ProtocolType.A2A, version="1.0.0")
            ],
            endpoints=[
                CardEndpoint(
                    endpoint_type=EndpointType.PRIMARY,
                    url="https://api1.example.com",
                    protocol=ProtocolType.A2A,
                ),
                CardEndpoint(
                    endpoint_type=EndpointType.PRIMARY,
                    url="https://api2.example.com",
                    protocol=ProtocolType.A2A,
                ),
            ],
        )
        # Should return first primary
        primary = card.get_primary_endpoint()
        assert primary.url == "https://api1.example.com"

    def test_protocol_negotiation_result_factories(self) -> None:
        """Test protocol negotiation result factory methods."""
        success = ProtocolNegotiationResult.successful(
            request_id="req-1",
            protocol=SupportedProtocol(protocol=ProtocolType.A2A, version="1.0.0"),
            endpoint=CardEndpoint(
                endpoint_type=EndpointType.PRIMARY,
                url="https://example.com",
                protocol=ProtocolType.A2A,
            ),
        )
        assert success.success is True
        assert success.failure_reason is None

        failed = ProtocolNegotiationResult.failed(
            request_id="req-2",
            reason="No compatible protocol",
        )
        assert failed.success is False
        assert failed.failure_reason == "No compatible protocol"

    def test_validation_error_structure(self) -> None:
        """Test validation error structure."""
        error = CardValidationError(
            field="identity.agent_id",
            error_code="REQUIRED_FIELD",
            message="Agent ID is required",
        )
        assert error.field == "identity.agent_id"
        assert error.error_code == "REQUIRED_FIELD"

    def test_validation_warning_structure(self) -> None:
        """Test validation warning structure."""
        warning = CardValidationWarning(
            field="endpoints",
            warning_code="NO_PRIMARY_ENDPOINT",
            message="No primary endpoint",
            suggestion="Add a primary endpoint",
        )
        assert warning.field == "endpoints"
        assert warning.suggestion == "Add a primary endpoint"
