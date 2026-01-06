# Context Primitives User Guide

This guide covers the BAML context primitives for session state management in Language User Interfaces (LUI). These types enable conversation history tracking, context variables, and multi-turn interactions with configurable storage backends.

## Quick Start

```python
from src.context_primitives.provider import (
    InMemoryContextProvider,
    ContextConfig,
    ConversationTurn,
)
from datetime import datetime, timezone

# Initialize provider
config = ContextConfig(max_history_turns=20, ttl_seconds=3600)
provider = InMemoryContextProvider(config)

# Create a session
async def main():
    session = await provider.create_session(
        session_id="user_123",
        user_id="alice",
        metadata={"channel": "web", "locale": "en-US"}
    )

    # Add a conversation turn
    turn = ConversationTurn(
        turn_id=1,
        timestamp=datetime.now(timezone.utc),
        user_input="Create a new task",
        assistant_response="I'll create a new task for you. What should it be called?",
        detected_intent="create-task",
        confidence=0.95
    )
    await provider.add_turn("user_123", turn)

    # Set context variables
    await provider.set_variable("user_123", "current_task_id", "task_456")

    # Get complete execution context
    context = await provider.get_execution_context("user_123")
    print(f"Session: {context.session.session_id}")
    print(f"Turns: {len(context.history.turns)}")
    print(f"Variables: {context.variables.variables}")
```

## Core Types

### SessionContext

Tracks session lifecycle and metadata:

```python
@dataclass
class SessionContext:
    session_id: str                    # Unique identifier
    user_id: Optional[str]             # User for personalization
    created_at: datetime               # Session creation time
    last_activity: datetime            # Last interaction time
    metadata: dict[str, str]           # Custom metadata
    ttl_seconds: Optional[int]         # Time-to-live
    is_active: bool                    # Session status
```

**Usage:**
```python
session = SessionContext(
    session_id="sess_abc123",
    user_id="user_456",
    ttl_seconds=3600,  # 1 hour
    metadata={"source": "mobile_app"}
)

# Update activity timestamp
session.touch()

# Check expiration
if session.is_expired():
    print("Session expired")
```

### ConversationTurn

Single turn in conversation history:

```python
@dataclass
class ConversationTurn:
    turn_id: int                       # Sequential turn number
    timestamp: datetime                # When turn occurred
    user_input: str                    # User's message
    assistant_response: str            # System response
    detected_intent: Optional[str]     # Extracted intent
    extracted_entities: Optional[dict] # Extracted entities
    confidence: Optional[float]        # Intent confidence (0-1)
    component_id: Optional[str]        # LUI component ID
    duration_ms: Optional[int]         # Processing time
```

**Usage:**
```python
from datetime import datetime, timezone

turn = ConversationTurn(
    turn_id=1,
    timestamp=datetime.now(timezone.utc),
    user_input="Schedule a meeting with Bob tomorrow at 3pm",
    assistant_response="I've scheduled a meeting with Bob for tomorrow at 3:00 PM.",
    detected_intent="schedule-meeting",
    extracted_entities={
        "attendee": "Bob",
        "date": "tomorrow",
        "time": "3pm"
    },
    confidence=0.92
)

# Serialize for storage
turn_dict = turn.to_dict()

# Deserialize
restored = ConversationTurn.from_dict(turn_dict)
```

### ConversationHistory

Windowed history with summarization support:

```python
@dataclass
class ConversationHistory:
    session_id: str                    # Associated session
    turns: list[ConversationTurn]      # Recent turns (windowed)
    max_turns: int = 20                # Window size
    total_turns: int                   # Total including summarized
    summary: Optional[str]             # Summary of older turns
    summary_updated_at: Optional[datetime]
    token_count: Optional[int]         # Estimated tokens
```

**Usage:**
```python
history = ConversationHistory(session_id="sess_123", max_turns=10)

# Add turns (automatic windowing)
for i in range(15):
    turn = ConversationTurn(
        turn_id=i+1,
        timestamp=datetime.now(timezone.utc),
        user_input=f"Question {i+1}",
        assistant_response=f"Answer {i+1}"
    )
    history.add_turn(turn)

# Only last 10 turns retained
assert len(history.turns) == 10
assert history.total_turns == 15

# Get recent turns
recent = history.get_recent(5)  # Last 5 turns
```

