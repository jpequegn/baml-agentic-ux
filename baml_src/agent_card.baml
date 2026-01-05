// Agent Card Schema (A2A-compatible)
// Complete agent advertisement format compatible with Google A2A protocol
// Issue #54 - Phase 3: Agent-to-Agent Interface Negotiation

// Dependencies:
// - AgentIdentity, AgentMetadata, TrustLevel, TrustRequirements from agent_identity.baml
// - AgentCapability from agent_capability.baml

// ============================================
// Protocol Types
// ============================================

/// Supported communication protocols for agent interaction
enum ProtocolType {
  A2A @description("Google Agent-to-Agent protocol")
  MCP @description("Model Context Protocol (Anthropic)")
  OPENAPI @description("OpenAPI/REST specification")
  JSON_RPC @description("JSON-RPC 2.0 protocol")
  GRPC @description("gRPC protocol")
  GRAPHQL @description("GraphQL API")
  WEBSOCKET @description("WebSocket real-time protocol")
  CUSTOM @description("Custom protocol implementation")
}

/// Protocol version declaration
class SupportedProtocol {
  comm_protocol ProtocolType @description("Protocol type")
  version string @description("Protocol version (semver)")
  uri string? @description("Protocol specification URI")
  extensions string[]? @description("Supported protocol extensions")
  deprecated bool @description("Whether this protocol version is deprecated")
}

// ============================================
// Endpoint Types
// ============================================

/// Types of endpoints an agent can expose
enum EndpointType {
  PRIMARY @description("Main service endpoint")
  FALLBACK @description("Backup endpoint for failover")
  HEALTH_CHECK @description("Health monitoring endpoint")
  DISCOVERY @description("Agent discovery endpoint (.well-known)")
  METRICS @description("Metrics and observability endpoint")
  ADMIN @description("Administrative endpoint")
}

/// Authentication methods for endpoints
enum AuthMethod {
  NONE @description("No authentication required")
  API_KEY @description("API key in header or query")
  BEARER_TOKEN @description("OAuth2 bearer token")
  BASIC @description("HTTP Basic authentication")
  MTLS @description("Mutual TLS certificate authentication")
  SPIFFE @description("SPIFFE-based authentication")
  OAUTH2 @description("OAuth 2.0 with client credentials")
  JWT @description("JWT token authentication")
  CUSTOM @description("Custom authentication scheme")
}

/// Authentication configuration for an endpoint
class AuthConfig {
  method AuthMethod @description("Authentication method")
  header_name string? @description("Custom header name for API key/token")
  token_endpoint string? @description("OAuth2 token endpoint URL")
  scopes string[]? @description("Required OAuth2 scopes")
  audience string? @description("Expected JWT audience")
  issuer string? @description("Trusted JWT issuer")
}

/// Complete endpoint definition for AgentCard
class CardEndpoint {
  endpoint_type EndpointType @description("Type of endpoint")
  url string @description("Endpoint URL")
  comm_protocol ProtocolType @description("Communication protocol")
  auth_config AuthConfig? @description("Authentication configuration")
  timeout_ms int? @description("Request timeout in milliseconds")
  retry_policy RetryPolicy? @description("Retry policy for this endpoint")
}

/// Retry policy for endpoint calls
class RetryPolicy {
  max_retries int @description("Maximum number of retry attempts")
  initial_backoff_ms int @description("Initial backoff delay in milliseconds")
  max_backoff_ms int @description("Maximum backoff delay in milliseconds")
  backoff_multiplier float @description("Multiplier for exponential backoff")
  retryable_status_codes int[]? @description("HTTP status codes that trigger retry")
}

// ============================================
// Compliance and Certification
// ============================================

/// Standard compliance certifications
enum ComplianceStandard {
  GDPR @description("General Data Protection Regulation (EU)")
  CCPA @description("California Consumer Privacy Act")
  HIPAA @description("Health Insurance Portability and Accountability Act")
  SOC2 @description("Service Organization Control 2")
  SOC2_TYPE1 @description("SOC 2 Type 1 certification")
  SOC2_TYPE2 @description("SOC 2 Type 2 certification")
  ISO27001 @description("ISO/IEC 27001 Information Security")
  ISO27017 @description("ISO/IEC 27017 Cloud Security")
  ISO27018 @description("ISO/IEC 27018 Cloud Privacy")
  PCI_DSS @description("Payment Card Industry Data Security Standard")
  FEDRAMP @description("Federal Risk and Authorization Management Program")
  FEDRAMP_HIGH @description("FedRAMP High Impact Level")
  FEDRAMP_MODERATE @description("FedRAMP Moderate Impact Level")
  NIST_800_53 @description("NIST SP 800-53 Security Controls")
  CSA_STAR @description("Cloud Security Alliance STAR")
}

/// Compliance tag with verification details
class ComplianceTag {
  standard ComplianceStandard @description("Compliance standard")
  certified bool @description("Whether certification is current")
  certificate_url string? @description("URL to compliance certificate")
  expiry_date string? @description("ISO 8601 expiry date of certification")
  auditor string? @description("Name of certifying auditor")
  scope string? @description("Scope of certification")
}

