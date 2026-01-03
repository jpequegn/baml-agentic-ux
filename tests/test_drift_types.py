"""Tests for intent drift type definitions.

Issue #78 - Task 5.1: Drift Analysis Types
Part of #28 - Phase 5: Intent Drift Detection
"""

import pytest

from src.intent_drift import (
    # Enums
    AbstractionLevel,
    CoherenceTrend,
    ConfidenceTier,
    DriftResponseTone,
    DriftType,
    GracefulResponseType,
    RecommendedAction,
    TemporalReferenceType,
    # Core Classes
    DriftAnalysis,
    RedirectSuggestion,
    # Semantic Analysis
    EntityMention,
    NearestIntent,
    SemanticAnalysis,
    TemporalReference,
    # Confidence
    ConfidenceAssessment,
    ConfidenceFactorScore,
    # Response
    DriftResponseTemplate,
    GracefulResponse,
    Redirect,
    # Context
    CoherenceAnalysis,
    ConversationDriftContext,
    DriftConversationTurn,
    DriftEvent,
    # Config
    DriftDetectionConfig,
    DriftDetectionResult,
    # Request/Response
    BatchDriftAnalysis,
    DriftAggregateStats,
    DriftAnalysisRequest,
)


# ============================================
# Enum Tests
# ============================================


class TestDriftType:
    """Tests for DriftType enum."""

    def test_all_drift_types_exist(self):
        """Test all expected drift types exist."""
        expected = [
            "NONE",
            "SCOPE_EXPANSION",
            "DOMAIN_SHIFT",
            "ABSTRACTION_CLIMB",
            "PERSONALIZATION",
            "TEMPORAL_DRIFT",
            "AMBIGUOUS",
        ]
        for name in expected:
            assert hasattr(DriftType, name)

    def test_drift_type_values(self):
        """Test drift type values are lowercase strings."""
        assert DriftType.NONE.value == "none"
        assert DriftType.SCOPE_EXPANSION.value == "scope_expansion"
        assert DriftType.DOMAIN_SHIFT.value == "domain_shift"

    def test_drift_type_count(self):
        """Test correct number of drift types."""
        assert len(DriftType) == 7


class TestAbstractionLevel:
    """Tests for AbstractionLevel enum."""

    def test_all_levels_exist(self):
        """Test all abstraction levels exist."""
        expected = ["CONCRETE", "MODERATE", "ABSTRACT", "PHILOSOPHICAL"]
        for name in expected:
            assert hasattr(AbstractionLevel, name)

    def test_abstraction_level_count(self):
        """Test correct number of levels."""
        assert len(AbstractionLevel) == 4


class TestConfidenceTier:
    """Tests for ConfidenceTier enum."""

    def test_all_tiers_exist(self):
        """Test all confidence tiers exist."""
        expected = ["VERY_HIGH", "HIGH", "MEDIUM", "LOW", "VERY_LOW"]
        for name in expected:
            assert hasattr(ConfidenceTier, name)

    def test_confidence_tier_count(self):
        """Test correct number of tiers."""
        assert len(ConfidenceTier) == 5


class TestRecommendedAction:
    """Tests for RecommendedAction enum."""

    def test_all_actions_exist(self):
        """Test all recommended actions exist."""
        expected = [
            "PROCEED",
            "PROCEED_WITH_CAVEAT",
            "CLARIFY",
            "REDIRECT",
            "ESCALATE",
            "DECLINE",
        ]
        for name in expected:
            assert hasattr(RecommendedAction, name)


class TestGracefulResponseType:
    """Tests for GracefulResponseType enum."""

    def test_all_response_types_exist(self):
        """Test all graceful response types exist."""
        expected = [
            "CLARIFICATION",
            "PARTIAL_HELP",
            "REDIRECT",
            "BOUNDARY_STATEMENT",
            "ESCALATION",
            "ACKNOWLEDGMENT",
        ]
        for name in expected:
            assert hasattr(GracefulResponseType, name)


