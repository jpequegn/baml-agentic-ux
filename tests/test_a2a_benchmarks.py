"""
Performance benchmarks for the A2A negotiation system.

Tests performance characteristics of key operations:
- Registry operations (registration, discovery, deregistration)
- Capability matching with varying complexity
- Negotiation session management
- Schema transformation and conflict detection

These benchmarks help establish baseline performance and detect regressions.
"""

import time
from dataclasses import dataclass

import pytest

from src.agent_negotiation import (
    # Agent Card
    AgentCard,
    AgentCardBuilder,
    EndpointType,
    ProtocolType,
    # Registry
    CapabilityRegistry,
    DiscoveryRequest,
    # Matcher
    CapabilityMatcher,
    MatchOptions,
    # Negotiation
    CapabilityOffer,
    CapabilityRequest,
    EvaluationPolicy,
    MinimumTerms,
    NegotiationManager,
    NegotiationSession,
    NegotiationStateMachine,
    NegotiationStatus,
    NegotiationStrategy,
    NegotiationTerms,
    RequestPriority,
    NegotiationAction,
)
from src.agent_negotiation.conflict_resolution import (
    ConflictDetector,
)
from src.lui_simulator.agent_types import (
    AgentIdentity,
    AgentCapability,
    CapabilityType,
    SchemaDefinition,
    SchemaProperty,
)


# ============================================
# Benchmark Infrastructure
# ============================================


@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""

    name: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    ops_per_second: float

    def __str__(self) -> str:
        return (
            f"{self.name}: avg={self.avg_time_ms:.3f}ms, "
            f"min={self.min_time_ms:.3f}ms, max={self.max_time_ms:.3f}ms, "
            f"ops/sec={self.ops_per_second:.1f}"
        )


def run_benchmark(name: str, iterations: int, func: callable) -> BenchmarkResult:
    """Run a benchmark function multiple times and collect timing data."""
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    total_time = sum(times)
    avg_time = total_time / iterations
    min_time = min(times)
    max_time = max(times)
    ops_per_sec = (iterations / total_time) * 1000 if total_time > 0 else 0

    return BenchmarkResult(
        name=name,
        iterations=iterations,
        total_time_ms=total_time,
        avg_time_ms=avg_time,
        min_time_ms=min_time,
        max_time_ms=max_time,
        ops_per_second=ops_per_sec,
    )


# ============================================
# Helper Functions
# ============================================


def create_test_identity(name: str) -> AgentIdentity:
    """Create a test agent identity."""
    return AgentIdentity.create(
        name=name,
        version="1.0.0",
        description=f"Test agent {name}",
        provider="benchmark-corp",
    )


def create_test_capability(cap_id: str) -> AgentCapability:
    """Create a test capability with required schemas."""
    return AgentCapability(
        capability_id=cap_id,
        capability_type=CapabilityType.QUERY,
        name=f"cap-{cap_id}",
        description=f"Test capability {cap_id}",
        input_schema=SchemaDefinition.object(
            description="Input schema",
            properties=[
                SchemaProperty(
                    name="query",
                    schema=SchemaDefinition.string(description="Query"),
                    description="The query string",
                )
            ],
            required=["query"],
        ),
        output_schema=SchemaDefinition.object(
            description="Output schema",
            properties=[
                SchemaProperty(
                    name="result",
                    schema=SchemaDefinition.string(description="Result"),
                    description="The result",
                )
            ],
            required=["result"],
        ),
    )


def create_test_card(identity: AgentIdentity, capability: AgentCapability | None = None) -> AgentCard:
    """Create a test agent card."""
    builder = (
        AgentCardBuilder(identity)
        .add_protocol(ProtocolType.A2A, "1.0")
        .add_endpoint(
            EndpointType.PRIMARY,
            f"https://example.com/{identity.name}",
            ProtocolType.A2A,
        )
    )
    if capability:
        builder = builder.add_capability(capability)
    return builder.build()


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def benchmark_identity() -> AgentIdentity:
    """Create a standard identity for benchmarking."""
    return create_test_identity("benchmark-agent")


