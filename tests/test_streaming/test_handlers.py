"""Tests for streaming handlers."""

import pytest
from io import StringIO
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

from src.streaming.types import StreamProgress
from src.streaming.handlers import (
    StreamingHandler,
    NullStreamingHandler,
    ConsoleStreamingHandler,
    CompositeStreamingHandler,
    CallbackStreamingHandler,
    stream_with_handler,
)


class TestNullStreamingHandler:
    """Tests for NullStreamingHandler."""

    @pytest.mark.asyncio
    async def test_all_methods_do_nothing(self) -> None:
        """Test that all methods complete without errors."""
        handler = NullStreamingHandler()

        await handler.on_start()
        await handler.on_partial({"test": "data"}, StreamProgress())
        await handler.on_complete({"result": "done"}, StreamProgress())
        await handler.on_error(ValueError("test"))

        # If we get here without exception, test passes


class TestConsoleStreamingHandler:
    """Tests for ConsoleStreamingHandler."""

    @pytest.mark.asyncio
    async def test_on_start_prints_message(self) -> None:
        """Test on_start prints starting message."""
        output = StringIO()
        handler = ConsoleStreamingHandler(file=output)

        await handler.on_start()

        assert "Streaming started" in output.getvalue()

    @pytest.mark.asyncio
    async def test_on_partial_shows_progress(self) -> None:
        """Test on_partial shows progress information."""
        output = StringIO()
        handler = ConsoleStreamingHandler(
            file=output,
            show_progress=True,
            show_partials=True,
            use_carriage_return=False,
        )

        @dataclass
        class MockPartial:
            field1: str | None = None
            field2: int | None = None

        progress = StreamProgress()
        progress.partial_count = 3
        progress.fields_received = {"field1", "field2"}

        await handler.on_partial(MockPartial(field1="test", field2=42), progress)

        output_text = output.getvalue()
        assert "updates" in output_text or "Fields" in output_text

    @pytest.mark.asyncio
    async def test_on_partial_hidden_when_disabled(self) -> None:
        """Test on_partial produces no output when disabled."""
        output = StringIO()
        handler = ConsoleStreamingHandler(
            file=output,
            show_partials=False,
        )

        @dataclass
        class MockPartial:
            field1: str | None = None

        await handler.on_partial(MockPartial(field1="test"), StreamProgress())

        # Should only be empty or minimal
        assert "test" not in output.getvalue()

    @pytest.mark.asyncio
    async def test_on_complete_prints_summary(self) -> None:
        """Test on_complete prints completion summary."""
        output = StringIO()
        handler = ConsoleStreamingHandler(
            file=output,
            use_carriage_return=False,
        )

        progress = StreamProgress()
        progress.partial_count = 10

        await handler.on_complete({"result": "done"}, progress)

        output_text = output.getvalue()
        assert "complete" in output_text.lower()

    @pytest.mark.asyncio
    async def test_on_error_prints_error(self) -> None:
        """Test on_error prints error message."""
        output = StringIO()
        handler = ConsoleStreamingHandler(file=output)

        await handler.on_error(ValueError("Something went wrong"))

        assert "error" in output.getvalue().lower()
        assert "Something went wrong" in output.getvalue()


class TestCompositeStreamingHandler:
    """Tests for CompositeStreamingHandler."""

    @pytest.mark.asyncio
    async def test_delegates_to_all_handlers(self) -> None:
        """Test that events are delegated to all handlers."""
        handler1 = AsyncMock(spec=StreamingHandler)
        handler2 = AsyncMock(spec=StreamingHandler)

        composite = CompositeStreamingHandler([handler1, handler2])

        await composite.on_start()
        handler1.on_start.assert_called_once()
        handler2.on_start.assert_called_once()

        progress = StreamProgress()
        partial = {"data": "test"}
        await composite.on_partial(partial, progress)
        handler1.on_partial.assert_called_once_with(partial, progress)
        handler2.on_partial.assert_called_once_with(partial, progress)

        result = {"result": "done"}
        await composite.on_complete(result, progress)
        handler1.on_complete.assert_called_once_with(result, progress)
        handler2.on_complete.assert_called_once_with(result, progress)

        error = ValueError("test")
        await composite.on_error(error)
        handler1.on_error.assert_called_once_with(error)
        handler2.on_error.assert_called_once_with(error)


