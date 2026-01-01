// Privacy and Consent Management
// GDPR/CCPA compliant profile handling with proper consent management
// Issue #49 - Phase 2: Adaptive Interface Personalization

// Dependencies:
// - ProfilingConsent from user_profile_types.baml (referenced but not duplicated)
// - PrivacyMode from metrics_collection.baml (referenced but not duplicated)

// ============================================
// Consent Types
// ============================================

/// Types of consent that can be granted or withdrawn
enum ConsentType {
  PROFILING @description("Track interaction patterns for personalization")
  PERSONALIZATION @description("Adapt responses based on behavior")
  ANALYTICS @description("Include in anonymous aggregate statistics")
  DATA_EXPORT @description("Allow profile data export")
  RETENTION @description("Allow data retention beyond session")
}

/// Status of a consent request
enum ConsentStatus {
  PENDING @description("Awaiting user response")
  GRANTED @description("User has granted consent")
  DENIED @description("User has denied consent")
  WITHDRAWN @description("User has withdrawn previous consent")
  EXPIRED @description("Consent has expired and needs renewal")
}

// ============================================
// Privacy Settings
// ============================================

/// User's privacy settings configuration
class PrivacySettings {
  profiling_enabled bool @description("Master switch for behavior profiling")
  data_retention_days int @description("Days to retain data (0 = session only)")
  on_device_only bool @description("Keep all data local, never sync")
  share_anonymous_stats bool @description("Allow anonymous aggregated statistics")
  privacy_mode string @description("Privacy mode: FULL, AGGREGATE_ONLY, SESSION_ONLY, DISABLED")
}

// ============================================
// Consent Records
// ============================================

/// Record of a specific consent grant or withdrawal
class ConsentRecord {
  record_id string @description("Unique identifier for this consent record")
  user_id string @description("User who gave/withdrew consent")
  consent_type ConsentType @description("Type of consent")
  status ConsentStatus @description("Current status of this consent")
  granted_at string? @description("ISO 8601 timestamp when consent was granted")
  withdrawn_at string? @description("ISO 8601 timestamp when consent was withdrawn")
  policy_version string @description("Version of privacy policy accepted")
  source string @description("How consent was obtained: ui, api, import")
}

/// Request to obtain consent from a user
class ConsentRequest {
  request_id string @description("Unique identifier for this request")
  user_id string @description("User being asked for consent")
  consent_types ConsentType[] @description("Types of consent being requested")
  policy_version string @description("Current privacy policy version")
  requested_at string @description("ISO 8601 timestamp of request")
  expires_at string? @description("ISO 8601 timestamp when request expires")
  purpose_explanation string @description("Human-readable explanation of data usage")
}

/// Response to a consent request
class ConsentResponse {
  request_id string @description("ID of the consent request being responded to")
  user_id string @description("User responding")
  responses ConsentDecision[] @description("Decisions for each consent type")
  responded_at string @description("ISO 8601 timestamp of response")
}

/// Individual consent decision
class ConsentDecision {
  consent_type ConsentType @description("Type of consent")
  granted bool @description("Whether consent was granted")
}

// ============================================
// Data Subject Requests (GDPR)
// ============================================

/// Types of data subject requests per GDPR
enum DSRType {
  ACCESS @description("GDPR Art. 15: Right to access personal data")
  RECTIFICATION @description("GDPR Art. 16: Right to correct inaccurate data")
  ERASURE @description("GDPR Art. 17: Right to be forgotten")
  PORTABILITY @description("GDPR Art. 20: Right to data portability")
  OBJECTION @description("GDPR Art. 21: Right to object to processing")
  RESTRICTION @description("GDPR Art. 18: Right to restrict processing")
}

/// Status of a data subject request
enum DSRStatus {
  RECEIVED @description("Request has been received")
  VALIDATING @description("Verifying requester identity")
  PROCESSING @description("Request is being processed")
  COMPLETED @description("Request has been fulfilled")
  REJECTED @description("Request was rejected (with reason)")
  FAILED @description("Request processing failed")
}

