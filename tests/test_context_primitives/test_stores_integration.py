"""
Integration tests for Context Store Implementations.

These tests require actual Redis and PostgreSQL instances.
They are marked with pytest.mark.integration and skip if infrastructure is unavailable.

Run with infrastructure:
    pytest tests/test_context_primitives/test_stores_integration.py -v

Skip integration tests:
    pytest tests/ -v --ignore=tests/test_context_primitives/test_stores_integration.py

Or use markers (if configured in pytest.ini):
    pytest -m "not integration"
"""

import pytest
import asyncio
import os
from datetime import datetime, timezone

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


# ============================================
# Redis Provider Tests
# ============================================

class TestRedisContextProvider:
    """Integration tests for RedisContextProvider."""

    @pytest.fixture
    async def redis_provider(self):
        """Create and connect a Redis provider, cleanup after test."""
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")

        try:
            from src.context_primitives.stores.redis import RedisContextProvider
            from src.context_primitives.provider import ContextConfig
        except ImportError:
            pytest.skip("Redis dependencies not installed")
            return

        config = ContextConfig(
            redis_url=redis_url,
            ttl_seconds=60,
            max_history_turns=10,
        )
        provider = RedisContextProvider(config)

        try:
            await provider.connect()
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")
            return

        yield provider

        # Cleanup
        await provider.close()

    @pytest.mark.asyncio
    async def test_session_lifecycle(self, redis_provider):
        """Test complete session lifecycle in Redis."""
        provider = redis_provider
        session_id = f"test_redis_{datetime.now(timezone.utc).timestamp()}"

        # Create session
        session = await provider.create_session(
            session_id=session_id,
            user_id="test_user",
            metadata={"env": "test"}
        )
        assert session.session_id == session_id
        assert session.user_id == "test_user"

        # Get session
        retrieved = await provider.get_session(session_id)
        assert retrieved is not None
        assert retrieved.session_id == session_id

        # Delete session
        deleted = await provider.delete_session(session_id)
        assert deleted is True

        # Verify deleted
        retrieved = await provider.get_session(session_id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_conversation_history(self, redis_provider):
        """Test conversation history in Redis."""
        from src.context_primitives.provider import ConversationTurn

        provider = redis_provider
        session_id = f"test_redis_hist_{datetime.now(timezone.utc).timestamp()}"

        # Create session
        await provider.create_session(session_id=session_id)

        # Add turns
        for i in range(5):
            turn = ConversationTurn(
                turn_id=i + 1,
                timestamp=datetime.now(timezone.utc),
                user_input=f"Question {i + 1}",
                assistant_response=f"Answer {i + 1}",
            )
            await provider.add_turn(session_id, turn)

        # Get history
        history = await provider.get_history(session_id)
        assert len(history.turns) == 5
        assert history.turns[0].turn_id == 1
        assert history.turns[-1].turn_id == 5

        # Cleanup
        await provider.delete_session(session_id)

    @pytest.mark.asyncio
    async def test_context_variables(self, redis_provider):
        """Test context variables in Redis."""
        provider = redis_provider
        session_id = f"test_redis_vars_{datetime.now(timezone.utc).timestamp()}"

        # Create session
        await provider.create_session(session_id=session_id)

        # Set variables
        await provider.set_variable(session_id, "string_var", "hello")
        await provider.set_variable(session_id, "number_var", 42)
        await provider.set_variable(session_id, "bool_var", True)
        await provider.set_variable(session_id, "list_var", ["a", "b", "c"])

        # Get variables
        variables = await provider.get_variables(session_id)
        assert variables.get("string_var") == "hello"
        assert variables.get("number_var") == 42.0
        assert variables.get("bool_var") is True
        assert variables.get("list_var") == ["a", "b", "c"]

        # Delete variable
        deleted = await provider.delete_variable(session_id, "string_var")
        assert deleted is True

        variables = await provider.get_variables(session_id)
        assert variables.get("string_var") is None

        # Cleanup
        await provider.delete_session(session_id)

    @pytest.mark.asyncio
    async def test_ttl_expiration(self, redis_provider):
        """Test TTL-based session expiration in Redis."""
        provider = redis_provider
        session_id = f"test_redis_ttl_{datetime.now(timezone.utc).timestamp()}"

        # Get remaining TTL
        await provider.create_session(session_id=session_id)

        ttl = await provider.get_session_ttl(session_id)
        assert ttl is not None
        assert ttl > 0
        assert ttl <= 60  # Our test config TTL

        # Cleanup
        await provider.delete_session(session_id)


# ============================================
# PostgreSQL Provider Tests
# ============================================

class TestPostgreSQLContextProvider:
    """Integration tests for PostgreSQLContextProvider."""

    @pytest.fixture
    async def postgres_provider(self):
        """Create and connect a PostgreSQL provider, cleanup after test."""
        postgres_url = os.environ.get(
            "POSTGRES_URL",
            "postgresql://postgres:postgres@localhost:5432/test_context"
        )

        try:
            from src.context_primitives.stores.postgres import PostgreSQLContextProvider
            from src.context_primitives.provider import ContextConfig
        except ImportError:
            pytest.skip("PostgreSQL dependencies not installed")
            return

        config = ContextConfig(
            postgres_url=postgres_url,
            ttl_seconds=3600,
            max_history_turns=20,
        )
        provider = PostgreSQLContextProvider(config)

        try:
            await provider.connect()
            await provider.create_tables()
        except Exception as e:
            pytest.skip(f"PostgreSQL not available: {e}")
            return

        yield provider

        # Cleanup
        await provider.close()

    @pytest.mark.asyncio
    async def test_session_lifecycle(self, postgres_provider):
        """Test complete session lifecycle in PostgreSQL."""
        provider = postgres_provider
        session_id = f"test_pg_{datetime.now(timezone.utc).timestamp()}"

        # Create session
        session = await provider.create_session(
            session_id=session_id,
            user_id="test_user",
            metadata={"env": "test", "version": "1.0"}
        )
        assert session.session_id == session_id

        # Get session
        retrieved = await provider.get_session(session_id)
        assert retrieved is not None
        assert retrieved.metadata.get("env") == "test"

        # Update session
        session.touch()
        await provider.update_session(session)

        # Delete session
        deleted = await provider.delete_session(session_id)
        assert deleted is True

    @pytest.mark.asyncio
    async def test_full_history_retrieval(self, postgres_provider):
        """Test full history retrieval (not windowed)."""
        from src.context_primitives.provider import ConversationTurn

        provider = postgres_provider
        session_id = f"test_pg_hist_{datetime.now(timezone.utc).timestamp()}"

        # Create session
        await provider.create_session(session_id=session_id)

        # Add many turns
        for i in range(30):
            turn = ConversationTurn(
                turn_id=i + 1,
                timestamp=datetime.now(timezone.utc),
                user_input=f"Question {i + 1}",
                assistant_response=f"Answer {i + 1}",
                detected_intent=f"intent_{i % 5}",
                confidence=0.9,
            )
            await provider.add_turn(session_id, turn)

        # Get windowed history
        history = await provider.get_history(session_id)
        assert len(history.turns) == 20  # max_history_turns

        # Get full history
        full_history = await provider.get_full_history(session_id)
        assert len(full_history) == 30

        # Cleanup
        await provider.delete_session(session_id)

    @pytest.mark.asyncio
    async def test_session_search(self, postgres_provider):
        """Test session search functionality."""
        provider = postgres_provider
        user_id = f"search_user_{datetime.now(timezone.utc).timestamp()}"

        # Create multiple sessions for same user
        session_ids = []
        for i in range(3):
            session_id = f"test_pg_search_{i}_{datetime.now(timezone.utc).timestamp()}"
            session_ids.append(session_id)
            await provider.create_session(
                session_id=session_id,
                user_id=user_id,
            )

        # Search by user_id
        sessions = await provider.search_sessions(user_id=user_id)
        assert len(sessions) >= 3

        # Cleanup
        for sid in session_ids:
            await provider.delete_session(sid)

    @pytest.mark.asyncio
    async def test_context_variables_persistence(self, postgres_provider):
        """Test variable persistence in PostgreSQL."""
        provider = postgres_provider
        session_id = f"test_pg_vars_{datetime.now(timezone.utc).timestamp()}"

        # Create session
        await provider.create_session(session_id=session_id)

        # Set complex variables
        await provider.set_variable(session_id, "user_prefs", {
            "theme": "dark",
            "language": "en-US",
            "notifications": True
        })
        await provider.set_variable(session_id, "task_history", ["task1", "task2", "task3"])

        # Retrieve and verify
        variables = await provider.get_variables(session_id)
        prefs = variables.get("user_prefs")
        assert prefs["theme"] == "dark"
        assert prefs["notifications"] is True

        tasks = variables.get("task_history")
        assert len(tasks) == 3

        # Cleanup
        await provider.delete_session(session_id)


# ============================================
# Hybrid Provider Tests
# ============================================

class TestHybridContextProvider:
    """Integration tests for HybridContextProvider."""

    @pytest.fixture
    async def hybrid_provider(self):
        """Create and connect a Hybrid provider, cleanup after test."""
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
        postgres_url = os.environ.get(
            "POSTGRES_URL",
            "postgresql://postgres:postgres@localhost:5432/test_context"
        )

        try:
            from src.context_primitives.stores.hybrid import HybridContextProvider
            from src.context_primitives.provider import ContextConfig
        except ImportError:
            pytest.skip("Hybrid provider dependencies not installed")
            return

        config = ContextConfig(
            redis_url=redis_url,
            postgres_url=postgres_url,
            ttl_seconds=60,
            max_history_turns=10,
        )
        provider = HybridContextProvider(config)

        try:
            await provider.connect()
        except Exception as e:
            pytest.skip(f"Redis or PostgreSQL not available: {e}")
            return

        yield provider

        # Cleanup
        await provider.close()

    @pytest.mark.asyncio
    async def test_dual_storage(self, hybrid_provider):
        """Test that data is written to both stores."""
        provider = hybrid_provider
        session_id = f"test_hybrid_{datetime.now(timezone.utc).timestamp()}"

        # Create session
        session = await provider.create_session(
            session_id=session_id,
            user_id="hybrid_user",
        )

        # Verify in Redis
        redis_session = await provider.redis.get_session(session_id)
        assert redis_session is not None

        # Verify in PostgreSQL
        pg_session = await provider.postgres.get_session(session_id)
        assert pg_session is not None

        # Cleanup
        await provider.delete_session(session_id)

    @pytest.mark.asyncio
    async def test_cache_miss_fallback(self, hybrid_provider):
        """Test fallback to PostgreSQL on Redis cache miss."""
        from src.context_primitives.provider import ConversationTurn

        provider = hybrid_provider
        session_id = f"test_hybrid_fallback_{datetime.now(timezone.utc).timestamp()}"

        # Create session
        await provider.create_session(session_id=session_id)

        # Add turns
        for i in range(3):
            turn = ConversationTurn(
                turn_id=i + 1,
                timestamp=datetime.now(timezone.utc),
                user_input=f"Question {i + 1}",
                assistant_response=f"Answer {i + 1}",
            )
            await provider.add_turn(session_id, turn)

        # Invalidate Redis cache
        await provider.invalidate_cache(session_id)

        # Verify Redis is empty
        redis_session = await provider.redis.get_session(session_id)
        assert redis_session is None

        # Get session (should fallback to PostgreSQL and warm cache)
        session = await provider.get_session(session_id)
        assert session is not None

        # Verify cache is now warmed
        redis_session = await provider.redis.get_session(session_id)
        assert redis_session is not None

        # Cleanup
        await provider.delete_session(session_id)

    @pytest.mark.asyncio
    async def test_sync_to_postgres(self, hybrid_provider):
        """Test explicit sync from Redis to PostgreSQL."""
        provider = hybrid_provider
        session_id = f"test_hybrid_sync_{datetime.now(timezone.utc).timestamp()}"

        # Create session
        await provider.create_session(session_id=session_id)

        # Add variable
        await provider.set_variable(session_id, "sync_test", "value")

        # Force sync
        result = await provider.sync_to_postgres(session_id)
        assert result is True

        # Verify in PostgreSQL directly
        pg_vars = await provider.postgres.get_variables(session_id)
        assert pg_vars.get("sync_test") == "value"

        # Cleanup
        await provider.delete_session(session_id)

    @pytest.mark.asyncio
    async def test_full_history_from_postgres(self, hybrid_provider):
        """Test retrieving full history from PostgreSQL via hybrid."""
        from src.context_primitives.provider import ConversationTurn

        provider = hybrid_provider
        session_id = f"test_hybrid_full_{datetime.now(timezone.utc).timestamp()}"

        # Create session
        await provider.create_session(session_id=session_id)

        # Add more turns than Redis window
        for i in range(15):
            turn = ConversationTurn(
                turn_id=i + 1,
                timestamp=datetime.now(timezone.utc),
                user_input=f"Question {i + 1}",
                assistant_response=f"Answer {i + 1}",
            )
            await provider.add_turn(session_id, turn)

        # Get full history (from PostgreSQL)
        full_history = await provider.get_full_history(session_id)
        assert len(full_history) == 15

        # Cleanup
        await provider.delete_session(session_id)


# ============================================
# Factory Integration Tests
# ============================================

class TestProviderFactory:
    """Integration tests for provider factory."""

    @pytest.mark.asyncio
    async def test_create_memory_provider(self):
        """Test creating in-memory provider via factory."""
        from src.context_primitives.stores.factory import create_memory_provider

        # create_memory_provider is synchronous
        provider = create_memory_provider()
        assert provider is not None

        # Test basic operation
        session = await provider.create_session("factory_test")
        assert session.session_id == "factory_test"

        await provider.delete_session("factory_test")

    @pytest.mark.asyncio
    async def test_create_redis_provider_via_factory(self):
        """Test creating Redis provider via factory."""
        redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")

        from src.context_primitives.stores.factory import create_provider
        from src.context_primitives.provider import ContextConfig, ContextBackend

        config = ContextConfig(
            backend=ContextBackend.REDIS,
            redis_url=redis_url,
        )

        try:
            provider = await create_provider(config)
        except Exception as e:
            pytest.skip(f"Redis not available: {e}")
            return

        assert provider is not None

        # Test basic operation
        session_id = f"factory_redis_{datetime.now(timezone.utc).timestamp()}"
        session = await provider.create_session(session_id)
        assert session.session_id == session_id

        await provider.delete_session(session_id)
        await provider.close()
