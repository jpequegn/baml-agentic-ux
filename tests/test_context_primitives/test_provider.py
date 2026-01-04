"""
Tests for Context Provider Interface and Data Classes

Part of Phase 7: BAML Context Primitives Implementation
"""

import pytest
from datetime import datetime, timezone, timedelta

from src.context_primitives import (
    ContextConfig,
    ContextBackend,
    ContextValueType,
    SessionContext,
    ConversationTurn,
    ConversationHistory,
    ContextValue,
    ContextVariables,
    ExecutionContext,
    InMemoryContextProvider,
    create_memory_provider,
)


class TestSessionContext:
    """Tests for SessionContext data class."""

    def test_create_session(self):
        """Test creating a session context."""
        session = SessionContext(
            session_id="test_123",
            user_id="user_1",
            metadata={"channel": "web"},
        )
        assert session.session_id == "test_123"
        assert session.user_id == "user_1"
        assert session.metadata == {"channel": "web"}
        assert session.is_active is True

    def test_touch_updates_last_activity(self):
        """Test that touch() updates last_activity."""
        session = SessionContext(session_id="test_123")
        original_time = session.last_activity
        session.touch()
        assert session.last_activity >= original_time

    def test_is_expired_with_ttl(self):
        """Test session expiration with TTL."""
        # Create session with very short TTL (already expired)
        past_time = datetime.now(timezone.utc) - timedelta(hours=2)
        session = SessionContext(
            session_id="test_123",
            ttl_seconds=3600,  # 1 hour
            last_activity=past_time,
        )
        assert session.is_expired() is True

    def test_is_expired_no_ttl(self):
        """Test session without TTL never expires."""
        past_time = datetime.now(timezone.utc) - timedelta(days=30)
        session = SessionContext(
            session_id="test_123",
            ttl_seconds=None,
            last_activity=past_time,
        )
        assert session.is_expired() is False


class TestConversationTurn:
    """Tests for ConversationTurn data class."""

    def test_create_turn(self):
        """Test creating a conversation turn."""
        turn = ConversationTurn(
            turn_id=1,
            timestamp=datetime.now(timezone.utc),
            user_input="Hello",
            assistant_response="Hi there!",
            detected_intent="greeting",
            confidence=0.95,
        )
        assert turn.turn_id == 1
        assert turn.user_input == "Hello"
        assert turn.detected_intent == "greeting"

    def test_to_dict_and_from_dict(self):
        """Test serialization round-trip."""
        turn = ConversationTurn(
            turn_id=1,
            timestamp=datetime.now(timezone.utc),
            user_input="Create a task",
            assistant_response="Task created",
            detected_intent="create-task",
            extracted_entities={"task_name": "Test"},
            confidence=0.9,
        )
        data = turn.to_dict()
        restored = ConversationTurn.from_dict(data)

        assert restored.turn_id == turn.turn_id
        assert restored.user_input == turn.user_input
        assert restored.detected_intent == turn.detected_intent
        assert restored.extracted_entities == turn.extracted_entities


class TestConversationHistory:
    """Tests for ConversationHistory data class."""

    def test_add_turn(self):
        """Test adding turns to history."""
        history = ConversationHistory(session_id="test_123", max_turns=20)

        turn = ConversationTurn(
            turn_id=1,
            timestamp=datetime.now(timezone.utc),
            user_input="Hello",
            assistant_response="Hi!",
        )
        history.add_turn(turn)

        assert len(history.turns) == 1
        assert history.total_turns == 1

    def test_windowing(self):
        """Test that history respects max_turns window."""
        history = ConversationHistory(session_id="test_123", max_turns=5)

        # Add 10 turns
        for i in range(10):
            turn = ConversationTurn(
                turn_id=i + 1,
                timestamp=datetime.now(timezone.utc),
                user_input=f"Message {i}",
                assistant_response=f"Response {i}",
            )
            history.add_turn(turn)

        # Should only keep last 5
        assert len(history.turns) == 5
        assert history.total_turns == 10
        assert history.turns[0].turn_id == 6  # First kept turn

    def test_get_recent(self):
        """Test getting recent turns."""
        history = ConversationHistory(session_id="test_123")

        for i in range(5):
            turn = ConversationTurn(
                turn_id=i + 1,
                timestamp=datetime.now(timezone.utc),
                user_input=f"Message {i}",
                assistant_response=f"Response {i}",
            )
            history.add_turn(turn)

        recent = history.get_recent(3)
        assert len(recent) == 3
        assert recent[-1].turn_id == 5


