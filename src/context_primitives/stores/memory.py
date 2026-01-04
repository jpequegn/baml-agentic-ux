"""
In-Memory Context Provider

Thread-safe in-memory storage for context management.
Ideal for development, testing, and single-instance deployments.

Part of Phase 7: BAML Context Primitives Implementation
Issue #baml-agentic-ux-78d - Task 7.3: Session Store Implementations
"""

import asyncio
from typing import Optional, Any
from datetime import datetime, timezone

from src.context_primitives.provider import (
    ContextProvider,
    ContextConfig,
    SessionContext,
    ConversationTurn,
    ConversationHistory,
    ContextVariables,
    ExecutionContext,
)


class InMemoryContextProvider(ContextProvider):
    """
    In-memory context storage for development and testing.

    Features:
    - Thread-safe with asyncio.Lock
    - Full ContextProvider interface implementation
    - Automatic session expiration based on TTL
    - No external dependencies

    Note: Data is not persisted across restarts.

    Example:
        config = ContextConfig(max_history_turns=20, ttl_seconds=3600)
        provider = InMemoryContextProvider(config)

        session = await provider.create_session("user_123")
        await provider.add_turn("user_123", turn)
        context = await provider.get_execution_context("user_123")
    """

    def __init__(self, config: ContextConfig):
        """
        Initialize in-memory provider.

        Args:
            config: Context configuration including max_history_turns and ttl_seconds
        """
        self.config = config
        self._sessions: dict[str, SessionContext] = {}
        self._histories: dict[str, ConversationHistory] = {}
        self._variables: dict[str, ContextVariables] = {}
        self._lock = asyncio.Lock()

    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> SessionContext:
        """Create a new session."""
        async with self._lock:
            session = SessionContext(
                session_id=session_id,
                user_id=user_id,
                metadata=metadata or {},
                ttl_seconds=self.config.ttl_seconds,
                is_active=True,
            )
            self._sessions[session_id] = session
            self._histories[session_id] = ConversationHistory(
                session_id=session_id,
                max_turns=self.config.max_history_turns,
            )
            self._variables[session_id] = ContextVariables(session_id=session_id)
            return session

    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Retrieve a session by ID."""
        session = self._sessions.get(session_id)
        if session and session.is_expired():
            # Auto-cleanup expired sessions
            await self.delete_session(session_id)
            return None
        return session

    async def update_session(self, session: SessionContext) -> None:
        """Update session data."""
        async with self._lock:
            if session.session_id in self._sessions:
                self._sessions[session.session_id] = session

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session and all associated data."""
        async with self._lock:
            existed = session_id in self._sessions
            self._sessions.pop(session_id, None)
            self._histories.pop(session_id, None)
            self._variables.pop(session_id, None)
            return existed

    async def get_history(self, session_id: str) -> ConversationHistory:
        """Get conversation history for a session."""
        history = self._histories.get(session_id)
        if history is None:
            # Return empty history if session doesn't exist
            return ConversationHistory(
                session_id=session_id,
                max_turns=self.config.max_history_turns,
            )
        return history

    async def add_turn(self, session_id: str, turn: ConversationTurn) -> None:
        """Add a conversation turn to history."""
        async with self._lock:
            # Create session if it doesn't exist
            if session_id not in self._sessions:
                await self._create_session_unlocked(session_id)

            history = self._histories.get(session_id)
            if history:
                history.add_turn(turn)
                # Touch session to update last_activity
                session = self._sessions.get(session_id)
                if session:
                    session.touch()

    async def _create_session_unlocked(self, session_id: str) -> SessionContext:
        """Create session without acquiring lock (for internal use)."""
        session = SessionContext(
            session_id=session_id,
            ttl_seconds=self.config.ttl_seconds,
            is_active=True,
        )
        self._sessions[session_id] = session
        self._histories[session_id] = ConversationHistory(
            session_id=session_id,
            max_turns=self.config.max_history_turns,
        )
        self._variables[session_id] = ContextVariables(session_id=session_id)
        return session

    async def get_variables(self, session_id: str) -> ContextVariables:
        """Get context variables for a session."""
        variables = self._variables.get(session_id)
        if variables is None:
            return ContextVariables(session_id=session_id)
        return variables

    async def set_variable(self, session_id: str, key: str, value: Any) -> None:
        """Set a context variable."""
        async with self._lock:
            # Create session if it doesn't exist
            if session_id not in self._variables:
                await self._create_session_unlocked(session_id)

            variables = self._variables.get(session_id)
            if variables:
                variables.set(key, value)

    async def delete_variable(self, session_id: str, key: str) -> bool:
        """Delete a context variable."""
        async with self._lock:
            variables = self._variables.get(session_id)
            if variables:
                return variables.delete(key)
            return False

    async def get_execution_context(self, session_id: str) -> ExecutionContext:
        """Get complete execution context for a session."""
        session = await self.get_session(session_id)
        if not session:
            session = await self.create_session(session_id)

        history = self._histories.get(
            session_id,
            ConversationHistory(
                session_id=session_id,
                max_turns=self.config.max_history_turns,
            ),
        )
        variables = self._variables.get(
            session_id, ContextVariables(session_id=session_id)
        )

        return ExecutionContext(
            session=session,
            history=history,
            variables=variables,
        )

    async def cleanup_expired(self) -> int:
        """Clean up expired sessions."""
        async with self._lock:
            expired = []
            now = datetime.now(timezone.utc)

            for session_id, session in self._sessions.items():
                if session.is_expired():
                    expired.append(session_id)

            for session_id in expired:
                self._sessions.pop(session_id, None)
                self._histories.pop(session_id, None)
                self._variables.pop(session_id, None)

            return len(expired)

    async def get_all_sessions(self) -> list[SessionContext]:
        """
        Get all active sessions (for debugging/admin).

        Returns:
            List of all active SessionContext objects
        """
        return list(self._sessions.values())

    async def get_session_count(self) -> int:
        """
        Get count of active sessions.

        Returns:
            Number of active sessions
        """
        return len(self._sessions)

    async def clear_all(self) -> None:
        """
        Clear all sessions (for testing).

        Warning: This deletes ALL data.
        """
        async with self._lock:
            self._sessions.clear()
            self._histories.clear()
            self._variables.clear()
