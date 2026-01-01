"""
Tests for the Privacy and Consent Management module.
Issue #49 - Phase 2: Adaptive Interface Personalization

Tests cover:
- Consent management (grant, withdraw, check)
- Data Subject Requests (all GDPR types)
- Data export (portability)
- Data deletion (erasure)
- Anonymization for analytics
- Audit logging
- Privacy settings validation
"""

import uuid
from datetime import datetime

import pytest

from src.lui_simulator.privacy import (
    ConsentDecision,
    ConsentResponse,
    ConsentStatus,
    ConsentType,
    DataSubjectRequest,
    DSRStatus,
    DSRType,
    ExportFormat,
    PrivacyManager,
    PrivacySettings,
)


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def privacy_manager() -> PrivacyManager:
    """Create a fresh privacy manager for each test."""
    return PrivacyManager()


@pytest.fixture
def user_id() -> str:
    """Generate a random user ID."""
    return str(uuid.uuid4())


@pytest.fixture
def user_with_data(privacy_manager: PrivacyManager, user_id: str) -> str:
    """Create a user with sample data."""
    privacy_manager.set_user_data(user_id, {
        "profile": {
            "expertise_level": "INTERMEDIATE",
            "preferences": {"theme": "dark"},
        },
        "metrics": {
            "session_count": 10,
            "success_rate": 0.85,
            "avg_session_duration_ms": 5000.0,
            "interactions": [{"id": 1}, {"id": 2}],
        },
        "history": [
            {"action": "search", "timestamp": "2025-01-01T00:00:00Z"},
            {"action": "create", "timestamp": "2025-01-01T01:00:00Z"},
        ],
    })
    return user_id


@pytest.fixture
def user_with_consent(
    privacy_manager: PrivacyManager,
    user_id: str,
) -> str:
    """Create a user with all consents granted."""
    request = privacy_manager.request_consent(
        user_id,
        list(ConsentType),
    )
    response = ConsentResponse(
        request_id=request.request_id,
        user_id=user_id,
        responses=[
            ConsentDecision(consent_type=ct, granted=True)
            for ct in ConsentType
        ],
        responded_at=datetime.now().isoformat() + "Z",
    )
    privacy_manager.process_consent_response(response)
    return user_id


# ============================================
# PrivacySettings Tests
# ============================================


class TestPrivacySettings:
    """Tests for PrivacySettings configuration."""

    def test_default_settings(self) -> None:
        """Test default privacy settings."""
        settings = PrivacySettings()

        assert settings.profiling_enabled is True
        assert settings.data_retention_days == 365
        assert settings.on_device_only is False
        assert settings.share_anonymous_stats is True
        assert settings.privacy_mode == "FULL"

    def test_custom_settings(self) -> None:
        """Test custom privacy settings."""
        settings = PrivacySettings(
            profiling_enabled=False,
            data_retention_days=30,
            on_device_only=True,
            share_anonymous_stats=False,
            privacy_mode="SESSION_ONLY",
        )

        assert settings.profiling_enabled is False
        assert settings.data_retention_days == 30
        assert settings.on_device_only is True
        assert settings.share_anonymous_stats is False
        assert settings.privacy_mode == "SESSION_ONLY"

    def test_invalid_retention_days(self) -> None:
        """Test that negative retention days raises error."""
        with pytest.raises(ValueError, match="data_retention_days"):
            PrivacySettings(data_retention_days=-1)

    def test_invalid_privacy_mode(self) -> None:
        """Test that invalid privacy mode raises error."""
        with pytest.raises(ValueError, match="Invalid privacy_mode"):
            PrivacySettings(privacy_mode="INVALID")


# ============================================
# Consent Management Tests
# ============================================


