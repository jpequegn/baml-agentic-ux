"""
Security & Trust Layer for Agent Negotiation.

Provides security context, trust chain validation, authentication,
and audit logging for agent-to-agent communication.

Issue #65 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.13)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional, Any
from datetime import datetime, timedelta
import threading
import hashlib
import hmac
import secrets
import re
import uuid
import json


# ============================================
# Credential Type Enums
# ============================================


class CredentialType(Enum):
    """Types of credentials for agent authentication."""
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    MTLS_CERT = "mtls_cert"
    DID = "did"
    VC = "vc"
    HMAC = "hmac"
    SPIFFE = "spiffe"


class TrustLevel(Enum):
    """Level of trust established."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ABSOLUTE = "absolute"


class DelegationType(Enum):
    """Type of delegation in trust chain."""
    DIRECT = "direct"
    DELEGATED = "delegated"
    TRANSITIVE = "transitive"
    INHERITED = "inherited"


class CredentialStatus(Enum):
    """Status of credential validation."""
    VALID = "valid"
    EXPIRED = "expired"
    REVOKED = "revoked"
    INVALID = "invalid"
    UNKNOWN = "unknown"


class PermissionType(Enum):
    """Type of permission grant."""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"
    DELEGATE = "delegate"


class SecurityEventType(Enum):
    """Security event type for auditing."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CREDENTIAL_CHECK = "credential_check"
    TRUST_CHAIN_VALIDATION = "trust_chain_validation"
    PERMISSION_GRANT = "permission_grant"
    PERMISSION_DENIED = "permission_denied"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    ANOMALY_DETECTED = "anomaly_detected"


class SecuritySeverity(Enum):
    """Severity of security warnings."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    ALERT = "alert"


# ============================================
# Identity Types
# ============================================


@dataclass
class AgentSecurityIdentity:
    """Agent identity for security context."""
    agent_id: str
    agent_name: str
    organization: Optional[str] = None
    spiffe_id: Optional[str] = None
    did: Optional[str] = None
    public_key: Optional[str] = None
    trust_domain: Optional[str] = None


# ============================================
# Credential Types
# ============================================


@dataclass
class CredentialMetadata:
    """Metadata for credentials."""
    algorithm: Optional[str] = None
    key_id: Optional[str] = None
    chain: Optional[list[str]] = None
    audience: Optional[list[str]] = None
    nonce: Optional[str] = None


@dataclass
class Credential:
    """A credential for authentication."""
    credential_id: str
    credential_type: CredentialType
    value: str  # Encrypted/hashed
    issuer: str
    subject: str
    scope: list[str]
    issued_at: str
    expires_at: Optional[str] = None
    not_before: Optional[str] = None
    revocation_endpoint: Optional[str] = None
    metadata: Optional[CredentialMetadata] = None


@dataclass
class CredentialValidation:
    """Result of credential validation."""
    credential_id: str
    status: CredentialStatus
    trust_level: TrustLevel
    valid_scopes: list[str]
    invalid_scopes: list[str]
    expires_at: Optional[str]
    warnings: list[str]
    error: Optional[str] = None


# ============================================
# Trust Chain Types
# ============================================


@dataclass
class TrustConstraint:
    """Constraint on trust delegation."""
    constraint_type: str
    value: str
    operator: str


@dataclass
class TrustChainEntry:
    """Entry in a trust chain."""
    entry_id: str
    issuer: str
    subject: str
    delegation_type: DelegationType
    permissions: list[str]
    issued_at: str
    expires_at: str
    constraints: Optional[list[TrustConstraint]] = None
    signature: Optional[str] = None
    parent_entry_id: Optional[str] = None


@dataclass
class TrustChainBreak:
    """Information about a break in trust chain."""
    position: int
    issuer: str
    subject: str
    reason: str
    severity: SecuritySeverity


@dataclass
class TrustChainValidation:
    """Result of trust chain validation."""
    valid: bool
    chain_length: int
    root_issuer: str
    final_subject: str
    effective_trust_level: TrustLevel
    effective_permissions: list[str]
    broken_links: Optional[list[TrustChainBreak]]
    warnings: list[str]


# ============================================
# Security Context Types
# ============================================