class TestDriftResponseTone:
    """Tests for DriftResponseTone enum."""

    def test_all_tones_exist(self):
        """Test all tones exist."""
        expected = ["EMPATHETIC", "HELPFUL", "PROFESSIONAL", "APOLOGETIC", "ENCOURAGING"]
        for name in expected:
            assert hasattr(DriftResponseTone, name)


class TestCoherenceTrend:
    """Tests for CoherenceTrend enum."""

    def test_all_trends_exist(self):
        """Test all coherence trends exist."""
        expected = ["IMPROVING", "STABLE", "DEGRADING", "VOLATILE"]
        for name in expected:
            assert hasattr(CoherenceTrend, name)


class TestTemporalReferenceType:
    """Tests for TemporalReferenceType enum."""

    def test_all_temporal_types_exist(self):
        """Test all temporal reference types exist."""
        expected = [
            "PAST_ABSOLUTE",
            "PAST_RELATIVE",
            "PRESENT",
            "FUTURE_RELATIVE",
            "FUTURE_ABSOLUTE",
            "HYPOTHETICAL",
        ]
        for name in expected:
            assert hasattr(TemporalReferenceType, name)


# ============================================
# Core Data Class Tests
# ============================================


class TestRedirectSuggestion:
    """Tests for RedirectSuggestion dataclass."""

    def test_create_redirect_suggestion(self):
        """Test creating a redirect suggestion."""
        suggestion = RedirectSuggestion(
            target_intent="create_task",
            similarity_score=0.85,
            redirect_reason="Similar to task creation",
            transition_phrase="Would you like to create a task instead?",
            confidence=0.9,
        )
        assert suggestion.target_intent == "create_task"
        assert suggestion.similarity_score == 0.85
        assert suggestion.confidence == 0.9

    def test_similarity_score_validation(self):
        """Test similarity score must be between 0 and 1."""
        with pytest.raises(ValueError):
            RedirectSuggestion(
                target_intent="test",
                similarity_score=1.5,
                redirect_reason="test",
                transition_phrase="test",
                confidence=0.5,
            )

    def test_confidence_validation(self):
        """Test confidence must be between 0 and 1."""
        with pytest.raises(ValueError):
            RedirectSuggestion(
                target_intent="test",
                similarity_score=0.5,
                redirect_reason="test",
                transition_phrase="test",
                confidence=-0.1,
            )


class TestDriftAnalysis:
    """Tests for DriftAnalysis dataclass."""

    def test_create_drift_analysis(self):
        """Test creating a drift analysis."""
        analysis = DriftAnalysis(
            current_input="What's the weather like?",
            drift_score=0.8,
            drift_type=DriftType.DOMAIN_SHIFT,
            confidence=0.95,
            semantic_distance=0.75,
            graceful_response="I can't check weather, but I can help with tasks.",
        )
        assert analysis.drift_score == 0.8
        assert analysis.drift_type == DriftType.DOMAIN_SHIFT
        assert analysis.has_drift is True

    def test_no_drift_analysis(self):
        """Test analysis with no drift."""
        analysis = DriftAnalysis(
            current_input="Create a new task",
            drift_score=0.1,
            drift_type=DriftType.NONE,
            confidence=0.95,
            semantic_distance=0.1,
            graceful_response="",
        )
        assert analysis.has_drift is False

    def test_has_drift_property(self):
        """Test has_drift property."""
        drift = DriftAnalysis(
            current_input="test",
            drift_score=0.5,
            drift_type=DriftType.SCOPE_EXPANSION,
            confidence=0.8,
            semantic_distance=0.5,
            graceful_response="test",
        )
        assert drift.has_drift is True

        no_drift = DriftAnalysis(
            current_input="test",
            drift_score=0.1,
            drift_type=DriftType.NONE,
            confidence=0.9,
            semantic_distance=0.1,
            graceful_response="",
        )
        assert no_drift.has_drift is False

    def test_needs_clarification_for_ambiguous(self):
        """Test needs_clarification for ambiguous drift."""
        analysis = DriftAnalysis(
            current_input="test",
            drift_score=0.5,
            drift_type=DriftType.AMBIGUOUS,
            confidence=0.9,
            semantic_distance=0.5,
            graceful_response="test",
        )
        assert analysis.needs_clarification is True

    def test_needs_clarification_for_low_confidence(self):
        """Test needs_clarification for low confidence."""
        analysis = DriftAnalysis(
            current_input="test",
            drift_score=0.3,
            drift_type=DriftType.NONE,
            confidence=0.4,
            semantic_distance=0.3,
            graceful_response="",
        )
        assert analysis.needs_clarification is True

    def test_has_redirects_property(self):
        """Test has_redirects property."""
        analysis = DriftAnalysis(
            current_input="test",
            drift_score=0.5,
            drift_type=DriftType.DOMAIN_SHIFT,
            confidence=0.8,
            semantic_distance=0.5,
            graceful_response="test",
            suggested_redirects=[
                RedirectSuggestion(
                    target_intent="task",
                    similarity_score=0.7,
                    redirect_reason="related",
                    transition_phrase="try this",
                    confidence=0.8,
                )
            ],
        )
        assert analysis.has_redirects is True

    def test_drift_score_validation(self):
        """Test drift score validation."""
        with pytest.raises(ValueError):
            DriftAnalysis(
                current_input="test",
                drift_score=1.5,
                drift_type=DriftType.NONE,
                confidence=0.8,
                semantic_distance=0.5,
                graceful_response="",
            )


