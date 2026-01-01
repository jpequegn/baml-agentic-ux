// User Preferences UI Types
// User-facing controls for managing personalization settings and preferences
// Issue #50 - Phase 2: Adaptive Interface Personalization

// Dependencies:
// - ExpertiseLevel, VerbosityLevel from response_generation.baml
// - UserProfile from user_profile_types.baml
// - PrivacySettings, ExportFormat from privacy_types.baml

// ============================================
// Preference Types
// ============================================

/// Types of user preferences that can be updated
enum PreferenceType {
  EXPERTISE_LEVEL_OVERRIDE @description("Manual override of expertise level")
  VERBOSITY_PREFERENCE @description("Preferred response verbosity")
  ADAPTATION_ENABLED @description("Enable/disable automatic adaptation")
  DATA_COLLECTION_CONSENT @description("Consent for data collection")
  INTERACTION_STYLE @description("Preferred communication style")
  PROACTIVE_HELP @description("Enable/disable proactive assistance")
}

/// Duration for temporary overrides
enum OverrideDuration {
  SESSION @description("Override for current session only")
  DAY @description("Override for 24 hours")
  WEEK @description("Override for 7 days")
  PERMANENT @description("Permanent override until reset")
}

/// Status of a preference update
enum PreferenceUpdateStatus {
  SUCCESS @description("Preference updated successfully")
  FAILED @description("Update failed")
  REQUIRES_CONFIRMATION @description("Requires user confirmation")
  INVALID_VALUE @description("Invalid preference value")
  UNAUTHORIZED @description("User not authorized to change this preference")
}

// ============================================
// Data Visibility Options
// ============================================

/// Options for what data users can see about themselves
class DataVisibilityOptions {
  show_collected_metrics bool @description("Show interaction metrics to user")
  show_expertise_score bool @description("Show numeric expertise score")
  show_level_history bool @description("Show history of level transitions")
  allow_data_export bool @description("Allow user to export their data")
  allow_data_deletion bool @description("Allow user to delete their data")
}

// ============================================
// User Preferences UI State
// ============================================

/// Complete UI state for user preferences management
class UserPreferencesUI {
  // Current state
  current_level ExpertiseLevel @description("Current expertise level")
  current_verbosity VerbosityLevel @description("Current verbosity setting")

  // Override controls
  can_override bool @description("Whether user can override expertise level")
  has_active_override bool @description("Whether an override is currently active")
  override_expires_at string? @description("ISO 8601 timestamp when override expires")

  // Available options
  available_levels ExpertiseLevel[] @description("Levels available for selection")
  verbosity_options VerbosityLevel[] @description("Verbosity levels available")

  // Data visibility
  data_visibility DataVisibilityOptions @description("What data user can access")

  // Adaptation settings
  adaptation_enabled bool @description("Whether automatic adaptation is on")

  // Privacy controls
  data_collection_enabled bool @description("Whether data collection is on")
  can_export_data bool @description("Whether export is available")
  can_delete_data bool @description("Whether deletion is available")
}

// ============================================
// Preference Update Request/Response
// ============================================

/// Request to update a user preference
class PreferenceUpdateRequest {
  request_id string @description("Unique identifier for this request")
  user_id string @description("User making the request")
  preference_type PreferenceType @description("Type of preference to update")
  new_value string @description("New value (JSON-encoded if complex)")
  reason string? @description("User's reason for the change")
  override_duration OverrideDuration? @description("Duration for override (if applicable)")
  requested_at string @description("ISO 8601 timestamp of request")
}

/// Result of a preference update
class PreferenceUpdateResult {
  request_id string @description("ID of the original request")
  status PreferenceUpdateStatus @description("Status of the update")
  previous_value string? @description("Previous value before update")
  new_value string? @description("New value after update (if successful)")
  effective_at string? @description("When the change takes effect")
  expires_at string? @description("When override expires (if applicable)")
  message string @description("Human-readable status message")
  requires_restart bool @description("Whether changes require session restart")
}

// ============================================
// Level Override
// ============================================

/// Configuration for a level override
class LevelOverride {
  override_id string @description("Unique identifier for this override")
  user_id string @description("User who created the override")
  original_level ExpertiseLevel @description("Level before override")
  override_level ExpertiseLevel @description("Level set by override")
  duration OverrideDuration @description("How long the override lasts")
  created_at string @description("ISO 8601 timestamp of creation")
  expires_at string? @description("ISO 8601 timestamp of expiration")
  reason string? @description("User's reason for override")
  is_active bool @description("Whether override is currently active")
}

/// Request to reset to automatic level detection
class ResetToAutoRequest {
  request_id string @description("Unique identifier for this request")
  user_id string @description("User requesting reset")
  requested_at string @description("ISO 8601 timestamp of request")
  recalculate_immediately bool @description("Whether to recalculate level now")
}