### ContextValue

Type-safe variable values:

```python
@dataclass
class ContextValue:
    value_type: ContextValueType       # STRING, NUMBER, BOOLEAN, etc.
    string_value: Optional[str]
    number_value: Optional[float]
    boolean_value: Optional[bool]
    list_value: Optional[list[str]]
    object_value: Optional[dict]
```

**Usage:**
```python
# Create from Python values
str_val = ContextValue.from_value("hello")        # STRING
num_val = ContextValue.from_value(42)             # NUMBER
bool_val = ContextValue.from_value(True)          # BOOLEAN
list_val = ContextValue.from_value(["a", "b"])    # LIST
obj_val = ContextValue.from_value({"key": "val"}) # OBJECT
null_val = ContextValue.from_value(None)          # NULL

# Convert back to Python
assert str_val.to_value() == "hello"
assert num_val.to_value() == 42.0
```

### ContextVariables

Session-scoped persistent variables:

```python
@dataclass
class ContextVariables:
    session_id: str
    variables: dict[str, ContextValue]
    updated_at: datetime
```

**Usage:**
```python
variables = ContextVariables(session_id="sess_123")

# Set variables
variables.set("current_task_id", "task_456")
variables.set("user_preference", {"theme": "dark"})
variables.set("retry_count", 3)

# Get variables
task_id = variables.get("current_task_id")       # "task_456"
missing = variables.get("unknown", "default")    # "default"

# Delete variable
variables.delete("retry_count")

# List all keys
keys = variables.keys()  # ["current_task_id", "user_preference"]

# Flatten to string dict
flat = variables.to_flat_dict()  # All values as strings
```

### ExecutionContext

Complete context for BAML function injection:

```python
@dataclass
class ExecutionContext:
    session: SessionContext
    history: ConversationHistory
    variables: ContextVariables
    current_intent: Optional[str]
    current_entities: Optional[dict]
```

**Usage:**
```python
context = await provider.get_execution_context("sess_123")

# Convert to conversation context for BAML
conv_context = context.to_conversation_context()
# Returns:
# {
#     "session_id": "sess_123",
#     "user_id": "alice",
#     "recent_turns": [...],
#     "variables": {...},
#     "history_summary": "...",
#     "turn_count": 5
# }
```

## Storage Backends

### InMemoryContextProvider

For development and testing:

```python
from src.context_primitives.provider import InMemoryContextProvider, ContextConfig

config = ContextConfig(
    max_history_turns=20,
    ttl_seconds=3600  # 1 hour
)
provider = InMemoryContextProvider(config)

# Basic operations
session = await provider.create_session("sess_123")
await provider.add_turn("sess_123", turn)
await provider.set_variable("sess_123", "key", "value")
context = await provider.get_execution_context("sess_123")

# Session management
exists = await provider.session_exists("sess_123")  # True
await provider.touch_session("sess_123")            # Update activity
await provider.delete_session("sess_123")           # Remove session

# Bulk operations
count = provider.session_count()
await provider.clear_all()
```

### ContextBackend Options

```python
from src.context_primitives.provider import ContextBackend

class ContextBackend(Enum):
    IN_MEMORY = "in_memory"    # Development/testing only
    REDIS = "redis"            # Hot session storage with TTL
    POSTGRESQL = "postgresql"  # Persistent history storage
    DYNAMODB = "dynamodb"      # Serverless deployments
    HYBRID = "hybrid"          # Redis + PostgreSQL combination
```

## BAML Integration

### BAML Type Definitions

The context primitives are defined in `baml_src/context_primitives.baml`:

```baml
// Session context
class SessionContext {
  session_id string @description("Unique session identifier")
  user_id string? @description("Optional user identifier")
  created_at string @description("ISO 8601 timestamp")
  last_activity string @description("Last interaction timestamp")
  metadata map<string, string>?
  ttl_seconds int?
  is_active bool
}

// Conversation history
class ContextConversationHistory {
  session_id string
  turns ContextConversationTurn[]
  max_turns int
  total_turns int
  summary string?
  token_count int?
}

// Full execution context
class FullExecutionContext {
  session SessionContext
  history ContextConversationHistory
  variables ContextVariables
  current_intent string?
  current_entities map<string, string>?
}
```

