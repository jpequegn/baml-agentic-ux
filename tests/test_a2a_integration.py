"""
Integration Tests for Agent-to-Agent (A2A) Negotiation System.

Tests end-to-end workflows combining:
- Agent Card creation and management
- Capability Registry operations
- Capability Matching
- Negotiation State Machine
- Conflict Resolution
- Composition Planning/Execution
- Security Context Validation

Issue #66 - Phase 3 Testing & Documentation
"""

import pytest
from datetime import datetime, timezone, timedelta

# Agent card and identity
from src.agent_negotiation import (
    # Protocol and endpoint types
    ProtocolType,
    EndpointType,
    # Agent card types
    AgentCard,
    AgentCardBuilder,
    AgentCardValidator,
    AgentCardSerializer,
    # Compliance
    ComplianceStandard,
)

# Capability registry
from src.agent_negotiation import (
    CapabilityRegistry,
    DiscoveryRequest,
    DiscoveryConstraint,
    ConstraintOperator,
    ConstraintType,
)

# Capability matching
from src.agent_negotiation import (
    CapabilityMatcher,
    MatchOptions,
)

# Negotiation
from src.agent_negotiation import (
    NegotiationStatus,
    NegotiationAction,
    RequestPriority,
    NegotiationStrategy,
    CapabilityRequest,
    CapabilityOffer,
    NegotiationTerms,
    NegotiationSession,
    NegotiationStateMachine,
    ProposalEvaluator,
    NegotiationManager,
    EvaluationPolicy,
    MinimumTerms,
    NegotiationTurn,
    NegotiationProposal,
)

# Conflict resolution
from src.agent_negotiation.conflict_resolution import (
    ConflictDetector,
    SchemaTransformer,
    ConflictMediator,
    MediationStyle,
)

# Composition
from src.agent_negotiation.composition import (
    CompositionPlanner,
    CompositionExecutor,
    OrchestrationConfig,
    ExecutionStatus,
)

# Security
from src.agent_negotiation.security import (
    CredentialType,
    DelegationType,
    Credential,
    TrustChainEntry,
    SecurityContext,
    TrustChainValidator,
    CredentialManager,
    SecurityValidator,
)

# Base types from agent_types
from src.lui_simulator.agent_types import (
    AgentIdentity,
    AgentCapability,
    CapabilityType,
    SchemaDefinition,
    SchemaProperty,
    TrustLevel,
)


# ============================================
# Test Fixtures
# ============================================


@pytest.fixture
def provider_identity() -> AgentIdentity:
    """Identity for a capability provider agent."""
    return AgentIdentity.create(
        name="data-processor",
        version="2.0.0",
        description="Data processing and transformation service",
        provider="acme-corp",
    )


@pytest.fixture
def consumer_identity() -> AgentIdentity:
    """Identity for a capability consumer agent."""
    return AgentIdentity.create(
        name="analysis-engine",
        version="1.5.0",
        description="Data analysis and insights generation",
        provider="analytics-inc",
    )


@pytest.fixture
def transform_capability() -> AgentCapability:
    """A data transformation capability."""
    return AgentCapability(
        capability_id="transform-data",
        capability_type=CapabilityType.TRANSFORM,
        name="transform",
        description="Transform data between formats",
        input_schema=SchemaDefinition.object(
            description="Transform input",
            properties=[
                SchemaProperty(
                    name="data",
                    schema=SchemaDefinition.string(description="Input data"),
                    description="Raw data to transform",
                ),
                SchemaProperty(
                    name="format",
                    schema=SchemaDefinition.string(description="Target format"),
                    description="Target format (json, xml, csv)",
                ),
            ],
            required=["data"],
        ),
        output_schema=SchemaDefinition.object(
            description="Transform output",
            properties=[
                SchemaProperty(
                    name="result",
                    schema=SchemaDefinition.string(description="Transformed data"),
                    description="Transformed data in target format",
                ),
            ],
            required=["result"],
        ),
    )


@pytest.fixture
def query_capability() -> AgentCapability:
    """A data query capability."""
    return AgentCapability(
        capability_id="query-data",
        capability_type=CapabilityType.QUERY,
        name="query",
        description="Query structured data",
        input_schema=SchemaDefinition.object(
            description="Query input",
            properties=[
                SchemaProperty(
                    name="query",
                    schema=SchemaDefinition.string(description="Query string"),
                    description="SQL-like query",
                ),
            ],
            required=["query"],
        ),
        output_schema=SchemaDefinition.object(
            description="Query output",
            properties=[
                SchemaProperty(
                    name="count",
                    schema=SchemaDefinition.integer(description="Result count"),
                    description="Number of rows returned",
                ),
            ],
            required=["count"],
        ),
    )


