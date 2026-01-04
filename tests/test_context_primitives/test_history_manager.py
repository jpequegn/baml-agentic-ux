"""
Tests for History Manager

Part of Phase 7: BAML Context Primitives Implementation
Issue #104 - Task 7.4: History Manager
"""

import pytest
from datetime import datetime, timezone, timedelta

from src.context_primitives import (
    ConversationTurn,
    ConversationHistory,
)
from src.context_primitives.history_manager import (
    # Token counting
    TiktokenCounter,
    SimpleTokenCounter,
    # Truncation
    TruncationStrategy,
    TruncationConfig,
    # Importance scoring
    TurnImportance,
    ImportanceWeights,
    ImportanceScorer,
    # Summarization
    ConversationSummary,
    SimpleSummarizer,
    # History manager
    HistoryManager,
    create_history_manager,
)


# ============================================
# Test Fixtures
# ============================================


def create_turn(
    turn_id: int,
    user_input: str = "Hello",
    assistant_response: str = "Hi there!",
    detected_intent: str | None = None,
    entities: dict | None = None,
    confidence: float | None = None,
) -> ConversationTurn:
    """Helper to create conversation turns for testing."""
    return ConversationTurn(
        turn_id=turn_id,
        timestamp=datetime.now(timezone.utc),
        user_input=user_input,
        assistant_response=assistant_response,
        detected_intent=detected_intent,
        extracted_entities=entities,
        confidence=confidence,
    )


def create_history(
    session_id: str = "test_session",
    num_turns: int = 10,
    max_turns: int = 20,
) -> ConversationHistory:
    """Helper to create conversation history for testing."""
    turns = [
        create_turn(
            turn_id=i + 1,
            user_input=f"User message {i + 1}",
            assistant_response=f"Assistant response {i + 1}",
            detected_intent=f"intent_{i % 3}",
            entities={"entity_key": f"value_{i}"} if i % 2 == 0 else None,
            confidence=0.7 + (i % 3) * 0.1,
        )
        for i in range(num_turns)
    ]

    history = ConversationHistory(
        session_id=session_id,
        max_turns=max_turns,
    )
    for turn in turns:
        history.add_turn(turn)

    return history


# ============================================
# Token Counter Tests
# ============================================


class TestSimpleTokenCounter:
    """Tests for SimpleTokenCounter."""

    def test_count_basic_text(self):
        """Test counting tokens in basic text."""
        counter = SimpleTokenCounter(chars_per_token=4.0)

        # 20 characters / 4 = 5 tokens
        assert counter.count("Hello World Test!!") == 4  # 18 chars / 4 = 4.5 -> 4

    def test_count_empty_text(self):
        """Test counting empty text returns 1 (minimum)."""
        counter = SimpleTokenCounter()
        assert counter.count("") == 1

    def test_count_turn(self):
        """Test counting tokens in a conversation turn."""
        counter = SimpleTokenCounter(chars_per_token=4.0)
        turn = create_turn(
            turn_id=1,
            user_input="Hello",  # 5 chars
            assistant_response="Hi there!",  # 9 chars
        )
        # (5 + 9) / 4 = 3.5 -> 3
        assert counter.count_turn(turn) == 3

    def test_count_turn_with_metadata(self):
        """Test counting turn with intent and entities."""
        counter = SimpleTokenCounter(chars_per_token=4.0)
        turn = create_turn(
            turn_id=1,
            user_input="Hello",
            assistant_response="Hi!",
            detected_intent="greeting",
            entities={"name": "Test"},
        )
        # Total chars includes intent and entities
        tokens = counter.count_turn(turn)
        assert tokens > 0


class TestTiktokenCounter:
    """Tests for TiktokenCounter."""

    def test_count_basic_text(self):
        """Test counting tokens with tiktoken (or fallback)."""
        counter = TiktokenCounter(model="gpt-4")
        tokens = counter.count("Hello, world!")
        assert tokens > 0

    def test_count_empty_text(self):
        """Test counting empty text."""
        counter = TiktokenCounter()
        # Should return at least 1 (from fallback) or 0 (from tiktoken)
        tokens = counter.count("")
        assert tokens >= 0

    def test_count_turn(self):
        """Test counting tokens in a turn."""
        counter = TiktokenCounter()
        turn = create_turn(turn_id=1)
        tokens = counter.count_turn(turn)
        assert tokens > 0

    def test_fallback_model(self):
        """Test that unknown model falls back gracefully."""
        counter = TiktokenCounter(model="unknown-model-xyz")
        tokens = counter.count("Test text")
        assert tokens > 0


# ============================================
# Truncation Config Tests
# ============================================


