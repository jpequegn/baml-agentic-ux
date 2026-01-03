"""Semantic analyzer for intent drift detection.

This module provides semantic similarity analysis between user input and
available LUI intents, including abstraction detection and domain classification.

Issue #79 - Task 5.2: Semantic Analyzer
Part of #28 - Phase 5: Intent Drift Detection
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

from .types import (
    AbstractionLevel,
    DriftType,
    EntityMention,
    NearestIntent,
    SemanticAnalysis,
    TemporalReference,
    TemporalReferenceType,
)


# ============================================
# Similarity Thresholds
# ============================================

# Threshold ranges for intent matching
IN_SCOPE_THRESHOLD = 0.7  # ≥0.7 = Clear intent match
SCOPE_EXPANSION_MIN = 0.4  # 0.4-0.7 = Related but uncertain
DOMAIN_SHIFT_THRESHOLD = 0.3  # <0.3 = Different domain


@dataclass
class SimilarityResult:
    """Result of similarity calculation between two texts.

    Attributes:
        score: Similarity score (0-1)
        method: The method used for calculation
        details: Additional calculation details
    """

    score: float
    method: str
    details: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate score is in valid range."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be between 0.0 and 1.0")


@dataclass
class IntentDefinition:
    """Definition of an available intent.

    Attributes:
        name: Intent name/identifier
        description: Human-readable description
        keywords: Keywords associated with this intent
        examples: Example phrases that trigger this intent
        capability_id: Optional capability ID
        domain: Domain this intent belongs to
    """

    name: str
    description: str
    keywords: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    capability_id: Optional[str] = None
    domain: Optional[str] = None


@dataclass
class SemanticAnalyzerConfig:
    """Configuration for semantic analyzer.

    Attributes:
        in_scope_threshold: Threshold for clear intent match
        scope_expansion_min: Minimum threshold for scope expansion
        domain_shift_threshold: Threshold below which is domain shift
        top_n_intents: Number of top intents to return
        abstraction_indicators: Words/phrases indicating abstract requests
        meta_indicators: Words/phrases indicating meta-level questions
        philosophical_indicators: Words/phrases indicating philosophical queries
    """

    in_scope_threshold: float = IN_SCOPE_THRESHOLD
    scope_expansion_min: float = SCOPE_EXPANSION_MIN
    domain_shift_threshold: float = DOMAIN_SHIFT_THRESHOLD
    top_n_intents: int = 5
    abstraction_indicators: list[str] = field(default_factory=lambda: [
        "why", "what is the meaning", "what does it mean",
        "philosophy", "concept", "theory", "abstract",
        "in general", "generally speaking", "theoretically",
        "hypothetically", "fundamentally", "essentially",
    ])
    meta_indicators: list[str] = field(default_factory=lambda: [
        "what can you do", "how do you work", "what are you",
        "who made you", "are you a", "tell me about yourself",
        "your capabilities", "your limits", "your purpose",
        "help me understand you", "explain yourself",
    ])
    philosophical_indicators: list[str] = field(default_factory=lambda: [
        "meaning of life", "consciousness", "free will",
        "existence", "reality", "truth", "morality",
        "ethics", "soul", "spirit", "god", "universe",
        "what is real", "why do we exist", "purpose of life",
    ])

    @classmethod
    def default(cls) -> SemanticAnalyzerConfig:
        """Create default configuration."""
        return cls()


# ============================================
# Temporal Pattern Detection
# ============================================

TEMPORAL_PATTERNS = {
    TemporalReferenceType.PAST_ABSOLUTE: [
        r"\b(in|on|during)\s+\d{4}\b",  # in 2023
        r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b",
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",  # MM/DD/YYYY or similar
    ],
    TemporalReferenceType.PAST_RELATIVE: [
        r"\b(yesterday|last\s+week|last\s+month|last\s+year)\b",
        r"\b(\d+)\s+(days?|weeks?|months?|years?)\s+ago\b",
        r"\b(previously|earlier|before|prior)\b",
    ],
    TemporalReferenceType.PRESENT: [
        r"\b(today|now|currently|at\s+the\s+moment|right\s+now)\b",
        r"\b(this\s+week|this\s+month|this\s+year)\b",
    ],
    TemporalReferenceType.FUTURE_RELATIVE: [
        r"\b(tomorrow|next\s+week|next\s+month|next\s+year)\b",
        r"\b(in\s+\d+\s+(days?|weeks?|months?|years?))\b",
        r"\b(soon|later|upcoming|forthcoming)\b",
    ],
    TemporalReferenceType.FUTURE_ABSOLUTE: [
        r"\b(in|on|by)\s+\d{4}\b(?!\s+ago)",  # in 2025 (not "in 2020 ago")
        r"\bby\s+(january|february|march|april|may|june|july|august|september|october|november|december)",
    ],
    TemporalReferenceType.HYPOTHETICAL: [
        r"\b(if|when|suppose|assuming|imagine|what\s+if)\b",
        r"\b(would|could|might)\s+(have\s+)?(been|be)\b",
    ],
}


# ============================================
# Entity Patterns
# ============================================

ENTITY_PATTERNS = {
    "person": [
        r"\b(my|your|his|her|their)\s+(name|account|profile)\b",
        r"\b(I|me|myself|you|he|she|they)\b",
    ],
    "organization": [
        r"\b[A-Z][a-zA-Z]*\s+(Inc|Corp|LLC|Ltd|Company|Co)\b",
        r"\b(the\s+)?company\b",
    ],
    "location": [
        r"\b(my|the|your)\s+(location|address|city|country)\b",
    ],
    "product": [
        r"\b(my|the|your)\s+(order|purchase|subscription)\b",
    ],
}

# Entity types that require personalization
PERSONALIZATION_ENTITY_TYPES = {"person", "account", "preference", "history"}


class SemanticAnalyzer:
    """Analyzes semantic similarity between user input and available intents.

    This class provides methods for:
    - Calculating text similarity using multiple methods
    - Detecting abstraction levels in user requests
    - Identifying domain relevance
    - Ranking nearest matching intents

    Example:
        >>> analyzer = SemanticAnalyzer()
        >>> result = analyzer.analyze(
        ...     user_input="How do I reset my password?",
        ...     available_intents=[{"name": "password_reset", ...}],
        ...     domain_keywords=["password", "account", "security"]
        ... )
    """

    def __init__(self, config: Optional[SemanticAnalyzerConfig] = None):
        """Initialize the semantic analyzer.

        Args:
            config: Optional configuration. Uses defaults if not provided.
        """
        self.config = config or SemanticAnalyzerConfig.default()
        self._stopwords = self._get_stopwords()

    def _get_stopwords(self) -> set[str]:
        """Get common English stopwords for filtering."""
        return {
            "a", "an", "the", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in",
            "for", "on", "with", "at", "by", "from", "as", "into",
            "through", "during", "before", "after", "above", "below",
            "between", "under", "again", "further", "then", "once",
            "here", "there", "when", "where", "why", "how", "all",
            "each", "few", "more", "most", "other", "some", "such",
            "no", "nor", "not", "only", "own", "same", "so", "than",
            "too", "very", "just", "and", "but", "if", "or", "because",
            "until", "while", "although", "though", "unless",
        }

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into words.

        Args:
            text: Input text to tokenize

        Returns:
            List of lowercase tokens
        """
        # Convert to lowercase and extract words
        words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
        return words

    def _tokenize_filtered(self, text: str) -> list[str]:
        """Tokenize and filter stopwords.

        Args:
            text: Input text to tokenize

        Returns:
            List of lowercase tokens without stopwords
        """
        tokens = self._tokenize(text)
        return [t for t in tokens if t not in self._stopwords]

    def calculate_jaccard_similarity(
        self, text1: str, text2: str
    ) -> SimilarityResult:
        """Calculate Jaccard similarity between two texts.

        Jaccard similarity = |A ∩ B| / |A ∪ B|

        Args:
            text1: First text
            text2: Second text

        Returns:
            SimilarityResult with Jaccard similarity score
        """
        tokens1 = set(self._tokenize_filtered(text1))
        tokens2 = set(self._tokenize_filtered(text2))

        if not tokens1 and not tokens2:
            return SimilarityResult(
                score=1.0,
                method="jaccard",
                details={"intersection": 0, "union": 0, "note": "both empty"},
            )

        if not tokens1 or not tokens2:
            return SimilarityResult(
                score=0.0,
                method="jaccard",
                details={"intersection": 0, "union": len(tokens1 | tokens2)},
            )

        intersection = tokens1 & tokens2
        union = tokens1 | tokens2

        score = len(intersection) / len(union)

        return SimilarityResult(
            score=score,
            method="jaccard",
            details={
                "intersection": len(intersection),
                "union": len(union),
                "common_tokens": list(intersection),
            },
        )

    def calculate_cosine_similarity(
        self, text1: str, text2: str
    ) -> SimilarityResult:
        """Calculate cosine similarity between two texts using TF vectors.

        Args:
            text1: First text
            text2: Second text

        Returns:
            SimilarityResult with cosine similarity score
        """
        tokens1 = self._tokenize_filtered(text1)
        tokens2 = self._tokenize_filtered(text2)

        if not tokens1 and not tokens2:
            return SimilarityResult(
                score=1.0,
                method="cosine",
                details={"note": "both empty"},
            )

        if not tokens1 or not tokens2:
            return SimilarityResult(
                score=0.0,
                method="cosine",
                details={"note": "one empty"},
            )

        # Build term frequency vectors
        counter1 = Counter(tokens1)
        counter2 = Counter(tokens2)

        # Get all unique terms
        all_terms = set(counter1.keys()) | set(counter2.keys())

        # Calculate dot product and magnitudes
        dot_product = sum(counter1.get(t, 0) * counter2.get(t, 0) for t in all_terms)
        magnitude1 = math.sqrt(sum(v ** 2 for v in counter1.values()))
        magnitude2 = math.sqrt(sum(v ** 2 for v in counter2.values()))

        if magnitude1 == 0 or magnitude2 == 0:
            return SimilarityResult(
                score=0.0,
                method="cosine",
                details={"note": "zero magnitude"},
            )

        score = dot_product / (magnitude1 * magnitude2)
        # Clamp to handle floating point precision issues
        score = max(0.0, min(1.0, score))

        return SimilarityResult(
            score=score,
            method="cosine",
            details={
                "dot_product": dot_product,
                "magnitude1": magnitude1,
                "magnitude2": magnitude2,
            },
        )

    def calculate_combined_similarity(
        self,
        text1: str,
        text2: str,
        jaccard_weight: float = 0.4,
        cosine_weight: float = 0.6,
    ) -> SimilarityResult:
        """Calculate weighted combination of similarity methods.

        Args:
            text1: First text
            text2: Second text
            jaccard_weight: Weight for Jaccard similarity
            cosine_weight: Weight for cosine similarity

        Returns:
            SimilarityResult with combined score
        """
        jaccard = self.calculate_jaccard_similarity(text1, text2)
        cosine = self.calculate_cosine_similarity(text1, text2)

        combined_score = (
            jaccard.score * jaccard_weight + cosine.score * cosine_weight
        )

        return SimilarityResult(
            score=combined_score,
            method="combined",
            details={
                "jaccard_score": jaccard.score,
                "cosine_score": cosine.score,
                "jaccard_weight": jaccard_weight,
                "cosine_weight": cosine_weight,
            },
        )

    def detect_abstraction_level(self, text: str) -> AbstractionLevel:
        """Detect the abstraction level of user input.

        Args:
            text: User input text

        Returns:
            AbstractionLevel classification
        """
        text_lower = text.lower()

        # Check for philosophical indicators first (most abstract)
        for indicator in self.config.philosophical_indicators:
            if indicator in text_lower:
                return AbstractionLevel.PHILOSOPHICAL

        # Check for meta-level questions about the system
        for indicator in self.config.meta_indicators:
            if indicator in text_lower:
                return AbstractionLevel.ABSTRACT

        # Check for general abstraction indicators
        abstraction_count = sum(
            1 for indicator in self.config.abstraction_indicators
            if indicator in text_lower
        )

        if abstraction_count >= 2:
            return AbstractionLevel.ABSTRACT
        elif abstraction_count == 1:
            return AbstractionLevel.MODERATE

        # Check for concrete action verbs
        action_verbs = [
            "create", "make", "build", "add", "remove", "delete",
            "update", "change", "set", "get", "find", "search",
            "show", "display", "send", "submit", "save", "load",
            "open", "close", "start", "stop", "run", "execute",
        ]

        has_action_verb = any(verb in text_lower for verb in action_verbs)

        # Check for specific nouns (indicates concrete request)
        has_specific_noun = bool(re.search(r"\b(file|button|page|form|field|user|account|password|email)\b", text_lower))

        if has_action_verb or has_specific_noun:
            return AbstractionLevel.CONCRETE

        return AbstractionLevel.MODERATE

    def detect_temporal_references(self, text: str) -> list[TemporalReference]:
        """Detect temporal references in user input.

        Args:
            text: User input text

        Returns:
            List of detected temporal references
        """
        references = []
        text_lower = text.lower()

        for ref_type, patterns in TEMPORAL_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    # Calculate drift risk based on reference type
                    drift_risk = self._calculate_temporal_drift_risk(ref_type)

                    references.append(
                        TemporalReference(
                            expression=match.group(),
                            reference_type=ref_type,
                            is_within_knowledge=ref_type in (
                                TemporalReferenceType.PRESENT,
                                TemporalReferenceType.PAST_RELATIVE,
                            ),
                            drift_risk=drift_risk,
                        )
                    )

        return references

    def _calculate_temporal_drift_risk(
        self, ref_type: TemporalReferenceType
    ) -> float:
        """Calculate drift risk for a temporal reference type.

        Args:
            ref_type: Type of temporal reference

        Returns:
            Drift risk score (0-1)
        """
        risk_map = {
            TemporalReferenceType.PRESENT: 0.0,
            TemporalReferenceType.PAST_RELATIVE: 0.1,
            TemporalReferenceType.PAST_ABSOLUTE: 0.3,
            TemporalReferenceType.FUTURE_RELATIVE: 0.4,
            TemporalReferenceType.FUTURE_ABSOLUTE: 0.7,
            TemporalReferenceType.HYPOTHETICAL: 0.5,
        }
        return risk_map.get(ref_type, 0.5)

    def detect_entities(self, text: str) -> list[EntityMention]:
        """Detect entity mentions in user input.

        Args:
            text: User input text

        Returns:
            List of detected entity mentions
        """
        entities = []
        text_lower = text.lower()

        for entity_type, patterns in ENTITY_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    requires_personalization = (
                        entity_type in PERSONALIZATION_ENTITY_TYPES
                        or "my" in match.group().lower()
                    )

                    entities.append(
                        EntityMention(
                            text=match.group(),
                            entity_type=entity_type,
                            start_offset=match.start(),
                            end_offset=match.end(),
                            requires_personalization=requires_personalization,
                        )
                    )

        return entities

    def calculate_domain_similarity(
        self, text: str, domain_keywords: list[str]
    ) -> float:
        """Calculate similarity between text and domain keywords.

        Args:
            text: User input text
            domain_keywords: Keywords defining the domain

        Returns:
            Domain similarity score (0-1)
        """
        if not domain_keywords:
            return 0.5  # Neutral if no domain defined

        tokens = set(self._tokenize_filtered(text))

        if not tokens:
            return 0.0

        domain_set = set(kw.lower() for kw in domain_keywords)
        matches = tokens & domain_set

        # Use Jaccard-like measure
        return len(matches) / max(len(tokens), len(domain_set))

    def rank_nearest_intents(
        self,
        user_input: str,
        available_intents: list[IntentDefinition],
        top_n: Optional[int] = None,
    ) -> list[NearestIntent]:
        """Rank intents by similarity to user input.

        Args:
            user_input: User's input text
            available_intents: List of available intent definitions
            top_n: Number of top intents to return (uses config default if None)

        Returns:
            List of nearest intents sorted by similarity
        """
        top_n = top_n or self.config.top_n_intents
        scored_intents = []

        for intent in available_intents:
            # Build comparison text from intent
            comparison_parts = [intent.description]
            comparison_parts.extend(intent.keywords)
            comparison_parts.extend(intent.examples)
            comparison_text = " ".join(comparison_parts)

            # Calculate similarity
            similarity = self.calculate_combined_similarity(
                user_input, comparison_text
            )

            # Determine if clarification is needed
            requires_clarification = (
                similarity.score < self.config.in_scope_threshold
                and similarity.score >= self.config.scope_expansion_min
            )

            scored_intents.append(
                NearestIntent(
                    intent_name=intent.name,
                    similarity=similarity.score,
                    capability_id=intent.capability_id,
                    requires_clarification=requires_clarification,
                )
            )

        # Sort by similarity descending
        scored_intents.sort(key=lambda x: x.similarity, reverse=True)

        return scored_intents[:top_n]

    def classify_drift_type(
        self,
        similarity_score: float,
        abstraction_level: AbstractionLevel,
        domain_similarity: float,
        has_personalization_need: bool,
        has_temporal_drift_risk: bool,
    ) -> DriftType:
        """Classify the type of drift based on analysis.

        Args:
            similarity_score: Similarity to nearest intent
            abstraction_level: Detected abstraction level
            domain_similarity: Domain relevance score
            has_personalization_need: Whether personalization is needed
            has_temporal_drift_risk: Whether temporal drift risk exists

        Returns:
            Classified DriftType
        """
        # Check for no drift first
        if similarity_score >= self.config.in_scope_threshold:
            return DriftType.NONE

        # Check for abstraction climb
        if abstraction_level in (
            AbstractionLevel.ABSTRACT,
            AbstractionLevel.PHILOSOPHICAL,
        ):
            return DriftType.ABSTRACTION_CLIMB

        # Check for personalization need
        if has_personalization_need:
            return DriftType.PERSONALIZATION

        # Check for temporal drift
        if has_temporal_drift_risk:
            return DriftType.TEMPORAL_DRIFT

        # Check for domain shift
        if domain_similarity < self.config.domain_shift_threshold:
            return DriftType.DOMAIN_SHIFT

        # Check for scope expansion
        if (
            similarity_score >= self.config.scope_expansion_min
            and similarity_score < self.config.in_scope_threshold
        ):
            return DriftType.SCOPE_EXPANSION

        # Default to domain shift for low similarity
        return DriftType.DOMAIN_SHIFT

    def classify_domains(
        self,
        text: str,
        domain_keywords_map: Optional[dict[str, list[str]]] = None,
    ) -> list[str]:
        """Classify text into domains based on keyword matching.

        Args:
            text: User input text
            domain_keywords_map: Map of domain names to keywords

        Returns:
            List of detected domain names
        """
        if not domain_keywords_map:
            return []

        detected_domains = []
        text_lower = text.lower()
        tokens = set(self._tokenize_filtered(text))

        for domain, keywords in domain_keywords_map.items():
            keyword_set = set(kw.lower() for kw in keywords)

            # Check for keyword matches
            if tokens & keyword_set:
                detected_domains.append(domain)
            # Also check for phrase matches
            elif any(kw.lower() in text_lower for kw in keywords):
                detected_domains.append(domain)

        return detected_domains

    def analyze(
        self,
        user_input: str,
        available_intents: list[dict],
        domain_keywords: list[str],
        domain_keywords_map: Optional[dict[str, list[str]]] = None,
    ) -> SemanticAnalysis:
        """Perform complete semantic analysis of user input.

        Args:
            user_input: The user's input text
            available_intents: List of available intent dictionaries
            domain_keywords: Keywords defining the supported domain
            domain_keywords_map: Optional map of domain names to keywords

        Returns:
            Complete SemanticAnalysis result
        """
        # Handle edge cases
        if not user_input or not user_input.strip():
            return SemanticAnalysis(
                input_text=user_input or "",
                abstraction_level=AbstractionLevel.CONCRETE,
                nearest_intents=[],
                domain_classification=[],
                temporal_references=[],
                entity_mentions=[],
            )

        # Convert intent dicts to IntentDefinition objects
        intent_definitions = []
        for intent_dict in available_intents:
            intent_definitions.append(
                IntentDefinition(
                    name=intent_dict.get("name", ""),
                    description=intent_dict.get("description", ""),
                    keywords=intent_dict.get("keywords", []),
                    examples=intent_dict.get("examples", []),
                    capability_id=intent_dict.get("capability_id"),
                    domain=intent_dict.get("domain"),
                )
            )

        # Perform analyses
        abstraction_level = self.detect_abstraction_level(user_input)
        nearest_intents = self.rank_nearest_intents(user_input, intent_definitions)
        temporal_references = self.detect_temporal_references(user_input)
        entity_mentions = self.detect_entities(user_input)
        domain_classification = self.classify_domains(
            user_input, domain_keywords_map
        )

        # If no domain map provided, check against flat keywords
        if not domain_classification and domain_keywords:
            domain_similarity = self.calculate_domain_similarity(
                user_input, domain_keywords
            )
            if domain_similarity > 0.1:
                domain_classification = ["primary"]

        return SemanticAnalysis(
            input_text=user_input,
            abstraction_level=abstraction_level,
            nearest_intents=nearest_intents,
            domain_classification=domain_classification,
            temporal_references=temporal_references,
            entity_mentions=entity_mentions,
        )
