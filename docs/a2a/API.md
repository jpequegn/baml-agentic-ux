# A2A API Reference

## Module Overview

The agent negotiation system is organized into the following modules:

| Module | Description |
|--------|-------------|
| `agent_types` | Base types for agent identity and capabilities |
| `agent_card` | Agent card schema and serialization |
| `capability_registry` | Capability registry and discovery |
| `capability_matcher` | Schema matching algorithms |
| `negotiation_state` | Negotiation protocol and state machine |
| `conflict_resolution` | Conflict detection and resolution |
| `composition` | Dynamic capability composition |
| `security` | Trust chain and authentication |

---

## agent_types

Base types for agent identity and capabilities.

### Enums

#### TrustLevel

```python
class TrustLevel(Enum):
    NONE = "none"
    BASIC = "basic"
    VERIFIED = "verified"
    TRUSTED = "trusted"
    PRIVILEGED = "privileged"
```

Supports comparison operators (`<`, `<=`, `>`, `>=`).

#### CapabilityType

```python
class CapabilityType(Enum):
    ACTION = "action"
    QUERY = "query"
    TRANSFORM = "transform"
    STREAM = "stream"
    COMPOSITE = "composite"
    DELEGATION = "delegation"
    NOTIFICATION = "notification"
```

#### SchemaType

```python
class SchemaType(Enum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"
    ANY = "any"
```

### Classes

#### AgentIdentity

```python
@dataclass
class AgentIdentity:
    agent_id: str
    name: str
    version: str
    description: str
    provider: str | None = None
    trust_domain: str | None = None
    metadata: AgentMetadata | None = None

    @classmethod
    def create(cls, name: str, version: str, description: str, ...) -> AgentIdentity
```

#### AgentCapability

```python
@dataclass
class AgentCapability:
    capability_id: str
    capability_type: CapabilityType
    name: str
    description: str
    input_schema: SchemaDefinition
    output_schema: SchemaDefinition
    constraints: list[CapabilityConstraint] = field(default_factory=list)
    performance_hints: PerformanceHints | None = None
    trust_requirements: TrustRequirements | None = None
    version: str = "1.0.0"
    deprecated: bool = False
```

#### SchemaDefinition

```python
@dataclass
class SchemaDefinition:
    schema_type: SchemaType
    description: str = ""
    properties: list[SchemaProperty] = field(default_factory=list)
    required: list[str] = field(default_factory=list)
    items: SchemaDefinition | None = None  # For arrays
    format: str | None = None
    enum_values: list[str] = field(default_factory=list)

    @classmethod
    def string(cls, description: str = "", format: str = None) -> SchemaDefinition
    @classmethod
    def integer(cls, description: str = "") -> SchemaDefinition
    @classmethod
    def object(cls, properties: list[SchemaProperty], required: list[str] = None) -> SchemaDefinition
    @classmethod
    def array(cls, items: SchemaDefinition, description: str = "") -> SchemaDefinition
```

---

## agent_card

Agent card schema compatible with Google A2A protocol.

### Enums

#### ProtocolType

```python
class ProtocolType(Enum):
    A2A = "a2a"
    MCP = "mcp"
    OPENAPI = "openapi"
    JSON_RPC = "json_rpc"
    GRPC = "grpc"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"
```

#### EndpointType

```python
class EndpointType(Enum):
    PRIMARY = "primary"
    FALLBACK = "fallback"
    HEALTH_CHECK = "health_check"
    DISCOVERY = "discovery"
    ADMIN = "admin"
```

#### AuthMethod

```python
class AuthMethod(Enum):
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    OAUTH2 = "oauth2"
    MTLS = "mtls"
    BASIC = "basic"
```

### Classes

#### AgentCard

```python
@dataclass
class AgentCard:
    identity: AgentIdentity
    capabilities: list[AgentCapability]
    supported_protocols: list[SupportedProtocol]
    endpoints: list[CardEndpoint]
    compliance_tags: list[ComplianceTag] = field(default_factory=list)
    data_handling: DataHandlingPolicy | None = None
```

#### AgentCardBuilder

