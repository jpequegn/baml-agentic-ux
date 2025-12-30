"""Tests for multi-modal response generation types."""

from __future__ import annotations

from baml_client.types import (
    # Enums - existing
    ResponseTone,
    FormalityLevel,
    ValidationSeverity,
    Modality,
    ReadingLevel,
    # Enums - new
    EmpathyLevel,
    EmojiUsage,
    ResponseLength,
    DetailLevel,
    BandwidthConstraint,
    QuickReplyLayout,
    # Classes - new
    ResponsePersona,
    PersonalityConfig,
    BrandGuidelines,
    LanguagePreferences,
    GenerationContext,
    UserFeedbackSummary,
    PerformanceHints,
    GenerationResult,
    GenerationMetadata,
    QualityMetrics,
    AlternativeResponse,
    QuickReply,
    QuickReplySet,
    ResponseValidation,
    ValidationIssue,
    # Classes - existing (for integration)
    MultiModalResponse,
    TextResponse,
    AccessibilityMeta,
    AriaLiveType,
    CognitiveLoad,
    TextFormat,
)


# ============================================
# Enum Tests
# ============================================


class TestEmpathyLevelEnum:
    """Tests for EmpathyLevel enum."""

    def test_all_values_exist(self) -> None:
        """Test all empathy level values are defined."""
        assert EmpathyLevel.LOW.value == "LOW"
        assert EmpathyLevel.MODERATE.value == "MODERATE"
        assert EmpathyLevel.HIGH.value == "HIGH"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(EmpathyLevel) == 3


class TestEmojiUsageEnum:
    """Tests for EmojiUsage enum."""

    def test_all_values_exist(self) -> None:
        """Test all emoji usage values are defined."""
        assert EmojiUsage.NONE.value == "NONE"
        assert EmojiUsage.MINIMAL.value == "MINIMAL"
        assert EmojiUsage.MODERATE.value == "MODERATE"
        assert EmojiUsage.EXPRESSIVE.value == "EXPRESSIVE"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(EmojiUsage) == 4


class TestResponseLengthEnum:
    """Tests for ResponseLength enum."""

    def test_all_values_exist(self) -> None:
        """Test all response length values are defined."""
        assert ResponseLength.VERY_SHORT.value == "VERY_SHORT"
        assert ResponseLength.SHORT.value == "SHORT"
        assert ResponseLength.MEDIUM.value == "MEDIUM"
        assert ResponseLength.LONG.value == "LONG"
        assert ResponseLength.DETAILED.value == "DETAILED"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(ResponseLength) == 5


class TestDetailLevelEnum:
    """Tests for DetailLevel enum."""

    def test_all_values_exist(self) -> None:
        """Test all detail level values are defined."""
        assert DetailLevel.OVERVIEW.value == "OVERVIEW"
        assert DetailLevel.STANDARD.value == "STANDARD"
        assert DetailLevel.COMPREHENSIVE.value == "COMPREHENSIVE"
        assert DetailLevel.EXHAUSTIVE.value == "EXHAUSTIVE"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(DetailLevel) == 4


class TestBandwidthConstraintEnum:
    """Tests for BandwidthConstraint enum."""

    def test_all_values_exist(self) -> None:
        """Test all bandwidth constraint values are defined."""
        assert BandwidthConstraint.NONE.value == "NONE"
        assert BandwidthConstraint.LOW.value == "LOW"
        assert BandwidthConstraint.VERY_LOW.value == "VERY_LOW"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(BandwidthConstraint) == 3


class TestQuickReplyLayoutEnum:
    """Tests for QuickReplyLayout enum."""

    def test_all_values_exist(self) -> None:
        """Test all quick reply layout values are defined."""
        assert QuickReplyLayout.HORIZONTAL.value == "HORIZONTAL"
        assert QuickReplyLayout.VERTICAL.value == "VERTICAL"
        assert QuickReplyLayout.GRID.value == "GRID"
        assert QuickReplyLayout.CHIPS.value == "CHIPS"

    def test_enum_count(self) -> None:
        """Test correct number of values."""
        assert len(QuickReplyLayout) == 4


# ============================================
# PersonalityConfig Tests
# ============================================