/// Result of reset to automatic
class ResetToAutoResult {
  request_id string @description("ID of the original request")
  success bool @description("Whether reset was successful")
  previous_override LevelOverride? @description("The override that was removed")
  new_level ExpertiseLevel? @description("New automatically determined level")
  new_score float? @description("New expertise score")
  message string @description("Human-readable status message")
}

// ============================================
// Verbosity Control
// ============================================

/// Verbosity preference settings with preview capability
class VerbosityPreferenceSetting {
  user_id string @description("User ID")
  current_verbosity VerbosityLevel @description("Current verbosity setting")
  preferred_verbosity VerbosityLevel @description("User's preferred verbosity")
  preview_available bool @description("Whether preview is available")
  sample_response string? @description("Sample response at this verbosity")
}

/// Request to preview verbosity
class VerbosityPreviewRequest {
  user_id string @description("User requesting preview")
  verbosity_level VerbosityLevel @description("Verbosity level to preview")
  sample_context string? @description("Optional context for preview")
}

/// Verbosity preview result
class VerbosityPreviewResult {
  verbosity_level VerbosityLevel @description("Verbosity level previewed")
  sample_response string @description("Sample response at this level")
  word_count int @description("Approximate word count")
  includes_examples bool @description("Whether examples are included")
  includes_explanations bool @description("Whether explanations are included")
}

// ============================================
// Data Transparency Panel
// ============================================

/// Data displayed in transparency panel
class DataTransparencyPanel {
  user_id string @description("User ID")
  generated_at string @description("ISO 8601 timestamp of generation")

  // Metrics
  total_interactions int @description("Total interaction count")
  session_count int @description("Total session count")
  success_rate float @description("Overall success rate")

  // Expertise
  current_level ExpertiseLevel @description("Current expertise level")
  expertise_score float @description("Current numeric score")
  score_confidence float @description("Confidence in the score")

  // History
  level_history LevelHistoryEntry[] @description("Recent level changes")

  // Data categories
  data_categories DataCategory[] @description("Categories of collected data")
}

/// Entry in level history
class LevelHistoryEntry {
  timestamp string @description("ISO 8601 timestamp of change")
  from_level ExpertiseLevel @description("Previous level")
  to_level ExpertiseLevel @description("New level")
  trigger string @description("What triggered the change")
  was_user_initiated bool @description("Whether user requested the change")
}

/// Category of collected data
class DataCategory {
  category_name string @description("Name of the data category")
  description string @description("What data is collected")
  record_count int @description("Number of records in this category")
  retention_days int @description("How long data is retained")
  can_export bool @description("Whether this data can be exported")
  can_delete bool @description("Whether this data can be deleted")
}

// ============================================
// Export/Delete Controls
// ============================================

/// Export control UI state
class ExportControlState {
  user_id string @description("User ID")
  can_export bool @description("Whether export is available")
  available_formats string[] @description("Available export formats")
  estimated_size_bytes int @description("Estimated export size")
  last_export_at string? @description("ISO 8601 timestamp of last export")
  exportable_categories string[] @description("Categories available for export")
}

/// Delete control UI state
class DeleteControlState {
  user_id string @description("User ID")
  can_delete bool @description("Whether deletion is available")
  deletable_categories string[] @description("Categories that can be deleted")
  requires_confirmation bool @description("Whether confirmation is required")
  confirmation_phrase string? @description("Phrase user must type to confirm")
  will_delete_account bool @description("Whether account will be deleted")
}

/// Confirmation request for deletion
class DeletionConfirmationRequest {
  request_id string @description("Unique identifier for this request")
  user_id string @description("User requesting deletion")
  categories_to_delete string[] @description("Categories to delete")
  confirmation_phrase string? @description("Confirmation phrase if required")
  requested_at string @description("ISO 8601 timestamp of request")
  understood_irreversible bool @description("User acknowledges irreversibility")
}

/// Result of deletion confirmation
class DeletionConfirmationResult {
  request_id string @description("ID of the original request")
  confirmed bool @description("Whether deletion was confirmed")
  scheduled_at string? @description("When deletion is scheduled")
  categories_deleted string[]? @description("Categories that will be deleted")
  message string @description("Human-readable status message")
}

// ============================================
// Accessibility
// ============================================

/// Accessibility settings for preferences UI
class AccessibilitySettings {
  keyboard_navigation bool @description("Enable keyboard navigation")
  screen_reader_compatible bool @description("Optimize for screen readers")
  high_contrast bool @description("Enable high contrast mode")
  large_text bool @description("Enable large text mode")
  reduce_motion bool @description("Reduce animations and motion")
  aria_labels_enabled bool @description("Include ARIA labels")
}

// ============================================
// Functions
// ============================================

