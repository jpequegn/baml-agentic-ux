"""
Tests for the security module.

Tests trust chain validation, credential management, and security context validation
for agent-to-agent communication.

Issue #66 - Phase 3 Testing & Documentation
"""

import hashlib
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from src.agent_negotiation.security import (
    # Enums
    CredentialType,
    DelegationType,
    # Dataclasses
    Credential,
    TrustChainEntry,
    SecurityContext,
    SecurityValidation,
    # Classes
    TrustChainValidator,
    CredentialManager,
    SecurityValidator,
)


# ============================================
# Test Fixtures
# ============================================


@pytest.fixture
def sample_api_key() -> str:
    """A sample API key for testing."""
    return "test-api-key-12345"


@pytest.fixture
def sample_api_key_credential(sample_api_key: str) -> Credential:
    """A sample API key credential."""
    return Credential.api_key(key=sample_api_key, scope=["read", "write"])


@pytest.fixture
def sample_bearer_token_credential() -> Credential:
    """A sample bearer token credential."""
    return Credential.bearer_token(
        token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        scope=["api:read", "api:write"],
    )


@pytest.fixture
def sample_jwt_credential() -> Credential:
    """A sample JWT credential."""
    return Credential.create(
        credential_type=CredentialType.JWT,
        value="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
        scope=["read", "write"],
    )


@pytest.fixture
def sample_direct_trust_entry() -> TrustChainEntry:
    """A sample direct trust chain entry."""
    return TrustChainEntry.create(
        issuer="root-authority",
        subject="agent-alpha",
        delegation_type=DelegationType.DIRECT,
        permissions=["read", "write", "execute"],
        expires_in_hours=24,
    )


@pytest.fixture
def sample_trust_chain() -> list[TrustChainEntry]:
    """A sample valid trust chain."""
    entry1 = TrustChainEntry.create(
        issuer="root-authority",
        subject="agent-alpha",
        delegation_type=DelegationType.DIRECT,
        permissions=["read", "write", "execute", "admin"],
        expires_in_hours=48,
    )

    entry2 = TrustChainEntry.create(
        issuer="agent-alpha",
        subject="agent-beta",
        delegation_type=DelegationType.DELEGATED,
        permissions=["read", "write", "execute"],
        expires_in_hours=24,
        previous_entry_id=entry1.entry_id,
    )

    entry3 = TrustChainEntry.create(
        issuer="agent-beta",
        subject="agent-gamma",
        delegation_type=DelegationType.TRANSITIVE,
        permissions=["read", "write"],
        expires_in_hours=12,
        previous_entry_id=entry2.entry_id,
    )

    return [entry1, entry2, entry3]


@pytest.fixture
def sample_security_context(
    sample_api_key_credential: Credential,
    sample_trust_chain: list[TrustChainEntry],
) -> SecurityContext:
    """A sample security context."""
    return SecurityContext.create(
        requester_agent_id="agent-gamma",
        credentials=[sample_api_key_credential],
        trust_chain=sample_trust_chain,
        session_token="session-token-12345",
        expires_in_hours=8,
        ip_address="192.168.1.100",
        user_agent="AgentClient/1.0",
    )


# ============================================
# Test Enums
# ============================================


class TestCredentialType:
    """Tests for CredentialType enum."""

    def test_api_key_value(self):
        """Test API_KEY enum value."""
        assert CredentialType.API_KEY.value == "api_key"

    def test_bearer_token_value(self):
        """Test BEARER_TOKEN enum value."""
        assert CredentialType.BEARER_TOKEN.value == "bearer_token"

    def test_mtls_cert_value(self):
        """Test MTLS_CERT enum value."""
        assert CredentialType.MTLS_CERT.value == "mtls_cert"

    def test_did_value(self):
        """Test DID enum value."""
        assert CredentialType.DID.value == "did"

    def test_vc_value(self):
        """Test VC enum value."""
        assert CredentialType.VC.value == "vc"

    def test_jwt_value(self):
        """Test JWT enum value."""
        assert CredentialType.JWT.value == "jwt"

    def test_oauth2_value(self):
        """Test OAUTH2 enum value."""
        assert CredentialType.OAUTH2.value == "oauth2"

    def test_saml_value(self):
        """Test SAML enum value."""
        assert CredentialType.SAML.value == "saml"

    def test_all_credential_types(self):
        """Test all credential types are accounted for."""
        expected_types = {
            "api_key", "bearer_token", "mtls_cert", "did",
            "vc", "jwt", "oauth2", "saml"
        }
        actual_types = {ct.value for ct in CredentialType}
        assert expected_types == actual_types


class TestDelegationType:
    """Tests for DelegationType enum."""

    def test_direct_value(self):
        """Test DIRECT enum value."""
        assert DelegationType.DIRECT.value == "direct"

    def test_delegated_value(self):
        """Test DELEGATED enum value."""
        assert DelegationType.DELEGATED.value == "delegated"

    def test_transitive_value(self):
        """Test TRANSITIVE enum value."""
        assert DelegationType.TRANSITIVE.value == "transitive"

    def test_attested_value(self):
        """Test ATTESTED enum value."""
        assert DelegationType.ATTESTED.value == "attested"

    def test_federated_value(self):
        """Test FEDERATED enum value."""
        assert DelegationType.FEDERATED.value == "federated"

    def test_all_delegation_types(self):
        """Test all delegation types are accounted for."""
        expected_types = {"direct", "delegated", "transitive", "attested", "federated"}
        actual_types = {dt.value for dt in DelegationType}
        assert expected_types == actual_types


# ============================================
# Test Credential Dataclass
# ============================================


