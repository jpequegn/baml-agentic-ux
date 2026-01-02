"""
Security Layer for Agent Negotiation

Trust chain validation, credential management, and security context validation
for secure agent-to-agent communication.

Issue #57 - Phase 3: Agent-to-Agent Interface Negotiation (Security Implementation)
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any
import hashlib
import uuid


# ============================================
# Credential Types
# ============================================


class CredentialType(Enum):
    """Types of credentials for agent authentication."""

    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    MTLS_CERT = "mtls_cert"
    DID = "did"  # Decentralized Identifier
    VC = "vc"  # Verifiable Credential
    JWT = "jwt"  # JSON Web Token
    OAUTH2 = "oauth2"
    SAML = "saml"


class DelegationType(Enum):
    """Types of trust delegation between agents."""

    DIRECT = "direct"  # Direct trust relationship
    DELEGATED = "delegated"  # Trust delegated from another agent
    TRANSITIVE = "transitive"  # Trust inherited through chain
    ATTESTED = "attested"  # Attested by third party
    FEDERATED = "federated"  # Federated trust across domains


# ============================================
# Credential
# ============================================


@dataclass
class Credential:
    """
    A credential used for agent authentication.

    Contains encrypted/hashed credential value with scope and expiration.
    """

    credential_id: str
    credential_type: CredentialType
    value: str
    scope: list[str] = field(default_factory=list)
    issued_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    expires_at: str | None = None
    issuer: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        credential_type: CredentialType,
        value: str,
        scope: list[str] | None = None,
        expires_at: str | None = None,
        issuer: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> "Credential":
        """Create a new credential with auto-generated ID."""
        return cls(
            credential_id=str(uuid.uuid4()),
            credential_type=credential_type,
            value=value,
            scope=scope or [],
            expires_at=expires_at,
            issuer=issuer,
            metadata=metadata or {},
        )

    @classmethod
    def api_key(
        cls,
        key: str,
        scope: list[str] | None = None,
        expires_in_days: int | None = None,
    ) -> "Credential":
        """Create an API key credential."""
        expires_at = None
        if expires_in_days:
            expires_dt = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
            expires_at = expires_dt.isoformat()

        # Hash the API key for storage
        hashed_key = hashlib.sha256(key.encode()).hexdigest()

        return cls.create(
            credential_type=CredentialType.API_KEY,
            value=hashed_key,
            scope=scope,
            expires_at=expires_at,
        )

    @classmethod
    def bearer_token(
        cls,
        token: str,
        scope: list[str] | None = None,
        expires_at: str | None = None,
    ) -> "Credential":
        """Create a bearer token credential."""
        return cls.create(
            credential_type=CredentialType.BEARER_TOKEN,
            value=token,
            scope=scope,
            expires_at=expires_at,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "credential_id": self.credential_id,
            "credential_type": self.credential_type.value,
            "value": self.value,
            "scope": self.scope,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "issuer": self.issuer,
            "metadata": self.metadata,
        }
        return result


# ============================================
# Trust Chain
# ============================================


@dataclass
class TrustChainEntry:
    """
    An entry in a trust chain representing delegation.

    Tracks who delegated trust to whom, with permissions and expiration.
    """

    entry_id: str
    issuer: str
    subject: str
    delegation_type: DelegationType
    permissions: list[str] = field(default_factory=list)
    issued_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    expires_at: str | None = None
    signature: str | None = None
    previous_entry_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        issuer: str,
        subject: str,
        delegation_type: DelegationType,
        permissions: list[str] | None = None,
        expires_in_hours: int | None = None,
        signature: str | None = None,
        previous_entry_id: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> "TrustChainEntry":
        """Create a new trust chain entry."""
        expires_at = None
        if expires_in_hours:
            expires_dt = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
            expires_at = expires_dt.isoformat()

        return cls(
            entry_id=str(uuid.uuid4()),
            issuer=issuer,
            subject=subject,
            delegation_type=delegation_type,
            permissions=permissions or [],
            expires_at=expires_at,
            signature=signature,
            previous_entry_id=previous_entry_id,
            metadata=metadata or {},
        )

    def is_expired(self) -> bool:
        """Check if this trust chain entry has expired."""
        if not self.expires_at:
            return False

        expires_dt = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
        return datetime.now(timezone.utc) > expires_dt

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "entry_id": self.entry_id,
            "issuer": self.issuer,
            "subject": self.subject,
            "delegation_type": self.delegation_type.value,
            "permissions": self.permissions,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "signature": self.signature,
            "previous_entry_id": self.previous_entry_id,
            "metadata": self.metadata,
        }


# ============================================
# Security Context
# ============================================


@dataclass
class SecurityContext:
    """
    Complete security context for an agent request.

    Contains credentials, trust chain, and session information.
    """

    context_id: str
    requester_agent_id: str
    credentials: list[Credential] = field(default_factory=list)
    trust_chain: list[TrustChainEntry] = field(default_factory=list)
    session_token: str | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    expires_at: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        requester_agent_id: str,
        credentials: list[Credential] | None = None,
        trust_chain: list[TrustChainEntry] | None = None,
        session_token: str | None = None,
        expires_in_hours: int = 24,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> "SecurityContext":
        """Create a new security context."""
        expires_dt = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)

        return cls(
            context_id=str(uuid.uuid4()),
            requester_agent_id=requester_agent_id,
            credentials=credentials or [],
            trust_chain=trust_chain or [],
            session_token=session_token,
            expires_at=expires_dt.isoformat(),
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
        )

    def add_credential(self, credential: Credential) -> None:
        """Add a credential to this security context."""
        self.credentials.append(credential)

    def add_trust_entry(self, entry: TrustChainEntry) -> None:
        """Add a trust chain entry to this security context."""
        self.trust_chain.append(entry)

    def is_expired(self) -> bool:
        """Check if this security context has expired."""
        if not self.expires_at:
            return False

        expires_dt = datetime.fromisoformat(self.expires_at.replace('Z', '+00:00'))
        return datetime.now(timezone.utc) > expires_dt

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "context_id": self.context_id,
            "requester_agent_id": self.requester_agent_id,
            "credentials": [c.to_dict() for c in self.credentials],
            "trust_chain": [t.to_dict() for t in self.trust_chain],
            "session_token": self.session_token,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "metadata": self.metadata,
        }


# ============================================
# Security Validation Result
# ============================================


@dataclass
class SecurityValidation:
    """
    Result of security context validation.

    Contains validation status, trust level, permissions, and warnings.
    """

    validation_id: str
    valid: bool
    trust_level: str  # TrustLevel from agent_types
    granted_permissions: list[str] = field(default_factory=list)
    denied_permissions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    validation_time_ms: int = 0
    expires_at: str | None = None
    failure_reasons: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    @classmethod
    def create_valid(
        cls,
        trust_level: str,
        granted_permissions: list[str] | None = None,
        warnings: list[str] | None = None,
        expires_at: str | None = None,
        validation_time_ms: int = 0,
    ) -> "SecurityValidation":
        """Create a valid security validation result."""
        return cls(
            validation_id=str(uuid.uuid4()),
            valid=True,
            trust_level=trust_level,
            granted_permissions=granted_permissions or [],
            warnings=warnings or [],
            expires_at=expires_at,
            validation_time_ms=validation_time_ms,
        )

    @classmethod
    def create_invalid(
        cls,
        failure_reasons: list[str],
        denied_permissions: list[str] | None = None,
        validation_time_ms: int = 0,
    ) -> "SecurityValidation":
        """Create an invalid security validation result."""
        return cls(
            validation_id=str(uuid.uuid4()),
            valid=False,
            trust_level="none",
            denied_permissions=denied_permissions or [],
            failure_reasons=failure_reasons,
            validation_time_ms=validation_time_ms,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "validation_id": self.validation_id,
            "valid": self.valid,
            "trust_level": self.trust_level,
            "granted_permissions": self.granted_permissions,
            "denied_permissions": self.denied_permissions,
            "warnings": self.warnings,
            "validation_time_ms": self.validation_time_ms,
            "expires_at": self.expires_at,
            "failure_reasons": self.failure_reasons,
            "metadata": self.metadata,
        }


# ============================================
# Trust Chain Validator
# ============================================


class TrustChainValidator:
    """
    Validates trust chains for agent-to-agent communication.

    Ensures chains are unbroken, unexpired, and permissions are properly delegated.
    """

    def __init__(self, max_chain_length: int = 10):
        """
        Initialize the trust chain validator.

        Args:
            max_chain_length: Maximum allowed chain length to prevent abuse
        """
        self.max_chain_length = max_chain_length

    def validate_chain(
        self,
        trust_chain: list[TrustChainEntry],
        required_issuer: str | None = None,
        required_subject: str | None = None,
    ) -> tuple[bool, list[str]]:
        """
        Validate a complete trust chain.

        Args:
            trust_chain: List of trust chain entries to validate
            required_issuer: Optional root issuer requirement
            required_subject: Optional final subject requirement

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors: list[str] = []

        if not trust_chain:
            errors.append("Trust chain is empty")
            return False, errors

        # Check chain length
        if len(trust_chain) > self.max_chain_length:
            errors.append(
                f"Trust chain too long: {len(trust_chain)} > {self.max_chain_length}"
            )
            return False, errors

        # Check each entry for expiration
        for i, entry in enumerate(trust_chain):
            if entry.is_expired():
                errors.append(
                    f"Trust chain entry {i} (id: {entry.entry_id}) has expired"
                )

        # Validate chain continuity
        for i in range(1, len(trust_chain)):
            prev_entry = trust_chain[i - 1]
            curr_entry = trust_chain[i]

            # Subject of previous should be issuer of current
            if prev_entry.subject != curr_entry.issuer:
                errors.append(
                    f"Chain break at entry {i}: "
                    f"previous subject '{prev_entry.subject}' != "
                    f"current issuer '{curr_entry.issuer}'"
                )

            # Check previous_entry_id reference
            if curr_entry.previous_entry_id and curr_entry.previous_entry_id != prev_entry.entry_id:
                errors.append(
                    f"Entry {i} previous_entry_id mismatch: "
                    f"expected {prev_entry.entry_id}, got {curr_entry.previous_entry_id}"
                )

        # Validate root issuer if required
        if required_issuer and trust_chain[0].issuer != required_issuer:
            errors.append(
                f"Root issuer mismatch: "
                f"expected '{required_issuer}', got '{trust_chain[0].issuer}'"
            )

        # Validate final subject if required
        if required_subject and trust_chain[-1].subject != required_subject:
            errors.append(
                f"Final subject mismatch: "
                f"expected '{required_subject}', got '{trust_chain[-1].subject}'"
            )

        return len(errors) == 0, errors

    def check_delegation(
        self,
        trust_chain: list[TrustChainEntry],
        required_permissions: list[str],
    ) -> tuple[bool, list[str], list[str]]:
        """
        Check if permissions are properly delegated through the chain.

        Args:
            trust_chain: Trust chain to check
            required_permissions: Permissions needed

        Returns:
            Tuple of (has_permissions, granted_permissions, missing_permissions)
        """
        if not trust_chain:
            return False, [], required_permissions

        # Start with permissions from the first entry
        available_permissions = set(trust_chain[0].permissions)

        # Each subsequent entry can only delegate permissions it has
        for i in range(1, len(trust_chain)):
            entry = trust_chain[i]
            entry_perms = set(entry.permissions)

            # Can only delegate permissions available in chain so far
            if not entry_perms.issubset(available_permissions):
                # Some permissions in this entry weren't delegated to it
                unauthorized = entry_perms - available_permissions
                # Continue but note the limitation
                available_permissions = available_permissions.intersection(entry_perms)
            else:
                # Narrow down to what this entry actually delegates
                available_permissions = entry_perms

        # Check if we have all required permissions
        required_set = set(required_permissions)
        granted = list(available_permissions.intersection(required_set))
        missing = list(required_set - available_permissions)

        has_all = len(missing) == 0

        return has_all, granted, missing

    def compute_trust_level(
        self,
        trust_chain: list[TrustChainEntry],
    ) -> str:
        """
        Compute effective trust level based on the chain.

        The trust level is determined by the weakest link in the chain.

        Args:
            trust_chain: Trust chain to analyze

        Returns:
            Trust level string (maps to TrustLevel enum values)
        """
        if not trust_chain:
            return "none"

        # Map delegation types to trust levels
        delegation_to_trust = {
            DelegationType.DIRECT: "trusted",
            DelegationType.DELEGATED: "verified",
            DelegationType.TRANSITIVE: "verified",
            DelegationType.ATTESTED: "verified",
            DelegationType.FEDERATED: "basic",
        }

        trust_levels_order = ["none", "basic", "verified", "trusted", "privileged"]

        # Find minimum trust level in chain
        min_trust_level = "privileged"
        min_index = len(trust_levels_order) - 1

        for entry in trust_chain:
            entry_trust = delegation_to_trust.get(entry.delegation_type, "none")
            entry_index = trust_levels_order.index(entry_trust)

            if entry_index < min_index:
                min_index = entry_index
                min_trust_level = entry_trust

        return min_trust_level


