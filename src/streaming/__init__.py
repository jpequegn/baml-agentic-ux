"""
Streaming Support for Complex BAML Types

This module provides utilities for consuming streaming BAML responses,
including progress tracking, UI integration, and callback support.

Example usage:
    from src.streaming import (
        stream_intent_extraction,
        StreamingHandler,
        ConsoleStreamingHandler,
    )

    # Simple streaming with callback
    result = await stream_intent_extraction(
        user_input="create a task",
        interface_schema=schema,
        on_partial=lambda p: print(f"Intent: {p.detected_intent}")
    )

    # With UI handler
    handler = ConsoleStreamingHandler()
    result = await stream_with_handler(
        b.stream.ExtractIntent,
        handler,
        user_input="create a task",
        interface_schema=schema
    )
"""

from src.streaming.types import (
    StreamProgress,
    StreamResult,
    PartialFieldTracker,
)
from src.streaming.consumers import (
    stream_intent_extraction,
    stream_multiple_intents,
    stream_response_generation,
    stream_usability_analysis,
    stream_with_callback,
)
from src.streaming.handlers import (
    StreamingHandler,
    ConsoleStreamingHandler,
    NullStreamingHandler,
    CompositeStreamingHandler,
    stream_with_handler,
)

__all__ = [
    # Types
    "StreamProgress",
    "StreamResult",
    "PartialFieldTracker",
    # Consumers
    "stream_intent_extraction",
    "stream_multiple_intents",
    "stream_response_generation",
    "stream_usability_analysis",
    "stream_with_callback",
    # Handlers
    "StreamingHandler",
    "ConsoleStreamingHandler",
    "NullStreamingHandler",
    "CompositeStreamingHandler",
    "stream_with_handler",
]