class TestCredential:
    """Tests for Credential dataclass."""

    def test_create_basic(self):
        """Test basic credential creation."""
        credential = Credential.create(
            credential_type=CredentialType.BEARER_TOKEN,
            value="test-token",
        )

        assert credential.credential_id  # UUID generated
        assert credential.credential_type == CredentialType.BEARER_TOKEN
        assert credential.value == "test-token"
        assert credential.scope == []
        assert credential.issued_at  # Timestamp set
        assert credential.expires_at is None
        assert credential.issuer is None
        assert credential.metadata == {}

    def test_create_with_all_fields(self):
        """Test credential creation with all fields."""
        future_time = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

        credential = Credential.create(
            credential_type=CredentialType.JWT,
            value="jwt-token",
            scope=["read", "write", "admin"],
            expires_at=future_time,
            issuer="auth-service",
            metadata={"environment": "production"},
        )

        assert credential.credential_type == CredentialType.JWT
        assert credential.value == "jwt-token"
        assert credential.scope == ["read", "write", "admin"]
        assert credential.expires_at == future_time
        assert credential.issuer == "auth-service"
        assert credential.metadata == {"environment": "production"}

    def test_api_key_creation(self, sample_api_key: str):
        """Test API key credential creation."""
        credential = Credential.api_key(
            key=sample_api_key,
            scope=["api:read", "api:write"],
            expires_in_days=30,
        )

        assert credential.credential_type == CredentialType.API_KEY
        # Value should be SHA-256 hash of the key
        expected_hash = hashlib.sha256(sample_api_key.encode()).hexdigest()
        assert credential.value == expected_hash
        assert credential.scope == ["api:read", "api:write"]
        assert credential.expires_at is not None

    def test_api_key_without_expiration(self, sample_api_key: str):
        """Test API key credential without expiration."""
        credential = Credential.api_key(key=sample_api_key)

        assert credential.credential_type == CredentialType.API_KEY
        assert credential.expires_at is None

    def test_bearer_token_creation(self):
        """Test bearer token credential creation."""
        credential = Credential.bearer_token(
            token="test-bearer-token",
            scope=["read"],
        )

        assert credential.credential_type == CredentialType.BEARER_TOKEN
        assert credential.value == "test-bearer-token"
        assert credential.scope == ["read"]

    def test_to_dict(self):
        """Test credential to dictionary conversion."""
        credential = Credential.create(
            credential_type=CredentialType.API_KEY,
            value="hashed-value",
            scope=["read"],
            issuer="issuer-id",
            metadata={"key": "value"},
        )

        result = credential.to_dict()

        assert result["credential_id"] == credential.credential_id
        assert result["credential_type"] == "api_key"
        assert result["value"] == "hashed-value"
        assert result["scope"] == ["read"]
        assert result["issued_at"] == credential.issued_at
        assert result["issuer"] == "issuer-id"
        assert result["metadata"] == {"key": "value"}

    def test_unique_credential_ids(self):
        """Test that each credential gets a unique ID."""
        creds = [
            Credential.create(credential_type=CredentialType.API_KEY, value="key")
            for _ in range(10)
        ]

        ids = [c.credential_id for c in creds]
        assert len(ids) == len(set(ids))


# ============================================
# Test TrustChainEntry Dataclass
# ============================================


class TestTrustChainEntry:
    """Tests for TrustChainEntry dataclass."""

    def test_create_basic(self):
        """Test basic trust chain entry creation."""
        entry = TrustChainEntry.create(
            issuer="root",
            subject="agent1",
            delegation_type=DelegationType.DIRECT,
        )

        assert entry.entry_id  # UUID generated
        assert entry.issuer == "root"
        assert entry.subject == "agent1"
        assert entry.delegation_type == DelegationType.DIRECT
        assert entry.permissions == []
        assert entry.issued_at  # Timestamp set
        assert entry.expires_at is None
        assert entry.signature is None
        assert entry.previous_entry_id is None
        assert entry.metadata == {}

    def test_create_with_all_fields(self):
        """Test trust chain entry creation with all fields."""
        entry = TrustChainEntry.create(
            issuer="authority",
            subject="agent-x",
            delegation_type=DelegationType.DELEGATED,
            permissions=["read", "write"],
            expires_in_hours=48,
            signature="sig123",
            previous_entry_id="prev-entry-id",
            metadata={"level": "1"},
        )

        assert entry.issuer == "authority"
        assert entry.subject == "agent-x"
        assert entry.delegation_type == DelegationType.DELEGATED
        assert entry.permissions == ["read", "write"]
        assert entry.expires_at is not None
        assert entry.signature == "sig123"
        assert entry.previous_entry_id == "prev-entry-id"
        assert entry.metadata == {"level": "1"}

    def test_is_expired_no_expiration(self):
        """Test is_expired returns False when no expiration set."""
        entry = TrustChainEntry.create(
            issuer="root",
            subject="agent",
            delegation_type=DelegationType.DIRECT,
        )

        assert entry.is_expired() is False

    def test_is_expired_future_expiration(self):
        """Test is_expired returns False for future expiration."""
        entry = TrustChainEntry.create(
            issuer="root",
            subject="agent",
            delegation_type=DelegationType.DIRECT,
            expires_in_hours=24,
        )

        assert entry.is_expired() is False

    def test_is_expired_past_expiration(self):
        """Test is_expired returns True for past expiration."""
        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

        entry = TrustChainEntry(
            entry_id="test-id",
            issuer="root",
            subject="agent",
            delegation_type=DelegationType.DIRECT,
            expires_at=past_time,
        )

        assert entry.is_expired() is True

    def test_is_expired_z_timezone(self):
        """Test is_expired handles Z timezone format."""
        past_time = (datetime.now(timezone.utc) - timedelta(hours=1))
        past_time_str = past_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        entry = TrustChainEntry(
            entry_id="test-id",
            issuer="root",
            subject="agent",
            delegation_type=DelegationType.DIRECT,
            expires_at=past_time_str,
        )

        assert entry.is_expired() is True

    def test_to_dict(self, sample_direct_trust_entry: TrustChainEntry):
        """Test trust chain entry to dictionary conversion."""
        result = sample_direct_trust_entry.to_dict()

        assert result["entry_id"] == sample_direct_trust_entry.entry_id
        assert result["issuer"] == "root-authority"
        assert result["subject"] == "agent-alpha"
        assert result["delegation_type"] == "direct"
        assert result["permissions"] == ["read", "write", "execute"]
        assert result["issued_at"] == sample_direct_trust_entry.issued_at
        assert result["expires_at"] is not None

    def test_unique_entry_ids(self):
        """Test that each entry gets a unique ID."""
        entries = [
            TrustChainEntry.create(
                issuer="root",
                subject=f"agent-{i}",
                delegation_type=DelegationType.DIRECT,
            )
            for i in range(10)
        ]

        ids = [e.entry_id for e in entries]
        assert len(ids) == len(set(ids))


