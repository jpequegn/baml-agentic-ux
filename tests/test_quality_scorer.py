"""Tests for Quality Scorer.

Issue #92 - Task 6.4: Quality Scorer
Part of #29 - Phase 6: Conversational Testing Framework
"""

import pytest

from src.testing import (
    CoherenceBreakdown,
    ContextRetentionBreakdown,
    ConversationQuality,
    DimensionScore,
    NaturalnessBreakdown,
    QualityDimension,
    QualityScorer,
    QualityScorerConfig,
    QualityThresholds,
    TurnResult,
)


# ============================================
# Configuration Tests
# ============================================


class TestQualityScorerConfig:
    """Test QualityScorerConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = QualityScorerConfig()
        assert config.use_llm_evaluation is False
        assert config.llm_evaluator is None
        assert config.min_response_length == 1
        assert config.max_repetition_ratio == 0.5
        assert config.enable_detailed_breakdown is True

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        thresholds = QualityThresholds(coherence_threshold=0.90)
        config = QualityScorerConfig(
            thresholds=thresholds,
            use_llm_evaluation=True,
            min_response_length=10,
        )
        assert config.thresholds.coherence_threshold == 0.90
        assert config.use_llm_evaluation is True
        assert config.min_response_length == 10


# ============================================
# Breakdown Type Tests
# ============================================


class TestCoherenceBreakdown:
    """Test CoherenceBreakdown calculations."""

    def test_overall_calculation(self) -> None:
        """Test overall coherence score calculation."""
        breakdown = CoherenceBreakdown(
            topic_consistency=0.9,
            reference_resolution=0.8,
            logical_flow=0.85,
            no_contradictions=1.0,
        )
        # Weighted: 0.9*0.3 + 0.8*0.25 + 0.85*0.25 + 1.0*0.2 = 0.8825
        assert abs(breakdown.overall - 0.8825) < 0.01

    def test_default_values(self) -> None:
        """Test default breakdown values."""
        breakdown = CoherenceBreakdown()
        assert breakdown.topic_consistency == 0.0
        assert breakdown.reference_resolution == 0.0
        assert breakdown.logical_flow == 0.0
        assert breakdown.no_contradictions == 1.0


class TestNaturalnessBreakdown:
    """Test NaturalnessBreakdown calculations."""

    def test_overall_calculation(self) -> None:
        """Test overall naturalness score calculation."""
        breakdown = NaturalnessBreakdown(
            fluency=0.9,
            appropriateness=0.85,
            diversity=0.8,
            human_likeness=0.75,
        )
        # Weighted: 0.9*0.3 + 0.85*0.3 + 0.8*0.2 + 0.75*0.2 = 0.835
        assert abs(breakdown.overall - 0.835) < 0.01


class TestContextRetentionBreakdown:
    """Test ContextRetentionBreakdown calculations."""

    def test_overall_calculation(self) -> None:
        """Test overall context retention score calculation."""
        breakdown = ContextRetentionBreakdown(
            entity_tracking=0.95,
            state_preservation=0.9,
            reference_accuracy=0.85,
        )
        # Weighted: 0.95*0.4 + 0.9*0.35 + 0.85*0.25 = 0.9075
        assert abs(breakdown.overall - 0.9075) < 0.01


class TestDimensionScore:
    """Test DimensionScore dataclass."""

    def test_create_score(self) -> None:
        """Test creating a dimension score."""
        score = DimensionScore(
            dimension=QualityDimension.COHERENCE,
            score=0.85,
            sub_scores={"topic": 0.9, "flow": 0.8},
            explanation="Good coherence overall",
            confidence=0.95,
        )
        assert score.dimension == QualityDimension.COHERENCE
        assert score.score == 0.85
        assert score.sub_scores["topic"] == 0.9
        assert score.confidence == 0.95


# ============================================
# Quality Scorer Basic Tests
# ============================================


class TestQualityScorerBasic:
    """Test basic QualityScorer functionality."""

    def test_create_scorer(self) -> None:
        """Test creating a quality scorer."""
        scorer = QualityScorer()
        assert scorer.config is not None
        assert scorer._conversation_history == []

    def test_reset(self) -> None:
        """Test resetting scorer state."""
        scorer = QualityScorer()
        scorer._conversation_history = ["hello", "hi there"]
        scorer._entity_mentions = {"name": ["John"]}
        scorer._context_state = {"key": "value"}

        scorer.reset()

        assert scorer._conversation_history == []
        assert scorer._entity_mentions == {}
        assert scorer._context_state == {}


# ============================================
# Turn Scoring Tests
# ============================================


class TestTurnScoring:
    """Test single turn scoring."""

    def test_score_simple_turn(self) -> None:
        """Test scoring a simple turn."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="Hello!",
            passed=True,
            latency_ms=100,
            actual_response="Hi there! How can I help you today?",
        )

        scores = scorer.score_turn(turn)

        assert QualityDimension.COHERENCE.value in scores
        assert QualityDimension.NATURALNESS.value in scores
        assert QualityDimension.RELEVANCE.value in scores
        assert scores[QualityDimension.COHERENCE.value].score >= 0.0
        assert scores[QualityDimension.COHERENCE.value].score <= 1.0

    def test_score_empty_response(self) -> None:
        """Test scoring a turn with empty response."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="Hello!",
            passed=True,
            latency_ms=100,
            actual_response="",
        )

        scores = scorer.score_turn(turn)

        # Empty responses should get low scores (but not necessarily 0 due to default sub-scores)
        assert scores[QualityDimension.COHERENCE.value].score <= 0.3
        assert scores[QualityDimension.NATURALNESS.value].score <= 0.3

    def test_score_high_quality_response(self) -> None:
        """Test scoring a high-quality response."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="What's the weather like in New York?",
            passed=True,
            latency_ms=150,
            actual_response="The weather in New York is currently sunny with temperatures around 72°F. It's a beautiful day! Would you like more details about the forecast?",
        )

        scores = scorer.score_turn(turn)

        # High-quality response should score well
        assert scores[QualityDimension.COHERENCE.value].score >= 0.6
        assert scores[QualityDimension.NATURALNESS.value].score >= 0.6
        assert scores[QualityDimension.RELEVANCE.value].score >= 0.5


