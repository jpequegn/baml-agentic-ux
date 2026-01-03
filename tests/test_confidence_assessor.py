"""Tests for the confidence assessor module.

Issue #81 - Task 5.4: Confidence Assessor
Part of #28 - Phase 5: Intent Drift Detection
"""

import math
import pytest

from src.intent_drift.confidence_assessor import (
    AssessmentAction,
    AssessmentResult,
    CalibrationResult,
    ConfidenceAssessor,
    ConfidenceAssessorConfig,
    ConfidenceThresholds,
    IntentResult,
)
from src.intent_drift.types import (
    AbstractionLevel,
    CoherenceAnalysis,
    CoherenceTrend,
    ConfidenceFactorScore,
    ConfidenceTier,
    ConversationDriftContext,
    DriftConversationTurn,
    DriftEvent,
    DriftType,
    NearestIntent,
    RecommendedAction,
    SemanticAnalysis,
)


# ============================================
# ConfidenceThresholds Tests
# ============================================

class TestConfidenceThresholds:
    """Tests for ConfidenceThresholds class."""

    def test_very_high_threshold(self):
        """Test VERY_HIGH threshold value."""
        assert ConfidenceThresholds.VERY_HIGH == 0.95

    def test_high_threshold(self):
        """Test HIGH threshold value."""
        assert ConfidenceThresholds.HIGH == 0.85

    def test_medium_high_threshold(self):
        """Test MEDIUM_HIGH threshold value."""
        assert ConfidenceThresholds.MEDIUM_HIGH == 0.70

    def test_medium_threshold(self):
        """Test MEDIUM threshold value."""
        assert ConfidenceThresholds.MEDIUM == 0.50

    def test_low_threshold(self):
        """Test LOW threshold value."""
        assert ConfidenceThresholds.LOW == 0.30

    def test_thresholds_in_descending_order(self):
        """Test that thresholds are in descending order."""
        assert ConfidenceThresholds.VERY_HIGH > ConfidenceThresholds.HIGH
        assert ConfidenceThresholds.HIGH > ConfidenceThresholds.MEDIUM_HIGH
        assert ConfidenceThresholds.MEDIUM_HIGH > ConfidenceThresholds.MEDIUM
        assert ConfidenceThresholds.MEDIUM > ConfidenceThresholds.LOW


# ============================================
# AssessmentAction Tests
# ============================================

class TestAssessmentAction:
    """Tests for AssessmentAction enum."""

    def test_execute_action(self):
        """Test EXECUTE action value."""
        assert AssessmentAction.EXECUTE.value == "execute"

    def test_execute_with_hedge_action(self):
        """Test EXECUTE_WITH_HEDGE action value."""
        assert AssessmentAction.EXECUTE_WITH_HEDGE.value == "execute_with_hedge"

    def test_clarify_action(self):
        """Test CLARIFY action value."""
        assert AssessmentAction.CLARIFY.value == "clarify"

    def test_offer_alternatives_action(self):
        """Test OFFER_ALTERNATIVES action value."""
        assert AssessmentAction.OFFER_ALTERNATIVES.value == "offer_alternatives"

    def test_graceful_reject_action(self):
        """Test GRACEFUL_REJECT action value."""
        assert AssessmentAction.GRACEFUL_REJECT.value == "graceful_reject"

    def test_all_actions_have_unique_values(self):
        """Test all actions have unique values."""
        values = [a.value for a in AssessmentAction]
        assert len(values) == len(set(values))


# ============================================
# IntentResult Tests
# ============================================

