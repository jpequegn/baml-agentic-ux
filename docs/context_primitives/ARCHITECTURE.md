# Context Primitives Architecture

This document describes the architecture and design decisions behind the Context Primitives module.

## Overview

Context Primitives provides session state management for Language User Interfaces (LUI). It enables multi-turn conversations with persistent context, history tracking, and variable management across various storage backends.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Application Layer                            │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │  @contextual │  │ @with_session│  │@persist_result│ Decorators    │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
├─────────────────────────────────────────────────────────────────────┤
│                        Integration Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐     │
│  │  ContextManager  │  │  ContextualBAML  │  │  session_scope   │     │
│  │                  │  │                  │  │  (contextvars)   │     │
│  └─────────────────┘  └─────────────────┘  └──────────────────┘     │
├─────────────────────────────────────────────────────────────────────┤
│                         Core Services                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐     │
│  │ HistoryManager   │  │   Serializers    │  │  TokenCounters   │     │
│  │ - Truncation     │  │ - JSON           │  │  - Tiktoken      │     │
│  │ - Summarization  │  │ - MessagePack    │  │  - Simple        │     │
│  │ - Importance     │  │ - Compressed     │  │                  │     │
│  └─────────────────┘  └─────────────────┘  └──────────────────┘     │
├─────────────────────────────────────────────────────────────────────┤
│                        Provider Interface                            │
│                    ┌─────────────────────┐                          │
│                    │   ContextProvider   │ (Abstract)               │
│                    │   - create_session  │                          │
│                    │   - get_history     │                          │
│                    │   - set_variable    │                          │
│                    └─────────────────────┘                          │
├─────────────────────────────────────────────────────────────────────┤
│                        Storage Backends                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │   Memory    │  │    Redis    │  │  PostgreSQL │  │  Hybrid   │  │
│  │ (dev/test)  │  │ (cache)     │  │ (persist)   │  │ (R+PG)    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Core Design Principles

### 1. Separation of Concerns

The architecture separates concerns into distinct layers:

- **Storage Layer**: Handles data persistence with pluggable backends
- **Core Services**: Provides history management, serialization, and token counting
- **Integration Layer**: Offers high-level APIs and BAML integration
- **Decorator Layer**: Enables declarative context injection

### 2. Backend Agnosticism

All storage backends implement the `ContextProvider` abstract interface:

```python
class ContextProvider(ABC):
    @abstractmethod
    async def create_session(self, session_id: str, ...) -> SessionContext: ...

    @abstractmethod
    async def get_history(self, session_id: str) -> ConversationHistory: ...

    @abstractmethod
    async def set_variable(self, session_id: str, key: str, value: Any) -> None: ...
    # ... more methods
```

This allows applications to switch backends without changing application code.

### 3. Async-First Design

All I/O operations are asynchronous, enabling high concurrency:

```python
async def process_request(session_id: str):
    context = await provider.get_execution_context(session_id)
    # Process with full context
    await provider.add_turn(session_id, turn)
```

### 4. Type Safety

The module uses Python dataclasses with type hints for all data structures:

```python
@dataclass
class ConversationTurn:
    turn_id: int
    timestamp: datetime
    user_input: str
    assistant_response: str
    detected_intent: Optional[str] = None
    # ...
```

## Component Details

### Storage Backends

#### InMemoryContextProvider

- **Use Case**: Development, testing, single-process applications
- **Persistence**: None (data lost on restart)
- **Performance**: Fastest (no I/O)
- **Scalability**: Single process only

```python
# Data structure
sessions: dict[str, SessionContext]
histories: dict[str, ConversationHistory]
variables: dict[str, ContextVariables]
```

#### RedisContextProvider

- **Use Case**: Production caching, multi-process applications
- **Persistence**: Optional (with RDB/AOF)
- **Performance**: Very fast (in-memory with network)
- **Scalability**: Horizontal (Redis Cluster)

