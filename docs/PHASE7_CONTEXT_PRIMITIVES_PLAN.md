# Phase 7: BAML Context Primitives Implementation Plan

## Overview

This document outlines the implementation plan for adding context primitives to BAML for session state management in Language User Interfaces (LUI). While BAML core changes would require upstream contributions, we can implement a comprehensive context management layer that provides similar benefits in our Python codebase.

## Research Findings Summary

### Context Management Patterns (LangChain, LlamaIndex, etc.)
- **Buffer Memory**: Store full conversation history up to token limit
- **Window Memory**: Keep last N turns for recent context
- **Summary Memory**: Compress old context into summaries
- **Entity Memory**: Track mentioned entities across turns
- **Knowledge Graph Memory**: Build relationship graphs from conversations

### Session State Management
- **Storage Backends**: Redis (hot), DynamoDB/PostgreSQL (cold), hybrid architectures
- **Lifecycle**: Creation, persistence, expiration (TTL), cleanup
- **Serialization**: JSON (standard), Protocol Buffers (3-6x faster), MessagePack (binary)
- **Distributed**: Sharding by session_id, sticky sessions vs distributed cache

### BAML Extension Approaches
- **Parameter-level `@context` attribute**: Mark parameters for auto-injection
- **Function-level `@@context` block**: Declare context dependencies
- **Ambient context with scope**: Client-level context providers

### Context Serialization
- **Compression**: LLMLingua achieves 20x compression with 1.5% accuracy loss
- **Truncation**: Token-based, turn-based, importance-based strategies
- **Summarization**: Recursive summarization for long conversations

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Application Layer                             │
├─────────────────────────────────────────────────────────────────────┤
│  ContextManager  │  SessionStore  │  HistoryManager  │  Serializer  │
├─────────────────────────────────────────────────────────────────────┤
│                      Context Provider Interface                       │
├─────────────────────────────────────────────────────────────────────┤
│  InMemory  │  Redis  │  PostgreSQL  │  DynamoDB  │  Hybrid          │
├─────────────────────────────────────────────────────────────────────┤
│                      BAML Function Integration                        │
│  - Context injection into function calls                              │
│  - Automatic history management                                       │
│  - Type-safe context validation                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 7.1: Context Type Definitions
Define comprehensive BAML types for context management.

### Phase 7.2: Context Provider Interface
Create pluggable context provider abstraction.

### Phase 7.3: Session Store Implementation
Implement multi-backend session storage.

### Phase 7.4: History Manager
Implement conversation history with truncation and summarization.

### Phase 7.5: Context Serialization
Efficient serialization with compression support.

### Phase 7.6: BAML Integration Layer
Wrapper functions that inject context automatically.

### Phase 7.7: Context Decorator System
Python decorators for clean context injection.

### Phase 7.8: Testing & Documentation
Comprehensive testing and usage documentation.

---

## Detailed Implementation

### Task 7.1: Context Type Definitions (3-4 hours)

**File**: `baml_src/context_primitives.baml`

```baml
// Session context for tracking conversation state
class SessionContext {
  session_id string @description("Unique session identifier")
  user_id string? @description("Optional user identifier")
  created_at string @description("ISO 8601 timestamp")
  last_activity string @description("Last interaction timestamp")
  metadata map<string, string>? @description("Custom session metadata")
}

// Conversation turn for history tracking
class ConversationTurn {
  turn_id int @description("Sequential turn number")
  timestamp string @description("ISO 8601 timestamp")
  user_input string @description("User's message")
  detected_intent string? @description("Extracted intent")
  extracted_entities map<string, string>? @description("Extracted entities")
  assistant_response string @description("System response")
  confidence float? @description("Intent confidence score")
}

// Conversation history with sliding window
class ConversationHistory {
  session_id string
  turns ConversationTurn[]
  max_turns int @description("Maximum turns to retain (default: 20)")
  total_turns int @description("Total turns including summarized")
  summary string? @description("Summary of older turns")
}

// Context variables that persist across turns
class ContextVariables {
  session_id string
  variables map<string, ContextValue>
  updated_at string
}

// Flexible context value with type tracking
class ContextValue {
  value_type ContextValueType
  string_value string?
  number_value float?
  boolean_value bool?
  list_value string[]?
  object_value map<string, string>?
}

enum ContextValueType {
  STRING
  NUMBER
  BOOLEAN
  LIST
  OBJECT
  NULL
}

// Full execution context combining all components
class ExecutionContext {
  session SessionContext
  history ConversationHistory
  variables ContextVariables
  current_intent string?
  current_entities map<string, string>?
}

// Context configuration
class ContextConfig {
  max_history_turns int @description("Maximum turns to keep (default: 20)")
  summarize_after int @description("Summarize after N turns (default: 10)")
  token_limit int @description("Maximum tokens for history (default: 4000)")
  persistence_backend ContextBackend @description("Storage backend type")
  ttl_seconds int? @description("Session TTL in seconds")
}

enum ContextBackend {
  IN_MEMORY
  REDIS
  POSTGRESQL
  DYNAMODB
  HYBRID
}

// Context-aware function result
class ContextualResult {
  result any
  context_updates ContextUpdate[]
  new_variables map<string, ContextValue>?
}

class ContextUpdate {
  update_type ContextUpdateType
  key string
  value ContextValue?
  reason string?
}

enum ContextUpdateType {
  SET_VARIABLE
  DELETE_VARIABLE
  UPDATE_ENTITY
  CLEAR_CONTEXT
}
```

**Deliverables**:
- Complete BAML type definitions for context primitives
- Support for session, history, and variables
- Flexible value types for different data shapes
- Configuration types for customization

---

### Task 7.2: Context Provider Interface (3-4 hours)

**File**: `src/context_primitives/provider.py`