### Using Context in BAML Functions

```baml
function ProcessUserInput(
  user_input: string,
  conversation_context: SessionConversationContext?
) -> IntentResult {
  client CustomSonnet4
  prompt #"
    {% if conversation_context %}
    CONVERSATION CONTEXT:
    Session: {{ conversation_context.session_id }}
    Previous turns: {{ conversation_context.turn_count }}

    {% if conversation_context.history_summary %}
    Summary: {{ conversation_context.history_summary }}
    {% endif %}

    Recent conversation:
    {% for turn in conversation_context.recent_turns %}
    User: {{ turn.user_input }}
    Assistant: {{ turn.assistant_response }}
    {% endfor %}

    Context variables:
    {{ conversation_context.variables }}
    {% endif %}

    USER INPUT: {{ user_input }}

    Extract the user's intent and any relevant entities.
    {{ ctx.output_format }}
  "#
}
```

### Summarization Functions

```baml
// Summarize conversation for context window management
function SummarizeConversation(
  turns: ContextConversationTurn[],
  existing_summary: string?,
  max_length: int?
) -> ConversationSummary {
  client CustomSonnet4
  prompt #"
    Create a concise summary of the conversation turns...
  "#
}

// Score turns for importance-based retention
function ScoreTurnImportance(
  turns: ContextConversationTurn[],
  current_context: string?,
  important_entities: string[]?
) -> TurnImportance[] {
  client CustomSonnet4
  prompt #"
    Evaluate conversation turns for importance...
  "#
}
```

## Python Dataclass Serialization

All types support serialization to/from Python dataclasses:

```python
from dataclasses import asdict

# To dictionary
session_dict = asdict(session)
turn_dict = turn.to_dict()
history_dict = history.to_dict()

# From dictionary
session = SessionContext(**session_dict)
turn = ConversationTurn.from_dict(turn_dict)
history = ConversationHistory.from_dict(history_dict)

# JSON serialization
import json

json_str = json.dumps(turn.to_dict(), default=str)
restored = ConversationTurn.from_dict(json.loads(json_str))
```

## Configuration

### ContextConfig

```python
@dataclass
class ContextConfig:
    max_history_turns: int = 20        # Window size
    summarize_after: int = 10          # When to summarize
    token_limit: int = 4000            # Max context tokens
    backend: ContextBackend = ContextBackend.IN_MEMORY
    ttl_seconds: Optional[int] = 3600  # Session TTL
```

### BAML Configuration Types

```baml
enum HistoryTruncationStrategy {
  SLIDING_WINDOW     // Keep last N turns
  TOKEN_BASED        // Keep until token limit
  IMPORTANCE_BASED   // Score and keep important
  SUMMARIZE          // Summarize before discard
  HYBRID             // Combine strategies
}

class TruncationConfig {
  strategy HistoryTruncationStrategy
  max_turns int
  max_tokens int
  importance_threshold float
  summarization_prompt string?
}
```

## Integration Layer

The integration layer provides high-level abstractions for using context primitives with BAML functions.

### ContextManager

Central manager for session lifecycle and context operations:

```python
from src.context_primitives import ContextManager, ContextConfig

# Create manager
config = ContextConfig(max_history_turns=20, ttl_seconds=3600)
manager = await ContextManager.create(config)

# Session operations
session = await manager.get_or_create_session("user_123")
context = await manager.get_context("user_123")

# Record a conversation turn
await manager.record_turn(
    session_id="user_123",
    user_input="Hello",
    response="Hi there!"
)
```

### ContextualBAML

Wrapper for BAML client with automatic context injection:

```python
from src.context_primitives import ContextualBAML

# Wrap your BAML client
baml = ContextualBAML(baml_client, manager)

# Call with automatic context
result = await baml.call_with_context(
    "ExtractIntent",
    session_id="user_123",
    user_input="Schedule a meeting"
)

# Access result and context
print(result.result)  # BAML function result
print(result.context)  # ExecutionContext used
```

### ContextualResult

Wrapper for BAML results with execution context:

```python
from src.context_primitives import ContextualResult

# Result includes both BAML output and context
result: ContextualResult = await baml.call_with_context(...)

# Access the BAML result
intent = result.result.intent

# Access the context used
session_id = result.context.session.session_id
turn_count = len(result.context.history.turns)
```

