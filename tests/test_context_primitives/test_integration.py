"""
Tests for BAML Integration Layer.

Tests ContextManager, ContextualBAML, and context injection functionality.

Part of Phase 7: BAML Context Primitives Implementation
Issue #106 - Task 7.6: BAML Integration Layer
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass
from typing import Optional

from src.context_primitives.integration import (
    ContextManager,
    ContextualBAML,
    ContextualResult,
    with_context,
    create_context_manager,
)
from src.context_primitives.provider import (
    ContextConfig,
    ExecutionContext,
    SessionContext,
    ConversationHistory,
    ContextVariables,
)
from src.context_primitives.stores.memory import InMemoryContextProvider


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def config():
    """Create test configuration."""
    return ContextConfig(
        max_history_turns=10,
        ttl_seconds=3600,
    )


@pytest.fixture
def memory_provider(config):
    """Create in-memory provider for testing."""
    return InMemoryContextProvider(config)


@pytest.fixture
async def manager(memory_provider):
    """Create initialized context manager."""
    mgr = ContextManager(provider=memory_provider)
    await mgr.initialize()
    yield mgr
    await mgr.close()


@pytest.fixture
def mock_baml_client():
    """Create mock BAML client."""

    @dataclass
    class IntentResult:
        intent: str
        confidence: float
        entities: Optional[dict] = None

    @dataclass
    class ResponseResult:
        response: str
        intent: Optional[str] = None

    # Use spec to prevent auto-creating nonexistent attributes
    client = MagicMock(spec=["ExtractIntent", "GenerateResponse"])

    # Mock ExtractIntent
    async def mock_extract_intent(**kwargs):
        return IntentResult(
            intent="greeting",
            confidence=0.95,
            entities={"sentiment": "positive"},
        )

    client.ExtractIntent = AsyncMock(side_effect=mock_extract_intent)

    # Mock GenerateResponse
    async def mock_generate_response(**kwargs):
        user_input = kwargs.get("user_input", "")
        return ResponseResult(
            response=f"Response to: {user_input}",
            intent="greeting",
        )

    client.GenerateResponse = AsyncMock(side_effect=mock_generate_response)

    return client


# ============================================
# ContextManager Tests
# ============================================


class TestContextManager:
    """Tests for ContextManager class."""

    @pytest.mark.asyncio
    async def test_initialization(self, memory_provider):
        """Test manager initialization."""
        manager = ContextManager(provider=memory_provider)
        assert not manager._initialized

        await manager.initialize()
        assert manager._initialized
        assert manager.provider is not None

        await manager.close()

    @pytest.mark.asyncio
    async def test_double_initialization(self, memory_provider):
        """Test that double initialization is safe."""
        manager = ContextManager(provider=memory_provider)
        await manager.initialize()
        await manager.initialize()  # Should not raise

        assert manager._initialized
        await manager.close()

    @pytest.mark.asyncio
    async def test_uninitialized_access(self, memory_provider):
        """Test that accessing uninitialized manager raises error."""
        manager = ContextManager(provider=memory_provider)

        with pytest.raises(RuntimeError, match="not initialized"):
            manager.provider

    @pytest.mark.asyncio
    async def test_get_or_create_session_new(self, manager):
        """Test creating a new session."""
        ctx = await manager.get_or_create_session(
            session_id="new_session",
            user_id="user_123",
            metadata={"source": "test"},
        )

        assert isinstance(ctx, ExecutionContext)
        assert ctx.session.session_id == "new_session"
        assert ctx.session.user_id == "user_123"

    @pytest.mark.asyncio
    async def test_get_or_create_session_existing(self, manager):
        """Test getting an existing session."""
        # Create session
        await manager.get_or_create_session("existing_session")

        # Get again
        ctx = await manager.get_or_create_session("existing_session")

        assert ctx.session.session_id == "existing_session"

    @pytest.mark.asyncio
    async def test_record_interaction(self, manager):
        """Test recording a conversation turn."""
        session_id = "interaction_test"
        await manager.get_or_create_session(session_id)

        await manager.record_interaction(
            session_id=session_id,
            user_input="Hello",
            response="Hi there!",
            intent="greeting",
            entities={"sentiment": "positive"},
            confidence=0.95,
            component_id="greeter",
            duration_ms=150,
        )

        # Verify turn was recorded
        ctx = await manager.get_session_context(session_id)
        assert ctx is not None
        assert len(ctx.history.turns) == 1

        turn = ctx.history.turns[0]
        assert turn.turn_id == 1
        assert turn.user_input == "Hello"
        assert turn.assistant_response == "Hi there!"
        assert turn.detected_intent == "greeting"
        assert turn.confidence == 0.95

    @pytest.mark.asyncio
    async def test_record_multiple_interactions(self, manager):
        """Test recording multiple conversation turns."""
        session_id = "multi_interaction"
        await manager.get_or_create_session(session_id)

        for i in range(5):
            await manager.record_interaction(
                session_id=session_id,
                user_input=f"Message {i}",
                response=f"Response {i}",
            )

        ctx = await manager.get_session_context(session_id)
        assert len(ctx.history.turns) == 5
        assert ctx.history.total_turns == 5

        # Verify turn IDs are sequential
        for i, turn in enumerate(ctx.history.turns):
            assert turn.turn_id == i + 1

    @pytest.mark.asyncio
    async def test_set_and_get_variable(self, manager):
        """Test setting and getting context variables."""
        session_id = "variable_test"
        await manager.get_or_create_session(session_id)

        # Set variables
        await manager.set_variable(session_id, "string_var", "hello")
        await manager.set_variable(session_id, "number_var", 42)
        await manager.set_variable(session_id, "bool_var", True)
        await manager.set_variable(session_id, "list_var", ["a", "b", "c"])

        # Get variables
        assert await manager.get_variable(session_id, "string_var") == "hello"
        assert await manager.get_variable(session_id, "number_var") == 42.0
        assert await manager.get_variable(session_id, "bool_var") is True
        assert await manager.get_variable(session_id, "list_var") == ["a", "b", "c"]

        # Default value for missing key
        assert await manager.get_variable(session_id, "missing", "default") == "default"

    @pytest.mark.asyncio
    async def test_clear_session(self, manager):
        """Test clearing a session."""
        session_id = "clear_test"
        await manager.get_or_create_session(session_id)
        await manager.set_variable(session_id, "key", "value")

        # Clear
        result = await manager.clear_session(session_id)
        assert result is True

        # Verify cleared
        ctx = await manager.get_session_context(session_id)
        assert ctx is None

    @pytest.mark.asyncio
    async def test_with_context_basic(self, manager):
        """Test executing function with context injection."""
        session_id = "with_context_test"

        async def my_function(user_input: str, context=None):
            assert context is not None
            assert "session_id" in context
            return f"Processed: {user_input}"

        result = await manager.with_context(
            session_id=session_id,
            func=my_function,
            user_input="test input",
        )

        assert isinstance(result, ContextualResult)
        assert result.result == "Processed: test input"
        assert result.session_id == session_id
        assert result.function_name == "my_function"
        assert result.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_with_context_no_injection(self, manager):
        """Test executing without context injection."""
        session_id = "no_inject_test"

        async def my_function(user_input: str, context=None):
            assert context is None
            return user_input.upper()

        result = await manager.with_context(
            session_id=session_id,
            func=my_function,
            inject_context=False,
            user_input="hello",
        )

        assert result.result == "HELLO"

    @pytest.mark.asyncio
    async def test_with_context_record_turn(self, manager):
        """Test executing with automatic turn recording."""
        session_id = "record_turn_test"

        async def my_function(user_input: str, context=None):
            return {"response": f"Echo: {user_input}"}

        result = await manager.with_context(
            session_id=session_id,
            func=my_function,
            record_as_turn=True,
            user_input="Hello world",
        )

        assert result.turn_recorded is True

        # Verify turn was recorded
        ctx = await manager.get_session_context(session_id)
        assert len(ctx.history.turns) == 1
        assert ctx.history.turns[0].user_input == "Hello world"


# ============================================
# ContextualBAML Tests
# ============================================


class TestContextualBAML:
    """Tests for ContextualBAML wrapper."""

    @pytest.mark.asyncio
    async def test_call_basic(self, manager, mock_baml_client):
        """Test basic BAML function call."""
        contextual = ContextualBAML(manager, mock_baml_client)

        result = await contextual.call(
            session_id="baml_test",
            function_name="ExtractIntent",
            user_input="Hello!",
        )

        assert isinstance(result, ContextualResult)
        assert result.function_name == "ExtractIntent"
        assert result.result.intent == "greeting"
        assert result.result.confidence == 0.95

    @pytest.mark.asyncio
    async def test_call_with_context_injection(self, manager, mock_baml_client):
        """Test that context is injected into BAML call."""
        contextual = ContextualBAML(manager, mock_baml_client)

        # Create session with some history
        await manager.get_or_create_session("context_inject_test")
        await manager.record_interaction(
            "context_inject_test",
            user_input="Previous message",
            response="Previous response",
        )

        await contextual.call(
            session_id="context_inject_test",
            function_name="ExtractIntent",
            user_input="New message",
        )

        # Verify context was passed
        call_kwargs = mock_baml_client.ExtractIntent.call_args.kwargs
        assert "context" in call_kwargs
        assert call_kwargs["context"]["session_id"] == "context_inject_test"

    @pytest.mark.asyncio
    async def test_call_nonexistent_function(self, manager, mock_baml_client):
        """Test calling nonexistent function raises error."""
        contextual = ContextualBAML(manager, mock_baml_client)

        with pytest.raises(AttributeError, match="NonexistentFunction"):
            await contextual.call(
                session_id="test",
                function_name="NonexistentFunction",
            )

    @pytest.mark.asyncio
    async def test_call_with_turn_recording(self, manager, mock_baml_client):
        """Test that turn is recorded when requested."""
        contextual = ContextualBAML(manager, mock_baml_client)

        result = await contextual.call(
            session_id="turn_record_test",
            function_name="GenerateResponse",
            user_input="Hello!",
            record_as_turn=True,
        )

        assert result.turn_recorded is True

        # Verify turn was recorded
        ctx = await manager.get_session_context("turn_record_test")
        assert len(ctx.history.turns) == 1
        assert ctx.history.turns[0].user_input == "Hello!"

    @pytest.mark.asyncio
    async def test_extract_intent_convenience(self, manager, mock_baml_client):
        """Test extract_intent convenience method."""
        contextual = ContextualBAML(manager, mock_baml_client)

        result = await contextual.extract_intent(
            session_id="intent_test",
            user_input="How are you?",
        )

        assert result.result.intent == "greeting"
        mock_baml_client.ExtractIntent.assert_called()

    @pytest.mark.asyncio
    async def test_generate_response_convenience(self, manager, mock_baml_client):
        """Test generate_response convenience method."""
        contextual = ContextualBAML(manager, mock_baml_client)

        result = await contextual.generate_response(
            session_id="response_test",
            user_input="Tell me a joke",
        )

        assert "Response to:" in result.result.response
        mock_baml_client.GenerateResponse.assert_called()

    @pytest.mark.asyncio
    async def test_auto_record_disabled(self, manager, mock_baml_client):
        """Test that auto_record can be disabled."""
        contextual = ContextualBAML(manager, mock_baml_client, auto_record=False)

        result = await contextual.call(
            session_id="no_auto_record",
            function_name="GenerateResponse",
            user_input="Hello",
            record_as_turn=True,  # Request recording
        )

        # Turn should not be recorded because auto_record=False
        assert result.turn_recorded is False

    @pytest.mark.asyncio
    async def test_context_before_after(self, manager, mock_baml_client):
        """Test that context_before and context_after are captured."""
        contextual = ContextualBAML(manager, mock_baml_client)

        result = await contextual.call(
            session_id="context_capture_test",
            function_name="ExtractIntent",
            user_input="Test",
        )

        assert result.context_before is not None
        assert result.context_after is not None
        assert result.context_before.session.session_id == "context_capture_test"


# ============================================
# ContextualResult Tests
# ============================================


class TestContextualResult:
    """Tests for ContextualResult dataclass."""

    def test_result_creation(self):
        """Test creating a ContextualResult."""
        result = ContextualResult(
            result="test result",
            session_id="session_123",
            function_name="TestFunction",
            duration_ms=100,
        )

        assert result.result == "test result"
        assert result.session_id == "session_123"
        assert result.function_name == "TestFunction"
        assert result.duration_ms == 100
        assert result.turn_recorded is False
        assert result.variables_updated == {}

    def test_result_with_context(self):
        """Test result with context objects."""
        session = SessionContext(session_id="test")
        history = ConversationHistory(session_id="test")
        variables = ContextVariables(session_id="test")
        ctx = ExecutionContext(
            session=session,
            history=history,
            variables=variables,
        )

        result = ContextualResult(
            result="test",
            session_id="test",
            function_name="test",
            duration_ms=50,
            context_before=ctx,
            context_after=ctx,
        )

        assert result.context_before is not None
        assert result.context_after is not None


# ============================================
# Decorator Tests
# ============================================


class TestWithContextDecorator:
    """Tests for with_context decorator."""

    @pytest.mark.asyncio
    async def test_decorator_basic(self, manager):
        """Test basic decorator usage."""

        @with_context(manager)
        async def my_function(session_id: str, context=None):
            assert context is not None
            return context["session_id"]

        result = await my_function(session_id="decorator_test")
        assert result == "decorator_test"

    @pytest.mark.asyncio
    async def test_decorator_missing_session_id(self, manager):
        """Test decorator raises error without session_id."""

        @with_context(manager)
        async def my_function(context=None):
            return "result"

        with pytest.raises(ValueError, match="session_id"):
            await my_function()

    @pytest.mark.asyncio
    async def test_decorator_with_recording(self, manager):
        """Test decorator with turn recording."""

        @with_context(manager, record_as_turn=True)
        async def my_function(session_id: str, user_input: str, context=None):
            return f"Echo: {user_input}"

        result = await my_function(session_id="record_test", user_input="Hello")
        assert result == "Echo: Hello"

        # Verify turn was recorded
        ctx = await manager.get_session_context("record_test")
        assert len(ctx.history.turns) == 1

    @pytest.mark.asyncio
    async def test_decorator_preserves_function_name(self, manager):
        """Test that decorator preserves function name."""

        @with_context(manager)
        async def original_name(session_id: str, context=None):
            return "result"

        assert original_name.__name__ == "original_name"


# ============================================
# Factory Function Tests
# ============================================


class TestCreateContextManager:
    """Tests for create_context_manager factory."""

    @pytest.mark.asyncio
    async def test_create_default(self):
        """Test creating manager with defaults."""
        manager = await create_context_manager()

        assert manager._initialized is True
        assert manager.provider is not None

        await manager.close()

    @pytest.mark.asyncio
    async def test_create_with_config(self):
        """Test creating manager with custom config."""
        config = ContextConfig(
            max_history_turns=50,
            ttl_seconds=7200,
        )

        manager = await create_context_manager(config=config)
        assert manager._initialized is True

        await manager.close()

    @pytest.mark.asyncio
    async def test_create_with_provider(self, memory_provider):
        """Test creating manager with custom provider."""
        manager = await create_context_manager(provider=memory_provider)

        assert manager._initialized is True
        assert manager.provider is memory_provider

        await manager.close()


# ============================================
# Integration Tests
# ============================================


class TestIntegration:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    async def test_full_conversation_flow(self, manager, mock_baml_client):
        """Test a complete conversation flow."""
        session_id = "full_flow_test"
        contextual = ContextualBAML(manager, mock_baml_client)

        # First interaction
        result1 = await contextual.extract_intent(
            session_id=session_id,
            user_input="Hello, how are you?",
            record_turn=True,
        )
        assert result1.result.intent == "greeting"

        # Set a variable
        await manager.set_variable(session_id, "user_name", "Alice")

        # Second interaction
        result2 = await contextual.generate_response(
            session_id=session_id,
            user_input="What's my name?",
            record_turn=True,
        )
        assert result2.result.response is not None

        # Verify conversation history
        ctx = await manager.get_session_context(session_id)
        assert ctx.history.total_turns == 2
        assert ctx.variables.get("user_name") == "Alice"

    @pytest.mark.asyncio
    async def test_session_isolation(self, manager):
        """Test that sessions are properly isolated."""
        # Create two sessions
        await manager.get_or_create_session("session_1")
        await manager.get_or_create_session("session_2")

        # Set different variables
        await manager.set_variable("session_1", "key", "value_1")
        await manager.set_variable("session_2", "key", "value_2")

        # Verify isolation
        assert await manager.get_variable("session_1", "key") == "value_1"
        assert await manager.get_variable("session_2", "key") == "value_2"

    @pytest.mark.asyncio
    async def test_context_continuity(self, manager, mock_baml_client):
        """Test that context is maintained across calls."""
        session_id = "continuity_test"
        contextual = ContextualBAML(manager, mock_baml_client)

        # First call - establishes session
        result1 = await contextual.call(
            session_id=session_id,
            function_name="ExtractIntent",
            user_input="First message",
            record_as_turn=True,
        )

        # Verify first turn was recorded
        ctx_after_first = await manager.get_session_context(session_id)
        assert len(ctx_after_first.history.turns) == 1

        # Second call - should have history from first
        result2 = await contextual.call(
            session_id=session_id,
            function_name="ExtractIntent",
            user_input="Second message",
            record_as_turn=True,
        )

        # Context after second call should have both turns
        ctx = await manager.get_session_context(session_id)
        assert len(ctx.history.turns) == 2
        assert ctx.history.turns[0].user_input == "First message"
        assert ctx.history.turns[1].user_input == "Second message"
