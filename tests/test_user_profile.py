"""
Tests for User Profile Types (Issue #43)
Phase 2: Adaptive Interface Personalization - Task 2.1

Tests validate type construction and enum values for:
- Expertise levels and transitions
- User preferences and verbosity
- Interaction metrics
- Privacy and consent settings
"""

import pytest
from baml_client.types import (
    # Enums
    ExpertiseLevel,
    ProfileVerbosity,
    ProfileInteractionStyle,
    TransitionTrigger,
    LearningMode,
    FeedbackFrequency,
    ProfileUpdateType,
    # Classes
    InteractionMetrics,
    SessionMetrics,
    ExpertiseTransition,
    ExpertiseHistory,
    DomainExpertise,
    ProfilePreferences,
    ProfilingConsent,
    UserProfile,
    ProfileUpdate,
    ProfileSummary,
)


class TestExpertiseLevelEnum:
    """Test ExpertiseLevel enum values"""

    def test_novice_value(self):
        assert ExpertiseLevel.NOVICE.value == "NOVICE"

    def test_beginner_value(self):
        assert ExpertiseLevel.BEGINNER.value == "BEGINNER"

    def test_intermediate_value(self):
        assert ExpertiseLevel.INTERMEDIATE.value == "INTERMEDIATE"

    def test_advanced_value(self):
        assert ExpertiseLevel.ADVANCED.value == "ADVANCED"

    def test_expert_value(self):
        assert ExpertiseLevel.EXPERT.value == "EXPERT"

    def test_all_levels_count(self):
        """Verify all 5 expertise levels exist"""
        assert len(ExpertiseLevel) == 5


class TestProfileVerbosityEnum:
    """Test ProfileVerbosity enum values"""

    def test_minimal_value(self):
        assert ProfileVerbosity.MINIMAL.value == "MINIMAL"

    def test_standard_value(self):
        assert ProfileVerbosity.STANDARD.value == "STANDARD"

    def test_detailed_value(self):
        assert ProfileVerbosity.DETAILED.value == "DETAILED"

    def test_tutorial_value(self):
        assert ProfileVerbosity.TUTORIAL.value == "TUTORIAL"

    def test_all_verbosity_count(self):
        """Verify all 4 verbosity levels exist"""
        assert len(ProfileVerbosity) == 4


class TestProfileInteractionStyleEnum:
    """Test ProfileInteractionStyle enum values"""

    def test_conversational_value(self):
        assert ProfileInteractionStyle.CONVERSATIONAL.value == "CONVERSATIONAL"

    def test_professional_value(self):
        assert ProfileInteractionStyle.PROFESSIONAL.value == "PROFESSIONAL"

    def test_terse_value(self):
        assert ProfileInteractionStyle.TERSE.value == "TERSE"

    def test_educational_value(self):
        assert ProfileInteractionStyle.EDUCATIONAL.value == "EDUCATIONAL"

    def test_all_styles_count(self):
        """Verify all 4 interaction styles exist"""
        assert len(ProfileInteractionStyle) == 4


class TestTransitionTriggerEnum:
    """Test TransitionTrigger enum values"""

    def test_consecutive_success_value(self):
        assert TransitionTrigger.CONSECUTIVE_SUCCESS.value == "CONSECUTIVE_SUCCESS"

    def test_shortcut_adoption_value(self):
        assert TransitionTrigger.SHORTCUT_ADOPTION.value == "SHORTCUT_ADOPTION"

    def test_reduced_help_seeking_value(self):
        assert TransitionTrigger.REDUCED_HELP_SEEKING.value == "REDUCED_HELP_SEEKING"

    def test_consecutive_errors_value(self):
        assert TransitionTrigger.CONSECUTIVE_ERRORS.value == "CONSECUTIVE_ERRORS"

    def test_high_help_rate_value(self):
        assert TransitionTrigger.HIGH_HELP_RATE.value == "HIGH_HELP_RATE"

    def test_user_request_value(self):
        assert TransitionTrigger.USER_REQUEST.value == "USER_REQUEST"

    def test_time_decay_value(self):
        assert TransitionTrigger.TIME_DECAY.value == "TIME_DECAY"

    def test_domain_change_value(self):
        assert TransitionTrigger.DOMAIN_CHANGE.value == "DOMAIN_CHANGE"

    def test_all_triggers_count(self):
        """Verify all 8 transition triggers exist"""
        assert len(TransitionTrigger) == 8


