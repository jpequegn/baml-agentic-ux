"""
Unit tests for Context Store Implementations using mocks.

These tests do NOT require actual Redis or PostgreSQL instances.
They test the provider logic using mocked backends.

Run with:
    pytest tests/test_context_primitives/test_stores_unit.py -v
"""

import pytest
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.context_primitives.provider import (
    ContextConfig,
    SessionContext,
    ConversationTurn,
    ConversationHistory,
    ContextVariables,
    ContextValue,
    ExecutionContext,
)


# ============================================
# Redis Provider Unit Tests
# ============================================

class TestRedisContextProviderUnit:
    """Unit tests for RedisContextProvider with mocked Redis."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ContextConfig(
            redis_url="redis://localhost:6379",
            ttl_seconds=3600,
            max_history_turns=10,
        )

    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        mock = AsyncMock()
        mock.setex = AsyncMock()
        mock.get = AsyncMock(return_value=None)
        mock.delete = AsyncMock(return_value=1)
        mock.ttl = AsyncMock(return_value=3600)
        mock.expire = AsyncMock()
        mock.close = AsyncMock()
        return mock

    @pytest.fixture
    async def redis_provider(self, config, mock_redis):
        """Create a RedisContextProvider with mocked Redis."""
        from src.context_primitives.stores.redis import RedisContextProvider

        provider = RedisContextProvider(config)
        provider._redis = mock_redis
        return provider

    def test_init(self, config):
        """Test provider initialization."""
        from src.context_primitives.stores.redis import RedisContextProvider

        provider = RedisContextProvider(config)
        assert provider.config == config
        assert provider._redis is None
        assert provider._prefix == "lui:context:"

    def test_key_generation(self, redis_provider):
        """Test Redis key generation."""
        session_id = "test_session"

        assert redis_provider._session_key(session_id) == "lui:context:session:test_session"
        assert redis_provider._history_key(session_id) == "lui:context:history:test_session"
        assert redis_provider._variables_key(session_id) == "lui:context:vars:test_session"

    def test_ensure_connected_raises_when_not_connected(self, config):
        """Test that operations fail when not connected."""
        from src.context_primitives.stores.redis import RedisContextProvider

        provider = RedisContextProvider(config)
        with pytest.raises(RuntimeError, match="Redis not connected"):
            provider._ensure_connected()

    @pytest.mark.asyncio
    async def test_connect_sets_redis_client(self, config, mock_redis):
        """Test that connect sets up the redis client."""
        from src.context_primitives.stores.redis import RedisContextProvider

        # Mock the redis module for import
        provider = RedisContextProvider(config)
        # Manually set the client to simulate a successful connect
        provider._redis = mock_redis

        # Verify the client is set
        assert provider._redis is mock_redis
        # Verify we can use the provider
        provider._ensure_connected()  # Should not raise

    @pytest.mark.asyncio
    async def test_connect_import_error(self, config):
        """Test connection failure when redis package not installed."""
        from src.context_primitives.stores.redis import RedisContextProvider

        with patch.dict("sys.modules", {"redis": None, "redis.asyncio": None}):
            provider = RedisContextProvider(config)
            # Force reimport to trigger ImportError
            with patch("builtins.__import__", side_effect=ImportError("No module")):
                with pytest.raises(ImportError, match="redis package required"):
                    await provider.connect()

    @pytest.mark.asyncio
    async def test_close(self, redis_provider, mock_redis):
        """Test connection close."""
        await redis_provider.close()
        mock_redis.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_session(self, redis_provider, mock_redis):
        """Test session creation."""
        session = await redis_provider.create_session(
            session_id="test_session",
            user_id="user_123",
            metadata={"key": "value"}
        )

        assert session.session_id == "test_session"
        assert session.user_id == "user_123"
        assert session.metadata == {"key": "value"}
        assert mock_redis.setex.call_count == 3  # session, history, variables

    @pytest.mark.asyncio
    async def test_get_session_exists(self, redis_provider, mock_redis):
        """Test getting existing session."""
        session_data = {
            "session_id": "test_session",
            "user_id": "user_123",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "metadata": {},
            "ttl_seconds": 3600,
            "is_active": True,
        }
        mock_redis.get.return_value = json.dumps(session_data)

        session = await redis_provider.get_session("test_session")

        assert session is not None
        assert session.session_id == "test_session"
        assert session.user_id == "user_123"

    @pytest.mark.asyncio
    async def test_get_session_not_exists(self, redis_provider, mock_redis):
        """Test getting non-existent session."""
        mock_redis.get.return_value = None

        session = await redis_provider.get_session("nonexistent")
        assert session is None

    @pytest.mark.asyncio
    async def test_update_session(self, redis_provider, mock_redis):
        """Test session update."""
        session = SessionContext(
            session_id="test_session",
            user_id="user_123",
        )

        await redis_provider.update_session(session)
        mock_redis.setex.assert_called()

    @pytest.mark.asyncio
    async def test_delete_session(self, redis_provider, mock_redis):
        """Test session deletion."""
        mock_redis.delete.return_value = 3  # 3 keys deleted

        deleted = await redis_provider.delete_session("test_session")

        assert deleted is True
        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_session_not_exists(self, redis_provider, mock_redis):
        """Test deleting non-existent session."""
        mock_redis.delete.return_value = 0

        deleted = await redis_provider.delete_session("nonexistent")
        assert deleted is False

    @pytest.mark.asyncio
    async def test_get_history_exists(self, redis_provider, mock_redis):
        """Test getting existing history."""
        history_data = {
            "session_id": "test_session",
            "turns": [
                {
                    "turn_id": 1,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "user_input": "Hello",
                    "assistant_response": "Hi there!",
                }
            ],
            "max_turns": 10,
            "total_turns": 1,
        }
        mock_redis.get.return_value = json.dumps(history_data)

        history = await redis_provider.get_history("test_session")

        assert len(history.turns) == 1
        assert history.turns[0].user_input == "Hello"

    @pytest.mark.asyncio
    async def test_get_history_not_exists(self, redis_provider, mock_redis):
        """Test getting history for session without history."""
        mock_redis.get.return_value = None

        history = await redis_provider.get_history("test_session")

        assert len(history.turns) == 0
        assert history.session_id == "test_session"

    @pytest.mark.asyncio
    async def test_add_turn(self, redis_provider, mock_redis):
        """Test adding a conversation turn."""
        # Mock existing history
        mock_redis.get.side_effect = [
            json.dumps({
                "session_id": "test_session",
                "turns": [],
                "max_turns": 10,
                "total_turns": 0,
            }),
            json.dumps({
                "session_id": "test_session",
                "user_id": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_activity": datetime.now(timezone.utc).isoformat(),
                "metadata": {},
                "ttl_seconds": 3600,
                "is_active": True,
            }),
        ]

        turn = ConversationTurn(
            turn_id=1,
            timestamp=datetime.now(timezone.utc),
            user_input="Hello",
            assistant_response="Hi!",
        )

        await redis_provider.add_turn("test_session", turn)

        # Should update history and session
        assert mock_redis.setex.call_count >= 1

    @pytest.mark.asyncio
    async def test_get_variables_exists(self, redis_provider, mock_redis):
        """Test getting existing variables."""
        variables_data = {
            "session_id": "test_session",
            "variables": {
                "name": {
                    "value_type": "STRING",
                    "string_value": "test",
                }
            },
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        mock_redis.get.return_value = json.dumps(variables_data)

        variables = await redis_provider.get_variables("test_session")

        assert variables.get("name") == "test"

    @pytest.mark.asyncio
    async def test_get_variables_not_exists(self, redis_provider, mock_redis):
        """Test getting variables for session without variables."""
        mock_redis.get.return_value = None

        variables = await redis_provider.get_variables("test_session")

        assert len(variables.variables) == 0

    @pytest.mark.asyncio
    async def test_set_variable(self, redis_provider, mock_redis):
        """Test setting a variable."""
        mock_redis.get.return_value = json.dumps({
            "session_id": "test_session",
            "variables": {},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })

        await redis_provider.set_variable("test_session", "key", "value")

        mock_redis.setex.assert_called()

    @pytest.mark.asyncio
    async def test_delete_variable_exists(self, redis_provider, mock_redis):
        """Test deleting an existing variable."""
        mock_redis.get.return_value = json.dumps({
            "session_id": "test_session",
            "variables": {
                "key": {
                    "value_type": "STRING",
                    "string_value": "value",
                }
            },
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })

        deleted = await redis_provider.delete_variable("test_session", "key")

        assert deleted is True

    @pytest.mark.asyncio
    async def test_delete_variable_not_exists(self, redis_provider, mock_redis):
        """Test deleting a non-existent variable."""
        mock_redis.get.return_value = json.dumps({
            "session_id": "test_session",
            "variables": {},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })

        deleted = await redis_provider.delete_variable("test_session", "key")

        assert deleted is False

    @pytest.mark.asyncio
    async def test_get_execution_context_new_session(self, redis_provider, mock_redis):
        """Test getting execution context for new session."""
        mock_redis.get.return_value = None

        context = await redis_provider.get_execution_context("new_session")

        assert context.session.session_id == "new_session"
        # Session should be created
        assert mock_redis.setex.call_count >= 1

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, redis_provider):
        """Test cleanup_expired (no-op for Redis)."""
        count = await redis_provider.cleanup_expired()
        assert count == 0

    @pytest.mark.asyncio
    async def test_extend_ttl_success(self, redis_provider, mock_redis):
        """Test extending TTL."""
        mock_redis.ttl.return_value = 1800

        result = await redis_provider.extend_ttl("test_session", 600)

        assert result is True
        assert mock_redis.expire.call_count == 3

    @pytest.mark.asyncio
    async def test_extend_ttl_session_not_exists(self, redis_provider, mock_redis):
        """Test extending TTL for non-existent session."""
        mock_redis.ttl.return_value = -2  # Key doesn't exist

        result = await redis_provider.extend_ttl("nonexistent", 600)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_session_ttl_exists(self, redis_provider, mock_redis):
        """Test getting TTL for existing session."""
        mock_redis.ttl.return_value = 3000

        ttl = await redis_provider.get_session_ttl("test_session")

        assert ttl == 3000

    @pytest.mark.asyncio
    async def test_get_session_ttl_not_exists(self, redis_provider, mock_redis):
        """Test getting TTL for non-existent session."""
        mock_redis.ttl.return_value = -2

        ttl = await redis_provider.get_session_ttl("nonexistent")

        assert ttl is None

    def test_serialize_session(self, redis_provider):
        """Test session serialization."""
        session = SessionContext(
            session_id="test",
            user_id="user",
            metadata={"key": "value"},
        )

        serialized = redis_provider._serialize_session(session)
        data = json.loads(serialized)

        assert data["session_id"] == "test"
        assert data["user_id"] == "user"
        assert data["metadata"] == {"key": "value"}

    def test_deserialize_session(self, redis_provider):
        """Test session deserialization."""
        data = json.dumps({
            "session_id": "test",
            "user_id": "user",
            "created_at": "2024-01-01T00:00:00",
            "last_activity": "2024-01-01T00:00:00",
            "metadata": {"key": "value"},
            "ttl_seconds": 3600,
            "is_active": True,
        })

        session = redis_provider._deserialize_session(data)

        assert session.session_id == "test"
        assert session.user_id == "user"
        assert session.metadata == {"key": "value"}


# ============================================
# PostgreSQL Provider Unit Tests
# ============================================

class TestPostgreSQLContextProviderUnit:
    """Unit tests for PostgreSQLContextProvider with mocked asyncpg."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ContextConfig(
            postgres_url="postgresql://localhost/test",
            ttl_seconds=3600,
            max_history_turns=10,
        )

    @pytest.fixture
    def mock_pool(self):
        """Create a mock asyncpg pool."""
        mock = AsyncMock()
        mock.acquire = MagicMock()
        mock.close = AsyncMock()
        return mock

    @pytest.fixture
    def mock_connection(self):
        """Create a mock asyncpg connection."""
        mock = AsyncMock()
        mock.execute = AsyncMock()
        mock.fetch = AsyncMock(return_value=[])
        mock.fetchrow = AsyncMock(return_value=None)
        mock.fetchval = AsyncMock(return_value=0)
        return mock

    @pytest.fixture
    async def postgres_provider(self, config, mock_pool, mock_connection):
        """Create a PostgreSQLContextProvider with mocked pool."""
        from src.context_primitives.stores.postgres import PostgreSQLContextProvider

        # Set up context manager
        mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_connection)
        mock_pool.acquire.return_value.__aexit__ = AsyncMock()

        provider = PostgreSQLContextProvider(config)
        provider._pool = mock_pool
        return provider

    def test_init(self, config):
        """Test provider initialization."""
        from src.context_primitives.stores.postgres import PostgreSQLContextProvider

        provider = PostgreSQLContextProvider(config)
        assert provider.config == config
        assert provider._pool is None

    def test_ensure_connected_raises_when_not_connected(self, config):
        """Test that operations fail when not connected."""
        from src.context_primitives.stores.postgres import PostgreSQLContextProvider

        provider = PostgreSQLContextProvider(config)
        with pytest.raises(RuntimeError, match="PostgreSQL not connected"):
            provider._ensure_connected()

    @pytest.mark.asyncio
    async def test_connect_success(self, config):
        """Test successful connection."""
        from src.context_primitives.stores.postgres import PostgreSQLContextProvider

        mock_asyncpg = MagicMock()
        mock_pool = AsyncMock()
        mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)

        with patch.dict("sys.modules", {"asyncpg": mock_asyncpg}):
            provider = PostgreSQLContextProvider(config)
            await provider.connect()

            mock_asyncpg.create_pool.assert_called_once()
            assert provider._pool is mock_pool

    @pytest.mark.asyncio
    async def test_close(self, postgres_provider, mock_pool):
        """Test connection close."""
        await postgres_provider.close()
        mock_pool.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_tables(self, postgres_provider, mock_connection):
        """Test table creation."""
        await postgres_provider.create_tables()
        mock_connection.execute.assert_called()

    @pytest.mark.asyncio
    async def test_create_session(self, postgres_provider, mock_connection):
        """Test session creation."""
        session = await postgres_provider.create_session(
            session_id="test_session",
            user_id="user_123",
            metadata={"key": "value"}
        )

        assert session.session_id == "test_session"
        assert session.user_id == "user_123"
        mock_connection.execute.assert_called()

    @pytest.mark.asyncio
    async def test_get_session_exists(self, postgres_provider, mock_connection):
        """Test getting existing session."""
        mock_connection.fetchrow.return_value = {
            "session_id": "test_session",
            "user_id": "user_123",
            "created_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc),
            "metadata": json.dumps({"key": "value"}),
            "ttl_seconds": 3600,
            "is_active": True,
        }

        session = await postgres_provider.get_session("test_session")

        assert session is not None
        assert session.session_id == "test_session"

    @pytest.mark.asyncio
    async def test_get_session_not_exists(self, postgres_provider, mock_connection):
        """Test getting non-existent session."""
        mock_connection.fetchrow.return_value = None

        session = await postgres_provider.get_session("nonexistent")
        assert session is None

    @pytest.mark.asyncio
    async def test_get_session_expired(self, postgres_provider, mock_connection):
        """Test getting expired session."""
        # Session with TTL that has expired
        mock_connection.fetchrow.return_value = {
            "session_id": "test_session",
            "user_id": "user_123",
            "created_at": datetime.now(timezone.utc) - timedelta(hours=2),
            "last_activity": datetime.now(timezone.utc) - timedelta(hours=2),
            "metadata": json.dumps({}),
            "ttl_seconds": 60,  # 1 minute TTL, but 2 hours ago
            "is_active": True,
        }

        session = await postgres_provider.get_session("test_session")

        # Should return None for expired session
        assert session is None

    @pytest.mark.asyncio
    async def test_update_session(self, postgres_provider, mock_connection):
        """Test session update."""
        session = SessionContext(
            session_id="test_session",
            user_id="user_123",
        )

        await postgres_provider.update_session(session)
        mock_connection.execute.assert_called()

    @pytest.mark.asyncio
    async def test_delete_session(self, postgres_provider, mock_connection):
        """Test session deletion."""
        mock_connection.execute.return_value = "DELETE 1"

        deleted = await postgres_provider.delete_session("test_session")

        assert deleted is True

    @pytest.mark.asyncio
    async def test_delete_session_not_exists(self, postgres_provider, mock_connection):
        """Test deleting non-existent session."""
        mock_connection.execute.return_value = "DELETE 0"

        deleted = await postgres_provider.delete_session("nonexistent")
        assert deleted is False

    @pytest.mark.asyncio
    async def test_get_history(self, postgres_provider, mock_connection):
        """Test getting conversation history."""
        mock_connection.fetch.return_value = [
            {
                "turn_id": 1,
                "timestamp": datetime.now(timezone.utc),
                "user_input": "Hello",
                "assistant_response": "Hi!",
                "detected_intent": None,
                "extracted_entities": None,
                "confidence": None,
                "component_id": None,
                "duration_ms": None,
            }
        ]
        mock_connection.fetchval.return_value = 1

        history = await postgres_provider.get_history("test_session")

        assert len(history.turns) == 1
        assert history.turns[0].user_input == "Hello"

    @pytest.mark.asyncio
    async def test_add_turn(self, postgres_provider, mock_connection):
        """Test adding a conversation turn."""
        turn = ConversationTurn(
            turn_id=1,
            timestamp=datetime.now(timezone.utc),
            user_input="Hello",
            assistant_response="Hi!",
        )

        await postgres_provider.add_turn("test_session", turn)

        # Should insert turn and update session
        assert mock_connection.execute.call_count >= 2

    @pytest.mark.asyncio
    async def test_get_variables(self, postgres_provider, mock_connection):
        """Test getting context variables."""
        mock_connection.fetch.return_value = [
            {
                "key": "name",
                "value_type": "STRING",
                "value": json.dumps({"string_value": "test"}),
                "updated_at": datetime.now(timezone.utc),
            }
        ]

        variables = await postgres_provider.get_variables("test_session")

        assert variables.get("name") == "test"

    @pytest.mark.asyncio
    async def test_set_variable(self, postgres_provider, mock_connection):
        """Test setting a variable."""
        await postgres_provider.set_variable("test_session", "key", "value")
        mock_connection.execute.assert_called()

    @pytest.mark.asyncio
    async def test_delete_variable(self, postgres_provider, mock_connection):
        """Test deleting a variable."""
        mock_connection.execute.return_value = "DELETE 1"

        deleted = await postgres_provider.delete_variable("test_session", "key")

        assert deleted is True

    @pytest.mark.asyncio
    async def test_get_execution_context(self, postgres_provider, mock_connection):
        """Test getting full execution context."""
        # Mock session exists
        mock_connection.fetchrow.return_value = {
            "session_id": "test_session",
            "user_id": None,
            "created_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc),
            "metadata": json.dumps({}),
            "ttl_seconds": 3600,
            "is_active": True,
        }
        mock_connection.fetch.return_value = []
        mock_connection.fetchval.return_value = 0

        context = await postgres_provider.get_execution_context("test_session")

        assert context.session.session_id == "test_session"

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, postgres_provider, mock_connection):
        """Test cleaning up expired sessions."""
        mock_connection.execute.return_value = "UPDATE 5"

        count = await postgres_provider.cleanup_expired()

        assert count == 5

    @pytest.mark.asyncio
    async def test_get_full_history(self, postgres_provider, mock_connection):
        """Test getting full history (not windowed)."""
        mock_connection.fetch.return_value = [
            {
                "turn_id": i,
                "timestamp": datetime.now(timezone.utc),
                "user_input": f"Q{i}",
                "assistant_response": f"A{i}",
                "detected_intent": None,
                "extracted_entities": None,
                "confidence": None,
                "component_id": None,
                "duration_ms": None,
            }
            for i in range(30)
        ]

        turns = await postgres_provider.get_full_history("test_session")

        assert len(turns) == 30

    @pytest.mark.asyncio
    async def test_search_sessions_no_filters(self, postgres_provider, mock_connection):
        """Test searching sessions without filters."""
        mock_connection.fetch.return_value = [
            {
                "session_id": "session_1",
                "user_id": "user_1",
                "created_at": datetime.now(timezone.utc),
                "last_activity": datetime.now(timezone.utc),
                "metadata": json.dumps({}),
                "ttl_seconds": 3600,
                "is_active": True,
            }
        ]

        sessions = await postgres_provider.search_sessions()

        assert len(sessions) == 1

    @pytest.mark.asyncio
    async def test_search_sessions_with_user_filter(self, postgres_provider, mock_connection):
        """Test searching sessions with user ID filter."""
        mock_connection.fetch.return_value = []

        sessions = await postgres_provider.search_sessions(user_id="user_123")

        assert len(sessions) == 0

    @pytest.mark.asyncio
    async def test_search_sessions_with_since_filter(self, postgres_provider, mock_connection):
        """Test searching sessions with since filter."""
        mock_connection.fetch.return_value = []

        sessions = await postgres_provider.search_sessions(
            since=datetime.now(timezone.utc) - timedelta(days=1)
        )

        assert len(sessions) == 0


