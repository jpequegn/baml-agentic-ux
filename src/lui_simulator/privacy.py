"""
Privacy and Consent Management for LUI Simulator.
GDPR/CCPA compliant profile handling with proper consent management.

Issue #49 - Phase 2: Adaptive Interface Personalization

Key Features:
- Consent management (grant, withdraw, check)
- Data Subject Request (DSR) handling
- Data export (portability)
- Data deletion (erasure)
- Anonymization for analytics
- Audit logging
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class ConsentType(Enum):
    """Types of consent that can be granted or withdrawn."""
    PROFILING = "PROFILING"
    PERSONALIZATION = "PERSONALIZATION"
    ANALYTICS = "ANALYTICS"
    DATA_EXPORT = "DATA_EXPORT"
    RETENTION = "RETENTION"


class ConsentStatus(Enum):
    """Status of a consent."""
    PENDING = "PENDING"
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    WITHDRAWN = "WITHDRAWN"
    EXPIRED = "EXPIRED"


class DSRType(Enum):
    """Types of Data Subject Requests per GDPR."""
    ACCESS = "ACCESS"
    RECTIFICATION = "RECTIFICATION"
    ERASURE = "ERASURE"
    PORTABILITY = "PORTABILITY"
    OBJECTION = "OBJECTION"
    RESTRICTION = "RESTRICTION"


class DSRStatus(Enum):
    """Status of a Data Subject Request."""
    RECEIVED = "RECEIVED"
    VALIDATING = "VALIDATING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class ExportFormat(Enum):
    """Format options for data export."""
    JSON = "JSON"
    CSV = "CSV"


@dataclass
class PrivacySettings:
    """User's privacy settings configuration."""
    profiling_enabled: bool = True
    data_retention_days: int = 365
    on_device_only: bool = False
    share_anonymous_stats: bool = True
    privacy_mode: str = "FULL"

    def __post_init__(self) -> None:
        if self.data_retention_days < 0:
            raise ValueError("data_retention_days must be >= 0")
        if self.privacy_mode not in ("FULL", "AGGREGATE_ONLY", "SESSION_ONLY", "DISABLED"):
            raise ValueError(f"Invalid privacy_mode: {self.privacy_mode}")


@dataclass
class ConsentRecord:
    """Record of a specific consent grant or withdrawal."""
    record_id: str
    user_id: str
    consent_type: ConsentType
    status: ConsentStatus
    policy_version: str
    source: str = "api"
    granted_at: Optional[str] = None
    withdrawn_at: Optional[str] = None


@dataclass
class ConsentRequest:
    """Request to obtain consent from a user."""
    request_id: str
    user_id: str
    consent_types: list[ConsentType]
    policy_version: str
    requested_at: str
    purpose_explanation: str
    expires_at: Optional[str] = None


@dataclass
class ConsentDecision:
    """Individual consent decision."""
    consent_type: ConsentType
    granted: bool


@dataclass
class ConsentResponse:
    """Response to a consent request."""
    request_id: str
    user_id: str
    responses: list[ConsentDecision]
    responded_at: str


@dataclass
class DataSubjectRequest:
    """A data subject request from a user."""
    request_id: str
    request_type: DSRType
    user_id: str
    requested_at: str
    status: DSRStatus
    status_updated_at: str
    notes: Optional[str] = None
    completed_at: Optional[str] = None
    rejection_reason: Optional[str] = None


@dataclass
class DSRResponse:
    """Response to a data subject request."""
    request_id: str
    status: DSRStatus
    completed_at: str
    data_included: bool
    message: str
    data_format: Optional[str] = None
    download_url: Optional[str] = None
    expires_at: Optional[str] = None


@dataclass
class DeletionItem:
    """A category of deleted data."""
    category: str
    count: int


@dataclass
class RetainedItem:
    """Data retained for legal or compliance reasons."""
    category: str
    reason: str
    retention_until: str


@dataclass
class DeletionResult:
    """Result of a data deletion request."""
    user_id: str
    success: bool
    deleted_at: str
    items_deleted: list[DeletionItem]
    confirmation_token: str
    retained_items: Optional[list[RetainedItem]] = None


@dataclass
class ExportRequest:
    """Request to export user data."""
    request_id: str
    user_id: str
    format: ExportFormat
    include_categories: list[str]
    requested_at: str


