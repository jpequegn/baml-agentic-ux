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
]
