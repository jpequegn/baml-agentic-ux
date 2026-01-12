"""Tests for streaming types."""

import pytest
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass

from src.streaming.types import (
    FieldState,
    StreamProgress,
    StreamResult,
    PartialFieldTracker,
)


class TestFieldState:
    """Tests for FieldState enum."""

    def test_field_state_values(self) -> None:
        """Test field state enum values."""
        assert FieldState.PENDING.value == "pending"
        assert FieldState.RECEIVED.value == "received"
        assert FieldState.COMPLETE.value == "complete"


class TestStreamProgress:
    """Tests for StreamProgress dataclass."""

    def test_default_values(self) -> None:
        """Test default values are set correctly."""
        progress = StreamProgress()

        assert progress.partial_count == 0
        assert len(progress.fields_received) == 0
        assert progress.estimated_completion is None
        assert isinstance(progress.started_at, datetime)
        assert isinstance(progress.last_update, datetime)

    def test_update_increments_count(self) -> None:
        """Test that update increments partial count."""
        progress = StreamProgress()

        @dataclass
        class MockPartial:
            field1: str | None = None
            field2: int | None = None

        partial = MockPartial(field1="test")
        progress.update(partial)

        assert progress.partial_count == 1

        progress.update(partial)
        assert progress.partial_count == 2

    def test_update_tracks_fields(self) -> None:
        """Test that update tracks which fields have values."""
        progress = StreamProgress()

        @dataclass
        class MockPartial:
            field1: str | None = None
            field2: int | None = None
            field3: bool | None = None

        # First update - only field1 has value
        partial1 = MockPartial(field1="test")
        progress.update(partial1)
        assert "field1" in progress.fields_received
        assert "field2" not in progress.fields_received

        # Second update - field2 also has value
        partial2 = MockPartial(field1="test", field2=42)
        progress.update(partial2)
        assert "field1" in progress.fields_received
        assert "field2" in progress.fields_received

    def test_update_with_field_names(self) -> None:
        """Test update with explicit field names to check."""
        progress = StreamProgress()

        @dataclass
        class MockPartial:
            field1: str | None = None
            field2: int | None = None
            _private: str | None = None

        partial = MockPartial(field1="test", _private="hidden")
        progress.update(partial, field_names=["field1", "field2"])

        assert "field1" in progress.fields_received
        assert "field2" not in progress.fields_received
        assert "_private" not in progress.fields_received

    def test_elapsed_ms(self) -> None:
        """Test elapsed time calculation."""
        progress = StreamProgress()

        # Manually set times for deterministic testing
        progress.started_at = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        progress.last_update = datetime(2025, 1, 1, 0, 0, 1, 500000, tzinfo=timezone.utc)

        # 1.5 seconds = 1500ms
        assert progress.elapsed_ms == 1500.0

    def test_avg_partial_interval_ms(self) -> None:
        """Test average partial interval calculation."""
        progress = StreamProgress()
        progress.started_at = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        progress.last_update = datetime(2025, 1, 1, 0, 0, 1, tzinfo=timezone.utc)

        # No partials yet
        assert progress.avg_partial_interval_ms == 0.0

        # One partial
        progress.partial_count = 1
        assert progress.avg_partial_interval_ms == 0.0

        # Two partials over 1 second = 1000ms average
        progress.partial_count = 2
        assert progress.avg_partial_interval_ms == 1000.0

        # Five partials over 1 second = 250ms average
        progress.partial_count = 5
        assert progress.avg_partial_interval_ms == 250.0


class TestStreamResult:
    """Tests for StreamResult dataclass."""

    def test_creation(self) -> None:
        """Test creating a stream result."""
        progress = StreamProgress()
        progress.partial_count = 5

        @dataclass
        class MockFinal:
            value: str

        @dataclass
        class MockPartial:
            value: str | None

        result: StreamResult[MockFinal, MockPartial] = StreamResult(
            final=MockFinal(value="complete"),
            last_partial=MockPartial(value="partial"),
            progress=progress,
        )

        assert result.final.value == "complete"
        assert result.last_partial is not None
        assert result.last_partial.value == "partial"
        assert result.progress.partial_count == 5

    def test_total_time_ms(self) -> None:
        """Test total time calculation."""
        progress = StreamProgress()
        progress.started_at = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        progress.last_update = datetime(2025, 1, 1, 0, 0, 2, tzinfo=timezone.utc)

        result: StreamResult[str, str] = StreamResult(
            final="done",
            last_partial="partial",
            progress=progress,
        )

        assert result.total_time_ms == 2000.0


