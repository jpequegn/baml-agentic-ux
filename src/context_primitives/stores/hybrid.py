"""
Hybrid Context Provider (Redis + PostgreSQL)

Combines Redis for hot data with PostgreSQL for persistence.
Provides the best of both worlds: fast access and durability.

Part of Phase 7: BAML Context Primitives Implementation
Issue #baml-agentic-ux-78d - Task 7.3: Session Store Implementations

Architecture:
- Redis: Current session, recent history, active variables (hot)
- PostgreSQL: Full history archive, audit log (cold)

Requirements:
    pip install redis asyncpg
"""

import asyncio
from typing import Optional, Any
from datetime import datetime

from src.context_primitives.provider import (
    ContextProvider,
    ContextConfig,
    SessionContext,
    ConversationTurn,
    ConversationHistory,
    ContextVariables,
    ExecutionContext,
)
from src.context_primitives.stores.redis import RedisContextProvider
from src.context_primitives.stores.postgres import PostgreSQLContextProvider


class HybridContextProvider(ContextProvider):
    """
    Hybrid storage combining Redis (hot) with PostgreSQL (cold).

    Architecture:
    - Redis: Fast access for current sessions and recent history
    - PostgreSQL: Persistent storage, audit trail, analytics

    Read path:
    1. Check Redis (hot cache)
    2. If miss, check PostgreSQL
    3. If found in PostgreSQL, warm up Redis cache

    Write path:
    1. Write to Redis immediately (for fast reads)
    2. Write to PostgreSQL in parallel (for persistence)

    Example:
        config = ContextConfig(
            redis_url="redis://localhost:6379",
            postgres_url="postgresql://user:pass@localhost/db",
            ttl_seconds=3600
        )
        provider = HybridContextProvider(config)
        await provider.connect()

        session = await provider.create_session("user_123")
    """

    def __init__(self, config: ContextConfig):
        """
        Initialize hybrid provider.

        Args:
            config: Context configuration with redis_url and postgres_url
        """
        self.config = config
        self.redis = RedisContextProvider(config)
        self.postgres = PostgreSQLContextProvider(config)

    async def connect(self) -> None:
        """Initialize connections to both backends."""
        await asyncio.gather(
            self.redis.connect(),
            self.postgres.connect(),
        )
        # Ensure PostgreSQL tables exist
        await self.postgres.create_tables()

    async def close(self) -> None:
        """Close connections to both backends."""
        await asyncio.gather(
            self.redis.close(),
            self.postgres.close(),
        )

    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> SessionContext:
        """Create a new session in both stores."""
        # Create in both stores in parallel
        redis_task = self.redis.create_session(session_id, user_id, metadata)
        postgres_task = self.postgres.create_session(session_id, user_id, metadata)

        results = await asyncio.gather(redis_task, postgres_task)
        return results[0]  # Return Redis result (same data)

    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """
        Get session, trying Redis first then PostgreSQL.

        Warms up Redis cache if found only in PostgreSQL.
        """
        # Try Redis first (hot cache)
        session = await self.redis.get_session(session_id)
        if session:
            return session

        # Fall back to PostgreSQL
        session = await self.postgres.get_session(session_id)
        if session:
            # Warm up Redis cache
            await self._warm_redis_session(session)
            return session

        return None

    async def _warm_redis_session(self, session: SessionContext) -> None:
        """Populate Redis cache from PostgreSQL data."""
        try:
            await self.redis.create_session(
                session.session_id,
                session.user_id,
                session.metadata,
            )
            # Also warm up history and variables
            history = await self.postgres.get_history(session.session_id)
            variables = await self.postgres.get_variables(session.session_id)

            # Re-add recent turns to Redis
            for turn in history.turns[-self.config.max_history_turns :]:
                await self.redis.add_turn(session.session_id, turn)

            # Re-add variables to Redis
            for key, value in variables.variables.items():
                await self.redis.set_variable(session.session_id, key, value.to_value())
        except Exception:
            # Cache warming is best-effort
            pass

    async def update_session(self, session: SessionContext) -> None:
        """Update session in both stores."""
        await asyncio.gather(
            self.redis.update_session(session),
            self.postgres.update_session(session),
        )

    async def delete_session(self, session_id: str) -> bool:
        """Delete session from both stores."""
        results = await asyncio.gather(
            self.redis.delete_session(session_id),
            self.postgres.delete_session(session_id),
        )
        return any(results)

    async def get_history(self, session_id: str) -> ConversationHistory:
        """
        Get history, trying Redis first.

        For full history, use get_full_history() which queries PostgreSQL.
        """
        # Try Redis first
        history = await self.redis.get_history(session_id)
        if history.turns:
            return history

        # Fall back to PostgreSQL
        return await self.postgres.get_history(session_id)

    async def add_turn(self, session_id: str, turn: ConversationTurn) -> None:
        """Add turn to both stores in parallel."""
        await asyncio.gather(
            self.redis.add_turn(session_id, turn),
            self.postgres.add_turn(session_id, turn),
        )

    async def get_variables(self, session_id: str) -> ContextVariables:
        """Get variables, trying Redis first."""
        # Try Redis first
        variables = await self.redis.get_variables(session_id)
        if variables.variables:
            return variables

        # Fall back to PostgreSQL
        return await self.postgres.get_variables(session_id)

    async def set_variable(self, session_id: str, key: str, value: Any) -> None:
        """Set variable in both stores."""
        await asyncio.gather(
            self.redis.set_variable(session_id, key, value),
            self.postgres.set_variable(session_id, key, value),
        )

    async def delete_variable(self, session_id: str, key: str) -> bool:
        """Delete variable from both stores."""
        results = await asyncio.gather(
            self.redis.delete_variable(session_id, key),
            self.postgres.delete_variable(session_id, key),
        )
        return any(results)

    async def get_execution_context(self, session_id: str) -> ExecutionContext:
        """
        Get complete execution context.

        Tries Redis first, falls back to PostgreSQL and warms cache.
        """
        # Try Redis first
        session = await self.redis.get_session(session_id)

        if session:
            history = await self.redis.get_history(session_id)
            variables = await self.redis.get_variables(session_id)
            return ExecutionContext(
                session=session,
                history=history,
                variables=variables,
            )

        # Fall back to PostgreSQL
        context = await self.postgres.get_execution_context(session_id)

        # Warm up Redis cache
        await self._warm_redis_session(context.session)

        return context

    async def cleanup_expired(self) -> int:
        """
        Clean up expired sessions from PostgreSQL.

        Redis handles expiration automatically via TTL.
        """
        return await self.postgres.cleanup_expired()

    async def get_full_history(
        self, session_id: str, limit: int = 1000
    ) -> list[ConversationTurn]:
        """
        Get full history from PostgreSQL (not windowed).

        Use this for analytics, audit, or conversation export.
        """
        return await self.postgres.get_full_history(session_id, limit)

    async def search_sessions(
        self,
        user_id: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[SessionContext]:
        """
        Search sessions in PostgreSQL.

        Use this for admin/analytics queries.
        """
        return await self.postgres.search_sessions(user_id, since, limit)

    async def sync_to_postgres(self, session_id: str) -> bool:
        """
        Force sync session from Redis to PostgreSQL.

        Useful for ensuring persistence before critical operations.
        """
        try:
            session = await self.redis.get_session(session_id)
            if not session:
                return False

            history = await self.redis.get_history(session_id)
            variables = await self.redis.get_variables(session_id)

            # Update PostgreSQL
            await self.postgres.update_session(session)

            # Add any turns not in PostgreSQL
            pg_history = await self.postgres.get_history(session_id)
            existing_turn_ids = {t.turn_id for t in pg_history.turns}

            for turn in history.turns:
                if turn.turn_id not in existing_turn_ids:
                    await self.postgres.add_turn(session_id, turn)

            # Sync variables
            for key, value in variables.variables.items():
                await self.postgres.set_variable(session_id, key, value.to_value())

            return True
        except Exception:
            return False

    async def invalidate_cache(self, session_id: str) -> bool:
        """
        Invalidate Redis cache for a session.

        Next read will fetch from PostgreSQL and re-warm cache.
        """
        return await self.redis.delete_session(session_id)
