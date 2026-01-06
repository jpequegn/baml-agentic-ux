"""
Tests for Intent Drift type definitions.

Part of Phase 5: Intent Drift Detection
Issue #109 - Task 5.11: Testing & Documentation
"""

import pytest
from src.intent_drift.types import (
    # Enums
    DriftType,
    AbstractionLevel,
    TemporalReferenceType,
    ConfidenceTier,
    RecommendedAction,
    GracefulResponseType,
    DriftResponseTone,
    CoherenceTrend,
    # Data classes
    RedirectSuggestion,
    DriftAnalysis,
    NearestIntent,
    TemporalReference,
    EntityMention,
    SemanticAnalysis,
    ConfidenceAssessment,
    GracefulResponse,
    DriftEvent,
)


class TestEnums:
    """Tests for enum value coverage."""

    def test_drift_type_values(self):
        """Test DriftType enum values."""
        assert DriftType.NONE.value == "none"
        assert DriftType.SCOPE_EXPANSION.value == "scope_expansion"
        assert DriftType.DOMAIN_SHIFT.value == "domain_shift"
        assert DriftType.ABSTRACTION_CLIMB.value == "abstraction_climb"
        assert DriftType.PERSONALIZATION.value == "personalization"
        assert DriftType.TEMPORAL_DRIFT.value == "temporal_drift"
        assert DriftType.AMBIGUOUS.value == "ambiguous"

    def test_abstraction_level_values(self):
        """Test AbstractionLevel enum values."""
        assert AbstractionLevel.CONCRETE.value == "concrete"
        assert AbstractionLevel.MODERATE.value == "moderate"
        assert AbstractionLevel.ABSTRACT.value == "abstract"
        assert AbstractionLevel.PHILOSOPHICAL.value == "philosophical"

    def test_temporal_reference_type_values(self):
        """Test TemporalReferenceType enum values."""
        assert TemporalReferenceType.PAST_ABSOLUTE.value == "past_absolute"
        assert TemporalReferenceType.PAST_RELATIVE.value == "past_relative"
        assert TemporalReferenceType.PRESENT.value == "present"
        assert TemporalReferenceType.FUTURE_RELATIVE.value == "future_relative"
        assert TemporalReferenceType.FUTURE_ABSOLUTE.value == "future_absolute"
        assert TemporalReferenceType.HYPOTHETICAL.value == "hypothetical"

    def test_confidence_tier_values(self):
        """Test ConfidenceTier enum values."""
        assert ConfidenceTier.VERY_HIGH.value == "very_high"
        assert ConfidenceTier.HIGH.value == "high"
        assert ConfidenceTier.MEDIUM.value == "medium"
        assert ConfidenceTier.LOW.value == "low"
        assert ConfidenceTier.VERY_LOW.value == "very_low"

    def test_recommended_action_values(self):
        """Test RecommendedAction enum values."""
        assert RecommendedAction.PROCEED.value == "proceed"
        assert RecommendedAction.PROCEED_WITH_CAVEAT.value == "proceed_with_caveat"
        assert RecommendedAction.CLARIFY.value == "clarify"
        assert RecommendedAction.REDIRECT.value == "redirect"
        assert RecommendedAction.ESCALATE.value == "escalate"
        assert RecommendedAction.DECLINE.value == "decline"

    def test_graceful_response_type_values(self):
        """Test GracefulResponseType enum values."""
        assert GracefulResponseType.CLARIFICATION.value == "clarification"
        assert GracefulResponseType.PARTIAL_HELP.value == "partial_help"
        assert GracefulResponseType.REDIRECT.value == "redirect"
        assert GracefulResponseType.BOUNDARY_STATEMENT.value == "boundary_statement"
        assert GracefulResponseType.ESCALATION.value == "escalation"
        assert GracefulResponseType.ACKNOWLEDGMENT.value == "acknowledgment"

    def test_drift_response_tone_values(self):
        """Test DriftResponseTone enum values."""
        assert DriftResponseTone.EMPATHETIC.value == "empathetic"
        assert DriftResponseTone.HELPFUL.value == "helpful"
        assert DriftResponseTone.PROFESSIONAL.value == "professional"
        assert DriftResponseTone.APOLOGETIC.value == "apologetic"
        assert DriftResponseTone.ENCOURAGING.value == "encouraging"

    def test_coherence_trend_values(self):
        """Test CoherenceTrend enum values."""
        assert CoherenceTrend.IMPROVING.value == "improving"
        assert CoherenceTrend.STABLE.value == "stable"
        assert CoherenceTrend.DEGRADING.value == "degrading"
        assert CoherenceTrend.VOLATILE.value == "volatile"