```python
class AgentCardBuilder:
    def __init__(self) -> None
    def with_identity(self, identity: AgentIdentity) -> AgentCardBuilder
    def with_capability(self, capability: AgentCapability) -> AgentCardBuilder
    def with_protocol(self, protocol: ProtocolType, version: str) -> AgentCardBuilder
    def with_endpoint(self, endpoint: CardEndpoint) -> AgentCardBuilder
    def with_compliance(self, standard: ComplianceStandard) -> AgentCardBuilder
    def build(self) -> AgentCard
```

#### AgentCardValidator

```python
class AgentCardValidator:
    def validate(self, card: AgentCard) -> CardValidationResult
```

#### AgentCardSerializer

```python
class AgentCardSerializer:
    def to_json(self, card: AgentCard) -> str
    def from_json(self, json_str: str) -> AgentCard
    def to_a2a_format(self, card: AgentCard) -> dict
    def to_well_known_format(self, card: AgentCard) -> dict
```

---

## capability_registry

In-memory capability registry with inverted indices.

### Enums

#### ConstraintOperator

```python
class ConstraintOperator(Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    REGEX = "regex"
    IN = "in"
    NOT_IN = "not_in"
```

### Classes

#### CapabilityRegistry

```python
class CapabilityRegistry:
    def __init__(self, cleanup_interval_seconds: int = 60) -> None

    def register(
        self,
        agent_card: AgentCard,
        ttl_seconds: int = 3600,
        metadata: dict | None = None
    ) -> RegistrationResponse

    def deregister(self, agent_id: str) -> DeregistrationResponse

    def discover(
        self,
        request: DiscoveryRequest
    ) -> DiscoveryResponse

    def get_agent(self, agent_id: str) -> AgentCard | None

    def get_status(self) -> RegistryStatus

    def cleanup_expired(self) -> int
```

#### DiscoveryRequest

```python
@dataclass
class DiscoveryRequest:
    required_capabilities: list[str] = field(default_factory=list)
    constraints: list[DiscoveryConstraint] = field(default_factory=list)
    max_results: int = 10
    timeout_ms: int = 5000
    include_metadata: bool = False
```

#### DiscoveryConstraint

```python
@dataclass
class DiscoveryConstraint:
    field: str
    operator: ConstraintOperator
    value: str | list[str]
```

---

## capability_matcher

Cupid-style capability matching algorithms.

### Enums

#### TransformationType

```python
class TransformationType(Enum):
    TYPE_COERCION = "type_coercion"
    PROPERTY_RENAME = "property_rename"
    PROPERTY_ADD = "property_add"
    PROPERTY_REMOVE = "property_remove"
    FORMAT_CONVERSION = "format_conversion"
    ARRAY_WRAP = "array_wrap"
    ARRAY_UNWRAP = "array_unwrap"
    OPTIONAL_TO_REQUIRED = "optional_to_required"
    ENUM_MAPPING = "enum_mapping"
    NESTED_TRANSFORM = "nested_transform"
```

#### TransformationComplexity

```python
class TransformationComplexity(Enum):
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    RISKY = "risky"
```

### Classes

#### CapabilityMatcher

```python
class CapabilityMatcher:
    def __init__(self, options: MatchOptions | None = None) -> None

    def match(
        self,
        required: AgentCapability,
        offered: list[AgentCapability]
    ) -> CapabilityMatchResult

    def find_best_match(
        self,
        required: AgentCapability,
        offered: list[AgentCapability]
    ) -> BestMatch | None

    def check_schema_compatibility(
        self,
        required_schema: SchemaDefinition,
        offered_schema: SchemaDefinition
    ) -> SchemaCompatibility

    def suggest_adaptations(
        self,
        required: AgentCapability,
        offered: AgentCapability
    ) -> list[AdaptationSuggestion]
```

#### MatchOptions

```python
@dataclass
class MatchOptions:
    min_score_threshold: float = 0.5
    type_weight: float = 0.4
    name_weight: float = 0.2
    description_weight: float = 0.2
    schema_weight: float = 0.2
    allow_type_coercion: bool = True
    fuzzy_name_matching: bool = True
```

---

## negotiation_state

Negotiation protocol and state machine.

### Enums