class TestConsentManagement:
    """Tests for consent management functionality."""

    def test_check_consent_no_records(
        self,
        privacy_manager: PrivacyManager,
        user_id: str,
    ) -> None:
        """Test checking consent when no records exist."""
        result = privacy_manager.check_consent(user_id, ConsentType.PROFILING)
        assert result is False

    def test_request_consent(
        self,
        privacy_manager: PrivacyManager,
        user_id: str,
    ) -> None:
        """Test requesting consent."""
        consent_types = [ConsentType.PROFILING, ConsentType.PERSONALIZATION]
        request = privacy_manager.request_consent(user_id, consent_types)

        assert request.user_id == user_id
        assert request.consent_types == consent_types
        assert request.policy_version == PrivacyManager.DEFAULT_POLICY_VERSION
        assert request.purpose_explanation is not None
        assert len(request.purpose_explanation) > 0

    def test_grant_consent(
        self,
        privacy_manager: PrivacyManager,
        user_id: str,
    ) -> None:
        """Test granting consent."""
        request = privacy_manager.request_consent(
            user_id, [ConsentType.PROFILING]
        )
        response = ConsentResponse(
            request_id=request.request_id,
            user_id=user_id,
            responses=[ConsentDecision(ConsentType.PROFILING, granted=True)],
            responded_at=datetime.now().isoformat() + "Z",
        )

        records = privacy_manager.process_consent_response(response)

        assert len(records) == 1
        assert records[0].status == ConsentStatus.GRANTED
        assert privacy_manager.check_consent(user_id, ConsentType.PROFILING) is True

    def test_deny_consent(
        self,
        privacy_manager: PrivacyManager,
        user_id: str,
    ) -> None:
        """Test denying consent."""
        request = privacy_manager.request_consent(
            user_id, [ConsentType.PROFILING]
        )
        response = ConsentResponse(
            request_id=request.request_id,
            user_id=user_id,
            responses=[ConsentDecision(ConsentType.PROFILING, granted=False)],
            responded_at=datetime.now().isoformat() + "Z",
        )

        records = privacy_manager.process_consent_response(response)

        assert len(records) == 1
        assert records[0].status == ConsentStatus.DENIED
        assert privacy_manager.check_consent(user_id, ConsentType.PROFILING) is False

    def test_withdraw_consent(
        self,
        privacy_manager: PrivacyManager,
        user_with_consent: str,
    ) -> None:
        """Test withdrawing previously granted consent."""
        assert privacy_manager.check_consent(user_with_consent, ConsentType.PROFILING) is True

        records = privacy_manager.withdraw_consent(
            user_with_consent, [ConsentType.PROFILING]
        )

        assert len(records) == 1
        assert records[0].status == ConsentStatus.WITHDRAWN
        assert privacy_manager.check_consent(user_with_consent, ConsentType.PROFILING) is False

    def test_check_all_consents(
        self,
        privacy_manager: PrivacyManager,
        user_with_consent: str,
    ) -> None:
        """Test checking all consent types."""
        all_consents = privacy_manager.check_all_consents(user_with_consent)

        assert all(all_consents.values())

    def test_get_user_consents(
        self,
        privacy_manager: PrivacyManager,
        user_with_consent: str,
    ) -> None:
        """Test getting all consent records for a user."""
        records = privacy_manager.get_user_consents(user_with_consent)

        assert len(records) == len(ConsentType)
        assert all(r.status == ConsentStatus.GRANTED for r in records)

    def test_invalid_consent_request(
        self,
        privacy_manager: PrivacyManager,
        user_id: str,
    ) -> None:
        """Test processing response to unknown request."""
        response = ConsentResponse(
            request_id="invalid-request-id",
            user_id=user_id,
            responses=[ConsentDecision(ConsentType.PROFILING, granted=True)],
            responded_at=datetime.now().isoformat() + "Z",
        )

        with pytest.raises(ValueError, match="Unknown consent request"):
            privacy_manager.process_consent_response(response)


# ============================================
# Data Subject Request Tests
# ============================================


