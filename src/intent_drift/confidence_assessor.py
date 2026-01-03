"""Confidence assessor for intent drift detection.

This module provides multi-factor confidence assessment for intent classification
with calibrated thresholds and action recommendations.

Issue #81 - Task 5.4: Confidence Assessor
Part of #28 - Phase 5: Intent Drift Detection
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .types import (
    ConfidenceAssessment,
    ConfidenceFactorScore,
    ConfidenceTier,
    ConversationDriftContext,
    RecommendedAction,
    SemanticAnalysis,
)


# ============================================
# Confidence Tier Thresholds
# ============================================

class ConfidenceThresholds:
    """Threshold values for confidence tiers."""

    VERY_HIGH = 0.95  # Direct execution
    HIGH = 0.85  # Direct execution
    MEDIUM_HIGH = 0.70  # Execute with hedge
    MEDIUM = 0.50  # Clarification needed
    LOW = 0.30  # Offer alternatives
    # Below LOW = VERY_LOW (graceful rejection)


# ============================================
# Action Types
# ============================================

class AssessmentAction(Enum):
    """Actions based on confidence assessment."""

    EXECUTE = "execute"
    """Direct execution - high confidence."""

    EXECUTE_WITH_HEDGE = "execute_with_hedge"
    """Execute but mention uncertainty."""

    CLARIFY = "clarify"
    """Ask for clarification before proceeding."""

    OFFER_ALTERNATIVES = "offer_alternatives"
    """Suggest alternative interpretations."""

    GRACEFUL_REJECT = "graceful_reject"
    """Politely decline due to low confidence."""


# ============================================
# Data Classes
# ============================================

@dataclass
class IntentResult:
    """Result of intent extraction.

    Attributes:
        intent_name: Name of the detected intent
        confidence: Confidence score (0-1)
        entities: Extracted entities with confidence
        raw_score: Raw model score before normalization
    """

    intent_name: str
    confidence: float
    entities: dict[str, tuple[str, float]] = field(default_factory=dict)
    raw_score: Optional[float] = None

    def __post_init__(self):
        """Validate confidence is in valid range."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    @property
    def avg_entity_confidence(self) -> float:
        """Calculate average entity extraction confidence."""
        if not self.entities:
            return 1.0  # No entities = no entity uncertainty
        confidences = [conf for _, conf in self.entities.values()]
        return sum(confidences) / len(confidences)


@dataclass
class ConfidenceAssessorConfig:
    """Configuration for confidence assessor.

    Attributes:
        intent_weight: Weight for intent classification confidence
        entity_weight: Weight for entity extraction confidence
        context_weight: Weight for context coherence score
        semantic_weight: Weight for semantic similarity score
        high_threshold: Threshold for HIGH tier
        medium_high_threshold: Threshold for MEDIUM_HIGH tier
        medium_threshold: Threshold for MEDIUM tier
        low_threshold: Threshold for LOW tier
        enable_calibration: Whether to apply calibration
        calibration_temperature: Temperature for probability calibration
    """

    intent_weight: float = 0.4
    entity_weight: float = 0.2
    context_weight: float = 0.2
    semantic_weight: float = 0.2
    high_threshold: float = ConfidenceThresholds.HIGH
    medium_high_threshold: float = ConfidenceThresholds.MEDIUM_HIGH
    medium_threshold: float = ConfidenceThresholds.MEDIUM
    low_threshold: float = ConfidenceThresholds.LOW
    enable_calibration: bool = False
    calibration_temperature: float = 1.0

    def __post_init__(self):
        """Validate weights sum to 1.0."""
        total = (
            self.intent_weight
            + self.entity_weight
            + self.context_weight
            + self.semantic_weight
        )
        if not 0.99 <= total <= 1.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    @classmethod
    def default(cls) -> ConfidenceAssessorConfig:
        """Create default configuration."""
        return cls()

    @classmethod
    def intent_focused(cls) -> ConfidenceAssessorConfig:
        """Create configuration focused on intent confidence."""
        return cls(
            intent_weight=0.6,
            entity_weight=0.15,
            context_weight=0.15,
            semantic_weight=0.1,
        )

    @classmethod
    def context_focused(cls) -> ConfidenceAssessorConfig:
        """Create configuration focused on context coherence."""
        return cls(
            intent_weight=0.3,
            entity_weight=0.1,
            context_weight=0.4,
            semantic_weight=0.2,
        )