/// A data subject request from a user
class DataSubjectRequest {
  request_id string @description("Unique identifier for this DSR")
  request_type DSRType @description("Type of GDPR request")
  user_id string @description("User making the request")
  requested_at string @description("ISO 8601 timestamp of request")
  status DSRStatus @description("Current status of the request")
  status_updated_at string @description("ISO 8601 timestamp of last status change")
  notes string? @description("Internal notes about processing")
  completed_at string? @description("ISO 8601 timestamp when completed")
  rejection_reason string? @description("Reason if request was rejected")
}

/// Response to a data subject request
class DSRResponse {
  request_id string @description("ID of the DSR being responded to")
  status DSRStatus @description("Final status of the request")
  completed_at string @description("ISO 8601 timestamp of completion")
  data_included bool @description("Whether data is included in response")
  data_format string? @description("Format of included data: json, csv")
  download_url string? @description("URL to download exported data")
  expires_at string? @description("When download URL expires")
  message string @description("Human-readable status message")
}

// ============================================
// Data Deletion
// ============================================

/// Result of a data deletion request
class DeletionResult {
  user_id string @description("User whose data was deleted")
  success bool @description("Whether deletion was successful")
  deleted_at string @description("ISO 8601 timestamp of deletion")
  items_deleted DeletionItem[] @description("List of deleted data categories")
  retained_items RetainedItem[]? @description("Items retained for legal reasons")
  confirmation_token string @description("Token confirming deletion")
}

/// A category of deleted data
class DeletionItem {
  category string @description("Category of data: profile, metrics, history, etc.")
  count int @description("Number of records deleted")
}

/// Data retained for legal or compliance reasons
class RetainedItem {
  category string @description("Category of retained data")
  reason string @description("Legal basis for retention")
  retention_until string @description("ISO 8601 date until which data is retained")
}

// ============================================
// Data Export (Portability)
// ============================================

/// Format options for data export
enum ExportFormat {
  JSON @description("JSON format (machine-readable)")
  CSV @description("CSV format (spreadsheet-compatible)")
}

/// Request to export user data
class ExportRequest {
  request_id string @description("Unique identifier for this export request")
  user_id string @description("User requesting export")
  format ExportFormat @description("Desired export format")
  include_categories string[] @description("Data categories to include")
  requested_at string @description("ISO 8601 timestamp of request")
}

/// Result of a data export
class ExportResult {
  request_id string @description("ID of the export request")
  user_id string @description("User whose data was exported")
  success bool @description("Whether export was successful")
  format ExportFormat @description("Format of exported data")
  size_bytes int @description("Size of exported data")
  created_at string @description("ISO 8601 timestamp of export creation")
  download_url string? @description("URL to download export")
  expires_at string? @description("When download URL expires")
  checksum string @description("SHA-256 checksum of exported data")
}

// ============================================
// Anonymized Metrics
// ============================================

/// Anonymized metrics for analytics (no PII)
class AnonymizedMetrics {
  metrics_id string @description("Unique identifier for this metrics snapshot")
  generated_at string @description("ISO 8601 timestamp of generation")
  expertise_level string @description("Expertise level (no user ID)")
  session_count int @description("Number of sessions")
  avg_success_rate float @description("Average success rate")
  avg_session_duration_ms float @description("Average session duration")
  feature_usage_rates FeatureUsageRate[] @description("Anonymous feature usage")
}

/// Feature usage rate for analytics
class FeatureUsageRate {
  feature_name string @description("Name of the feature")
  usage_rate float @description("Percentage of users using this feature")
}

// ============================================
// Consent Audit Log
// ============================================

/// Audit log entry for consent changes
class ConsentAuditEntry {
  entry_id string @description("Unique identifier for this audit entry")
  user_id string @description("User whose consent changed")
  action string @description("Action taken: granted, withdrawn, expired")
  consent_type ConsentType @description("Type of consent affected")
  old_status ConsentStatus? @description("Previous consent status")
  new_status ConsentStatus @description("New consent status")
  timestamp string @description("ISO 8601 timestamp of change")
  policy_version string @description("Policy version at time of change")
  ip_address string? @description("IP address (hashed for privacy)")
  user_agent string? @description("User agent (for audit)")
}