# ============================================
# Coherence Scoring Tests
# ============================================


class TestCoherenceScoring:
    """Test coherence scoring functionality."""

    def test_topic_consistency_on_topic(self) -> None:
        """Test topic consistency for on-topic response."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="Tell me about Python programming",
            passed=True,
            latency_ms=100,
            actual_response="Python is a versatile programming language known for its simplicity and readability. It's widely used in web development, data science, and automation.",
        )

        scores = scorer.score_turn(turn)
        coherence = scores[QualityDimension.COHERENCE.value]

        assert coherence.score >= 0.5
        assert "topic_consistency" in coherence.sub_scores

    def test_topic_consistency_off_topic(self) -> None:
        """Test topic consistency for off-topic response."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="What's the weather like?",
            passed=True,
            latency_ms=100,
            actual_response="I enjoy eating pizza on Fridays with my friends.",
        )

        scores = scorer.score_turn(turn)
        coherence = scores[QualityDimension.COHERENCE.value]

        # Off-topic should have lower coherence
        assert coherence.sub_scores["topic_consistency"] < 0.7

    def test_logical_flow_good(self) -> None:
        """Test logical flow scoring for well-structured response."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="How do I make coffee?",
            passed=True,
            latency_ms=100,
            actual_response="First, boil some water. Then, add coffee grounds to your filter. Next, pour the hot water over the grounds. Finally, let it brew for a few minutes.",
        )

        scores = scorer.score_turn(turn)
        coherence = scores[QualityDimension.COHERENCE.value]

        # Good logical flow with transitions
        assert coherence.sub_scores["logical_flow"] >= 0.7


# ============================================
# Naturalness Scoring Tests
# ============================================


class TestNaturalnessScoring:
    """Test naturalness scoring functionality."""

    def test_fluency_complete_sentence(self) -> None:
        """Test fluency for complete sentences."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="Hello",
            passed=True,
            latency_ms=100,
            actual_response="Hello! I'm happy to assist you today. What can I help you with?",
        )

        scores = scorer.score_turn(turn)
        naturalness = scores[QualityDimension.NATURALNESS.value]

        assert naturalness.sub_scores["fluency"] >= 0.8

    def test_appropriateness_helpful_response(self) -> None:
        """Test appropriateness for helpful response."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="Can you help me?",
            passed=True,
            latency_ms=100,
            actual_response="I'd be happy to help you! Please let me know what you need assistance with, and I'll do my best to support you.",
        )

        scores = scorer.score_turn(turn)
        naturalness = scores[QualityDimension.NATURALNESS.value]

        assert naturalness.sub_scores["appropriateness"] >= 0.7

    def test_human_likeness_natural_response(self) -> None:
        """Test human-likeness for natural response."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="What do you think about AI?",
            passed=True,
            latency_ms=100,
            actual_response="I think AI is a fascinating field. It's interesting how technology continues to evolve. What aspects of AI are you curious about?",
        )

        scores = scorer.score_turn(turn)
        naturalness = scores[QualityDimension.NATURALNESS.value]

        assert naturalness.sub_scores["human_likeness"] >= 0.7

    def test_diversity_no_repetition(self) -> None:
        """Test diversity for non-repetitive response."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="Tell me something",
            passed=True,
            latency_ms=100,
            actual_response="The Earth orbits the Sun once every 365 days. This journey through space creates our seasons and marks the passage of time.",
        )

        scores = scorer.score_turn(turn)
        naturalness = scores[QualityDimension.NATURALNESS.value]

        assert naturalness.sub_scores["diversity"] >= 0.6


# ============================================
# Relevance Scoring Tests
# ============================================


class TestRelevanceScoring:
    """Test relevance scoring functionality."""

    def test_relevant_answer_to_question(self) -> None:
        """Test relevance for answer matching question."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="What is the capital of France?",
            passed=True,
            latency_ms=100,
            actual_response="The capital of France is Paris.",
        )

        scores = scorer.score_turn(turn)
        relevance = scores[QualityDimension.RELEVANCE.value]

        assert relevance.score >= 0.6

    def test_irrelevant_response(self) -> None:
        """Test relevance for unrelated response."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="What time is it?",
            passed=True,
            latency_ms=100,
            actual_response="Bananas are a good source of potassium.",
        )

        scores = scorer.score_turn(turn)
        relevance = scores[QualityDimension.RELEVANCE.value]

        assert relevance.score < 0.7


# ============================================
# Context Retention Tests
# ============================================


class TestContextRetentionScoring:
    """Test context retention scoring functionality."""

    def test_entity_tracking(self) -> None:
        """Test entity tracking in responses."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="Tell me about John's appointment",
            passed=True,
            latency_ms=100,
            actual_response="John has an appointment scheduled for tomorrow at 3 PM.",
        )

        scores = scorer.score_turn(turn, expected_entities=["John", "appointment"])
        retention = scores[QualityDimension.CONTEXT_RETENTION.value]

        assert retention.sub_scores["entity_tracking"] >= 0.9

    def test_entity_tracking_missing_entities(self) -> None:
        """Test entity tracking when entities are missing."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="What about the meeting?",
            passed=True,
            latency_ms=100,
            actual_response="Sure, I can help with that.",
        )

        scores = scorer.score_turn(turn, expected_entities=["meeting", "time", "location"])
        retention = scores[QualityDimension.CONTEXT_RETENTION.value]

        # Missing entities should lower score
        assert retention.sub_scores["entity_tracking"] < 0.5


# ============================================
# Conversation Scoring Tests
# ============================================


class TestConversationScoring:
    """Test full conversation scoring."""

    def test_score_simple_conversation(self) -> None:
        """Test scoring a simple conversation."""
        scorer = QualityScorer()
        turns = [
            TurnResult(
                turn_number=1,
                input="Hello!",
                passed=True,
                latency_ms=100,
                actual_response="Hi there! How can I help you?",
            ),
            TurnResult(
                turn_number=2,
                input="What's 2 + 2?",
                passed=True,
                latency_ms=80,
                actual_response="2 + 2 equals 4.",
            ),
        ]

        quality = scorer.score_conversation(turns)

        assert isinstance(quality, ConversationQuality)
        assert 0.0 <= quality.coherence.score <= 1.0
        assert 0.0 <= quality.naturalness.score <= 1.0
        assert 0.0 <= quality.overall_score <= 1.0

    def test_threshold_pass(self) -> None:
        """Test passing quality thresholds."""
        config = QualityScorerConfig(
            thresholds=QualityThresholds(
                coherence_threshold=0.5,
                naturalness_threshold=0.5,
                accuracy_threshold=0.5,
                relevance_threshold=0.5,
            )
        )
        scorer = QualityScorer(config)
        turns = [
            TurnResult(
                turn_number=1,
                input="Hello!",
                passed=True,
                latency_ms=100,
                actual_response="Hello! I'm here to help you with anything you need.",
            ),
        ]

        quality = scorer.score_conversation(turns)

        # With low thresholds, should pass
        assert quality.passed_thresholds is True
        assert len(quality.threshold_failures) == 0

    def test_threshold_fail(self) -> None:
        """Test failing quality thresholds."""
        config = QualityScorerConfig(
            thresholds=QualityThresholds(
                coherence_threshold=0.99,  # Very high threshold
                naturalness_threshold=0.99,
                accuracy_threshold=0.99,
                relevance_threshold=0.99,
            )
        )
        scorer = QualityScorer(config)
        turns = [
            TurnResult(
                turn_number=1,
                input="Hello",
                passed=True,
                latency_ms=100,
                actual_response="Hi",
            ),
        ]

        quality = scorer.score_conversation(turns)

        # With very high thresholds, should fail
        assert quality.passed_thresholds is False
        assert len(quality.threshold_failures) > 0

    def test_to_quality_scores(self) -> None:
        """Test converting ConversationQuality to QualityScores."""
        scorer = QualityScorer()
        turns = [
            TurnResult(
                turn_number=1,
                input="Test",
                passed=True,
                latency_ms=100,
                actual_response="This is a test response.",
            ),
        ]

        quality = scorer.score_conversation(turns)
        scores = quality.to_quality_scores()

        assert scores.coherence == quality.coherence.score
        assert scores.naturalness == quality.naturalness.score
        assert scores.accuracy == quality.accuracy.score
        assert scores.relevance == quality.relevance.score


# ============================================
# Edge Cases
# ============================================


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_very_short_response(self) -> None:
        """Test scoring very short responses."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="Yes or no?",
            passed=True,
            latency_ms=50,
            actual_response="Yes.",
        )

        scores = scorer.score_turn(turn)

        # Should still produce valid scores
        assert all(
            0.0 <= scores[dim.value].score <= 1.0
            for dim in QualityDimension
            if dim.value in scores
        )

    def test_long_response(self) -> None:
        """Test scoring long responses."""
        scorer = QualityScorer()
        long_response = (
            "This is a very detailed and comprehensive response. "
            * 20
        )
        turn = TurnResult(
            turn_number=1,
            input="Tell me everything",
            passed=True,
            latency_ms=500,
            actual_response=long_response,
        )

        scores = scorer.score_turn(turn)

        # Should handle long responses
        assert scores[QualityDimension.COHERENCE.value].score >= 0.0

    def test_special_characters(self) -> None:
        """Test handling responses with special characters."""
        scorer = QualityScorer()
        turn = TurnResult(
            turn_number=1,
            input="What's the formula?",
            passed=True,
            latency_ms=100,
            actual_response="The formula is: E = mc² where E is energy, m is mass, and c is the speed of light.",
        )

        scores = scorer.score_turn(turn)

        # Should handle special characters
        assert scores[QualityDimension.COHERENCE.value].score >= 0.0

    def test_multiple_turns_context(self) -> None:
        """Test context builds across multiple turns."""
        scorer = QualityScorer()

        # First turn
        turn1 = TurnResult(
            turn_number=1,
            input="My name is Alice",
            passed=True,
            latency_ms=100,
            actual_response="Nice to meet you, Alice! How can I help you today?",
        )
        scorer.score_turn(turn1)

        # Second turn should have history context
        turn2 = TurnResult(
            turn_number=2,
            input="What's my name?",
            passed=True,
            latency_ms=100,
            actual_response="Your name is Alice, as you mentioned earlier.",
        )
        scores2 = scorer.score_turn(turn2)

        # Context retention should be high
        assert scores2[QualityDimension.CONTEXT_RETENTION.value].score >= 0.7

    def test_empty_conversation(self) -> None:
        """Test scoring empty conversation."""
        scorer = QualityScorer()
        quality = scorer.score_conversation([])

        assert quality.coherence.score == 0.0
        assert quality.naturalness.score == 0.0
        assert quality.overall_score == 0.0


