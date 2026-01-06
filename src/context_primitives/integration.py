"""
BAML Integration Layer

High-level integration between Context Primitives and BAML functions.
Provides automatic context injection, session management, and result handling.

Part of Phase 7: BAML Context Primitives Implementation
Issue #106 - Task 7.6: BAML Integration Layer

Example usage:
    from src.context_primitives.integration import ContextManager, ContextualBAML
    from baml_client import b

    # Create manager with in-memory provider
    manager = ContextManager()
    await manager.initialize()

    # Wrap BAML client
    contextual = ContextualBAML(manager, b)

    # Execute with automatic context
    result = await contextual.with_context(
        "session_123",
        "ExtractIntent",
        user_input="What's the weather like?"
    )

    # Context is automatically updated after execution
"""

import time
from datetime import datetime, timezone
from typing import Any, Callable, Optional, TypeVar, ParamSpec
from dataclasses import dataclass, field
from functools import wraps

from src.context_primitives.provider import (
    ContextProvider,
    ContextConfig,
    SessionContext,
    ConversationTurn,
    ConversationHistory,
    ContextVariables,
    ExecutionContext,
)
from src.context_primitives.stores.factory import create_provider, create_memory_provider


def _utcnow() -> datetime:
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


P = ParamSpec("P")
T = TypeVar("T")