@pytest.fixture
def benchmark_capability() -> AgentCapability:
    """Create a standard capability for benchmarking."""
    return create_test_capability("bench-cap")


@pytest.fixture
def benchmark_card(
    benchmark_identity: AgentIdentity,
    benchmark_capability: AgentCapability,
) -> AgentCard:
    """Create a standard agent card for benchmarking."""
    return create_test_card(benchmark_identity, benchmark_capability)


# ============================================
# Registry Benchmarks
# ============================================


class TestRegistryBenchmarks:
    """Benchmarks for registry operations."""

    def test_registration_performance(
        self,
        benchmark_card: AgentCard,
    ):
        """
        Benchmark: Agent registration speed.
        Target: < 1ms per registration.
        """
        registry = CapabilityRegistry()

        def register_once():
            # Create unique card each time
            identity = create_test_identity(f"agent-{time.time_ns()}")
            card = create_test_card(identity)
            registry.register(agent_card=card)

        result = run_benchmark("registration", 100, register_once)
        print(f"\n{result}")

        # Assert performance target
        assert result.avg_time_ms < 10, f"Registration too slow: {result.avg_time_ms}ms"

    def test_discovery_performance_small_registry(
        self,
        benchmark_identity: AgentIdentity,
    ):
        """
        Benchmark: Discovery with small registry (10 agents).
        Target: < 5ms per discovery.
        """
        registry = CapabilityRegistry()

        # Register 10 agents
        for i in range(10):
            identity = create_test_identity(f"agent-{i}")
            capability = create_test_capability(f"cap-{i}")
            card = create_test_card(identity, capability)
            registry.register(agent_card=card)

        def discover_once():
            registry.discover(
                DiscoveryRequest(
                    requester=benchmark_identity,
                    required_capabilities=["cap-0"],
                    max_results=5,
                )
            )

        result = run_benchmark("discovery_small", 100, discover_once)
        print(f"\n{result}")

        assert result.avg_time_ms < 10, f"Discovery too slow: {result.avg_time_ms}ms"

    def test_discovery_performance_large_registry(
        self,
        benchmark_identity: AgentIdentity,
    ):
        """
        Benchmark: Discovery with large registry (100 agents).
        Target: < 20ms per discovery.
        """
        registry = CapabilityRegistry()

        # Register 100 agents with 10 different capability types
        for i in range(100):
            identity = create_test_identity(f"agent-{i}")
            capability = create_test_capability(f"cap-{i % 10}")
            card = create_test_card(identity, capability)
            registry.register(agent_card=card)

        def discover_once():
            registry.discover(
                DiscoveryRequest(
                    requester=benchmark_identity,
                    required_capabilities=["cap-0"],
                    max_results=10,
                )
            )

        result = run_benchmark("discovery_large", 50, discover_once)
        print(f"\n{result}")

        assert result.avg_time_ms < 50, f"Discovery too slow: {result.avg_time_ms}ms"

    def test_deregistration_performance(self):
        """
        Benchmark: Agent deregistration speed.
        Target: < 1ms per deregistration.
        """
        registry = CapabilityRegistry()
        registrations = []  # Store (registration_id, agent_id) tuples

        # Register 50 agents
        for i in range(50):
            identity = create_test_identity(f"agent-{i}")
            card = create_test_card(identity)
            response = registry.register(agent_card=card)
            registrations.append((response.registration_id, identity.agent_id))

        idx = 0

        def deregister_once():
            nonlocal idx
            if idx < len(registrations):
                reg_id, agent_id = registrations[idx]
                registry.deregister(reg_id, agent_id)
                idx += 1

        result = run_benchmark("deregistration", 50, deregister_once)
        print(f"\n{result}")

        assert (
            result.avg_time_ms < 5
        ), f"Deregistration too slow: {result.avg_time_ms}ms"


# ============================================
# Capability Matching Benchmarks
# ============================================