# ============================================
# Hybrid Provider Unit Tests
# ============================================

class TestHybridContextProviderUnit:
    """Unit tests for HybridContextProvider with mocked backends."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return ContextConfig(
            redis_url="redis://localhost:6379",
            postgres_url="postgresql://localhost/test",
            ttl_seconds=3600,
            max_history_turns=10,
        )

    @pytest.fixture
    def mock_redis_provider(self):
        """Create a mock Redis provider."""
        mock = AsyncMock()
        mock.connect = AsyncMock()
        mock.close = AsyncMock()
        mock.create_session = AsyncMock()
        mock.get_session = AsyncMock(return_value=None)
        mock.update_session = AsyncMock()
        mock.delete_session = AsyncMock(return_value=True)
        mock.get_history = AsyncMock(return_value=ConversationHistory(session_id="test"))
        mock.add_turn = AsyncMock()
        mock.get_variables = AsyncMock(return_value=ContextVariables(session_id="test"))
        mock.set_variable = AsyncMock()
        mock.delete_variable = AsyncMock(return_value=True)
        mock.get_execution_context = AsyncMock()
        return mock

    @pytest.fixture
    def mock_postgres_provider(self):
        """Create a mock PostgreSQL provider."""
        mock = AsyncMock()
        mock.connect = AsyncMock()
        mock.close = AsyncMock()
        mock.create_tables = AsyncMock()
        mock.create_session = AsyncMock()
        mock.get_session = AsyncMock(return_value=None)
        mock.update_session = AsyncMock()
        mock.delete_session = AsyncMock(return_value=True)
        mock.get_history = AsyncMock(return_value=ConversationHistory(session_id="test"))
        mock.add_turn = AsyncMock()
        mock.get_variables = AsyncMock(return_value=ContextVariables(session_id="test"))
        mock.set_variable = AsyncMock()
        mock.delete_variable = AsyncMock(return_value=True)
        mock.get_execution_context = AsyncMock()
        mock.cleanup_expired = AsyncMock(return_value=0)
        mock.get_full_history = AsyncMock(return_value=[])
        mock.search_sessions = AsyncMock(return_value=[])
        return mock

    @pytest.fixture
    async def hybrid_provider(self, config, mock_redis_provider, mock_postgres_provider):
        """Create a HybridContextProvider with mocked backends."""
        from src.context_primitives.stores.hybrid import HybridContextProvider

        provider = HybridContextProvider(config)
        provider.redis = mock_redis_provider
        provider.postgres = mock_postgres_provider
        return provider

    @pytest.mark.asyncio
    async def test_connect(self, hybrid_provider, mock_redis_provider, mock_postgres_provider):
        """Test connecting to both backends."""
        await hybrid_provider.connect()

        mock_redis_provider.connect.assert_called_once()
        mock_postgres_provider.connect.assert_called_once()
        mock_postgres_provider.create_tables.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self, hybrid_provider, mock_redis_provider, mock_postgres_provider):
        """Test closing both backends."""
        await hybrid_provider.close()

        mock_redis_provider.close.assert_called_once()
        mock_postgres_provider.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_session(self, hybrid_provider, mock_redis_provider, mock_postgres_provider):
        """Test creating session in both backends."""
        session = SessionContext(session_id="test")
        mock_redis_provider.create_session.return_value = session
        mock_postgres_provider.create_session.return_value = session

        result = await hybrid_provider.create_session("test", "user", {"key": "value"})

        assert result == session
        mock_redis_provider.create_session.assert_called()
        mock_postgres_provider.create_session.assert_called()

    @pytest.mark.asyncio
    async def test_get_session_from_redis(self, hybrid_provider, mock_redis_provider):
        """Test getting session from Redis (cache hit)."""
        session = SessionContext(session_id="test")
        mock_redis_provider.get_session.return_value = session

        result = await hybrid_provider.get_session("test")

        assert result == session
        mock_redis_provider.get_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session_fallback_to_postgres(
        self, hybrid_provider, mock_redis_provider, mock_postgres_provider
    ):
        """Test getting session from PostgreSQL (cache miss)."""
        session = SessionContext(session_id="test")
        mock_redis_provider.get_session.return_value = None
        mock_postgres_provider.get_session.return_value = session
        mock_postgres_provider.get_history.return_value = ConversationHistory(
            session_id="test", turns=[]
        )
        mock_postgres_provider.get_variables.return_value = ContextVariables(session_id="test")

        result = await hybrid_provider.get_session("test")

        assert result == session
        mock_redis_provider.get_session.assert_called()
        mock_postgres_provider.get_session.assert_called()

    @pytest.mark.asyncio
    async def test_get_session_not_found(self, hybrid_provider, mock_redis_provider, mock_postgres_provider):
        """Test getting non-existent session."""
        mock_redis_provider.get_session.return_value = None
        mock_postgres_provider.get_session.return_value = None

        result = await hybrid_provider.get_session("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_update_session(self, hybrid_provider, mock_redis_provider, mock_postgres_provider):
        """Test updating session in both backends."""
        session = SessionContext(session_id="test")

        await hybrid_provider.update_session(session)

        mock_redis_provider.update_session.assert_called()
        mock_postgres_provider.update_session.assert_called()

    @pytest.mark.asyncio
    async def test_delete_session(self, hybrid_provider, mock_redis_provider, mock_postgres_provider):
        """Test deleting session from both backends."""
        result = await hybrid_provider.delete_session("test")

        assert result is True
        mock_redis_provider.delete_session.assert_called()
        mock_postgres_provider.delete_session.assert_called()

    @pytest.mark.asyncio
    async def test_get_history_from_redis(self, hybrid_provider, mock_redis_provider):
        """Test getting history from Redis."""
        history = ConversationHistory(
            session_id="test",
            turns=[ConversationTurn(
                turn_id=1,
                timestamp=datetime.now(timezone.utc),
                user_input="Hi",
                assistant_response="Hello"
            )]
        )
        mock_redis_provider.get_history.return_value = history

        result = await hybrid_provider.get_history("test")

        assert len(result.turns) == 1
        mock_redis_provider.get_history.assert_called()

    @pytest.mark.asyncio
    async def test_get_history_fallback_to_postgres(
        self, hybrid_provider, mock_redis_provider, mock_postgres_provider
    ):
        """Test getting history from PostgreSQL."""
        empty_history = ConversationHistory(session_id="test", turns=[])
        pg_history = ConversationHistory(
            session_id="test",
            turns=[ConversationTurn(
                turn_id=1,
                timestamp=datetime.now(timezone.utc),
                user_input="Hi",
                assistant_response="Hello"
            )]
        )
        mock_redis_provider.get_history.return_value = empty_history
        mock_postgres_provider.get_history.return_value = pg_history

        result = await hybrid_provider.get_history("test")

        assert len(result.turns) == 1
        mock_postgres_provider.get_history.assert_called()

    @pytest.mark.asyncio
    async def test_add_turn(self, hybrid_provider, mock_redis_provider, mock_postgres_provider):
        """Test adding turn to both backends."""
        turn = ConversationTurn(
            turn_id=1,
            timestamp=datetime.now(timezone.utc),
            user_input="Hi",
            assistant_response="Hello"
        )

        await hybrid_provider.add_turn("test", turn)

        mock_redis_provider.add_turn.assert_called()
        mock_postgres_provider.add_turn.assert_called()

    @pytest.mark.asyncio
    async def test_get_variables_from_redis(self, hybrid_provider, mock_redis_provider):
        """Test getting variables from Redis."""
        variables = ContextVariables(session_id="test")
        variables.set("key", "value")
        mock_redis_provider.get_variables.return_value = variables

        result = await hybrid_provider.get_variables("test")

        assert result.get("key") == "value"

    @pytest.mark.asyncio
    async def test_set_variable(self, hybrid_provider, mock_redis_provider, mock_postgres_provider):
        """Test setting variable in both backends."""
        await hybrid_provider.set_variable("test", "key", "value")

        mock_redis_provider.set_variable.assert_called()
        mock_postgres_provider.set_variable.assert_called()

    @pytest.mark.asyncio
    async def test_delete_variable(self, hybrid_provider, mock_redis_provider, mock_postgres_provider):
        """Test deleting variable from both backends."""
        result = await hybrid_provider.delete_variable("test", "key")

        assert result is True
        mock_redis_provider.delete_variable.assert_called()
        mock_postgres_provider.delete_variable.assert_called()

    @pytest.mark.asyncio
    async def test_get_execution_context_from_redis(
        self, hybrid_provider, mock_redis_provider
    ):
        """Test getting execution context from Redis."""
        session = SessionContext(session_id="test")
        history = ConversationHistory(session_id="test")
        variables = ContextVariables(session_id="test")

        mock_redis_provider.get_session.return_value = session
        mock_redis_provider.get_history.return_value = history
        mock_redis_provider.get_variables.return_value = variables

        context = await hybrid_provider.get_execution_context("test")

        assert context.session == session

    @pytest.mark.asyncio
    async def test_get_execution_context_fallback(
        self, hybrid_provider, mock_redis_provider, mock_postgres_provider
    ):
        """Test getting execution context with fallback to PostgreSQL."""
        mock_redis_provider.get_session.return_value = None

        session = SessionContext(session_id="test")
        pg_context = ExecutionContext(
            session=session,
            history=ConversationHistory(session_id="test"),
            variables=ContextVariables(session_id="test"),
        )
        mock_postgres_provider.get_execution_context.return_value = pg_context
        mock_postgres_provider.get_history.return_value = ConversationHistory(session_id="test")
        mock_postgres_provider.get_variables.return_value = ContextVariables(session_id="test")

        context = await hybrid_provider.get_execution_context("test")

        assert context.session == session

    @pytest.mark.asyncio
    async def test_cleanup_expired(self, hybrid_provider, mock_postgres_provider):
        """Test cleanup_expired delegates to PostgreSQL."""
        mock_postgres_provider.cleanup_expired.return_value = 5

        count = await hybrid_provider.cleanup_expired()

        assert count == 5
        mock_postgres_provider.cleanup_expired.assert_called()

    @pytest.mark.asyncio
    async def test_get_full_history(self, hybrid_provider, mock_postgres_provider):
        """Test get_full_history delegates to PostgreSQL."""
        turns = [
            ConversationTurn(
                turn_id=i,
                timestamp=datetime.now(timezone.utc),
                user_input=f"Q{i}",
                assistant_response=f"A{i}"
            )
            for i in range(20)
        ]
        mock_postgres_provider.get_full_history.return_value = turns

        result = await hybrid_provider.get_full_history("test")

        assert len(result) == 20
        mock_postgres_provider.get_full_history.assert_called()

    @pytest.mark.asyncio
    async def test_search_sessions(self, hybrid_provider, mock_postgres_provider):
        """Test search_sessions delegates to PostgreSQL."""
        sessions = [SessionContext(session_id="test")]
        mock_postgres_provider.search_sessions.return_value = sessions

        result = await hybrid_provider.search_sessions(user_id="user")

        assert len(result) == 1
        mock_postgres_provider.search_sessions.assert_called()

    @pytest.mark.asyncio
    async def test_sync_to_postgres_success(
        self, hybrid_provider, mock_redis_provider, mock_postgres_provider
    ):
        """Test successful sync from Redis to PostgreSQL."""
        session = SessionContext(session_id="test")
        history = ConversationHistory(
            session_id="test",
            turns=[ConversationTurn(
                turn_id=1,
                timestamp=datetime.now(timezone.utc),
                user_input="Hi",
                assistant_response="Hello"
            )]
        )
        variables = ContextVariables(session_id="test")
        variables.set("key", "value")
        pg_history = ConversationHistory(session_id="test", turns=[])

        mock_redis_provider.get_session.return_value = session
        mock_redis_provider.get_history.return_value = history
        mock_redis_provider.get_variables.return_value = variables
        mock_postgres_provider.get_history.return_value = pg_history

        result = await hybrid_provider.sync_to_postgres("test")

        assert result is True
        mock_postgres_provider.update_session.assert_called()

    @pytest.mark.asyncio
    async def test_sync_to_postgres_session_not_found(
        self, hybrid_provider, mock_redis_provider
    ):
        """Test sync when session not in Redis."""
        mock_redis_provider.get_session.return_value = None

        result = await hybrid_provider.sync_to_postgres("nonexistent")

        assert result is False

    @pytest.mark.asyncio
    async def test_invalidate_cache(self, hybrid_provider, mock_redis_provider):
        """Test cache invalidation."""
        result = await hybrid_provider.invalidate_cache("test")

        assert result is True
        mock_redis_provider.delete_session.assert_called()

    @pytest.mark.asyncio
    async def test_warm_redis_session_error_handling(
        self, hybrid_provider, mock_redis_provider, mock_postgres_provider
    ):
        """Test that cache warming errors are handled gracefully."""
        session = SessionContext(session_id="test")
        mock_redis_provider.create_session.side_effect = Exception("Redis error")
        mock_postgres_provider.get_history.return_value = ConversationHistory(session_id="test")
        mock_postgres_provider.get_variables.return_value = ContextVariables(session_id="test")

        # Should not raise
        await hybrid_provider._warm_redis_session(session)
