"""
Tests for Capability Registry & Discovery Service

Issue #55 - Phase 3: Agent-to-Agent Interface Negotiation
"""

import time

import pytest

from src.lui_simulator.agent_types import (
    AgentIdentity,
    AgentCapability,
    CapabilityType,
    SchemaDefinition,
)
from src.agent_negotiation.agent_card import (
    AgentCard,
    SupportedProtocol,
    ProtocolType,
    CardEndpoint,
    EndpointType,
)
from src.agent_negotiation.capability_registry import (
    ConstraintType,
    ConstraintOperator,
    DiscoveryConstraint,
    DiscoverySource,
    DiscoveryRequest,
    AgentMatch,
    DiscoveryResponse,
    RegistrationRequest,
    RegistrationError,
    RegistrationResponse,
    DeregistrationRequest,
    RegistryStatus,
    CapabilityStats,
    CapabilityIndex,
    CapabilityRegistry,
)


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def sample_identity() -> AgentIdentity:
    """Create a sample agent identity."""
    return AgentIdentity(
        agent_id="urn:agent:acme:assistant:1.0.0",
        name="Acme Assistant",
        version="1.0.0",
        description="A helpful assistant agent",
        provider="acme",
    )


@pytest.fixture
def sample_capability() -> AgentCapability:
    """Create a sample capability."""
    return AgentCapability.create(
        name="text-generation",
        description="Generate text based on prompts",
        capability_type=CapabilityType.ACTION,
        input_schema=SchemaDefinition.string(description="Input text"),
        output_schema=SchemaDefinition.string(description="Generated text"),
    )


@pytest.fixture
def sample_protocol() -> SupportedProtocol:
    """Create a sample protocol."""
    return SupportedProtocol(
        protocol=ProtocolType.A2A,
        version="1.0.0",
    )


@pytest.fixture
def sample_endpoint() -> CardEndpoint:
    """Create a sample endpoint."""
    return CardEndpoint(
        endpoint_type=EndpointType.PRIMARY,
        url="https://api.acme.com/agent",
        protocol=ProtocolType.A2A,
    )


@pytest.fixture
def sample_agent_card(
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
    )


@pytest.fixture
def registry() -> CapabilityRegistry:
    """Create a fresh registry."""
    return CapabilityRegistry()


def create_agent_card(
    agent_id: str,
    name: str,
    provider: str,
    capabilities: list[str],
    protocols: list[ProtocolType] | None = None,
) -> AgentCard:
    """Helper to create agent cards with specific capabilities."""
    identity = AgentIdentity(
        agent_id=agent_id,
        name=name,
        version="1.0.0",
        description=f"Agent {name}",
        provider=provider,
    )

    caps = [
        AgentCapability.create(
            name=cap_id,
            description=f"Description for {cap_id}",
            capability_type=CapabilityType.ACTION,
            input_schema=SchemaDefinition.string(),
            output_schema=SchemaDefinition.string(),
        )
        for cap_id in capabilities
    ]
    # Override capability_id to match expected values
    for cap, cap_id in zip(caps, capabilities):
        object.__setattr__(cap, "capability_id", cap_id)

    prots = [
        SupportedProtocol(protocol=p, version="1.0.0")
        for p in (protocols or [ProtocolType.A2A])
    ]

    endpoints = [
        CardEndpoint(
            endpoint_type=EndpointType.PRIMARY,
            url=f"https://api.{provider}.com/{name.lower().replace(' ', '-')}",
            protocol=prots[0].protocol if prots else ProtocolType.A2A,
        )
    ]

    return AgentCard(
        identity=identity,
        capabilities=caps,
        supported_protocols=prots,
        endpoints=endpoints,
    )


# ============================================
# Constraint Type Tests
# ============================================


