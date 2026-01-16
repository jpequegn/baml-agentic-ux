# Context Primitives API Reference

Complete API reference for the Context Primitives module - session state management for Language User Interfaces.

## Table of Contents

- [Core Types](#core-types)
- [Provider Interface](#provider-interface)
- [Storage Backends](#storage-backends)
- [History Manager](#history-manager)
- [Serialization](#serialization)
- [Integration Layer](#integration-layer)
- [Decorators](#decorators)

---

## Core Types

### ContextBackend (Enum)

Storage backend selector for context providers.

```python
from src.context_primitives import ContextBackend

class ContextBackend(Enum):
    MEMORY = "memory"      # In-memory storage (development)
    REDIS = "redis"        # Redis-backed storage (production)
    POSTGRES = "postgres"  # PostgreSQL-backed storage (persistence)
    HYBRID = "hybrid"      # Redis + PostgreSQL hybrid
```

### ContextValueType (Enum)

Type discriminator for context variable values.

```python
from src.context_primitives import ContextValueType

class ContextValueType(Enum):
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOLEAN = "BOOLEAN"
    LIST = "LIST"
    OBJECT = "OBJECT"
    NULL = "NULL"
```

### ContextConfig

Configuration for context providers.

```python
@dataclass
class ContextConfig:
    # Backend selection
    backend: ContextBackend = ContextBackend.MEMORY

    # Session settings
    max_history_turns: int = 20
    ttl_seconds: Optional[int] = 3600

    # Backend URLs
    redis_url: Optional[str] = None
    postgres_url: Optional[str] = None
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `backend` | `ContextBackend` | `MEMORY` | Storage backend to use |
| `max_history_turns` | `int` | `20` | Maximum conversation turns to retain |
| `ttl_seconds` | `int \| None` | `3600` | Session time-to-live in seconds |
| `redis_url` | `str \| None` | `None` | Redis connection URL |
| `postgres_url` | `str \| None` | `None` | PostgreSQL connection URL |

### SessionContext

Session metadata and state.

```python
@dataclass
class SessionContext:
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=_utcnow)
    last_activity: datetime = field(default_factory=_utcnow)
    metadata: dict[str, str] = field(default_factory=dict)
    ttl_seconds: Optional[int] = None
    is_active: bool = True
```

**Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `touch()` | `() -> None` | Update last_activity to current time |
| `is_expired()` | `() -> bool` | Check if session has expired |
| `to_dict()` | `() -> dict[str, Any]` | Serialize to dictionary |
| `from_dict()` | `(classmethod) (data: dict) -> SessionContext` | Create from dictionary |

### ConversationTurn

Single conversation turn data.

```python
@dataclass
class ConversationTurn:
    turn_id: int
    timestamp: datetime
    user_input: str
    assistant_response: str
    detected_intent: Optional[str] = None
    extracted_entities: Optional[dict[str, Any]] = None
    confidence: Optional[float] = None
    component_id: Optional[str] = None
    duration_ms: Optional[int] = None
```

**Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `to_dict()` | `() -> dict[str, Any]` | Serialize to dictionary |
| `from_dict()` | `(classmethod) (data: dict) -> ConversationTurn` | Create from dictionary |

### ConversationHistory

Collection of conversation turns with windowing.

```python
@dataclass
class ConversationHistory:
    session_id: str
    turns: list[ConversationTurn] = field(default_factory=list)
    max_turns: int = 20
    total_turns: int = 0
    summary: Optional[str] = None
    summary_updated_at: Optional[datetime] = None
    token_count: Optional[int] = None
```

**Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `add_turn()` | `(turn: ConversationTurn) -> None` | Add a turn (respects max_turns) |
| `get_recent()` | `(n: int) -> list[ConversationTurn]` | Get last N turns |
| `to_dict()` | `() -> dict[str, Any]` | Serialize to dictionary |
| `from_dict()` | `(classmethod) (data: dict) -> ConversationHistory` | Create from dictionary |

### ContextValue

Type-safe context variable value.

```python
@dataclass
class ContextValue:
    value_type: ContextValueType
    string_value: Optional[str] = None
    number_value: Optional[float] = None
    boolean_value: Optional[bool] = None
    list_value: Optional[list[Any]] = None
    object_value: Optional[dict[str, Any]] = None
```

**Class Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `from_value()` | `(value: Any) -> ContextValue` | Create from Python value |
| `to_value()` | `() -> Any` | Extract Python value |
| `from_dict()` | `(data: dict) -> ContextValue` | Create from dictionary |
| `to_dict()` | `() -> dict[str, Any]` | Serialize to dictionary |

### ContextVariables

Session-scoped context variables.

```python
@dataclass
class ContextVariables:
    session_id: str
    variables: dict[str, ContextValue] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=_utcnow)
```

**Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `get()` | `(key: str, default: Any = None) -> Any` | Get variable value |
| `set()` | `(key: str, value: Any) -> None` | Set variable value |
| `delete()` | `(key: str) -> bool` | Delete variable |
| `keys()` | `() -> list[str]` | Get all variable keys |
| `to_dict()` | `() -> dict[str, Any]` | Serialize to dictionary |
| `from_dict()` | `(classmethod) (data: dict) -> ContextVariables` | Create from dictionary |

### ExecutionContext

Complete execution context for BAML calls.

```python
@dataclass
class ExecutionContext:
    session: SessionContext
    history: ConversationHistory
    variables: ContextVariables
```

**Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `to_dict()` | `() -> dict[str, Any]` | Serialize to dictionary |

---

## Provider Interface

### ContextProvider (Abstract Base Class)

Abstract interface for context storage backends.

```python
class ContextProvider(ABC):
    """Base class for all context storage providers."""
```

**Abstract Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `create_session()` | `async (session_id: str, user_id: str?, metadata: dict?) -> SessionContext` | Create a new session |
| `get_session()` | `async (session_id: str) -> SessionContext?` | Retrieve a session |
| `update_session()` | `async (session: SessionContext) -> None` | Update session data |
| `delete_session()` | `async (session_id: str) -> bool` | Delete a session |
| `get_history()` | `async (session_id: str) -> ConversationHistory` | Get conversation history |
| `add_turn()` | `async (session_id: str, turn: ConversationTurn) -> None` | Add a conversation turn |
| `get_variables()` | `async (session_id: str) -> ContextVariables` | Get context variables |
| `set_variable()` | `async (session_id: str, key: str, value: Any) -> None` | Set a variable |
| `delete_variable()` | `async (session_id: str, key: str) -> bool` | Delete a variable |
| `get_execution_context()` | `async (session_id: str) -> ExecutionContext` | Get complete context |
| `cleanup_expired()` | `async () -> int` | Clean up expired sessions |

---

## Storage Backends

### InMemoryContextProvider

In-memory storage for development and testing.

```python
from src.context_primitives import InMemoryContextProvider, ContextConfig

config = ContextConfig(max_history_turns=20, ttl_seconds=3600)
provider = InMemoryContextProvider(config)
```

**Additional Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `list_sessions()` | `async () -> list[str]` | List all session IDs |

### RedisContextProvider

Redis-backed storage for production.

```python
from src.context_primitives.stores.redis import RedisContextProvider

config = ContextConfig(redis_url="redis://localhost:6379")
provider = RedisContextProvider(config)
await provider.connect()
```

**Additional Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `connect()` | `async () -> None` | Initialize Redis connection |
| `close()` | `async () -> None` | Close Redis connection |
| `extend_ttl()` | `async (session_id: str, additional_seconds: int) -> bool` | Extend session TTL |
| `get_session_ttl()` | `async (session_id: str) -> int?` | Get remaining TTL |

### PostgreSQLContextProvider

PostgreSQL-backed storage for persistence.

```python
from src.context_primitives.stores.postgres import PostgreSQLContextProvider

config = ContextConfig(postgres_url="postgresql://user:pass@localhost/db")
provider = PostgreSQLContextProvider(config)
await provider.connect()
await provider.create_tables()
```

**Additional Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `connect()` | `async () -> None` | Initialize connection pool |
| `close()` | `async () -> None` | Close connection pool |
| `create_tables()` | `async () -> None` | Create database tables |
| `get_full_history()` | `async (session_id: str, limit: int = 1000) -> list[ConversationTurn]` | Get full history (not windowed) |
| `search_sessions()` | `async (user_id: str?, since: datetime?, limit: int = 100) -> list[SessionContext]` | Search sessions |

### HybridContextProvider

Redis + PostgreSQL hybrid for optimal performance and persistence.

```python
from src.context_primitives.stores.hybrid import HybridContextProvider

config = ContextConfig(
    redis_url="redis://localhost:6379",
    postgres_url="postgresql://user:pass@localhost/db"
)
provider = HybridContextProvider(config)
await provider.connect()
```

**Additional Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `connect()` | `async () -> None` | Initialize both backends |
| `close()` | `async () -> None` | Close both backends |
| `get_full_history()` | `async (session_id: str, limit: int = 1000) -> list[ConversationTurn]` | Get full history from PostgreSQL |
| `search_sessions()` | `async (user_id: str?, since: datetime?, limit: int = 100) -> list[SessionContext]` | Search sessions in PostgreSQL |
| `sync_to_postgres()` | `async (session_id: str) -> bool` | Force sync Redis to PostgreSQL |
| `invalidate_cache()` | `async (session_id: str) -> bool` | Invalidate Redis cache |

### Factory Functions

```python
from src.context_primitives import create_provider, create_memory_provider

# Create provider from config
provider = await create_provider(config)

# Create in-memory provider (synchronous)
provider = create_memory_provider()
```

---

## History Manager

### TokenCounter (Abstract)

Abstract interface for token counting.

```python
class TokenCounter(ABC):
    @abstractmethod
    def count_tokens(self, text: str) -> int: ...

    @abstractmethod
    def count_turn_tokens(self, turn: ConversationTurn) -> int: ...
```

### TiktokenCounter

Token counter using tiktoken library.

```python
from src.context_primitives import TiktokenCounter

counter = TiktokenCounter(model="gpt-4")
tokens = counter.count_tokens("Hello, world!")
```

### SimpleTokenCounter

Simple word-based token estimation.

```python
from src.context_primitives import SimpleTokenCounter

counter = SimpleTokenCounter(chars_per_token=4)
tokens = counter.count_tokens("Hello, world!")
```

### TruncationStrategy (Enum)

Strategy for truncating conversation history.

```python
class TruncationStrategy(Enum):
    FIFO = "fifo"                    # Remove oldest first
    IMPORTANCE = "importance"         # Keep important turns
    SUMMARIZE = "summarize"           # Summarize old turns
    SLIDING_WINDOW = "sliding_window" # Fixed-size window
```

### TruncationConfig

Configuration for history truncation.

```python
@dataclass
class TruncationConfig:
    max_tokens: int = 4000
    max_turns: int = 20
    strategy: TruncationStrategy = TruncationStrategy.FIFO
    keep_first_n: int = 1
    keep_last_n: int = 3
    min_importance: float = 0.0
```

### HistoryManager

Manages conversation history with truncation and summarization.

```python
from src.context_primitives import HistoryManager, create_history_manager

manager = await create_history_manager(
    truncation_config=TruncationConfig(max_tokens=4000),
    summarizer=SimpleSummarizer()
)

result = await manager.truncate(history)
```

**Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `truncate()` | `async (history: ConversationHistory) -> TruncationResult` | Truncate history to fit limits |
| `score_importance()` | `(history: ConversationHistory) -> list[TurnImportance]` | Score turn importance |

### Summarizers

```python
from src.context_primitives import SimpleSummarizer, LLMSummarizer

# Simple rule-based summarizer
summarizer = SimpleSummarizer()

# LLM-based summarizer
summarizer = LLMSummarizer(
    model_name="gpt-4",
    max_summary_tokens=200
)
```

---

## Serialization

### SerializationFormat (Enum)

Available serialization formats.

```python
class SerializationFormat(Enum):
    JSON = "json"
    MSGPACK = "msgpack"
    COMPRESSED = "compressed"
```

### ContextSerializer (Abstract)

Abstract interface for context serialization.

```python
class ContextSerializer(ABC):
    @abstractmethod
    def serialize(self, context: ExecutionContext) -> bytes: ...

    @abstractmethod
    def deserialize(self, data: bytes) -> ExecutionContext: ...
```

### Concrete Serializers

```python
from src.context_primitives import (
    JSONSerializer,
    MessagePackSerializer,
    CompressedSerializer,
    create_serializer
)

# Create by format
serializer = create_serializer(SerializationFormat.JSON)

# Or directly
serializer = JSONSerializer()
serializer = MessagePackSerializer()
serializer = CompressedSerializer(base_serializer=JSONSerializer())

# Usage
data = serializer.serialize(context)
context = serializer.deserialize(data)
```

---

## Integration Layer

### ContextManager

High-level context management with automatic injection.

```python
from src.context_primitives import ContextManager, create_context_manager

manager = await create_context_manager(config)

# Create or get session
session = await manager.get_or_create_session("user_123")

# Add turn and get context
await manager.add_turn(session.session_id, turn)
context = await manager.get_context(session.session_id)
```

**Methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `get_or_create_session()` | `async (session_id: str, user_id: str?, metadata: dict?) -> SessionContext` | Get or create session |
| `get_context()` | `async (session_id: str) -> ExecutionContext` | Get execution context |
| `add_turn()` | `async (session_id: str, turn: ConversationTurn) -> None` | Add conversation turn |
| `set_variable()` | `async (session_id: str, key: str, value: Any) -> None` | Set context variable |
| `get_variable()` | `async (session_id: str, key: str) -> Any` | Get context variable |
| `close()` | `async () -> None` | Clean up resources |

### ContextualBAML

Wrapper for BAML functions with automatic context injection.

```python
from src.context_primitives import ContextualBAML

baml = ContextualBAML(manager)

# Call BAML function with context
result = await baml.call(
    "chat_function",
    session_id="user_123",
    user_input="Hello!"
)
```

### ContextualResult

Result type that includes context metadata.

```python
@dataclass
class ContextualResult[T]:
    value: T
    session_id: str
    turn_id: int
    context: ExecutionContext
    duration_ms: int
```

---

## Decorators

### Global Context System

Initialize the global context system for decorator-based usage.

```python
from src.context_primitives import (
    init_context_system,
    init_context_system_async,
    get_context_manager,
    get_current_session_id,
    set_current_session_id,
    session_scope
)

# Synchronous initialization
manager = init_context_system(provider=provider)

# Async initialization (creates provider)
manager = await init_context_system_async(config=config)

# Get current manager
manager = get_context_manager()

# Session ID via contextvars
set_current_session_id("user_123")
session_id = get_current_session_id()

# Session scope context manager
async with session_scope("user_123") as session_id:
    # All calls within this scope use this session
    result = await my_function()
```

### Core Decorators

#### @with_context

Basic decorator for context injection (explicit manager parameter).

```python
from src.context_primitives import with_context

@with_context(inject_history=True, inject_variables=True)
async def my_function(context: ExecutionContext, ...):
    ...
```

#### @contextual

Main decorator using global manager via contextvars.

```python
from src.context_primitives import contextual

@contextual(
    inject_history=True,
    inject_variables=True,
    record_interaction=False,
    format=ContextFormat.DICT
)
async def my_function(*, context: ExecutionContext, **kwargs):
    history = context.history
    variables = context.variables
    ...

# Usage with session_scope
async with session_scope("user_123"):
    result = await my_function(arg="value")
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `inject_history` | `bool` | `True` | Inject conversation history |
| `inject_variables` | `bool` | `True` | Inject context variables |
| `record_interaction` | `bool` | `False` | Automatically record turn |
| `format` | `ContextFormat` | `DICT` | Context format in function |
| `session_id_arg` | `str` | `"session_id"` | Argument name for session ID |

#### @persist_result

Decorator for persisting function results to context variables.

```python
from src.context_primitives import persist_result

@persist_result("last_analysis", extractor=lambda r: r.summary)
async def analyze_data(session_id: str, data: dict) -> AnalysisResult:
    ...
```

#### @with_session

Inject session context into function.

```python
from src.context_primitives import with_session

@with_session()
async def my_function(*, session: SessionContext, **kwargs):
    print(f"Session: {session.session_id}")
```

#### @record_turn

Automatically record interaction as conversation turn.

```python
from src.context_primitives import record_turn

@record_turn(input_arg="user_message", output_extractor=lambda r: r.response)
async def chat(session_id: str, user_message: str) -> ChatResponse:
    ...
```

#### @inject_variables

Inject specific context variables.

```python
from src.context_primitives import inject_variables

@inject_variables("user_preferences", "theme")
async def render_page(*, user_preferences: dict, theme: str, **kwargs):
    ...
```

#### @require_context

Validate that context meets requirements.

```python
from src.context_primitives import require_context

@require_context(
    min_history_turns=3,
    required_variables=["user_id", "preferences"]
)
async def process_request(session_id: str, ...):
    ...
```

#### @track_metrics

Track execution metrics (time, calls, errors).

```python
from src.context_primitives import track_metrics, get_metrics

@track_metrics(include_context_size=True)
async def my_function(...):
    ...

metrics = get_metrics("my_function")
```

### Convenience Decorators

```python
from src.context_primitives import (
    with_history,        # Inject history only
    with_variables_only, # Inject variables only
    stateless           # Marker for stateless functions
)

@with_history()
async def analyze_conversation(*, history: ConversationHistory, **kwargs):
    ...

@with_variables_only()
async def get_preferences(*, variables: ContextVariables, **kwargs):
    ...

@stateless
async def calculate(x: int, y: int) -> int:
    return x + y
```

### Class Decorator

```python
from src.context_primitives import contextual_class

@contextual_class(inject_history=True)
class ChatService:
    async def respond(self, user_input: str) -> str:
        # self.context is available
        history = self.context.history
        ...
```

### Decorator Composition

```python
from src.context_primitives import compose, create_contextual_decorator

# Compose multiple decorators
combined = compose(
    with_session(),
    inject_variables("user_prefs"),
    track_metrics()
)

@combined
async def my_function(...):
    ...

# Create reusable decorator
my_decorator = create_contextual_decorator(
    inject_history=True,
    required_variables=["api_key"]
)
```

### Metrics

```python
from src.context_primitives import DecoratorMetrics, get_metrics, clear_metrics

# Get metrics for a function
metrics: DecoratorMetrics = get_metrics("my_function")
print(f"Calls: {metrics.total_calls}")
print(f"Avg time: {metrics.average_duration_ms}ms")
print(f"Errors: {metrics.error_count}")

# Clear metrics
clear_metrics("my_function")
clear_metrics()  # Clear all
```

---

## Error Types

### ContextSystemNotInitializedError

Raised when using context decorators before initialization.

```python
from src.context_primitives import ContextSystemNotInitializedError

try:
    manager = get_context_manager()
except ContextSystemNotInitializedError:
    manager = await init_context_system_async(config)
```

---

## Type Definitions

### ContextFormat (Enum)

Format for injected context in decorated functions.

```python
class ContextFormat(Enum):
    DICT = "dict"       # Inject as dictionary
    OBJECT = "object"   # Inject as ExecutionContext
    STRING = "string"   # Inject as formatted string
```

---

## Usage Examples

### Basic Usage

```python
from src.context_primitives import (
    ContextConfig,
    InMemoryContextProvider,
    ConversationTurn,
)
from datetime import datetime, timezone

# Create provider
config = ContextConfig(max_history_turns=20)
provider = InMemoryContextProvider(config)

# Create session
session = await provider.create_session(
    session_id="user_123",
    user_id="user_123",
    metadata={"source": "web"}
)

# Add conversation turn
turn = ConversationTurn(
    turn_id=1,
    timestamp=datetime.now(timezone.utc),
    user_input="Hello!",
    assistant_response="Hi there!"
)
await provider.add_turn("user_123", turn)

# Get full context
context = await provider.get_execution_context("user_123")
```

### With Decorators

```python
from src.context_primitives import (
    init_context_system_async,
    session_scope,
    contextual,
    ContextConfig,
)

# Initialize global context
await init_context_system_async(config=ContextConfig())

@contextual(inject_history=True, inject_variables=True)
async def chat(user_input: str, *, context, **kwargs):
    history = context.history
    return f"You said: {user_input}"

# Use with session scope
async with session_scope("user_123"):
    response = await chat("Hello!")
```

### Production Setup

```python
from src.context_primitives import (
    ContextConfig,
    ContextBackend,
    create_provider,
)

config = ContextConfig(
    backend=ContextBackend.HYBRID,
    redis_url="redis://localhost:6379",
    postgres_url="postgresql://user:pass@localhost/db",
    max_history_turns=50,
    ttl_seconds=86400,  # 24 hours
)

provider = await create_provider(config)

# Use in application
try:
    context = await provider.get_execution_context("session_id")
finally:
    await provider.close()
```