#### NegotiationStatus

```python
class NegotiationStatus(Enum):
    INITIATED = "initiated"
    PROPOSAL_SENT = "proposal_sent"
    COUNTER_OFFERED = "counter_offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    ADAPTED = "adapted"
```

#### NegotiationAction

```python
class NegotiationAction(Enum):
    PROPOSE = "propose"
    COUNTER = "counter"
    ACCEPT = "accept"
    REJECT = "reject"
    WITHDRAW = "withdraw"
    TIMEOUT = "timeout"
```

### Classes

#### NegotiationStateMachine

```python
class NegotiationStateMachine:
    VALID_TRANSITIONS: dict[NegotiationStatus, list[NegotiationStatus]]

    def __init__(self, session: NegotiationSession) -> None

    def can_transition(self, target: NegotiationStatus) -> bool

    def transition(
        self,
        target: NegotiationStatus,
        actor: str,
        action: NegotiationAction,
        proposal: NegotiationProposal | None = None,
        rationale: str | None = None
    ) -> bool

    def on_transition(self, callback: Callable) -> None
```

#### NegotiationManager

```python
class NegotiationManager:
    def __init__(
        self,
        our_identity: AgentIdentity,
        our_capabilities: list[AgentCapability],
        evaluation_policy: EvaluationPolicy
    ) -> None

    def initiate(
        self,
        target: AgentIdentity,
        requested_capabilities: list[CapabilityRequest],
        offered_capabilities: list[CapabilityOffer],
        terms: NegotiationTerms
    ) -> NegotiationSession

    def receive_proposal(
        self,
        session_id: str,
        proposal: NegotiationProposal
    ) -> ProposalEvaluation

    def finalize(self, session_id: str) -> Agreement
```

---

## conflict_resolution

Conflict detection and resolution.

### Enums

#### ConflictType

```python
class ConflictType(Enum):
    SCHEMA_MISMATCH = "schema_mismatch"
    CONSTRAINT_VIOLATION = "constraint_violation"
    RESOURCE_CONTENTION = "resource_contention"
    PRIORITY_CLASH = "priority_clash"
    TRUST_INSUFFICIENT = "trust_insufficient"
    SEMANTIC_AMBIGUITY = "semantic_ambiguity"
```

#### ConflictSeverity

```python
class ConflictSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

#### ResolutionStrategy

```python
class ResolutionStrategy(Enum):
    TRANSFORM = "transform"
    SUBSET = "subset"
    MEDIATE = "mediate"
    ESCALATE = "escalate"
    ALTERNATIVE = "alternative"
    NEGOTIATE_TERMS = "negotiate_terms"
    BRIDGE = "bridge"
```

### Classes

#### ConflictDetector

```python
class ConflictDetector:
    def detect_schema_conflicts(
        self,
        source: SchemaDefinition,
        target: SchemaDefinition
    ) -> list[Conflict]

    def detect_constraint_conflicts(
        self,
        constraints_a: list[CapabilityConstraint],
        constraints_b: list[CapabilityConstraint]
    ) -> list[Conflict]

    def analyze(
        self,
        proposal_a: NegotiationProposal,
        proposal_b: NegotiationProposal
    ) -> ConflictAnalysis
```

#### SchemaTransformer

```python
class SchemaTransformer:
    def create_plan(
        self,
        source: SchemaDefinition,
        target: SchemaDefinition
    ) -> SchemaTransformPlan

    def apply(
        self,
        data: dict,
        plan: SchemaTransformPlan
    ) -> TransformResult
```

#### ConflictMediator

```python
class ConflictMediator:
    def mediate(self, request: MediationRequest) -> MediationResult

    def resolve_deadlock(
        self,
        session: NegotiationSession,
        deadlock_turns: int
    ) -> DeadlockResolution
```

---

## composition

Dynamic capability composition.

### Enums

#### ExecutionStatus

```python
class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
```

#### InputSource

```python
class InputSource(Enum):
    LITERAL = "literal"
    PREVIOUS_STEP = "previous_step"
    USER_INPUT = "user_input"
    CONTEXT = "context"
