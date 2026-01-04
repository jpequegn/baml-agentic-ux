"""Redirect Suggestion Engine for intent drift handling.

This module provides tools for generating relevant redirect suggestions
when drift is detected, guiding users to available capabilities.

Issue #84 - Task 5.7: Redirect Suggestion Engine
Part of #28 - Phase 5: Intent Drift Detection
Dependencies: Task 5.3 (Drift Classifier)
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .semantic_analyzer import IntentDefinition, SemanticAnalyzer
from .types import (
    DriftType,
    NearestIntent,
    RedirectSuggestion,
    SemanticAnalysis,
)


# ============================================
# Redirect Engine Enums
# ============================================


class RedirectStrategy(Enum):
    """Strategy for ranking redirect suggestions."""

    SEMANTIC_SIMILARITY = "semantic_similarity"
    """Rank by semantic similarity to original request."""

    CORE_CAPABILITIES = "core_capabilities"
    """Prioritize core/primary capabilities."""

    PRACTICAL_ACTIONS = "practical_actions"
    """Prioritize practical, actionable intents."""

    NON_PERSONAL = "non_personal"
    """Prioritize intents that don't require personal data."""

    CURRENT_FOCUSED = "current_focused"
    """Prioritize intents focused on current state/time."""

    DIVERSITY = "diversity"
    """Maximize diversity across capabilities."""


# ============================================
# Redirect Engine Configuration
# ============================================


@dataclass
class RedirectEngineConfig:
    """Configuration for the redirect suggestion engine.

    Attributes:
        min_relevance_threshold: Minimum relevance score for suggestions (0-1)
        max_suggestions: Default maximum number of suggestions
        diversity_weight: Weight for diversity in ranking (0-1)
        recency_penalty: Penalty for recently failed intents (0-1)
        core_capability_boost: Boost for core capabilities (0-1)
        phrase_variation: Whether to vary redirect phrases
        include_explanation: Whether to include redirect reasons
    """

    min_relevance_threshold: float = 0.2
    max_suggestions: int = 3
    diversity_weight: float = 0.3
    recency_penalty: float = 0.5
    core_capability_boost: float = 0.2
    phrase_variation: bool = True
    include_explanation: bool = True

    def __post_init__(self):
        """Validate configuration values."""
        if not 0.0 <= self.min_relevance_threshold <= 1.0:
            raise ValueError("min_relevance_threshold must be between 0.0 and 1.0")
        if self.max_suggestions < 1:
            raise ValueError("max_suggestions must be at least 1")
        if not 0.0 <= self.diversity_weight <= 1.0:
            raise ValueError("diversity_weight must be between 0.0 and 1.0")
        if not 0.0 <= self.recency_penalty <= 1.0:
            raise ValueError("recency_penalty must be between 0.0 and 1.0")
        if not 0.0 <= self.core_capability_boost <= 1.0:
            raise ValueError("core_capability_boost must be between 0.0 and 1.0")


# ============================================
# Redirect Phrase Templates
# ============================================


# Phrase templates organized by style
REDIRECT_PHRASE_TEMPLATES = {
    "offer": [
        "Would you like me to {action} instead?",
        "I can help you {action} if that's useful.",
        "How about we {action}?",
        "Would it help if I {action}?",
    ],
    "suggest": [
        "I could {action} for you.",
        "Perhaps I can {action}.",
        "You might find it helpful if I {action}.",
        "One thing I can do is {action}.",
    ],
    "capability": [
        "I'm able to {action}.",
        "Something I can help with is {action}.",
        "I have the ability to {action}.",
        "What I can do is {action}.",
    ],
    "question": [
        "Would {action} be helpful?",
        "Are you interested in {action}?",
        "Should I {action}?",
        "Do you want me to {action}?",
    ],
}

