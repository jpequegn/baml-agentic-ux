// Security & Trust Layer Types
// Provides security context, trust chain validation, and authentication
// Issue #65 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.13)

// Dependencies:
// - AgentIdentity from negotiation_state.baml

// ============================================
// Credential Type Enums
// ============================================

/// Types of credentials for agent authentication
enum CredentialType {
  API_KEY @description("API key authentication")
  BEARER_TOKEN @description("OAuth/JWT bearer token")
  MTLS_CERT @description("Mutual TLS certificate")
  DID @description("Decentralized Identifier")
  VC @description("Verifiable Credential")
  HMAC @description("HMAC signature")
  SPIFFE @description("SPIFFE SVID")
}

/// Level of trust established
enum TrustLevel {
  NONE @description("No trust established")
  LOW @description("Basic authentication only")
  MEDIUM @description("Authenticated with limited verification")
  HIGH @description("Fully verified trust chain")
  ABSOLUTE @description("Cryptographically verified with hardware attestation")
}

/// Type of delegation in trust chain
enum DelegationType {
  DIRECT @description("Direct trust relationship")
  DELEGATED @description("Trust delegated from another agent")
  TRANSITIVE @description("Trust inherited through chain")
  INHERITED @description("Trust inherited from parent organization")
}

/// Status of credential validation
enum CredentialStatus {
  VALID @description("Credential is valid")
  EXPIRED @description("Credential has expired")
  REVOKED @description("Credential has been revoked")
  INVALID @description("Credential is malformed or incorrect")
  UNKNOWN @description("Credential status cannot be determined")
}

/// Type of permission grant
enum PermissionType {
  READ @description("Read access to resources")
  WRITE @description("Write/modify access")
  EXECUTE @description("Execute operations")
  DELETE @description("Delete resources")
  ADMIN @description("Administrative access")
  DELEGATE @description("Can delegate permissions to others")
}

/// Security event type for auditing
enum SecurityEventType {
  AUTHENTICATION @description("Authentication attempt")
  AUTHORIZATION @description("Authorization decision")
  CREDENTIAL_CHECK @description("Credential validation")
  TRUST_CHAIN_VALIDATION @description("Trust chain verification")
  PERMISSION_GRANT @description("Permission granted")
  PERMISSION_DENIED @description("Permission denied")
  SESSION_START @description("Security session started")
  SESSION_END @description("Security session ended")
  ANOMALY_DETECTED @description("Security anomaly detected")
}

/// Severity of security warnings
enum SecuritySeverity {
  INFO @description("Informational notice")
  WARNING @description("Potential security concern")
  CRITICAL @description("Serious security issue")
  ALERT @description("Immediate action required")
}

// ============================================
// Identity Types
// ============================================

/// Agent identity for security context
class AgentSecurityIdentity {
  agent_id string @description("Unique agent identifier")
  agent_name string @description("Human-readable agent name")
  organization string? @description("Organization the agent belongs to")
  spiffe_id string? @description("SPIFFE identity (e.g., spiffe://trust-domain/path)")
  did string? @description("Decentralized Identifier")
  public_key string? @description("Agent's public key (PEM or JWK)")
  trust_domain string? @description("Trust domain the agent belongs to")
}

// ============================================
// Credential Types
// ============================================

/// A credential for authentication
class Credential {
  credential_id string @description("Unique credential identifier")
  credential_type CredentialType @description("Type of credential")
  value string @description("Encrypted/hashed credential value")
  issuer string @description("Who issued the credential")
  subject string @description("Who the credential is for")
  scope string[] @description("Permissions/scopes granted by credential")
  issued_at string @description("ISO 8601 issuance timestamp")
  expires_at string? @description("ISO 8601 expiration timestamp")
  not_before string? @description("ISO 8601 earliest valid time")
  revocation_endpoint string? @description("URL to check revocation status")
  metadata CredentialMetadata? @description("Additional credential metadata")
}

/// Metadata for credentials
class CredentialMetadata {
  algorithm string? @description("Signing algorithm used")
  key_id string? @description("Key identifier for verification")
  chain string[]? @description("Certificate chain if applicable")
  audience string[]? @description("Intended audience(s)")
  nonce string? @description("One-time use token")
}

/// Result of credential validation
class CredentialValidation {
  credential_id string @description("ID of validated credential")
  status CredentialStatus @description("Validation status")
  trust_level TrustLevel @description("Trust level achieved")
  valid_scopes string[] @description("Scopes that are valid")
  invalid_scopes string[] @description("Scopes that are invalid/expired")
  expires_at string? @description("When credential expires")
  warnings string[] @description("Any validation warnings")
  error string? @description("Error message if invalid")
}

// ============================================
// Trust Chain Types
// ============================================

