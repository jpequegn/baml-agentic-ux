"""
Redis Context Provider

Redis-backed context storage for production deployments.
Provides fast key-value storage with automatic TTL expiration.

Part of Phase 7: BAML Context Primitives Implementation
Issue #baml-agentic-ux-78d - Task 7.3: Session Store Implementations

Requirements:
    pip install redis
"""

import json
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


class RedisContextProvider(ContextProvider):
    """
    Redis-backed context storage for production.

    Features:
    - Automatic TTL-based session expiration
    - Key prefixing for namespace isolation
    - JSON serialization for complex types
    - Async Redis operations

    Key structure:
    - lui:context:session:{session_id} - Session data
    - lui:context:history:{session_id} - Conversation history
    - lui:context:vars:{session_id} - Context variables

    Example:
        config = ContextConfig(
            redis_url="redis://localhost:6379",
            ttl_seconds=3600
        )
        provider = RedisContextProvider(config)
        await provider.connect()

        session = await provider.create_session("user_123")
    """

    def __init__(self, config: ContextConfig):
        """
        Initialize Redis provider.

        Args:
            config: Context configuration with redis_url
        """
        self.config = config
        self._redis = None
        self._prefix = "lui:context:"

    async def connect(self) -> None:
        """
        Initialize Redis connection.

        Must be called before using other methods.
        """
        try:
            import redis.asyncio as aioredis
        except ImportError:
            raise ImportError("redis package required: pip install redis")

        self._redis = aioredis.from_url(
            self.config.redis_url or "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=True,
        )

    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()

    def _session_key(self, session_id: str) -> str:
        """Generate key for session data."""
        return f"{self._prefix}session:{session_id}"

    def _history_key(self, session_id: str) -> str:
        """Generate key for history data."""
        return f"{self._prefix}history:{session_id}"

    def _variables_key(self, session_id: str) -> str:
        """Generate key for variables data."""
        return f"{self._prefix}vars:{session_id}"

    def _ensure_connected(self) -> None:
        """Ensure Redis connection is established."""
        if self._redis is None:
            raise RuntimeError("Redis not connected. Call connect() first.")

    def _serialize_session(self, session: SessionContext) -> str:
        """Serialize session to JSON."""
        return json.dumps(
            {
                "session_id": session.session_id,
                "user_id": session.user_id,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "metadata": session.metadata,
                "ttl_seconds": session.ttl_seconds,
                "is_active": session.is_active,
            }
        )

    def _deserialize_session(self, data: str) -> SessionContext:
        """Deserialize session from JSON."""
        obj = json.loads(data)
        return SessionContext(
            session_id=obj["session_id"],
            user_id=obj.get("user_id"),
            created_at=datetime.fromisoformat(obj["created_at"]),
            last_activity=datetime.fromisoformat(obj["last_activity"]),
            metadata=obj.get("metadata", {}),
            ttl_seconds=obj.get("ttl_seconds"),
            is_active=obj.get("is_active", True),
        )

    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> SessionContext:
        """Create a new session."""
        self._ensure_connected()

        session = SessionContext(
            session_id=session_id,
            user_id=user_id,
            metadata=metadata or {},
            ttl_seconds=self.config.ttl_seconds,
            is_active=True,
        )

        # Store session with TTL
        ttl = self.config.ttl_seconds or 3600
        await self._redis.setex(
            self._session_key(session_id), ttl, self._serialize_session(session)
        )

        # Initialize empty history and variables
        history = ConversationHistory(
            session_id=session_id,
            max_turns=self.config.max_history_turns,
        )
        await self._redis.setex(
            self._history_key(session_id), ttl, json.dumps(history.to_dict())
        )

        variables = ContextVariables(session_id=session_id)
        await self._redis.setex(
            self._variables_key(session_id), ttl, json.dumps(variables.to_dict())
        )

        return session

    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Retrieve a session by ID."""
        self._ensure_connected()

        data = await self._redis.get(self._session_key(session_id))
        if data:
            return self._deserialize_session(data)
        return None

    async def update_session(self, session: SessionContext) -> None:
        """Update session data."""
        self._ensure_connected()

        # Get remaining TTL to preserve it
        ttl = await self._redis.ttl(self._session_key(session.session_id))
        if ttl < 0:
            ttl = self.config.ttl_seconds or 3600

        await self._redis.setex(
            self._session_key(session.session_id),
            ttl,
            self._serialize_session(session),
        )

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and all associated data."""
        self._ensure_connected()

        # Delete all keys for this session
        keys = [
            self._session_key(session_id),
            self._history_key(session_id),
            self._variables_key(session_id),
        ]
        deleted = await self._redis.delete(*keys)
        return deleted > 0

    async def get_history(self, session_id: str) -> ConversationHistory:
        """Get conversation history for a session."""
        self._ensure_connected()

        data = await self._redis.get(self._history_key(session_id))
        if data:
            return ConversationHistory.from_dict(json.loads(data))

        return ConversationHistory(
            session_id=session_id,
            max_turns=self.config.max_history_turns,
        )

    async def add_turn(self, session_id: str, turn: ConversationTurn) -> None:
        """Add a conversation turn to history."""
        self._ensure_connected()

        # Get current history
        history = await self.get_history(session_id)
        history.add_turn(turn)

        # Get TTL from session key
        ttl = await self._redis.ttl(self._session_key(session_id))
        if ttl < 0:
            ttl = self.config.ttl_seconds or 3600

        # Update history
        await self._redis.setex(
            self._history_key(session_id), ttl, json.dumps(history.to_dict())
        )

        # Touch session
        session = await self.get_session(session_id)
        if session:
            session.touch()
            await self.update_session(session)

    async def get_variables(self, session_id: str) -> ContextVariables:
        """Get context variables for a session."""
        self._ensure_connected()

        data = await self._redis.get(self._variables_key(session_id))
        if data:
            return ContextVariables.from_dict(json.loads(data))

        return ContextVariables(session_id=session_id)

    async def set_variable(self, session_id: str, key: str, value: Any) -> None:
        """Set a context variable."""
        self._ensure_connected()

        variables = await self.get_variables(session_id)
        variables.set(key, value)

        # Get TTL from session key
        ttl = await self._redis.ttl(self._session_key(session_id))
        if ttl < 0:
            ttl = self.config.ttl_seconds or 3600

        await self._redis.setex(
            self._variables_key(session_id), ttl, json.dumps(variables.to_dict())
        )

    async def delete_variable(self, session_id: str, key: str) -> bool:
        """Delete a context variable."""
        self._ensure_connected()

        variables = await self.get_variables(session_id)
        result = variables.delete(key)

        if result:
            ttl = await self._redis.ttl(self._session_key(session_id))
            if ttl < 0:
                ttl = self.config.ttl_seconds or 3600

            await self._redis.setex(
                self._variables_key(session_id), ttl, json.dumps(variables.to_dict())
            )

        return result

    async def get_execution_context(self, session_id: str) -> ExecutionContext:
        """Get complete execution context for a session."""
        self._ensure_connected()

        session = await self.get_session(session_id)
        if not session:
            session = await self.create_session(session_id)

        history = await self.get_history(session_id)
        variables = await self.get_variables(session_id)

        return ExecutionContext(
            session=session,
            history=history,
            variables=variables,
        )

    async def cleanup_expired(self) -> int:
        """
        Clean up expired sessions.

        Note: Redis handles TTL expiration automatically, so this
        method is a no-op. Included for interface compliance.
        """
        # Redis handles expiration automatically via TTL
        return 0

    async def extend_ttl(self, session_id: str, additional_seconds: int) -> bool:
        """
        Extend the TTL for a session.

        Args:
            session_id: Session to extend
            additional_seconds: Seconds to add to current TTL

        Returns:
            True if session exists and TTL was extended
        """
        self._ensure_connected()

        current_ttl = await self._redis.ttl(self._session_key(session_id))
        if current_ttl < 0:
            return False

        new_ttl = current_ttl + additional_seconds

        # Extend TTL on all keys
        await self._redis.expire(self._session_key(session_id), new_ttl)
        await self._redis.expire(self._history_key(session_id), new_ttl)
        await self._redis.expire(self._variables_key(session_id), new_ttl)

        return True

    async def get_session_ttl(self, session_id: str) -> Optional[int]:
        """
        Get remaining TTL for a session.

        Returns:
            Remaining seconds, or None if session doesn't exist
        """
        self._ensure_connected()

        ttl = await self._redis.ttl(self._session_key(session_id))
        if ttl < 0:
            return None
        return ttl
