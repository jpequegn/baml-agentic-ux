// Agent Identity Types
// Core BAML types for agent identity representation compatible with A2A and MCP standards
// Issue #53 - Phase 3: Agent-to-Agent Interface Negotiation

// ============================================
// Agent Identity
// ============================================

/// Unique identifier for an agent in URN format
/// Format: urn:agent:{provider}:{name}:{version}
class AgentIdentity {
  agent_id string @description("Unique agent identifier in URN format: urn:agent:{provider}:{name}:{version}")
  name string @description("Human-readable agent name")
  version string @description("Semantic version (e.g., 1.0.0)")
  description string @description("Brief description of agent purpose and capabilities")
  provider string? @description("Provider/organization that created the agent")
  trust_domain string? @description("SPIFFE trust domain for identity verification")
  metadata AgentMetadata? @description("Additional agent metadata")
}

/// Additional metadata about an agent
class AgentMetadata {
  created_at string @description("ISO 8601 timestamp of agent creation")
  updated_at string @description("ISO 8601 timestamp of last update")
  homepage string? @description("URL to agent documentation or homepage")
  repository string? @description("URL to source code repository")
  license string? @description("License identifier (e.g., MIT, Apache-2.0)")
  authors string[]? @description("List of agent authors or maintainers")
  tags string[]? @description("Tags for categorization and discovery")
}

// ============================================
// Trust Levels
// ============================================

/// Trust levels for agent-to-agent communication
/// Defines the level of authentication/authorization required
enum TrustLevel {
  NONE @description("Public access, no authentication required")
  BASIC @description("API key or basic authentication")
  VERIFIED @description("Verified identity through certificate or token")
  TRUSTED @description("Established relationship with mutual trust")
  PRIVILEGED @description("High-privilege operations, requires strong auth")
}

/// Requirements for establishing trust
class TrustRequirements {
  minimum_trust_level TrustLevel @description("Minimum trust level required")
  require_mutual_tls bool @description("Whether mTLS is required")
  allowed_trust_domains string[]? @description("Whitelist of trusted SPIFFE domains")
  require_attestation bool @description("Whether runtime attestation is required")
  allowed_issuers string[]? @description("Whitelist of trusted certificate issuers")
}

// ============================================
// Agent Registration
// ============================================

/// Request to register an agent in a registry
class AgentRegistration {
  identity AgentIdentity @description("Agent identity information")
  endpoints AgentEndpoint[] @description("Available communication endpoints")
  capabilities string[] @description("List of capability IDs this agent provides")
  trust_requirements TrustRequirements? @description("Trust requirements for invoking this agent")
  registration_token string? @description("Token for authenticated registration")
}

/// An endpoint where an agent can be reached
class AgentEndpoint {
  endpoint_id string @description("Unique identifier for this endpoint")
  comm_protocol EndpointProtocol @description("Communication protocol")
  url string @description("Endpoint URL")
  priority int @description("Priority for endpoint selection (lower = preferred)")
  health_check_path string? @description("Path for health check requests")
  rate_limit RateLimit? @description("Rate limiting configuration")
}

/// Supported communication protocols
enum EndpointProtocol {
  HTTP @description("HTTP/HTTPS REST endpoint")
  GRPC @description("gRPC endpoint")
  WEBSOCKET @description("WebSocket endpoint for real-time communication")
  MCP @description("Model Context Protocol endpoint")
  A2A @description("Agent-to-Agent protocol endpoint")
}

/// Rate limiting configuration for an endpoint
class RateLimit {
  requests_per_second float @description("Maximum requests per second")
  burst_size int @description("Maximum burst size allowed")
  retry_after_seconds int @description("Seconds to wait after rate limit hit")
}

// ============================================
// Agent Discovery
// ============================================

/// Query for discovering agents
class AgentDiscoveryQuery {
  query_id string @description("Unique identifier for this query")
  capability_filter string[]? @description("Filter by capability IDs")
  provider_filter string[]? @description("Filter by provider")
  tag_filter string[]? @description("Filter by tags")
  trust_level_filter TrustLevel? @description("Minimum trust level required")
  limit int @description("Maximum number of results")
  offset int @description("Offset for pagination")
}

/// Result of an agent discovery query
class AgentDiscoveryResult {
  query_id string @description("ID of the original query")
  agents DiscoveredAgent[] @description("List of discovered agents")
  total_count int @description("Total number of matching agents")
  has_more bool @description("Whether more results are available")
}

/// A discovered agent with summary information
class DiscoveredAgent {
  identity AgentIdentity @description("Agent identity")
  capability_count int @description("Number of capabilities offered")
  endpoint_count int @description("Number of available endpoints")
  trust_level TrustLevel @description("Agent's trust level")
  last_seen string @description("ISO 8601 timestamp of last health check")
  health_status HealthStatus @description("Current health status")
}

/// Health status of an agent
enum HealthStatus {
  HEALTHY @description("Agent is healthy and responsive")
  DEGRADED @description("Agent is responding but with issues")
  UNHEALTHY @description("Agent is not responding or failing")
  UNKNOWN @description("Health status could not be determined")
}

// ============================================
// Agent Verification
// ============================================

/// Request to verify an agent's identity
class VerificationRequest {
  request_id string @description("Unique identifier for this verification request")
  agent_id string @description("ID of agent to verify")
  verification_type VerificationType @description("Type of verification to perform")
  challenge string? @description("Challenge for challenge-response verification")
  timestamp string @description("ISO 8601 timestamp of request")
}

/// Types of identity verification
enum VerificationType {
  CERTIFICATE @description("Verify certificate chain")
  SPIFFE @description("Verify SPIFFE ID and trust domain")
  CHALLENGE_RESPONSE @description("Challenge-response verification")
  TOKEN @description("Verify bearer token")
  ATTESTATION @description("Remote attestation verification")
}

/// Result of identity verification
class VerificationResult {
  request_id string @description("ID of the verification request")
  agent_id string @description("ID of verified agent")
  verified bool @description("Whether verification succeeded")
  trust_level TrustLevel @description("Established trust level")
  verification_time_ms int @description("Time taken for verification in milliseconds")
  certificate_info CertificateInfo? @description("Certificate details if applicable")
  failure_reason string? @description("Reason for verification failure")
}

/// Certificate information for verified agents
class CertificateInfo {
  issuer string @description("Certificate issuer")
  subject string @description("Certificate subject")
  valid_from string @description("ISO 8601 start of validity period")
  valid_until string @description("ISO 8601 end of validity period")
  fingerprint string @description("Certificate fingerprint (SHA-256)")
  spiffe_id string? @description("SPIFFE ID if present")
}