/// Entry in a trust chain
class TrustChainEntry {
  entry_id string @description("Unique entry identifier")
  issuer string @description("Entity granting trust")
  subject string @description("Entity receiving trust")
  delegation_type DelegationType @description("How trust was delegated")
  permissions string[] @description("Permissions granted")
  constraints TrustConstraint[]? @description("Constraints on delegation")
  issued_at string @description("ISO 8601 issuance timestamp")
  expires_at string @description("ISO 8601 expiration timestamp")
  signature string? @description("Cryptographic signature")
  parent_entry_id string? @description("ID of parent entry in chain")
}

/// Constraint on trust delegation
class TrustConstraint {
  constraint_type string @description("Type of constraint")
  value string @description("Constraint value")
  operator string @description("Comparison operator")
}

/// Result of trust chain validation
class TrustChainValidation {
  valid bool @description("Whether chain is valid")
  chain_length int @description("Number of entries in chain")
  root_issuer string @description("Root of trust")
  final_subject string @description("End of trust chain")
  effective_trust_level TrustLevel @description("Trust level after chain analysis")
  effective_permissions string[] @description("Intersection of all permissions")
  broken_links TrustChainBreak[]? @description("Any breaks in chain")
  warnings string[] @description("Validation warnings")
}

/// Information about a break in trust chain
class TrustChainBreak {
  position int @description("Position in chain where break occurred")
  issuer string @description("Issuer at break point")
  subject string @description("Subject at break point")
  reason string @description("Reason for break")
  severity SecuritySeverity @description("Severity of the break")
}

// ============================================
// Security Context Types
// ============================================

/// Complete security context for a request
class SecurityContext {
  context_id string @description("Unique context identifier")
  requester AgentSecurityIdentity @description("Agent making the request")
  credentials Credential[] @description("Credentials presented")
  trust_chain TrustChainEntry[] @description("Chain of trust")
  session_token string? @description("Active session token")
  session_expires_at string? @description("Session expiration")
  request_timestamp string @description("ISO 8601 request timestamp")
  request_nonce string? @description("One-time request nonce")
  source_ip string? @description("Source IP address if applicable")
  user_agent string? @description("User agent string")
}

/// Permission being requested or granted
class Permission {
  permission_id string @description("Unique permission identifier")
  resource string @description("Resource being accessed")
  action PermissionType @description("Action being performed")
  conditions PermissionCondition[]? @description("Conditions for permission")
}

/// Condition on a permission
class PermissionCondition {
  field string @description("Field to check")
  operator string @description("Comparison operator")
  value string @description("Value to compare against")
}

// ============================================
// Security Validation Types
// ============================================

/// Result of security context validation
class SecurityValidation {
  validation_id string @description("Unique validation identifier")
  valid bool @description("Whether validation passed")
  trust_level TrustLevel @description("Established trust level")
  granted_permissions string[] @description("Permissions granted")
  denied_permissions string[] @description("Permissions denied")
  required_permissions string[] @description("Permissions that were required")
  credential_validations CredentialValidation[] @description("Individual credential results")
  trust_chain_validation TrustChainValidation? @description("Trust chain validation result")
  warnings SecurityWarning[] @description("Security warnings")
  errors string[] @description("Validation errors")
  expires_at string @description("When this validation expires")
  audit_id string @description("ID for audit trail")
}

/// Security warning
class SecurityWarning {
  warning_id string @description("Unique warning identifier")
  severity SecuritySeverity @description("Warning severity")
  category string @description("Warning category")
  message string @description("Warning message")
  recommendation string? @description("Recommended action")
}

/// Request to validate security context
class ValidateSecurityRequest {
  request_id string @description("Unique request identifier")
  context SecurityContext @description("Security context to validate")
  required_permissions string[] @description("Permissions required for operation")
  resource string? @description("Resource being accessed")
  operation string? @description("Operation being performed")
  strict_mode bool @description("Whether to enforce strict validation")
}

/// Response from security validation
class ValidateSecurityResponse {
  request_id string @description("Original request ID")
  validation SecurityValidation @description("Validation result")
  recommended_action string? @description("Recommended action based on result")
}

// ============================================
// Audit Types
// ============================================

/// Security audit log entry
class SecurityAuditEntry {
  audit_id string @description("Unique audit entry identifier")
  timestamp string @description("ISO 8601 timestamp")
  event_type SecurityEventType @description("Type of security event")
  actor string @description("Agent/entity that performed action")
  target string? @description("Target of the action")
  action string @description("Action performed")
  result string @description("Result of action")
  trust_level TrustLevel? @description("Trust level at time of event")
  details AuditDetails @description("Additional event details")
}

/// Additional audit details
class AuditDetails {
  context_id string? @description("Related security context ID")
  credentials_used string[]? @description("Credential IDs used")
  permissions_checked string[]? @description("Permissions that were checked")
  ip_address string? @description("Source IP if available")
  user_agent string? @description("User agent if available")
  error_message string? @description("Error message if failed")
  metadata string? @description("Additional metadata as JSON")
}

// ============================================
// Session Types
// ============================================