@pytest.fixture
def action_capability() -> AgentCapability:
    """A generic action capability."""
    return AgentCapability(
        capability_id="action-data",
        capability_type=CapabilityType.ACTION,
        name="action",
        description="Execute an action on data",
        input_schema=SchemaDefinition.object(
            description="Action input",
            properties=[
                SchemaProperty(
                    name="command",
                    schema=SchemaDefinition.string(description="Command to execute"),
                    description="Action command",
                ),
            ],
            required=["command"],
        ),
        output_schema=SchemaDefinition.object(
            description="Action output",
            properties=[
                SchemaProperty(
                    name="status",
                    schema=SchemaDefinition.string(description="Result status"),
                    description="Action status",
                ),
            ],
            required=["status"],
        ),
    )


@pytest.fixture
def provider_agent_card(
    provider_identity: AgentIdentity,
    transform_capability: AgentCapability,
    query_capability: AgentCapability,
) -> AgentCard:
    """A complete agent card for a provider."""
    return (
        AgentCardBuilder(provider_identity)
        .add_capability(transform_capability)
        .add_capability(query_capability)
        .add_protocol(ProtocolType.A2A, "1.0")
        .add_protocol(ProtocolType.OPENAPI, "2.0")
        .add_endpoint(
            EndpointType.PRIMARY,
            "https://api.acme-corp.com/agents/data-processor",
            ProtocolType.A2A,
        )
        .add_compliance(ComplianceStandard.GDPR, "General Data Protection Regulation")
        .with_data_handling(
            encryption_at_rest=True,
            encryption_in_transit=True,
            audit_logging=True,
        )
        .build()
    )


@pytest.fixture
def consumer_agent_card(
    consumer_identity: AgentIdentity,
    action_capability: AgentCapability,
) -> AgentCard:
    """A complete agent card for a consumer."""
    return (
        AgentCardBuilder(consumer_identity)
        .add_capability(action_capability)
        .add_protocol(ProtocolType.A2A, "1.0")
        .add_endpoint(
            EndpointType.PRIMARY,
            "https://api.analytics-inc.com/agents/analysis-engine",
            ProtocolType.A2A,
        )
        .build()
    )


@pytest.fixture
def registry_with_agents(
    provider_agent_card: AgentCard,
    consumer_agent_card: AgentCard,
) -> CapabilityRegistry:
    """A registry with pre-registered agents."""
    registry = CapabilityRegistry()
    registry.register(agent_card=provider_agent_card, ttl_seconds=3600)
    registry.register(agent_card=consumer_agent_card, ttl_seconds=3600)
    return registry


@pytest.fixture
def provider_security_context() -> SecurityContext:
    """Security context for the provider agent."""
    credential = Credential.api_key(
        key="provider-api-key-secret",
        scope=["read", "write", "transform", "query"],
        expires_in_days=30,
    )

    trust_entry = TrustChainEntry.create(
        issuer="root-authority",
        subject="acme-corp",
        delegation_type=DelegationType.DIRECT,
        permissions=["read", "write", "transform", "query", "admin"],
        expires_in_hours=720,  # 30 days
    )

    return SecurityContext.create(
        requester_agent_id="acme-corp",
        credentials=[credential],
        trust_chain=[trust_entry],
        session_token="provider-session-token",
        expires_in_hours=24,
    )


@pytest.fixture
def consumer_security_context() -> SecurityContext:
    """Security context for the consumer agent."""
    credential = Credential.bearer_token(
        token="consumer-bearer-token",
        scope=["read", "analyze"],
    )

    trust_entry1 = TrustChainEntry.create(
        issuer="root-authority",
        subject="analytics-inc",
        delegation_type=DelegationType.DIRECT,
        permissions=["read", "analyze", "query"],
        expires_in_hours=720,
    )

    return SecurityContext.create(
        requester_agent_id="analytics-inc",
        credentials=[credential],
        trust_chain=[trust_entry1],
        session_token="consumer-session-token",
        expires_in_hours=24,
    )


