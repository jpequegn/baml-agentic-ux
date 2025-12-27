"""Tests for Response Generation Types."""

import pytest
from baml_client.types import (
    # Response types
    GeneratedResponse,
    ResponseType,
    FollowUpAction,
    UrgencyLevel,
    VisualElement,
    VisualElementType,
    # Action result types
    ActionResult,
    ResultStatus,
    ResultMetadata,
    # User context types
    UserContext,
    UserResponsePreferences,
    VerbosityLevel,
    ExpertiseLevel,
    FormatPreference,
    AccessibilityNeeds,
    ResponseHistory,
    RecentResponse,
    # Style types
    ResponseStyle,
    ResponseTone,
    FormalityLevel,
    PersonalityTraits,
    BrandVoice,
    EmojiStyle,
    # Specialized types
    ProgressInfo,
    BatchResult,
    FailureReason,
    # LUI types for integration
    LUIComponent,
    LUIComponentType,
    InvocationPattern,
    FeedbackConfig,
)


class TestResponseTypeEnum:
    """Test ResponseType enum values."""

    def test_response_type_has_all_values(self):
        """Verify all expected response types exist."""
        expected = {
            "CONFIRMATION",
            "RESULT",
            "ERROR",
            "CLARIFICATION",
            "PROGRESS",
            "COMPLETION",
            "SUGGESTION",
            "ACKNOWLEDGMENT",
        }
        actual = {t.name for t in ResponseType}
        assert actual == expected


class TestResultStatusEnum:
    """Test ResultStatus enum values."""

    def test_result_status_has_all_values(self):
        """Verify all expected result statuses exist."""
        expected = {
            "SUCCESS",
            "PARTIAL",
            "FAILURE",
            "PENDING",
            "CANCELLED",
            "TIMEOUT",
            "REQUIRES_INPUT",
        }
        actual = {s.name for s in ResultStatus}
        assert actual == expected


class TestUrgencyLevelEnum:
    """Test UrgencyLevel enum values."""

    def test_urgency_level_values(self):
        """Verify all urgency levels exist."""
        expected = {"IMMEDIATE", "SOON", "OPTIONAL", "INFORMATIONAL"}
        actual = {u.name for u in UrgencyLevel}
        assert actual == expected


class TestVisualElementTypeEnum:
    """Test VisualElementType enum values."""

    def test_visual_element_type_values(self):
        """Verify all visual element types exist."""
        expected = {
            "TABLE",
            "LIST",
            "CODE_BLOCK",
            "LINK",
            "IMAGE_REF",
            "CARD",
            "CHART",
            "BADGE",
            "QUOTE",
        }
        actual = {t.name for t in VisualElementType}
        assert actual == expected


class TestResponseToneEnum:
    """Test ResponseTone enum values."""

    def test_response_tone_values(self):
        """Verify all response tones exist."""
        expected = {
            "PROFESSIONAL",
            "FRIENDLY",
            "EMPATHETIC",
            "ENTHUSIASTIC",
            "CALM",
            "DIRECT",
            "PLAYFUL",
        }
        actual = {t.name for t in ResponseTone}
        assert actual == expected


class TestFormalityLevelEnum:
    """Test FormalityLevel enum values."""

    def test_formality_level_values(self):
        """Verify all formality levels exist."""
        expected = {
            "VERY_FORMAL",
            "FORMAL",
            "NEUTRAL",
            "CASUAL",
            "VERY_CASUAL",
        }
        actual = {f.name for f in FormalityLevel}
        assert actual == expected


class TestVerbosityLevelEnum:
    """Test VerbosityLevel enum values."""

    def test_verbosity_level_values(self):
        """Verify all verbosity levels exist."""
        expected = {"MINIMAL", "CONCISE", "STANDARD", "DETAILED", "EXHAUSTIVE"}
        actual = {v.name for v in VerbosityLevel}
        assert actual == expected


class TestExpertiseLevelEnum:
    """Test ExpertiseLevel enum values."""

    def test_expertise_level_values(self):
        """Verify all expertise levels exist."""
        expected = {"NOVICE", "BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"}
        actual = {e.name for e in ExpertiseLevel}
        assert actual == expected


class TestEmojiStyleEnum:
    """Test EmojiStyle enum values."""

    def test_emoji_style_values(self):
        """Verify all emoji styles exist."""
        expected = {"NONE", "MINIMAL", "MODERATE", "EXPRESSIVE"}
        actual = {e.name for e in EmojiStyle}
        assert actual == expected