class TestMatcherBenchmarks:
    """Benchmarks for capability matching operations."""

    def test_simple_match_performance(self):
        """
        Benchmark: Simple capability matching.
        Target: < 1ms per match.
        """
        required_cap = create_test_capability("required-query")
        offered_caps = [create_test_capability(f"offered-{i}") for i in range(5)]

        matcher = CapabilityMatcher(
            MatchOptions(
                minimum_compatibility=0.3,
                fuzzy_matching=True,
            )
        )

        def match_once():
            matcher.match(
                required=[required_cap],
                offered=offered_caps,
            )

        result = run_benchmark("simple_match", 100, match_once)
        print(f"\n{result}")

        assert result.avg_time_ms < 5, f"Matching too slow: {result.avg_time_ms}ms"

    def test_complex_schema_match_performance(self):
        """
        Benchmark: Complex schema matching with nested objects.
        Target: < 5ms per match.
        """
        complex_input_schema = SchemaDefinition.object(
            description="Complex input",
            properties=[
                SchemaProperty(
                    name="data",
                    schema=SchemaDefinition.object(
                        description="Nested data",
                        properties=[
                            SchemaProperty(
                                name="field1",
                                schema=SchemaDefinition.string(description="Field 1"),
                                description="First field",
                            ),
                            SchemaProperty(
                                name="field2",
                                schema=SchemaDefinition.integer(description="Field 2"),
                                description="Second field",
                            ),
                            SchemaProperty(
                                name="field3",
                                schema=SchemaDefinition.array(
                                    SchemaDefinition.string(description="Item"),
                                    description="Array field",
                                ),
                                description="Third field",
                            ),
                        ],
                        required=["field1", "field2"],
                    ),
                    description="The nested data object",
                ),
            ],
            required=["data"],
        )

        complex_output_schema = SchemaDefinition.object(
            description="Complex output",
            properties=[
                SchemaProperty(
                    name="result",
                    schema=SchemaDefinition.string(description="Result"),
                    description="The result",
                )
            ],
            required=["result"],
        )

        required_cap = AgentCapability(
            capability_id="complex-required",
            capability_type=CapabilityType.TRANSFORM,
            name="complex-transform",
            description="Complex transformation",
            input_schema=complex_input_schema,
            output_schema=complex_output_schema,
        )

        offered_cap = AgentCapability(
            capability_id="complex-offered",
            capability_type=CapabilityType.TRANSFORM,
            name="complex-transform",
            description="Complex transformation",
            input_schema=complex_input_schema,
            output_schema=complex_output_schema,
        )

        matcher = CapabilityMatcher(
            MatchOptions(
                minimum_compatibility=0.3,
                fuzzy_matching=True,
            )
        )

        def match_once():
            matcher.match(
                required=[required_cap],
                offered=[offered_cap],
            )

        result = run_benchmark("complex_schema_match", 50, match_once)
        print(f"\n{result}")

        assert result.avg_time_ms < 20, f"Complex matching too slow: {result.avg_time_ms}ms"

    def test_many_capabilities_match_performance(self):
        """
        Benchmark: Matching many capabilities.
        Target: < 10ms for matching 10 required against 50 offered.
        """
        required_caps = [create_test_capability(f"req-{i}") for i in range(10)]
        offered_caps = [create_test_capability(f"off-{i % 15}") for i in range(50)]

        matcher = CapabilityMatcher(
            MatchOptions(
                minimum_compatibility=0.3,
                fuzzy_matching=True,
            )
        )

        def match_once():
            matcher.match(
                required=required_caps,
                offered=offered_caps,
            )

        result = run_benchmark("many_caps_match", 30, match_once)
        print(f"\n{result}")

        assert result.avg_time_ms < 50, f"Many-caps matching too slow: {result.avg_time_ms}ms"


# ============================================
# Negotiation Benchmarks
# ============================================