```python
"""
Context Provider Interface

Defines the abstract interface for context storage backends,
enabling pluggable implementations (in-memory, Redis, PostgreSQL, etc.)
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ContextBackend(Enum):
    """Supported context storage backends."""
    IN_MEMORY = "in_memory"
    REDIS = "redis"
    POSTGRESQL = "postgresql"
    DYNAMODB = "dynamodb"
    HYBRID = "hybrid"


@dataclass
class SessionContext:
    """Session-level context information."""
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, str] = field(default_factory=dict)

    def touch(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()


@dataclass
class ConversationTurn:
    """Single conversation turn."""
    turn_id: int
    timestamp: datetime
    user_input: str
    assistant_response: str
    detected_intent: Optional[str] = None
    extracted_entities: Optional[Dict[str, str]] = None
    confidence: Optional[float] = None


@dataclass
class ConversationHistory:
    """Conversation history with windowing support."""
    session_id: str
    turns: List[ConversationTurn] = field(default_factory=list)
    max_turns: int = 20
    total_turns: int = 0
    summary: Optional[str] = None

    def add_turn(self, turn: ConversationTurn) -> None:
        """Add a turn, applying windowing if needed."""
        self.turns.append(turn)
        self.total_turns += 1

        # Windowing: keep only last max_turns
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]

    def get_recent(self, n: int = 10) -> List[ConversationTurn]:
        """Get the N most recent turns."""
        return self.turns[-n:]


@dataclass
class ContextValue:
    """Type-safe context variable value."""
    value_type: str  # STRING, NUMBER, BOOLEAN, LIST, OBJECT, NULL
    string_value: Optional[str] = None
    number_value: Optional[float] = None
    boolean_value: Optional[bool] = None
    list_value: Optional[List[str]] = None
    object_value: Optional[Dict[str, Any]] = None

    @classmethod
    def from_value(cls, value: Any) -> "ContextValue":
        """Create ContextValue from Python value."""
        if value is None:
            return cls(value_type="NULL")
        elif isinstance(value, bool):
            return cls(value_type="BOOLEAN", boolean_value=value)
        elif isinstance(value, (int, float)):
            return cls(value_type="NUMBER", number_value=float(value))
        elif isinstance(value, str):
            return cls(value_type="STRING", string_value=value)
        elif isinstance(value, list):
            return cls(value_type="LIST", list_value=[str(v) for v in value])
        elif isinstance(value, dict):
            return cls(value_type="OBJECT", object_value=value)
        else:
            return cls(value_type="STRING", string_value=str(value))

    def to_value(self) -> Any:
        """Convert back to Python value."""
        if self.value_type == "NULL":
            return None
        elif self.value_type == "BOOLEAN":
            return self.boolean_value
        elif self.value_type == "NUMBER":
            return self.number_value
        elif self.value_type == "STRING":
            return self.string_value
        elif self.value_type == "LIST":
            return self.list_value
        elif self.value_type == "OBJECT":
            return self.object_value
        return None


@dataclass
class ContextVariables:
    """Session-scoped context variables."""
    session_id: str
    variables: Dict[str, ContextValue] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def set(self, key: str, value: Any) -> None:
        """Set a variable value."""
        self.variables[key] = ContextValue.from_value(value)
        self.updated_at = datetime.utcnow()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a variable value."""
        if key in self.variables:
            return self.variables[key].to_value()
        return default

    def delete(self, key: str) -> bool:
        """Delete a variable."""
        if key in self.variables:
            del self.variables[key]
            self.updated_at = datetime.utcnow()
            return True
        return False


@dataclass
class ExecutionContext:
    """Complete execution context for BAML functions."""
    session: SessionContext
    history: ConversationHistory
    variables: ContextVariables
    current_intent: Optional[str] = None
    current_entities: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for BAML function injection."""
        return {
            "session_id": self.session.session_id,
            "user_id": self.session.user_id,
            "recent_turns": [
                {
                    "user": t.user_input,
                    "assistant": t.assistant_response,
                    "intent": t.detected_intent
                }
                for t in self.history.get_recent(10)
            ],
            "variables": {
                k: v.to_value()
                for k, v in self.variables.variables.items()
            },
            "history_summary": self.history.summary,
            "current_intent": self.current_intent,
            "current_entities": self.current_entities
        }


class ContextProvider(ABC):
    """Abstract base class for context storage providers."""

    @abstractmethod
    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> SessionContext:
        """Create a new session."""
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Retrieve a session by ID."""
        pass

    @abstractmethod
    async def update_session(self, session: SessionContext) -> None:
        """Update session data."""
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        pass

    @abstractmethod
    async def get_history(self, session_id: str) -> ConversationHistory:
        """Get conversation history for a session."""
        pass

    @abstractmethod
    async def add_turn(self, session_id: str, turn: ConversationTurn) -> None:
        """Add a conversation turn."""
        pass

    @abstractmethod
    async def get_variables(self, session_id: str) -> ContextVariables:
        """Get context variables for a session."""
        pass

    @abstractmethod
    async def set_variable(
        self,
        session_id: str,
        key: str,
        value: Any
    ) -> None:
        """Set a context variable."""
        pass

    @abstractmethod
    async def delete_variable(self, session_id: str, key: str) -> bool:
        """Delete a context variable."""
        pass

    @abstractmethod
    async def get_execution_context(self, session_id: str) -> ExecutionContext:
        """Get complete execution context for a session."""
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Clean up expired sessions. Returns count of deleted sessions."""
        pass


class ContextConfig:
    """Configuration for context management."""

    def __init__(
        self,
        max_history_turns: int = 20,
        summarize_after: int = 10,
        token_limit: int = 4000,
        backend: ContextBackend = ContextBackend.IN_MEMORY,
        ttl_seconds: Optional[int] = 3600,  # 1 hour default
        redis_url: Optional[str] = None,
        postgres_url: Optional[str] = None
    ):
        self.max_history_turns = max_history_turns
        self.summarize_after = summarize_after
        self.token_limit = token_limit
        self.backend = backend
        self.ttl_seconds = ttl_seconds
        self.redis_url = redis_url
        self.postgres_url = postgres_url
```

**Deliverables**:
- Abstract `ContextProvider` base class
- Data classes for session, history, variables
- Type-safe context value handling
- Configuration management

---

### Task 7.3: Session Store Implementations (5-6 hours)

