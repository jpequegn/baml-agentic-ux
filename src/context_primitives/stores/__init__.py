"""
Context Storage Backends

Provides multiple storage implementations for context management:
- InMemoryContextProvider: Development/testing (no persistence)
- RedisContextProvider: Production hot storage with TTL
- PostgreSQLContextProvider: Persistent storage with SQL
- HybridContextProvider: Redis cache + PostgreSQL persistence

Example:
    from src.context_primitives.stores import (
        InMemoryContextProvider,
        create_provider
    )

    # For development
    provider = InMemoryContextProvider(config)

    # Using factory
    provider = create_provider(config)
"""

from src.context_primitives.stores.memory import InMemoryContextProvider
from src.context_primitives.stores.factory import create_provider

__all__ = [
    "InMemoryContextProvider",
    "create_provider",
]

# Optional imports for Redis/PostgreSQL when available
try:
    from src.context_primitives.stores.redis import RedisContextProvider

    __all__.append("RedisContextProvider")
except ImportError:
    pass

try:
    from src.context_primitives.stores.postgres import PostgreSQLContextProvider

    __all__.append("PostgreSQLContextProvider")
except ImportError:
    pass

try:
    from src.context_primitives.stores.hybrid import HybridContextProvider

    __all__.append("HybridContextProvider")
except ImportError:
    pass
