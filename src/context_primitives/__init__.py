"""
Context Primitives for Session State Management

Phase 7: BAML Context Primitives Implementation

This module provides session state management for Language User Interfaces,
including conversation history tracking, context variables, and multi-turn
interactions with configurable storage backends.

Example usage:
    from src.context_primitives import (
        ContextConfig, ContextBackend,
        InMemoryContextProvider,
        SessionContext, ConversationTurn, ContextVariables,
        create_provider
    )

    # Create provider (simple)
    config = ContextConfig(max_history_turns=20, ttl_seconds=3600)
    provider = InMemoryContextProvider(config)

    # Create provider (using factory)
    provider = await create_provider(config)

    # Create session
    session = await provider.create_session("user_123")

    # Add conversation turn
    turn = ConversationTurn(
        turn_id=1,
        timestamp=datetime.utcnow(),
        user_input="Hello",
        assistant_response="Hi there!"
    )
    await provider.add_turn("user_123", turn)

    # Get full context
    context = await provider.get_execution_context("user_123")
"""

from src.context_primitives.provider import (
    # Enums
    ContextBackend,
    ContextValueType,
    # Data classes
    SessionContext,
    ConversationTurn,
    ConversationHistory,
    ContextValue,
    ContextVariables,
    ExecutionContext,
    # Configuration
    ContextConfig,
    # Abstract provider
    ContextProvider,
)
from src.context_primitives.stores.memory import InMemoryContextProvider
from src.context_primitives.stores.factory import create_provider, create_memory_provider
from src.context_primitives.history_manager import (
    # Token counting
    TokenCounter,
    TiktokenCounter,
    SimpleTokenCounter,
    # Truncation
    TruncationStrategy,
    TruncationConfig,
    TruncationResult,
    # Importance scoring
    TurnImportance,
    ImportanceWeights,
    ImportanceScorer,
    # Summarization
    ConversationSummary,
    Summarizer,
    SimpleSummarizer,
    LLMSummarizer,
    # History manager
    HistoryManager,
    create_history_manager,
)
from src.context_primitives.serialization import (
    # Serialization formats
    SerializationFormat,
    # Abstract serializer
    ContextSerializer,
    # Concrete serializers
    JSONSerializer,
    MessagePackSerializer,
    CompressedSerializer,
    # Factory
    SerializerFactory,
    create_serializer,
)
from src.context_primitives.integration import (
    # Result type
    ContextualResult,
    # Context Manager
    ContextManager,
    # BAML wrapper
    ContextualBAML,
    # Decorator (basic version)
    with_context,
    # Factory
    create_context_manager,
)
from src.context_primitives.decorators import (
    # Context format enum
    ContextFormat,
    # Metrics
    DecoratorMetrics,
    get_metrics,
    clear_metrics,
    # Core decorators
    with_context as with_context_enhanced,
    with_session,
    record_turn,
    inject_variables,
    require_context,
    track_metrics,
    # Class decorator
    contextual_class,
    # Context manager
    context_scope,
    # Composition helpers
    compose,
    create_contextual_decorator,
)

__all__ = [
    # Enums
    "ContextBackend",
    "ContextValueType",
    # Data classes
    "SessionContext",
    "ConversationTurn",
    "ConversationHistory",
    "ContextValue",
    "ContextVariables",
    "ExecutionContext",
    # Configuration
    "ContextConfig",
    # Abstract provider
    "ContextProvider",
    # Concrete providers
    "InMemoryContextProvider",
    # Factory functions
    "create_provider",
    "create_memory_provider",
    # History Manager - Token counting
    "TokenCounter",
    "TiktokenCounter",
    "SimpleTokenCounter",
    # History Manager - Truncation
    "TruncationStrategy",
    "TruncationConfig",
    "TruncationResult",
    # History Manager - Importance scoring
    "TurnImportance",
    "ImportanceWeights",
    "ImportanceScorer",
    # History Manager - Summarization
    "ConversationSummary",
    "Summarizer",
    "SimpleSummarizer",
    "LLMSummarizer",
    # History Manager - Main class
    "HistoryManager",
    "create_history_manager",
    # Serialization - Formats
    "SerializationFormat",
    # Serialization - Abstract
    "ContextSerializer",
    # Serialization - Concrete serializers
    "JSONSerializer",
    "MessagePackSerializer",
    "CompressedSerializer",
    # Serialization - Factory
    "SerializerFactory",
    "create_serializer",
    # Integration - Result type
    "ContextualResult",
    # Integration - Context Manager
    "ContextManager",
    # Integration - BAML wrapper
    "ContextualBAML",
    # Integration - Decorator
    "with_context",
    # Integration - Factory
    "create_context_manager",
    # Decorators - Enum
    "ContextFormat",
    # Decorators - Metrics
    "DecoratorMetrics",
    "get_metrics",
    "clear_metrics",
    # Decorators - Core
    "with_context_enhanced",
    "with_session",
    "record_turn",
    "inject_variables",
    "require_context",
    "track_metrics",
    # Decorators - Class
    "contextual_class",
    # Decorators - Context manager
    "context_scope",
    # Decorators - Composition
    "compose",
    "create_contextual_decorator",
]
