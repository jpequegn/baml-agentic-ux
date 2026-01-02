# A2A Security Model

## Overview

The agent-to-agent security model implements defense-in-depth with multiple layers of protection: authentication, authorization, trust chain validation, and secure communication.

## Threat Model

### Primary Threats

| Threat | Impact | Mitigation |
|--------|--------|------------|
| Prompt injection via agents | Critical | Input validation, sandboxing, content filtering |
| Capability escalation | High | OCAP model, least privilege, permission boundaries |
| Memory poisoning | High | Provenance tracking, tenant isolation |
| Cross-agent contamination | Medium | Memory brokers, ABAC policies |
| Man-in-the-middle | High | Mutual TLS, certificate pinning |
| Credential theft | High | Short-lived tokens, secure storage |
| Denial of service | Medium | Rate limiting, circuit breakers |

### Attack Vectors

1. **Malicious Agent Registration** - Fake agents mimicking legitimate services
2. **Proposal Manipulation** - Tampering with negotiation messages
3. **Trust Chain Forgery** - Creating fake delegation chains
4. **Capability Abuse** - Using capabilities beyond granted scope
5. **Data Exfiltration** - Extracting sensitive data via capabilities

## Trust Levels

```python
class TrustLevel(Enum):
    NONE = "none"        # Public access, no authentication
    BASIC = "basic"      # API key or basic authentication
    VERIFIED = "verified" # Verified identity (certificate/token)
    TRUSTED = "trusted"   # Established trust relationship
    PRIVILEGED = "privileged"  # High-privilege operations
```

### Trust Level Requirements by Operation

| Operation | Minimum Trust Level |
|-----------|-------------------|
| Discovery (public) | NONE |
| Registration | BASIC |
| Negotiation (initiate) | VERIFIED |
| Negotiation (accept) | VERIFIED |
| Capability invocation | TRUSTED |
| Privileged capabilities | PRIVILEGED |
| Admin operations | PRIVILEGED |

## Authentication

### Supported Methods

```python
class CredentialType(Enum):
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    MTLS_CERT = "mtls_cert"
    DID = "did"  # Decentralized Identifier
    VC = "vc"    # Verifiable Credential
```

### Authentication Flow

```
Client                                       Server
  │                                            │
  ├── Request with credentials ──────────────→ │
  │                                            │
  │                    ┌───────────────────────┤
  │                    │ Validate credential   │
  │                    │ Check expiration      │
  │                    │ Verify signature      │
  │                    └───────────────────────┤
  │                                            │
  │ ←─────────── Success + Security Context ───┤
  │                                            │
```

### Credential Structure

```json
{
  "credential_type": "bearer_token",
  "value": "eyJhbGciOiJSUzI1NiIs...",
  "expires_at": "2024-12-29T12:00:00Z",
  "scope": ["read:capabilities", "invoke:translate"],
  "issuer": "urn:agent:auth:issuer:1.0.0"
}
```

## Trust Chain

### Delegation Types

```python
class DelegationType(Enum):
    DIRECT = "direct"         # Direct trust relationship
    DELEGATED = "delegated"   # Trust delegated from another agent
    TRANSITIVE = "transitive" # Trust inherited through chain
```

### Trust Chain Entry

```json
{
  "issuer": "urn:agent:root:authority:1.0.0",
  "subject": "urn:agent:acme:translator:1.0.0",
  "delegation_type": "direct",
  "permissions": ["translate:*", "detect:language"],
  "issued_at": "2024-12-01T00:00:00Z",
  "expires_at": "2025-12-01T00:00:00Z"
}
```

### Chain Validation

```python
def validate_chain(entries: list[TrustChainEntry]) -> bool:
    """
    Validate a trust chain:
    1. Each entry's subject is the next entry's issuer
    2. All entries are not expired
    3. Permissions are properly delegated (no escalation)
    4. Chain terminates at a trusted root
    """
```

### Trust Chain Visualization

```
Root Authority
      │
      ├── [DIRECT] Platform Provider
      │         │
      │         ├── [DELEGATED] Service Agent A
      │         │         │
      │         │         └── [TRANSITIVE] Sub-Agent A1
      │         │
      │         └── [DELEGATED] Service Agent B
      │
      └── [DIRECT] Enterprise Customer
                │
                └── [DELEGATED] Internal Agent
```

## Authorization

### Permission Model

Permissions follow a hierarchical namespace:

```
<domain>:<action>:<resource>

Examples:
- translate:invoke:*         # Invoke any translate capability
- negotiate:accept:agreements # Accept negotiation agreements
- compose:execute:plans      # Execute composition plans
- admin:manage:registry      # Manage registry entries
```

### Permission Checking

```python
def check_permissions(
    required: list[str],
    granted: list[str]
) -> tuple[list[str], list[str]]:
    """
    Returns (granted_permissions, denied_permissions)

    Wildcards (*) expand to match any value at that level.
    More specific permissions override wildcards.
    """
```