class TestIntentResult:
    """Tests for IntentResult dataclass."""

    def test_basic_creation(self):
        """Test basic IntentResult creation."""
        result = IntentResult(intent_name="book_flight", confidence=0.9)
        assert result.intent_name == "book_flight"
        assert result.confidence == 0.9
        assert result.entities == {}
        assert result.raw_score is None

    def test_with_entities(self):
        """Test IntentResult with entities."""
        entities = {
            "destination": ("Paris", 0.95),
            "date": ("tomorrow", 0.8),
        }
        result = IntentResult(
            intent_name="book_flight",
            confidence=0.9,
            entities=entities,
        )
        assert len(result.entities) == 2
        assert result.entities["destination"] == ("Paris", 0.95)

    def test_with_raw_score(self):
        """Test IntentResult with raw score."""
        result = IntentResult(
            intent_name="book_flight",
            confidence=0.9,
            raw_score=0.87,
        )
        assert result.raw_score == 0.87

    def test_confidence_too_low(self):
        """Test confidence below 0 raises error."""
        with pytest.raises(ValueError, match="confidence must be between"):
            IntentResult(intent_name="test", confidence=-0.1)

    def test_confidence_too_high(self):
        """Test confidence above 1 raises error."""
        with pytest.raises(ValueError, match="confidence must be between"):
            IntentResult(intent_name="test", confidence=1.1)

    def test_avg_entity_confidence_no_entities(self):
        """Test average entity confidence with no entities."""
        result = IntentResult(intent_name="test", confidence=0.9)
        assert result.avg_entity_confidence == 1.0

    def test_avg_entity_confidence_single_entity(self):
        """Test average entity confidence with single entity."""
        result = IntentResult(
            intent_name="test",
            confidence=0.9,
            entities={"city": ("NYC", 0.8)},
        )
        assert result.avg_entity_confidence == 0.8

    def test_avg_entity_confidence_multiple_entities(self):
        """Test average entity confidence with multiple entities."""
        result = IntentResult(
            intent_name="test",
            confidence=0.9,
            entities={
                "city": ("NYC", 0.9),
                "date": ("today", 0.7),
            },
        )
        assert result.avg_entity_confidence == 0.8


# ============================================
# ConfidenceAssessorConfig Tests
# ============================================

class TestConfidenceAssessorConfig:
    """Tests for ConfidenceAssessorConfig dataclass."""

    def test_default_config(self):
        """Test default configuration."""
        config = ConfidenceAssessorConfig.default()
        assert config.intent_weight == 0.4
        assert config.entity_weight == 0.2
        assert config.context_weight == 0.2
        assert config.semantic_weight == 0.2
        assert config.enable_calibration is False

    def test_weights_sum_to_one(self):
        """Test that default weights sum to 1.0."""
        config = ConfidenceAssessorConfig.default()
        total = (
            config.intent_weight
            + config.entity_weight
            + config.context_weight
            + config.semantic_weight
        )
        assert abs(total - 1.0) < 0.01

    def test_invalid_weights_raises_error(self):
        """Test that invalid weights raise error."""
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            ConfidenceAssessorConfig(
                intent_weight=0.5,
                entity_weight=0.5,
                context_weight=0.5,
                semantic_weight=0.5,
            )

    def test_intent_focused_config(self):
        """Test intent-focused configuration."""
        config = ConfidenceAssessorConfig.intent_focused()
        assert config.intent_weight == 0.6
        assert config.entity_weight == 0.15
        assert config.context_weight == 0.15
        assert config.semantic_weight == 0.1

    def test_context_focused_config(self):
        """Test context-focused configuration."""
        config = ConfidenceAssessorConfig.context_focused()
        assert config.intent_weight == 0.3
        assert config.entity_weight == 0.1
        assert config.context_weight == 0.4
        assert config.semantic_weight == 0.2

    def test_custom_thresholds(self):
        """Test custom threshold configuration."""
        config = ConfidenceAssessorConfig(
            high_threshold=0.9,
            medium_high_threshold=0.75,
            medium_threshold=0.55,
            low_threshold=0.35,
        )
        assert config.high_threshold == 0.9
        assert config.medium_high_threshold == 0.75

    def test_calibration_enabled(self):
        """Test calibration configuration."""
        config = ConfidenceAssessorConfig(
            enable_calibration=True,
            calibration_temperature=1.5,
        )
        assert config.enable_calibration is True
        assert config.calibration_temperature == 1.5


# ============================================
# CalibrationResult Tests
# ============================================

class TestCalibrationResult:
    """Tests for CalibrationResult dataclass."""

    def test_basic_creation(self):
        """Test basic CalibrationResult creation."""
        result = CalibrationResult(
            original_score=0.7,
            calibrated_score=0.65,
            method="temperature_scaling",
        )
        assert result.original_score == 0.7
        assert result.calibrated_score == 0.65
        assert result.method == "temperature_scaling"
        assert result.temperature is None

    def test_with_temperature(self):
        """Test CalibrationResult with temperature."""
        result = CalibrationResult(
            original_score=0.7,
            calibrated_score=0.65,
            method="temperature_scaling",
            temperature=1.5,
        )
        assert result.temperature == 1.5


# ============================================
# AssessmentResult Tests
# ============================================