@dataclass
class CalibrationResult:
    """Result of probability calibration.

    Attributes:
        original_score: Score before calibration
        calibrated_score: Score after calibration
        method: Calibration method used
        temperature: Temperature parameter if applicable
    """

    original_score: float
    calibrated_score: float
    method: str
    temperature: Optional[float] = None


@dataclass
class AssessmentResult:
    """Complete confidence assessment result.

    Attributes:
        overall_confidence: Combined confidence score (0-1)
        tier: Confidence tier classification
        recommended_action: Suggested action based on confidence
        factor_scores: Individual factor confidence scores
        calibration: Calibration result if applied
        explanation: Human-readable explanation
    """

    overall_confidence: float
    tier: ConfidenceTier
    recommended_action: AssessmentAction
    factor_scores: list[ConfidenceFactorScore]
    calibration: Optional[CalibrationResult] = None
    explanation: str = ""

    def __post_init__(self):
        """Validate confidence is in valid range."""
        if not 0.0 <= self.overall_confidence <= 1.0:
            raise ValueError("overall_confidence must be between 0.0 and 1.0")

    def to_confidence_assessment(self) -> ConfidenceAssessment:
        """Convert to ConfidenceAssessment for integration.

        Returns:
            ConfidenceAssessment instance
        """
        # Map AssessmentAction to RecommendedAction
        action_map = {
            AssessmentAction.EXECUTE: RecommendedAction.PROCEED,
            AssessmentAction.EXECUTE_WITH_HEDGE: RecommendedAction.PROCEED_WITH_CAVEAT,
            AssessmentAction.CLARIFY: RecommendedAction.CLARIFY,
            AssessmentAction.OFFER_ALTERNATIVES: RecommendedAction.REDIRECT,
            AssessmentAction.GRACEFUL_REJECT: RecommendedAction.DECLINE,
        }

        return ConfidenceAssessment(
            overall_confidence=self.overall_confidence,
            confidence_tier=self.tier,
            recommended_action=action_map.get(
                self.recommended_action, RecommendedAction.CLARIFY
            ),
            factor_scores=self.factor_scores,
            explanation=self.explanation,
        )


# ============================================
# Confidence Assessor
# ============================================

