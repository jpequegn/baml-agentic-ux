# Streaming for Complex Types - Design Document

## Overview

This document outlines the implementation of BAML streaming support for complex LUI types. Streaming enables progressive response delivery, improving perceived performance by showing partial results as they become available.

## Problem Statement

Currently, all BAML function calls are blocking - users wait for the complete response before seeing any output. For complex operations like intent extraction or usability analysis, this can result in several seconds of blank screen before any feedback.

## Solution

Add streaming control attributes to key BAML types and create a Python integration module for consuming streamed responses.

## BAML Streaming Attributes

BAML supports three streaming control attributes:

| Attribute | Effect | Use Case |
|-----------|--------|----------|
| `@stream.done` | Field appears only when fully complete | Nested objects that should be atomic |
| `@stream.not_null` | Object emits only after this field has value | Discriminator fields, required metadata |
| `@stream.with_state` | Wraps value with completion state | Long text fields with loading indicators |

## Types to Enhance

### 1. IntentExtraction (High Priority)

```baml
class IntentExtraction {
  detected_intent Intent @stream.done @stream.not_null
  confidence float
  extracted_parameters ExtractedParameter[]
  ambiguity AmbiguityInfo?
  suggested_clarification string? @stream.with_state
}
```

**Rationale:**
- `detected_intent` is atomic - users need complete intent before acting
- `extracted_parameters` streams as array items complete
- `suggested_clarification` shows loading state for long text

### 2. MultiIntentExtraction (High Priority)

```baml
class MultiIntentExtraction {
  execution_strategy ExecutionStrategy @stream.not_null
  intents IntentExtraction[]
  dependencies IntentDependency[]? @stream.done
}
```

**Rationale:**
- Know execution strategy immediately
- Intents stream as each completes
- Dependencies wait for complete graph (correctness)

### 3. GeneratedResponse (High Priority)

```baml
class GeneratedResponse {
  response_type ResponseType @stream.not_null
  response_text string @stream.with_state
  follow_up FollowUpAction?
  visual_elements VisualElement[]?
  tone_applied string?
  personalization_notes string[]?
}
```

**Rationale:**
- Response type known immediately for UI routing
- Response text streams with loading indicator
- Visual elements build up progressively

### 4. UsabilityAnalysis (Medium Priority)

```baml
class UsabilityAnalysis {
  grade UsabilityGrade @stream.not_null
  overall_score float
  summary string @stream.with_state
  category_scores CategoryScore[]
  issues UsabilityIssue[]
  recommendations UsabilityRecommendation[]
  strengths string[]
  comparison_to_gui GUIComparisonResult? @stream.done
}
```

**Rationale:**
- Grade visible immediately (pass/fail indicator)
- Summary shows loading state
- Issues and recommendations stream progressively
- GUI comparison waits for completeness

### 5. RoutingResult (Medium Priority)

```baml
class RoutingResult {
  execution_ready bool @stream.not_null
  matched_component ComponentMatch @stream.done
  parameter_bindings ParameterBinding[]
  missing_required MissingParameter[]?
}
```

**Rationale:**
- Know if execution is ready immediately
- Component match is atomic (need full match reason)
- Parameters stream as bound

## Python Integration Module

### Module Structure

```
src/
└── streaming/
    ├── __init__.py
    ├── types.py         # StreamState, StreamingResult types
    ├── consumers.py     # Stream consumer utilities
    └── handlers.py      # UI integration handlers
```

### Core Types

```python
from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar, AsyncIterator, Optional

T = TypeVar('T')

class StreamState(Enum):
    """State of a streaming field."""
    PENDING = "pending"      # Not yet received
    INCOMPLETE = "incomplete"  # Partially received
    COMPLETE = "complete"    # Fully received

@dataclass
class StreamValue(Generic[T]):
    """Wrapper for streaming field values with state."""
    value: Optional[T]
    state: StreamState

    @property
    def is_ready(self) -> bool:
        return self.state == StreamState.COMPLETE

@dataclass
class StreamingResult(Generic[T]):
    """Result of a streaming operation."""
    partial: T  # Current partial value
    is_complete: bool
    tokens_received: int
```

### Consumer API

```python
async def stream_intent_extraction(
    user_input: str,
    interface_schema: InterfaceSchema,
    conversation_context: Optional[ConversationContext] = None,
    on_partial: Optional[Callable[[IntentExtractionPartial], None]] = None
) -> IntentExtraction:
    """
    Stream intent extraction with partial updates.

    Args:
        user_input: User's input text
        interface_schema: Available components
        conversation_context: Optional conversation context
        on_partial: Callback for partial results

    Returns:
        Complete IntentExtraction when done
    """
    stream = b.stream.ExtractIntent(
        user_input=user_input,
        interface_schema=interface_schema,
        conversation_context=conversation_context
    )

    async for partial in stream:
        if on_partial:
            on_partial(partial)

    return await stream.get_final_response()
```

### UI Integration Handlers