class TestDataSubjectRequests:
    """Tests for GDPR data subject requests."""

    def test_handle_access_request(
        self,
        privacy_manager: PrivacyManager,
        user_with_data: str,
    ) -> None:
        """Test GDPR Art. 15 access request."""
        request = DataSubjectRequest(
            request_id=str(uuid.uuid4()),
            request_type=DSRType.ACCESS,
            user_id=user_with_data,
            requested_at=datetime.now().isoformat() + "Z",
            status=DSRStatus.RECEIVED,
            status_updated_at=datetime.now().isoformat() + "Z",
        )

        response = privacy_manager.handle_dsr(request)

        assert response.status == DSRStatus.COMPLETED
        assert response.data_included is True
        assert response.data_format == "json"
        assert response.download_url is not None

    def test_handle_erasure_request(
        self,
        privacy_manager: PrivacyManager,
        user_with_data: str,
    ) -> None:
        """Test GDPR Art. 17 erasure request."""
        # Verify user has data
        assert privacy_manager.get_user_data(user_with_data) is not None

        request = DataSubjectRequest(
            request_id=str(uuid.uuid4()),
            request_type=DSRType.ERASURE,
            user_id=user_with_data,
            requested_at=datetime.now().isoformat() + "Z",
            status=DSRStatus.RECEIVED,
            status_updated_at=datetime.now().isoformat() + "Z",
        )

        response = privacy_manager.handle_dsr(request)

        assert response.status == DSRStatus.COMPLETED
        assert "deleted" in response.message.lower()
        assert "confirmation" in response.message.lower()
        # Data should be deleted
        assert privacy_manager.get_user_data(user_with_data) is None

    def test_handle_portability_request(
        self,
        privacy_manager: PrivacyManager,
        user_with_data: str,
    ) -> None:
        """Test GDPR Art. 20 portability request."""
        request = DataSubjectRequest(
            request_id=str(uuid.uuid4()),
            request_type=DSRType.PORTABILITY,
            user_id=user_with_data,
            requested_at=datetime.now().isoformat() + "Z",
            status=DSRStatus.RECEIVED,
            status_updated_at=datetime.now().isoformat() + "Z",
        )

        response = privacy_manager.handle_dsr(request)

        assert response.status == DSRStatus.COMPLETED
        assert response.data_included is True
        assert response.data_format == "json"
        assert "portable" in response.message.lower()

    def test_handle_rectification_request(
        self,
        privacy_manager: PrivacyManager,
        user_with_data: str,
    ) -> None:
        """Test GDPR Art. 16 rectification request."""
        request = DataSubjectRequest(
            request_id=str(uuid.uuid4()),
            request_type=DSRType.RECTIFICATION,
            user_id=user_with_data,
            requested_at=datetime.now().isoformat() + "Z",
            status=DSRStatus.RECEIVED,
            status_updated_at=datetime.now().isoformat() + "Z",
        )

        response = privacy_manager.handle_dsr(request)

        assert response.status == DSRStatus.PROCESSING
        assert "rectification" in response.message.lower()

    def test_handle_objection_request(
        self,
        privacy_manager: PrivacyManager,
        user_with_consent: str,
    ) -> None:
        """Test GDPR Art. 21 objection request."""
        # Verify consent is granted
        assert privacy_manager.check_consent(user_with_consent, ConsentType.PROFILING) is True

        request = DataSubjectRequest(
            request_id=str(uuid.uuid4()),
            request_type=DSRType.OBJECTION,
            user_id=user_with_consent,
            requested_at=datetime.now().isoformat() + "Z",
            status=DSRStatus.RECEIVED,
            status_updated_at=datetime.now().isoformat() + "Z",
        )

        response = privacy_manager.handle_dsr(request)

        assert response.status == DSRStatus.COMPLETED
        assert "stopped" in response.message.lower()
        # Consents should be withdrawn
        assert privacy_manager.check_consent(user_with_consent, ConsentType.PROFILING) is False

    def test_handle_restriction_request(
        self,
        privacy_manager: PrivacyManager,
        user_with_data: str,
    ) -> None:
        """Test GDPR Art. 18 restriction request."""
        request = DataSubjectRequest(
            request_id=str(uuid.uuid4()),
            request_type=DSRType.RESTRICTION,
            user_id=user_with_data,
            requested_at=datetime.now().isoformat() + "Z",
            status=DSRStatus.RECEIVED,
            status_updated_at=datetime.now().isoformat() + "Z",
        )

        response = privacy_manager.handle_dsr(request)

        assert response.status == DSRStatus.COMPLETED
        assert "restricted" in response.message.lower()


# ============================================
# Data Export Tests
# ============================================


class TestDataExport:
    """Tests for data export functionality."""

    def test_export_json(
        self,
        privacy_manager: PrivacyManager,
        user_with_data: str,
    ) -> None:
        """Test exporting data as JSON."""
        result = privacy_manager.export_user_data(
            user_with_data,
            format=ExportFormat.JSON,
        )

        assert result.success is True
        assert result.format == ExportFormat.JSON
        assert result.size_bytes > 0
        assert result.checksum is not None
        assert result.download_url is not None

    def test_export_csv(
        self,
        privacy_manager: PrivacyManager,
        user_with_data: str,
    ) -> None:
        """Test exporting data as CSV."""
        result = privacy_manager.export_user_data(
            user_with_data,
            format=ExportFormat.CSV,
        )

        assert result.success is True
        assert result.format == ExportFormat.CSV
        assert result.size_bytes > 0

    def test_export_specific_categories(
        self,
        privacy_manager: PrivacyManager,
        user_with_data: str,
    ) -> None:
        """Test exporting specific data categories."""
        result = privacy_manager.export_user_data(
            user_with_data,
            format=ExportFormat.JSON,
            include_categories=["profile"],
        )

        assert result.success is True

    def test_export_empty_user(
        self,
        privacy_manager: PrivacyManager,
        user_id: str,
    ) -> None:
        """Test exporting data for user with no data."""
        result = privacy_manager.export_user_data(
            user_id,
            format=ExportFormat.JSON,
        )

        # Should still succeed with empty data
        assert result.success is True