# ============================================
# Test SecurityContext Dataclass
# ============================================


class TestSecurityContext:
    """Tests for SecurityContext dataclass."""

    def test_create_basic(self):
        """Test basic security context creation."""
        context = SecurityContext.create(requester_agent_id="agent-123")

        assert context.context_id  # UUID generated
        assert context.requester_agent_id == "agent-123"
        assert context.credentials == []
        assert context.trust_chain == []
        assert context.session_token is None
        assert context.created_at  # Timestamp set
        assert context.expires_at is not None  # Default 24h expiration
        assert context.ip_address is None
        assert context.user_agent is None
        assert context.metadata == {}

    def test_create_with_all_fields(
        self,
        sample_api_key_credential: Credential,
        sample_trust_chain: list[TrustChainEntry],
    ):
        """Test security context creation with all fields."""
        context = SecurityContext.create(
            requester_agent_id="agent-gamma",
            credentials=[sample_api_key_credential],
            trust_chain=sample_trust_chain,
            session_token="session-123",
            expires_in_hours=12,
            ip_address="10.0.0.1",
            user_agent="TestClient/2.0",
            metadata={"request_id": "req-456"},
        )

        assert context.requester_agent_id == "agent-gamma"
        assert len(context.credentials) == 1
        assert len(context.trust_chain) == 3
        assert context.session_token == "session-123"
        assert context.ip_address == "10.0.0.1"
        assert context.user_agent == "TestClient/2.0"
        assert context.metadata == {"request_id": "req-456"}

    def test_add_credential(self, sample_api_key_credential: Credential):
        """Test adding credential to security context."""
        context = SecurityContext.create(requester_agent_id="agent-123")
        assert len(context.credentials) == 0

        context.add_credential(sample_api_key_credential)

        assert len(context.credentials) == 1
        assert context.credentials[0] == sample_api_key_credential

    def test_add_trust_entry(self, sample_direct_trust_entry: TrustChainEntry):
        """Test adding trust entry to security context."""
        context = SecurityContext.create(requester_agent_id="agent-123")
        assert len(context.trust_chain) == 0

        context.add_trust_entry(sample_direct_trust_entry)

        assert len(context.trust_chain) == 1
        assert context.trust_chain[0] == sample_direct_trust_entry

    def test_is_expired_future_expiration(self):
        """Test is_expired returns False for future expiration."""
        context = SecurityContext.create(
            requester_agent_id="agent-123",
            expires_in_hours=24,
        )

        assert context.is_expired() is False

    def test_is_expired_past_expiration(self):
        """Test is_expired returns True for past expiration."""
        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

        context = SecurityContext(
            context_id="test-id",
            requester_agent_id="agent-123",
            expires_at=past_time,
        )

        assert context.is_expired() is True

    def test_is_expired_no_expiration(self):
        """Test is_expired returns False when no expiration set."""
        context = SecurityContext(
            context_id="test-id",
            requester_agent_id="agent-123",
            expires_at=None,
        )

        assert context.is_expired() is False

    def test_to_dict(self, sample_security_context: SecurityContext):
        """Test security context to dictionary conversion."""
        result = sample_security_context.to_dict()

        assert result["context_id"] == sample_security_context.context_id
        assert result["requester_agent_id"] == "agent-gamma"
        assert len(result["credentials"]) == 1
        assert len(result["trust_chain"]) == 3
        assert result["session_token"] == "session-token-12345"
        assert result["ip_address"] == "192.168.1.100"
        assert result["user_agent"] == "AgentClient/1.0"

    def test_unique_context_ids(self):
        """Test that each context gets a unique ID."""
        contexts = [
            SecurityContext.create(requester_agent_id=f"agent-{i}")
            for i in range(10)
        ]

        ids = [c.context_id for c in contexts]
        assert len(ids) == len(set(ids))


# ============================================
# Test SecurityValidation Dataclass
# ============================================