class TestTruncationConfig:
    """Tests for TruncationConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = TruncationConfig()
        assert config.strategy == TruncationStrategy.SLIDING_WINDOW
        assert config.max_turns == 20
        assert config.max_tokens == 4000
        assert config.importance_threshold == 0.3
        assert config.keep_first_turn is True
        assert config.keep_last_n == 3

    def test_custom_config(self):
        """Test custom configuration."""
        config = TruncationConfig(
            strategy=TruncationStrategy.TOKEN_BASED,
            max_turns=10,
            max_tokens=2000,
            importance_threshold=0.5,
        )
        assert config.strategy == TruncationStrategy.TOKEN_BASED
        assert config.max_turns == 10
        assert config.max_tokens == 2000

    def test_invalid_max_turns(self):
        """Test that invalid max_turns raises error."""
        with pytest.raises(ValueError, match="max_turns must be at least 1"):
            TruncationConfig(max_turns=0)

    def test_invalid_max_tokens(self):
        """Test that invalid max_tokens raises error."""
        with pytest.raises(ValueError, match="max_tokens must be at least 100"):
            TruncationConfig(max_tokens=50)

    def test_invalid_threshold(self):
        """Test that invalid importance_threshold raises error."""
        with pytest.raises(ValueError, match="importance_threshold must be between"):
            TruncationConfig(importance_threshold=1.5)


# ============================================
# Importance Scoring Tests
# ============================================


class TestImportanceWeights:
    """Tests for ImportanceWeights."""

    def test_default_weights(self):
        """Test default weights sum to 1.0."""
        weights = ImportanceWeights()
        total = weights.recency + weights.relevance + weights.entity + weights.intent
        assert abs(total - 1.0) < 0.001

    def test_custom_weights(self):
        """Test custom weights validation."""
        weights = ImportanceWeights(
            recency=0.25,
            relevance=0.25,
            entity=0.25,
            intent=0.25,
        )
        assert weights.recency == 0.25

    def test_invalid_weights(self):
        """Test that weights not summing to 1.0 raise error."""
        with pytest.raises(ValueError, match="Weights must sum to 1.0"):
            ImportanceWeights(
                recency=0.5,
                relevance=0.5,
                entity=0.5,
                intent=0.5,
            )


class TestImportanceScorer:
    """Tests for ImportanceScorer."""

    def test_score_single_turn(self):
        """Test scoring a single turn."""
        scorer = ImportanceScorer()
        turn = create_turn(turn_id=1, detected_intent="greeting", confidence=0.9)

        importance = scorer.score_turn(turn, turn_index=0, total_turns=1)

        assert importance.turn_id == 1
        assert 0.0 <= importance.overall_score <= 1.0
        assert importance.recency_score == 1.0  # Only turn = most recent

    def test_score_multiple_turns(self):
        """Test scoring multiple turns - recency increases with index."""
        scorer = ImportanceScorer()
        turns = [create_turn(turn_id=i + 1) for i in range(5)]

        scores = []
        for i, turn in enumerate(turns):
            importance = scorer.score_turn(turn, i, len(turns))
            scores.append(importance.recency_score)

        # Recency should increase (newer turns score higher)
        for i in range(1, len(scores)):
            assert scores[i] > scores[i - 1]

    def test_score_with_context(self):
        """Test scoring with current context for relevance."""
        scorer = ImportanceScorer(current_context="task management project")
        turn = create_turn(
            turn_id=1,
            user_input="Create a new task for the project",
            assistant_response="Task created successfully",
        )

        importance = scorer.score_turn(turn, 0, 1)

        # Should have some relevance due to word overlap
        assert importance.relevance_score > 0.0

    def test_score_with_important_entities(self):
        """Test scoring with important entity tracking."""
        scorer = ImportanceScorer()
        scorer.set_important_entities(["task_id", "project_id"])

        turn = create_turn(
            turn_id=1,
            entities={"task_id": "123", "other_field": "value"},
        )

        importance = scorer.score_turn(turn, 0, 1)

        # Should have entity score due to matching important entity
        assert importance.entity_score > 0.0

    def test_score_turns_with_threshold(self):
        """Test scoring turns and marking retention."""
        scorer = ImportanceScorer()
        turns = [create_turn(turn_id=i + 1) for i in range(5)]

        scored = scorer.score_turns(turns, threshold=0.3)

        assert len(scored) == 5
        # Some turns should be marked for retention based on score
        retained = [s for s in scored if s.should_retain]
        assert len(retained) > 0


# ============================================
# Summarizer Tests
# ============================================


class TestSimpleSummarizer:
    """Tests for SimpleSummarizer."""

    @pytest.mark.asyncio
    async def test_summarize_empty_turns(self):
        """Test summarizing empty turn list."""
        summarizer = SimpleSummarizer()
        summary = await summarizer.summarize([])

        assert summary.summary == "No conversation to summarize."
        assert summary.turn_count == 0

    @pytest.mark.asyncio
    async def test_summarize_basic(self):
        """Test basic summarization."""
        summarizer = SimpleSummarizer()
        turns = [
            create_turn(
                turn_id=1,
                user_input="Create a task",
                assistant_response="Task created",
                detected_intent="create_task",
            ),
            create_turn(
                turn_id=2,
                user_input="Show my tasks",
                assistant_response="Here are your tasks",
                detected_intent="list_tasks",
            ),
        ]

        summary = await summarizer.summarize(turns)

        assert summary.turn_count == 2
        assert "create_task" in summary.key_intents or "list_tasks" in summary.key_intents
        assert summary.start_turn == 1
        assert summary.end_turn == 2

    @pytest.mark.asyncio
    async def test_summarize_with_existing(self):
        """Test updating an existing summary."""
        summarizer = SimpleSummarizer()
        turns = [create_turn(turn_id=3)]

        summary = await summarizer.summarize(
            turns,
            existing_summary="Previous conversation about tasks.",
        )

        assert "Previous" in summary.summary
        assert summary.turn_count == 1

    @pytest.mark.asyncio
    async def test_summarize_with_max_length(self):
        """Test summary truncation with max_length."""
        summarizer = SimpleSummarizer()
        turns = [create_turn(turn_id=i + 1) for i in range(10)]

        summary = await summarizer.summarize(turns, max_length=100)

        assert len(summary.summary) <= 100

    @pytest.mark.asyncio
    async def test_summarize_extracts_entities(self):
        """Test that entities are extracted."""
        summarizer = SimpleSummarizer()
        turns = [
            create_turn(
                turn_id=1,
                entities={"task_id": "123", "project": "test"},
            ),
        ]

        summary = await summarizer.summarize(turns)

        assert "task_id" in summary.key_entities or "project" in summary.key_entities


# ============================================
# History Manager Tests
# ============================================


class TestHistoryManager:
    """Tests for HistoryManager."""

    @pytest.fixture
    def manager(self):
        """Create a test history manager."""
        return create_history_manager(
            strategy=TruncationStrategy.SLIDING_WINDOW,
            max_turns=5,
            max_tokens=1000,
        )

    @pytest.mark.asyncio
    async def test_truncate_no_change_needed(self, manager):
        """Test truncation when history is within limits."""
        history = create_history(num_turns=3)

        result = await manager.truncate(history)

        assert result.final_count == 3
        assert len(result.removed_turns) == 0

    @pytest.mark.asyncio
    async def test_truncate_sliding_window(self, manager):
        """Test sliding window truncation."""
        history = create_history(num_turns=10)

        result = await manager.truncate(
            history,
            strategy=TruncationStrategy.SLIDING_WINDOW,
        )

        # Should keep max_turns (5) including first turn
        assert result.final_count <= 5
        assert result.original_count == 10
        # First turn should be retained (keep_first_turn=True by default)
        assert result.retained_turns[0].turn_id == 1

    @pytest.mark.asyncio
    async def test_truncate_token_based(self, manager):
        """Test token-based truncation."""
        # Create history with longer messages to exceed token limit
        history = ConversationHistory(session_id="test", max_turns=100)
        for i in range(50):
            turn = create_turn(
                turn_id=i + 1,
                user_input="This is a much longer user message that contains many more tokens " * 5,
                assistant_response="This is a much longer assistant response with detailed information " * 5,
            )
            history.add_turn(turn)

        result = await manager.truncate(
            history,
            strategy=TruncationStrategy.TOKEN_BASED,
        )

        # Should reduce turns since we exceed token limit
        assert result.final_count < result.original_count
        assert result.final_tokens <= manager.config.max_tokens

    @pytest.mark.asyncio
    async def test_truncate_importance_based(self, manager):
        """Test importance-based truncation."""
        history = create_history(num_turns=10)

        result = await manager.truncate(
            history,
            strategy=TruncationStrategy.IMPORTANCE_BASED,
        )

        assert result.final_count <= manager.config.max_turns
        # Last turns should be retained (high recency)
        turn_ids = [t.turn_id for t in result.retained_turns]
        assert history.turns[-1].turn_id in turn_ids

    @pytest.mark.asyncio
    async def test_truncate_with_summarization(self, manager):
        """Test truncation with summarization."""
        history = create_history(num_turns=10)

        result = await manager.truncate(
            history,
            strategy=TruncationStrategy.SUMMARIZE,
        )

        # Should have a summary of removed turns
        if result.removed_turns:
            assert result.summary is not None
            assert result.summary.turn_count > 0

    @pytest.mark.asyncio
    async def test_truncate_hybrid(self, manager):
        """Test hybrid truncation strategy."""
        # Create manager with lower summarize threshold
        config = TruncationConfig(
            strategy=TruncationStrategy.HYBRID,
            max_turns=5,
            summarize_threshold=3,
        )
        manager = HistoryManager(config=config)
        history = create_history(num_turns=10)

        result = await manager.truncate(history)

        assert result.final_count <= config.max_turns

    def test_count_tokens(self, manager):
        """Test token counting for history."""
        history = create_history(num_turns=5)

        token_count = manager.count_tokens(history)

        assert token_count > 0

    def test_estimate_context_size(self, manager):
        """Test context size estimation."""
        history = create_history(num_turns=5)
        history.summary = "This is a summary of previous conversation."

        estimate = manager.estimate_context_size(history)

        assert "turn_tokens" in estimate
        assert "summary_tokens" in estimate
        assert "total_tokens" in estimate
        assert estimate["turn_count"] == 5
        assert estimate["summary_tokens"] > 0

    @pytest.mark.asyncio
    async def test_update_summary_not_needed(self, manager):
        """Test summary update when not needed."""
        history = create_history(num_turns=3)

        summary = await manager.update_summary(history)

        # Not enough turns to trigger summarization
        assert summary is None

    @pytest.mark.asyncio
    async def test_update_summary_forced(self, manager):
        """Test forced summary update."""
        history = create_history(num_turns=10)

        summary = await manager.update_summary(history, force=True)

        assert summary is not None
        assert summary.turn_count > 0


class TestCreateHistoryManager:
    """Tests for factory function."""

    def test_create_with_defaults(self):
        """Test creating manager with defaults."""
        manager = create_history_manager()

        assert manager.config.strategy == TruncationStrategy.SLIDING_WINDOW
        assert manager.config.max_turns == 20
        assert manager.config.max_tokens == 4000

    def test_create_token_based(self):
        """Test creating token-based manager."""
        manager = create_history_manager(
            strategy=TruncationStrategy.TOKEN_BASED,
            max_tokens=2000,
        )

        assert manager.config.strategy == TruncationStrategy.TOKEN_BASED
        assert manager.config.max_tokens == 2000

    def test_create_with_llm_summarization(self):
        """Test creating manager with LLM summarization."""
        manager = create_history_manager(use_llm_summarization=True)

        # Should have LLMSummarizer (which will fall back if BAML not available)
        assert manager.summarizer is not None


class TestTruncationResult:
    """Tests for TruncationResult metrics."""

    @pytest.mark.asyncio
    async def test_result_metrics(self):
        """Test that truncation result has accurate metrics."""
        manager = create_history_manager(max_turns=5)
        history = create_history(num_turns=10)

        result = await manager.truncate(history)

        assert result.original_count == 10
        assert result.final_count == len(result.retained_turns)
        assert result.original_tokens > 0
        assert result.final_tokens > 0
        assert result.final_tokens <= result.original_tokens
        assert result.strategy_used == TruncationStrategy.SLIDING_WINDOW


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.mark.asyncio
    async def test_truncate_empty_history(self):
        """Test truncating empty history."""
        manager = create_history_manager()
        history = ConversationHistory(session_id="test", max_turns=20)

        result = await manager.truncate(history)

        assert result.final_count == 0
        assert len(result.retained_turns) == 0

    @pytest.mark.asyncio
    async def test_truncate_single_turn(self):
        """Test truncating single-turn history."""
        manager = create_history_manager(max_turns=5)
        history = create_history(num_turns=1)

        result = await manager.truncate(history)

        assert result.final_count == 1
        assert result.retained_turns[0].turn_id == 1

    @pytest.mark.asyncio
    async def test_truncate_exactly_at_limit(self):
        """Test truncating history exactly at limit."""
        manager = create_history_manager(max_turns=5)
        history = create_history(num_turns=5)

        result = await manager.truncate(history)

        assert result.final_count == 5
        assert len(result.removed_turns) == 0

    def test_importance_scorer_no_context(self):
        """Test importance scorer without context."""
        scorer = ImportanceScorer()  # No context
        turn = create_turn(turn_id=1)

        importance = scorer.score_turn(turn, 0, 1)

        # Should still work with neutral relevance
        assert importance.relevance_score == 0.5

    def test_importance_scorer_empty_entities(self):
        """Test importance scorer with no entities."""
        scorer = ImportanceScorer()
        turn = create_turn(turn_id=1, entities=None)

        importance = scorer.score_turn(turn, 0, 1)

        assert importance.entity_score == 0.0