class TestRedirectSuggestion:
    """Tests for RedirectSuggestion dataclass."""

    def test_valid_creation(self):
        """Test creating valid RedirectSuggestion."""
        suggestion = RedirectSuggestion(
            target_intent="search_products",
            similarity_score=0.85,
            redirect_reason="Product search is available",
            transition_phrase="I can help you search for products instead",
            confidence=0.9,
        )

        assert suggestion.target_intent == "search_products"
        assert suggestion.similarity_score == 0.85
        assert suggestion.confidence == 0.9

    def test_invalid_similarity_score_too_high(self):
        """Test that similarity_score > 1.0 raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            RedirectSuggestion(
                target_intent="test",
                similarity_score=1.5,
                redirect_reason="test",
                transition_phrase="test",
                confidence=0.5,
            )
        assert "similarity_score" in str(exc_info.value)

    def test_invalid_similarity_score_negative(self):
        """Test that negative similarity_score raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            RedirectSuggestion(
                target_intent="test",
                similarity_score=-0.1,
                redirect_reason="test",
                transition_phrase="test",
                confidence=0.5,
            )
        assert "similarity_score" in str(exc_info.value)

    def test_invalid_confidence_too_high(self):
        """Test that confidence > 1.0 raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            RedirectSuggestion(
                target_intent="test",
                similarity_score=0.5,
                redirect_reason="test",
                transition_phrase="test",
                confidence=1.1,
            )
        assert "confidence" in str(exc_info.value)

    def test_boundary_values(self):
        """Test boundary values 0.0 and 1.0 are valid."""
        suggestion = RedirectSuggestion(
            target_intent="test",
            similarity_score=0.0,
            redirect_reason="test",
            transition_phrase="test",
            confidence=1.0,
        )
        assert suggestion.similarity_score == 0.0
        assert suggestion.confidence == 1.0


class TestDriftAnalysis:
    """Tests for DriftAnalysis dataclass."""

    def test_valid_creation(self):
        """Test creating valid DriftAnalysis."""
        analysis = DriftAnalysis(
            current_input="What's the meaning of life?",
            drift_score=0.7,
            drift_type=DriftType.ABSTRACTION_CLIMB,
            confidence=0.85,
            semantic_distance=0.65,
            graceful_response="That's a philosophical question.",
        )

        assert analysis.current_input == "What's the meaning of life?"
        assert analysis.drift_score == 0.7
        assert analysis.drift_type == DriftType.ABSTRACTION_CLIMB

    def test_has_drift_property_true(self):
        """Test has_drift returns True when drift detected."""
        analysis = DriftAnalysis(
            current_input="test",
            drift_score=0.5,
            drift_type=DriftType.DOMAIN_SHIFT,
            confidence=0.8,
            semantic_distance=0.6,
            graceful_response="test",
        )
        assert analysis.has_drift is True

    def test_has_drift_property_false(self):
        """Test has_drift returns False when no drift."""
        analysis = DriftAnalysis(
            current_input="test",
            drift_score=0.1,
            drift_type=DriftType.NONE,
            confidence=0.95,
            semantic_distance=0.1,
            graceful_response="test",
        )
        assert analysis.has_drift is False

    def test_needs_clarification_ambiguous(self):
        """Test needs_clarification for ambiguous drift."""
        analysis = DriftAnalysis(
            current_input="test",
            drift_score=0.5,
            drift_type=DriftType.AMBIGUOUS,
            confidence=0.8,
            semantic_distance=0.5,
            graceful_response="test",
        )
        assert analysis.needs_clarification is True

    def test_needs_clarification_low_confidence(self):
        """Test needs_clarification for low confidence."""
        analysis = DriftAnalysis(
            current_input="test",
            drift_score=0.3,
            drift_type=DriftType.SCOPE_EXPANSION,
            confidence=0.5,  # Below 0.6 threshold
            semantic_distance=0.4,
            graceful_response="test",
        )
        assert analysis.needs_clarification is True

    def test_needs_clarification_false(self):
        """Test needs_clarification returns False when not needed."""
        analysis = DriftAnalysis(
            current_input="test",
            drift_score=0.2,
            drift_type=DriftType.NONE,
            confidence=0.9,
            semantic_distance=0.2,
            graceful_response="test",
        )
        assert analysis.needs_clarification is False

    def test_has_redirects_true(self):
        """Test has_redirects when redirects available."""
        redirect = RedirectSuggestion(
            target_intent="alt",
            similarity_score=0.8,
            redirect_reason="reason",
            transition_phrase="phrase",
            confidence=0.9,
        )
        analysis = DriftAnalysis(
            current_input="test",
            drift_score=0.5,
            drift_type=DriftType.SCOPE_EXPANSION,
            confidence=0.8,
            semantic_distance=0.5,
            graceful_response="test",
            suggested_redirects=[redirect],
        )
        assert analysis.has_redirects is True

    def test_has_redirects_false(self):
        """Test has_redirects when no redirects."""
        analysis = DriftAnalysis(
            current_input="test",
            drift_score=0.5,
            drift_type=DriftType.DOMAIN_SHIFT,
            confidence=0.8,
            semantic_distance=0.5,
            graceful_response="test",
        )
        assert analysis.has_redirects is False

    def test_invalid_drift_score(self):
        """Test invalid drift_score raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            DriftAnalysis(
                current_input="test",
                drift_score=1.5,
                drift_type=DriftType.NONE,
                confidence=0.8,
                semantic_distance=0.5,
                graceful_response="test",
            )
        assert "drift_score" in str(exc_info.value)

    def test_invalid_confidence(self):
        """Test invalid confidence raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            DriftAnalysis(
                current_input="test",
                drift_score=0.5,
                drift_type=DriftType.NONE,
                confidence=-0.1,
                semantic_distance=0.5,
                graceful_response="test",
            )
        assert "confidence" in str(exc_info.value)


class TestNearestIntent:
    """Tests for NearestIntent dataclass."""

    def test_valid_creation(self):
        """Test creating valid NearestIntent."""
        intent = NearestIntent(
            intent_name="search_products",
            similarity=0.85,
            capability_id="cap_001",
            requires_clarification=False,
        )

        assert intent.intent_name == "search_products"
        assert intent.similarity == 0.85
        assert intent.capability_id == "cap_001"

    def test_invalid_similarity(self):
        """Test invalid similarity raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            NearestIntent(
                intent_name="test",
                similarity=1.5,
            )
        assert "similarity" in str(exc_info.value)

    def test_default_values(self):
        """Test default values are applied."""
        intent = NearestIntent(
            intent_name="test",
            similarity=0.5,
        )
        assert intent.capability_id is None
        assert intent.requires_clarification is False