# ============================================
# Semantic Analysis Tests
# ============================================


class TestNearestIntent:
    """Tests for NearestIntent dataclass."""

    def test_create_nearest_intent(self):
        """Test creating a nearest intent."""
        intent = NearestIntent(
            intent_name="create_task",
            similarity=0.85,
            capability_id="cap_123",
            requires_clarification=False,
        )
        assert intent.intent_name == "create_task"
        assert intent.similarity == 0.85

    def test_similarity_validation(self):
        """Test similarity validation."""
        with pytest.raises(ValueError):
            NearestIntent(intent_name="test", similarity=1.5)


class TestTemporalReference:
    """Tests for TemporalReference dataclass."""

    def test_create_temporal_reference(self):
        """Test creating a temporal reference."""
        ref = TemporalReference(
            expression="tomorrow",
            reference_type=TemporalReferenceType.FUTURE_RELATIVE,
            is_within_knowledge=True,
            drift_risk=0.1,
        )
        assert ref.expression == "tomorrow"
        assert ref.is_within_knowledge is True

    def test_drift_risk_validation(self):
        """Test drift risk validation."""
        with pytest.raises(ValueError):
            TemporalReference(
                expression="test",
                reference_type=TemporalReferenceType.PRESENT,
                is_within_knowledge=True,
                drift_risk=1.5,
            )


class TestEntityMention:
    """Tests for EntityMention dataclass."""

    def test_create_entity_mention(self):
        """Test creating an entity mention."""
        entity = EntityMention(
            text="John Smith",
            entity_type="person",
            start_offset=0,
            end_offset=10,
            requires_personalization=True,
        )
        assert entity.text == "John Smith"
        assert entity.requires_personalization is True