@dataclass
class ExportResult:
    """Result of a data export."""
    request_id: str
    user_id: str
    success: bool
    format: ExportFormat
    size_bytes: int
    created_at: str
    checksum: str
    download_url: Optional[str] = None
    expires_at: Optional[str] = None


@dataclass
class AnonymizedMetrics:
    """Anonymized metrics for analytics (no PII)."""
    metrics_id: str
    generated_at: str
    expertise_level: str
    session_count: int
    avg_success_rate: float
    avg_session_duration_ms: float
    feature_usage_rates: list[dict[str, float]] = field(default_factory=list)


@dataclass
class ConsentAuditEntry:
    """Audit log entry for consent changes."""
    entry_id: str
    user_id: str
    action: str
    consent_type: ConsentType
    new_status: ConsentStatus
    timestamp: str
    policy_version: str
    old_status: Optional[ConsentStatus] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


# Default privacy explanations
CONSENT_EXPLANATIONS = {
    ConsentType.PROFILING: (
        "We track your interaction patterns to learn how you use the system. "
        "This helps us provide better suggestions and adapt to your workflow."
    ),
    ConsentType.PERSONALIZATION: (
        "We use your behavior patterns to adapt responses to your expertise level. "
        "This means less hand-holding as you become more experienced."
    ),
    ConsentType.ANALYTICS: (
        "We include your anonymized usage data in aggregate statistics. "
        "This helps us understand how users interact with the system overall."
    ),
    ConsentType.DATA_EXPORT: (
        "You can export all your profile data at any time in a machine-readable format. "
        "This is your data, and you have the right to take it with you."
    ),
    ConsentType.RETENTION: (
        "We retain your profile data between sessions to provide continuity. "
        "You can opt for session-only mode where data is deleted when you leave."
    ),
}