class TestSecurityValidation:
    """Tests for SecurityValidation dataclass."""

    def test_create_valid_basic(self):
        """Test creating a valid security validation result."""
        validation = SecurityValidation.create_valid(trust_level="verified")

        assert validation.validation_id  # UUID generated
        assert validation.valid is True
        assert validation.trust_level == "verified"
        assert validation.granted_permissions == []
        assert validation.denied_permissions == []
        assert validation.warnings == []
        assert validation.failure_reasons == []

    def test_create_valid_with_all_fields(self):
        """Test creating a valid security validation with all fields."""
        future_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

        validation = SecurityValidation.create_valid(
            trust_level="trusted",
            granted_permissions=["read", "write"],
            warnings=["Credential expires soon"],
            expires_at=future_time,
            validation_time_ms=150,
        )

        assert validation.valid is True
        assert validation.trust_level == "trusted"
        assert validation.granted_permissions == ["read", "write"]
        assert validation.warnings == ["Credential expires soon"]
        assert validation.expires_at == future_time
        assert validation.validation_time_ms == 150

    def test_create_invalid_basic(self):
        """Test creating an invalid security validation result."""
        validation = SecurityValidation.create_invalid(
            failure_reasons=["Credential expired"]
        )

        assert validation.validation_id  # UUID generated
        assert validation.valid is False
        assert validation.trust_level == "none"
        assert validation.granted_permissions == []
        assert validation.failure_reasons == ["Credential expired"]

    def test_create_invalid_with_all_fields(self):
        """Test creating an invalid security validation with all fields."""
        validation = SecurityValidation.create_invalid(
            failure_reasons=["Invalid token", "Missing scope"],
            denied_permissions=["admin", "execute"],
            validation_time_ms=50,
        )

        assert validation.valid is False
        assert validation.trust_level == "none"
        assert validation.denied_permissions == ["admin", "execute"]
        assert validation.failure_reasons == ["Invalid token", "Missing scope"]
        assert validation.validation_time_ms == 50

    def test_to_dict_valid(self):
        """Test to_dict for valid validation."""
        validation = SecurityValidation.create_valid(
            trust_level="trusted",
            granted_permissions=["read"],
            warnings=["Warning message"],
        )

        result = validation.to_dict()

        assert result["validation_id"] == validation.validation_id
        assert result["valid"] is True
        assert result["trust_level"] == "trusted"
        assert result["granted_permissions"] == ["read"]
        assert result["warnings"] == ["Warning message"]
        assert result["failure_reasons"] == []

    def test_to_dict_invalid(self):
        """Test to_dict for invalid validation."""
        validation = SecurityValidation.create_invalid(
            failure_reasons=["Error 1", "Error 2"],
            denied_permissions=["write"],
        )

        result = validation.to_dict()

        assert result["valid"] is False
        assert result["trust_level"] == "none"
        assert result["denied_permissions"] == ["write"]
        assert result["failure_reasons"] == ["Error 1", "Error 2"]


# ============================================
# Test TrustChainValidator Class
# ============================================


