"""
History Manager for Conversation Context

Implements conversation history management with truncation and summarization
strategies for LUI (Language User Interface) context management.

Part of Phase 7: BAML Context Primitives Implementation
Issue #104 - Task 7.4: History Manager

Features:
- Token counting with tiktoken
- Sliding window truncation
- Token-based truncation
- Importance-based truncation
- LLM-powered summarization

Requirements:
    pip install tiktoken  # For token counting (optional, gracefully degrades)
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional

from src.context_primitives.provider import (
    ConversationHistory,
    ConversationTurn,
)


# ============================================
# Token Counter Interface
# ============================================


class TokenCounter(ABC):
    """Abstract interface for token counting."""

    @abstractmethod
    def count(self, text: str) -> int:
        """Count tokens in text."""
        pass

    @abstractmethod
    def count_turn(self, turn: ConversationTurn) -> int:
        """Count tokens in a conversation turn."""
        pass


class TiktokenCounter(TokenCounter):
    """Token counter using tiktoken library.

    Provides accurate token counting for OpenAI models.
    Falls back to estimate if tiktoken is not available.
    """

    def __init__(self, model: str = "gpt-4"):
        """Initialize with a model encoding.

        Args:
            model: Model name for encoding (default: gpt-4)
        """
        self._model = model
        self._encoding = None
        self._fallback = False

        try:
            import tiktoken
            try:
                self._encoding = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fall back to cl100k_base for unknown models
                self._encoding = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            self._fallback = True

    def count(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: Text to count tokens in

        Returns:
            Number of tokens
        """
        if self._fallback or self._encoding is None:
            return self._estimate_tokens(text)
        return len(self._encoding.encode(text))

    def count_turn(self, turn: ConversationTurn) -> int:
        """Count tokens in a conversation turn.

        Counts tokens in user input, assistant response, and metadata.

        Args:
            turn: Conversation turn to count

        Returns:
            Total token count for the turn
        """
        parts = [turn.user_input, turn.assistant_response]

        if turn.detected_intent:
            parts.append(turn.detected_intent)

        if turn.extracted_entities:
            parts.append(str(turn.extracted_entities))

        return sum(self.count(part) for part in parts)

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Estimate token count without tiktoken.

        Uses simple heuristic: ~4 characters per token.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        # Roughly 4 characters per token for English text
        return max(1, len(text) // 4)


class SimpleTokenCounter(TokenCounter):
    """Simple token counter using character-based estimation.

    Useful when tiktoken is not available or for fast approximations.
    """

    def __init__(self, chars_per_token: float = 4.0):
        """Initialize with characters per token ratio.

        Args:
            chars_per_token: Average characters per token (default: 4.0)
        """
        self._chars_per_token = chars_per_token

    def count(self, text: str) -> int:
        """Count tokens using character estimation."""
        return max(1, int(len(text) / self._chars_per_token))

    def count_turn(self, turn: ConversationTurn) -> int:
        """Count tokens in a conversation turn."""
        total_chars = len(turn.user_input) + len(turn.assistant_response)
        if turn.detected_intent:
            total_chars += len(turn.detected_intent)
        if turn.extracted_entities:
            total_chars += len(str(turn.extracted_entities))
        return max(1, int(total_chars / self._chars_per_token))


# ============================================
# Truncation Strategies
# ============================================


class TruncationStrategy(Enum):
    """Strategy for truncating conversation history."""

    SLIDING_WINDOW = "sliding_window"
    """Keep last N turns, discard older."""

    TOKEN_BASED = "token_based"
    """Keep turns until token limit reached."""

    IMPORTANCE_BASED = "importance_based"
    """Score turns and keep most important."""

    SUMMARIZE = "summarize"
    """Summarize old turns before discarding."""

    HYBRID = "hybrid"
    """Combine summarization with windowing."""


@dataclass
class TruncationConfig:
    """Configuration for history truncation.

    Attributes:
        strategy: Which truncation strategy to use
        max_turns: Maximum turns for sliding window (default: 20)
        max_tokens: Maximum tokens for token-based (default: 4000)
        importance_threshold: Threshold for importance-based (0-1, default: 0.3)
        keep_first_turn: Always keep the first turn (default: True)
        keep_last_n: Always keep at least this many recent turns (default: 3)
        summarize_threshold: Summarize when exceeding this many turns (default: 10)
    """

    strategy: TruncationStrategy = TruncationStrategy.SLIDING_WINDOW
    max_turns: int = 20
    max_tokens: int = 4000
    importance_threshold: float = 0.3
    keep_first_turn: bool = True
    keep_last_n: int = 3
    summarize_threshold: int = 10

    def __post_init__(self):
        """Validate configuration."""
        if self.max_turns < 1:
            raise ValueError("max_turns must be at least 1")
        if self.max_tokens < 100:
            raise ValueError("max_tokens must be at least 100")
        if not 0.0 <= self.importance_threshold <= 1.0:
            raise ValueError("importance_threshold must be between 0.0 and 1.0")
        if self.keep_last_n < 1:
            raise ValueError("keep_last_n must be at least 1")


# ============================================
# Turn Importance Scoring
# ============================================


@dataclass
class TurnImportance:
    """Importance assessment for a conversation turn.

    Attributes:
        turn_id: Which turn this assessment is for
        recency_score: Score based on how recent (0-1)
        relevance_score: Score based on relevance to current context (0-1)
        entity_score: Score based on entity presence (0-1)
        intent_score: Score based on successful intent detection (0-1)
        overall_score: Weighted combination of scores (0-1)
        should_retain: Whether this turn should be kept
    """

    turn_id: int
    recency_score: float = 0.0
    relevance_score: float = 0.0
    entity_score: float = 0.0
    intent_score: float = 0.0
    overall_score: float = 0.0
    should_retain: bool = False


@dataclass
class ImportanceWeights:
    """Weights for importance scoring factors.

    Attributes:
        recency: Weight for recency score (default: 0.3)
        relevance: Weight for relevance score (default: 0.3)
        entity: Weight for entity presence score (default: 0.2)
        intent: Weight for intent detection score (default: 0.2)
    """

    recency: float = 0.3
    relevance: float = 0.3
    entity: float = 0.2
    intent: float = 0.2

    def __post_init__(self):
        """Validate weights sum to 1.0."""
        total = self.recency + self.relevance + self.entity + self.intent
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")


class ImportanceScorer:
    """Scores conversation turns by importance.

    Uses multiple factors to determine which turns are most
    important to retain in context.

    Attributes:
        weights: Factor weights for scoring
        current_context: Optional current context for relevance scoring
    """

    def __init__(
        self,
        weights: Optional[ImportanceWeights] = None,
        current_context: Optional[str] = None,
    ):
        """Initialize the importance scorer.

        Args:
            weights: Custom weights for scoring factors
            current_context: Current conversation context for relevance
        """
        self.weights = weights or ImportanceWeights()
        self.current_context = current_context or ""
        self._important_intents: set[str] = set()
        self._important_entities: set[str] = set()

    def set_important_intents(self, intents: list[str]) -> None:
        """Set intents considered important to retain.

        Args:
            intents: List of important intent names
        """
        self._important_intents = set(intents)

    def set_important_entities(self, entities: list[str]) -> None:
        """Set entity keys considered important to retain.

        Args:
            entities: List of important entity keys
        """
        self._important_entities = set(entities)

    def score_turn(
        self,
        turn: ConversationTurn,
        turn_index: int,
        total_turns: int,
    ) -> TurnImportance:
        """Score a single turn's importance.

        Args:
            turn: The conversation turn to score
            turn_index: Position in the turn list (0-indexed)
            total_turns: Total number of turns

        Returns:
            TurnImportance with all scores
        """
        # Recency score: newer turns score higher
        if total_turns > 1:
            recency = turn_index / (total_turns - 1)
        else:
            recency = 1.0

        # Relevance score: based on text similarity to current context
        relevance = self._calculate_relevance(turn)

        # Entity score: based on entity presence
        entity = self._calculate_entity_score(turn)

        # Intent score: based on intent detection
        intent = self._calculate_intent_score(turn)

        # Calculate overall weighted score
        overall = (
            self.weights.recency * recency
            + self.weights.relevance * relevance
            + self.weights.entity * entity
            + self.weights.intent * intent
        )

        return TurnImportance(
            turn_id=turn.turn_id,
            recency_score=recency,
            relevance_score=relevance,
            entity_score=entity,
            intent_score=intent,
            overall_score=overall,
        )

    def score_turns(
        self,
        turns: list[ConversationTurn],
        threshold: float = 0.3,
    ) -> list[TurnImportance]:
        """Score all turns and mark which to retain.

        Args:
            turns: List of conversation turns
            threshold: Minimum score to retain (default: 0.3)

        Returns:
            List of TurnImportance assessments
        """
        total = len(turns)
        scored = []

        for i, turn in enumerate(turns):
            importance = self.score_turn(turn, i, total)
            importance.should_retain = importance.overall_score >= threshold
            scored.append(importance)

        return scored

    def _calculate_relevance(self, turn: ConversationTurn) -> float:
        """Calculate relevance score based on text similarity.

        Args:
            turn: Turn to calculate relevance for

        Returns:
            Relevance score (0-1)
        """
        if not self.current_context:
            return 0.5  # Neutral score if no context

        # Simple word overlap for relevance
        context_words = set(self.current_context.lower().split())
        turn_words = set(
            f"{turn.user_input} {turn.assistant_response}".lower().split()
        )

        if not context_words or not turn_words:
            return 0.0

        overlap = len(context_words & turn_words)
        max_possible = min(len(context_words), len(turn_words))

        return overlap / max_possible if max_possible > 0 else 0.0

    def _calculate_entity_score(self, turn: ConversationTurn) -> float:
        """Calculate entity presence score.

        Args:
            turn: Turn to calculate entity score for

        Returns:
            Entity score (0-1)
        """
        if not turn.extracted_entities:
            return 0.0

        if not self._important_entities:
            # All entities considered somewhat important
            return min(1.0, len(turn.extracted_entities) * 0.2)

        # Score based on important entity presence
        present = set(turn.extracted_entities.keys()) & self._important_entities
        return len(present) / len(self._important_entities)

    def _calculate_intent_score(self, turn: ConversationTurn) -> float:
        """Calculate intent detection score.

        Args:
            turn: Turn to calculate intent score for

        Returns:
            Intent score (0-1)
        """
        if not turn.detected_intent:
            return 0.0

        # Base score from confidence
        base_score = turn.confidence if turn.confidence else 0.5

        # Boost if intent is in important set
        if (
            self._important_intents
            and turn.detected_intent in self._important_intents
        ):
            base_score = min(1.0, base_score + 0.3)

        return base_score


# ============================================
# Summarization Types
# ============================================


@dataclass
class ConversationSummary:
    """Summary of conversation turns.

    Attributes:
        summary: The text summary
        key_entities: Important entities mentioned
        key_intents: Main intents from summarized turns
        current_state: Current conversation state/topic
        start_turn: First turn number summarized
        end_turn: Last turn number summarized
        turn_count: Number of turns summarized
        token_count: Token count of the summary
        created_at: When summary was created
    """

    summary: str
    key_entities: list[str] = field(default_factory=list)
    key_intents: list[str] = field(default_factory=list)
    current_state: Optional[str] = None
    start_turn: int = 0
    end_turn: int = 0
    turn_count: int = 0
    token_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class Summarizer(ABC):
    """Abstract interface for conversation summarization."""

    @abstractmethod
    async def summarize(
        self,
        turns: list[ConversationTurn],
        existing_summary: Optional[str] = None,
        max_length: Optional[int] = None,
    ) -> ConversationSummary:
        """Summarize conversation turns.

        Args:
            turns: Turns to summarize
            existing_summary: Previous summary to update
            max_length: Maximum summary length in characters

        Returns:
            ConversationSummary with the result
        """
        pass


class SimpleSummarizer(Summarizer):
    """Simple rule-based summarizer.

    Creates basic summaries without LLM. Useful for testing
    and when LLM access is not available.
    """

    def __init__(self, token_counter: Optional[TokenCounter] = None):
        """Initialize with optional token counter.

        Args:
            token_counter: Counter for token estimation
        """
        self._token_counter = token_counter or SimpleTokenCounter()

    async def summarize(
        self,
        turns: list[ConversationTurn],
        existing_summary: Optional[str] = None,
        max_length: Optional[int] = None,
    ) -> ConversationSummary:
        """Create simple rule-based summary.

        Args:
            turns: Turns to summarize
            existing_summary: Previous summary to update
            max_length: Maximum summary length

        Returns:
            ConversationSummary
        """
        if not turns:
            return ConversationSummary(
                summary="No conversation to summarize.",
                turn_count=0,
            )

        # Collect entities and intents
        entities: set[str] = set()
        intents: set[str] = set()

        for turn in turns:
            if turn.detected_intent:
                intents.add(turn.detected_intent)
            if turn.extracted_entities:
                entities.update(turn.extracted_entities.keys())

        # Build summary text
        parts = []

        if existing_summary:
            parts.append(f"Previous context: {existing_summary}")

        parts.append(f"Conversation of {len(turns)} turns.")

        if intents:
            parts.append(f"Topics discussed: {', '.join(sorted(intents))}.")

        if entities:
            parts.append(f"Key elements: {', '.join(sorted(entities))}.")

        # Add recent context
        if turns:
            last_turn = turns[-1]
            parts.append(f"Most recent topic: {last_turn.user_input[:100]}...")

        summary_text = " ".join(parts)

        # Truncate if needed
        if max_length and len(summary_text) > max_length:
            summary_text = summary_text[: max_length - 3] + "..."

        return ConversationSummary(
            summary=summary_text,
            key_entities=sorted(entities),
            key_intents=sorted(intents),
            current_state=turns[-1].detected_intent if turns else None,
            start_turn=turns[0].turn_id if turns else 0,
            end_turn=turns[-1].turn_id if turns else 0,
            turn_count=len(turns),
            token_count=self._token_counter.count(summary_text),
        )


class LLMSummarizer(Summarizer):
    """LLM-powered conversation summarizer.

    Uses BAML SummarizeConversation function for high-quality summaries.
    Falls back to simple summarization if BAML is not available.
    """

    def __init__(
        self,
        token_counter: Optional[TokenCounter] = None,
        baml_client: Optional[Any] = None,
    ):
        """Initialize with BAML client.

        Args:
            token_counter: Token counter for estimation
            baml_client: BAML client instance (optional, will try import)
        """
        self._token_counter = token_counter or TiktokenCounter()
        self._baml_client = baml_client
        self._fallback = SimpleSummarizer(token_counter)

    async def summarize(
        self,
        turns: list[ConversationTurn],
        existing_summary: Optional[str] = None,
        max_length: Optional[int] = None,
    ) -> ConversationSummary:
        """Summarize using LLM.

        Args:
            turns: Turns to summarize
            existing_summary: Previous summary to update
            max_length: Maximum summary length

        Returns:
            ConversationSummary
        """
        if not turns:
            return await self._fallback.summarize(turns, existing_summary, max_length)

        try:
            # Try to use BAML client
            if self._baml_client is None:
                try:
                    from baml_client import b

                    self._baml_client = b
                except ImportError:
                    return await self._fallback.summarize(
                        turns, existing_summary, max_length
                    )

            # Format turns for BAML
            turn_dicts = [
                {
                    "turn_id": t.turn_id,
                    "timestamp": t.timestamp.isoformat() if t.timestamp else "",
                    "user_input": t.user_input,
                    "assistant_response": t.assistant_response,
                    "detected_intent": t.detected_intent,
                    "extracted_entities": t.extracted_entities,
                    "confidence": t.confidence,
                }
                for t in turns
            ]

            # Call BAML function
            result = await self._baml_client.SummarizeConversation(
                turns=turn_dicts,
                existing_summary=existing_summary,
                max_length=max_length,
            )

            return ConversationSummary(
                summary=result.summary,
                key_entities=result.key_entities or [],
                key_intents=result.key_intents or [],
                current_state=result.current_state,
                start_turn=turns[0].turn_id if turns else 0,
                end_turn=turns[-1].turn_id if turns else 0,
                turn_count=len(turns),
                token_count=self._token_counter.count(result.summary),
            )

        except Exception:
            # Fall back to simple summarization
            return await self._fallback.summarize(turns, existing_summary, max_length)


# ============================================
# History Manager
# ============================================


@dataclass
class TruncationResult:
    """Result of history truncation.

    Attributes:
        retained_turns: Turns kept after truncation
        removed_turns: Turns removed during truncation
        summary: Generated summary of removed turns
        original_count: Original number of turns
        final_count: Final number of turns
        original_tokens: Original token count
        final_tokens: Final token count
        strategy_used: Which strategy was applied
    """

    retained_turns: list[ConversationTurn]
    removed_turns: list[ConversationTurn] = field(default_factory=list)
    summary: Optional[ConversationSummary] = None
    original_count: int = 0
    final_count: int = 0
    original_tokens: int = 0
    final_tokens: int = 0
    strategy_used: TruncationStrategy = TruncationStrategy.SLIDING_WINDOW


class HistoryManager:
    """Manages conversation history with truncation and summarization.

    Provides multiple strategies for managing context window size
    while preserving important conversation context.

    Example:
        >>> manager = HistoryManager(
        ...     config=TruncationConfig(
        ...         strategy=TruncationStrategy.TOKEN_BASED,
        ...         max_tokens=4000
        ...     )
        ... )
        >>> result = await manager.truncate(history)
        >>> print(f"Reduced from {result.original_count} to {result.final_count} turns")
    """

    def __init__(
        self,
        config: Optional[TruncationConfig] = None,
        token_counter: Optional[TokenCounter] = None,
        summarizer: Optional[Summarizer] = None,
        importance_scorer: Optional[ImportanceScorer] = None,
    ):
        """Initialize the history manager.

        Args:
            config: Truncation configuration
            token_counter: Token counter implementation
            summarizer: Summarizer implementation
            importance_scorer: Importance scorer for importance-based truncation
        """
        self.config = config or TruncationConfig()
        self.token_counter = token_counter or TiktokenCounter()
        self.summarizer = summarizer or SimpleSummarizer(self.token_counter)
        self.importance_scorer = importance_scorer or ImportanceScorer()

    async def truncate(
        self,
        history: ConversationHistory,
        strategy: Optional[TruncationStrategy] = None,
    ) -> TruncationResult:
        """Truncate history using configured strategy.

        Args:
            history: Conversation history to truncate
            strategy: Override strategy (uses config default if None)

        Returns:
            TruncationResult with retained turns and summary
        """
        strategy = strategy or self.config.strategy

        # Calculate original metrics
        original_count = len(history.turns)
        original_tokens = sum(
            self.token_counter.count_turn(t) for t in history.turns
        )

        # Apply strategy
        if strategy == TruncationStrategy.SLIDING_WINDOW:
            result = self._truncate_sliding_window(history)
        elif strategy == TruncationStrategy.TOKEN_BASED:
            result = self._truncate_token_based(history)
        elif strategy == TruncationStrategy.IMPORTANCE_BASED:
            result = self._truncate_importance_based(history)
        elif strategy == TruncationStrategy.SUMMARIZE:
            result = await self._truncate_with_summarization(history)
        elif strategy == TruncationStrategy.HYBRID:
            result = await self._truncate_hybrid(history)
        else:
            result = self._truncate_sliding_window(history)

        # Update metrics
        result.original_count = original_count
        result.original_tokens = original_tokens
        result.final_count = len(result.retained_turns)
        result.final_tokens = sum(
            self.token_counter.count_turn(t) for t in result.retained_turns
        )
        result.strategy_used = strategy

        return result

    def _truncate_sliding_window(
        self,
        history: ConversationHistory,
    ) -> TruncationResult:
        """Apply sliding window truncation.

        Keeps the most recent N turns.

        Args:
            history: History to truncate

        Returns:
            TruncationResult
        """
        turns = history.turns
        max_turns = self.config.max_turns

        if len(turns) <= max_turns:
            return TruncationResult(retained_turns=list(turns))

        # Keep first turn if configured
        if self.config.keep_first_turn and turns:
            first_turn = turns[0]
            remaining = turns[-(max_turns - 1) :]
            retained = [first_turn] + list(remaining)
            removed = turns[1 : -(max_turns - 1)]
        else:
            retained = list(turns[-max_turns:])
            removed = list(turns[:-max_turns])

        return TruncationResult(
            retained_turns=retained,
            removed_turns=removed,
        )

    def _truncate_token_based(
        self,
        history: ConversationHistory,
    ) -> TruncationResult:
        """Apply token-based truncation.

        Keeps turns until token limit is reached, working backwards
        from most recent.

        Args:
            history: History to truncate

        Returns:
            TruncationResult
        """
        turns = history.turns
        max_tokens = self.config.max_tokens

        # Calculate token count for each turn
        turn_tokens = [
            (t, self.token_counter.count_turn(t)) for t in turns
        ]

        total_tokens = sum(tokens for _, tokens in turn_tokens)

        if total_tokens <= max_tokens:
            return TruncationResult(retained_turns=list(turns))

        retained: list[ConversationTurn] = []
        removed: list[ConversationTurn] = []
        current_tokens = 0

        # Always keep last N turns
        keep_last = min(self.config.keep_last_n, len(turns))
        guaranteed_turns = turns[-keep_last:]
        guaranteed_tokens = sum(
            self.token_counter.count_turn(t) for t in guaranteed_turns
        )

        # Check if first turn should be kept
        first_turn_tokens = 0
        if self.config.keep_first_turn and turns:
            first_turn_tokens = self.token_counter.count_turn(turns[0])

        available_tokens = max_tokens - guaranteed_tokens - first_turn_tokens

        # Work backwards through non-guaranteed turns
        middle_turns = turns[1:-keep_last] if self.config.keep_first_turn else turns[:-keep_last]

        for turn, tokens in reversed(list(zip(middle_turns, [self.token_counter.count_turn(t) for t in middle_turns]))):
            if current_tokens + tokens <= available_tokens:
                retained.insert(0, turn)
                current_tokens += tokens
            else:
                removed.insert(0, turn)

        # Add first turn if kept
        if self.config.keep_first_turn and turns:
            retained.insert(0, turns[0])

        # Add guaranteed last turns
        retained.extend(guaranteed_turns)

        return TruncationResult(
            retained_turns=retained,
            removed_turns=removed,
        )

    def _truncate_importance_based(
        self,
        history: ConversationHistory,
    ) -> TruncationResult:
        """Apply importance-based truncation.

        Scores each turn and keeps the most important ones.

        Args:
            history: History to truncate

        Returns:
            TruncationResult
        """
        turns = history.turns

        if len(turns) <= self.config.max_turns:
            return TruncationResult(retained_turns=list(turns))

        # Score all turns
        scored = self.importance_scorer.score_turns(
            turns, threshold=self.config.importance_threshold
        )

        # Always keep first and last N turns
        retained_indices: set[int] = set()
        removed_indices: set[int] = set()

        if self.config.keep_first_turn:
            retained_indices.add(0)

        for i in range(max(0, len(turns) - self.config.keep_last_n), len(turns)):
            retained_indices.add(i)

        # Sort remaining by score
        remaining_scored = [
            (i, s) for i, s in enumerate(scored)
            if i not in retained_indices
        ]
        remaining_scored.sort(key=lambda x: x[1].overall_score, reverse=True)

        # Keep top scoring until max_turns
        slots_available = self.config.max_turns - len(retained_indices)

        for i, importance in remaining_scored[:slots_available]:
            retained_indices.add(i)

        for i, importance in remaining_scored[slots_available:]:
            removed_indices.add(i)

        # Build result lists preserving order
        retained = [turns[i] for i in sorted(retained_indices)]
        removed = [turns[i] for i in sorted(removed_indices)]

        return TruncationResult(
            retained_turns=retained,
            removed_turns=removed,
        )

    async def _truncate_with_summarization(
        self,
        history: ConversationHistory,
    ) -> TruncationResult:
        """Apply truncation with summarization of removed turns.

        Args:
            history: History to truncate

        Returns:
            TruncationResult with summary
        """
        # First apply sliding window
        result = self._truncate_sliding_window(history)

        # Summarize removed turns
        if result.removed_turns:
            summary = await self.summarizer.summarize(
                result.removed_turns,
                existing_summary=history.summary,
            )
            result.summary = summary

        return result

    async def _truncate_hybrid(
        self,
        history: ConversationHistory,
    ) -> TruncationResult:
        """Apply hybrid truncation strategy.

        Combines importance-based selection with summarization.

        Args:
            history: History to truncate

        Returns:
            TruncationResult with summary
        """
        turns = history.turns

        # If under summarize threshold, just use importance-based
        if len(turns) <= self.config.summarize_threshold:
            return self._truncate_importance_based(history)

        # Split into summarize vs. keep sections
        summarize_count = len(turns) - self.config.summarize_threshold
        to_summarize = turns[:summarize_count]
        to_evaluate = turns[summarize_count:]

        # Generate summary for old turns
        summary = await self.summarizer.summarize(
            to_summarize,
            existing_summary=history.summary,
        )

        # Apply importance-based on remaining
        temp_history = ConversationHistory(
            session_id=history.session_id,
            turns=to_evaluate,
            max_turns=self.config.max_turns,
        )
        result = self._truncate_importance_based(temp_history)

        result.removed_turns = list(to_summarize) + result.removed_turns
        result.summary = summary

        return result

    def count_tokens(self, history: ConversationHistory) -> int:
        """Count total tokens in history.

        Args:
            history: Conversation history

        Returns:
            Total token count
        """
        total = sum(self.token_counter.count_turn(t) for t in history.turns)
        if history.summary:
            total += self.token_counter.count(history.summary)
        return total

    def estimate_context_size(
        self,
        history: ConversationHistory,
        include_summary: bool = True,
    ) -> dict[str, int]:
        """Estimate context size breakdown.

        Args:
            history: Conversation history
            include_summary: Whether to include summary in estimate

        Returns:
            Dict with token counts by component
        """
        turn_tokens = sum(self.token_counter.count_turn(t) for t in history.turns)
        summary_tokens = 0

        if include_summary and history.summary:
            summary_tokens = self.token_counter.count(history.summary)

        return {
            "turn_tokens": turn_tokens,
            "summary_tokens": summary_tokens,
            "total_tokens": turn_tokens + summary_tokens,
            "turn_count": len(history.turns),
        }

    async def update_summary(
        self,
        history: ConversationHistory,
        force: bool = False,
    ) -> Optional[ConversationSummary]:
        """Update conversation summary if needed.

        Args:
            history: Conversation history
            force: Force summary update even if not needed

        Returns:
            New summary if updated, None otherwise
        """
        should_update = force or (
            len(history.turns) >= self.config.summarize_threshold
            and (not history.summary or history.total_turns > len(history.turns) + 5)
        )

        if not should_update:
            return None

        # Summarize turns beyond the window
        if len(history.turns) > self.config.keep_last_n:
            to_summarize = history.turns[:-self.config.keep_last_n]
            return await self.summarizer.summarize(
                to_summarize,
                existing_summary=history.summary,
            )

        return None


# ============================================
# Factory Functions
# ============================================


def create_history_manager(
    strategy: TruncationStrategy = TruncationStrategy.SLIDING_WINDOW,
    max_turns: int = 20,
    max_tokens: int = 4000,
    use_llm_summarization: bool = False,
    model: str = "gpt-4",
) -> HistoryManager:
    """Create a configured history manager.

    Args:
        strategy: Truncation strategy to use
        max_turns: Maximum turns for sliding window
        max_tokens: Maximum tokens for token-based
        use_llm_summarization: Whether to use LLM for summarization
        model: Model name for token counting

    Returns:
        Configured HistoryManager
    """
    config = TruncationConfig(
        strategy=strategy,
        max_turns=max_turns,
        max_tokens=max_tokens,
    )

    token_counter = TiktokenCounter(model=model)

    summarizer: Summarizer
    if use_llm_summarization:
        summarizer = LLMSummarizer(token_counter=token_counter)
    else:
        summarizer = SimpleSummarizer(token_counter=token_counter)

    return HistoryManager(
        config=config,
        token_counter=token_counter,
        summarizer=summarizer,
    )