# ============================================
# Data Deletion Tests
# ============================================


class TestDataDeletion:
    """Tests for data deletion functionality."""

    def test_delete_user_data(
        self,
        privacy_manager: PrivacyManager,
        user_with_data: str,
    ) -> None:
        """Test deleting all user data."""
        # Verify data exists
        assert privacy_manager.get_user_data(user_with_data) is not None

        result = privacy_manager.delete_user_data(user_with_data)

        assert result.success is True
        assert result.user_id == user_with_data
        assert result.confirmation_token is not None
        assert len(result.items_deleted) > 0
        # Data should be gone
        assert privacy_manager.get_user_data(user_with_data) is None

    def test_delete_includes_category_counts(
        self,
        privacy_manager: PrivacyManager,
        user_with_data: str,
    ) -> None:
        """Test that deletion includes category counts."""
        result = privacy_manager.delete_user_data(user_with_data)

        categories = {item.category for item in result.items_deleted}
        assert "profile" in categories
        assert "metrics" in categories

    def test_delete_with_consent_records(
        self,
        privacy_manager: PrivacyManager,
        user_with_consent: str,
    ) -> None:
        """Test deleting user with consent records."""
        # Add some data
        privacy_manager.set_user_data(user_with_consent, {"profile": {"test": True}})

        result = privacy_manager.delete_user_data(user_with_consent)

        assert result.success is True
        # Consent records should be deleted
        assert len(privacy_manager.get_user_consents(user_with_consent)) == 0

    def test_delete_empty_user(
        self,
        privacy_manager: PrivacyManager,
        user_id: str,
    ) -> None:
        """Test deleting user with no data."""
        result = privacy_manager.delete_user_data(user_id)

        assert result.success is True
        assert len(result.items_deleted) == 0


# ============================================
# Anonymization Tests
# ============================================


class TestAnonymization:
    """Tests for anonymization functionality."""

    def test_anonymize_with_consent(
        self,
        privacy_manager: PrivacyManager,
        user_with_consent: str,
    ) -> None:
        """Test anonymizing data when consent is granted."""
        privacy_manager.set_user_data(user_with_consent, {
            "profile": {"expertise_level": "ADVANCED"},
            "metrics": {"session_count": 5, "success_rate": 0.9},
        })

        result = privacy_manager.anonymize_for_analytics(user_with_consent)

        assert result is not None
        assert result.expertise_level == "ADVANCED"
        assert result.session_count == 5

    def test_anonymize_without_consent(
        self,
        privacy_manager: PrivacyManager,
        user_with_data: str,
    ) -> None:
        """Test anonymizing data when consent is not granted."""
        # No consent granted
        result = privacy_manager.anonymize_for_analytics(user_with_data)

        assert result is None

    def test_anonymize_no_data(
        self,
        privacy_manager: PrivacyManager,
        user_with_consent: str,
    ) -> None:
        """Test anonymizing when user has no data."""
        result = privacy_manager.anonymize_for_analytics(user_with_consent)

        assert result is None


# ============================================
# Audit Log Tests
# ============================================


class TestAuditLog:
    """Tests for audit logging functionality."""

    def test_consent_grant_logged(
        self,
        privacy_manager: PrivacyManager,
        user_id: str,
    ) -> None:
        """Test that consent grants are logged."""
        request = privacy_manager.request_consent(
            user_id, [ConsentType.PROFILING]
        )
        response = ConsentResponse(
            request_id=request.request_id,
            user_id=user_id,
            responses=[ConsentDecision(ConsentType.PROFILING, granted=True)],
            responded_at=datetime.now().isoformat() + "Z",
        )
        privacy_manager.process_consent_response(response)

        audit_log = privacy_manager.get_audit_log(user_id=user_id)

        assert len(audit_log) >= 1
        assert audit_log[0].action == "granted"
        assert audit_log[0].consent_type == ConsentType.PROFILING
        assert audit_log[0].new_status == ConsentStatus.GRANTED

    def test_consent_withdrawal_logged(
        self,
        privacy_manager: PrivacyManager,
        user_with_consent: str,
    ) -> None:
        """Test that consent withdrawals are logged."""
        privacy_manager.withdraw_consent(
            user_with_consent, [ConsentType.PROFILING]
        )

        audit_log = privacy_manager.get_audit_log(user_id=user_with_consent)

        withdrawal_entry = next(
            (e for e in audit_log if e.action == "withdrawn"),
            None,
        )
        assert withdrawal_entry is not None
        assert withdrawal_entry.new_status == ConsentStatus.WITHDRAWN

    def test_audit_log_with_ip_hashing(
        self,
        privacy_manager: PrivacyManager,
        user_id: str,
    ) -> None:
        """Test that IP addresses are hashed in audit log."""
        request = privacy_manager.request_consent(
            user_id, [ConsentType.PROFILING]
        )
        response = ConsentResponse(
            request_id=request.request_id,
            user_id=user_id,
            responses=[ConsentDecision(ConsentType.PROFILING, granted=True)],
            responded_at=datetime.now().isoformat() + "Z",
        )
        privacy_manager.process_consent_response(
            response,
            ip_address="192.168.1.1",
        )

        audit_log = privacy_manager.get_audit_log(user_id=user_id)

        assert audit_log[0].ip_address is not None
        # IP should be hashed, not raw
        assert audit_log[0].ip_address != "192.168.1.1"

    def test_audit_log_limit(
        self,
        privacy_manager: PrivacyManager,
        user_with_consent: str,
    ) -> None:
        """Test audit log limit."""
        audit_log = privacy_manager.get_audit_log(limit=2)

        assert len(audit_log) <= 2