class TestConstraintTypes:
    """Tests for constraint types."""

    def test_constraint_type_values(self):
        """Test ConstraintType enum values."""
        assert ConstraintType.CAPABILITY.value == "capability"
        assert ConstraintType.PROTOCOL.value == "protocol"
        assert ConstraintType.COMPLIANCE.value == "compliance"
        assert ConstraintType.TRUST_LEVEL.value == "trust_level"
        assert ConstraintType.REGION.value == "region"
        assert ConstraintType.PROVIDER.value == "provider"

    def test_constraint_operator_values(self):
        """Test ConstraintOperator enum values."""
        assert ConstraintOperator.EQUALS.value == "equals"
        assert ConstraintOperator.NOT_EQUALS.value == "not_equals"
        assert ConstraintOperator.CONTAINS.value == "contains"
        assert ConstraintOperator.IN.value == "in"
        assert ConstraintOperator.REGEX.value == "regex"

    def test_discovery_constraint_creation(self):
        """Test creating a discovery constraint."""
        constraint = DiscoveryConstraint(
            constraint_type=ConstraintType.PROVIDER,
            field="identity.provider",
            operator=ConstraintOperator.EQUALS,
            value="acme",
            weight=1.0,
            required=True,
        )

        assert constraint.constraint_type == ConstraintType.PROVIDER
        assert constraint.field == "identity.provider"
        assert constraint.operator == ConstraintOperator.EQUALS
        assert constraint.value == "acme"
        assert constraint.weight == 1.0
        assert constraint.required is True

    def test_discovery_constraint_to_dict(self):
        """Test constraint serialization."""
        constraint = DiscoveryConstraint(
            constraint_type=ConstraintType.PROTOCOL,
            field="supported_protocols",
            operator=ConstraintOperator.IN,
            value="a2a",
            weight=0.8,
            required=False,
        )

        data = constraint.to_dict()
        assert data["constraint_type"] == "protocol"
        assert data["operator"] == "in"
        assert data["weight"] == 0.8
        assert data["required"] is False


# ============================================
# Discovery Types Tests
# ============================================


class TestDiscoveryTypes:
    """Tests for discovery types."""

    def test_discovery_source_values(self):
        """Test DiscoverySource enum values."""
        assert DiscoverySource.REGISTRY.value == "registry"
        assert DiscoverySource.CACHE.value == "cache"
        assert DiscoverySource.PEER_DISCOVERY.value == "peer_discovery"
        assert DiscoverySource.LOCAL.value == "local"
        assert DiscoverySource.WELL_KNOWN.value == "well_known"

    def test_discovery_request_creation(self, sample_identity: AgentIdentity):
        """Test creating a discovery request."""
        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=["cap:text-generation", "cap:summarization"],
            max_results=5,
        )

        assert request.requester == sample_identity
        assert len(request.required_capabilities) == 2
        assert request.max_results == 5
        assert request.request_id is not None
        assert request.requested_at is not None

    def test_discovery_request_to_dict(self, sample_identity: AgentIdentity):
        """Test discovery request serialization."""
        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=["cap:text-generation"],
            optional_capabilities=["cap:translation"],
            max_results=10,
            timeout_ms=5000,
        )

        data = request.to_dict()
        assert "request_id" in data
        assert data["required_capabilities"] == ["cap:text-generation"]
        assert data["optional_capabilities"] == ["cap:translation"]
        assert data["max_results"] == 10
        assert data["timeout_ms"] == 5000

    def test_agent_match_creation(self, sample_agent_card: AgentCard):
        """Test creating an agent match."""
        match = AgentMatch(
            agent=sample_agent_card,
            match_score=0.95,
            capability_coverage=1.0,
            constraint_satisfaction=0.9,
            matched_capabilities=["cap:text-generation"],
            compatibility_notes=["Full protocol support"],
        )

        assert match.match_score == 0.95
        assert match.capability_coverage == 1.0
        assert len(match.matched_capabilities) == 1

    def test_agent_match_to_dict(self, sample_agent_card: AgentCard):
        """Test agent match serialization."""
        match = AgentMatch(
            agent=sample_agent_card,
            match_score=0.8,
            capability_coverage=0.75,
            constraint_satisfaction=0.85,
            matched_capabilities=["cap:text-generation"],
            missing_capabilities=["cap:summarization"],
        )

        data = match.to_dict()
        assert data["match_score"] == 0.8
        assert "agent" in data
        assert data["missing_capabilities"] == ["cap:summarization"]

    def test_discovery_response_creation(self, sample_agent_card: AgentCard):
        """Test creating a discovery response."""
        match = AgentMatch(
            agent=sample_agent_card,
            match_score=0.9,
            capability_coverage=1.0,
            constraint_satisfaction=1.0,
            matched_capabilities=["cap:text-generation"],
        )

        response = DiscoveryResponse(
            request_id="test-req-id",
            agents=[match],
            total_count=1,
            returned_count=1,
            discovery_time_ms=5,
            source=DiscoverySource.REGISTRY,
        )

        assert len(response.agents) == 1
        assert response.total_count == 1
        assert response.source == DiscoverySource.REGISTRY