class TestSemanticAnalysis:
    """Tests for SemanticAnalysis dataclass."""

    def test_create_semantic_analysis(self):
        """Test creating a semantic analysis."""
        analysis = SemanticAnalysis(
            input_text="Create a task for tomorrow",
            abstraction_level=AbstractionLevel.CONCRETE,
            nearest_intents=[
                NearestIntent(intent_name="create_task", similarity=0.9)
            ],
            temporal_references=[
                TemporalReference(
                    expression="tomorrow",
                    reference_type=TemporalReferenceType.FUTURE_RELATIVE,
                    is_within_knowledge=True,
                    drift_risk=0.1,
                )
            ],
        )
        assert analysis.input_text == "Create a task for tomorrow"
        assert len(analysis.nearest_intents) == 1

    def test_has_temporal_drift_risk(self):
        """Test has_temporal_drift_risk property."""
        analysis = SemanticAnalysis(
            input_text="test",
            abstraction_level=AbstractionLevel.CONCRETE,
            temporal_references=[
                TemporalReference(
                    expression="2050",
                    reference_type=TemporalReferenceType.FUTURE_ABSOLUTE,
                    is_within_knowledge=False,
                    drift_risk=0.9,
                )
            ],
        )
        assert analysis.has_temporal_drift_risk is True

    def test_requires_personalization(self):
        """Test requires_personalization property."""
        analysis = SemanticAnalysis(
            input_text="test",
            abstraction_level=AbstractionLevel.CONCRETE,
            entity_mentions=[
                EntityMention(
                    text="my account",
                    entity_type="account",
                    start_offset=0,
                    end_offset=10,
                    requires_personalization=True,
                )
            ],
        )
        assert analysis.requires_personalization is True


# ============================================
# Confidence Assessment Tests
# ============================================


class TestConfidenceFactorScore:
    """Tests for ConfidenceFactorScore dataclass."""

    def test_create_factor_score(self):
        """Test creating a factor score."""
        score = ConfidenceFactorScore(
            factor_name="semantic_match",
            score=0.85,
            weight=0.3,
            explanation="High semantic similarity",
        )
        assert score.factor_name == "semantic_match"
        assert score.weighted_score == pytest.approx(0.255)

    def test_score_validation(self):
        """Test score validation."""
        with pytest.raises(ValueError):
            ConfidenceFactorScore(factor_name="test", score=1.5, weight=0.5)

    def test_weight_validation(self):
        """Test weight validation."""
        with pytest.raises(ValueError):
            ConfidenceFactorScore(factor_name="test", score=0.5, weight=1.5)


class TestConfidenceAssessment:
    """Tests for ConfidenceAssessment dataclass."""

    def test_create_assessment(self):
        """Test creating a confidence assessment."""
        assessment = ConfidenceAssessment(
            overall_confidence=0.85,
            confidence_tier=ConfidenceTier.HIGH,
            recommended_action=RecommendedAction.PROCEED_WITH_CAVEAT,
            explanation="High confidence based on semantic match",
        )
        assert assessment.overall_confidence == 0.85
        assert assessment.confidence_tier == ConfidenceTier.HIGH

    def test_from_score_very_high(self):
        """Test from_score with very high confidence."""
        assessment = ConfidenceAssessment.from_score(0.97)
        assert assessment.confidence_tier == ConfidenceTier.VERY_HIGH
        assert assessment.recommended_action == RecommendedAction.PROCEED

    def test_from_score_high(self):
        """Test from_score with high confidence."""
        assessment = ConfidenceAssessment.from_score(0.85)
        assert assessment.confidence_tier == ConfidenceTier.HIGH
        assert assessment.recommended_action == RecommendedAction.PROCEED_WITH_CAVEAT

    def test_from_score_medium(self):
        """Test from_score with medium confidence."""
        assessment = ConfidenceAssessment.from_score(0.65)
        assert assessment.confidence_tier == ConfidenceTier.MEDIUM
        assert assessment.recommended_action == RecommendedAction.CLARIFY

    def test_from_score_low(self):
        """Test from_score with low confidence."""
        assessment = ConfidenceAssessment.from_score(0.45)
        assert assessment.confidence_tier == ConfidenceTier.LOW
        assert assessment.recommended_action == RecommendedAction.REDIRECT

    def test_from_score_very_low(self):
        """Test from_score with very low confidence."""
        assessment = ConfidenceAssessment.from_score(0.25)
        assert assessment.confidence_tier == ConfidenceTier.VERY_LOW
        assert assessment.recommended_action == RecommendedAction.DECLINE

    def test_confidence_validation(self):
        """Test confidence validation."""
        with pytest.raises(ValueError):
            ConfidenceAssessment(
                overall_confidence=1.5,
                confidence_tier=ConfidenceTier.HIGH,
                recommended_action=RecommendedAction.PROCEED,
                explanation="test",
            )