# ============================================
# Integration Tests
# ============================================


class TestIntegration:
    """Integration tests for quality scorer."""

    def test_full_workflow(self) -> None:
        """Test complete scoring workflow."""
        # Configure scorer
        config = QualityScorerConfig(
            thresholds=QualityThresholds(
                coherence_threshold=0.6,
                naturalness_threshold=0.6,
            )
        )
        scorer = QualityScorer(config)

        # Multi-turn conversation
        turns = [
            TurnResult(
                turn_number=1,
                input="Hi, I need help planning a trip",
                passed=True,
                latency_ms=120,
                actual_response="Hello! I'd be happy to help you plan your trip. Where are you thinking of going?",
            ),
            TurnResult(
                turn_number=2,
                input="I want to go to Paris",
                passed=True,
                latency_ms=150,
                actual_response="Paris is a wonderful choice! The city offers amazing art, cuisine, and architecture. When are you planning to visit?",
            ),
            TurnResult(
                turn_number=3,
                input="Next month",
                passed=True,
                latency_ms=100,
                actual_response="Great! Next month is a lovely time to visit Paris. I recommend booking hotels in the Marais district and visiting the Louvre and Eiffel Tower.",
            ),
        ]

        # Score conversation
        quality = scorer.score_conversation(turns)

        # Verify results
        assert isinstance(quality, ConversationQuality)
        assert quality.coherence.score > 0
        assert quality.naturalness.score > 0
        assert quality.relevance.score > 0
        assert quality.overall_score > 0

        # Convert to test result format
        scores = quality.to_quality_scores()
        assert scores.coherence == quality.coherence.score

    def test_scorer_reuse(self) -> None:
        """Test reusing scorer for multiple conversations."""
        scorer = QualityScorer()

        # First conversation
        turns1 = [
            TurnResult(
                turn_number=1,
                input="Hello",
                passed=True,
                latency_ms=100,
                actual_response="Hi there!",
            ),
        ]
        quality1 = scorer.score_conversation(turns1)

        # Second conversation (should reset)
        turns2 = [
            TurnResult(
                turn_number=1,
                input="Goodbye",
                passed=True,
                latency_ms=100,
                actual_response="Farewell!",
            ),
        ]
        quality2 = scorer.score_conversation(turns2)

        # Both should be valid independent scores
        assert quality1 is not quality2
        assert quality1.overall_score >= 0
        assert quality2.overall_score >= 0