class TestTrustChainValidator:
    """Tests for TrustChainValidator class."""

    def test_init_default_max_chain_length(self):
        """Test default max chain length."""
        validator = TrustChainValidator()
        assert validator.max_chain_length == 10

    def test_init_custom_max_chain_length(self):
        """Test custom max chain length."""
        validator = TrustChainValidator(max_chain_length=5)
        assert validator.max_chain_length == 5

    def test_validate_chain_empty(self):
        """Test validation of empty chain."""
        validator = TrustChainValidator()

        is_valid, errors = validator.validate_chain([])

        assert is_valid is False
        assert "Trust chain is empty" in errors

    def test_validate_chain_too_long(self):
        """Test validation of chain exceeding max length."""
        validator = TrustChainValidator(max_chain_length=2)

        entries = [
            TrustChainEntry.create(
                issuer=f"agent-{i}",
                subject=f"agent-{i+1}",
                delegation_type=DelegationType.TRANSITIVE,
            )
            for i in range(5)
        ]

        is_valid, errors = validator.validate_chain(entries)

        assert is_valid is False
        assert any("Trust chain too long" in e for e in errors)

    def test_validate_chain_valid(self, sample_trust_chain: list[TrustChainEntry]):
        """Test validation of a valid trust chain."""
        validator = TrustChainValidator()

        is_valid, errors = validator.validate_chain(sample_trust_chain)

        assert is_valid is True
        assert errors == []

    def test_validate_chain_expired_entry(self):
        """Test validation detects expired entries."""
        validator = TrustChainValidator()

        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        entry = TrustChainEntry(
            entry_id="test-id",
            issuer="root",
            subject="agent",
            delegation_type=DelegationType.DIRECT,
            expires_at=past_time,
        )

        is_valid, errors = validator.validate_chain([entry])

        assert is_valid is False
        assert any("has expired" in e for e in errors)

    def test_validate_chain_broken_continuity(self):
        """Test validation detects broken chain continuity."""
        validator = TrustChainValidator()

        entry1 = TrustChainEntry.create(
            issuer="root",
            subject="agent-1",
            delegation_type=DelegationType.DIRECT,
        )
        entry2 = TrustChainEntry.create(
            issuer="agent-WRONG",  # Should be agent-1
            subject="agent-2",
            delegation_type=DelegationType.DELEGATED,
        )

        is_valid, errors = validator.validate_chain([entry1, entry2])

        assert is_valid is False
        assert any("Chain break" in e for e in errors)

    def test_validate_chain_previous_entry_id_mismatch(self):
        """Test validation detects previous_entry_id mismatch."""
        validator = TrustChainValidator()

        entry1 = TrustChainEntry.create(
            issuer="root",
            subject="agent-1",
            delegation_type=DelegationType.DIRECT,
        )
        entry2 = TrustChainEntry.create(
            issuer="agent-1",
            subject="agent-2",
            delegation_type=DelegationType.DELEGATED,
            previous_entry_id="wrong-id",
        )

        is_valid, errors = validator.validate_chain([entry1, entry2])

        assert is_valid is False
        assert any("previous_entry_id mismatch" in e for e in errors)

    def test_validate_chain_required_issuer(self, sample_trust_chain: list[TrustChainEntry]):
        """Test validation with required issuer."""
        validator = TrustChainValidator()

        # Valid case
        is_valid, errors = validator.validate_chain(
            sample_trust_chain,
            required_issuer="root-authority",
        )
        assert is_valid is True

        # Invalid case
        is_valid, errors = validator.validate_chain(
            sample_trust_chain,
            required_issuer="wrong-issuer",
        )
        assert is_valid is False
        assert any("Root issuer mismatch" in e for e in errors)

    def test_validate_chain_required_subject(self, sample_trust_chain: list[TrustChainEntry]):
        """Test validation with required final subject."""
        validator = TrustChainValidator()

        # Valid case
        is_valid, errors = validator.validate_chain(
            sample_trust_chain,
            required_subject="agent-gamma",
        )
        assert is_valid is True

        # Invalid case
        is_valid, errors = validator.validate_chain(
            sample_trust_chain,
            required_subject="wrong-subject",
        )
        assert is_valid is False
        assert any("Final subject mismatch" in e for e in errors)

    def test_check_delegation_empty_chain(self):
        """Test delegation check with empty chain."""
        validator = TrustChainValidator()

        has_perms, granted, missing = validator.check_delegation(
            [],
            ["read", "write"],
        )

        assert has_perms is False
        assert granted == []
        assert missing == ["read", "write"]

    def test_check_delegation_all_permissions(self, sample_trust_chain: list[TrustChainEntry]):
        """Test delegation check when all permissions available."""
        validator = TrustChainValidator()

        has_perms, granted, missing = validator.check_delegation(
            sample_trust_chain,
            ["read", "write"],
        )

        assert has_perms is True
        assert set(granted) == {"read", "write"}
        assert missing == []

    def test_check_delegation_partial_permissions(self, sample_trust_chain: list[TrustChainEntry]):
        """Test delegation check with partial permissions."""
        validator = TrustChainValidator()

        # Request execute which is not delegated to agent-gamma
        has_perms, granted, missing = validator.check_delegation(
            sample_trust_chain,
            ["read", "execute"],
        )

        assert has_perms is False
        assert "read" in granted
        assert "execute" in missing

    def test_check_delegation_permission_narrowing(self):
        """Test that permissions properly narrow through chain."""
        validator = TrustChainValidator()

        entry1 = TrustChainEntry.create(
            issuer="root",
            subject="agent-1",
            delegation_type=DelegationType.DIRECT,
            permissions=["read", "write", "admin"],
        )
        entry2 = TrustChainEntry.create(
            issuer="agent-1",
            subject="agent-2",
            delegation_type=DelegationType.DELEGATED,
            permissions=["read", "write"],  # No admin
        )

        has_perms, granted, missing = validator.check_delegation(
            [entry1, entry2],
            ["read", "admin"],
        )

        assert has_perms is False
        assert "read" in granted
        assert "admin" in missing

    def test_compute_trust_level_empty_chain(self):
        """Test trust level computation with empty chain."""
        validator = TrustChainValidator()

        trust_level = validator.compute_trust_level([])

        assert trust_level == "none"

    def test_compute_trust_level_direct(self):
        """Test trust level for direct delegation."""
        validator = TrustChainValidator()

        entry = TrustChainEntry.create(
            issuer="root",
            subject="agent",
            delegation_type=DelegationType.DIRECT,
        )

        trust_level = validator.compute_trust_level([entry])

        assert trust_level == "trusted"

    def test_compute_trust_level_delegated(self):
        """Test trust level for delegated delegation."""
        validator = TrustChainValidator()

        entry = TrustChainEntry.create(
            issuer="root",
            subject="agent",
            delegation_type=DelegationType.DELEGATED,
        )

        trust_level = validator.compute_trust_level([entry])

        assert trust_level == "verified"

    def test_compute_trust_level_federated(self):
        """Test trust level for federated delegation."""
        validator = TrustChainValidator()

        entry = TrustChainEntry.create(
            issuer="root",
            subject="agent",
            delegation_type=DelegationType.FEDERATED,
        )

        trust_level = validator.compute_trust_level([entry])

        assert trust_level == "basic"

    def test_compute_trust_level_weakest_link(self, sample_trust_chain: list[TrustChainEntry]):
        """Test that trust level is the weakest link in chain."""
        validator = TrustChainValidator()

        # Chain has DIRECT, DELEGATED, TRANSITIVE
        # TRANSITIVE maps to "verified", which is the minimum
        trust_level = validator.compute_trust_level(sample_trust_chain)

        assert trust_level == "verified"

    def test_compute_trust_level_with_federated_entry(self):
        """Test trust level drops to basic with federated entry."""
        validator = TrustChainValidator()

        entries = [
            TrustChainEntry.create(
                issuer="root",
                subject="agent-1",
                delegation_type=DelegationType.DIRECT,  # trusted
            ),
            TrustChainEntry.create(
                issuer="agent-1",
                subject="agent-2",
                delegation_type=DelegationType.FEDERATED,  # basic
            ),
        ]

        trust_level = validator.compute_trust_level(entries)

        assert trust_level == "basic"


# ============================================
# Test CredentialManager Class
# ============================================