class TestTemporalReference:
    """Tests for TemporalReference dataclass."""

    def test_valid_creation(self):
        """Test creating valid TemporalReference."""
        ref = TemporalReference(
            expression="yesterday",
            reference_type=TemporalReferenceType.PAST_RELATIVE,
            is_within_knowledge=True,
            drift_risk=0.1,
            resolved_date="2026-01-05",
        )

        assert ref.expression == "yesterday"
        assert ref.reference_type == TemporalReferenceType.PAST_RELATIVE
        assert ref.drift_risk == 0.1

    def test_invalid_drift_risk(self):
        """Test invalid drift_risk raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            TemporalReference(
                expression="test",
                reference_type=TemporalReferenceType.PRESENT,
                is_within_knowledge=True,
                drift_risk=1.5,
            )
        assert "drift_risk" in str(exc_info.value)


class TestEntityMention:
    """Tests for EntityMention dataclass."""

    def test_valid_creation(self):
        """Test creating valid EntityMention."""
        entity = EntityMention(
            text="Apple Inc.",
            entity_type="ORGANIZATION",
            start_offset=10,
            end_offset=20,
            requires_personalization=False,
        )

        assert entity.text == "Apple Inc."
        assert entity.entity_type == "ORGANIZATION"
        assert entity.start_offset == 10
        assert entity.end_offset == 20

    def test_personalization_flag(self):
        """Test requires_personalization flag."""
        entity = EntityMention(
            text="my account",
            entity_type="ACCOUNT",
            start_offset=0,
            end_offset=10,
            requires_personalization=True,
        )
        assert entity.requires_personalization is True


class TestSemanticAnalysis:
    """Tests for SemanticAnalysis dataclass."""

    def test_valid_creation(self):
        """Test creating valid SemanticAnalysis."""
        analysis = SemanticAnalysis(
            input_text="Search for products",
            abstraction_level=AbstractionLevel.CONCRETE,
        )

        assert analysis.input_text == "Search for products"
        assert analysis.abstraction_level == AbstractionLevel.CONCRETE
        assert analysis.nearest_intents == []
        assert analysis.domain_classification == []

    def test_with_nearest_intents(self):
        """Test SemanticAnalysis with nearest intents."""
        intent = NearestIntent(
            intent_name="product_search",
            similarity=0.9,
        )
        analysis = SemanticAnalysis(
            input_text="Find products",
            abstraction_level=AbstractionLevel.CONCRETE,
            nearest_intents=[intent],
        )
        assert len(analysis.nearest_intents) == 1
        assert analysis.nearest_intents[0].intent_name == "product_search"


class TestConfidenceAssessment:
    """Tests for ConfidenceAssessment dataclass."""

    def test_valid_creation(self):
        """Test creating valid ConfidenceAssessment."""
        assessment = ConfidenceAssessment(
            overall_confidence=0.85,
            confidence_tier=ConfidenceTier.HIGH,
            recommended_action=RecommendedAction.PROCEED,
            explanation="High confidence in intent detection",
        )

        assert assessment.overall_confidence == 0.85
        assert assessment.confidence_tier == ConfidenceTier.HIGH
        assert assessment.recommended_action == RecommendedAction.PROCEED

    def test_from_score_factory(self):
        """Test ConfidenceAssessment.from_score factory method."""
        # Very high confidence
        assessment = ConfidenceAssessment.from_score(0.96, "Test high score")
        assert assessment.confidence_tier == ConfidenceTier.VERY_HIGH
        assert assessment.recommended_action == RecommendedAction.PROCEED

        # Low confidence
        assessment = ConfidenceAssessment.from_score(0.45)
        assert assessment.confidence_tier == ConfidenceTier.LOW
        assert assessment.recommended_action == RecommendedAction.REDIRECT

    def test_invalid_overall_confidence(self):
        """Test invalid overall_confidence raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ConfidenceAssessment(
                overall_confidence=1.5,
                confidence_tier=ConfidenceTier.HIGH,
                recommended_action=RecommendedAction.PROCEED,
                explanation="test",
            )
        assert "overall_confidence" in str(exc_info.value)


