"""
User Preferences Manager

Implements user-facing controls for managing personalization settings and preferences.
Issue #50 - Phase 2: Adaptive Interface Personalization

This module provides:
- Level override controls (manual expertise level setting)
- Verbosity preference management with preview
- Data transparency panel for showing collected data
- Export/delete controls for GDPR compliance
- Accessibility settings management
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional
import hashlib
import uuid


# ============================================
# Enums (matching BAML schema)
# ============================================


class PreferenceType(Enum):
    """Types of user preferences that can be updated."""

    EXPERTISE_LEVEL_OVERRIDE = "EXPERTISE_LEVEL_OVERRIDE"
    VERBOSITY_PREFERENCE = "VERBOSITY_PREFERENCE"
    ADAPTATION_ENABLED = "ADAPTATION_ENABLED"
    DATA_COLLECTION_CONSENT = "DATA_COLLECTION_CONSENT"
    INTERACTION_STYLE = "INTERACTION_STYLE"
    PROACTIVE_HELP = "PROACTIVE_HELP"


class OverrideDuration(Enum):
    """Duration for temporary overrides."""

    SESSION = "SESSION"
    DAY = "DAY"
    WEEK = "WEEK"
    PERMANENT = "PERMANENT"


class PreferenceUpdateStatus(Enum):
    """Status of a preference update."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION"
    INVALID_VALUE = "INVALID_VALUE"
    UNAUTHORIZED = "UNAUTHORIZED"


class ExpertiseLevel(Enum):
    """User expertise levels."""

    NOVICE = "NOVICE"
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class VerbosityLevel(Enum):
    """Response verbosity levels."""

    MINIMAL = "MINIMAL"
    CONCISE = "CONCISE"
    STANDARD = "STANDARD"
    DETAILED = "DETAILED"
    EXHAUSTIVE = "EXHAUSTIVE"


class ProfileInteractionStyle(Enum):
    """Profile interaction styles."""

    CONVERSATIONAL = "CONVERSATIONAL"
    PROFESSIONAL = "PROFESSIONAL"
    TERSE = "TERSE"
    EDUCATIONAL = "EDUCATIONAL"


# ============================================
# Data Classes
# ============================================


@dataclass
class DataVisibilityOptions:
    """Options for what data users can see about themselves."""

    show_collected_metrics: bool = True
    show_expertise_score: bool = True
    show_level_history: bool = True
    allow_data_export: bool = True
    allow_data_deletion: bool = True


@dataclass
class UserPreferencesUI:
    """Complete UI state for user preferences management."""

    current_level: ExpertiseLevel
    current_verbosity: VerbosityLevel
    can_override: bool
    has_active_override: bool
    override_expires_at: Optional[str]
    available_levels: list[ExpertiseLevel]
    verbosity_options: list[VerbosityLevel]
    data_visibility: DataVisibilityOptions
    adaptation_enabled: bool
    data_collection_enabled: bool
    can_export_data: bool
    can_delete_data: bool


@dataclass
class PreferenceUpdateRequest:
    """Request to update a user preference."""

    request_id: str
    user_id: str
    preference_type: PreferenceType
    new_value: str
    requested_at: str
    reason: Optional[str] = None
    override_duration: Optional[OverrideDuration] = None


@dataclass
class PreferenceUpdateResult:
    """Result of a preference update."""

    request_id: str
    status: PreferenceUpdateStatus
    message: str
    requires_restart: bool = False
    previous_value: Optional[str] = None
    new_value: Optional[str] = None
    effective_at: Optional[str] = None
    expires_at: Optional[str] = None


@dataclass
class LevelOverride:
    """Configuration for a level override."""

    override_id: str
    user_id: str
    original_level: ExpertiseLevel
    override_level: ExpertiseLevel
    duration: OverrideDuration
    created_at: str
    is_active: bool
    expires_at: Optional[str] = None
    reason: Optional[str] = None


@dataclass
class ResetToAutoRequest:
    """Request to reset to automatic level detection."""

    request_id: str
    user_id: str
    requested_at: str
    recalculate_immediately: bool = True


@dataclass
class ResetToAutoResult:
    """Result of reset to automatic."""

    request_id: str
    success: bool
    message: str
    previous_override: Optional[LevelOverride] = None
    new_level: Optional[ExpertiseLevel] = None
    new_score: Optional[float] = None