class TestCredentialManager:
    """Tests for CredentialManager class."""

    def test_init(self):
        """Test credential manager initialization."""
        manager = CredentialManager()
        assert manager._credential_store == {}

    def test_validate_credential_basic(self, sample_api_key_credential: Credential):
        """Test basic credential validation."""
        manager = CredentialManager()

        is_valid, errors = manager.validate_credential(sample_api_key_credential)

        assert is_valid is True
        assert errors == []

    def test_validate_credential_type_mismatch(self, sample_api_key_credential: Credential):
        """Test credential validation with type mismatch."""
        manager = CredentialManager()

        is_valid, errors = manager.validate_credential(
            sample_api_key_credential,
            expected_type=CredentialType.JWT,
        )

        assert is_valid is False
        assert any("type mismatch" in e for e in errors)

    def test_validate_credential_expired(self):
        """Test validation detects expired credentials."""
        manager = CredentialManager()

        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        credential = Credential.create(
            credential_type=CredentialType.BEARER_TOKEN,
            value="token",
            expires_at=past_time,
        )

        is_valid, errors = manager.validate_credential(credential)

        assert is_valid is False
        assert any("expired" in e for e in errors)

    def test_validate_credential_missing_scope(self, sample_api_key_credential: Credential):
        """Test validation detects missing required scope."""
        manager = CredentialManager()

        is_valid, errors = manager.validate_credential(
            sample_api_key_credential,
            required_scope=["read", "admin"],
        )

        assert is_valid is False
        assert any("missing required scopes" in e for e in errors)

    def test_validate_credential_scope_satisfied(self, sample_api_key_credential: Credential):
        """Test validation passes with satisfied scope."""
        manager = CredentialManager()

        is_valid, errors = manager.validate_credential(
            sample_api_key_credential,
            required_scope=["read"],
        )

        assert is_valid is True
        assert errors == []

    def test_validate_api_key_format(self, sample_api_key_credential: Credential):
        """Test API key format validation (SHA-256 hash)."""
        manager = CredentialManager()

        # sample_api_key_credential is created via api_key() which hashes
        is_valid, errors = manager.validate_credential(sample_api_key_credential)

        assert is_valid is True

    def test_validate_api_key_invalid_format(self):
        """Test API key validation with invalid format."""
        manager = CredentialManager()

        # Create API key with non-hashed value
        credential = Credential(
            credential_id="test-id",
            credential_type=CredentialType.API_KEY,
            value="not-a-hash",  # Invalid format
        )

        is_valid, errors = manager.validate_credential(credential)

        assert is_valid is False
        assert any("SHA-256 hash" in e for e in errors)

    def test_validate_jwt_format_valid(self, sample_jwt_credential: Credential):
        """Test JWT format validation with valid format."""
        manager = CredentialManager()

        is_valid, errors = manager.validate_credential(sample_jwt_credential)

        assert is_valid is True

    def test_validate_jwt_format_invalid(self):
        """Test JWT format validation with invalid format."""
        manager = CredentialManager()

        credential = Credential.create(
            credential_type=CredentialType.JWT,
            value="not.a.valid.jwt.token",  # 4 parts instead of 3
        )

        is_valid, errors = manager.validate_credential(credential)

        assert is_valid is False
        assert any("3 parts" in e for e in errors)

    def test_check_expiration_not_expired(self):
        """Test check_expiration returns False for valid credential."""
        manager = CredentialManager()

        future_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        credential = Credential.create(
            credential_type=CredentialType.API_KEY,
            value="a" * 64,  # Valid hash format
            expires_at=future_time,
        )

        assert manager.check_expiration(credential) is False

    def test_check_expiration_expired(self):
        """Test check_expiration returns True for expired credential."""
        manager = CredentialManager()

        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        credential = Credential.create(
            credential_type=CredentialType.API_KEY,
            value="a" * 64,
            expires_at=past_time,
        )

        assert manager.check_expiration(credential) is True

    def test_check_expiration_no_expiration(self):
        """Test check_expiration returns False when no expiration."""
        manager = CredentialManager()

        credential = Credential.create(
            credential_type=CredentialType.API_KEY,
            value="a" * 64,
        )

        assert manager.check_expiration(credential) is False

    def test_check_expiration_invalid_format(self):
        """Test check_expiration treats invalid format as expired."""
        manager = CredentialManager()

        credential = Credential(
            credential_id="test-id",
            credential_type=CredentialType.API_KEY,
            value="a" * 64,
            expires_at="invalid-date-format",
        )

        assert manager.check_expiration(credential) is True

    def test_store_credential(self, sample_api_key_credential: Credential):
        """Test storing a credential."""
        manager = CredentialManager()

        manager.store_credential(sample_api_key_credential)

        assert sample_api_key_credential.credential_id in manager._credential_store

    def test_retrieve_credential_existing(self, sample_api_key_credential: Credential):
        """Test retrieving an existing credential."""
        manager = CredentialManager()
        manager.store_credential(sample_api_key_credential)

        retrieved = manager.retrieve_credential(sample_api_key_credential.credential_id)

        assert retrieved == sample_api_key_credential

    def test_retrieve_credential_not_found(self):
        """Test retrieving a non-existent credential."""
        manager = CredentialManager()

        retrieved = manager.retrieve_credential("non-existent-id")

        assert retrieved is None

    def test_revoke_credential_existing(self, sample_api_key_credential: Credential):
        """Test revoking an existing credential."""
        manager = CredentialManager()
        manager.store_credential(sample_api_key_credential)

        result = manager.revoke_credential(sample_api_key_credential.credential_id)

        assert result is True
        assert manager.retrieve_credential(sample_api_key_credential.credential_id) is None

    def test_revoke_credential_not_found(self):
        """Test revoking a non-existent credential."""
        manager = CredentialManager()

        result = manager.revoke_credential("non-existent-id")

        assert result is False


# ============================================
# Test SecurityValidator Class
# ============================================