class TestPartialFieldTracker:
    """Tests for PartialFieldTracker."""

    def test_initial_state(self) -> None:
        """Test tracker starts with empty state."""
        tracker = PartialFieldTracker()

        @dataclass
        class MockPartial:
            field1: str | None = None

        changes = tracker.update(MockPartial())

        assert len(changes.new_fields) == 0
        assert len(changes.changed_fields) == 0
        assert len(changes.all_fields) == 0

    def test_detects_new_fields(self) -> None:
        """Test tracker detects when fields get values."""
        tracker = PartialFieldTracker()

        @dataclass
        class MockPartial:
            field1: str | None = None
            field2: int | None = None

        # First update - no fields
        changes1 = tracker.update(MockPartial())
        assert len(changes1.new_fields) == 0

        # Second update - field1 appears
        changes2 = tracker.update(MockPartial(field1="test"))
        assert "field1" in changes2.new_fields
        assert "field2" not in changes2.new_fields

        # Third update - field2 appears
        changes3 = tracker.update(MockPartial(field1="test", field2=42))
        assert "field2" in changes3.new_fields
        assert "field1" not in changes3.new_fields  # Not new anymore

    def test_detects_changed_fields(self) -> None:
        """Test tracker detects when field values change."""
        tracker = PartialFieldTracker()

        @dataclass
        class MockPartial:
            field1: str | None = None

        # Initial value
        tracker.update(MockPartial(field1="initial"))

        # Same value - no change
        changes = tracker.update(MockPartial(field1="initial"))
        assert "field1" not in changes.changed_fields

        # Different value - changed
        changes = tracker.update(MockPartial(field1="updated"))
        assert "field1" in changes.changed_fields

    def test_tracks_all_fields(self) -> None:
        """Test tracker reports all fields with values."""
        tracker = PartialFieldTracker()

        @dataclass
        class MockPartial:
            field1: str | None = None
            field2: int | None = None
            field3: bool | None = None

        changes = tracker.update(
            MockPartial(field1="test", field2=42, field3=None)
        )

        assert "field1" in changes.all_fields
        assert "field2" in changes.all_fields
        assert "field3" not in changes.all_fields  # None value

    def test_time_to_field(self) -> None:
        """Test tracking when fields first appear."""
        tracker = PartialFieldTracker()

        @dataclass
        class MockPartial:
            field1: str | None = None
            field2: int | None = None

        # Update 1 - no fields
        tracker.update(MockPartial())

        # Update 2 - field1 appears
        tracker.update(MockPartial(field1="test"))

        # Update 3 - field2 appears
        tracker.update(MockPartial(field1="test", field2=42))

        assert tracker.time_to_field("field1") == 2
        assert tracker.time_to_field("field2") == 3
        assert tracker.time_to_field("field3") is None  # Never appeared

    def test_reset(self) -> None:
        """Test resetting tracker state."""
        tracker = PartialFieldTracker()

        @dataclass
        class MockPartial:
            field1: str | None = None

        tracker.update(MockPartial(field1="test"))
        assert tracker.time_to_field("field1") == 1

        tracker.reset()

        # After reset, field1 should be "new" again
        changes = tracker.update(MockPartial(field1="test"))
        assert "field1" in changes.new_fields
        assert tracker.time_to_field("field1") == 1

    def test_works_with_pydantic_models(self) -> None:
        """Test tracker works with Pydantic models via model_dump."""
        from pydantic import BaseModel

        class MockPydanticPartial(BaseModel):
            field1: str | None = None
            field2: int | None = None

        tracker = PartialFieldTracker()

        changes = tracker.update(MockPydanticPartial(field1="test"))
        assert "field1" in changes.new_fields