**File**: `src/context_primitives/stores/`

Implement multiple storage backends:

#### In-Memory Store
```python
# src/context_primitives/stores/memory.py

class InMemoryContextProvider(ContextProvider):
    """In-memory context storage for development/testing."""

    def __init__(self, config: ContextConfig):
        self.config = config
        self._sessions: Dict[str, SessionContext] = {}
        self._histories: Dict[str, ConversationHistory] = {}
        self._variables: Dict[str, ContextVariables] = {}
        self._lock = asyncio.Lock()

    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> SessionContext:
        async with self._lock:
            session = SessionContext(
                session_id=session_id,
                user_id=user_id,
                metadata=metadata or {}
            )
            self._sessions[session_id] = session
            self._histories[session_id] = ConversationHistory(
                session_id=session_id,
                max_turns=self.config.max_history_turns
            )
            self._variables[session_id] = ContextVariables(session_id=session_id)
            return session

    async def get_session(self, session_id: str) -> Optional[SessionContext]:
        return self._sessions.get(session_id)

    async def get_execution_context(self, session_id: str) -> ExecutionContext:
        session = await self.get_session(session_id)
        if not session:
            session = await self.create_session(session_id)

        return ExecutionContext(
            session=session,
            history=self._histories.get(
                session_id,
                ConversationHistory(session_id=session_id)
            ),
            variables=self._variables.get(
                session_id,
                ContextVariables(session_id=session_id)
            )
        )

    # ... implement remaining methods
```

#### Redis Store
```python
# src/context_primitives/stores/redis.py

class RedisContextProvider(ContextProvider):
    """Redis-backed context storage for production."""

    def __init__(self, config: ContextConfig):
        self.config = config
        self.redis = None
        self._prefix = "lui:context:"

    async def connect(self):
        """Initialize Redis connection."""
        import aioredis
        self.redis = await aioredis.from_url(
            self.config.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    def _session_key(self, session_id: str) -> str:
        return f"{self._prefix}session:{session_id}"

    def _history_key(self, session_id: str) -> str:
        return f"{self._prefix}history:{session_id}"

    def _variables_key(self, session_id: str) -> str:
        return f"{self._prefix}vars:{session_id}"

    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> SessionContext:
        session = SessionContext(
            session_id=session_id,
            user_id=user_id,
            metadata=metadata or {}
        )

        # Store with TTL
        await self.redis.setex(
            self._session_key(session_id),
            self.config.ttl_seconds,
            json.dumps(asdict(session), default=str)
        )

        return session

    # ... implement remaining methods with Redis commands
```

#### PostgreSQL Store
```python
# src/context_primitives/stores/postgres.py

class PostgreSQLContextProvider(ContextProvider):
    """PostgreSQL-backed context storage for persistent history."""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS lui_sessions (
        session_id VARCHAR(255) PRIMARY KEY,
        user_id VARCHAR(255),
        created_at TIMESTAMP DEFAULT NOW(),
        last_activity TIMESTAMP DEFAULT NOW(),
        metadata JSONB DEFAULT '{}'
    );

    CREATE TABLE IF NOT EXISTS lui_conversation_turns (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(255) REFERENCES lui_sessions(session_id),
        turn_id INT NOT NULL,
        timestamp TIMESTAMP DEFAULT NOW(),
        user_input TEXT NOT NULL,
        assistant_response TEXT NOT NULL,
        detected_intent VARCHAR(255),
        extracted_entities JSONB,
        confidence FLOAT,
        INDEX idx_session_turn (session_id, turn_id)
    );

    CREATE TABLE IF NOT EXISTS lui_context_variables (
        session_id VARCHAR(255) REFERENCES lui_sessions(session_id),
        key VARCHAR(255) NOT NULL,
        value_type VARCHAR(50) NOT NULL,
        value JSONB NOT NULL,
        updated_at TIMESTAMP DEFAULT NOW(),
        PRIMARY KEY (session_id, key)
    );
    """

    # ... implement methods with asyncpg
```

#### Hybrid Store (Redis + PostgreSQL)
```python
# src/context_primitives/stores/hybrid.py

class HybridContextProvider(ContextProvider):
    """
    Hybrid storage: Redis for hot data, PostgreSQL for persistence.

    Architecture:
    - Redis: Current session, recent history, active variables
    - PostgreSQL: Full history archive, audit log
    """

    def __init__(self, config: ContextConfig):
        self.redis = RedisContextProvider(config)
        self.postgres = PostgreSQLContextProvider(config)

    async def get_execution_context(self, session_id: str) -> ExecutionContext:
        # Try Redis first (hot cache)
        context = await self.redis.get_execution_context(session_id)

        if not context:
            # Fall back to PostgreSQL
            context = await self.postgres.get_execution_context(session_id)
            if context:
                # Warm up Redis cache
                await self.redis.cache_context(context)

        return context

    async def add_turn(self, session_id: str, turn: ConversationTurn) -> None:
        # Write to both
        await asyncio.gather(
            self.redis.add_turn(session_id, turn),
            self.postgres.add_turn(session_id, turn)
        )
```

**Deliverables**:
- InMemoryContextProvider (development/testing)
- RedisContextProvider (production hot storage)
- PostgreSQLContextProvider (persistent storage)
- HybridContextProvider (Redis cache + PostgreSQL persistence)
- Factory function to create appropriate provider

---

### Task 7.4: History Manager (4-5 hours)

**File**: `src/context_primitives/history.py`