## Decorators

The decorator system provides flexible ways to inject context into functions.

### Basic Context Injection

```python
from src.context_primitives import with_context_enhanced, ContextFormat

@with_context_enhanced(
    manager,
    context_format=ContextFormat.CONVERSATION,  # FULL, CONVERSATION, MINIMAL, VARIABLES_ONLY
    create_session=True
)
async def process_input(session_id: str, user_input: str, context=None):
    # context is automatically injected
    print(f"Session: {context['session_id']}")
    print(f"Turn count: {context['turn_count']}")
    return f"Processed: {user_input}"
```

### Session Management

```python
from src.context_primitives import with_session

@with_session(manager, touch_on_access=True)
async def handle_request(session_id: str, user_id: str = None):
    # Session is automatically created if needed
    # Activity timestamp is updated
    return "Request handled"
```

### Turn Recording

```python
from src.context_primitives import record_turn

@record_turn(
    manager,
    user_input_param="user_input",
    response_extractor=lambda r: r["message"],
    component_id="chat_handler"
)
async def chat(session_id: str, user_input: str):
    response = {"message": f"Reply to: {user_input}"}
    # Turn is automatically recorded with timing
    return response
```

### Variable Injection

```python
from src.context_primitives import inject_variables

@inject_variables(
    manager,
    keys=["user_preference", "current_task"],
    defaults={"user_preference": "default"}
)
async def get_preferences(session_id: str, variables=None):
    # variables contains requested context variables
    return variables.get("user_preference")
```

### Context Validation

```python
from src.context_primitives import require_context

@require_context(
    manager,
    require_history=True,
    min_turns=3,
    required_variables=["user_id"]
)
async def continue_conversation(session_id: str):
    # Raises ValueError if requirements not met
    return "Continuing..."
```

### Metrics Tracking

```python
from src.context_primitives import track_metrics, get_metrics, clear_metrics

@track_metrics(store_metrics=True, on_complete=lambda m: print(f"Duration: {m.duration_ms}ms"))
async def timed_operation(session_id: str):
    # Execution time and success/failure tracked
    return "Done"

# Retrieve collected metrics
metrics = get_metrics()
for m in metrics:
    print(f"{m.function_name}: {m.duration_ms}ms, success={m.success}")
```

### Class Decorator

```python
from src.context_primitives import contextual_class

@contextual_class(manager, method_prefix="handle_", exclude_methods=["internal"])
class ChatHandler:
    async def handle_message(self, session_id: str, text: str, context=None):
        # context automatically injected for handle_* methods
        return f"Handled: {text}"

    async def internal(self, data):
        # This method is not decorated
        pass
```

### Context Scope

```python
from src.context_primitives import context_scope

async def process_conversation(session_id: str):
    async with context_scope(manager, session_id, user_id="alice") as ctx:
        # Session is active within this scope
        print(f"Session: {ctx.session.session_id}")
        # Do work...
    # Session remains active after scope (unless cleanup_on_exit=True)
```

### Decorator Composition

```python
from src.context_primitives import compose, create_contextual_decorator

# Compose multiple decorators
combined = compose(
    with_session(manager),
    record_turn(manager, user_input_param="text"),
    track_metrics()
)

@combined
async def full_handler(session_id: str, text: str):
    return f"Handled: {text}"

# Or create a custom decorator
custom = create_contextual_decorator(
    manager,
    inject_context=True,
    record_turns=True,
    track=True,
    context_format=ContextFormat.CONVERSATION
)

@custom
async def custom_handler(session_id: str, user_input: str, context=None):
    return "Custom handling"
```

## Serialization

The serialization module provides efficient context serialization with multiple format support.

### JSON Serialization

```python
from src.context_primitives import JSONSerializer, create_serializer

# Create serializer
serializer = JSONSerializer(indent=2)  # Pretty print
# Or compact
serializer = JSONSerializer()

# Serialize context
context = await manager.get_context("user_123")
data = serializer.serialize(context)

# Deserialize
restored = serializer.deserialize(data)
```

### MessagePack Serialization

3-6x faster than JSON, ~30% smaller:

```python
from src.context_primitives import MessagePackSerializer

# Requires: pip install msgpack
serializer = MessagePackSerializer()

data = serializer.serialize(context)  # Binary format
restored = serializer.deserialize(data)
```