# ============================================
# Registration Types Tests
# ============================================


class TestRegistrationTypes:
    """Tests for registration types."""

    def test_registration_request_creation(self, sample_agent_card: AgentCard):
        """Test creating a registration request."""
        request = RegistrationRequest(
            agent_card=sample_agent_card,
            ttl_seconds=7200,
            tags=["production", "us-west"],
            priority=10,
        )

        assert request.ttl_seconds == 7200
        assert "production" in request.tags
        assert request.priority == 10

    def test_registration_error_creation(self):
        """Test creating a registration error."""
        error = RegistrationError(
            error_code="INVALID_AGENT_ID",
            message="Agent ID is required",
            field="identity.agent_id",
        )

        assert error.error_code == "INVALID_AGENT_ID"
        assert error.field == "identity.agent_id"

    def test_registration_response_success(self):
        """Test creating a success response."""
        response = RegistrationResponse.success_response(
            request_id="req-123",
            registration_id="reg-456",
            expires_at="2025-12-31T23:59:59Z",
        )

        assert response.success is True
        assert response.registration_id == "reg-456"
        assert response.error is None

    def test_registration_response_error(self):
        """Test creating an error response."""
        response = RegistrationResponse.error_response(
            request_id="req-123",
            error_code="DUPLICATE_AGENT",
            message="Agent already registered",
        )

        assert response.success is False
        assert response.registration_id is None
        assert response.error is not None
        assert response.error.error_code == "DUPLICATE_AGENT"

    def test_deregistration_request_creation(self):
        """Test creating a deregistration request."""
        request = DeregistrationRequest(
            registration_id="reg-123",
            agent_id="urn:agent:acme:test:1.0.0",
            reason="Shutdown",
        )

        assert request.registration_id == "reg-123"
        assert request.reason == "Shutdown"


# ============================================
# Registry Status Tests
# ============================================


class TestRegistryStatus:
    """Tests for registry status types."""

    def test_registry_status_creation(self):
        """Test creating registry status."""
        status = RegistryStatus(
            healthy=True,
            agent_count=100,
            capability_count=50,
            last_cleanup="2025-12-30T12:00:00Z",
            uptime_seconds=86400,
            cache_hit_rate=0.85,
        )

        assert status.healthy is True
        assert status.agent_count == 100
        assert status.cache_hit_rate == 0.85

    def test_capability_stats_creation(self):
        """Test creating capability stats."""
        stats = CapabilityStats(
            capability_id="cap:text-generation",
            agent_count=25,
            average_version="1.2.0",
            protocols=[ProtocolType.A2A, ProtocolType.MCP],
        )

        assert stats.agent_count == 25
        assert len(stats.protocols) == 2

    def test_capability_index_creation(self):
        """Test creating capability index."""
        index = CapabilityIndex(
            capability_id="cap:summarization",
            agent_ids=["agent-1", "agent-2", "agent-3"],
            last_updated="2025-12-30T12:00:00Z",
        )

        assert len(index.agent_ids) == 3


# ============================================
# Capability Registry Tests
# ============================================


