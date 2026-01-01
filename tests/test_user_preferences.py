"""
Tests for User Preferences Manager

Tests all preference update flows, override persistence, data export,
deletion completeness, and accessibility features.

Issue #50 - Phase 2: Adaptive Interface Personalization
"""

from datetime import datetime, timezone

from src.lui_simulator.preferences import (
    AccessibilitySettings,
    DeletionConfirmationRequest,
    ExpertiseLevel,
    OverrideDuration,
    PreferencesManager,
    PreferenceType,
    PreferenceUpdateRequest,
    PreferenceUpdateStatus,
    ResetToAutoRequest,
    VerbosityLevel,
    VerbosityPreviewRequest,
)


class TestGetUserPreferencesUI:
    """Tests for getting user preferences UI state."""

    def test_get_preferences_ui_new_user(self) -> None:
        """Test getting preferences UI for a new user returns defaults."""
        manager = PreferencesManager()
        ui = manager.get_user_preferences_ui("new-user")

        assert ui.current_level == ExpertiseLevel.INTERMEDIATE
        assert ui.current_verbosity == VerbosityLevel.STANDARD
        assert ui.can_override is True
        assert ui.has_active_override is False
        assert ui.override_expires_at is None
        assert len(ui.available_levels) == 5
        assert len(ui.verbosity_options) == 5
        assert ui.adaptation_enabled is True
        assert ui.data_collection_enabled is True

    def test_get_preferences_ui_data_visibility(self) -> None:
        """Test data visibility options are set correctly."""
        manager = PreferencesManager()
        ui = manager.get_user_preferences_ui("test-user")

        assert ui.data_visibility.show_collected_metrics is True
        assert ui.data_visibility.show_expertise_score is True
        assert ui.data_visibility.show_level_history is True
        assert ui.data_visibility.allow_data_export is True
        assert ui.data_visibility.allow_data_deletion is True

    def test_preferences_ui_with_active_override(self) -> None:
        """Test preferences UI shows active override correctly."""
        manager = PreferencesManager()

        # Create an override
        request = PreferenceUpdateRequest(
            request_id="req-1",
            user_id="test-user",
            preference_type=PreferenceType.EXPERTISE_LEVEL_OVERRIDE,
            new_value="ADVANCED",
            requested_at=datetime.now(timezone.utc).isoformat(),
            override_duration=OverrideDuration.WEEK,
        )
        manager.update_preference(request)

        ui = manager.get_user_preferences_ui("test-user")
        assert ui.has_active_override is True
        assert ui.current_level == ExpertiseLevel.ADVANCED