@dataclass
class VerbosityPreviewRequest:
    """Request to preview verbosity."""

    user_id: str
    verbosity_level: VerbosityLevel
    sample_context: Optional[str] = None


@dataclass
class VerbosityPreviewResult:
    """Verbosity preview result."""

    verbosity_level: VerbosityLevel
    sample_response: str
    word_count: int
    includes_examples: bool
    includes_explanations: bool


@dataclass
class LevelHistoryEntry:
    """Entry in level history."""

    timestamp: str
    from_level: ExpertiseLevel
    to_level: ExpertiseLevel
    trigger: str
    was_user_initiated: bool


@dataclass
class DataCategory:
    """Category of collected data."""

    category_name: str
    description: str
    record_count: int
    retention_days: int
    can_export: bool
    can_delete: bool


@dataclass
class DataTransparencyPanel:
    """Data displayed in transparency panel."""

    user_id: str
    generated_at: str
    total_interactions: int
    session_count: int
    success_rate: float
    current_level: ExpertiseLevel
    expertise_score: float
    score_confidence: float
    level_history: list[LevelHistoryEntry]
    data_categories: list[DataCategory]


@dataclass
class ExportControlState:
    """Export control UI state."""

    user_id: str
    can_export: bool
    available_formats: list[str]
    estimated_size_bytes: int
    exportable_categories: list[str]
    last_export_at: Optional[str] = None


@dataclass
class DeleteControlState:
    """Delete control UI state."""

    user_id: str
    can_delete: bool
    deletable_categories: list[str]
    requires_confirmation: bool
    will_delete_account: bool
    confirmation_phrase: Optional[str] = None


@dataclass
class DeletionConfirmationRequest:
    """Confirmation request for deletion."""

    request_id: str
    user_id: str
    categories_to_delete: list[str]
    requested_at: str
    understood_irreversible: bool
    confirmation_phrase: Optional[str] = None


@dataclass
class DeletionConfirmationResult:
    """Result of deletion confirmation."""

    request_id: str
    confirmed: bool
    message: str
    scheduled_at: Optional[str] = None
    categories_deleted: Optional[list[str]] = None


@dataclass
class AccessibilitySettings:
    """Accessibility settings for preferences UI."""

    keyboard_navigation: bool = True
    screen_reader_compatible: bool = True
    high_contrast: bool = False
    large_text: bool = False
    reduce_motion: bool = False
    aria_labels_enabled: bool = True


# ============================================
# User Data Store (Simple in-memory store)
# ============================================


@dataclass
class UserData:
    """User data stored by the preferences manager."""

    user_id: str
    expertise_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE
    expertise_score: float = 0.5
    expertise_confidence: float = 0.3
    verbosity: VerbosityLevel = VerbosityLevel.STANDARD
    interaction_style: ProfileInteractionStyle = ProfileInteractionStyle.CONVERSATIONAL
    adaptation_enabled: bool = True
    data_collection_enabled: bool = True
    proactive_help_enabled: bool = True
    total_interactions: int = 0
    session_count: int = 0
    success_rate: float = 0.0
    level_history: list[LevelHistoryEntry] = field(default_factory=list)
    active_override: Optional[LevelOverride] = None
    accessibility: AccessibilitySettings = field(default_factory=AccessibilitySettings)


# ============================================
# Preferences Manager
# ============================================