class TestContextValue:
    """Tests for ContextValue data class."""

    def test_from_string(self):
        """Test creating from string value."""
        value = ContextValue.from_value("hello")
        assert value.value_type == ContextValueType.STRING
        assert value.string_value == "hello"
        assert value.to_value() == "hello"

    def test_from_number(self):
        """Test creating from numeric value."""
        value = ContextValue.from_value(42)
        assert value.value_type == ContextValueType.NUMBER
        assert value.number_value == 42.0
        assert value.to_value() == 42.0

    def test_from_boolean(self):
        """Test creating from boolean value."""
        value = ContextValue.from_value(True)
        assert value.value_type == ContextValueType.BOOLEAN
        assert value.boolean_value is True
        assert value.to_value() is True

    def test_from_list(self):
        """Test creating from list value."""
        value = ContextValue.from_value([1, 2, 3])
        assert value.value_type == ContextValueType.LIST
        assert value.list_value == ["1", "2", "3"]

    def test_from_dict(self):
        """Test creating from dict value."""
        data = {"key": "value"}
        value = ContextValue.from_value(data)
        assert value.value_type == ContextValueType.OBJECT
        assert value.object_value == data

    def test_from_none(self):
        """Test creating from None value."""
        value = ContextValue.from_value(None)
        assert value.value_type == ContextValueType.NULL
        assert value.to_value() is None


class TestContextVariables:
    """Tests for ContextVariables data class."""

    def test_set_and_get(self):
        """Test setting and getting variables."""
        variables = ContextVariables(session_id="test_123")
        variables.set("name", "Alice")
        variables.set("count", 42)

        assert variables.get("name") == "Alice"
        assert variables.get("count") == 42.0

    def test_get_default(self):
        """Test getting non-existent variable returns default."""
        variables = ContextVariables(session_id="test_123")
        assert variables.get("missing") is None
        assert variables.get("missing", "default") == "default"

    def test_delete(self):
        """Test deleting variables."""
        variables = ContextVariables(session_id="test_123")
        variables.set("key", "value")
        assert variables.delete("key") is True
        assert variables.get("key") is None
        assert variables.delete("key") is False

    def test_keys(self):
        """Test getting all keys."""
        variables = ContextVariables(session_id="test_123")
        variables.set("a", 1)
        variables.set("b", 2)
        variables.set("c", 3)

        keys = variables.keys()
        assert sorted(keys) == ["a", "b", "c"]

    def test_to_flat_dict(self):
        """Test converting to flat dictionary."""
        variables = ContextVariables(session_id="test_123")
        variables.set("name", "Alice")
        variables.set("active", True)

        flat = variables.to_flat_dict()
        assert flat["name"] == "Alice"
        assert flat["active"] is True


class TestExecutionContext:
    """Tests for ExecutionContext data class."""

    def test_to_dict(self):
        """Test converting to dictionary."""
        session = SessionContext(session_id="test_123", user_id="user_1")
        history = ConversationHistory(session_id="test_123")
        variables = ContextVariables(session_id="test_123")
        variables.set("mode", "advanced")

        context = ExecutionContext(
            session=session,
            history=history,
            variables=variables,
            current_intent="greeting",
        )

        data = context.to_dict()
        assert data["session_id"] == "test_123"
        assert data["user_id"] == "user_1"
        assert data["variables"]["mode"] == "advanced"
        assert data["current_intent"] == "greeting"

    def test_to_conversation_context(self):
        """Test converting to BAML-compatible format."""
        session = SessionContext(session_id="test_123")
        history = ConversationHistory(session_id="test_123")

        turn = ConversationTurn(
            turn_id=1,
            timestamp=datetime.now(timezone.utc),
            user_input="Hello",
            assistant_response="Hi!",
        )
        history.add_turn(turn)

        variables = ContextVariables(session_id="test_123")
        context = ExecutionContext(session=session, history=history, variables=variables)

        conv_context = context.to_conversation_context()
        assert conv_context["session_id"] == "test_123"
        assert len(conv_context["recent_turns"]) == 1
        assert conv_context["turn_count"] == 1