**Key Structure:**
```
lui:context:session:{session_id}  -> Session JSON
lui:context:history:{session_id}  -> History JSON
lui:context:vars:{session_id}     -> Variables JSON
```

**Features:**
- Automatic TTL-based expiration
- Key prefixing for namespace isolation
- TTL extension for active sessions

#### PostgreSQLContextProvider

- **Use Case**: Long-term persistence, analytics, audit logs
- **Persistence**: Full ACID compliance
- **Performance**: Good (optimized queries, connection pooling)
- **Scalability**: Vertical + read replicas

**Schema:**
```sql
CREATE TABLE lui_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    created_at TIMESTAMP,
    last_activity TIMESTAMP,
    metadata JSONB,
    ttl_seconds INTEGER,
    is_active BOOLEAN
);

CREATE TABLE lui_conversation_turns (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) REFERENCES lui_sessions,
    turn_id INTEGER,
    timestamp TIMESTAMP,
    user_input TEXT,
    assistant_response TEXT,
    detected_intent VARCHAR(255),
    extracted_entities JSONB
);

CREATE TABLE lui_context_variables (
    session_id VARCHAR(255) REFERENCES lui_sessions,
    key VARCHAR(255),
    value_type VARCHAR(50),
    value JSONB,
    PRIMARY KEY (session_id, key)
);
```

#### HybridContextProvider

- **Use Case**: Production systems requiring both speed and durability
- **Architecture**: Redis for hot data, PostgreSQL for cold storage

**Read Path:**
```
1. Check Redis (hot cache)
2. If miss, check PostgreSQL
3. If found in PostgreSQL, warm up Redis cache
4. Return data
```

**Write Path:**
```
1. Write to Redis immediately (for fast reads)
2. Write to PostgreSQL in parallel (for persistence)
```

### History Manager

The HistoryManager handles conversation history optimization:

#### Token Counting

Two implementations available:
- `TiktokenCounter`: Accurate OpenAI token counting
- `SimpleTokenCounter`: Fast estimation (chars_per_token ratio)

#### Truncation Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| FIFO | Remove oldest turns first | Simple, predictable |
| IMPORTANCE | Keep high-importance turns | Quality over quantity |
| SUMMARIZE | Summarize old turns | Maximum context |
| SLIDING_WINDOW | Fixed-size window | Consistent memory |

#### Importance Scoring

Turns are scored based on:
- Recency (newer = more important)
- Intent presence (detected intents boost score)
- Entity density (more entities = more important)
- Response length (longer responses indicate substance)
- Position (first/last turns often important)

### Serialization

Three serialization formats:

| Format | Size | Speed | Human Readable |
|--------|------|-------|----------------|
| JSON | Largest | Fast | Yes |
| MessagePack | Medium | Faster | No |
| Compressed | Smallest | Slower | No |

### Decorator System

The decorator system uses Python's `contextvars` for thread-safe session tracking:

```python
_current_manager: ContextVar[Optional[ContextManager]] = ContextVar("current_manager")
_current_session_id: ContextVar[Optional[str]] = ContextVar("current_session_id")
```

This enables session scope to work across async boundaries:

```python
async with session_scope("user_123"):
    # All nested calls have access to session context
    result = await decorated_function()
```

## Data Flow

### Request Processing

```
1. Request arrives with session_id
2. session_scope sets current session in contextvars
3. @contextual decorator intercepts function call
4. Context is fetched from ContextManager
5. Context is injected into function parameters
6. Function executes with full context
7. (Optional) Turn is recorded
8. Response returned
```

### Context Injection Flow

```
┌────────────────┐
│ @contextual    │
└───────┬────────┘
        │ get_current_session_id()
        ▼
┌────────────────┐
│ ContextManager │
└───────┬────────┘
        │ get_execution_context()
        ▼
┌────────────────┐
│ContextProvider │
└───────┬────────┘
        │ Parallel fetch
        ▼
┌─────────────────────────────────────┐
│ Session + History + Variables       │
└───────┬─────────────────────────────┘
        │ Combine into ExecutionContext
        ▼
┌────────────────┐
│ Inject into fn │
└────────────────┘
```