class TestCapabilityRegistry:
    """Tests for the capability registry."""

    def test_registry_creation(self, registry: CapabilityRegistry):
        """Test creating a registry."""
        status = registry.get_status()
        assert status.healthy is True
        assert status.agent_count == 0
        assert status.capability_count == 0

    def test_register_agent(
        self, registry: CapabilityRegistry, sample_agent_card: AgentCard
    ):
        """Test registering an agent."""
        response = registry.register(sample_agent_card, ttl_seconds=3600)

        assert response.success is True
        assert response.registration_id is not None
        assert response.expires_at is not None

        status = registry.get_status()
        assert status.agent_count == 1

    def test_register_duplicate_updates(
        self, registry: CapabilityRegistry, sample_agent_card: AgentCard
    ):
        """Test that duplicate registration updates existing entry."""
        response1 = registry.register(sample_agent_card, ttl_seconds=3600)
        response2 = registry.register(sample_agent_card, ttl_seconds=7200)

        assert response1.success is True
        assert response2.success is True
        # Different registration IDs
        assert response1.registration_id != response2.registration_id

        status = registry.get_status()
        # Only one agent
        assert status.agent_count == 1

    def test_register_invalid_agent(self, registry: CapabilityRegistry):
        """Test registering an agent with invalid ID."""
        identity = AgentIdentity(
            agent_id="",  # Invalid empty ID
            name="Invalid Agent",
            version="1.0.0",
            description="Invalid",
        )
        card = AgentCard(
            identity=identity,
            capabilities=[],
            supported_protocols=[
                SupportedProtocol(protocol=ProtocolType.A2A, version="1.0.0")
            ],
            endpoints=[
                CardEndpoint(
                    endpoint_type=EndpointType.PRIMARY,
                    url="https://example.com",
                    protocol=ProtocolType.A2A,
                )
            ],
        )

        response = registry.register(card)
        assert response.success is False
        assert response.error is not None
        assert response.error.error_code == "INVALID_AGENT_ID"

    def test_deregister_agent(
        self, registry: CapabilityRegistry, sample_agent_card: AgentCard
    ):
        """Test deregistering an agent."""
        reg_response = registry.register(sample_agent_card)
        assert reg_response.success is True

        dereg_response = registry.deregister(
            registration_id=reg_response.registration_id,
            agent_id=sample_agent_card.identity.agent_id,
        )
        assert dereg_response.success is True

        status = registry.get_status()
        assert status.agent_count == 0

    def test_deregister_not_found(self, registry: CapabilityRegistry):
        """Test deregistering a non-existent agent."""
        response = registry.deregister(
            registration_id="nonexistent",
            agent_id="urn:agent:test:unknown:1.0.0",
        )
        assert response.success is False
        assert "not found" in response.message.lower()

    def test_deregister_wrong_agent_id(
        self, registry: CapabilityRegistry, sample_agent_card: AgentCard
    ):
        """Test deregistering with wrong agent ID."""
        reg_response = registry.register(sample_agent_card)

        dereg_response = registry.deregister(
            registration_id=reg_response.registration_id,
            agent_id="urn:agent:wrong:id:1.0.0",
        )
        assert dereg_response.success is False
        assert "does not match" in dereg_response.message.lower()

    def test_update_registration(
        self, registry: CapabilityRegistry, sample_agent_card: AgentCard
    ):
        """Test updating a registration."""
        reg_response = registry.register(sample_agent_card, ttl_seconds=3600)

        # Create updated card
        updated_identity = AgentIdentity(
            agent_id=sample_agent_card.identity.agent_id,
            name="Updated Name",
            version="1.1.0",
            description="Updated description",
            provider=sample_agent_card.identity.provider,
        )
        updated_card = AgentCard(
            identity=updated_identity,
            capabilities=sample_agent_card.capabilities,
            supported_protocols=sample_agent_card.supported_protocols,
            endpoints=sample_agent_card.endpoints,
        )

        update_response = registry.update(
            registration_id=reg_response.registration_id,
            agent_card=updated_card,
            extend_ttl=True,
            new_ttl_seconds=7200,
        )

        assert update_response.success is True

        # Verify update
        agent = registry.get_agent(sample_agent_card.identity.agent_id)
        assert agent is not None
        assert agent.identity.name == "Updated Name"
        assert agent.identity.version == "1.1.0"

    def test_get_agent(
        self, registry: CapabilityRegistry, sample_agent_card: AgentCard
    ):
        """Test getting an agent by ID."""
        registry.register(sample_agent_card)

        agent = registry.get_agent(sample_agent_card.identity.agent_id)
        assert agent is not None
        assert agent.identity.name == sample_agent_card.identity.name

    def test_get_agent_not_found(self, registry: CapabilityRegistry):
        """Test getting a non-existent agent."""
        agent = registry.get_agent("urn:agent:unknown:test:1.0.0")
        assert agent is None

    def test_list_capabilities(self, registry: CapabilityRegistry):
        """Test listing registered capabilities."""
        card1 = create_agent_card(
            "urn:agent:acme:agent1:1.0.0",
            "Agent 1",
            "acme",
            ["cap:text-gen", "cap:summarize"],
        )
        card2 = create_agent_card(
            "urn:agent:acme:agent2:1.0.0",
            "Agent 2",
            "acme",
            ["cap:translate", "cap:summarize"],
        )

        registry.register(card1)
        registry.register(card2)

        capabilities = registry.list_capabilities()
        assert "cap:text-gen" in capabilities
        assert "cap:summarize" in capabilities
        assert "cap:translate" in capabilities

    def test_list_agents(self, registry: CapabilityRegistry):
        """Test listing registered agents."""
        card1 = create_agent_card(
            "urn:agent:acme:agent1:1.0.0", "Agent 1", "acme", ["cap:test"]
        )
        card2 = create_agent_card(
            "urn:agent:acme:agent2:1.0.0", "Agent 2", "acme", ["cap:test"]
        )

        registry.register(card1)
        registry.register(card2)

        agents = registry.list_agents()
        assert len(agents) == 2
        assert "urn:agent:acme:agent1:1.0.0" in agents
        assert "urn:agent:acme:agent2:1.0.0" in agents

    def test_clear_registry(
        self, registry: CapabilityRegistry, sample_agent_card: AgentCard
    ):
        """Test clearing the registry."""
        registry.register(sample_agent_card)
        assert registry.get_status().agent_count == 1

        registry.clear()
        assert registry.get_status().agent_count == 0
        assert registry.get_status().capability_count == 0


