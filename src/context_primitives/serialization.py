"""
Context Serialization

Efficient serialization for context with multiple format support.

Part of Phase 7: BAML Context Primitives Implementation
Issue #105 - Task 7.5: Context Serialization

Formats:
- JSON: Standard, human-readable (baseline)
- MessagePack: Binary, 3-6x faster, ~30% smaller
- Compressed: Gzip compression for large contexts (50-70% smaller)

Requirements:
    pip install msgpack  # Optional, for MessagePackSerializer
"""

import gzip
import json
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Type

from src.context_primitives.provider import (
    ExecutionContext,
    SessionContext,
    ConversationHistory,
    ConversationTurn,
    ContextVariables,
    ContextValue,
    ContextValueType,
)


class SerializationFormat(Enum):
    """Supported serialization formats."""

    JSON = "json"
    MSGPACK = "msgpack"
    COMPRESSED_JSON = "compressed_json"
    COMPRESSED_MSGPACK = "compressed_msgpack"


class ContextSerializer(ABC):
    """
    Abstract interface for context serialization.

    Implementations must handle datetime conversion and
    support round-trip serialization of ExecutionContext.
    """

    @abstractmethod
    def serialize(self, context: ExecutionContext) -> bytes:
        """
        Serialize an ExecutionContext to bytes.

        Args:
            context: The execution context to serialize

        Returns:
            Serialized bytes representation
        """
        pass

    @abstractmethod
    def deserialize(self, data: bytes) -> ExecutionContext:
        """
        Deserialize bytes to an ExecutionContext.

        Args:
            data: The serialized bytes

        Returns:
            Reconstructed ExecutionContext
        """
        pass

    @property
    @abstractmethod
    def format(self) -> SerializationFormat:
        """Return the serialization format."""
        pass

    @property
    def content_type(self) -> str:
        """Return the MIME content type for this format."""
        return "application/octet-stream"


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder with datetime support."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return {"__datetime__": True, "value": obj.isoformat()}
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


def datetime_decoder(obj: dict) -> Any:
    """JSON decoder hook for datetime objects."""
    if obj.get("__datetime__"):
        return datetime.fromisoformat(obj["value"])
    return obj


def _context_to_dict(context: ExecutionContext) -> dict[str, Any]:
    """
    Convert ExecutionContext to a serializable dictionary.

    Handles datetime conversion and nested dataclass structures.
    """
    session = context.session
    history = context.history
    variables = context.variables

    return {
        "session": {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "metadata": session.metadata,
            "ttl_seconds": session.ttl_seconds,
            "is_active": session.is_active,
        },
        "history": {
            "session_id": history.session_id,
            "turns": [
                {
                    "turn_id": t.turn_id,
                    "timestamp": t.timestamp.isoformat(),
                    "user_input": t.user_input,
                    "assistant_response": t.assistant_response,
                    "detected_intent": t.detected_intent,
                    "extracted_entities": t.extracted_entities,
                    "confidence": t.confidence,
                    "component_id": t.component_id,
                    "duration_ms": t.duration_ms,
                }
                for t in history.turns
            ],
            "max_turns": history.max_turns,
            "total_turns": history.total_turns,
            "summary": history.summary,
            "summary_updated_at": (
                history.summary_updated_at.isoformat()
                if history.summary_updated_at
                else None
            ),
            "token_count": history.token_count,
        },
        "variables": {
            "session_id": variables.session_id,
            "variables": {
                k: {
                    "value_type": v.value_type.value,
                    "string_value": v.string_value,
                    "number_value": v.number_value,
                    "boolean_value": v.boolean_value,
                    "list_value": v.list_value,
                    "object_value": v.object_value,
                }
                for k, v in variables.variables.items()
            },
            "updated_at": variables.updated_at.isoformat(),
        },
        "current_intent": context.current_intent,
        "current_entities": context.current_entities,
    }