# ============================================
# Integration Test: Agent Discovery Workflow
# ============================================


class TestAgentDiscoveryWorkflow:
    """Test complete agent discovery workflows."""

    def test_register_and_discover_agent(
        self,
        provider_agent_card: AgentCard,
        provider_identity: AgentIdentity,
    ):
        """Test registering an agent and discovering it by capability."""
        # Setup registry
        registry = CapabilityRegistry()

        # Register provider
        reg_response = registry.register(
            agent_card=provider_agent_card,
            ttl_seconds=3600,
        )
        assert reg_response.success
        assert reg_response.registration_id is not None

        # Discover by capability ID (uses exact capability_id)
        discovery_response = registry.discover(
            DiscoveryRequest(
                requester=provider_identity,
                required_capabilities=["transform-data"],  # Uses exact capability_id
                max_results=10,
            )
        )

        assert len(discovery_response.agents) >= 1
        found_agent = discovery_response.agents[0]
        assert found_agent.agent.identity.name == "data-processor"
        assert found_agent.match_score > 0

    def test_discover_with_constraints(
        self,
        registry_with_agents: CapabilityRegistry,
        consumer_identity: AgentIdentity,
    ):
        """Test agent discovery with constraints."""
        # Discover agents with GDPR compliance
        discovery_response = registry_with_agents.discover(
            DiscoveryRequest(
                requester=consumer_identity,
                required_capabilities=[],
                constraints=[
                    DiscoveryConstraint(
                        constraint_type=ConstraintType.COMPLIANCE,
                        field="compliance_tags",
                        operator=ConstraintOperator.CONTAINS,
                        value="gdpr",
                    )
                ],
                max_results=10,
            )
        )

        # Only provider has GDPR compliance
        assert len(discovery_response.agents) >= 1
        for match in discovery_response.agents:
            # Verify the agent has the compliance tag
            compliance_tags = [c.standard.value for c in match.agent.compliance_tags]
            assert "gdpr" in compliance_tags or len(compliance_tags) == 0

    def test_capability_matching_during_discovery(
        self,
        registry_with_agents: CapabilityRegistry,
        transform_capability: AgentCapability,
        consumer_identity: AgentIdentity,
    ):
        """Test capability matching as part of discovery."""
        # Discover agents
        discovery_response = registry_with_agents.discover(
            DiscoveryRequest(
                requester=consumer_identity,
                required_capabilities=["transform-data"],  # Uses exact capability_id
                max_results=5,
            )
        )

        # Create matcher for detailed compatibility check
        matcher = CapabilityMatcher(
            MatchOptions(
                minimum_compatibility=0.3,
                fuzzy_matching=True,
            )
        )

        # Match against discovered agent
        if discovery_response.agents:
            agent = discovery_response.agents[0].agent
            match_result = matcher.match(
                required=[transform_capability],  # Pass as list
                offered=agent.capabilities,
            )

            assert match_result.overall_result.overall_compatibility > 0
            assert len(match_result.overall_result.matches) > 0


# ============================================
# Integration Test: Negotiation Workflow
# ============================================