class TestPersonalityConfig:
    """Tests for PersonalityConfig class."""

    def test_create_basic_personality(self) -> None:
        """Test creating a basic personality config."""
        config = PersonalityConfig(
            is_humorous=False,
            is_encouraging=True,
            is_concise=True,
            uses_analogies=False,
            is_proactive=True,
        )

        assert config.is_humorous is False
        assert config.is_encouraging is True
        assert config.is_concise is True
        assert config.uses_analogies is False
        assert config.is_proactive is True
        assert config.empathy_level is None

    def test_create_with_empathy(self) -> None:
        """Test creating personality config with empathy level."""
        config = PersonalityConfig(
            is_humorous=True,
            is_encouraging=True,
            is_concise=False,
            uses_analogies=True,
            is_proactive=False,
            empathy_level=EmpathyLevel.HIGH,
        )

        assert config.is_humorous is True
        assert config.empathy_level == EmpathyLevel.HIGH


# ============================================
# BrandGuidelines Tests
# ============================================


class TestBrandGuidelines:
    """Tests for BrandGuidelines class."""

    def test_create_basic_guidelines(self) -> None:
        """Test creating basic brand guidelines."""
        guidelines = BrandGuidelines(
            brand_name="Acme Corp",
            voice_description="Professional yet approachable",
            emoji_usage=EmojiUsage.MINIMAL,
        )

        assert guidelines.brand_name == "Acme Corp"
        assert guidelines.voice_description == "Professional yet approachable"
        assert guidelines.emoji_usage == EmojiUsage.MINIMAL
        assert guidelines.key_phrases is None

    def test_create_full_guidelines(self) -> None:
        """Test creating complete brand guidelines."""
        guidelines = BrandGuidelines(
            brand_name="FunCorp",
            voice_description="Playful and energetic",
            key_phrases=["Let's go!", "You got this!"],
            avoided_phrases=["Unfortunately", "We regret"],
            emoji_usage=EmojiUsage.EXPRESSIVE,
            signature_elements=["sparkle effect", "celebration animation"],
        )

        assert guidelines.key_phrases is not None
        assert guidelines.avoided_phrases is not None
        assert len(guidelines.key_phrases) == 2
        assert len(guidelines.avoided_phrases) == 2
        assert guidelines.emoji_usage == EmojiUsage.EXPRESSIVE


# ============================================
# LanguagePreferences Tests
# ============================================


class TestLanguagePreferences:
    """Tests for LanguagePreferences class."""

    def test_create_basic_preferences(self) -> None:
        """Test creating basic language preferences."""
        prefs = LanguagePreferences(
            primary_language="en-US",
        )

        assert prefs.primary_language == "en-US"
        assert prefs.reading_level is None
        assert prefs.use_contractions is None

    def test_create_full_preferences(self) -> None:
        """Test creating complete language preferences."""
        prefs = LanguagePreferences(
            primary_language="en-GB",
            reading_level=ReadingLevel.HIGH_SCHOOL,
            use_contractions=True,
            date_format="DD/MM/YYYY",
            number_format="1.000,00",
            currency_symbol="£",
        )

        assert prefs.primary_language == "en-GB"
        assert prefs.reading_level == ReadingLevel.HIGH_SCHOOL
        assert prefs.use_contractions is True
        assert prefs.currency_symbol == "£"


# ============================================
# ResponsePersona Tests
# ============================================


class TestResponsePersona:
    """Tests for ResponsePersona class."""

    def test_create_basic_persona(self) -> None:
        """Test creating a basic response persona."""
        persona = ResponsePersona(
            name="Helpful Assistant",
            tone=ResponseTone.FRIENDLY,
            formality=FormalityLevel.CASUAL,
        )

        assert persona.name == "Helpful Assistant"
        assert persona.tone == ResponseTone.FRIENDLY
        assert persona.formality == FormalityLevel.CASUAL
        assert persona.description is None
        assert persona.personality is None

    def test_create_full_persona(self) -> None:
        """Test creating a complete response persona."""
        personality = PersonalityConfig(
            is_humorous=False,
            is_encouraging=True,
            is_concise=True,
            uses_analogies=False,
            is_proactive=True,
            empathy_level=EmpathyLevel.MODERATE,
        )

        brand = BrandGuidelines(
            brand_name="TechCorp",
            voice_description="Modern and efficient",
            emoji_usage=EmojiUsage.MINIMAL,
        )

        lang = LanguagePreferences(
            primary_language="en-US",
            use_contractions=True,
        )

        persona = ResponsePersona(
            name="Corporate Assistant",
            description="Professional assistant for enterprise users",
            tone=ResponseTone.PROFESSIONAL,
            formality=FormalityLevel.FORMAL,
            personality=personality,
            brand_guidelines=brand,
            language_preferences=lang,
        )

        assert persona.name == "Corporate Assistant"
        assert persona.description is not None
        assert persona.personality is not None
        assert persona.brand_guidelines is not None
        assert persona.language_preferences is not None