class PreferencesManager:
    """
    Manages user preferences and personalization controls.

    Provides:
    - Level override controls (manual expertise level setting)
    - Verbosity preference management with preview
    - Data transparency for showing collected data
    - Export/delete controls for GDPR compliance
    - Accessibility settings
    """

    def __init__(self) -> None:
        """Initialize the preferences manager."""
        self._users: dict[str, UserData] = {}
        self._preference_history: list[dict] = []

    def _get_or_create_user(self, user_id: str) -> UserData:
        """Get or create user data."""
        if user_id not in self._users:
            self._users[user_id] = UserData(user_id=user_id)
        return self._users[user_id]

    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return str(uuid.uuid4())

    def _now_iso(self) -> str:
        """Get current timestamp in ISO 8601 format."""
        return datetime.now(timezone.utc).isoformat()

    # ============================================
    # Get User Preferences UI
    # ============================================

    def get_user_preferences_ui(self, user_id: str) -> UserPreferencesUI:
        """
        Get the complete user preferences UI state.

        Args:
            user_id: User identifier

        Returns:
            UserPreferencesUI with current state and available options
        """
        user = self._get_or_create_user(user_id)

        # Check if override is still active
        has_active_override = False
        override_expires_at = None
        if user.active_override and user.active_override.is_active:
            if user.active_override.expires_at:
                expires = datetime.fromisoformat(
                    user.active_override.expires_at.replace("Z", "+00:00")
                )
                if expires > datetime.now(timezone.utc):
                    has_active_override = True
                    override_expires_at = user.active_override.expires_at
                else:
                    # Override expired
                    user.active_override.is_active = False
            else:
                # Permanent or session override
                has_active_override = True

        return UserPreferencesUI(
            current_level=user.expertise_level,
            current_verbosity=user.verbosity,
            can_override=user.data_collection_enabled,
            has_active_override=has_active_override,
            override_expires_at=override_expires_at,
            available_levels=list(ExpertiseLevel),
            verbosity_options=list(VerbosityLevel),
            data_visibility=DataVisibilityOptions(
                show_collected_metrics=user.data_collection_enabled,
                show_expertise_score=user.data_collection_enabled,
                show_level_history=user.data_collection_enabled,
                allow_data_export=user.data_collection_enabled,
                allow_data_deletion=True,
            ),
            adaptation_enabled=user.adaptation_enabled,
            data_collection_enabled=user.data_collection_enabled,
            can_export_data=user.data_collection_enabled,
            can_delete_data=True,
        )

    # ============================================
    # Update Preferences
    # ============================================

    def update_preference(
        self, request: PreferenceUpdateRequest
    ) -> PreferenceUpdateResult:
        """
        Update a user preference.

        Args:
            request: Preference update request

        Returns:
            PreferenceUpdateResult with status and details
        """
        user = self._get_or_create_user(request.user_id)

        # Validate and process based on preference type
        if request.preference_type == PreferenceType.EXPERTISE_LEVEL_OVERRIDE:
            return self._update_expertise_override(user, request)
        elif request.preference_type == PreferenceType.VERBOSITY_PREFERENCE:
            return self._update_verbosity(user, request)
        elif request.preference_type == PreferenceType.ADAPTATION_ENABLED:
            return self._update_adaptation(user, request)
        elif request.preference_type == PreferenceType.DATA_COLLECTION_CONSENT:
            return self._update_data_collection(user, request)
        elif request.preference_type == PreferenceType.INTERACTION_STYLE:
            return self._update_interaction_style(user, request)
        elif request.preference_type == PreferenceType.PROACTIVE_HELP:
            return self._update_proactive_help(user, request)
        else:
            return PreferenceUpdateResult(
                request_id=request.request_id,
                status=PreferenceUpdateStatus.INVALID_VALUE,
                message=f"Unknown preference type: {request.preference_type}",
            )

    def _update_expertise_override(
        self, user: UserData, request: PreferenceUpdateRequest
    ) -> PreferenceUpdateResult:
        """Update expertise level override."""
        try:
            new_level = ExpertiseLevel(request.new_value)
        except ValueError:
            return PreferenceUpdateResult(
                request_id=request.request_id,
                status=PreferenceUpdateStatus.INVALID_VALUE,
                message=f"Invalid expertise level: {request.new_value}",
            )

        if not user.data_collection_enabled:
            return PreferenceUpdateResult(
                request_id=request.request_id,
                status=PreferenceUpdateStatus.UNAUTHORIZED,
                message="Cannot override level when data collection is disabled",
            )

        previous_level = user.expertise_level
        duration = request.override_duration or OverrideDuration.SESSION

        # Create override
        override = self.create_level_override(
            user_id=user.user_id,
            target_level=new_level,
            duration=duration,
            reason=request.reason,
        )

        user.active_override = override
        user.expertise_level = new_level

        # Record history
        user.level_history.append(
            LevelHistoryEntry(
                timestamp=self._now_iso(),
                from_level=previous_level,
                to_level=new_level,
                trigger="USER_REQUEST",
                was_user_initiated=True,
            )
        )

        return PreferenceUpdateResult(
            request_id=request.request_id,
            status=PreferenceUpdateStatus.SUCCESS,
            previous_value=previous_level.value,
            new_value=new_level.value,
            effective_at=self._now_iso(),
            expires_at=override.expires_at,
            message=f"Expertise level overridden to {new_level.value}",
            requires_restart=False,
        )

    def _update_verbosity(
        self, user: UserData, request: PreferenceUpdateRequest
    ) -> PreferenceUpdateResult:
        """Update verbosity preference."""
        try:
            new_verbosity = VerbosityLevel(request.new_value)
        except ValueError:
            return PreferenceUpdateResult(
                request_id=request.request_id,
                status=PreferenceUpdateStatus.INVALID_VALUE,
                message=f"Invalid verbosity level: {request.new_value}",
            )

        previous = user.verbosity.value
        user.verbosity = new_verbosity

        return PreferenceUpdateResult(
            request_id=request.request_id,
            status=PreferenceUpdateStatus.SUCCESS,
            previous_value=previous,
            new_value=new_verbosity.value,
            effective_at=self._now_iso(),
            message=f"Verbosity updated to {new_verbosity.value}",
            requires_restart=False,
        )

    def _update_adaptation(
        self, user: UserData, request: PreferenceUpdateRequest
    ) -> PreferenceUpdateResult:
        """Update adaptation enabled setting."""
        new_value = request.new_value.lower() == "true"
        previous = str(user.adaptation_enabled).lower()
        user.adaptation_enabled = new_value

        return PreferenceUpdateResult(
            request_id=request.request_id,
            status=PreferenceUpdateStatus.SUCCESS,
            previous_value=previous,
            new_value=str(new_value).lower(),
            effective_at=self._now_iso(),
            message=f"Automatic adaptation {'enabled' if new_value else 'disabled'}",
            requires_restart=False,
        )

    def _update_data_collection(
        self, user: UserData, request: PreferenceUpdateRequest
    ) -> PreferenceUpdateResult:
        """Update data collection consent."""
        new_value = request.new_value.lower() == "true"
        previous = str(user.data_collection_enabled).lower()
        user.data_collection_enabled = new_value

        # If disabling, clear any active override
        if not new_value and user.active_override:
            user.active_override.is_active = False

        return PreferenceUpdateResult(
            request_id=request.request_id,
            status=PreferenceUpdateStatus.SUCCESS,
            previous_value=previous,
            new_value=str(new_value).lower(),
            effective_at=self._now_iso(),
            message=f"Data collection {'enabled' if new_value else 'disabled'}",
            requires_restart=False,
        )

    def _update_interaction_style(
        self, user: UserData, request: PreferenceUpdateRequest
    ) -> PreferenceUpdateResult:
        """Update interaction style."""
        try:
            new_style = ProfileInteractionStyle(request.new_value)
        except ValueError:
            return PreferenceUpdateResult(
                request_id=request.request_id,
                status=PreferenceUpdateStatus.INVALID_VALUE,
                message=f"Invalid interaction style: {request.new_value}",
            )

        previous = user.interaction_style.value
        user.interaction_style = new_style

        return PreferenceUpdateResult(
            request_id=request.request_id,
            status=PreferenceUpdateStatus.SUCCESS,
            previous_value=previous,
            new_value=new_style.value,
            effective_at=self._now_iso(),
            message=f"Interaction style updated to {new_style.value}",
            requires_restart=False,
        )

    def _update_proactive_help(
        self, user: UserData, request: PreferenceUpdateRequest
    ) -> PreferenceUpdateResult:
        """Update proactive help setting."""
        new_value = request.new_value.lower() == "true"
        previous = str(user.proactive_help_enabled).lower()
        user.proactive_help_enabled = new_value

        return PreferenceUpdateResult(
            request_id=request.request_id,
            status=PreferenceUpdateStatus.SUCCESS,
            previous_value=previous,
            new_value=str(new_value).lower(),
            effective_at=self._now_iso(),
            message=f"Proactive help {'enabled' if new_value else 'disabled'}",
            requires_restart=False,
        )

    # ============================================
    # Level Override Controls
    # ============================================

    def create_level_override(
        self,
        user_id: str,
        target_level: ExpertiseLevel,
        duration: OverrideDuration,
        reason: Optional[str] = None,
    ) -> LevelOverride:
        """
        Create a level override for manual expertise level setting.

        Args:
            user_id: User identifier
            target_level: Target expertise level
            duration: How long the override lasts
            reason: Optional reason for override

        Returns:
            LevelOverride configuration
        """
        user = self._get_or_create_user(user_id)
        now = datetime.now(timezone.utc)

        # Calculate expiration
        expires_at: Optional[str] = None
        if duration == OverrideDuration.DAY:
            expires_at = (now + timedelta(days=1)).isoformat()
        elif duration == OverrideDuration.WEEK:
            expires_at = (now + timedelta(weeks=1)).isoformat()
        # SESSION and PERMANENT have no fixed expiration

        override = LevelOverride(
            override_id=self._generate_id(),
            user_id=user_id,
            original_level=user.expertise_level,
            override_level=target_level,
            duration=duration,
            created_at=now.isoformat(),
            expires_at=expires_at,
            reason=reason,
            is_active=True,
        )

        return override

    def reset_to_automatic(self, request: ResetToAutoRequest) -> ResetToAutoResult:
        """
        Reset expertise level to automatic detection.

        Args:
            request: Reset request

        Returns:
            ResetToAutoResult with status
        """
        user = self._get_or_create_user(request.user_id)

        if not user.active_override or not user.active_override.is_active:
            return ResetToAutoResult(
                request_id=request.request_id,
                success=True,
                message="Already using automatic level detection",
            )

        previous_override = user.active_override
        user.active_override.is_active = False

        # Reset to original level if we have it
        original_level = previous_override.original_level
        user.expertise_level = original_level

        # Record history
        user.level_history.append(
            LevelHistoryEntry(
                timestamp=self._now_iso(),
                from_level=previous_override.override_level,
                to_level=original_level,
                trigger="RESET_TO_AUTOMATIC",
                was_user_initiated=True,
            )
        )

        return ResetToAutoResult(
            request_id=request.request_id,
            success=True,
            previous_override=previous_override,
            new_level=original_level if request.recalculate_immediately else None,
            new_score=user.expertise_score if request.recalculate_immediately else None,
            message="Reset to automatic level detection",
        )

    # ============================================
    # Verbosity Preview
    # ============================================

    def preview_verbosity(
        self, request: VerbosityPreviewRequest
    ) -> VerbosityPreviewResult:
        """
        Generate a sample response to preview verbosity level.

        Args:
            request: Verbosity preview request

        Returns:
            VerbosityPreviewResult with sample response
        """
        # Generate sample responses for each verbosity level
        samples = {
            VerbosityLevel.MINIMAL: (
                "Go to Settings > Security > Reset Password.",
                5,
                False,
                False,
            ),
            VerbosityLevel.CONCISE: (
                "To reset your password, navigate to Settings, then Security, "
                "and click Reset Password. You'll receive an email confirmation.",
                18,
                False,
                False,
            ),
            VerbosityLevel.STANDARD: (
                "To reset your password:\n"
                "1. Go to Settings\n"
                "2. Select Security\n"
                "3. Click Reset Password\n"
                "4. Enter your email\n"
                "5. Check your inbox for a confirmation link\n\n"
                "The link expires in 24 hours.",
                35,
                False,
                True,
            ),
            VerbosityLevel.DETAILED: (
                "To reset your password, follow these steps:\n\n"
                "1. **Navigate to Settings**: Click your profile icon in the top right "
                "corner, then select 'Settings' from the dropdown menu.\n\n"
                "2. **Open Security Settings**: In the left sidebar, click on "
                "'Security' to access security options.\n\n"
                "3. **Initiate Password Reset**: Look for the 'Reset Password' button "
                "and click it.\n\n"
                "4. **Verify Your Identity**: Enter your registered email address. "
                "For security, you may need to complete additional verification.\n\n"
                "5. **Check Your Email**: A password reset link will be sent to your "
                "email. The link expires after 24 hours for security.\n\n"
                "**Note**: If you don't receive the email within 5 minutes, check your "
                "spam folder or contact support.",
                120,
                False,
                True,
            ),
            VerbosityLevel.EXHAUSTIVE: (
                "# Complete Guide to Resetting Your Password\n\n"
                "## Overview\n"
                "Resetting your password is a security measure that allows you to "
                "regain access to your account or update your credentials.\n\n"
                "## Step-by-Step Instructions\n\n"
                "### Step 1: Access Settings\n"
                "Click your profile icon in the top right corner of any page. "
                "From the dropdown menu, select 'Settings'.\n\n"
                "### Step 2: Navigate to Security\n"
                "In the Settings page, find the left sidebar. Click on 'Security' "
                "to view your security options.\n\n"
                "### Step 3: Initiate Reset\n"
                "Locate and click the 'Reset Password' button. This begins the "
                "secure reset process.\n\n"
                "### Step 4: Email Verification\n"
                "Enter your registered email address. You may be asked to complete "
                "a CAPTCHA or two-factor authentication.\n\n"
                "### Step 5: Complete Reset\n"
                "Check your email inbox for a message from us. Click the reset link "
                "within 24 hours. Choose a strong password.\n\n"
                "## Password Requirements\n"
                "- At least 8 characters\n"
                "- One uppercase letter\n"
                "- One lowercase letter\n"
                "- One number\n"
                "- One special character\n\n"
                "## Troubleshooting\n"
                "- **Email not received**: Check spam folder, verify email address\n"
                "- **Link expired**: Request a new reset link\n"
                "- **Still having issues**: Contact support@example.com\n\n"
                "## Security Tips\n"
                "- Never share your password\n"
                "- Use a unique password for this account\n"
                "- Consider using a password manager\n"
                "- Enable two-factor authentication",
                280,
                True,
                True,
            ),
        }

        sample, word_count, includes_examples, includes_explanations = samples.get(
            request.verbosity_level,
            samples[VerbosityLevel.STANDARD],
        )

        return VerbosityPreviewResult(
            verbosity_level=request.verbosity_level,
            sample_response=sample,
            word_count=word_count,
            includes_examples=includes_examples,
            includes_explanations=includes_explanations,
        )

    # ============================================
    # Data Transparency
    # ============================================

    def get_data_transparency_panel(self, user_id: str) -> DataTransparencyPanel:
        """
        Get the data transparency panel showing collected data.

        Args:
            user_id: User identifier

        Returns:
            DataTransparencyPanel with metrics and data categories
        """
        user = self._get_or_create_user(user_id)

        # Standard data categories
        data_categories = [
            DataCategory(
                category_name="Profile Data",
                description="Your preferences, settings, and account information",
                record_count=1,
                retention_days=90 if user.data_collection_enabled else 0,
                can_export=True,
                can_delete=True,
            ),
            DataCategory(
                category_name="Interaction History",
                description="Records of your commands and system responses",
                record_count=user.total_interactions,
                retention_days=90 if user.data_collection_enabled else 0,
                can_export=user.data_collection_enabled,
                can_delete=True,
            ),
            DataCategory(
                category_name="Expertise Metrics",
                description="Scores and factors used for expertise detection",
                record_count=1 if user.data_collection_enabled else 0,
                retention_days=90 if user.data_collection_enabled else 0,
                can_export=user.data_collection_enabled,
                can_delete=True,
            ),
            DataCategory(
                category_name="Session Data",
                description="Current session information (temporary)",
                record_count=1,
                retention_days=0,  # Session only
                can_export=False,
                can_delete=False,
            ),
        ]

        return DataTransparencyPanel(
            user_id=user_id,
            generated_at=self._now_iso(),
            total_interactions=user.total_interactions,
            session_count=user.session_count,
            success_rate=user.success_rate,
            current_level=user.expertise_level,
            expertise_score=user.expertise_score,
            score_confidence=user.expertise_confidence,
            level_history=user.level_history[-10:],  # Last 10 entries
            data_categories=data_categories,
        )

    # ============================================
    # Export Controls
    # ============================================

    def get_export_control_state(self, user_id: str) -> ExportControlState:
        """
        Get the export control UI state.

        Args:
            user_id: User identifier

        Returns:
            ExportControlState with export options
        """
        user = self._get_or_create_user(user_id)

        return ExportControlState(
            user_id=user_id,
            can_export=user.data_collection_enabled,
            available_formats=["JSON", "CSV"],
            estimated_size_bytes=1024 * (1 + user.total_interactions),  # Rough estimate
            last_export_at=None,  # Would track from export history
            exportable_categories=[
                "Profile Data",
                "Interaction History",
                "Expertise Metrics",
            ]
            if user.data_collection_enabled
            else ["Profile Data"],
        )

    # ============================================
    # Delete Controls
    # ============================================

    def get_delete_control_state(self, user_id: str) -> DeleteControlState:
        """
        Get the delete control UI state.

        Args:
            user_id: User identifier

        Returns:
            DeleteControlState with deletion options
        """
        # Generate confirmation phrase for security
        phrase_hash = hashlib.sha256(user_id.encode()).hexdigest()[:8]
        confirmation_phrase = f"DELETE-{phrase_hash.upper()}"

        return DeleteControlState(
            user_id=user_id,
            can_delete=True,
            deletable_categories=[
                "Profile Data",
                "Interaction History",
                "Expertise Metrics",
                "Level History",
            ],
            requires_confirmation=True,
            confirmation_phrase=confirmation_phrase,
            will_delete_account=False,  # Data deletion, not account
        )

    def confirm_deletion(
        self, request: DeletionConfirmationRequest
    ) -> DeletionConfirmationResult:
        """
        Process a deletion confirmation request.

        Args:
            request: Deletion confirmation request

        Returns:
            DeletionConfirmationResult with status
        """
        user = self._get_or_create_user(request.user_id)

        # Verify confirmation phrase
        expected_phrase = hashlib.sha256(request.user_id.encode()).hexdigest()[:8]
        expected_phrase = f"DELETE-{expected_phrase.upper()}"

        if request.confirmation_phrase != expected_phrase:
            return DeletionConfirmationResult(
                request_id=request.request_id,
                confirmed=False,
                message="Confirmation phrase does not match",
            )

        if not request.understood_irreversible:
            return DeletionConfirmationResult(
                request_id=request.request_id,
                confirmed=False,
                message="You must acknowledge that deletion is irreversible",
            )

        # Perform deletion
        categories_deleted = []
        for category in request.categories_to_delete:
            if category == "Interaction History":
                user.total_interactions = 0
                categories_deleted.append(category)
            elif category == "Expertise Metrics":
                user.expertise_score = 0.5
                user.expertise_confidence = 0.3
                categories_deleted.append(category)
            elif category == "Level History":
                user.level_history.clear()
                categories_deleted.append(category)
            elif category == "Profile Data":
                # Reset to defaults
                user.verbosity = VerbosityLevel.STANDARD
                user.interaction_style = ProfileInteractionStyle.CONVERSATIONAL
                categories_deleted.append(category)

        return DeletionConfirmationResult(
            request_id=request.request_id,
            confirmed=True,
            scheduled_at=self._now_iso(),
            categories_deleted=categories_deleted,
            message=f"Successfully deleted {len(categories_deleted)} data categories",
        )

    # ============================================
    # Accessibility Settings
    # ============================================

    def get_accessibility_settings(self, user_id: str) -> AccessibilitySettings:
        """
        Get user's accessibility settings.

        Args:
            user_id: User identifier

        Returns:
            AccessibilitySettings for the user
        """
        user = self._get_or_create_user(user_id)
        return user.accessibility

    def update_accessibility_settings(
        self, user_id: str, settings: AccessibilitySettings
    ) -> AccessibilitySettings:
        """
        Update user's accessibility settings.

        Args:
            user_id: User identifier
            settings: New accessibility settings

        Returns:
            Updated AccessibilitySettings
        """
        user = self._get_or_create_user(user_id)
        user.accessibility = settings
        return user.accessibility

    # ============================================
    # Simulation Helpers
    # ============================================

    def simulate_interaction(
        self, user_id: str, success: bool = True
    ) -> None:
        """
        Simulate a user interaction for testing.

        Args:
            user_id: User identifier
            success: Whether the interaction was successful
        """
        user = self._get_or_create_user(user_id)
        user.total_interactions += 1
        if success:
            total = user.total_interactions
            successes = int(user.success_rate * (total - 1)) + 1
            user.success_rate = successes / total
        else:
            total = user.total_interactions
            successes = int(user.success_rate * (total - 1))
            user.success_rate = successes / total

    def reset_user(self, user_id: str) -> None:
        """
        Reset all user data (for testing).

        Args:
            user_id: User identifier
        """
        if user_id in self._users:
            del self._users[user_id]