@dataclass
class SecurityContext:
    """Complete security context for a request."""
    context_id: str
    requester: AgentSecurityIdentity
    credentials: list[Credential]
    trust_chain: list[TrustChainEntry]
    request_timestamp: str
    session_token: Optional[str] = None
    session_expires_at: Optional[str] = None
    request_nonce: Optional[str] = None
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class PermissionCondition:
    """Condition on a permission."""
    field: str
    operator: str
    value: str


@dataclass
class Permission:
    """Permission being requested or granted."""
    permission_id: str
    resource: str
    action: PermissionType
    conditions: Optional[list[PermissionCondition]] = None


# ============================================
# Security Validation Types
# ============================================


@dataclass
class SecurityWarning:
    """Security warning."""
    warning_id: str
    severity: SecuritySeverity
    category: str
    message: str
    recommendation: Optional[str] = None


@dataclass
class SecurityValidation:
    """Result of security context validation."""
    validation_id: str
    valid: bool
    trust_level: TrustLevel
    granted_permissions: list[str]
    denied_permissions: list[str]
    required_permissions: list[str]
    credential_validations: list[CredentialValidation]
    trust_chain_validation: Optional[TrustChainValidation]
    warnings: list[SecurityWarning]
    errors: list[str]
    expires_at: str
    audit_id: str


# ============================================
# Audit Types
# ============================================