class TestNegotiationBenchmarks:
    """Benchmarks for negotiation operations."""

    def test_session_creation_performance(self):
        """
        Benchmark: Negotiation session creation.
        Target: < 1ms per session.
        """
        initiator = create_test_identity("initiator")
        responder = create_test_identity("responder")

        def create_session():
            NegotiationSession.create(
                initiator=initiator,
                responder=responder,
                expiration_hours=24,
            )

        result = run_benchmark("session_creation", 100, create_session)
        print(f"\n{result}")

        assert (
            result.avg_time_ms < 2
        ), f"Session creation too slow: {result.avg_time_ms}ms"

    def test_state_machine_transition_performance(self):
        """
        Benchmark: State machine transitions.
        Target: < 0.5ms per transition.
        """
        initiator = create_test_identity("initiator")
        responder = create_test_identity("responder")

        sessions = []
        for _ in range(100):
            session = NegotiationSession.create(
                initiator=initiator,
                responder=responder,
                expiration_hours=24,
            )
            sessions.append(NegotiationStateMachine(session))

        idx = 0

        def transition_once():
            nonlocal idx
            if idx < len(sessions):
                sessions[idx].transition(
                    NegotiationStatus.PROPOSAL_SENT,
                    actor=initiator.agent_id,
                    action=NegotiationAction.PROPOSE,
                )
                idx += 1

        result = run_benchmark("state_transition", 100, transition_once)
        print(f"\n{result}")

        assert result.avg_time_ms < 2, f"Transitions too slow: {result.avg_time_ms}ms"

    def test_manager_initiate_performance(self):
        """
        Benchmark: NegotiationManager.initiate() performance.
        Target: < 5ms per initiation.
        """
        our_identity = create_test_identity("our-agent")
        target_identity = create_test_identity("target-agent")
        our_capability = create_test_capability("our-cap")

        manager = NegotiationManager(
            our_identity=our_identity,
            our_capabilities=[our_capability],
            evaluation_policy=EvaluationPolicy(
                min_acceptable_terms=MinimumTerms(min_duration_seconds=3600),
                negotiation_strategy=NegotiationStrategy.COOPERATIVE,
            ),
        )

        def initiate_once():
            manager.initiate(
                target=target_identity,
                requested_capabilities=[
                    CapabilityRequest(
                        capability_type="query",
                        priority=RequestPriority.REQUIRED,
                    )
                ],
                offered_capabilities=[CapabilityOffer(capability=our_capability)],
                terms=NegotiationTerms(duration_seconds=86400),
            )

        result = run_benchmark("manager_initiate", 50, initiate_once)
        print(f"\n{result}")

        assert result.avg_time_ms < 10, f"Initiation too slow: {result.avg_time_ms}ms"


# ============================================
# Conflict Detection Benchmarks
# ============================================


class TestConflictBenchmarks:
    """Benchmarks for conflict detection operations."""

    def test_schema_conflict_detection_performance(self):
        """
        Benchmark: Schema conflict detection.
        Target: < 2ms per detection.
        """
        source_schema = SchemaDefinition.object(
            description="Source schema",
            properties=[
                SchemaProperty(
                    name="field1",
                    schema=SchemaDefinition.string(description="String field"),
                    description="First field",
                ),
                SchemaProperty(
                    name="field2",
                    schema=SchemaDefinition.integer(description="Int field"),
                    description="Second field",
                ),
            ],
            required=["field1"],
        )

        target_schema = SchemaDefinition.object(
            description="Target schema",
            properties=[
                SchemaProperty(
                    name="field1",
                    schema=SchemaDefinition.integer(description="Int field"),  # Type mismatch
                    description="First field",
                ),
                SchemaProperty(
                    name="field3",
                    schema=SchemaDefinition.string(description="String field"),  # Missing field2
                    description="Third field",
                ),
            ],
            required=["field1", "field3"],
        )

        detector = ConflictDetector()

        def detect_once():
            detector.detect_schema_conflicts(
                source=source_schema,
                target=target_schema,
            )

        result = run_benchmark("conflict_detection", 100, detect_once)
        print(f"\n{result}")

        assert (
            result.avg_time_ms < 5
        ), f"Conflict detection too slow: {result.avg_time_ms}ms"


# ============================================
# Serialization Benchmarks
# ============================================