class TestLearningModeEnum:
    """Test LearningMode enum values"""

    def test_active_value(self):
        assert LearningMode.ACTIVE.value == "ACTIVE"

    def test_passive_value(self):
        assert LearningMode.PASSIVE.value == "PASSIVE"

    def test_disabled_value(self):
        assert LearningMode.DISABLED.value == "DISABLED"

    def test_all_modes_count(self):
        """Verify all 3 learning modes exist"""
        assert len(LearningMode) == 3


class TestFeedbackFrequencyEnum:
    """Test FeedbackFrequency enum values"""

    def test_always_value(self):
        assert FeedbackFrequency.ALWAYS.value == "ALWAYS"

    def test_significant_value(self):
        assert FeedbackFrequency.SIGNIFICANT.value == "SIGNIFICANT"

    def test_never_value(self):
        assert FeedbackFrequency.NEVER.value == "NEVER"

    def test_all_frequencies_count(self):
        """Verify all 3 feedback frequencies exist"""
        assert len(FeedbackFrequency) == 3


class TestProfileUpdateTypeEnum:
    """Test ProfileUpdateType enum values"""

    def test_expertise_change_value(self):
        assert ProfileUpdateType.EXPERTISE_CHANGE.value == "EXPERTISE_CHANGE"

    def test_preference_change_value(self):
        assert ProfileUpdateType.PREFERENCE_CHANGE.value == "PREFERENCE_CHANGE"

    def test_metrics_update_value(self):
        assert ProfileUpdateType.METRICS_UPDATE.value == "METRICS_UPDATE"

    def test_consent_change_value(self):
        assert ProfileUpdateType.CONSENT_CHANGE.value == "CONSENT_CHANGE"

    def test_session_start_value(self):
        assert ProfileUpdateType.SESSION_START.value == "SESSION_START"

    def test_session_end_value(self):
        assert ProfileUpdateType.SESSION_END.value == "SESSION_END"

    def test_all_update_types_count(self):
        """Verify all 6 update types exist"""
        assert len(ProfileUpdateType) == 6


class TestInteractionMetricsConstruction:
    """Test InteractionMetrics class construction"""

    def test_minimal_metrics(self):
        """Test construction with required fields only"""
        metrics = InteractionMetrics(
            total_interactions=100,
            session_count=10,
            successful_intents=85,
            failed_intents=15,
            success_rate=0.85,
            avg_completion_time_ms=1500.0,
            shortcut_usage_rate=0.3,
            help_requests=5,
            disambiguation_requests=10,
            correction_rate=0.1,
            cancellation_rate=0.05,
        )
        assert metrics.total_interactions == 100
        assert metrics.session_count == 10
        assert metrics.success_rate == 0.85
        assert metrics.shortcut_usage_rate == 0.3

    def test_new_user_metrics(self):
        """Test metrics for a brand new user"""
        metrics = InteractionMetrics(
            total_interactions=0,
            session_count=0,
            successful_intents=0,
            failed_intents=0,
            success_rate=0.0,
            avg_completion_time_ms=0.0,
            shortcut_usage_rate=0.0,
            help_requests=0,
            disambiguation_requests=0,
            correction_rate=0.0,
            cancellation_rate=0.0,
        )
        assert metrics.total_interactions == 0
        assert metrics.success_rate == 0.0