# ============================================
# Discovery Tests
# ============================================


class TestDiscovery:
    """Tests for agent discovery."""

    def test_discover_by_capability(
        self, registry: CapabilityRegistry, sample_identity: AgentIdentity
    ):
        """Test discovering agents by capability."""
        # Register agents with different capabilities
        card1 = create_agent_card(
            "urn:agent:acme:agent1:1.0.0",
            "Agent 1",
            "acme",
            ["cap:text-gen", "cap:summarize"],
        )
        card2 = create_agent_card(
            "urn:agent:acme:agent2:1.0.0",
            "Agent 2",
            "acme",
            ["cap:translate"],
        )
        card3 = create_agent_card(
            "urn:agent:acme:agent3:1.0.0",
            "Agent 3",
            "acme",
            ["cap:text-gen", "cap:translate"],
        )

        registry.register(card1)
        registry.register(card2)
        registry.register(card3)

        # Discover agents with text-gen capability
        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=["cap:text-gen"],
            max_results=10,
        )

        response = registry.discover(request)

        assert response.total_count == 2
        agent_ids = [m.agent.identity.agent_id for m in response.agents]
        assert "urn:agent:acme:agent1:1.0.0" in agent_ids
        assert "urn:agent:acme:agent3:1.0.0" in agent_ids
        assert "urn:agent:acme:agent2:1.0.0" not in agent_ids

    def test_discover_multiple_capabilities(
        self, registry: CapabilityRegistry, sample_identity: AgentIdentity
    ):
        """Test discovering agents with multiple required capabilities."""
        card1 = create_agent_card(
            "urn:agent:acme:agent1:1.0.0",
            "Agent 1",
            "acme",
            ["cap:text-gen", "cap:summarize"],
        )
        card2 = create_agent_card(
            "urn:agent:acme:agent2:1.0.0",
            "Agent 2",
            "acme",
            ["cap:text-gen"],
        )

        registry.register(card1)
        registry.register(card2)

        # Require both capabilities
        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=["cap:text-gen", "cap:summarize"],
            max_results=10,
        )

        response = registry.discover(request)

        assert response.total_count == 1
        assert response.agents[0].agent.identity.agent_id == "urn:agent:acme:agent1:1.0.0"
        assert response.agents[0].capability_coverage == 1.0

    def test_discover_with_optional_capabilities(
        self, registry: CapabilityRegistry, sample_identity: AgentIdentity
    ):
        """Test discovering with optional capabilities."""
        card1 = create_agent_card(
            "urn:agent:acme:agent1:1.0.0",
            "Agent 1",
            "acme",
            ["cap:text-gen", "cap:translate"],
        )
        card2 = create_agent_card(
            "urn:agent:acme:agent2:1.0.0",
            "Agent 2",
            "acme",
            ["cap:text-gen"],
        )

        registry.register(card1)
        registry.register(card2)

        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=["cap:text-gen"],
            optional_capabilities=["cap:translate"],
            max_results=10,
        )

        response = registry.discover(request)

        assert response.total_count == 2
        # Agent 1 should score higher due to optional capability
        assert response.agents[0].agent.identity.agent_id == "urn:agent:acme:agent1:1.0.0"
        assert response.agents[0].match_score > response.agents[1].match_score

    def test_discover_with_constraints(
        self, registry: CapabilityRegistry, sample_identity: AgentIdentity
    ):
        """Test discovering with constraints."""
        card1 = create_agent_card(
            "urn:agent:acme:agent1:1.0.0",
            "Agent 1",
            "acme",
            ["cap:text-gen"],
        )
        card2 = create_agent_card(
            "urn:agent:other:agent2:1.0.0",
            "Agent 2",
            "other",
            ["cap:text-gen"],
        )

        registry.register(card1)
        registry.register(card2)

        # Only agents from "acme" provider
        constraint = DiscoveryConstraint(
            constraint_type=ConstraintType.PROVIDER,
            field="identity.provider",
            operator=ConstraintOperator.EQUALS,
            value="acme",
            required=True,
        )

        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=["cap:text-gen"],
            constraints=[constraint],
            max_results=10,
        )

        response = registry.discover(request)

        assert response.total_count == 1
        assert response.agents[0].agent.identity.provider == "acme"

    def test_discover_max_results(
        self, registry: CapabilityRegistry, sample_identity: AgentIdentity
    ):
        """Test max_results limit."""
        # Register 10 agents
        for i in range(10):
            card = create_agent_card(
                f"urn:agent:acme:agent{i}:1.0.0",
                f"Agent {i}",
                "acme",
                ["cap:text-gen"],
            )
            registry.register(card)

        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=["cap:text-gen"],
            max_results=3,
        )

        response = registry.discover(request)

        assert response.total_count == 10
        assert response.returned_count == 3
        assert len(response.agents) == 3

    def test_discover_empty_registry(
        self, registry: CapabilityRegistry, sample_identity: AgentIdentity
    ):
        """Test discovery on empty registry."""
        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=["cap:text-gen"],
            max_results=10,
        )

        response = registry.discover(request)

        assert response.total_count == 0
        assert len(response.agents) == 0

    def test_discover_no_matching_capabilities(
        self, registry: CapabilityRegistry, sample_identity: AgentIdentity
    ):
        """Test discovery when no agents match."""
        card = create_agent_card(
            "urn:agent:acme:agent1:1.0.0",
            "Agent 1",
            "acme",
            ["cap:translate"],
        )
        registry.register(card)

        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=["cap:text-gen"],
            max_results=10,
        )

        response = registry.discover(request)

        assert response.total_count == 0

    def test_discover_scores_sorted(
        self, registry: CapabilityRegistry, sample_identity: AgentIdentity
    ):
        """Test that results are sorted by score descending."""
        card1 = create_agent_card(
            "urn:agent:acme:agent1:1.0.0",
            "Agent 1",
            "acme",
            ["cap:text-gen"],
        )
        card2 = create_agent_card(
            "urn:agent:acme:agent2:1.0.0",
            "Agent 2",
            "acme",
            ["cap:text-gen", "cap:summarize", "cap:translate"],
        )

        registry.register(card1)
        registry.register(card2)

        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=["cap:text-gen"],
            optional_capabilities=["cap:summarize", "cap:translate"],
            max_results=10,
        )

        response = registry.discover(request)

        scores = [m.match_score for m in response.agents]
        assert scores == sorted(scores, reverse=True)