class PrivacyManager:
    """
    Manages privacy and consent for user profiles.

    Handles:
    - Consent management (grant, withdraw, check)
    - Data Subject Requests (GDPR Art. 15-22)
    - Data export (portability)
    - Data deletion (erasure)
    - Anonymization for analytics
    - Audit logging
    """

    DEFAULT_POLICY_VERSION = "1.0.0"
    CONSENT_EXPIRY_DAYS = 365

    def __init__(
        self,
        policy_version: str = DEFAULT_POLICY_VERSION,
        consent_expiry_days: int = CONSENT_EXPIRY_DAYS,
    ) -> None:
        """
        Initialize the privacy manager.

        Args:
            policy_version: Current privacy policy version.
            consent_expiry_days: Days until consent expires.
        """
        self.policy_version = policy_version
        self.consent_expiry_days = consent_expiry_days
        self._consent_records: dict[str, dict[ConsentType, ConsentRecord]] = {}
        self._pending_requests: dict[str, ConsentRequest] = {}
        self._dsr_requests: dict[str, DataSubjectRequest] = {}
        self._audit_log: list[ConsentAuditEntry] = []
        self._user_data: dict[str, dict] = {}  # Simulated user data store

    # ============================================
    # Consent Management
    # ============================================

    def check_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        """
        Check if a user has granted a specific consent.

        Args:
            user_id: User identifier.
            consent_type: Type of consent to check.

        Returns:
            True if consent is granted and not expired.
        """
        user_consents = self._consent_records.get(user_id, {})
        record = user_consents.get(consent_type)

        if not record:
            return False

        if record.status != ConsentStatus.GRANTED:
            return False

        # Check if consent has expired
        if record.granted_at:
            granted_time = datetime.fromisoformat(record.granted_at.rstrip("Z"))
            expiry_time = granted_time + timedelta(days=self.consent_expiry_days)
            if datetime.now() > expiry_time:
                # Mark as expired
                self._update_consent_status(
                    user_id, consent_type, ConsentStatus.EXPIRED
                )
                return False

        return True

    def check_all_consents(self, user_id: str) -> dict[ConsentType, bool]:
        """
        Check all consent types for a user.

        Args:
            user_id: User identifier.

        Returns:
            Dictionary mapping consent types to their granted status.
        """
        return {
            consent_type: self.check_consent(user_id, consent_type)
            for consent_type in ConsentType
        }

    def request_consent(
        self,
        user_id: str,
        consent_types: list[ConsentType],
        purpose_explanation: Optional[str] = None,
    ) -> ConsentRequest:
        """
        Create a consent request for a user.

        Args:
            user_id: User identifier.
            consent_types: Types of consent being requested.
            purpose_explanation: Optional custom explanation.

        Returns:
            ConsentRequest object.
        """
        now = datetime.now()
        request_id = str(uuid.uuid4())

        # Build explanation from defaults if not provided
        if not purpose_explanation:
            explanations = [
                CONSENT_EXPLANATIONS.get(ct, f"Permission for {ct.value}")
                for ct in consent_types
            ]
            purpose_explanation = " ".join(explanations)

        request = ConsentRequest(
            request_id=request_id,
            user_id=user_id,
            consent_types=consent_types,
            policy_version=self.policy_version,
            requested_at=now.isoformat() + "Z",
            expires_at=(now + timedelta(days=7)).isoformat() + "Z",
            purpose_explanation=purpose_explanation,
        )

        self._pending_requests[request_id] = request
        return request

    def process_consent_response(
        self,
        response: ConsentResponse,
        source: str = "ui",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> list[ConsentRecord]:
        """
        Process a consent response from a user.

        Args:
            response: The consent response.
            source: Source of consent (ui, api, import).
            ip_address: Optional IP address for audit.
            user_agent: Optional user agent for audit.

        Returns:
            List of created/updated consent records.
        """
        request = self._pending_requests.get(response.request_id)
        if not request:
            raise ValueError(f"Unknown consent request: {response.request_id}")

        now = datetime.now()
        records = []

        # Initialize user's consent records if needed
        if response.user_id not in self._consent_records:
            self._consent_records[response.user_id] = {}

        for decision in response.responses:
            old_record = self._consent_records[response.user_id].get(decision.consent_type)
            old_status = old_record.status if old_record else None

            new_status = ConsentStatus.GRANTED if decision.granted else ConsentStatus.DENIED
            record = ConsentRecord(
                record_id=str(uuid.uuid4()),
                user_id=response.user_id,
                consent_type=decision.consent_type,
                status=new_status,
                policy_version=self.policy_version,
                source=source,
                granted_at=now.isoformat() + "Z" if decision.granted else None,
                withdrawn_at=None,
            )

            self._consent_records[response.user_id][decision.consent_type] = record
            records.append(record)

            # Audit log
            self._add_audit_entry(
                user_id=response.user_id,
                action="granted" if decision.granted else "denied",
                consent_type=decision.consent_type,
                old_status=old_status,
                new_status=new_status,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        # Remove processed request
        del self._pending_requests[response.request_id]

        return records

    def withdraw_consent(
        self,
        user_id: str,
        consent_types: list[ConsentType],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> list[ConsentRecord]:
        """
        Withdraw consent for specified types.

        Args:
            user_id: User identifier.
            consent_types: Types of consent to withdraw.
            ip_address: Optional IP address for audit.
            user_agent: Optional user agent for audit.

        Returns:
            List of updated consent records.
        """
        now = datetime.now()
        records = []

        user_consents = self._consent_records.get(user_id, {})

        for consent_type in consent_types:
            old_record = user_consents.get(consent_type)
            old_status = old_record.status if old_record else None

            record = ConsentRecord(
                record_id=str(uuid.uuid4()),
                user_id=user_id,
                consent_type=consent_type,
                status=ConsentStatus.WITHDRAWN,
                policy_version=self.policy_version,
                source="withdrawal",
                granted_at=old_record.granted_at if old_record else None,
                withdrawn_at=now.isoformat() + "Z",
            )

            if user_id not in self._consent_records:
                self._consent_records[user_id] = {}
            self._consent_records[user_id][consent_type] = record
            records.append(record)

            # Audit log
            self._add_audit_entry(
                user_id=user_id,
                action="withdrawn",
                consent_type=consent_type,
                old_status=old_status,
                new_status=ConsentStatus.WITHDRAWN,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        return records

    def get_user_consents(self, user_id: str) -> list[ConsentRecord]:
        """
        Get all consent records for a user.

        Args:
            user_id: User identifier.

        Returns:
            List of consent records.
        """
        return list(self._consent_records.get(user_id, {}).values())

    # ============================================
    # Data Subject Requests (GDPR)
    # ============================================

    def handle_dsr(self, request: DataSubjectRequest) -> DSRResponse:
        """
        Handle a data subject request.

        Args:
            request: The data subject request.

        Returns:
            DSRResponse with result.
        """
        # Store the request
        self._dsr_requests[request.request_id] = request
        now = datetime.now()

        handlers = {
            DSRType.ACCESS: self._handle_access_request,
            DSRType.ERASURE: self._handle_erasure_request,
            DSRType.PORTABILITY: self._handle_portability_request,
            DSRType.RECTIFICATION: self._handle_rectification_request,
            DSRType.OBJECTION: self._handle_objection_request,
            DSRType.RESTRICTION: self._handle_restriction_request,
        }

        handler = handlers.get(request.request_type)
        if not handler:
            return DSRResponse(
                request_id=request.request_id,
                status=DSRStatus.REJECTED,
                completed_at=now.isoformat() + "Z",
                data_included=False,
                message=f"Unknown request type: {request.request_type.value}",
            )

        return handler(request)

    def _handle_access_request(self, request: DataSubjectRequest) -> DSRResponse:
        """Handle GDPR Art. 15 access request."""
        now = datetime.now()

        # Export user data
        export_result = self.export_user_data(
            request.user_id,
            format=ExportFormat.JSON,
        )

        return DSRResponse(
            request_id=request.request_id,
            status=DSRStatus.COMPLETED,
            completed_at=now.isoformat() + "Z",
            data_included=True,
            data_format="json",
            download_url=export_result.download_url,
            expires_at=export_result.expires_at,
            message="Your data has been prepared for download.",
        )

    def _handle_erasure_request(self, request: DataSubjectRequest) -> DSRResponse:
        """Handle GDPR Art. 17 erasure request."""
        now = datetime.now()

        # Delete user data
        deletion_result = self.delete_user_data(request.user_id)

        if deletion_result.success:
            return DSRResponse(
                request_id=request.request_id,
                status=DSRStatus.COMPLETED,
                completed_at=now.isoformat() + "Z",
                data_included=False,
                message=(
                    f"Your data has been deleted. "
                    f"Confirmation token: {deletion_result.confirmation_token}"
                ),
            )
        else:
            return DSRResponse(
                request_id=request.request_id,
                status=DSRStatus.FAILED,
                completed_at=now.isoformat() + "Z",
                data_included=False,
                message="Failed to delete data. Please contact support.",
            )

    def _handle_portability_request(self, request: DataSubjectRequest) -> DSRResponse:
        """Handle GDPR Art. 20 portability request."""
        now = datetime.now()

        # Export in machine-readable format
        export_result = self.export_user_data(
            request.user_id,
            format=ExportFormat.JSON,
        )

        return DSRResponse(
            request_id=request.request_id,
            status=DSRStatus.COMPLETED,
            completed_at=now.isoformat() + "Z",
            data_included=True,
            data_format="json",
            download_url=export_result.download_url,
            expires_at=export_result.expires_at,
            message="Your data is ready for download in a portable format.",
        )

    def _handle_rectification_request(self, request: DataSubjectRequest) -> DSRResponse:
        """Handle GDPR Art. 16 rectification request."""
        now = datetime.now()

        # In a real implementation, this would update specific fields
        # For now, we acknowledge the request
        return DSRResponse(
            request_id=request.request_id,
            status=DSRStatus.PROCESSING,
            completed_at=now.isoformat() + "Z",
            data_included=False,
            message=(
                "Your rectification request has been received. "
                "Please provide the corrections you would like to make."
            ),
        )

    def _handle_objection_request(self, request: DataSubjectRequest) -> DSRResponse:
        """Handle GDPR Art. 21 objection request."""
        now = datetime.now()

        # Withdraw all processing consents
        self.withdraw_consent(
            request.user_id,
            [ConsentType.PROFILING, ConsentType.PERSONALIZATION, ConsentType.ANALYTICS],
        )

        return DSRResponse(
            request_id=request.request_id,
            status=DSRStatus.COMPLETED,
            completed_at=now.isoformat() + "Z",
            data_included=False,
            message="Processing of your data has been stopped.",
        )

    def _handle_restriction_request(self, request: DataSubjectRequest) -> DSRResponse:
        """Handle GDPR Art. 18 restriction request."""
        now = datetime.now()

        # Update privacy settings to restrict processing
        if request.user_id in self._user_data:
            self._user_data[request.user_id]["privacy_settings"] = PrivacySettings(
                profiling_enabled=False,
                data_retention_days=0,
                on_device_only=True,
                share_anonymous_stats=False,
                privacy_mode="SESSION_ONLY",
            )

        return DSRResponse(
            request_id=request.request_id,
            status=DSRStatus.COMPLETED,
            completed_at=now.isoformat() + "Z",
            data_included=False,
            message="Processing of your data has been restricted.",
        )

    # ============================================
    # Data Export (Portability)
    # ============================================

    def export_user_data(
        self,
        user_id: str,
        format: ExportFormat = ExportFormat.JSON,
        include_categories: Optional[list[str]] = None,
    ) -> ExportResult:
        """
        Export all user data in a portable format.

        Args:
            user_id: User identifier.
            format: Export format (JSON or CSV).
            include_categories: Optional list of categories to include.

        Returns:
            ExportResult with download information.
        """
        now = datetime.now()
        request_id = str(uuid.uuid4())

        if include_categories is None:
            include_categories = ["profile", "consents", "metrics", "history"]

        # Gather all user data
        data: dict = {
            "export_metadata": {
                "user_id": user_id,
                "exported_at": now.isoformat() + "Z",
                "format": format.value,
                "categories": include_categories,
            }
        }

        if "profile" in include_categories:
            data["profile"] = self._user_data.get(user_id, {}).get("profile", {})

        if "consents" in include_categories:
            consents = self._consent_records.get(user_id, {})
            data["consents"] = {
                ct.value: {
                    "status": cr.status.value,
                    "granted_at": cr.granted_at,
                    "withdrawn_at": cr.withdrawn_at,
                    "policy_version": cr.policy_version,
                }
                for ct, cr in consents.items()
            }

        if "metrics" in include_categories:
            data["metrics"] = self._user_data.get(user_id, {}).get("metrics", {})

        if "history" in include_categories:
            data["interaction_history"] = self._user_data.get(user_id, {}).get("history", [])

        # Serialize
        if format == ExportFormat.JSON:
            serialized = json.dumps(data, indent=2).encode("utf-8")
        else:
            # CSV format - simplified
            serialized = self._to_csv(data).encode("utf-8")

        # Calculate checksum
        checksum = hashlib.sha256(serialized).hexdigest()

        # In a real implementation, this would upload to a secure storage
        download_url = f"https://example.com/exports/{request_id}.{format.value.lower()}"
        expires_at = (now + timedelta(days=7)).isoformat() + "Z"

        return ExportResult(
            request_id=request_id,
            user_id=user_id,
            success=True,
            format=format,
            size_bytes=len(serialized),
            created_at=now.isoformat() + "Z",
            checksum=checksum,
            download_url=download_url,
            expires_at=expires_at,
        )

    def _to_csv(self, data: dict) -> str:
        """Convert data to CSV format (simplified)."""
        lines = []
        for category, content in data.items():
            if isinstance(content, dict):
                for key, value in content.items():
                    lines.append(f"{category},{key},{json.dumps(value)}")
            else:
                lines.append(f"{category},,{json.dumps(content)}")
        return "\n".join(lines)

    # ============================================
    # Data Deletion (Erasure)
    # ============================================

    def delete_user_data(
        self,
        user_id: str,
        retain_for_legal: bool = True,
    ) -> DeletionResult:
        """
        Delete all user data.

        Args:
            user_id: User identifier.
            retain_for_legal: Whether to retain data required for legal reasons.

        Returns:
            DeletionResult with deletion details.
        """
        now = datetime.now()
        items_deleted = []
        retained_items = []

        # Delete consent records
        if user_id in self._consent_records:
            count = len(self._consent_records[user_id])
            del self._consent_records[user_id]
            items_deleted.append(DeletionItem(category="consents", count=count))

        # Delete user data
        if user_id in self._user_data:
            user_data = self._user_data[user_id]

            # Count items in each category
            if "profile" in user_data:
                items_deleted.append(DeletionItem(category="profile", count=1))

            if "metrics" in user_data:
                metrics_count = len(user_data.get("metrics", {}).get("interactions", []))
                items_deleted.append(DeletionItem(category="metrics", count=metrics_count))

            if "history" in user_data:
                history_count = len(user_data.get("history", []))
                items_deleted.append(DeletionItem(category="history", count=history_count))

            del self._user_data[user_id]

        # Some audit logs may need to be retained for legal compliance
        if retain_for_legal:
            audit_count = sum(1 for e in self._audit_log if e.user_id == user_id)
            if audit_count > 0:
                retained_items.append(RetainedItem(
                    category="audit_log",
                    reason="Legal requirement to maintain audit trail",
                    retention_until=(now + timedelta(days=365 * 7)).isoformat() + "Z",
                ))

        # Generate confirmation token
        confirmation_token = hashlib.sha256(
            f"{user_id}:{now.isoformat()}:{uuid.uuid4()}".encode()
        ).hexdigest()[:32]

        return DeletionResult(
            user_id=user_id,
            success=True,
            deleted_at=now.isoformat() + "Z",
            items_deleted=items_deleted,
            confirmation_token=confirmation_token,
            retained_items=retained_items if retained_items else None,
        )

    # ============================================
    # Anonymization
    # ============================================

    def anonymize_for_analytics(
        self,
        user_id: str,
    ) -> Optional[AnonymizedMetrics]:
        """
        Create anonymized metrics from a user profile.

        Args:
            user_id: User identifier.

        Returns:
            AnonymizedMetrics with no PII, or None if user has no data.
        """
        # Check consent for analytics
        if not self.check_consent(user_id, ConsentType.ANALYTICS):
            return None

        user_data = self._user_data.get(user_id, {})
        profile = user_data.get("profile", {})
        metrics = user_data.get("metrics", {})

        if not profile:
            return None

        now = datetime.now()

        return AnonymizedMetrics(
            metrics_id=str(uuid.uuid4()),
            generated_at=now.isoformat() + "Z",
            expertise_level=profile.get("expertise_level", "INTERMEDIATE"),
            session_count=metrics.get("session_count", 0),
            avg_success_rate=metrics.get("success_rate", 0.0),
            avg_session_duration_ms=metrics.get("avg_session_duration_ms", 0.0),
            feature_usage_rates=[],
        )

    # ============================================
    # Audit Logging
    # ============================================

    def _add_audit_entry(
        self,
        user_id: str,
        action: str,
        consent_type: ConsentType,
        new_status: ConsentStatus,
        old_status: Optional[ConsentStatus] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Add an entry to the audit log."""
        now = datetime.now()

        # Hash IP address for privacy
        hashed_ip = None
        if ip_address:
            hashed_ip = hashlib.sha256(ip_address.encode()).hexdigest()[:16]

        entry = ConsentAuditEntry(
            entry_id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            consent_type=consent_type,
            old_status=old_status,
            new_status=new_status,
            timestamp=now.isoformat() + "Z",
            policy_version=self.policy_version,
            ip_address=hashed_ip,
            user_agent=user_agent,
        )

        self._audit_log.append(entry)

    def get_audit_log(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[ConsentAuditEntry]:
        """
        Get audit log entries.

        Args:
            user_id: Optional user ID to filter by.
            limit: Maximum number of entries to return.

        Returns:
            List of audit entries (newest first).
        """
        entries = self._audit_log
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]

        return sorted(entries, key=lambda e: e.timestamp, reverse=True)[:limit]

    def _update_consent_status(
        self,
        user_id: str,
        consent_type: ConsentType,
        new_status: ConsentStatus,
    ) -> None:
        """Update a consent record's status."""
        if user_id in self._consent_records:
            record = self._consent_records[user_id].get(consent_type)
            if record:
                old_status = record.status
                record.status = new_status

                self._add_audit_entry(
                    user_id=user_id,
                    action="status_change",
                    consent_type=consent_type,
                    old_status=old_status,
                    new_status=new_status,
                )

    # ============================================
    # User Data Management (for testing/simulation)
    # ============================================

    def set_user_data(self, user_id: str, data: dict) -> None:
        """Set user data (for testing purposes)."""
        self._user_data[user_id] = data

    def get_user_data(self, user_id: str) -> Optional[dict]:
        """Get user data (for testing purposes)."""
        return self._user_data.get(user_id)

    def reset(self) -> None:
        """Reset all state (for testing)."""
        self._consent_records.clear()
        self._pending_requests.clear()
        self._dsr_requests.clear()
        self._audit_log.clear()
        self._user_data.clear()
