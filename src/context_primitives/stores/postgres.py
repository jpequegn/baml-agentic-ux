"""
PostgreSQL Context Provider

PostgreSQL-backed context storage for persistent history.
Ideal for audit logs, long-term persistence, and analytics.

Part of Phase 7: BAML Context Primitives Implementation
Issue #baml-agentic-ux-78d - Task 7.3: Session Store Implementations

Requirements:
    pip install asyncpg
"""

import json
from typing import Optional, Any
from datetime import datetime, timedelta, timezone

from src.context_primitives.provider import (
    ContextProvider,
    ContextConfig,
    SessionContext,
    ConversationTurn,
    ConversationHistory,
    ContextVariables,
    ContextValue,
    ExecutionContext,
)


class PostgreSQLContextProvider(ContextProvider):
    """
    PostgreSQL-backed context storage for persistence.

    Features:
    - Full ACID compliance
    - SQL-based queries for analytics
    - Long-term history storage
    - Audit trail support

    Tables:
    - lui_sessions: Session metadata
    - lui_conversation_turns: Conversation history
    - lui_context_variables: Context variables

    Example:
        config = ContextConfig(
            postgres_url="postgresql://user:pass@localhost/db",
            ttl_seconds=86400  # 24 hours
        )
        provider = PostgreSQLContextProvider(config)
        await provider.connect()
        await provider.create_tables()

        session = await provider.create_session("user_123")
    """

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS lui_sessions (
        session_id VARCHAR(255) PRIMARY KEY,
        user_id VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW(),
        last_activity TIMESTAMP DEFAULT NOW(),
        metadata JSONB DEFAULT '{}',
        ttl_seconds INTEGER,
        is_active BOOLEAN DEFAULT TRUE
    );

    CREATE TABLE IF NOT EXISTS lui_conversation_turns (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(255) REFERENCES lui_sessions(session_id) ON DELETE CASCADE,
        turn_id INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT NOW(),
        user_input TEXT NOT NULL,
        assistant_response TEXT NOT NULL,
        detected_intent VARCHAR(255),
        extracted_entities JSONB,
        confidence FLOAT,
        component_id VARCHAR(255),
        duration_ms INTEGER
    );

    CREATE INDEX IF NOT EXISTS idx_turns_session_turn
        ON lui_conversation_turns(session_id, turn_id);

    CREATE TABLE IF NOT EXISTS lui_context_variables (
        session_id VARCHAR(255) REFERENCES lui_sessions(session_id) ON DELETE CASCADE,
        key VARCHAR(255) NOT NULL,
        value_type VARCHAR(50) NOT NULL,
        value JSONB NOT NULL,
        updated_at TIMESTAMP DEFAULT NOW(),
        PRIMARY KEY (session_id, key)
    );

    CREATE INDEX IF NOT EXISTS idx_sessions_last_activity
        ON lui_sessions(last_activity);
    """

    def __init__(self, config: ContextConfig):
        """
        Initialize PostgreSQL provider.

        Args:
            config: Context configuration with postgres_url
        """
        self.config = config
        self._pool = None

    async def connect(self) -> None:
        """
        Initialize PostgreSQL connection pool.

        Must be called before using other methods.
        """
        try:
            import asyncpg
        except ImportError:
            raise ImportError("asyncpg package required: pip install asyncpg")

        self._pool = await asyncpg.create_pool(
            self.config.postgres_url or "postgresql://localhost/lui_context",
            min_size=2,
            max_size=10,
        )

    async def close(self) -> None:
        """Close PostgreSQL connection pool."""
        if self._pool:
            await self._pool.close()

    async def create_tables(self) -> None:
        """Create database tables if they don't exist."""
        self._ensure_connected()
        async with self._pool.acquire() as conn:
            await conn.execute(self.SCHEMA)

    def _ensure_connected(self) -> None:
        """Ensure database connection is established."""
        if self._pool is None:
            raise RuntimeError("PostgreSQL not connected. Call connect() first.")

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

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO lui_sessions
                    (session_id, user_id, created_at, last_activity, metadata, ttl_seconds, is_active)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (session_id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    last_activity = EXCLUDED.last_activity,
                    metadata = EXCLUDED.metadata,
                    ttl_seconds = EXCLUDED.ttl_seconds,
                    is_active = EXCLUDED.is_active
                """,
                session.session_id,
                session.user_id,
                session.created_at,
                session.last_activity,
                json.dumps(session.metadata),
                session.ttl_seconds,
                session.is_active,
            )

        return session

    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Retrieve a session by ID."""
        self._ensure_connected()

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT session_id, user_id, created_at, last_activity,
                       metadata, ttl_seconds, is_active
                FROM lui_sessions
                WHERE session_id = $1 AND is_active = TRUE
                """,
                session_id,
            )

        if not row:
            return None

        session = SessionContext(
            session_id=row["session_id"],
            user_id=row["user_id"],
            created_at=row["created_at"],
            last_activity=row["last_activity"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            ttl_seconds=row["ttl_seconds"],
            is_active=row["is_active"],
        )

        # Check expiration
        if session.is_expired():
            await self._mark_session_inactive(session_id)
            return None

        return session

    async def _mark_session_inactive(self, session_id: str) -> None:
        """Mark a session as inactive (soft delete)."""
        async with self._pool.acquire() as conn:
            await conn.execute(
                "UPDATE lui_sessions SET is_active = FALSE WHERE session_id = $1",
                session_id,
            )

    async def update_session(self, session: SessionContext) -> None:
        """Update session data."""
        self._ensure_connected()

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE lui_sessions SET
                    user_id = $2,
                    last_activity = $3,
                    metadata = $4,
                    ttl_seconds = $5,
                    is_active = $6
                WHERE session_id = $1
                """,
                session.session_id,
                session.user_id,
                session.last_activity,
                json.dumps(session.metadata),
                session.ttl_seconds,
                session.is_active,
            )

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and all associated data."""
        self._ensure_connected()

        async with self._pool.acquire() as conn:
            # CASCADE will delete turns and variables
            result = await conn.execute(
                "DELETE FROM lui_sessions WHERE session_id = $1",
                session_id,
            )

        return result.split()[-1] != "0"

    async def get_history(self, session_id: str) -> ConversationHistory:
        """Get conversation history for a session."""
        self._ensure_connected()

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT turn_id, timestamp, user_input, assistant_response,
                       detected_intent, extracted_entities, confidence,
                       component_id, duration_ms
                FROM lui_conversation_turns
                WHERE session_id = $1
                ORDER BY turn_id DESC
                LIMIT $2
                """,
                session_id,
                self.config.max_history_turns,
            )

        turns = []
        for row in reversed(rows):  # Restore chronological order
            entities = row["extracted_entities"]
            if isinstance(entities, str):
                entities = json.loads(entities)

            turns.append(
                ConversationTurn(
                    turn_id=row["turn_id"],
                    timestamp=row["timestamp"],
                    user_input=row["user_input"],
                    assistant_response=row["assistant_response"],
                    detected_intent=row["detected_intent"],
                    extracted_entities=entities,
                    confidence=row["confidence"],
                    component_id=row["component_id"],
                    duration_ms=row["duration_ms"],
                )
            )

        # Get total turn count
        async with self._pool.acquire() as conn:
            total = await conn.fetchval(
                "SELECT COUNT(*) FROM lui_conversation_turns WHERE session_id = $1",
                session_id,
            )

        return ConversationHistory(
            session_id=session_id,
            turns=turns,
            max_turns=self.config.max_history_turns,
            total_turns=total or 0,
        )

    async def add_turn(self, session_id: str, turn: ConversationTurn) -> None:
        """Add a conversation turn to history."""
        self._ensure_connected()

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO lui_conversation_turns
                    (session_id, turn_id, timestamp, user_input, assistant_response,
                     detected_intent, extracted_entities, confidence, component_id, duration_ms)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                session_id,
                turn.turn_id,
                turn.timestamp,
                turn.user_input,
                turn.assistant_response,
                turn.detected_intent,
                json.dumps(turn.extracted_entities) if turn.extracted_entities else None,
                turn.confidence,
                turn.component_id,
                turn.duration_ms,
            )

            # Touch session
            await conn.execute(
                "UPDATE lui_sessions SET last_activity = $2 WHERE session_id = $1",
                session_id,
                datetime.now(timezone.utc),
            )

    async def get_variables(self, session_id: str) -> ContextVariables:
        """Get context variables for a session."""
        self._ensure_connected()

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT key, value_type, value, updated_at
                FROM lui_context_variables
                WHERE session_id = $1
                """,
                session_id,
            )

        variables = ContextVariables(session_id=session_id)

        for row in rows:
            value_data = row["value"]
            if isinstance(value_data, str):
                value_data = json.loads(value_data)

            variables.variables[row["key"]] = ContextValue.from_dict(
                {"value_type": row["value_type"], **value_data}
            )

        if rows:
            variables.updated_at = max(row["updated_at"] for row in rows)

        return variables

    async def set_variable(self, session_id: str, key: str, value: Any) -> None:
        """Set a context variable."""
        self._ensure_connected()

        ctx_value = ContextValue.from_value(value)
        value_dict = ctx_value.to_dict()
        value_type = value_dict.pop("value_type")

        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO lui_context_variables (session_id, key, value_type, value, updated_at)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (session_id, key) DO UPDATE SET
                    value_type = EXCLUDED.value_type,
                    value = EXCLUDED.value,
                    updated_at = EXCLUDED.updated_at
                """,
                session_id,
                key,
                value_type,
                json.dumps(value_dict),
                datetime.now(timezone.utc),
            )

    async def delete_variable(self, session_id: str, key: str) -> bool:
        """Delete a context variable."""
        self._ensure_connected()

        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM lui_context_variables WHERE session_id = $1 AND key = $2",
                session_id,
                key,
            )

        return result.split()[-1] != "0"

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
        """Clean up expired sessions."""
        self._ensure_connected()

        async with self._pool.acquire() as conn:
            # Find and mark expired sessions
            result = await conn.execute(
                """
                UPDATE lui_sessions SET is_active = FALSE
                WHERE is_active = TRUE
                  AND ttl_seconds IS NOT NULL
                  AND last_activity + (ttl_seconds || ' seconds')::interval < NOW()
                """
            )

        count = int(result.split()[-1])
        return count

    async def get_full_history(
        self, session_id: str, limit: int = 1000
    ) -> list[ConversationTurn]:
        """
        Get full conversation history (not windowed).

        Useful for analytics and audit purposes.

        Args:
            session_id: Session to get history for
            limit: Maximum turns to retrieve

        Returns:
            List of all conversation turns
        """
        self._ensure_connected()

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT turn_id, timestamp, user_input, assistant_response,
                       detected_intent, extracted_entities, confidence,
                       component_id, duration_ms
                FROM lui_conversation_turns
                WHERE session_id = $1
                ORDER BY turn_id ASC
                LIMIT $2
                """,
                session_id,
                limit,
            )

        turns = []
        for row in rows:
            entities = row["extracted_entities"]
            if isinstance(entities, str):
                entities = json.loads(entities)

            turns.append(
                ConversationTurn(
                    turn_id=row["turn_id"],
                    timestamp=row["timestamp"],
                    user_input=row["user_input"],
                    assistant_response=row["assistant_response"],
                    detected_intent=row["detected_intent"],
                    extracted_entities=entities,
                    confidence=row["confidence"],
                    component_id=row["component_id"],
                    duration_ms=row["duration_ms"],
                )
            )

        return turns

    async def search_sessions(
        self,
        user_id: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> list[SessionContext]:
        """
        Search for sessions by criteria.

        Args:
            user_id: Filter by user ID
            since: Filter by sessions created after this time
            limit: Maximum results

        Returns:
            List of matching sessions
        """
        self._ensure_connected()

        query = "SELECT * FROM lui_sessions WHERE is_active = TRUE"
        params = []
        param_idx = 1

        if user_id:
            query += f" AND user_id = ${param_idx}"
            params.append(user_id)
            param_idx += 1

        if since:
            query += f" AND created_at > ${param_idx}"
            params.append(since)
            param_idx += 1

        query += f" ORDER BY last_activity DESC LIMIT ${param_idx}"
        params.append(limit)

        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

        return [
            SessionContext(
                session_id=row["session_id"],
                user_id=row["user_id"],
                created_at=row["created_at"],
                last_activity=row["last_activity"],
                metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                ttl_seconds=row["ttl_seconds"],
                is_active=row["is_active"],
            )
            for row in rows
        ]