class TestAssessmentResult:
    """Tests for AssessmentResult dataclass."""

    def test_basic_creation(self):
        """Test basic AssessmentResult creation."""
        result = AssessmentResult(
            overall_confidence=0.85,
            tier=ConfidenceTier.HIGH,
            recommended_action=AssessmentAction.EXECUTE,
            factor_scores=[],
        )
        assert result.overall_confidence == 0.85
        assert result.tier == ConfidenceTier.HIGH
        assert result.recommended_action == AssessmentAction.EXECUTE

    def test_with_factor_scores(self):
        """Test AssessmentResult with factor scores."""
        factors = [
            ConfidenceFactorScore(
                factor_name="intent",
                score=0.9,
                weight=0.4,
                explanation="High intent confidence",
            ),
        ]
        result = AssessmentResult(
            overall_confidence=0.85,
            tier=ConfidenceTier.HIGH,
            recommended_action=AssessmentAction.EXECUTE,
            factor_scores=factors,
        )
        assert len(result.factor_scores) == 1

    def test_confidence_too_low(self):
        """Test confidence below 0 raises error."""
        with pytest.raises(ValueError, match="overall_confidence must be between"):
            AssessmentResult(
                overall_confidence=-0.1,
                tier=ConfidenceTier.LOW,
                recommended_action=AssessmentAction.CLARIFY,
                factor_scores=[],
            )

    def test_confidence_too_high(self):
        """Test confidence above 1 raises error."""
        with pytest.raises(ValueError, match="overall_confidence must be between"):
            AssessmentResult(
                overall_confidence=1.1,
                tier=ConfidenceTier.HIGH,
                recommended_action=AssessmentAction.EXECUTE,
                factor_scores=[],
            )

    def test_to_confidence_assessment_execute(self):
        """Test conversion to ConfidenceAssessment with EXECUTE action."""
        result = AssessmentResult(
            overall_confidence=0.95,
            tier=ConfidenceTier.VERY_HIGH,
            recommended_action=AssessmentAction.EXECUTE,
            factor_scores=[],
            explanation="Very high confidence",
        )
        assessment = result.to_confidence_assessment()
        assert assessment.overall_confidence == 0.95
        assert assessment.confidence_tier == ConfidenceTier.VERY_HIGH
        assert assessment.recommended_action == RecommendedAction.PROCEED

    def test_to_confidence_assessment_clarify(self):
        """Test conversion to ConfidenceAssessment with CLARIFY action."""
        result = AssessmentResult(
            overall_confidence=0.5,
            tier=ConfidenceTier.MEDIUM,
            recommended_action=AssessmentAction.CLARIFY,
            factor_scores=[],
        )
        assessment = result.to_confidence_assessment()
        assert assessment.recommended_action == RecommendedAction.CLARIFY

    def test_to_confidence_assessment_all_actions(self):
        """Test all action mappings to RecommendedAction."""
        action_map = {
            AssessmentAction.EXECUTE: RecommendedAction.PROCEED,
            AssessmentAction.EXECUTE_WITH_HEDGE: RecommendedAction.PROCEED_WITH_CAVEAT,
            AssessmentAction.CLARIFY: RecommendedAction.CLARIFY,
            AssessmentAction.OFFER_ALTERNATIVES: RecommendedAction.REDIRECT,
            AssessmentAction.GRACEFUL_REJECT: RecommendedAction.DECLINE,
        }
        for action, expected in action_map.items():
            result = AssessmentResult(
                overall_confidence=0.5,
                tier=ConfidenceTier.MEDIUM,
                recommended_action=action,
                factor_scores=[],
            )
            assessment = result.to_confidence_assessment()
            assert assessment.recommended_action == expected


# ============================================
# ConfidenceAssessor Tests
# ============================================