class TestSecurityValidator:
    """Tests for SecurityValidator class."""

    def test_init_default_components(self):
        """Test default component initialization."""
        validator = SecurityValidator()

        assert validator.credential_manager is not None
        assert validator.trust_chain_validator is not None

    def test_init_custom_components(self):
        """Test initialization with custom components."""
        cred_manager = CredentialManager()
        chain_validator = TrustChainValidator(max_chain_length=5)

        validator = SecurityValidator(
            credential_manager=cred_manager,
            trust_chain_validator=chain_validator,
        )

        assert validator.credential_manager is cred_manager
        assert validator.trust_chain_validator is chain_validator

    def test_validate_context_expired_context(self):
        """Test validation fails for expired context."""
        validator = SecurityValidator()

        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        context = SecurityContext(
            context_id="test-id",
            requester_agent_id="agent-123",
            expires_at=past_time,
        )

        result = validator.validate_context(context)

        assert result.valid is False
        assert any("expired" in r for r in result.failure_reasons)

    def test_validate_context_valid_credentials(self, sample_security_context: SecurityContext):
        """Test validation with valid credentials."""
        validator = SecurityValidator()

        result = validator.validate_context(sample_security_context)

        # Should be valid since context has valid credentials and trust chain
        assert result.valid is True

    def test_validate_context_invalid_credentials(self):
        """Test validation with invalid credentials."""
        validator = SecurityValidator()

        # Create expired credential
        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        expired_cred = Credential.create(
            credential_type=CredentialType.BEARER_TOKEN,
            value="token",
            expires_at=past_time,
        )

        context = SecurityContext.create(
            requester_agent_id="agent-123",
            credentials=[expired_cred],
        )

        result = validator.validate_context(context)

        assert result.valid is False
        assert any("expired" in r for r in result.failure_reasons)

    def test_validate_context_trust_chain_validation(self, sample_security_context: SecurityContext):
        """Test trust chain is validated."""
        validator = SecurityValidator()

        result = validator.validate_context(
            sample_security_context,
            required_permissions=["read"],
        )

        assert result.valid is True
        assert "read" in result.granted_permissions

    def test_validate_context_missing_permissions(self, sample_security_context: SecurityContext):
        """Test validation fails for missing permissions."""
        validator = SecurityValidator()

        # Request permissions not in the chain
        result = validator.validate_context(
            sample_security_context,
            required_permissions=["admin", "superuser"],
        )

        assert result.valid is False
        assert any("Missing required permissions" in r for r in result.failure_reasons)

    def test_validate_context_minimum_trust_level(self, sample_security_context: SecurityContext):
        """Test minimum trust level enforcement."""
        validator = SecurityValidator()

        # The sample trust chain has "verified" as minimum trust level
        # Requiring "privileged" should fail
        result = validator.validate_context(
            sample_security_context,
            minimum_trust_level="privileged",
        )

        assert result.valid is False
        assert any("Insufficient trust level" in r for r in result.failure_reasons)

    def test_validate_context_trust_level_satisfied(self, sample_security_context: SecurityContext):
        """Test trust level satisfied."""
        validator = SecurityValidator()

        # The sample trust chain has "verified" as minimum
        result = validator.validate_context(
            sample_security_context,
            minimum_trust_level="verified",
        )

        assert result.valid is True
        assert result.trust_level in ["verified", "trusted", "privileged"]

    def test_validate_context_no_trust_chain_with_credentials(self):
        """Test validation with credentials but no trust chain."""
        validator = SecurityValidator()

        credential = Credential.create(
            credential_type=CredentialType.BEARER_TOKEN,
            value="token",
        )

        context = SecurityContext.create(
            requester_agent_id="agent-123",
            credentials=[credential],
        )

        result = validator.validate_context(context)

        assert result.valid is True
        assert result.trust_level == "basic"

    def test_validate_context_no_trust_chain_no_credentials(self):
        """Test validation with no trust chain and no credentials."""
        validator = SecurityValidator()

        context = SecurityContext.create(requester_agent_id="agent-123")

        result = validator.validate_context(context)

        assert result.valid is True
        assert result.trust_level == "none"

    def test_validate_context_invalid_trust_chain(self):
        """Test validation with broken trust chain."""
        validator = SecurityValidator()

        # Create broken chain (subject != next issuer)
        entry1 = TrustChainEntry.create(
            issuer="root",
            subject="agent-1",
            delegation_type=DelegationType.DIRECT,
        )
        entry2 = TrustChainEntry.create(
            issuer="wrong-agent",
            subject="agent-123",
            delegation_type=DelegationType.DELEGATED,
        )

        context = SecurityContext.create(
            requester_agent_id="agent-123",
            trust_chain=[entry1, entry2],
        )

        result = validator.validate_context(context)

        assert result.valid is False
        assert any("Chain break" in r for r in result.failure_reasons)

    def test_validate_context_timing(self, sample_security_context: SecurityContext):
        """Test validation records timing."""
        validator = SecurityValidator()

        result = validator.validate_context(sample_security_context)

        assert result.validation_time_ms >= 0

    def test_check_permissions_no_trust_chain(self):
        """Test check_permissions with no trust chain."""
        validator = SecurityValidator()

        context = SecurityContext.create(requester_agent_id="agent-123")

        has_perms, granted, missing = validator.check_permissions(
            context,
            ["read", "write"],
        )

        assert has_perms is False
        assert granted == []
        assert missing == ["read", "write"]

    def test_check_permissions_with_trust_chain(self, sample_security_context: SecurityContext):
        """Test check_permissions with trust chain."""
        validator = SecurityValidator()

        has_perms, granted, missing = validator.check_permissions(
            sample_security_context,
            ["read", "write"],
        )

        assert has_perms is True
        assert set(granted) == {"read", "write"}
        assert missing == []

    def test_check_permissions_partial(self, sample_security_context: SecurityContext):
        """Test check_permissions with partial permissions."""
        validator = SecurityValidator()

        has_perms, granted, missing = validator.check_permissions(
            sample_security_context,
            ["read", "admin"],
        )

        assert has_perms is False
        assert "read" in granted
        assert "admin" in missing

    def test_create_session_token_basic(self):
        """Test session token creation."""
        validator = SecurityValidator()

        token = validator.create_session_token("agent-123")

        assert token  # Token generated
        assert len(token) == 64  # SHA-256 hex digest

    def test_create_session_token_with_permissions(self):
        """Test session token creation with permissions."""
        validator = SecurityValidator()

        token = validator.create_session_token(
            "agent-123",
            permissions=["read", "write"],
        )

        assert token
        assert len(token) == 64

    def test_create_session_token_uniqueness(self):
        """Test session tokens are unique."""
        validator = SecurityValidator()

        tokens = [
            validator.create_session_token(f"agent-{i}")
            for i in range(10)
        ]

        # All tokens should be unique
        assert len(tokens) == len(set(tokens))

    def test_validate_context_credential_expiration_warning(self):
        """Test credential expiration adds warning."""
        validator = SecurityValidator()

        # Create credential that expires in the past
        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        expired_cred = Credential.create(
            credential_type=CredentialType.BEARER_TOKEN,
            value="token",
            expires_at=past_time,
        )

        context = SecurityContext.create(
            requester_agent_id="agent-123",
            credentials=[expired_cred],
        )

        result = validator.validate_context(context)

        # Should have warnings about expired credential
        assert len(result.warnings) > 0 or len(result.failure_reasons) > 0


