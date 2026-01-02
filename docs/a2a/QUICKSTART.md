# A2A Quickstart Guide

Get started with agent-to-agent negotiation in 5 minutes.

## Installation

The A2A negotiation system is part of the baml-agentic-ux framework:

```bash
# Clone the repository
git clone https://github.com/your-org/baml-agentic-ux.git
cd baml-agentic-ux

# Install dependencies
uv sync
```

## Quick Example

### 1. Create an Agent

```python
from src.agent_negotiation import (
    AgentIdentity,
    AgentCapability,
    AgentCard,
    AgentCardBuilder,
    CapabilityType,
    SchemaDefinition,
    SchemaProperty,
    ProtocolType,
    EndpointType,
    CardEndpoint,
    AuthMethod,
)

# Define your agent's identity
identity = AgentIdentity.create(
    name="my-assistant",
    version="1.0.0",
    description="A helpful assistant agent",
    provider="my-company"
)

# Define a capability
summarize_capability = AgentCapability(
    capability_id="summarize-text",
    capability_type=CapabilityType.TRANSFORM,
    name="summarize",
    description="Summarize text content",
    input_schema=SchemaDefinition.object(
        description="Input for summarization",
        properties=[
            SchemaProperty(
                name="text",
                schema=SchemaDefinition.string(description="Text to summarize"),
                description="The text content to summarize"
            ),
            SchemaProperty(
                name="max_length",
                schema=SchemaDefinition.integer(description="Maximum summary length"),
                description="Maximum length of the summary"
            )
        ],
        required=["text"]
    ),
    output_schema=SchemaDefinition.object(
        description="Summarization result",
        properties=[
            SchemaProperty(
                name="summary",
                schema=SchemaDefinition.string(description="The summary"),
                description="Summarized text"
            )
        ],
        required=["summary"]
    )
)

# Build the agent card
card = (
    AgentCardBuilder(identity)
    .add_capability(summarize_capability)
    .add_protocol(ProtocolType.A2A, "1.0")
    .add_endpoint(
        EndpointType.PRIMARY,
        "https://api.my-company.com/agents/my-assistant",
        ProtocolType.A2A,
    )
    .build()
)

print(f"Created agent: {card.identity.agent_id}")
```

### 2. Register with the Registry

```python
from src.agent_negotiation import CapabilityRegistry

# Create a registry (in production, this would be a shared service)
registry = CapabilityRegistry()

# Register the agent
response = registry.register(agent_card=card)

print(f"Registered: {response.success}")
print(f"Registration ID: {response.registration_id}")
```

### 3. Discover Other Agents

```python
from src.agent_negotiation import (
    DiscoveryRequest,
    DiscoveryConstraint,
    ConstraintOperator,
)

# Find agents that can transform data
discovery_response = registry.discover(
    DiscoveryRequest(
        requester=identity,  # The agent making the request
        required_capabilities=["transform"],
        max_results=10
    )
)

print(f"Found {len(discovery_response.agents)} agents:")
for match in discovery_response.agents:
    print(f"  - {match.agent.identity.name}: score={match.match_score:.2f}")
```

### 4. Match Capabilities

```python
from src.agent_negotiation import CapabilityMatcher, MatchOptions

# Create a matcher
matcher = CapabilityMatcher(MatchOptions(
    minimum_compatibility=0.5,
    fuzzy_matching=True
))

# Match a required capability against offered ones
result = matcher.match(
    required=[my_required_capability],  # List of required capabilities
    offered=discovered_agent.capabilities
)

print(f"Overall compatibility: {result.overall_result.overall_compatibility:.2f}")
for match in result.matches:
    print(f"  {match.required_capability} -> {match.matched_capability}")
    print(f"    Score: {match.compatibility_score:.2f}")
```

### 5. Negotiate an Agreement

```python
from src.agent_negotiation import (
    NegotiationManager,
    CapabilityRequest,
    CapabilityOffer,
    NegotiationTerms,
    EvaluationPolicy,
    RequestPriority,
    NegotiationStrategy,
)

# Set up negotiation manager
manager = NegotiationManager(
    our_identity=identity,
    our_capabilities=[summarize_capability],
    evaluation_policy=EvaluationPolicy(
        negotiation_strategy=NegotiationStrategy.COOPERATIVE,
        auto_accept_threshold=0.8,
        max_counter_offers=3
    )
)

# Initiate negotiation with another agent
session = manager.initiate(
    target=other_agent_identity,
    requested_capabilities=[
        CapabilityRequest(
            capability_type="query",
            priority=RequestPriority.REQUIRED
        )
    ],
    offered_capabilities=[
        CapabilityOffer(capability=summarize_capability)
    ],
    terms=NegotiationTerms(
        duration_seconds=86400,  # 1 day
        auto_renew=True
    )
)

print(f"Negotiation session: {session.session_id}")
print(f"Status: {session.status.value}")
```

### 6. Handle Conflicts