# ============================================
# Graceful Response Tests
# ============================================


class TestRedirect:
    """Tests for Redirect dataclass."""

    def test_create_redirect(self):
        """Test creating a redirect."""
        redirect = Redirect(
            capability_name="Task Manager",
            description="Create and manage tasks",
            relevance_score=0.8,
            action_phrase="Would you like to create a task?",
        )
        assert redirect.capability_name == "Task Manager"
        assert redirect.relevance_score == 0.8

    def test_relevance_score_validation(self):
        """Test relevance score validation."""
        with pytest.raises(ValueError):
            Redirect(
                capability_name="test",
                description="test",
                relevance_score=1.5,
                action_phrase="test",
            )


class TestGracefulResponse:
    """Tests for GracefulResponse dataclass."""

    def test_create_graceful_response(self):
        """Test creating a graceful response."""
        response = GracefulResponse(
            response_type=GracefulResponseType.REDIRECT,
            primary_message="I can help with something similar.",
            tone=DriftResponseTone.HELPFUL,
            acknowledgment="I understand you want weather info.",
            alternatives=[
                Redirect(
                    capability_name="Task",
                    description="Create tasks",
                    relevance_score=0.7,
                    action_phrase="Create a task?",
                )
            ],
        )
        assert response.response_type == GracefulResponseType.REDIRECT
        assert len(response.alternatives) == 1

    def test_to_message(self):
        """Test to_message method."""
        response = GracefulResponse(
            response_type=GracefulResponseType.REDIRECT,
            primary_message="I can help with tasks instead.",
            tone=DriftResponseTone.HELPFUL,
            acknowledgment="I see you're asking about weather.",
            follow_up_prompt="Would you like to try that?",
        )
        message = response.to_message()
        assert "I see you're asking about weather" in message
        assert "I can help with tasks instead" in message
        assert "Would you like to try that?" in message


class TestDriftResponseTemplate:
    """Tests for DriftResponseTemplate dataclass."""

    def test_create_template(self):
        """Test creating a template."""
        template = DriftResponseTemplate(
            template_id="scope_redirect",
            drift_types=[DriftType.SCOPE_EXPANSION],
            template_text="I can't {requested}, but I can {alternative}.",
            required_variables=["requested", "alternative"],
            tone=DriftResponseTone.HELPFUL,
        )
        assert template.template_id == "scope_redirect"
        assert len(template.required_variables) == 2

    def test_render_template(self):
        """Test rendering a template."""
        template = DriftResponseTemplate(
            template_id="test",
            drift_types=[DriftType.DOMAIN_SHIFT],
            template_text="Hello {name}, welcome to {place}!",
            required_variables=["name", "place"],
            tone=DriftResponseTone.HELPFUL,
        )
        result = template.render({"name": "Alice", "place": "TaskApp"})
        assert result == "Hello Alice, welcome to TaskApp!"

    def test_render_missing_variable(self):
        """Test rendering with missing variable."""
        template = DriftResponseTemplate(
            template_id="test",
            drift_types=[DriftType.DOMAIN_SHIFT],
            template_text="Hello {name}!",
            required_variables=["name"],
            tone=DriftResponseTone.HELPFUL,
        )
        with pytest.raises(ValueError, match="Missing required variables"):
            template.render({})


# ============================================
# Conversation Context Tests
# ============================================


class TestDriftEvent:
    """Tests for DriftEvent dataclass."""

    def test_create_drift_event(self):
        """Test creating a drift event."""
        event = DriftEvent(
            turn_id="turn_1",
            drift_type=DriftType.DOMAIN_SHIFT,
            drift_score=0.8,
            recovery_attempted=True,
            recovery_successful=True,
        )
        assert event.turn_id == "turn_1"
        assert event.drift_score == 0.8