class TestGracefulResponse:
    """Tests for GracefulResponse dataclass."""

    def test_valid_creation(self):
        """Test creating valid GracefulResponse."""
        response = GracefulResponse(
            response_type=GracefulResponseType.CLARIFICATION,
            primary_message="Could you clarify what you mean?",
            tone=DriftResponseTone.HELPFUL,
        )

        assert response.response_type == GracefulResponseType.CLARIFICATION
        assert "clarify" in response.primary_message.lower()
        assert response.tone == DriftResponseTone.HELPFUL

    def test_to_message_method(self):
        """Test GracefulResponse to_message method."""
        response = GracefulResponse(
            response_type=GracefulResponseType.REDIRECT,
            primary_message="I can help with something similar.",
            tone=DriftResponseTone.ENCOURAGING,
            acknowledgment="I understand what you're looking for.",
            follow_up_prompt="Would you like me to try one of these?",
        )
        message = response.to_message()
        assert "I understand" in message
        assert "similar" in message
        assert "Would you like" in message


class TestDriftEvent:
    """Tests for DriftEvent dataclass."""

    def test_valid_creation(self):
        """Test creating valid DriftEvent."""
        event = DriftEvent(
            turn_id="turn_123",
            drift_type=DriftType.SCOPE_EXPANSION,
            drift_score=0.6,
        )

        assert event.turn_id == "turn_123"
        assert event.drift_type == DriftType.SCOPE_EXPANSION
        assert event.drift_score == 0.6

    def test_default_values(self):
        """Test DriftEvent default values."""
        event = DriftEvent(
            turn_id="turn_456",
            drift_type=DriftType.DOMAIN_SHIFT,
            drift_score=0.7,
        )
        assert event.recovery_attempted is False
        assert event.recovery_successful is False
        assert event.notes is None

    def test_event_with_recovery(self):
        """Test DriftEvent with recovery info."""
        event = DriftEvent(
            turn_id="turn_789",
            drift_type=DriftType.DOMAIN_SHIFT,
            drift_score=0.7,
            recovery_attempted=True,
            recovery_successful=True,
            notes="User clarified their intent",
        )
        assert event.recovery_attempted is True
        assert event.recovery_successful is True
        assert "clarified" in event.notes