@dataclass
class AuditDetails:
    """Additional audit details."""
    context_id: Optional[str] = None
    credentials_used: Optional[list[str]] = None
    permissions_checked: Optional[list[str]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[str] = None


@dataclass
class SecurityAuditEntry:
    """Security audit log entry."""
    audit_id: str
    timestamp: str
    event_type: SecurityEventType
    actor: str
    action: str
    result: str
    target: Optional[str] = None
    trust_level: Optional[TrustLevel] = None
    details: Optional[AuditDetails] = None


# ============================================
# Session Types
# ============================================


@dataclass
class SessionMetadata:
    """Session metadata."""
    created_from: Optional[str] = None
    credential_ids: list[str] = field(default_factory=list)
    trust_chain_depth: int = 0
    original_ip: Optional[str] = None
    renewal_count: int = 0


@dataclass
class SecuritySession:
    """Security session for ongoing communication."""
    session_id: str
    agent_id: str
    created_at: str
    expires_at: str
    last_activity: str
    trust_level: TrustLevel
    permissions: list[str]
    session_token: str
    refresh_token: Optional[str] = None
    metadata: Optional[SessionMetadata] = None


# ============================================
# Rate Limiting Types
# ============================================


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    by_agent: bool = True
    by_ip: bool = False


@dataclass
class RateLimitStatus:
    """Rate limit status."""
    allowed: bool
    remaining: int
    reset_at: str
    retry_after_ms: Optional[int] = None


# ============================================
# Input Validation Types
# ============================================


@dataclass
class InputValidationConfig:
    """Configuration for input validation."""
    max_input_length: int = 10000
    allowed_patterns: list[str] = field(default_factory=list)
    blocked_patterns: list[str] = field(default_factory=lambda: [
        r"<script",  # Script injection
        r"{{.*}}",   # Template injection
        r"\$\{.*\}",  # Expression injection
        r"system\s*\(",  # System call injection
        r"exec\s*\(",   # Exec injection
    ])
    sanitization_level: str = "standard"
    escape_special_chars: bool = True


@dataclass
class InputValidationResult:
    """Result of input validation."""
    valid: bool
    sanitized_input: Optional[str]
    blocked_patterns_found: list[str]
    warnings: list[str]


# ============================================
# Callback Types
# ============================================


# Type for audit callback
AuditCallback = Callable[[SecurityAuditEntry], None]


# ============================================
# SecurityValidator Class
# ============================================


class SecurityValidator:
    """
    Validates security contexts, credentials, and trust chains.

    Provides:
    - Credential validation (expiry, format, issuer)
    - Trust chain verification
    - Permission checking
    - SPIFFE ID format support
    - Audit logging
    """

    def __init__(
        self,
        trusted_issuers: Optional[list[str]] = None,
        trusted_domains: Optional[list[str]] = None,
        audit_callback: Optional[AuditCallback] = None,
        rate_limit_config: Optional[RateLimitConfig] = None,
        input_validation_config: Optional[InputValidationConfig] = None,
    ):
        """
        Initialize the security validator.

        Args:
            trusted_issuers: List of trusted credential issuers
            trusted_domains: List of trusted SPIFFE domains
            audit_callback: Callback for audit logging
            rate_limit_config: Rate limiting configuration
            input_validation_config: Input validation configuration
        """
        self.trusted_issuers = trusted_issuers or []
        self.trusted_domains = trusted_domains or []
        self.audit_callback = audit_callback
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.input_validation_config = input_validation_config or InputValidationConfig()

        self._sessions: dict[str, SecuritySession] = {}
        self._revoked_credentials: set[str] = set()
        self._rate_limit_counters: dict[str, list[datetime]] = {}
        self._audit_log: list[SecurityAuditEntry] = []
        self._lock = threading.Lock()

    def validate_context(
        self,
        context: SecurityContext,
        required_permissions: list[str],
        strict_mode: bool = False,
    ) -> SecurityValidation:
        """
        Validate a security context against required permissions.

        Args:
            context: Security context to validate
            required_permissions: Permissions required for operation
            strict_mode: Whether to enforce strict validation

        Returns:
            SecurityValidation with results
        """
        validation_id = str(uuid.uuid4())
        audit_id = str(uuid.uuid4())
        errors: list[str] = []
        warnings: list[SecurityWarning] = []

        # Validate credentials
        credential_validations = [
            self._validate_credential(cred) for cred in context.credentials
        ]

        # Check for any invalid credentials
        valid_credentials = [
            cv for cv in credential_validations
            if cv.status == CredentialStatus.VALID
        ]

        if not valid_credentials:
            errors.append("No valid credentials provided")

        # Validate trust chain
        trust_chain_validation = self._validate_trust_chain(
            context.trust_chain,
            context.requester.agent_id,
        )

        if not trust_chain_validation.valid:
            if strict_mode:
                errors.append("Trust chain validation failed")
            else:
                warnings.append(SecurityWarning(
                    warning_id=str(uuid.uuid4()),
                    severity=SecuritySeverity.WARNING,
                    category="trust_chain",
                    message="Trust chain validation had issues",
                    recommendation="Review trust chain configuration",
                ))

        # Collect all granted permissions
        granted_permissions: set[str] = set()
        for cv in valid_credentials:
            granted_permissions.update(cv.valid_scopes)

        # Add permissions from trust chain
        if trust_chain_validation.valid:
            granted_permissions.update(trust_chain_validation.effective_permissions)

        # Check required permissions
        granted = list(granted_permissions)
        denied = [p for p in required_permissions if p not in granted_permissions]

        if denied:
            errors.append(f"Missing required permissions: {', '.join(denied)}")

        # Determine overall trust level
        trust_level = self._calculate_trust_level(
            credential_validations,
            trust_chain_validation,
        )

        # Calculate expiration
        expires_at = self._calculate_validation_expiry(credential_validations)

        # Validate SPIFFE ID if present
        if context.requester.spiffe_id:
            spiffe_warnings = self._validate_spiffe_id(context.requester.spiffe_id)
            warnings.extend(spiffe_warnings)

        # Check session if present
        if context.session_token:
            session_warnings = self._validate_session_token(context.session_token)
            warnings.extend(session_warnings)

        # Create validation result
        validation = SecurityValidation(
            validation_id=validation_id,
            valid=len(errors) == 0,
            trust_level=trust_level,
            granted_permissions=granted,
            denied_permissions=denied,
            required_permissions=required_permissions,
            credential_validations=credential_validations,
            trust_chain_validation=trust_chain_validation,
            warnings=warnings,
            errors=errors,
            expires_at=expires_at,
            audit_id=audit_id,
        )

        # Log audit entry
        self._log_audit(
            SecurityAuditEntry(
                audit_id=audit_id,
                timestamp=datetime.now().isoformat(),
                event_type=SecurityEventType.AUTHORIZATION,
                actor=context.requester.agent_id,
                action="validate_context",
                result="success" if validation.valid else "failure",
                trust_level=trust_level,
                details=AuditDetails(
                    context_id=context.context_id,
                    credentials_used=[c.credential_id for c in context.credentials],
                    permissions_checked=required_permissions,
                    ip_address=context.source_ip,
                    error_message=errors[0] if errors else None,
                ),
            )
        )

        return validation

    def validate_credential(self, credential: Credential) -> CredentialValidation:
        """
        Validate a single credential.

        Args:
            credential: Credential to validate

        Returns:
            CredentialValidation with results
        """
        return self._validate_credential(credential)

    def validate_trust_chain(
        self,
        chain: list[TrustChainEntry],
        target_subject: str,
    ) -> TrustChainValidation:
        """
        Validate a trust chain.

        Args:
            chain: Trust chain entries
            target_subject: Expected final subject

        Returns:
            TrustChainValidation with results
        """
        return self._validate_trust_chain(chain, target_subject)

    def create_session(
        self,
        context: SecurityContext,
        duration_ms: int = 3600000,  # 1 hour default
        requested_permissions: Optional[list[str]] = None,
    ) -> tuple[Optional[SecuritySession], SecurityValidation]:
        """
        Create a security session.

        Args:
            context: Security context for session
            duration_ms: Session duration in milliseconds
            requested_permissions: Permissions requested for session

        Returns:
            Tuple of (session or None, validation result)
        """
        requested_permissions = requested_permissions or []

        # Validate context
        validation = self.validate_context(context, requested_permissions)

        if not validation.valid:
            return None, validation

        # Create session
        now = datetime.now()
        session_id = str(uuid.uuid4())
        session_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)

        session = SecuritySession(
            session_id=session_id,
            agent_id=context.requester.agent_id,
            created_at=now.isoformat(),
            expires_at=(now + timedelta(milliseconds=duration_ms)).isoformat(),
            last_activity=now.isoformat(),
            trust_level=validation.trust_level,
            permissions=validation.granted_permissions,
            session_token=session_token,
            refresh_token=refresh_token,
            metadata=SessionMetadata(
                created_from="security_context",
                credential_ids=[c.credential_id for c in context.credentials],
                trust_chain_depth=len(context.trust_chain),
                original_ip=context.source_ip,
            ),
        )

        # Store session
        with self._lock:
            self._sessions[session_token] = session

        # Log audit
        self._log_audit(
            SecurityAuditEntry(
                audit_id=str(uuid.uuid4()),
                timestamp=now.isoformat(),
                event_type=SecurityEventType.SESSION_START,
                actor=context.requester.agent_id,
                action="create_session",
                result="success",
                trust_level=validation.trust_level,
                details=AuditDetails(
                    context_id=context.context_id,
                    ip_address=context.source_ip,
                ),
            )
        )

        return session, validation

    def validate_session(self, session_token: str) -> tuple[bool, Optional[SecuritySession]]:
        """
        Validate a session token.

        Args:
            session_token: Session token to validate

        Returns:
            Tuple of (is_valid, session or None)
        """
        with self._lock:
            session = self._sessions.get(session_token)

        if not session:
            return False, None

        # Check expiration
        expires_at = datetime.fromisoformat(session.expires_at.replace("Z", "+00:00").replace("+00:00", ""))
        if datetime.now() > expires_at:
            return False, None

        # Update last activity
        session.last_activity = datetime.now().isoformat()

        return True, session

    def end_session(self, session_token: str) -> bool:
        """
        End a security session.

        Args:
            session_token: Session token to end

        Returns:
            True if session was ended, False if not found
        """
        session = None
        with self._lock:
            if session_token in self._sessions:
                session = self._sessions.pop(session_token)

        if session:
            # Log audit (outside lock to avoid deadlock)
            self._log_audit(
                SecurityAuditEntry(
                    audit_id=str(uuid.uuid4()),
                    timestamp=datetime.now().isoformat(),
                    event_type=SecurityEventType.SESSION_END,
                    actor=session.agent_id,
                    action="end_session",
                    result="success",
                )
            )
            return True

        return False

    def revoke_credential(self, credential_id: str) -> None:
        """
        Revoke a credential.

        Args:
            credential_id: ID of credential to revoke
        """
        with self._lock:
            self._revoked_credentials.add(credential_id)

        self._log_audit(
            SecurityAuditEntry(
                audit_id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                event_type=SecurityEventType.CREDENTIAL_CHECK,
                actor="system",
                action="revoke_credential",
                result="success",
                target=credential_id,
            )
        )

    def check_rate_limit(self, identifier: str) -> RateLimitStatus:
        """
        Check rate limit for an identifier.

        Args:
            identifier: Agent ID or IP address

        Returns:
            RateLimitStatus
        """
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)

        with self._lock:
            if identifier not in self._rate_limit_counters:
                self._rate_limit_counters[identifier] = []

            # Clean old entries
            self._rate_limit_counters[identifier] = [
                ts for ts in self._rate_limit_counters[identifier]
                if ts > hour_ago
            ]

            timestamps = self._rate_limit_counters[identifier]

            # Count requests
            requests_last_minute = sum(1 for ts in timestamps if ts > minute_ago)
            requests_last_hour = len(timestamps)

            # Check limits
            if requests_last_minute >= self.rate_limit_config.requests_per_minute:
                return RateLimitStatus(
                    allowed=False,
                    remaining=0,
                    reset_at=(minute_ago + timedelta(minutes=1)).isoformat(),
                    retry_after_ms=60000,
                )

            if requests_last_hour >= self.rate_limit_config.requests_per_hour:
                return RateLimitStatus(
                    allowed=False,
                    remaining=0,
                    reset_at=(hour_ago + timedelta(hours=1)).isoformat(),
                    retry_after_ms=3600000,
                )

            # Record this request
            self._rate_limit_counters[identifier].append(now)

            remaining = min(
                self.rate_limit_config.requests_per_minute - requests_last_minute - 1,
                self.rate_limit_config.requests_per_hour - requests_last_hour - 1,
            )

            return RateLimitStatus(
                allowed=True,
                remaining=remaining,
                reset_at=(now + timedelta(minutes=1)).isoformat(),
            )

    def validate_input(self, input_text: str) -> InputValidationResult:
        """
        Validate input for security issues (prompt injection, etc.).

        Args:
            input_text: Input to validate

        Returns:
            InputValidationResult
        """
        warnings: list[str] = []
        blocked_patterns: list[str] = []

        # Check length
        if len(input_text) > self.input_validation_config.max_input_length:
            return InputValidationResult(
                valid=False,
                sanitized_input=None,
                blocked_patterns_found=["input_too_long"],
                warnings=["Input exceeds maximum length"],
            )

        # Check blocked patterns
        for pattern in self.input_validation_config.blocked_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                blocked_patterns.append(pattern)

        if blocked_patterns:
            return InputValidationResult(
                valid=False,
                sanitized_input=None,
                blocked_patterns_found=blocked_patterns,
                warnings=["Potentially dangerous patterns detected"],
            )

        # Sanitize if enabled
        sanitized = input_text
        if self.input_validation_config.escape_special_chars:
            # Escape HTML-like characters
            sanitized = sanitized.replace("<", "&lt;")
            sanitized = sanitized.replace(">", "&gt;")
            sanitized = sanitized.replace("&", "&amp;")

        return InputValidationResult(
            valid=True,
            sanitized_input=sanitized,
            blocked_patterns_found=[],
            warnings=warnings,
        )

    def add_trusted_issuer(self, issuer: str) -> None:
        """Add a trusted credential issuer."""
        if issuer not in self.trusted_issuers:
            self.trusted_issuers.append(issuer)

    def add_trusted_domain(self, domain: str) -> None:
        """Add a trusted SPIFFE domain."""
        if domain not in self.trusted_domains:
            self.trusted_domains.append(domain)

    def get_audit_log(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_types: Optional[list[SecurityEventType]] = None,
    ) -> list[SecurityAuditEntry]:
        """
        Get audit log entries.

        Args:
            start_time: Filter by start time
            end_time: Filter by end time
            event_types: Filter by event types

        Returns:
            List of audit entries
        """
        with self._lock:
            entries = self._audit_log.copy()

        if start_time:
            entries = [
                e for e in entries
                if datetime.fromisoformat(e.timestamp) >= start_time
            ]

        if end_time:
            entries = [
                e for e in entries
                if datetime.fromisoformat(e.timestamp) <= end_time
            ]

        if event_types:
            entries = [e for e in entries if e.event_type in event_types]

        return entries

    # ============================================
    # Private Helper Methods
    # ============================================

    def _validate_credential(self, credential: Credential) -> CredentialValidation:
        """Validate a single credential."""
        warnings: list[str] = []
        error: Optional[str] = None
        status = CredentialStatus.VALID
        trust_level = TrustLevel.MEDIUM
        valid_scopes = credential.scope.copy()
        invalid_scopes: list[str] = []

        # Check if revoked
        if credential.credential_id in self._revoked_credentials:
            status = CredentialStatus.REVOKED
            error = "Credential has been revoked"
            valid_scopes = []
            invalid_scopes = credential.scope.copy()
            trust_level = TrustLevel.NONE

        # Check expiration
        elif credential.expires_at:
            try:
                expires = datetime.fromisoformat(
                    credential.expires_at.replace("Z", "+00:00").replace("+00:00", "")
                )
                if datetime.now() > expires:
                    status = CredentialStatus.EXPIRED
                    error = "Credential has expired"
                    valid_scopes = []
                    invalid_scopes = credential.scope.copy()
                    trust_level = TrustLevel.NONE
                elif datetime.now() > expires - timedelta(hours=1):
                    warnings.append("Credential expires within 1 hour")
            except ValueError:
                warnings.append("Could not parse expiration date")

        # Check not_before
        if credential.not_before and status == CredentialStatus.VALID:
            try:
                not_before = datetime.fromisoformat(
                    credential.not_before.replace("Z", "+00:00").replace("+00:00", "")
                )
                if datetime.now() < not_before:
                    status = CredentialStatus.INVALID
                    error = "Credential not yet valid"
                    valid_scopes = []
                    invalid_scopes = credential.scope.copy()
                    trust_level = TrustLevel.NONE
            except ValueError:
                warnings.append("Could not parse not_before date")

        # Check issuer trust
        if status == CredentialStatus.VALID:
            if self.trusted_issuers and credential.issuer not in self.trusted_issuers:
                warnings.append(f"Issuer {credential.issuer} is not in trusted list")
                trust_level = TrustLevel.LOW

        # Adjust trust level based on credential type
        if status == CredentialStatus.VALID:
            if credential.credential_type in [CredentialType.MTLS_CERT, CredentialType.SPIFFE]:
                trust_level = TrustLevel.HIGH
            elif credential.credential_type == CredentialType.API_KEY:
                trust_level = TrustLevel.LOW

        return CredentialValidation(
            credential_id=credential.credential_id,
            status=status,
            trust_level=trust_level,
            valid_scopes=valid_scopes,
            invalid_scopes=invalid_scopes,
            expires_at=credential.expires_at,
            warnings=warnings,
            error=error,
        )

    def _validate_trust_chain(
        self,
        chain: list[TrustChainEntry],
        target_subject: str,
    ) -> TrustChainValidation:
        """Validate a trust chain."""
        warnings: list[str] = []
        broken_links: list[TrustChainBreak] = []
        effective_permissions: set[str] = set()

        if not chain:
            return TrustChainValidation(
                valid=False,
                chain_length=0,
                root_issuer="",
                final_subject="",
                effective_trust_level=TrustLevel.NONE,
                effective_permissions=[],
                broken_links=None,
                warnings=["Empty trust chain"],
            )

        # Check chain continuity
        for i, entry in enumerate(chain):
            # Check expiration
            try:
                expires = datetime.fromisoformat(
                    entry.expires_at.replace("Z", "+00:00").replace("+00:00", "")
                )
                if datetime.now() > expires:
                    broken_links.append(TrustChainBreak(
                        position=i,
                        issuer=entry.issuer,
                        subject=entry.subject,
                        reason="Entry has expired",
                        severity=SecuritySeverity.CRITICAL,
                    ))
            except ValueError:
                warnings.append(f"Could not parse expiration for entry {i}")

            # Check chain continuity (subject should match next issuer)
            if i < len(chain) - 1:
                next_entry = chain[i + 1]
                if entry.subject != next_entry.issuer:
                    broken_links.append(TrustChainBreak(
                        position=i,
                        issuer=entry.subject,
                        subject=next_entry.issuer,
                        reason="Chain discontinuity - subject does not match next issuer",
                        severity=SecuritySeverity.CRITICAL,
                    ))

            # Collect permissions (intersection for security)
            if i == 0:
                effective_permissions = set(entry.permissions)
            else:
                effective_permissions &= set(entry.permissions)

        # Check final subject matches target
        if chain[-1].subject != target_subject:
            warnings.append(f"Final subject {chain[-1].subject} does not match target {target_subject}")

        # Determine trust level
        trust_level = TrustLevel.HIGH if not broken_links else TrustLevel.LOW
        if any(bl.severity == SecuritySeverity.CRITICAL for bl in broken_links):
            trust_level = TrustLevel.NONE

        # Reduce trust for transitive delegations
        transitive_count = sum(1 for e in chain if e.delegation_type == DelegationType.TRANSITIVE)
        if transitive_count > 2:
            warnings.append("Many transitive delegations in chain")
            if trust_level == TrustLevel.HIGH:
                trust_level = TrustLevel.MEDIUM

        return TrustChainValidation(
            valid=len(broken_links) == 0,
            chain_length=len(chain),
            root_issuer=chain[0].issuer,
            final_subject=chain[-1].subject,
            effective_trust_level=trust_level,
            effective_permissions=list(effective_permissions),
            broken_links=broken_links if broken_links else None,
            warnings=warnings,
        )

    def _validate_spiffe_id(self, spiffe_id: str) -> list[SecurityWarning]:
        """Validate a SPIFFE ID format."""
        warnings: list[SecurityWarning] = []

        # SPIFFE ID format: spiffe://trust-domain/path
        if not spiffe_id.startswith("spiffe://"):
            warnings.append(SecurityWarning(
                warning_id=str(uuid.uuid4()),
                severity=SecuritySeverity.WARNING,
                category="spiffe",
                message="SPIFFE ID does not start with spiffe://",
                recommendation="Use format: spiffe://trust-domain/path",
            ))
            return warnings

        # Extract trust domain
        parts = spiffe_id[9:].split("/", 1)  # Remove "spiffe://"
        if not parts or not parts[0]:
            warnings.append(SecurityWarning(
                warning_id=str(uuid.uuid4()),
                severity=SecuritySeverity.WARNING,
                category="spiffe",
                message="SPIFFE ID missing trust domain",
            ))
            return warnings

        trust_domain = parts[0]

        # Check if trust domain is in trusted list
        if self.trusted_domains and trust_domain not in self.trusted_domains:
            warnings.append(SecurityWarning(
                warning_id=str(uuid.uuid4()),
                severity=SecuritySeverity.WARNING,
                category="spiffe",
                message=f"Trust domain {trust_domain} is not in trusted list",
                recommendation="Add trust domain to trusted list or verify identity",
            ))

        return warnings

    def _validate_session_token(self, session_token: str) -> list[SecurityWarning]:
        """Validate a session token."""
        warnings: list[SecurityWarning] = []

        with self._lock:
            session = self._sessions.get(session_token)

        if not session:
            warnings.append(SecurityWarning(
                warning_id=str(uuid.uuid4()),
                severity=SecuritySeverity.WARNING,
                category="session",
                message="Session token not found",
            ))
            return warnings

        # Check expiration
        try:
            expires = datetime.fromisoformat(
                session.expires_at.replace("Z", "+00:00").replace("+00:00", "")
            )
            if datetime.now() > expires:
                warnings.append(SecurityWarning(
                    warning_id=str(uuid.uuid4()),
                    severity=SecuritySeverity.CRITICAL,
                    category="session",
                    message="Session has expired",
                    recommendation="Create a new session",
                ))
            elif datetime.now() > expires - timedelta(minutes=5):
                warnings.append(SecurityWarning(
                    warning_id=str(uuid.uuid4()),
                    severity=SecuritySeverity.INFO,
                    category="session",
                    message="Session expires within 5 minutes",
                    recommendation="Consider refreshing session",
                ))
        except ValueError:
            warnings.append(SecurityWarning(
                warning_id=str(uuid.uuid4()),
                severity=SecuritySeverity.WARNING,
                category="session",
                message="Could not parse session expiration",
            ))

        return warnings

    def _calculate_trust_level(
        self,
        credential_validations: list[CredentialValidation],
        trust_chain_validation: TrustChainValidation,
    ) -> TrustLevel:
        """Calculate overall trust level."""
        if not credential_validations:
            return TrustLevel.NONE

        # Get highest credential trust level
        credential_levels = [cv.trust_level for cv in credential_validations if cv.status == CredentialStatus.VALID]
        if not credential_levels:
            return TrustLevel.NONE

        # Order of trust levels
        level_order = [TrustLevel.NONE, TrustLevel.LOW, TrustLevel.MEDIUM, TrustLevel.HIGH, TrustLevel.ABSOLUTE]

        max_cred_level = max(credential_levels, key=lambda x: level_order.index(x))

        # Combine with trust chain level
        if trust_chain_validation.valid:
            chain_level = trust_chain_validation.effective_trust_level
            # Take the minimum of credential and chain levels
            return min(max_cred_level, chain_level, key=lambda x: level_order.index(x))

        # If trust chain is invalid, reduce trust level
        if max_cred_level in [TrustLevel.HIGH, TrustLevel.ABSOLUTE]:
            return TrustLevel.MEDIUM

        return max_cred_level

    def _calculate_validation_expiry(
        self,
        credential_validations: list[CredentialValidation],
    ) -> str:
        """Calculate when validation expires (earliest credential expiry)."""
        expires_dates: list[datetime] = []

        for cv in credential_validations:
            if cv.status == CredentialStatus.VALID and cv.expires_at:
                try:
                    expires = datetime.fromisoformat(
                        cv.expires_at.replace("Z", "+00:00").replace("+00:00", "")
                    )
                    expires_dates.append(expires)
                except ValueError:
                    pass

        if expires_dates:
            return min(expires_dates).isoformat()

        # Default to 1 hour if no expiry found
        return (datetime.now() + timedelta(hours=1)).isoformat()

    def _log_audit(self, entry: SecurityAuditEntry) -> None:
        """Log an audit entry."""
        with self._lock:
            self._audit_log.append(entry)

        if self.audit_callback:
            try:
                self.audit_callback(entry)
            except Exception:
                pass  # Don't fail on audit callback errors