class TestDriftConversationTurn:
    """Tests for DriftConversationTurn dataclass."""

    def test_create_turn(self):
        """Test creating a conversation turn."""
        turn = DriftConversationTurn(
            turn_id="turn_1",
            turn_number=1,
            user_input="Hello",
            timestamp="2024-01-01T00:00:00Z",
            detected_intent="greeting",
        )
        assert turn.turn_number == 1
        assert turn.had_drift is False

    def test_had_drift_property(self):
        """Test had_drift property."""
        analysis = DriftAnalysis(
            current_input="test",
            drift_score=0.8,
            drift_type=DriftType.DOMAIN_SHIFT,
            confidence=0.9,
            semantic_distance=0.7,
            graceful_response="test",
        )
        turn = DriftConversationTurn(
            turn_id="turn_1",
            turn_number=1,
            user_input="test",
            timestamp="2024-01-01T00:00:00Z",
            drift_analysis=analysis,
        )
        assert turn.had_drift is True


class TestCoherenceAnalysis:
    """Tests for CoherenceAnalysis dataclass."""

    def test_create_coherence_analysis(self):
        """Test creating a coherence analysis."""
        analysis = CoherenceAnalysis(
            coherence_score=0.85,
            topic_consistency=0.9,
            intent_stability=0.8,
            coherence_trend=CoherenceTrend.STABLE,
        )
        assert analysis.coherence_score == 0.85
        assert analysis.is_healthy is True

    def test_is_healthy_degrading(self):
        """Test is_healthy with degrading trend."""
        analysis = CoherenceAnalysis(
            coherence_score=0.7,
            topic_consistency=0.7,
            intent_stability=0.7,
            coherence_trend=CoherenceTrend.DEGRADING,
        )
        assert analysis.is_healthy is False

    def test_is_healthy_low_score(self):
        """Test is_healthy with low score."""
        analysis = CoherenceAnalysis(
            coherence_score=0.4,
            topic_consistency=0.5,
            intent_stability=0.5,
            coherence_trend=CoherenceTrend.STABLE,
        )
        assert analysis.is_healthy is False

    def test_score_validation(self):
        """Test score validation."""
        with pytest.raises(ValueError):
            CoherenceAnalysis(
                coherence_score=1.5,
                topic_consistency=0.5,
                intent_stability=0.5,
                coherence_trend=CoherenceTrend.STABLE,
            )


class TestConversationDriftContext:
    """Tests for ConversationDriftContext dataclass."""

    def test_create_context(self):
        """Test creating a conversation context."""
        context = ConversationDriftContext(
            session_id="session_123",
            initial_intent="greeting",
            current_topic="task_management",
        )
        assert context.session_id == "session_123"
        assert context.turn_count == 0

    def test_add_turn(self):
        """Test adding a turn."""
        context = ConversationDriftContext(session_id="test")
        turn = DriftConversationTurn(
            turn_id="turn_1",
            turn_number=1,
            user_input="Hello",
            timestamp="2024-01-01T00:00:00Z",
        )
        context.add_turn(turn)
        assert context.turn_count == 1

    def test_record_drift(self):
        """Test recording a drift event."""
        context = ConversationDriftContext(session_id="test")
        event = DriftEvent(
            turn_id="turn_1",
            drift_type=DriftType.DOMAIN_SHIFT,
            drift_score=0.8,
        )
        context.record_drift(event)
        assert context.drift_count == 1

    def test_drift_rate(self):
        """Test drift rate calculation."""
        context = ConversationDriftContext(session_id="test")

        # Add turns without drift
        for i in range(3):
            context.add_turn(
                DriftConversationTurn(
                    turn_id=f"turn_{i}",
                    turn_number=i,
                    user_input="test",
                    timestamp="2024-01-01T00:00:00Z",
                )
            )

        # Add turn with drift
        analysis = DriftAnalysis(
            current_input="test",
            drift_score=0.8,
            drift_type=DriftType.DOMAIN_SHIFT,
            confidence=0.9,
            semantic_distance=0.7,
            graceful_response="test",
        )
        context.add_turn(
            DriftConversationTurn(
                turn_id="turn_3",
                turn_number=3,
                user_input="test",
                timestamp="2024-01-01T00:00:00Z",
                drift_analysis=analysis,
            )
        )

        assert context.drift_rate == 0.25  # 1 out of 4

    def test_drift_rate_empty(self):
        """Test drift rate with no turns."""
        context = ConversationDriftContext(session_id="test")
        assert context.drift_rate == 0.0