def _dict_to_context(data: dict[str, Any]) -> ExecutionContext:
    """
    Convert a dictionary back to ExecutionContext.

    Reconstructs nested dataclass structures from dict.
    """
    session_data = data["session"]
    session = SessionContext(
        session_id=session_data["session_id"],
        user_id=session_data.get("user_id"),
        created_at=datetime.fromisoformat(session_data["created_at"]),
        last_activity=datetime.fromisoformat(session_data["last_activity"]),
        metadata=session_data.get("metadata", {}),
        ttl_seconds=session_data.get("ttl_seconds"),
        is_active=session_data.get("is_active", True),
    )

    history_data = data["history"]
    turns = []
    for t in history_data.get("turns", []):
        turn = ConversationTurn(
            turn_id=t["turn_id"],
            timestamp=datetime.fromisoformat(t["timestamp"]),
            user_input=t["user_input"],
            assistant_response=t["assistant_response"],
            detected_intent=t.get("detected_intent"),
            extracted_entities=t.get("extracted_entities"),
            confidence=t.get("confidence"),
            component_id=t.get("component_id"),
            duration_ms=t.get("duration_ms"),
        )
        turns.append(turn)

    summary_updated_at = history_data.get("summary_updated_at")
    if summary_updated_at:
        summary_updated_at = datetime.fromisoformat(summary_updated_at)

    history = ConversationHistory(
        session_id=history_data["session_id"],
        turns=turns,
        max_turns=history_data.get("max_turns", 20),
        total_turns=history_data.get("total_turns", len(turns)),
        summary=history_data.get("summary"),
        summary_updated_at=summary_updated_at,
        token_count=history_data.get("token_count"),
    )

    variables_data = data["variables"]
    variables_dict = {}
    for k, v in variables_data.get("variables", {}).items():
        cv = ContextValue(
            value_type=ContextValueType(v["value_type"]),
            string_value=v.get("string_value"),
            number_value=v.get("number_value"),
            boolean_value=v.get("boolean_value"),
            list_value=v.get("list_value"),
            object_value=v.get("object_value"),
        )
        variables_dict[k] = cv

    variables = ContextVariables(
        session_id=variables_data["session_id"],
        variables=variables_dict,
        updated_at=datetime.fromisoformat(variables_data["updated_at"]),
    )

    return ExecutionContext(
        session=session,
        history=history,
        variables=variables,
        current_intent=data.get("current_intent"),
        current_entities=data.get("current_entities"),
    )


class JSONSerializer(ContextSerializer):
    """
    JSON-based context serializer.

    Human-readable format suitable for development and debugging.
    Handles datetime objects with ISO 8601 formatting.

    Example:
        serializer = JSONSerializer()
        data = serializer.serialize(context)
        restored = serializer.deserialize(data)
    """

    def __init__(self, indent: Optional[int] = None, ensure_ascii: bool = False):
        """
        Initialize JSON serializer.

        Args:
            indent: JSON indentation (None for compact)
            ensure_ascii: Whether to escape non-ASCII characters
        """
        self._indent = indent
        self._ensure_ascii = ensure_ascii

    def serialize(self, context: ExecutionContext) -> bytes:
        """Serialize ExecutionContext to JSON bytes."""
        data = _context_to_dict(context)
        json_str = json.dumps(
            data,
            indent=self._indent,
            ensure_ascii=self._ensure_ascii,
            cls=DateTimeEncoder,
        )
        return json_str.encode("utf-8")

    def deserialize(self, data: bytes) -> ExecutionContext:
        """Deserialize JSON bytes to ExecutionContext."""
        json_str = data.decode("utf-8")
        parsed = json.loads(json_str, object_hook=datetime_decoder)
        return _dict_to_context(parsed)

    @property
    def format(self) -> SerializationFormat:
        return SerializationFormat.JSON

    @property
    def content_type(self) -> str:
        return "application/json"


class MessagePackSerializer(ContextSerializer):
    """
    MessagePack-based context serializer.

    Binary format that is 3-6x faster than JSON and ~30% smaller.
    Requires the msgpack package.

    Example:
        serializer = MessagePackSerializer()
        data = serializer.serialize(context)
        restored = serializer.deserialize(data)

    Requirements:
        pip install msgpack
    """

    def __init__(self):
        """Initialize MessagePack serializer."""
        try:
            import msgpack

            self._msgpack = msgpack
        except ImportError:
            raise ImportError(
                "MessagePack serialization requires the 'msgpack' package. "
                "Install with: pip install msgpack"
            )

    def serialize(self, context: ExecutionContext) -> bytes:
        """Serialize ExecutionContext to MessagePack bytes."""
        data = _context_to_dict(context)
        return self._msgpack.packb(data, use_bin_type=True)

    def deserialize(self, data: bytes) -> ExecutionContext:
        """Deserialize MessagePack bytes to ExecutionContext."""
        parsed = self._msgpack.unpackb(data, raw=False)
        return _dict_to_context(parsed)

    @property
    def format(self) -> SerializationFormat:
        return SerializationFormat.MSGPACK

    @property
    def content_type(self) -> str:
        return "application/msgpack"