class TestSessionMetricsConstruction:
    """Test SessionMetrics class construction"""

    def test_active_session(self):
        """Test construction for an active session"""
        session = SessionMetrics(
            session_id="session-123",
            session_start="2024-01-15T10:00:00Z",
            interactions_this_session=15,
            successes_this_session=12,
            errors_this_session=3,
            consecutive_errors=0,
            consecutive_successes=5,
            new_features_used=["shortcuts", "voice-commands"],
            shortcuts_used=["quick-save", "undo"],
            help_topics_accessed=["getting-started"],
        )
        assert session.session_id == "session-123"
        assert session.interactions_this_session == 15
        assert session.consecutive_successes == 5
        assert len(session.new_features_used) == 2

    def test_session_with_errors(self):
        """Test session with consecutive errors"""
        session = SessionMetrics(
            session_id="session-456",
            session_start="2024-01-15T14:00:00Z",
            interactions_this_session=10,
            successes_this_session=5,
            errors_this_session=5,
            consecutive_errors=3,
            consecutive_successes=0,
            new_features_used=[],
            shortcuts_used=[],
            help_topics_accessed=["troubleshooting", "faq"],
        )
        assert session.consecutive_errors == 3
        assert session.consecutive_successes == 0


class TestExpertiseTransitionConstruction:
    """Test ExpertiseTransition class construction"""

    def test_upgrade_transition(self):
        """Test expertise upgrade transition"""
        transition = ExpertiseTransition(
            transition_id="trans-001",
            previous_level=ExpertiseLevel.BEGINNER,
            new_level=ExpertiseLevel.INTERMEDIATE,
            trigger=TransitionTrigger.CONSECUTIVE_SUCCESS,
            timestamp="2024-01-15T12:00:00Z",
            confidence=0.85,
            evidence_summary="10 consecutive successful interactions",
            user_confirmed=False,
        )
        assert transition.previous_level == ExpertiseLevel.BEGINNER
        assert transition.new_level == ExpertiseLevel.INTERMEDIATE
        assert transition.trigger == TransitionTrigger.CONSECUTIVE_SUCCESS
        assert transition.confidence == 0.85

    def test_downgrade_transition(self):
        """Test expertise downgrade transition"""
        transition = ExpertiseTransition(
            transition_id="trans-002",
            previous_level=ExpertiseLevel.ADVANCED,
            new_level=ExpertiseLevel.INTERMEDIATE,
            trigger=TransitionTrigger.HIGH_HELP_RATE,
            timestamp="2024-01-15T15:00:00Z",
            confidence=0.7,
            evidence_summary=None,
            user_confirmed=True,
        )
        assert transition.previous_level == ExpertiseLevel.ADVANCED
        assert transition.new_level == ExpertiseLevel.INTERMEDIATE
        assert transition.trigger == TransitionTrigger.HIGH_HELP_RATE
        assert transition.user_confirmed is True


class TestExpertiseHistoryConstruction:
    """Test ExpertiseHistory class construction"""

    def test_empty_history(self):
        """Test history with no transitions"""
        history = ExpertiseHistory(
            transitions=[],
            current_level=ExpertiseLevel.INTERMEDIATE,
            level_tenure_days=0,
            stability_score=0.5,
        )
        assert len(history.transitions) == 0
        assert history.current_level == ExpertiseLevel.INTERMEDIATE

    def test_history_with_transitions(self):
        """Test history with multiple transitions"""
        transitions = [
            ExpertiseTransition(
                transition_id="trans-001",
                previous_level=ExpertiseLevel.NOVICE,
                new_level=ExpertiseLevel.BEGINNER,
                trigger=TransitionTrigger.CONSECUTIVE_SUCCESS,
                timestamp="2024-01-01T00:00:00Z",
                confidence=0.8,
                evidence_summary=None,
                user_confirmed=False,
            ),
            ExpertiseTransition(
                transition_id="trans-002",
                previous_level=ExpertiseLevel.BEGINNER,
                new_level=ExpertiseLevel.INTERMEDIATE,
                trigger=TransitionTrigger.SHORTCUT_ADOPTION,
                timestamp="2024-01-10T00:00:00Z",
                confidence=0.9,
                evidence_summary=None,
                user_confirmed=False,
            ),
        ]
        history = ExpertiseHistory(
            transitions=transitions,
            current_level=ExpertiseLevel.INTERMEDIATE,
            level_tenure_days=5,
            stability_score=0.8,
        )
        assert len(history.transitions) == 2
        assert history.level_tenure_days == 5
        assert history.stability_score == 0.8