### Security Context

```python
@dataclass
class SecurityContext:
    requester: AgentIdentity
    credentials: list[Credential]
    trust_chain: list[TrustChainEntry]
    session_token: str | None

    # Computed properties
    trust_level: TrustLevel
    effective_permissions: list[str]
```

## Secure Communication

### Transport Security

| Protocol | Security | Notes |
|----------|----------|-------|
| HTTPS | TLS 1.3 | Required for all external communication |
| mTLS | Mutual TLS | For high-trust agent communication |
| gRPC | TLS + Auth | Built-in authentication |

### Certificate Requirements

- Minimum 2048-bit RSA or 256-bit ECDSA
- Valid chain to trusted CA
- Certificate transparency logs (optional)
- Regular rotation (90 days recommended)

## Input Validation

### Schema Validation

All inputs are validated against defined schemas:

```python
def validate_input(data: dict, schema: SchemaDefinition) -> ValidationResult:
    """
    Validates:
    1. Required fields present
    2. Type correctness
    3. Format compliance (email, uri, etc.)
    4. Enum value validity
    5. Size/length constraints
    """
```

### Sanitization

- Strip control characters
- Normalize Unicode
- Limit nested depth (max 10 levels)
- Limit array sizes (max 1000 items)
- Limit string lengths (max 1MB)

### Prompt Injection Defense

```python
INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"system prompt",
    r"you are now",
    r"new persona",
    # ... more patterns
]

def detect_injection(text: str) -> bool:
    """Check for common prompt injection patterns."""
```

## Rate Limiting

### Default Limits

| Operation | Limit | Window |
|-----------|-------|--------|
| Discovery | 100/min | Per IP |
| Registration | 10/min | Per agent |
| Negotiation | 50/min | Per session |
| Invocation | 1000/min | Per capability |

### Circuit Breaker

```python
@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5     # Failures before opening
    recovery_timeout_ms: int = 30000  # Wait before half-open
    half_open_requests: int = 3    # Test requests in half-open
```

## Audit Logging

### Logged Events

| Event | Level | Retention |
|-------|-------|-----------|
| Authentication | INFO | 90 days |
| Authorization failure | WARN | 1 year |
| Negotiation | INFO | 90 days |
| Capability invocation | DEBUG | 30 days |
| Security violation | ERROR | 2 years |
| Admin actions | INFO | 2 years |

### Log Format

```json
{
  "timestamp": "2024-12-28T10:00:00Z",
  "event_type": "capability_invoke",
  "actor": "urn:agent:client:app:1.0.0",
  "target": "urn:agent:acme:translator:1.0.0",
  "capability": "translate-text",
  "result": "success",
  "latency_ms": 120,
  "trace_id": "trace-123",
  "metadata": {
    "input_size": 256,
    "output_size": 280
  }
}
```

## Compliance

### Supported Standards

- **GDPR**: Data protection, right to erasure
- **HIPAA**: Healthcare data protection
- **SOC2**: Security controls
- **PCI-DSS**: Payment data security

### Compliance Tags

```python
class ComplianceStandard(Enum):
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    ISO27001 = "iso27001"
    FEDRAMP = "fedramp"
```

### Data Handling

```python
@dataclass
class DataHandlingPolicy:
    encryption_at_rest: bool = True
    encryption_in_transit: bool = True
    data_residency: list[str] = field(default_factory=list)  # ["us", "eu"]
    retention_days: int | None = None
    audit_logging: bool = True
    pii_handling: str = "masked"  # masked, encrypted, none
```

## Security Best Practices

### For Agent Developers

1. **Validate all inputs** against schemas
2. **Use short-lived tokens** (1 hour max)
3. **Implement rate limiting** at the edge
4. **Log security events** with trace IDs
5. **Rotate credentials** regularly
6. **Use mTLS** for agent-to-agent communication
7. **Sanitize outputs** to prevent injection

### For Operators

1. **Enable audit logging** for all operations
2. **Monitor for anomalies** in invocation patterns
3. **Review trust chains** periodically
4. **Rotate certificates** before expiration
5. **Implement network segmentation**
6. **Use secrets management** for credentials
7. **Regular security assessments**

## Incident Response

### Security Event Handling

```
1. Detection
   └── Anomaly detection / Alert trigger

2. Triage
   └── Assess severity and scope

3. Containment
   ├── Revoke credentials
   ├── Block agent
   └── Isolate affected systems

4. Investigation
   ├── Collect logs
   ├── Trace affected operations
   └── Identify root cause

5. Remediation
   ├── Patch vulnerability
   ├── Rotate credentials
   └── Update policies

6. Recovery
   ├── Restore service
   └── Verify security

7. Post-Incident
   ├── Document findings
   └── Update procedures
```
