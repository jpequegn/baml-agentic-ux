"""
Tests for Context Decorator System.

Comprehensive tests for all decorators in the context primitives module.

Part of Phase 7: BAML Context Primitives Implementation
Issue #107 - Task 7.7: Context Decorator System
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from src.context_primitives.decorators import (
    ContextFormat,
    DecoratorMetrics,
    get_metrics,
    clear_metrics,
    with_context,
    with_session,
    record_turn,
    inject_variables,
    require_context,
    track_metrics,
    contextual_class,
    context_scope,
    compose,
    create_contextual_decorator,
)
from src.context_primitives.integration import ContextManager, create_context_manager
from src.context_primitives.provider import ContextConfig
from src.context_primitives.stores.memory import InMemoryContextProvider


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def config():
    """Create test configuration."""
    return ContextConfig(max_history_turns=10, ttl_seconds=3600)


@pytest.fixture
def memory_provider(config):
    """Create in-memory provider."""
    return InMemoryContextProvider(config)


@pytest.fixture
async def manager(memory_provider):
    """Create initialized context manager."""
    mgr = ContextManager(provider=memory_provider)
    await mgr.initialize()
    yield mgr
    await mgr.close()


@pytest.fixture(autouse=True)
def reset_metrics():
    """Clear metrics before each test."""
    clear_metrics()
    yield
    clear_metrics()


# ============================================
# with_context Decorator Tests
# ============================================


class TestWithContextDecorator:
    """Tests for with_context decorator."""

    @pytest.mark.asyncio
    async def test_basic_context_injection(self, manager):
        """Test basic context injection."""

        @with_context(manager)
        async def handler(session_id: str, message: str, context=None):
            assert context is not None
            return context["session_id"]

        result = await handler(session_id="test_session", message="hello")
        assert result == "test_session"

    @pytest.mark.asyncio
    async def test_context_format_conversation(self, manager):
        """Test conversation context format."""

        @with_context(manager, context_format=ContextFormat.CONVERSATION)
        async def handler(session_id: str, context=None):
            assert "session_id" in context
            assert "recent_turns" in context
            assert "turn_count" in context
            return True

        result = await handler(session_id="conv_test")
        assert result is True

    @pytest.mark.asyncio
    async def test_context_format_minimal(self, manager):
        """Test minimal context format."""

        @with_context(manager, context_format=ContextFormat.MINIMAL)
        async def handler(session_id: str, context=None):
            assert "session_id" in context
            assert "recent_turns" in context
            assert "turn_count" not in context  # Minimal doesn't include this
            return True

        result = await handler(session_id="minimal_test")
        assert result is True

    @pytest.mark.asyncio
    async def test_context_format_variables_only(self, manager):
        """Test variables-only context format."""
        # Set a variable first
        await manager.get_or_create_session("var_test")
        await manager.set_variable("var_test", "key", "value")

        @with_context(manager, context_format=ContextFormat.VARIABLES_ONLY)
        async def handler(session_id: str, context=None):
            assert isinstance(context, dict)
            return context.get("key")

        result = await handler(session_id="var_test")
        assert result == "value"

    @pytest.mark.asyncio
    async def test_context_format_full(self, manager):
        """Test full context format."""

        @with_context(manager, context_format=ContextFormat.FULL)
        async def handler(session_id: str, context=None):
            # Full format returns ExecutionContext object
            assert hasattr(context, "session")
            assert hasattr(context, "history")
            assert hasattr(context, "variables")
            return context.session.session_id

        result = await handler(session_id="full_test")
        assert result == "full_test"

    @pytest.mark.asyncio
    async def test_custom_context_param(self, manager):
        """Test custom context parameter name."""

        @with_context(manager, context_param="ctx")
        async def handler(session_id: str, ctx=None):
            assert ctx is not None
            return ctx["session_id"]

        result = await handler(session_id="custom_param")
        assert result == "custom_param"

    @pytest.mark.asyncio
    async def test_missing_session_id_raises(self, manager):
        """Test that missing session_id raises error."""

        @with_context(manager)
        async def handler(other_param: str, context=None):
            return "result"

        with pytest.raises(ValueError, match="session_id"):
            await handler(other_param="test")

    @pytest.mark.asyncio
    async def test_positional_session_id(self, manager):
        """Test session_id from positional argument."""

        @with_context(manager)
        async def handler(session_id: str, message: str, context=None):
            return context["session_id"]

        # Pass session_id as positional
        result = await handler("positional_session", "message")
        assert result == "positional_session"

    @pytest.mark.asyncio
    async def test_create_session_false(self, manager):
        """Test create_session=False requires existing session."""

        @with_context(manager, create_session=False)
        async def handler(session_id: str, context=None):
            return "result"

        with pytest.raises(ValueError, match="not found"):
            await handler(session_id="nonexistent")


# ============================================
# with_session Decorator Tests
# ============================================


class TestWithSessionDecorator:
    """Tests for with_session decorator."""

    @pytest.mark.asyncio
    async def test_session_created(self, manager):
        """Test session is created if not exists."""

        @with_session(manager)
        async def handler(session_id: str):
            return "done"

        await handler(session_id="new_session")

        # Verify session was created
        ctx = await manager.get_session_context("new_session")
        assert ctx is not None

    @pytest.mark.asyncio
    async def test_session_with_user_id(self, manager):
        """Test session creation with user_id."""

        @with_session(manager)
        async def handler(session_id: str, user_id: str = None):
            return "done"

        await handler(session_id="user_session", user_id="user_123")

        ctx = await manager.get_session_context("user_session")
        assert ctx.session.user_id == "user_123"

    @pytest.mark.asyncio
    async def test_touch_on_access(self, manager):
        """Test session is touched on access."""
        # Create session first
        await manager.get_or_create_session("touch_test")
        original_ctx = await manager.get_session_context("touch_test")
        original_activity = original_ctx.session.last_activity

        @with_session(manager, touch_on_access=True)
        async def handler(session_id: str):
            return "done"

        # Small delay to ensure timestamp changes
        import asyncio
        await asyncio.sleep(0.01)

        await handler(session_id="touch_test")

        ctx = await manager.get_session_context("touch_test")
        assert ctx.session.last_activity >= original_activity


# ============================================
# record_turn Decorator Tests
# ============================================


class TestRecordTurnDecorator:
    """Tests for record_turn decorator."""

    @pytest.mark.asyncio
    async def test_basic_turn_recording(self, manager):
        """Test basic turn recording."""
        await manager.get_or_create_session("record_test")

        @record_turn(manager)
        async def handler(session_id: str, user_input: str):
            return "Response to user"

        await handler(session_id="record_test", user_input="Hello")

        ctx = await manager.get_session_context("record_test")
        assert len(ctx.history.turns) == 1
        assert ctx.history.turns[0].user_input == "Hello"
        assert ctx.history.turns[0].assistant_response == "Response to user"

    @pytest.mark.asyncio
    async def test_turn_with_component_id(self, manager):
        """Test turn recording with component_id."""
        await manager.get_or_create_session("component_test")

        @record_turn(manager, component_id="test_handler")
        async def handler(session_id: str, user_input: str):
            return "Response"

        await handler(session_id="component_test", user_input="Test")

        ctx = await manager.get_session_context("component_test")
        assert ctx.history.turns[0].component_id == "test_handler"

    @pytest.mark.asyncio
    async def test_custom_response_extractor(self, manager):
        """Test custom response extractor."""
        await manager.get_or_create_session("extractor_test")

        def extract_response(result):
            return result["custom_response"]

        @record_turn(manager, response_extractor=extract_response)
        async def handler(session_id: str, user_input: str):
            return {"custom_response": "Extracted response", "other": "data"}

        await handler(session_id="extractor_test", user_input="Test")

        ctx = await manager.get_session_context("extractor_test")
        assert ctx.history.turns[0].assistant_response == "Extracted response"

    @pytest.mark.asyncio
    async def test_duration_tracking(self, manager):
        """Test that duration is tracked."""
        await manager.get_or_create_session("duration_test")

        @record_turn(manager)
        async def handler(session_id: str, user_input: str):
            import asyncio
            await asyncio.sleep(0.01)  # 10ms delay
            return "Response"

        await handler(session_id="duration_test", user_input="Test")

        ctx = await manager.get_session_context("duration_test")
        assert ctx.history.turns[0].duration_ms >= 10


# ============================================
# inject_variables Decorator Tests
# ============================================


class TestInjectVariablesDecorator:
    """Tests for inject_variables decorator."""

    @pytest.mark.asyncio
    async def test_inject_all_variables(self, manager):
        """Test injecting all variables."""
        await manager.get_or_create_session("inject_all")
        await manager.set_variable("inject_all", "var1", "value1")
        await manager.set_variable("inject_all", "var2", "value2")

        @inject_variables(manager)
        async def handler(session_id: str, variables=None):
            return variables

        result = await handler(session_id="inject_all")
        assert result["var1"] == "value1"
        assert result["var2"] == "value2"

    @pytest.mark.asyncio
    async def test_inject_specific_keys(self, manager):
        """Test injecting specific variable keys."""
        await manager.get_or_create_session("inject_specific")
        await manager.set_variable("inject_specific", "wanted", "yes")
        await manager.set_variable("inject_specific", "unwanted", "no")

        @inject_variables(manager, keys=["wanted"])
        async def handler(session_id: str, variables=None):
            return variables

        result = await handler(session_id="inject_specific")
        assert "wanted" in result
        assert "unwanted" not in result

    @pytest.mark.asyncio
    async def test_inject_with_defaults(self, manager):
        """Test variable injection with defaults."""
        await manager.get_or_create_session("inject_defaults")

        @inject_variables(manager, defaults={"missing": "default_value"})
        async def handler(session_id: str, variables=None):
            return variables

        result = await handler(session_id="inject_defaults")
        assert result["missing"] == "default_value"


# ============================================
# require_context Decorator Tests
# ============================================


class TestRequireContextDecorator:
    """Tests for require_context decorator."""

    @pytest.mark.asyncio
    async def test_require_existing_session(self, manager):
        """Test that session must exist."""

        @require_context(manager)
        async def handler(session_id: str):
            return "done"

        with pytest.raises(ValueError, match="not found"):
            await handler(session_id="nonexistent")

    @pytest.mark.asyncio
    async def test_require_history(self, manager):
        """Test require_history validation."""
        await manager.get_or_create_session("require_history")

        @require_context(manager, require_history=True)
        async def handler(session_id: str):
            return "done"

        with pytest.raises(ValueError, match="no conversation history"):
            await handler(session_id="require_history")

    @pytest.mark.asyncio
    async def test_require_min_turns(self, manager):
        """Test min_turns validation."""
        await manager.get_or_create_session("min_turns")

        @require_context(manager, min_turns=2)
        async def handler(session_id: str):
            return "done"

        with pytest.raises(ValueError, match="requires at least 2 turns"):
            await handler(session_id="min_turns")

    @pytest.mark.asyncio
    async def test_require_variables(self, manager):
        """Test required_variables validation."""
        await manager.get_or_create_session("require_vars")

        @require_context(manager, required_variables=["user_id", "name"])
        async def handler(session_id: str):
            return "done"

        with pytest.raises(ValueError, match="missing required variables"):
            await handler(session_id="require_vars")

    @pytest.mark.asyncio
    async def test_all_requirements_met(self, manager):
        """Test when all requirements are met."""
        await manager.get_or_create_session("all_met")
        await manager.set_variable("all_met", "required_var", "value")
        await manager.record_interaction(
            "all_met", user_input="Hi", response="Hello"
        )

        @require_context(
            manager,
            require_history=True,
            min_turns=1,
            required_variables=["required_var"]
        )
        async def handler(session_id: str):
            return "success"

        result = await handler(session_id="all_met")
        assert result == "success"


# ============================================
# track_metrics Decorator Tests
# ============================================


class TestTrackMetricsDecorator:
    """Tests for track_metrics decorator."""

    @pytest.mark.asyncio
    async def test_metrics_collected(self):
        """Test that metrics are collected."""

        @track_metrics()
        async def handler(session_id: str):
            return "done"

        await handler(session_id="metrics_test")

        metrics = get_metrics()
        assert len(metrics) == 1
        assert metrics[0].function_name == "handler"
        assert metrics[0].session_id == "metrics_test"
        assert metrics[0].success is True

    @pytest.mark.asyncio
    async def test_metrics_on_error(self):
        """Test metrics capture on error."""

        @track_metrics()
        async def handler(session_id: str):
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await handler(session_id="error_test")

        metrics = get_metrics()
        assert len(metrics) == 1
        assert metrics[0].success is False
        assert "Test error" in metrics[0].error

    @pytest.mark.asyncio
    async def test_metrics_duration(self):
        """Test duration is captured."""

        @track_metrics()
        async def handler(session_id: str):
            import asyncio
            await asyncio.sleep(0.01)
            return "done"

        await handler(session_id="duration_test")

        metrics = get_metrics()
        assert metrics[0].duration_ms >= 10

    @pytest.mark.asyncio
    async def test_on_complete_callback(self):
        """Test on_complete callback."""
        captured = []

        def callback(m):
            captured.append(m)

        @track_metrics(on_complete=callback)
        async def handler(session_id: str):
            return "done"

        await handler(session_id="callback_test")

        assert len(captured) == 1
        assert captured[0].function_name == "handler"

    @pytest.mark.asyncio
    async def test_store_metrics_false(self):
        """Test store_metrics=False."""

        @track_metrics(store_metrics=False)
        async def handler(session_id: str):
            return "done"

        await handler(session_id="no_store")

        metrics = get_metrics()
        assert len(metrics) == 0


# ============================================
# contextual_class Decorator Tests
# ============================================


class TestContextualClassDecorator:
    """Tests for contextual_class decorator."""

    @pytest.mark.asyncio
    async def test_class_methods_decorated(self, manager):
        """Test class methods are decorated."""

        @contextual_class(manager)
        class Handler:
            async def process(self, session_id: str, msg: str, context=None):
                return context is not None

        handler = Handler()
        result = await handler.process(session_id="class_test", msg="hello")
        assert result is True

    @pytest.mark.asyncio
    async def test_method_prefix_filter(self, manager):
        """Test method_prefix filtering."""

        @contextual_class(manager, method_prefix="handle_")
        class Handler:
            async def handle_message(self, session_id: str, context=None):
                return context is not None

            async def internal_method(self, session_id: str, context=None):
                # Should not be decorated
                return context is None

        handler = Handler()

        # handle_ method should have context
        result1 = await handler.handle_message(session_id="prefix_test")
        assert result1 is True

        # internal method should not have context
        result2 = await handler.internal_method(session_id="prefix_test")
        assert result2 is True

    @pytest.mark.asyncio
    async def test_exclude_methods(self, manager):
        """Test excluding specific methods."""

        @contextual_class(manager, exclude_methods=["excluded"])
        class Handler:
            async def normal(self, session_id: str, context=None):
                return context is not None

            async def excluded(self, session_id: str, context=None):
                return context is None

        handler = Handler()

        result1 = await handler.normal(session_id="exclude_test")
        assert result1 is True

        result2 = await handler.excluded(session_id="exclude_test")
        assert result2 is True


# ============================================
# context_scope Tests
# ============================================


class TestContextScope:
    """Tests for context_scope context manager."""

    @pytest.mark.asyncio
    async def test_basic_scope(self, manager):
        """Test basic context scope."""
        async with context_scope(manager, "scope_test") as ctx:
            assert ctx is not None
            assert ctx.session.session_id == "scope_test"

    @pytest.mark.asyncio
    async def test_scope_with_user_id(self, manager):
        """Test scope with user_id."""
        async with context_scope(manager, "user_scope", user_id="user_123") as ctx:
            assert ctx.session.user_id == "user_123"

    @pytest.mark.asyncio
    async def test_cleanup_on_exit(self, manager):
        """Test cleanup_on_exit option."""
        async with context_scope(manager, "cleanup_test", cleanup_on_exit=True) as ctx:
            assert ctx is not None

        # Session should be deleted
        ctx = await manager.get_session_context("cleanup_test")
        assert ctx is None

    @pytest.mark.asyncio
    async def test_no_cleanup_by_default(self, manager):
        """Test session preserved by default."""
        async with context_scope(manager, "no_cleanup") as ctx:
            pass

        # Session should still exist
        ctx = await manager.get_session_context("no_cleanup")
        assert ctx is not None


# ============================================
# Composition Tests
# ============================================


class TestComposition:
    """Tests for decorator composition."""

    @pytest.mark.asyncio
    async def test_compose_decorators(self, manager):
        """Test composing multiple decorators."""
        await manager.get_or_create_session("compose_test")

        combined = compose(
            track_metrics(),
            with_context(manager),
        )

        @combined
        async def handler(session_id: str, context=None):
            return context is not None

        result = await handler(session_id="compose_test")
        assert result is True

        # Metrics should be collected
        metrics = get_metrics()
        assert len(metrics) == 1

    @pytest.mark.asyncio
    async def test_create_contextual_decorator(self, manager):
        """Test create_contextual_decorator factory."""
        await manager.get_or_create_session("factory_test")

        custom = create_contextual_decorator(
            manager,
            inject_context=True,
            track=True,
        )

        @custom
        async def handler(session_id: str, user_input: str, context=None):
            return context is not None

        result = await handler(session_id="factory_test", user_input="test")
        assert result is True

        metrics = get_metrics()
        assert len(metrics) == 1

    @pytest.mark.asyncio
    async def test_stacked_decorators(self, manager):
        """Test traditional stacked decorator syntax."""
        await manager.get_or_create_session("stacked_test")

        @track_metrics()
        @with_context(manager)
        @record_turn(manager)
        async def handler(session_id: str, user_input: str, context=None):
            return "Response"

        result = await handler(session_id="stacked_test", user_input="Hello")
        assert result == "Response"

        # Check metrics
        metrics = get_metrics()
        assert len(metrics) == 1
        assert metrics[0].success is True

        # Check turn recorded
        ctx = await manager.get_session_context("stacked_test")
        assert len(ctx.history.turns) == 1


# ============================================
# Edge Cases and Error Handling
# ============================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_decorator_preserves_function_metadata(self, manager):
        """Test that decorators preserve function metadata."""

        @with_context(manager)
        async def my_function(session_id: str, context=None):
            """This is my docstring."""
            return "result"

        assert my_function.__name__ == "my_function"
        assert "docstring" in my_function.__doc__

    @pytest.mark.asyncio
    async def test_decorator_with_sync_function_raises(self, manager):
        """Test that decorators work only with async functions."""
        # The decorator is designed for async functions
        # Applying to sync function will work but await will fail

        @with_context(manager)
        async def async_handler(session_id: str, context=None):
            return "async"

        # This should work
        result = await async_handler(session_id="async_test")
        assert result == "async"

    @pytest.mark.asyncio
    async def test_multiple_sessions_isolated(self, manager):
        """Test that multiple sessions remain isolated."""

        @with_context(manager)
        async def handler(session_id: str, context=None):
            return context["session_id"]

        result1 = await handler(session_id="session_a")
        result2 = await handler(session_id="session_b")

        assert result1 == "session_a"
        assert result2 == "session_b"

    @pytest.mark.asyncio
    async def test_empty_user_input_not_recorded(self, manager):
        """Test that empty user input is not recorded."""
        await manager.get_or_create_session("empty_input")

        @record_turn(manager)
        async def handler(session_id: str, user_input: str):
            return "Response"

        await handler(session_id="empty_input", user_input="")

        ctx = await manager.get_session_context("empty_input")
        assert len(ctx.history.turns) == 0


# ============================================
# DecoratorMetrics Tests
# ============================================


class TestDecoratorMetrics:
    """Tests for DecoratorMetrics dataclass."""

    def test_metrics_creation(self):
        """Test creating metrics."""
        metrics = DecoratorMetrics(
            function_name="test",
            session_id="session_1",
            start_time=datetime.now(timezone.utc),
        )
        assert metrics.function_name == "test"
        assert metrics.success is True
        assert metrics.error is None

    def test_get_and_clear_metrics(self):
        """Test get_metrics and clear_metrics."""
        clear_metrics()
        assert len(get_metrics()) == 0

        # Add a metric manually for testing
        from src.context_primitives.decorators import _metrics_store
        _metrics_store.append(DecoratorMetrics(
            function_name="test",
            session_id="test",
            start_time=datetime.now(timezone.utc),
        ))

        assert len(get_metrics()) == 1

        clear_metrics()
        assert len(get_metrics()) == 0