class TestDomainExpertiseConstruction:
    """Test DomainExpertise class construction"""

    def test_familiar_domain(self):
        """Test expertise in a familiar domain"""
        domain = DomainExpertise(
            domain_id="task-management",
            domain_name="Task Management",
            expertise_level=ExpertiseLevel.ADVANCED,
            expertise_score=0.85,
            interaction_count=500,
            last_interaction="2024-01-15T10:00:00Z",
            key_concepts_known=["tasks", "projects", "deadlines", "priorities"],
        )
        assert domain.domain_id == "task-management"
        assert domain.expertise_level == ExpertiseLevel.ADVANCED
        assert len(domain.key_concepts_known) == 4

    def test_new_domain(self):
        """Test expertise in a new domain"""
        domain = DomainExpertise(
            domain_id="analytics",
            domain_name="Analytics",
            expertise_level=ExpertiseLevel.NOVICE,
            expertise_score=0.1,
            interaction_count=5,
            last_interaction=None,
            key_concepts_known=[],
        )
        assert domain.expertise_level == ExpertiseLevel.NOVICE
        assert domain.expertise_score == 0.1


class TestProfilePreferencesConstruction:
    """Test ProfilePreferences class construction"""

    def test_default_preferences(self):
        """Test default user preferences"""
        prefs = ProfilePreferences(
            preferred_verbosity=ProfileVerbosity.STANDARD,
            preferred_style=ProfileInteractionStyle.CONVERSATIONAL,
            learning_mode=LearningMode.ACTIVE,
            feedback_frequency=FeedbackFrequency.SIGNIFICANT,
            enable_shortcuts=True,
            enable_proactive_help=True,
            preferred_language="en",
            timezone="America/New_York",
        )
        assert prefs.preferred_verbosity == ProfileVerbosity.STANDARD
        assert prefs.preferred_style == ProfileInteractionStyle.CONVERSATIONAL
        assert prefs.learning_mode == LearningMode.ACTIVE

    def test_power_user_preferences(self):
        """Test power user preferences"""
        prefs = ProfilePreferences(
            preferred_verbosity=ProfileVerbosity.MINIMAL,
            preferred_style=ProfileInteractionStyle.TERSE,
            learning_mode=LearningMode.DISABLED,
            feedback_frequency=FeedbackFrequency.NEVER,
            enable_shortcuts=True,
            enable_proactive_help=False,
            preferred_language=None,
            timezone=None,
        )
        assert prefs.preferred_verbosity == ProfileVerbosity.MINIMAL
        assert prefs.preferred_style == ProfileInteractionStyle.TERSE
        assert prefs.enable_proactive_help is False


class TestProfilingConsentConstruction:
    """Test ProfilingConsent class construction"""

    def test_full_consent(self):
        """Test full profiling consent"""
        consent = ProfilingConsent(
            profiling_enabled=True,
            store_interaction_history=True,
            allow_expertise_inference=True,
            allow_preference_learning=True,
            data_retention_days=90,
            consent_timestamp="2024-01-01T00:00:00Z",
            consent_version="1.0",
        )
        assert consent.profiling_enabled is True
        assert consent.data_retention_days == 90

    def test_minimal_consent(self):
        """Test minimal/opt-out consent"""
        consent = ProfilingConsent(
            profiling_enabled=False,
            store_interaction_history=False,
            allow_expertise_inference=False,
            allow_preference_learning=False,
            data_retention_days=0,
            consent_timestamp="2024-01-01T00:00:00Z",
            consent_version="1.0",
        )
        assert consent.profiling_enabled is False
        assert consent.data_retention_days == 0