# ============================================
# Integration Tests
# ============================================


class TestIntegration:
    """Integration tests for privacy manager."""

    def test_full_consent_lifecycle(
        self,
        privacy_manager: PrivacyManager,
        user_id: str,
    ) -> None:
        """Test complete consent lifecycle: request -> grant -> withdraw."""
        # Request consent
        request = privacy_manager.request_consent(
            user_id,
            [ConsentType.PROFILING, ConsentType.ANALYTICS],
        )
        assert request is not None

        # Grant consent
        response = ConsentResponse(
            request_id=request.request_id,
            user_id=user_id,
            responses=[
                ConsentDecision(ConsentType.PROFILING, granted=True),
                ConsentDecision(ConsentType.ANALYTICS, granted=True),
            ],
            responded_at=datetime.now().isoformat() + "Z",
        )
        privacy_manager.process_consent_response(response)

        # Verify granted
        assert privacy_manager.check_consent(user_id, ConsentType.PROFILING) is True
        assert privacy_manager.check_consent(user_id, ConsentType.ANALYTICS) is True

        # Withdraw one consent
        privacy_manager.withdraw_consent(user_id, [ConsentType.ANALYTICS])

        # Verify partial withdrawal
        assert privacy_manager.check_consent(user_id, ConsentType.PROFILING) is True
        assert privacy_manager.check_consent(user_id, ConsentType.ANALYTICS) is False

    def test_full_dsr_workflow(
        self,
        privacy_manager: PrivacyManager,
        user_with_data: str,
    ) -> None:
        """Test complete DSR workflow: access -> portability -> erasure."""
        # Access request
        access_request = DataSubjectRequest(
            request_id=str(uuid.uuid4()),
            request_type=DSRType.ACCESS,
            user_id=user_with_data,
            requested_at=datetime.now().isoformat() + "Z",
            status=DSRStatus.RECEIVED,
            status_updated_at=datetime.now().isoformat() + "Z",
        )
        access_response = privacy_manager.handle_dsr(access_request)
        assert access_response.status == DSRStatus.COMPLETED
        assert access_response.data_included is True

        # Portability request
        port_request = DataSubjectRequest(
            request_id=str(uuid.uuid4()),
            request_type=DSRType.PORTABILITY,
            user_id=user_with_data,
            requested_at=datetime.now().isoformat() + "Z",
            status=DSRStatus.RECEIVED,
            status_updated_at=datetime.now().isoformat() + "Z",
        )
        port_response = privacy_manager.handle_dsr(port_request)
        assert port_response.status == DSRStatus.COMPLETED

        # Erasure request
        erase_request = DataSubjectRequest(
            request_id=str(uuid.uuid4()),
            request_type=DSRType.ERASURE,
            user_id=user_with_data,
            requested_at=datetime.now().isoformat() + "Z",
            status=DSRStatus.RECEIVED,
            status_updated_at=datetime.now().isoformat() + "Z",
        )
        erase_response = privacy_manager.handle_dsr(erase_request)
        assert erase_response.status == DSRStatus.COMPLETED

        # Data should be gone
        assert privacy_manager.get_user_data(user_with_data) is None

    def test_privacy_preserved_after_reset(
        self,
        privacy_manager: PrivacyManager,
        user_with_consent: str,
    ) -> None:
        """Test that reset clears all data."""
        privacy_manager.set_user_data(user_with_consent, {"test": True})

        privacy_manager.reset()

        assert privacy_manager.get_user_data(user_with_consent) is None
        assert len(privacy_manager.get_user_consents(user_with_consent)) == 0
        assert len(privacy_manager.get_audit_log()) == 0