class TestContextConfig:
    """Tests for ContextConfig data class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ContextConfig()
        assert config.max_history_turns == 20
        assert config.summarize_after == 10
        assert config.token_limit == 4000
        assert config.backend == ContextBackend.IN_MEMORY
        assert config.ttl_seconds == 3600

    def test_custom_config(self):
        """Test custom configuration."""
        config = ContextConfig(
            max_history_turns=50,
            backend=ContextBackend.REDIS,
            redis_url="redis://localhost:6379",
            ttl_seconds=7200,
        )
        assert config.max_history_turns == 50
        assert config.backend == ContextBackend.REDIS
        assert config.redis_url == "redis://localhost:6379"


class TestInMemoryProvider:
    """Tests for InMemoryContextProvider."""

    @pytest.fixture
    def provider(self):
        """Create a test provider."""
        return create_memory_provider(max_history_turns=20, ttl_seconds=3600)

    @pytest.mark.asyncio
    async def test_create_session(self, provider):
        """Test creating a session."""
        session = await provider.create_session("test_123", user_id="user_1")
        assert session.session_id == "test_123"
        assert session.user_id == "user_1"

    @pytest.mark.asyncio
    async def test_get_session(self, provider):
        """Test retrieving a session."""
        await provider.create_session("test_123")
        session = await provider.get_session("test_123")
        assert session is not None
        assert session.session_id == "test_123"

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self, provider):
        """Test getting a session that doesn't exist."""
        session = await provider.get_session("nonexistent")
        assert session is None

    @pytest.mark.asyncio
    async def test_delete_session(self, provider):
        """Test deleting a session."""
        await provider.create_session("test_123")
        result = await provider.delete_session("test_123")
        assert result is True

        session = await provider.get_session("test_123")
        assert session is None

    @pytest.mark.asyncio
    async def test_add_and_get_turns(self, provider):
        """Test adding and retrieving conversation turns."""
        await provider.create_session("test_123")

        turn = ConversationTurn(
            turn_id=1,
            timestamp=datetime.now(timezone.utc),
            user_input="Hello",
            assistant_response="Hi there!",
        )
        await provider.add_turn("test_123", turn)

        history = await provider.get_history("test_123")
        assert len(history.turns) == 1
        assert history.turns[0].user_input == "Hello"

    @pytest.mark.asyncio
    async def test_add_turn_creates_session(self, provider):
        """Test that adding a turn auto-creates session if needed."""
        turn = ConversationTurn(
            turn_id=1,
            timestamp=datetime.now(timezone.utc),
            user_input="Hello",
            assistant_response="Hi!",
        )
        await provider.add_turn("auto_session", turn)

        session = await provider.get_session("auto_session")
        assert session is not None

    @pytest.mark.asyncio
    async def test_set_and_get_variables(self, provider):
        """Test setting and getting context variables."""
        await provider.create_session("test_123")

        await provider.set_variable("test_123", "task_id", "task_456")
        await provider.set_variable("test_123", "count", 5)

        variables = await provider.get_variables("test_123")
        assert variables.get("task_id") == "task_456"
        assert variables.get("count") == 5.0

    @pytest.mark.asyncio
    async def test_delete_variable(self, provider):
        """Test deleting a context variable."""
        await provider.create_session("test_123")
        await provider.set_variable("test_123", "key", "value")

        result = await provider.delete_variable("test_123", "key")
        assert result is True

        variables = await provider.get_variables("test_123")
        assert variables.get("key") is None

    @pytest.mark.asyncio
    async def test_get_execution_context(self, provider):
        """Test getting complete execution context."""
        await provider.create_session("test_123", user_id="user_1")
        await provider.set_variable("test_123", "mode", "advanced")

        turn = ConversationTurn(
            turn_id=1,
            timestamp=datetime.now(timezone.utc),
            user_input="Hello",
            assistant_response="Hi!",
        )
        await provider.add_turn("test_123", turn)

        context = await provider.get_execution_context("test_123")
        assert context.session.session_id == "test_123"
        assert context.session.user_id == "user_1"
        assert context.variables.get("mode") == "advanced"
        assert len(context.history.turns) == 1

    @pytest.mark.asyncio
    async def test_get_execution_context_creates_session(self, provider):
        """Test that get_execution_context creates session if needed."""
        context = await provider.get_execution_context("new_session")
        assert context.session.session_id == "new_session"

    @pytest.mark.asyncio
    async def test_session_count(self, provider):
        """Test getting session count."""
        assert await provider.get_session_count() == 0

        await provider.create_session("session_1")
        await provider.create_session("session_2")

        assert await provider.get_session_count() == 2

    @pytest.mark.asyncio
    async def test_clear_all(self, provider):
        """Test clearing all sessions."""
        await provider.create_session("session_1")
        await provider.create_session("session_2")

        await provider.clear_all()

        assert await provider.get_session_count() == 0

    @pytest.mark.asyncio
    async def test_touch_session(self, provider):
        """Test touching a session updates last_activity."""
        await provider.create_session("test_123")
        session_before = await provider.get_session("test_123")

        result = await provider.touch_session("test_123")
        assert result is True

        session_after = await provider.get_session("test_123")
        assert session_after.last_activity >= session_before.last_activity

    @pytest.mark.asyncio
    async def test_session_exists(self, provider):
        """Test checking if session exists."""
        assert await provider.session_exists("test_123") is False

        await provider.create_session("test_123")
        assert await provider.session_exists("test_123") is True