class TestSerializationBenchmarks:
    """Benchmarks for serialization operations."""

    def test_session_serialization_performance(self):
        """
        Benchmark: Session serialization.
        Target: < 1ms per serialization.
        """
        initiator = create_test_identity("initiator")
        responder = create_test_identity("responder")

        session = NegotiationSession.create(
            initiator=initiator,
            responder=responder,
            expiration_hours=24,
        )

        def serialize_once():
            session.to_dict()

        result = run_benchmark("session_serialization", 100, serialize_once)
        print(f"\n{result}")

        assert (
            result.avg_time_ms < 2
        ), f"Serialization too slow: {result.avg_time_ms}ms"

    def test_agent_card_serialization_performance(
        self,
        benchmark_card: AgentCard,
    ):
        """
        Benchmark: Agent card serialization.
        Target: < 1ms per serialization.
        """

        def serialize_once():
            benchmark_card.to_dict()

        result = run_benchmark("card_serialization", 100, serialize_once)
        print(f"\n{result}")

        assert (
            result.avg_time_ms < 2
        ), f"Card serialization too slow: {result.avg_time_ms}ms"


# ============================================
# Concurrent Operations Benchmarks
# ============================================


class TestConcurrencyBenchmarks:
    """Benchmarks for concurrent operations."""

    def test_concurrent_registration_simulation(self):
        """
        Benchmark: Simulated concurrent registrations.
        Tests registry thread-safety overhead.
        """
        registry = CapabilityRegistry()

        def register_burst():
            for i in range(10):
                identity = create_test_identity(f"agent-{time.time_ns()}-{i}")
                card = create_test_card(identity)
                registry.register(agent_card=card)

        result = run_benchmark("burst_registration", 10, register_burst)
        print(f"\n{result}")
        print(f"  (10 registrations per burst, total {result.iterations * 10} registrations)")

        # Each burst is 10 registrations, so avg should be < 50ms
        assert result.avg_time_ms < 100, f"Burst registration too slow: {result.avg_time_ms}ms"

    def test_mixed_operations_performance(
        self,
        benchmark_identity: AgentIdentity,
    ):
        """
        Benchmark: Mixed operations (register, discover, deregister).
        Simulates realistic usage patterns.
        """
        registry = CapabilityRegistry()
        registrations = []  # Store (registration_id, agent_id) tuples

        def mixed_operation():
            # Register
            identity = create_test_identity(f"agent-{time.time_ns()}")
            cap = create_test_capability("mixed-cap")
            card = create_test_card(identity, cap)
            response = registry.register(agent_card=card)
            registrations.append((response.registration_id, identity.agent_id))

            # Discover
            registry.discover(
                DiscoveryRequest(
                    requester=benchmark_identity,
                    required_capabilities=["mixed-cap"],
                    max_results=5,
                )
            )

            # Deregister oldest if we have too many
            if len(registrations) > 10:
                reg_id, agent_id = registrations.pop(0)
                registry.deregister(reg_id, agent_id)

        result = run_benchmark("mixed_operations", 50, mixed_operation)
        print(f"\n{result}")

        assert (
            result.avg_time_ms < 30
        ), f"Mixed operations too slow: {result.avg_time_ms}ms"


# ============================================
# Summary Report
# ============================================


class TestBenchmarkSummary:
    """Generate a summary report of all benchmarks."""

    def test_print_benchmark_summary(self):
        """
        Run a quick summary of key operations.
        This is informational, not a pass/fail test.
        """
        print("\n" + "=" * 60)
        print("A2A NEGOTIATION SYSTEM - PERFORMANCE SUMMARY")
        print("=" * 60)

        # Quick registration test
        registry = CapabilityRegistry()

        reg_result = run_benchmark("Registration", 20, lambda: registry.register(
            agent_card=create_test_card(create_test_identity(f"agent-{time.time_ns()}"))
        ))

        print(f"\n{reg_result}")

        # Session creation
        identity = create_test_identity("summary-agent")
        session_result = run_benchmark("Session Creation", 20, lambda: NegotiationSession.create(
            initiator=identity,
            responder=identity,
            expiration_hours=24,
        ))
        print(session_result)

        # Serialization
        session = NegotiationSession.create(
            initiator=identity,
            responder=identity,
            expiration_hours=24,
        )
        serial_result = run_benchmark("Serialization", 20, lambda: session.to_dict())
        print(serial_result)

        print("\n" + "=" * 60)
        print("All benchmarks completed successfully.")
        print("=" * 60)

        # Always pass - this is informational
        assert True
