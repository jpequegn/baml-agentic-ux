"""Drift classifier for intent drift detection.

This module provides classification of intent drift based on semantic analysis,
pattern matching, and heuristic rules.

Issue #80 - Task 5.3: Drift Classifier
Part of #28 - Phase 5: Intent Drift Detection
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from .semantic_analyzer import (
    IN_SCOPE_THRESHOLD,
    SCOPE_EXPANSION_MIN,
    DOMAIN_SHIFT_THRESHOLD,
    SemanticAnalyzer,
    SemanticAnalyzerConfig,
)
from .types import (
    AbstractionLevel,
    ConfidenceAssessment,
    ConfidenceTier,
    DriftAnalysis,
    DriftType,
    RecommendedAction,
    RedirectSuggestion,
    SemanticAnalysis,
)


# ============================================
# Pattern Definitions
# ============================================

# PII request patterns - detect requests for personal information
PII_PATTERNS = [
    r"\b(my|mine)\b.*(account|balance|password|credit|card|ssn|social\s+security)",
    r"\b(personal|private)\b.*\b(information|data|details)\b",
    r"\b(show|display|get|retrieve)\b.*(my|personal)\b",
    r"\bwhat\s+is\s+my\b",
    r"\b(my|the)\s+(user|account)\s*(name|id|number)\b",
    r"\b(billing|payment|financial)\s+(info|information|details|history)\b",
    r"\b(address|phone|email|dob|birth)\b.*(my|personal|account)\b",
]

# Temporal patterns for future predictions
TEMPORAL_FUTURE_PATTERNS = [
    r"\b(will|going\s+to|predict|forecast|future)\b",
    r"\bwhat\s+(will|would)\s+happen\b",
    r"\b(next|upcoming|tomorrow|later)\b",
    r"\b(in\s+\d+\s+(days?|weeks?|months?|years?))\b",
    r"\b(by|before|until)\s+\d{4}\b",
]

# Temporal patterns for historical data
TEMPORAL_PAST_PATTERNS = [
    r"\b(was|were|did|had|used\s+to)\b",
    r"\b(history|historical|past|previous)\b",
    r"\b(last|ago|earlier|before|prior)\b",
    r"\b(in|during)\s+\d{4}\b(?!.*(will|going|plan))",
]

# Abstraction indicators for philosophical/meta questions
ABSTRACTION_PATTERNS = [
    r"\bwhy\s+(do|does|is|are|should)\b",
    r"\bwhat\s+is\s+the\s+(meaning|purpose|point)\b",
    r"\b(philosophy|philosophical|existential)\b",
    r"\b(concept|theory|abstract|fundamental)\b",
    r"\bin\s+general\b",
    r"\bhow\s+does\s+(life|universe|reality|existence)\b",
]

# Meta-level questions about the system
META_PATTERNS = [
    r"\bwhat\s+(can|do)\s+you\s+(do|know|understand)\b",
    r"\b(your|you)\s+(capabilities|limitations|purpose)\b",
    r"\bare\s+you\s+(a|an)\b",
    r"\bwho\s+(made|created|built)\s+you\b",
    r"\btell\s+me\s+about\s+(yourself|you)\b",
    r"\bhow\s+do\s+you\s+work\b",
]


# ============================================
# Drift Score Ranges
# ============================================

class DriftScoreRange:
    """Drift score interpretation ranges."""

    ON_TOPIC = (0.0, 0.2)
    MINOR_DEVIATION = (0.2, 0.4)
    MODERATE_DRIFT = (0.4, 0.6)
    SIGNIFICANT_DRIFT = (0.6, 0.8)
    COMPLETE_DRIFT = (0.8, 1.0)


# ============================================
# Data Classes
# ============================================


@dataclass
class PatternMatch:
    """Result of pattern matching.

    Attributes:
        pattern_type: Type of pattern matched
        matched_text: The text that matched
        pattern: The regex pattern that matched
        confidence: Confidence in the match (0-1)
    """

    pattern_type: str
    matched_text: str
    pattern: str
    confidence: float = 1.0


@dataclass
class DriftClassification:
    """Complete drift classification result.

    Attributes:
        drift_type: The classified drift type
        drift_score: Drift severity score (0-1)
        confidence: Classification confidence (0-1)
        pattern_matches: Patterns that contributed to classification
        reasoning: Explanation of classification decision
        semantic_analysis: Underlying semantic analysis
    """

    drift_type: DriftType
    drift_score: float
    confidence: float
    pattern_matches: list[PatternMatch] = field(default_factory=list)
    reasoning: str = ""
    semantic_analysis: Optional[SemanticAnalysis] = None

    def __post_init__(self):
        """Validate scores are in valid range."""
        if not 0.0 <= self.drift_score <= 1.0:
            raise ValueError("drift_score must be between 0.0 and 1.0")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    @property
    def has_drift(self) -> bool:
        """Check if drift was detected."""
        return self.drift_type != DriftType.NONE

    @property
    def severity_level(self) -> str:
        """Get human-readable severity level."""
        if self.drift_score < DriftScoreRange.MINOR_DEVIATION[0]:
            return "on_topic"
        elif self.drift_score < DriftScoreRange.MODERATE_DRIFT[0]:
            return "minor"
        elif self.drift_score < DriftScoreRange.SIGNIFICANT_DRIFT[0]:
            return "moderate"
        elif self.drift_score < DriftScoreRange.COMPLETE_DRIFT[0]:
            return "significant"
        else:
            return "complete"

    def to_drift_analysis(
        self,
        graceful_response: str = "",
        suggested_redirects: Optional[list[RedirectSuggestion]] = None,
    ) -> DriftAnalysis:
        """Convert to DriftAnalysis for integration with other components.

        Args:
            graceful_response: Suggested response for handling drift
            suggested_redirects: Optional redirect suggestions

        Returns:
            DriftAnalysis instance
        """
        input_text = ""
        semantic_distance = 1.0 - self.confidence

        if self.semantic_analysis:
            input_text = self.semantic_analysis.input_text
            if self.semantic_analysis.nearest_intents:
                semantic_distance = 1.0 - self.semantic_analysis.nearest_intents[0].similarity

        return DriftAnalysis(
            current_input=input_text,
            drift_score=self.drift_score,
            drift_type=self.drift_type,
            confidence=self.confidence,
            semantic_distance=semantic_distance,
            graceful_response=graceful_response,
            suggested_redirects=suggested_redirects or [],
        )


@dataclass
class DriftClassifierConfig:
    """Configuration for drift classifier.

    Attributes:
        pii_patterns: Patterns for detecting PII requests
        temporal_future_patterns: Patterns for future temporal references
        temporal_past_patterns: Patterns for past temporal references
        abstraction_patterns: Patterns for abstract/philosophical queries
        meta_patterns: Patterns for meta-level questions
        high_confidence_threshold: Threshold for high similarity (no drift)
        medium_confidence_min: Minimum threshold for medium similarity
        low_confidence_threshold: Threshold for low similarity (domain shift)
        ambiguity_threshold: Max similarity gap for ambiguous classification
    """

    pii_patterns: list[str] = field(default_factory=lambda: PII_PATTERNS.copy())
    temporal_future_patterns: list[str] = field(
        default_factory=lambda: TEMPORAL_FUTURE_PATTERNS.copy()
    )
    temporal_past_patterns: list[str] = field(
        default_factory=lambda: TEMPORAL_PAST_PATTERNS.copy()
    )
    abstraction_patterns: list[str] = field(
        default_factory=lambda: ABSTRACTION_PATTERNS.copy()
    )
    meta_patterns: list[str] = field(default_factory=lambda: META_PATTERNS.copy())
    high_confidence_threshold: float = IN_SCOPE_THRESHOLD
    medium_confidence_min: float = SCOPE_EXPANSION_MIN
    low_confidence_threshold: float = DOMAIN_SHIFT_THRESHOLD
    ambiguity_threshold: float = 0.15

    @classmethod
    def default(cls) -> DriftClassifierConfig:
        """Create default configuration."""
        return cls()


# ============================================
# Drift Classifier
# ============================================


class DriftClassifier:
    """Classifies intent drift based on semantic analysis and heuristics.

    This classifier uses a combination of:
    - Pattern matching for specific drift types (PII, temporal, abstraction)
    - Similarity scores from semantic analysis
    - Decision tree logic for classification

    Example:
        >>> classifier = DriftClassifier()
        >>> result = classifier.classify(
        ...     user_input="What is my account balance?",
        ...     semantic_result=semantic_analysis,
        ... )
        >>> print(result.drift_type)
        DriftType.PERSONALIZATION
    """

    def __init__(
        self,
        config: Optional[DriftClassifierConfig] = None,
        semantic_analyzer: Optional[SemanticAnalyzer] = None,
    ):
        """Initialize the drift classifier.

        Args:
            config: Optional configuration. Uses defaults if not provided.
            semantic_analyzer: Optional semantic analyzer for full analysis.
        """
        self.config = config or DriftClassifierConfig.default()
        self.semantic_analyzer = semantic_analyzer

        # Compile regex patterns for efficiency
        self._compiled_patterns = {
            "pii": [re.compile(p, re.IGNORECASE) for p in self.config.pii_patterns],
            "temporal_future": [
                re.compile(p, re.IGNORECASE)
                for p in self.config.temporal_future_patterns
            ],
            "temporal_past": [
                re.compile(p, re.IGNORECASE)
                for p in self.config.temporal_past_patterns
            ],
            "abstraction": [
                re.compile(p, re.IGNORECASE)
                for p in self.config.abstraction_patterns
            ],
            "meta": [re.compile(p, re.IGNORECASE) for p in self.config.meta_patterns],
        }

    def _match_patterns(
        self, text: str, pattern_type: str
    ) -> list[PatternMatch]:
        """Match text against a set of patterns.

        Args:
            text: Text to match against
            pattern_type: Type of patterns to use

        Returns:
            List of pattern matches
        """
        matches = []
        patterns = self._compiled_patterns.get(pattern_type, [])

        for i, pattern in enumerate(patterns):
            match = pattern.search(text)
            if match:
                matches.append(
                    PatternMatch(
                        pattern_type=pattern_type,
                        matched_text=match.group(),
                        pattern=pattern.pattern,
                        confidence=1.0,
                    )
                )

        return matches

    def detect_pii_request(self, text: str) -> tuple[bool, list[PatternMatch]]:
        """Detect if text contains PII request patterns.

        Args:
            text: User input text

        Returns:
            Tuple of (is_pii_request, pattern_matches)
        """
        matches = self._match_patterns(text, "pii")
        return len(matches) > 0, matches

    def detect_temporal_drift(
        self, text: str
    ) -> tuple[bool, str, list[PatternMatch]]:
        """Detect temporal drift patterns in text.

        Args:
            text: User input text

        Returns:
            Tuple of (has_temporal_drift, direction, pattern_matches)
        """
        future_matches = self._match_patterns(text, "temporal_future")
        past_matches = self._match_patterns(text, "temporal_past")

        all_matches = future_matches + past_matches

        if future_matches and not past_matches:
            return True, "future", all_matches
        elif past_matches and not future_matches:
            return True, "past", all_matches
        elif future_matches and past_matches:
            return True, "mixed", all_matches

        return False, "none", []

    def detect_abstraction(self, text: str) -> tuple[bool, list[PatternMatch]]:
        """Detect abstraction/philosophical patterns in text.

        Args:
            text: User input text

        Returns:
            Tuple of (is_abstract, pattern_matches)
        """
        abstraction_matches = self._match_patterns(text, "abstraction")
        meta_matches = self._match_patterns(text, "meta")

        all_matches = abstraction_matches + meta_matches
        return len(all_matches) > 0, all_matches

    def calculate_drift_score(
        self,
        intent_confidence: float,
        domain_similarity: float,
        pattern_matches: list[PatternMatch],
        abstraction_level: AbstractionLevel,
    ) -> float:
        """Calculate overall drift score.

        Args:
            intent_confidence: Confidence in intent match (0-1)
            domain_similarity: Similarity to domain (0-1)
            pattern_matches: Detected pattern matches
            abstraction_level: Level of abstraction in input

        Returns:
            Drift score (0-1, higher = more drift)
        """
        # Base score from inverse of confidence
        base_score = 1.0 - intent_confidence

        # Adjust for domain similarity
        domain_factor = 1.0 - domain_similarity

        # Adjust for pattern matches
        pattern_penalty = min(len(pattern_matches) * 0.1, 0.3)

        # Adjust for abstraction level
        abstraction_penalty = {
            AbstractionLevel.CONCRETE: 0.0,
            AbstractionLevel.MODERATE: 0.1,
            AbstractionLevel.ABSTRACT: 0.2,
            AbstractionLevel.PHILOSOPHICAL: 0.3,
        }.get(abstraction_level, 0.0)

        # Combine factors
        drift_score = (
            base_score * 0.5
            + domain_factor * 0.2
            + pattern_penalty
            + abstraction_penalty
        )

        # Clamp to valid range
        return max(0.0, min(1.0, drift_score))

    def _classify_by_decision_tree(
        self,
        intent_confidence: float,
        domain_similarity: float,
        has_pii: bool,
        has_temporal: bool,
        temporal_direction: str,
        has_abstraction: bool,
        abstraction_level: AbstractionLevel,
        has_multiple_matches: bool,
    ) -> tuple[DriftType, str]:
        """Apply decision tree logic for classification.

        Args:
            intent_confidence: Confidence in intent match
            domain_similarity: Domain similarity score
            has_pii: Whether PII patterns were detected
            has_temporal: Whether temporal patterns were detected
            temporal_direction: Direction of temporal reference
            has_abstraction: Whether abstraction patterns were detected
            abstraction_level: Level of abstraction
            has_multiple_matches: Whether multiple intents matched closely

        Returns:
            Tuple of (drift_type, reasoning)
        """
        # Decision tree implementation
        if intent_confidence >= self.config.high_confidence_threshold:
            # High confidence - likely no drift
            if has_pii:
                return (
                    DriftType.PERSONALIZATION,
                    "High intent confidence but PII request detected",
                )
            return DriftType.NONE, "High confidence match to known intent"

        elif intent_confidence < self.config.low_confidence_threshold:
            # Low confidence - likely significant drift
            if domain_similarity < self.config.low_confidence_threshold:
                return (
                    DriftType.DOMAIN_SHIFT,
                    "Low intent and domain confidence indicates domain shift",
                )
            elif has_temporal:
                direction_text = f"({temporal_direction})" if temporal_direction != "none" else ""
                return (
                    DriftType.TEMPORAL_DRIFT,
                    f"Temporal reference {direction_text} with low intent confidence",
                )
            else:
                return (
                    DriftType.SCOPE_EXPANSION,
                    "Low confidence but in domain - likely scope expansion",
                )

        else:
            # Medium confidence (0.3-0.7 range)
            if has_multiple_matches:
                return (
                    DriftType.AMBIGUOUS,
                    "Multiple intents matched with similar confidence",
                )

            if has_abstraction or abstraction_level in (
                AbstractionLevel.ABSTRACT,
                AbstractionLevel.PHILOSOPHICAL,
            ):
                return (
                    DriftType.ABSTRACTION_CLIMB,
                    "Abstract or philosophical request detected",
                )

            if has_pii:
                return (
                    DriftType.PERSONALIZATION,
                    "Request for personal/private information detected",
                )

            if has_temporal:
                return (
                    DriftType.TEMPORAL_DRIFT,
                    f"Temporal reference ({temporal_direction}) detected",
                )

            return (
                DriftType.SCOPE_EXPANSION,
                "Moderate confidence suggests related but unsupported request",
            )

    def classify(
        self,
        user_input: str,
        semantic_result: Optional[SemanticAnalysis] = None,
        conversation_context: Optional[dict] = None,
        available_intents: Optional[list[dict]] = None,
        domain_keywords: Optional[list[str]] = None,
    ) -> DriftClassification:
        """Classify intent drift for user input.

        Args:
            user_input: The user's input text
            semantic_result: Pre-computed semantic analysis result
            conversation_context: Optional conversation context
            available_intents: Available intent definitions (if no semantic_result)
            domain_keywords: Domain keywords (if no semantic_result)

        Returns:
            Complete drift classification
        """
        # Get or compute semantic analysis
        if semantic_result is None:
            if self.semantic_analyzer is None:
                self.semantic_analyzer = SemanticAnalyzer()

            semantic_result = self.semantic_analyzer.analyze(
                user_input=user_input,
                available_intents=available_intents or [],
                domain_keywords=domain_keywords or [],
            )

        # Extract metrics from semantic analysis
        intent_confidence = 0.0
        domain_similarity = 0.0
        has_multiple_matches = False

        if semantic_result.nearest_intents:
            intent_confidence = semantic_result.nearest_intents[0].similarity

            # Check for ambiguity
            if len(semantic_result.nearest_intents) >= 2:
                top_two = semantic_result.nearest_intents[:2]
                gap = top_two[0].similarity - top_two[1].similarity
                has_multiple_matches = gap < self.config.ambiguity_threshold

        # Domain similarity from domain classification
        if semantic_result.domain_classification:
            domain_similarity = 0.5  # Has some domain match

        # Pattern detection
        has_pii, pii_matches = self.detect_pii_request(user_input)
        has_temporal, temporal_dir, temporal_matches = self.detect_temporal_drift(
            user_input
        )
        has_abstraction, abstraction_matches = self.detect_abstraction(user_input)

        # Collect all pattern matches
        all_matches = pii_matches + temporal_matches + abstraction_matches

        # Apply decision tree
        drift_type, reasoning = self._classify_by_decision_tree(
            intent_confidence=intent_confidence,
            domain_similarity=domain_similarity,
            has_pii=has_pii,
            has_temporal=has_temporal,
            temporal_direction=temporal_dir,
            has_abstraction=has_abstraction,
            abstraction_level=semantic_result.abstraction_level,
            has_multiple_matches=has_multiple_matches,
        )

        # Calculate drift score
        drift_score = self.calculate_drift_score(
            intent_confidence=intent_confidence,
            domain_similarity=domain_similarity,
            pattern_matches=all_matches,
            abstraction_level=semantic_result.abstraction_level,
        )

        # Calculate classification confidence
        classification_confidence = self._calculate_classification_confidence(
            intent_confidence=intent_confidence,
            pattern_matches=all_matches,
            drift_type=drift_type,
        )

        return DriftClassification(
            drift_type=drift_type,
            drift_score=drift_score,
            confidence=classification_confidence,
            pattern_matches=all_matches,
            reasoning=reasoning,
            semantic_analysis=semantic_result,
        )

    def _calculate_classification_confidence(
        self,
        intent_confidence: float,
        pattern_matches: list[PatternMatch],
        drift_type: DriftType,
    ) -> float:
        """Calculate confidence in the classification.

        Args:
            intent_confidence: Intent matching confidence
            pattern_matches: Pattern matches found
            drift_type: Classified drift type

        Returns:
            Classification confidence (0-1)
        """
        # Base confidence from intent confidence
        if drift_type == DriftType.NONE:
            # For no drift, confidence matches intent confidence
            base = intent_confidence
        else:
            # For drift types, confidence is based on pattern matches
            base = 0.5

        # Boost confidence if patterns support the classification
        pattern_bonus = 0.0
        if pattern_matches:
            if drift_type == DriftType.PERSONALIZATION:
                pii_count = sum(1 for m in pattern_matches if m.pattern_type == "pii")
                pattern_bonus = min(pii_count * 0.15, 0.3)
            elif drift_type == DriftType.TEMPORAL_DRIFT:
                temporal_count = sum(
                    1 for m in pattern_matches
                    if m.pattern_type in ("temporal_future", "temporal_past")
                )
                pattern_bonus = min(temporal_count * 0.15, 0.3)
            elif drift_type == DriftType.ABSTRACTION_CLIMB:
                abstract_count = sum(
                    1 for m in pattern_matches
                    if m.pattern_type in ("abstraction", "meta")
                )
                pattern_bonus = min(abstract_count * 0.15, 0.3)

        confidence = base + pattern_bonus
        return max(0.0, min(1.0, confidence))

    def classify_batch(
        self,
        inputs: list[str],
        available_intents: Optional[list[dict]] = None,
        domain_keywords: Optional[list[str]] = None,
    ) -> list[DriftClassification]:
        """Classify multiple inputs.

        Args:
            inputs: List of user inputs
            available_intents: Available intent definitions
            domain_keywords: Domain keywords

        Returns:
            List of classifications for each input
        """
        return [
            self.classify(
                user_input=inp,
                available_intents=available_intents,
                domain_keywords=domain_keywords,
            )
            for inp in inputs
        ]

    def get_recommended_action(
        self, classification: DriftClassification
    ) -> RecommendedAction:
        """Get recommended action based on classification.

        Args:
            classification: Drift classification result

        Returns:
            Recommended action to take
        """
        if classification.drift_type == DriftType.NONE:
            if classification.confidence >= 0.8:
                return RecommendedAction.PROCEED
            else:
                return RecommendedAction.PROCEED_WITH_CAVEAT

        elif classification.drift_type == DriftType.AMBIGUOUS:
            return RecommendedAction.CLARIFY

        elif classification.drift_type in (
            DriftType.SCOPE_EXPANSION,
            DriftType.PERSONALIZATION,
        ):
            return RecommendedAction.REDIRECT

        elif classification.drift_type in (
            DriftType.DOMAIN_SHIFT,
            DriftType.ABSTRACTION_CLIMB,
        ):
            if classification.drift_score > 0.8:
                return RecommendedAction.DECLINE
            else:
                return RecommendedAction.REDIRECT

        elif classification.drift_type == DriftType.TEMPORAL_DRIFT:
            return RecommendedAction.CLARIFY

        return RecommendedAction.CLARIFY

    def get_confidence_assessment(
        self, classification: DriftClassification
    ) -> ConfidenceAssessment:
        """Get confidence assessment from classification.

        Args:
            classification: Drift classification result

        Returns:
            Confidence assessment with tier and action
        """
        return ConfidenceAssessment.from_score(
            score=classification.confidence,
            explanation=classification.reasoning,
        )