```python
from src.agent_negotiation import (
    ConflictDetector,
    SchemaTransformer,
    ConflictMediator,
    MediationStyle,
)

# Detect conflicts between schemas
detector = ConflictDetector()
conflicts = detector.detect_schema_conflicts(
    source=my_output_schema,
    target=their_input_schema
)

if conflicts:
    print(f"Found {len(conflicts)} conflicts:")
    for conflict in conflicts:
        print(f"  - {conflict.conflict_type.value}: {conflict.description}")

    # Create transformation plan
    transformer = SchemaTransformer()
    plan = transformer.create_plan(
        source=my_output_schema,
        target=their_input_schema
    )

    print(f"Transformation plan created:")
    print(f"  Data loss risk: {plan.data_loss_risk.value}")
    print(f"  Reversible: {plan.reversible}")
```

### 7. Compose Capabilities

```python
from src.agent_negotiation import (
    CompositionPlanner,
    CompositionExecutor,
    OrchestrationConfig,
)

# Plan a composition
planner = CompositionPlanner(registry)
plan = planner.plan(
    goal="Translate and summarize document",
    required_capabilities=["transform"],  # translate, summarize
    constraints=[]
)

print(f"Composition plan: {plan.plan_id}")
print(f"Steps: {len(plan.steps)}")
for step in plan.steps:
    print(f"  {step.step_id}: {step.capability.name}")

# Execute (async)
import asyncio

async def run_composition():
    executor = CompositionExecutor(
        agent_client=my_agent_client,
        config=OrchestrationConfig(
            parallel_execution=False,
            global_timeout_ms=30000
        )
    )

    execution = await executor.execute(
        plan=plan,
        inputs={"document": "Long document text..."}
    )

    print(f"Execution status: {execution.status.value}")
    print(f"Final output: {execution.final_output}")

asyncio.run(run_composition())
```

## Common Patterns

### Pattern 1: Service Discovery

```python
# Find all agents that support GDPR compliance
response = registry.discover(
    DiscoveryRequest(
        constraints=[
            DiscoveryConstraint(
                field="compliance_tags",
                operator=ConstraintOperator.CONTAINS,
                value="gdpr"
            )
        ]
    )
)
```

### Pattern 2: Fallback Agent Selection

```python
# Try primary agent, fall back to alternatives
for match in sorted(discovery_response.agents, key=lambda m: -m.match_score):
    try:
        result = invoke_agent(match.agent, input_data)
        break
    except Exception as e:
        print(f"Agent {match.agent.identity.name} failed: {e}")
        continue
```

### Pattern 3: Capability Upgrade

```python
# Check if a newer version of a capability exists
current_version = "1.0.0"
response = registry.discover(
    DiscoveryRequest(
        required_capabilities=["transform"],
        constraints=[
            DiscoveryConstraint(
                field="capability_version",
                operator=ConstraintOperator.GREATER_THAN,
                value=current_version
            )
        ]
    )
)
```

## Configuration

### Environment Variables

```bash
# Registry configuration
REGISTRY_CLEANUP_INTERVAL=60  # seconds
REGISTRY_DEFAULT_TTL=3600     # seconds

# Negotiation configuration
NEGOTIATION_TIMEOUT=300       # seconds
MAX_COUNTER_OFFERS=5

# Security configuration
REQUIRE_MTLS=true
MIN_TRUST_LEVEL=verified
```

### Custom Match Options

```python
options = MatchOptions(
    minimum_compatibility=0.7,  # Higher threshold for strict matching
    type_weight=0.5,            # Emphasize type compatibility
    name_weight=0.1,            # De-emphasize name matching
    description_weight=0.2,
    schema_weight=0.2,
    allow_type_coercion=False,  # Strict type matching
    fuzzy_matching=False        # Exact name matching
)
```

## Troubleshooting

### Agent Not Found

```python
# Check if agent is registered
agent = registry.get_agent(agent_id)
if agent is None:
    print("Agent not registered or registration expired")

# Check registry status
status = registry.get_status()
print(f"Total agents: {status.agent_count}")
print(f"Total capabilities: {status.capability_count}")
```

### Low Match Scores

```python
# Get detailed matching information
result = matcher.match(required, offered)

for match in result.matches:
    print(f"Match: {match.required_capability} -> {match.matched_capability}")
    print(f"  Score: {match.compatibility_score}")
    print(f"  Schema compatible: {match.schema_compatibility.input_compatible}")

# Check suggestions
for suggestion in result.adaptation_suggestions:
    print(f"Suggestion: {suggestion.suggestion_type.value}")
    print(f"  Description: {suggestion.description}")
```

### Negotiation Deadlock

```python
from src.agent_negotiation import ConflictMediator, MediationRequest

# Use mediation to resolve deadlock
mediator = ConflictMediator()
resolution = mediator.resolve_deadlock(
    session=stuck_session,
    deadlock_turns=3
)

if resolution.resolution_possible:
    print(f"Suggested strategy: {resolution.strategy.value}")
else:
    print("Manual intervention required")
```

## Next Steps

- Read the [Architecture Guide](./ARCHITECTURE.md) for system design details
- Review the [Protocol Specifications](./PROTOCOLS.md) for message formats
- Check the [Security Model](./SECURITY.md) for authentication and authorization
- Explore the [API Reference](./API.md) for complete API documentation