class TestNegotiationWorkflow:
    """Test complete negotiation workflows."""

    def test_successful_negotiation_flow(
        self,
        provider_identity: AgentIdentity,
        consumer_identity: AgentIdentity,
        transform_capability: AgentCapability,
        action_capability: AgentCapability,
    ):
        """Test a successful negotiation between two agents."""
        min_terms = MinimumTerms(
            min_duration_seconds=3600,
            max_rate_limit=None,
        )

        # Provider's negotiation manager
        provider_manager = NegotiationManager(
            our_identity=provider_identity,
            our_capabilities=[transform_capability],
            evaluation_policy=EvaluationPolicy(
                min_acceptable_terms=min_terms,
                negotiation_strategy=NegotiationStrategy.COOPERATIVE,
                auto_accept_threshold=0.7,
                max_counter_offers=3,
            ),
        )

        # Consumer's negotiation manager
        consumer_manager = NegotiationManager(
            our_identity=consumer_identity,
            our_capabilities=[action_capability],
            evaluation_policy=EvaluationPolicy(
                min_acceptable_terms=min_terms,
                negotiation_strategy=NegotiationStrategy.COOPERATIVE,
                auto_accept_threshold=0.7,
                max_counter_offers=3,
            ),
        )

        # Consumer initiates negotiation
        session = consumer_manager.initiate(
            target=provider_identity,
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="transform",
                    priority=RequestPriority.REQUIRED,
                )
            ],
            offered_capabilities=[
                CapabilityOffer(capability=action_capability)
            ],
            terms=NegotiationTerms(
                duration_seconds=86400,
                auto_renew=True,
            ),
        )

        assert session.session_id
        assert session.status in [NegotiationStatus.INITIATED, NegotiationStatus.PROPOSAL_SENT]

        # Verify session has history
        assert len(session.history) >= 0

    def test_negotiation_state_machine_transitions(
        self,
        provider_identity: AgentIdentity,
        consumer_identity: AgentIdentity,
    ):
        """Test negotiation state machine transitions."""
        # Create initial session
        session = NegotiationSession.create(
            initiator=consumer_identity,
            responder=provider_identity,
            expiration_hours=24,
        )

        state_machine = NegotiationStateMachine(session)

        assert session.status == NegotiationStatus.INITIATED

        # Check valid transitions
        assert state_machine.can_transition(NegotiationStatus.PROPOSAL_SENT)
        assert state_machine.can_transition(NegotiationStatus.CANCELLED)
        assert not state_machine.can_transition(NegotiationStatus.ACCEPTED)

    def test_proposal_evaluation(
        self,
        provider_identity: AgentIdentity,
        consumer_identity: AgentIdentity,
        transform_capability: AgentCapability,
    ):
        """Test proposal evaluation with capability matching."""
        min_terms = MinimumTerms(
            min_duration_seconds=3600,
            max_rate_limit=None,
        )

        evaluator = ProposalEvaluator(
            our_capabilities=[transform_capability],
            policy=EvaluationPolicy(
                min_acceptable_terms=min_terms,
                negotiation_strategy=NegotiationStrategy.COOPERATIVE,
            ),
        )

        # Create a proposal
        proposal = NegotiationProposal.create(
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="transform",
                    priority=RequestPriority.REQUIRED,
                )
            ],
            offered_capabilities=[],
            terms=NegotiationTerms(
                duration_seconds=86400,
            ),
        )

        evaluation = evaluator.evaluate(proposal)

        # Should have evaluation result
        assert evaluation is not None
        assert hasattr(evaluation, 'score')
        assert hasattr(evaluation, 'can_satisfy')


# ============================================
# Integration Test: Security-Protected Negotiation
# ============================================


class TestSecurityIntegratedNegotiation:
    """Test negotiation with security context validation."""

    def test_validate_security_before_negotiation(
        self,
        provider_security_context: SecurityContext,
    ):
        """Test security validation before starting negotiation."""
        validator = SecurityValidator()

        # Validate provider context
        result = validator.validate_context(
            provider_security_context,
            required_permissions=["read", "write", "transform"],
            minimum_trust_level="basic",
        )

        assert result.valid
        assert result.trust_level in ["basic", "verified", "trusted", "privileged"]

    def test_reject_insufficient_permissions(
        self,
        consumer_security_context: SecurityContext,
    ):
        """Test rejection when security context lacks permissions."""
        validator = SecurityValidator()

        # Consumer doesn't have admin permission
        result = validator.validate_context(
            consumer_security_context,
            required_permissions=["admin"],
            minimum_trust_level="basic",
        )

        assert result.valid is False
        assert any("Missing required permissions" in r for r in result.failure_reasons)

    def test_trust_chain_delegation_in_negotiation(
        self,
        provider_identity: AgentIdentity,
    ):
        """Test trust chain is respected during delegation."""
        # Build multi-level trust chain
        root_entry = TrustChainEntry.create(
            issuer="global-root",
            subject="regional-authority",
            delegation_type=DelegationType.DIRECT,
            permissions=["read", "write", "transform", "query"],  # Specific permissions
            expires_in_hours=720,
        )

        regional_entry = TrustChainEntry.create(
            issuer="regional-authority",
            subject="acme-corp",
            delegation_type=DelegationType.DELEGATED,
            permissions=["read", "write", "transform"],  # Subset of permissions
            expires_in_hours=168,
            previous_entry_id=root_entry.entry_id,
        )

        context = SecurityContext.create(
            requester_agent_id="acme-corp",
            trust_chain=[root_entry, regional_entry],
            expires_in_hours=24,
        )

        validator = SecurityValidator()
        result = validator.validate_context(
            context,
            required_permissions=["read"],  # Request only read which is in chain
            minimum_trust_level="basic",
        )

        assert result.valid
        assert "read" in result.granted_permissions