# ============================================
# UserFeedbackSummary Tests
# ============================================


class TestUserFeedbackSummary:
    """Tests for UserFeedbackSummary class."""

    def test_create_empty_summary(self) -> None:
        """Test creating an empty feedback summary."""
        summary = UserFeedbackSummary()

        assert summary.preferred_length is None
        assert summary.preferred_detail is None

    def test_create_full_summary(self) -> None:
        """Test creating a complete feedback summary."""
        summary = UserFeedbackSummary(
            preferred_length=ResponseLength.SHORT,
            preferred_detail=DetailLevel.STANDARD,
            positive_reactions=["concise answers", "helpful examples"],
            negative_reactions=["too verbose", "technical jargon"],
        )

        assert summary.preferred_length == ResponseLength.SHORT
        assert summary.preferred_detail == DetailLevel.STANDARD
        assert summary.positive_reactions is not None
        assert summary.negative_reactions is not None
        assert len(summary.positive_reactions) == 2
        assert len(summary.negative_reactions) == 2


# ============================================
# PerformanceHints Tests
# ============================================


class TestPerformanceHints:
    """Tests for PerformanceHints class."""

    def test_create_basic_hints(self) -> None:
        """Test creating basic performance hints."""
        hints = PerformanceHints()

        assert hints.max_response_time_ms is None
        assert hints.bandwidth_constraint is None

    def test_create_constrained_hints(self) -> None:
        """Test creating constrained performance hints."""
        hints = PerformanceHints(
            max_response_time_ms=500,
            bandwidth_constraint=BandwidthConstraint.LOW,
            prefer_cached=True,
        )

        assert hints.max_response_time_ms == 500
        assert hints.bandwidth_constraint == BandwidthConstraint.LOW
        assert hints.prefer_cached is True


# ============================================
# GenerationContext Tests
# ============================================


class TestGenerationContext:
    """Tests for GenerationContext class."""

    def test_create_empty_context(self) -> None:
        """Test creating an empty generation context."""
        context = GenerationContext()

        assert context.session_id is None
        assert context.turn_count is None

    def test_create_full_context(self) -> None:
        """Test creating a complete generation context."""
        feedback = UserFeedbackSummary(
            preferred_length=ResponseLength.MEDIUM,
        )

        hints = PerformanceHints(
            max_response_time_ms=1000,
        )

        context = GenerationContext(
            session_id="session_123",
            turn_count=5,
            last_response_modality=Modality.TEXT,
            user_feedback_history=feedback,
            performance_hints=hints,
        )

        assert context.session_id == "session_123"
        assert context.turn_count == 5
        assert context.last_response_modality == Modality.TEXT
        assert context.user_feedback_history is not None
        assert context.performance_hints is not None


# ============================================
# QualityMetrics Tests
# ============================================


class TestQualityMetrics:
    """Tests for QualityMetrics class."""

    def test_create_basic_metrics(self) -> None:
        """Test creating basic quality metrics."""
        metrics = QualityMetrics(
            clarity_score=0.9,
            relevance_score=0.85,
            completeness_score=0.8,
            accessibility_score=0.95,
        )

        assert metrics.clarity_score == 0.9
        assert metrics.relevance_score == 0.85
        assert metrics.completeness_score == 0.8
        assert metrics.accessibility_score == 0.95
        assert metrics.brand_alignment_score is None

    def test_create_full_metrics(self) -> None:
        """Test creating complete quality metrics."""
        metrics = QualityMetrics(
            clarity_score=0.92,
            relevance_score=0.88,
            completeness_score=0.85,
            accessibility_score=0.97,
            brand_alignment_score=0.9,
        )

        assert metrics.brand_alignment_score == 0.9


# ============================================
# GenerationMetadata Tests
# ============================================