class TestPreferenceUpdates:
    """Tests for updating user preferences."""

    def test_update_expertise_level_override(self) -> None:
        """Test updating expertise level via override."""
        manager = PreferencesManager()

        request = PreferenceUpdateRequest(
            request_id="req-1",
            user_id="test-user",
            preference_type=PreferenceType.EXPERTISE_LEVEL_OVERRIDE,
            new_value="EXPERT",
            requested_at=datetime.now(timezone.utc).isoformat(),
            override_duration=OverrideDuration.DAY,
        )

        result = manager.update_preference(request)

        assert result.status == PreferenceUpdateStatus.SUCCESS
        assert result.previous_value == "INTERMEDIATE"
        assert result.new_value == "EXPERT"
        assert result.expires_at is not None

    def test_update_expertise_invalid_level(self) -> None:
        """Test updating expertise level with invalid value fails."""
        manager = PreferencesManager()

        request = PreferenceUpdateRequest(
            request_id="req-1",
            user_id="test-user",
            preference_type=PreferenceType.EXPERTISE_LEVEL_OVERRIDE,
            new_value="SUPER_EXPERT",
            requested_at=datetime.now(timezone.utc).isoformat(),
        )

        result = manager.update_preference(request)
        assert result.status == PreferenceUpdateStatus.INVALID_VALUE

    def test_update_verbosity_preference(self) -> None:
        """Test updating verbosity preference."""
        manager = PreferencesManager()

        request = PreferenceUpdateRequest(
            request_id="req-1",
            user_id="test-user",
            preference_type=PreferenceType.VERBOSITY_PREFERENCE,
            new_value="DETAILED",
            requested_at=datetime.now(timezone.utc).isoformat(),
        )

        result = manager.update_preference(request)

        assert result.status == PreferenceUpdateStatus.SUCCESS
        assert result.previous_value == "STANDARD"
        assert result.new_value == "DETAILED"

    def test_update_verbosity_invalid(self) -> None:
        """Test updating verbosity with invalid value fails."""
        manager = PreferencesManager()

        request = PreferenceUpdateRequest(
            request_id="req-1",
            user_id="test-user",
            preference_type=PreferenceType.VERBOSITY_PREFERENCE,
            new_value="ULTRA_VERBOSE",
            requested_at=datetime.now(timezone.utc).isoformat(),
        )

        result = manager.update_preference(request)
        assert result.status == PreferenceUpdateStatus.INVALID_VALUE

    def test_update_adaptation_enabled(self) -> None:
        """Test enabling/disabling adaptation."""
        manager = PreferencesManager()

        # Disable
        request = PreferenceUpdateRequest(
            request_id="req-1",
            user_id="test-user",
            preference_type=PreferenceType.ADAPTATION_ENABLED,
            new_value="false",
            requested_at=datetime.now(timezone.utc).isoformat(),
        )

        result = manager.update_preference(request)
        assert result.status == PreferenceUpdateStatus.SUCCESS
        assert result.new_value == "false"

        ui = manager.get_user_preferences_ui("test-user")
        assert ui.adaptation_enabled is False

    def test_update_data_collection_consent(self) -> None:
        """Test updating data collection consent."""
        manager = PreferencesManager()

        request = PreferenceUpdateRequest(
            request_id="req-1",
            user_id="test-user",
            preference_type=PreferenceType.DATA_COLLECTION_CONSENT,
            new_value="false",
            requested_at=datetime.now(timezone.utc).isoformat(),
        )

        result = manager.update_preference(request)
        assert result.status == PreferenceUpdateStatus.SUCCESS

        ui = manager.get_user_preferences_ui("test-user")
        assert ui.data_collection_enabled is False
        assert ui.can_override is False  # Cannot override when collection disabled

    def test_update_interaction_style(self) -> None:
        """Test updating interaction style."""
        manager = PreferencesManager()

        request = PreferenceUpdateRequest(
            request_id="req-1",
            user_id="test-user",
            preference_type=PreferenceType.INTERACTION_STYLE,
            new_value="PROFESSIONAL",
            requested_at=datetime.now(timezone.utc).isoformat(),
        )

        result = manager.update_preference(request)
        assert result.status == PreferenceUpdateStatus.SUCCESS
        assert result.new_value == "PROFESSIONAL"

    def test_update_proactive_help(self) -> None:
        """Test updating proactive help setting."""
        manager = PreferencesManager()

        request = PreferenceUpdateRequest(
            request_id="req-1",
            user_id="test-user",
            preference_type=PreferenceType.PROACTIVE_HELP,
            new_value="false",
            requested_at=datetime.now(timezone.utc).isoformat(),
        )

        result = manager.update_preference(request)
        assert result.status == PreferenceUpdateStatus.SUCCESS
        assert result.new_value == "false"