# ============================================
# Configuration Tests
# ============================================


class TestDriftDetectionConfig:
    """Tests for DriftDetectionConfig dataclass."""

    def test_create_config(self):
        """Test creating a config."""
        config = DriftDetectionConfig(
            drift_threshold=0.6,
            confidence_threshold=0.7,
            supported_domains=["tasks", "calendar"],
        )
        assert config.drift_threshold == 0.6
        assert len(config.supported_domains) == 2

    def test_default_config(self):
        """Test default config values."""
        config = DriftDetectionConfig()
        assert config.drift_threshold == 0.5
        assert config.confidence_threshold == 0.6
        assert config.enable_personalization_detection is True

    def test_threshold_validation(self):
        """Test threshold validation."""
        with pytest.raises(ValueError):
            DriftDetectionConfig(drift_threshold=1.5)


class TestDriftDetectionResult:
    """Tests for DriftDetectionResult dataclass."""

    def test_create_result(self):
        """Test creating a detection result."""
        config = DriftDetectionConfig()
        analysis = DriftAnalysis(
            current_input="test",
            drift_score=0.8,
            drift_type=DriftType.DOMAIN_SHIFT,
            confidence=0.9,
            semantic_distance=0.7,
            graceful_response="test",
        )
        confidence = ConfidenceAssessment.from_score(0.9)
        semantic = SemanticAnalysis(
            input_text="test",
            abstraction_level=AbstractionLevel.CONCRETE,
        )

        result = DriftDetectionResult(
            input="test",
            config=config,
            analysis=analysis,
            confidence_assessment=confidence,
            semantic_analysis=semantic,
            processing_time_ms=50,
        )
        assert result.processing_time_ms == 50

    def test_needs_intervention(self):
        """Test needs_intervention property."""
        config = DriftDetectionConfig()
        analysis = DriftAnalysis(
            current_input="test",
            drift_score=0.8,
            drift_type=DriftType.DOMAIN_SHIFT,
            confidence=0.9,
            semantic_distance=0.7,
            graceful_response="test",
        )
        confidence = ConfidenceAssessment(
            overall_confidence=0.5,
            confidence_tier=ConfidenceTier.LOW,
            recommended_action=RecommendedAction.REDIRECT,
            explanation="test",
        )
        semantic = SemanticAnalysis(
            input_text="test",
            abstraction_level=AbstractionLevel.CONCRETE,
        )

        result = DriftDetectionResult(
            input="test",
            config=config,
            analysis=analysis,
            confidence_assessment=confidence,
            semantic_analysis=semantic,
            processing_time_ms=50,
        )
        assert result.needs_intervention is True


# ============================================
# Request/Response Tests
# ============================================


class TestDriftAnalysisRequest:
    """Tests for DriftAnalysisRequest dataclass."""

    def test_create_request(self):
        """Test creating a request."""
        request = DriftAnalysisRequest(
            input="What's the weather?",
            include_semantic_analysis=True,
            include_suggestions=True,
        )
        assert request.input == "What's the weather?"
        assert request.include_semantic_analysis is True


class TestDriftAggregateStats:
    """Tests for DriftAggregateStats dataclass."""

    def test_create_stats(self):
        """Test creating aggregate stats."""
        stats = DriftAggregateStats(
            total_inputs=100,
            drift_count=25,
            drift_rate=0.25,
            avg_drift_score=0.45,
            avg_confidence=0.85,
            drift_type_counts={"domain_shift": 15, "scope_expansion": 10},
        )
        assert stats.total_inputs == 100
        assert stats.drift_rate == 0.25