class TestConfidenceAssessor:
    """Tests for ConfidenceAssessor class."""

    @pytest.fixture
    def assessor(self):
        """Create default assessor."""
        return ConfidenceAssessor()

    @pytest.fixture
    def intent_result_high(self):
        """Create high confidence intent result."""
        return IntentResult(
            intent_name="book_flight",
            confidence=0.95,
            entities={"destination": ("Paris", 0.9)},
        )

    @pytest.fixture
    def intent_result_low(self):
        """Create low confidence intent result."""
        return IntentResult(
            intent_name="unknown",
            confidence=0.3,
        )

    @pytest.fixture
    def semantic_analysis_high(self):
        """Create high similarity semantic analysis."""
        return SemanticAnalysis(
            input_text="book a flight to Paris",
            abstraction_level=AbstractionLevel.CONCRETE,
            nearest_intents=[
                NearestIntent(intent_name="book_flight", similarity=0.95),
            ],
            temporal_references=[],
            entity_mentions=[],
        )

    @pytest.fixture
    def semantic_analysis_low(self):
        """Create low similarity semantic analysis."""
        return SemanticAnalysis(
            input_text="what is the meaning of life",
            abstraction_level=AbstractionLevel.ABSTRACT,
            nearest_intents=[
                NearestIntent(intent_name="general_query", similarity=0.3),
            ],
            temporal_references=[],
            entity_mentions=[],
        )

    @pytest.fixture
    def conversation_context_coherent(self):
        """Create coherent conversation context."""
        return ConversationDriftContext(
            session_id="test-session",
            turns=[],
            drift_history=[],
            coherence=CoherenceAnalysis(
                coherence_score=0.9,
                topic_consistency=0.88,
                intent_stability=0.85,
                coherence_trend=CoherenceTrend.STABLE,
            ),
        )

    @pytest.fixture
    def conversation_context_incoherent(self):
        """Create incoherent conversation context."""
        return ConversationDriftContext(
            session_id="test-session",
            turns=[],
            drift_history=[],
            coherence=CoherenceAnalysis(
                coherence_score=0.2,
                topic_consistency=0.25,
                intent_stability=0.3,
                coherence_trend=CoherenceTrend.DEGRADING,
            ),
        )

    # Basic Assessment Tests

    def test_assess_high_confidence(
        self,
        assessor,
        intent_result_high,
        semantic_analysis_high,
        conversation_context_coherent,
    ):
        """Test assessment with all high confidence inputs."""
        result = assessor.assess(
            intent_result=intent_result_high,
            semantic_analysis=semantic_analysis_high,
            conversation_context=conversation_context_coherent,
        )
        assert result.tier in [ConfidenceTier.HIGH, ConfidenceTier.VERY_HIGH]
        assert result.recommended_action == AssessmentAction.EXECUTE

    def test_assess_low_confidence(
        self,
        assessor,
        intent_result_low,
        semantic_analysis_low,
        conversation_context_incoherent,
    ):
        """Test assessment with all low confidence inputs."""
        result = assessor.assess(
            intent_result=intent_result_low,
            semantic_analysis=semantic_analysis_low,
            conversation_context=conversation_context_incoherent,
        )
        assert result.tier in [ConfidenceTier.LOW, ConfidenceTier.VERY_LOW]
        assert result.recommended_action in [
            AssessmentAction.OFFER_ALTERNATIVES,
            AssessmentAction.GRACEFUL_REJECT,
        ]

    def test_assess_no_inputs(self, assessor):
        """Test assessment with no inputs."""
        result = assessor.assess()
        assert result.overall_confidence < 0.5
        assert len(result.factor_scores) == 4

    def test_assess_only_intent(self, assessor, intent_result_high):
        """Test assessment with only intent result."""
        result = assessor.assess(intent_result=intent_result_high)
        assert 0.0 <= result.overall_confidence <= 1.0
        assert len(result.factor_scores) == 4

    def test_assess_only_semantic(self, assessor, semantic_analysis_high):
        """Test assessment with only semantic analysis."""
        result = assessor.assess(semantic_analysis=semantic_analysis_high)
        assert 0.0 <= result.overall_confidence <= 1.0

    def test_assess_only_context(self, assessor, conversation_context_coherent):
        """Test assessment with only conversation context."""
        result = assessor.assess(conversation_context=conversation_context_coherent)
        assert 0.0 <= result.overall_confidence <= 1.0

    # Factor Score Tests

    def test_factor_scores_have_names(self, assessor, intent_result_high):
        """Test that factor scores have proper names."""
        result = assessor.assess(intent_result=intent_result_high)
        factor_names = {f.factor_name for f in result.factor_scores}
        assert "intent_classification" in factor_names
        assert "entity_extraction" in factor_names
        assert "context_coherence" in factor_names
        assert "semantic_similarity" in factor_names

    def test_factor_scores_have_weights(self, assessor, intent_result_high):
        """Test that factor scores have weights that sum to 1."""
        result = assessor.assess(intent_result=intent_result_high)
        total_weight = sum(f.weight for f in result.factor_scores)
        assert abs(total_weight - 1.0) < 0.01

    def test_factor_scores_have_explanations(self, assessor, intent_result_high):
        """Test that factor scores have explanations."""
        result = assessor.assess(intent_result=intent_result_high)
        for factor in result.factor_scores:
            assert factor.explanation
            assert len(factor.explanation) > 0

    # Tier Determination Tests

    def test_tier_very_high(self, assessor):
        """Test VERY_HIGH tier determination."""
        result = assessor.assess_with_scores(
            intent_confidence=0.98,
            entity_confidence=0.95,
            context_coherence=0.95,
            semantic_similarity=0.96,
        )
        assert result.tier == ConfidenceTier.VERY_HIGH

    def test_tier_high(self, assessor):
        """Test HIGH tier determination."""
        result = assessor.assess_with_scores(
            intent_confidence=0.9,
            entity_confidence=0.85,
            context_coherence=0.85,
            semantic_similarity=0.85,
        )
        assert result.tier == ConfidenceTier.HIGH

    def test_tier_medium(self, assessor):
        """Test MEDIUM tier determination."""
        result = assessor.assess_with_scores(
            intent_confidence=0.6,
            entity_confidence=0.5,
            context_coherence=0.5,
            semantic_similarity=0.5,
        )
        assert result.tier == ConfidenceTier.MEDIUM

    def test_tier_low(self, assessor):
        """Test LOW tier determination."""
        result = assessor.assess_with_scores(
            intent_confidence=0.35,
            entity_confidence=0.35,
            context_coherence=0.35,
            semantic_similarity=0.35,
        )
        assert result.tier == ConfidenceTier.LOW

    def test_tier_very_low(self, assessor):
        """Test VERY_LOW tier determination."""
        result = assessor.assess_with_scores(
            intent_confidence=0.1,
            entity_confidence=0.1,
            context_coherence=0.1,
            semantic_similarity=0.1,
        )
        assert result.tier == ConfidenceTier.VERY_LOW

    # Action Recommendation Tests

    def test_action_execute_for_very_high(self, assessor):
        """Test EXECUTE action for VERY_HIGH tier."""
        result = assessor.assess_with_scores(
            intent_confidence=0.98,
            entity_confidence=0.98,
            context_coherence=0.98,
            semantic_similarity=0.98,
        )
        assert result.recommended_action == AssessmentAction.EXECUTE

    def test_action_execute_for_high(self, assessor):
        """Test EXECUTE action for HIGH tier."""
        result = assessor.assess_with_scores(
            intent_confidence=0.9,
            entity_confidence=0.9,
            context_coherence=0.9,
            semantic_similarity=0.9,
        )
        assert result.recommended_action == AssessmentAction.EXECUTE

    def test_action_clarify_for_medium(self, assessor):
        """Test CLARIFY action for MEDIUM tier."""
        result = assessor.assess_with_scores(
            intent_confidence=0.6,
            entity_confidence=0.55,
            context_coherence=0.55,
            semantic_similarity=0.55,
        )
        assert result.recommended_action == AssessmentAction.CLARIFY

    def test_action_offer_alternatives_for_low(self, assessor):
        """Test OFFER_ALTERNATIVES action for LOW tier."""
        result = assessor.assess_with_scores(
            intent_confidence=0.35,
            entity_confidence=0.35,
            context_coherence=0.35,
            semantic_similarity=0.35,
        )
        assert result.recommended_action == AssessmentAction.OFFER_ALTERNATIVES

    def test_action_graceful_reject_for_very_low(self, assessor):
        """Test GRACEFUL_REJECT action for VERY_LOW tier."""
        result = assessor.assess_with_scores(
            intent_confidence=0.1,
            entity_confidence=0.1,
            context_coherence=0.1,
            semantic_similarity=0.1,
        )
        assert result.recommended_action == AssessmentAction.GRACEFUL_REJECT

    # assess_with_scores Tests

    def test_assess_with_scores_basic(self, assessor):
        """Test assess_with_scores basic functionality."""
        result = assessor.assess_with_scores(
            intent_confidence=0.8,
            entity_confidence=0.9,
            context_coherence=0.7,
            semantic_similarity=0.85,
        )
        assert 0.0 <= result.overall_confidence <= 1.0
        assert result.tier is not None
        assert result.recommended_action is not None

    def test_assess_with_scores_default_values(self, assessor):
        """Test assess_with_scores with default values."""
        result = assessor.assess_with_scores(intent_confidence=0.8)
        # entity_confidence defaults to 1.0
        # context_coherence defaults to 0.5
        # semantic_similarity defaults to 0.5
        assert 0.0 <= result.overall_confidence <= 1.0

    def test_assess_with_scores_matches_factor_count(self, assessor):
        """Test that assess_with_scores produces 4 factors."""
        result = assessor.assess_with_scores(intent_confidence=0.8)
        assert len(result.factor_scores) == 4

    # Custom Config Tests

    def test_custom_config_intent_focused(self, intent_result_high):
        """Test assessor with intent-focused config."""
        config = ConfidenceAssessorConfig.intent_focused()
        assessor = ConfidenceAssessor(config)
        result = assessor.assess(intent_result=intent_result_high)

        # With intent-focused, intent factor should have higher weight
        intent_factor = next(
            f for f in result.factor_scores
            if f.factor_name == "intent_classification"
        )
        assert intent_factor.weight == 0.6

    def test_custom_config_context_focused(self, conversation_context_coherent):
        """Test assessor with context-focused config."""
        config = ConfidenceAssessorConfig.context_focused()
        assessor = ConfidenceAssessor(config)
        result = assessor.assess(conversation_context=conversation_context_coherent)

        # With context-focused, context factor should have higher weight
        context_factor = next(
            f for f in result.factor_scores
            if f.factor_name == "context_coherence"
        )
        assert context_factor.weight == 0.4

    # Calibration Tests

    def test_calibration_not_applied_by_default(self, assessor, intent_result_high):
        """Test that calibration is not applied by default."""
        result = assessor.assess(intent_result=intent_result_high)
        assert result.calibration is None

    def test_calibration_applied_when_enabled(self, intent_result_high):
        """Test that calibration is applied when enabled."""
        config = ConfidenceAssessorConfig(enable_calibration=True)
        assessor = ConfidenceAssessor(config)
        result = assessor.assess(intent_result=intent_result_high)
        assert result.calibration is not None
        assert result.calibration.method == "temperature_scaling"

    def test_calibration_with_temperature_above_one(self, intent_result_high):
        """Test calibration with temperature > 1 (softer probabilities)."""
        config = ConfidenceAssessorConfig(
            enable_calibration=True,
            calibration_temperature=2.0,
        )
        assessor = ConfidenceAssessor(config)
        result = assessor.assess(intent_result=intent_result_high)

        # Higher temperature should move probabilities toward 0.5
        assert result.calibration is not None
        original = result.calibration.original_score
        calibrated = result.calibration.calibrated_score

        # For high scores, calibration should reduce them slightly
        if original > 0.5:
            assert calibrated < original or abs(calibrated - original) < 0.1

    def test_calibration_with_temperature_below_one(self, intent_result_high):
        """Test calibration with temperature < 1 (sharper probabilities)."""
        config = ConfidenceAssessorConfig(
            enable_calibration=True,
            calibration_temperature=0.5,
        )
        assessor = ConfidenceAssessor(config)
        result = assessor.assess(intent_result=intent_result_high)

        # Lower temperature should move probabilities away from 0.5
        assert result.calibration is not None

    def test_calibration_temperature_one_no_change(self):
        """Test that temperature=1 results in minimal change."""
        config = ConfidenceAssessorConfig(
            enable_calibration=True,
            calibration_temperature=1.0,
        )
        assessor = ConfidenceAssessor(config)
        result = assessor.assess_with_scores(intent_confidence=0.7)

        if result.calibration:
            # Should be very close to original
            diff = abs(
                result.calibration.calibrated_score
                - result.calibration.original_score
            )
            assert diff < 0.01

    # get_tier_thresholds Tests

    def test_get_tier_thresholds(self, assessor):
        """Test get_tier_thresholds returns all thresholds."""
        thresholds = assessor.get_tier_thresholds()
        assert "very_high" in thresholds
        assert "high" in thresholds
        assert "medium_high" in thresholds
        assert "medium" in thresholds
        assert "low" in thresholds

    def test_get_tier_thresholds_values(self, assessor):
        """Test get_tier_thresholds returns correct values."""
        thresholds = assessor.get_tier_thresholds()
        assert thresholds["very_high"] == 0.95
        assert thresholds["high"] == 0.85
        assert thresholds["medium_high"] == 0.70
        assert thresholds["medium"] == 0.50
        assert thresholds["low"] == 0.30

    # Explanation Tests

    def test_explanation_included(self, assessor, intent_result_high):
        """Test that explanation is included in result."""
        result = assessor.assess(intent_result=intent_result_high)
        assert result.explanation
        assert len(result.explanation) > 0

    def test_explanation_mentions_tier(self, assessor, intent_result_high):
        """Test that explanation mentions confidence level."""
        result = assessor.assess(intent_result=intent_result_high)
        # Should contain relevant keywords
        assert any(
            word in result.explanation.lower()
            for word in ["high", "low", "medium", "confidence"]
        )

    def test_explanation_mentions_weak_factor(self, assessor):
        """Test that explanation mentions weak factor when present."""
        result = assessor.assess_with_scores(
            intent_confidence=0.9,
            entity_confidence=0.2,  # Weak factor
            context_coherence=0.8,
            semantic_similarity=0.8,
        )
        # Should mention the weak factor
        assert "entity_extraction" in result.explanation.lower()

    # ECE Tests

    def test_ece_perfect_calibration(self, assessor):
        """Test ECE with perfectly calibrated predictions."""
        # Predictions that exactly match outcomes
        predictions = [0.9, 0.9, 0.1, 0.1]
        actuals = [True, True, False, False]

        ece = assessor.calculate_expected_calibration_error(predictions, actuals)
        assert ece < 0.1  # Should be very low

    def test_ece_poor_calibration(self, assessor):
        """Test ECE with poorly calibrated predictions."""
        # High confidence predictions that are wrong
        predictions = [0.9, 0.9, 0.9, 0.9]
        actuals = [False, False, False, False]

        ece = assessor.calculate_expected_calibration_error(predictions, actuals)
        assert ece > 0.5  # Should be high

    def test_ece_empty_inputs(self, assessor):
        """Test ECE with empty inputs."""
        ece = assessor.calculate_expected_calibration_error([], [])
        assert ece == 0.0

    def test_ece_mismatched_lengths(self, assessor):
        """Test ECE with mismatched input lengths."""
        with pytest.raises(ValueError, match="same length"):
            assessor.calculate_expected_calibration_error(
                [0.5, 0.6],
                [True],
            )

    def test_ece_returns_valid_range(self, assessor):
        """Test ECE returns value in valid range."""
        predictions = [0.1, 0.3, 0.5, 0.7, 0.9]
        actuals = [False, True, True, False, True]

        ece = assessor.calculate_expected_calibration_error(predictions, actuals)
        assert 0.0 <= ece <= 1.0

    def test_ece_with_custom_bins(self, assessor):
        """Test ECE with custom number of bins."""
        predictions = [0.1, 0.3, 0.5, 0.7, 0.9]
        actuals = [False, True, True, True, True]

        ece_5_bins = assessor.calculate_expected_calibration_error(
            predictions, actuals, n_bins=5
        )
        ece_20_bins = assessor.calculate_expected_calibration_error(
            predictions, actuals, n_bins=20
        )

        # Both should be valid
        assert 0.0 <= ece_5_bins <= 1.0
        assert 0.0 <= ece_20_bins <= 1.0

    # Edge Cases

    def test_extreme_confidence_values(self, assessor):
        """Test with extreme confidence values."""
        result = assessor.assess_with_scores(
            intent_confidence=1.0,
            entity_confidence=1.0,
            context_coherence=1.0,
            semantic_similarity=1.0,
        )
        assert result.overall_confidence == 1.0
        assert result.tier == ConfidenceTier.VERY_HIGH

    def test_zero_confidence_values(self, assessor):
        """Test with zero confidence values."""
        result = assessor.assess_with_scores(
            intent_confidence=0.0,
            entity_confidence=0.0,
            context_coherence=0.0,
            semantic_similarity=0.0,
        )
        assert result.overall_confidence == 0.0
        assert result.tier == ConfidenceTier.VERY_LOW

    def test_empty_nearest_intents(self, assessor):
        """Test with empty nearest intents list."""
        semantic_analysis = SemanticAnalysis(
            input_text="test query",
            abstraction_level=AbstractionLevel.CONCRETE,
            nearest_intents=[],
            temporal_references=[],
            entity_mentions=[],
        )
        result = assessor.assess(semantic_analysis=semantic_analysis)
        # Should handle gracefully
        assert 0.0 <= result.overall_confidence <= 1.0

    def test_weighted_score_calculation(self):
        """Test that weighted scores are calculated correctly."""
        # Default weights: intent=0.4, entity=0.2, context=0.2, semantic=0.2
        assessor = ConfidenceAssessor()
        result = assessor.assess_with_scores(
            intent_confidence=1.0,  # contributes 0.4
            entity_confidence=1.0,  # contributes 0.2
            context_coherence=0.0,  # contributes 0.0
            semantic_similarity=0.0,  # contributes 0.0
        )
        # Expected: 0.4 + 0.2 + 0.0 + 0.0 = 0.6
        assert abs(result.overall_confidence - 0.6) < 0.01