# Reason templates by drift type
REDIRECT_REASON_TEMPLATES = {
    DriftType.SCOPE_EXPANSION: [
        "This is related to your request",
        "This covers a similar area",
        "This is the closest match to what you asked",
    ],
    DriftType.DOMAIN_SHIFT: [
        "This is one of my core capabilities",
        "This is something I'm designed to help with",
        "This falls within my expertise",
    ],
    DriftType.ABSTRACTION_CLIMB: [
        "This is a practical action I can take",
        "This provides concrete help",
        "This gives you something actionable",
    ],
    DriftType.PERSONALIZATION: [
        "This doesn't require personal information",
        "This works without access to your data",
        "This is a general capability I can offer",
    ],
    DriftType.TEMPORAL_DRIFT: [
        "This focuses on current information",
        "This uses up-to-date data",
        "This works with present-day context",
    ],
    DriftType.AMBIGUOUS: [
        "This might be what you're looking for",
        "This is one interpretation of your request",
        "This could help clarify what you need",
    ],
    DriftType.NONE: [
        "This is a related capability",
        "This might also be helpful",
        "This is something else I can assist with",
    ],
}


# ============================================
# Scored Suggestion for Internal Ranking
# ============================================


@dataclass
class ScoredSuggestion:
    """Internal representation of a scored redirect suggestion.

    Attributes:
        intent: The intent definition
        base_score: Base similarity score
        adjusted_score: Score after adjustments
        domain: Domain of the intent
        is_core: Whether this is a core capability
        requires_personal_data: Whether personal data is needed
        is_current_focused: Whether focused on current state
    """

    intent: IntentDefinition
    base_score: float
    adjusted_score: float = 0.0
    domain: Optional[str] = None
    is_core: bool = False
    requires_personal_data: bool = False
    is_current_focused: bool = True


# ============================================
# Conversation Context for Redirect Engine
# ============================================


@dataclass
class RedirectContext:
    """Context for generating redirect suggestions.

    Attributes:
        failed_intents: Recently failed intent names
        successful_intents: Recently successful intent names
        current_domain: Current conversation domain
        turn_count: Number of turns in conversation
        last_successful_action: Last successful action taken
    """

    failed_intents: list[str] = field(default_factory=list)
    successful_intents: list[str] = field(default_factory=list)
    current_domain: Optional[str] = None
    turn_count: int = 0
    last_successful_action: Optional[str] = None


# ============================================
# Main Redirect Suggestion Engine
# ============================================