# ============================================
# Utility Functions
# ============================================


def create_credential(
    credential_type: CredentialType,
    value: str,
    issuer: str,
    subject: str,
    scope: list[str],
    expires_in_hours: int = 24,
) -> Credential:
    """
    Helper to create a credential.

    Args:
        credential_type: Type of credential
        value: Credential value (will be hashed)
        issuer: Credential issuer
        subject: Credential subject
        scope: Permission scopes
        expires_in_hours: Hours until expiration

    Returns:
        New Credential instance
    """
    now = datetime.now()

    # Hash the value
    hashed_value = hashlib.sha256(value.encode()).hexdigest()

    return Credential(
        credential_id=str(uuid.uuid4()),
        credential_type=credential_type,
        value=hashed_value,
        issuer=issuer,
        subject=subject,
        scope=scope,
        issued_at=now.isoformat(),
        expires_at=(now + timedelta(hours=expires_in_hours)).isoformat(),
    )


def create_trust_chain_entry(
    issuer: str,
    subject: str,
    delegation_type: DelegationType,
    permissions: list[str],
    expires_in_hours: int = 24,
    parent_entry_id: Optional[str] = None,
) -> TrustChainEntry:
    """
    Helper to create a trust chain entry.

    Args:
        issuer: Entity granting trust
        subject: Entity receiving trust
        delegation_type: Type of delegation
        permissions: Permissions granted
        expires_in_hours: Hours until expiration
        parent_entry_id: ID of parent entry

    Returns:
        New TrustChainEntry instance
    """
    now = datetime.now()

    return TrustChainEntry(
        entry_id=str(uuid.uuid4()),
        issuer=issuer,
        subject=subject,
        delegation_type=delegation_type,
        permissions=permissions,
        issued_at=now.isoformat(),
        expires_at=(now + timedelta(hours=expires_in_hours)).isoformat(),
        parent_entry_id=parent_entry_id,
    )


def create_security_context(
    requester: AgentSecurityIdentity,
    credentials: list[Credential],
    trust_chain: Optional[list[TrustChainEntry]] = None,
    session_token: Optional[str] = None,
    source_ip: Optional[str] = None,
) -> SecurityContext:
    """
    Helper to create a security context.

    Args:
        requester: Agent identity
        credentials: Credentials to include
        trust_chain: Trust chain entries
        session_token: Active session token
        source_ip: Source IP address

    Returns:
        New SecurityContext instance
    """
    return SecurityContext(
        context_id=str(uuid.uuid4()),
        requester=requester,
        credentials=credentials,
        trust_chain=trust_chain or [],
        request_timestamp=datetime.now().isoformat(),
        session_token=session_token,
        request_nonce=secrets.token_urlsafe(16),
        source_ip=source_ip,
    )
