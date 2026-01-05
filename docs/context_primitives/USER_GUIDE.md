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

## Related Documentation

- [Phase 7 Implementation Plan](../PHASE7_CONTEXT_PRIMITIVES_PLAN.md)
- [BAML Type Definitions](../../baml_src/context_primitives.baml)
- [Provider Implementation](../../src/context_primitives/provider.py)
- [Unit Tests](../../tests/test_context_primitives/)
