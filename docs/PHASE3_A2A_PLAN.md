# Phase 3: Agent-to-Agent Interface Negotiation - Implementation Plan

## Executive Summary

This plan outlines the implementation of agent-to-agent (A2A) interface negotiation capabilities for the BAML Agentic UX framework. Based on comprehensive research into MCP, Google A2A protocol, FIPA Contract-Net, and modern multi-agent architectures, this phase enables AI agents to discover, negotiate, and compose each other's capabilities dynamically.

**Total Estimated Effort**: 45-55 hours
**Sub-phases**: 4 (as recommended in issue #26)
**Risk Level**: High complexity - requires careful security considerations

---

## Research Summary

### Key Standards Analyzed

| Protocol | Purpose | Adoption | Key Feature |
|----------|---------|----------|-------------|
| **MCP** (Model Context Protocol) | Host-to-Server communication | Industry standard (2025) | JSON-RPC 2.0, capability negotiation |
| **Google A2A** | Agent-to-Agent delegation | 50+ partners (Salesforce, SAP) | Agent Cards, task abstraction |
| **FIPA Contract-Net** | Task allocation | Academic/research | CFP-Propose-Accept flow |
| **OpenAI Function Calling** | Tool invocation | Production | Strict schema validation |
| **LangGraph** | Multi-agent orchestration | Production | Graph-based workflows |

### Discovery Mechanisms

| Mechanism | Latency | Scale | Best For |
|-----------|---------|-------|----------|
| Registry-based (A2A/MCP) | 10-100ms | 100K agents | Well-known services |
| DHT (Kademlia) | 50-500ms | 1M+ agents | Decentralized networks |
| mDNS | 1-50ms | 1K agents | Local networks |
| Consul | 10-100ms | 10K agents | Enterprise |

### Security Considerations

| Threat | Impact | Mitigation |
|--------|--------|------------|
| Prompt injection via agents | Critical | Input validation, sandboxing |
| Capability escalation | High | OCAP model, least privilege |
| Memory poisoning | High | Provenance tracking, tenant isolation |
| Cross-agent contamination | Medium | Memory brokers, ABAC policies |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Negotiation Layer                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Capability  │  │  Negotiation │  │   Conflict           │  │
│  │   Discovery   │  │   Protocol   │  │   Resolution         │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│         └─────────────────┼──────────────────────┘              │
│                           │                                      │
│                    ┌──────▼───────┐                             │
│                    │   Security    │                             │
│                    │   Layer       │                             │
│                    └──────┬───────┘                             │
│                           │                                      │
├───────────────────────────┼─────────────────────────────────────┤
│                           │                                      │
│  ┌────────────────────────▼────────────────────────────────┐   │
│  │              Existing LUI Framework                      │   │
│  │  (InterfaceSchema, Components, Intent, Response)        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sub-phase 3a: Capability Advertisement

### Objective
Enable agents to advertise their capabilities in a discoverable format compatible with A2A and MCP standards.

### BAML Type Definitions

```baml
// Core agent identity
class AgentIdentity {
  agent_id string @description("Unique agent identifier (URN format)")
  name string
  version string @description("Semantic version")
  description string
  provider string? @description("Organization/platform providing the agent")
  trust_domain string? @description("SPIFFE trust domain")
}

// Capability definition (A2A-compatible)
class AgentCapability {
  capability_id string
  capability_type CapabilityType
  name string
  description string
  input_schema SchemaDefinition
  output_schema SchemaDefinition
  constraints CapabilityConstraint[]
  performance_hints PerformanceHints?
  trust_requirements TrustRequirements?
}

enum CapabilityType {
  ACTION      // Performs an action
  QUERY       // Retrieves information
  TRANSFORM   // Transforms data
  COMPOSITE   // Combines multiple capabilities
  DELEGATION  // Delegates to other agents
}

class SchemaDefinition {
  type SchemaType
  properties SchemaProperty[]
  required string[]
  examples string[]?
}

enum SchemaType {
  OBJECT
  ARRAY
  STRING
  NUMBER
  BOOLEAN
  NULL
}

class SchemaProperty {
  name string
  type SchemaType
  description string
  format string? @description("date-time, email, uri, etc.")
  enum_values string[]?
  default_value string?
}

class CapabilityConstraint {
  constraint_type ConstraintType
  name string
  value string
  description string?
}

enum ConstraintType {
  RATE_LIMIT        // Max calls per time period
  MAX_INPUT_SIZE    // Maximum input bytes
  TIMEOUT           // Maximum execution time
  REQUIRES_AUTH     // Authentication required
  GEOGRAPHIC        // Geographic restrictions
  COMPLIANCE        // Regulatory compliance (GDPR, HIPAA)
}

class PerformanceHints {
  latency_p50_ms int?
  latency_p95_ms int?
  throughput_per_second int?
  availability_sla float? @description("0.0-1.0, e.g., 0.999 for 99.9%")
}

class TrustRequirements {
  min_trust_level TrustLevel
  required_credentials string[]
  verification_method VerificationMethod
}

enum TrustLevel {
  NONE        // Public access
  BASIC       // API key
  VERIFIED    // Verified identity
  TRUSTED     // Established trust relationship
  PRIVILEGED  // High-privilege operations
}

enum VerificationMethod {
  NONE
  API_KEY
  OAUTH2
  MTLS
  DID_VC      // Decentralized ID + Verifiable Credential
}
```

### Agent Card (A2A-compatible)

```baml
// Complete agent advertisement
class AgentCard {
  identity AgentIdentity
  capabilities AgentCapability[]
  supported_protocols SupportedProtocol[]
  endpoints AgentEndpoint[]
  compliance_tags string[] @description("GDPR, SOC2, HIPAA, etc.")
  metadata AgentMetadata?
}

class SupportedProtocol {
  protocol ProtocolType
  version string
  uri string? @description("Protocol specification URI")
}

enum ProtocolType {
  A2A           // Google Agent-to-Agent
  MCP           // Model Context Protocol
  OPENAPI       // REST API
  JSON_RPC      // Generic JSON-RPC
  CUSTOM        // Custom protocol
}

class AgentEndpoint {
  endpoint_type EndpointType
  url string
  protocol ProtocolType
  authentication AuthMethod?
}

enum EndpointType {
  PRIMARY
  FALLBACK
  HEALTH_CHECK
  DISCOVERY
}

enum AuthMethod {
  NONE
  API_KEY
  BEARER_TOKEN
  OAUTH2
  MTLS
}

class AgentMetadata {
  created_at string @description("ISO 8601 datetime")
  updated_at string
  tags string[]
  documentation_url string?
  support_contact string?
}
```

### Discovery Service

```baml
// Discovery request
class DiscoveryRequest {
  requester AgentIdentity
  required_capabilities string[] @description("Capability types needed")
  constraints DiscoveryConstraint[]
  max_results int?
  timeout_ms int?
}

class DiscoveryConstraint {
  field string @description("AgentCard field to filter on")
  operator FilterOperator
  value string
}

enum FilterOperator {
  EQUALS
  CONTAINS
  GREATER_THAN
  LESS_THAN
  IN
  NOT_IN
}

// Discovery response
class DiscoveryResponse {
  agents AgentMatch[]
  total_count int
  discovery_time_ms int
  source DiscoverySource
}

class AgentMatch {
  agent AgentCard
  match_score float @description("0.0-1.0 relevance score")
  capability_coverage float @description("% of required capabilities matched")
  compatibility_notes string[]?
}

enum DiscoverySource {
  REGISTRY
  CACHE
  PEER_DISCOVERY
  LOCAL
}
```

### Functions

```baml
function AdvertiseCapabilities(
  agent: AgentCard
) -> AdvertisementResult {
  client GPT4o
  prompt #"
    Validate and register the following agent capabilities.

    Agent Card:
    {{ agent }}

    Validate:
    1. All capability schemas are well-formed
    2. Constraints are realistic
    3. Endpoints are properly formatted
    4. Trust requirements are consistent

    {{ ctx.output_format }}
  "#
}

class AdvertisementResult {
  success bool
  agent_id string
  registered_capabilities string[]
  validation_warnings string[]
  expiration_time string @description("ISO 8601 datetime")
}

function DiscoverAgents(
  request: DiscoveryRequest
) -> DiscoveryResponse {
  client GPT4o
  prompt #"
    Find agents matching the discovery request.

    Request:
    {{ request }}

    Search strategy:
    1. Match required capabilities semantically
    2. Filter by constraints
    3. Score by capability coverage and performance
    4. Verify trust requirements can be met

    {{ ctx.output_format }}
  "#
}

function MatchCapabilities(
  required: AgentCapability[],
  offered: AgentCapability[]
) -> CapabilityMatchResult {
  client GPT4o
  prompt #"
    Analyze compatibility between required and offered capabilities.

    Required Capabilities:
    {{ required }}

    Offered Capabilities:
    {{ offered }}

    For each required capability:
    1. Find best matching offered capability
    2. Analyze schema compatibility (input/output)
    3. Check constraint satisfaction
    4. Identify adaptation needs

    {{ ctx.output_format }}
  "#
}

class CapabilityMatchResult {
  overall_compatibility float @description("0.0-1.0")
  matches CapabilityMatch[]
  unmatched_requirements string[]
  adaptation_suggestions Suggestion[]
}

class CapabilityMatch {
  required_capability string
  matched_capability string
  compatibility_score float
  schema_compatibility SchemaCompatibility
  constraint_satisfaction bool
}

class SchemaCompatibility {
  input_compatible bool
  output_compatible bool
  transformations_needed SchemaTransformation[]
}

class SchemaTransformation {
  source_field string
  target_field string
  transformation_type TransformationType
  description string
}

enum TransformationType {
  RENAME
  TYPE_COERCE
  RESTRUCTURE
  DEFAULT_VALUE
  OMIT
}
```

### Python Implementation

```python
# src/agent_negotiation/capability_discovery.py

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import hashlib
import json
from datetime import datetime, timedelta

class CapabilityRegistry:
    """
    In-memory capability registry for agent discovery.
    Production would use distributed registry (Consul, etcd, etc.)
    """

    def __init__(self):
        self._agents: dict[str, AgentCard] = {}
        self._capability_index: dict[str, set[str]] = {}  # capability_type -> agent_ids
        self._expiration_times: dict[str, datetime] = {}

    def register(self, agent_card: AgentCard, ttl_seconds: int = 3600) -> str:
        """Register an agent and its capabilities."""
        agent_id = agent_card.identity.agent_id

        # Store agent card
        self._agents[agent_id] = agent_card
        self._expiration_times[agent_id] = datetime.utcnow() + timedelta(seconds=ttl_seconds)

        # Index capabilities
        for capability in agent_card.capabilities:
            cap_type = capability.capability_type.value
            if cap_type not in self._capability_index:
                self._capability_index[cap_type] = set()
            self._capability_index[cap_type].add(agent_id)

        return agent_id

    def discover(
        self,
        required_capabilities: list[str],
        constraints: list[DiscoveryConstraint] = None,
        max_results: int = 10
    ) -> list[AgentMatch]:
        """Find agents matching requirements."""
        candidates: dict[str, float] = {}

        # Find agents with required capabilities
        for cap_type in required_capabilities:
            if cap_type in self._capability_index:
                for agent_id in self._capability_index[cap_type]:
                    if agent_id not in candidates:
                        candidates[agent_id] = 0.0
                    candidates[agent_id] += 1.0 / len(required_capabilities)

        # Apply constraints
        if constraints:
            candidates = self._apply_constraints(candidates, constraints)

        # Build matches
        matches = []
        for agent_id, score in sorted(candidates.items(), key=lambda x: -x[1]):
            if len(matches) >= max_results:
                break

            agent_card = self._agents[agent_id]
            coverage = self._calculate_coverage(agent_card, required_capabilities)

            matches.append(AgentMatch(
                agent=agent_card,
                match_score=score,
                capability_coverage=coverage,
                compatibility_notes=[]
            ))

        return matches

    def _apply_constraints(
        self,
        candidates: dict[str, float],
        constraints: list[DiscoveryConstraint]
    ) -> dict[str, float]:
        """Filter candidates by constraints."""
        filtered = {}
        for agent_id, score in candidates.items():
            agent = self._agents[agent_id]
            if self._satisfies_constraints(agent, constraints):
                filtered[agent_id] = score
        return filtered

    def _satisfies_constraints(
        self,
        agent: AgentCard,
        constraints: list[DiscoveryConstraint]
    ) -> bool:
        """Check if agent satisfies all constraints."""
        for constraint in constraints:
            value = self._get_field_value(agent, constraint.field)
            if not self._evaluate_constraint(value, constraint):
                return False
        return True

    def _calculate_coverage(
        self,
        agent: AgentCard,
        required: list[str]
    ) -> float:
        """Calculate what percentage of required capabilities are covered."""
        agent_caps = {c.capability_type.value for c in agent.capabilities}
        covered = len(set(required) & agent_caps)
        return covered / len(required) if required else 0.0


class CapabilityMatcher:
    """
    Matches and scores capability compatibility between agents.
    Uses schema matching algorithms (Cupid-style).
    """

    def match(
        self,
        required: list[AgentCapability],
        offered: list[AgentCapability]
    ) -> CapabilityMatchResult:
        """Match required capabilities against offered ones."""
        matches = []
        unmatched = []
        suggestions = []

        for req in required:
            best_match = self._find_best_match(req, offered)

            if best_match:
                matches.append(best_match)
            else:
                unmatched.append(req.capability_id)
                suggestion = self._generate_adaptation_suggestion(req, offered)
                if suggestion:
                    suggestions.append(suggestion)

        overall = sum(m.compatibility_score for m in matches) / len(required) if required else 0.0

        return CapabilityMatchResult(
            overall_compatibility=overall,
            matches=matches,
            unmatched_requirements=unmatched,
            adaptation_suggestions=suggestions
        )

    def _find_best_match(
        self,
        required: AgentCapability,
        offered: list[AgentCapability]
    ) -> Optional[CapabilityMatch]:
        """Find the best matching offered capability."""
        best_score = 0.0
        best_match = None

        for off in offered:
            score = self._calculate_compatibility(required, off)
            if score > best_score:
                best_score = score
                schema_compat = self._check_schema_compatibility(required, off)
                constraint_ok = self._check_constraints(required, off)

                best_match = CapabilityMatch(
                    required_capability=required.capability_id,
                    matched_capability=off.capability_id,
                    compatibility_score=score,
                    schema_compatibility=schema_compat,
                    constraint_satisfaction=constraint_ok
                )

        return best_match if best_score > 0.5 else None  # Threshold

    def _calculate_compatibility(
        self,
        required: AgentCapability,
        offered: AgentCapability
    ) -> float:
        """Calculate compatibility score between two capabilities."""
        score = 0.0

        # Type match (40%)
        if required.capability_type == offered.capability_type:
            score += 0.4

        # Name similarity (20%)
        name_sim = self._string_similarity(required.name, offered.name)
        score += 0.2 * name_sim

        # Description similarity (20%)
        desc_sim = self._string_similarity(required.description, offered.description)
        score += 0.2 * desc_sim

        # Schema compatibility (20%)
        schema_score = self._schema_compatibility_score(required, offered)
        score += 0.2 * schema_score

        return score

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Simple Jaccard similarity for strings."""
        words1 = set(s1.lower().split())
        words2 = set(s2.lower().split())
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0

    def _schema_compatibility_score(
        self,
        required: AgentCapability,
        offered: AgentCapability
    ) -> float:
        """Score schema compatibility."""
        # Compare input schemas
        input_score = self._compare_schemas(
            required.input_schema,
            offered.input_schema
        )

        # Compare output schemas
        output_score = self._compare_schemas(
            offered.output_schema,  # Offered output...
            required.output_schema   # ...must satisfy required output
        )

        return (input_score + output_score) / 2

    def _compare_schemas(
        self,
        source: SchemaDefinition,
        target: SchemaDefinition
    ) -> float:
        """Compare two schemas for compatibility."""
        if source.type != target.type:
            return 0.0

        # Compare properties
        source_props = {p.name: p for p in source.properties}
        target_props = {p.name: p for p in target.properties}

        matched = 0
        for name in target_props:
            if name in source_props:
                if source_props[name].type == target_props[name].type:
                    matched += 1

        total = len(target_props)
        return matched / total if total > 0 else 1.0
```

### Acceptance Criteria

- [ ] AgentCard schema validates against A2A specification
- [ ] Capability registry supports CRUD operations
- [ ] Discovery returns ranked matches with scores
- [ ] Schema matching identifies type/structure compatibility
- [ ] Performance: discovery < 100ms for 1000 agents

---

## Sub-phase 3b: Basic Negotiation Protocol

### Objective
Implement negotiation state machine for agents to propose, counter-offer, and accept/reject capability agreements.

### BAML Type Definitions

```baml
// Negotiation session
class NegotiationSession {
  session_id string
  initiator AgentIdentity
  responder AgentIdentity
  status NegotiationStatus
  created_at string
  updated_at string
  expires_at string
  history NegotiationTurn[]
}

enum NegotiationStatus {
  INITIATED
  PROPOSAL_SENT
  COUNTER_OFFERED
  ACCEPTED
  REJECTED
  EXPIRED
  CANCELLED
  ADAPTED
}

class NegotiationTurn {
  turn_number int
  actor string @description("Agent ID of the actor")
  action NegotiationAction
  proposal NegotiationProposal?
  timestamp string
  rationale string?
}

enum NegotiationAction {
  PROPOSE
  COUNTER
  ACCEPT
  REJECT
  WITHDRAW
  TIMEOUT
}

// Proposal structure
class NegotiationProposal {
  proposal_id string
  requested_capabilities CapabilityRequest[]
  offered_capabilities CapabilityOffer[]
  terms NegotiationTerms
  validity_period_seconds int
}

class CapabilityRequest {
  capability_type string
  required_schema SchemaDefinition?
  constraints CapabilityConstraint[]
  priority RequestPriority
}

enum RequestPriority {
  REQUIRED    // Must have
  PREFERRED   // Want but negotiable
  OPTIONAL    // Nice to have
}

class CapabilityOffer {
  capability AgentCapability
  conditions OfferCondition[]
  rate_limit RateLimit?
}

class OfferCondition {
  condition_type ConditionType
  description string
  value string
}

enum ConditionType {
  AUTHENTICATION_REQUIRED
  RATE_LIMIT
  DATA_RETENTION
  AUDIT_LOGGING
  GEOGRAPHIC_RESTRICTION
  TIME_WINDOW
}

class RateLimit {
  requests_per_second int?
  requests_per_minute int?
  requests_per_hour int?
  burst_limit int?
}

class NegotiationTerms {
  duration_seconds int @description("How long the agreement lasts")
  auto_renew bool
  termination_conditions string[]
  dispute_resolution string?
}

// Negotiation result
class NegotiationResult {
  session_id string
  status NegotiationStatus
  agreement Agreement?
  rejection_reason string?
  final_proposal NegotiationProposal?
}

class Agreement {
  agreement_id string
  parties AgentIdentity[]
  capabilities_granted GrantedCapability[]
  terms NegotiationTerms
  signature_method string
  created_at string
  expires_at string
}

class GrantedCapability {
  capability AgentCapability
  grantee string @description("Agent ID receiving access")
  grantor string @description("Agent ID providing access")
  access_token string? @description("Credential for access")
  conditions OfferCondition[]
}
```

### Contract-Net Protocol Implementation

```baml
// Call for Proposals (CFP)
class CallForProposals {
  cfp_id string
  issuer AgentIdentity
  task_specification TaskSpecification
  deadline string @description("ISO 8601 deadline for proposals")
  selection_criteria SelectionCriteria[]
}

class TaskSpecification {
  task_type string
  description string
  required_capabilities string[]
  input_schema SchemaDefinition
  expected_output_schema SchemaDefinition
  constraints TaskConstraint[]
}

class TaskConstraint {
  constraint_type string
  value string
  weight float @description("Importance 0.0-1.0")
}

class SelectionCriteria {
  criterion CriterionType
  weight float @description("0.0-1.0, weights must sum to 1.0")
  direction OptimizationDirection
}

enum CriterionType {
  COST
  LATENCY
  QUALITY
  RELIABILITY
  TRUST_LEVEL
}

enum OptimizationDirection {
  MINIMIZE
  MAXIMIZE
}

// Proposal response
class ContractProposal {
  proposal_id string
  cfp_id string
  proposer AgentIdentity
  offered_capabilities AgentCapability[]
  cost CostEstimate?
  estimated_latency_ms int?
  quality_score float?
  validity_until string
}

class CostEstimate {
  amount float
  currency string
  billing_model BillingModel
}

enum BillingModel {
  PER_REQUEST
  PER_TOKEN
  FLAT_RATE
  TIERED
}

// Contract award
class ContractAward {
  award_id string
  cfp_id string
  winning_proposal_id string
  contractor AgentIdentity
  agreement Agreement
}
```

### Functions

```baml
function InitiateNegotiation(
  initiator: AgentIdentity,
  target: AgentIdentity,
  proposal: NegotiationProposal
) -> NegotiationSession {
  client GPT4o
  prompt #"
    Initialize a negotiation session between agents.

    Initiator: {{ initiator }}
    Target: {{ target }}
    Initial Proposal: {{ proposal }}

    Create session with:
    1. Unique session ID
    2. Initial status PROPOSAL_SENT
    3. First turn recorded
    4. Appropriate expiration time

    {{ ctx.output_format }}
  "#
}

function EvaluateProposal(
  session: NegotiationSession,
  proposal: NegotiationProposal,
  evaluator_capabilities: AgentCapability[],
  evaluation_policy: EvaluationPolicy
) -> ProposalEvaluation {
  client GPT4o
  prompt #"
    Evaluate a negotiation proposal from another agent.

    Session Context: {{ session }}
    Proposal to Evaluate: {{ proposal }}
    Our Capabilities: {{ evaluator_capabilities }}
    Evaluation Policy: {{ evaluation_policy }}

    Determine:
    1. Can we satisfy the requested capabilities?
    2. Are the terms acceptable?
    3. Should we accept, reject, or counter-offer?
    4. If counter-offering, what modifications?

    {{ ctx.output_format }}
  "#
}

class EvaluationPolicy {
  min_acceptable_terms MinimumTerms
  negotiation_strategy NegotiationStrategy
  max_counter_offers int
  auto_accept_threshold float @description("Accept if score > threshold")
}

class MinimumTerms {
  min_duration_seconds int
  max_rate_limit RateLimit
  required_conditions ConditionType[]
}

enum NegotiationStrategy {
  COOPERATIVE     // Maximize mutual benefit
  COMPETITIVE     // Maximize own benefit
  PRINCIPLED      // Fair, objective criteria
  ACCOMMODATING   // Prioritize relationship
}

class ProposalEvaluation {
  decision NegotiationAction
  score float @description("0.0-1.0 attractiveness")
  can_satisfy bool
  gap_analysis GapAnalysis?
  counter_proposal NegotiationProposal?
  rationale string
}

class GapAnalysis {
  unmet_requirements string[]
  constraint_violations string[]
  suggested_modifications Suggestion[]
}

function GenerateCounterProposal(
  original: NegotiationProposal,
  gaps: GapAnalysis,
  our_capabilities: AgentCapability[],
  strategy: NegotiationStrategy
) -> NegotiationProposal {
  client GPT4o
  prompt #"
    Generate a counter-proposal based on negotiation gaps.

    Original Proposal: {{ original }}
    Gap Analysis: {{ gaps }}
    Our Capabilities: {{ our_capabilities }}
    Strategy: {{ strategy }}

    Create counter-proposal that:
    1. Addresses as many gaps as possible
    2. Maintains acceptable terms for us
    3. Follows the negotiation strategy
    4. Moves toward agreement

    {{ ctx.output_format }}
  "#
}

function FinalizeAgreement(
  session: NegotiationSession,
  accepted_proposal: NegotiationProposal
) -> Agreement {
  client GPT4o
  prompt #"
    Finalize the negotiation into a binding agreement.

    Session: {{ session }}
    Accepted Proposal: {{ accepted_proposal }}

    Create agreement with:
    1. Unique agreement ID
    2. Both parties listed
    3. Granted capabilities with access details
    4. Terms and conditions
    5. Expiration handling

    {{ ctx.output_format }}
  "#
}

// Contract-Net functions
function IssueCallForProposals(
  issuer: AgentIdentity,
  task: TaskSpecification,
  target_agents: AgentIdentity[]?,
  deadline_seconds: int
) -> CallForProposals {
  client GPT4o
  prompt #"
    Issue a Call for Proposals for a task.

    Issuer: {{ issuer }}
    Task: {{ task }}
    Target Agents: {{ target_agents }}
    Deadline: {{ deadline_seconds }} seconds from now

    Create CFP with:
    1. Clear task specification
    2. Selection criteria and weights
    3. Appropriate deadline

    {{ ctx.output_format }}
  "#
}

function EvaluateBids(
  cfp: CallForProposals,
  proposals: ContractProposal[]
) -> BidEvaluation {
  client GPT4o
  prompt #"
    Evaluate proposals received for a CFP.

    Call for Proposals: {{ cfp }}
    Received Proposals: {{ proposals }}

    For each proposal:
    1. Score against each criterion
    2. Calculate weighted total
    3. Check capability satisfaction
    4. Rank proposals

    {{ ctx.output_format }}
  "#
}

class BidEvaluation {
  cfp_id string
  evaluated_proposals EvaluatedProposal[]
  recommended_winner string? @description("Proposal ID")
  recommendation_rationale string
}

class EvaluatedProposal {
  proposal_id string
  proposer_id string
  criterion_scores CriterionScore[]
  total_score float
  satisfies_requirements bool
  rank int
}

class CriterionScore {
  criterion CriterionType
  raw_value float
  normalized_score float @description("0.0-1.0")
  weighted_score float
}
```

### Python Implementation

```python
# src/agent_negotiation/negotiation_protocol.py

from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum
import uuid
from datetime import datetime, timedelta

class NegotiationStateMachine:
    """
    State machine for managing negotiation sessions.
    Implements Contract-Net inspired protocol.
    """

    VALID_TRANSITIONS = {
        NegotiationStatus.INITIATED: [
            NegotiationStatus.PROPOSAL_SENT,
            NegotiationStatus.CANCELLED
        ],
        NegotiationStatus.PROPOSAL_SENT: [
            NegotiationStatus.COUNTER_OFFERED,
            NegotiationStatus.ACCEPTED,
            NegotiationStatus.REJECTED,
            NegotiationStatus.EXPIRED
        ],
        NegotiationStatus.COUNTER_OFFERED: [
            NegotiationStatus.COUNTER_OFFERED,  # Multiple counter-offers
            NegotiationStatus.ACCEPTED,
            NegotiationStatus.REJECTED,
            NegotiationStatus.EXPIRED
        ],
        NegotiationStatus.ACCEPTED: [],  # Terminal
        NegotiationStatus.REJECTED: [],  # Terminal
        NegotiationStatus.EXPIRED: [],   # Terminal
        NegotiationStatus.CANCELLED: [], # Terminal
        NegotiationStatus.ADAPTED: [],   # Terminal
    }

    def __init__(self, session: NegotiationSession):
        self.session = session
        self._on_transition_callbacks: list[Callable] = []

    def can_transition(self, target: NegotiationStatus) -> bool:
        """Check if transition is valid."""
        return target in self.VALID_TRANSITIONS.get(self.session.status, [])

    def transition(
        self,
        target: NegotiationStatus,
        actor: str,
        action: NegotiationAction,
        proposal: Optional[NegotiationProposal] = None,
        rationale: Optional[str] = None
    ) -> bool:
        """Execute state transition with turn recording."""
        if not self.can_transition(target):
            return False

        # Record turn
        turn = NegotiationTurn(
            turn_number=len(self.session.history) + 1,
            actor=actor,
            action=action,
            proposal=proposal,
            timestamp=datetime.utcnow().isoformat(),
            rationale=rationale
        )
        self.session.history.append(turn)

        # Update session
        old_status = self.session.status
        self.session.status = target
        self.session.updated_at = datetime.utcnow().isoformat()

        # Notify callbacks
        for callback in self._on_transition_callbacks:
            callback(old_status, target, turn)

        return True

    def on_transition(self, callback: Callable):
        """Register callback for state transitions."""
        self._on_transition_callbacks.append(callback)


class NegotiationManager:
    """
    Manages multiple negotiation sessions and provides
    high-level negotiation operations.
    """

    def __init__(
        self,
        our_identity: AgentIdentity,
        our_capabilities: list[AgentCapability],
        evaluation_policy: EvaluationPolicy
    ):
        self.identity = our_identity
        self.capabilities = our_capabilities
        self.policy = evaluation_policy
        self._sessions: dict[str, NegotiationStateMachine] = {}

    def initiate(
        self,
        target: AgentIdentity,
        requested_capabilities: list[CapabilityRequest],
        offered_capabilities: list[CapabilityOffer],
        terms: NegotiationTerms
    ) -> NegotiationSession:
        """Start a new negotiation."""
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()

        proposal = NegotiationProposal(
            proposal_id=str(uuid.uuid4()),
            requested_capabilities=requested_capabilities,
            offered_capabilities=offered_capabilities,
            terms=terms,
            validity_period_seconds=3600
        )

        session = NegotiationSession(
            session_id=session_id,
            initiator=self.identity,
            responder=target,
            status=NegotiationStatus.INITIATED,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            expires_at=(now + timedelta(hours=24)).isoformat(),
            history=[]
        )

        sm = NegotiationStateMachine(session)
        sm.transition(
            NegotiationStatus.PROPOSAL_SENT,
            self.identity.agent_id,
            NegotiationAction.PROPOSE,
            proposal=proposal
        )

        self._sessions[session_id] = sm
        return session

    def receive_proposal(
        self,
        session_id: str,
        proposal: NegotiationProposal
    ) -> ProposalEvaluation:
        """Evaluate and respond to a received proposal."""
        sm = self._sessions.get(session_id)
        if not sm:
            raise ValueError(f"Unknown session: {session_id}")

        # Evaluate proposal
        evaluation = self._evaluate(proposal)

        if evaluation.decision == NegotiationAction.ACCEPT:
            sm.transition(
                NegotiationStatus.ACCEPTED,
                self.identity.agent_id,
                NegotiationAction.ACCEPT,
                rationale=evaluation.rationale
            )
        elif evaluation.decision == NegotiationAction.REJECT:
            sm.transition(
                NegotiationStatus.REJECTED,
                self.identity.agent_id,
                NegotiationAction.REJECT,
                rationale=evaluation.rationale
            )
        elif evaluation.decision == NegotiationAction.COUNTER:
            sm.transition(
                NegotiationStatus.COUNTER_OFFERED,
                self.identity.agent_id,
                NegotiationAction.COUNTER,
                proposal=evaluation.counter_proposal,
                rationale=evaluation.rationale
            )

        return evaluation

    def _evaluate(self, proposal: NegotiationProposal) -> ProposalEvaluation:
        """Internal proposal evaluation logic."""
        # Check if we can satisfy requirements
        can_satisfy = self._can_satisfy(proposal.requested_capabilities)

        # Score the proposal
        score = self._score_proposal(proposal)

        # Decide based on policy
        if not can_satisfy:
            return ProposalEvaluation(
                decision=NegotiationAction.REJECT,
                score=score,
                can_satisfy=False,
                rationale="Cannot satisfy requested capabilities"
            )

        if score >= self.policy.auto_accept_threshold:
            return ProposalEvaluation(
                decision=NegotiationAction.ACCEPT,
                score=score,
                can_satisfy=True,
                rationale="Proposal meets acceptance threshold"
            )

        # Generate counter-proposal
        counter = self._generate_counter(proposal)
        return ProposalEvaluation(
            decision=NegotiationAction.COUNTER,
            score=score,
            can_satisfy=True,
            counter_proposal=counter,
            rationale="Counter-offering with modified terms"
        )

    def _can_satisfy(self, requests: list[CapabilityRequest]) -> bool:
        """Check if we can satisfy capability requests."""
        our_types = {c.capability_type.value for c in self.capabilities}

        for req in requests:
            if req.priority == RequestPriority.REQUIRED:
                if req.capability_type not in our_types:
                    return False
        return True

    def _score_proposal(self, proposal: NegotiationProposal) -> float:
        """Score a proposal based on policy."""
        score = 0.0

        # Term attractiveness (40%)
        term_score = self._score_terms(proposal.terms)
        score += 0.4 * term_score

        # Offered capabilities value (30%)
        offer_score = self._score_offers(proposal.offered_capabilities)
        score += 0.3 * offer_score

        # Request burden (30%)
        request_burden = self._score_requests(proposal.requested_capabilities)
        score += 0.3 * (1.0 - request_burden)  # Lower burden = higher score

        return score

    def finalize(self, session_id: str) -> Agreement:
        """Finalize an accepted negotiation into an agreement."""
        sm = self._sessions.get(session_id)
        if not sm or sm.session.status != NegotiationStatus.ACCEPTED:
            raise ValueError("Session not in ACCEPTED state")

        # Get the accepted proposal
        accepted_proposal = None
        for turn in reversed(sm.session.history):
            if turn.proposal:
                accepted_proposal = turn.proposal
                break

        if not accepted_proposal:
            raise ValueError("No proposal found in session history")

        # Create agreement
        agreement = Agreement(
            agreement_id=str(uuid.uuid4()),
            parties=[sm.session.initiator, sm.session.responder],
            capabilities_granted=self._create_grants(accepted_proposal),
            terms=accepted_proposal.terms,
            signature_method="none",  # TODO: Implement signing
            created_at=datetime.utcnow().isoformat(),
            expires_at=(datetime.utcnow() + timedelta(
                seconds=accepted_proposal.terms.duration_seconds
            )).isoformat()
        )

        return agreement
```

### Acceptance Criteria

- [ ] Negotiation state machine enforces valid transitions
- [ ] Proposal evaluation scores against policy thresholds
- [ ] Counter-proposal generation addresses gaps
- [ ] Contract-Net CFP flow works end-to-end
- [ ] Agreement finalization creates valid grants
- [ ] Session history provides audit trail

---

## Sub-phase 3c: Conflict Resolution

### Objective
Handle schema mismatches, constraint conflicts, and negotiation deadlocks with intelligent resolution strategies.

### BAML Type Definitions

```baml
// Conflict detection
class ConflictAnalysis {
  conflicts Conflict[]
  severity ConflictSeverity
  resolvable bool
  resolution_paths ResolutionPath[]
}

class Conflict {
  conflict_id string
  conflict_type ConflictType
  description string
  source_element string
  target_element string
  severity ConflictSeverity
}

enum ConflictType {
  SCHEMA_MISMATCH       // Type/structure incompatibility
  CONSTRAINT_VIOLATION  // Cannot meet constraint
  RESOURCE_CONTENTION   // Both need exclusive resource
  PRIORITY_CLASH        // Conflicting priorities
  TRUST_INSUFFICIENT    // Trust level too low
  SEMANTIC_AMBIGUITY    // Same term, different meanings
}

enum ConflictSeverity {
  LOW         // Minor, auto-resolvable
  MEDIUM      // Requires adaptation
  HIGH        // May require human intervention
  CRITICAL    // Blocks negotiation
}

class ResolutionPath {
  path_id string
  strategy ResolutionStrategy
  steps ResolutionStep[]
  estimated_success_probability float
  side_effects string[]
}

enum ResolutionStrategy {
  TRANSFORM           // Convert one format to another
  SUBSET              // Use common subset
  MEDIATE             // Third-party mediation
  ESCALATE            // Human decision
  ALTERNATIVE         // Find different capability
  NEGOTIATE_TERMS     // Adjust terms
  BRIDGE              // Create adapter
}

class ResolutionStep {
  step_number int
  action string
  input_type string
  output_type string
  reversible bool
}

// Schema transformation
class SchemaTransformPlan {
  source_schema SchemaDefinition
  target_schema SchemaDefinition
  transformations FieldTransformation[]
  data_loss_risk DataLossRisk
  reversible bool
}

class FieldTransformation {
  source_path string @description("JSONPath to source field")
  target_path string @description("JSONPath to target field")
  transform_type FieldTransformType
  transform_function string? @description("Custom transform logic")
  default_value string?
}

enum FieldTransformType {
  COPY              // Direct copy
  RENAME            // Change field name
  TYPE_COERCE       // Convert type (string->int)
  RESTRUCTURE       // Nested -> flat or vice versa
  AGGREGATE         // Combine multiple fields
  SPLIT             // Split into multiple fields
  COMPUTE           // Derived value
  DEFAULT           // Use default if missing
  OMIT              // Drop field
}

enum DataLossRisk {
  NONE              // Lossless transformation
  LOW               // Minor precision loss
  MEDIUM            // Some data may be lost
  HIGH              // Significant data loss
}

// Mediation
class MediationRequest {
  session_id string
  conflict ConflictAnalysis
  party_a_position NegotiationProposal
  party_b_position NegotiationProposal
  mediation_style MediationStyle
}

enum MediationStyle {
  FACILITATIVE      // Help parties find solution
  EVALUATIVE        // Suggest/evaluate solutions
  TRANSFORMATIVE    // Change relationship dynamics
  DIRECTIVE         // Provide binding decision
}

class MediationResult {
  resolved bool
  compromise_proposal NegotiationProposal?
  accepted_by string[] @description("Agent IDs accepting compromise")
  remaining_conflicts Conflict[]
  mediator_notes string
}
```

### Functions

```baml
function AnalyzeConflicts(
  proposal_a: NegotiationProposal,
  proposal_b: NegotiationProposal
) -> ConflictAnalysis {
  client GPT4o
  prompt #"
    Analyze conflicts between two negotiation proposals.

    Proposal A: {{ proposal_a }}
    Proposal B: {{ proposal_b }}

    Identify:
    1. Schema mismatches (type, structure differences)
    2. Constraint violations (incompatible limits)
    3. Resource contentions (exclusive access needs)
    4. Priority clashes (conflicting requirements)
    5. Trust level gaps

    For each conflict, assess severity and suggest resolution paths.

    {{ ctx.output_format }}
  "#
}

function GenerateTransformPlan(
  source: SchemaDefinition,
  target: SchemaDefinition
) -> SchemaTransformPlan {
  client GPT4o
  prompt #"
    Create a transformation plan to convert source schema to target.

    Source Schema: {{ source }}
    Target Schema: {{ target }}

    For each target field:
    1. Find matching source field
    2. Determine transformation type
    3. Specify transform function if needed
    4. Assess data loss risk

    {{ ctx.output_format }}
  "#
}

function ApplyTransformation(
  data: string,
  plan: SchemaTransformPlan
) -> TransformResult {
  client GPT4o
  prompt #"
    Apply transformation plan to data.

    Input Data (JSON): {{ data }}
    Transform Plan: {{ plan }}

    Execute each transformation step and produce output.
    Track any data loss or errors.

    {{ ctx.output_format }}
  "#
}

class TransformResult {
  success bool
  output_data string @description("Transformed JSON")
  warnings string[]
  data_loss_occurred bool
  lost_fields string[]
}

function MediateConflict(
  request: MediationRequest
) -> MediationResult {
  client GPT4o
  prompt #"
    Mediate between conflicting parties.

    Mediation Request: {{ request }}

    Using {{ request.mediation_style }} style:
    1. Identify common ground
    2. Find creative compromises
    3. Propose fair resolution
    4. Note any unresolvable issues

    {{ ctx.output_format }}
  "#
}

function ResolveDeadlock(
  session: NegotiationSession,
  deadlock_turns: int
) -> DeadlockResolution {
  client GPT4o
  prompt #"
    Resolve a negotiation deadlock.

    Session History: {{ session }}
    Turns Without Progress: {{ deadlock_turns }}

    Strategies to consider:
    1. Identify blocking issues
    2. Suggest package deals
    3. Propose side payments/trade-offs
    4. Recommend escalation if needed

    {{ ctx.output_format }}
  "#
}

class DeadlockResolution {
  resolution_possible bool
  strategy ResolutionStrategy
  proposal NegotiationProposal?
  explanation string
  escalation_needed bool
  escalation_reason string?
}
```

### Python Implementation

```python
# src/agent_negotiation/conflict_resolution.py

from dataclasses import dataclass
from typing import Optional
import json

class ConflictDetector:
    """
    Detects conflicts between schemas, constraints, and proposals.
    """

    def detect_schema_conflicts(
        self,
        source: SchemaDefinition,
        target: SchemaDefinition
    ) -> list[Conflict]:
        """Detect schema incompatibilities."""
        conflicts = []

        # Type mismatch at root level
        if source.type != target.type:
            conflicts.append(Conflict(
                conflict_id=f"type-{source.type}-{target.type}",
                conflict_type=ConflictType.SCHEMA_MISMATCH,
                description=f"Root type mismatch: {source.type} vs {target.type}",
                source_element="root",
                target_element="root",
                severity=ConflictSeverity.HIGH
            ))
            return conflicts  # Can't proceed with field comparison

        # Property conflicts
        source_props = {p.name: p for p in source.properties}
        target_props = {p.name: p for p in target.properties}

        # Missing required fields
        for name in target.required:
            if name not in source_props:
                conflicts.append(Conflict(
                    conflict_id=f"missing-{name}",
                    conflict_type=ConflictType.SCHEMA_MISMATCH,
                    description=f"Required field '{name}' missing in source",
                    source_element="properties",
                    target_element=name,
                    severity=ConflictSeverity.HIGH
                ))

        # Type mismatches
        for name, target_prop in target_props.items():
            if name in source_props:
                source_prop = source_props[name]
                if source_prop.type != target_prop.type:
                    conflicts.append(Conflict(
                        conflict_id=f"type-mismatch-{name}",
                        conflict_type=ConflictType.SCHEMA_MISMATCH,
                        description=f"Field '{name}': {source_prop.type} vs {target_prop.type}",
                        source_element=name,
                        target_element=name,
                        severity=self._assess_type_coercion_severity(
                            source_prop.type, target_prop.type
                        )
                    ))

        return conflicts

    def _assess_type_coercion_severity(
        self,
        source_type: SchemaType,
        target_type: SchemaType
    ) -> ConflictSeverity:
        """Assess how severe a type coercion would be."""
        # Safe coercions
        safe_coercions = {
            (SchemaType.NUMBER, SchemaType.STRING),
            (SchemaType.BOOLEAN, SchemaType.STRING),
        }

        if (source_type, target_type) in safe_coercions:
            return ConflictSeverity.LOW

        # Lossy but possible
        if source_type == SchemaType.STRING:
            return ConflictSeverity.MEDIUM

        return ConflictSeverity.HIGH


class SchemaTransformer:
    """
    Transforms data between incompatible schemas.
    """

    def create_plan(
        self,
        source: SchemaDefinition,
        target: SchemaDefinition
    ) -> SchemaTransformPlan:
        """Create transformation plan."""
        transformations = []
        data_loss_risk = DataLossRisk.NONE

        source_props = {p.name: p for p in source.properties}
        target_props = {p.name: p for p in target.properties}

        for target_name, target_prop in target_props.items():
            if target_name in source_props:
                source_prop = source_props[target_name]

                if source_prop.type == target_prop.type:
                    # Direct copy
                    transformations.append(FieldTransformation(
                        source_path=f"$.{target_name}",
                        target_path=f"$.{target_name}",
                        transform_type=FieldTransformType.COPY
                    ))
                else:
                    # Type coercion
                    transformations.append(FieldTransformation(
                        source_path=f"$.{target_name}",
                        target_path=f"$.{target_name}",
                        transform_type=FieldTransformType.TYPE_COERCE,
                        transform_function=self._get_coercion_function(
                            source_prop.type, target_prop.type
                        )
                    ))
                    data_loss_risk = max(data_loss_risk, DataLossRisk.MEDIUM)
            else:
                # Need default or compute
                if target_prop.default_value:
                    transformations.append(FieldTransformation(
                        source_path="",
                        target_path=f"$.{target_name}",
                        transform_type=FieldTransformType.DEFAULT,
                        default_value=target_prop.default_value
                    ))
                else:
                    # Try to find similar field (fuzzy match)
                    similar = self._find_similar_field(target_name, source_props)
                    if similar:
                        transformations.append(FieldTransformation(
                            source_path=f"$.{similar}",
                            target_path=f"$.{target_name}",
                            transform_type=FieldTransformType.RENAME
                        ))
                    else:
                        data_loss_risk = max(data_loss_risk, DataLossRisk.HIGH)

        return SchemaTransformPlan(
            source_schema=source,
            target_schema=target,
            transformations=transformations,
            data_loss_risk=data_loss_risk,
            reversible=(data_loss_risk == DataLossRisk.NONE)
        )

    def apply(self, data: dict, plan: SchemaTransformPlan) -> TransformResult:
        """Apply transformation plan to data."""
        output = {}
        warnings = []
        lost_fields = []

        for transform in plan.transformations:
            try:
                if transform.transform_type == FieldTransformType.COPY:
                    output[self._extract_field_name(transform.target_path)] = \
                        self._get_by_path(data, transform.source_path)

                elif transform.transform_type == FieldTransformType.RENAME:
                    output[self._extract_field_name(transform.target_path)] = \
                        self._get_by_path(data, transform.source_path)

                elif transform.transform_type == FieldTransformType.TYPE_COERCE:
                    value = self._get_by_path(data, transform.source_path)
                    coerced = self._coerce_type(value, transform.transform_function)
                    output[self._extract_field_name(transform.target_path)] = coerced

                elif transform.transform_type == FieldTransformType.DEFAULT:
                    output[self._extract_field_name(transform.target_path)] = \
                        transform.default_value

            except Exception as e:
                warnings.append(f"Transform failed for {transform.target_path}: {e}")

        return TransformResult(
            success=len(warnings) == 0,
            output_data=json.dumps(output),
            warnings=warnings,
            data_loss_occurred=plan.data_loss_risk != DataLossRisk.NONE,
            lost_fields=lost_fields
        )


class ConflictMediator:
    """
    Mediates conflicts between negotiating parties.
    """

    def mediate(self, request: MediationRequest) -> MediationResult:
        """Attempt to mediate conflict."""
        conflicts = request.conflict.conflicts

        # Sort by severity
        critical = [c for c in conflicts if c.severity == ConflictSeverity.CRITICAL]
        high = [c for c in conflicts if c.severity == ConflictSeverity.HIGH]

        if critical:
            # Cannot auto-resolve critical conflicts
            return MediationResult(
                resolved=False,
                remaining_conflicts=critical,
                mediator_notes="Critical conflicts require manual intervention"
            )

        # Try to generate compromise
        compromise = self._generate_compromise(
            request.party_a_position,
            request.party_b_position,
            request.mediation_style
        )

        if compromise:
            return MediationResult(
                resolved=True,
                compromise_proposal=compromise,
                accepted_by=[],  # Parties haven't accepted yet
                remaining_conflicts=high,
                mediator_notes="Compromise proposal generated"
            )

        return MediationResult(
            resolved=False,
            remaining_conflicts=conflicts,
            mediator_notes="Could not find acceptable compromise"
        )

    def _generate_compromise(
        self,
        pos_a: NegotiationProposal,
        pos_b: NegotiationProposal,
        style: MediationStyle
    ) -> Optional[NegotiationProposal]:
        """Generate a compromise proposal."""
        # Split the difference on terms
        duration_a = pos_a.terms.duration_seconds
        duration_b = pos_b.terms.duration_seconds
        compromise_duration = (duration_a + duration_b) // 2

        # Take intersection of requested capabilities (REQUIRED only)
        required_a = {r.capability_type for r in pos_a.requested_capabilities
                     if r.priority == RequestPriority.REQUIRED}
        required_b = {r.capability_type for r in pos_b.requested_capabilities
                     if r.priority == RequestPriority.REQUIRED}
        common_required = required_a & required_b

        if not common_required:
            return None  # No common ground

        # Build compromise
        compromise_requests = [
            CapabilityRequest(
                capability_type=cap_type,
                priority=RequestPriority.REQUIRED,
                constraints=[]
            )
            for cap_type in common_required
        ]

        return NegotiationProposal(
            proposal_id=str(uuid.uuid4()),
            requested_capabilities=compromise_requests,
            offered_capabilities=[],  # To be filled by accepting party
            terms=NegotiationTerms(
                duration_seconds=compromise_duration,
                auto_renew=False,
                termination_conditions=["mutual agreement"]
            ),
            validity_period_seconds=3600
        )
```

### Acceptance Criteria

- [ ] Schema conflicts detected accurately
- [ ] Transformation plans handle common type coercions
- [ ] Data loss risk assessed correctly
- [ ] Mediation generates viable compromises
- [ ] Deadlock detection triggers after N turns
- [ ] Critical conflicts escalate appropriately

---

## Sub-phase 3d: Dynamic Composition

### Objective
Enable runtime capability composition where agents can combine their capabilities to fulfill complex requests.

### BAML Type Definitions

```baml
// Composition planning
class CompositionPlan {
  plan_id string
  goal string
  steps CompositionStep[]
  data_flow DataFlowEdge[]
  estimated_latency_ms int
  failure_modes FailureMode[]
}

class CompositionStep {
  step_id string
  agent AgentIdentity
  capability AgentCapability
  input_bindings InputBinding[]
  output_name string
  timeout_ms int
  retry_policy RetryPolicy?
}

class InputBinding {
  parameter_name string
  source InputSource
  source_reference string @description("Step ID or literal value")
}

enum InputSource {
  LITERAL         // Hardcoded value
  PREVIOUS_STEP   // Output from earlier step
  USER_INPUT      // From original request
  CONTEXT         // From session context
}

class DataFlowEdge {
  from_step string
  to_step string
  data_path string @description("JSONPath to data")
}

class RetryPolicy {
  max_retries int
  backoff_strategy BackoffStrategy
  retry_on string[] @description("Error types to retry")
}

enum BackoffStrategy {
  FIXED
  LINEAR
  EXPONENTIAL
}

class FailureMode {
  step_id string
  failure_type string
  impact string
  mitigation string
}

// Composition execution
class CompositionExecution {
  execution_id string
  plan_id string
  status ExecutionStatus
  started_at string
  completed_at string?
  step_results StepResult[]
  final_output string?
  error CompositionError?
}

enum ExecutionStatus {
  PENDING
  RUNNING
  COMPLETED
  FAILED
  CANCELLED
  TIMEOUT
}

class StepResult {
  step_id string
  status StepStatus
  output string?
  latency_ms int
  error string?
  retries int
}

enum StepStatus {
  PENDING
  RUNNING
  COMPLETED
  FAILED
  SKIPPED
}

class CompositionError {
  step_id string
  error_type string
  message string
  recoverable bool
  recovery_suggestion string?
}

// Orchestration
class OrchestrationConfig {
  parallel_execution bool
  max_concurrent_steps int
  global_timeout_ms int
  circuit_breaker CircuitBreakerConfig?
}

class CircuitBreakerConfig {
  failure_threshold int @description("Failures before opening")
  recovery_timeout_ms int @description("Time before retry")
  half_open_requests int @description("Requests to test recovery")
}
```

### Functions

```baml
function PlanComposition(
  goal: string,
  available_agents: AgentCard[],
  constraints: CompositionConstraint[]
) -> CompositionPlan {
  client GPT4o
  prompt #"
    Plan a capability composition to achieve a goal.

    Goal: {{ goal }}
    Available Agents: {{ available_agents }}
    Constraints: {{ constraints }}

    Create a plan that:
    1. Identifies required capabilities
    2. Maps capabilities to agents
    3. Orders steps for data dependencies
    4. Binds inputs/outputs between steps
    5. Estimates total latency
    6. Identifies potential failure modes

    {{ ctx.output_format }}
  "#
}

class CompositionConstraint {
  constraint_type string
  value string
}

function OptimizePlan(
  plan: CompositionPlan,
  optimization_goals: OptimizationGoal[]
) -> CompositionPlan {
  client GPT4o
  prompt #"
    Optimize the composition plan.

    Current Plan: {{ plan }}
    Goals: {{ optimization_goals }}

    Optimizations to consider:
    1. Parallelize independent steps
    2. Reduce data transfer
    3. Use caching where possible
    4. Add fallback paths

    {{ ctx.output_format }}
  "#
}

enum OptimizationGoal {
  MINIMIZE_LATENCY
  MAXIMIZE_RELIABILITY
  MINIMIZE_COST
  MINIMIZE_DATA_TRANSFER
}

function ExecuteComposition(
  plan: CompositionPlan,
  inputs: string,
  config: OrchestrationConfig
) -> CompositionExecution {
  client GPT4o
  prompt #"
    Execute a composition plan.

    Plan: {{ plan }}
    Inputs: {{ inputs }}
    Config: {{ config }}

    For each step:
    1. Resolve input bindings
    2. Call agent capability
    3. Capture output
    4. Handle errors with retry policy

    {{ ctx.output_format }}
  "#
}

function RecoverFromFailure(
  execution: CompositionExecution,
  error: CompositionError,
  available_agents: AgentCard[]
) -> RecoveryPlan {
  client GPT4o
  prompt #"
    Recover from a composition failure.

    Execution State: {{ execution }}
    Error: {{ error }}
    Available Agents: {{ available_agents }}

    Recovery options:
    1. Retry failed step
    2. Use alternative agent
    3. Skip step if optional
    4. Rollback and retry different path

    {{ ctx.output_format }}
  "#
}

class RecoveryPlan {
  strategy RecoveryStrategy
  modified_plan CompositionPlan?
  resume_from_step string?
  skip_steps string[]
  explanation string
}

enum RecoveryStrategy {
  RETRY
  ALTERNATIVE_AGENT
  SKIP
  ROLLBACK
  ABORT
}
```

### Python Implementation

```python
# src/agent_negotiation/composition.py

from dataclasses import dataclass, field
from typing import Optional, Any, Callable
from enum import Enum
import asyncio
import uuid
from datetime import datetime
import json

class CompositionPlanner:
    """
    Plans capability compositions across multiple agents.
    """

    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry

    def plan(
        self,
        goal: str,
        required_capabilities: list[str],
        constraints: list[CompositionConstraint]
    ) -> CompositionPlan:
        """Create a composition plan."""
        steps = []
        data_flow = []

        # Find agents for each capability
        for i, cap_type in enumerate(required_capabilities):
            agents = self.registry.discover([cap_type], max_results=3)

            if not agents:
                raise ValueError(f"No agent found for capability: {cap_type}")

            # Select best agent
            best_agent = agents[0].agent
            capability = next(
                c for c in best_agent.capabilities
                if c.capability_type.value == cap_type
            )

            step = CompositionStep(
                step_id=f"step-{i+1}",
                agent=best_agent.identity,
                capability=capability,
                input_bindings=self._create_bindings(i, capability),
                output_name=f"output_{i+1}",
                timeout_ms=capability.performance_hints.latency_p95_ms * 2
                          if capability.performance_hints else 5000,
                retry_policy=RetryPolicy(
                    max_retries=3,
                    backoff_strategy=BackoffStrategy.EXPONENTIAL,
                    retry_on=["timeout", "rate_limit"]
                )
            )
            steps.append(step)

            # Create data flow edge to next step
            if i > 0:
                data_flow.append(DataFlowEdge(
                    from_step=f"step-{i}",
                    to_step=f"step-{i+1}",
                    data_path="$.output"
                ))

        return CompositionPlan(
            plan_id=str(uuid.uuid4()),
            goal=goal,
            steps=steps,
            data_flow=data_flow,
            estimated_latency_ms=sum(s.timeout_ms for s in steps),
            failure_modes=self._analyze_failure_modes(steps)
        )

    def _create_bindings(
        self,
        step_index: int,
        capability: AgentCapability
    ) -> list[InputBinding]:
        """Create input bindings for a step."""
        bindings = []

        for prop in capability.input_schema.properties:
            if step_index == 0:
                # First step gets from user input
                bindings.append(InputBinding(
                    parameter_name=prop.name,
                    source=InputSource.USER_INPUT,
                    source_reference=prop.name
                ))
            else:
                # Subsequent steps get from previous
                bindings.append(InputBinding(
                    parameter_name=prop.name,
                    source=InputSource.PREVIOUS_STEP,
                    source_reference=f"step-{step_index}"
                ))

        return bindings

    def _analyze_failure_modes(
        self,
        steps: list[CompositionStep]
    ) -> list[FailureMode]:
        """Identify potential failure modes."""
        modes = []

        for step in steps:
            # Timeout failure
            modes.append(FailureMode(
                step_id=step.step_id,
                failure_type="timeout",
                impact="Step does not complete in time",
                mitigation="Retry with backoff"
            ))

            # Agent unavailable
            modes.append(FailureMode(
                step_id=step.step_id,
                failure_type="agent_unavailable",
                impact="Cannot reach agent",
                mitigation="Try alternative agent"
            ))

        return modes


class CompositionExecutor:
    """
    Executes composition plans with orchestration.
    """

    def __init__(
        self,
        agent_client: 'AgentClient',
        config: OrchestrationConfig
    ):
        self.agent_client = agent_client
        self.config = config
        self._circuit_breakers: dict[str, CircuitBreaker] = {}

    async def execute(
        self,
        plan: CompositionPlan,
        inputs: dict
    ) -> CompositionExecution:
        """Execute a composition plan."""
        execution = CompositionExecution(
            execution_id=str(uuid.uuid4()),
            plan_id=plan.plan_id,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.utcnow().isoformat(),
            step_results=[]
        )

        context = {"inputs": inputs, "outputs": {}}

        try:
            if self.config.parallel_execution:
                await self._execute_parallel(plan, context, execution)
            else:
                await self._execute_sequential(plan, context, execution)

            execution.status = ExecutionStatus.COMPLETED
            execution.final_output = json.dumps(context["outputs"])

        except asyncio.TimeoutError:
            execution.status = ExecutionStatus.TIMEOUT
            execution.error = CompositionError(
                step_id="global",
                error_type="timeout",
                message=f"Exceeded global timeout of {self.config.global_timeout_ms}ms",
                recoverable=True
            )
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = CompositionError(
                step_id="unknown",
                error_type="exception",
                message=str(e),
                recoverable=False
            )

        execution.completed_at = datetime.utcnow().isoformat()
        return execution

    async def _execute_sequential(
        self,
        plan: CompositionPlan,
        context: dict,
        execution: CompositionExecution
    ):
        """Execute steps sequentially."""
        for step in plan.steps:
            result = await self._execute_step(step, context)
            execution.step_results.append(result)

            if result.status == StepStatus.FAILED:
                raise Exception(f"Step {step.step_id} failed: {result.error}")

            context["outputs"][step.output_name] = json.loads(result.output)

    async def _execute_parallel(
        self,
        plan: CompositionPlan,
        context: dict,
        execution: CompositionExecution
    ):
        """Execute independent steps in parallel."""
        # Build dependency graph
        dependencies = self._build_dependency_graph(plan)

        # Group steps by level (no dependencies within level)
        levels = self._topological_sort(plan.steps, dependencies)

        for level in levels:
            # Execute level in parallel
            tasks = [
                self._execute_step(step, context)
                for step in level
            ]

            # Limit concurrency
            semaphore = asyncio.Semaphore(self.config.max_concurrent_steps)

            async def limited_task(task):
                async with semaphore:
                    return await task

            results = await asyncio.gather(*[limited_task(t) for t in tasks])

            for step, result in zip(level, results):
                execution.step_results.append(result)
                if result.status == StepStatus.COMPLETED:
                    context["outputs"][step.output_name] = json.loads(result.output)

    async def _execute_step(
        self,
        step: CompositionStep,
        context: dict
    ) -> StepResult:
        """Execute a single step with retry."""
        start_time = datetime.utcnow()
        retries = 0

        while True:
            try:
                # Resolve inputs
                inputs = self._resolve_inputs(step.input_bindings, context)

                # Check circuit breaker
                agent_id = step.agent.agent_id
                if agent_id in self._circuit_breakers:
                    if not self._circuit_breakers[agent_id].allow_request():
                        raise Exception("Circuit breaker open")

                # Call agent
                output = await asyncio.wait_for(
                    self.agent_client.invoke(step.agent, step.capability, inputs),
                    timeout=step.timeout_ms / 1000
                )

                return StepResult(
                    step_id=step.step_id,
                    status=StepStatus.COMPLETED,
                    output=json.dumps(output),
                    latency_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                    retries=retries
                )

            except Exception as e:
                retries += 1

                if step.retry_policy and retries <= step.retry_policy.max_retries:
                    # Backoff
                    await self._backoff(retries, step.retry_policy.backoff_strategy)
                    continue

                return StepResult(
                    step_id=step.step_id,
                    status=StepStatus.FAILED,
                    error=str(e),
                    latency_ms=int((datetime.utcnow() - start_time).total_seconds() * 1000),
                    retries=retries
                )

    def _resolve_inputs(
        self,
        bindings: list[InputBinding],
        context: dict
    ) -> dict:
        """Resolve input bindings to actual values."""
        inputs = {}

        for binding in bindings:
            if binding.source == InputSource.LITERAL:
                inputs[binding.parameter_name] = binding.source_reference
            elif binding.source == InputSource.USER_INPUT:
                inputs[binding.parameter_name] = context["inputs"].get(binding.source_reference)
            elif binding.source == InputSource.PREVIOUS_STEP:
                step_output = context["outputs"].get(f"output_{binding.source_reference.split('-')[1]}")
                if step_output:
                    inputs[binding.parameter_name] = step_output
            elif binding.source == InputSource.CONTEXT:
                inputs[binding.parameter_name] = context.get(binding.source_reference)

        return inputs

    async def _backoff(self, retry: int, strategy: BackoffStrategy):
        """Wait based on backoff strategy."""
        if strategy == BackoffStrategy.FIXED:
            await asyncio.sleep(1.0)
        elif strategy == BackoffStrategy.LINEAR:
            await asyncio.sleep(retry * 1.0)
        elif strategy == BackoffStrategy.EXPONENTIAL:
            await asyncio.sleep(2 ** retry * 0.1)


class CircuitBreaker:
    """
    Circuit breaker for agent availability.
    """

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open

    def allow_request(self) -> bool:
        """Check if request should be allowed."""
        if self.state == "closed":
            return True

        if self.state == "open":
            # Check if recovery timeout passed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds() * 1000
                if elapsed > self.config.recovery_timeout_ms:
                    self.state = "half-open"
                    return True
            return False

        # Half-open: allow limited requests
        return True

    def record_success(self):
        """Record successful request."""
        if self.state == "half-open":
            self.state = "closed"
            self.failure_count = 0

    def record_failure(self):
        """Record failed request."""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.config.failure_threshold:
            self.state = "open"
```

### Acceptance Criteria

- [ ] Composition plans correctly sequence capabilities
- [ ] Data flow edges connect step outputs to inputs
- [ ] Parallel execution respects dependencies
- [ ] Circuit breaker protects against cascading failures
- [ ] Retry with backoff handles transient errors
- [ ] Recovery plans provide viable alternatives

---

## Security Implementation

### Trust and Authentication

```baml
// Security context
class SecurityContext {
  requester AgentIdentity
  credentials Credential[]
  trust_chain TrustChainEntry[]
  session_token string?
}

class Credential {
  credential_type CredentialType
  value string @description("Encrypted/hashed value")
  expires_at string?
  scope string[]
}

enum CredentialType {
  API_KEY
  BEARER_TOKEN
  MTLS_CERT
  DID
  VC
}

class TrustChainEntry {
  issuer string
  subject string
  delegation_type DelegationType
  permissions string[]
  issued_at string
  expires_at string
}

enum DelegationType {
  DIRECT          // Direct trust relationship
  DELEGATED       // Trust delegated from another agent
  TRANSITIVE      // Trust inherited through chain
}

// Security validation
function ValidateSecurityContext(
  context: SecurityContext,
  required_permissions: string[]
) -> SecurityValidation {
  client GPT4o
  prompt #"
    Validate security context for requested permissions.

    Context: {{ context }}
    Required Permissions: {{ required_permissions }}

    Check:
    1. Credentials are valid and not expired
    2. Trust chain is unbroken
    3. Permissions cover all required operations
    4. No security policy violations

    {{ ctx.output_format }}
  "#
}

class SecurityValidation {
  valid bool
  trust_level TrustLevel
  granted_permissions string[]
  denied_permissions string[]
  warnings string[]
  expires_at string
}
```

---

## Testing Strategy

### Test Categories

1. **Unit Tests**
   - Schema matching algorithms
   - Conflict detection
   - State machine transitions
   - Transformation logic

2. **Integration Tests**
   - Discovery → Negotiation → Agreement flow
   - Multi-agent composition execution
   - Error recovery scenarios

3. **Scenario Tests**
   - Capability discovery with varying agent counts
   - Negotiation with counter-offers
   - Deadlock resolution
   - Composition with failures

4. **Security Tests**
   - Trust chain validation
   - Credential expiration
   - Permission boundary enforcement

### Performance Benchmarks

| Operation | Target |
|-----------|--------|
| Discovery (1000 agents) | < 100ms |
| Schema matching | < 10ms |
| Negotiation turn | < 500ms |
| Composition planning | < 1s |
| Step execution | < 5s |

---

## Task Summary

| Task | Description | Effort | Dependencies |
|------|-------------|--------|--------------|
| 3.1 | Agent Identity & Capability Types | 4-5h | None |
| 3.2 | Agent Card Schema (A2A-compatible) | 3-4h | 3.1 |
| 3.3 | Capability Registry & Discovery | 5-6h | 3.2 |
| 3.4 | Capability Matching Algorithms | 4-5h | 3.3 |
| 3.5 | Negotiation State Machine | 4-5h | 3.2 |
| 3.6 | Proposal Evaluation & Counter-Offer | 5-6h | 3.5 |
| 3.7 | Contract-Net Protocol | 4-5h | 3.6 |
| 3.8 | Schema Conflict Detection | 3-4h | 3.4 |
| 3.9 | Schema Transformation Engine | 5-6h | 3.8 |
| 3.10 | Conflict Mediation | 4-5h | 3.9 |
| 3.11 | Composition Planning | 5-6h | 3.4, 3.7 |
| 3.12 | Composition Execution | 5-6h | 3.11 |
| 3.13 | Security & Trust Layer | 4-5h | 3.2 |
| 3.14 | Testing & Documentation | 5-6h | All |

**Total Estimated Effort**: 61-74 hours

---

## Dependencies

- **Phase 1** (Multi-Modal): Can integrate multi-modal responses in negotiations
- **Phase 2** (Adaptive): Can adapt negotiation style to user expertise
- **Existing Framework**: Builds on InterfaceSchema, LUIComponent types

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Security vulnerabilities | Critical | Thorough security review, sandboxing |
| Performance at scale | High | Caching, connection pooling |
| Protocol interoperability | Medium | A2A/MCP compliance testing |
| Complexity | High | Incremental sub-phases |

---

## References

- [Google A2A Protocol Specification](https://a2a-protocol.org)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [FIPA Contract-Net Specification](http://www.fipa.org/specs/fipa00029/)
- [SPIFFE/SPIRE](https://spiffe.io)
- [Object-Capability Model](https://en.wikipedia.org/wiki/Object-capability_model)

---

*Generated as part of the baml-agentic-ux research project, December 2024*
