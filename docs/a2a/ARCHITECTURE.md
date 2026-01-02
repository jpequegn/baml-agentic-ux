# Agent-to-Agent (A2A) Negotiation Architecture

## Overview

The A2A negotiation system enables AI agents to discover, negotiate, and compose each other's capabilities dynamically. This architecture implements patterns from Google's A2A protocol, MCP (Model Context Protocol), and FIPA Contract-Net.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Agent Negotiation Layer                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐   │
│  │    Capability    │  │   Negotiation    │  │     Conflict         │   │
│  │    Discovery     │  │    Protocol      │  │    Resolution        │   │
│  │                  │  │                  │  │                      │   │
│  │  - Registry      │  │  - State Machine │  │  - Detection         │   │
│  │  - Matching      │  │  - Proposals     │  │  - Transformation    │   │
│  │  - Indexing      │  │  - Agreements    │  │  - Mediation         │   │
│  └────────┬─────────┘  └────────┬─────────┘  └──────────┬───────────┘   │
│           │                     │                       │               │
│           └─────────────────────┼───────────────────────┘               │
│                                 │                                        │
│                    ┌────────────▼────────────┐                          │
│                    │     Dynamic             │                          │
│                    │     Composition         │                          │
│                    │                         │                          │
│                    │  - Planning             │                          │
│                    │  - Execution            │                          │
│                    │  - Recovery             │                          │
│                    └────────────┬────────────┘                          │
│                                 │                                        │
│                    ┌────────────▼────────────┐                          │
│                    │     Security Layer      │                          │
│                    │                         │                          │
│                    │  - Trust Chain          │                          │
│                    │  - Credentials          │                          │
│                    │  - Permissions          │                          │
│                    └────────────┬────────────┘                          │
│                                 │                                        │
├─────────────────────────────────┼────────────────────────────────────────┤
│                                 │                                        │
│  ┌──────────────────────────────▼────────────────────────────────────┐  │
│  │                   Existing LUI Framework                           │  │
│  │                                                                    │  │
│  │  - InterfaceSchema          - Intent Extraction                   │  │
│  │  - LUI Components           - Response Generation                 │  │
│  │  - Adaptive Personalization - Multi-Modal Output                  │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Agent Identity (`agent_types.py`)

Unique identification for agents using URN format:

```
urn:agent:{provider}:{name}:{version}
```

**Key Types:**
- `AgentIdentity` - Unique agent identifier with metadata
- `AgentCapability` - Capability definition with schemas
- `TrustLevel` - Trust levels (NONE → PRIVILEGED)
- `TrustRequirements` - Requirements for establishing trust

### 2. Agent Card (`agent_card.py`)

A2A-compatible agent advertisement containing:
- Identity information
- Supported protocols (A2A, MCP, OpenAPI, etc.)
- Endpoints with authentication
- Capabilities with schemas
- Compliance tags (GDPR, HIPAA, SOC2)

**Key Classes:**
- `AgentCard` - Complete agent advertisement
- `AgentCardBuilder` - Builder pattern for card creation
- `AgentCardValidator` - Comprehensive validation
- `AgentCardSerializer` - JSON/A2A serialization

### 3. Capability Registry (`capability_registry.py`)

In-memory registry with inverted indices for fast discovery:

```python
# Index Structure
capability_index: dict[str, set[str]]  # capability_type → agent_ids
protocol_index: dict[str, set[str]]    # protocol → agent_ids
provider_index: dict[str, set[str]]    # provider → agent_ids
```

**Operations:**
- Registration with TTL
- Multi-constraint discovery
- Automatic cleanup of expired entries
- Thread-safe with RLock

**Performance:**
- O(1) registration lookups
- O(k) discovery where k = matching capabilities
- Target: <100ms for 1000 agents

### 4. Capability Matcher (`capability_matcher.py`)

Cupid-style multi-factor matching algorithm:

| Factor | Weight | Description |
|--------|--------|-------------|
| Type Compatibility | 40% | Capability type matching |
| Name Similarity | 20% | Jaccard + sequence matching |
| Description Similarity | 20% | Token-based comparison |
| Schema Compatibility | 20% | Input/output schema matching |

**Features:**
- Property-level matching with fuzzy name matching
- Transformation detection and suggestion
- Constraint satisfaction checking
- Adaptation recommendations

### 5. Negotiation State Machine (`negotiation_state.py`)

Contract-Net inspired negotiation protocol:

```
INITIATED → PROPOSAL_SENT → COUNTER_OFFERED → ACCEPTED
                    ↓               ↓            ↓
                REJECTED        REJECTED      (Terminal)
                    ↓               ↓
               (Terminal)      (Terminal)

                    ↓               ↓
                 EXPIRED         EXPIRED
                    ↓               ↓
               (Terminal)      (Terminal)
```

**Key Classes:**
- `NegotiationSession` - Session state and history
- `NegotiationStateMachine` - State transitions with validation
- `NegotiationManager` - High-level negotiation operations
- `ProposalEvaluator` - Proposal scoring and counter-offer generation

### 6. Conflict Resolution (`conflict_resolution.py`)

Handles schema mismatches and negotiation deadlocks:

**Conflict Types:**
- `SCHEMA_MISMATCH` - Type/structure incompatibility
- `CONSTRAINT_VIOLATION` - Cannot meet constraint
- `RESOURCE_CONTENTION` - Exclusive resource needs
- `PRIORITY_CLASH` - Conflicting priorities
- `TRUST_INSUFFICIENT` - Trust level too low
- `SEMANTIC_AMBIGUITY` - Same term, different meanings

**Resolution Strategies:**
- Schema transformation
- Subset selection
- Third-party mediation
- Alternative capability discovery
- Adapter/bridge creation

### 7. Dynamic Composition (`composition.py`)

Runtime capability composition across agents:

**Planning:**
- Goal decomposition into steps
- Agent selection per capability
- Data flow graph construction
- Failure mode analysis

**Execution:**
- Sequential or parallel execution
- Input binding resolution
- Retry with exponential backoff
- Circuit breaker protection

**Recovery:**
- Alternative agent substitution
- Step skipping
- Rollback and retry
- Graceful degradation

### 8. Security Layer (`security.py`)

Trust and authentication framework:

**Credential Types:**
- API_KEY, BEARER_TOKEN, MTLS_CERT
- DID (Decentralized Identifier)
- VC (Verifiable Credential)

**Trust Chain:**
- Direct, delegated, and transitive trust
- Permission tracking
- Expiration handling

## Data Flow

### 1. Discovery Flow

```
Client → DiscoveryRequest
           ↓
       Registry.discover()
           ↓
       Apply constraints
           ↓
       Score and rank
           ↓
       DiscoveryResponse ← [AgentMatch...]
```

### 2. Negotiation Flow

```
Initiator                          Responder
    │                                   │
    ├── PROPOSE ──────────────────────→ │
    │                                   │
    │ ←─────────────── COUNTER ─────────┤
    │                                   │
    ├── COUNTER ──────────────────────→ │
    │                                   │
    │ ←─────────────── ACCEPT ──────────┤
    │                                   │
    ├── FINALIZE ─────────────────────→ │
    │                                   │
    │ ←────────────── Agreement ────────┤
```

### 3. Composition Flow

```
Goal → CompositionPlanner.plan()
            ↓
       CompositionPlan
            ↓
       CompositionExecutor.execute()
            ↓
       For each step:
         ├── Resolve inputs
         ├── Check circuit breaker
         ├── Invoke agent capability
         ├── Handle errors/retry
         └── Store output
            ↓
       CompositionExecution (result)
```

## Module Dependencies

```
agent_types.py (base types)
      ↓
agent_card.py ←───────────────────┐
      ↓                           │
capability_registry.py            │
      ↓                           │
capability_matcher.py ────────────┤
      ↓                           │
negotiation_state.py ─────────────┤
      ↓                           │
conflict_resolution.py ───────────┤
      ↓                           │
composition.py ───────────────────┤
      ↓                           │
security.py ──────────────────────┘
```

## Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Discovery (1000 agents) | <100ms | With inverted indices |
| Schema matching | <10ms | Cached type compatibility |
| Negotiation turn | <500ms | Including validation |
| Composition planning | <1s | Depends on complexity |
| Step execution | <5s | Varies by capability |

## Thread Safety

All registry operations use `RLock` for thread safety:
- Multiple readers allowed
- Exclusive writer access
- Reentrant for nested calls

## Error Handling

All modules follow consistent error handling:
- Specific exception types per module
- Detailed error messages
- Recovery suggestions where applicable
- Logging at appropriate levels

## Extension Points

1. **Custom Discovery Providers** - Add new discovery sources (Consul, etcd)
2. **Protocol Bridges** - Bridge between A2A, MCP, and custom protocols
3. **Negotiation Strategies** - Custom evaluation policies
4. **Resolution Strategies** - Domain-specific conflict resolution
5. **Composition Optimizers** - Custom optimization goals