## Concurrency Model

### Thread Safety

- All providers are designed for concurrent access
- `contextvars` ensure session isolation across tasks
- Redis and PostgreSQL handle concurrent writes

### Connection Pooling

- PostgreSQL: asyncpg connection pool (min=2, max=10)
- Redis: Single connection with async operations

### Race Conditions

The system handles race conditions through:
- Optimistic concurrency for variables
- Append-only history (no conflicts)
- TTL-based expiration (no explicit locking)

## Error Handling

### Provider Errors

```python
try:
    context = await provider.get_execution_context(session_id)
except RuntimeError:
    # Provider not connected
    await provider.connect()
    context = await provider.get_execution_context(session_id)
```

### Decorator Errors

```python
try:
    get_context_manager()
except ContextSystemNotInitializedError:
    await init_context_system_async(config)
```

### Graceful Degradation

The HybridProvider handles backend failures:
- Redis failure: Falls back to PostgreSQL
- Cache warming failure: Silent (best-effort)
- PostgreSQL failure: Returns cached data if available

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**: Context is only fetched when needed
2. **Parallel Fetching**: Session, history, and variables fetched concurrently
3. **Connection Pooling**: Reuse database connections
4. **TTL-Based Cleanup**: Automatic expiration vs manual cleanup

### Benchmarks

Typical performance characteristics:

| Operation | InMemory | Redis | PostgreSQL | Hybrid |
|-----------|----------|-------|------------|--------|
| Create Session | <1ms | 2-5ms | 5-10ms | 5-10ms |
| Get Context | <1ms | 2-5ms | 10-20ms | 2-5ms |
| Add Turn | <1ms | 2-5ms | 5-10ms | 5-10ms |
| Set Variable | <1ms | 2-5ms | 5-10ms | 5-10ms |

## Extension Points

### Custom Providers

Implement the `ContextProvider` interface:

```python
class CustomProvider(ContextProvider):
    async def create_session(self, session_id: str, ...) -> SessionContext:
        # Custom implementation
        pass
```

### Custom Serializers

Implement the `ContextSerializer` interface:

```python
class CustomSerializer(ContextSerializer):
    def serialize(self, context: ExecutionContext) -> bytes:
        # Custom serialization
        pass

    def deserialize(self, data: bytes) -> ExecutionContext:
        # Custom deserialization
        pass
```

### Custom Token Counters

Implement the `TokenCounter` interface:

```python
class CustomTokenCounter(TokenCounter):
    def count_tokens(self, text: str) -> int:
        # Custom token counting
        pass
```

## Testing Strategy

### Unit Tests

- Mock-based tests for all providers
- No external dependencies required
- Fast execution (<1s for full suite)

### Integration Tests

- Real Redis and PostgreSQL instances
- Marked with `pytest.mark.integration`
- Skipped if infrastructure unavailable

### Coverage Target

- Overall: 90%+ code coverage
- Critical paths: 100% coverage
- Error handling: Comprehensive

## Security Considerations

### Data Protection

- Sessions tied to user IDs
- TTL-based automatic expiration
- Soft delete for audit compliance

### Input Validation

- Type-safe dataclasses
- Enum validation for value types
- SQL injection prevention (parameterized queries)

### Access Control

- Session ID required for all operations
- User ID validation at application layer
- Metadata storage for custom auth tokens

## Future Considerations

### Potential Enhancements

1. **Distributed Locking**: For strict consistency requirements
2. **Event Sourcing**: Full audit trail with replay capability
3. **Encryption**: At-rest encryption for sensitive data
4. **Sharding**: Horizontal scaling for very large deployments
5. **Compression**: Automatic compression for large histories

### Migration Path

The abstract `ContextProvider` interface ensures backward compatibility:
- New backends can be added without breaking existing code
- Configuration-driven backend selection
- Factory functions abstract initialization details
