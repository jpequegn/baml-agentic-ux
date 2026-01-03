"""Quality Scorer for Conversational Testing Framework.

This module provides multi-dimensional quality scoring for conversational responses.

Issue #92 - Task 6.4: Quality Scorer
Part of #29 - Phase 6: Conversational Testing Framework
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from .types import QualityScores, QualityThresholds, TurnResult


# ============================================
# Quality Dimension Types
# ============================================


class QualityDimension(Enum):
    """Dimensions of quality being measured."""

    COHERENCE = "coherence"
    NATURALNESS = "naturalness"
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    CONTEXT_RETENTION = "context_retention"


@dataclass
class DimensionScore:
    """Score for a single quality dimension with breakdown."""

    dimension: QualityDimension
    score: float
    sub_scores: dict[str, float] = field(default_factory=dict)
    explanation: Optional[str] = None
    confidence: float = 1.0


@dataclass
class CoherenceBreakdown:
    """Detailed coherence score breakdown."""

    topic_consistency: float = 0.0
    reference_resolution: float = 0.0
    logical_flow: float = 0.0
    no_contradictions: float = 1.0

    @property
    def overall(self) -> float:
        """Calculate weighted overall coherence score."""
        weights = {
            "topic_consistency": 0.30,
            "reference_resolution": 0.25,
            "logical_flow": 0.25,
            "no_contradictions": 0.20,
        }
        return (
            self.topic_consistency * weights["topic_consistency"]
            + self.reference_resolution * weights["reference_resolution"]
            + self.logical_flow * weights["logical_flow"]
            + self.no_contradictions * weights["no_contradictions"]
        )


@dataclass
class NaturalnessBreakdown:
    """Detailed naturalness score breakdown."""

    fluency: float = 0.0
    appropriateness: float = 0.0
    diversity: float = 0.0
    human_likeness: float = 0.0

    @property
    def overall(self) -> float:
        """Calculate weighted overall naturalness score."""
        weights = {
            "fluency": 0.30,
            "appropriateness": 0.30,
            "diversity": 0.20,
            "human_likeness": 0.20,
        }
        return (
            self.fluency * weights["fluency"]
            + self.appropriateness * weights["appropriateness"]
            + self.diversity * weights["diversity"]
            + self.human_likeness * weights["human_likeness"]
        )


@dataclass
class ContextRetentionBreakdown:
    """Detailed context retention score breakdown."""

    entity_tracking: float = 0.0
    state_preservation: float = 0.0
    reference_accuracy: float = 0.0

    @property
    def overall(self) -> float:
        """Calculate weighted overall context retention score."""
        weights = {
            "entity_tracking": 0.40,
            "state_preservation": 0.35,
            "reference_accuracy": 0.25,
        }
        return (
            self.entity_tracking * weights["entity_tracking"]
            + self.state_preservation * weights["state_preservation"]
            + self.reference_accuracy * weights["reference_accuracy"]
        )


@dataclass
class ConversationQuality:
    """Overall quality assessment for a conversation."""

    coherence: DimensionScore
    naturalness: DimensionScore
    accuracy: DimensionScore
    relevance: DimensionScore
    context_retention: DimensionScore
    overall_score: float
    passed_thresholds: bool
    threshold_failures: list[str] = field(default_factory=list)

    def to_quality_scores(self) -> QualityScores:
        """Convert to QualityScores for test results."""
        return QualityScores(
            coherence=self.coherence.score,
            naturalness=self.naturalness.score,
            accuracy=self.accuracy.score,
            relevance=self.relevance.score,
            avg_confidence=sum(
                [
                    self.coherence.confidence,
                    self.naturalness.confidence,
                    self.accuracy.confidence,
                    self.relevance.confidence,
                    self.context_retention.confidence,
                ]
            )
            / 5,
            max_drift_score=0.0,  # Will be set by runner
            avg_latency_ms=0.0,  # Will be set by runner
        )


@dataclass
class QualityScorerConfig:
    """Configuration for the quality scorer."""

    thresholds: QualityThresholds = field(default_factory=QualityThresholds)
    use_llm_evaluation: bool = False
    llm_evaluator: Optional[Callable[[str, str], dict[str, float]]] = None
    min_response_length: int = 1
    max_repetition_ratio: float = 0.5
    enable_detailed_breakdown: bool = True


# ============================================
# Quality Scorer Implementation
# ============================================


class QualityScorer:
    """Multi-dimensional quality scoring for conversational responses."""

    def __init__(self, config: Optional[QualityScorerConfig] = None) -> None:
        """Initialize the quality scorer."""
        self.config = config or QualityScorerConfig()
        self._conversation_history: list[str] = []
        self._entity_mentions: dict[str, list[str]] = {}
        self._context_state: dict[str, Any] = {}

    def reset(self) -> None:
        """Reset scorer state for a new conversation."""
        self._conversation_history = []
        self._entity_mentions = {}
        self._context_state = {}

    def score_turn(
        self,
        turn_result: TurnResult,
        context: Optional[dict[str, Any]] = None,
        expected_entities: Optional[list[str]] = None,
    ) -> dict[str, DimensionScore]:
        """Score a single conversation turn.

        Args:
            turn_result: The turn result to score.
            context: Current conversation context.
            expected_entities: Entities expected to be tracked.

        Returns:
            Dictionary of dimension scores.
        """
        response = turn_result.actual_response or ""
        user_input = turn_result.input

        # Update history
        self._conversation_history.append(user_input)
        if response:
            self._conversation_history.append(response)

        # Update context
        if context:
            self._context_state.update(context)

        # Score each dimension
        scores = {}

        # Coherence
        coherence = self._score_coherence(response, user_input)
        scores[QualityDimension.COHERENCE.value] = DimensionScore(
            dimension=QualityDimension.COHERENCE,
            score=coherence.overall,
            sub_scores={
                "topic_consistency": coherence.topic_consistency,
                "reference_resolution": coherence.reference_resolution,
                "logical_flow": coherence.logical_flow,
                "no_contradictions": coherence.no_contradictions,
            },
        )

        # Naturalness
        naturalness = self._score_naturalness(response)
        scores[QualityDimension.NATURALNESS.value] = DimensionScore(
            dimension=QualityDimension.NATURALNESS,
            score=naturalness.overall,
            sub_scores={
                "fluency": naturalness.fluency,
                "appropriateness": naturalness.appropriateness,
                "diversity": naturalness.diversity,
                "human_likeness": naturalness.human_likeness,
            },
        )

        # Accuracy (based on detected intent matching)
        accuracy = self._score_accuracy(turn_result)
        scores[QualityDimension.ACCURACY.value] = DimensionScore(
            dimension=QualityDimension.ACCURACY,
            score=accuracy,
        )

        # Relevance
        relevance = self._score_relevance(response, user_input)
        scores[QualityDimension.RELEVANCE.value] = DimensionScore(
            dimension=QualityDimension.RELEVANCE,
            score=relevance,
        )

        # Context retention
        retention = self._score_context_retention(response, expected_entities)
        scores[QualityDimension.CONTEXT_RETENTION.value] = DimensionScore(
            dimension=QualityDimension.CONTEXT_RETENTION,
            score=retention.overall,
            sub_scores={
                "entity_tracking": retention.entity_tracking,
                "state_preservation": retention.state_preservation,
                "reference_accuracy": retention.reference_accuracy,
            },
        )

        return scores

    def score_conversation(
        self,
        turn_results: list[TurnResult],
        contexts: Optional[list[dict[str, Any]]] = None,
    ) -> ConversationQuality:
        """Score an entire conversation.

        Args:
            turn_results: All turn results from the conversation.
            contexts: Optional contexts for each turn.

        Returns:
            ConversationQuality with aggregated scores.
        """
        self.reset()

        all_scores: list[dict[str, DimensionScore]] = []

        for i, turn_result in enumerate(turn_results):
            context = contexts[i] if contexts and i < len(contexts) else None
            turn_scores = self.score_turn(turn_result, context)
            all_scores.append(turn_scores)

        # Aggregate scores across turns
        coherence_scores = [
            s[QualityDimension.COHERENCE.value].score
            for s in all_scores
            if QualityDimension.COHERENCE.value in s
        ]
        naturalness_scores = [
            s[QualityDimension.NATURALNESS.value].score
            for s in all_scores
            if QualityDimension.NATURALNESS.value in s
        ]
        accuracy_scores = [
            s[QualityDimension.ACCURACY.value].score
            for s in all_scores
            if QualityDimension.ACCURACY.value in s
        ]
        relevance_scores = [
            s[QualityDimension.RELEVANCE.value].score
            for s in all_scores
            if QualityDimension.RELEVANCE.value in s
        ]
        retention_scores = [
            s[QualityDimension.CONTEXT_RETENTION.value].score
            for s in all_scores
            if QualityDimension.CONTEXT_RETENTION.value in s
        ]

        avg_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0
        avg_naturalness = sum(naturalness_scores) / len(naturalness_scores) if naturalness_scores else 0.0
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
        avg_retention = sum(retention_scores) / len(retention_scores) if retention_scores else 0.0

        # Check thresholds
        threshold_failures = []
        thresholds = self.config.thresholds

        if avg_coherence < thresholds.coherence_threshold:
            threshold_failures.append(
                f"Coherence {avg_coherence:.2f} < {thresholds.coherence_threshold}"
            )
        if avg_naturalness < thresholds.naturalness_threshold:
            threshold_failures.append(
                f"Naturalness {avg_naturalness:.2f} < {thresholds.naturalness_threshold}"
            )
        if avg_accuracy < thresholds.accuracy_threshold:
            threshold_failures.append(
                f"Accuracy {avg_accuracy:.2f} < {thresholds.accuracy_threshold}"
            )
        if avg_relevance < thresholds.relevance_threshold:
            threshold_failures.append(
                f"Relevance {avg_relevance:.2f} < {thresholds.relevance_threshold}"
            )

        # Calculate overall score
        overall = (
            avg_coherence * 0.25
            + avg_naturalness * 0.20
            + avg_accuracy * 0.25
            + avg_relevance * 0.20
            + avg_retention * 0.10
        )

        return ConversationQuality(
            coherence=DimensionScore(
                dimension=QualityDimension.COHERENCE,
                score=avg_coherence,
            ),
            naturalness=DimensionScore(
                dimension=QualityDimension.NATURALNESS,
                score=avg_naturalness,
            ),
            accuracy=DimensionScore(
                dimension=QualityDimension.ACCURACY,
                score=avg_accuracy,
            ),
            relevance=DimensionScore(
                dimension=QualityDimension.RELEVANCE,
                score=avg_relevance,
            ),
            context_retention=DimensionScore(
                dimension=QualityDimension.CONTEXT_RETENTION,
                score=avg_retention,
            ),
            overall_score=overall,
            passed_thresholds=len(threshold_failures) == 0,
            threshold_failures=threshold_failures,
        )

    # ============================================
    # Coherence Scoring
    # ============================================

    def _score_coherence(
        self, response: str, user_input: str
    ) -> CoherenceBreakdown:
        """Score coherence of a response."""
        if not response:
            return CoherenceBreakdown()

        breakdown = CoherenceBreakdown()

        # Topic consistency - check if response relates to input
        breakdown.topic_consistency = self._calculate_topic_consistency(
            response, user_input
        )

        # Reference resolution - check if pronouns/references make sense
        breakdown.reference_resolution = self._calculate_reference_resolution(response)

        # Logical flow - check sentence structure and transitions
        breakdown.logical_flow = self._calculate_logical_flow(response)

        # Contradictions - check for self-contradictions
        breakdown.no_contradictions = self._check_no_contradictions(response)

        return breakdown

    def _calculate_topic_consistency(self, response: str, user_input: str) -> float:
        """Calculate how well response stays on topic with user input."""
        if not response or not user_input:
            return 0.0

        # Extract key words from input (simple approach)
        input_words = set(self._extract_content_words(user_input.lower()))
        response_words = set(self._extract_content_words(response.lower()))

        if not input_words:
            return 0.8  # Default for short inputs

        # Check word overlap
        overlap = input_words & response_words
        overlap_ratio = len(overlap) / len(input_words) if input_words else 0

        # Also check for question-answer patterns
        is_question = "?" in user_input
        has_answer_pattern = any(
            pattern in response.lower()
            for pattern in ["is", "are", "was", "were", "yes", "no", "i can", "i'll", "here"]
        )

        if is_question and has_answer_pattern:
            return min(1.0, 0.7 + overlap_ratio * 0.3)

        return min(1.0, 0.5 + overlap_ratio * 0.5)

    def _calculate_reference_resolution(self, response: str) -> float:
        """Check if references (pronouns, etc.) resolve properly."""
        if not response:
            return 0.0

        # Check for dangling pronouns without context
        pronouns = ["it", "they", "them", "this", "that", "these", "those"]
        response_lower = response.lower()

        # If response starts with a pronoun without prior context, penalize
        first_word = response_lower.split()[0] if response else ""

        if first_word in pronouns and len(self._conversation_history) < 2:
            return 0.6

        # Check for clear subject-verb agreement
        has_clear_subject = any(
            marker in response_lower
            for marker in ["i ", "you ", "we ", "the ", "a ", "an "]
        )

        return 0.9 if has_clear_subject else 0.7

    def _calculate_logical_flow(self, response: str) -> float:
        """Evaluate logical flow and sentence structure."""
        if not response:
            return 0.0

        sentences = self._split_sentences(response)

        if not sentences:
            return 0.0

        # Check for transition words between sentences
        transition_words = [
            "however", "therefore", "also", "additionally", "furthermore",
            "first", "second", "then", "next", "finally", "because", "so",
            "but", "and", "or", "if", "when", "while", "although"
        ]

        has_transitions = any(
            word in response.lower() for word in transition_words
        )

        # Check sentence length variety (good writing has varied lengths)
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths) if lengths else 0

        # Penalize very short or very long average
        length_score = 1.0
        if avg_length < 3:
            length_score = 0.6
        elif avg_length > 30:
            length_score = 0.7
        elif avg_length > 20:
            length_score = 0.85

        # Base score
        base_score = 0.75

        # Bonus for transitions in multi-sentence responses
        if len(sentences) > 1 and has_transitions:
            base_score += 0.15

        return min(1.0, base_score * length_score)

    def _check_no_contradictions(self, response: str) -> float:
        """Check for self-contradictions in response."""
        if not response:
            return 1.0

        response_lower = response.lower()

        # Simple contradiction patterns
        contradiction_patterns = [
            (r"\bis\s+(\w+).*\bis\s+not\s+\1\b", "contradictory is/is not"),
            (r"\bcan\s+.*\bcannot\b", "can/cannot"),
            (r"\bwill\s+.*\bwill\s+not\b", "will/will not"),
            (r"\byes\b.*\bno\b", "yes/no in same response"),
        ]

        for pattern, _ in contradiction_patterns:
            if re.search(pattern, response_lower):
                return 0.5

        # Check against conversation history for contradictions
        if len(self._conversation_history) >= 2:
            # Simple check: response shouldn't directly negate previous statements
            prev_response = self._conversation_history[-1] if self._conversation_history else ""
            if prev_response:
                # Very basic negation check
                if "not" in response_lower and prev_response.lower().replace("not ", "") in response_lower:
                    return 0.7

        return 1.0

    # ============================================
    # Naturalness Scoring
    # ============================================

    def _score_naturalness(self, response: str) -> NaturalnessBreakdown:
        """Score naturalness of a response."""
        if not response:
            return NaturalnessBreakdown()

        breakdown = NaturalnessBreakdown()

        # Fluency - grammatical correctness and readability
        breakdown.fluency = self._calculate_fluency(response)

        # Appropriateness - tone and formality
        breakdown.appropriateness = self._calculate_appropriateness(response)

        # Diversity - avoiding repetition
        breakdown.diversity = self._calculate_diversity(response)

        # Human-likeness - natural patterns
        breakdown.human_likeness = self._calculate_human_likeness(response)

        return breakdown

    def _calculate_fluency(self, response: str) -> float:
        """Calculate language fluency score."""
        if not response:
            return 0.0

        # Check minimum length
        if len(response) < self.config.min_response_length:
            return 0.3

        # Check for complete sentences
        sentences = self._split_sentences(response)
        if not sentences:
            return 0.5

        # Check capitalization and punctuation
        has_capital = response[0].isupper()
        has_end_punct = response.rstrip()[-1] in ".!?"

        score = 0.6
        if has_capital:
            score += 0.2
        if has_end_punct:
            score += 0.2

        return min(1.0, score)

    def _calculate_appropriateness(self, response: str) -> float:
        """Calculate tone and formality appropriateness."""
        if not response:
            return 0.0

        response_lower = response.lower()

        # Check for helpful/professional markers
        helpful_markers = [
            "help", "assist", "support", "happy to", "glad to",
            "i can", "let me", "here's", "please", "thank"
        ]
        professional_markers = [
            "recommend", "suggest", "consider", "option", "alternative"
        ]

        helpful_count = sum(1 for m in helpful_markers if m in response_lower)
        professional_count = sum(1 for m in professional_markers if m in response_lower)

        # Check for inappropriate markers
        inappropriate_markers = [
            "stupid", "dumb", "idiot", "hate", "terrible"
        ]
        has_inappropriate = any(m in response_lower for m in inappropriate_markers)

        if has_inappropriate:
            return 0.3

        # Base score with bonuses
        score = 0.7
        score += min(0.15, helpful_count * 0.05)
        score += min(0.15, professional_count * 0.05)

        return min(1.0, score)

    def _calculate_diversity(self, response: str) -> float:
        """Calculate response diversity (avoiding repetition)."""
        if not response:
            return 0.0

        words = response.lower().split()
        if len(words) < 3:
            return 0.8  # Short responses are fine

        # Calculate word repetition ratio
        unique_words = set(words)
        unique_ratio = len(unique_words) / len(words)

        # Check for phrase repetition
        bigrams = [" ".join(words[i : i + 2]) for i in range(len(words) - 1)]
        unique_bigrams = set(bigrams)
        bigram_ratio = len(unique_bigrams) / len(bigrams) if bigrams else 1.0

        # Check against previous responses in history
        history_penalty = 0.0
        for prev in self._conversation_history[-4:]:  # Last 4 items
            if response.lower() == prev.lower():
                history_penalty = 0.3
                break
            elif len(set(response.lower().split()) & set(prev.lower().split())) > len(words) * 0.7:
                history_penalty = max(history_penalty, 0.15)

        diversity_score = (unique_ratio * 0.4 + bigram_ratio * 0.4 + 0.2) - history_penalty

        return max(0.0, min(1.0, diversity_score))

    def _calculate_human_likeness(self, response: str) -> float:
        """Calculate how human-like the response sounds."""
        if not response:
            return 0.0

        response_lower = response.lower()

        # Positive markers for human-like responses
        human_markers = [
            "i think", "i believe", "in my experience", "typically",
            "usually", "often", "sometimes", "it depends", "good question",
            "that's a great", "interesting", "sure", "absolutely", "of course"
        ]

        # Robotic/template markers to avoid
        robotic_markers = [
            "as an ai", "i am a", "i don't have", "i cannot feel",
            "i am not able to", "error:", "warning:", "exception:"
        ]

        human_count = sum(1 for m in human_markers if m in response_lower)
        robotic_count = sum(1 for m in robotic_markers if m in response_lower)

        # Base score
        score = 0.75

        # Add for human markers
        score += min(0.20, human_count * 0.05)

        # Penalize robotic markers
        score -= robotic_count * 0.15

        # Check for contractions (more human-like)
        contractions = ["'s", "'t", "'re", "'ve", "'ll", "'d", "'m"]
        has_contractions = any(c in response for c in contractions)
        if has_contractions:
            score += 0.05

        return max(0.0, min(1.0, score))

    # ============================================
    # Accuracy Scoring
    # ============================================

    def _score_accuracy(self, turn_result: TurnResult) -> float:
        """Score accuracy based on intent detection and entity extraction."""
        # If we have detected intent, score based on confidence
        if turn_result.detected_intent:
            # Score based on entity extraction
            entity_score = 1.0
            if turn_result.extracted_entities:
                confidences = [e.confidence for e in turn_result.extracted_entities]
                entity_score = sum(confidences) / len(confidences) if confidences else 0.8

            return entity_score

        # Default score when no intent detected
        return 0.85

    # ============================================
    # Relevance Scoring
    # ============================================

    def _score_relevance(self, response: str, user_input: str) -> float:
        """Score how relevant the response is to the input."""
        if not response or not user_input:
            return 0.0

        # Extract content words
        input_words = self._extract_content_words(user_input.lower())
        response_words = self._extract_content_words(response.lower())

        if not input_words:
            return 0.8

        # Calculate Jaccard-like overlap
        input_set = set(input_words)
        response_set = set(response_words)

        intersection = len(input_set & response_set)
        union = len(input_set | response_set)

        overlap_score = intersection / union if union > 0 else 0

        # Check for question-answer relevance
        is_question = "?" in user_input
        question_words = ["what", "where", "when", "why", "how", "who", "which", "can", "could", "would", "should"]

        if is_question:
            # Check if response attempts to answer
            starts_with_answer = any(
                response.lower().startswith(word)
                for word in ["yes", "no", "the", "it", "i", "you", "we", "they", "there", "here"]
            )
            has_info = len(response_words) > 3

            if starts_with_answer and has_info:
                return min(1.0, 0.7 + overlap_score * 0.3)

        # General relevance score
        return min(1.0, 0.5 + overlap_score * 0.5)

    # ============================================
    # Context Retention Scoring
    # ============================================

    def _score_context_retention(
        self, response: str, expected_entities: Optional[list[str]] = None
    ) -> ContextRetentionBreakdown:
        """Score context retention across conversation."""
        breakdown = ContextRetentionBreakdown()

        if not response:
            return breakdown

        # Entity tracking
        breakdown.entity_tracking = self._calculate_entity_tracking(
            response, expected_entities
        )

        # State preservation
        breakdown.state_preservation = self._calculate_state_preservation(response)

        # Reference accuracy
        breakdown.reference_accuracy = self._calculate_reference_accuracy(response)

        return breakdown

    def _calculate_entity_tracking(
        self, response: str, expected_entities: Optional[list[str]] = None
    ) -> float:
        """Check if expected entities are properly tracked."""
        if not expected_entities:
            return 0.9  # Default high score when no specific entities expected

        response_lower = response.lower()
        found_entities = sum(
            1 for entity in expected_entities if entity.lower() in response_lower
        )

        return found_entities / len(expected_entities) if expected_entities else 0.9

    def _calculate_state_preservation(self, response: str) -> float:
        """Check if conversation state is preserved."""
        # Check if response references previous context appropriately
        if len(self._conversation_history) < 2:
            return 0.9  # First turn, nothing to preserve yet

        # Check for acknowledgment of previous context
        context_markers = [
            "as mentioned", "as you said", "regarding", "about",
            "you mentioned", "earlier", "previously", "before"
        ]

        response_lower = response.lower()
        has_context_reference = any(
            marker in response_lower for marker in context_markers
        )

        # For ongoing conversations, expect some state awareness
        if len(self._conversation_history) > 4:
            return 0.95 if has_context_reference else 0.8

        return 0.9

    def _calculate_reference_accuracy(self, response: str) -> float:
        """Check if references to previous turns are accurate."""
        # This would ideally use more sophisticated NLP
        # For now, use a simple heuristic

        if not response:
            return 0.0

        # Check for clear references
        has_clear_refs = any(
            marker in response.lower()
            for marker in ["the ", "this ", "that ", "it ", "your "]
        )

        return 0.9 if has_clear_refs else 0.8

    # ============================================
    # Utility Methods
    # ============================================

    def _extract_content_words(self, text: str) -> list[str]:
        """Extract meaningful content words from text."""
        # Remove punctuation and split
        words = re.findall(r"\b[a-z]+\b", text.lower())

        # Filter stop words
        stop_words = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "to", "of", "in", "for", "on", "with", "at", "by",
            "from", "as", "into", "through", "during", "before", "after",
            "above", "below", "between", "under", "again", "further",
            "then", "once", "here", "there", "when", "where", "why",
            "how", "all", "each", "few", "more", "most", "other", "some",
            "such", "no", "nor", "not", "only", "own", "same", "so",
            "than", "too", "very", "just", "and", "but", "if", "or",
            "because", "until", "while", "i", "me", "my", "myself",
            "we", "our", "ours", "ourselves", "you", "your", "yours",
            "yourself", "yourselves", "he", "him", "his", "himself",
            "she", "her", "hers", "herself", "it", "its", "itself",
            "they", "them", "their", "theirs", "themselves", "what",
            "which", "who", "whom", "this", "that", "these", "those",
            "am", "about", "get", "got", "let", "s", "t", "re", "ve", "ll", "d", "m"
        }

        return [w for w in words if w not in stop_words and len(w) > 1]

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]