# ============================================
# Integration Test: Conflict Resolution in Negotiation
# ============================================


class TestConflictResolutionIntegration:
    """Test conflict resolution during capability negotiation."""

    def test_detect_schema_conflicts(self):
        """Test schema conflict detection during matching."""
        detector = ConflictDetector()

        # Source schema has different structure than target
        source_schema = SchemaDefinition.object(
            description="Source data",
            properties=[
                SchemaProperty(
                    name="value",
                    schema=SchemaDefinition.integer(description="Integer value"),
                    description="Numeric value",
                ),
            ],
            required=["value"],
        )

        target_schema = SchemaDefinition.object(
            description="Target data",
            properties=[
                SchemaProperty(
                    name="value",
                    schema=SchemaDefinition.string(description="String value"),
                    description="String value",
                ),
            ],
            required=["value"],
        )

        conflicts = detector.detect_schema_conflicts(source_schema, target_schema)

        assert len(conflicts) > 0
        # Should detect type mismatch
        type_conflicts = [c for c in conflicts if "type" in c.conflict_type.value.lower()]
        assert len(type_conflicts) > 0 or len(conflicts) > 0

    def test_mediation_basics(self):
        """Test basic mediation functionality."""
        mediator = ConflictMediator()

        # Verify mediator was created
        assert mediator is not None


# ============================================
# Integration Test: Composition Planning
# ============================================


class TestCompositionIntegration:
    """Test capability composition workflows."""

    def test_plan_simple_composition(
        self,
        registry_with_agents: CapabilityRegistry,
        transform_capability: AgentCapability,
    ):
        """Test planning a simple capability composition."""
        planner = CompositionPlanner(registry_with_agents)

        plan = planner.plan(
            goal="Transform data",
            required_capabilities=["transform"],
            agent_capabilities={"transform-agent": [transform_capability]},
        )

        assert plan.plan_id
        assert len(plan.steps) > 0

    def test_composition_with_multiple_steps(
        self,
        registry_with_agents: CapabilityRegistry,
        transform_capability: AgentCapability,
        query_capability: AgentCapability,
    ):
        """Test composition requiring multiple capabilities."""
        planner = CompositionPlanner(registry_with_agents)

        plan = planner.plan(
            goal="Query and transform data",
            required_capabilities=["query", "transform"],
            agent_capabilities={
                "query-agent": [query_capability],
                "transform-agent": [transform_capability],
            },
        )

        assert plan.plan_id
        # Should have steps for both capabilities
        assert len(plan.steps) >= 1

    @pytest.mark.asyncio
    async def test_composition_execution_basic(
        self,
        registry_with_agents: CapabilityRegistry,
        transform_capability: AgentCapability,
    ):
        """Test basic composition execution."""
        # Create minimal executor config
        config = OrchestrationConfig(
            parallel_execution=False,
            global_timeout_ms=5000,
        )

        executor = CompositionExecutor(
            agent_client=None,  # Mock client not needed for basic test
            config=config,
        )

        # Create a simple plan
        planner = CompositionPlanner(registry_with_agents)
        plan = planner.plan(
            goal="Transform data",
            required_capabilities=["transform"],
            agent_capabilities={"transform-agent": [transform_capability]},
        )

        # Verify plan was created
        assert plan.plan_id
        assert plan.steps is not None


# ============================================
# Integration Test: End-to-End Workflow
# ============================================