# ============================================
# Performance Tests
# ============================================


class TestPerformance:
    """Performance tests for the registry."""

    def test_register_1000_agents(self, registry: CapabilityRegistry):
        """Test registering 1000 agents."""
        start = time.time()

        for i in range(1000):
            card = create_agent_card(
                f"urn:agent:acme:agent{i}:1.0.0",
                f"Agent {i}",
                "acme",
                [f"cap:type{i % 10}", f"cap:common{i % 5}"],
            )
            registry.register(card)

        elapsed = (time.time() - start) * 1000

        assert registry.get_status().agent_count == 1000
        # Should complete in reasonable time
        assert elapsed < 5000  # 5 seconds

    def test_discover_in_1000_agents(
        self, registry: CapabilityRegistry, sample_identity: AgentIdentity
    ):
        """Test discovery performance with 1000 agents."""
        # Register 1000 agents
        for i in range(1000):
            card = create_agent_card(
                f"urn:agent:acme:agent{i}:1.0.0",
                f"Agent {i}",
                "acme",
                [f"cap:type{i % 10}", "cap:common"],
            )
            registry.register(card)

        # Discover agents with common capability
        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=["cap:common"],
            max_results=100,
        )

        response = registry.discover(request)

        # Should find all 1000 agents (with cap:common)
        assert response.total_count == 1000
        # Discovery should be under 100ms
        assert response.discovery_time_ms < 100


