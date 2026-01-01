// Capability Registry & Discovery Service
// Agent discovery and capability matching for Phase 3 agent negotiation
// Issue #55 - Phase 3: Agent-to-Agent Interface Negotiation

// Dependencies:
// - AgentIdentity from agent_identity.baml
// - AgentCard from agent_card.baml

// ============================================
// Discovery Constraints
// ============================================

/// Types of constraints for agent discovery
enum ConstraintType {
  CAPABILITY @description("Must have specific capability")
  PROTOCOL @description("Must support specific protocol")
  COMPLIANCE @description("Must meet compliance standard")
  TRUST_LEVEL @description("Must meet minimum trust level")
  REGION @description("Must be in specific region")
  PROVIDER @description("Must be from specific provider")
  VERSION @description("Must meet version requirements")
  PERFORMANCE @description("Must meet performance criteria")
}

/// Comparison operators for constraint matching
enum ConstraintOperator {
  EQUALS @description("Exact match")
  NOT_EQUALS @description("Must not match")
  GREATER_THAN @description("Greater than value")
  LESS_THAN @description("Less than value")
  GREATER_OR_EQUAL @description("Greater than or equal")
  LESS_OR_EQUAL @description("Less than or equal")
  CONTAINS @description("Value contains substring")
  IN @description("Value is in list")
  NOT_IN @description("Value is not in list")
  REGEX @description("Value matches regex pattern")
}

/// A constraint for filtering agents in discovery
class DiscoveryConstraint {
  constraint_type ConstraintType @description("Type of constraint")
  field string @description("Field path to check (e.g., 'identity.provider')")
  operator ConstraintOperator @description("Comparison operator")
  value string @description("Value to compare against")
  weight float? @description("Weight for scoring (0.0-1.0)")
  required bool @description("Whether constraint is required vs preferred")
}

// ============================================
// Discovery Request/Response
// ============================================

/// Source of discovery results
enum DiscoverySource {
  REGISTRY @description("Local capability registry")
  CACHE @description("Cached results from previous discovery")
  PEER_DISCOVERY @description("Discovered via peer agents")
  LOCAL @description("Local/embedded agents")
  WELL_KNOWN @description("From .well-known discovery endpoint")
}

/// Request to discover agents with specific capabilities
class DiscoveryRequest {
  request_id string @description("Unique request identifier")
  requester AgentIdentity @description("Identity of requesting agent")
  required_capabilities string[] @description("Capability IDs that must be present")
  optional_capabilities string[]? @description("Capability IDs that are nice to have")
  constraints DiscoveryConstraint[] @description("Additional filtering constraints")
  max_results int @description("Maximum number of results to return")
  timeout_ms int? @description("Request timeout in milliseconds")
  include_inactive bool @description("Whether to include inactive/unhealthy agents")
  requested_at string @description("ISO 8601 timestamp of request")
}

/// A matching agent with relevance scoring
class AgentMatch {
  agent AgentCard @description("The matched agent's card")
  match_score float @description("Overall match score (0.0-1.0)")
  capability_coverage float @description("Percentage of required capabilities matched")
  constraint_satisfaction float @description("Percentage of constraints satisfied")
  compatibility_notes string[]? @description("Notes about compatibility considerations")
  matched_capabilities string[] @description("List of matched capability IDs")
  missing_capabilities string[]? @description("List of missing required capabilities")
}

/// Response from capability discovery
class DiscoveryResponse {
  request_id string @description("ID of the original request")
  agents AgentMatch[] @description("List of matched agents, sorted by score")
  total_count int @description("Total number of matching agents")
  returned_count int @description("Number of agents returned (may be limited)")
  discovery_time_ms int @description("Time taken for discovery in milliseconds")
  source DiscoverySource @description("Source of the discovery results")
  cached bool @description("Whether results are from cache")
  cache_expires_at string? @description("ISO 8601 timestamp when cache expires")
}

// ============================================
// Registry Operations
// ============================================

/// Request to register an agent in the registry
class RegistrationRequest {
  request_id string @description("Unique request identifier")
  agent_card AgentCard @description("Agent card to register")
  ttl_seconds int @description("Time-to-live for registration")
  tags string[]? @description("Additional tags for categorization")
  priority int? @description("Registration priority (higher = preferred)")
}

/// Response from agent registration
class RegistrationResponse {
  request_id string @description("ID of the original request")
  success bool @description("Whether registration succeeded")
  registration_id string? @description("Unique registration ID if successful")
  expires_at string? @description("ISO 8601 timestamp when registration expires")
  error RegistrationError? @description("Error details if registration failed")
}

/// Error during registration
class RegistrationError {
  error_code string @description("Machine-readable error code")
  message string @description("Human-readable error message")
  field string? @description("Field that caused the error")
}

/// Request to update an existing registration
class UpdateRequest {
  request_id string @description("Unique request identifier")
  registration_id string @description("ID of registration to update")
  agent_card AgentCard @description("Updated agent card")
  extend_ttl bool @description("Whether to extend TTL")
  new_ttl_seconds int? @description("New TTL if extending")
}

/// Request to deregister an agent
class DeregistrationRequest {
  request_id string @description("Unique request identifier")
  registration_id string @description("ID of registration to remove")
  agent_id string @description("Agent ID for verification")
  reason string? @description("Reason for deregistration")
}

/// Response from deregistration
class DeregistrationResponse {
  request_id string @description("ID of the original request")
  success bool @description("Whether deregistration succeeded")
  message string? @description("Additional information")
}

// ============================================
// Registry Status
// ============================================

/// Health status of the registry
class RegistryStatus {
  healthy bool @description("Whether registry is healthy")
  agent_count int @description("Number of registered agents")
  capability_count int @description("Number of unique capabilities indexed")
  last_cleanup string @description("ISO 8601 timestamp of last cleanup")
  uptime_seconds int @description("Registry uptime in seconds")
  cache_hit_rate float @description("Cache hit rate (0.0-1.0)")
}

/// Statistics about a registered capability
class CapabilityStats {
  capability_id string @description("Capability identifier")
  agent_count int @description("Number of agents with this capability")
  average_version string @description("Average version of capability")
  protocols ProtocolType[] @description("Protocols supporting this capability")
}

/// Index entry for fast capability lookup
class CapabilityIndex {
  capability_id string @description("Capability identifier")
  agent_ids string[] @description("IDs of agents with this capability")
  last_updated string @description("ISO 8601 timestamp of last update")
}
