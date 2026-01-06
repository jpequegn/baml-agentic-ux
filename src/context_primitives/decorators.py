"""
Context Decorator System

Comprehensive decorators for context management in BAML functions.
Provides flexible, composable decorators for session management,
context injection, turn recording, and metrics tracking.

Part of Phase 7: BAML Context Primitives Implementation
Issue #107 - Task 7.7: Context Decorator System

Example usage:
    from src.context_primitives.decorators import (
        with_context, with_session, record_turn,
        inject_variables, require_context, track_metrics
    )

    manager = await create_context_manager()

    @with_context(manager)
    @record_turn(manager)
    async def handle_message(session_id: str, user_input: str, context=None):
        return f"Response to: {user_input}"

    # Or use class decorator
    @contextual_class(manager)
    class ChatHandler:
        async def handle(self, session_id: str, message: str, context=None):
            return f"Handled: {message}"
"""

import asyncio
import inspect
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from functools import wraps
from typing import (
    Any,
    Callable,
    Optional,
    TypeVar,
    ParamSpec,
    Union,
    Awaitable,
    Type,
    get_type_hints,
)

# Import from integration to avoid circular imports
# ContextManager is imported at runtime to avoid circular dependency


def _utcnow() -> datetime:
    """Get current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


P = ParamSpec("P")
T = TypeVar("T")
R = TypeVar("R")


class ContextFormat(Enum):
    """Format options for injected context."""

    FULL = "full"  # Full ExecutionContext
    CONVERSATION = "conversation"  # SessionConversationContext format
    MINIMAL = "minimal"  # Just session_id and recent turns
    VARIABLES_ONLY = "variables_only"  # Only context variables


@dataclass
class DecoratorMetrics:
    """Metrics captured by decorators."""

    function_name: str
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: int = 0
    success: bool = True
    error: Optional[str] = None
    turn_recorded: bool = False
    context_injected: bool = False
    variables_injected: list[str] = field(default_factory=list)


# Global metrics store (can be replaced with custom implementation)
_metrics_store: list[DecoratorMetrics] = []


def get_metrics() -> list[DecoratorMetrics]:
    """Get collected decorator metrics."""
    return _metrics_store.copy()


def clear_metrics() -> None:
    """Clear collected metrics."""
    _metrics_store.clear()


def _get_manager_lazy():
    """Lazy import of ContextManager to avoid circular imports."""
    from src.context_primitives.integration import ContextManager
    return ContextManager


# ============================================
# Core Decorators
# ============================================


def with_context(
    manager: Any,
    *,
    session_id_param: str = "session_id",
    context_param: str = "context",
    context_format: ContextFormat = ContextFormat.CONVERSATION,
    create_session: bool = True,
    user_id_param: Optional[str] = None,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    Decorator for automatic context injection into async functions.

    Injects conversation context into the decorated function based on
    the session_id parameter. Supports multiple context formats.

    Args:
        manager: ContextManager instance
        session_id_param: Name of the session_id parameter in function signature
        context_param: Name of the parameter to inject context into
        context_format: Format of the injected context
        create_session: Whether to create session if it doesn't exist
        user_id_param: Optional parameter name for user_id (for session creation)

    Returns:
        Decorated async function with context injection

    Example:
        @with_context(manager)
        async def process(session_id: str, message: str, context=None):
            # context is automatically populated
            return f"Session {context['session_id']}: {message}"

        @with_context(manager, context_format=ContextFormat.MINIMAL)
        async def quick_lookup(session_id: str, query: str, context=None):
            # Minimal context for faster execution
            return lookup(query, context['recent_turns'])
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Extract session_id
            session_id = kwargs.get(session_id_param)
            if session_id is None:
                # Try to get from positional args using signature
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if session_id_param in params:
                    idx = params.index(session_id_param)
                    if idx < len(args):
                        session_id = args[idx]

            if session_id is None:
                raise ValueError(
                    f"Missing required parameter '{session_id_param}' for context injection"
                )

            # Get or create session
            if create_session:
                user_id = kwargs.get(user_id_param) if user_id_param else None
                ctx = await manager.get_or_create_session(
                    str(session_id),
                    user_id=str(user_id) if user_id else None,
                )
            else:
                ctx = await manager.get_session_context(str(session_id))
                if ctx is None:
                    raise ValueError(f"Session '{session_id}' not found")

            # Format context based on requested format
            if context_format == ContextFormat.FULL:
                context_value = ctx
            elif context_format == ContextFormat.CONVERSATION:
                context_value = ctx.to_conversation_context()
            elif context_format == ContextFormat.MINIMAL:
                context_value = {
                    "session_id": ctx.session.session_id,
                    "recent_turns": [
                        {"user_input": t.user_input, "assistant_response": t.assistant_response}
                        for t in ctx.history.get_recent(5)
                    ],
                }
            elif context_format == ContextFormat.VARIABLES_ONLY:
                context_value = ctx.variables.to_flat_dict()
            else:
                context_value = ctx.to_conversation_context()

            # Inject context
            kwargs[context_param] = context_value

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def with_session(
    manager: Any,
    *,
    session_id_param: str = "session_id",
    user_id_param: Optional[str] = "user_id",
    metadata_param: Optional[str] = None,
    touch_on_access: bool = True,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    Decorator for session management without full context injection.

    Ensures a session exists and optionally updates last activity.
    Useful when you need session management but not full context.

    Args:
        manager: ContextManager instance
        session_id_param: Name of session_id parameter
        user_id_param: Optional parameter name for user_id
        metadata_param: Optional parameter name for session metadata
        touch_on_access: Whether to update last activity timestamp

    Returns:
        Decorated function with session management

    Example:
        @with_session(manager)
        async def api_call(session_id: str, data: dict):
            # Session is guaranteed to exist
            return await process(data)
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            session_id = kwargs.get(session_id_param)
            if session_id is None:
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if session_id_param in params:
                    idx = params.index(session_id_param)
                    if idx < len(args):
                        session_id = args[idx]

            if session_id is None:
                raise ValueError(f"Missing required parameter: {session_id_param}")

            user_id = kwargs.get(user_id_param) if user_id_param else None
            metadata = kwargs.get(metadata_param) if metadata_param else None

            # Ensure session exists
            await manager.get_or_create_session(
                str(session_id),
                user_id=str(user_id) if user_id else None,
                metadata=metadata,
            )

            # Touch session if configured
            if touch_on_access:
                await manager.provider.touch_session(str(session_id))

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def record_turn(
    manager: Any,
    *,
    session_id_param: str = "session_id",
    user_input_param: str = "user_input",
    response_extractor: Optional[Callable[[Any], str]] = None,
    intent_extractor: Optional[Callable[[Any], Optional[str]]] = None,
    entity_extractor: Optional[Callable[[Any], Optional[dict[str, str]]]] = None,
    component_id: Optional[str] = None,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    Decorator for automatic conversation turn recording.

    Records the function execution as a conversation turn, extracting
    user input, response, intent, and entities.

    Args:
        manager: ContextManager instance
        session_id_param: Name of session_id parameter
        user_input_param: Name of user input parameter
        response_extractor: Function to extract response from result
        intent_extractor: Function to extract intent from result
        entity_extractor: Function to extract entities from result
        component_id: LUI component identifier for this handler

    Returns:
        Decorated function with turn recording

    Example:
        @record_turn(manager, component_id="chat_handler")
        async def chat(session_id: str, user_input: str) -> str:
            response = await generate_response(user_input)
            return response
    """

    def default_response_extractor(result: Any) -> str:
        if isinstance(result, str):
            return result
        if hasattr(result, "response"):
            return str(result.response)
        if hasattr(result, "message"):
            return str(result.message)
        if isinstance(result, dict) and "response" in result:
            return str(result["response"])
        return str(result)

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            session_id = kwargs.get(session_id_param)
            user_input = kwargs.get(user_input_param, "")

            # Get from positional args if not in kwargs
            if session_id is None or not user_input:
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if session_id is None and session_id_param in params:
                    idx = params.index(session_id_param)
                    if idx < len(args):
                        session_id = args[idx]
                if not user_input and user_input_param in params:
                    idx = params.index(user_input_param)
                    if idx < len(args):
                        user_input = args[idx]

            if session_id is None:
                raise ValueError(f"Missing required parameter: {session_id_param}")

            start_time = time.monotonic()

            # Execute function
            result = await func(*args, **kwargs)

            duration_ms = int((time.monotonic() - start_time) * 1000)

            # Extract response
            extractor = response_extractor or default_response_extractor
            response = extractor(result)

            # Extract intent if extractor provided
            intent = intent_extractor(result) if intent_extractor else None

            # Extract entities if extractor provided
            entities = entity_extractor(result) if entity_extractor else None

            # Record the turn
            if user_input and response:
                await manager.record_interaction(
                    session_id=str(session_id),
                    user_input=str(user_input),
                    response=response,
                    intent=intent,
                    entities=entities,
                    component_id=component_id,
                    duration_ms=duration_ms,
                )

            return result

        return wrapper

    return decorator