# ============================================
# TTL Expiration Tests
# ============================================


class TestTTLExpiration:
    """Tests for TTL-based expiration."""

    def test_expired_agent_not_discoverable(
        self, registry: CapabilityRegistry, sample_identity: AgentIdentity
    ):
        """Test that expired agents are not returned in discovery."""
        card = create_agent_card(
            "urn:agent:acme:agent1:1.0.0",
            "Agent 1",
            "acme",
            ["cap:text-gen"],
        )

        # Register with very short TTL
        registry.register(card, ttl_seconds=1)

        # Wait for expiration
        time.sleep(1.1)

        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=["cap:text-gen"],
            max_results=10,
        )

        response = registry.discover(request)
        assert response.total_count == 0

    def test_expired_agent_not_retrievable(self, registry: CapabilityRegistry):
        """Test that expired agents are not returned by get_agent."""
        card = create_agent_card(
            "urn:agent:acme:agent1:1.0.0",
            "Agent 1",
            "acme",
            ["cap:text-gen"],
        )

        registry.register(card, ttl_seconds=1)

        # Agent should be retrievable immediately
        agent = registry.get_agent("urn:agent:acme:agent1:1.0.0")
        assert agent is not None

        # Wait for expiration
        time.sleep(1.1)

        # Agent should no longer be retrievable
        agent = registry.get_agent("urn:agent:acme:agent1:1.0.0")
        assert agent is None


# ============================================
# Capability Stats Tests
# ============================================