/// Get user preferences UI state
function GetUserPreferencesUI(
  user_id: string,
  profile: UserProfile
) -> UserPreferencesUI {
  client CustomSonnet4
  prompt #"
    Generate the user preferences UI state for this user.

    User ID: {{ user_id }}

    User Profile:
    {{ profile }}

    Build the preferences UI state:
    1. Set current_level and current_verbosity from profile
    2. Check if user can override (profiling_enabled must be true)
    3. List all available expertise levels and verbosity options
    4. Set data visibility based on consent settings
    5. Determine export/delete availability based on consent

    All users can view available levels:
    - NOVICE, BEGINNER, INTERMEDIATE, ADVANCED, EXPERT

    All verbosity options:
    - MINIMAL, CONCISE, STANDARD, DETAILED, EXHAUSTIVE

    {{ ctx.output_format }}
  "#
}

/// Update a user preference
function UpdateUserPreference(
  request: PreferenceUpdateRequest,
  current_profile: UserProfile
) -> PreferenceUpdateResult {
  client CustomSonnet4
  prompt #"
    Process a user preference update request.

    Request:
    {{ request }}

    Current Profile:
    {{ current_profile }}

    Validation Rules:
    1. EXPERTISE_LEVEL_OVERRIDE: Must be a valid ExpertiseLevel
    2. VERBOSITY_PREFERENCE: Must be a valid VerbosityLevel
    3. ADAPTATION_ENABLED: Must be "true" or "false"
    4. DATA_COLLECTION_CONSENT: Requires profiling_enabled check
    5. INTERACTION_STYLE: Must be valid ProfileInteractionStyle
    6. PROACTIVE_HELP: Must be "true" or "false"

    Process the update:
    - Validate the new value
    - Check authorization
    - Determine if restart is required
    - Generate appropriate response

    {{ ctx.output_format }}
  "#
}

/// Generate verbosity preview
function GenerateVerbosityPreview(
  request: VerbosityPreviewRequest
) -> VerbosityPreviewResult {
  client CustomSonnet4
  prompt #"
    Generate a sample response to preview the verbosity level.

    Request:
    {{ request }}

    Sample Context: {% if request.sample_context %}{{ request.sample_context }}{% else %}How do I reset my password?{% endif %}

    Generate a sample response that demonstrates this verbosity level:

    MINIMAL: 1-2 sentences, just the answer
    CONCISE: 2-3 sentences, brief but complete
    STANDARD: Short paragraph, balanced detail
    DETAILED: Multiple paragraphs, comprehensive
    EXHAUSTIVE: Full explanation with examples, warnings, alternatives

    {{ ctx.output_format }}
  "#
}

/// Get data transparency panel
function GetDataTransparencyPanel(
  user_id: string,
  profile: UserProfile
) -> DataTransparencyPanel {
  client CustomSonnet4
  prompt #"
    Generate the data transparency panel for this user.

    User ID: {{ user_id }}

    User Profile:
    {{ profile }}

    Build the transparency panel:
    1. Include interaction metrics if available
    2. Show current expertise level and score
    3. Generate level history from expertise_history
    4. List data categories with retention info

    Data categories typically include:
    - Profile Data (name, preferences) - retained based on consent
    - Interaction History (commands, responses) - retained based on consent
    - Expertise Metrics (scores, factors) - retained while profiling enabled
    - Session Data (current session info) - session only

    {{ ctx.output_format }}
  "#
}

/// Create a level override
function CreateLevelOverride(
  user_id: string,
  target_level: ExpertiseLevel,
  duration: OverrideDuration,
  reason: string?
) -> LevelOverride {
  client CustomSonnet4
  prompt #"
    Create a new expertise level override.

    User ID: {{ user_id }}
    Target Level: {{ target_level }}
    Duration: {{ duration }}
    Reason: {% if reason %}{{ reason }}{% else %}User preference{% endif %}

    Generate the override:
    1. Create unique override_id
    2. Set appropriate timestamps
    3. Calculate expires_at based on duration:
       - SESSION: null (handled by session end)
       - DAY: current time + 24 hours
       - WEEK: current time + 7 days
       - PERMANENT: null (no expiration)
    4. Set is_active to true

    {{ ctx.output_format }}
  "#
}

/// Reset to automatic level detection
function ResetToAutomatic(
  request: ResetToAutoRequest,
  current_override: LevelOverride?
) -> ResetToAutoResult {
  client CustomSonnet4
  prompt #"
    Process a request to reset to automatic expertise detection.

    Request:
    {{ request }}

    Current Override:
    {% if current_override %}{{ current_override }}{% else %}None active{% endif %}

    Process the reset:
    1. If no override exists, indicate already automatic
    2. If override exists, deactivate it
    3. If recalculate_immediately, indicate new level will be computed
    4. Generate appropriate success/failure response

    {{ ctx.output_format }}
  "#
}