class TestGenerationMetadata:
    """Tests for GenerationMetadata class."""

    def test_create_basic_metadata(self) -> None:
        """Test creating basic generation metadata."""
        metadata = GenerationMetadata(
            generation_time_ms=150,
            modality_selection_rationale="Voice selected for confirmation message",
            persona_applied="Helpful Assistant",
        )

        assert metadata.generation_time_ms == 150
        assert "Voice" in metadata.modality_selection_rationale
        assert metadata.persona_applied == "Helpful Assistant"
        assert metadata.accessibility_adaptations is None

    def test_create_full_metadata(self) -> None:
        """Test creating complete generation metadata."""
        metadata = GenerationMetadata(
            generation_time_ms=250,
            modality_selection_rationale="Text selected due to loud environment",
            persona_applied="Corporate Assistant",
            accessibility_adaptations=["High contrast mode", "Screen reader optimized"],
            content_warnings=["Contains technical terms"],
        )

        assert metadata.accessibility_adaptations is not None
        assert metadata.content_warnings is not None
        assert len(metadata.accessibility_adaptations) == 2
        assert len(metadata.content_warnings) == 1


# ============================================
# QuickReply Tests
# ============================================


class TestQuickReply:
    """Tests for QuickReply class."""

    def test_create_basic_reply(self) -> None:
        """Test creating a basic quick reply."""
        reply = QuickReply(
            id="reply_1",
            label="Show details",
            value="show_details",
            is_primary=True,
        )

        assert reply.id == "reply_1"
        assert reply.label == "Show details"
        assert reply.value == "show_details"
        assert reply.is_primary is True
        assert reply.icon is None

    def test_create_with_icon(self) -> None:
        """Test creating quick reply with icon."""
        reply = QuickReply(
            id="reply_2",
            label="Cancel",
            value="cancel_action",
            icon="close",
            is_primary=False,
        )

        assert reply.icon == "close"
        assert reply.is_primary is False


# ============================================
# QuickReplySet Tests
# ============================================


class TestQuickReplySet:
    """Tests for QuickReplySet class."""

    def test_create_reply_set(self) -> None:
        """Test creating a quick reply set."""
        replies = [
            QuickReply(id="1", label="Yes", value="yes", is_primary=True),
            QuickReply(id="2", label="No", value="no", is_primary=False),
            QuickReply(id="3", label="Cancel", value="cancel", is_primary=False),
        ]

        reply_set = QuickReplySet(
            replies=replies,
            layout=QuickReplyLayout.HORIZONTAL,
        )

        assert len(reply_set.replies) == 3
        assert reply_set.layout == QuickReplyLayout.HORIZONTAL
        assert reply_set.max_visible is None

    def test_create_with_max_visible(self) -> None:
        """Test creating reply set with max visible limit."""
        replies = [
            QuickReply(id=str(i), label=f"Option {i}", value=f"opt_{i}", is_primary=i == 1)
            for i in range(1, 6)
        ]

        reply_set = QuickReplySet(
            replies=replies,
            max_visible=3,
            layout=QuickReplyLayout.CHIPS,
        )

        assert len(reply_set.replies) == 5
        assert reply_set.max_visible == 3


# ============================================
# ValidationIssue Tests
# ============================================


class TestValidationIssue:
    """Tests for ValidationIssue class."""

    def test_create_error_issue(self) -> None:
        """Test creating an error validation issue."""
        issue = ValidationIssue(
            severity=ValidationSeverity.ERROR,
            category="modality",
            message="Primary modality not available on device",
        )

        assert issue.severity == ValidationSeverity.ERROR
        assert issue.category == "modality"
        assert issue.field is None

    def test_create_warning_with_recommendation(self) -> None:
        """Test creating a warning with recommendation."""
        issue = ValidationIssue(
            severity=ValidationSeverity.WARNING,
            category="accessibility",
            message="Voice response exceeds 30 seconds",
            field="voice.text",
            recommendation="Shorten the response or split into parts",
        )

        assert issue.severity == ValidationSeverity.WARNING
        assert issue.field == "voice.text"
        assert issue.recommendation is not None


# ============================================
# ResponseValidation Tests
# ============================================