@dataclass
class ContextualResult:
    """
    Result from a context-aware BAML function execution.

    Captures the function result along with timing and context updates.
    """

    result: Any
    session_id: str
    function_name: str
    duration_ms: int
    context_before: Optional[ExecutionContext] = None
    context_after: Optional[ExecutionContext] = None
    turn_recorded: bool = False
    variables_updated: dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """
    High-level context management for BAML function execution.

    Provides session lifecycle management, context injection,
    and automatic history recording.

    Example:
        manager = ContextManager()
        await manager.initialize()

        # Get or create session context
        ctx = await manager.get_or_create_session("user_123")

        # Execute with context
        result = await manager.with_context(
            "user_123",
            my_async_function,
            arg1="value1"
        )

        # Record interaction
        await manager.record_interaction(
            "user_123",
            user_input="Hello",
            response="Hi there!",
            intent="greeting"
        )
    """

    def __init__(
        self,
        provider: Optional[ContextProvider] = None,
        config: Optional[ContextConfig] = None,
    ):
        """
        Initialize the context manager.

        Args:
            provider: Optional pre-configured provider
            config: Optional configuration (uses defaults if not provided)
        """
        self._provider = provider
        self._config = config or ContextConfig()
        self._initialized = False

    async def initialize(self) -> None:
        """
        Initialize the context manager and underlying provider.

        Must be called before using the manager.
        """
        if self._initialized:
            return

        if self._provider is None:
            self._provider = await create_provider(self._config)

        self._initialized = True

    def _ensure_initialized(self) -> None:
        """Ensure manager is initialized."""
        if not self._initialized:
            raise RuntimeError(
                "ContextManager not initialized. Call await manager.initialize() first."
            )

    @property
    def provider(self) -> ContextProvider:
        """Get the underlying provider."""
        self._ensure_initialized()
        return self._provider  # type: ignore

    async def get_or_create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> ExecutionContext:
        """
        Get existing session or create a new one.

        Args:
            session_id: Session identifier
            user_id: Optional user identifier
            metadata: Optional session metadata

        Returns:
            ExecutionContext for the session
        """
        self._ensure_initialized()

        session = await self._provider.get_session(session_id)  # type: ignore
        if session is None:
            await self._provider.create_session(  # type: ignore
                session_id=session_id,
                user_id=user_id,
                metadata=metadata,
            )

        return await self._provider.get_execution_context(session_id)  # type: ignore

    async def with_context(
        self,
        session_id: str,
        func: Callable[..., Any],
        inject_context: bool = True,
        record_as_turn: bool = False,
        user_input_key: str = "user_input",
        response_key: str = "response",
        **kwargs: Any,
    ) -> ContextualResult:
        """
        Execute a function with automatic context injection.

        Args:
            session_id: Session identifier
            func: Async function to execute
            inject_context: Whether to inject context into function args
            record_as_turn: Whether to record this as a conversation turn
            user_input_key: Key for user input in kwargs (for recording)
            response_key: Key for response in result (for recording)
            **kwargs: Arguments to pass to the function

        Returns:
            ContextualResult with execution details
        """
        self._ensure_initialized()

        start_time = time.monotonic()

        # Get context before execution
        context_before = await self.get_or_create_session(session_id)

        # Inject context if requested
        if inject_context:
            kwargs["context"] = context_before.to_conversation_context()

        # Execute function
        result = await func(**kwargs)

        # Calculate duration
        duration_ms = int((time.monotonic() - start_time) * 1000)

        # Get context after (may have been modified)
        context_after = await self._provider.get_execution_context(session_id)  # type: ignore

        # Record as turn if requested
        turn_recorded = False
        if record_as_turn:
            user_input = kwargs.get(user_input_key, "")
            response = (
                result.get(response_key, str(result))
                if isinstance(result, dict)
                else str(result)
            )
            if user_input and response:
                await self.record_interaction(
                    session_id=session_id,
                    user_input=user_input,
                    response=response,
                    duration_ms=duration_ms,
                )
                turn_recorded = True

        return ContextualResult(
            result=result,
            session_id=session_id,
            function_name=func.__name__ if hasattr(func, "__name__") else str(func),
            duration_ms=duration_ms,
            context_before=context_before,
            context_after=context_after,
            turn_recorded=turn_recorded,
        )

    async def record_interaction(
        self,
        session_id: str,
        user_input: str,
        response: str,
        intent: Optional[str] = None,
        entities: Optional[dict[str, str]] = None,
        confidence: Optional[float] = None,
        component_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
    ) -> None:
        """
        Record a conversation turn.

        Args:
            session_id: Session identifier
            user_input: User's input message
            response: Assistant's response
            intent: Detected intent (optional)
            entities: Extracted entities (optional)
            confidence: Intent confidence score (optional)
            component_id: LUI component that handled this (optional)
            duration_ms: Processing time (optional)
        """
        self._ensure_initialized()

        # Get current history to determine turn_id
        history = await self._provider.get_history(session_id)  # type: ignore
        turn_id = history.total_turns + 1

        turn = ConversationTurn(
            turn_id=turn_id,
            timestamp=_utcnow(),
            user_input=user_input,
            assistant_response=response,
            detected_intent=intent,
            extracted_entities=entities,
            confidence=confidence,
            component_id=component_id,
            duration_ms=duration_ms,
        )

        await self._provider.add_turn(session_id, turn)  # type: ignore

    async def set_variable(
        self,
        session_id: str,
        key: str,
        value: Any,
    ) -> None:
        """
        Set a context variable.

        Args:
            session_id: Session identifier
            key: Variable key
            value: Variable value
        """
        self._ensure_initialized()
        await self._provider.set_variable(session_id, key, value)  # type: ignore

    async def get_variable(
        self,
        session_id: str,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get a context variable.

        Args:
            session_id: Session identifier
            key: Variable key
            default: Default value if not found

        Returns:
            Variable value or default
        """
        self._ensure_initialized()
        variables = await self._provider.get_variables(session_id)  # type: ignore
        return variables.get(key, default)

    async def clear_session(self, session_id: str) -> bool:
        """
        Clear all data for a session.

        Args:
            session_id: Session identifier

        Returns:
            True if session existed and was cleared
        """
        self._ensure_initialized()
        return await self._provider.delete_session(session_id)  # type: ignore

    async def get_session_context(self, session_id: str) -> Optional[ExecutionContext]:
        """
        Get the current execution context for a session.

        Args:
            session_id: Session identifier

        Returns:
            ExecutionContext if session exists, None otherwise
        """
        self._ensure_initialized()

        session = await self._provider.get_session(session_id)  # type: ignore
        if session is None:
            return None

        return await self._provider.get_execution_context(session_id)  # type: ignore

    async def close(self) -> None:
        """Close the context manager and underlying provider."""
        if self._provider and hasattr(self._provider, "close"):
            await self._provider.close()
        self._initialized = False


class ContextualBAML:
    """
    BAML client wrapper with automatic context injection.

    Wraps a BAML client to automatically inject context into
    function calls and record interactions.

    Example:
        from baml_client import b

        manager = ContextManager()
        await manager.initialize()

        contextual = ContextualBAML(manager, b)

        # Execute BAML function with context
        result = await contextual.call(
            "session_123",
            "ExtractIntent",
            user_input="Hello, how are you?"
        )

        # Or use the convenience method for intent extraction
        intent = await contextual.extract_intent(
            "session_123",
            "Hello, how are you?"
        )
    """

    def __init__(
        self,
        manager: ContextManager,
        baml_client: Any,
        auto_record: bool = True,
    ):
        """
        Initialize the contextual BAML wrapper.

        Args:
            manager: ContextManager instance
            baml_client: BAML client (e.g., from baml_client import b)
            auto_record: Whether to automatically record interactions
        """
        self._manager = manager
        self._client = baml_client
        self._auto_record = auto_record

    async def call(
        self,
        session_id: str,
        function_name: str,
        record_as_turn: bool = False,
        inject_context: bool = True,
        context_param: str = "context",
        **kwargs: Any,
    ) -> ContextualResult:
        """
        Call a BAML function with context injection.

        Args:
            session_id: Session identifier
            function_name: BAML function name
            record_as_turn: Whether to record as conversation turn
            inject_context: Whether to inject context
            context_param: Parameter name for context injection
            **kwargs: Arguments for the BAML function

        Returns:
            ContextualResult with function result and metadata

        Raises:
            AttributeError: If function doesn't exist on client
        """
        # Get the BAML function
        func = getattr(self._client, function_name, None)
        if func is None:
            raise AttributeError(f"BAML function '{function_name}' not found")

        start_time = time.monotonic()

        # Get context before execution
        context_before = await self._manager.get_or_create_session(session_id)

        # Prepare arguments with context injection
        call_kwargs = dict(kwargs)
        if inject_context:
            call_kwargs[context_param] = context_before.to_conversation_context()

        # Call the BAML function
        result = await func(**call_kwargs)

        # Calculate duration
        duration_ms = int((time.monotonic() - start_time) * 1000)

        # Get updated context
        context_after = await self._manager.get_session_context(session_id)

        # Record as turn if requested
        turn_recorded = False
        if record_as_turn and self._auto_record:
            user_input = kwargs.get("user_input", "")
            response = self._extract_response(result)
            if user_input and response:
                intent = self._extract_intent(result)
                entities = self._extract_entities(result)
                await self._manager.record_interaction(
                    session_id=session_id,
                    user_input=user_input,
                    response=response,
                    intent=intent,
                    entities=entities,
                    duration_ms=duration_ms,
                )
                turn_recorded = True

        return ContextualResult(
            result=result,
            session_id=session_id,
            function_name=function_name,
            duration_ms=duration_ms,
            context_before=context_before,
            context_after=context_after,
            turn_recorded=turn_recorded,
        )

    def _extract_response(self, result: Any) -> str:
        """Extract response text from BAML result."""
        if isinstance(result, str):
            return result
        if hasattr(result, "response"):
            return str(result.response)
        if hasattr(result, "message"):
            return str(result.message)
        if hasattr(result, "text"):
            return str(result.text)
        if isinstance(result, dict):
            for key in ["response", "message", "text", "output"]:
                if key in result:
                    return str(result[key])
        return str(result)

    def _extract_intent(self, result: Any) -> Optional[str]:
        """Extract intent from BAML result if available."""
        if hasattr(result, "intent"):
            return str(result.intent)
        if hasattr(result, "detected_intent"):
            return str(result.detected_intent)
        if isinstance(result, dict):
            for key in ["intent", "detected_intent", "primary_intent"]:
                if key in result:
                    return str(result[key])
        return None

    def _extract_entities(self, result: Any) -> Optional[dict[str, str]]:
        """Extract entities from BAML result if available."""
        if hasattr(result, "entities"):
            return dict(result.entities) if result.entities else None
        if hasattr(result, "extracted_entities"):
            return dict(result.extracted_entities) if result.extracted_entities else None
        if isinstance(result, dict):
            for key in ["entities", "extracted_entities"]:
                if key in result and result[key]:
                    return dict(result[key])
        return None

    async def extract_intent(
        self,
        session_id: str,
        user_input: str,
        function_name: str = "ExtractIntent",
        record_turn: bool = True,
        **kwargs: Any,
    ) -> ContextualResult:
        """
        Convenience method for intent extraction with context.

        Args:
            session_id: Session identifier
            user_input: User's input message
            function_name: BAML function for intent extraction
            record_turn: Whether to record this interaction
            **kwargs: Additional arguments for the function

        Returns:
            ContextualResult with extracted intent
        """
        return await self.call(
            session_id=session_id,
            function_name=function_name,
            user_input=user_input,
            record_as_turn=record_turn,
            **kwargs,
        )

    async def generate_response(
        self,
        session_id: str,
        user_input: str,
        function_name: str = "GenerateResponse",
        record_turn: bool = True,
        **kwargs: Any,
    ) -> ContextualResult:
        """
        Convenience method for response generation with context.

        Args:
            session_id: Session identifier
            user_input: User's input message
            function_name: BAML function for response generation
            record_turn: Whether to record this interaction
            **kwargs: Additional arguments for the function

        Returns:
            ContextualResult with generated response
        """
        return await self.call(
            session_id=session_id,
            function_name=function_name,
            user_input=user_input,
            record_as_turn=record_turn,
            **kwargs,
        )


def with_context(
    manager: ContextManager,
    session_id_param: str = "session_id",
    inject_context: bool = True,
    record_as_turn: bool = False,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator for adding context management to async functions.

    Args:
        manager: ContextManager instance
        session_id_param: Name of the session_id parameter
        inject_context: Whether to inject context
        record_as_turn: Whether to record as conversation turn

    Returns:
        Decorated function with context management

    Example:
        manager = ContextManager()

        @with_context(manager)
        async def my_function(session_id: str, user_input: str, context=None):
            # context is automatically injected
            return f"You said: {user_input}"
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Extract session_id
            session_id = kwargs.get(session_id_param)
            if session_id is None:
                raise ValueError(f"Missing required parameter: {session_id_param}")

            # Get context
            if inject_context:
                ctx = await manager.get_or_create_session(str(session_id))
                kwargs["context"] = ctx.to_conversation_context()

            # Execute function
            result = await func(*args, **kwargs)

            # Record as turn if configured
            if record_as_turn:
                user_input = kwargs.get("user_input", "")
                response = str(result)
                if user_input:
                    await manager.record_interaction(
                        session_id=str(session_id),
                        user_input=str(user_input),
                        response=response,
                    )

            return result

        return wrapper  # type: ignore

    return decorator


async def create_context_manager(
    config: Optional[ContextConfig] = None,
    provider: Optional[ContextProvider] = None,
) -> ContextManager:
    """
    Factory function to create and initialize a ContextManager.

    Args:
        config: Optional configuration
        provider: Optional pre-configured provider

    Returns:
        Initialized ContextManager

    Example:
        manager = await create_context_manager()
        ctx = await manager.get_or_create_session("my_session")
    """
    manager = ContextManager(provider=provider, config=config)
    await manager.initialize()
    return manager