def inject_variables(
    manager: Any,
    *,
    session_id_param: str = "session_id",
    variables_param: str = "variables",
    keys: Optional[list[str]] = None,
    defaults: Optional[dict[str, Any]] = None,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    Decorator for injecting specific context variables.

    Injects session context variables into a parameter, optionally
    filtering to specific keys and providing defaults.

    Args:
        manager: ContextManager instance
        session_id_param: Name of session_id parameter
        variables_param: Name of parameter to inject variables into
        keys: Optional list of variable keys to inject (None = all)
        defaults: Default values for missing variables

    Returns:
        Decorated function with variable injection

    Example:
        @inject_variables(manager, keys=["user_name", "preferences"])
        async def personalize(session_id: str, message: str, variables=None):
            name = variables.get("user_name", "User")
            return f"Hello {name}! {message}"
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            session_id = kwargs.get(session_id_param)
            if session_id is None:
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if session_id_param in params:
                    idx = params.index(session_id_param)
                    if idx < len(args):
                        session_id = args[idx]

            if session_id is None:
                raise ValueError(f"Missing required parameter: {session_id_param}")

            # Get variables from session
            ctx_vars = await manager.provider.get_variables(str(session_id))
            all_vars = ctx_vars.to_flat_dict()

            # Filter to specified keys if provided
            if keys:
                filtered = {k: all_vars.get(k) for k in keys}
            else:
                filtered = all_vars

            # Apply defaults
            if defaults:
                for k, v in defaults.items():
                    if k not in filtered or filtered[k] is None:
                        filtered[k] = v

            kwargs[variables_param] = filtered

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_context(
    manager: Any,
    *,
    session_id_param: str = "session_id",
    require_history: bool = False,
    min_turns: int = 0,
    required_variables: Optional[list[str]] = None,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    Decorator that validates context requirements before execution.

    Raises an error if the session doesn't meet specified requirements.

    Args:
        manager: ContextManager instance
        session_id_param: Name of session_id parameter
        require_history: Whether conversation history is required
        min_turns: Minimum number of conversation turns required
        required_variables: List of required context variable keys

    Returns:
        Decorated function with context validation

    Raises:
        ValueError: If context requirements are not met

    Example:
        @require_context(manager, min_turns=1, required_variables=["user_id"])
        async def continue_conversation(session_id: str, message: str):
            # Only executes if session has at least 1 turn and user_id variable
            return await process(message)
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            session_id = kwargs.get(session_id_param)
            if session_id is None:
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if session_id_param in params:
                    idx = params.index(session_id_param)
                    if idx < len(args):
                        session_id = args[idx]

            if session_id is None:
                raise ValueError(f"Missing required parameter: {session_id_param}")

            # Get session context
            ctx = await manager.get_session_context(str(session_id))
            if ctx is None:
                raise ValueError(f"Session '{session_id}' not found")

            # Validate history requirement
            if require_history and len(ctx.history.turns) == 0:
                raise ValueError(
                    f"Session '{session_id}' has no conversation history"
                )

            # Validate minimum turns
            if min_turns > 0 and ctx.history.total_turns < min_turns:
                raise ValueError(
                    f"Session '{session_id}' requires at least {min_turns} turns, "
                    f"has {ctx.history.total_turns}"
                )

            # Validate required variables
            if required_variables:
                variables = ctx.variables.to_flat_dict()
                missing = [k for k in required_variables if k not in variables or variables[k] is None]
                if missing:
                    raise ValueError(
                        f"Session '{session_id}' missing required variables: {missing}"
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def track_metrics(
    *,
    session_id_param: str = "session_id",
    store_metrics: bool = True,
    on_complete: Optional[Callable[[DecoratorMetrics], None]] = None,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    Decorator for tracking execution metrics.

    Captures timing, success/failure, and other metrics for decorated functions.

    Args:
        session_id_param: Name of session_id parameter
        store_metrics: Whether to store metrics in global store
        on_complete: Optional callback invoked with metrics after execution

    Returns:
        Decorated function with metrics tracking

    Example:
        @track_metrics(on_complete=lambda m: logger.info(f"Completed in {m.duration_ms}ms"))
        async def process(session_id: str, data: dict):
            return await heavy_operation(data)
    """

    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            session_id = kwargs.get(session_id_param, "unknown")
            if session_id is None:
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if session_id_param in params:
                    idx = params.index(session_id_param)
                    if idx < len(args):
                        session_id = args[idx]

            metrics = DecoratorMetrics(
                function_name=func.__name__,
                session_id=str(session_id) if session_id else "unknown",
                start_time=_utcnow(),
            )

            try:
                result = await func(*args, **kwargs)
                metrics.success = True
                return result
            except Exception as e:
                metrics.success = False
                metrics.error = str(e)
                raise
            finally:
                metrics.end_time = _utcnow()
                metrics.duration_ms = int(
                    (metrics.end_time - metrics.start_time).total_seconds() * 1000
                )

                if store_metrics:
                    _metrics_store.append(metrics)

                if on_complete:
                    on_complete(metrics)

        return wrapper

    return decorator


# ============================================
# Class Decorator
# ============================================


def contextual_class(
    manager: Any,
    *,
    session_id_param: str = "session_id",
    context_param: str = "context",
    method_prefix: str = "",
    exclude_methods: Optional[list[str]] = None,
) -> Callable[[Type[T]], Type[T]]:
    """
    Class decorator for adding context management to all async methods.

    Wraps all async methods (optionally filtered by prefix) with context injection.

    Args:
        manager: ContextManager instance
        session_id_param: Name of session_id parameter
        context_param: Name of context parameter
        method_prefix: Only decorate methods starting with this prefix (empty = all)
        exclude_methods: List of method names to exclude

    Returns:
        Decorated class with context-aware methods

    Example:
        @contextual_class(manager, method_prefix="handle_")
        class MessageHandler:
            async def handle_greeting(self, session_id: str, msg: str, context=None):
                return f"Hello! Context has {context['turn_count']} turns"

            async def internal_helper(self):
                # Not decorated (no prefix match)
                pass
    """
    exclude = set(exclude_methods or [])
    exclude.add("__init__")
    exclude.add("__new__")

    def decorator(cls: Type[T]) -> Type[T]:
        for name, method in inspect.getmembers(cls, predicate=inspect.iscoroutinefunction):
            if name in exclude:
                continue
            if method_prefix and not name.startswith(method_prefix):
                continue

            # Check if method accepts the required parameters
            sig = inspect.signature(method)
            params = list(sig.parameters.keys())

            # Skip if session_id_param not in signature
            if session_id_param not in params:
                continue

            # Apply with_context decorator
            decorated = with_context(
                manager,
                session_id_param=session_id_param,
                context_param=context_param,
            )(method)

            setattr(cls, name, decorated)

        return cls

    return decorator


# ============================================
# Context Manager (async with)
# ============================================


@asynccontextmanager
async def context_scope(
    manager: Any,
    session_id: str,
    *,
    user_id: Optional[str] = None,
    auto_record: bool = False,
    cleanup_on_exit: bool = False,
):
    """
    Async context manager for scoped context operations.

    Provides a context scope where the session context is available
    and optionally cleaned up on exit.

    Args:
        manager: ContextManager instance
        session_id: Session identifier
        user_id: Optional user identifier
        auto_record: Whether to auto-record interactions
        cleanup_on_exit: Whether to delete session on exit

    Yields:
        ExecutionContext for the session

    Example:
        async with context_scope(manager, "session_123") as ctx:
            # ctx is the ExecutionContext
            print(f"Session: {ctx.session.session_id}")
            print(f"Turns: {ctx.history.total_turns}")

        # With cleanup
        async with context_scope(manager, "temp_session", cleanup_on_exit=True) as ctx:
            # Do work...
            pass
        # Session is deleted after exiting
    """
    ctx = await manager.get_or_create_session(session_id, user_id=user_id)

    try:
        yield ctx
    finally:
        if cleanup_on_exit:
            await manager.clear_session(session_id)


# ============================================
# Composition Helpers
# ============================================


def compose(*decorators: Callable) -> Callable:
    """
    Compose multiple decorators into one.

    Applies decorators from right to left (bottom to top in stacked notation).

    Args:
        *decorators: Decorators to compose

    Returns:
        Composed decorator

    Example:
        combined = compose(
            with_context(manager),
            record_turn(manager),
            track_metrics()
        )

        @combined
        async def handler(session_id: str, user_input: str, context=None):
            return "response"
    """

    def composed(func: Callable) -> Callable:
        result = func
        for decorator in reversed(decorators):
            result = decorator(result)
        return result

    return composed


def create_contextual_decorator(
    manager: Any,
    *,
    inject_context: bool = True,
    record_turns: bool = False,
    track: bool = False,
    context_format: ContextFormat = ContextFormat.CONVERSATION,
    component_id: Optional[str] = None,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    Factory for creating custom combined decorators.

    Creates a single decorator that combines multiple context features.

    Args:
        manager: ContextManager instance
        inject_context: Whether to inject context
        record_turns: Whether to record conversation turns
        track: Whether to track metrics
        context_format: Format for context injection
        component_id: Component ID for turn recording

    Returns:
        Combined decorator with specified features

    Example:
        # Create a decorator for chat handlers
        chat_decorator = create_contextual_decorator(
            manager,
            inject_context=True,
            record_turns=True,
            track=True,
            component_id="chat"
        )

        @chat_decorator
        async def chat(session_id: str, user_input: str, context=None):
            return generate_response(user_input, context)
    """
    decorators = []

    if track:
        decorators.append(track_metrics())

    if inject_context:
        decorators.append(with_context(manager, context_format=context_format))

    if record_turns:
        decorators.append(record_turn(manager, component_id=component_id))

    if not decorators:
        # Return identity decorator
        def identity(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
            return func
        return identity

    return compose(*decorators)
