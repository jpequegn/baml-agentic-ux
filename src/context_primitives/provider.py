"""
Context Provider Interface

Defines the abstract interface for context storage backends,
enabling pluggable implementations (in-memory, Redis, PostgreSQL, etc.)

Part of Phase 7: BAML Context Primitives Implementation
Issue #baml-agentic-ux-qww - Task 7.2: Context Provider Interface
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


def _utcnow() -> datetime:
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


class ContextBackend(Enum):
    """Supported context storage backends."""

    IN_MEMORY = "in_memory"
    REDIS = "redis"
    POSTGRESQL = "postgresql"
    DYNAMODB = "dynamodb"
    HYBRID = "hybrid"


class ContextValueType(Enum):
    """Type discriminator for context variable values."""

    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    LIST = "LIST"
    OBJECT = "OBJECT"
    NULL = "NULL"


@dataclass
class SessionContext:
    """
    Session-level context information.

    Tracks the lifecycle of a conversation session including
    creation time, last activity, and custom metadata.
    """

    session_id: str
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=_utcnow)
    last_activity: datetime = field(default_factory=_utcnow)
    metadata: dict[str, str] = field(default_factory=dict)
    ttl_seconds: Optional[int] = None
    is_active: bool = True

    def touch(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = _utcnow()

    def is_expired(self) -> bool:
        """Check if session has expired based on TTL."""
        if self.ttl_seconds is None:
            return False
        elapsed = (_utcnow() - self.last_activity).total_seconds()
        return elapsed > self.ttl_seconds


@dataclass
class ConversationTurn:
    """
    Single conversation turn for detailed history tracking.

    Captures both user input and assistant response along with
    extracted intent and entities for context.
    """

    turn_id: int
    timestamp: datetime
    user_input: str
    assistant_response: str
    detected_intent: Optional[str] = None
    extracted_entities: Optional[dict[str, str]] = None
    confidence: Optional[float] = None
    component_id: Optional[str] = None
    duration_ms: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "turn_id": self.turn_id,
            "timestamp": self.timestamp.isoformat(),
            "user_input": self.user_input,
            "assistant_response": self.assistant_response,
            "detected_intent": self.detected_intent,
            "extracted_entities": self.extracted_entities,
            "confidence": self.confidence,
            "component_id": self.component_id,
            "duration_ms": self.duration_ms,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationTurn":
        """Create from dictionary representation."""
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = _utcnow()

        return cls(
            turn_id=data["turn_id"],
            timestamp=timestamp,
            user_input=data["user_input"],
            assistant_response=data["assistant_response"],
            detected_intent=data.get("detected_intent"),
            extracted_entities=data.get("extracted_entities"),
            confidence=data.get("confidence"),
            component_id=data.get("component_id"),
            duration_ms=data.get("duration_ms"),
        )


@dataclass
class ConversationHistory:
    """
    Conversation history with sliding window support.

    Maintains a windowed view of recent conversation turns
    with optional summarization of older turns.
    """

    session_id: str
    turns: list[ConversationTurn] = field(default_factory=list)
    max_turns: int = 20
    total_turns: int = 0
    summary: Optional[str] = None
    summary_updated_at: Optional[datetime] = None
    token_count: Optional[int] = None

    def add_turn(self, turn: ConversationTurn) -> None:
        """
        Add a turn, applying windowing if needed.

        If the number of turns exceeds max_turns, older turns
        are removed to maintain the window size.
        """
        self.turns.append(turn)
        self.total_turns += 1

        # Windowing: keep only last max_turns
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns :]

    def get_recent(self, n: int = 10) -> list[ConversationTurn]:
        """Get the N most recent turns."""
        return self.turns[-n:]

    def clear(self) -> None:
        """Clear all turns while preserving summary."""
        self.turns = []

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "session_id": self.session_id,
            "turns": [t.to_dict() for t in self.turns],
            "max_turns": self.max_turns,
            "total_turns": self.total_turns,
            "summary": self.summary,
            "summary_updated_at": (
                self.summary_updated_at.isoformat() if self.summary_updated_at else None
            ),
            "token_count": self.token_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationHistory":
        """Create from dictionary representation."""
        summary_updated_at = data.get("summary_updated_at")
        if isinstance(summary_updated_at, str):
            summary_updated_at = datetime.fromisoformat(summary_updated_at)

        return cls(
            session_id=data["session_id"],
            turns=[ConversationTurn.from_dict(t) for t in data.get("turns", [])],
            max_turns=data.get("max_turns", 20),
            total_turns=data.get("total_turns", 0),
            summary=data.get("summary"),
            summary_updated_at=summary_updated_at,
            token_count=data.get("token_count"),
        )


@dataclass
class ContextValue:
    """
    Type-safe context variable value.

    Supports multiple value types with type discrimination
    for safe serialization and deserialization.
    """

    value_type: ContextValueType
    string_value: Optional[str] = None
    number_value: Optional[float] = None
    boolean_value: Optional[bool] = None
    list_value: Optional[list[str]] = None
    object_value: Optional[dict[str, Any]] = None

    @classmethod
    def from_value(cls, value: Any) -> "ContextValue":
        """Create ContextValue from Python value with automatic type detection."""
        if value is None:
            return cls(value_type=ContextValueType.NULL)
        elif isinstance(value, bool):
            return cls(value_type=ContextValueType.BOOLEAN, boolean_value=value)
        elif isinstance(value, (int, float)):
            return cls(value_type=ContextValueType.NUMBER, number_value=float(value))
        elif isinstance(value, str):
            return cls(value_type=ContextValueType.STRING, string_value=value)
        elif isinstance(value, list):
            return cls(
                value_type=ContextValueType.LIST, list_value=[str(v) for v in value]
            )
        elif isinstance(value, dict):
            return cls(value_type=ContextValueType.OBJECT, object_value=value)
        else:
            return cls(value_type=ContextValueType.STRING, string_value=str(value))

    def to_value(self) -> Any:
        """Convert back to Python value."""
        if self.value_type == ContextValueType.NULL:
            return None
        elif self.value_type == ContextValueType.BOOLEAN:
            return self.boolean_value
        elif self.value_type == ContextValueType.NUMBER:
            return self.number_value
        elif self.value_type == ContextValueType.STRING:
            return self.string_value
        elif self.value_type == ContextValueType.LIST:
            return self.list_value
        elif self.value_type == ContextValueType.OBJECT:
            return self.object_value
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "value_type": self.value_type.value,
            "string_value": self.string_value,
            "number_value": self.number_value,
            "boolean_value": self.boolean_value,
            "list_value": self.list_value,
            "object_value": self.object_value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContextValue":
        """Create from dictionary representation."""
        value_type = data.get("value_type", "NULL")
        if isinstance(value_type, str):
            value_type = ContextValueType(value_type)
        return cls(
            value_type=value_type,
            string_value=data.get("string_value"),
            number_value=data.get("number_value"),
            boolean_value=data.get("boolean_value"),
            list_value=data.get("list_value"),
            object_value=data.get("object_value"),
        )


@dataclass
class ContextVariables:
    """
    Session-scoped context variables.

    Provides a type-safe key-value store for persistent
    context that spans conversation turns.
    """

    session_id: str
    variables: dict[str, ContextValue] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=_utcnow)

    def set(self, key: str, value: Any) -> None:
        """Set a variable value with automatic type detection."""
        self.variables[key] = ContextValue.from_value(value)
        self.updated_at = _utcnow()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a variable value, returning default if not found."""
        if key in self.variables:
            return self.variables[key].to_value()
        return default

    def delete(self, key: str) -> bool:
        """Delete a variable, returning True if it existed."""
        if key in self.variables:
            del self.variables[key]
            self.updated_at = _utcnow()
            return True
        return False

    def keys(self) -> list[str]:
        """Get all variable keys."""
        return list(self.variables.keys())

    def to_flat_dict(self) -> dict[str, Any]:
        """Convert to flat dictionary of values."""
        return {k: v.to_value() for k, v in self.variables.items()}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "session_id": self.session_id,
            "variables": {k: v.to_dict() for k, v in self.variables.items()},
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContextVariables":
        """Create from dictionary representation."""
        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        elif updated_at is None:
            updated_at = _utcnow()

        return cls(
            session_id=data["session_id"],
            variables={
                k: ContextValue.from_dict(v)
                for k, v in data.get("variables", {}).items()
            },
            updated_at=updated_at,
        )