```python
"""
History Manager

Handles conversation history with:
- Sliding window (keep N recent turns)
- Summarization (compress older turns)
- Token-aware truncation
- Importance-based retention
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
import tiktoken


@dataclass
class HistoryConfig:
    """Configuration for history management."""
    max_turns: int = 20
    summarize_after: int = 10
    max_tokens: int = 4000
    model: str = "gpt-4"
    summarization_prompt: str = """
Summarize the following conversation turns into a brief paragraph
that captures the key context, decisions made, and current state:

{turns}

Summary:
"""


class HistoryManager:
    """
    Manages conversation history with intelligent truncation.
    """

    def __init__(self, config: HistoryConfig):
        self.config = config
        self._tokenizer = tiktoken.encoding_for_model(config.model)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self._tokenizer.encode(text))

    def count_turn_tokens(self, turn: ConversationTurn) -> int:
        """Count tokens in a conversation turn."""
        text = f"User: {turn.user_input}\nAssistant: {turn.assistant_response}"
        return self.count_tokens(text)

    def should_summarize(self, history: ConversationHistory) -> bool:
        """Check if history should be summarized."""
        return len(history.turns) > self.config.summarize_after

    async def summarize_turns(
        self,
        turns: List[ConversationTurn],
        existing_summary: Optional[str] = None
    ) -> str:
        """
        Summarize conversation turns using LLM.

        Uses recursive summarization if existing summary provided.
        """
        turns_text = "\n".join([
            f"Turn {t.turn_id}:\n"
            f"User: {t.user_input}\n"
            f"Assistant: {t.assistant_response}"
            for t in turns
        ])

        if existing_summary:
            prompt = f"""
Previous summary: {existing_summary}

New turns to incorporate:
{turns_text}

Updated summary (incorporate new information):
"""
        else:
            prompt = self.config.summarization_prompt.format(turns=turns_text)

        # Use BAML function for summarization
        from baml_client import b
        result = await b.SummarizeConversation(
            conversation_turns=turns_text,
            existing_summary=existing_summary
        )

        return result.summary

    def truncate_by_tokens(
        self,
        turns: List[ConversationTurn],
        max_tokens: int
    ) -> List[ConversationTurn]:
        """Keep as many recent turns as fit within token limit."""
        total_tokens = 0
        kept_turns = []

        # Work backwards from most recent
        for turn in reversed(turns):
            turn_tokens = self.count_turn_tokens(turn)
            if total_tokens + turn_tokens <= max_tokens:
                kept_turns.insert(0, turn)
                total_tokens += turn_tokens
            else:
                break

        return kept_turns

    def truncate_by_importance(
        self,
        turns: List[ConversationTurn],
        max_tokens: int,
        current_query: str
    ) -> List[ConversationTurn]:
        """
        Keep turns based on importance scoring.

        Importance factors:
        - Recency (more recent = higher)
        - Intent relevance to current query
        - Entity overlap with current context
        """
        # Always keep first turn (establishes context) and last N turns
        must_keep = [turns[0]] + turns[-3:] if len(turns) > 3 else turns
        must_keep_tokens = sum(self.count_turn_tokens(t) for t in must_keep)

        if must_keep_tokens >= max_tokens:
            return self.truncate_by_tokens(must_keep, max_tokens)

        # Score remaining turns
        remaining = turns[1:-3] if len(turns) > 3 else []
        remaining_budget = max_tokens - must_keep_tokens

        scored = []
        for i, turn in enumerate(remaining):
            score = self._score_turn_importance(
                turn,
                i / len(remaining),  # Recency factor (0-1)
                current_query
            )
            scored.append((turn, score))

        # Sort by importance and take highest scoring within budget
        scored.sort(key=lambda x: x[1], reverse=True)

        selected = []
        tokens_used = 0
        for turn, score in scored:
            turn_tokens = self.count_turn_tokens(turn)
            if tokens_used + turn_tokens <= remaining_budget:
                selected.append(turn)
                tokens_used += turn_tokens

        # Combine: first turn + selected + last turns, sorted by turn_id
        all_turns = must_keep[:1] + selected + must_keep[1:]
        all_turns.sort(key=lambda t: t.turn_id)

        return all_turns

    def _score_turn_importance(
        self,
        turn: ConversationTurn,
        recency: float,
        current_query: str
    ) -> float:
        """Score turn importance (0-1)."""
        score = 0.0

        # Recency factor (0.4 weight)
        score += recency * 0.4

        # Intent relevance (0.3 weight)
        if turn.detected_intent:
            # Simple keyword matching (could use embeddings)
            query_words = set(current_query.lower().split())
            intent_words = set(turn.detected_intent.lower().replace("-", " ").split())
            overlap = len(query_words & intent_words)
            if overlap > 0:
                score += min(overlap / len(query_words), 1.0) * 0.3

        # Entity presence (0.2 weight)
        if turn.extracted_entities:
            score += 0.2

        # Confidence factor (0.1 weight)
        if turn.confidence and turn.confidence > 0.8:
            score += 0.1

        return score

    async def process_history(
        self,
        history: ConversationHistory,
        current_query: Optional[str] = None
    ) -> Tuple[List[ConversationTurn], Optional[str]]:
        """
        Process history for optimal context window usage.

        Returns:
            Tuple of (processed turns, summary if created)
        """
        total_turns = len(history.turns)

        # No processing needed for small histories
        if total_turns <= self.config.summarize_after:
            return history.turns, history.summary

        # Split into old and recent
        split_point = total_turns - self.config.summarize_after
        old_turns = history.turns[:split_point]
        recent_turns = history.turns[split_point:]

        # Summarize old turns
        summary = await self.summarize_turns(old_turns, history.summary)

        # Token-aware truncation of recent turns
        summary_tokens = self.count_tokens(summary) if summary else 0
        remaining_budget = self.config.max_tokens - summary_tokens

        if current_query:
            processed_recent = self.truncate_by_importance(
                recent_turns,
                remaining_budget,
                current_query
            )
        else:
            processed_recent = self.truncate_by_tokens(
                recent_turns,
                remaining_budget
            )

        return processed_recent, summary


# BAML function for summarization
SUMMARIZATION_BAML = """
function SummarizeConversation(
  conversation_turns: string,
  existing_summary: string?
) -> ConversationSummary {
  client GPT4
  prompt #"
    {% if existing_summary %}
    Update this conversation summary with new information:
    Previous summary: {{ existing_summary }}

    New conversation turns:
    {{ conversation_turns }}

    Create an updated summary that:
    1. Preserves important context from the previous summary
    2. Incorporates key information from new turns
    3. Stays concise (2-3 sentences)
    {% else %}
    Summarize this conversation:
    {{ conversation_turns }}

    Create a summary that captures:
    1. The main topic/goal of the conversation
    2. Key decisions or information exchanged
    3. Current state or pending actions

    Keep it to 2-3 sentences.
    {% endif %}
  "#
}

class ConversationSummary {
  summary string @description("Concise summary of the conversation")
  key_entities string[]? @description("Important entities mentioned")
  current_state string? @description("Current conversation state")
}
"""
```