/// Security session for ongoing communication
class SecuritySession {
  session_id string @description("Unique session identifier")
  agent_id string @description("Agent the session is for")
  created_at string @description("ISO 8601 creation timestamp")
  expires_at string @description("ISO 8601 expiration timestamp")
  last_activity string @description("ISO 8601 last activity timestamp")
  trust_level TrustLevel @description("Session trust level")
  permissions string[] @description("Permissions for this session")
  session_token string @description("Session token")
  refresh_token string? @description("Token to refresh session")
  metadata SessionMetadata? @description("Session metadata")
}

/// Session metadata
class SessionMetadata {
  created_from string? @description("How session was created")
  credential_ids string[] @description("Credentials used to create session")
  trust_chain_depth int @description("Depth of trust chain at creation")
  original_ip string? @description("Original IP address")
  renewal_count int @description("Number of times renewed")
}

/// Request to create a session
class CreateSessionRequest {
  request_id string @description("Unique request identifier")
  context SecurityContext @description("Security context for session")
  requested_duration_ms int @description("Requested session duration")
  requested_permissions string[] @description("Permissions requested")
}

/// Response from session creation
class CreateSessionResponse {
  request_id string @description("Original request ID")
  session SecuritySession? @description("Created session if successful")
  validation SecurityValidation @description("Validation result")
  error string? @description("Error if session creation failed")
}

// ============================================
// Attack Mitigation Types
// ============================================

/// Configuration for input validation (prompt injection mitigation)
class InputValidationConfig {
  max_input_length int @description("Maximum input length")
  allowed_patterns string[] @description("Allowed input patterns (regex)")
  blocked_patterns string[] @description("Blocked input patterns (regex)")
  sanitization_level string @description("Level of input sanitization")
  escape_special_chars bool @description("Whether to escape special characters")
}

/// Result of input validation
class InputValidationResult {
  valid bool @description("Whether input is valid")
  sanitized_input string? @description("Sanitized version of input")
  blocked_patterns_found string[] @description("Blocked patterns that were found")
  warnings string[] @description("Validation warnings")
}

/// Rate limiting configuration
class RateLimitConfig {
  requests_per_minute int @description("Maximum requests per minute")
  requests_per_hour int @description("Maximum requests per hour")
  burst_limit int @description("Maximum burst of requests")
  by_agent bool @description("Rate limit per agent")
  by_ip bool @description("Rate limit per IP")
}

/// Rate limit status
class RateLimitStatus {
  allowed bool @description("Whether request is allowed")
  remaining int @description("Remaining requests in window")
  reset_at string @description("When limit resets")
  retry_after_ms int? @description("Milliseconds to wait before retry")
}

// ============================================
// AI Functions
// ============================================

/// Validate a security context against required permissions
function ValidateSecurityContext(
  context string,
  required_permissions string
) -> SecurityValidation {
  client CustomSonnet4
  prompt #"
    Validate this security context against the required permissions.

    Security Context:
    {{ context }}

    Required Permissions:
    {{ required_permissions }}

    Check:
    1. Credential validity (expiry, format, issuer)
    2. Trust chain integrity (no breaks, valid delegations)
    3. Permission coverage (required vs granted)
    4. Security anomalies or warnings

    {{ ctx.output_format }}
  "#
}

/// Analyze trust chain for security issues
function AnalyzeTrustChain(
  trust_chain string,
  target_permissions string
) -> TrustChainValidation {
  client CustomSonnet4
  prompt #"
    Analyze this trust chain for security issues.

    Trust Chain:
    {{ trust_chain }}

    Target Permissions:
    {{ target_permissions }}

    Verify:
    1. Chain continuity (each subject matches next issuer)
    2. Permission inheritance (no escalation)
    3. Expiration validity
    4. Delegation constraints
    5. Cryptographic signatures if present

    {{ ctx.output_format }}
  "#
}

/// Generate security recommendations
function GenerateSecurityRecommendations(
  validation_result string,
  threat_model string
) -> SecurityRecommendations {
  client CustomSonnet4
  prompt #"
    Generate security recommendations based on validation results.

    Validation Result:
    {{ validation_result }}

    Threat Model:
    {{ threat_model }}

    Provide recommendations for:
    1. Credential improvements
    2. Trust chain strengthening
    3. Permission tightening
    4. Attack surface reduction
    5. Monitoring enhancements

    {{ ctx.output_format }}
  "#
}

/// Security recommendations
class SecurityRecommendations {
  recommendation_id string @description("Unique ID")
  priority_recommendations Recommendation[] @description("High priority items")
  optional_recommendations Recommendation[] @description("Optional improvements")
  risk_summary string @description("Summary of current risks")
  overall_security_score float @description("Security score 0.0-1.0")
}

/// A single recommendation
class Recommendation {
  title string @description("Recommendation title")
  description string @description("Detailed description")
  priority string @description("Priority level")
  effort string @description("Implementation effort")
  impact string @description("Security impact")
}