```python
class StreamingUIHandler(ABC):
    """Abstract handler for streaming UI updates."""

    @abstractmethod
    async def on_intent_detected(self, intent: Intent) -> None:
        """Called when intent is fully detected."""
        pass

    @abstractmethod
    async def on_parameter_extracted(self, param: ExtractedParameter) -> None:
        """Called for each extracted parameter."""
        pass

    @abstractmethod
    async def on_clarification_update(self, text: str, state: StreamState) -> None:
        """Called as clarification text streams."""
        pass

class ConsoleStreamingHandler(StreamingUIHandler):
    """Handler that prints streaming updates to console."""

    async def on_intent_detected(self, intent: Intent) -> None:
        print(f"Intent: {intent.intent_name} ({intent.intent_category})")

    async def on_parameter_extracted(self, param: ExtractedParameter) -> None:
        print(f"  Parameter: {param.parameter_name} = {param.extracted_value}")

    async def on_clarification_update(self, text: str, state: StreamState) -> None:
        if state == StreamState.INCOMPLETE:
            print(f"\r  Clarification: {text}...", end="", flush=True)
        else:
            print(f"\r  Clarification: {text}")
```

## Implementation Checklist

### Phase 1: BAML Type Updates
- [ ] Add streaming attributes to `IntentExtraction`
- [ ] Add streaming attributes to `MultiIntentExtraction`
- [ ] Add streaming attributes to `GeneratedResponse`
- [ ] Add streaming attributes to `UsabilityAnalysis`
- [ ] Add streaming attributes to `RoutingResult`
- [ ] Regenerate BAML client code

### Phase 2: Python Streaming Module
- [ ] Create `src/streaming/__init__.py`
- [ ] Create `src/streaming/types.py` with StreamState, StreamValue
- [ ] Create `src/streaming/consumers.py` with streaming wrappers
- [ ] Create `src/streaming/handlers.py` with UI handlers

### Phase 3: Tests
- [ ] Unit tests for streaming types
- [ ] Integration tests for streaming consumers
- [ ] Mock-based tests for streaming handlers

### Phase 4: Documentation
- [ ] Update README with streaming section
- [ ] Add streaming examples
- [ ] Document streaming attributes in BAML files

## Example Usage

### Basic Streaming

```python
from src.streaming import stream_intent_extraction

# Simple usage - just get final result with streaming
result = await stream_intent_extraction(
    user_input="create a task called Review PR",
    interface_schema=schema
)
```

### With Progress Callbacks

```python
from src.streaming import stream_intent_extraction

def on_update(partial):
    if partial.detected_intent:
        print(f"Detected: {partial.detected_intent.intent_name}")
    if partial.extracted_parameters:
        print(f"Found {len(partial.extracted_parameters)} parameters")

result = await stream_intent_extraction(
    user_input="create a task called Review PR",
    interface_schema=schema,
    on_partial=on_update
)
```

### With UI Handler

```python
from src.streaming import stream_with_handler, ConsoleStreamingHandler

handler = ConsoleStreamingHandler()
result = await stream_with_handler(
    b.stream.ExtractIntent,
    handler,
    user_input="create a task",
    interface_schema=schema
)
```

## Testing Strategy

### Unit Tests

```python
def test_stream_state_enum():
    assert StreamState.PENDING.value == "pending"
    assert StreamState.COMPLETE.value == "complete"

def test_stream_value_is_ready():
    pending = StreamValue(value=None, state=StreamState.PENDING)
    complete = StreamValue(value="test", state=StreamState.COMPLETE)

    assert not pending.is_ready
    assert complete.is_ready
```

### Mock Streaming Tests

```python
@pytest.mark.asyncio
async def test_streaming_consumer_with_mock():
    # Create mock partial values
    partials = [
        IntentExtractionPartial(detected_intent=None, confidence=None),
        IntentExtractionPartial(detected_intent=mock_intent, confidence=None),
        IntentExtractionPartial(detected_intent=mock_intent, confidence=0.95),
    ]

    # Mock the stream
    mock_stream = AsyncMock()
    mock_stream.__aiter__.return_value = iter(partials)

    collected = []
    async for partial in mock_stream:
        collected.append(partial)

    assert len(collected) == 3
    assert collected[-1].confidence == 0.95
```

## Performance Considerations

1. **Token Counting**: Track tokens received for progress indication
2. **Memory**: Partial objects are small - no special memory management needed
3. **Network**: Streaming adds minimal overhead vs batched responses
4. **UI Updates**: Debounce rapid partial updates (e.g., every 100ms)

## Compatibility

- BAML 0.70+ required for streaming attributes
- Python 3.10+ for async generator support
- Works with all BAML clients (TypeScript, Python, Ruby)

## Metrics

Track these metrics to measure streaming effectiveness:

| Metric | Target |
|--------|--------|
| Time to first intent | <500ms |
| Time to first parameter | <1s |
| Total streaming overhead | <5% |
| User-perceived improvement | 60-80% |