class RedirectSuggestionEngine:
    """Generates relevant redirect suggestions for drift scenarios.

    This engine analyzes the user's input and drift context to suggest
    alternative capabilities that might be helpful. It uses semantic
    similarity, drift-type specific ranking, and context awareness
    to generate relevant suggestions.

    Attributes:
        config: Engine configuration
        semantic_analyzer: Analyzer for similarity calculations
        available_intents: List of available intent definitions
        core_capability_names: Names of core capabilities

    Example:
        >>> engine = RedirectSuggestionEngine(available_intents=intents)
        >>> suggestions = engine.suggest_redirects(
        ...     semantic_result=analysis,
        ...     drift_type=DriftType.DOMAIN_SHIFT,
        ...     max_suggestions=3
        ... )
    """

    def __init__(
        self,
        config: Optional[RedirectEngineConfig] = None,
        available_intents: Optional[list[IntentDefinition]] = None,
        core_capability_names: Optional[list[str]] = None,
        semantic_analyzer: Optional[SemanticAnalyzer] = None,
    ):
        """Initialize the redirect suggestion engine.

        Args:
            config: Engine configuration
            available_intents: Available intent definitions
            core_capability_names: Names of core/primary capabilities
            semantic_analyzer: Optional pre-configured analyzer
        """
        self.config = config or RedirectEngineConfig()
        self.semantic_analyzer = semantic_analyzer or SemanticAnalyzer()
        self.available_intents = available_intents or []
        self.core_capability_names = set(core_capability_names or [])
        self._phrase_index = 0  # For rotating phrases

    def set_available_intents(self, intents: list[IntentDefinition]) -> None:
        """Set the available intents for suggestion.

        Args:
            intents: List of intent definitions
        """
        self.available_intents = intents

    def set_core_capabilities(self, names: list[str]) -> None:
        """Set the core capability names.

        Args:
            names: List of core capability names
        """
        self.core_capability_names = set(names)

    def suggest_redirects(
        self,
        semantic_result: SemanticAnalysis,
        drift_type: DriftType,
        max_suggestions: Optional[int] = None,
        context: Optional[RedirectContext] = None,
    ) -> list[RedirectSuggestion]:
        """Generate redirect suggestions based on drift analysis.

        Args:
            semantic_result: Semantic analysis result
            drift_type: Type of drift detected
            max_suggestions: Maximum suggestions (uses config default)
            context: Optional conversation context

        Returns:
            List of redirect suggestions, ranked by relevance
        """
        max_suggestions = max_suggestions or self.config.max_suggestions
        context = context or RedirectContext()

        if not self.available_intents:
            return []

        # Get the ranking strategy for this drift type
        strategy = self._get_strategy_for_drift_type(drift_type)

        # Score all available intents
        scored = self._score_intents(
            semantic_result=semantic_result,
            drift_type=drift_type,
            strategy=strategy,
            context=context,
        )

        # Filter by minimum relevance
        filtered = [
            s for s in scored
            if s.adjusted_score >= self.config.min_relevance_threshold
        ]

        # Apply diversity selection if needed
        if self.config.diversity_weight > 0:
            selected = self._select_diverse(filtered, max_suggestions)
        else:
            selected = sorted(
                filtered, key=lambda x: x.adjusted_score, reverse=True
            )[:max_suggestions]

        # Convert to RedirectSuggestion objects
        return [
            self._create_suggestion(s, drift_type, semantic_result)
            for s in selected
        ]

    def suggest_redirects_from_input(
        self,
        user_input: str,
        drift_type: DriftType,
        max_suggestions: Optional[int] = None,
        context: Optional[RedirectContext] = None,
    ) -> list[RedirectSuggestion]:
        """Generate redirect suggestions from raw user input.

        Convenience method that performs semantic analysis first.

        Args:
            user_input: User's input text
            drift_type: Type of drift detected
            max_suggestions: Maximum suggestions
            context: Optional conversation context

        Returns:
            List of redirect suggestions
        """
        # Convert intents to dict format for analyzer
        intent_dicts = [
            {
                "name": intent.name,
                "description": intent.description,
                "keywords": intent.keywords,
                "examples": intent.examples,
                "capability_id": intent.capability_id,
                "domain": intent.domain,
            }
            for intent in self.available_intents
        ]

        # Perform semantic analysis
        semantic_result = self.semantic_analyzer.analyze(
            user_input=user_input,
            available_intents=intent_dicts,
            domain_keywords=[],
        )

        return self.suggest_redirects(
            semantic_result=semantic_result,
            drift_type=drift_type,
            max_suggestions=max_suggestions,
            context=context,
        )

    def _get_strategy_for_drift_type(self, drift_type: DriftType) -> RedirectStrategy:
        """Get the ranking strategy for a drift type.

        Args:
            drift_type: Type of drift

        Returns:
            Appropriate ranking strategy
        """
        strategy_map = {
            DriftType.SCOPE_EXPANSION: RedirectStrategy.SEMANTIC_SIMILARITY,
            DriftType.DOMAIN_SHIFT: RedirectStrategy.CORE_CAPABILITIES,
            DriftType.ABSTRACTION_CLIMB: RedirectStrategy.PRACTICAL_ACTIONS,
            DriftType.PERSONALIZATION: RedirectStrategy.NON_PERSONAL,
            DriftType.TEMPORAL_DRIFT: RedirectStrategy.CURRENT_FOCUSED,
            DriftType.AMBIGUOUS: RedirectStrategy.DIVERSITY,
            DriftType.NONE: RedirectStrategy.SEMANTIC_SIMILARITY,
        }
        return strategy_map.get(drift_type, RedirectStrategy.SEMANTIC_SIMILARITY)

    def _score_intents(
        self,
        semantic_result: SemanticAnalysis,
        drift_type: DriftType,
        strategy: RedirectStrategy,
        context: RedirectContext,
    ) -> list[ScoredSuggestion]:
        """Score all available intents for suggestion.

        Args:
            semantic_result: Semantic analysis result
            drift_type: Type of drift
            strategy: Ranking strategy
            context: Conversation context

        Returns:
            List of scored suggestions
        """
        # Build a map of nearest intent scores from semantic analysis
        intent_scores: dict[str, float] = {
            ni.intent_name: ni.similarity
            for ni in semantic_result.nearest_intents
        }

        scored = []
        for intent in self.available_intents:
            # Get base score from semantic analysis or calculate
            if intent.name in intent_scores:
                base_score = intent_scores[intent.name]
            else:
                # Calculate similarity if not in analysis
                similarity = self.semantic_analyzer.calculate_combined_similarity(
                    semantic_result.input_text,
                    f"{intent.description} {' '.join(intent.keywords)}",
                )
                base_score = similarity.score

            # Determine intent properties
            is_core = intent.name in self.core_capability_names
            requires_personal = self._requires_personal_data(intent)
            is_current = self._is_current_focused(intent)

            suggestion = ScoredSuggestion(
                intent=intent,
                base_score=base_score,
                domain=intent.domain,
                is_core=is_core,
                requires_personal_data=requires_personal,
                is_current_focused=is_current,
            )

            # Apply adjustments based on strategy
            suggestion.adjusted_score = self._apply_strategy_adjustments(
                suggestion, strategy, context
            )

            scored.append(suggestion)

        return scored

    def _apply_strategy_adjustments(
        self,
        suggestion: ScoredSuggestion,
        strategy: RedirectStrategy,
        context: RedirectContext,
    ) -> float:
        """Apply strategy-specific score adjustments.

        Args:
            suggestion: The scored suggestion
            strategy: Ranking strategy
            context: Conversation context

        Returns:
            Adjusted score
        """
        score = suggestion.base_score

        # Apply recency penalty for failed intents
        if suggestion.intent.name in context.failed_intents:
            score *= (1 - self.config.recency_penalty)

        # Apply boost for related to last successful action
        if (
            context.last_successful_action
            and suggestion.intent.domain == context.current_domain
        ):
            score *= 1.1

        # Strategy-specific adjustments
        if strategy == RedirectStrategy.CORE_CAPABILITIES:
            if suggestion.is_core:
                score += self.config.core_capability_boost

        elif strategy == RedirectStrategy.PRACTICAL_ACTIONS:
            # Boost practical/actionable intents
            if self._is_practical_intent(suggestion.intent):
                score *= 1.2

        elif strategy == RedirectStrategy.NON_PERSONAL:
            # Penalize intents requiring personal data
            if suggestion.requires_personal_data:
                score *= 0.5

        elif strategy == RedirectStrategy.CURRENT_FOCUSED:
            # Boost current-focused intents
            if suggestion.is_current_focused:
                score *= 1.2

        # Clamp score to valid range
        return min(1.0, max(0.0, score))

    def _requires_personal_data(self, intent: IntentDefinition) -> bool:
        """Check if intent requires personal data.

        Args:
            intent: Intent definition

        Returns:
            True if personal data is required
        """
        personal_indicators = [
            "my ", "your ", "personal", "account", "profile",
            "history", "preference", "settings", "private",
        ]
        text = f"{intent.name} {intent.description}".lower()
        return any(indicator in text for indicator in personal_indicators)

    def _is_current_focused(self, intent: IntentDefinition) -> bool:
        """Check if intent is focused on current state/time.

        Args:
            intent: Intent definition

        Returns:
            True if focused on current state
        """
        temporal_indicators = [
            "historical", "past", "future", "prediction",
            "forecast", "archive", "old", "previous",
        ]
        text = f"{intent.name} {intent.description}".lower()
        return not any(indicator in text for indicator in temporal_indicators)

    def _is_practical_intent(self, intent: IntentDefinition) -> bool:
        """Check if intent is practical/actionable.

        Args:
            intent: Intent definition

        Returns:
            True if practical/actionable
        """
        action_verbs = [
            "create", "make", "build", "add", "remove", "delete",
            "update", "change", "set", "get", "find", "search",
            "show", "display", "send", "submit", "save", "load",
            "open", "close", "start", "stop", "run", "execute",
            "check", "verify", "validate", "calculate", "convert",
        ]
        text = f"{intent.name} {intent.description}".lower()
        return any(verb in text for verb in action_verbs)

    def _select_diverse(
        self,
        scored: list[ScoredSuggestion],
        max_count: int,
    ) -> list[ScoredSuggestion]:
        """Select diverse suggestions from scored list.

        Uses a combination of score and diversity to select suggestions.

        Args:
            scored: List of scored suggestions
            max_count: Maximum number to select

        Returns:
            Diverse selection of suggestions
        """
        if len(scored) <= max_count:
            return sorted(scored, key=lambda x: x.adjusted_score, reverse=True)

        # Sort by score
        sorted_scored = sorted(scored, key=lambda x: x.adjusted_score, reverse=True)

        selected: list[ScoredSuggestion] = []
        selected_domains: set[str] = set()

        for suggestion in sorted_scored:
            if len(selected) >= max_count:
                break

            # Check for diversity
            domain = suggestion.domain or "default"
            if domain in selected_domains and self.config.diversity_weight > 0:
                # Apply diversity penalty
                if random.random() < self.config.diversity_weight:
                    continue

            selected.append(suggestion)
            selected_domains.add(domain)

        # If we don't have enough, fill from remaining
        if len(selected) < max_count:
            for suggestion in sorted_scored:
                if suggestion not in selected:
                    selected.append(suggestion)
                    if len(selected) >= max_count:
                        break

        return selected

    def _create_suggestion(
        self,
        scored: ScoredSuggestion,
        drift_type: DriftType,
        semantic_result: SemanticAnalysis,
    ) -> RedirectSuggestion:
        """Create a RedirectSuggestion from scored suggestion.

        Args:
            scored: The scored suggestion
            drift_type: Type of drift
            semantic_result: Semantic analysis result

        Returns:
            RedirectSuggestion object
        """
        # Generate redirect phrase
        transition_phrase = self.generate_redirect_phrase(
            scored.intent, semantic_result.input_text
        )

        # Generate reason
        redirect_reason = self._generate_reason(scored, drift_type)

        # Calculate confidence based on score and context
        confidence = self._calculate_confidence(scored, drift_type)

        return RedirectSuggestion(
            target_intent=scored.intent.name,
            similarity_score=scored.base_score,
            redirect_reason=redirect_reason,
            transition_phrase=transition_phrase,
            confidence=confidence,
        )

    def generate_redirect_phrase(
        self,
        intent: IntentDefinition,
        original_input: str,
    ) -> str:
        """Generate a natural redirect phrase for an intent.

        Args:
            intent: The intent to redirect to
            original_input: Original user input

        Returns:
            Natural language redirect phrase
        """
        # Extract action from intent
        action = self._extract_action_phrase(intent)

        # Select template style based on intent type
        if self._is_practical_intent(intent):
            style = "offer"
        elif intent.name in self.core_capability_names:
            style = "capability"
        else:
            style = random.choice(["offer", "suggest", "question"])

        # Get template
        templates = REDIRECT_PHRASE_TEMPLATES.get(style, REDIRECT_PHRASE_TEMPLATES["offer"])

        if self.config.phrase_variation:
            template = random.choice(templates)
        else:
            self._phrase_index = (self._phrase_index + 1) % len(templates)
            template = templates[self._phrase_index]

        return template.format(action=action)

    def _extract_action_phrase(self, intent: IntentDefinition) -> str:
        """Extract an action phrase from intent definition.

        Args:
            intent: Intent definition

        Returns:
            Action phrase for templates
        """
        # Try to extract from description
        description = intent.description.lower()

        # Common patterns to extract action
        action_starters = [
            "helps you ", "allows you to ", "enables you to ",
            "lets you ", "can ", "will ",
        ]

        for starter in action_starters:
            if starter in description:
                idx = description.find(starter) + len(starter)
                action = description[idx:].split(".")[0].strip()
                return action

        # Use name as fallback, converting underscores/camelCase
        name = intent.name.replace("_", " ").replace("-", " ")
        # Handle camelCase
        import re
        name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name).lower()

        return name

    def _generate_reason(
        self,
        scored: ScoredSuggestion,
        drift_type: DriftType,
    ) -> str:
        """Generate a reason for the redirect suggestion.

        Args:
            scored: The scored suggestion
            drift_type: Type of drift

        Returns:
            Reason string
        """
        if not self.config.include_explanation:
            return ""

        templates = REDIRECT_REASON_TEMPLATES.get(
            drift_type, REDIRECT_REASON_TEMPLATES[DriftType.NONE]
        )

        return random.choice(templates)

    def _calculate_confidence(
        self,
        scored: ScoredSuggestion,
        drift_type: DriftType,
    ) -> float:
        """Calculate confidence in the suggestion.

        Args:
            scored: The scored suggestion
            drift_type: Type of drift

        Returns:
            Confidence score (0-1)
        """
        # Base confidence on adjusted score
        confidence = scored.adjusted_score

        # Boost confidence for core capabilities
        if scored.is_core:
            confidence = min(1.0, confidence + 0.1)

        # Reduce confidence for ambiguous drift
        if drift_type == DriftType.AMBIGUOUS:
            confidence *= 0.8

        # Boost confidence for high base scores
        if scored.base_score > 0.7:
            confidence = min(1.0, confidence + 0.1)

        return min(1.0, max(0.0, confidence))

    def get_suggestions_for_nearest_intents(
        self,
        nearest_intents: list[NearestIntent],
        drift_type: DriftType,
        max_suggestions: Optional[int] = None,
    ) -> list[RedirectSuggestion]:
        """Generate suggestions directly from nearest intents.

        Args:
            nearest_intents: List of nearest intents from analysis
            drift_type: Type of drift
            max_suggestions: Maximum suggestions

        Returns:
            List of redirect suggestions
        """
        max_suggestions = max_suggestions or self.config.max_suggestions

        # Filter by minimum relevance
        filtered = [
            ni for ni in nearest_intents
            if ni.similarity >= self.config.min_relevance_threshold
        ]

        # Sort by similarity
        sorted_intents = sorted(
            filtered, key=lambda x: x.similarity, reverse=True
        )[:max_suggestions]

        suggestions = []
        for ni in sorted_intents:
            # Find intent definition if available
            intent_def = next(
                (i for i in self.available_intents if i.name == ni.intent_name),
                None,
            )

            if intent_def:
                phrase = self.generate_redirect_phrase(intent_def, "")
            else:
                phrase = f"Would you like me to help with {ni.intent_name}?"

            reason = random.choice(
                REDIRECT_REASON_TEMPLATES.get(
                    drift_type, REDIRECT_REASON_TEMPLATES[DriftType.NONE]
                )
            )

            suggestions.append(
                RedirectSuggestion(
                    target_intent=ni.intent_name,
                    similarity_score=ni.similarity,
                    redirect_reason=reason,
                    transition_phrase=phrase,
                    confidence=min(1.0, ni.similarity + 0.1),
                )
            )

        return suggestions