class CompressedSerializer(ContextSerializer):
    """
    Gzip-compressed context serializer.

    Wraps another serializer and applies gzip compression.
    Results in 50-70% size reduction at the cost of CPU time.
    Ideal for large contexts or bandwidth-constrained environments.

    Example:
        # Compressed JSON
        json_serializer = JSONSerializer()
        compressed = CompressedSerializer(json_serializer)

        # Compressed MessagePack
        msgpack_serializer = MessagePackSerializer()
        compressed = CompressedSerializer(msgpack_serializer)
    """

    def __init__(
        self,
        inner_serializer: ContextSerializer,
        compression_level: int = 6,
    ):
        """
        Initialize compressed serializer.

        Args:
            inner_serializer: The serializer to wrap
            compression_level: Gzip compression level (1-9, default 6)
        """
        self._inner = inner_serializer
        self._level = compression_level

    def serialize(self, context: ExecutionContext) -> bytes:
        """Serialize and compress ExecutionContext."""
        uncompressed = self._inner.serialize(context)
        return gzip.compress(uncompressed, compresslevel=self._level)

    def deserialize(self, data: bytes) -> ExecutionContext:
        """Decompress and deserialize to ExecutionContext."""
        decompressed = gzip.decompress(data)
        return self._inner.deserialize(decompressed)

    @property
    def format(self) -> SerializationFormat:
        if self._inner.format == SerializationFormat.JSON:
            return SerializationFormat.COMPRESSED_JSON
        elif self._inner.format == SerializationFormat.MSGPACK:
            return SerializationFormat.COMPRESSED_MSGPACK
        return self._inner.format

    @property
    def content_type(self) -> str:
        return "application/gzip"

    @property
    def inner_serializer(self) -> ContextSerializer:
        """Return the wrapped serializer."""
        return self._inner


def create_serializer(
    format: SerializationFormat = SerializationFormat.JSON,
    compression_level: Optional[int] = None,
    **kwargs,
) -> ContextSerializer:
    """
    Factory function to create a serializer for the specified format.

    Args:
        format: The serialization format to use
        compression_level: Gzip compression level (for compressed formats)
        **kwargs: Additional arguments passed to the serializer

    Returns:
        Configured ContextSerializer instance

    Raises:
        ValueError: If format is not supported
        ImportError: If required dependencies are not installed

    Example:
        # JSON (default)
        serializer = create_serializer()

        # Compact JSON
        serializer = create_serializer(SerializationFormat.JSON)

        # MessagePack (requires msgpack)
        serializer = create_serializer(SerializationFormat.MSGPACK)

        # Compressed JSON
        serializer = create_serializer(SerializationFormat.COMPRESSED_JSON)

        # Compressed MessagePack with custom level
        serializer = create_serializer(
            SerializationFormat.COMPRESSED_MSGPACK,
            compression_level=9
        )
    """
    level = compression_level or 6

    if format == SerializationFormat.JSON:
        return JSONSerializer(**kwargs)
    elif format == SerializationFormat.MSGPACK:
        return MessagePackSerializer()
    elif format == SerializationFormat.COMPRESSED_JSON:
        inner = JSONSerializer(**kwargs)
        return CompressedSerializer(inner, compression_level=level)
    elif format == SerializationFormat.COMPRESSED_MSGPACK:
        inner = MessagePackSerializer()
        return CompressedSerializer(inner, compression_level=level)
    else:
        raise ValueError(f"Unsupported serialization format: {format}")


class SerializerFactory:
    """
    Factory for creating and caching serializer instances.

    Provides a convenient interface for obtaining serializers
    with optional caching for repeated use.

    Example:
        factory = SerializerFactory()

        # Get JSON serializer
        json_ser = factory.get(SerializationFormat.JSON)

        # Get compressed MessagePack serializer
        compressed = factory.get(SerializationFormat.COMPRESSED_MSGPACK)

        # Create without caching
        fresh = factory.create(SerializationFormat.JSON, indent=2)
    """

    def __init__(self):
        """Initialize the serializer factory."""
        self._cache: dict[SerializationFormat, ContextSerializer] = {}

    def get(self, format: SerializationFormat) -> ContextSerializer:
        """
        Get a serializer for the format, using cache if available.

        Args:
            format: The serialization format

        Returns:
            Cached or newly created serializer
        """
        if format not in self._cache:
            self._cache[format] = create_serializer(format)
        return self._cache[format]

    def create(
        self,
        format: SerializationFormat,
        **kwargs,
    ) -> ContextSerializer:
        """
        Create a new serializer with custom options (no caching).

        Args:
            format: The serialization format
            **kwargs: Additional arguments for the serializer

        Returns:
            Newly created serializer
        """
        return create_serializer(format, **kwargs)

    def clear_cache(self) -> None:
        """Clear the serializer cache."""
        self._cache.clear()

    @staticmethod
    def available_formats() -> list[SerializationFormat]:
        """
        Return list of available serialization formats.

        Checks which optional dependencies are installed.
        """
        formats = [
            SerializationFormat.JSON,
            SerializationFormat.COMPRESSED_JSON,
        ]

        try:
            import msgpack  # noqa: F401

            formats.extend([
                SerializationFormat.MSGPACK,
                SerializationFormat.COMPRESSED_MSGPACK,
            ])
        except ImportError:
            pass

        return formats