**Deliverables**:
- HistoryManager with sliding window support
- Token-aware truncation
- Importance-based retention
- LLM-powered summarization
- BAML function for summarization

---

### Task 7.5: Context Serialization (3-4 hours)

**File**: `src/context_primitives/serialization.py`

```python
"""
Context Serialization

Efficient serialization with multiple format support:
- JSON (standard, human-readable)
- MessagePack (binary, faster)
- Compressed (for large contexts)
"""

import json
import gzip
from abc import ABC, abstractmethod
from typing import Any, Dict
from dataclasses import asdict


class ContextSerializer(ABC):
    """Abstract serializer interface."""

    @abstractmethod
    def serialize(self, context: ExecutionContext) -> bytes:
        """Serialize context to bytes."""
        pass

    @abstractmethod
    def deserialize(self, data: bytes) -> ExecutionContext:
        """Deserialize bytes to context."""
        pass


class JSONSerializer(ContextSerializer):
    """Standard JSON serialization."""

    def serialize(self, context: ExecutionContext) -> bytes:
        data = self._to_serializable(context)
        return json.dumps(data, default=str).encode('utf-8')

    def deserialize(self, data: bytes) -> ExecutionContext:
        obj = json.loads(data.decode('utf-8'))
        return self._from_dict(obj)

    def _to_serializable(self, context: ExecutionContext) -> Dict[str, Any]:
        return {
            "session": asdict(context.session),
            "history": {
                "session_id": context.history.session_id,
                "turns": [asdict(t) for t in context.history.turns],
                "max_turns": context.history.max_turns,
                "total_turns": context.history.total_turns,
                "summary": context.history.summary
            },
            "variables": {
                "session_id": context.variables.session_id,
                "variables": {
                    k: asdict(v) for k, v in context.variables.variables.items()
                },
                "updated_at": str(context.variables.updated_at)
            },
            "current_intent": context.current_intent,
            "current_entities": context.current_entities
        }

    def _from_dict(self, data: Dict[str, Any]) -> ExecutionContext:
        # Reconstruct from dictionary
        session = SessionContext(**data["session"])

        turns = [
            ConversationTurn(**t) for t in data["history"]["turns"]
        ]
        history = ConversationHistory(
            session_id=data["history"]["session_id"],
            turns=turns,
            max_turns=data["history"]["max_turns"],
            total_turns=data["history"]["total_turns"],
            summary=data["history"]["summary"]
        )

        variables = ContextVariables(
            session_id=data["variables"]["session_id"],
            variables={
                k: ContextValue(**v)
                for k, v in data["variables"]["variables"].items()
            }
        )

        return ExecutionContext(
            session=session,
            history=history,
            variables=variables,
            current_intent=data.get("current_intent"),
            current_entities=data.get("current_entities")
        )


class MessagePackSerializer(ContextSerializer):
    """Binary MessagePack serialization (faster, smaller)."""

    def __init__(self):
        try:
            import msgpack
            self._msgpack = msgpack
        except ImportError:
            raise ImportError("msgpack required: pip install msgpack")

    def serialize(self, context: ExecutionContext) -> bytes:
        data = JSONSerializer()._to_serializable(context)
        return self._msgpack.packb(data, default=str)

    def deserialize(self, data: bytes) -> ExecutionContext:
        obj = self._msgpack.unpackb(data, raw=False)
        return JSONSerializer()._from_dict(obj)


class CompressedSerializer(ContextSerializer):
    """Gzip-compressed JSON for large contexts."""

    def __init__(self, base_serializer: ContextSerializer = None):
        self._base = base_serializer or JSONSerializer()
        self._compression_level = 6  # Balance speed/size

    def serialize(self, context: ExecutionContext) -> bytes:
        data = self._base.serialize(context)
        return gzip.compress(data, compresslevel=self._compression_level)

    def deserialize(self, data: bytes) -> ExecutionContext:
        decompressed = gzip.decompress(data)
        return self._base.deserialize(decompressed)


class SerializerFactory:
    """Factory for creating appropriate serializer."""

    @staticmethod
    def create(format: str = "json") -> ContextSerializer:
        if format == "json":
            return JSONSerializer()
        elif format == "msgpack":
            return MessagePackSerializer()
        elif format == "compressed":
            return CompressedSerializer()
        elif format == "msgpack_compressed":
            return CompressedSerializer(MessagePackSerializer())
        else:
            raise ValueError(f"Unknown format: {format}")
```

**Deliverables**:
- JSONSerializer for standard use
- MessagePackSerializer for performance
- CompressedSerializer for large contexts
- Factory pattern for format selection

---

### Task 7.6: BAML Integration Layer (4-5 hours)

**File**: `src/context_primitives/integration.py`

