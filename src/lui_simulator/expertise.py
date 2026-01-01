"""
Expertise Detection Algorithm for LUI Simulator.
Weighted scoring model for adaptive expertise level determination.

Issue #45 - Phase 2: Adaptive Interface Personalization

Algorithm Overview:
- Command Fluency (30%): Efficient command formulation
- Success Rate (25%): Task completion effectiveness
- Self-Sufficiency (25%): Independence from assistance
- Engagement (20%): Consistent interaction patterns

Level Thresholds:
- NOVICE: 0.0 - 0.2
- BEGINNER: 0.2 - 0.4
- INTERMEDIATE: 0.4 - 0.6
- ADVANCED: 0.6 - 0.8
- EXPERT: 0.8 - 1.0

Uses Exponential Moving Average (EMA) with alpha=0.3 for score smoothing.
"""

import math
import statistics
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .metrics import (
    InteractionOutcome,
    InteractionRecord,
    MetricsWindow,
    TrendDirection,
)


class ExpertiseLevel(Enum):
    """User expertise level matching BAML ExpertiseLevel enum."""
    NOVICE = "NOVICE"
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


@dataclass
class ExpertiseFactor:
    """Individual factor contributing to expertise score."""
    factor_name: str
    weight: float
    raw_value: float
    weighted_value: float
    confidence: float
    evidence: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate factor values."""
        if not 0 <= self.weight <= 1:
            raise ValueError(f"Weight must be 0-1, got {self.weight}")
        if not 0 <= self.raw_value <= 1:
            raise ValueError(f"Raw value must be 0-1, got {self.raw_value}")
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Confidence must be 0-1, got {self.confidence}")


@dataclass
class ExpertiseFactorBreakdown:
    """Complete breakdown of expertise factors."""
    command_fluency: ExpertiseFactor
    success_rate: ExpertiseFactor
    self_sufficiency: ExpertiseFactor
    engagement: ExpertiseFactor

    def total_score(self) -> float:
        """Calculate total weighted score."""
        return (
            self.command_fluency.weighted_value +
            self.success_rate.weighted_value +
            self.self_sufficiency.weighted_value +
            self.engagement.weighted_value
        )


@dataclass
class LevelThreshold:
    """Threshold configuration for an expertise level."""
    level: ExpertiseLevel
    min_score: float
    max_score: float
    description: str


@dataclass
class ColdStartConfig:
    """Configuration for handling cold start scenarios."""
    min_interactions: int = 10
    default_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE
    default_score: float = 0.5
    default_confidence: float = 0.3
    ramp_up_interactions: int = 50


@dataclass
class ExpertiseDetectionConfig:
    """Configuration for expertise detection algorithm."""
    # Factor weights (must sum to 1.0)
    command_fluency_weight: float = 0.30
    success_rate_weight: float = 0.25
    self_sufficiency_weight: float = 0.25
    engagement_weight: float = 0.20

    # EMA configuration
    ema_alpha: float = 0.3

    # Level thresholds
    upgrade_buffer: float = 0.05
    downgrade_buffer: float = 0.05

    # Cold start
    cold_start: ColdStartConfig = field(default_factory=ColdStartConfig)

    # Stability
    stability_window: int = 5
    stability_threshold: float = 0.1

    def __post_init__(self):
        """Validate configuration."""
        total_weight = (
            self.command_fluency_weight +
            self.success_rate_weight +
            self.self_sufficiency_weight +
            self.engagement_weight
        )
        if not math.isclose(total_weight, 1.0, rel_tol=1e-6):
            raise ValueError(f"Factor weights must sum to 1.0, got {total_weight}")
        if not 0 < self.ema_alpha <= 1:
            raise ValueError(f"EMA alpha must be (0, 1], got {self.ema_alpha}")


@dataclass
class ExpertiseEstimate:
    """Result of expertise level estimation."""
    estimated_level: ExpertiseLevel
    expertise_score: float
    previous_score: Optional[float]
    score_delta: Optional[float]
    factor_breakdown: ExpertiseFactorBreakdown
    confidence: float
    is_cold_start: bool
    cold_start_reason: Optional[str]
    interactions_analyzed: int
    ema_alpha: float
    ema_applied: bool
    level_stable: bool
    recommended_action: Optional[str]
    action_rationale: Optional[str]


class ExpertiseDetector:
    """
    Expertise detection algorithm using weighted scoring model.

    Uses Exponential Moving Average (EMA) to smooth expertise scores
    over time and avoid rapid level changes.
    """

    # Default level thresholds
    DEFAULT_THRESHOLDS = [
        LevelThreshold(ExpertiseLevel.NOVICE, 0.0, 0.2, "New to the system, needs extensive guidance"),
        LevelThreshold(ExpertiseLevel.BEGINNER, 0.2, 0.4, "Some familiarity, still learning"),
        LevelThreshold(ExpertiseLevel.INTERMEDIATE, 0.4, 0.6, "Regular user, comfortable with basics"),
        LevelThreshold(ExpertiseLevel.ADVANCED, 0.6, 0.8, "Power user, uses advanced features"),
        LevelThreshold(ExpertiseLevel.EXPERT, 0.8, 1.0, "Deep system knowledge, optimal efficiency"),
    ]

    def __init__(self, config: Optional[ExpertiseDetectionConfig] = None):
        """
        Initialize the expertise detector.

        Args:
            config: Detection configuration. Uses defaults if not provided.
        """
        self.config = config or ExpertiseDetectionConfig()
        self._estimate_history: list[ExpertiseEstimate] = []
        self._current_estimate: Optional[ExpertiseEstimate] = None

    @property
    def current_estimate(self) -> Optional[ExpertiseEstimate]:
        """Get the most recent expertise estimate."""
        return self._current_estimate

    @property
    def estimate_history(self) -> list[ExpertiseEstimate]:
        """Get the history of expertise estimates."""
        return list(self._estimate_history)

    def estimate_expertise(
        self,
        interactions: list[InteractionRecord],
        metrics_window: Optional[MetricsWindow] = None,
    ) -> ExpertiseEstimate:
        """
        Estimate user expertise from interaction data.

        Args:
            interactions: List of recent interaction records.
            metrics_window: Optional pre-computed metrics window.

        Returns:
            ExpertiseEstimate with level, score, and factor breakdown.
        """
        num_interactions = len(interactions)

        # Check for cold start
        is_cold_start = num_interactions < self.config.cold_start.min_interactions
        cold_start_reason = None

        if num_interactions == 0:
            # No data at all - return default
            return self._create_default_estimate(
                cold_start_reason="No interaction data available"
            )

        if is_cold_start:
            cold_start_reason = f"Only {num_interactions} interactions (minimum: {self.config.cold_start.min_interactions})"

        # Calculate factor breakdown
        factor_breakdown = self._calculate_factors(interactions, metrics_window)

        # Calculate raw score
        raw_score = factor_breakdown.total_score()

        # Apply EMA if we have previous estimates
        previous_score = self._current_estimate.expertise_score if self._current_estimate else None
        ema_applied = previous_score is not None

        if ema_applied:
            expertise_score = self._apply_ema(raw_score, previous_score)
            score_delta = expertise_score - previous_score
        else:
            expertise_score = raw_score
            score_delta = None

        # Calculate confidence
        confidence = self._calculate_confidence(
            num_interactions,
            factor_breakdown,
            is_cold_start
        )

        # Determine level from score
        estimated_level = self._score_to_level(expertise_score)

        # Check for level transition with hysteresis
        recommended_action, action_rationale = self._evaluate_transition(
            expertise_score,
            estimated_level
        )

        # Check stability
        level_stable = self._is_level_stable()

        estimate = ExpertiseEstimate(
            estimated_level=estimated_level,
            expertise_score=expertise_score,
            previous_score=previous_score,
            score_delta=score_delta,
            factor_breakdown=factor_breakdown,
            confidence=confidence,
            is_cold_start=is_cold_start,
            cold_start_reason=cold_start_reason,
            interactions_analyzed=num_interactions,
            ema_alpha=self.config.ema_alpha,
            ema_applied=ema_applied,
            level_stable=level_stable,
            recommended_action=recommended_action,
            action_rationale=action_rationale,
        )

        # Update history
        self._current_estimate = estimate
        self._estimate_history.append(estimate)

        # Trim history to stability window size * 2
        max_history = self.config.stability_window * 2
        if len(self._estimate_history) > max_history:
            self._estimate_history = self._estimate_history[-max_history:]

        return estimate

    def _calculate_factors(
        self,
        interactions: list[InteractionRecord],
        metrics_window: Optional[MetricsWindow] = None,
    ) -> ExpertiseFactorBreakdown:
        """Calculate all expertise factors from interactions."""
        # Command Fluency (30%)
        command_fluency = self._calculate_command_fluency(interactions)

        # Success Rate (25%)
        success_rate = self._calculate_success_rate(interactions, metrics_window)

        # Self-Sufficiency (25%)
        self_sufficiency = self._calculate_self_sufficiency(interactions, metrics_window)

        # Engagement (20%)
        engagement = self._calculate_engagement(interactions, metrics_window)

        return ExpertiseFactorBreakdown(
            command_fluency=command_fluency,
            success_rate=success_rate,
            self_sufficiency=self_sufficiency,
            engagement=engagement,
        )

    def _calculate_command_fluency(
        self,
        interactions: list[InteractionRecord],
    ) -> ExpertiseFactor:
        """
        Calculate command fluency factor (30%).

        Measures:
        - Shortcut usage rate
        - Input efficiency (shorter inputs for same intent type)
        - Complete parameter provision
        """
        if not interactions:
            return self._empty_factor("command_fluency", self.config.command_fluency_weight)

        evidence = []

        # Shortcut usage rate (0-1)
        shortcut_count = sum(1 for i in interactions if i.used_shortcut)
        shortcut_rate = shortcut_count / len(interactions)
        evidence.append(f"Shortcut usage: {shortcut_rate:.1%} ({shortcut_count}/{len(interactions)})")

        # Parameter completeness (0-1)
        param_scores = []
        for i in interactions:
            if i.parameters_required > 0:
                param_scores.append(i.parameters_provided / i.parameters_required)
            else:
                param_scores.append(1.0)  # No params required = perfect
        param_completeness = statistics.mean(param_scores) if param_scores else 0.5
        evidence.append(f"Parameter completeness: {param_completeness:.1%}")

        # Input efficiency (normalized by intent type)
        # Use inverse of average input length, normalized to 0-1
        # Shorter inputs (relative to average) = higher efficiency
        input_lengths = [i.input_length for i in interactions]
        if input_lengths:
            avg_length = statistics.mean(input_lengths)
            # Normalize: 20 chars = 1.0 efficiency, 200 chars = 0.1 efficiency
            # Using log scale for smoother curve
            if avg_length > 0:
                efficiency = max(0.1, min(1.0, 1.0 - (math.log10(avg_length) - 1.3) / 1.5))
            else:
                efficiency = 1.0
            evidence.append(f"Input efficiency: {efficiency:.2f} (avg length: {avg_length:.0f})")
        else:
            efficiency = 0.5

        # Combine factors with internal weights
        # Shortcuts: 40%, Parameters: 35%, Input efficiency: 25%
        raw_value = (
            shortcut_rate * 0.40 +
            param_completeness * 0.35 +
            efficiency * 0.25
        )

        # Confidence based on sample size
        confidence = min(1.0, len(interactions) / 20)

        return ExpertiseFactor(
            factor_name="command_fluency",
            weight=self.config.command_fluency_weight,
            raw_value=raw_value,
            weighted_value=raw_value * self.config.command_fluency_weight,
            confidence=confidence,
            evidence=evidence,
        )

    def _calculate_success_rate(
        self,
        interactions: list[InteractionRecord],
        metrics_window: Optional[MetricsWindow] = None,
    ) -> ExpertiseFactor:
        """
        Calculate success rate factor (25%).

        Measures:
        - SUCCESS and PARTIAL_SUCCESS outcomes
        - Low error counts
        - Few retries
        """
        if not interactions:
            return self._empty_factor("success_rate", self.config.success_rate_weight)

        evidence = []

        # Use metrics window if available, otherwise calculate
        if metrics_window:
            success_ratio = metrics_window.success_rate + (metrics_window.partial_success_rate * 0.5)
            evidence.append(f"Success rate: {metrics_window.success_rate:.1%}")
            evidence.append(f"Partial success rate: {metrics_window.partial_success_rate:.1%}")
            error_rate = metrics_window.error_rate
            retry_rate = metrics_window.avg_retries
        else:
            # Calculate from interactions
            success_count = sum(1 for i in interactions if i.outcome == InteractionOutcome.SUCCESS)
            partial_count = sum(1 for i in interactions if i.outcome == InteractionOutcome.PARTIAL_SUCCESS)
            success_ratio = (success_count + partial_count * 0.5) / len(interactions)
            evidence.append(f"Success: {success_count}/{len(interactions)}, Partial: {partial_count}")

            error_rate = statistics.mean([i.error_count for i in interactions])
            retry_rate = statistics.mean([i.retries for i in interactions])

        evidence.append(f"Error rate: {error_rate:.2f} per interaction")
        evidence.append(f"Retry rate: {retry_rate:.2f} per interaction")

        # Normalize error and retry rates (0 = perfect, 3+ = 0)
        error_score = max(0, 1 - error_rate / 3)
        retry_score = max(0, 1 - retry_rate / 3)

        # Combine: Success 60%, Errors 25%, Retries 15%
        raw_value = (
            success_ratio * 0.60 +
            error_score * 0.25 +
            retry_score * 0.15
        )

        confidence = min(1.0, len(interactions) / 20)

        return ExpertiseFactor(
            factor_name="success_rate",
            weight=self.config.success_rate_weight,
            raw_value=raw_value,
            weighted_value=raw_value * self.config.success_rate_weight,
            confidence=confidence,
            evidence=evidence,
        )

    def _calculate_self_sufficiency(
        self,
        interactions: list[InteractionRecord],
        metrics_window: Optional[MetricsWindow] = None,
    ) -> ExpertiseFactor:
        """
        Calculate self-sufficiency factor (25%).

        Measures:
        - No help requests
        - No disambiguation needed
        - Confident interactions (high intent confidence)
        """
        if not interactions:
            return self._empty_factor("self_sufficiency", self.config.self_sufficiency_weight)

        evidence = []

        # Help request rate (0 = perfect, 1 = always needs help)
        if metrics_window:
            help_rate = metrics_window.help_rate
            disambiguation_rate = metrics_window.disambiguation_rate
        else:
            help_count = sum(1 for i in interactions if i.help_requested)
            help_rate = help_count / len(interactions)
            disambig_count = sum(1 for i in interactions if i.disambiguation_needed)
            disambiguation_rate = disambig_count / len(interactions)

        evidence.append(f"Help request rate: {help_rate:.1%}")
        evidence.append(f"Disambiguation rate: {disambiguation_rate:.1%}")

        # Intent confidence average
        intent_confidences = [i.intent_confidence for i in interactions]
        avg_intent_confidence = statistics.mean(intent_confidences) if intent_confidences else 0.5
        evidence.append(f"Avg intent confidence: {avg_intent_confidence:.1%}")

        # Invert help and disambiguation (lower = better)
        help_score = 1 - help_rate
        disambig_score = 1 - disambiguation_rate

        # Combine: No help 40%, No disambiguation 35%, Intent confidence 25%
        raw_value = (
            help_score * 0.40 +
            disambig_score * 0.35 +
            avg_intent_confidence * 0.25
        )

        confidence = min(1.0, len(interactions) / 20)

        return ExpertiseFactor(
            factor_name="self_sufficiency",
            weight=self.config.self_sufficiency_weight,
            raw_value=raw_value,
            weighted_value=raw_value * self.config.self_sufficiency_weight,
            confidence=confidence,
            evidence=evidence,
        )

    def _calculate_engagement(
        self,
        interactions: list[InteractionRecord],
        metrics_window: Optional[MetricsWindow] = None,
    ) -> ExpertiseFactor:
        """
        Calculate engagement factor (20%).

        Measures:
        - Interaction frequency (based on timestamps)
        - Session consistency
        - Feature exploration (variety of intents)
        """
        if not interactions:
            return self._empty_factor("engagement", self.config.engagement_weight)

        evidence = []

        # Interaction frequency - based on number of interactions in window
        # Normalize: 1 interaction = 0.1, 50+ = 1.0
        frequency_score = min(1.0, len(interactions) / 50)
        evidence.append(f"Interactions in window: {len(interactions)}")

        # Intent variety - number of unique intents
        unique_intents = set(i.intent_detected for i in interactions)
        variety_score = min(1.0, len(unique_intents) / 10)
        evidence.append(f"Unique intents: {len(unique_intents)}")

        # Session consistency - based on session diversity
        unique_sessions = set(i.session_id for i in interactions)
        session_score = min(1.0, len(unique_sessions) / 5)
        evidence.append(f"Unique sessions: {len(unique_sessions)}")

        # Abandonment penalty
        if metrics_window:
            abandonment_rate = metrics_window.abandonment_rate
        else:
            abandoned = sum(1 for i in interactions if i.outcome == InteractionOutcome.ABANDONED)
            abandonment_rate = abandoned / len(interactions)

        abandonment_penalty = abandonment_rate * 0.3  # Up to 30% penalty
        evidence.append(f"Abandonment rate: {abandonment_rate:.1%}")

        # Combine: Frequency 35%, Variety 35%, Sessions 30%, minus penalty
        raw_value = max(0, (
            frequency_score * 0.35 +
            variety_score * 0.35 +
            session_score * 0.30 -
            abandonment_penalty
        ))

        confidence = min(1.0, len(interactions) / 20)

        return ExpertiseFactor(
            factor_name="engagement",
            weight=self.config.engagement_weight,
            raw_value=raw_value,
            weighted_value=raw_value * self.config.engagement_weight,
            confidence=confidence,
            evidence=evidence,
        )

    def _empty_factor(self, name: str, weight: float) -> ExpertiseFactor:
        """Create an empty/default factor for when no data is available."""
        return ExpertiseFactor(
            factor_name=name,
            weight=weight,
            raw_value=0.5,
            weighted_value=0.5 * weight,
            confidence=0.0,
            evidence=["No data available - using default"],
        )

    def _apply_ema(self, current_score: float, previous_score: float) -> float:
        """
        Apply Exponential Moving Average smoothing.

        Formula: new = alpha * current + (1 - alpha) * previous
        """
        alpha = self.config.ema_alpha
        return alpha * current_score + (1 - alpha) * previous_score

    def _calculate_confidence(
        self,
        num_interactions: int,
        factor_breakdown: ExpertiseFactorBreakdown,
        is_cold_start: bool,
    ) -> float:
        """Calculate overall confidence in the expertise estimate."""
        # Base confidence from sample size
        sample_confidence = min(1.0, num_interactions / self.config.cold_start.ramp_up_interactions)

        # Factor confidence average
        factor_confidences = [
            factor_breakdown.command_fluency.confidence,
            factor_breakdown.success_rate.confidence,
            factor_breakdown.self_sufficiency.confidence,
            factor_breakdown.engagement.confidence,
        ]
        factor_confidence = statistics.mean(factor_confidences)

        # Combine: Sample 60%, Factors 40%
        base_confidence = sample_confidence * 0.6 + factor_confidence * 0.4

        # Cold start penalty
        if is_cold_start:
            # Reduce confidence proportionally to how far below minimum we are
            cold_start_ratio = num_interactions / self.config.cold_start.min_interactions
            base_confidence *= cold_start_ratio

        return min(1.0, max(0.1, base_confidence))

    def _score_to_level(self, score: float) -> ExpertiseLevel:
        """Convert numeric score to expertise level."""
        for threshold in self.DEFAULT_THRESHOLDS:
            if threshold.min_score <= score < threshold.max_score:
                return threshold.level

        # Edge case: exactly 1.0
        if score >= 1.0:
            return ExpertiseLevel.EXPERT

        return ExpertiseLevel.INTERMEDIATE  # Fallback

    def _evaluate_transition(
        self,
        score: float,
        new_level: ExpertiseLevel,
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Evaluate if level transition should be recommended.

        Applies hysteresis to prevent rapid oscillation.
        """
        if not self._current_estimate:
            return None, None

        current_level = self._current_estimate.estimated_level

        if new_level == current_level:
            return "MAINTAIN", "Score within current level range"

        # Get threshold info for current level
        current_threshold = next(
            (t for t in self.DEFAULT_THRESHOLDS if t.level == current_level),
            None
        )

        if not current_threshold:
            return None, None

        # Check for upgrade (need to exceed max + buffer)
        if score > current_threshold.max_score + self.config.upgrade_buffer:
            return "UPGRADE", f"Score {score:.2f} exceeds level maximum {current_threshold.max_score} + buffer"

        # Check for downgrade (need to fall below min - buffer)
        if score < current_threshold.min_score - self.config.downgrade_buffer:
            return "DOWNGRADE", f"Score {score:.2f} below level minimum {current_threshold.min_score} - buffer"

        # In buffer zone - monitor but don't change
        return "MONITOR", f"Score {score:.2f} in transition buffer zone"

    def _is_level_stable(self) -> bool:
        """Check if the expertise level has been stable recently."""
        if len(self._estimate_history) < self.config.stability_window:
            return False

        recent = self._estimate_history[-self.config.stability_window:]
        scores = [e.expertise_score for e in recent]

        # Check variance
        try:
            variance = statistics.variance(scores)
            return variance < self.config.stability_threshold ** 2
        except statistics.StatisticsError:
            return False

    def _create_default_estimate(self, cold_start_reason: str) -> ExpertiseEstimate:
        """Create a default estimate for cold start scenarios."""
        config = self.config.cold_start

        def default_factor(name: str, weight: float) -> ExpertiseFactor:
            return ExpertiseFactor(
                factor_name=name,
                weight=weight,
                raw_value=config.default_score,
                weighted_value=config.default_score * weight,
                confidence=config.default_confidence,
                evidence=["Cold start - using defaults"],
            )

        factor_breakdown = ExpertiseFactorBreakdown(
            command_fluency=default_factor("command_fluency", self.config.command_fluency_weight),
            success_rate=default_factor("success_rate", self.config.success_rate_weight),
            self_sufficiency=default_factor("self_sufficiency", self.config.self_sufficiency_weight),
            engagement=default_factor("engagement", self.config.engagement_weight),
        )

        return ExpertiseEstimate(
            estimated_level=config.default_level,
            expertise_score=config.default_score,
            previous_score=None,
            score_delta=None,
            factor_breakdown=factor_breakdown,
            confidence=config.default_confidence,
            is_cold_start=True,
            cold_start_reason=cold_start_reason,
            interactions_analyzed=0,
            ema_alpha=self.config.ema_alpha,
            ema_applied=False,
            level_stable=False,
            recommended_action=None,
            action_rationale="Cold start - insufficient data for recommendations",
        )

    def get_expertise_trend(self) -> TrendDirection:
        """
        Analyze the trend in expertise scores over recent estimates.

        Returns:
            TrendDirection indicating if expertise is IMPROVING, STABLE, or DECLINING.
        """
        if len(self._estimate_history) < 3:
            return TrendDirection.STABLE

        recent = self._estimate_history[-min(10, len(self._estimate_history)):]
        scores = [e.expertise_score for e in recent]

        # Compare first half to second half
        mid = len(scores) // 2
        first_half_avg = statistics.mean(scores[:mid])
        second_half_avg = statistics.mean(scores[mid:])

        delta = second_half_avg - first_half_avg

        if delta > 0.05:
            return TrendDirection.IMPROVING
        elif delta < -0.05:
            return TrendDirection.DECLINING
        else:
            return TrendDirection.STABLE

    def reset(self) -> None:
        """Reset the detector state, clearing all history."""
        self._estimate_history.clear()
        self._current_estimate = None