class TestBatchDriftAnalysis:
    """Tests for BatchDriftAnalysis dataclass."""

    def test_create_batch_analysis(self):
        """Test creating a batch analysis."""
        batch = BatchDriftAnalysis(
            requests=[],
            results=[],
            aggregate_stats=DriftAggregateStats(
                total_inputs=0,
                drift_count=0,
                drift_rate=0.0,
                avg_drift_score=0.0,
                avg_confidence=0.0,
            ),
        )
        assert batch.aggregate_stats.total_inputs == 0


# ============================================
# Integration Tests
# ============================================


class TestIntegration:
    """Integration tests for drift types."""

    def test_full_drift_detection_flow(self):
        """Test complete drift detection flow."""
        # Create configuration
        config = DriftDetectionConfig(
            drift_threshold=0.5,
            supported_domains=["tasks", "calendar"],
        )

        # Create semantic analysis
        semantic = SemanticAnalysis(
            input_text="What will the stock market do in 2030?",
            abstraction_level=AbstractionLevel.ABSTRACT,
            temporal_references=[
                TemporalReference(
                    expression="2030",
                    reference_type=TemporalReferenceType.FUTURE_ABSOLUTE,
                    is_within_knowledge=False,
                    drift_risk=0.9,
                )
            ],
        )

        # Create drift analysis
        analysis = DriftAnalysis(
            current_input="What will the stock market do in 2030?",
            drift_score=0.85,
            drift_type=DriftType.TEMPORAL_DRIFT,
            confidence=0.92,
            semantic_distance=0.8,
            graceful_response="I can't predict future events.",
            suggested_redirects=[
                RedirectSuggestion(
                    target_intent="financial_summary",
                    similarity_score=0.6,
                    redirect_reason="Related to finance",
                    transition_phrase="I can show current data instead.",
                    confidence=0.7,
                )
            ],
        )

        # Create confidence assessment
        confidence = ConfidenceAssessment.from_score(0.92)

        # Create result
        result = DriftDetectionResult(
            input="What will the stock market do in 2030?",
            config=config,
            analysis=analysis,
            confidence_assessment=confidence,
            semantic_analysis=semantic,
            processing_time_ms=45,
        )

        # Verify flow
        assert result.analysis.has_drift is True
        assert result.analysis.drift_type == DriftType.TEMPORAL_DRIFT
        assert result.semantic_analysis.has_temporal_drift_risk is True
        assert result.needs_intervention is True

    def test_conversation_context_tracking(self):
        """Test conversation context with drift tracking."""
        context = ConversationDriftContext(
            session_id="test_session",
            initial_intent="greeting",
        )

        # Add initial turn
        context.add_turn(
            DriftConversationTurn(
                turn_id="turn_1",
                turn_number=1,
                user_input="Hello",
                timestamp="2024-01-01T00:00:00Z",
                detected_intent="greeting",
            )
        )

        # Add turn with drift
        drift_analysis = DriftAnalysis(
            current_input="What's the weather?",
            drift_score=0.8,
            drift_type=DriftType.DOMAIN_SHIFT,
            confidence=0.9,
            semantic_distance=0.75,
            graceful_response="I can't check weather.",
        )

        context.add_turn(
            DriftConversationTurn(
                turn_id="turn_2",
                turn_number=2,
                user_input="What's the weather?",
                timestamp="2024-01-01T00:01:00Z",
                drift_analysis=drift_analysis,
            )
        )

        context.record_drift(
            DriftEvent(
                turn_id="turn_2",
                drift_type=DriftType.DOMAIN_SHIFT,
                drift_score=0.8,
                recovery_attempted=True,
                recovery_successful=False,
            )
        )

        # Verify tracking
        assert context.turn_count == 2
        assert context.drift_count == 1
        assert context.drift_rate == 0.5
