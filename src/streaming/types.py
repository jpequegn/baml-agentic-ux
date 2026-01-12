"""
Types for streaming support.

Provides progress tracking and result wrappers for streaming BAML operations.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, Optional, TypeVar, Set

T = TypeVar("T")
P = TypeVar("P")


class FieldState(Enum):
    """State of a field in a streaming partial object."""

    PENDING = "pending"  # Not yet received
    RECEIVED = "received"  # Has been received (may be partial for strings)
    COMPLETE = "complete"  # Fully complete


@dataclass
class StreamProgress:
    """Tracks progress of a streaming operation.

    Attributes:
        started_at: When streaming started
        last_update: When last partial was received
        partial_count: Number of partial updates received
        fields_received: Set of field names that have values
        estimated_completion: Optional percentage estimate (0-100)
    """

    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    partial_count: int = 0
    fields_received: Set[str] = field(default_factory=set)
    estimated_completion: Optional[float] = None

    def update(self, partial: Any, field_names: Optional[list[str]] = None) -> None:
        """Update progress with a new partial result.

        Args:
            partial: The partial object received
            field_names: Optional list of field names to check
        """
        self.last_update = datetime.now(timezone.utc)
        self.partial_count += 1

        # Track which fields have non-None values
        if field_names:
            for name in field_names:
                if hasattr(partial, name) and getattr(partial, name) is not None:
                    self.fields_received.add(name)
        elif hasattr(partial, "__dict__"):
            for name, value in vars(partial).items():
                if value is not None and not name.startswith("_"):
                    self.fields_received.add(name)

    @property
    def elapsed_ms(self) -> float:
        """Time elapsed since streaming started in milliseconds."""
        delta = self.last_update - self.started_at
        return delta.total_seconds() * 1000

    @property
    def avg_partial_interval_ms(self) -> float:
        """Average time between partial updates in milliseconds."""
        if self.partial_count <= 1:
            return 0.0
        return self.elapsed_ms / (self.partial_count - 1)


@dataclass
class StreamResult(Generic[T, P]):
    """Result of a streaming operation.

    Type Parameters:
        T: The complete result type
        P: The partial result type

    Attributes:
        final: The complete final result
        last_partial: The last partial result before completion
        progress: Progress tracking information
    """

    final: T
    last_partial: Optional[P]
    progress: StreamProgress

    @property
    def time_to_first_partial_ms(self) -> float:
        """Time from start to first partial in milliseconds."""
        if self.progress.partial_count == 0:
            return self.progress.elapsed_ms
        # First partial comes after some time - approximate
        return self.progress.elapsed_ms / max(1, self.progress.partial_count)

    @property
    def total_time_ms(self) -> float:
        """Total streaming time in milliseconds."""
        return self.progress.elapsed_ms


class PartialFieldTracker:
    """Tracks changes between partial updates.

    Useful for detecting when specific fields become available
    or change during streaming.

    Example:
        tracker = PartialFieldTracker()

        for partial in stream:
            changes = tracker.update(partial)
            if "detected_intent" in changes.new_fields:
                print(f"Intent detected: {partial.detected_intent}")
    """

    def __init__(self) -> None:
        """Initialize the tracker."""
        self._previous: dict[str, Any] = {}
        self._field_first_seen: dict[str, int] = {}
        self._update_count = 0

    @dataclass
    class Changes:
        """Changes detected between partial updates."""

        new_fields: Set[str]  # Fields that just got values
        changed_fields: Set[str]  # Fields that changed values
        all_fields: Set[str]  # All fields with values

    def update(self, partial: Any) -> Changes:
        """Update tracker with new partial and return changes.

        Args:
            partial: The new partial object

        Returns:
            Changes detected since last update
        """
        self._update_count += 1

        current: dict[str, Any] = {}
        if hasattr(partial, "__dict__"):
            current = {
                k: v for k, v in vars(partial).items() if not k.startswith("_")
            }
        elif hasattr(partial, "model_dump"):
            current = partial.model_dump()

        new_fields: Set[str] = set()
        changed_fields: Set[str] = set()

        for name, value in current.items():
            if value is None:
                continue

            if name not in self._previous or self._previous[name] is None:
                new_fields.add(name)
                self._field_first_seen[name] = self._update_count
            elif self._previous[name] != value:
                changed_fields.add(name)

        self._previous = current

        return self.Changes(
            new_fields=new_fields,
            changed_fields=changed_fields,
            all_fields={k for k, v in current.items() if v is not None},
        )

    def time_to_field(self, field_name: str) -> Optional[int]:
        """Get the update count when a field was first seen.

        Args:
            field_name: Name of the field

        Returns:
            Update count when field appeared, or None if not yet seen
        """
        return self._field_first_seen.get(field_name)

    def reset(self) -> None:
        """Reset the tracker state."""
        self._previous = {}
        self._field_first_seen = {}
        self._update_count = 0