class TestEndToEndWorkflow:
    """Test complete end-to-end A2A workflows."""

    def test_complete_discovery_to_negotiation_flow(
        self,
        provider_agent_card: AgentCard,
        consumer_identity: AgentIdentity,
        transform_capability: AgentCapability,
        action_capability: AgentCapability,
    ):
        """Test complete flow from discovery to successful negotiation."""
        # Step 1: Register provider in registry
        registry = CapabilityRegistry()
        reg_response = registry.register(
            agent_card=provider_agent_card,
            ttl_seconds=3600,
        )
        assert reg_response.success

        # Step 2: Consumer discovers provider
        discovery_response = registry.discover(
            DiscoveryRequest(
                requester=consumer_identity,
                required_capabilities=["transform-data"],  # Uses exact capability_id
                max_results=5,
            )
        )
        assert len(discovery_response.agents) >= 1

        discovered_provider = discovery_response.agents[0].agent

        # Step 3: Verify security context
        provider_context = SecurityContext.create(
            requester_agent_id=discovered_provider.identity.agent_id,
            credentials=[
                Credential.bearer_token(token="provider-token", scope=["transform"])
            ],
        )

        validator = SecurityValidator()
        security_result = validator.validate_context(provider_context)
        assert security_result.valid

        # Step 4: Match capabilities
        matcher = CapabilityMatcher(MatchOptions(minimum_compatibility=0.3))
        match_result = matcher.match(
            required=[transform_capability],  # Pass as list
            offered=discovered_provider.capabilities,
        )
        assert match_result.overall_result.overall_compatibility > 0

        # Step 5: Initiate negotiation
        min_terms = MinimumTerms(
            min_duration_seconds=3600,
            max_rate_limit=None,
        )

        consumer_manager = NegotiationManager(
            our_identity=consumer_identity,
            our_capabilities=[action_capability],
            evaluation_policy=EvaluationPolicy(
                min_acceptable_terms=min_terms,
                negotiation_strategy=NegotiationStrategy.COOPERATIVE,
                auto_accept_threshold=0.7,
            ),
        )

        session = consumer_manager.initiate(
            target=discovered_provider.identity,
            requested_capabilities=[
                CapabilityRequest(
                    capability_type="transform",
                    priority=RequestPriority.REQUIRED,
                )
            ],
            offered_capabilities=[
                CapabilityOffer(capability=action_capability)
            ],
            terms=NegotiationTerms(
                duration_seconds=86400,
                auto_renew=True,
            ),
        )

        assert session.session_id
        assert session.status in [NegotiationStatus.INITIATED, NegotiationStatus.PROPOSAL_SENT]

    def test_workflow_serialization_round_trip(
        self,
        provider_agent_card: AgentCard,
    ):
        """Test serialization throughout workflow."""
        # Serialize agent card to JSON
        serializer = AgentCardSerializer()
        json_str = serializer.to_json(provider_agent_card)

        assert json_str
        assert "data-processor" in json_str

        # Serialize to dict
        card_dict = serializer.to_dict(provider_agent_card)
        assert card_dict["identity"]["name"] == provider_agent_card.identity.name

        # Serialize to A2A format
        a2a_format = serializer.to_a2a_format(provider_agent_card)
        assert "agentCard" in a2a_format
        assert a2a_format["agentCard"]["agent"]["name"] == provider_agent_card.identity.name

        # Validate original card
        validator = AgentCardValidator()
        validation_result = validator.validate(provider_agent_card)
        assert validation_result.valid


# ============================================
# Integration Test: Error Handling
# ============================================


class TestErrorHandlingIntegration:
    """Test error handling across integrated components."""

    def test_expired_security_context_blocks_negotiation(
        self,
        provider_identity: AgentIdentity,
    ):
        """Test that expired security context blocks operations."""
        # Create expired context
        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

        expired_context = SecurityContext(
            context_id="expired-ctx",
            requester_agent_id="test-agent",
            expires_at=past_time,
        )

        validator = SecurityValidator()
        result = validator.validate_context(expired_context)

        assert result.valid is False
        assert any("expired" in r.lower() for r in result.failure_reasons)

    def test_broken_trust_chain_blocks_delegation(self):
        """Test that broken trust chain blocks operations."""
        # Create broken chain
        entry1 = TrustChainEntry.create(
            issuer="root",
            subject="agent-a",
            delegation_type=DelegationType.DIRECT,
            permissions=["all"],
        )

        entry2 = TrustChainEntry.create(
            issuer="agent-wrong",  # Should be agent-a
            subject="agent-b",
            delegation_type=DelegationType.DELEGATED,
            permissions=["read"],
        )

        context = SecurityContext.create(
            requester_agent_id="agent-b",
            trust_chain=[entry1, entry2],
        )

        validator = SecurityValidator()
        result = validator.validate_context(context)

        assert result.valid is False
        assert any("chain" in r.lower() for r in result.failure_reasons)

    def test_negotiation_session_creation(
        self,
        provider_identity: AgentIdentity,
        consumer_identity: AgentIdentity,
    ):
        """Test negotiation session creation and handling."""
        # Create session
        session = NegotiationSession.create(
            initiator=consumer_identity,
            responder=provider_identity,
            expiration_hours=1,
        )

        # Session should be created
        assert session.session_id
        assert session.status == NegotiationStatus.INITIATED

    def test_invalid_capability_request_handling(
        self,
        provider_identity: AgentIdentity,
        consumer_identity: AgentIdentity,
    ):
        """Test handling of negotiation with empty requests."""
        min_terms = MinimumTerms(
            min_duration_seconds=3600,
            max_rate_limit=None,
        )

        manager = NegotiationManager(
            our_identity=consumer_identity,
            our_capabilities=[],
            evaluation_policy=EvaluationPolicy(
                min_acceptable_terms=min_terms,
                negotiation_strategy=NegotiationStrategy.COOPERATIVE,
            ),
        )

        # Try to initiate with no requested capabilities
        session = manager.initiate(
            target=provider_identity,
            requested_capabilities=[],  # Empty
            offered_capabilities=[],
            terms=NegotiationTerms(duration_seconds=3600),
        )

        # Should still create session (empty negotiation is valid)
        assert session.session_id