@dataclass
class ExecutionContext:
    """
    Complete execution context for BAML functions.

    Combines session, history, and variables into a single
    context object that can be injected into BAML function calls.
    """

    session: SessionContext
    history: ConversationHistory
    variables: ContextVariables
    current_intent: Optional[str] = None
    current_entities: Optional[dict[str, str]] = None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for BAML function injection.

        Returns a flattened structure suitable for injection
        into BAML function parameters.
        """
        return {
            "session_id": self.session.session_id,
            "user_id": self.session.user_id,
            "recent_turns": [
                {
                    "user_input": t.user_input,
                    "assistant_response": t.assistant_response,
                    "detected_intent": t.detected_intent,
                    "extracted_entities": t.extracted_entities,
                }
                for t in self.history.get_recent(10)
            ],
            "variables": self.variables.to_flat_dict(),
            "history_summary": self.history.summary,
            "current_intent": self.current_intent,
            "current_entities": self.current_entities,
            "turn_count": self.history.total_turns,
        }

    def to_conversation_context(self) -> dict[str, Any]:
        """
        Convert to SessionConversationContext format for BAML injection.

        Matches the SessionConversationContext BAML type structure.
        """
        return {
            "session_id": self.session.session_id,
            "user_id": self.session.user_id,
            "recent_turns": [
                {
                    "user_input": t.user_input,
                    "assistant_response": t.assistant_response,
                    "detected_intent": t.detected_intent,
                    "extracted_entities": t.extracted_entities,
                }
                for t in self.history.get_recent(10)
            ],
            "variables": {
                k: str(v) if v is not None else None
                for k, v in self.variables.to_flat_dict().items()
            },
            "history_summary": self.history.summary,
            "turn_count": self.history.total_turns,
        }


@dataclass
class ContextConfig:
    """
    Configuration for context management.

    Controls history management, storage backend selection,
    and session lifecycle parameters.
    """

    max_history_turns: int = 20
    summarize_after: int = 10
    token_limit: int = 4000
    backend: ContextBackend = ContextBackend.IN_MEMORY
    ttl_seconds: Optional[int] = 3600  # 1 hour default
    redis_url: Optional[str] = None
    postgres_url: Optional[str] = None
    enable_summarization: bool = True
    summarization_model: Optional[str] = None


class ContextProvider(ABC):
    """
    Abstract base class for context storage providers.

    Implementations must provide session management, conversation
    history tracking, and context variable storage. Storage backends
    can range from in-memory (for development) to Redis/PostgreSQL
    (for production).

    Example implementation:
        class MyProvider(ContextProvider):
            async def create_session(self, session_id, user_id=None, metadata=None):
                # Store session in your backend
                ...
    """

    @abstractmethod
    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> SessionContext:
        """
        Create a new session.

        Args:
            session_id: Unique session identifier
            user_id: Optional user identifier for personalization
            metadata: Optional custom session metadata

        Returns:
            Created SessionContext
        """
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """
        Retrieve a session by ID.

        Args:
            session_id: Session identifier to retrieve

        Returns:
            SessionContext if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_session(self, session: SessionContext) -> None:
        """
        Update session data.

        Args:
            session: Session with updated data to persist
        """
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all associated data.

        Args:
            session_id: Session identifier to delete

        Returns:
            True if session existed and was deleted
        """
        pass

    @abstractmethod
    async def get_history(self, session_id: str) -> ConversationHistory:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier

        Returns:
            ConversationHistory (empty if session not found)
        """
        pass

    @abstractmethod
    async def add_turn(self, session_id: str, turn: ConversationTurn) -> None:
        """
        Add a conversation turn to history.

        Args:
            session_id: Session identifier
            turn: Conversation turn to add
        """
        pass

    @abstractmethod
    async def get_variables(self, session_id: str) -> ContextVariables:
        """
        Get context variables for a session.

        Args:
            session_id: Session identifier

        Returns:
            ContextVariables (empty if session not found)
        """
        pass

    @abstractmethod
    async def set_variable(self, session_id: str, key: str, value: Any) -> None:
        """
        Set a context variable.

        Args:
            session_id: Session identifier
            key: Variable key
            value: Variable value (any JSON-serializable type)
        """
        pass

    @abstractmethod
    async def delete_variable(self, session_id: str, key: str) -> bool:
        """
        Delete a context variable.

        Args:
            session_id: Session identifier
            key: Variable key to delete

        Returns:
            True if variable existed and was deleted
        """
        pass

    @abstractmethod
    async def get_execution_context(self, session_id: str) -> ExecutionContext:
        """
        Get complete execution context for a session.

        Creates session if it doesn't exist.

        Args:
            session_id: Session identifier

        Returns:
            Complete ExecutionContext with session, history, and variables
        """
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """
        Clean up expired sessions.

        Should be called periodically to remove sessions
        that have exceeded their TTL.

        Returns:
            Number of sessions deleted
        """
        pass

    async def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists.

        Args:
            session_id: Session identifier

        Returns:
            True if session exists
        """
        session = await self.get_session(session_id)
        return session is not None

    async def touch_session(self, session_id: str) -> bool:
        """
        Update session last activity timestamp.

        Args:
            session_id: Session identifier

        Returns:
            True if session exists and was updated
        """
        session = await self.get_session(session_id)
        if session:
            session.touch()
            await self.update_session(session)
            return True
        return False