/// Data handling policies for compliance
class DataHandlingPolicy {
  data_residency string[]? @description("Allowed data residency regions (ISO 3166-1)")
  data_retention_days int? @description("Maximum data retention period")
  encryption_at_rest bool @description("Whether data is encrypted at rest")
  encryption_in_transit bool @description("Whether data is encrypted in transit")
  pii_handling string? @description("PII handling policy description")
  audit_logging bool @description("Whether audit logging is enabled")
}

// ============================================
// Agent Card
// ============================================

/// Complete agent advertisement card (A2A-compatible)
/// This is the primary format for agent discovery and capability advertisement
class AgentCard {
  card_version string @description("AgentCard schema version (e.g., 1.0.0)")
  identity AgentIdentity @description("Agent identity information")
  capabilities AgentCapability[] @description("List of advertised capabilities")
  supported_protocols SupportedProtocol[] @description("Supported communication protocols")
  endpoints CardEndpoint[] @description("Available service endpoints")
  compliance_tags ComplianceTag[]? @description("Compliance certifications")
  data_handling DataHandlingPolicy? @description("Data handling policy")
  trust_requirements TrustRequirements? @description("Trust requirements for invocation")
  metadata AgentMetadata? @description("Additional metadata")
  signature string? @description("Cryptographic signature of card contents")
}

/// Lightweight agent card for discovery responses
class AgentCardSummary {
  agent_id string @description("Agent ID for full card retrieval")
  name string @description("Agent name")
  description string @description("Brief description")
  capability_count int @description("Number of capabilities")
  protocols ProtocolType[] @description("Supported protocols")
  compliance_standards ComplianceStandard[] @description("Compliance standards met")
  discovery_url string @description("URL to retrieve full AgentCard")
}

// ============================================
// Well-Known Discovery
// ============================================

/// Response format for .well-known/agent-descriptions endpoint
class WellKnownAgentDescriptions {
  schema_version string @description("Schema version for this format")
  generated_at string @description("ISO 8601 timestamp of generation")
  agents AgentCardSummary[] @description("List of available agent summaries")
  total_count int @description("Total number of agents available")
  next_cursor string? @description("Cursor for pagination")
}

/// Request to retrieve agent card
class AgentCardRequest {
  request_id string @description("Unique request identifier")
  agent_id string @description("ID of agent to retrieve")
  include_capabilities bool @description("Whether to include full capability details")
  include_signature bool @description("Whether to include cryptographic signature")
  requested_at string @description("ISO 8601 timestamp of request")
}

/// Response containing agent card
class AgentCardResponse {
  request_id string @description("ID of the original request")
  agent_card AgentCard? @description("The agent card if found")
  found bool @description("Whether the agent was found")
  cached bool @description("Whether response is from cache")
  cache_expires_at string? @description("ISO 8601 timestamp when cache expires")
  error AgentCardError? @description("Error details if not found")
}

/// Error response for agent card retrieval
class AgentCardError {
  error_code string @description("Machine-readable error code")
  error_message string @description("Human-readable error message")
  suggested_action string? @description("Suggested action to resolve")
}

// ============================================
// Protocol Negotiation
// ============================================

/// Request to negotiate communication protocol
class ProtocolNegotiationRequest {
  request_id string @description("Unique request identifier")
  client_protocols SupportedProtocol[] @description("Protocols supported by client")
  preferred_comm_protocol ProtocolType? @description("Client's preferred protocol")
  capabilities_required string[]? @description("Capability IDs that must be supported")
}

/// Result of protocol negotiation
class ProtocolNegotiationResult {
  request_id string @description("ID of the negotiation request")
  success bool @description("Whether negotiation succeeded")
  selected_protocol SupportedProtocol? @description("Agreed-upon protocol")
  selected_endpoint CardEndpoint? @description("Endpoint to use")
  fallback_protocols SupportedProtocol[]? @description("Alternative protocols if primary fails")
  failure_reason string? @description("Reason for negotiation failure")
}

// ============================================
// Card Validation
// ============================================

/// Result of validating an agent card
class CardValidationResult {
  valid bool @description("Whether the card is valid")
  errors CardValidationError[] @description("List of validation errors")
  warnings CardValidationWarning[] @description("List of validation warnings")
  signature_verified bool? @description("Whether signature verification passed")
  a2a_compliant bool @description("Whether card is A2A-compliant")
  mcp_compliant bool @description("Whether card is MCP-compliant")
}

/// Validation error for agent card
class CardValidationError {
  field string @description("Field path with error")
  error_code string @description("Error code")
  message string @description("Error description")
}

/// Validation warning for agent card
class CardValidationWarning {
  field string @description("Field path with warning")
  warning_code string @description("Warning code")
  message string @description("Warning description")
  suggestion string? @description("Suggested fix")
}