# ============================================
# Integration Tests
# ============================================

class TestConfidenceAssessorIntegration:
    """Integration tests for ConfidenceAssessor."""

    def test_full_workflow_high_confidence(self):
        """Test full workflow with high confidence scenario."""
        # Create realistic inputs
        intent_result = IntentResult(
            intent_name="book_flight",
            confidence=0.92,
            entities={
                "destination": ("Paris", 0.95),
                "date": ("2024-03-15", 0.88),
            },
        )

        semantic_analysis = SemanticAnalysis(
            input_text="book a flight to Paris on March 15th",
            abstraction_level=AbstractionLevel.CONCRETE,
            nearest_intents=[
                NearestIntent(intent_name="book_flight", similarity=0.94),
                NearestIntent(intent_name="search_flights", similarity=0.78),
            ],
            temporal_references=[],
            entity_mentions=[],
        )

        conversation_context = ConversationDriftContext(
            session_id="session-123",
            turns=[
                DriftConversationTurn(
                    turn_id="turn-1",
                    turn_number=1,
                    user_input="I want to fly to Paris",
                    timestamp="2024-01-01T10:00:00Z",
                ),
            ],
            drift_history=[],
            coherence=CoherenceAnalysis(
                coherence_score=0.88,
                topic_consistency=0.85,
                intent_stability=0.9,
                coherence_trend=CoherenceTrend.STABLE,
            ),
        )

        # Create assessor and assess
        assessor = ConfidenceAssessor()
        result = assessor.assess(
            intent_result=intent_result,
            semantic_analysis=semantic_analysis,
            conversation_context=conversation_context,
        )

        # Verify high confidence result
        assert result.tier in [ConfidenceTier.HIGH, ConfidenceTier.VERY_HIGH]
        assert result.recommended_action == AssessmentAction.EXECUTE
        assert result.overall_confidence > 0.85

        # Verify conversion to ConfidenceAssessment
        assessment = result.to_confidence_assessment()
        assert assessment.recommended_action == RecommendedAction.PROCEED

    def test_full_workflow_low_confidence(self):
        """Test full workflow with low confidence scenario."""
        # Create low confidence inputs
        intent_result = IntentResult(
            intent_name="unknown",
            confidence=0.25,
        )

        semantic_analysis = SemanticAnalysis(
            input_text="what is the meaning of life",
            abstraction_level=AbstractionLevel.PHILOSOPHICAL,
            nearest_intents=[
                NearestIntent(intent_name="general_query", similarity=0.2),
            ],
            temporal_references=[],
            entity_mentions=[],
        )

        conversation_context = ConversationDriftContext(
            session_id="session-456",
            turns=[],
            drift_history=[
                DriftEvent(
                    turn_id="turn-1",
                    drift_type=DriftType.DOMAIN_SHIFT,
                    drift_score=0.8,
                    notes="Significant topic change detected",
                ),
            ],
            coherence=CoherenceAnalysis(
                coherence_score=0.15,
                topic_consistency=0.2,
                intent_stability=0.25,
                coherence_trend=CoherenceTrend.DEGRADING,
            ),
        )

        # Create assessor and assess
        assessor = ConfidenceAssessor()
        result = assessor.assess(
            intent_result=intent_result,
            semantic_analysis=semantic_analysis,
            conversation_context=conversation_context,
        )

        # Verify low confidence result
        assert result.tier in [ConfidenceTier.LOW, ConfidenceTier.VERY_LOW]
        assert result.recommended_action in [
            AssessmentAction.OFFER_ALTERNATIVES,
            AssessmentAction.GRACEFUL_REJECT,
        ]
        assert result.overall_confidence < 0.4

    def test_calibration_workflow(self):
        """Test calibration workflow."""
        # Create calibration-enabled assessor
        config = ConfidenceAssessorConfig(
            enable_calibration=True,
            calibration_temperature=1.2,
        )
        assessor = ConfidenceAssessor(config)

        # Collect predictions for ECE calculation
        predictions = []
        actuals = []

        # Simulate multiple assessments
        test_cases = [
            (0.9, True),   # High confidence, correct
            (0.8, True),   # Medium-high confidence, correct
            (0.7, False),  # Medium confidence, incorrect
            (0.3, False),  # Low confidence, correct
            (0.2, True),   # Low confidence, incorrect
        ]

        for intent_conf, actual in test_cases:
            result = assessor.assess_with_scores(intent_confidence=intent_conf)
            predictions.append(result.overall_confidence)
            actuals.append(actual)

        # Calculate ECE
        ece = assessor.calculate_expected_calibration_error(predictions, actuals)
        assert 0.0 <= ece <= 1.0
