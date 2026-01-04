"""
Context Provider Factory

Factory function to create the appropriate context provider
based on configuration.

Part of Phase 7: BAML Context Primitives Implementation
Issue #baml-agentic-ux-78d - Task 7.3: Session Store Implementations
"""

from src.context_primitives.provider import ContextProvider, ContextConfig, ContextBackend
from src.context_primitives.stores.memory import InMemoryContextProvider


async def create_provider(config: ContextConfig) -> ContextProvider:
    """
    Create a context provider based on configuration.

    Factory function that instantiates the appropriate provider
    based on the backend specified in the configuration.

    Args:
        config: Context configuration with backend selection

    Returns:
        Configured ContextProvider instance

    Raises:
        ValueError: If backend is not supported
        ImportError: If required dependencies are not installed

    Example:
        # In-memory (default)
        config = ContextConfig()
        provider = await create_provider(config)

        # Redis
        config = ContextConfig(
            backend=ContextBackend.REDIS,
            redis_url="redis://localhost:6379"
        )
        provider = await create_provider(config)

        # PostgreSQL
        config = ContextConfig(
            backend=ContextBackend.POSTGRESQL,
            postgres_url="postgresql://user:pass@localhost/db"
        )
        provider = await create_provider(config)

        # Hybrid (Redis + PostgreSQL)
        config = ContextConfig(
            backend=ContextBackend.HYBRID,
            redis_url="redis://localhost:6379",
            postgres_url="postgresql://user:pass@localhost/db"
        )
        provider = await create_provider(config)
    """
    if config.backend == ContextBackend.IN_MEMORY:
        return InMemoryContextProvider(config)

    elif config.backend == ContextBackend.REDIS:
        try:
            from src.context_primitives.stores.redis import RedisContextProvider
        except ImportError:
            raise ImportError(
                "Redis backend requires 'redis' package. "
                "Install with: pip install redis"
            )

        if not config.redis_url:
            raise ValueError("Redis backend requires redis_url in config")

        provider = RedisContextProvider(config)
        await provider.connect()
        return provider

    elif config.backend == ContextBackend.POSTGRESQL:
        try:
            from src.context_primitives.stores.postgres import PostgreSQLContextProvider
        except ImportError:
            raise ImportError(
                "PostgreSQL backend requires 'asyncpg' package. "
                "Install with: pip install asyncpg"
            )

        if not config.postgres_url:
            raise ValueError("PostgreSQL backend requires postgres_url in config")

        provider = PostgreSQLContextProvider(config)
        await provider.connect()
        await provider.create_tables()
        return provider

    elif config.backend == ContextBackend.HYBRID:
        try:
            from src.context_primitives.stores.hybrid import HybridContextProvider
        except ImportError:
            raise ImportError(
                "Hybrid backend requires 'redis' and 'asyncpg' packages. "
                "Install with: pip install redis asyncpg"
            )

        if not config.redis_url:
            raise ValueError("Hybrid backend requires redis_url in config")
        if not config.postgres_url:
            raise ValueError("Hybrid backend requires postgres_url in config")

        provider = HybridContextProvider(config)
        await provider.connect()
        return provider

    elif config.backend == ContextBackend.DYNAMODB:
        raise NotImplementedError(
            "DynamoDB backend not yet implemented. "
            "Use REDIS or POSTGRESQL for production."
        )

    else:
        raise ValueError(f"Unsupported backend: {config.backend}")


def create_memory_provider(
    max_history_turns: int = 20,
    ttl_seconds: int = 3600,
) -> InMemoryContextProvider:
    """
    Convenience function to create an in-memory provider.

    Useful for testing and development when you don't need
    async initialization.

    Args:
        max_history_turns: Maximum turns to keep in history window
        ttl_seconds: Session time-to-live in seconds

    Returns:
        Configured InMemoryContextProvider

    Example:
        provider = create_memory_provider(max_history_turns=10)
        session = await provider.create_session("test_123")
    """
    config = ContextConfig(
        max_history_turns=max_history_turns,
        ttl_seconds=ttl_seconds,
        backend=ContextBackend.IN_MEMORY,
    )
    return InMemoryContextProvider(config)