class TestFollowUpAction:
    """Test FollowUpAction type creation."""

    def test_create_required_follow_up(self):
        """Test creating a required follow-up action."""
        follow_up = FollowUpAction(
            suggested_action="Select a project to add the task to",
            action_phrase="add to project",
            is_required=True,
            component_id="select-project",
            urgency=UrgencyLevel.IMMEDIATE,
        )

        assert follow_up.is_required is True
        assert follow_up.component_id == "select-project"
        assert follow_up.urgency == UrgencyLevel.IMMEDIATE

    def test_create_optional_follow_up(self):
        """Test creating an optional follow-up action."""
        follow_up = FollowUpAction(
            suggested_action="Add more details to the task",
            action_phrase="add details",
            is_required=False,
            component_id=None,
            urgency=UrgencyLevel.OPTIONAL,
        )

        assert follow_up.is_required is False
        assert follow_up.component_id is None


class TestVisualElement:
    """Test VisualElement type creation."""

    def test_create_table_element(self):
        """Test creating a table visual element."""
        element = VisualElement(
            element_type=VisualElementType.TABLE,
            content="| Name | Status |\n|------|--------|\n| Task 1 | Done |",
            alt_text="Task status table",
            title="Task Summary",
            metadata={"columns": "2", "rows": "2"},
        )

        assert element.element_type == VisualElementType.TABLE
        assert element.title == "Task Summary"
        assert element.metadata is not None
        assert element.metadata["columns"] == "2"

    def test_create_list_element(self):
        """Test creating a list visual element."""
        element = VisualElement(
            element_type=VisualElementType.LIST,
            content="- Item 1\n- Item 2\n- Item 3",
            alt_text="List of items",
            title=None,
            metadata=None,
        )

        assert element.element_type == VisualElementType.LIST
        assert element.alt_text == "List of items"

    def test_create_code_block_element(self):
        """Test creating a code block visual element."""
        element = VisualElement(
            element_type=VisualElementType.CODE_BLOCK,
            content="def hello():\n    print('Hello, World!')",
            alt_text="Python function example",
            title=None,
            metadata={"language": "python"},
        )

        assert element.element_type == VisualElementType.CODE_BLOCK
        assert element.metadata is not None
        assert element.metadata["language"] == "python"


class TestActionResult:
    """Test ActionResult type creation."""

    def test_create_success_result(self):
        """Test creating a successful action result."""
        metadata = ResultMetadata(
            timestamp="2025-01-15T10:30:00Z",
            affected_count=1,
            warnings=None,
            debug_info=None,
            related_actions=None,
        )

        result = ActionResult(
            status=ResultStatus.SUCCESS,
            data="Task 'Review PR' created with ID task-123",
            error_message=None,
            metadata=metadata,
            affected_entities=["task-123"],
            execution_time_ms=150,
        )

        assert result.status == ResultStatus.SUCCESS
        assert result.data is not None
        assert result.error_message is None
        assert result.affected_entities is not None
        assert len(result.affected_entities) == 1

    def test_create_failure_result(self):
        """Test creating a failed action result."""
        result = ActionResult(
            status=ResultStatus.FAILURE,
            data=None,
            error_message="Permission denied: insufficient privileges",
            metadata=None,
            affected_entities=None,
            execution_time_ms=50,
        )

        assert result.status == ResultStatus.FAILURE
        assert result.data is None
        assert result.error_message is not None

    def test_create_partial_result(self):
        """Test creating a partial action result."""
        metadata = ResultMetadata(
            timestamp="2025-01-15T10:35:00Z",
            affected_count=8,
            warnings=["2 items skipped due to validation errors"],
            debug_info=None,
            related_actions=["fix-validation"],
        )

        result = ActionResult(
            status=ResultStatus.PARTIAL,
            data="8 of 10 items imported",
            error_message=None,
            metadata=metadata,
            affected_entities=None,
            execution_time_ms=2500,
        )

        assert result.status == ResultStatus.PARTIAL
        assert result.metadata is not None
        assert result.metadata.warnings is not None
        assert len(result.metadata.warnings) == 1