```python
"""
BAML Integration Layer

Provides context injection into BAML function calls without
modifying BAML core. Uses wrapper functions and middleware pattern.
"""

from typing import Callable, TypeVar, Any, Optional
from functools import wraps
import asyncio


T = TypeVar('T')


class ContextManager:
    """
    Central context manager that integrates with BAML functions.

    Usage:
        ctx_manager = ContextManager(provider)

        # Use context in BAML calls
        result = await ctx_manager.with_context(
            session_id="user_123",
            func=b.ExtractIntent,
            user_input="Create a task"
        )
    """

    def __init__(
        self,
        provider: ContextProvider,
        history_manager: Optional[HistoryManager] = None
    ):
        self.provider = provider
        self.history_manager = history_manager or HistoryManager(HistoryConfig())
        self._current_context: Optional[ExecutionContext] = None

    async def get_or_create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> ExecutionContext:
        """Get existing session or create new one."""
        context = await self.provider.get_execution_context(session_id)

        if not context.session:
            await self.provider.create_session(session_id, user_id)
            context = await self.provider.get_execution_context(session_id)

        return context

    async def with_context(
        self,
        session_id: str,
        func: Callable[..., T],
        **kwargs
    ) -> T:
        """
        Execute a BAML function with automatic context injection.

        Args:
            session_id: Session identifier
            func: BAML function to call
            **kwargs: Arguments for the function

        Returns:
            Function result with context updates applied
        """
        # Get context
        context = await self.get_or_create_session(session_id)
        context.session.touch()

        # Process history for optimal context
        if context.history.turns:
            current_query = kwargs.get("user_input", "")
            processed_turns, summary = await self.history_manager.process_history(
                context.history,
                current_query
            )
            context.history.turns = processed_turns
            if summary:
                context.history.summary = summary

        # Build context parameter
        conversation_context = self._build_conversation_context(context)

        # Inject context into kwargs if function accepts it
        if "conversation_context" in kwargs or self._function_accepts_context(func):
            kwargs["conversation_context"] = conversation_context

        # Execute function
        result = await func(**kwargs)

        # Update context with result
        await self._update_context_from_result(context, kwargs, result)

        return result

    def _build_conversation_context(
        self,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Build ConversationContext dict for BAML function."""
        return {
            "session_id": context.session.session_id,
            "recent_turns": [
                {
                    "user_input": t.user_input,
                    "assistant_response": t.assistant_response,
                    "detected_intent": t.detected_intent,
                    "extracted_entities": t.extracted_entities
                }
                for t in context.history.get_recent(10)
            ],
            "variables": {
                k: v.to_value()
                for k, v in context.variables.variables.items()
            },
            "history_summary": context.history.summary,
            "turn_count": context.history.total_turns
        }

    def _function_accepts_context(self, func: Callable) -> bool:
        """Check if function has conversation_context parameter."""
        import inspect
        sig = inspect.signature(func)
        return "conversation_context" in sig.parameters

    async def _update_context_from_result(
        self,
        context: ExecutionContext,
        inputs: Dict[str, Any],
        result: Any
    ) -> None:
        """Update context based on function result."""
        user_input = inputs.get("user_input", "")

        # Create new turn
        turn = ConversationTurn(
            turn_id=context.history.total_turns + 1,
            timestamp=datetime.utcnow(),
            user_input=user_input,
            assistant_response=getattr(result, 'response_text', str(result)),
            detected_intent=getattr(result, 'intent', None),
            extracted_entities=getattr(result, 'entities', None),
            confidence=getattr(result, 'confidence', None)
        )

        # Save turn
        await self.provider.add_turn(context.session.session_id, turn)

        # Update variables if result contains them
        if hasattr(result, 'context_updates'):
            for update in result.context_updates:
                if update.update_type == "SET_VARIABLE":
                    await self.provider.set_variable(
                        context.session.session_id,
                        update.key,
                        update.value.to_value()
                    )
                elif update.update_type == "DELETE_VARIABLE":
                    await self.provider.delete_variable(
                        context.session.session_id,
                        update.key
                    )

    async def record_interaction(
        self,
        session_id: str,
        user_input: str,
        assistant_response: str,
        intent: Optional[str] = None,
        entities: Optional[Dict[str, str]] = None,
        confidence: Optional[float] = None
    ) -> None:
        """
        Manually record an interaction (for non-BAML responses).
        """
        context = await self.get_or_create_session(session_id)

        turn = ConversationTurn(
            turn_id=context.history.total_turns + 1,
            timestamp=datetime.utcnow(),
            user_input=user_input,
            assistant_response=assistant_response,
            detected_intent=intent,
            extracted_entities=entities,
            confidence=confidence
        )

        await self.provider.add_turn(session_id, turn)

    async def set_variable(
        self,
        session_id: str,
        key: str,
        value: Any
    ) -> None:
        """Set a context variable."""
        await self.provider.set_variable(session_id, key, value)

    async def get_variable(
        self,
        session_id: str,
        key: str,
        default: Any = None
    ) -> Any:
        """Get a context variable."""
        variables = await self.provider.get_variables(session_id)
        return variables.get(key, default)

    async def clear_session(self, session_id: str) -> None:
        """Clear all context for a session."""
        await self.provider.delete_session(session_id)


# Context-aware BAML function wrappers
class ContextualBAML:
    """
    Wrapper for BAML client that provides automatic context management.

    Usage:
        from baml_client import b

        ctx_baml = ContextualBAML(b, context_manager)

        result = await ctx_baml.ExtractIntent(
            session_id="user_123",
            user_input="Create a task",
            interface_schema=schema
        )
    """

    def __init__(self, baml_client: Any, context_manager: ContextManager):
        self._baml = baml_client
        self._ctx = context_manager

    def __getattr__(self, name: str):
        """Wrap BAML functions with context management."""
        func = getattr(self._baml, name)

        @wraps(func)
        async def wrapper(session_id: str, **kwargs):
            return await self._ctx.with_context(
                session_id=session_id,
                func=func,
                **kwargs
            )

        return wrapper
```

**Deliverables**:
- ContextManager for centralized context handling
- Automatic context injection
- Context update from results
- ContextualBAML wrapper class
- Manual interaction recording

---

### Task 7.7: Context Decorator System (3-4 hours)

**File**: `src/context_primitives/decorators.py`