class ConfidenceAssessor:
    """Assesses overall confidence in intent understanding.

    This assessor combines multiple confidence factors:
    - Intent classification confidence
    - Entity extraction confidence
    - Context coherence score
    - Semantic similarity score

    The combined score is mapped to a confidence tier which
    determines the recommended action.

    Example:
        >>> assessor = ConfidenceAssessor()
        >>> result = assessor.assess(
        ...     intent_result=intent_result,
        ...     semantic_analysis=semantic_analysis,
        ... )
        >>> print(result.tier, result.recommended_action)
    """

    def __init__(self, config: Optional[ConfidenceAssessorConfig] = None):
        """Initialize the confidence assessor.

        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self.config = config or ConfidenceAssessorConfig.default()

    def _calculate_intent_confidence(
        self, intent_result: Optional[IntentResult]
    ) -> ConfidenceFactorScore:
        """Calculate intent classification confidence factor.

        Args:
            intent_result: Intent extraction result

        Returns:
            Confidence factor score for intent
        """
        if intent_result is None:
            return ConfidenceFactorScore(
                factor_name="intent_classification",
                score=0.0,
                weight=self.config.intent_weight,
                explanation="No intent result provided",
            )

        return ConfidenceFactorScore(
            factor_name="intent_classification",
            score=intent_result.confidence,
            weight=self.config.intent_weight,
            explanation=f"Intent '{intent_result.intent_name}' detected with {intent_result.confidence:.2f} confidence",
        )

    def _calculate_entity_confidence(
        self, intent_result: Optional[IntentResult]
    ) -> ConfidenceFactorScore:
        """Calculate entity extraction confidence factor.

        Args:
            intent_result: Intent extraction result with entities

        Returns:
            Confidence factor score for entities
        """
        if intent_result is None or not intent_result.entities:
            return ConfidenceFactorScore(
                factor_name="entity_extraction",
                score=1.0,  # No entities = no entity uncertainty
                weight=self.config.entity_weight,
                explanation="No entities to extract",
            )

        avg_confidence = intent_result.avg_entity_confidence
        entity_count = len(intent_result.entities)

        return ConfidenceFactorScore(
            factor_name="entity_extraction",
            score=avg_confidence,
            weight=self.config.entity_weight,
            explanation=f"{entity_count} entities extracted with avg confidence {avg_confidence:.2f}",
        )

    def _calculate_context_confidence(
        self, conversation_context: Optional[ConversationDriftContext]
    ) -> ConfidenceFactorScore:
        """Calculate context coherence confidence factor.

        Args:
            conversation_context: Conversation drift context

        Returns:
            Confidence factor score for context
        """
        if conversation_context is None:
            return ConfidenceFactorScore(
                factor_name="context_coherence",
                score=0.5,  # Neutral if no context (first turn)
                weight=self.config.context_weight,
                explanation="No conversation context (first turn)",
            )

        # Use coherence score from context
        coherence_score = conversation_context.coherence.coherence_score

        return ConfidenceFactorScore(
            factor_name="context_coherence",
            score=coherence_score,
            weight=self.config.context_weight,
            explanation=f"Conversation coherence: {coherence_score:.2f}",
        )

    def _calculate_semantic_confidence(
        self, semantic_analysis: Optional[SemanticAnalysis]
    ) -> ConfidenceFactorScore:
        """Calculate semantic similarity confidence factor.

        Args:
            semantic_analysis: Semantic analysis result

        Returns:
            Confidence factor score for semantic similarity
        """
        if semantic_analysis is None:
            return ConfidenceFactorScore(
                factor_name="semantic_similarity",
                score=0.5,  # Neutral if no analysis
                weight=self.config.semantic_weight,
                explanation="No semantic analysis provided",
            )

        if not semantic_analysis.nearest_intents:
            return ConfidenceFactorScore(
                factor_name="semantic_similarity",
                score=0.0,
                weight=self.config.semantic_weight,
                explanation="No similar intents found",
            )

        # Use top intent similarity
        top_similarity = semantic_analysis.nearest_intents[0].similarity

        return ConfidenceFactorScore(
            factor_name="semantic_similarity",
            score=top_similarity,
            weight=self.config.semantic_weight,
            explanation=f"Top intent similarity: {top_similarity:.2f}",
        )

    def _combine_factors(
        self, factors: list[ConfidenceFactorScore]
    ) -> float:
        """Combine confidence factors into overall score.

        Args:
            factors: List of confidence factor scores

        Returns:
            Combined confidence score (0-1)
        """
        if not factors:
            return 0.0

        weighted_sum = sum(f.weighted_score for f in factors)
        total_weight = sum(f.weight for f in factors)

        if total_weight == 0:
            return 0.0

        return weighted_sum / total_weight

    def _apply_temperature_scaling(
        self, score: float, temperature: float
    ) -> CalibrationResult:
        """Apply temperature scaling for calibration.

        Temperature scaling adjusts the "sharpness" of probabilities.
        T < 1: More confident (sharper)
        T > 1: Less confident (softer)
        T = 1: No change

        Args:
            score: Original confidence score
            temperature: Temperature parameter

        Returns:
            Calibration result with adjusted score
        """
        if temperature <= 0:
            temperature = 1.0

        # Apply logit transformation, scale, then sigmoid
        # Avoid log(0) and log(1) issues
        epsilon = 1e-7
        score = max(epsilon, min(1 - epsilon, score))

        logit = math.log(score / (1 - score))
        scaled_logit = logit / temperature
        calibrated = 1 / (1 + math.exp(-scaled_logit))

        return CalibrationResult(
            original_score=score,
            calibrated_score=calibrated,
            method="temperature_scaling",
            temperature=temperature,
        )

    def _determine_tier(self, confidence: float) -> ConfidenceTier:
        """Determine confidence tier from score.

        Args:
            confidence: Confidence score (0-1)

        Returns:
            Appropriate confidence tier
        """
        if confidence >= ConfidenceThresholds.VERY_HIGH:
            return ConfidenceTier.VERY_HIGH
        elif confidence >= self.config.high_threshold:
            return ConfidenceTier.HIGH
        elif confidence >= self.config.medium_high_threshold:
            return ConfidenceTier.HIGH  # Map to HIGH for action purposes
        elif confidence >= self.config.medium_threshold:
            return ConfidenceTier.MEDIUM
        elif confidence >= self.config.low_threshold:
            return ConfidenceTier.LOW
        else:
            return ConfidenceTier.VERY_LOW

    def _recommend_action(self, tier: ConfidenceTier) -> AssessmentAction:
        """Recommend action based on confidence tier.

        Args:
            tier: Confidence tier

        Returns:
            Recommended action
        """
        action_map = {
            ConfidenceTier.VERY_HIGH: AssessmentAction.EXECUTE,
            ConfidenceTier.HIGH: AssessmentAction.EXECUTE,
            ConfidenceTier.MEDIUM: AssessmentAction.CLARIFY,
            ConfidenceTier.LOW: AssessmentAction.OFFER_ALTERNATIVES,
            ConfidenceTier.VERY_LOW: AssessmentAction.GRACEFUL_REJECT,
        }
        return action_map.get(tier, AssessmentAction.CLARIFY)

    def _generate_explanation(
        self,
        tier: ConfidenceTier,
        factors: list[ConfidenceFactorScore],
        confidence: float,
    ) -> str:
        """Generate human-readable explanation.

        Args:
            tier: Confidence tier
            factors: Factor scores
            confidence: Overall confidence

        Returns:
            Explanation string
        """
        # Find weakest factor
        weakest = min(factors, key=lambda f: f.score) if factors else None

        tier_descriptions = {
            ConfidenceTier.VERY_HIGH: "Very high confidence - proceed directly",
            ConfidenceTier.HIGH: "High confidence - safe to proceed",
            ConfidenceTier.MEDIUM: "Medium confidence - clarification recommended",
            ConfidenceTier.LOW: "Low confidence - consider alternatives",
            ConfidenceTier.VERY_LOW: "Very low confidence - cannot proceed reliably",
        }

        explanation = tier_descriptions.get(tier, "Unknown confidence level")

        if weakest and weakest.score < 0.5:
            explanation += f". Weakest factor: {weakest.factor_name} ({weakest.score:.2f})"

        return explanation

    def assess(
        self,
        intent_result: Optional[IntentResult] = None,
        semantic_analysis: Optional[SemanticAnalysis] = None,
        conversation_context: Optional[ConversationDriftContext] = None,
    ) -> AssessmentResult:
        """Assess overall confidence in intent understanding.

        Args:
            intent_result: Intent extraction result
            semantic_analysis: Semantic analysis result
            conversation_context: Conversation drift context

        Returns:
            Complete assessment result
        """
        # Calculate individual factor scores
        factors = [
            self._calculate_intent_confidence(intent_result),
            self._calculate_entity_confidence(intent_result),
            self._calculate_context_confidence(conversation_context),
            self._calculate_semantic_confidence(semantic_analysis),
        ]

        # Combine factors
        overall_confidence = self._combine_factors(factors)

        # Apply calibration if enabled
        calibration = None
        if self.config.enable_calibration:
            calibration = self._apply_temperature_scaling(
                overall_confidence,
                self.config.calibration_temperature,
            )
            overall_confidence = calibration.calibrated_score

        # Determine tier and action
        tier = self._determine_tier(overall_confidence)
        action = self._recommend_action(tier)

        # Generate explanation
        explanation = self._generate_explanation(tier, factors, overall_confidence)

        return AssessmentResult(
            overall_confidence=overall_confidence,
            tier=tier,
            recommended_action=action,
            factor_scores=factors,
            calibration=calibration,
            explanation=explanation,
        )

    def assess_with_scores(
        self,
        intent_confidence: float,
        entity_confidence: float = 1.0,
        context_coherence: float = 0.5,
        semantic_similarity: float = 0.5,
    ) -> AssessmentResult:
        """Assess confidence from raw scores.

        Convenience method when you have raw scores rather than
        full analysis objects.

        Args:
            intent_confidence: Intent classification confidence
            entity_confidence: Entity extraction confidence
            context_coherence: Context coherence score
            semantic_similarity: Semantic similarity score

        Returns:
            Complete assessment result
        """
        factors = [
            ConfidenceFactorScore(
                factor_name="intent_classification",
                score=intent_confidence,
                weight=self.config.intent_weight,
                explanation=f"Intent confidence: {intent_confidence:.2f}",
            ),
            ConfidenceFactorScore(
                factor_name="entity_extraction",
                score=entity_confidence,
                weight=self.config.entity_weight,
                explanation=f"Entity confidence: {entity_confidence:.2f}",
            ),
            ConfidenceFactorScore(
                factor_name="context_coherence",
                score=context_coherence,
                weight=self.config.context_weight,
                explanation=f"Context coherence: {context_coherence:.2f}",
            ),
            ConfidenceFactorScore(
                factor_name="semantic_similarity",
                score=semantic_similarity,
                weight=self.config.semantic_weight,
                explanation=f"Semantic similarity: {semantic_similarity:.2f}",
            ),
        ]

        # Combine factors
        overall_confidence = self._combine_factors(factors)

        # Apply calibration if enabled
        calibration = None
        if self.config.enable_calibration:
            calibration = self._apply_temperature_scaling(
                overall_confidence,
                self.config.calibration_temperature,
            )
            overall_confidence = calibration.calibrated_score

        # Determine tier and action
        tier = self._determine_tier(overall_confidence)
        action = self._recommend_action(tier)

        # Generate explanation
        explanation = self._generate_explanation(tier, factors, overall_confidence)

        return AssessmentResult(
            overall_confidence=overall_confidence,
            tier=tier,
            recommended_action=action,
            factor_scores=factors,
            calibration=calibration,
            explanation=explanation,
        )

    def get_tier_thresholds(self) -> dict[str, float]:
        """Get current tier thresholds.

        Returns:
            Dictionary of tier names to threshold values
        """
        return {
            "very_high": ConfidenceThresholds.VERY_HIGH,
            "high": self.config.high_threshold,
            "medium_high": self.config.medium_high_threshold,
            "medium": self.config.medium_threshold,
            "low": self.config.low_threshold,
        }

    def calculate_expected_calibration_error(
        self,
        predictions: list[float],
        actuals: list[bool],
        n_bins: int = 10,
    ) -> float:
        """Calculate Expected Calibration Error (ECE).

        ECE measures how well predicted probabilities match actual outcomes.
        Lower is better (0 = perfectly calibrated).

        Args:
            predictions: Predicted probabilities
            actuals: Actual outcomes (True/False)
            n_bins: Number of bins for calibration

        Returns:
            Expected Calibration Error (0-1)
        """
        if len(predictions) != len(actuals):
            raise ValueError("predictions and actuals must have same length")

        if not predictions:
            return 0.0

        # Create bins
        bin_boundaries = [i / n_bins for i in range(n_bins + 1)]
        bin_accuracies = []
        bin_confidences = []
        bin_counts = []

        for i in range(n_bins):
            low, high = bin_boundaries[i], bin_boundaries[i + 1]

            # Find predictions in this bin
            in_bin = [
                (p, a) for p, a in zip(predictions, actuals)
                if low <= p < high or (i == n_bins - 1 and p == high)
            ]

            if in_bin:
                bin_preds, bin_acts = zip(*in_bin)
                bin_accuracies.append(sum(bin_acts) / len(bin_acts))
                bin_confidences.append(sum(bin_preds) / len(bin_preds))
                bin_counts.append(len(bin_acts))
            else:
                bin_accuracies.append(0.0)
                bin_confidences.append(0.0)
                bin_counts.append(0)

        # Calculate weighted ECE
        total = sum(bin_counts)
        if total == 0:
            return 0.0

        ece = sum(
            (count / total) * abs(acc - conf)
            for acc, conf, count in zip(bin_accuracies, bin_confidences, bin_counts)
        )

        return ece