class TestUserProfileConstruction:
    """Test UserProfile class construction"""

    def test_minimal_profile(self):
        """Test minimal profile with required fields"""
        profile = UserProfile(
            user_id="user-123",
            profile_version="1.0.0",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-15T00:00:00Z",
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            expertise_score=0.5,
            expertise_confidence=0.3,
            expertise_history=None,
            domain_expertise=None,
            preferences=ProfilePreferences(
                preferred_verbosity=ProfileVerbosity.STANDARD,
                preferred_style=ProfileInteractionStyle.CONVERSATIONAL,
                learning_mode=LearningMode.ACTIVE,
                feedback_frequency=FeedbackFrequency.SIGNIFICANT,
                enable_shortcuts=True,
                enable_proactive_help=True,
                preferred_language=None,
                timezone=None,
            ),
            interaction_metrics=None,
            current_session=None,
            consent=ProfilingConsent(
                profiling_enabled=True,
                store_interaction_history=True,
                allow_expertise_inference=True,
                allow_preference_learning=True,
                data_retention_days=90,
                consent_timestamp="2024-01-01T00:00:00Z",
                consent_version="1.0",
            ),
        )
        assert profile.user_id == "user-123"
        assert profile.expertise_level == ExpertiseLevel.INTERMEDIATE
        assert profile.expertise_confidence == 0.3

    def test_full_profile(self):
        """Test full profile with all fields"""
        metrics = InteractionMetrics(
            total_interactions=100,
            session_count=10,
            successful_intents=85,
            failed_intents=15,
            success_rate=0.85,
            avg_completion_time_ms=1500.0,
            shortcut_usage_rate=0.3,
            help_requests=5,
            disambiguation_requests=10,
            correction_rate=0.1,
            cancellation_rate=0.05,
        )

        session = SessionMetrics(
            session_id="session-current",
            session_start="2024-01-15T10:00:00Z",
            interactions_this_session=15,
            successes_this_session=12,
            errors_this_session=3,
            consecutive_errors=0,
            consecutive_successes=5,
            new_features_used=[],
            shortcuts_used=["quick-save"],
            help_topics_accessed=[],
        )

        domain_expertise = [
            DomainExpertise(
                domain_id="task-management",
                domain_name="Task Management",
                expertise_level=ExpertiseLevel.ADVANCED,
                expertise_score=0.85,
                interaction_count=500,
                last_interaction="2024-01-15T10:00:00Z",
                key_concepts_known=["tasks", "projects"],
            ),
        ]

        profile = UserProfile(
            user_id="user-456",
            profile_version="1.0.0",
            created_at="2023-06-01T00:00:00Z",
            updated_at="2024-01-15T12:00:00Z",
            expertise_level=ExpertiseLevel.ADVANCED,
            expertise_score=0.8,
            expertise_confidence=0.9,
            expertise_history=None,
            domain_expertise=domain_expertise,
            preferences=ProfilePreferences(
                preferred_verbosity=ProfileVerbosity.MINIMAL,
                preferred_style=ProfileInteractionStyle.TERSE,
                learning_mode=LearningMode.ACTIVE,
                feedback_frequency=FeedbackFrequency.NEVER,
                enable_shortcuts=True,
                enable_proactive_help=False,
                preferred_language="en",
                timezone="America/Los_Angeles",
            ),
            interaction_metrics=metrics,
            current_session=session,
            consent=ProfilingConsent(
                profiling_enabled=True,
                store_interaction_history=True,
                allow_expertise_inference=True,
                allow_preference_learning=True,
                data_retention_days=365,
                consent_timestamp="2023-06-01T00:00:00Z",
                consent_version="1.0",
            ),
        )
        assert profile.user_id == "user-456"
        assert profile.expertise_level == ExpertiseLevel.ADVANCED
        assert profile.expertise_score == 0.8
        assert profile.interaction_metrics.total_interactions == 100
        assert len(profile.domain_expertise) == 1