class TestCallbackStreamingHandler:
    """Tests for CallbackStreamingHandler."""

    @pytest.mark.asyncio
    async def test_calls_sync_callbacks(self) -> None:
        """Test that sync callbacks are called."""
        start_called = False
        partial_data = None
        complete_data = None
        error_data = None

        def on_start() -> None:
            nonlocal start_called
            start_called = True

        def on_partial(partial: object, progress: StreamProgress) -> None:
            nonlocal partial_data
            partial_data = partial

        def on_complete(result: object, progress: StreamProgress) -> None:
            nonlocal complete_data
            complete_data = result

        def on_error(error: Exception) -> None:
            nonlocal error_data
            error_data = error

        handler = CallbackStreamingHandler(
            on_start=on_start,
            on_partial=on_partial,
            on_complete=on_complete,
            on_error=on_error,
        )

        await handler.on_start()
        assert start_called

        await handler.on_partial({"test": "data"}, StreamProgress())
        assert partial_data == {"test": "data"}

        await handler.on_complete({"result": "done"}, StreamProgress())
        assert complete_data == {"result": "done"}

        error = ValueError("test")
        await handler.on_error(error)
        assert error_data is error

    @pytest.mark.asyncio
    async def test_calls_async_callbacks(self) -> None:
        """Test that async callbacks are properly awaited."""
        results: list[str] = []

        async def async_on_start() -> None:
            results.append("start")

        async def async_on_partial(partial: object, progress: StreamProgress) -> None:
            results.append("partial")

        handler = CallbackStreamingHandler(
            on_start=async_on_start,
            on_partial=async_on_partial,
        )

        await handler.on_start()
        await handler.on_partial({}, StreamProgress())

        assert results == ["start", "partial"]

    @pytest.mark.asyncio
    async def test_handles_missing_callbacks(self) -> None:
        """Test that missing callbacks don't cause errors."""
        handler = CallbackStreamingHandler()

        # Should not raise
        await handler.on_start()
        await handler.on_partial({}, StreamProgress())
        await handler.on_complete({}, StreamProgress())
        await handler.on_error(ValueError())


class TestStreamWithHandler:
    """Tests for stream_with_handler function."""

    @pytest.mark.asyncio
    async def test_basic_streaming(self) -> None:
        """Test basic streaming with a handler."""

        @dataclass
        class MockPartial:
            value: str | None = None

        @dataclass
        class MockFinal:
            value: str

        # Create mock stream
        partials = [
            MockPartial(),
            MockPartial(value="part"),
            MockPartial(value="partial"),
        ]
        final = MockFinal(value="complete")

        class MockStream:
            def __init__(self) -> None:
                self._index = 0

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self._index >= len(partials):
                    raise StopAsyncIteration
                result = partials[self._index]
                self._index += 1
                return result

            async def get_final_response(self):
                return final

        mock_stream = MockStream()
        handler = AsyncMock(spec=StreamingHandler)

        result = await stream_with_handler(mock_stream, handler)

        # Verify handler was called correctly
        handler.on_start.assert_called_once()
        assert handler.on_partial.call_count == 3
        handler.on_complete.assert_called_once()

        # Verify result
        assert result.final.value == "complete"
        assert result.progress.partial_count == 3

    @pytest.mark.asyncio
    async def test_error_handling(self) -> None:
        """Test that errors trigger on_error and are re-raised."""

        class ErrorStream:
            def __aiter__(self):
                return self

            async def __anext__(self):
                raise ValueError("Stream error")

            async def get_final_response(self):
                pass

        handler = AsyncMock(spec=StreamingHandler)

        with pytest.raises(ValueError, match="Stream error"):
            await stream_with_handler(ErrorStream(), handler)

        handler.on_error.assert_called_once()
        error = handler.on_error.call_args[0][0]
        assert isinstance(error, ValueError)