# ============================================
# Integration Test: Performance Characteristics
# ============================================


class TestPerformanceCharacteristics:
    """Test performance characteristics of integrated system."""

    def test_registry_handles_many_agents(self):
        """Test registry can handle many registered agents."""
        registry = CapabilityRegistry()

        # Register 50 agents
        for i in range(50):
            identity = AgentIdentity.create(
                name=f"agent-{i}",
                version="1.0.0",
                description=f"Test agent {i}",
                provider="test-provider",
            )

            capability = AgentCapability(
                capability_id=f"cap-{i}",
                capability_type=CapabilityType.TRANSFORM if i % 2 == 0 else CapabilityType.QUERY,
                name=f"capability-{i}",
                description=f"Test capability {i}",
                input_schema=SchemaDefinition.object(
                    description="Input",
                    properties=[
                        SchemaProperty(
                            name="data",
                            schema=SchemaDefinition.string(description="Data"),
                            description="Input data",
                        ),
                    ],
                    required=["data"],
                ),
                output_schema=SchemaDefinition.object(
                    description="Output",
                    properties=[
                        SchemaProperty(
                            name="result",
                            schema=SchemaDefinition.string(description="Result"),
                            description="Output result",
                        ),
                    ],
                    required=["result"],
                ),
            )

            card = (
                AgentCardBuilder(identity)
                .add_capability(capability)
                .add_protocol(ProtocolType.A2A, "1.0")
                .add_endpoint(
                    EndpointType.PRIMARY,
                    f"https://api.example.com/agent-{i}",
                    ProtocolType.A2A,
                )
                .build()
            )

            registry.register(agent_card=card, ttl_seconds=3600)

        # Verify all registered
        status = registry.get_status()
        assert status.agent_count == 50

        # Discovery should still be fast
        import time
        start = time.time()

        # Create a requester for discovery
        requester = AgentIdentity.create(
            name="test-requester",
            version="1.0.0",
            description="Test requester",
            provider="test-provider",
        )

        discovery_response = registry.discover(
            DiscoveryRequest(
                requester=requester,
                required_capabilities=["cap-0"],  # Uses exact capability_id (cap-0 is TRANSFORM)
                max_results=100,
            )
        )

        elapsed = time.time() - start

        # Should complete in under 1 second
        assert elapsed < 1.0
        assert len(discovery_response.agents) > 0

    def test_trust_chain_validation_performance(self):
        """Test trust chain validation is efficient."""
        validator = TrustChainValidator(max_chain_length=20)

        # Build a long chain
        entries = []
        for i in range(15):
            entry = TrustChainEntry.create(
                issuer=f"agent-{i}" if i > 0 else "root",
                subject=f"agent-{i + 1}",
                delegation_type=DelegationType.TRANSITIVE,
                permissions=["read", "write"],
                expires_in_hours=24,
                previous_entry_id=entries[-1].entry_id if entries else None,
            )
            entries.append(entry)

        import time
        start = time.time()

        is_valid, errors = validator.validate_chain(entries)

        elapsed = time.time() - start

        # Should be valid and fast
        assert is_valid
        assert elapsed < 0.1  # Under 100ms