```

### Classes

#### CompositionPlanner

```python
class CompositionPlanner:
    def __init__(self, registry: CapabilityRegistry) -> None

    def plan(
        self,
        goal: str,
        required_capabilities: list[str],
        constraints: list[CompositionConstraint] = None
    ) -> CompositionPlan
```

#### CompositionExecutor

```python
class CompositionExecutor:
    def __init__(
        self,
        agent_client: AgentClient,
        config: OrchestrationConfig
    ) -> None

    async def execute(
        self,
        plan: CompositionPlan,
        inputs: dict
    ) -> CompositionExecution
```

#### CircuitBreaker

```python
class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig) -> None

    def allow_request(self) -> bool
    def record_success(self) -> None
    def record_failure(self) -> None

    @property
    def state(self) -> str  # "closed", "open", "half-open"
```

---

## security

Trust chain and authentication.

### Enums

#### CredentialType

```python
class CredentialType(Enum):
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    MTLS_CERT = "mtls_cert"
    DID = "did"
    VC = "vc"
```

#### DelegationType

```python
class DelegationType(Enum):
    DIRECT = "direct"
    DELEGATED = "delegated"
    TRANSITIVE = "transitive"
```

### Classes

#### TrustChainValidator

```python
class TrustChainValidator:
    def __init__(self, trusted_roots: list[str]) -> None

    def validate_chain(
        self,
        entries: list[TrustChainEntry]
    ) -> tuple[bool, list[str]]  # (valid, errors)

    def get_effective_permissions(
        self,
        entries: list[TrustChainEntry]
    ) -> list[str]
```

#### SecurityValidator

```python
class SecurityValidator:
    def __init__(
        self,
        trust_validator: TrustChainValidator,
        credential_manager: CredentialManager
    ) -> None

    def validate_context(
        self,
        context: SecurityContext,
        required_permissions: list[str]
    ) -> SecurityValidation
```

---

## Common Patterns

### Creating an Agent

```python
from src.agent_negotiation import (
    AgentIdentity,
    AgentCapability,
    AgentCard,
    AgentCardBuilder,
    CapabilityType,
    SchemaDefinition,
    ProtocolType,
)

# Create identity
identity = AgentIdentity.create(
    name="translator",
    version="1.0.0",
    description="Translation service",
    provider="acme"
)

# Create capability
translate = AgentCapability(
    capability_id="translate-text",
    capability_type=CapabilityType.TRANSFORM,
    name="translate_text",
    description="Translate text between languages",
    input_schema=SchemaDefinition.object(
        properties=[...],
        required=["text", "target_language"]
    ),
    output_schema=SchemaDefinition.object(...)
)

# Build card
card = (
    AgentCardBuilder()
    .with_identity(identity)
    .with_capability(translate)
    .with_protocol(ProtocolType.A2A, "1.0")
    .with_endpoint(...)
    .build()
)
```

### Discovering Agents

```python
from src.agent_negotiation import (
    CapabilityRegistry,
    DiscoveryRequest,
    DiscoveryConstraint,
    ConstraintOperator,
)

registry = CapabilityRegistry()

# Register agents...

# Discover
response = registry.discover(
    DiscoveryRequest(
        required_capabilities=["transform"],
        constraints=[
            DiscoveryConstraint(
                field="compliance_tags",
                operator=ConstraintOperator.CONTAINS,
                value="gdpr"
            )
        ],
        max_results=5
    )
)

for match in response.agents:
    print(f"{match.agent.identity.name}: {match.match_score}")
```

### Running a Negotiation

```python
from src.agent_negotiation import (
    NegotiationManager,
    CapabilityRequest,
    NegotiationTerms,
    RequestPriority,
)

manager = NegotiationManager(
    our_identity=our_identity,
    our_capabilities=our_capabilities,
    evaluation_policy=policy
)

# Initiate
session = manager.initiate(
    target=target_identity,
    requested_capabilities=[
        CapabilityRequest(
            capability_type="transform",
            priority=RequestPriority.REQUIRED
        )
    ],
    offered_capabilities=[],
    terms=NegotiationTerms(duration_seconds=86400)
)

# Later: finalize
agreement = manager.finalize(session.session_id)
```