class TestResponseValidation:
    """Tests for ResponseValidation class."""

    def test_create_valid_response(self) -> None:
        """Test creating a validation result for valid response."""
        validation = ResponseValidation(
            is_valid=True,
            is_optimal=True,
            issues=[],
            accessibility_compliant=True,
        )

        assert validation.is_valid is True
        assert validation.is_optimal is True
        assert len(validation.issues) == 0
        assert validation.accessibility_compliant is True

    def test_create_with_issues(self) -> None:
        """Test creating a validation with issues."""
        issues = [
            ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="voice",
                message="Voice duration may exceed recommendation",
            ),
            ValidationIssue(
                severity=ValidationSeverity.INFO,
                category="actions",
                message="Consider adding undo action",
            ),
        ]

        validation = ResponseValidation(
            is_valid=True,
            is_optimal=False,
            issues=issues,
            suggestions=["Shorten voice content", "Add undo button"],
            accessibility_compliant=True,
            estimated_voice_duration_seconds=35.5,
        )

        assert validation.is_valid is True
        assert validation.is_optimal is False
        assert len(validation.issues) == 2
        assert validation.suggestions is not None
        assert len(validation.suggestions) == 2
        assert validation.estimated_voice_duration_seconds == 35.5


# ============================================
# GenerationResult Tests
# ============================================