class TestUserContext:
    """Test UserContext type creation."""

    def test_create_minimal_user_context(self):
        """Test creating a minimal user context."""
        context = UserContext(
            user_id=None,
            preferences=None,
            interaction_count=0,
            expertise_level=ExpertiseLevel.NOVICE,
            accessibility_needs=None,
            locale=None,
            previous_responses=None,
        )

        assert context.interaction_count == 0
        assert context.expertise_level == ExpertiseLevel.NOVICE

    def test_create_full_user_context(self):
        """Test creating a complete user context."""
        preferences = UserResponsePreferences(
            preferred_verbosity=VerbosityLevel.DETAILED,
            include_explanations=True,
            include_examples=True,
            preferred_format=FormatPreference.STRUCTURED,
            use_emojis=False,
        )

        accessibility = AccessibilityNeeds(
            screen_reader_optimized=True,
            high_contrast=False,
            reduce_motion=True,
            simple_language=True,
            large_text=False,
        )

        recent = RecentResponse(
            response_type=ResponseType.CONFIRMATION,
            timestamp="2025-01-15T10:00:00Z",
            was_helpful=True,
        )

        history = ResponseHistory(
            recent_responses=[recent],
            common_follow_ups=["view details", "create another"],
            avoided_phrases=None,
        )

        context = UserContext(
            user_id="user-123",
            preferences=preferences,
            interaction_count=50,
            expertise_level=ExpertiseLevel.ADVANCED,
            accessibility_needs=accessibility,
            locale="en-US",
            previous_responses=history,
        )

        assert context.user_id == "user-123"
        assert context.preferences is not None
        assert context.preferences.preferred_verbosity == VerbosityLevel.DETAILED
        assert context.accessibility_needs is not None
        assert context.accessibility_needs.screen_reader_optimized is True
        assert context.previous_responses is not None
        assert len(context.previous_responses.recent_responses) == 1


class TestResponseStyle:
    """Test ResponseStyle type creation."""

    def test_create_minimal_style(self):
        """Test creating a minimal response style."""
        style = ResponseStyle(
            tone=ResponseTone.PROFESSIONAL,
            formality=FormalityLevel.NEUTRAL,
            personality=None,
            brand_voice=None,
        )

        assert style.tone == ResponseTone.PROFESSIONAL
        assert style.formality == FormalityLevel.NEUTRAL

    def test_create_style_with_personality(self):
        """Test creating a style with personality traits."""
        personality = PersonalityTraits(
            is_humorous=True,
            is_encouraging=True,
            is_concise=False,
            uses_analogies=True,
            is_proactive=True,
        )

        style = ResponseStyle(
            tone=ResponseTone.FRIENDLY,
            formality=FormalityLevel.CASUAL,
            personality=personality,
            brand_voice=None,
        )

        assert style.personality is not None
        assert style.personality.is_humorous is True
        assert style.personality.uses_analogies is True

    def test_create_style_with_brand_voice(self):
        """Test creating a style with brand voice."""
        brand = BrandVoice(
            brand_name="TechCorp",
            voice_description="Innovative, helpful, and forward-thinking",
            key_phrases=["Let's make it happen", "Innovation awaits"],
            avoided_phrases=["unfortunately", "we regret"],
            emoji_style=EmojiStyle.MINIMAL,
            signature_elements=["rocket emojis", "tech references"],
        )

        style = ResponseStyle(
            tone=ResponseTone.ENTHUSIASTIC,
            formality=FormalityLevel.CASUAL,
            personality=None,
            brand_voice=brand,
        )

        assert style.brand_voice is not None
        assert style.brand_voice.brand_name == "TechCorp"
        assert style.brand_voice.emoji_style == EmojiStyle.MINIMAL


