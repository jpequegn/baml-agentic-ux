"""
Tests for Context Provider Factory

Part of Phase 7: BAML Context Primitives Implementation
Issue #108 - Task 7.8: Context Primitives Testing & Documentation
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from src.context_primitives.provider import ContextConfig, ContextBackend
from src.context_primitives.stores.factory import create_provider, create_memory_provider
from src.context_primitives.stores.memory import InMemoryContextProvider


class TestCreateMemoryProvider:
    """Tests for create_memory_provider convenience function."""

    def test_default_config(self):
        """Test creating provider with default config."""
        provider = create_memory_provider()

        assert isinstance(provider, InMemoryContextProvider)
        assert provider.config.max_history_turns == 20
        assert provider.config.ttl_seconds == 3600
        assert provider.config.backend == ContextBackend.IN_MEMORY

    def test_custom_max_history_turns(self):
        """Test creating provider with custom max_history_turns."""
        provider = create_memory_provider(max_history_turns=50)

        assert provider.config.max_history_turns == 50
        assert provider.config.ttl_seconds == 3600

    def test_custom_ttl_seconds(self):
        """Test creating provider with custom ttl_seconds."""
        provider = create_memory_provider(ttl_seconds=7200)

        assert provider.config.max_history_turns == 20
        assert provider.config.ttl_seconds == 7200

    def test_custom_both_params(self):
        """Test creating provider with both custom params."""
        provider = create_memory_provider(max_history_turns=10, ttl_seconds=1800)

        assert provider.config.max_history_turns == 10
        assert provider.config.ttl_seconds == 1800


class TestCreateProviderInMemory:
    """Tests for create_provider with IN_MEMORY backend."""

    @pytest.mark.asyncio
    async def test_in_memory_default(self):
        """Test creating in-memory provider with default config."""
        config = ContextConfig()
        provider = await create_provider(config)

        assert isinstance(provider, InMemoryContextProvider)

    @pytest.mark.asyncio
    async def test_in_memory_explicit_backend(self):
        """Test creating in-memory provider with explicit backend."""
        config = ContextConfig(backend=ContextBackend.IN_MEMORY)
        provider = await create_provider(config)

        assert isinstance(provider, InMemoryContextProvider)


class TestCreateProviderRedis:
    """Tests for create_provider with REDIS backend."""

    @pytest.mark.asyncio
    async def test_redis_missing_url(self):
        """Test Redis backend raises error when URL is missing."""
        config = ContextConfig(backend=ContextBackend.REDIS)

        with pytest.raises(ValueError) as exc_info:
            await create_provider(config)

        assert "redis_url" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_redis_success_with_mock(self):
        """Test Redis backend creation with mocked provider."""
        mock_provider = MagicMock()
        mock_provider.connect = AsyncMock()

        config = ContextConfig(
            backend=ContextBackend.REDIS,
            redis_url="redis://localhost:6379"
        )

        # Patch the import inside the factory function
        with patch.object(
            __import__("src.context_primitives.stores.redis", fromlist=["RedisContextProvider"]),
            "RedisContextProvider",
            return_value=mock_provider
        ):
            provider = await create_provider(config)

            assert provider == mock_provider
            mock_provider.connect.assert_called_once()


class TestCreateProviderPostgreSQL:
    """Tests for create_provider with POSTGRESQL backend."""

    @pytest.mark.asyncio
    async def test_postgres_missing_url(self):
        """Test PostgreSQL backend raises error when URL is missing."""
        config = ContextConfig(backend=ContextBackend.POSTGRESQL)

        with pytest.raises(ValueError) as exc_info:
            await create_provider(config)

        assert "postgres_url" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_postgres_success_with_mock(self):
        """Test PostgreSQL backend creation with mocked provider."""
        mock_provider = MagicMock()
        mock_provider.connect = AsyncMock()
        mock_provider.create_tables = AsyncMock()

        config = ContextConfig(
            backend=ContextBackend.POSTGRESQL,
            postgres_url="postgresql://user:pass@localhost/db"
        )

        with patch(
            "src.context_primitives.stores.postgres.PostgreSQLContextProvider",
            return_value=mock_provider
        ):
            provider = await create_provider(config)

            assert provider == mock_provider
            mock_provider.connect.assert_called_once()
            mock_provider.create_tables.assert_called_once()


class TestCreateProviderHybrid:
    """Tests for create_provider with HYBRID backend."""

    @pytest.mark.asyncio
    async def test_hybrid_missing_redis_url(self):
        """Test Hybrid backend raises error when Redis URL is missing."""
        config = ContextConfig(
            backend=ContextBackend.HYBRID,
            postgres_url="postgresql://user:pass@localhost/db"
        )

        with pytest.raises(ValueError) as exc_info:
            await create_provider(config)

        assert "redis_url" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_hybrid_missing_postgres_url(self):
        """Test Hybrid backend raises error when PostgreSQL URL is missing."""
        config = ContextConfig(
            backend=ContextBackend.HYBRID,
            redis_url="redis://localhost:6379"
        )

        with pytest.raises(ValueError) as exc_info:
            await create_provider(config)

        assert "postgres_url" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_hybrid_success_with_mock(self):
        """Test Hybrid backend creation with mocked provider."""
        mock_provider = MagicMock()
        mock_provider.connect = AsyncMock()

        config = ContextConfig(
            backend=ContextBackend.HYBRID,
            redis_url="redis://localhost:6379",
            postgres_url="postgresql://user:pass@localhost/db"
        )

        with patch(
            "src.context_primitives.stores.hybrid.HybridContextProvider",
            return_value=mock_provider
        ):
            provider = await create_provider(config)

            assert provider == mock_provider
            mock_provider.connect.assert_called_once()


class TestCreateProviderDynamoDB:
    """Tests for create_provider with DYNAMODB backend."""

    @pytest.mark.asyncio
    async def test_dynamodb_not_implemented(self):
        """Test DynamoDB backend raises NotImplementedError."""
        config = ContextConfig(backend=ContextBackend.DYNAMODB)

        with pytest.raises(NotImplementedError) as exc_info:
            await create_provider(config)

        assert "DynamoDB" in str(exc_info.value)


class TestCreateProviderEdgeCases:
    """Edge case tests for create_provider."""

    @pytest.mark.asyncio
    async def test_config_with_all_options(self):
        """Test creating provider with fully configured ContextConfig."""
        config = ContextConfig(
            max_history_turns=50,
            summarize_after=25,
            token_limit=8000,
            backend=ContextBackend.IN_MEMORY,
            ttl_seconds=7200,
        )

        provider = await create_provider(config)

        assert isinstance(provider, InMemoryContextProvider)
        assert provider.config.max_history_turns == 50
        assert provider.config.summarize_after == 25
        assert provider.config.token_limit == 8000
        assert provider.config.ttl_seconds == 7200

    @pytest.mark.asyncio
    async def test_provider_is_reusable(self):
        """Test that created provider can be used for operations."""
        config = ContextConfig()
        provider = await create_provider(config)

        # Verify provider works
        session = await provider.create_session("test_session")
        assert session.session_id == "test_session"

        exists = await provider.session_exists("test_session")
        assert exists is True

        await provider.delete_session("test_session")
        exists = await provider.session_exists("test_session")
        assert exists is False