# ============================================
# Credential Manager
# ============================================


class CredentialManager:
    """
    Manages credential validation and lifecycle.

    Validates credentials, checks expiration, and manages credential storage.
    """

    def __init__(self):
        """Initialize the credential manager."""
        self._credential_store: dict[str, Credential] = {}

    def validate_credential(
        self,
        credential: Credential,
        expected_type: CredentialType | None = None,
        required_scope: list[str] | None = None,
    ) -> tuple[bool, list[str]]:
        """
        Validate a credential.

        Args:
            credential: Credential to validate
            expected_type: Expected credential type
            required_scope: Required scope (all must be present)

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors: list[str] = []

        # Check type if specified
        if expected_type and credential.credential_type != expected_type:
            errors.append(
                f"Credential type mismatch: "
                f"expected {expected_type.value}, got {credential.credential_type.value}"
            )

        # Check expiration
        if self.check_expiration(credential):
            errors.append(f"Credential {credential.credential_id} has expired")

        # Check scope if specified
        if required_scope:
            credential_scopes = set(credential.scope)
            required_scopes = set(required_scope)

            if not required_scopes.issubset(credential_scopes):
                missing = required_scopes - credential_scopes
                errors.append(
                    f"Credential missing required scopes: {', '.join(missing)}"
                )

        # Basic format validation based on type
        type_errors = self._validate_credential_format(credential)
        errors.extend(type_errors)

        return len(errors) == 0, errors

    def check_expiration(self, credential: Credential) -> bool:
        """
        Check if a credential has expired.

        Args:
            credential: Credential to check

        Returns:
            True if expired, False otherwise
        """
        if not credential.expires_at:
            return False

        try:
            expires_dt = datetime.fromisoformat(
                credential.expires_at.replace('Z', '+00:00')
            )
            return datetime.now(timezone.utc) > expires_dt
        except (ValueError, AttributeError):
            # Invalid date format treated as expired
            return True

    def store_credential(self, credential: Credential) -> None:
        """
        Store a credential for later retrieval.

        Args:
            credential: Credential to store
        """
        self._credential_store[credential.credential_id] = credential

    def retrieve_credential(self, credential_id: str) -> Credential | None:
        """
        Retrieve a stored credential.

        Args:
            credential_id: ID of credential to retrieve

        Returns:
            Credential if found, None otherwise
        """
        return self._credential_store.get(credential_id)

    def revoke_credential(self, credential_id: str) -> bool:
        """
        Revoke a credential.

        Args:
            credential_id: ID of credential to revoke

        Returns:
            True if revoked, False if not found
        """
        if credential_id in self._credential_store:
            del self._credential_store[credential_id]
            return True
        return False

    def _validate_credential_format(self, credential: Credential) -> list[str]:
        """
        Validate credential format based on type.

        Args:
            credential: Credential to validate

        Returns:
            List of format validation errors
        """
        errors: list[str] = []

        if credential.credential_type == CredentialType.API_KEY:
            # API keys should be hashed (64 hex chars for SHA-256)
            if len(credential.value) != 64 or not all(
                c in "0123456789abcdef" for c in credential.value.lower()
            ):
                errors.append("API key should be SHA-256 hash (64 hex characters)")

        elif credential.credential_type == CredentialType.JWT:
            # JWT should have 3 parts separated by dots
            parts = credential.value.split('.')
            if len(parts) != 3:
                errors.append("JWT should have 3 parts (header.payload.signature)")

        # Add more type-specific validation as needed

        return errors


# ============================================
# Security Validator
# ============================================


class SecurityValidator:
    """
    Validates complete security contexts for agent requests.

    Combines credential validation, trust chain validation, and permission checking.
    """

    def __init__(
        self,
        credential_manager: CredentialManager | None = None,
        trust_chain_validator: TrustChainValidator | None = None,
    ):
        """
        Initialize the security validator.

        Args:
            credential_manager: Optional credential manager instance
            trust_chain_validator: Optional trust chain validator instance
        """
        self.credential_manager = credential_manager or CredentialManager()
        self.trust_chain_validator = trust_chain_validator or TrustChainValidator()

    def validate_context(
        self,
        context: SecurityContext,
        required_permissions: list[str] | None = None,
        minimum_trust_level: str = "none",
    ) -> SecurityValidation:
        """
        Validate a complete security context.

        Args:
            context: Security context to validate
            required_permissions: Permissions needed for the operation
            minimum_trust_level: Minimum trust level required

        Returns:
            SecurityValidation result
        """
        import time
        start_time = time.time()

        errors: list[str] = []
        warnings: list[str] = []
        granted_permissions: list[str] = []

        # Check context expiration
        if context.is_expired():
            errors.append("Security context has expired")
            return SecurityValidation.create_invalid(
                failure_reasons=errors,
                validation_time_ms=int((time.time() - start_time) * 1000),
            )

        # Validate all credentials
        for credential in context.credentials:
            is_valid, cred_errors = self.credential_manager.validate_credential(credential)
            if not is_valid:
                errors.extend(cred_errors)

            # Check expiration specifically
            if self.credential_manager.check_expiration(credential):
                warnings.append(
                    f"Credential {credential.credential_id} has expired"
                )

        # Validate trust chain
        if context.trust_chain:
            chain_valid, chain_errors = self.trust_chain_validator.validate_chain(
                context.trust_chain,
                required_subject=context.requester_agent_id,
            )
            if not chain_valid:
                errors.extend(chain_errors)

            # Check permissions through delegation
            if required_permissions:
                has_perms, granted, missing = self.trust_chain_validator.check_delegation(
                    context.trust_chain,
                    required_permissions,
                )
                granted_permissions = granted
                if not has_perms:
                    errors.append(
                        f"Missing required permissions: {', '.join(missing)}"
                    )

            # Compute trust level from chain
            trust_level = self.trust_chain_validator.compute_trust_level(
                context.trust_chain
            )
        else:
            # No trust chain, basic trust from credentials
            if context.credentials:
                trust_level = "basic"
                granted_permissions = required_permissions or []
            else:
                trust_level = "none"

        # Check if trust level meets minimum
        trust_levels_order = ["none", "basic", "verified", "trusted", "privileged"]
        try:
            context_trust_index = trust_levels_order.index(trust_level)
            min_trust_index = trust_levels_order.index(minimum_trust_level)

            if context_trust_index < min_trust_index:
                errors.append(
                    f"Insufficient trust level: {trust_level} < {minimum_trust_level}"
                )
        except ValueError:
            errors.append(f"Invalid trust level: {trust_level}")

        validation_time_ms = int((time.time() - start_time) * 1000)

        # Create result
        if errors:
            return SecurityValidation.create_invalid(
                failure_reasons=errors,
                denied_permissions=required_permissions or [],
                validation_time_ms=validation_time_ms,
            )
        else:
            return SecurityValidation.create_valid(
                trust_level=trust_level,
                granted_permissions=granted_permissions,
                warnings=warnings,
                expires_at=context.expires_at,
                validation_time_ms=validation_time_ms,
            )

    def check_permissions(
        self,
        context: SecurityContext,
        required_permissions: list[str],
    ) -> tuple[bool, list[str], list[str]]:
        """
        Check if a security context has required permissions.

        Args:
            context: Security context to check
            required_permissions: Permissions needed

        Returns:
            Tuple of (has_all_permissions, granted_permissions, missing_permissions)
        """
        if not context.trust_chain:
            # Without trust chain, we can't verify permissions
            return False, [], required_permissions

        return self.trust_chain_validator.check_delegation(
            context.trust_chain,
            required_permissions,
        )

    def create_session_token(
        self,
        agent_id: str,
        permissions: list[str] | None = None,
    ) -> str:
        """
        Create a session token for an agent.

        Args:
            agent_id: Agent identifier
            permissions: Permissions granted in this session

        Returns:
            Session token string
        """
        # Simple session token generation (production would use JWT or similar)
        token_data = f"{agent_id}:{datetime.now(timezone.utc).isoformat()}"
        if permissions:
            token_data += f":{','.join(permissions)}"

        token = hashlib.sha256(token_data.encode()).hexdigest()
        return token