class TestCapabilityStats:
    """Tests for capability statistics."""

    def test_get_capability_stats(self, registry: CapabilityRegistry):
        """Test getting capability statistics."""
        card1 = create_agent_card(
            "urn:agent:acme:agent1:1.0.0",
            "Agent 1",
            "acme",
            ["cap:text-gen"],
            [ProtocolType.A2A],
        )
        card2 = create_agent_card(
            "urn:agent:acme:agent2:1.0.0",
            "Agent 2",
            "acme",
            ["cap:text-gen"],
            [ProtocolType.MCP],
        )

        registry.register(card1)
        registry.register(card2)

        stats = registry.get_capability_stats("cap:text-gen")
        assert stats is not None
        assert stats.agent_count == 2
        assert len(stats.protocols) == 2

    def test_get_capability_stats_not_found(self, registry: CapabilityRegistry):
        """Test getting stats for non-existent capability."""
        stats = registry.get_capability_stats("cap:nonexistent")
        assert stats is None


# ============================================
# Edge Cases
# ============================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_capabilities_discovery(
        self, registry: CapabilityRegistry, sample_identity: AgentIdentity
    ):
        """Test discovery with empty required capabilities."""
        card = create_agent_card(
            "urn:agent:acme:agent1:1.0.0",
            "Agent 1",
            "acme",
            ["cap:text-gen"],
        )
        registry.register(card)

        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=[],
            max_results=10,
        )

        response = registry.discover(request)
        # Should return all agents
        assert response.total_count == 1

    def test_constraint_not_equals(
        self, registry: CapabilityRegistry, sample_identity: AgentIdentity
    ):
        """Test NOT_EQUALS constraint operator."""
        card1 = create_agent_card(
            "urn:agent:acme:agent1:1.0.0", "Agent 1", "acme", ["cap:test"]
        )
        card2 = create_agent_card(
            "urn:agent:other:agent2:1.0.0", "Agent 2", "other", ["cap:test"]
        )

        registry.register(card1)
        registry.register(card2)

        constraint = DiscoveryConstraint(
            constraint_type=ConstraintType.PROVIDER,
            field="identity.provider",
            operator=ConstraintOperator.NOT_EQUALS,
            value="acme",
            required=True,
        )

        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=["cap:test"],
            constraints=[constraint],
            max_results=10,
        )

        response = registry.discover(request)

        assert response.total_count == 1
        assert response.agents[0].agent.identity.provider == "other"

    def test_constraint_contains(
        self, registry: CapabilityRegistry, sample_identity: AgentIdentity
    ):
        """Test CONTAINS constraint operator."""
        card1 = create_agent_card(
            "urn:agent:acme:agent1:1.0.0",
            "Agent Alpha",
            "acme",
            ["cap:test"],
        )
        card2 = create_agent_card(
            "urn:agent:acme:agent2:1.0.0",
            "Agent Beta",
            "acme",
            ["cap:test"],
        )

        registry.register(card1)
        registry.register(card2)

        constraint = DiscoveryConstraint(
            constraint_type=ConstraintType.PROVIDER,
            field="identity.name",
            operator=ConstraintOperator.CONTAINS,
            value="Alpha",
            required=True,
        )

        request = DiscoveryRequest(
            requester=sample_identity,
            required_capabilities=["cap:test"],
            constraints=[constraint],
            max_results=10,
        )

        response = registry.discover(request)

        assert response.total_count == 1
        assert "Alpha" in response.agents[0].agent.identity.name

    def test_serialization_round_trip(self, sample_agent_card: AgentCard):
        """Test that types serialize and deserialize correctly."""
        match = AgentMatch(
            agent=sample_agent_card,
            match_score=0.95,
            capability_coverage=1.0,
            constraint_satisfaction=0.9,
            matched_capabilities=["cap:text-generation"],
        )

        data = match.to_dict()

        # Verify essential fields preserved
        assert data["match_score"] == 0.95
        assert data["capability_coverage"] == 1.0
        assert "agent" in data