class TestLevelOverrideControls:
    """Tests for level override functionality."""

    def test_create_level_override_session(self) -> None:
        """Test creating a session-duration override."""
        manager = PreferencesManager()

        override = manager.create_level_override(
            user_id="test-user",
            target_level=ExpertiseLevel.ADVANCED,
            duration=OverrideDuration.SESSION,
            reason="Testing advanced features",
        )

        assert override.is_active is True
        assert override.override_level == ExpertiseLevel.ADVANCED
        assert override.duration == OverrideDuration.SESSION
        assert override.expires_at is None  # Session has no fixed expiration
        assert override.reason == "Testing advanced features"

    def test_create_level_override_day(self) -> None:
        """Test creating a day-duration override."""
        manager = PreferencesManager()

        override = manager.create_level_override(
            user_id="test-user",
            target_level=ExpertiseLevel.NOVICE,
            duration=OverrideDuration.DAY,
        )

        assert override.is_active is True
        assert override.expires_at is not None
        expires = datetime.fromisoformat(override.expires_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        # Should expire in approximately 24 hours
        diff = (expires - now).total_seconds()
        assert 86300 < diff < 86500  # ~24 hours

    def test_create_level_override_week(self) -> None:
        """Test creating a week-duration override."""
        manager = PreferencesManager()

        override = manager.create_level_override(
            user_id="test-user",
            target_level=ExpertiseLevel.EXPERT,
            duration=OverrideDuration.WEEK,
        )

        assert override.expires_at is not None
        expires = datetime.fromisoformat(override.expires_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = (expires - now).total_seconds()
        assert 604000 < diff < 605000  # ~7 days

    def test_create_level_override_permanent(self) -> None:
        """Test creating a permanent override."""
        manager = PreferencesManager()

        override = manager.create_level_override(
            user_id="test-user",
            target_level=ExpertiseLevel.BEGINNER,
            duration=OverrideDuration.PERMANENT,
        )

        assert override.is_active is True
        assert override.expires_at is None

    def test_reset_to_automatic_with_override(self) -> None:
        """Test resetting to automatic when override exists."""
        manager = PreferencesManager()

        # Create override first
        request = PreferenceUpdateRequest(
            request_id="req-1",
            user_id="test-user",
            preference_type=PreferenceType.EXPERTISE_LEVEL_OVERRIDE,
            new_value="EXPERT",
            requested_at=datetime.now(timezone.utc).isoformat(),
            override_duration=OverrideDuration.PERMANENT,
        )
        manager.update_preference(request)

        # Verify override is active
        ui = manager.get_user_preferences_ui("test-user")
        assert ui.has_active_override is True
        assert ui.current_level == ExpertiseLevel.EXPERT

        # Reset to automatic
        reset_request = ResetToAutoRequest(
            request_id="reset-1",
            user_id="test-user",
            requested_at=datetime.now(timezone.utc).isoformat(),
            recalculate_immediately=True,
        )
        result = manager.reset_to_automatic(reset_request)

        assert result.success is True
        assert result.previous_override is not None
        assert result.new_level == ExpertiseLevel.INTERMEDIATE  # Original level

        # Verify override is gone
        ui = manager.get_user_preferences_ui("test-user")
        assert ui.has_active_override is False

    def test_reset_to_automatic_no_override(self) -> None:
        """Test resetting to automatic when no override exists."""
        manager = PreferencesManager()

        reset_request = ResetToAutoRequest(
            request_id="reset-1",
            user_id="test-user",
            requested_at=datetime.now(timezone.utc).isoformat(),
        )
        result = manager.reset_to_automatic(reset_request)

        assert result.success is True
        assert "already" in result.message.lower()

    def test_override_blocked_when_collection_disabled(self) -> None:
        """Test that override is blocked when data collection is disabled."""
        manager = PreferencesManager()

        # Disable data collection
        disable_request = PreferenceUpdateRequest(
            request_id="req-0",
            user_id="test-user",
            preference_type=PreferenceType.DATA_COLLECTION_CONSENT,
            new_value="false",
            requested_at=datetime.now(timezone.utc).isoformat(),
        )
        manager.update_preference(disable_request)

        # Try to create override
        override_request = PreferenceUpdateRequest(
            request_id="req-1",
            user_id="test-user",
            preference_type=PreferenceType.EXPERTISE_LEVEL_OVERRIDE,
            new_value="EXPERT",
            requested_at=datetime.now(timezone.utc).isoformat(),
        )
        result = manager.update_preference(override_request)

        assert result.status == PreferenceUpdateStatus.UNAUTHORIZED


class TestVerbosityPreview:
    """Tests for verbosity preview functionality."""

    def test_preview_minimal_verbosity(self) -> None:
        """Test preview of minimal verbosity."""
        manager = PreferencesManager()

        request = VerbosityPreviewRequest(
            user_id="test-user",
            verbosity_level=VerbosityLevel.MINIMAL,
        )
        result = manager.preview_verbosity(request)

        assert result.verbosity_level == VerbosityLevel.MINIMAL
        assert result.word_count < 20
        assert result.includes_examples is False
        assert result.includes_explanations is False

    def test_preview_exhaustive_verbosity(self) -> None:
        """Test preview of exhaustive verbosity."""
        manager = PreferencesManager()

        request = VerbosityPreviewRequest(
            user_id="test-user",
            verbosity_level=VerbosityLevel.EXHAUSTIVE,
        )
        result = manager.preview_verbosity(request)

        assert result.verbosity_level == VerbosityLevel.EXHAUSTIVE
        assert result.word_count > 100
        assert result.includes_examples is True
        assert result.includes_explanations is True

    def test_preview_with_custom_context(self) -> None:
        """Test preview with custom context."""
        manager = PreferencesManager()

        request = VerbosityPreviewRequest(
            user_id="test-user",
            verbosity_level=VerbosityLevel.STANDARD,
            sample_context="How do I export my data?",
        )
        result = manager.preview_verbosity(request)

        assert result.verbosity_level == VerbosityLevel.STANDARD
        assert len(result.sample_response) > 0

    def test_preview_all_verbosity_levels(self) -> None:
        """Test that all verbosity levels produce increasing word counts."""
        manager = PreferencesManager()

        word_counts = []
        for level in VerbosityLevel:
            request = VerbosityPreviewRequest(
                user_id="test-user",
                verbosity_level=level,
            )
            result = manager.preview_verbosity(request)
            word_counts.append(result.word_count)

        # Word counts should generally increase (allow some variance)
        assert word_counts[0] < word_counts[-1]  # MINIMAL < EXHAUSTIVE


class TestDataTransparencyPanel:
    """Tests for data transparency panel."""

    def test_get_transparency_panel_new_user(self) -> None:
        """Test transparency panel for new user."""
        manager = PreferencesManager()
        panel = manager.get_data_transparency_panel("new-user")

        assert panel.user_id == "new-user"
        assert panel.total_interactions == 0
        assert panel.session_count == 0
        assert panel.current_level == ExpertiseLevel.INTERMEDIATE
        assert len(panel.data_categories) == 4

    def test_transparency_panel_data_categories(self) -> None:
        """Test that data categories are correctly populated."""
        manager = PreferencesManager()
        panel = manager.get_data_transparency_panel("test-user")

        category_names = [c.category_name for c in panel.data_categories]
        assert "Profile Data" in category_names
        assert "Interaction History" in category_names
        assert "Expertise Metrics" in category_names
        assert "Session Data" in category_names

    def test_transparency_panel_with_interactions(self) -> None:
        """Test transparency panel reflects interactions."""
        manager = PreferencesManager()

        # Simulate some interactions
        for _ in range(5):
            manager.simulate_interaction("test-user", success=True)
        manager.simulate_interaction("test-user", success=False)

        panel = manager.get_data_transparency_panel("test-user")

        assert panel.total_interactions == 6
        assert 0.8 < panel.success_rate < 0.9  # 5/6 success

    def test_transparency_panel_level_history(self) -> None:
        """Test that level history is included in panel."""
        manager = PreferencesManager()

        # Create some level changes
        for level in [ExpertiseLevel.ADVANCED, ExpertiseLevel.EXPERT]:
            request = PreferenceUpdateRequest(
                request_id=f"req-{level.value}",
                user_id="test-user",
                preference_type=PreferenceType.EXPERTISE_LEVEL_OVERRIDE,
                new_value=level.value,
                requested_at=datetime.now(timezone.utc).isoformat(),
            )
            manager.update_preference(request)

        panel = manager.get_data_transparency_panel("test-user")

        assert len(panel.level_history) == 2
        assert panel.level_history[-1].to_level == ExpertiseLevel.EXPERT


class TestExportControls:
    """Tests for data export controls."""

    def test_get_export_control_state(self) -> None:
        """Test getting export control state."""
        manager = PreferencesManager()
        state = manager.get_export_control_state("test-user")

        assert state.user_id == "test-user"
        assert state.can_export is True
        assert "JSON" in state.available_formats
        assert "CSV" in state.available_formats
        assert len(state.exportable_categories) > 0

    def test_export_disabled_when_collection_disabled(self) -> None:
        """Test export is limited when data collection is disabled."""
        manager = PreferencesManager()

        # Disable data collection
        request = PreferenceUpdateRequest(
            request_id="req-1",
            user_id="test-user",
            preference_type=PreferenceType.DATA_COLLECTION_CONSENT,
            new_value="false",
            requested_at=datetime.now(timezone.utc).isoformat(),
        )
        manager.update_preference(request)

        state = manager.get_export_control_state("test-user")

        assert state.can_export is False
        assert "Profile Data" in state.exportable_categories
        assert "Interaction History" not in state.exportable_categories


class TestDeleteControls:
    """Tests for data deletion controls."""

    def test_get_delete_control_state(self) -> None:
        """Test getting delete control state."""
        manager = PreferencesManager()
        state = manager.get_delete_control_state("test-user")

        assert state.user_id == "test-user"
        assert state.can_delete is True
        assert state.requires_confirmation is True
        assert state.confirmation_phrase is not None
        assert state.confirmation_phrase.startswith("DELETE-")

    def test_confirm_deletion_success(self) -> None:
        """Test successful deletion confirmation."""
        manager = PreferencesManager()

        # Get the confirmation phrase
        state = manager.get_delete_control_state("test-user")

        request = DeletionConfirmationRequest(
            request_id="del-1",
            user_id="test-user",
            categories_to_delete=["Interaction History", "Expertise Metrics"],
            requested_at=datetime.now(timezone.utc).isoformat(),
            understood_irreversible=True,
            confirmation_phrase=state.confirmation_phrase,
        )

        result = manager.confirm_deletion(request)

        assert result.confirmed is True
        assert "Interaction History" in (result.categories_deleted or [])
        assert "Expertise Metrics" in (result.categories_deleted or [])

    def test_confirm_deletion_wrong_phrase(self) -> None:
        """Test deletion fails with wrong confirmation phrase."""
        manager = PreferencesManager()

        request = DeletionConfirmationRequest(
            request_id="del-1",
            user_id="test-user",
            categories_to_delete=["Interaction History"],
            requested_at=datetime.now(timezone.utc).isoformat(),
            understood_irreversible=True,
            confirmation_phrase="WRONG-PHRASE",
        )

        result = manager.confirm_deletion(request)

        assert result.confirmed is False
        assert "does not match" in result.message

    def test_confirm_deletion_not_understood(self) -> None:
        """Test deletion fails when irreversibility not acknowledged."""
        manager = PreferencesManager()
        state = manager.get_delete_control_state("test-user")

        request = DeletionConfirmationRequest(
            request_id="del-1",
            user_id="test-user",
            categories_to_delete=["Interaction History"],
            requested_at=datetime.now(timezone.utc).isoformat(),
            understood_irreversible=False,
            confirmation_phrase=state.confirmation_phrase,
        )

        result = manager.confirm_deletion(request)

        assert result.confirmed is False
        assert "irreversible" in result.message.lower()

    def test_deletion_clears_data(self) -> None:
        """Test that deletion actually clears the data."""
        manager = PreferencesManager()

        # Add some data first
        for _ in range(10):
            manager.simulate_interaction("test-user", success=True)

        # Verify data exists
        panel = manager.get_data_transparency_panel("test-user")
        assert panel.total_interactions == 10

        # Delete
        state = manager.get_delete_control_state("test-user")
        request = DeletionConfirmationRequest(
            request_id="del-1",
            user_id="test-user",
            categories_to_delete=["Interaction History"],
            requested_at=datetime.now(timezone.utc).isoformat(),
            understood_irreversible=True,
            confirmation_phrase=state.confirmation_phrase,
        )
        manager.confirm_deletion(request)

        # Verify data is gone
        panel = manager.get_data_transparency_panel("test-user")
        assert panel.total_interactions == 0


class TestAccessibilitySettings:
    """Tests for accessibility settings."""

    def test_get_default_accessibility_settings(self) -> None:
        """Test getting default accessibility settings."""
        manager = PreferencesManager()
        settings = manager.get_accessibility_settings("test-user")

        assert settings.keyboard_navigation is True
        assert settings.screen_reader_compatible is True
        assert settings.high_contrast is False
        assert settings.large_text is False
        assert settings.reduce_motion is False
        assert settings.aria_labels_enabled is True

    def test_update_accessibility_settings(self) -> None:
        """Test updating accessibility settings."""
        manager = PreferencesManager()

        new_settings = AccessibilitySettings(
            keyboard_navigation=True,
            screen_reader_compatible=True,
            high_contrast=True,
            large_text=True,
            reduce_motion=True,
            aria_labels_enabled=True,
        )

        result = manager.update_accessibility_settings("test-user", new_settings)

        assert result.high_contrast is True
        assert result.large_text is True
        assert result.reduce_motion is True

        # Verify persistence
        retrieved = manager.get_accessibility_settings("test-user")
        assert retrieved.high_contrast is True


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_preference_workflow(self) -> None:
        """Test complete preference management workflow."""
        manager = PreferencesManager()
        user_id = "workflow-user"

        # 1. Get initial UI state
        ui = manager.get_user_preferences_ui(user_id)
        assert ui.current_level == ExpertiseLevel.INTERMEDIATE

        # 2. Override expertise level
        override_request = PreferenceUpdateRequest(
            request_id="req-1",
            user_id=user_id,
            preference_type=PreferenceType.EXPERTISE_LEVEL_OVERRIDE,
            new_value="ADVANCED",
            requested_at=datetime.now(timezone.utc).isoformat(),
            override_duration=OverrideDuration.DAY,
        )
        result = manager.update_preference(override_request)
        assert result.status == PreferenceUpdateStatus.SUCCESS

        # 3. Change verbosity
        verbosity_request = PreferenceUpdateRequest(
            request_id="req-2",
            user_id=user_id,
            preference_type=PreferenceType.VERBOSITY_PREFERENCE,
            new_value="DETAILED",
            requested_at=datetime.now(timezone.utc).isoformat(),
        )
        result = manager.update_preference(verbosity_request)
        assert result.status == PreferenceUpdateStatus.SUCCESS

        # 4. Preview verbosity
        preview = manager.preview_verbosity(
            VerbosityPreviewRequest(
                user_id=user_id,
                verbosity_level=VerbosityLevel.DETAILED,
            )
        )
        assert preview.includes_explanations is True

        # 5. Check transparency panel
        panel = manager.get_data_transparency_panel(user_id)
        assert panel.current_level == ExpertiseLevel.ADVANCED
        assert len(panel.level_history) == 1

        # 6. Reset to automatic
        reset_result = manager.reset_to_automatic(
            ResetToAutoRequest(
                request_id="reset-1",
                user_id=user_id,
                requested_at=datetime.now(timezone.utc).isoformat(),
            )
        )
        assert reset_result.success is True

        # 7. Verify final state
        ui = manager.get_user_preferences_ui(user_id)
        assert ui.has_active_override is False
        assert ui.current_level == ExpertiseLevel.INTERMEDIATE

    def test_gdpr_workflow(self) -> None:
        """Test GDPR compliance workflow (export/delete)."""
        manager = PreferencesManager()
        user_id = "gdpr-user"

        # Simulate activity
        for i in range(20):
            manager.simulate_interaction(user_id, success=i % 3 != 0)

        # Check export state
        export_state = manager.get_export_control_state(user_id)
        assert export_state.can_export is True
        assert len(export_state.exportable_categories) >= 3

        # Check delete state
        delete_state = manager.get_delete_control_state(user_id)
        assert delete_state.can_delete is True
        assert delete_state.requires_confirmation is True

        # Perform deletion
        result = manager.confirm_deletion(
            DeletionConfirmationRequest(
                request_id="del-gdpr",
                user_id=user_id,
                categories_to_delete=["Interaction History", "Expertise Metrics"],
                requested_at=datetime.now(timezone.utc).isoformat(),
                understood_irreversible=True,
                confirmation_phrase=delete_state.confirmation_phrase,
            )
        )
        assert result.confirmed is True

        # Verify deletion
        panel = manager.get_data_transparency_panel(user_id)
        assert panel.total_interactions == 0

    def test_reset_user(self) -> None:
        """Test resetting user data."""
        manager = PreferencesManager()
        user_id = "reset-user"

        # Add data
        manager.simulate_interaction(user_id, success=True)
        panel = manager.get_data_transparency_panel(user_id)
        assert panel.total_interactions == 1

        # Reset
        manager.reset_user(user_id)

        # New user should have defaults
        panel = manager.get_data_transparency_panel(user_id)
        assert panel.total_interactions == 0