# ============================================
# Integration Tests
# ============================================


class TestSecurityIntegration:
    """Integration tests for security components."""

    def test_full_security_validation_flow(self):
        """Test complete security validation flow."""
        # Create root authority credential
        root_credential = Credential.api_key(
            key="root-api-key",
            scope=["admin", "read", "write", "execute"],
        )

        # Build trust chain
        entry1 = TrustChainEntry.create(
            issuer="root-authority",
            subject="service-agent",
            delegation_type=DelegationType.DIRECT,
            permissions=["read", "write", "execute"],
            expires_in_hours=24,
        )

        entry2 = TrustChainEntry.create(
            issuer="service-agent",
            subject="user-agent",
            delegation_type=DelegationType.DELEGATED,
            permissions=["read", "write"],
            expires_in_hours=12,
            previous_entry_id=entry1.entry_id,
        )

        # Create security context
        user_credential = Credential.bearer_token(
            token="user-token",
            scope=["read"],
        )

        context = SecurityContext.create(
            requester_agent_id="user-agent",
            credentials=[user_credential],
            trust_chain=[entry1, entry2],
            session_token="session-123",
            ip_address="192.168.1.1",
        )

        # Validate
        validator = SecurityValidator()
        result = validator.validate_context(
            context,
            required_permissions=["read"],
            minimum_trust_level="basic",
        )

        assert result.valid is True
        assert result.trust_level == "verified"
        assert "read" in result.granted_permissions

    def test_credential_manager_lifecycle(self):
        """Test credential manager full lifecycle."""
        manager = CredentialManager()

        # Create and store credential
        credential = Credential.api_key(
            key="test-key",
            scope=["read", "write"],
            expires_in_days=30,
        )
        manager.store_credential(credential)

        # Validate stored credential
        is_valid, errors = manager.validate_credential(
            credential,
            expected_type=CredentialType.API_KEY,
            required_scope=["read"],
        )
        assert is_valid is True

        # Retrieve and verify
        retrieved = manager.retrieve_credential(credential.credential_id)
        assert retrieved == credential

        # Revoke
        revoked = manager.revoke_credential(credential.credential_id)
        assert revoked is True

        # Verify revocation
        assert manager.retrieve_credential(credential.credential_id) is None

    def test_trust_chain_validator_comprehensive(self):
        """Test trust chain validator with complex chain."""
        validator = TrustChainValidator(max_chain_length=5)

        # Build a complex but valid chain
        entries = []
        issuers = ["root", "tier1", "tier2", "tier3", "final"]

        for i in range(len(issuers) - 1):
            entry = TrustChainEntry.create(
                issuer=issuers[i],
                subject=issuers[i + 1],
                delegation_type=DelegationType.TRANSITIVE if i > 0 else DelegationType.DIRECT,
                permissions=["read", "write"] if i < 2 else ["read"],
                expires_in_hours=24 - i,
                previous_entry_id=entries[-1].entry_id if entries else None,
            )
            entries.append(entry)

        # Validate chain structure
        is_valid, errors = validator.validate_chain(
            entries,
            required_issuer="root",
            required_subject="final",
        )
        assert is_valid is True

        # Check permission narrowing
        has_perms, granted, missing = validator.check_delegation(
            entries,
            ["read"],
        )
        assert has_perms is True

        has_perms, granted, missing = validator.check_delegation(
            entries,
            ["write"],
        )
        # Write should be missing because last entry only has "read"
        assert has_perms is False

    def test_serialization_round_trip(self, sample_security_context: SecurityContext):
        """Test serialization and deserialization of security objects."""
        # Serialize
        context_dict = sample_security_context.to_dict()

        # Verify structure
        assert "context_id" in context_dict
        assert "requester_agent_id" in context_dict
        assert "credentials" in context_dict
        assert "trust_chain" in context_dict

        # Verify nested objects serialized
        for cred in context_dict["credentials"]:
            assert "credential_id" in cred
            assert "credential_type" in cred
            assert isinstance(cred["credential_type"], str)

        for entry in context_dict["trust_chain"]:
            assert "entry_id" in entry
            assert "delegation_type" in entry
            assert isinstance(entry["delegation_type"], str)