```python
"""
Context Decorator System

Python decorators for clean context injection into BAML functions.
Provides both sync and async decorators with configuration options.
"""

from typing import Callable, TypeVar, Optional, Any, Union
from functools import wraps
import asyncio
import contextvars


T = TypeVar('T')

# Context variable for current session
_current_session: contextvars.ContextVar[Optional[str]] = \
    contextvars.ContextVar('current_session', default=None)

# Global context manager (set during initialization)
_context_manager: Optional[ContextManager] = None


def init_context_system(
    provider: ContextProvider,
    history_config: Optional[HistoryConfig] = None
) -> ContextManager:
    """
    Initialize the global context system.

    Call once at application startup:
        init_context_system(InMemoryContextProvider(config))
    """
    global _context_manager
    _context_manager = ContextManager(
        provider=provider,
        history_manager=HistoryManager(history_config or HistoryConfig())
    )
    return _context_manager


def get_context_manager() -> ContextManager:
    """Get the global context manager."""
    if _context_manager is None:
        raise RuntimeError("Context system not initialized. Call init_context_system() first.")
    return _context_manager


def with_session(session_id: str):
    """
    Context manager for setting current session.

    Usage:
        async with with_session("user_123"):
            result = await extract_intent(user_input="hello")
    """
    class SessionContext:
        def __init__(self, session_id: str):
            self.session_id = session_id
            self._token = None

        async def __aenter__(self):
            self._token = _current_session.set(self.session_id)
            return self

        async def __aexit__(self, *args):
            _current_session.reset(self._token)

    return SessionContext(session_id)


def contextual(
    *,
    inject_history: bool = True,
    inject_variables: bool = True,
    record_interaction: bool = True,
    session_param: str = "session_id"
):
    """
    Decorator for BAML functions that need context injection.

    Args:
        inject_history: Include conversation history in context
        inject_variables: Include context variables
        record_interaction: Record this call as an interaction
        session_param: Name of session_id parameter (or use current session)

    Usage:
        @contextual()
        async def extract_intent(user_input: str, session_id: str = None):
            return await b.ExtractIntent(user_input=user_input)

        # With explicit session
        result = await extract_intent("hello", session_id="user_123")

        # Or with context manager
        async with with_session("user_123"):
            result = await extract_intent("hello")
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx = get_context_manager()

            # Get session ID from parameter or context variable
            session_id = kwargs.pop(session_param, None) or _current_session.get()
            if not session_id:
                raise ValueError(
                    f"No session_id provided. Either pass '{session_param}' "
                    "or use 'async with with_session(id):'"
                )

            # Get execution context
            exec_ctx = await ctx.get_or_create_session(session_id)

            # Build conversation context
            if inject_history or inject_variables:
                conv_context = {}

                if inject_history:
                    conv_context["recent_turns"] = [
                        {
                            "user_input": t.user_input,
                            "assistant_response": t.assistant_response,
                            "detected_intent": t.detected_intent
                        }
                        for t in exec_ctx.history.get_recent(10)
                    ]
                    conv_context["history_summary"] = exec_ctx.history.summary

                if inject_variables:
                    conv_context["variables"] = {
                        k: v.to_value()
                        for k, v in exec_ctx.variables.variables.items()
                    }

                kwargs["conversation_context"] = conv_context

            # Call the function
            result = await func(*args, **kwargs)

            # Record interaction if enabled
            if record_interaction:
                user_input = kwargs.get("user_input", str(args[0]) if args else "")
                await ctx.record_interaction(
                    session_id=session_id,
                    user_input=user_input,
                    assistant_response=getattr(result, 'response_text', str(result)),
                    intent=getattr(result, 'intent', None),
                    entities=getattr(result, 'entities', None),
                    confidence=getattr(result, 'confidence', None)
                )

            return result

        return wrapper
    return decorator


def contextual_variable(
    key: str,
    *,
    session_param: str = "session_id",
    create_if_missing: bool = True,
    default: Any = None
):
    """
    Decorator to inject a specific context variable as a parameter.

    Usage:
        @contextual_variable("current_task_id")
        async def update_task(task_id: str, new_data: dict, session_id: str = None):
            # task_id is automatically injected from context
            return await b.UpdateTask(task_id=task_id, data=new_data)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx = get_context_manager()

            session_id = kwargs.pop(session_param, None) or _current_session.get()
            if not session_id:
                raise ValueError(f"No session_id provided")

            # Get variable value
            value = await ctx.get_variable(session_id, key, default)

            if value is None and not create_if_missing:
                raise ValueError(f"Context variable '{key}' not found")

            # Inject as first positional argument
            args = (value,) + args

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def persist_result(
    *,
    variable_name: str,
    extractor: Callable[[Any], Any] = lambda x: x,
    session_param: str = "session_id"
):
    """
    Decorator to persist function result to context variable.

    Usage:
        @persist_result(variable_name="current_task_id", extractor=lambda r: r.task_id)
        async def create_task(name: str, session_id: str = None):
            return await b.CreateTask(name=name)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx = get_context_manager()

            session_id = kwargs.get(session_param) or _current_session.get()
            if not session_id:
                raise ValueError(f"No session_id provided")

            result = await func(*args, **kwargs)

            # Extract and persist value
            value = extractor(result)
            await ctx.set_variable(session_id, variable_name, value)

            return result

        return wrapper
    return decorator


# Convenience decorators
def with_history(func: Callable[..., T]) -> Callable[..., T]:
    """Shorthand for @contextual(inject_history=True, inject_variables=False)"""
    return contextual(inject_history=True, inject_variables=False)(func)


def with_variables(func: Callable[..., T]) -> Callable[..., T]:
    """Shorthand for @contextual(inject_history=False, inject_variables=True)"""
    return contextual(inject_history=False, inject_variables=True)(func)


def stateless(func: Callable[..., T]) -> Callable[..., T]:
    """Mark function as stateless (no context injection, still records)."""
    return contextual(inject_history=False, inject_variables=False)(func)
```

**Deliverables**:
- `@contextual` decorator for automatic context injection
- `@contextual_variable` for specific variable injection
- `@persist_result` for saving results to context
- `with_session()` context manager
- Session context variable support
- Convenience decorators

---

### Task 7.8: Testing & Documentation (4-5 hours)

**Tests**: `tests/test_context_primitives/`

