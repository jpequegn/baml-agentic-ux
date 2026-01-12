"""
Streaming handlers for UI integration.

Provides abstract and concrete handlers for displaying streaming
progress in various UI contexts.
"""

import sys
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, TypeVar

from baml_client import types

from src.streaming.types import StreamProgress, StreamResult, PartialFieldTracker

T = TypeVar("T")
P = TypeVar("P")


class StreamingHandler(ABC):
    """Abstract base class for streaming UI handlers.

    Implement this class to integrate streaming updates with your UI framework.
    """

    @abstractmethod
    async def on_start(self) -> None:
        """Called when streaming starts."""
        pass

    @abstractmethod
    async def on_partial(self, partial: Any, progress: StreamProgress) -> None:
        """Called for each partial update.

        Args:
            partial: The partial result object
            progress: Current progress information
        """
        pass

    @abstractmethod
    async def on_complete(self, result: Any, progress: StreamProgress) -> None:
        """Called when streaming completes.

        Args:
            result: The final complete result
            progress: Final progress information
        """
        pass

    @abstractmethod
    async def on_error(self, error: Exception) -> None:
        """Called if an error occurs during streaming.

        Args:
            error: The exception that occurred
        """
        pass


class NullStreamingHandler(StreamingHandler):
    """Handler that does nothing - useful for testing or silent operation."""

    async def on_start(self) -> None:
        pass

    async def on_partial(self, partial: Any, progress: StreamProgress) -> None:
        pass

    async def on_complete(self, result: Any, progress: StreamProgress) -> None:
        pass

    async def on_error(self, error: Exception) -> None:
        pass


class ConsoleStreamingHandler(StreamingHandler):
    """Handler that prints streaming updates to the console.

    Provides real-time feedback as streaming progresses, with
    special formatting for different field types.
    """

    def __init__(
        self,
        show_progress: bool = True,
        show_partials: bool = True,
        use_carriage_return: bool = True,
        file: Any = None,
    ) -> None:
        """Initialize console handler.

        Args:
            show_progress: Whether to show progress information
            show_partials: Whether to show partial updates
            use_carriage_return: Use \\r for updating in place
            file: File to write to (defaults to stdout)
        """
        self.show_progress = show_progress
        self.show_partials = show_partials
        self.use_carriage_return = use_carriage_return
        self.file = file or sys.stdout
        self._tracker = PartialFieldTracker()

    async def on_start(self) -> None:
        print("Streaming started...", file=self.file)

    async def on_partial(self, partial: Any, progress: StreamProgress) -> None:
        if not self.show_partials:
            return

        changes = self._tracker.update(partial)

        if self.show_progress:
            progress_str = f"[{progress.partial_count} updates, {progress.elapsed_ms:.0f}ms]"
            fields_str = ", ".join(sorted(progress.fields_received))
            status = f"{progress_str} Fields: {fields_str}"

            if self.use_carriage_return:
                print(f"\r{status:<80}", end="", file=self.file, flush=True)
            else:
                print(status, file=self.file)

        # Print new fields as they appear
        for field in changes.new_fields:
            value = getattr(partial, field, None)
            if value is not None:
                self._print_field(field, value)

    def _print_field(self, name: str, value: Any) -> None:
        """Print a field value with appropriate formatting."""
        if self.use_carriage_return:
            print(file=self.file)  # New line before field

        # Format based on type
        if isinstance(value, str):
            if len(value) > 100:
                value = value[:97] + "..."
            print(f"  {name}: {value}", file=self.file)
        elif isinstance(value, list):
            print(f"  {name}: [{len(value)} items]", file=self.file)
        elif hasattr(value, "__dict__"):
            # Nested object - show type name
            type_name = type(value).__name__
            print(f"  {name}: <{type_name}>", file=self.file)
        else:
            print(f"  {name}: {value}", file=self.file)

    async def on_complete(self, result: Any, progress: StreamProgress) -> None:
        if self.use_carriage_return:
            print(file=self.file)  # Clear the line

        print(
            f"Streaming complete in {progress.elapsed_ms:.0f}ms "
            f"({progress.partial_count} updates)",
            file=self.file,
        )

        self._tracker.reset()

    async def on_error(self, error: Exception) -> None:
        print(f"\nStreaming error: {error}", file=self.file)
        self._tracker.reset()


class CompositeStreamingHandler(StreamingHandler):
    """Handler that delegates to multiple handlers.

    Useful for combining console output with UI updates.
    """

    def __init__(self, handlers: list[StreamingHandler]) -> None:
        """Initialize composite handler.

        Args:
            handlers: List of handlers to delegate to
        """
        self.handlers = handlers

    async def on_start(self) -> None:
        for handler in self.handlers:
            await handler.on_start()

    async def on_partial(self, partial: Any, progress: StreamProgress) -> None:
        for handler in self.handlers:
            await handler.on_partial(partial, progress)

    async def on_complete(self, result: Any, progress: StreamProgress) -> None:
        for handler in self.handlers:
            await handler.on_complete(result, progress)

    async def on_error(self, error: Exception) -> None:
        for handler in self.handlers:
            await handler.on_error(error)


class CallbackStreamingHandler(StreamingHandler):
    """Handler that calls provided callbacks.

    Useful for simple integrations without subclassing.
    """

    def __init__(
        self,
        on_start: Optional[Callable[[], Any]] = None,
        on_partial: Optional[Callable[[Any, StreamProgress], Any]] = None,
        on_complete: Optional[Callable[[Any, StreamProgress], Any]] = None,
        on_error: Optional[Callable[[Exception], Any]] = None,
    ) -> None:
        """Initialize callback handler.

        Args:
            on_start: Called when streaming starts
            on_partial: Called for each partial update
            on_complete: Called when streaming completes
            on_error: Called if an error occurs
        """
        self._on_start = on_start
        self._on_partial = on_partial
        self._on_complete = on_complete
        self._on_error = on_error

    async def on_start(self) -> None:
        if self._on_start:
            result = self._on_start()
            if hasattr(result, "__await__"):
                await result

    async def on_partial(self, partial: Any, progress: StreamProgress) -> None:
        if self._on_partial:
            result = self._on_partial(partial, progress)
            if hasattr(result, "__await__"):
                await result

    async def on_complete(self, result: Any, progress: StreamProgress) -> None:
        if self._on_complete:
            cb_result = self._on_complete(result, progress)
            if hasattr(cb_result, "__await__"):
                await cb_result

    async def on_error(self, error: Exception) -> None:
        if self._on_error:
            result = self._on_error(error)
            if hasattr(result, "__await__"):
                await result


async def stream_with_handler(
    stream: Any,
    handler: StreamingHandler,
    field_names: Optional[list[str]] = None,
) -> StreamResult[Any, Any]:
    """Execute a streaming operation with a handler.

    Args:
        stream: A BAML stream object
        handler: Handler for streaming events
        field_names: Optional field names to track

    Returns:
        StreamResult with final result and progress info
    """
    progress = StreamProgress()
    last_partial = None

    await handler.on_start()

    try:
        async for partial in stream:
            progress.update(partial, field_names)
            last_partial = partial
            await handler.on_partial(partial, progress)

        final = await stream.get_final_response()
        await handler.on_complete(final, progress)

        return StreamResult(
            final=final,
            last_partial=last_partial,
            progress=progress,
        )

    except Exception as e:
        await handler.on_error(e)
        raise