class TestGeneratedResponse:
    """Test GeneratedResponse type creation."""

    def test_create_simple_response(self):
        """Test creating a simple response."""
        response = GeneratedResponse(
            response_text="Task 'Review PR' has been created successfully.",
            response_type=ResponseType.CONFIRMATION,
            follow_up=None,
            visual_elements=None,
            tone_applied="friendly",
            personalization_notes=None,
        )

        assert response.response_type == ResponseType.CONFIRMATION
        assert "Review PR" in response.response_text

    def test_create_response_with_follow_up(self):
        """Test creating a response with follow-up action."""
        follow_up = FollowUpAction(
            suggested_action="Add a due date to the task",
            action_phrase="set due date",
            is_required=False,
            component_id="set-due-date",
            urgency=UrgencyLevel.OPTIONAL,
        )

        response = GeneratedResponse(
            response_text="Task created! Would you like to set a due date?",
            response_type=ResponseType.CONFIRMATION,
            follow_up=follow_up,
            visual_elements=None,
            tone_applied=None,
            personalization_notes=None,
        )

        assert response.follow_up is not None
        assert response.follow_up.action_phrase == "set due date"

    def test_create_response_with_visual_elements(self):
        """Test creating a response with visual elements."""
        table = VisualElement(
            element_type=VisualElementType.TABLE,
            content="| Task | Status |\n|------|--------|\n| Review | Done |",
            alt_text="Task status summary",
            title=None,
            metadata=None,
        )

        badge = VisualElement(
            element_type=VisualElementType.BADGE,
            content="Completed",
            alt_text="Status: Completed",
            title=None,
            metadata={"color": "green"},
        )

        response = GeneratedResponse(
            response_text="Here are your completed tasks:",
            response_type=ResponseType.RESULT,
            follow_up=None,
            visual_elements=[table, badge],
            tone_applied="professional",
            personalization_notes=["Included table for user's structured format preference"],
        )

        assert response.visual_elements is not None
        assert len(response.visual_elements) == 2
        assert response.personalization_notes is not None


class TestProgressInfo:
    """Test ProgressInfo type creation."""

    def test_create_progress_info(self):
        """Test creating progress information."""
        progress = ProgressInfo(
            current_step=3,
            total_steps=10,
            percentage_complete=30.0,
            status_message="Processing file 3 of 10...",
            estimated_time_remaining="About 5 minutes",
            can_cancel=True,
        )

        assert progress.current_step == 3
        assert progress.total_steps == 10
        assert progress.percentage_complete == 30.0
        assert progress.can_cancel is True


class TestBatchResult:
    """Test BatchResult type creation."""

    def test_create_successful_batch_result(self):
        """Test creating a successful batch result."""
        result = BatchResult(
            total_count=100,
            success_count=100,
            failure_count=0,
            skipped_count=0,
            sample_successes=["item-1", "item-2", "item-3"],
            failure_reasons=None,
            overall_status=ResultStatus.SUCCESS,
        )

        assert result.overall_status == ResultStatus.SUCCESS
        assert result.failure_count == 0

    def test_create_partial_batch_result(self):
        """Test creating a partial batch result."""
        failure1 = FailureReason(
            reason="Invalid format",
            count=3,
            affected_ids=["item-10", "item-25", "item-50"],
        )
        failure2 = FailureReason(
            reason="Duplicate entry",
            count=2,
            affected_ids=["item-15", "item-30"],
        )

        result = BatchResult(
            total_count=100,
            success_count=95,
            failure_count=5,
            skipped_count=0,
            sample_successes=None,
            failure_reasons=[failure1, failure2],
            overall_status=ResultStatus.PARTIAL,
        )

        assert result.overall_status == ResultStatus.PARTIAL
        assert result.failure_reasons is not None
        assert len(result.failure_reasons) == 2
        assert result.failure_reasons[0].count == 3


class TestIntegrationWithLUIComponent:
    """Test integration with LUIComponent types."""

    def test_create_response_for_component(self):
        """Test creating a response for a LUI component action."""
        component = LUIComponent(
            component_id="create-task",
            component_type=LUIComponentType.ACTION,
            intent="Create a new task",
            invocation=InvocationPattern(
                primary_phrase="create task",
                alternate_phrases=["add task"],
                examples=["Create a task to review code"],
                context_requirements=None,
            ),
            parameters=[],
            feedback=FeedbackConfig(
                success_template="Task '{title}' created successfully",
                error_template="Failed to create task: {error}",
                progress_template=None,
                confirmation_required=False,
                confirmation_prompt=None,
            ),
            accessibility=None,
        )

        result = ActionResult(
            status=ResultStatus.SUCCESS,
            data="Task created with ID task-456",
            error_message=None,
            metadata=None,
            affected_entities=["task-456"],
            execution_time_ms=100,
        )

        # The response would be generated by the LLM using these inputs
        response = GeneratedResponse(
            response_text=component.feedback.success_template.replace("{title}", "Review Code"),
            response_type=ResponseType.CONFIRMATION,
            follow_up=FollowUpAction(
                suggested_action="View the task details",
                action_phrase="show task",
                is_required=False,
                component_id="view-task",
                urgency=UrgencyLevel.OPTIONAL,
            ),
            visual_elements=None,
            tone_applied=None,
            personalization_notes=None,
        )

        assert response.response_type == ResponseType.CONFIRMATION
        assert "Review Code" in response.response_text
        assert response.follow_up is not None