class TestGenerationResult:
    """Tests for GenerationResult class."""

    def test_create_basic_result(self) -> None:
        """Test creating a basic generation result."""
        response = MultiModalResponse(
            response_id="resp_001",
            primary_modality=Modality.TEXT,
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.LOW,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        metadata = GenerationMetadata(
            generation_time_ms=120,
            modality_selection_rationale="Text for error message",
            persona_applied="Default",
        )

        result = GenerationResult(
            response=response,
            generation_metadata=metadata,
        )

        assert result.response.response_id == "resp_001"
        assert result.generation_metadata.generation_time_ms == 120
        assert result.quality_metrics is None
        assert result.alternatives is None

    def test_create_full_result(self) -> None:
        """Test creating a complete generation result with alternatives."""
        response = MultiModalResponse(
            response_id="resp_002",
            primary_modality=Modality.VOICE,
            text=TextResponse(
                content="Task created: Review PR #123",
                format=TextFormat.PLAIN,
            ),
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.MINIMAL,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        metadata = GenerationMetadata(
            generation_time_ms=180,
            modality_selection_rationale="Voice for confirmation",
            persona_applied="Helpful Assistant",
        )

        metrics = QualityMetrics(
            clarity_score=0.95,
            relevance_score=0.92,
            completeness_score=0.88,
            accessibility_score=0.97,
        )

        # Alternative response
        alt_response = MultiModalResponse(
            response_id="resp_002_alt",
            primary_modality=Modality.TEXT,
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.MINIMAL,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        alternative = AlternativeResponse(
            response=alt_response,
            rationale="Text-only for noisy environments",
            use_case="When voice output is not appropriate",
        )

        result = GenerationResult(
            response=response,
            generation_metadata=metadata,
            quality_metrics=metrics,
            alternatives=[alternative],
        )

        assert result.quality_metrics is not None
        assert result.quality_metrics.clarity_score == 0.95
        assert result.alternatives is not None
        assert len(result.alternatives) == 1
        assert result.alternatives[0].rationale == "Text-only for noisy environments"


# ============================================
# Integration Tests
# ============================================


class TestMultiModalGenerationIntegration:
    """Integration tests for multi-modal generation types."""

    def test_full_generation_workflow(self) -> None:
        """Test complete generation workflow with all types."""
        # 1. Create persona
        persona = ResponsePersona(
            name="Customer Support",
            description="Helpful support persona",
            tone=ResponseTone.EMPATHETIC,
            formality=FormalityLevel.CASUAL,
            personality=PersonalityConfig(
                is_humorous=False,
                is_encouraging=True,
                is_concise=True,
                uses_analogies=False,
                is_proactive=True,
                empathy_level=EmpathyLevel.HIGH,
            ),
        )

        # 2. Create generation context
        context = GenerationContext(
            session_id="support_session_001",
            turn_count=3,
            last_response_modality=Modality.TEXT,
            user_feedback_history=UserFeedbackSummary(
                preferred_length=ResponseLength.SHORT,
            ),
        )

        # 3. Create response
        response = MultiModalResponse(
            response_id="support_resp_001",
            primary_modality=Modality.TEXT,
            text=TextResponse(
                content="I understand that's frustrating. Let me help you resolve this.",
                format=TextFormat.PLAIN,
            ),
            accessibility=AccessibilityMeta(
                aria_live=AriaLiveType.POLITE,
                cognitive_load=CognitiveLoad.LOW,
                supports_screen_reader=True,
                supports_keyboard_nav=True,
                high_contrast_available=True,
                reduced_motion_safe=True,
            ),
        )

        # 4. Create generation metadata
        metadata = GenerationMetadata(
            generation_time_ms=95,
            modality_selection_rationale="Text for support conversation continuity",
            persona_applied=persona.name,
            accessibility_adaptations=["Screen reader compatible"],
        )

        # 5. Create quality metrics
        metrics = QualityMetrics(
            clarity_score=0.92,
            relevance_score=0.88,
            completeness_score=0.85,
            accessibility_score=0.96,
        )

        # 6. Create result
        result = GenerationResult(
            response=response,
            generation_metadata=metadata,
            quality_metrics=metrics,
        )

        # Assertions
        assert persona.personality is not None
        assert persona.personality.empathy_level == EmpathyLevel.HIGH
        assert context.user_feedback_history is not None
        assert context.user_feedback_history.preferred_length == ResponseLength.SHORT
        assert result.response.text is not None
        assert result.response.text.content.startswith("I understand")
        assert result.generation_metadata.persona_applied == "Customer Support"
        assert result.quality_metrics is not None
        assert result.quality_metrics.accessibility_score > 0.9

    def test_quick_replies_for_confirmation(self) -> None:
        """Test quick replies for confirmation response."""
        replies = QuickReplySet(
            replies=[
                QuickReply(
                    id="details",
                    label="Show details",
                    value="show_task_details",
                    icon="info",
                    is_primary=True,
                ),
                QuickReply(
                    id="create",
                    label="Create another",
                    value="create_new_task",
                    icon="add",
                    is_primary=False,
                ),
                QuickReply(
                    id="undo",
                    label="Undo",
                    value="undo_creation",
                    icon="undo",
                    is_primary=False,
                ),
            ],
            max_visible=3,
            layout=QuickReplyLayout.CHIPS,
        )

        assert len(replies.replies) == 3
        assert replies.replies[0].is_primary is True
        assert replies.layout == QuickReplyLayout.CHIPS

    def test_validation_for_response(self) -> None:
        """Test validation of a generated response."""
        issues = [
            ValidationIssue(
                severity=ValidationSeverity.INFO,
                category="optimization",
                message="Response could be more concise",
                recommendation="Consider shortening by 20%",
            ),
        ]

        validation = ResponseValidation(
            is_valid=True,
            is_optimal=False,
            issues=issues,
            suggestions=["Reduce response length"],
            accessibility_compliant=True,
            estimated_voice_duration_seconds=22.5,
        )

        assert validation.is_valid is True
        assert validation.is_optimal is False
        assert len(validation.issues) == 1
        assert validation.issues[0].severity == ValidationSeverity.INFO


class TestTypeImports:
    """Tests to verify all generation types are importable."""

    def test_all_new_enums_importable(self) -> None:
        """Test all new enum imports work."""
        assert EmpathyLevel is not None
        assert EmojiUsage is not None
        assert ResponseLength is not None
        assert DetailLevel is not None
        assert BandwidthConstraint is not None
        assert QuickReplyLayout is not None

    def test_all_new_classes_importable(self) -> None:
        """Test all new class imports work."""
        assert ResponsePersona is not None
        assert PersonalityConfig is not None
        assert BrandGuidelines is not None
        assert LanguagePreferences is not None
        assert GenerationContext is not None
        assert UserFeedbackSummary is not None
        assert PerformanceHints is not None
        assert GenerationResult is not None
        assert GenerationMetadata is not None
        assert QualityMetrics is not None
        assert AlternativeResponse is not None
        assert QuickReply is not None
        assert QuickReplySet is not None
        assert ResponseValidation is not None
        assert ValidationIssue is not None

    def test_existing_types_available(self) -> None:
        """Test existing types are still available."""
        assert ResponseTone is not None
        assert FormalityLevel is not None
        assert ValidationSeverity is not None
        assert Modality is not None