```python
# tests/test_context_primitives/test_provider.py

import pytest
from src.context_primitives.provider import (
    InMemoryContextProvider, ContextConfig, SessionContext,
    ConversationTurn, ContextValue
)


@pytest.fixture
def config():
    return ContextConfig(max_history_turns=20, ttl_seconds=3600)


@pytest.fixture
async def provider(config):
    return InMemoryContextProvider(config)


class TestInMemoryProvider:
    @pytest.mark.asyncio
    async def test_create_session(self, provider):
        session = await provider.create_session("test_123", user_id="user_1")
        assert session.session_id == "test_123"
        assert session.user_id == "user_1"

    @pytest.mark.asyncio
    async def test_get_session(self, provider):
        await provider.create_session("test_123")
        session = await provider.get_session("test_123")
        assert session is not None
        assert session.session_id == "test_123"

    @pytest.mark.asyncio
    async def test_add_and_get_turns(self, provider):
        await provider.create_session("test_123")

        turn = ConversationTurn(
            turn_id=1,
            timestamp=datetime.utcnow(),
            user_input="Hello",
            assistant_response="Hi there!"
        )
        await provider.add_turn("test_123", turn)

        history = await provider.get_history("test_123")
        assert len(history.turns) == 1
        assert history.turns[0].user_input == "Hello"

    @pytest.mark.asyncio
    async def test_context_variables(self, provider):
        await provider.create_session("test_123")

        await provider.set_variable("test_123", "task_id", "task_456")
        variables = await provider.get_variables("test_123")

        assert variables.get("task_id") == "task_456"

    @pytest.mark.asyncio
    async def test_get_execution_context(self, provider):
        await provider.create_session("test_123", user_id="user_1")
        await provider.set_variable("test_123", "mode", "advanced")

        context = await provider.get_execution_context("test_123")

        assert context.session.session_id == "test_123"
        assert context.variables.get("mode") == "advanced"


# tests/test_context_primitives/test_history.py

class TestHistoryManager:
    @pytest.mark.asyncio
    async def test_token_truncation(self):
        manager = HistoryManager(HistoryConfig(max_tokens=100))

        turns = [
            ConversationTurn(i, datetime.utcnow(), f"User {i}", f"Response {i}")
            for i in range(10)
        ]

        truncated = manager.truncate_by_tokens(turns, 100)
        assert len(truncated) < len(turns)

    @pytest.mark.asyncio
    async def test_importance_truncation(self):
        manager = HistoryManager(HistoryConfig())

        turns = [
            ConversationTurn(
                i, datetime.utcnow(),
                f"Create task {i}", f"Task {i} created",
                detected_intent="create-task"
            )
            for i in range(20)
        ]

        truncated = manager.truncate_by_importance(
            turns, 1000, "create task"
        )

        # Should keep first and last turns
        assert truncated[0].turn_id == 0
        assert truncated[-1].turn_id == 19


# tests/test_context_primitives/test_decorators.py

class TestDecorators:
    @pytest.mark.asyncio
    async def test_contextual_decorator(self):
        init_context_system(InMemoryContextProvider(ContextConfig()))

        @contextual()
        async def test_func(user_input: str, conversation_context: dict = None):
            return {"input": user_input, "has_context": conversation_context is not None}

        result = await test_func("hello", session_id="test_123")
        assert result["has_context"] is True

    @pytest.mark.asyncio
    async def test_with_session_context_manager(self):
        init_context_system(InMemoryContextProvider(ContextConfig()))

        @contextual()
        async def test_func(user_input: str, conversation_context: dict = None):
            return {"input": user_input}

        async with with_session("test_456"):
            result = await test_func("hello")
            assert result["input"] == "hello"
```

**Documentation**: `docs/CONTEXT_PRIMITIVES_GUIDE.md`

```markdown
# Context Primitives User Guide

## Quick Start

```python
from src.context_primitives import (
    init_context_system, InMemoryContextProvider, ContextConfig,
    contextual, with_session
)

# Initialize at startup
config = ContextConfig(max_history_turns=20, ttl_seconds=3600)
init_context_system(InMemoryContextProvider(config))

# Use decorators for automatic context
@contextual()
async def chat(user_input: str, conversation_context: dict = None):
    return await b.ExtractIntent(
        user_input=user_input,
        conversation_context=conversation_context
    )

# Call with explicit session
result = await chat("Create a task", session_id="user_123")

# Or use context manager
async with with_session("user_123"):
    result = await chat("Create a task")
```

## Architecture

[Include architecture diagram]

## Configuration

[Document all configuration options]

## Storage Backends

[Document each backend with examples]

## Best Practices

[Include patterns and anti-patterns]
```

**Deliverables**:
- Unit tests for all components (90%+ coverage)
- Integration tests for full workflows
- User guide with examples
- API reference documentation
- Architecture documentation

---

## Implementation Summary

| Task | Description | Effort | Dependencies |
|------|-------------|--------|--------------|
| 7.1 | Context Type Definitions | 3-4h | None |
| 7.2 | Context Provider Interface | 3-4h | 7.1 |
| 7.3 | Session Store Implementations | 5-6h | 7.2 |
| 7.4 | History Manager | 4-5h | 7.1, 7.2 |
| 7.5 | Context Serialization | 3-4h | 7.1 |
| 7.6 | BAML Integration Layer | 4-5h | 7.2, 7.4 |
| 7.7 | Context Decorator System | 3-4h | 7.6 |
| 7.8 | Testing & Documentation | 4-5h | All |

**Total Estimated Effort: 30-37 hours**

## Success Criteria

- [ ] All context types defined in BAML
- [ ] Multiple storage backends implemented
- [ ] History management with summarization
- [ ] Clean decorator-based API
- [ ] 90%+ test coverage
- [ ] Comprehensive documentation
- [ ] Performance benchmarks documented

## Future Enhancements

1. **BAML Upstream Proposal**: Once stable, propose native `@context` attribute
2. **Distributed Sessions**: Multi-region session support
3. **Context Compression**: LLMLingua integration for token efficiency
4. **Context Analytics**: Track context usage patterns
5. **Vector Memory**: Semantic search over past conversations

## Related Issues

- Issue #29: Conversational Testing Framework (uses context)
- Issue #28: Intent Drift Detection (analyzes context)
- Issue #26: Session State Management (foundational)