### Compressed Serialization

50-70% size reduction with gzip:

```python
from src.context_primitives import CompressedSerializer, JSONSerializer

# Compressed JSON
inner = JSONSerializer()
serializer = CompressedSerializer(inner, compression_level=6)

data = serializer.serialize(context)  # Gzip compressed
restored = serializer.deserialize(data)
```

### Serializer Factory

```python
from src.context_primitives import SerializationFormat, create_serializer, SerializerFactory

# Using factory function
serializer = create_serializer(SerializationFormat.JSON)
serializer = create_serializer(SerializationFormat.COMPRESSED_JSON)
serializer = create_serializer(SerializationFormat.MSGPACK)

# Using factory class with caching
factory = SerializerFactory()
json_ser = factory.get(SerializationFormat.JSON)  # Cached
another = factory.get(SerializationFormat.JSON)   # Same instance

# Check available formats
formats = SerializerFactory.available_formats()
```

## History Manager

Advanced history management with truncation, summarization, and importance scoring.

### Token Counting

```python
from src.context_primitives import TiktokenCounter, SimpleTokenCounter

# Accurate token counting (requires tiktoken)
counter = TiktokenCounter(model="gpt-4")
tokens = counter.count("Hello, world!")

# Simple estimation (no dependencies)
counter = SimpleTokenCounter()
tokens = counter.count("Hello, world!")
```

### Truncation Strategies

```python
from src.context_primitives import (
    HistoryManager,
    TruncationStrategy,
    TruncationConfig,
    create_history_manager
)

# Create manager with truncation config
config = TruncationConfig(
    strategy=TruncationStrategy.SLIDING_WINDOW,
    max_turns=20,
    max_tokens=4000
)

history_manager = create_history_manager(
    truncation_config=config,
    token_counter=SimpleTokenCounter()
)

# Truncate history
result = await history_manager.truncate(history)
print(f"Kept {len(result.turns)} turns, removed {result.removed_count}")
```

### Importance Scoring

```python
from src.context_primitives import ImportanceScorer, ImportanceWeights

weights = ImportanceWeights(
    recency_weight=0.3,
    intent_weight=0.25,
    entity_weight=0.25,
    confidence_weight=0.2
)

scorer = ImportanceScorer(weights)
scores = scorer.score_turns(
    history.turns,
    current_intent="schedule-meeting",
    important_entities=["meeting", "Bob"]
)

# Get top N important turns
top_turns = scorer.get_top_turns(history.turns, n=5)
```

### Summarization

```python
from src.context_primitives import SimpleSummarizer, LLMSummarizer

# Simple rule-based summarization
summarizer = SimpleSummarizer(max_length=500)
summary = await summarizer.summarize(history.turns)

# LLM-based summarization (requires BAML client)
summarizer = LLMSummarizer(baml_client)
summary = await summarizer.summarize(
    history.turns,
    existing_summary=history.summary
)
```

## Best Practices

1. **Session Management**
   - Always set TTL for production sessions
   - Use meaningful session IDs (UUIDs recommended)
   - Store user preferences in metadata

2. **History Management**
   - Set appropriate window size for your use case
   - Enable summarization for long conversations
   - Use importance-based truncation for complex dialogues

3. **Variable Storage**
   - Use consistent naming conventions
   - Store only essential context
   - Clean up stale variables

4. **Performance**
   - Use Redis for production hot storage
   - Archive to PostgreSQL for persistence
   - Consider HYBRID backend for best of both

5. **Decorators**
   - Use `with_context_enhanced` for simple context injection
   - Use `record_turn` to automatically track conversations
   - Compose decorators for complex workflows
   - Use `track_metrics` in production for monitoring

6. **Serialization**
   - Use JSON for debugging and human-readable storage
   - Use MessagePack for performance-critical paths
   - Use compression for large contexts or bandwidth constraints

## Related Documentation

- [Phase 7 Implementation Plan](../PHASE7_CONTEXT_PRIMITIVES_PLAN.md)
- [BAML Type Definitions](../../baml_src/context_primitives.baml)
- [Provider Implementation](../../src/context_primitives/provider.py)
- [Unit Tests](../../tests/test_context_primitives/)