class TestProfileUpdateConstruction:
    """Test ProfileUpdate class construction"""

    def test_expertise_update(self):
        """Test recording an expertise level change"""
        update = ProfileUpdate(
            update_id="update-001",
            update_type=ProfileUpdateType.EXPERTISE_CHANGE,
            timestamp="2024-01-15T12:00:00Z",
            field_path="expertise_level",
            previous_value="BEGINNER",
            new_value="INTERMEDIATE",
            reason="Consecutive successful interactions",
        )
        assert update.update_type == ProfileUpdateType.EXPERTISE_CHANGE
        assert update.field_path == "expertise_level"

    def test_preference_update(self):
        """Test recording a preference change"""
        update = ProfileUpdate(
            update_id="update-002",
            update_type=ProfileUpdateType.PREFERENCE_CHANGE,
            timestamp="2024-01-15T14:00:00Z",
            field_path="preferences.preferred_verbosity",
            previous_value=None,
            new_value="MINIMAL",
            reason="User manually changed setting",
        )
        assert update.update_type == ProfileUpdateType.PREFERENCE_CHANGE


class TestProfileSummaryConstruction:
    """Test ProfileSummary class construction"""

    def test_basic_summary(self):
        """Test creating a profile summary"""
        summary = ProfileSummary(
            user_id="user-123",
            expertise_level=ExpertiseLevel.INTERMEDIATE,
            preferred_verbosity=ProfileVerbosity.STANDARD,
            preferred_style=ProfileInteractionStyle.CONVERSATIONAL,
            profiling_enabled=True,
            session_count=10,
            success_rate=0.85,
        )
        assert summary.user_id == "user-123"
        assert summary.expertise_level == ExpertiseLevel.INTERMEDIATE
        assert summary.success_rate == 0.85


class TestEnumCompleteness:
    """Test that all enums have expected values accessible"""

    def test_all_expertise_levels_accessible(self):
        """Verify all expertise levels can be accessed"""
        levels = [
            ExpertiseLevel.NOVICE,
            ExpertiseLevel.BEGINNER,
            ExpertiseLevel.INTERMEDIATE,
            ExpertiseLevel.ADVANCED,
            ExpertiseLevel.EXPERT,
        ]
        assert len(levels) == 5

    def test_all_verbosity_levels_accessible(self):
        """Verify all verbosity levels can be accessed"""
        levels = [
            ProfileVerbosity.MINIMAL,
            ProfileVerbosity.STANDARD,
            ProfileVerbosity.DETAILED,
            ProfileVerbosity.TUTORIAL,
        ]
        assert len(levels) == 4

    def test_all_interaction_styles_accessible(self):
        """Verify all interaction styles can be accessed"""
        styles = [
            ProfileInteractionStyle.CONVERSATIONAL,
            ProfileInteractionStyle.PROFESSIONAL,
            ProfileInteractionStyle.TERSE,
            ProfileInteractionStyle.EDUCATIONAL,
        ]
        assert len(styles) == 4

    def test_all_transition_triggers_accessible(self):
        """Verify all transition triggers can be accessed"""
        triggers = [
            TransitionTrigger.CONSECUTIVE_SUCCESS,
            TransitionTrigger.SHORTCUT_ADOPTION,
            TransitionTrigger.REDUCED_HELP_SEEKING,
            TransitionTrigger.CONSECUTIVE_ERRORS,
            TransitionTrigger.HIGH_HELP_RATE,
            TransitionTrigger.USER_REQUEST,
            TransitionTrigger.TIME_DECAY,
            TransitionTrigger.DOMAIN_CHANGE,
        ]
        assert len(triggers) == 8
